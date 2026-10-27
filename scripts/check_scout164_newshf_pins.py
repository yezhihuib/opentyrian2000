#!/usr/bin/env python3
"""Read-only record164 identity reproduction. Original bytes never emitted."""
import argparse,hashlib,json
from pathlib import Path
from build_newshf_prototype_pins import decode,fnv64,IDENTITY,PALETTE_SHA256
ROOT=Path(__file__).resolve().parents[1]
HEADER_SHA256='998ecaa3fbbf70891be5ca871f51adbf149fa45dc0ae477fccbde175d238ea5a'
TILES=(9,10,11,12,13,14,28,29,30,31,32,33)
def verify(root=ROOT,game_data=None):
 p=root/'src/newshf_scout164_pins.h'
 assert p.is_file() and not p.is_symlink(),'missing/unsafe scout164 pins'
 header=p.read_bytes();assert hashlib.sha256(header).hexdigest()==HEADER_SHA256,'immutable scout164 pins drift'
 if game_data is not None:
  bank=(game_data/'newshf.shp').read_bytes();table=(game_data/'tyrian.hdt').read_bytes();pal=(game_data/'palette.dat').read_bytes()
  assert hashlib.sha256(bank).hexdigest()==IDENTITY['bank_sha256']
  assert hashlib.sha256(table).hexdigest()==IDENTITY['item_table_sha256']
  assert hashlib.sha256(pal).hexdigest()==PALETTE_SHA256
  raw=table[176643:176720];assert len(raw)==77 and hashlib.sha256(raw).hexdigest()=='14a77c8eecdd93b62d70481e580f3fe81f0b2dfc25aaeee908721c197dc81fb1'
  assert raw[0]==1 and raw[62]==0 and raw[63]==10
  assert [int.from_bytes(raw[21+i*2:23+i*2],'little') for i in range(3)]==[11,9,13]
  text=header.decode();assert f'UINT64_C(0x{fnv64(raw):016x})' in text
  for i in TILES:assert f'{{{i}u,UINT64_C(0x{fnv64(decode(bank,i)):016x})}}' in text
 return dict(status='PASS',header_sha256=HEADER_SHA256,records=[164],tiles=list(TILES),original_bytes_verified=game_data is not None)
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--game-data',type=Path);p.add_argument('--source-root',type=Path,default=ROOT);a=p.parse_args();print(json.dumps(verify(a.source_root,a.game_data),sort_keys=True))
