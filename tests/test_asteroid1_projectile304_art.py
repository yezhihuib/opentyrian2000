#!/usr/bin/env python3
"""Exact source304 mask, payload and reproducible imagegen registration."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,subprocess,sys
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1];A=R/'assets/hd/artwork/asteroid1-projectile304-v1'
def main():
 p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();assert not a.out.exists();a.out.mkdir(parents=True)
 spec=importlib.util.spec_from_file_location('art304',R/'prototype/build-asteroid1-projectile304-art.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 bank,mask,indices=m.decode(a.data);inv=json.loads((A/'art-inventory.json').read_text());prov=json.loads((A/'provenance.json').read_text());assert hashlib.sha256((A/'imagegen-master.png').read_bytes()).hexdigest()==prov['master_sha256']==inv['master_sha256']
 stem='enemy-projectile304-304-8';im=Image.open(A/(stem+'.png'));assert im.mode=='RGBA' and im.size==(96,112);rgba=np.array(im);coverage=np.repeat(np.repeat(mask,8,axis=0),8,axis=1);assert np.all(rgba[~coverage]==0) and np.all(rgba[coverage,3]==255);assert mask.sum()==13
 raw=(R/'assets/hd/packs/asteroid1-ten-v1'/(stem+'.hda')).read_bytes();assert raw[28:]==im.tobytes() and hashlib.sha256(raw).hexdigest()==inv['hda_sha256'];assert m.fnv(im.tobytes())==inv['rgba_fnv64']
 subprocess.run([sys.executable,str(R/'prototype/build-asteroid1-projectile304-art.py'),'--data',str(a.data),'--out',str(a.out/'rebuilt')],check=True,capture_output=True)
 assert (a.out/'rebuilt'/(stem+'.hda')).read_bytes()==raw and (a.out/'rebuilt'/(stem+'.png')).read_bytes()==(A/(stem+'.png')).read_bytes()
 report={'status':'PASS','inventory':inv,'exact_original_13_cell_alpha':True,'transparent_rgb_zero':True,'no_external_glow_or_new_animation':True,'rebuild_png_HDA_exact':True,'master_provenance_exact':True,'scope':'Portable art registration only; native enemy-role rendering tested separately.'};(a.out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
