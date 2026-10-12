from PIL import Image,ImageDraw
from pathlib import Path
P=Path(__file__).parent
s=12;im=Image.new('RGB',(320*s,200*s));d=ImageDraw.Draw(im);d.polygon([(264*s,0),(320*s,0),(320*s,200*s),(0,200*s),(0,184*s),(264*s,184*s)],fill='#403c35')
for x,y,w,h,r in [(267,10,12,98,1.5),(283,3,30,19,1),(283,24,30,19,1),(284.5,44,10.5,8,1),(301.5,44,10.5,8,1),(283,53,30,8,.5),(282.5,63,31,36,1.5),(266.5,114,50,14,1.5),(269,134,11,62,1.5),(306,134,11,62,1.5),(283,136,9,41,1),(294,136,9,41,1),(268.5,2.5,8.5,5.5,2),(7,188,250,10,1.5)]:
 d.rounded_rectangle((x*s,y*s,(x+w)*s-1,(y+h)*s-1),radius=r*s,fill='#050606',outline='#696259',width=4)
for pts in [[(265,111),(319,111)],[(265,131),(319,131)],[(281,1),(281,109)],[(281,180),(304,180)],[(5,185),(259,185)]]:d.line([(x*s,y*s) for x,y in pts],fill='#201e1b',width=4)
a=Image.new('RGB',(1536,1536))
a.paste(im.crop((264*s,0,320*s,112*s)),(32,32));a.paste(im.crop((264*s,112*s,320*s,200*s)),(800,32));a.paste(im.crop((0,184*s,264*s,200*s)).resize((1320,80),Image.Resampling.LANCZOS),(32,1424));a.save(P/'component-layout-guide.png')
