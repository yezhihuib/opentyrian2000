#!/usr/bin/env python3
"""Production Shield22 observer with a bounded SDL shim; not native engine proof.
Original shape/palette bytes remain in memory and travel only over child stdin.
"""
import argparse,hashlib,json,os,resource,shlex,struct,subprocess,tempfile
from pathlib import Path
from global_talon_reconstruction import extract,fnv64,reference_decode
ROOT=Path(__file__).resolve().parents[1]
HERE=Path(__file__).resolve().parent

def limits():
 resource.setrlimit(resource.RLIMIT_CORE,(0,0))
 resource.setrlimit(resource.RLIMIT_CPU,(240,240))

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--data',type=Path,required=True);p.add_argument('--assets',type=Path,default=ROOT/'assets/hd/global-assets-v1');p.add_argument('--receipt',type=Path,required=True);p.add_argument('--sanitize',action='store_true');a=p.parse_args()
 j=json.loads((a.assets/'registry.json').read_text());f=j['families'][1];assert f['name']=='player-shield-hit'
 shape=(a.data/'tyrian.shp').read_bytes();off=struct.unpack_from('<13I',shape,2);banks=[shape[off[8]:off[9]],(a.data/'newsh6.shp').read_bytes()]
 assert list(map(len,banks))==[33484,17810]
 for family,bank in zip([j['families'][0],f],banks):
  for t in family['source_identity']['tiles']: assert fnv64(reference_decode(bank,t['index']))==int(t['source_fnv64'],16)
 raw=(a.data/'palette.dat').read_bytes()[5*768:6*768];rgb=bytes((v<<2)|(v>>4) for v in raw)
 assert rgb[384:432].hex()==''.join(f['source_identity']['palette']['rgb_hex'])
 payload=b''.join(struct.pack('<I',len(b))+b for b in banks)+b''.join(struct.pack('<I',int.from_bytes(rgb[n:n+3],'big')) for n in range(0,768,3))
 ids={x['resource_identity'] for x in f['phases'] if x.get('resource_identity')};records=[x for x in j['resources'] if x['identity'] in ids];assert len(records)==22
 for item in records:
  b=(a.assets/item['path']).read_bytes();assert len(b)==43036 and hashlib.sha256(b).hexdigest()==item['sha256'];assert fnv64(b[28:])==int(item['payload_fnv64'],16)
 paths=[ROOT/'src'/x for x in ['render_mirror.c','render_mirror.h','global_talon_mirror.inc','global_shield_mirror.inc','global_asset_registry.h','varz.c']]+[HERE/'global_shield_reconstruction.c',HERE/'global_shield_reconstruction.py',HERE/'global_shield_reconstruction.md']
 snap={x:x.read_bytes() for x in paths};mirror=snap[ROOT/'src/render_mirror.c'].decode();varz=snap[ROOT/'src/varz.c'].decode()
 names=['palette_rgb','blend_rgba','darken_rgba','decode_tile','upscale','cloud_shadow_rgba','normal15_palette','normal15_branch','normal15_index','normal15_channel','normal15_rgba','normal15_indices_match']
 with tempfile.TemporaryDirectory(prefix='shield-production-test-') as d:
  d=Path(d)
  for x,b in snap.items():
   if x.suffix in ['.c','.h','.inc']:(d/x.name).write_bytes(b)
  (d/'primitives.inc').write_text('\n'.join(extract(mirror,n) for n in names))
  (d/'pixel.inc').write_text(extract(mirror,'render_mirror_pixel'))
  (d/'root.inc').write_text(extract(mirror,'render_mirror_set_global_assets')+extract(mirror,'render_mirror_global_reset'))
  (d/'fade.inc').write_text(extract(mirror,'render_mirror_fade_start')+extract(mirror,'render_mirror_fade_step'))
  (d/'allocation.inc').write_text(extract(varz,'JE_setupExplosion')+extract(varz,'JE_setupShieldExplosion'))
  for n,item in enumerate(records):
   for mode in ['missing','corrupt','header','trailing']:
    base=d/(mode+str(n));(base/'content').mkdir(parents=True)
    for other in records:
     target=base/other['path']
     if other is not item:target.symlink_to((a.assets/other['path']).resolve())
     elif mode!='missing':
      b=bytearray((a.assets/other['path']).read_bytes())
      if mode=='corrupt':b[31]^=1
      if mode=='header':b[4]^=1
      if mode=='trailing':b+=b'!'
      target.write_bytes(b)
  only=d/'shield-only';(only/'content').mkdir(parents=True)
  for item in records:(only/item['path']).symlink_to((a.assets/item['path']).resolve())
  (d/'feature_off.c').write_text("""#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#define SPRITE_H
#define GROUND101_MATERIAL_H
#define GAMEPLAY_HUD_METERS_H
#define RENDER_MIRROR_DISABLED
#include "render_mirror.h"
int main(void) {
 if(!render_mirror_set_global_assets("/not-read"))return 1;
 if(render_mirror_global_shield(NULL,0,0,0,229,0,0)!=-1)return 2;
 render_mirror_shield_birth_begin(1,14,0,0,true);
 render_mirror_explosion_allocated(0);render_mirror_explosion_initialized(0,14);
 render_mirror_shield_birth_end();render_mirror_global_reset();return 0;
}
""")
  off=shlex.split(os.environ.get('CC','cc'))+['-std=c99','-Wall','-Wextra','-Werror','-I'+str(d),'-I'+str(ROOT/'src'),str(d/'feature_off.c'),'-o',str(d/'feature_off')]
  subprocess.run(off,check=True,timeout=60,preexec_fn=limits)
  subprocess.run([str(d/'feature_off')],check=True,timeout=10,preexec_fn=limits)
  cmd=shlex.split(os.environ.get('CC','cc'))+['-std=c99','-O1','-g','-Wall','-Wextra','-Werror=implicit-function-declaration','-Wno-unused-function','-Wno-unused-variable','-Wno-unused-parameter','-Wno-misleading-indentation','-I'+str(d)]
  if a.sanitize:cmd+=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-no-pie']
  cmd+=[str(d/'global_shield_reconstruction.c'),'-o',str(d/'observer')]
  c=subprocess.run(cmd,capture_output=True,text=True,timeout=120,preexec_fn=limits)
  if c.returncode: print(c.stdout+c.stderr);raise SystemExit(c.returncode)
  result=subprocess.run([str(d/'observer'),str(a.assets.resolve()),str(d)],input=payload,capture_output=True,timeout=240,preexec_fn=limits,env={**os.environ,'ASAN_OPTIONS':'detect_leaks=0:halt_on_error=1','UBSAN_OPTIONS':'halt_on_error=1:print_stacktrace=1'})
  out=result.stdout.decode();err=result.stderr.decode();print(out+err)
  report={'status':'PASS' if result.returncode==0 else 'FAIL','scope':'Extracted production Shield22 and Talon owner helpers, original allocation function; SDL shim and independent indexed-write emission, not native engine proof','returncode':result.returncode,'stdout':out,'stderr':err,'sanitizers':'ASan+UBSan' if a.sanitize else 'none','feature_off_header_compile_and_run':'PASS','original_bytes_persisted':False,'source_sha256':{str(x.relative_to(ROOT)):hashlib.sha256(b).hexdigest() for x,b in snap.items()},'sources_unchanged':all(x.read_bytes()==b for x,b in snap.items()),'resources':{str(x['identity']):x['sha256'] for x in records}}
  a.receipt.parent.mkdir(parents=True,exist_ok=True);a.receipt.write_text(json.dumps(report,indent=2)+'\n');raise SystemExit(0 if result.returncode==0 else 1)
if __name__=='__main__':main()
