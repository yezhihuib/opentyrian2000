"""Rebuild nine roads from generated crops and frozen accepted HD neighbors."""
from pathlib import Path
import argparse,hashlib,json,os,shutil,subprocess,struct
from PIL import Image
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();repo=Path(__file__).resolve().parents[1];src=repo/'assets/hd/artwork/road-nine-v2';out=a.output.resolve();assert not a.output.is_symlink() and not out.exists() and out!=repo and repo not in out.parents
shutil.copytree(src,out/'source-package');m=json.loads((repo/'assets/hd/manifest.json').read_text());# Preserve the immutable road recipe's historical neighbors after sand refresh.
historical=out/'historical-base';historical.mkdir();refresh=repo/'assets/hd/artwork/sand-road-grass21-v1';headers=json.loads((refresh/'headers.json').read_text());contract=json.loads((src/'source/rebuild-contract.json').read_text())
for identity,expected in contract['frozen_hda'].items():
 name=f'terrain-shapesz-{identity}-8'
 if int(identity) in (37,49,50,57):
  raw=b'HDR1'+struct.pack('<6I',*headers[name])+Image.open(refresh/'source/accepted'/f'{name}.png').convert('RGBA').tobytes()
 else:raw=(repo/'assets/hd/packs'/m['default_debug_pack']/f'{name}.hda').read_bytes()
 assert hashlib.sha256(raw).hexdigest()==expected, name
 (historical/f'{name}.hda').write_bytes(raw)
env=dict(os.environ,TYRIAN_HD_BASE_PACK=str(historical));subprocess.run(['bash',str(out/'source-package/rebuild-selected.sh'),str(out/'rebuilt')],check=True,env=env)
for e in json.loads((src/'selected-manifest.json').read_text()):
 name=f"terrain-shapesz-{e['id']}-8";raw=(out/'rebuilt/runtime-overlay'/f'{name}.hda').read_bytes();assert hashlib.sha256(raw).hexdigest()==e['sha256'];assert Image.open(out/'rebuilt/output'/f'{name}.png').tobytes()==Image.open(repo/e['source_png']).tobytes();assert hashlib.sha256((repo/e['source_png']).read_bytes()).hexdigest()==e['source_png_sha256']
print('Verified all9 selected HDA/RGBA bytes and committed PNG hashes; no original game data required.')
