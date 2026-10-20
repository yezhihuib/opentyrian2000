#!/usr/bin/env python3
"""Verify exact registered reuse of authored112/113 artwork, no default edits."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,struct,subprocess,sys
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];ART=ROOT/'assets/hd/artwork/asteroid1-orb112113-v1';PACK=ROOT/'assets/hd/packs/asteroid1-ten-v1'
SHA=lambda b:hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();assert not a.out.exists();a.out.mkdir(parents=True)
 spec=importlib.util.spec_from_file_location('orb',ROOT/'prototype/build-asteroid1-orb112113-art.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 subprocess.run([sys.executable,str(ROOT/'prototype/build-asteroid1-orb112113-art.py'),'--data',str(a.data),'--out',str(a.out/'rebuilt')],check=True,capture_output=True)
 inv=json.loads((ART/'art-inventory.json').read_text());rows=[]
 for b in (112,113):
  bank,mask,indices=m.decode(a.data,b);stem=f'enemy-orb112113-{b}-8';source=np.array(Image.open(ART/f'retained-source-{b}.png').convert('RGBA'));im=Image.open(ART/(stem+'.png'));rgba=np.array(im);support=np.repeat(np.repeat(mask,8,0),8,1);raw=(PACK/(stem+'.hda')).read_bytes()
  assert im.mode=='RGBA' and im.size==(96,112) and struct.unpack('<4s6I',raw[:28])==(b'HDR1',1420000+b,8,12,14,0,0)
  assert np.array_equal(rgba[support],source[support]) and not rgba[~support].any()
  assert np.array_equal((rgba[:,:,3]>0).reshape(14,8,12,8).any(axis=(1,3)),mask)
  assert raw[28:]==im.tobytes() and SHA(raw)==inv[str(b)]['hda_sha256'] and m.fnv(im.tobytes())==inv[str(b)]['rgba_fnv64']
  assert raw==(a.out/'rebuilt'/(stem+'.hda')).read_bytes() and (ART/(stem+'.png')).read_bytes()==(a.out/'rebuilt'/(stem+'.png')).read_bytes()
  rows.append({'selector':b,'occupied_logical_cells':int(mask.sum()),'outside_source_RGBA_zero':True,'inside_source_authored_RGBA_unchanged':True,'hda_sha256':SHA(raw),'rgba_fnv64':m.fnv(im.tobytes())})
 report={'status':'PASS','images':rows,'rebuild_exact':True,'scope':'Finite retained-art registration; native firing and visual acceptance separately required.'};(a.out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
