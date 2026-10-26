#!/usr/bin/env python3
"""Read-only exact shared-dualmissile identity reproduction; no original bytes emitted."""
import argparse,hashlib,json
from pathlib import Path
from build_newshf_prototype_pins import decode,fnv64,IDENTITY,PALETTE_SHA256
ROOT=Path(__file__).resolve().parents[1]
HEADER_SHA256='28b70229016267cdb9e5156c94a2d4f8ea23773027f04970781283843e0544ff'
RECORDS=[(2,164169,'1b2fce7aca1f55944af75b2a9805a87b1275a572403a6de40f52b48c759d2bb1'),(500,202515,'143b7eab6201367563b0e748c185cd4d6dbf505cfe367cb5277b31363932e1ca')]
def verify(root=ROOT,game_data=None):
 path=root/'src/newshf_dualmissile_pins.h'
 assert path.is_file() and not path.is_symlink(),'missing/unsafe dualmissile pins'
 header=path.read_bytes();assert hashlib.sha256(header).hexdigest()==HEADER_SHA256,'immutable dualmissile pins drift'
 if game_data is not None:
  bank=(game_data/'newshf.shp').read_bytes();table=(game_data/'tyrian.hdt').read_bytes();pal=(game_data/'palette.dat').read_bytes()
  assert hashlib.sha256(bank).hexdigest()==IDENTITY['bank_sha256']
  assert hashlib.sha256(table).hexdigest()==IDENTITY['item_table_sha256']
  assert hashlib.sha256(pal).hexdigest()==PALETTE_SHA256
  text=header.decode()
  for record,offset,digest in RECORDS:
   raw=table[offset:offset+77];assert len(raw)==77 and hashlib.sha256(raw).hexdigest()==digest
   assert raw[0]==1 and raw[62]==0 and raw[63]==10
   assert int.from_bytes(raw[21:23],'little')==169
   assert f'UINT64_C(0x{fnv64(raw):016x})' in text
  for i in (169,170,188,189):assert f'{{{i}u,UINT64_C(0x{fnv64(decode(bank,i)):016x})}}' in text
  assert decode(bank,169)==decode(bank,170) and decode(bank,188)==decode(bank,189)
 return dict(status='PASS',header_sha256=HEADER_SHA256,records=[2,500],tiles=[169,170,188,189],original_bytes_verified=game_data is not None)
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--game-data',type=Path);p.add_argument('--source-root',type=Path,default=ROOT);a=p.parse_args();print(json.dumps(verify(a.source_root,a.game_data),sort_keys=True))
