#!/usr/bin/env python3
"""Reconstructed generator; validates original numeric resource bytes exactly.
This generator source is new, not recovered original source. No runtime C edits.
"""
from pathlib import Path
import hashlib,json,struct,random,argparse
from PIL import Image,ImageDraw,ImageFont,features
import PIL
P=Path(__file__).resolve().parent
ROOT=P.parents[2]
FONT=ROOT/'assets/hd/shared-menu-runs-v1/fonts/osifont.ttf'
TARGET={'path':'assets/hd/shared-menu-runs-v1/numeric-runs-v1.nfr','size':41110,'sha256':'7becf23de59c40582992f3c8caeea4b953405f014f86a070b0d25cef63f4878d','blob':'9fb2d2fb5f3c8adbfa3da7fb51609db6e7cab99c'}
EXPECTED_ALPHA='09ee5232896a1d9540608eef1762ff169fb2e20650e21a7194e139041972eb8e'
TOKENS=list('0123456789-')+['Cost: ']
sha=lambda b:hashlib.sha256(b).hexdigest()
def fnv(b):
 h=14695981039346656037
 for n in b:h=((h^n)*1099511628211)&0xffffffffffffffff
 return h

def build(out):
 font_bytes=FONT.read_bytes();assert sha(font_bytes)=='1459a7c4143932cec1140ea15e765908be184d07ca34d271320958349c9bc9dd'
 assert PIL.__version__=='12.3.0' and features.version('freetype2')=='2.14.3' and features.version('raqm')=='0.10.5'
 f=ImageFont.truetype(str(FONT),128,layout_engine=ImageFont.Layout.RAQM)
 masks=[];rows=[];advances=[];payload=b''
 for tid,token in enumerate(TOKENS):
  advance=round(f.getlength(token)*16);advances.append(advance);descriptors=[]
  for residue in range(64):
   im=Image.new('L',(512,160));ImageDraw.Draw(im).text((8+residue/16,96),token,font=f,anchor='ls',fill=255)
   im=im.resize((128,40),Image.Resampling.BOX);l,t,r,b=im.getbbox();tile=im.crop((l,t,r,b));raw=tile.tobytes()
   hit=next((i for i,m in enumerate(masks) if m['size']==list(tile.size) and m['alpha']==raw),None)
   if hit is None:
    hit=len(masks);masks.append({'size':list(tile.size),'alpha':raw,'offset':len(payload)});payload+=raw
   descriptors.append({'residue64':residue,'mask':hit,'x':l-2,'y':t})
  rows.append({'id':tid,'token':token,'advance64':advance,'descriptors':descriptors})
 assert advances==[958,700,955,984,1051,1018,1013,979,1056,1030,952,5023]
 assert len(masks)==64 and len(payload)==41046 and sha(payload)==EXPECTED_ALPHA
 h=struct.pack('<4s7I4Q',b'NFR1',1,64,12,64,64,len(payload),0,int.from_bytes(hashlib.sha256(font_bytes).digest()[:8],'little'),fnv(payload),0,0)
 resource=h+payload;blob=hashlib.sha1(b'blob '+str(len(resource)).encode()+b'\0'+resource).hexdigest()
 assert len(resource)==TARGET['size'] and sha(resource)==TARGET['sha256'] and blob==TARGET['blob']
 resource_path=out/'numeric-runs-v1.nfr'
 if resource_path.exists():assert resource_path.read_bytes()==resource,'Refuse mutation of exact resource'
 else:resource_path.write_bytes(resource)
 # New, explicit reference descriptors, not the missing original C serialization.
 (out/'reconstructed-numeric-manifest.json').write_text(json.dumps({'status':'new_specs_for_byte_identical_numeric_resource','mask_count':len(masks),'descriptor_count':768,'masks':[{k:v for k,v in m.items() if k!='alpha'} for m in masks],'tokens':rows},indent=2)+'\n')
 return f,masks,rows,{'sha256':sha(resource),'git_blob':blob,'bytes':len(resource),'payload_sha256':sha(payload),'payload_bytes':len(payload),'masks':len(masks),'header_hex':h.hex()}

def verify(f,masks,rows):
 by_token={r['token']:r for r in rows};randomizer=random.Random(0x4e465231);cases=[]
 fixed=['0','1','-1','0123456789','Cost: 0','Cost: 1','Cost: 1234567890','2147483647','-2147483648','4294967295','18446744073709551615','Cost: -2147483648','Cost: 65535']
 for text in fixed:
  for residue in range(64):cases.append((text,residue))
 for _ in range(1000):
  text=('Cost: ' if randomizer.randrange(2) else '')+str(randomizer.randrange(-2**31,2**64))
  cases.append((text,randomizer.randrange(-256,257)))
 overlaps=0
 for text,start in cases:
  # Canvas generous enough for negative starting offsets and all tested values.
  hi=Image.new('L',(3072,160));ImageDraw.Draw(hi).text((128+start/16,96),text,font=f,anchor='ls',fill=255)
  reference=hi.resize((768,40),Image.Resampling.BOX).tobytes();made=bytearray(len(reference));pen=32*64+start
  tokens=(['Cost: ']+list(text[6:])) if text.startswith('Cost: ') else list(text)
  for token in tokens:
   row=by_token[token];d=row['descriptors'][pen%64];mask=masks[d['mask']];w,h=mask['size'];x=pen//64+d['x'];y=d['y']
   for yy in range(h):
    for xx in range(w):
     alpha=mask['alpha'][yy*w+xx];pos=(y+yy)*768+x+xx
     if alpha and made[pos]:overlaps+=1
     # Fractional support union is checked explicitly rather than alpha product.
     made[pos]=alpha+(made[pos]*(255-alpha)+127)//255
   pen+=row['advance64']
  assert bytes(made)==reference,(text,start,sha(made),sha(reference))
 return {'whole_string_raqm_cases':len(cases),'all_64_residues_for_each_fixed_case':True,'signed_start_pen_range64':[-256,256],'boolean_overlap_samples':overlaps,'mismatches':0,'note':'Independent whole-string RAQM draw compared with packed-mask assembly; no pair-advance-only proof.'}

def c_specs(masks,rows,receipt):
 def q(n):return 'UINT64_C(0x%016x)'%n
 resource=bytes.fromhex(receipt['header_hex'])+b''.join(m['alpha'] for m in masks)
 lines=['/* Reconstructed C descriptors for the verified exact NFR1 resource. */','#ifndef CMR_RECONSTRUCTED_NUMERIC_SPECS_H','#define CMR_RECONSTRUCTED_NUMERIC_SPECS_H','#include <stdint.h>',
 '#define CMR_NUMERIC_FILE_BYTES 41110u','#define CMR_NUMERIC_HEADER_BYTES 64u','#define CMR_NUMERIC_PAYLOAD_BYTES 41046u','#define CMR_NUMERIC_MASK_COUNT 64u','#define CMR_NUMERIC_TOKEN_COUNT 12u','#define CMR_NUMERIC_PHASE_COUNT 64u',
 '#define CMR_NUMERIC_FONT_PREFIX64 '+q(int.from_bytes(hashlib.sha256(FONT.read_bytes()).digest()[:8],'little')),
 '#define CMR_NUMERIC_PAYLOAD_FNV64 '+q(fnv(resource[64:])),
 '#define CMR_NUMERIC_HEADER_FNV64 '+q(fnv(resource[:64])),
 '#define CMR_NUMERIC_FILE_FNV64 '+q(fnv(resource)),
 '#define CMR_NUMERIC_SHA256 "'+TARGET['sha256']+'"',
 '#define CMR_NUMERIC_PAYLOAD_SHA256 "'+EXPECTED_ALPHA+'"',
 '/* advance64 is canonical4 pixels times64. For signed pen P64, use floor quotient P64/64 and nonnegative remainder. */',
 '/* x/y below are offsets from that quotient and the caller top; do not apply another baseline shift. */',
 'struct CmrNumericMask { uint32_t offset; uint16_t width, height; };',
 'struct CmrNumericPhase { uint16_t mask; int16_t x, y; };',
 'static const char *const cmr_numeric_tokens[12]={'+','.join(json.dumps(r['token']) for r in rows)+'};',
 'static const int32_t cmr_numeric_advances64[12]={'+','.join(str(r['advance64']) for r in rows)+'};',
 'static const struct CmrNumericMask cmr_numeric_masks[64]={']
 for m in masks:lines.append(' {%d,%d,%d},'%(m['offset'],*m['size']))
 lines+=['};','static const struct CmrNumericPhase cmr_numeric_phases[12][64]={']
 for r in rows:
  lines.append(' { /* '+r['token']+' */')
  for start in range(0,64,8):lines.append('  '+','.join('{%d,%d,%d}'%(d['mask'],d['x'],d['y']) for d in r['descriptors'][start:start+8])+',')
  lines.append(' },')
 lines+=['};','#endif','']
 return '\n'.join(lines)

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True);a=parser.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=True)
 assert not any(q.name=='frozen' for q in [out,*out.parents]),'No generated source in frozen exact staging'
 f,masks,rows,receipt=build(out);receipt['validation']=verify(f,masks,rows);receipt['status']='byte_identical_resource_new_generator_source';receipt['runtime_validated']=False
 (out/'reconstructed_numeric_specs.h').write_text(c_specs(masks,rows,receipt))
 (out/'reconstructed-numeric-validation.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
