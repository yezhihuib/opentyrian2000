#!/usr/bin/env python3
"""Read-only linked identity reproduction; originals stay private."""
import argparse,hashlib,json
from pathlib import Path
from build_newshf_prototype_pins import decode,fnv64,IDENTITY,PALETTE_SHA256
ROOT=Path(__file__).resolve().parents[1]
HEADER_SHA256='4a6876272e9a1b3a25733fb7e566d06be918f8f7b2054d5b196e9c797a0fdaf1'
RECORDS=[(177182, '98046192d08960aeee594a5f9d127e0b097b7e7e49456ba1e3206b5c9294d602'), (177259, '082604553fac787b53239624ab6004511cfa314df637bed98567703114f19ad6'), (177336, '03c1c7ae23f319c4618e10164e32c5b4f61063daddd6b0e51b45e5804bf7c9bf')]
def verify(root=ROOT,game_data=None):
 path=root/'src/newshf_linked_pins.h'
 assert path.is_file() and not path.is_symlink(),'missing/unsafe linked pins'
 header=path.read_bytes()
 assert hashlib.sha256(header).hexdigest()==HEADER_SHA256,'immutable linked pins drift'
 if game_data is not None:
  bank=(game_data/'newshf.shp').read_bytes();table=(game_data/'tyrian.hdt').read_bytes();pal=(game_data/'palette.dat').read_bytes()
  assert hashlib.sha256(bank).hexdigest()==IDENTITY['bank_sha256']
  assert hashlib.sha256(table).hexdigest()==IDENTITY['item_table_sha256']
  assert hashlib.sha256(pal).hexdigest()==PALETTE_SHA256
  text=header.decode()
  for offset,digest in RECORDS:
   raw=table[offset:offset+77];assert len(raw)==77 and hashlib.sha256(raw).hexdigest()==digest
   assert f'UINT64_C(0x{fnv64(raw):016x})' in text
  for i in sorted({b+q for b in [43,45,81,83,119,121] for q in [0,1,19,20]}):
   assert f'{{{i}u,UINT64_C(0x{fnv64(decode(bank,i)):016x})}}' in text
 return dict(status='PASS',header_sha256=HEADER_SHA256,original_bytes_verified=game_data is not None)
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--game-data',type=Path);p.add_argument('--source-root',type=Path,default=ROOT);a=p.parse_args();print(json.dumps(verify(a.source_root,a.game_data),sort_keys=True))
