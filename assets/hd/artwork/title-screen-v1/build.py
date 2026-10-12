#!/usr/bin/env python3
"""Rebuild approved title artwork from immutable generated masters, with no game data."""
from pathlib import Path
from PIL import Image, ImageChops
from collections import deque
import argparse,hashlib,json
ROOT=Path(__file__).resolve().parent
SPECS={'pic4':((1280,800),None),'tyrian146':((1216,484),(4,4,1216,484)),'year151':((648,256),(8,8,644,252))}
CUTS=[('left',(85,38,115,78),[(90,46,96,58)]),('right',(190,43,222,80),[(200,61,207,67),(210,63,215,77)])]
def sha(b):return hashlib.sha256(b).hexdigest()
def fnv(b):
 h=14695981039346656037
 for x in b:h=((h^x)*1099511628211)&0xffffffffffffffff
 return f'{h:016x}'
def safe_output(value):
 raw=Path(value).expanduser()
 if not raw.is_absolute():raise ValueError('output must be an absolute path')
 if any(p.is_symlink() for p in [raw,*raw.parents]):raise ValueError('output path must not contain symlinks')
 out=raw.resolve()
 if out.exists():raise ValueError('output must not already exist')
 if not out.parent.is_dir():raise ValueError('output parent must already exist')
 if out==ROOT or ROOT in out.parents or out in ROOT.parents:raise ValueError('output must be external to the source package')
 return out

def normalise(im):
 b=bytearray(im.convert('RGBA').tobytes())
 for i in range(0,len(b),4):
  if b[i+3]==0:b[i:i+3]=b'\0\0\0'
 return Image.frombytes('RGBA',im.size,bytes(b))
def make_assets():
 stamps=json.loads((ROOT/'expected-hashes.json').read_text())
 for name,expected in stamps['master_file_sha256'].items():
  path=ROOT/'masters'/name
  if path.is_symlink() or sha(path.read_bytes())!=expected:raise ValueError('master identity mismatch: '+name)
 assets={}; records=[]
 for name,(canvas,bounds) in SPECS.items():
  path=ROOT/'masters'/f'{name}-master.png';src=Image.open(path).convert('RGBA' if bounds else 'RGB')
  bbox=src.getchannel('A').point(lambda x:255 if x>16 else 0).getbbox() if bounds else None
  if bounds:
   im=Image.new('RGBA',canvas);im.paste(src.crop(bbox).resize((bounds[2]-bounds[0],bounds[3]-bounds[1]),Image.Resampling.LANCZOS),bounds[:2])
  else:im=src.resize(canvas,Image.Resampling.LANCZOS).convert('RGBA')
  assets[name]=im
  records.append({'asset':name,'master_sha256':sha(path.read_bytes()),'master_size':list(src.size),'master_visible_alpha_bbox_gt16':list(bbox)if bbox else None,'canonical_size':list(canvas),'alpha_support_bound':list(bounds)if bounds else None})
 # Only alpha from the generated correction masters is used. RGB and unrelated alpha stay exact.
 prior=assets['tyrian146']; alpha=prior.getchannel('A');mask=Image.new('L',prior.size)
 for name,box,regions in CUTS:
  src=Image.open(ROOT/'masters'/f'{name}-clearance-master.png').convert('RGBA')
  tile=src.resize(((box[2]-box[0])*4,(box[3]-box[1])*4),Image.Resampling.LANCZOS).getchannel('A')
  for x0,y0,x1,y1 in regions:
   target=(x0*4,y0*4,x1*4,y1*4);local=((x0-box[0])*4,(y0-box[1])*4,(x1-box[0])*4,(y1-box[1])*4)
   alpha.paste(ImageChops.darker(alpha.crop(target),tile.crop(local)),target);mask.paste(255,target)
 corrected=prior.copy();corrected.putalpha(alpha);assets['tyrian146']=corrected
 difference=ImageChops.difference(prior.getchannel('A'),alpha)
 changed=sum(1 for v in difference.tobytes()if v);assert changed==1498
 assert not ImageChops.multiply(difference,ImageChops.invert(mask)).getbbox()
 assert prior.convert('RGB').tobytes()==corrected.convert('RGB').tobytes()
 for name in assets:assets[name]=normalise(assets[name])
 return assets,records,mask,changed

def meaningful_holes(im,density):
 a=im.getchannel('A');w,h=a.size;b=a.tobytes();seen=bytearray(w*h);found=[]
 for seed in range(w*h):
  if seen[seed]or b[seed]>16:continue
  q=deque([seed]);seen[seed]=1;count=0;x0=w;y0=h;x1=y1=0;edge=False
  while q:
   i=q.popleft();y,x=divmod(i,w);count+=1;x0=min(x0,x);x1=max(x1,x);y0=min(y0,y);y1=max(y1,y)
   if x==0 or y==0 or x==w-1 or y==h-1:edge=True
   for n in ([i-1]if x else [])+([i+1]if x+1<w else [])+([i-w]if y else [])+([i+w]if y+1<h else []):
    if not seen[n]and b[n]<=16:seen[n]=1;q.append(n)
  if not edge and count>=8*density*density:found.append({'area_logical':count/(density*density),'bbox_logical':[x0/density,y0/density,(x1+1)/density,(y1+1)/density]})
 return found

def composite(assets,yl,yk):
 im=assets['pic4'].copy();im.alpha_composite(assets['tyrian146'],(44,yl*4));im.alpha_composite(assets['year151'],(620,yk*4));return im.convert('RGB')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);args=ap.parse_args();out=safe_output(args.output)
 # Validate masters before creating the output directory.
 assets,records,mask,changed=make_assets();out.mkdir()
 for rec in records:
  name=rec['asset'];im=assets[name];path=out/f'{name}-canonical4x.png';im.save(path);raw=im.tobytes();expected=json.loads((ROOT/'expected-hashes.json').read_text())['canonical'][name];assert sha(path.read_bytes())==expected['png_sha256'] and sha(raw)==expected['rgba_sha256'];a=im.getchannel('A');bbox=a.getbbox();bound=rec['alpha_support_bound']
  assert (a.getextrema()==(255,255))if not bound else (bbox[0]>=bound[0]and bbox[1]>=bound[1]and bbox[2]<=bound[2]and bbox[3]<=bound[3])
  assert all(raw[i:i+3]==b'\0\0\0'for i in range(0,len(raw),4)if raw[i+3]==0)
  rec.update(png_sha256=sha(path.read_bytes()),rgba_sha256=sha(raw),rgba_fnv64=fnv(raw),rgba_bytes=len(raw),alpha_sha256=sha(a.tobytes()),alpha_bbox=list(bbox))
  if name!='pic4':
   holes4=meaningful_holes(im,4);holes2=meaningful_holes(im.resize((im.width//2,im.height//2),Image.Resampling.NEAREST),2);assert len(holes4)==(1 if name=='tyrian146'else 3);assert len(holes2)==len(holes4);rec.update(meaningful_holes_4x=holes4,meaningful_holes_2x=holes2)
 mask.save(out/'tyrian-alpha-correction-boundary-mask4x.png')
 states=[]
 for i,yl in enumerate(range(60,3,-2)):
  yk=45+i;assert 11+304<=320 and yl+121<=200 and 155+162<=320 and yk+64<=200
  im=composite(assets,yl,yk);two=im.resize((640,400),Image.Resampling.NEAREST);states.append({'step':i,'tyrian':[11,yl],'year':[155,yk],'canonical4x_RGB_sha256':sha(im.tobytes()),'native2x_RGB_sha256':sha(two.tobytes())})
 for name,yl,yk in [('initial',62,41),('mid',32,59),('settled',4,73)]:
  im=composite(assets,yl,yk);im.save(out/f'{name}-offline-native4x.png');im.resize((640,400),Image.Resampling.NEAREST).save(out/f'{name}-offline-native2x.png')
 proof={'status':'OFFLINE_SOURCE_REPRODUCTION_ONLY','pillow_version':Image.__version__,'assets':records,'tyrian_alpha_correction':{'changed_4x_samples':changed,'outside_corridors_changes':0,'visible_RGB_changes':0,'cuts':CUTS,'boundary_mask_sha256':sha(mask.tobytes())},'alpha_policy':'straight RGBA; RGB zero only where alpha is exactly zero; other soft coverage retained','all29_positions':states,'UI':'Menu, version and cursor are separate original live draws, absent from these art-only proofs','runtime_claims':'None; this verifies offline registration and canonical sampling only.'}
 (out/'validation.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({'status':'PASS','assets':[(r['asset'],r['png_sha256'])for r in records],'movement_positions':len(states),'output_files':len(list(out.iterdir()))}))
if __name__=='__main__':main()
