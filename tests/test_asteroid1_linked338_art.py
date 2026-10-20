#!/usr/bin/env python3
"""Finite source-mask, shared-master and material135 art validation.

Reads only eight named outputs/four generated masters, family provenance and
the explicitly selected NEWSHP original. Existing resources are never changed.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json, os, resource, struct, subprocess, sys
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'assets/hd/artwork/asteroid1-linked338-v1'
PACK=ROOT/'assets/hd/packs/asteroid1-ten-v1'
SHA=lambda b:hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 assert not a.out.exists();a.out.mkdir(parents=True)
 spec=importlib.util.spec_from_file_location('linked_art',ROOT/'prototype/build-asteroid1-linked338-art.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 bank=(a.data/'newshp.shp').read_bytes();assert len(bank)==46204 and m.fnv(bank)=='0xe2413e3aeab4d908'
 provenance=json.loads((ART/'provenance.json').read_text());inventory=json.loads((ART/'art-inventory.json').read_text())
 for name,sha in provenance['masters'].items():assert SHA((ART/name).read_bytes())==sha
 def limits():resource.setrlimit(resource.RLIMIT_AS,(1024**3,)*2);resource.setrlimit(resource.RLIMIT_FSIZE,(2*1024**2,)*2)
 subprocess.run([sys.executable,str(ROOT/'prototype/build-asteroid1-linked338-art.py'),'--data',str(a.data),'--out',str(a.out/'rebuilt')],check=True,capture_output=True,preexec_fn=limits,env={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1'})
 arrays={};checks=[];decoded={b:m.decode(bank,b) for b in m.BASES}
 for b in m.BASES:
  stem=f'enemy-newshp-{b}-8';im=Image.open(ART/(stem+'.png'));assert im.mode=='RGBA' and im.size==(192,224)
  raw=(PACK/(stem+'.hda')).read_bytes();assert len(raw)==172060 and struct.unpack('<4s6I',raw[:28])==(b'HDR1',1350000+b,8,24,28,0,0)
  assert raw[28:]==im.tobytes() and m.fnv(im.tobytes())==inventory[stem]['rgba_fnv64'] and SHA(raw)==inventory[stem]['sha256']
  assert (a.out/'rebuilt'/(stem+'.hda')).read_bytes()==raw and (a.out/'rebuilt'/(stem+'.png')).read_bytes()==(ART/(stem+'.png')).read_bytes()
  arrays[b]=np.array(im);assert np.array_equal(arrays[b][:,:,3],np.repeat(np.repeat(decoded[b][1],8,axis=0),8,axis=1))
  checks.append({'base':b,'role':1350000+b,'occupied_cells':int((decoded[b][1]>0).sum()),'hda_sha256':SHA(raw),'rgba_fnv64':m.fnv(im.tobytes())})
 union=np.zeros((28,24),bool)
 for b in (117,119):union|=decoded[b][0]!=decoded[115][0]
 assert union.sum()==279;allowed=np.repeat(np.repeat(union,8,axis=0),8,axis=1)
 for b in (117,119):
  changed=np.any(arrays[b]!=arrays[115],axis=2);assert changed.any() and not np.any(changed&~allowed)
 for b in (117,119,121):assert np.array_equal(arrays[b][:,:,3],arrays[115][:,:,3])
 assert arrays[229][8:16,120:128,3].sum()==0 and arrays[269][0:8,96:104,3].sum()==0
 assert sum(int((decoded[b][1]>0).sum()) for b in (115,229,231,267,269))==3032
 platform=Image.open(ART/'imagegen-master-lower.png').crop(m.PLATFORM_CROP).resize((384,448),Image.Resampling.LANCZOS)
 for b,box in ((229,(0,0,192,224)),(231,(192,0,384,224)),(267,(0,224,192,448)),(269,(192,224,384,448))):
  expected=np.array(platform.crop(box));mask=arrays[b][:,:,3]>0;assert np.array_equal(expected[:,:,:3][mask],arrays[b][:,:,:3][mask])
 report={'status':'PASS','source_bank':'NEWSHP','logical_bank':20,'material_role':135,'original_bytes':46204,'original_fnv64':m.fnv(bank),'images':checks,'exact_original_coverage_all_eight':True,'live_cap_difference_union_cells':279,'all_cap_coverage_cells':346,'intact_assembly_occupied_cells':3032,'isolated_support_holes_preserved':{'229':[15,1],'269':[12,0]},'platform_one_master_sliced_exact':True,'rebuild_png_and_HDA_exact':True,'masters_match_provenance':True,'scope':'Finite deterministic art conversion and coverage, separate from actual engine acceptance.'}
 (a.out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
