#!/usr/bin/env python3
"""Rebuild only generated artwork. No original game data, runtime, network or repo write."""
from pathlib import Path
import sys,subprocess,tempfile,json,hashlib,struct,importlib.util,shutil
from PIL import Image
sys.dont_write_bytecode=True
P=Path(__file__).resolve().parent;S=P/'source'
GRAY=[121,122,123,124,125,131,132,133,134,135,141,142,143,144,151,152,153,154]
PURPLE=[150,156,157,158,159,160,166,168,169,170,176,177,178]
ACTORS=[279,281,283,245,169,207,273,275,277]
SIX=[121,122,123,141,142,143]
RING=[(121,0,0,'ES'),(122,192,0,'WES'),(123,576,0,'WS'),(124,0,224,'ENS'),(125,576,224,'WNS'),(131,0,448,'ENS'),(133,576,448,'WNS'),(134,0,672,'ENS'),(135,576,672,'WNS'),(141,0,896,'EN'),(142,192,896,'WEN'),(143,576,896,'WN')]
def run(*a):subprocess.run([str(x) for x in a],check=True,stdout=subprocess.DEVNULL)
def raw(src,out):run('convert',src,'-depth','8','rgba:'+str(out));return out
def crop(src,x,y,out):run('convert',src,'-crop',f'192x224+{x}+{y}','+repage','-depth','8','rgba:'+str(out));return out
def png(src,out):run('convert','-size','192x224','-depth','8','rgba:'+str(src),'-strip','PNG32:'+str(out))
def sha(b):return hashlib.sha256(b).hexdigest()
def rebuild(out):
 out=out.resolve()
 if out==P or P in out.parents or out in P.parents:raise ValueError('Output must be outside the immutable package and its ancestors')
 out.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory(prefix='tyrian-island-rebuild-') as td:
  w=Path(td);exe={}
  for src in sorted((S/'cpp').glob('*.cpp')):
   q=w/src.stem;run('c++','-O2','-std=c++17',src,'-o',q);exe[src.stem]=q
  # Authored six-rim precursor retained for its contour and lower cliff faces.
  old=w/'six-old.rgba';art=w/'six-art.rgba';old.write_bytes(b''.join(Image.open(S/'accepted-gray'/f'terrain-shapesz-{i}-8.png').convert('RGBA').tobytes() for i in SIX))
  chunks=[]
  for k,i in enumerate(SIX):chunks.append(crop(S/'registered/registered-canonical-edge-v1.png',(k%3)*192,0 if k<3 else 448,w/f'six-art-{i}.rgba').read_bytes())
  art.write_bytes(b''.join(chunks));top=raw(S/'registered/registered122-wrap-v1.png',w/'six-top.rgba');bottom=raw(S/'registered/registered142-wrap-v1.png',w/'six-bottom.rgba');sixout=w/'six-out.rgba';run(exe['register_six_rims'],old,art,top,bottom,sixout);sixbytes=sixout.read_bytes();oldtile={}
  for i in GRAY:
   q=w/f'old-{i}.rgba'
   if i in SIX:k=SIX.index(i);q.write_bytes(sixbytes[k*172032:(k+1)*172032])
   else:raw(S/'accepted-gray'/f'terrain-shapesz-{i}-8.png',q)
   oldtile[i]=q
  # Large-stone material with explicitly painted opposite-edge wrapping.
  a=raw(S/'registered/rolled-large-base.png',w/'rolled-base.rgba');b=raw(S/'registered/rolled-large-edit.png',w/'rolled-edit.rgba');base=w/'base.rgba';run(exe['register_material'],a,b,base)
  selected={151:base}
  for i,x,y in [(132,0,0),(152,192,0),(153,0,224)]:
   q=crop(S/'registered/registered-large-variants-v2.png',x,y,w/f'fill-{i}.rgba');o=w/f'selected-{i}.rgba';run(exe['compose_fill'],base,q,o);selected[i]=o
  for i in [144,154]:
   q=raw(S/'registered'/f'crater{i}.png',w/f'fill-{i}.rgba');o=w/f'selected-{i}.rgba';run(exe['compose_fill'],base,q,o);selected[i]=o
  for i,x,y,faces in RING:
   q=crop(S/'registered/registered-structural-ring-v2.png',x,y,w/f'ring-{i}.rgba');o=w/f'selected-{i}.rgba';run(exe['compose_structural_ring'],i,faces,oldtile[i],q,base,o);selected[i]=o
  for i,x,y,side in [(124,0,224,0),(125,576,224,1),(131,0,448,0),(133,576,448,1),(134,0,672,0),(135,576,672,1)]:
   q=crop(S/'registered/registered-lateral-depth-v3.png',x,y,w/f'depth-{i}.rgba');o=w/f'depth-final-{i}.rgba';run(exe['apply_lateral_depth'],selected[i],q,side,o);selected[i]=o
  for i in GRAY:
   o=w/f'clean-{i}.rgba';run(exe['cleanup_edge_specks'],selected[i],o);selected[i]=o;png(o,out/f'terrain-shapesz-{i}-8.png')
  for i in PURPLE:
   a=raw(S/'accepted-purple'/f'terrain-shapesz-{i}-8.png',w/f'purple-{i}.rgba');o=w/f'purple-final-{i}.rgba';run(exe['replace_gray_backing'],a,base,0,o,w/f'purple-mask-{i}.gray');png(o,out/f'terrain-shapesz-{i}-8.png')
  for j,i in enumerate(ACTORS):
   a=raw(S/'accepted-entities'/f'newsh2-base{i}-8.png',w/f'entity-{i}.rgba');o=w/f'entity-final-{i}.rgba';shift=[0,-8,8][j//3];run(exe['replace_gray_backing'],a,base,shift,o,w/f'entity-mask-{i}.gray');png(o,out/f'enemy-newsh2-{i}-8.png')
  # Same original turret exporter/body/core phases; only the generated backing changes.
  t=w/'turret';t.mkdir();shutil.copyfile(S/'imagegen-originals/generated-turret-atlas.png',t/'generated-turret-atlas.png');shutil.copyfile(out/'terrain-shapesz-144-8.png',t/'frozen144-8.png')
  spec=importlib.util.spec_from_file_location('turret_upstream',S/'turret-upstream-export.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.P=t;m.export(t/'frames')
  for i in [153,155,157]:run('convert',t/'frames'/f'newsh2-base{i}-8.png','-strip','PNG32:'+str(out/f'enemy-newsh2-{i}-8.png'))
  headers=json.loads((P/'headers.json').read_text());result={}
  for name,fields in headers.items():
   p=out/(name+'.png');rgba=Image.open(p).convert('RGBA').tobytes();blob=b'HDR1'+struct.pack('<6i',*fields)+rgba;(out/(name+'.hda')).write_bytes(blob);result[name]={'rgba_sha256':sha(rgba),'hda_sha256':sha(blob),'png_sha256':sha(p.read_bytes())}
  expected=P/'expected-output.json'
  if expected.exists():
   E=json.loads(expected.read_text())
   for n,v in E.items():
    for k in ['rgba_sha256','hda_sha256']:
     if result[n][k]!=v[k]:raise RuntimeError(f'Rebuild mismatch: {n} {k}')
  (out/'rebuild-receipt.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'verified':len(result),'output':str(out)}))
if __name__=='__main__':
 if len(sys.argv)!=2:raise SystemExit('Usage: rebuild.py OUTPUT_DIRECTORY_OUTSIDE_PACKAGE')
 rebuild(Path(sys.argv[1]))
