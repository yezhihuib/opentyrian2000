#!/usr/bin/env python3
"""Build all 38 missing ASTEROID2 terrain candidates. Never edits native data.

Generated RGB only. Native zero/nonzero coverage is derived from caller-owned
input; it is not bundled as a separate source mask. No native RGB border copy.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import struct
import sys
import numpy as np
import PIL
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'assets/hd/artwork/level2-terrain-completion-v1'
GROUPS = {
 'bronze-pit': ((299,300),(309,310)),
 'broken-pit': ((306,307),(316,317)),
 'cross-pit': ((319,320),(329,330)),
 'bronze-column': ((318,),(328,)),
 'twin-shafts': ((423,424,421,422),(433,434,431,432)),
 'fixtures': ((339,347,348,357),(358,359,385,389)),
 'architecture': ((410,400,384,419),(416,417,418,420)),
}
IDS = tuple(sorted(i for rows in GROUPS.values() for row in rows for i in row))
RAW_PINS = {
 'broken-pit':'2594c03e2ea494ddefeedfbbe047d49c8678f36c23b21aa4863820dcccb0f8cc',
 'fixtures':'ba3d0e601324639be2642f3d03d94156ecf6b09941a26e3eeb8ec8b06341fd3f',
 'architecture':'3b2d844f7b72649bf29381387fa43ad83070d791baf6241dbe9e6cf569d86bda',
 'cross-pit':'69736da9eec094d3ae08514adf8ee273268ec49200fe33c6e84051fce742eae0',
 'bronze-pit':'602b601956c9868cdeda4bf497de8d8dd16b390db094bf31b2f8df98a68c4fb3',
 'bronze-column':'f6027c511bb6b090b0160d18ac1492084860de7733f9406e99a11e6dade4e368',
 'twin-shafts':'aebe232b6b0eeded3f226f40bf524c95686e49d7c5a5413764c5cacd6de6d5ee',
}
MASTER_SIZES = {name: ((821, 1915) if name == 'bronze-column' else
 (1161, 1355) if len(rows[0]) == 2 else (1642, 958))
 for name, rows in GROUPS.items()}
SHAPES_PIN='3ecc9b59c82e8e7d9c91889aac7d337ca28a59519c4970e256250e4603a9b248'

def sha(data): return hashlib.sha256(data).hexdigest()

def checked(path, pin, size=None):
 path=Path(path)
 if any(p.is_symlink() for p in (path,*path.parents)) or not path.is_file():
  raise ValueError('Regular nonsymlink input required: '+str(path))
 if path.stat().st_size > 20*1024*1024: raise ValueError('Oversized input')
 data=path.read_bytes()
 if (size is not None and len(data)!=size) or sha(data)!=pin:
  raise ValueError('Input identity mismatch: '+path.name)
 return data

def decode_shapes(data):
 pos=0; shapes={}
 for tile in range(1,601):
  if pos>=len(data) or data[pos] not in (0,1): raise ValueError('Invalid shape flag')
  blank=data[pos];pos+=1
  raw=bytes(672) if blank else data[pos:pos+672]
  pos+=0 if blank else 672
  if len(raw)!=672: raise ValueError('Truncated shape')
  shapes[tile]=raw
 if pos!=318456 or len(data)!=318976: raise ValueError('Unsupported shape layout')
 return shapes

def crop_group(master, rows):
 """Resize whole coherent master once, THEN cut at exact shared boundaries."""
 rows=tuple(tuple(row) for row in rows)
 if not rows or not rows[0] or any(len(row)!=len(rows[0]) for row in rows):
  raise ValueError('Empty or ragged group')
 ids=[tile for row in rows for tile in row]
 if any(type(tile) is not int or not 1 <= tile <= 600 for tile in ids) or len(set(ids))!=len(ids):
  raise ValueError('Invalid or duplicate tile identity')
 cols=len(rows[0])
 canvas=master.convert('RGB').resize((cols*192,len(rows)*224),Image.Resampling.LANCZOS)
 return {tile:np.array(canvas.crop((x*192,y*224,(x+1)*192,(y+1)*224)))
         for y,row in enumerate(rows) for x,tile in enumerate(row)}

def apply_coverage(rgb, source):
 if rgb.shape!=(224,192,3) or rgb.dtype!=np.uint8 or len(source)!=672: raise ValueError('Invalid tile geometry')
 mask=np.repeat(np.repeat(np.frombuffer(source,dtype=np.uint8).reshape(28,24)!=0,8,axis=0),8,axis=1)
 rgba=np.zeros((224,192,4),dtype=np.uint8);rgba[:,:,:3]=rgb;rgba[:,:,3]=mask*255
 rgba[~mask,:3]=0
 return rgba

def hda(tile, rgba):
 if rgba.shape!=(224,192,4) or rgba.dtype!=np.uint8: raise ValueError('Invalid RGBA')
 return struct.pack('<4s4I2i',b'HDR1',2010000+tile,8,24,28,0,0)+rgba.tobytes()

def build(data_dir, output, art=ART):
 data_dir,output,art=map(Path,(data_dir,output,art))
 if output.exists() or output.is_symlink(): raise ValueError('Output must be fresh; no overwrite')
 if any(p.is_symlink() for p in output.parents): raise ValueError('Output symlink ancestor')
 if not output.parent.is_dir(): raise ValueError('Output parent must exist')
 for inp in (data_dir.resolve(),art.resolve()):
  if output.resolve().is_relative_to(inp) or inp.is_relative_to(output.resolve()):
   raise ValueError('Output overlaps input')
 native=decode_shapes(checked(data_dir/'shapesz.dat',SHAPES_PIN,318976))
 pending={};entries=[]
 for name,rows in GROUPS.items():
  raw=checked(art/(name+'.png'),RAW_PINS[name])
  with Image.open(io.BytesIO(raw)) as master:
   if master.format!='PNG' or master.mode!='RGB' or master.size!=MASTER_SIZES[name]:
    raise ValueError('Invalid master geometry or mode: '+name)
   tiles=crop_group(master,rows)
  for tile,rgb in tiles.items():
   rgba=apply_coverage(rgb,native[tile]);payload=hda(tile,rgba)
   stem=f'terrain-shapesz-{tile}-8';pending[stem+'.hda']=payload
   bio=io.BytesIO();Image.fromarray(rgba).save(bio,format='PNG');pending[stem+'.png']=bio.getvalue()
   entries.append({'id':tile,'family':name,'source_sha256':sha(native[tile]),
    'source_zero_cells':native[tile].count(0),'hda_sha256':sha(payload),
    'rgba_sha256':sha(rgba.tobytes()),'png_sha256':sha(bio.getvalue()),
    'opaque_hd_pixels':int(np.count_nonzero(rgba[:,:,3])),
    'original_rgb_copied_pixels':0})
 if len(entries)!=38 or len(set(e['id'] for e in entries))!=38: raise ValueError('Incomplete batch')
 report={'schema':'level2-terrain-completion-v1','scale':8,'source_shapes_sha256':SHAPES_PIN,
  'generated_master_pins':RAW_PINS,'generated_master_sizes':MASTER_SIZES,
  'build_versions':{'Pillow':PIL.__version__,'numpy':np.__version__},'group_layouts':GROUPS,'ids':list(IDS),
  'resource_count':38,'art_tool':'built-in image generation',
  'coverage':'Exact caller-derived zero/nonzero coverage; transparent RGB is zero.',
  'rgb':'Only resized image-generated masters. No copied native RGB or native perimeter.',
  'status':'complete resource candidate batch; NOT gameplay-qualified',
  'runtime_integrated':False,'integration_scope':'This resource producer does not establish runtime admission; see separate adapter validation.','all_neighbor_joins_verified':False,
  'source_data_included':False,'source_derived_geometry':True,
  'tiles':sorted(entries,key=lambda e:e['id'])}
 pending['MANIFEST.json']=(json.dumps(report,indent=2)+'\n').encode()
 output.mkdir()
 for name,content in pending.items(): (output/name).write_bytes(content)
 return report

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--data',type=Path,required=True)
 ap.add_argument('--output',type=Path,required=True);ap.add_argument('--art',type=Path,default=ART)
 args=ap.parse_args();report=build(args.data,args.output,args.art)
 print(json.dumps({'resource_count':report['resource_count'],'output':str(args.output),'status':report['status']}))
if __name__=='__main__':
 try:main()
 except (ValueError,OSError) as e:sys.exit(str(e))
