#!/usr/bin/env python3
"""Extract production functions, test finite family coherence under ASan/UBSan.
This source/loader recorder does not claim rendered pixels or actual game state.
"""
from pathlib import Path
import argparse,hashlib,json,os,re,struct,subprocess
BASE='2efdc890217330e75a873252ca96b576495b23b9'
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
 declarations+='\nstatic bool linked31_checked,linked31_valid;\nstatic bool newsh4_long7_checked,newsh4_long7_valid;\nstatic bool newsh4_opposite7_checked,newsh4_opposite7_valid;\n'
 declarations+='\nstatic bool type15_eightheading_checked,type15_eightheading_valid;\n'
 if label=='candidate':declarations+='\nstatic bool late_spike_checked,late_spike_valid;\n'
 (d/'production-types.inc').write_text(declarations)
 names=['read_asset','scene_asset','linked31_family_ready','newsh4_long7_family_ready','newsh4_opposite7_family_ready','type15_eightheading_family_ready']+(['late_spike_family_ready'] if label=='candidate' else [])+['render_mirror_enemy_tile','render_mirror_map_begin']
 names+=re.findall(r'static int (\w+_slot)\(unsigned int id\)',s)
 names+=['render_mirror_bind_terrain','render_mirror_terrain_row','palette_rgb','enemy_filter_rgba']
 helpers={n:extract(s,n) for n in names};(d/'production-helpers.inc').write_text('\n'.join(helpers.values()));functions[label]={n:sha(v.encode()) for n,v in helpers.items()}
 cmd=[os.environ.get('CC','cc'),'-std=c99','-O1','-g','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','-DBASELINE='+str(int(label=='baseline')),'-I'+str(d),str(repo/'prototype/test-late-spike-binding.c'),'-o',str(d/'test')]
 r=subprocess.run(cmd,capture_output=True,text=True);(d/'compile.log').write_text(r.stdout+r.stderr);r.check_returncode()
 r=subprocess.run([str(d/'test'),str(pack),'trace','1'],env=env,capture_output=True,text=True,timeout=90);(d/'trace.log').write_text(r.stdout+r.stderr);r.check_returncode();traces[label]={tuple(x.split()[:3]):int(x.split()[3]) for x in r.stdout.splitlines()}
expected=dict(traces['baseline']);expected.update({('a','1',str(i)):404+k for k,i in enumerate([1,3,5,7,9,11])});assert traces['candidate']==expected
results=[]
def check(d,present,label):
 r=subprocess.run([str(out/'candidate/test'),str(d),'test',str(present)],env=env,capture_output=True,text=True,timeout=90)
 if r.returncode:(out/(label+'.log')).write_text(r.stdout+r.stderr)
 r.check_returncode();results.append(label)
check(pack,1,'complete-six');fixtures=out/'fixtures';fixtures.mkdir();names=[f'enemy-newsh2-{i}-8.hda' for i in [1,3,5,7,9,11]];neighbors=['enemy-newsh2-153-8.hda']+[f'enemy-newshe-{i}-8.hda'for i in [1,3,5,7,9,11]]+[f'enemy-newsh2-{i}-8.hda'for i in [39,41,43,45,91,93,129,131,15,17,53,55]]+[f'terrain-shapesz-{i}-8.hda'for i in [161,162,171,172]]+[f'enemy-newsh4-{i}-8.hda'for i in [153,155,157,159,191,193,195,231,233,235,267,269,271,273]]
for name in names:
 raw=(pack/name).read_bytes();invalid={'missing':None,'magic':b'BAD!'+raw[4:],'truncated':raw[:-1],'trailing':raw+b'\0','alpha':raw[:31]+bytes([raw[31]^255])+raw[32:],'partial-alpha':raw[:31]+b'\x7f'+raw[32:],'rgb':raw[:28]+bytes([raw[28]^1])+raw[29:]}
 for field in range(6):
  data=bytearray(raw);struct.pack_into('<I',data,4+field*4,struct.unpack_from('<I',data,4+field*4)[0]+1);invalid['field-'+str(field)]=bytes(data)
 for label,data in invalid.items():
  d=fixtures/(name+'-'+label);d.mkdir()
  for other in names+neighbors:
   if other!=name:os.link(pack/other,d/other)
  if data is not None:(d/name).write_bytes(data)
  check(d,0,name+'-'+label)
for target in neighbors:
 for corruption in ['missing','rgb']:
  d=fixtures/('independent-'+target+'-'+corruption);d.mkdir()
  for other in names+neighbors:
   if other!=target:os.link(pack/other,d/other)
  if corruption=='rgb':
   raw=(pack/target).read_bytes();(d/target).write_bytes(raw[:28]+bytes([raw[28]^1])+raw[29:])
  r=subprocess.run([str(out/'candidate/test'),str(d),'independent','1'],env=env,capture_output=True,text=True,timeout=90)
  if r.returncode:(out/('independent-'+target+'-'+corruption+'.log')).write_text(r.stdout+r.stderr)
  r.check_returncode();results.append('independent-'+target+'-'+corruption)
report={'status':'passed','baseline':a.baseline,'sanitizers':['address','undefined'],'leak_detection':False,'leak_detection_reason':'LSan cannot run under this executor ptrace; allocations freed by recorder reset','unchanged_prior_bindings':len(traces['baseline']),'new_bindings':6,'geometric_quadrant_fallback':{'family_only':True,'required_layout':[320,200,320,8,1],'safe_x':[0,308],'pitch_cases':['INT_MIN',-1,0,11,12,319,320,321,'INT_MAX'],'all_six_all_parts_all_256_filters':True,'clipped_y_cases':[-214,-28,-14,-1,0,1,185,199,200,214],'extreme_x_corners':True,'invalid_width_height_bpp_null_format':True,'neighbor_edge_routes_unchanged':True},'fixture_mirrors':'read-only-by-workflow hardlinks, never symlinks or mutated in place','all_sheet_identities_checked':list(range(37)),'preflight_allocation_failure_positions':list(range(6)),'disabled_scene_combinations':[0,2],'cache_lifecycle':'startup-selected pack; failed and successful preflight are cached; process/cache reset retries successfully; no mid-session reload writer','family_fallback_cases':results,'functions':functions,'limitations':['Recorder only; no game runs, rendered pixels or Windows runtime.']};(out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['functions','family_fallback_cases']},indent=2));print('Fallback cases:',len(results))
