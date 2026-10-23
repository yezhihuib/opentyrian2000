#!/usr/bin/env python3
"""Bind the fixed approved shared fireball sources to original registration.

The normal selected manifest is the only source authority. Retained PNGs remain
historical evidence, never fallback inputs. This is not a new-art publication path.
"""
from pathlib import Path
from io import BytesIO
import argparse,hashlib,json,re,struct
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
SELECTED='assets/hd/artwork/enemy-orb112-113-v1/selected-manifest.json'
PINS={112:'c28da6740c5827bab6e2ab44faf0e5218fb8f033af7c6bc500d80167cf47405b',113:'49a4ef3fe0c25cb5cabe153a83d4cf72fc204c45872af83178521d33a902d412'}
def unique_keys(pairs):
 result={}
 for key,value in pairs:
  if key in result:raise ValueError(f'Duplicate manifest key: {key}')
  result[key]=value
 return result
def owned_file(root,relative):
 path=root
 for part in relative.split('/'):
  path=path/part
  if path.is_symlink():raise ValueError(f'Symlink input is not allowed: {relative}')
 if not path.is_file():raise ValueError(f'Missing approved input: {relative}')
 return path
def load_approved_sources(root=None):
 """Read exactly the two pinned role8 PNGs; no retained-source fallback."""
 root=Path(ROOT if root is None else root).resolve()
 manifest=owned_file(root,SELECTED).read_bytes()
 records=json.loads(manifest,object_pairs_hook=unique_keys)
 if not isinstance(records,list) or len(records)!=2:raise ValueError('Expected exactly selectors 112 and 113')
 sources={};inputs=[]
 for row in records:
  if not isinstance(row,dict):raise ValueError('Expected a selected source record')
  selector=row.get('id')
  if type(selector) is not int or selector not in PINS or selector in sources:raise ValueError('Expected unique selectors 112 and 113')
  header=row.get('header_u32')
  if not isinstance(header,list) or any(type(v) is not int for v in header) or header!=[80000+selector,8,12,14,0,0]:raise ValueError(f'Wrong role8 geometry: {selector}')
  relative=row.get('source_png')
  if not isinstance(relative,str) or not re.fullmatch(r'assets/hd/source/[A-Za-z0-9][A-Za-z0-9_-]*\.png',relative):raise ValueError(f'Unsafe approved source path: {relative!r}')
  if row.get('source_png_sha256')!=PINS[selector]:raise ValueError(f'Unapproved source pin: {selector}')
  raw=owned_file(root,relative).read_bytes()
  if hashlib.sha256(raw).hexdigest()!=PINS[selector]:raise ValueError(f'Approved source hash mismatch: {selector}')
  with Image.open(BytesIO(raw)) as im:
   if im.format!='PNG' or im.mode!='RGBA' or im.size!=(96,112) or getattr(im,'n_frames',1)!=1:raise ValueError(f'Wrong source PNG geometry or mode: {selector}')
   sources[selector]=np.array(im)
  inputs.append({'selector':selector,'source_png':relative,'source_png_sha256':PINS[selector]})
 binding={'method':'Fixed-approved-revision shared-source binding; no new-art approval.',
          'selected_manifest':SELECTED,'selected_manifest_sha256':hashlib.sha256(manifest).hexdigest(),
          'sources':sorted(inputs,key=lambda row:row['selector']),
          'retained_sources_used':False,
          'legacy_inventory_note':'retained_source_sha256 preserves the historical byte pin, not the input path used by this build.'}
 return sources,binding
def register_rgba(source,mask):
 """Preserve RGBA inside a supplied 45-cell mask and zero everything outside.

 This pure derivation does not authenticate a mask; production decode does that.
 """
 if source.shape!=(112,96,4) or source.dtype!=np.uint8:raise ValueError('Expected 96x112 RGBA8 source')
 if mask.shape!=(14,12) or mask.dtype!=np.bool_ or int(mask.sum())!=45:raise ValueError('Expected a 12x14 boolean mask with 45 occupied cells')
 support=np.repeat(np.repeat(mask,8,axis=0),8,axis=1);rgba=source.copy();rgba[~support]=0
 if not np.array_equal((rgba[:,:,3]>0).reshape(14,8,12,8).any(axis=(1,3)),mask):raise ValueError('Source does not cover every mask cell')
 return rgba
def fnv(raw):
 h=0xcbf29ce484222325
 for v in raw:h=((h^v)*0x100000001b3)&0xffffffffffffffff
 return f'0x{h:016x}'
def decode(data,index):
 raw=(data/'tyrian.shp').read_bytes();o=struct.unpack_from('<13i',raw,2);bank=raw[o[7]:o[8]];assert len(bank)==32060 and hashlib.sha256(bank).hexdigest()=='9bba1e94d38df61f152412c226bfd6df235e42027c9143c5961d4a5add853a68'
 mask=np.zeros((14,12),bool);indices=np.zeros((14,12),np.uint8);p=struct.unpack_from('<H',bank,2*(index-1))[0];x=y=0
 while True:
  v=bank[p];p+=1
  if v==15:break
  x+=v&15;n=v>>4
  if not n:y+=1;x-=12
  else:
   for _ in range(n):
    assert 0<=x<12 and 0<=y<14
    indices[y,x]=bank[p];mask[y,x]=True;p+=1;x+=1
 assert mask.sum()==45
 return bank,mask,indices
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args(argv);a.out=a.out.resolve()
 if a.out==ROOT or ROOT in a.out.parents:raise ValueError('Output must be outside the repository')
 sources,binding=load_approved_sources();a.out.mkdir(parents=True,exist_ok=True);inventory={}
 for b in (112,113):
  bank,mask,indices=decode(a.data,b);rgba=register_rgba(sources[b],mask)
  out=Image.fromarray(rgba,'RGBA');stem=f'enemy-orb112113-{b}-8';out.save(a.out/(stem+'.png'));raw=struct.pack('<4s6I',b'HDR1',1420000+b,8,12,14,0,0)+out.tobytes();(a.out/(stem+'.hda')).write_bytes(raw)
  inventory[str(b)]={'source_bank':'tyrian.shp/player-shot-bank','source_bank_bytes':len(bank),'source_bank_fnv64':fnv(bank),'source_index':b,'material_role':142,'logical_size':[12,14],'density':8,'anchor':[0,0],'source_occupied_cells':45,'retained_source_sha256':PINS[b],'rgba_fnv64':fnv(out.tobytes()),'hda_sha256':hashlib.sha256(raw).hexdigest(),'source_png_sha256':hashlib.sha256((a.out/(stem+'.png')).read_bytes()).hexdigest()}
 (a.out/'art-inventory.json').write_text(json.dumps(inventory,indent=2)+'\n',encoding='utf-8',newline='\n')
 (a.out/'source-binding.json').write_text(json.dumps(binding,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(inventory,indent=2))
if __name__=='__main__':main()
