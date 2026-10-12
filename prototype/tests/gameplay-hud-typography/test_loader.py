#!/usr/bin/env python3
from pathlib import Path
import argparse,os,re,struct,subprocess,tempfile
from test_fixed_contract import fnv,select,HEADER,PAYLOAD
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def fixture(path,source=None):
 source=source or bytes(i%253 for i in range(64000));palette=bytes(v for i in range(256) for v in (i*3%256,i*7%256,i*11%256))
 rgba=bytes(c for i in range(PAYLOAD//4) for c in (i*7%256,i//13%256,i//37%256,255))
 guards=[fnv(source),fnv(palette),fnv(select(source))]
 raw=HEADER.pack(b'HUT1',1,4,12,370,PAYLOAD,1,0,*guards,fnv(rgba))+rgba
 (path/'gameplay-hud-fixed-text-v1.hda').write_bytes(raw)
 (path/'source.bin').write_bytes(source);(path/'payload.bin').write_bytes(rgba)
 return guards,raw

def main():
 p=argparse.ArgumentParser();p.add_argument('--sanitize',action='store_true');a=p.parse_args()
 text=(ROOT/'src/gameplay_hud_fixed_text.c').read_text()
 for name,value in {'PIC3':0x14c1441f3d5dc0e2,'PALETTE':0x5e80e83992be2927,'SOURCE':0xb110512dd1fc63f4}.items():
  match=re.search(r'#define HUD_FIXED_'+name+r'_FNV UINT64_C\(0x([0-9a-f]+)\)',text)
  assert match and int(match[1],16)==value,('production guard drift',name)
 with tempfile.TemporaryDirectory(prefix='hut-loader-') as tmp:
  d=Path(tmp);guards,raw=fixture(d);bad=[b'',raw[:63],raw[:-1],raw+b'\0',raw*2]
  for offset in range(64):
   b=bytearray(raw);b[offset]^=1;bad.append(b)
  for alpha in range(255):
   b=bytearray(raw);b[67]=alpha;struct.pack_into('<Q',b,56,fnv(b[64:]));bad.append(b)
  b=bytearray(raw);b[-4]^=1;bad.append(b)
  for i,data in enumerate(bad):
   folder=d/('bad-%d'%i);folder.mkdir();(folder/'case').touch();(folder/'gameplay-hud-fixed-text-v1.hda').write_bytes(data)
  for kind in ('missing','directory','fifo'):
   folder=d/('bad-%d'%len(bad));folder.mkdir();(folder/'case').touch();name=folder/'gameplay-hud-fixed-text-v1.hda'
   if kind=='directory':name.mkdir()
   if kind=='fifo':os.mkfifo(name)
   bad.append(None)
  flags=['-DHUD_FIXED_'+k+'_FNV=UINT64_C(0x%016x)'%v for k,v in zip(('PIC3','PALETTE','SOURCE'),guards)]
  cmd=[os.environ.get('CC','cc'),'-std=c99','-O1','-g','-Wall','-Wextra','-Werror','-I'+str(ROOT/'src')]+flags+[str(HERE/'test_loader.c'),str(ROOT/'src/gameplay_hud_fixed_text.c'),'-o',str(d/'test')]
  if a.sanitize:cmd+=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-no-pie']
  env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1')
  subprocess.run(cmd,check=True);subprocess.run([str(d/'test'),str(d)],check=True,env=env)
  common=[os.environ.get('CC','cc'),'-std=c99','-O1','-g','-Wall','-Wextra','-Werror','-I'+str(ROOT/'src')]
  if a.sanitize:common+=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-no-pie']
  for production in (False,True):
   defs=[] if production else flags
   probes=['-D'+name+'=fixed_test_'+name for name in ('malloc','free','open','read','fstat','close')]
   subprocess.run(common+defs+probes+['-c',str(ROOT/'src/gameplay_hud_fixed_text.c'),'-o',str(d/'io.o')],check=True)
   subprocess.run(common+[str(HERE/'test_loader_io.c'),str(d/'io.o'),'-o',str(d/'io')],check=True)
   subprocess.run([str(d/'io'),str(d)]+(['production'] if production else []),check=True,env=env)
if __name__=='__main__':main()
