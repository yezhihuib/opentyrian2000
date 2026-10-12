#!/usr/bin/env python3
"""Rebuild nine authored grass tiles from bundled generated sources only."""
import argparse, hashlib, json, os, shutil, struct, subprocess, tempfile
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parent
def sha(b): return hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--cxx',default=os.environ.get('CXX','c++'));args=p.parse_args()
 contract=json.loads((ROOT/'contract.json').read_text());out=args.output_dir.expanduser().resolve()
 if out==ROOT or ROOT.is_relative_to(out) or out.is_relative_to(ROOT) or (out.exists() and any(out.iterdir())):raise ValueError('Use an empty, separate output directory')
 compiler=shutil.which(args.cxx)
 if compiler is None:raise ValueError('C++17 compiler not found')
 for relative,expected in contract['inputs'].items():
  f=ROOT/relative
  if f.is_symlink() or not f.is_file() or not f.resolve().is_relative_to(ROOT) or sha(f.read_bytes())!=expected['file_sha256']:raise ValueError('Canonical source mismatch: '+relative)
  if f.suffix=='.png':
   with Image.open(f)as im:
    if list(im.size)!=expected['size'] or sha(im.convert('RGBA').tobytes())!=expected['rgba_sha256']:raise ValueError('Decoded source mismatch: '+relative)
 images={n:Image.open(ROOT/'source'/n).convert('RGBA')for n in ['generated-family-v1.png','generated-interior-v2.png','generated-fringe-v3.png','frozen-generated-sand47.png']}
 with tempfile.TemporaryDirectory(prefix='grass9 build ')as t:
  work=Path(t);executables={}
  for name in ['register_vegetation','register_interior','register_footprint']:
   exe=work/name;subprocess.run([compiler,'-O2','-std=c++17',str(ROOT/'source'/(name+'.cpp')),'-o',str(exe)],check=True);executables[name]=exe
  def run(name,inputs,extra=()):
   paths=[]
   for k,b in enumerate(inputs):f=work/f'input{k}.rgba';f.write_bytes(b);paths.append(str(f))
   dest=work/'selected.rgba';subprocess.run([str(executables[name]),*paths,str(dest),*map(str,extra)],check=True);return dest.read_bytes()
  sand=images['frozen-generated-sand47.png'].tobytes();v2={}
  for i in contract['ids']:
   x,y=contract['crop_origins_v1_v2'][str(i)];box=(x,y,x+192,y+224)
   initial=images['generated-family-v1.png'].crop(box).tobytes();one=run('register_vegetation',[initial,sand],[i]);interior=images['generated-interior-v2.png'].crop(box).tobytes();v2[i]=run('register_interior',[one,interior,sand])
  six=Image.new('RGBA',(384,672))
  for y,row in enumerate(contract['six_layout']):
   for x,i in enumerate(row):six.paste(Image.frombytes('RGBA',(192,224),v2[i]),(x*192,y*224))
  selected=run('register_footprint',[six.tobytes(),images['generated-fringe-v3.png'].tobytes()]);six=Image.frombytes('RGBA',(384,672),selected);final=dict(v2)
  for y,row in enumerate(contract['six_layout']):
   for x,i in enumerate(row):final[i]=six.crop((x*192,y*224,(x+1)*192,(y+1)*224)).tobytes()
 (out/'output').mkdir(parents=True);(out/'runtime-overlay').mkdir();reports=[]
 for item in contract['selected']:
  i=item['source_id'];rgba=final[i]
  if len(rgba)!=192*224*4 or sha(rgba)!=item['rgba_sha256']:raise ValueError(f'Selected RGBA mismatch: {i}')
  hda=b'HDR1'+struct.pack('<6I',*item['header_u32'])+rgba
  if sha(hda)!=item['hda_sha256']:raise ValueError(f'Selected HDA mismatch: {i}')
  stem=f'terrain-shapesz-{i}-8';Image.frombytes('RGBA',(192,224),rgba).save(out/'output'/(stem+'.png'),compress_level=9);(out/'runtime-overlay'/(stem+'.hda')).write_bytes(hda)
  reports.append({'id':i,'rgba_sha256':sha(rgba),'hda_sha256':sha(hda),'exact':True})
 report={'schema':'grass9-v3-rebuild-result','generated_only':True,'original_data_required':False,'selected_count':len(reports),'results':reports};(out/'rebuild-result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
