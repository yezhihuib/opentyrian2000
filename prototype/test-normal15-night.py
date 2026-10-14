#!/usr/bin/env python3
"""Finite OFFLINE physical15 approved branch-residual source units. Never starts the game or copies packs.
Reads explicitly supplied original palette/PIC3/tiny-font/options and six frozen
HUD resources. All private fixtures and binaries remain in an external folder.
"""
import argparse,hashlib,json,os,re,runpy,struct,subprocess,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
TREE='2a60deb74b1a677e3d3cd6c5ea0c251e8ac54028'
SHA=lambda b:hashlib.sha256(b).hexdigest()
MODULES=['gameplay_hud','gameplay_hud_components','gameplay_hud_meters','gameplay_hud_indicators','gameplay_hud_fixed_text','gameplay_hud_font','mtrand']
PINS={'palette.dat':'f628396306805387f07f72c4ccf0fdee9ca84b8e70ae23ba4ec58ec5fb362da0','tyrian.pic':'76fa51ba6878c886f67daa65cf6d19968615e4423822c9fe1dde797fc2f8d802','tyrian.shp':'80cae98e073be6d7f710495920b71497bb23f108ea6631d6faf352c4729474f0'}
def git(root,*args):return subprocess.check_output(['git','-C',str(root),*args])
def extract(s,name):
 m=re.search(r'^[A-Za-z_][^\n;{}]*\b'+name+r'\([^;{}]*\)\s*\{',s,re.M);assert m,name
 end=s.index('{',m.start())+1;depth=1
 while depth:depth+=(s[end]=='{')-(s[end]=='}');end+=1
 return s[m.start():end]+'\n'
def named_hashes(value,name):
 if not isinstance(value,dict):return set()
 found={value[name]['sha256']} if isinstance(value.get(name),dict) and 'sha256' in value[name] else set()
 for nested in value.values():found.update(named_hashes(nested,name))
 return found
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,default=HERE.parent);p.add_argument('--baseline',type=Path);p.add_argument('--normal-data',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--prepare-only',action='store_true');a=p.parse_args()
 a.candidate=a.candidate.resolve();a.baseline=(a.baseline or a.candidate).resolve();a.out=a.out.resolve()
 assert a.out!=a.candidate and a.candidate not in a.out.parents
 if (a.out/'result.json').exists():
  prior=json.loads((a.out/'result.json').read_text());assert prior.get('authored_operator_status')=='APPROVED_BOUNDED_BRANCH_RESIDUAL_OFFLINE_CANDIDATE','Do not overwrite another policy receipt'
 exact=runpy.run_path(str(HERE/'test-normal15-source.py'))['verify_source'](a.candidate)
 assert git(a.baseline,'cat-file','-t',TREE).decode().strip()=='tree'
 a.out.mkdir(parents=True,exist_ok=True);work=a.out/'work';work.mkdir(exist_ok=True);fixtures=work/'fixtures';fixtures.mkdir(exist_ok=True)
 sources={str(p.relative_to(a.candidate)):p.read_bytes() for p in (a.candidate/'src').iterdir() if p.suffix in {'.c','.h','.inc'}}
 baseline={n:git(a.baseline,'show',TREE+':'+n) for n in sources}
 changed=sorted(n for n in sources if sources[n]!=baseline[n]);assert changed==['src/render_mirror.c','src/render_mirror.h','src/tyrian2.c'],changed
 s=sources['src/render_mirror.c'].decode();old=baseline['src/render_mirror.c'].decode()
 unchanged=['cloud_shadow_rgba','darken_rgba','brightness_rgba','enemy_filter_rgba','explosion_blend_rgba','render_mirror_pixel','render_mirror_fade_start','render_mirror_fade_step','render_mirror_present','restore_classic_rect']
 for n in unchanged:assert extract(s,n)==extract(old,n),n
 # Only annotation/classification is allowed inside the original INDEX8 routine.
 candidate=extract(sources['src/tyrian2.c'].decode(),'JE_starShowVGA');original=extract(baseline['src/tyrian2.c'].decode(),'JE_starShowVGA')
 strip=lambda t:re.sub(r'^.*(?:MirrorOutputKind mirror_output|int mirror_lightx|mirror_output =|mirror_lightx =|mirror_lighty =|render_mirror_finish\().*\n','',t,flags=re.M)
 assert strip(candidate)==strip(original),'Original starShow loops changed'
 assert sources['src/tyrian2.c'].decode().replace(candidate,original)==baseline['src/tyrian2.c'].decode(),'Unrelated game logic changed'
 (work/'render-under-test.inc').write_bytes(sources['src/render_mirror.c'])
 (work/'starshow-under-test.inc').write_text(candidate)
 (work/'text-under-test.inc').write_text(''.join(extract(sources['src/fonthand.c'].decode(),n) for n in ['JE_outText','JE_textShade'])+''.join(extract(sources['src/sprite.c'].decode(),n) for n in ['blit_sprite_hv_unsafe','blit_sprite_dark']))
 (work/'ascii-under-test.inc').write_text(re.search(r'const int font_ascii\[256\] =.*?\n};',sources['src/fonthand.c'].decode(),re.S).group())
 raw={n:(a.normal_data/n).read_bytes() for n in PINS}
 assert {n:SHA(b) for n,b in raw.items()}==PINS
 pal=bytes((v<<2)|(v>>4) for v in raw['palette.dat'][5*768:6*768]);assert len(pal)==768
 fnv=14695981039346656037
 for v in pal:fnv=((fnv^v)*1099511628211)&((1<<64)-1)
 assert fnv==0x5e80e83992be2927
 # Independent PCX-style run decoder for original PIC3 only.
 pos=struct.unpack_from('<I',raw['tyrian.pic'],2+2*4)[0];pic=bytearray()
 while len(pic)<64000:
  v=raw['tyrian.pic'][pos];pos+=1
  if v>=192:n=v&63;v=raw['tyrian.pic'][pos];pos+=1
  else:n=1
  pic.extend(bytes([v])*n)
 assert len(pic)==64000
 (fixtures/'pic3.bin').write_bytes(pic);(fixtures/'palette5.bin').write_bytes(pal)
 shp=raw['tyrian.shp'];count=struct.unpack_from('<H',shp)[0];offs=struct.unpack_from('<'+str(count)+'I',shp,2)
 for table in [2,5]:
  start=offs[table];cursor=start;n=struct.unpack_from('<H',shp,cursor)[0];cursor+=2
  assert n<=152
  for i in range(n):
   live=shp[cursor];cursor+=1
   if live:w,h,z=struct.unpack_from('<HHH',shp,cursor);cursor+=6+z
  (fixtures/f'sprites-{table}.bin').write_bytes(shp[start:cursor])
 manifest=json.loads(git(a.baseline,'show',TREE+':assets/hd/manifest.json'));pack=manifest['default_preview_pack'];resources={}
 for name in ['gameplay-hud-v1.hda','gameplay-hud-components-v1.hda','gameplay-hud-meters-v2.hda','gameplay-hud-indicators-v1.hda','gameplay-hud-fixed-text-v1.hda','gameplay-hud-font-v1.hda']:
  path='assets/hd/packs/'+pack+'/'+name;b=git(a.baseline,'show',TREE+':'+path);assert SHA(b) in named_hashes(manifest,name);(fixtures/name).write_bytes(b);resources[path]=SHA(b)
 for k,name in enumerate(['gameplay-hud-v1.hda','gameplay-hud-components-v1.hda','gameplay-hud-meters-v2.hda','gameplay-hud-indicators-v1.hda','gameplay-hud-fixed-text-v1.hda','gameplay-hud-font-v1.hda']):
  folder=fixtures/f'invalid-{k}';folder.mkdir(exist_ok=True)
  for source in fixtures.glob('*.hda'):
   dest=folder/source.name
   if dest.exists() or dest.is_symlink():dest.unlink()
   if source.name==name:b=bytearray(source.read_bytes());b[0]^=1;dest.write_bytes(b)
   else:dest.symlink_to(source)
 (work/'test-fixtures.inc').write_text('static const char *fixture_dir='+json.dumps(str(fixtures))+';\n#include "ascii-under-test.inc"\n')
 report={'status':'PREPARED','public_baseline_commit':exact['public_baseline_commit'],'baseline_tree':TREE,'combined_delta_inverse_exact':exact['combined_delta_inverse_exact'],'changed_production_files':changed,'source_sha256':{n:SHA(b) for n,b in sources.items()},'unchanged_functions':unchanged,'original_indexed_loop_unchanged':True,'original_inputs':PINS,'bounded_resources':resources,'game_runs':0,'full_pack_copies':0,'authored_operator_status':'APPROVED_BOUNDED_BRANCH_RESIDUAL_OFFLINE_CANDIDATE','runs':{},'limitations':['No game loop, actual Hard entry, event timing, visual acceptance, GPU or performance qualification.','Synthetic composed scene swatches; scene-asset loaders and terrain bind identity are not exercised.','Six unchanged real HUD modules and real font bytecode are used; unrelated menu/title-layer hooks and logging are inert.','Invalid normal15 surface layouts decline presentation and clear caches rather than upscale an unsafe destination.','Owner2 is exact current-palette classic at finish; existing owner2 fade interpolation is verified separately.','LeakSanitizer disabled; AddressSanitizer and UndefinedBehaviorSanitizer enabled.']}
 (a.out/'result.json').write_text(json.dumps(report,indent=2)+'\n')
 for config,flags in ([] if a.prepare_only else [('optimized',['-O2']),('sanitized',['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie'])]):
  binary=work/('test-'+config);cmd=[os.environ.get('CC','cc'),'-std=c99','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Wno-unused-function','-Wno-misleading-indentation',*flags,*subprocess.check_output(['pkg-config','--cflags','sdl2'],text=True).split(),'-I'+str(a.candidate/'src'),'-I'+str(work),str(HERE/'test-normal15-night.c'),*[str(a.candidate/'src'/f'{n}.c') for n in MODULES],'-Wl,--gc-sections',*subprocess.check_output(['pkg-config','--libs','sdl2'],text=True).split(),'-o',str(binary)]
  cp=subprocess.run(cmd,text=True,capture_output=True);(a.out/(config+'-compile.log')).write_text(cp.stdout+cp.stderr)
  if cp.returncode:print(cp.stderr);cp.check_returncode()
  env=dict(os.environ,SDL_VIDEODRIVER='dummy',ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1');started=time.monotonic();r=subprocess.run([str(binary)],text=True,capture_output=True,env=env,timeout=300);(a.out/(config+'.log')).write_text(r.stdout+r.stderr);print(config+': '+r.stdout+r.stderr,flush=True);r.check_returncode();report['runs'][config]={'elapsed_seconds':time.monotonic()-started,'result':json.loads(r.stdout)}
 assert all((a.candidate/n).read_bytes()==b for n,b in sources.items()),'source changed during test'
 # Source identities and the exact inverse are retained without a full source copy.
 assert runpy.run_path(str(HERE/'test-normal15-source.py'))['verify_source'](a.candidate)==exact,'Source changed during test'
 report['status']='PREPARED_NOT_EXECUTED' if a.prepare_only else 'PASS';report['harness_sha256']={n:SHA((HERE/n).read_bytes()) for n in ['test-normal15-night.py','test-normal15-night.c','test-normal15-source.py']}
 (a.out/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status']+': '+str(a.out/'result.json'))
if __name__=='__main__':main()
