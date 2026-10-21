#!/usr/bin/env python3
"""New RFR3 generator. This is reconstruction, never original-source recovery.
Pinned whole-run shaping, no stretch. Never writes exact frozen staging or NFR.
"""
from pathlib import Path
import argparse,hashlib,json,math,struct
from PIL import Image,ImageDraw,ImageFont,features
import PIL
P=Path(__file__).resolve().parent
ROOT=P.parents[2]
FAMILIES=['esc','main','shop','category','product','names']
FONT_SHA={'DejaVuSansCondensed-Bold.ttf':'21f02ebcea75529d3ed9d26e089cd1b9c59a4b784119ba3a96e9bc83cf755ec7','osifont.ttf':'1459a7c4143932cec1140ea15e765908be184d07ca34d271320958349c9bc9dd'}
COUNTS=[16,7,7,9,19,113]
SHA=lambda b:hashlib.sha256(b).hexdigest()

def fnv(b):
 h=14695981039346656037
 for x in b:h=((h^x)*1099511628211)&0xffffffffffffffff
 return h

def u64(n):return 'UINT64_C(0x%016x)'%n

def build_run(name,original):
 family=name.split('-')[0];fid=FAMILIES.index(family);rid=int(name.split('-')[-1].split('.')[0])
 size=128 if family=='names' else 131 if family=='product' and rid>=7 else 288 if (family in ['shop','category'] and rid==0) or (family=='product' and rid<7) else 219
 fontname='osifont.ttf' if family=='names' else 'DejaVuSansCondensed-Bold.ttf'
 fb=(P/'fonts'/fontname).read_bytes();assert SHA(fb)==FONT_SHA[fontname]
 font=ImageFont.truetype(str(P/'fonts'/fontname),size,layout_engine=ImageFont.Layout.RAQM)
 baseline=96 if family=='names' else -font.getbbox('H',anchor='ls')[1]
 text=original['text'];l,t,r,b=font.getbbox(text,anchor='ls');padding=3 if family=='main' else 1
 dx=math.floor(l/4)-padding;dy=math.floor((baseline+t)/4)-padding
 w=math.ceil(r/4)+padding-dx;h=math.ceil((baseline+b)/4)+padding-dy
 advance=round(font.getlength(text)*64);planes=3 if family=='main' else 2
 assert 64+w*h*planes==original['bytes'],(name,w,h)
 if 'advance_256' in original:assert advance==original['advance_256']
 profile=(1 if family=='esc' else 2 if family=='main' else 3+(rid!=0) if family=='shop' else 5+(rid!=0) if family=='category' else 7+(rid>=7) if family=='product' else 9)
 tiny=profile in (8,9)
 im=Image.new('L',(w*4,h*4));ImageDraw.Draw(im).text((-dx*4,baseline-dy*4),text,font=font,anchor='ls',fill=255)
 alpha=im.resize((w,h),Image.Resampling.BOX).tobytes()
 roles=bytearray(w*h)
 for yy in range(h):
  # Full descent remains gold. There is no baseline-dependent lower stripe.
  logical_y=(dy+yy+.5)/4
  role=7 if tiny else 15 if logical_y<.6 else 14 if logical_y<1.275 else 13
  for xx in range(w):
   at=yy*w+xx
   if alpha[at]:roles[at]=role
 stroke=b''
 if family=='main':
  contour=Image.new('L',im.size)
  ImageDraw.Draw(contour).text((-dx*4,baseline-dy*4),text,font=font,anchor='ls',fill=255,stroke_width=8,stroke_fill=255)
  stroke=contour.resize((w,h),Image.Resampling.BOX).tobytes()
  assert all(s>=a for s,a in zip(stroke,alpha))
 assert all((a==0)==(r==0) for a,r in zip(alpha,roles))
 assert all(r==0 or (r==7 if tiny else 13<=r<=15) for r in roles)
 payload=alpha+bytes(roles)+stroke
 fontprefix=int.from_bytes(hashlib.sha256(fb).digest()[:8],'little');th=fnv(text.encode('ascii'));ph=fnv(payload)
 header=struct.pack('<4s4I2i3I3Q',b'RFR3',3,64,w,h,dx,dy,advance,planes,profile,th,ph,fontprefix)
 assert len(header)==64
 raw=header+payload
 result={'family':fid,'family_name':family,'id':rid,'filename':name,'text':text,'width':w,'height':h,'dx':dx,'dy':dy,'advance256':advance,'planes':planes,'role_profile':profile,'role_min':7 if tiny else 13,'role_max':7 if tiny else 15,'font_file':'fonts/'+fontname,'font_size_supersampled':size,'baseline_supersampled':baseline,'font_sha256':SHA(fb),'font_prefix64':fontprefix,'text_fnv64':th,'payload_fnv64':ph,'header_fnv64':fnv(header),'file_fnv64':fnv(raw),'bytes':len(raw),'payload_bytes':len(payload),'sha256':SHA(raw),'original_target_sha256':original['sha256'],'original_target_bytes':original['bytes'],'original_byte_identity':False}
 return result,raw,alpha,bytes(roles),stroke

def specs(rows):
 lines=['/* Newly reconstructed RFR3 specs. Not original source. */','#ifndef CMR3_RECONSTRUCTED_RUN_SPECS_H','#define CMR3_RECONSTRUCTED_RUN_SPECS_H','#include <stdint.h>','#define CMR3_HEADER_BYTES 64u','#define CMR3_DENSITY 4u','#define CMR3_VERSION 3u','#define CMR3_SPEC_COUNT 171u','#define CMR3_FAMILY_COUNT 6u','/* dx/dy/width/height are canonical4 pixels. advance256 is canonical4 pixels times256. */','enum Cmr3Family { CMR3_ESC=0, CMR3_MAIN, CMR3_SHOP, CMR3_CATEGORY, CMR3_PRODUCT, CMR3_NAMES };','enum Cmr3Profile { CMR3_ESC_MEDIUM=1, CMR3_MAIN_CONTOUR, CMR3_SHOP_HEADING, CMR3_SHOP_CHOICE, CMR3_CATEGORY_HEADING, CMR3_CATEGORY_CHOICE, CMR3_PRODUCT_HEADING, CMR3_PRODUCT_TINY, CMR3_NAMES_UPRIGHT };','struct Cmr3Spec {',' const char *filename, *text;',' uint32_t family, id, width, height;',' int32_t dx, dy;',' uint32_t advance256, planes, role_profile, role_min, role_max;',' uint64_t text_fnv64, payload_fnv64, font_prefix64, header_fnv64, file_fnv64;',' const char *sha256;','};','static const uint32_t cmr3_family_first[6]={0,16,23,30,39,58};','static const uint32_t cmr3_family_count[6]={16,7,7,9,19,113};','static const struct Cmr3Spec cmr3_specs[171]={']
 for r in rows:
  nums=[r[k] for k in ['family','id','width','height','dx','dy','advance256','planes','role_profile','role_min','role_max']]
  qs=[r[k] for k in ['text_fnv64','payload_fnv64','font_prefix64','header_fnv64','file_fnv64']]
  lines.append(' {%s,%s,%s,%s,%s},'%(json.dumps(r['filename']),json.dumps(r['text']),','.join(map(str,nums)),','.join(u64(n) for n in qs),json.dumps(r['sha256'])))
 lines+=['};']
 totals=[sum(r['bytes'] for r in rows if r['family']==i) for i in range(6)]
 lines.append('#define CMR3_TOTAL_FILE_BYTES %du'%sum(totals))
 for name,total in zip(FAMILIES,totals):lines.append('#define CMR3_%s_FILE_BYTES %du'%(name.upper(),total))
 lines.append('static const uint32_t cmr3_family_file_bytes[6]={'+','.join(map(str,totals))+'};')
 lines.append('#define CMR3_TOTAL_TEXT_BYTES %du'%sum(len(r['text'])+1 for r in rows))
 lines.append('#define CMR3_TOTAL_FILENAME_BYTES %du'%sum(len(r['filename'])+1 for r in rows))
 lines+=['#endif','']
 return '\n'.join(lines)

def preview(items,out):
 # Illustrative only. Native runtime palette/order/underlay checks remain required.
 labels=ImageFont.truetype(str(P/'fonts/DejaVuSansCondensed-Bold.ttf'),16)
 headings=ImageFont.truetype(str(P/'fonts/DejaVuSansCondensed-Bold.ttf'),24)
 canvas=Image.new('RGB',(1300,1050),(15,21,34));draw=ImageDraw.Draw(canvas)
 draw.text((28,20),'RFR3 reconstruction: whole-run font specimens',font=headings,fill=(230,234,244))
 draw.text((28,56),'New resources, same pinned fonts and advances. Not a native runtime screenshot.',font=labels,fill=(151,164,189))
 y=100
 colors={7:(233,224,193),13:(214,187,109),14:(235,220,145),15:(255,255,182)}
 for row,raw,alpha,roles,stroke in items:
  w=row['width'];h=row['height'];title=f"{row['family_name'].upper()}  {row['text']}  |  {w}x{h}, natural advance {row['advance256']/256:.4f} canonical pixels"
  draw.text((28,y),title,font=labels,fill=(149,170,207));y+=25
  image=Image.new('RGBA',(w,h))
  image.putdata([(*colors.get(r,(0,0,0)),a) for a,r in zip(alpha,roles)])
  x=34
  if stroke:
   shadow=Image.new('RGBA',(w,h),(3,5,8,0));shadow.putalpha(Image.frombytes('L',(w,h),stroke));canvas.paste(shadow,(x,y),shadow)
  elif row['role_profile'] not in (8,9):
   shadow=Image.new('RGBA',(w,h),(3,5,8,0));shadow.putalpha(Image.frombytes('L',(w,h),alpha));canvas.paste(shadow,(x+4,y+4),shadow)
  canvas.paste(image,(x,y),image)
  # Same raster at half dimensions is the 2x scale specimen, not a separate font fit.
  combined=image.copy()
  if stroke:
   combined=Image.new('RGBA',(w,h),(3,5,8,0));combined.putalpha(Image.frombytes('L',(w,h),stroke));combined.alpha_composite(image)
  half=combined.resize((max(1,(w+1)//2),max(1,(h+1)//2)),Image.Resampling.BOX)
  canvas.paste(half,(710,y+4),half);draw.text((1010,y+6),'2x scale specimen',font=labels,fill=(116,132,158))
  y+=max(h,28)+18
 canvas=canvas.crop((0,0,1300,min(canvas.height,y+20)));canvas.save(out/'representative-rfr3-specimens.png')

PREVIEW=['esc-run-00.rfr','main-run-02.rfr','main-run-03.rfr','shop-run-00.rfr','shop-run-03.rfr','product-run-07.rfr','product-run-18.rfr','names-run-01.rfr','names-run-02.rfr','names-run-07.rfr']
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True);parser.add_argument('--preview-only',action='store_true');a=parser.parse_args()
 out=a.out.resolve();out.mkdir(parents=True,exist_ok=True)
 assert not any(p.name=='frozen' for p in [out,*out.parents]),'Never generate reconstructed assets into exact staging'
 assert PIL.__version__=='12.3.0' and features.version('freetype2')=='2.14.3' and features.version('raqm')=='0.10.5'
 original_manifest=ROOT/'assets/hd/manifest.json';source=original_manifest.read_bytes();m=json.loads(source)['shared_menu_runs'];entries=[]
 for family in FAMILIES:
  names=sorted((n for n in m['files'] if n.startswith(family+'-')),key=lambda n:int(n.split('-')[-1].split('.')[0]))
  assert len(names)==COUNTS[FAMILIES.index(family)]
  for n in names:
   if a.preview_only and n not in PREVIEW:continue
   entries.append(build_run(n,m['files'][n]))
 for row,raw,*_ in entries:
  path=out/row['filename']
  if path.exists():assert path.read_bytes().startswith(b'RFR3'),'Refuse overwrite of authenticated old-format resource'
  path.write_bytes(raw)
 rows=[r for r,*_ in entries]
 preview([next(e for e in entries if e[0]['filename']==n) for n in PREVIEW],out)
 if not a.preview_only:(out/'reconstructed_run_specs.h').write_text(specs(rows))
 manifest={'schema':'new-rfr3-reconstruction-20261020','original_byte_identity':False,'preview_only':a.preview_only,'font_redesign':False,'density':4,'units':{'bearing_dimensions':'canonical4 pixels','advance256':'canonical4 pixels times256'},'original_manifest_sha256':SHA(source),'rasterizer':{'pillow':PIL.__version__,**{n:features.version(n) for n in ['freetype2','raqm','harfbuzz','fribidi']}},'role_style':'Whole-run gold roles13..15 extend continuously through descenders; no baseline stripe. Tiny PRODUCT and NAMES role7. Runtime retains distinct native family color/shadow operators.','stroke':'MAIN whole-string FreeType contour radius8 supersampled pixels =2 canonical pixels =0.5 logical pixel, reduced BOX4. Not four shifted face masks.','names_style':'Pinned upright OSIfont Medium, natural advances, unemboldened, no per-glyph stretching.','resources':rows,'runtime_validation':False}
 (out/'reconstructed-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 assert original_manifest.read_bytes()==source,'Original target metadata must stay immutable'
 print(json.dumps({'out':str(out),'runs':len(rows),'preview_only':a.preview_only,'payload_bytes':sum(r['payload_bytes'] for r in rows),'original_byte_identity':False}))
if __name__=='__main__':main()
