#!/usr/bin/env python3
"""Verify/rebuild frozen generated Sonic242/243 inverted-oblique pair. Never launches the game."""
from pathlib import Path
from PIL import Image,ImageOps
import argparse,hashlib,json,struct,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[1];ART='assets/hd/artwork/player-sonic-inverted-oblique-pair-v1'
CONTRACT='689bb3f873499b842063e99c2314aa5ec096b44e3214dca000a0dbbf11696774'
SHA=lambda b:hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path);a=p.parse_args();art=ROOT/ART;craw=(art/'contract.json').read_bytes();assert SHA(craw)==CONTRACT;c=json.loads(craw)
 assert SHA((ROOT/c['upstream_published_contract']['path']).read_bytes())==c['upstream_published_contract']['sha256'];assert SHA((art/c['source']).read_bytes())==c['source_sha256'];m=json.loads((ROOT/'assets/hd/manifest.json').read_text());defaults={m['default_preview_pack'],m['default_debug_pack']};images={}
 for e in c['entries']:
  i=e['id'];raw=(art/f'output/bullet-{i}-8.hda').read_bytes();png=(art/f'output/bullet-{i}-8.png').read_bytes();h=e['HDA_sha256'];assert len(raw)==43036 and raw[:28]==struct.pack('<4s6I',b'HDR1',80000+i,8,12,14,0,0)
  assert SHA(raw)==h and SHA(png)==e['PNG_sha256']and SHA(raw[28:])==e['RGBA_sha256'];im=Image.open(art/f'output/bullet-{i}-8.png');assert im.mode=='RGBA'and im.size==(96,112)and im.tobytes()==raw[28:];images[i]=im.copy()
  assert sum(0<v<255 for v in raw[31::4])==e['fractional_alpha_samples'];canonical=f'assets/hd/source/bullet-{i}-8-{h[:12]}.png';assert (ROOT/canonical).read_bytes()==png
  assert m['source_pngs'][h]=={'path':canonical,'sha256':SHA(png),'RGBA_sha256':SHA(raw[28:])}
  for name,pack in m['packs'].items():
   assert pack['count']==len(pack['files'])
   if name in defaults:
    assert pack['files'][f'bullet-{i}-8.hda']=={'header_u32':e['header_u32'],'sha256':h,'source_png':canonical,'source_png_sha256':SHA(png)};assert (ROOT/'assets/hd/packs'/name/f'bullet-{i}-8.hda').read_bytes()==raw
   else:assert f'bullet-{i}-8.hda'not in pack['files']
 family=m['player_sonic_inverted_oblique_pair_v1'];assert family['contract_sha256']==CONTRACT and family['ids']==[242,243]and family['entries']==[{'id':e['id'],'slot':e['slot'],'HDA_sha256':e['HDA_sha256']}for e in c['entries']]
 if a.output:subprocess.run([sys.executable,str(art/'rebuild.py'),'--output',str(a.output.absolute())],check=True)
 else:
  with tempfile.TemporaryDirectory(prefix='sonic-inverted-oblique-pair-rebuild-')as d:subprocess.run([sys.executable,str(art/'rebuild.py'),'--output',str(Path(d)/'rebuilt')],check=True)
 assert ImageOps.mirror(images[242]).tobytes()==images[243].tobytes()
 for upstream,new in [(223,242),(224,243)]:
  assert ImageOps.flip(Image.open(ROOT/f'assets/hd/artwork/player-sonic-oblique-pair-v1/output/bullet-{upstream}-8.png')).tobytes()==images[new].tobytes()
 assert all(not any(pic.tobytes()[(110*96)*4+3::4]) for pic in images.values())
 print('PASS Sonic242/243 generated-only master, proportional RGBA and exact whole-canvas flipY/flipX; canonicalPNG/HDA and both defaults; prior13 untouched, remaining6 original; game runs0')
if __name__=='__main__':main()
