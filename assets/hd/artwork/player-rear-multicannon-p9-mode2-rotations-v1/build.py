#!/usr/bin/env python3
"""Lossless asset coordinate conversion of accepted generated art only.

No original game inputs, drawing, filtering, resampling, recolor, or re-encoding
of the RGBA values. Each density is transformed independently at full density.
"""
from pathlib import Path
import argparse,hashlib,json,struct,zlib
ROOT=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def fnv(b):
 h=14695981039346656037
 for v in b:h=((h^v)*1099511628211)&((1<<64)-1)
 return f'{h:016x}'
def png(raw,w,h):
 def chunk(k,b):return struct.pack('>I',len(b))+k+b+struct.pack('>I',zlib.crc32(k+b)&0xffffffff)
 # Stored DEFLATE blocks make the asset PNG version-independent.
 scan=b''.join(b'\0'+raw[y*w*4:(y+1)*w*4] for y in range(h));blocks=[]
 for p in range(0,len(scan),65535):
  b=scan[p:p+65535];blocks.append(bytes([1 if p+len(b)==len(scan) else 0])+struct.pack('<HH',len(b),len(b)^65535)+b)
 stream=b'\x78\x01'+b''.join(blocks)+struct.pack('>I',zlib.adler32(scan)&0xffffffff)
 return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>2I5B',w,h,8,6,0,0,0))+chunk(b'IDAT',stream)+chunk(b'IEND',b'')
def transform(src,d,target):
 w,h=12*d,14*d;out=bytearray(len(src));clipped=0
 for y in range(h):
  for x in range(w):
   p=src[4*(y*w+x):4*(y*w+x+1)];xx=y if target==298 else w-1-y;yy=h-1-x
   if 0<=xx<w and 0<=yy<h:out[4*(yy*w+xx):4*(yy*w+xx+1)]=p
   else:
    assert p==bytes(4),'Nonzero RGBA would be clipped';clipped+=1
 return bytes(out),clipped
def mirror(src,d):
 w,h=12*d,14*d
 return b''.join(src[4*(y*w+w-1-x):4*(y*w+w-x)] for y in range(h) for x in range(w))
def stats(b,d):
 w,h=12*d,14*d;p=list(zip(*[iter(b)]*4));xy=[(i%w,i//w) for i,v in enumerate(p) if v[3]]
 return {'alpha_bounds_exclusive':[min(x for x,y in xy),min(y for x,y in xy),max(x for x,y in xy)+1,max(y for x,y in xy)+1],'alpha_sum':sum(v[3] for v in p),'alpha_nonzero_samples':len(xy),'fractional_alpha_samples':sum(0<v[3]<255 for v in p),'premultiplied_RGB_numerators':[sum(v[c]*v[3] for v in p) for c in range(3)],'transparent_black_canonical':all(not any(v) for v in p if not v[3])}
def build(out):
 assert not out.exists(),'Fresh output destination required';contract=json.loads((ROOT/'inputs.json').read_text());inputs={}
 for e in contract['inputs']:
  b=(ROOT/e['rgba']).read_bytes();assert sha(b)==e['rgba_sha256'] and fnv(b)==e['rgba_fnv1a64'] and sha((ROOT/e['png']).read_bytes())==e['png_sha256'];assert len(b)==168*e['density']**2*4;inputs[e['id'],e['density']]=b
 for d in [4,8]:assert mirror(inputs[277,d],d)==inputs[278,d]
 out.mkdir(parents=True);rows=[]
 for d in [4,8]:
  src=inputs[277,d];s=stats(src,d);results={}
  for target in [298,299]:
   b,clipped=transform(src,d,target);t=stats(b,d);assert t['transparent_black_canonical']
   for key in ['alpha_sum','alpha_nonzero_samples','fractional_alpha_samples','premultiplied_RGB_numerators']:assert s[key]==t[key]
   assert t['alpha_bounds_exclusive']==[v*d for v in ([0,3,10,14] if target==298 else [2,3,12,14])]
   stem=f'rear-multi-p9-{target}-{d}';pb=png(b,12*d,14*d);hb=struct.pack('<4s4I2i',b'HDR1',1310000+target,d,12,14,0,0)+b
   for suffix,raw in [('.rgba',b),('.png',pb),('.hda',hb)]:(out/(stem+suffix)).write_bytes(raw)
   results[target]=b;rows.append({'id':target,'role':131,'key':1310000+target,'density':d,'logical_size':[12,14],'anchor':[0,0],'source_id':277,'rgba':stem+'.rgba','rgba_sha256':sha(b),'rgba_fnv1a64':fnv(b),'png':stem+'.png','png_sha256':sha(pb),'hda':stem+'.hda','hda_sha256':sha(hb),'mapped_source_samples':144*d*d,'clipped_transparent_black_samples':clipped,'clipped_nonzero_RGBA_samples':0,'source_stats':s,'output_stats':t})
  assert mirror(results[298],d)==results[299]
 result={'schema':'rear-multicannon-p9-mode2-rigid-art-v1','status':'OFFLINE_CANDIDATE_NOT_INTEGRATED','logical_size':[12,14],'anchor':[0,0],'densities':[4,8],'source_lineage':'Accepted P5 mode2 generated277/278 exact rational lower-over-upper assembly of accepted generated281/282 vector masters; preserved RGBA as full-density coordinate permutation.','mapping':{'298':['y','14*d-1-x'],'299':['12*d-1-y','14*d-1-x']},'all_supported_RGBA_samples_preserved':True,'alpha_RGB_energy_preserved_exactly':True,'298_299_full_canvas_exact_horizontal_mirrors':True,'no_original_game_data_required':True,'no_original_data_or_captures_in_artifact':True,'no_resampling_filtering_normalization_recoloring':True,'outputs':rows,'limitations':['Offline transform proof and previews only. No ownership/compositor/gameplay/runtime acceptance.','Native sampling is performed on the transformed full-density resource. Transform after native sampling is not equivalent because of phase differences.','No new artistic geometry: exact rotation/canvas placement is justified by separately verified authentic original source indices and coverage.']}
 (out/'build-receipt.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'output');args=p.parse_args();r=build(args.output);print('PASS: four exact RGBA/PNG/HDR1 transforms; no supported sample or energy lost.')
