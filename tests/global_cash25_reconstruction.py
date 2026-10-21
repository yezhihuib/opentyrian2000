#!/usr/bin/env python3
"""Production Cash25BodyAndValue7 observer with a bounded SDL shim; not native engine proof.
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
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--data',type=Path,required=True);p.add_argument('--assets',type=Path,default=ROOT/'assets/hd/global-assets-v1');p.add_argument('--receipt',type=Path,required=True);p.add_argument('--sanitize',action='store_true');p.add_argument('--negative-control',action='store_true',help='Remove observed-revocation preflight only from temporary build; must be caught');a=p.parse_args()
 j=json.loads((a.assets/'registry.json').read_text());families=j['families'][7:12];f=families[0];assert [v['name'] for v in families]==['cash25-body-and-value','cash50-body-and-value','cash75-body-and-value','gem100-body-and-value','gem250-body-and-value']
 shape=(a.data/'tyrian.shp').read_bytes();off=struct.unpack_from('<13I',shape,2);banks=[shape[off[8]:off[9]],(a.data/'newsh6.shp').read_bytes(),shape[off[10]:off[11]]]
 assert list(map(len,banks))==[33484,17810,29032]
 for source,bank in zip([j['families'][0]['source_identity'],f['source_identity']['value_source'],f['source_identity']],banks):
  for t in source['tiles']: assert fnv64(reference_decode(bank,t['index']))==int(t['source_fnv64'],16)
 raw=(a.data/'palette.dat').read_bytes()[5*768:6*768];rgb=bytes((v<<2)|(v>>4) for v in raw)
 pal=f['source_identity']['palette']; indices=pal.get('indices',list(range(pal.get('first_index',0),pal.get('first_index',0)+pal.get('count',0))))
 assert [rgb[i*3:i*3+3].hex() for i in indices]==pal['rgb_hex']
 payload=b''.join(struct.pack('<I',len(b))+b for b in banks)+(a.data/'tyrian.hdt').read_bytes()[164015+391*77:164015+396*77]+b''.join(struct.pack('<I',int.from_bytes(rgb[n:n+3],'big')) for n in range(0,768,3))
 ids={i for f in families for i in f['resources']};records=[x for x in j['resources'] if x['identity'] in ids];assert len(records)==33
 for item in records:
  b=(a.assets/item['path']).read_bytes();assert len(b)==43036 and hashlib.sha256(b).hexdigest()==item['sha256'];assert fnv64(b[28:])==int(item['payload_fnv64'],16)
 paths=[ROOT/'src'/x for x in ['render_mirror.c','render_mirror.h','global_talon_mirror.inc','global_cash25_mirror.inc','global_cash25_identity.inc','global_asset_registry.h','shared_asset_reader.h','varz.c','episodes.h','varz.h','ground101_material.h']]+[HERE/'global_cash25_reconstruction.c',HERE/'global_cash25_reconstruction.py',HERE/'global_cash25_reconstruction.md',HERE/'global_talon_reconstruction.py']
 snap={x:x.read_bytes() for x in paths};mirror=snap[ROOT/'src/render_mirror.c'].decode();varz=snap[ROOT/'src/varz.c'].decode()
 names=['palette_rgb','blend_rgba','darken_rgba','decode_tile','upscale','cloud_shadow_rgba','normal15_palette','normal15_branch','normal15_index','normal15_channel','normal15_rgba','normal15_indices_match','explosion_asset_blend_rgba']
 with tempfile.TemporaryDirectory(prefix='cash25-production-test-') as d:
  d=Path(d)
  for x,b in snap.items():
   if x.suffix in ['.c','.h','.inc']:(d/x.name).write_bytes(b)
  if a.negative_control:
   inc=d/'global_cash25_mirror.inc';text=inc.read_text();start=text.index(' if(global_cash25_contributed&&(');end=text.index('global_cash25_fail();',start)+len('global_cash25_fail();');inc.write_text(text[:start]+text[end:])
  episodes=snap[ROOT/'src/episodes.h'].decode();varzh=snap[ROOT/'src/varz.h'].decode();ctx=snap[ROOT/'src/ground101_material.h'].decode()
  rec=episodes.split('/* EnemyData */',1)[1].split('extern JE_WeaponPortType',1)[0]
  body='struct JE_SingleEnemyType'+varzh.split('struct JE_SingleEnemyType',1)[1].split('typedef struct JE_SingleEnemyType JE_MultiEnemyType[100];',1)[0]+'typedef struct JE_SingleEnemyType JE_MultiEnemyType[100];\n'
  context='typedef struct {\n unsigned type,pool_slot,availability,size;\n bool score_item,damaged,independent_motion,static_animation;\n} G101EnemyContext;\n'
  assert context.strip() in ctx
  (d/'cash25_identity_types.h').write_text(rec+body+context)
  (d/'primitives.inc').write_text('\n'.join(extract(mirror,n) for n in names))
  (d/'pixel.inc').write_text(extract(mirror,'render_mirror_pixel'))
  (d/'root.inc').write_text(extract(mirror,'render_mirror_set_global_assets')+extract(mirror,'render_mirror_global_reset'))
  (d/'fade.inc').write_text(extract(mirror,'render_mirror_fade_start')+extract(mirror,'render_mirror_fade_step'))
  (d/'allocation.inc').write_text(extract(varz,'JE_setupExplosion'))
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
  only=d/'cash25-only';(only/'content').mkdir(parents=True)
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
 if(render_mirror_global_cash25_value(NULL,0,0,0,185,0,0)!=-1)return 2;
 render_mirror_cash25_value_allocated(0,36,0,0,0,true,false);render_mirror_cash25_value_initialized(0,36);
 render_mirror_global_reset();return 0;
}
""")
  off=shlex.split(os.environ.get('CC','cc'))+['-std=c99','-Wall','-Wextra','-Werror','-I'+str(d),'-I'+str(ROOT/'src'),str(d/'feature_off.c'),'-o',str(d/'feature_off')]
  subprocess.run(off,check=True,timeout=60,preexec_fn=limits)
  subprocess.run([str(d/'feature_off')],check=True,timeout=10,preexec_fn=limits)
  cmd=shlex.split(os.environ.get('CC','cc'))+['-std=c99','-O1','-g','-Wall','-Wextra','-Werror=implicit-function-declaration','-Wno-unused-function','-Wno-unused-variable','-Wno-unused-parameter','-Wno-misleading-indentation','-I'+str(d)]
  if a.sanitize:cmd+=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-no-pie']
  cmd+=[str(d/'global_cash25_reconstruction.c'),'-o',str(d/'observer')]
  c=subprocess.run(cmd,capture_output=True,text=True,timeout=120,preexec_fn=limits)
  if c.returncode: print(c.stdout+c.stderr);raise SystemExit(c.returncode)
  result=subprocess.run([str(d/'observer'),str(a.assets.resolve()),str(d)],input=payload,capture_output=True,timeout=240,preexec_fn=limits,env={**os.environ,'ASAN_OPTIONS':'detect_leaks=0:halt_on_error=1','UBSAN_OPTIONS':'halt_on_error=1:print_stacktrace=1'})
  out=result.stdout.decode();err=result.stderr.decode();print(out+err)
  accepted=(result.returncode!=0 and 'global_cash25_fault&&!global_cash25_finish_proof()' in err) if a.negative_control else result.returncode==0
  sources_unchanged=all(x.read_bytes()==b for x,b in snap.items())
  accepted=accepted and sources_unchanged
  report={'status':'PASS' if accepted else 'FAIL','negative_control':a.negative_control,'scope':'Extracted production Cash25BodyAndValue7 and Talon owner helpers, original allocation function; SDL shim and independent indexed-write emission, not native engine proof','returncode':result.returncode,'stdout':out,'stderr':err,'sanitizers':'ASan+UBSan' if a.sanitize else 'none','feature_off_header_compile_and_run':'PASS','original_bytes_persisted':False,'source_sha256':{str(x.relative_to(ROOT)):hashlib.sha256(b).hexdigest() for x,b in snap.items()},'sources_unchanged':sources_unchanged,'resources':{str(x['identity']):x['sha256'] for x in records}}
  a.receipt.parent.mkdir(parents=True,exist_ok=True);a.receipt.write_text(json.dumps(report,indent=2)+'\n');raise SystemExit(0 if accepted else 1)
if __name__=='__main__':main()
