#!/usr/bin/env python3
"""Three distinct authored mechanical poses, exact per-pose original support."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,struct,subprocess,sys
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];ART=ROOT/'assets/hd/artwork/asteroid1-clamshell285-v1';PACK=ROOT/'assets/hd/packs/asteroid1-ten-v1';SHA=lambda b:hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();assert not a.out.exists();a.out.mkdir(parents=True)
 spec=importlib.util.spec_from_file_location('art',ROOT/'prototype/build-asteroid1-clamshell285-art.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 prov=json.loads((ART/'provenance.json').read_text());inv=json.loads((ART/'art-inventory.json').read_text());bank=(a.data/'newshd.shp').read_bytes();assert len(bank)==42012 and m.fnv(bank)=='0x913975450e0fc00d'
 for n,h in prov['masters'].items():assert SHA((ART/n).read_bytes())==h
 subprocess.run([sys.executable,str(ROOT/'prototype/build-asteroid1-clamshell285-art.py'),'--data',str(a.data),'--out',str(a.out/'rebuilt')],check=True,capture_output=True)
 rows=[];masks=[];warms=[]
 for b,cells in zip((157,159,161),(362,314,252)):
  idx,cov=m.decode(bank,b);mask=cov!=0;masks.append(mask);stem=f'enemy-newshd-{b}-8';im=Image.open(ART/(stem+'.png'));rgba=np.array(im);support=np.repeat(np.repeat(mask,8,0),8,1);raw=(PACK/(stem+'.hda')).read_bytes()
  assert im.mode=='RGBA' and im.size==(192,224) and struct.unpack('<4s6I',raw[:28])==(b'HDR1',1430000+b,8,24,28,0,0)
  assert int(mask.sum())==cells and not rgba[~support].any() and np.array_equal((rgba[:,:,3]>0).reshape(28,8,24,8).any(axis=(1,3)),mask)
  assert raw[28:]==im.tobytes() and SHA(raw)==inv[stem]['sha256'] and m.fnv(im.tobytes())==inv[stem]['rgba_fnv64']
  assert raw==(a.out/'rebuilt'/(stem+'.hda')).read_bytes() and (ART/(stem+'.png')).read_bytes()==(a.out/'rebuilt'/(stem+'.png')).read_bytes()
  warm=(rgba[:,:,0].astype(int)>rgba[:,:,1].astype(int)+40)&(rgba[:,:,0].astype(int)>rgba[:,:,2].astype(int)+60)&(rgba[:,:,3]>128);warms.append(int(warm.sum()));rows.append({'base':b,'source_cells':cells,'hda_sha256':SHA(raw),'warm_core_subpixels':warms[-1]})
 assert all(not np.array_equal(masks[i],masks[j]) for i in range(3) for j in range(i));assert warms[0]>0 and warms[1]>0 and warms[2]==0
 report={'status':'PASS','images':rows,'three_distinct_original_silhouettes':True,'all_original_cells_represented':True,'outside_each_pose_source_RGBA_zero':True,'generated_alpha_preserved_inside_mask':True,'closed_pose_hides_core':True,'rebuild_HDA_and_PNG_exact':True,'masters_match_provenance':True,'scope':'Body art only; original gameplay/animation validation separately required.'};(a.out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
