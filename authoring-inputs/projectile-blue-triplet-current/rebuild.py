"""Check/rebuild selected generated-only candidates; no game input required.
Default is check-only. --write writes three PNGs and payload-pins.json only.
"""
from pathlib import Path
import argparse,hashlib,io,json,stat,struct
from PIL import Image,__version__
ROOT=Path(__file__).resolve().parent
REGISTRATION_SHA256='193e04f50c741211b6bad41229ff3a192679335b620dadbed0cb8878336f7119'
COVERAGE_SHA256='c667b52db7c28fd8d9ee96ffd0531a16b5cb4875c05995c2026bf381ab38d1c9'
sha=lambda b:hashlib.sha256(b).hexdigest()
def fnv(b):
 v=14695981039346656037
 for c in b:v=((v^c)*1099511628211)&((1<<64)-1)
 return f'{v:016x}'
def safe(root,name):
 p=Path(name)
 if p.is_absolute() or '..' in p.parts or str(p)!=name or '\\' in name:raise ValueError('Unsafe path')
 q=root/p
 for a in [root,*root.parents,*[root/Path(*p.parts[:i]) for i in range(1,len(p.parts)+1)]]:
  if a.is_symlink():raise ValueError('Linked path')
 if q.exists() and (not stat.S_ISREG(q.lstat().st_mode) or q.stat().st_nlink!=1):raise ValueError('Nonregular/hardlinked input or output')
 return q

def products(root):
 regraw=safe(root,'registration.json').read_bytes();covraw=safe(root,'coverage-contract.json').read_bytes()
 if sha(regraw)!=REGISTRATION_SHA256 or sha(covraw)!=COVERAGE_SHA256:raise ValueError('Changed closed registration/coverage')
 r=json.loads(regraw);coverage=json.loads(covraw)
 if __version__!='12.3.0':raise ValueError('Fixed Pillow12.3.0 required')
 outputs={};rows=[]
 for source,t in zip(r['sources'],r['tiles']):
  s=source['selector'];m=coverage['members'][str(s)];name=source['source_png'].removeprefix('authoring-inputs/projectile-blue-triplet-current/')
  raw=safe(root,name).read_bytes()
  if sha(raw)!=source['source_sha256']:raise ValueError('Changed selected master')
  with Image.open(io.BytesIO(raw)) as im:
   if im.mode!='RGBA' or im.format!='PNG' or list(im.size)!=source['source_size'] or getattr(im,'n_frames',1)!=1:raise ValueError('Changed master geometry')
   tile=im.crop(tuple(source['crop'])).resize((96,112),Image.Resampling.LANCZOS)
  raw=bytearray(tile.tobytes());mask=''.join(t['native_support_rows'])
  if mask!=m['native_mask']:raise ValueError('Changed native support')
  for y in range(112):
   for x in range(96):
    i=(y*96+x)*4
    if mask[(y//8)*12+x//8]=='0' or raw[i+3]==0:raw[i:i+4]=b'\0'*4
  matrix=[[max(raw[((y*8+dy)*96+x*8+dx)*4+3] for dy in range(8) for dx in range(8)) for x in range(12)] for y in range(14)]
  zero=[[y,x] for y in range(14) for x in range(12) if mask[y*12+x]=='1' and matrix[y][x]==0]
  used=[matrix[y][x] for y in range(14) for x in range(12) if mask[y*12+x]=='1']
  distribution=dict(at_least200=sum(v>=200 for v in used),from1_to199=sum(0<v<200 for v in used),fully_transparent=used.count(0))
  if matrix!=m['max_alpha_per_native_cell'] or zero!=m['fully_transparent_native_cells'] or distribution!=m['cell_alpha_distribution']:raise ValueError('Changed exact alpha contract')
  if sha(raw)!=m['payload_sha256'] or fnv(raw)!=m['payload_fnv64']:raise ValueError('Changed payload')
  out=io.BytesIO();Image.frombytes('RGBA',(96,112),bytes(raw)).save(out,format='PNG',compress_level=source['png_compress_level']);png=out.getvalue()
  if sha(png)!=m['png_sha256'] or sha(struct.pack('<4s6I',b'HDR1',*m['header_values'])+raw)!=m['hda_sha256']:raise ValueError('Changed exact transport')
  outputs[t['output']]=png;a=raw[3::4]
  rows.append(dict(selector=s,png=t['output'],png_sha256=sha(png),rgba_sha256=sha(raw),rgba_fnv1a64=fnv(raw),rgba_bytes=len(raw),occupied_native_cells=len(used),max_alpha_per_native_cell=matrix,cell_alpha_distribution=distribution,fully_transparent_native_cells=zero,first_row_alpha=list(a[:96]),last_row_alpha=list(a[-96:]),nonzero_alpha_pixels=sum(v>0 for v in a),opaque_pixels=a.count(255),soft_pixels=sum(0<v<255 for v in a),transparent_pixels=a.count(0),unsupported_RGBA_all_zero=True,all_alpha0_RGBA_zero=True))
 pins=dict(status='AUTHORING_REBUILD_ONLY_NOT_FULL_RUNTIME_QUALIFICATION',epoch=r['epoch'],registration_sha256=sha(regraw),coverage_contract_sha256=sha(covraw),source_pins={str(s['selector']):s['source_sha256'] for s in r['sources']},canvas_per_tile=[96,112],native_canvas=[12,14],anchor=[0,0],density=8,tiles=rows,native_RGB_used=False,game_data_required_for_rebuild=False,alpha_promoted=False,Christmas='classic fallback',legacy_erratum='Old shared-master adjacency/seam thresholds and every-native-cell>=200 are not the selected epoch contract; exact matrix/payload/endpoints replace them prospectively, never retroactively.')
 outputs['payload-pins.json']=(json.dumps(pins,indent=2)+'\n').encode()
 return outputs

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--write',action='store_true');a=p.parse_args();outputs=products(a.root)
 for name,raw in outputs.items():
  q=safe(a.root,name)
  if a.write:q.write_bytes(raw)
  elif not q.is_file() or q.read_bytes()!=raw:raise ValueError('Stale generated product: '+name)
 print(json.dumps({'status':'PASS_AUTHORING_REBUILD_ONLY','files':{p:sha(b) for p,b in outputs.items()}},indent=2))
if __name__=='__main__':main()
