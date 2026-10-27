#!/usr/bin/env python3
"""Read-only record165 identity reproduction. Original bytes never emitted."""
import argparse,hashlib,json
from pathlib import Path
from build_newshf_prototype_pins import decode,fnv64,IDENTITY,PALETTE_SHA256
ROOT=Path(__file__).resolve().parents[1]
HEADER_SHA256='10d020b1821231167abf5d6e7942dc257811ccc33de726e2818fd5996de37ddf'
TILES=(47, 48, 49, 50, 51, 52, 66, 67, 68, 69, 70, 71)
def verify(root=ROOT,game_data=None):
 p=root/'src/newshf_fighter165_pins.h'
 assert p.is_file() and not p.is_symlink(),'missing/unsafe fighter165 pins'
 header=p.read_bytes();assert hashlib.sha256(header).hexdigest()==HEADER_SHA256,'immutable fighter165 pins drift'
 if game_data is not None:
  bank=(game_data/'newshf.shp').read_bytes();table=(game_data/'tyrian.hdt').read_bytes();pal=(game_data/'palette.dat').read_bytes()
  assert hashlib.sha256(bank).hexdigest()==IDENTITY['bank_sha256']
  assert hashlib.sha256(table).hexdigest()==IDENTITY['item_table_sha256']
  assert hashlib.sha256(pal).hexdigest()==PALETTE_SHA256
  raw=table[176720:176797];assert len(raw)==77 and hashlib.sha256(raw).hexdigest()=='ac72171e76617805661f09b6544e0aed7eb107e6385b59ad9111d9af7124588f'
  assert raw[0]==1 and raw[62]==0 and raw[63]==10
  assert [int.from_bytes(raw[21+i*2:23+i*2],'little') for i in range(3)]==[49,47,51]
  text=header.decode();assert f'UINT64_C(0x{fnv64(raw):016x})' in text
  for i in TILES:assert f'{{{i}u,UINT64_C(0x{fnv64(decode(bank,i)):016x})}}' in text
 return dict(status='PASS',header_sha256=HEADER_SHA256,records=[165],tiles=list(TILES),original_bytes_verified=game_data is not None)
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--game-data',type=Path);p.add_argument('--source-root',type=Path,default=ROOT);a=p.parse_args();print(json.dumps(verify(a.source_root,a.game_data),sort_keys=True))
