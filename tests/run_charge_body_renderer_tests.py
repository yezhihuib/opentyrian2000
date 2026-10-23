#!/usr/bin/env python3
"""Real renderer/SDL component checks, not a game/UI acceptance run.

Requires an explicit authentic private tyrian.shp; no source pixels are bundled.
All generated source slices, test art, compiled objects and logs stay in --out,
which MUST be outside the checkout. Test art is synthetic and not approved art.
"""
import argparse, concurrent.futures, hashlib, json, os, shlex, struct, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE='11a9c7f6eaf60ddb2607fe702b03d6ccadcfb6f4'
IDS=(258,259,260,277,278,279,296,297,298)
def run(cmd,log,env):
 r=subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,text=True,capture_output=True)
 log.write_text('$ '+shlex.join(map(str,cmd))+'\n'+r.stdout+r.stderr)
 if r.returncode:raise RuntimeError(f'{log}: exit {r.returncode}\n{r.stdout[-1000:]}{r.stderr[-2000:]}')
 return r.stdout
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--sysroot',type=Path);a=p.parse_args();out=a.out.resolve()
 if out==ROOT or ROOT in out.parents:p.error('--out must be outside checkout')
 if out.exists():p.error('--out must be fresh')
 out.mkdir(parents=True);env=dict(os.environ);env['SDL_VIDEODRIVER']='dummy'
 if a.sysroot:
  sysroot=a.sysroot.resolve();pc=list(sysroot.glob('usr/lib/**/pkgconfig/sdl2.pc'));assert len(pc)==1
  env.update(PKG_CONFIG_SYSROOT_DIR=str(sysroot),PKG_CONFIG_LIBDIR=str(pc[0].parent),LD_LIBRARY_PATH=str(pc[0].parent.parent))
 cflags=shlex.split(subprocess.check_output(['pkg-config','--cflags','sdl2','SDL2_net'],env=env,text=True));libs=shlex.split(subprocess.check_output(['pkg-config','--libs','sdl2','SDL2_net'],env=env,text=True))
 if a.sysroot:
  inc=list(sysroot.glob('usr/include/*/SDL2/_real_SDL_config.h'));assert len(inc)<=1
  if inc:cflags+=['-I'+str(inc[0].parent.parent)]
 shp=(a.data/'tyrian.shp').resolve();raw=shp.read_bytes();assert hashlib.sha256(raw).hexdigest()=='80cae98e073be6d7f710495920b71497bb23f108ea6631d6faf352c4729474f0'
 offsets=struct.unpack_from('<'+str(struct.unpack_from('<H',raw)[0])+'I',raw,2);assert hashlib.sha256(raw[offsets[8]:offsets[9]]).hexdigest()=='6e783ccf58eb55a4fad82cd1fb600968e1397f297d30398ac935c7f81dfd9cff'
 def dispatch(s):
  start=s.index('\t// draw sidekicks\n');end=s.index('\n}\n\nvoid JE_mainGamePlayerFunctions',start);return s[start:end]
 baseline=subprocess.check_output(['git','show',BASE+':src/mainint.c'],cwd=ROOT,text=True)
 candidate=(ROOT/'src/mainint.c').read_text();(out/'charge_dispatch.inc').write_text('static void baseline_dispatch(Player *this_player,unsigned playerNum_){\n'+dispatch(baseline)+'\n}\nstatic void candidate_dispatch(Player *this_player,unsigned playerNum_){\n'+dispatch(candidate)+'\n}\n')
 fixtures=out/'fixtures';fixtures.mkdir();variants=('valid','missing','truncated','wrong_identity','wrong_density','wrong_geometry','wrong_anchor','trailing','only4','mixed')
 for variant in variants:
  d=fixtures/variant;d.mkdir()
  for i in IDS:
   density=4 if variant=='only4' else 8
   h=struct.pack('<4s6I',b'HDR1',1450000+i+(variant=='wrong_identity'),density if variant!='wrong_density' else 4,12+(variant=='wrong_geometry'),14,variant=='wrong_anchor',0)
   rgba=bytes(v for y in range(14*density) for x in range(12*density) for v in ((x*5+i)%256,(y*7+i)%256,(x*3+y*11)%256,(0,64,128,192,255)[(x+y+i)%5]))
   blob=h+rgba
   if variant=='missing' or (variant=='mixed' and IDS.index(i)%2):continue
   if variant=='truncated':blob=blob[:-1]
   if variant=='trailing':blob+=b'x'
   (d/f'option-charge-bank9-{i}-{density}.hda').write_bytes(blob)
 old=fixtures/'old';old.mkdir()
 for folder,prefix,ids in [('option-marlo152-one-v1','option-marlo-bank9',(152,)),('option-mint-body-three-v1','option-mint-bank9',(112,131,150)),('option-frontblaster-body-one-v1','option-frontblaster-bank10',(83,)),('option-plasma-body-five-v1','option-plasma-bank9',(224,243,262,281,300))]:
  for i in ids:
   path=ROOT/'assets/hd/artwork'/folder/'output'/f'{prefix}-{i}-8.hda';(old/path.name).write_bytes(path.read_bytes())
 cc=os.environ.get('CC','cc');flags=['-std=c99','-O1','-DNDEBUG','-DTARGET_UNIX','-DWITH_NETWORK','-DTYRIAN_DIR="/nonexistent"',*cflags,'-I'+str(out),'-I'+str(ROOT/'src')];objects=out/'objects';objects.mkdir()
 sources=[s for s in sorted((ROOT/'src').glob('*.c')) if s.name!='render_mirror.c']
 def compile_one(s):
  obj=objects/(s.stem+'.o');extra=['-Dmain=charge_engine_main'] if s.name=='opentyr.c' else []
  run([cc,*flags,*extra,'-c',s,'-o',obj],objects/(s.stem+'.log'),env);return obj
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:objs=list(pool.map(compile_one,sources))
 harness=objects/'charge_body_renderer_test.o';run([cc,*flags,'-c',ROOT/'tests/charge_body_renderer_test.c','-o',harness],out/'harness-build.log',env)
 binary=out/'charge-body-test';run([cc,harness,*objs,*libs,'-lm','-Wl,--wrap=blit_sprite2','-o',binary],out/'link.log',env)
 result=json.loads(run([binary,shp,fixtures],out/'run.log',env));result.update(baseline=BASE,private_input_sha256=hashlib.sha256(raw).hexdigest(),synthetic_test_art=True,full_production_renderer=True,sdl_surface_backend=True,windows_or_gpu_acceptance=False)
 (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
