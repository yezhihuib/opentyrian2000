from pathlib import Path
from PIL import Image,ImageChops,ImageDraw
import hashlib,json
import sys
O=Path(sys.argv[1]).resolve();C=O/'captures';result={}
for w,h in [(640,400),(1280,800),(913,599)]:
 ims={n:Image.open(C/f'{n}-{w}x{h}-hd.bmp').convert('RGB') for n in ['fonts','metal','talon','front','generator','menu']}
 classic=Image.open(C/f'fonts-{w}x{h}-classic.bmp').convert('RGB')
 for n in ims:assert ImageChops.difference(classic,Image.open(C/f'{n}-{w}x{h}-classic.bmp').convert('RGB')).getbbox() is None
 pairs={}
 for a,b in [('fonts','metal'),('metal','talon'),('talon','front'),('front','generator'),('generator','menu')]:
  box=ImageChops.difference(ims[a],ims[b]).getbbox();assert box is not None;(pairs)[a+'-'+b]=box
  if b in ('front','generator'):
   import math
   x,y,r,t=(61,48,94,82) if b=='front' else (62,84,93,119)
   allowance=2 if (w,h)==(913,599) else 0
   bound=(math.floor(x*w/320)-allowance,math.floor(y*h/200)-allowance,math.ceil(r*w/320)+allowance,math.ceil(t*h/200)+allowance)
   assert box[0]>=bound[0] and box[1]>=bound[1] and box[2]<=bound[2] and box[3]<=bound[3],(b,box,bound)
 result[f'{w}x{h}']={'all_classic_exact':True,'hd_delta_bboxes':pairs}
assert len({hashlib.sha256(p.read_bytes()).hexdigest() for p in C.glob('*.index8')})==1
result['index8_all_root_variants_exact']=True
result['capture_files']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in C.iterdir() if p.is_file()}
(O/'capture-inspection.json').write_text(json.dumps(result,indent=2)+'\n')
canvas=Image.new('RGB',(1280,1200),'#202020');draw=ImageDraw.Draw(canvas)
for i,n in enumerate(['fonts','metal','talon','front','generator','menu']):
 canvas.paste(Image.open(C/f'{n}-640x400-hd.bmp').convert('RGB'),((i%2)*640,(i//2)*400));draw.text(((i%2)*640+4,(i//2)*400+4),n,fill='red')
canvas.save(O/'root-contact-sheet.png')
print(json.dumps({k:v for k,v in result.items() if k!='capture_files'},indent=2))
