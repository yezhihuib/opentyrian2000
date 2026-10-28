#!/usr/bin/env python3
"""Read-only record170 identity reproduction. Original bytes never emitted."""
import argparse,hashlib,json
from pathlib import Path
from build_newshf_prototype_pins import decode,fnv64,IDENTITY,PALETTE_SHA256
ROOT=Path(__file__).resolve().parents[1]
HEADER_SHA256='c9b395397622179c2b8f3d5fa364d4e120ab6a447d2f88292e1887b6edda265e'
TILES=(15, 16, 34, 35, 53, 54, 72, 73, 91, 92, 110, 111)
def verify(root=ROOT,game_data=None):
 p=root/'src/newshf_aircraft170_pins.h'
 assert p.is_file() and not p.is_symlink(),'missing/unsafe aircraft170 pins'
 header=p.read_bytes();assert hashlib.sha256(header).hexdigest()==HEADER_SHA256,'immutable aircraft170 pins drift'
 if game_data is not None:
  bank=(game_data/'newshf.shp').read_bytes();table=(game_data/'tyrian.hdt').read_bytes();pal=(game_data/'palette.dat').read_bytes()
  assert hashlib.sha256(bank).hexdigest()==IDENTITY['bank_sha256']
  assert hashlib.sha256(table).hexdigest()==IDENTITY['item_table_sha256']
  assert hashlib.sha256(pal).hexdigest()==PALETTE_SHA256
  raw=table[177105:177182];assert len(raw)==77 and hashlib.sha256(raw).hexdigest()=='a748cb13a7cc08411b625a622a0818b5f95b987329db627760edb28d180c66a4'
  assert raw[0]==1 and raw[62]==0 and raw[63]==10
  assert [int.from_bytes(raw[21+i*2:23+i*2],'little') for i in range(3)]==[53,15,91]
  text=header.decode();assert f'UINT64_C(0x{fnv64(raw):016x})' in text
  for i in TILES:assert f'{{{i}u,UINT64_C(0x{fnv64(decode(bank,i)):016x})}}' in text
 return dict(status='PASS',header_sha256=HEADER_SHA256,records=[170],tiles=list(TILES),original_bytes_verified=game_data is not None)
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--game-data',type=Path);p.add_argument('--source-root',type=Path,default=ROOT);a=p.parse_args();print(json.dumps(verify(a.source_root,a.game_data),sort_keys=True))
