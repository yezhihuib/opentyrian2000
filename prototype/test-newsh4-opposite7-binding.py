#!/usr/bin/env python3
"""Extract production functions, test finite family coherence under ASan/UBSan.
This source/loader recorder does not claim rendered pixels or actual game state.
"""
from pathlib import Path
import argparse,hashlib,json,os,re,struct,subprocess
BASE='67656d102a67cd1bd76c823a2b20f6023f7bb9f0'
sha=lambda x:hashlib.sha256(x).hexdigest()
def extract(s,n):
 m=re.search(r'^[A-Za-z_][^\n;{}]*\b'+n+r'\([^;{}]*\)\s*\{',s,re.M);assert m,n
 b=s.index('{',m.start());e=b+1;depth=1
 while depth:depth+=(s[e]=='{')-(s[e]=='}');e+=1
 return s[m.start():e]+'\n'
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);p.add_argument('--baseline',default=BASE);a=p.parse_args();repo=Path(__file__).resolve().parents[1];given=a.out.absolute();out=given.resolve()
if out.exists() or any(q.is_symlink() for q in [given,*given.parents]) or out==repo or out in repo.parents or repo in out.parents:p.error('Fresh output outside repository required')
assert re.findall(r'game_probe_assets\s*=',(repo/'src/game_probe.c').read_text())==['game_probe_assets='], 'Selected pack must remain startup-only; reassess cache invalidation if a reload writer is added'
assert 'reload-fresh-process' in (repo/'src/asset_debug.c').read_text() and 'asset_debug_exit_code=75' in (repo/'src/asset_debug.c').read_text()
out.mkdir(parents=True);git=lambda *x:subprocess.check_output(['git','-C',str(repo),*x]);baseline=git('show',a.baseline+':src/render_mirror.c').decode();current=(repo/'src/render_mirror.c').read_text();m=json.loads((repo/'assets/hd/manifest.json').read_text());pack=repo/'assets/hd/packs'/m['default_preview_pack'];env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1');traces={};functions={}
for label,s in [('baseline',baseline),('candidate',current)]:
 d=out/label;d.mkdir();patterns=[r'typedef struct \{\s*bool initialized,valid;.*?\} Asset;',r'static Asset assets\[\d+\];',r'static struct \{const Uint8 \*data;unsigned int id;\} terrain_sources\[\d+\];']
 declarations='\n'.join(re.search(p,s,re.S).group() for p in patterns)
 declarations+='\nstatic bool linked31_checked,linked31_valid;\nstatic bool newsh4_long7_checked,newsh4_long7_valid;\n'
 if label=='candidate':declarations+='\nstatic bool newsh4_opposite7_checked,newsh4_opposite7_valid;\n'
 (d/'production-types.inc').write_text(declarations)
 names=['read_asset','scene_asset','linked31_family_ready','newsh4_long7_family_ready']+(['newsh4_opposite7_family_ready'] if label=='candidate' else [])+['render_mirror_enemy_tile','render_mirror_map_begin']
 names+=re.findall(r'static int (\w+_slot)\(unsigned int id\)',s)
 names+=['render_mirror_bind_terrain','render_mirror_terrain_row','palette_rgb','enemy_filter_rgba']
 helpers={n:extract(s,n) for n in names};(d/'production-helpers.inc').write_text('\n'.join(helpers.values()));functions[label]={n:sha(v.encode()) for n,v in helpers.items()}
 cmd=[os.environ.get('CC','cc'),'-std=c99','-O1','-g','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','-DBASELINE='+str(int(label=='baseline')),'-I'+str(d),str(repo/'prototype/test-newsh4-opposite7-binding.c'),'-o',str(d/'test')]
 r=subprocess.run(cmd,capture_output=True,text=True);(d/'compile.log').write_text(r.stdout+r.stderr);r.check_returncode()
 r=subprocess.run([str(d/'test'),str(pack),'trace','1'],env=env,capture_output=True,text=True,timeout=90);(d/'trace.log').write_text(r.stdout+r.stderr);r.check_returncode();traces[label]={tuple(x.split()[:3]):int(x.split()[3]) for x in r.stdout.splitlines()}
expected=dict(traces['baseline']);expected.update({('a','2',str(i)):389+k for k,i in enumerate([231,233,235,267,269,271,273])});assert traces['candidate']==expected
results=[]
def check(d,present,label):
 r=subprocess.run([str(out/'candidate/test'),str(d),'test',str(present)],env=env,capture_output=True,text=True,timeout=90)
 if r.returncode:(out/(label+'.log')).write_text(r.stdout+r.stderr)
 r.check_returncode();results.append(label)
check(pack,1,'complete-seven');fixtures=out/'fixtures';fixtures.mkdir();names=[f'enemy-newsh4-{i}-8.hda' for i in [231,233,235,267,269,271,273]];left_names=[f'enemy-newsh4-{i}-8.hda' for i in [153,155,157,159,191,193,195]];neighbors=['enemy-newsh2-153-8.hda']+left_names
for name in names:
 raw=(pack/name).read_bytes();invalid={'missing':None,'magic':b'BAD!'+raw[4:],'truncated':raw[:-1],'trailing':raw+b'\0','alpha':raw[:31]+bytes([raw[31]^255])+raw[32:],'rgb':raw[:28]+bytes([raw[28]^1])+raw[29:]}
 for field in range(6):
  data=bytearray(raw);struct.pack_into('<I',data,4+field*4,struct.unpack_from('<I',data,4+field*4)[0]+1);invalid['field-'+str(field)]=bytes(data)
 for label,data in invalid.items():
  d=fixtures/(name+'-'+label);d.mkdir()
  for other in names+neighbors:
   if other!=name:os.link(pack/other,d/other)
  if data is not None:(d/name).write_bytes(data)
  check(d,0,name+'-'+label)
# Either family may be bad without disabling the other family.
for family,bad_names,right in [('left',left_names,1),('right',names,0)]:
 for name in bad_names:
  for kind in ['missing','corrupt']:
   d=fixtures/(family+'-independent-'+name+'-'+kind);d.mkdir()
   for other in names+neighbors:
    if other!=name:os.link(pack/other,d/other)
   if kind=='corrupt':
    raw=(pack/name).read_bytes();(d/name).write_bytes(raw[:28]+bytes([raw[28]^1])+raw[29:])
   r=subprocess.run([str(out/'candidate/test'),str(d),'independent',str(right)],env=env,capture_output=True,text=True,timeout=90)
   if r.returncode:(out/(d.name+'.log')).write_text(r.stdout+r.stderr)
   r.check_returncode();results.append(d.name)
report={'status':'passed','baseline':a.baseline,'sanitizers':['address','undefined'],'leak_detection':False,'leak_detection_reason':'LSan cannot run under this executor ptrace; allocations freed by recorder reset','unchanged_prior_bindings':len(traces['baseline']),'new_bindings':7,'separate_left_right_fallback':True,'empty_quadrant231_preserves_complete_composite':True,'fixture_mirrors':'read-only-by-workflow hardlinks, never symlinks or mutated in place','all_sheet_identities_checked':list(range(37)),'preflight_allocation_failure_positions':list(range(7)),'disabled_scene_combinations':[0,2],'cache_lifecycle':'startup-selected pack; failed and successful preflight are cached; process/cache reset retries successfully; no mid-session reload writer','family_fallback_cases':results,'functions':functions,'limitations':['Recorder only; no game runs, rendered pixels or Windows runtime.']};(out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['functions','family_fallback_cases']},indent=2));print('Fallback cases:',len(results))
