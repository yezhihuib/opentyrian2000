#!/usr/bin/env python3
"""Read-only exact shared-turret identity reproduction; no original bytes emitted."""
import argparse,hashlib,json
from pathlib import Path
from build_newshf_prototype_pins import decode,fnv64,IDENTITY,PALETTE_SHA256
ROOT=Path(__file__).resolve().parents[1]
HEADER_SHA256='23bbcbbe7b41073e1a60d2256042b5b89dfd48323e6500a2ade6b55d484c058c'
RECORDS=[(162,176489,'0d4dfa213ce709d8a4b0c58b448f502e434235d78b6fb07364af801f0d60980f'),(840,228695,'05024f85ecf5f225ed2c60f49a67ec0aacd0412f5a1eea2ef16dcbfce3227d62')]
def verify(root=ROOT,game_data=None):
 path=root/'src/newshf_turret_pins.h'
 assert path.is_file() and not path.is_symlink(),'missing/unsafe turret pins'
 header=path.read_bytes();assert hashlib.sha256(header).hexdigest()==HEADER_SHA256,'immutable turret pins drift'
 if game_data is not None:
  bank=(game_data/'newshf.shp').read_bytes();table=(game_data/'tyrian.hdt').read_bytes();pal=(game_data/'palette.dat').read_bytes()
  assert hashlib.sha256(bank).hexdigest()==IDENTITY['bank_sha256']
  assert hashlib.sha256(table).hexdigest()==IDENTITY['item_table_sha256']
  assert hashlib.sha256(pal).hexdigest()==PALETTE_SHA256
  text=header.decode()
  for record,offset,digest in RECORDS:
   raw=table[offset:offset+77];assert len(raw)==77 and hashlib.sha256(raw).hexdigest()==digest
   assert raw[0]==7 and raw[62]==2 and raw[63]==10
   assert [int.from_bytes(raw[21+i*2:23+i*2],'little') for i in range(7)]==[39,41,41,41,39,39,39]
   assert f'UINT64_C(0x{fnv64(raw):016x})' in text
  for i in (39,40,41,42,58,59,60,61):assert f'{{{i}u,UINT64_C(0x{fnv64(decode(bank,i)):016x})}}' in text
 return dict(status='PASS',header_sha256=HEADER_SHA256,records=[162,840],tiles=[39,40,41,42,58,59,60,61],original_bytes_verified=game_data is not None)
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--game-data',type=Path);p.add_argument('--source-root',type=Path,default=ROOT);a=p.parse_args();print(json.dumps(verify(a.source_root,a.game_data),sort_keys=True))
