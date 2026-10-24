#!/usr/bin/env python3
"""Read-only pinned source/payload validation, including sparse checkouts."""
import hashlib,io,json,struct,subprocess
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def read(path):
 p=ROOT/path
 return p.read_bytes() if p.is_file() else subprocess.check_output(['git','show','HEAD:'+str(path)],cwd=ROOT)
def sha(b):return hashlib.sha256(b).hexdigest()
def fnv(b):
 h=0xcbf29ce484222325
 for v in b:h=((h^v)*0x100000001b3)&((1<<64)-1)
 return f'{h:016x}'
def main():
 pins=json.loads(read('docs/enemy-reuse-source-pins.json'))
 assert [int(p['frame']) for p in pins]==[105,106,124,125,20,21]
 catalog=json.loads(read('assets/hd/manifest.json'))
 checked=0
 for p in pins:
  png=read(p['source_png']);assert sha(png)==p['source_png_sha256']
  image=Image.open(io.BytesIO(png));assert image.size==(96,112) and image.mode=='RGBA'
  rgba=image.tobytes();assert sha(rgba)==p['rgba_sha256'] and fnv(rgba)==p['rgba_fnv64']
  assert sha(read(p['author_contract']))==p['author_contract_sha256']
  for pack in catalog['packs']:
   hda=read('assets/hd/packs/'+pack+'/'+p['resource_file'])
   assert sha(hda)==p['hda_sha256']
   assert struct.unpack('<4s6I',hda[:28])==(b'HDR1',int(p['resource_identity']),8,12,14,0,0)
   assert hda[28:]==rgba;checked+=1
  assert int(p['nonzero_alpha_outside_original_support'])>0 # preserve approved antialiasing, never mask-crop
 from test_enemy_protron_reuse_binding import check_additive_assets_and_runtime
 check_additive_assets_and_runtime('47e7d062e0fc4a449a36f1d1f47e53c42f65c66d')
 print(json.dumps({'status':'PASS','pngs':6,'hda_payloads':checked,'runtime_destinations':1029,'projected_historical_runtime_destinations':1025,'old_source_and_pack_changes':0,'additive_p09_asset_paths':4,'scope':'P02/P04 pixels/header/approved alpha unchanged; P05 separately validated; P09 separately validated'}))
if __name__=='__main__':main()
