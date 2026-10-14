#!/usr/bin/env python3
"""Validate/rebuild the one frozen generated Marlo body. Never runs the game."""
from pathlib import Path
from PIL import Image
import argparse,hashlib,json,struct,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
ART='assets/hd/artwork/option-marlo152-one-v1'
SHA=lambda b:hashlib.sha256(b).hexdigest()
CONTRACT='f011ddecc962cba60ff2139a17cb52a9aa8de3e131002a2cb6952b951675fa6f'
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path);a=p.parse_args();art=ROOT/ART;craw=(art/'contract.json').read_bytes();assert SHA(craw)==CONTRACT;c=json.loads(craw)
 assert SHA((art/c['source']).read_bytes())==c['source_sha256']
 raw=(art/'output/option-marlo-bank9-152-8.hda').read_bytes();png=(art/'output/option-marlo-bank9-152-8.png').read_bytes();assert len(raw)==43036 and raw[:28]==struct.pack('<4s6I',b'HDR1',1260152,8,12,14,0,0)
 assert SHA(raw)==c['HDA_sha256'] and SHA(png)==c['PNG_sha256'] and SHA(raw[28:])==c['RGBA_sha256']
 im=Image.open(art/'output/option-marlo-bank9-152-8.png');assert im.mode=='RGBA'and im.size==(96,112)and im.tobytes()==raw[28:]
 assert sum(0<x<255 for x in raw[31::4])==c['metrics']['fractional_alpha_pixels']==2935
 m=json.loads((ROOT/'assets/hd/manifest.json').read_text());h=SHA(raw);canonical=f'assets/hd/source/option-marlo-bank9-152-8-{h[:12]}.png';assert (ROOT/canonical).read_bytes()==png
 assert m['source_pngs'][h]=={'path':canonical,'sha256':SHA(png),'RGBA_sha256':SHA(raw[28:])}
 defaults={m['default_preview_pack'],m['default_debug_pack']}
 for name,pack in m['packs'].items():
  assert pack['count']==len(pack['files'])
  if name in defaults:
   assert pack['files']['option-marlo-bank9-152-8.hda']=={'header_u32':[1260152,8,12,14,0,0],'sha256':h,'source_png':canonical,'source_png_sha256':SHA(png)}
   assert (ROOT/'assets/hd/packs'/name/'option-marlo-bank9-152-8.hda').read_bytes()==raw
  else:assert 'option-marlo-bank9-152-8.hda'not in pack['files']
 assert m['option_marlo152_one_v1']['contract_sha256']==CONTRACT and m['option_marlo152_one_v1']['entries']==[{'id':152,'slot':536,'HDA_sha256':h}]
 if a.output:subprocess.run([sys.executable,str(art/'rebuild.py'),'--output',str(a.output.absolute())],check=True)
 else:
  with tempfile.TemporaryDirectory(prefix='marlo152-rebuild-')as d:subprocess.run([sys.executable,str(art/'rebuild.py'),'--output',str(Path(d)/'output')],check=True)
 print('PASS frozen generated master, original RGBA, exact canonical PNG/HDA, both default manifest bindings; game runs0')
if __name__=='__main__':main()
