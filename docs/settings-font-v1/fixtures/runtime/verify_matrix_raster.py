#!/usr/bin/env python3
"""Full retained-matrix raster oracle using literal original menu call sites."""
import argparse,hashlib,json,pathlib,re,struct,csv
import numpy as np
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('--repo',type=pathlib.Path,required=True);p.add_argument('--data',type=pathlib.Path,required=True);p.add_argument('--reference',type=pathlib.Path,required=True);p.add_argument('--candidate',type=pathlib.Path,required=True);p.add_argument('--out',type=pathlib.Path,required=True);a=p.parse_args()
text=(a.repo/'src/fonthand.c').read_text().split('const int font_ascii[256] =',1)[1].split('};',1)[0];mapping=list(map(int,re.findall(r'-?\d+',re.sub(r'//[^\n]*','',text))));assert len(mapping)==256
raw=(a.data/'tyrian.shp').read_bytes();n=struct.unpack_from('<H',raw)[0];offset=struct.unpack_from('<'+str(n)+'I',raw,2);banks=[]
for b in range(3):
 q=offset[b];n=struct.unpack_from('<H',raw,q)[0];q+=2;bank=[]
 for id in range(n):
  assert raw[q]==1;q+=1;w,h,size=struct.unpack_from('<HHH',raw,q);q+=6;rle=raw[q:q+size];q+=size;mask=np.full((h,w),-1,dtype=np.int16);x=y=i=0
  while i<size:
   v=rle[i];i+=1
   if v==255:x+=rle[i];i+=1
   elif v==254:x=w
   elif v==253:x+=1
   else:mask[y,x]=v&15;x+=1
   if x==w:x=0;y+=1
  bank.append(mask)
 banks.append(bank)
pal=np.frombuffer((a.data/'palette.dat').read_bytes()[7*768:8*768],dtype=np.uint8).astype(np.uint32);pal=(pal*4+(pal>>4)).reshape((256,3))
raw=(a.data/'tyrian.pic').read_bytes();n=struct.unpack_from('<H',raw)[0];offset=struct.unpack_from('<'+str(n)+'I',raw,2);q=offset[1];decoded=[]
while len(decoded)<64000:
 v=raw[q];q+=1
 if v&192==192:decoded.extend([raw[q]]*(v&63));q+=1
 else:decoded.append(v)
index=np.array(decoded,dtype=np.uint8).reshape((200,320));index[192:]=0;canvas=np.repeat(np.repeat(pal[index],4,axis=0),4,axis=1);support=np.zeros((800,1280),bool)
assets=[]
for name in ['large','medium','tiny']:
 raw=(a.repo/f'assets/hd/artwork/settings-font-v1/canonical/settings-font-{name}-v1.hda').read_bytes();fields=struct.unpack_from('<15I',raw,4);aw,ah,cw,ch=fields[3:7];plane=fields[10];alpha=np.frombuffer(raw[128:128+plane],dtype=np.uint8).reshape((ah,aw));roles=np.frombuffer(raw[128+plane:],dtype=np.uint8).reshape((ah,aw)) if fields[12] else None;assets.append((cw,ch,alpha,roles))
def width(bank,s):return sum(6 if c==' ' else banks[bank][mapping[ord(c)]].shape[1]+1 for c in s)
def run(bank,s,x,y,value):
 cw,ch,atlas,roles=assets[bank]
 for shadow in [True,False]:
  xx=x+(1 if bank==2 else 2) if shadow else x;yy=y+(1 if bank==2 else 2) if shadow else y
  for c in s:
   if c==' ':xx+=6;continue
   id=mapping[ord(c)];mask=banks[bank][id];h,w=mask.shape;ax=(id%16)*cw+4;ay=(id//16)*ch+4;a4=atlas[ay:ay+4*h,ax:ax+4*w].astype(np.uint32);old=index[yy:yy+h,xx:xx+w]
   src=((old&240)|((old&15)//2)) if shadow and bank!=2 else np.zeros_like(old) if shadow else None
   if shadow:rgb=np.repeat(np.repeat(pal[src],4,axis=0),4,axis=1)
   else:
    role=np.full(a4.shape,7) if bank==2 else roles[ay:ay+4*h,ax:ax+4*w];tone=np.clip(role.astype(np.int16)+value,0,15);rgb=pal[240|tone]
   dest=canvas[yy*4:(yy+h)*4,xx*4:(xx+w)*4];dest[:]=(rgb*a4[:,:,None]+dest*(255-a4[:,:,None])+127)//255
   support[yy*4:(yy+h)*4,xx*4:(xx+w)*4] |= (a4>0)|np.repeat(np.repeat(mask>=0,4,axis=0),4,axis=1)
   if shadow:old[mask>=0]=src[mask>=0]
   else:old[mask>=0]=(240|np.clip(mask+value,0,15))[mask>=0]
   xx+=w+1
base=index.copy()
headers=['Setup','Graphics','Sound']
labels=[['Graphics...','Sound...','Jukebox','Done'],['Display:','Scaler:','Scaling Mode:','Done'],['Music Volume','Sound Volume','Done']]
footers=[['Change the graphics settings.','Change the sound settings.','Listen to the music of Tyrian.','Return to the main menu.'],['Change the display mode.','Change the pixel art scaling algorithm.','Change the scaling mode.','Return to the previous menu.'],['Change volume with the left/right arrow keys.','Change volume with the left/right arrow keys.','Return to the previous menu.']]
scalers=['None','2x','Scale2x','hq2x','3x','Scale3x','hq3x','4x','hq4x'];modes=['Center','Integer','Fit 8:5','Fit 4:3']
shop=(a.data/'newsh1.shp').read_bytes()
def rect(x,y,w,h,color=None):
 old=index[y:y+h,x:x+w];old[:]=((old&240)|((old&15)//2)) if color is None else color
 canvas[y*4:(y+h)*4,x*4:(x+w)*4]=np.repeat(np.repeat(pal[old],4,axis=0),4,axis=1);support[y*4:(y+h)*4,x*4:(x+w)*4]=False

def border(x,y,w,h,color):
 rect(x,y,w,1,color);rect(x,y+h-1,w,1,color);rect(x,y+1,1,h-2,color);rect(x+w-1,y+1,1,h-2,color)

def bar(row,volume,muted):
 y=37+21*row;color=170 if muted else 174
 for n in range((volume+4)//8):
  x=180+3*n;rect(x+2,y+2,2,10);rect(x,y,2,10,color+12);rect(x,y,2,1,color+13);rect(x,y,1,1,color+15);rect(x,y+9,2,1,color+11)
 border(178,y-2,99,14,242)

def cursor(x,y):
 for id,dx,dy in [(273,0,0),(274,12,0),(292,0,14),(293,12,14)]:
  q=struct.unpack_from('<H',shop,(id-1)*2)[0];xx=x+dx;yy=y+dy
  while shop[q]!=15:
   v=shop[q];q+=1;xx+=v&15;n=v>>4
   if n==0:yy+=1;xx-=12
   else:
    for _ in range(n):
     color=shop[q];q+=1
     if 0<=xx<320 and 0<=yy<200:rect(xx,yy,1,1,color)
     xx+=1

rows=list(csv.DictReader((a.candidate/'presentations.tsv').open(),delimiter='\t'));stream=(a.candidate/'indexed-palette-stream.bin').read_bytes();reports=[]
for record in rows:
 name=record['image']
 if name=='-':continue
 numeric={k:int(v) for k,v in record.items() if k not in ['owner','image','RNG','writes']}
 index=base.copy();canvas=np.repeat(np.repeat(pal[index],4,axis=0),4,axis=1);support=np.zeros((800,1280),bool)
 menu=numeric['menu']-1;selected=numeric['selected'];picker=numeric['picker'];fullscreen=numeric['fullscreen'];sidx=numeric['scaler'];mode=numeric['scaling_mode']
 displays=['Window']+[f'Display {i}' for i in range(1,numeric['displays']+1)]
 values=[displays[fullscreen+1],scalers[sidx],modes[mode]]
 run(0,headers[menu],160-width(0,headers[menu])//2,4,-3)
 for row,text in enumerate(labels[menu]):
  value=-1 if row==selected else -7 if picker else -3
  run(1,text,45,37+21*row,value)
  if menu==1 and row<3:run(1,values[row],180,37+21*row,value)
  if menu==2 and row<2:bar(row,numeric['music' if row==0 else 'fx'],numeric['music_muted' if row==0 else 'fx_muted'])
 run(2,footers[menu][selected],45,190,4)
 if picker:
  items=[displays,scalers,modes][picker-1];h=15*len(items)-2;y=min(37+21*selected,183-h)
  border(175,y-3,105,h+6,248);border(176,y-4,103,h+8,250);border(177,y-5,101,h+10,248);rect(178,y-2,99,h+4,224)
  for row,text in enumerate(items):run(1,text,180,y+15*row,-1 if row==numeric['picker_selected'] else -3)
 if numeric['has_mouse'] and not numeric['mouse_inactive']:cursor(numeric['mouse_x'],numeric['mouse_y'])
 offset=(numeric['settings_present']-1)*65024;actual_index=np.frombuffer(stream[offset:offset+64000],dtype=np.uint8).reshape(200,320)
 assert np.array_equal(index,actual_index),(name,'literal original indexed reconstruction mismatch',int(np.count_nonzero(index!=actual_index)))
 reference=np.asarray(Image.open(a.reference/(name+'.bmp')).convert('RGB'));candidate=np.asarray(Image.open(a.candidate/(name+'.bmp')).convert('RGB'));changed=np.any(reference!=candidate,axis=2)
 report={'name':name,'changed_pixels':int(changed.sum()),'literal_indexed_mismatches':0,'owner':record['owner']}
 if record['owner']=='classic':assert not changed.any();report['outside_font_support_changes']=0;report['fallback_byte_exact']=True
 else:
  density=numeric['width']//320;assert density in [2,4] and numeric['height']==200*density
  expected=canvas if density==4 else (canvas.reshape(400,2,640,2,3).sum(axis=(1,3))+2)//4
  allowed=support if density==4 else support.reshape(400,2,640,2).any(axis=(1,3))
  classic=np.repeat(np.repeat(pal[index],density,axis=0),density,axis=1)
  report['candidate_mismatched_pixels']=int(np.any(candidate!=expected,axis=2).sum());report['reference_mismatched_pixels']=int(np.any(reference!=classic,axis=2).sum());report['outside_font_support_changes']=int((changed&~allowed).sum())
  assert not report['candidate_mismatched_pixels'] and not report['reference_mismatched_pixels'] and not report['outside_font_support_changes'],report
 reports.append(report)
result={'schema':'settings-matrix-actual-full-raster-oracle-v1','captures':reports,'result':'PASS','scope':'Each retained actual still reconstructed from literal menu strings, original RLE/PIC2/palette7, bars/picker rectangles, original cursor tiles and immutable SFN1 planes; no private command/base data shared.'};a.out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
