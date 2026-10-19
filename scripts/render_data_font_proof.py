from pathlib import Path
import json,struct
# Build-time Pillow only. Preview uses the shipped alpha atlas and its metrics.
from PIL import Image
import argparse
parser=argparse.ArgumentParser(description='Draw a preview from the exact derived Data atlas; this is not a game screenshot.')
parser.add_argument('--assets',type=Path,default=Path(__file__).resolve().parents[1]/'assets/data-text-zh-CN-v1')
parser.add_argument('--output',type=Path)
args=parser.parse_args()
p=args.assets
blob=(p/'data-text-zh-CN-v1.dzf').read_bytes()
_,_,w,h,cw,ch,n,cols,baseline,px,recbytes,abytes,fnv,zero=struct.unpack('<4s11IQQ',blob[:64])
records=[struct.unpack('<IHH',blob[64+i*8:72+i*8]) for i in range(n)]
alpha=Image.frombytes('L',(w,h),blob[64+n*8:]);indices={cp:i for i,(cp,adv,z) in enumerate(records)};advances={cp:adv for cp,adv,z in records}
e=next(e for e in json.loads((p/'data-text-zh-CN-v1.json').read_text())['entries'] if e['id']=='ep1.cube11')
im=Image.new('RGB',(1280,800),(18,24,39))
def draw(text,x,y,size=20):
 scale=size/36
 for c in text:
  if c=='~':continue
  i=indices[ord(c)];sx,sy=i%cols*cw,i//cols*ch
  mask=alpha.crop((sx,sy,sx+cw,sy+ch)).resize((round(cw*scale),round(ch*scale)),Image.Resampling.LANCZOS)
  im.paste((240,240,228),(round(x-2*scale),round(y)),mask);x+=advances[ord(c)]*scale
lines=[]
for para in e['paragraphs']:
 line='';used=0
 for c in para:
  if c=='~':continue
  advance=advances[ord(c)]*20/36
  if line and used+advance>584:lines.append(line);line='';used=0
  line+=c;used+=advance
 lines.append(line);lines.append('')
if lines and not lines[-1]:lines.pop()
for x,label,start in [(28,'FIRST PAGE / 20px',0),(668,'LAST PAGE / 20px',max(0,len(lines)-18))]:
 draw(label,x,24);draw(e['title'],x,78,24);draw(e['header'],x,126,24)
 y=192
 for line in lines[start:start+18]:
  if line:draw(line,x,y)
  y+=26 if line else 13
 draw(f'{e["id"]} / {start+1}-{min(start+18,len(lines))} / {len(lines)}',x,714,18)
draw('DZF1 ACTUAL ATLAS PIXELS / FONT PROOF ONLY / NOT A GAME SCREENSHOT',28,758,18)
im.save(args.output or p/'chinese-body-font-proof.png')
