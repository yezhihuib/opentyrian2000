#!/usr/bin/env python3
"""Rebuild the selected forest13 bases, masks and continuous canopy from generated-only frozen sources."""
import argparse,hashlib,json,os,shutil,struct,subprocess,tempfile
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',required=True,type=Path);p.add_argument('--cxx',default=os.environ.get('CXX','c++'));a=p.parse_args();target=a.output_dir.expanduser()
 if target.is_symlink() or target.exists():raise ValueError('Output must be a new external directory, not an existing path or symlink')
 out=target.resolve()
 if out==ROOT or out.is_relative_to(ROOT) or ROOT.is_relative_to(out):raise ValueError('Output must be outside the source package')
 con=json.loads((ROOT/'contracts/composition.json').read_text());cxx=shutil.which(a.cxx)
 if cxx is None:raise ValueError('C++17 compiler is required')
 for rel,v in con['inputs'].items():
  f=ROOT/rel
  if f.is_symlink() or not f.is_file() or not f.resolve().is_relative_to(ROOT) or sha(f.read_bytes())!=v['file_sha256']:raise ValueError('Source file mismatch: '+rel)
  if 'decoded_mode'in v:
   with Image.open(f)as im:
    if list(im.size)!=v['size'] or sha(im.convert(v['decoded_mode']).tobytes())!=v['decoded_sha256']:raise ValueError('Source pixels mismatch: '+rel)
 def pixels(rel,mode='RGBA'):return Image.open(ROOT/rel).convert(mode).tobytes()
 results=[];final={}
 with tempfile.TemporaryDirectory(prefix='forest13 build ')as td:
  t=Path(td)
  for name in ['compose_bases','compose_wrap']:subprocess.run([cxx,'-O2','-std=c++17',str(ROOT/'source'/(name+'.cpp')),'-o',str(t/name)],check=True)
  for name,rel in [('frame','generated-geometry-frame.png'),('grass','frozen-generated-grass69.png'),('front234','generated-front234.png')]:(t/name).write_bytes(pixels('source/'+rel))
  for i in con['ids']:(t/f'w{i}').write_bytes(pixels(f'source/authored-masks/{i}.png','L'))
  subprocess.run([str(t/'compose_bases'),str(t)],check=True)
  (t/'offset').write_bytes(pixels('source/generated-atlas-half-offset.png'));(t/'repair').write_bytes(pixels('source/generated-wrap-calibrated.png'))
  subprocess.run([str(t/'compose_wrap'),str(t/'offset'),str(t/'repair'),str(t/'atlas'),str(t/'wrap-weight')],check=True)
  atlas=(t/'atlas').read_bytes()
  if len(atlas)!=768*896*4 or sha(atlas)!=con['atlas']['rgba_sha256'] or any(atlas[j]!=255 for j in range(3,len(atlas),4)):raise ValueError('Atlas pixel mismatch')
  final['selected/atlas.png']=('RGBA',(768,896),atlas)
  for v in con['selected']:
   i=v['source_id'];rgba=(t/f'base{i}').read_bytes();mask=(t/f'mask{i}').read_bytes();hda=b'HDR1'+struct.pack('<6I',*v['header_u32'])+rgba
   if len(rgba)!=192*224*4 or sha(rgba)!=v['base_rgba_sha256'] or any(rgba[j]!=255 for j in range(3,len(rgba),4)):raise ValueError(f'Base pixel mismatch:{i}')
   if len(mask)!=192*224 or sha(mask)!=v['mask_l8_sha256']:raise ValueError(f'Mask pixel mismatch:{i}')
   if sha(hda)!=v['hda_sha256']:raise ValueError(f'HDA byte mismatch:{i}')
   final[v['base_path']]=('RGBA',(192,224),rgba);final[v['mask_path']]=('L',(192,224),mask);final[v['hda_path']]=hda;results.append({'source_id':i,'base_rgba_exact':True,'mask_l8_exact':True,'hda_bytes_exact':True})
 out.mkdir(parents=True)
 for rel,item in final.items():
  dest=out/rel;dest.parent.mkdir(parents=True,exist_ok=True)
  if isinstance(item,bytes):dest.write_bytes(item)
  else:mode,size,b=item;Image.frombytes(mode,size,b).save(dest,compress_level=9)
 report={'schema':'forest13-world-canopy-rebuild-result-v1','generated_only':True,'original_game_data_required':False,'atlas_rgba_exact':True,'selected_pixel_outputs':27,'HDA_outputs':13,'results':results};(out/'rebuild-result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
