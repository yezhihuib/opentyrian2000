"""Rebuild selected generated cloud art in a NEW external directory.

Requires ImageMagick7, GEGL0.4 Python bindings, Pillow, C++17 and external legal
Tyrian2000 data for original opacity geometry only. No original RGB is copied.
"""
from pathlib import Path
import argparse,hashlib,json,os,shutil,subprocess,sys
from PIL import Image
repo=Path(__file__).resolve().parents[1];art=repo/'assets/hd/artwork/cloud-layer2-v1'
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--data',type=Path,required=True);a=p.parse_args();out=a.output.resolve()
if out.exists():p.error('Choose a new output directory')
if out==repo or repo in out.parents:p.error('Keep rebuild outputs outside the production checkout')
shutil.copytree(art,out);env=dict(os.environ,TYRIAN_DATA_DIR=str(a.data.resolve()))
subprocess.run(['bash',str(out/'rebuild-selected.sh')],env=env,check=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
for e in json.loads((art/'selected-manifest.json').read_text())['assets']:
 assert sha((out/'runtime-overlay'/e['hda']).read_bytes())==e['sha256'],e['id']
 # ImageMagick PNG timestamps/encoding may differ; decoded authored RGBA may not.
 assert sha((repo/e['source_png']).read_bytes())==e['png_sha256'],e['id']
 rebuilt=Image.open(out/'output'/e['png']);formal=Image.open(repo/e['source_png'])
 assert rebuilt.mode==formal.mode=='RGBA' and rebuilt.size==formal.size==(192,224),e['id']
 assert rebuilt.tobytes()==formal.tobytes(),e['id']
# Preserve the exact v2 rebuild above, then apply the independently authored64 addendum.
correction=out/'cloud64-v3-rebuild'
subprocess.run([sys.executable,str(repo/'prototype/build-cloud64-art.py'),'--output',str(correction)],check=True)
for folder,extension in [('output','png'),('runtime-overlay','hda')]:
 shutil.copy2(correction/folder/f'terrain-shapesz-64-8.{extension}',out/folder/f'terrain-shapesz-64-8.{extension}')
manifest=json.loads((repo/'assets/hd/manifest.json').read_text());current=manifest['packs'][manifest['default_debug_pack']]['files']
for i in manifest['cloud_layer2_v1']['ids']:
 name=f'terrain-shapesz-{i}-8.hda';assert sha((out/'runtime-overlay'/name).read_bytes())==current[name]['sha256']
print('PASS: all15 current cloud RGBA/HDR1 reproduced; accepted55 retained and cloud64 v3 applied.')
