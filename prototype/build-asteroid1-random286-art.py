#!/usr/bin/env python3
"""Derive four fixed-geometry rock pulse states from one imagegen master.

Original source differences guide continuous center-only color/light fields.
No alpha or exterior byte varies, and original data remains external.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,struct
import numpy as np
from PIL import Image,ImageFilter
ROOT=Path(__file__).resolve().parents[1]
BASES=(229,231,233,235)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--master',type=Path,default=ROOT/'assets/hd/artwork/asteroid1-random286-v1/imagegen-master.png');a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
 s=importlib.util.spec_from_file_location('asteroid_helpers',ROOT/'prototype/build-asteroid1-ten-art.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 bank=(a.data/'newshd.shp').read_bytes();assert len(bank)==42012 and m.fnv(bank)=='0x913975450e0fc00d'
 pal=np.frombuffer(bytes((v<<2)|(v>>4)for v in(a.data/'palette.dat').read_bytes()[:768]),np.uint8).reshape(256,3)
 originals=[];masks=[]
 for base in BASES:
  idx=np.zeros((28,24),np.uint8);mask=idx.copy()
  for di,x,y in((0,0,0),(1,12,0),(19,0,14),(20,12,14)):
   c,cov=m.decode(bank,base+di);idx[y:y+14,x:x+12]=c;mask[y:y+14,x:x+12]=cov
  originals.append(pal[idx]);masks.append(mask)
 assert all(np.array_equal(masks[0],v)for v in masks)
 pulse=np.any(np.stack(originals)!=originals[0],axis=(0,3));assert int(pulse.sum())==65
 support=Image.fromarray(masks[0]);bbox=support.getbbox();density=8;size=(24*8,28*8)
 generated=Image.open(a.master).convert('RGBA');ys,xs=np.where(np.asarray(generated.getchannel('A'))>=128)
 crop=generated.crop((xs.min(),ys.min(),xs.max()+1,ys.max()+1)).resize(((bbox[2]-bbox[0])*8,(bbox[3]-bbox[1])*8),Image.Resampling.LANCZOS)
 aligned=Image.new('RGBA',size);aligned.paste(crop,(bbox[0]*8,bbox[1]*8))
 high=support.resize(size,Image.Resampling.NEAREST);smooth=np.asarray(high.filter(ImageFilter.GaussianBlur(4))).astype(float)
 inward=np.minimum(np.clip((smooth-127.5)*2,0,255).astype(np.uint8),np.asarray(high));rgba=np.array(aligned);rgba[:,:,3]=np.minimum(rgba[:,:,3],inward)
 highpulse=np.repeat(np.repeat(pulse,8,axis=0),8,axis=1)
 # The 65-cell source region is an outer safety bound, not a painted pixel grid.
 # Blur the semantic source RGB delta and smoothly feather to zero strictly inside it.
 pimage=Image.fromarray((pulse*255).astype(np.uint8)).resize(size,Image.Resampling.NEAREST)
 weight=np.clip((np.asarray(pimage.filter(ImageFilter.GaussianBlur(3))).astype(float)-127.5)/100,0,1)*highpulse
 inventory={};outs=[]
 for i,base in enumerate(BASES):
  delta=originals[i].astype(float)-originals[0].astype(float)
  fields=[]
  for c in range(3):
   # F-mode interpolation keeps signed deltas, avoiding hue clipping before blending.
   plane=Image.fromarray(delta[:,:,c].astype(np.float32),'F').resize(size,Image.Resampling.BICUBIC)
   # PIL does not blur float images; RGB-independent smooth resampling is enough here.
   fields.append(np.asarray(plane))
  change=np.stack(fields,axis=2)*weight[:,:,None]
  out=rgba.copy();out[:,:,:3]=np.clip(np.rint(out[:,:,:3].astype(float)+change),0,255).astype(np.uint8)
  out[~highpulse]=rgba[~highpulse];im=Image.fromarray(out,'RGBA');stem=f'enemy-newshd-{base}-8';im.save(a.out/f'{stem}.png');payload=im.tobytes();raw=struct.pack('<4s6I',b'HDR1',1080000+base,8,24,28,0,0)+payload;(a.out/f'{stem}.hda').write_bytes(raw);outs.append(out)
  inventory[stem]=dict(record=286,base=base,size=1,logical_size=[24,28],rgba_fnv64=m.fnv(payload),sha256=hashlib.sha256(raw).hexdigest(),changed_pixels=int(np.any(out!=rgba,axis=2).sum()))
 assert all(np.array_equal(outs[0][~highpulse],o[~highpulse])for o in outs)
 assert all(np.array_equal(outs[0][:,:,3],o[:,:,3])for o in outs)
 assert all(not np.any(o[:,:,3][np.asarray(high)==0])for o in outs)
 (a.out/'art-inventory.json').write_text(json.dumps(inventory,indent=2)+'\n');print(json.dumps(inventory,indent=2))
if __name__=='__main__':main()
