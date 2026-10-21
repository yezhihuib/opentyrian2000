#!/usr/bin/env python3
"""Focused current-production green renderer test; native identity proved separately."""
import argparse,hashlib,json,os,resource,shlex,struct,subprocess,tempfile
from pathlib import Path
from global_talon_reconstruction import extract,fnv64,reference_decode
ROOT=Path(__file__).resolve().parents[1];HERE=Path(__file__).resolve().parent

def limits():
 resource.setrlimit(resource.RLIMIT_CORE,(0,0));resource.setrlimit(resource.RLIMIT_CPU,(240,240))
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--data',type=Path,required=True);p.add_argument('--assets',type=Path,default=ROOT/'assets/hd/global-assets-v1');p.add_argument('--receipt',type=Path,required=True);p.add_argument('--sanitize',action='store_true');p.add_argument('--negative-control',action='store_true');a=p.parse_args()
 j=json.loads((a.assets/'registry.json').read_text());
 shape=(a.data/'tyrian.shp').read_bytes();off=struct.unpack_from('<13I',shape,2);banks=[shape[off[7]:off[8]],(a.data/'newsh6.shp').read_bytes()]
 assert list(map(len,banks))==[32060,17810]
 raw=(a.data/'palette.dat').read_bytes()[5*768:6*768];rgb=bytes((v<<2)|(v>>4) for v in raw)
 payload=b''.join(struct.pack('<I',len(b))+b for b in banks)+b''.join(struct.pack('<I',int.from_bytes(rgb[n:n+3],'big')) for n in range(0,768,3))
 f=next(f for f in j['families'] if f['name']=='green-energy-head-and-trail');ids=set(f['resources']);records=[r for r in j['resources'] if r['identity'] in ids];assert len(records)==11
 for source,bank in zip(['head_source','smoke_source'],banks):
  for t in f['source_identity'][source]['tiles']:assert fnv64(reference_decode(bank,t['index']))==int(t['source_fnv64'],16)
 for r in records:
  b=(a.assets/r['path']).read_bytes();assert len(b)==43036 and hashlib.sha256(b).hexdigest()==r['sha256'];assert fnv64(b[28:])==int(r['payload_fnv64'],16)
 paths=[ROOT/'src'/n for n in ['render_mirror.c','global_talon_mirror.inc','global_green_mirror.inc','global_asset_registry.h','shared_asset_reader.h']]+[HERE/('global_green_reconstruction'+e) for e in ['.c','.py','.md']]
 snap={p:p.read_bytes() for p in paths};mirror=snap[ROOT/'src/render_mirror.c'].decode()
 with tempfile.TemporaryDirectory(prefix='green-renderer-test-') as tmp:
  d=Path(tmp)
  for p,b in snap.items():
   if p.suffix in ['.c','.h','.inc']:(d/p.name).write_bytes(b)
  (d/'primitives.inc').write_text('\n'.join(extract(mirror,n) for n in ['palette_rgb','blend_rgba','decode_tile','explosion_asset_blend_rgba','green_background_snapshot','green_background_peak','green_head_composite']))
  (d/'resource.inc').write_text('#include \"shared_asset_reader.h\"\n'+'\n'.join(extract(snap[ROOT/'src/global_talon_mirror.inc'].decode(),n) for n in ['global_bytes_hash','global_resource_load']))
  (d/'global_green_identity.inc').write_text('''static bool global_green_identity_fault;
static bool global_green_identity_records_match(void){return true;}
static void global_green_identity_reset(void){global_green_identity_fault=false;}
static void global_green_identity_frame_begin(void){}
static bool global_green_identity_complete(void){return true;}
static bool global_green_trail_identity(int x,int y,int d,int t,bool f,bool p){return true;}
static int global_green_head_identity(unsigned s,unsigned r,unsigned i,int x,int y,int st){return 1;}
''')
  if a.negative_control:
   p=d/'global_green_mirror.inc';s=p.read_text();start=s.index(' if(global_green_contributed&&(',s.index('static void global_green_preflight'));end=s.index('global_green_fail();',start)+len('global_green_fail();');p.write_text(s[:start]+s[end:])
  for n,r in enumerate(records):
   for mode in ['missing','corrupt','header','trailing']:
    base=d/(mode+str(n));(base/'content').mkdir(parents=True)
    for other in records:
     target=base/other['path']
     if other is not r:target.symlink_to((a.assets/other['path']).resolve())
     elif mode!='missing':
      b=bytearray((a.assets/other['path']).read_bytes())
      if mode=='corrupt':b[31]^=1
      if mode=='header':b[4]^=1
      if mode=='trailing':b+=b'!'
      target.write_bytes(b)
  cmd=shlex.split(os.environ.get('CC','cc'))+['-std=c99','-O1','-g','-Wall','-Wextra','-Werror=implicit-function-declaration','-Wno-unused-function','-Wno-unused-variable','-Wno-unused-parameter','-Wno-misleading-indentation','-I'+str(d)]
  if a.sanitize:cmd+=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-no-pie']
  c=subprocess.run(cmd+[str(d/'global_green_reconstruction.c'),'-o',str(d/'observer')],capture_output=True,text=True,timeout=120,preexec_fn=limits)
  if c.returncode:print(c.stdout+c.stderr);raise SystemExit(c.returncode)
  result=subprocess.run([str(d/'observer'),str(a.assets.resolve()),str(d)],input=payload,capture_output=True,timeout=240,preexec_fn=limits,env={**os.environ,'ASAN_OPTIONS':'detect_leaks=0:halt_on_error=1','UBSAN_OPTIONS':'halt_on_error=1:print_stacktrace=1'})
  out=result.stdout.decode();err=result.stderr.decode();print(out+err)
  accepted=(result.returncode!=0 and 'global_green_fault&&!global_green_finish_proof()' in err) if a.negative_control else result.returncode==0
  unchanged=all(p.read_bytes()==b for p,b in snap.items());accepted=accepted and unchanged
  report={'status':'PASS' if accepted else 'FAIL','negative_control':a.negative_control,'scope':'Production green combined renderer with independent RGBA oracle; identity stubbed, native identity tested separately','returncode':result.returncode,'stdout':out,'stderr':err,'sanitizers':'ASan+UBSan' if a.sanitize else 'none','original_bytes_persisted':False,'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(b).hexdigest() for p,b in snap.items()},'sources_unchanged':unchanged,'resources':{str(r['identity']):r['sha256'] for r in records}}
  a.receipt.parent.mkdir(parents=True,exist_ok=True);a.receipt.write_text(json.dumps(report,indent=2)+'\n');raise SystemExit(0 if accepted else 1)
if __name__=='__main__':main()
