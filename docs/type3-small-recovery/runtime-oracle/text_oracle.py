"""Read-only original SMALL_FONT_SHAPES INSERT COIN overlay oracle.
Decodes original tyrian.shp table1 and palette5, then independently replays
JE_dString: each glyph darkens at(+2,+2), followed by F0 hue/value−3 at(0,0).
Only the earlier type15-owned support is recomposed; all outside pixels remain
from the exact paired baseline. No visible-opacity inference from RGB is used.
"""
from pathlib import Path
import hashlib,json,struct
import numpy as np
D=Path('/workspace/scratch/f67dd347fa0a/recovery-dependencies-20261013/game-data/tyrian2000')
raw=(D/'tyrian.shp').read_bytes();count=struct.unpack_from('<H',raw)[0];offs=struct.unpack_from('<'+str(count)+'i',raw,2);p=offs[1];n=struct.unpack_from('<H',raw,p)[0];p+=2;glyphs={}
for i in range(n):
 present=raw[p];p+=1
 if not present:continue
 w,h,size=struct.unpack_from('<HHH',raw,p);p+=6;data=raw[p:p+size];p+=size;mask=np.zeros((h,w),dtype=bool);indices=np.zeros((h,w),dtype=np.uint8);q=0;x=0;y=0
 while q<len(data):
  b=data[q];q+=1
  if b==255:x+=data[q];q+=1
  elif b==254:x=w
  elif b==253:x+=1
  else:assert 0<=x<w and 0<=y<h;(mask.__setitem__((y,x),True));indices[y,x]=b;x+=1
  if x>=w:x=0;y+=1
 glyphs[i]=(w,h,mask,indices)
palraw=(D/'palette.dat').read_bytes()[5*768:6*768];PALETTE=np.array([[(c<<2)|(c>>4)for c in palraw[i:i+3]]for i in range(0,768,3)],dtype=np.uint8)
TEXT='INSERT COIN';XY=(115,10)
def apply_insert_coin(expected,support,scale):
 x,y=XY;shadowed=np.zeros(support.shape,bool);covered=np.zeros(support.shape,bool)
 for ch in TEXT:
  if ch==' ':x+=6;continue
  i=ord(ch)-ord('A');w,h,mask,indices=glyphs[i]
  for yy,xx in zip(*np.where(mask)):
   dx=(x+int(xx)+2-24)*scale;dy=(y+int(yy)+2)*scale
   if dx<0 or dy<0 or dx+scale>264*scale or dy+scale>184*scale:continue
   own=support[dy:dy+scale,dx:dx+scale];v=expected[dy:dy+scale,dx:dx+scale,:3];v[own]=((v[own].astype(np.uint16)+1)//2).astype(np.uint8);shadowed[dy:dy+scale,dx:dx+scale]|=own
  for yy,xx in zip(*np.where(mask)):
   dx=(x+int(xx)-24)*scale;dy=(y+int(yy))*scale
   if dx<0 or dy<0 or dx+scale>264*scale or dy+scale>184*scale:continue
   own=support[dy:dy+scale,dx:dx+scale];index=(0xf0|((int(indices[yy,xx])&15)-3))&255;expected[dy:dy+scale,dx:dx+scale,:3][own]=PALETTE[index];covered[dy:dy+scale,dx:dx+scale]|=own
  x+=w+1
 return {'fully_covered_native_pixels':int(covered.sum()),'shadow_only_native_pixels':int((shadowed&~covered).sum()),'text_source':'original tyrian.shp table1 / JE_dString at115,10 / F0 value−3 / shadow+2,+2','original_font_file_sha256':hashlib.sha256(raw).hexdigest(),'original_palette_sha256':hashlib.sha256((D/'palette.dat').read_bytes()).hexdigest()}
