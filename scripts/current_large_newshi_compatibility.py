"""One registered 96x84 NEWSHI master; independent native parts and nose states.

Only original-derived binary masks/differences are distributed, not game data.
V2 preserves retained RGB; newly transparent RGB is normalized to zero.
"""
import io
import struct
import numpy as np
from PIL import Image
from current_guided_compatibility import read, parse, sha, image
from build_newshf_hd import fnv
INPUT_ROOT='authoring-inputs/newshi-large'
ROOT='assets/hd/current-compat/newshi-large'
HEADER='src/current_large_newshi_hd_assets.h'
SELECTION='assets/hd/authoring/newshi-large.json'
MAPPING='packaging/current-large-newshi-compatibility.json'
IDS=tuple(range(2100018,2100028))
SCHEMA='opentyrian-large-newshi-authoring-v1'
REVISION='current-single-source-large-newshi-ten'
PARTS=((302,201,24,0),(303,203,48,0),(304,237,0,28),(305,239,24,28),(306,241,48,28),(307,243,72,28),(308,278,36,56))
MASK_PINS={"center-difference-268.png": "73d203ff3289f794e28d469137868d41ce4fde77dd425deabcbe1ba155ef6e23", "center-difference-272.png": "980e4db250bc83e877c98c7d83141c384f4fdfbb78c52b43f56daa9aa2c88323", "native-mask-201.png": "3ff2273c6ed235f3926e265590cc2b7276cce7510fd818223192980c6a455503", "native-mask-203.png": "f323c58e27d685855376b4ac44ea1dd8d79db5f6f38b334747c349ef4e0a8419", "native-mask-237.png": "16eeef246565a0caab86940ce0aa50e23181e4a7a2340f638522bd4c59a67ab5", "native-mask-239.png": "cd7a0436f6a03c470d9782ebdbcfb9e34724e1eddd64c536dd08a8ebe4796957", "native-mask-241.png": "37c59a02d114f3b79d4c8dc7578f6848a97450752168b8470bb9dd008e17438a", "native-mask-243.png": "b345abb0ce46441cede46f40add1982dc3e366b4d7b12f3878238540b199b458", "native-mask-268.png": "e24ad036183528946e005aa80ca94618fe3599d0d93748a6c933a4b0297b3fac", "native-mask-270.png": "ebc76082f8d34c86c6ca1c485b19d785e538140a5561b890ae95a2139943a4d8", "native-mask-272.png": "1f6b5d66f406b5009b5072668b2d0a1c2d8e127a2b2acc1b9f2a11d4d17fce20", "native-mask-278.png": "aff37db1e5c911c3674aed95ae243e1cdf126e2858c7305e43af6c6670562b4e", "native-whole-mask.png": "911322b6fdb9d94f4b452e884ee72dd0b81b0af5cc029600578be0803618b79b", "normal-difference-268.png": "c96c98ba9b522b2cd116097ff4cdbaf7fdb9c80cd82453b1b2e26de3ef5b8c3a", "normal-difference-270.png": "7647e84a967c5f720d14cf159dad336e19db535f7310eb88681828a9015fb0ee", "normal-difference-272.png": "a34835e8ef562f3bc9d89418d07179be480db1ca9ecf2f9e067fb59a786a8d62"}
INPUTS=tuple(sorted((*MASK_PINS,'normal-generated-v1.png','open-center-generated-v1.png','prompt-normal-v1.txt','prompt-open-center-v1.txt','generation-provenance.txt','registration-recipe.json')))
def name(i):
 if type(i) is not int or i not in IDS:raise ValueError('Unknown large NEWSHI identity')
 return f'newshi-role{i}-8.hda'
def png(i):return INPUT_ROOT+'/derived/'+name(i).replace('.hda','.png')
def generated_paths():return {png(i) for i in IDS}|{INPUT_ROOT+'/derived/normal-master-v2.png'}
def input_paths(root):return {INPUT_ROOT+'/'+n for n in INPUTS}|{SELECTION}
def encode_png(im):
 out=io.BytesIO();im.save(out,format='PNG',optimize=False);return out.getvalue()
def expand(a):return np.repeat(np.repeat(a,8,0),8,1)
def normalized(a):
 a=a.copy();a[a[:,:,3]==0,:3]=0;return a

def generate(root,raw,candidate=False):
 selected=parse(raw)
 if not isinstance(selected,dict) or set(selected)!={'schema','version','inputs'} or selected['schema']!=SCHEMA:raise ValueError('Invalid large NEWSHI selection')
 if not isinstance(selected['version'],str) or not 1<=len(selected['version'])<=128:raise ValueError('Invalid large NEWSHI version')
 if not isinstance(selected['inputs'],dict) or set(selected['inputs'])!={INPUT_ROOT+'/'+n for n in INPUTS}:raise ValueError('Invalid fixed large NEWSHI input closure')
 for p,h in selected['inputs'].items():
  if sha(read(root,p))!=h:raise ValueError('Changed large NEWSHI input: '+p)
 def mask(n):
  b=read(root,INPUT_ROOT+'/'+n)
  if sha(b)!=MASK_PINS[n]:raise ValueError('Changed original-derived mask '+n)
  im=Image.open(io.BytesIO(b)).convert('L')
  if im.size!=((96,84) if n=='native-whole-mask.png' else (24,28)) or not set(im.tobytes())<={0,255}:raise ValueError('Invalid native mask')
  return expand(np.array(im)>0)
 recipe=parse(read(root,INPUT_ROOT+'/registration-recipe.json'))
 if recipe['schema']!='opentyrian-newshi-registration-v2':raise ValueError('Invalid registration recipe')
 raw_normal=Image.open(io.BytesIO(read(root,INPUT_ROOT+'/normal-generated-v1.png'))).convert('RGBA')
 normal=Image.new('RGBA',(768,672));normal.paste(raw_normal.crop(recipe['normal_crop']).resize(recipe['normal_size'],Image.Resampling.LANCZOS),recipe['normal_position'])
 normal=np.array(normal);normal[~mask('native-whole-mask.png')]=0;normal=normalized(normal)
 normal_nose=normal[448:672,288:480].copy()
 raw_open=Image.open(io.BytesIO(read(root,INPUT_ROOT+'/open-center-generated-v1.png'))).convert('RGBA')
 opened=Image.new('RGBA',(192,224))
 for crop,pos in zip(recipe['open_crops'],recipe['open_positions']):opened.paste(raw_open.crop(crop).resize(recipe['open_size'],Image.Resampling.LANCZOS),pos)
 center=normal_nose.copy();diff=mask('normal-difference-270.png');center[diff]=np.array(opened)[diff];center[~mask('native-mask-270.png')]=0;center=normalized(center)
 states={270:center}
 for base,left,right in ((268,8,-8),(272,-8,8)):
  result=center.copy()
  for y,x in np.argwhere(mask(f'center-difference-{base}.png')):
   sy=y-(left if x<96 else right);result[y,x]=center[sy,x] if 0<=sy<224 else 0
  diff=mask(f'normal-difference-{base}.png');result[~diff]=normal_nose[~diff];result[~mask(f'native-mask-{base}.png')]=0;states[base]=normalized(result)
 for contour in recipe['contours']:
  l,t,r,b=contour['box']
  for y in range(t,b):
   if 'points' in contour:edge=np.interp(y+.5,[p[0] for p in contour['points']],[p[1] for p in contour['points']])
   else:edge=contour['line'][0]*y+contour['line'][1]
   x=np.arange(l,r)+.5;coverage=np.clip(edge-x+.5 if contour['side']=='right' else x-edge+.5,0,1)
   normal[y,l:r,3]=np.rint(normal[y,l:r,3]*coverage).astype('uint8')
 normal=normalized(normal)
 pieces=[];assembly=np.zeros_like(normal)
 for record,base,x,y in PARTS:
  piece=normal[y*8:(y+28)*8,x*8:(x+24)*8].copy()
  if np.any(piece[:,:,3][~mask(f'native-mask-{base}.png')]):raise ValueError('Normal piece leaves native mask')
  assembly[y*8:(y+28)*8,x*8:(x+24)*8]=piece;pieces.append((record,base,piece))
 if not np.array_equal(normal,assembly):raise ValueError('Seven part assembly differs')
 for base in (268,270,272):
  piece=states[base];diff=mask(f'normal-difference-{base}.png')
  if not np.array_equal(piece[~diff],normal_nose[~diff]) or not np.array_equal(piece[:40],normal_nose[:40]):raise ValueError('Nose changed unchanged native cells')
  pieces.append((308,base,piece))
 rows=[];pngs={INPUT_ROOT+'/derived/normal-master-v2.png':encode_png(Image.fromarray(normal))};blobs={}
 for identity,(record,base,piece) in zip(IDS,pieces):
  data=encode_png(Image.fromarray(piece));blob=struct.pack('<4s6I',b'HDR1',identity,8,24,28,6,7)+piece.tobytes()
  pngs[png(identity)]=data;blobs[identity]=blob
  rows.append(dict(identity=identity,records=[record],base=base,source_path=ROOT+'/'+name(identity),destination='assets/global/newshi-large/'+name(identity),source_png=png(identity),source_png_sha256=sha(data),bytes=len(blob),sha256=sha(blob),payload_fnv=f'{fnv(blob[28:]):016x}'))
 return selected,pngs,blobs,rows

def payload_header(rows):
 if tuple(r['identity'] for r in rows)!=IDS:raise ValueError('Invalid large NEWSHI rows')
 lines=[f' {{{r["identity"]}u,{r["bytes"]}u,8u,24u,28u,6,7,"newshi-large/{name(r["identity"])}",UINT64_C(0x{r["payload_fnv"]})}},' for r in rows]
 return ('/* Generated by build_current_large_newshi.py. */\n#ifndef CURRENT_LARGE_NEWSHI_HD_ASSETS_H\n#define CURRENT_LARGE_NEWSHI_HD_ASSETS_H\n#include "global_asset_registry.h"\nenum { LARGE_NEWSHI_HD_RESOURCE_COUNT = 10 };\nstatic const GlobalAssetResource large_newshi_hd_resources[10] = {\n'+'\n'.join(lines)+'\n};\n#endif\n').encode()
def load(root):
 selected,pngs,blobs,rows=generate(root,read(root,SELECTION))
 if parse(read(root,MAPPING))!=dict(schema='opentyrian-large-newshi-compatibility-v1',selection=SELECTION,files=rows):raise ValueError('Large NEWSHI mapping differs')
 for p,data in pngs.items():
  if read(root,p)!=data:raise ValueError('Changed large NEWSHI derived PNG')
 for identity,data in blobs.items():
  if read(root,ROOT+'/'+name(identity))!=data:raise ValueError('Changed large NEWSHI transport')
 if read(root,HEADER)!=payload_header(rows):raise ValueError('Changed large NEWSHI header')
 return {row['destination']:row for row in rows}
