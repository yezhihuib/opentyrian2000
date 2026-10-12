#!/usr/bin/env python3
"""Read-only frozen HUM2/resource check; never copies art or original data."""
import argparse,hashlib,json,os,struct,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
SHA='3f8d9c35a3a9791d554a3c46f3431289c8ecd68b57419747ce3a40c225dafa4c'
def fnv(b):
 h=14695981039346656037
 for x in b:h=((h^x)*1099511628211)&((1<<64)-1)
 return h

def main():
 p=argparse.ArgumentParser();p.add_argument('--resource',type=Path,required=True);a=p.parse_args();f=a.resource.resolve();raw=f.read_bytes()
 assert len(raw)==621920 and hashlib.sha256(raw).hexdigest()==SHA
 h=struct.unpack('<4s11I8Q',raw[:112]);assert h[:12]==(b'HUM2',2,112,4,320,200,4224,51840,120832,444912,944,222456)
 pins=[int(x,16) for x in ('14c1441f3d5dc0e2','5e80e83992be2927','92ce2a65c65f67db','33f13810daec0125','c4231771a5413868','1d129d23c2edc134','fcc77c108870c9db')];assert list(h[12:])==pins+[0]
 data=raw[112:];sections=[data[:4224],data[4224:56064],data[56064:176896],data[176896:]]
 assert [fnv(b) for b in sections]+[fnv(data)]==pins[2:]
 assert all(a==255 for a in data[:176896][3::4]);lookup=struct.unpack('<222456H',sections[3]);assert min(lookup)==0 and max(lookup)==943
 hashes=json.loads((f.parent/'all-generator-run-material-hashes.json').read_text());assert len(hashes)==1196
 entry=0
 for spec in hashes:
  i=spec['palette_role'];height=spec['logical_run_height'];assert entry==(i-113)*17112+2*height*(height-1)
  material=b''.join(sections[2][128*r:128*(r+1)] for r in lookup[entry:entry+4*height]);entry+=4*height
  assert hashlib.sha256(material).hexdigest()==spec['sha256']
 assert entry==222456
 tiles=json.loads((f.parent/'tile-layout.json').read_text());assert len(tiles['firepower'])==11 and len(tiles['armor'])==29
 for key,section in zip(('firepower','armor'),sections[:2]):
  for tile in tiles[key]:
   b=section[tile['rgba_offset_bytes']:tile['rgba_offset_bytes']+tile['rgba_bytes']]
   assert len(b)==tile['width']*tile['height']*4 and hashlib.sha256(b).hexdigest()==tile['rgba_sha256']
 with tempfile.TemporaryDirectory(prefix='hum2-frozen-loader-') as t:
  c=Path(t)/'test.c';c.write_text('#include <assert.h>\n#include "gameplay_hud_meters.h"\nint main(int argc,char **argv){assert(argc==2);assert(hud_meters_load(argv[1]));assert(!hud_meters_ready());hud_meters_shutdown();return 0;}\n')
  subprocess.run([os.environ.get('CC','cc'),'-std=c99','-Wall','-Wextra','-Werror','-I'+str(ROOT/'src'),str(c),str(ROOT/'src/gameplay_hud_meters.c'),'-o',t+'/test'],check=True)
  subprocess.run([t+'/test',str(f.parent)],check=True)
 print(json.dumps({'status':'PASS','resource_sha256':SHA,'file_bytes':621920,'payload_bytes':621808,'canonical_tiles':40,'generator_spans':1196,'production_loader_with_default_pins':True,'original_data_or_art_copies':0}))
if __name__=='__main__':main()
