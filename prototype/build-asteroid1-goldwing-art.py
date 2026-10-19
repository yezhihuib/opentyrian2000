#!/usr/bin/env python3
"""Pack record282's fixed gold shell with three source-bound jewel-color states.

Only the original 12-pixel jewel region may vary. Geometry, alpha and every
exterior byte remain identical across79/81/83. Source data remains external.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,struct
import numpy as np
from PIL import Image,ImageFilter
ROOT=Path(__file__).resolve().parents[1]
BASES=(79,81,83)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
 p.add_argument('--master',type=Path,default=ROOT/'assets/hd/artwork/asteroid1-goldwing-v1/imagegen-master.png');a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
 spec=importlib.util.spec_from_file_location('asteroid_helpers',ROOT/'prototype/build-asteroid1-ten-art.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 bank=(a.data/'newshd.shp').read_bytes();assert len(bank)==42012 and m.fnv(bank)=='0x913975450e0fc00d'
 pal=np.frombuffer(bytes((v<<2)|(v>>4)for v in(a.data/'palette.dat').read_bytes()[:768]),np.uint8).reshape(256,3)
 originals=[];masks=[]
 for base in BASES:
  idx=np.zeros((28,24),np.uint8);mask=idx.copy()
  for di,x,y in((0,0,0),(1,12,0),(19,0,14),(20,12,14)):
   rgb,cov=m.decode(bank,base+di);idx[y:y+14,x:x+12]=rgb;mask[y:y+14,x:x+12]=cov
  originals.append(pal[idx]);masks.append(mask)
 assert all(np.array_equal(masks[0],v)for v in masks)
 pulse=np.any(originals[0]!=originals[1],axis=2)|np.any(originals[0]!=originals[2],axis=2)
 assert int(pulse.sum())==12
 support=Image.fromarray(masks[0]);bbox=support.getbbox();density=8
 generated=Image.open(a.master).convert('RGBA');alpha=np.asarray(generated.getchannel('A'));ys,xs=np.where(alpha>=128)
 crop=generated.crop((xs.min(),ys.min(),xs.max()+1,ys.max()+1)).resize(((bbox[2]-bbox[0])*8,(bbox[3]-bbox[1])*8),Image.Resampling.LANCZOS)
 aligned=Image.new('RGBA',(24*8,28*8));aligned.paste(crop,(bbox[0]*8,bbox[1]*8))
 high=support.resize(aligned.size,Image.Resampling.NEAREST);smooth=np.asarray(high.filter(ImageFilter.GaussianBlur(4.0))).astype(float)
 inward=np.minimum(np.clip((smooth-127.5)*2,0,255).astype(np.uint8),np.asarray(high));rgba=np.array(aligned);rgba[:,:,3]=np.minimum(rgba[:,:,3],inward)
 highpulse=np.repeat(np.repeat(pulse,8,axis=0),8,axis=1);source_mean=np.asarray([o[pulse].mean(axis=0)for o in originals]);art_mean=rgba[:,:,:3][highpulse].mean(axis=0)
 inventory={};outs=[]
 for i,base in enumerate(BASES):
  out=rgba.copy();out[:,:,:3][highpulse]=np.clip(out[:,:,:3][highpulse].astype(float)*source_mean[i]/art_mean,0,255).astype(np.uint8)
  im=Image.fromarray(out,'RGBA');stem=f'enemy-newshd-{base}-8';im.save(a.out/f'{stem}.png');payload=im.tobytes();raw=struct.pack('<4s6I',b'HDR1',1080000+base,8,24,28,0,0)+payload;(a.out/f'{stem}.hda').write_bytes(raw);outs.append(out)
  inventory[stem]=dict(record=282,base=base,size=1,logical_size=[24,28],rgba_fnv64=m.fnv(payload),sha256=hashlib.sha256(raw).hexdigest())
 assert all(np.array_equal(outs[0][~highpulse],o[~highpulse])for o in outs)
 assert all(np.array_equal(outs[0][:,:,3],o[:,:,3])for o in outs)
 assert all(not np.any(o[:,:,3][np.asarray(high)==0])for o in outs)
 (a.out/'art-inventory.json').write_text(json.dumps(inventory,indent=2)+'\n');print(json.dumps(inventory,indent=2))
if __name__=='__main__':main()
