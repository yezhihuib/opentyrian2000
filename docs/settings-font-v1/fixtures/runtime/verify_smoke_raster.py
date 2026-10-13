#!/usr/bin/env python3
"""Full native2 Setup oracle, independently reconstructing reviewed call sites."""
import argparse,hashlib,json,pathlib,re,struct
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
run(0,'Setup',160-width(0,'Setup')//2,4,-3)
for i,s in enumerate(['Graphics...','Sound...','Jukebox','Done']):run(1,s,45,37+21*i,-1 if i==0 else -3)
run(2,'Change the graphics settings.',45,190,4)
expected=(canvas.reshape(400,2,640,2,3).sum(axis=(1,3))+2)//4;classic=np.repeat(np.repeat(pal[index],2,axis=0),2,axis=1);allowed=support.reshape(400,2,640,2).any(axis=(1,3))
r=np.asarray(Image.open(a.reference).convert('RGB'));c=np.asarray(Image.open(a.candidate).convert('RGB'));assert r.shape==c.shape==(400,640,3)
report={'schema':'settings-native2-actual-full-raster-oracle-v1','reference_mismatched_pixels':int(np.any(r!=classic,axis=2).sum()),'candidate_mismatched_pixels':int(np.any(c!=expected,axis=2).sum()),'changed_pixels':int(np.any(r!=c,axis=2).sum()),'outside_font_support_changes':int((np.any(r!=c,axis=2)&~allowed).sum()),'support_pixels':int(allowed.sum()),'scope':'Setup selected Graphics; independent literal call sites, original RLE/PIC2/palette7 and immutable SFN1 planes; complete final4x samples reduced once'}
assert not report['reference_mismatched_pixels'] and not report['candidate_mismatched_pixels'] and not report['outside_font_support_changes'];report['result']='PASS';a.out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
