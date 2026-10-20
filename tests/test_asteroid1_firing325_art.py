#!/usr/bin/env python3
"""Finite reproducible source-bound NEWSHS record325 artwork regression.

Reads three named imagegen masters, their three PNG/HDA outputs, this family's
provenance and explicitly supplied original newshs.shp. No repository scan or
private projection. Outputs stay below 2MiB; no original data is modified.
"""
from pathlib import Path
import argparse, hashlib, json, os, resource, struct, subprocess, sys
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'assets/hd/artwork/asteroid1-firing325-v1'
PACK=ROOT/'assets/hd/packs/asteroid1-ten-v1'
SHA=lambda raw:hashlib.sha256(raw).hexdigest()
def fnv(raw):
 h=0xcbf29ce484222325
 for v in raw:h=((h^v)*0x100000001b3)&0xffffffffffffffff
 return f'0x{h:016x}'
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 assert not a.out.exists();a.out.mkdir(parents=True)
 source=(a.data/'newshs.shp').read_bytes();assert len(source)==46566 and fnv(source)=='0xf22ec1295ced5d11'
 provenance=json.loads((ART/'provenance.json').read_text());inventory=json.loads((ART/'art-inventory.json').read_text())
 for name,expected in provenance['masters'].items():assert SHA((ART/name).read_bytes())==expected
 def limits():resource.setrlimit(resource.RLIMIT_AS,(1024**3,)*2);resource.setrlimit(resource.RLIMIT_FSIZE,(2*1024**2,)*2)
 rebuilt=a.out/'rebuilt';subprocess.run([sys.executable,str(ROOT/'prototype/build-asteroid1-firing325-art.py'),'--data',str(a.data),'--out',str(rebuilt)],check=True,capture_output=True,preexec_fn=limits,env={**os.environ,"OPENBLAS_NUM_THREADS":"1","OMP_NUM_THREADS":"1"})
 arrays={};checks=[]
 for base in [11,125,277]:
  stem=f'enemy-newshs-{base}-8';im=Image.open(ART/(stem+'.png'));assert im.mode=='RGBA' and im.size==(192,224)
  raw=(PACK/(stem+'.hda')).read_bytes();assert len(raw)==172060 and struct.unpack('<4s6I',raw[:28])==(b'HDR1',1080000+base,8,24,28,0,0)
  assert raw[28:]==im.tobytes() and fnv(im.tobytes())==inventory[stem]['rgba_fnv64'] and SHA(raw)==inventory[stem]['sha256']
  assert (rebuilt/(stem+'.hda')).read_bytes()==raw and (rebuilt/(stem+'.png')).read_bytes()==(ART/(stem+'.png')).read_bytes()
  arrays[base]=np.array(im);assert np.all(arrays[base][:,:,3]==255);checks.append({'base':base,'hda_sha256':SHA(raw),'rgba_fnv64':fnv(im.tobytes())})
 allowed=np.zeros((224,192),bool);allowed[16:48,72:128]=True
 for x,y in [(11,125),(11,277),(125,277)]:
  diff=np.any(arrays[x]!=arrays[y],axis=2);assert np.any(diff) and not np.any(diff&~allowed)
 lamp={b:arrays[b][16:48,72:128,:3].mean(axis=(0,1))for b in arrays}
 assert lamp[125][1]>lamp[277][1] and lamp[11].max()-lamp[11].min()<5
 assert lamp[125][1]>2*max(lamp[125][0],lamp[125][2]) and lamp[277][1]>2*max(lamp[277][0],lamp[277][2])
 report={'status':'PASS','source_bank':'NEWSHS','logical_bank':23,'original_bytes':46566,'original_fnv64':fnv(source),'roles':[1080011,1080125,1080277],'images':checks,'occupied_logical_cells_per_image':672,'state_difference_region':[9,2,7,4],'shared_housing_outside_state_region_exact':True,'rebuild_png_and_HDA_exact':True,'masters_match_provenance':True,'scope':'Finite art conversion only; real engine and original firing acceptance are separate.'}
 (a.out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
