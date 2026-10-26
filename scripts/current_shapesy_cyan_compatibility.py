"""One generated static cloud master, four independent layer2 resource identities.

Only original-derived binary support is distributed; no original RGB/index data.
All opaque and soft pixels stay inside original nonzero cells. Source zero is
transparent, unlike the separate layer1 platform zero-black convention.
"""
import io
import struct
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
from current_guided_compatibility import read, parse, sha
from build_newshf_hd import fnv
INPUT_ROOT='authoring-inputs/shapesy-cyan'
ROOT='assets/hd/current-compat/shapesy-cyan'
HEADER='src/current_shapesy_cyan_hd_assets.h'
SOURCE_HEADER='src/current_shapesy_cyan_source.h'
SELECTION='assets/hd/authoring/shapesy-cyan.json'
MAPPING='packaging/current-shapesy-cyan-compatibility.json'
SCHEMA='opentyrian-shapesy-cyan-authoring-v1'
REVISION='current-single-source-shapesy-cyan-four'
IDS=(111,112,121,122)
ROLE=203
INPUTS=('native-mask.png','raw-generated.png','prompt.txt','provenance.json','registration-recipe.json')
MASK_PIN='3a9a71ac5c8768cb0db75eba14392f43dab5b0e2175376fc187a1efd36660807'
MASTER_PIN='69ba9e3a0b6c22ce7885d2d5443ee367eb83a71f2cb1fdffabdaee3bdce88e63'
SOURCE_PINS=('d5dd76195190aaa2','791e6ab3efec5c7f','474e697606a47780','3df3b4ff46b4b4b2')
def name(i):
 if type(i) is not int or i not in IDS:raise ValueError('Unknown cyan identity')
 return f'terrain-shapesy-cyan-{i}-8.hda'
def png(i):return INPUT_ROOT+'/derived/'+name(i).replace('.hda','.png')
def generated_paths():return {png(i) for i in IDS}|{INPUT_ROOT+'/derived/master-384x448.png'}
def input_paths(root):return {INPUT_ROOT+'/'+n for n in INPUTS}|{SELECTION}
def encode_png(im):
 out=io.BytesIO();im.save(out,format='PNG');return out.getvalue()
def smooth(v):
 v=np.clip(v,0,1);return v*v*(3-2*v)
def generate(root,raw):
 selected=parse(raw)
 if not isinstance(selected,dict) or set(selected)!={'schema','version','inputs'} or selected['schema']!=SCHEMA:raise ValueError('Invalid cyan selection schema')
 if not isinstance(selected['version'],str) or not 1<=len(selected['version'])<=128:raise ValueError('Invalid cyan version')
 if not isinstance(selected['inputs'],dict) or set(selected['inputs'])!={INPUT_ROOT+'/'+n for n in INPUTS}:raise ValueError('Invalid cyan fixed input closure')
 for p,h in selected['inputs'].items():
  if sha(read(root,p))!=h:raise ValueError('Changed cyan input: '+p)
 mask_bytes=read(root,INPUT_ROOT+'/native-mask.png')
 if sha(mask_bytes)!=MASK_PIN:raise ValueError('Changed original cyan support')
 mask_image=Image.open(io.BytesIO(mask_bytes))
 if mask_image.mode!='L' or mask_image.size!=(48,56) or not set(mask_image.tobytes())<={0,255}:raise ValueError('Invalid cyan mask format')
 native=np.array(mask_image)>0
 if int(native.sum())!=521:raise ValueError('Changed cyan native support count')
 mask=np.repeat(np.repeat(native,8,0),8,1)
 r=parse(read(root,INPUT_ROOT+'/registration-recipe.json'))
 if r['schema']!='opentyrian-shapesy-cyan-registration-v1' or r['size']!=[384,448] or r['density']!=8 or r['mask_sha256']!=MASK_PIN or r['master_sha256']!=MASTER_PIN or tuple(r['source_pins'][str(i)] for i in IDS)!=SOURCE_PINS or r['palette_fnv']!='5e80e83992be2927':raise ValueError('Invalid cyan registration identity')
 raw_image=Image.open(io.BytesIO(read(root,INPUT_ROOT+'/raw-generated.png'))).convert('RGBA')
 pixels=np.array(raw_image.resize((384,448),Image.Resampling.LANCZOS));a=pixels[:,:,3].astype(float)/255
 b=gaussian_filter(mask.astype(float),sigma=r['mask_sigma'],mode='nearest')
 matte=smooth((b-r['mask_threshold'])/r['mask_ramp']);matte[~mask]=0
 yy,xx=np.mgrid[:448,:384];cap=r['cap']
 window=smooth((yy-cap['window_top'])/cap['window_ramp'])*smooth((cap['window_bottom']-yy)/cap['window_ramp'])
 curve=cap['curve_origin']-cap['curve_scale']*(yy-cap['curve_y'])**2
 matte*=1-window*(1-smooth((curve-xx)/cap['ramp']))
 pixels[:,:,3]=np.rint(a*matte*255).astype('uint8');pixels[pixels[:,:,3]<=r['alpha_floor']]=0
 master=encode_png(Image.fromarray(pixels))
 if sha(master)!=MASTER_PIN:raise ValueError('Cyan canonical master differs')
 if np.any(pixels[~mask]) or np.any(pixels[pixels[:,:,3]==0]):raise ValueError('Cyan zero-cell / transparent RGB drift')
 # Two original boundary cells intentionally have no generated visible subpixel.
 if int(np.count_nonzero(native & ~pixels[:,:,3].reshape(56,8,48,8).any(axis=(1,3))))!=2:raise ValueError('Cyan accepted inward boundary differs')
 pngs={INPUT_ROOT+'/derived/master-384x448.png':master};blobs={};rows=[];assembly=np.zeros_like(pixels)
 for i,x,y in ((111,0,0),(112,192,0),(121,0,224),(122,192,224)):
  part=pixels[y:y+224,x:x+192].copy();assembly[y:y+224,x:x+192]=part
  data=encode_png(Image.fromarray(part));blob=struct.pack('<4s6I',b'HDR1',ROLE*10000+i,8,24,28,0,0)+part.tobytes()
  pngs[png(i)]=data;blobs[i]=blob
  rows.append(dict(identity=ROLE*10000+i,base=i,source_bank='shapesy.dat',source_layer=2,source_path=ROOT+'/'+name(i),destination='assets/gameplay/'+name(i),source_png=png(i),source_png_sha256=sha(data),bytes=len(blob),sha256=sha(blob),payload_fnv=f'{fnv(blob[28:]):016x}'))
 if not np.array_equal(pixels,assembly):raise ValueError('Cyan inverse assembly differs')
 return selected,pngs,blobs,rows

def payload_header(rows):
 if tuple(r['base'] for r in rows)!=IDS:raise ValueError('Invalid cyan header order')
 entries='\n'.join(f' UINT64_C(0x{r["payload_fnv"]}), /* {r["base"]} */' for r in rows)
 return ('/* Generated by build_current_shapesy_cyan.py. */\n#ifndef CURRENT_SHAPESY_CYAN_HD_ASSETS_H\n#define CURRENT_SHAPESY_CYAN_HD_ASSETS_H\n#include <stdint.h>\nstatic const uint64_t cyan_rgba_pins[4] = {\n'+entries+'\n};\n#endif\n').encode()
def source_header():
 return ('/* Original identity witnesses only; no source image bytes. */\n#ifndef CURRENT_SHAPESY_CYAN_SOURCE_H\n#define CURRENT_SHAPESY_CYAN_SOURCE_H\n#include <stdint.h>\nstatic const unsigned cyan_ids[4]={111,112,121,122};\nstatic const uint64_t cyan_source_pins[4]={'+','.join('UINT64_C(0x'+p+')' for p in SOURCE_PINS)+'};\n#define CYAN_PALETTE_FNV UINT64_C(0x5e80e83992be2927)\n#endif\n').encode()
def load(root):
 selected,pngs,blobs,rows=generate(root,read(root,SELECTION))
 if parse(read(root,MAPPING))!=dict(schema='opentyrian-shapesy-cyan-compatibility-v1',selection=SELECTION,files=rows):raise ValueError('Cyan mapping differs')
 for p,b in pngs.items():
  if read(root,p)!=b:raise ValueError('Changed cyan derived PNG')
 for i,b in blobs.items():
  if read(root,ROOT+'/'+name(i))!=b:raise ValueError('Changed cyan transport')
 if read(root,HEADER)!=payload_header(rows) or read(root,SOURCE_HEADER)!=source_header():raise ValueError('Changed cyan header')
 return {r['destination']:r for r in rows}
