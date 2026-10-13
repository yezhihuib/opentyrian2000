#!/usr/bin/env python3
"""Reproduce the locked large-heading vector atlas without game data. No runtime wrapper."""
from pathlib import Path
import argparse,hashlib,json,struct
from PIL import Image,ImageDraw,ImageChops
ROOT=Path(__file__).resolve().parent

def fnv(b):
 n=14695981039346656037
 for x in b:n=((n^x)*1099511628211)&0xffffffffffffffff
 return n

def safe_output(arg):
 p=Path(arg).expanduser().absolute()
 for q in [p,*p.parents]:
  if q.is_symlink():raise ValueError('output path must not contain symlinks')
 p=p.resolve()
 if p==ROOT or ROOT in p.parents or p in ROOT.parents:raise ValueError('output must be external to source and not its ancestor')
 if p.exists():raise ValueError('output must be a new non-existing directory')
 return p

def curve_paths(curves):
 paths=[]
 for line in curves:
  pts=[]
  for c in line:
   if c[0] in ['M','L']:pts.append(c[1:])
   else:
    p0=pts[-1];c1=c[1:3];c2=c[3:5];p3=c[5:7]
    for j in range(1,33):
     t=j/32;pts.append([(1-t)**3*p0[k]+3*(1-t)**2*t*c1[k]+3*(1-t)*t*t*c2[k]+t**3*p3[k] for k in [0,1]])
  paths.append(pts)
 return paths

def build(out):
 v=json.loads((ROOT/'sources/menu-large-vectors.json').read_text());c=json.loads((ROOT/'contract.json').read_text())
 assert v['density']==4 and v['atlas_size']==[1216,384]
 atlas=Image.new('RGBA',(1216,384));roles=Image.new('L',atlas.size);svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1216" height="384" viewBox="0 0 304 96">']
 for g in v['glyphs']:
  sid=g['sprite_id'];w=g['width'];h=g['height'];box=g['source_opaque_bbox_half_open'];stroke=g['stroke_width_logical'];paths=curve_paths(g['curve_commands']);assert paths==g['paths'];a=Image.new('L',(w*32,h*32))
  if not g['blank_original']:
   d=ImageDraw.Draw(a)
   for line in paths:
    pts=[(round(x*32),round(y*32)) for x,y in line]
    if len(pts)==1:
     x,y=pts[0];rr=stroke/2*32;d.ellipse((x-rr,y-rr,x+rr,y+rr),fill=255)
    else:d.line(pts,fill=255,width=round(stroke*32),joint='curve')
   clip=Image.new('L',a.size);ImageDraw.Draw(clip).rectangle((box[0]*32,box[1]*32,box[2]*32-1,box[3]*32-1),fill=255);a=ImageChops.multiply(a,clip)
  a=a.resize((w*4,h*4),Image.Resampling.BOX);ab=a.tobytes();rb=bytearray(len(ab))
  for y in range(h*4):
   if g['blank_original']:break
   yy=(y+.5)/4-box[1];bottom=box[3]-(y+.5)/4;role=15 if yy<.6 else (14 if yy<1.275 else (12 if bottom<.525 else 13))
   for x in range(w*4):
    i=y*w*4+x
    if ab[i]:rb[i]=role
  assert hashlib.sha256(ab).hexdigest()==g['coverage_sha256'];assert hashlib.sha256(rb).hexdigest()==g['role_sha256']
  rgba=bytearray(len(ab)*4)
  for i,alpha in enumerate(ab):
   if alpha:rgba[i*4:i*4+4]=bytes((255,255,255,alpha))
  tile=Image.frombytes('RGBA',a.size,bytes(rgba));ax,ay,_,_=g['atlas_box_half_open'];atlas.paste(tile,(ax,ay));roles.paste(Image.frombytes('L',a.size,bytes(rb)),(ax,ay))
  if paths:
   x0,y0,x1,y1=box;svg.append(f'<defs><clipPath id="g{sid}"><rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}"/></clipPath></defs>');svg.append(f'<g transform="translate({ax/4} {ay/4})" clip-path="url(#g{sid})" fill="none" stroke="white" stroke-width="{stroke}" stroke-linejoin="round" stroke-linecap="butt">')
   for line in g['curve_commands']:
    if len(line)==1:svg.append(f'<circle cx="{line[0][1]}" cy="{line[0][2]}" r="{stroke/2}" fill="white" stroke="none"/>')
    else:svg.append('<path d="'+' '.join(c[0]+' '+' '.join(map(str,c[1:])) for c in line)+'"/>')
   svg.append('</g>')
 svg.append('</svg>');alpha=atlas.getchannel('A').tobytes();role=roles.tobytes();payload=alpha+role
 out.mkdir(parents=True);atlas.save(out/'menu-large-coverage-4x.png');roles.save(out/'menu-large-roles-4x.png');(out/'menu-large-coverage-4x.alpha.bin').write_bytes(alpha);(out/'menu-large-roles-4x.bin').write_bytes(role);(out/'menu-large-vector-atlas.svg').write_text('\n'.join(svg)+'\n')
 result={p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'fnv64':f'{fnv(p.read_bytes()):016x}'} for p in sorted(out.iterdir())}
 for name,expected in c.get('expected_outputs',{}).items():
  assert result[name]==expected,(name,result[name],expected)
 print(json.dumps({'outputs':result,'payload_fnv64':f'{fnv(payload):016x}','glyphs':60,'visible':53,'materials':'alpha and authored shade role; caller palette/brightness remains live'},indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args()
 try:out=safe_output(a.output);build(out)
 except (ValueError,AssertionError) as e:p.exit(2,str(e)+'\n')
