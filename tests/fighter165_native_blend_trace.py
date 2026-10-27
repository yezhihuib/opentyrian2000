#!/usr/bin/env python3
"""Test-only unconditional actual sprite2 native blend audit; no production edits."""
from pathlib import Path
import argparse,json,os,shutil,subprocess
from fighter165_gameplay import SHA,inventory,tree_inputs
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ('native-build','sysroot','data','present-pack','missing-pack','out'):p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--end',type=int,default=450)
 a=p.parse_args();a=argparse.Namespace(**{k:v.resolve() if isinstance(v,Path) else v for k,v in vars(a).items()})
 out=a.out;out.mkdir(exist_ok=False);source=inventory(ROOT);driver=SHA(Path(__file__));helper=ROOT/'tests/fighter165_gameplay.py';helper_before=SHA(helper);build=a.native_build
 receipt=json.loads((build/'build-receipt.json').read_text());assert receipt['status']=='PASS'
 assert {k:v for k,v in receipt['source_before'].items() if k.startswith('src/')}==source
 assert SHA(build/'opentyrian2000')==receipt['binary_sha256']
 stage=out/'instrumented';shutil.copytree(ROOT/'src',stage/'src');(stage/'assets').symlink_to(ROOT/'assets',target_is_directory=True)
 f=stage/'src/sprite.c';s=f.read_text();s=s.replace('#include "asset_debug.h"','#include "asset_debug.h"\n#include "game_probe.h"')
 old='{ *pixels = (((*data & 0x0f) + (*pixels & 0x0f)) / 2) | (*data & 0xf0); render_mirror_sprite2_blend_pixel(surface,pixels,*data,sprite2s,index,x,y); }'
 new='''{ unsigned before=*pixels; static FILE *trace; if(!trace){trace=fopen("native-blend-writes.tsv","w");assert(trace);fprintf(trace,"tick\\tw\\th\\tpitch\\tindex\\torigin_x\\torigin_y\\twrite_x\\twrite_y\\tbefore\\tsource\\tafter\\n");}
 *pixels = (((*data & 0x0f) + (*pixels & 0x0f)) / 2) | (*data & 0xf0);
 long offset=pixels-(Uint8*)surface->pixels;
 fprintf(trace,"%u\\t%d\\t%d\\t%d\\t%u\\t%d\\t%d\\t%ld\\t%ld\\t%u\\t%u\\t%u\\n",game_probe_tick,surface->w,surface->h,surface->pitch,(unsigned)index,x,y,offset%surface->pitch,offset/surface->pitch,before,(unsigned)*data,(unsigned)*pixels);
 render_mirror_sprite2_blend_pixel(surface,pixels,*data,sprite2s,index,x,y); }'''
 assert s.count(old)==1;s=s.replace(old,new);f.write_text(s)
 env={**os.environ,'PKG_CONFIG_SYSROOT_DIR':str(a.sysroot),'PKG_CONFIG_LIBDIR':str(a.sysroot/'usr/lib/x86_64-linux-gnu/pkgconfig'),'LD_LIBRARY_PATH':str(a.sysroot/'usr/lib/x86_64-linux-gnu')}
 flags=subprocess.check_output(['pkg-config','--cflags','sdl2','SDL2_net'],env=env,text=True).split();libs=subprocess.check_output(['pkg-config','--libs','sdl2','SDL2_net'],env=env,text=True).split()
 objs=sorted((build/'obj').glob('*.o'));dependencies={str(f):SHA(f) for f in objs}
 cmd=['cc','-std=c99','-O2','-g','-DWITH_NETWORK','-DTARGET_UNIX','-DNEWSHF_HD_COMPOSITOR=1','-I'+str(a.sysroot/'usr/include/x86_64-linux-gnu'),*flags,'-I'+str(stage/'src'),'-c',str(f),'-o',str(stage/'sprite.o')]
 compile_cmd=cmd.copy();z=subprocess.run(cmd,env=env,capture_output=True);(out/'compile.log').write_bytes(z.stdout+z.stderr);assert z.returncode==0
 exe=stage/'diagnostic';link=['cc',str(stage/'sprite.o'),*[str(x) for x in objs if x.stem!='sprite'],*libs,'-lm','-o',str(exe)];subprocess.run(link,env=env,check=True)
 instrumented=inventory(stage);runs=[]
 for name,pack in [('missing',a.missing_pack),('present',a.present_pack)]:
  d=out/name;d.mkdir();cfg=d/'config/opentyrian2000';cfg.mkdir(parents=True);(cfg/'opentyrian.cfg').write_text('section video\nitem scaler 4x\nitem fullscreen -1\n')
  e={**env,'SDL_VIDEODRIVER':'dummy','SDL_AUDIODRIVER':'dummy','SDL_RENDER_DRIVER':'software','HOME':str(d),'XDG_CONFIG_HOME':str(d/'config')}
  cmd=[str(exe),f'--data={a.data}','--no-sound','--no-joystick','--no-xmas','--asset-debug=custom','--asset-debug-episode=1','--asset-debug-level=8','--asset-debug-tick=438','--asset-debug-running',f'--render-ticks={a.end}',f'--render-assets={pack}',f'--global-assets={pack}','--render-test=8']
  def bound():return dict(binary=SHA(exe),instrumented_source=inventory(stage),native_objects={str(f):SHA(f) for f in objs},source=inventory(ROOT),pack=tree_inputs(pack),data=tree_inputs(a.data),driver=SHA(Path(__file__)))
  before=bound();(d/'inputs-before.json').write_text(json.dumps(before,indent=2)+'\n')
  with (d/'stdout.log').open('w') as stdout,(d/'stderr.log').open('w') as stderr:z=subprocess.run(cmd,cwd=d,env=e,stdout=stdout,stderr=stderr,timeout=600)
  after=bound();(d/'inputs-after.json').write_text(json.dumps(after,indent=2)+'\n');runs.append(dict(name=name,argv=cmd,exit=z.returncode,unchanged=before==after))
 logs=('native-blend-writes.tsv','state.tsv','enemy-projectiles.tsv','collisions.tsv','fire-events.tsv','player-projectiles.tsv','player-shot-emissions.tsv')
 equal={n:(out/'missing'/n).read_bytes()==(out/'present'/n).read_bytes() for n in logs}
 count=len((out/'present/native-blend-writes.tsv').read_text().splitlines())-1
 okay=all(equal.values()) and count>0 and all(x['exit']==0 and x['unchanged'] for x in runs) and source==inventory(ROOT) and driver==SHA(Path(__file__)) and helper_before==SHA(helper) and dependencies=={str(f):SHA(f) for f in objs}
 result=dict(status='PASS' if okay else 'FAIL',scope='Test-only unconditional actual native sprite2 blend before/source/after/xy; natural visual proof remains separate',equal=equal,writes=count,runs=runs,compile=compile_cmd,link=link,original_source=source,instrumented_source=instrumented,driver_sha256=driver,helper_before_sha256=helper_before,helper_after_sha256=SHA(helper))
 (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'],count);assert okay
if __name__=='__main__':main()
