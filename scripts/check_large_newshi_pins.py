#!/usr/bin/env python3
"""Read-only original NEWSHI record/tile/mask reproduction; emit no game data."""
import argparse,hashlib,json,io
from pathlib import Path
import numpy as np
from PIL import Image
from build_newshf_prototype_pins import decode,fnv64,IDENTITY,PALETTE_SHA256
import current_large_newshi_compatibility as c
ROOT=Path(__file__).resolve().parents[1]
HEADER_SHA256='eee067f7661123175f7e12053d244f99f3f0ee8e5308793b52ed83df4fd0bab5'
RECORDS=[(302, 187269, 'da1a30f9d80736139f9aadef0ad476ba4eabcb3811a12784ddf7b5a1d0298e95'), (303, 187346, '00fa2a5642a40580fb6684c1cb85f26e4b4244b0d03cdf75dd967578a954dc76'), (304, 187423, 'c262b51a92437dc0efa181887e8a38fa8ecf12a174cf618ca9c41330477e5aac'), (305, 187500, '37d50803b597a29f126ac8fc0f6614f38050184c3bf34963f5943c74afcfd963'), (306, 187577, 'eefb7f4dfcdcde1a0e730685f782fc769cdf9d7fab2342c225ed74cccc9bf429'), (307, 187654, '01344151ce437e0a24ae1902cd5752483e459ebba2b71c4c33af8fa302014e9e'), (308, 187731, 'e4c4a2f0649c664fc834d0747be3d8f575b3084aa1f3ccf81b292492212daad2')]
BANK_SHA256='226da9b33b9b16f7a4212b9cc785fbd82c9517172b3a15a7f58798a38b0a12e4'
def verify(root=ROOT,game_data=None):
 path=root/'src/newshi_large_pins.h'
 assert path.is_file() and not path.is_symlink(),'missing/unsafe NEWSHI pins'
 header=path.read_bytes();assert hashlib.sha256(header).hexdigest()==HEADER_SHA256,'immutable NEWSHI pins drift'
 bases=[p[1] for p in c.PARTS]+[268,270,272];tiles=sorted({b+q for b in bases for q in (0,1,19,20)})
 if game_data is not None:
  bank=(game_data/'newshi.shp').read_bytes();table=(game_data/'tyrian.hdt').read_bytes();pal=(game_data/'palette.dat').read_bytes()
  assert len(bank)==30860 and hashlib.sha256(bank).hexdigest()==BANK_SHA256
  assert hashlib.sha256(table).hexdigest()==IDENTITY['item_table_sha256']
  assert hashlib.sha256(pal).hexdigest()==PALETTE_SHA256
  text=header.decode();assert f'UINT64_C(0x{fnv64(bank):016x})' in text
  for record,offset,digest in RECORDS:
   raw=table[offset:offset+77];assert len(raw)==77 and hashlib.sha256(raw).hexdigest()==digest
   assert raw[63]==13 and f'UINT64_C(0x{fnv64(raw):016x})' in text
  for i in tiles:assert f'{{{i}u,UINT64_C(0x{fnv64(decode(bank,i)):016x})}}' in text
  rgb=np.array([(v<<2)|(v>>4) for v in pal[5*768:6*768]],dtype='uint8').reshape(256,3)
  originals={}
  for base in bases:
   a=np.zeros((28,24,4),dtype='uint8')
   for q,x,y in ((0,0,0),(1,12,0),(19,0,14),(20,12,14)):
    decoded=decode(bank,base+q);idx=np.frombuffer(decoded[:168],dtype='uint8').reshape(14,12);alpha=np.frombuffer(decoded[168:],dtype='uint8').reshape(14,12)
    a[y:y+14,x:x+12,:3]=rgb[idx];a[y:y+14,x:x+12,3]=alpha
   a[a[:,:,3]==0,:3]=0;originals[base]=a
  expected={f'native-mask-{b}.png':v[:,:,3]>0 for b,v in originals.items()}
  expected.update({f'normal-difference-{b}.png':np.any(originals[278]!=originals[b],axis=2) for b in (268,270,272)})
  expected.update({f'center-difference-{b}.png':np.any(originals[270]!=originals[b],axis=2) for b in (268,272)})
  whole=np.zeros((84,96),dtype=bool)
  for rec,base,x,y in c.PARTS:whole[y:y+28,x:x+24]=originals[base][:,:,3]>0
  expected['native-whole-mask.png']=whole
  for n,v in expected.items():
   raw=c.read(root,c.INPUT_ROOT+'/'+n);assert c.sha(raw)==c.MASK_PINS[n]
   assert np.array_equal(np.array(Image.open(io.BytesIO(raw)))>0,v),('original mask mismatch',n)
 return dict(status='PASS',header_sha256=HEADER_SHA256,records=list(range(302,309)),tiles=tiles,original_bytes_verified=game_data is not None)
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--game-data',type=Path);p.add_argument('--source-root',type=Path,default=ROOT);a=p.parse_args();print(json.dumps(verify(a.source_root,a.game_data),sort_keys=True))
