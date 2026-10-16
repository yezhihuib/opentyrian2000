#!/usr/bin/env python3
"""Exact accepted-R2 component preview. Standard library only; no original data.
Whole-canvas flip, integer translation, bounded clipping, byte-exact union.
No new generation, blur, resampling, recoloring, normalization, or HDA packing.
"""
from pathlib import Path
import argparse,hashlib,itertools,json,struct,zlib
ROOT=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()

def pp(b):return list(zip(*[iter(b)]*4))
def png(b,w,h):
 raw=b''.join(b'\0'+b[y*w*4:(y+1)*w*4]for y in range(h));z=bytearray(b'\x78\x01')
 for pos in range(0,len(raw),65535):
  part=raw[pos:pos+65535];z+=bytes([int(pos+len(part)==len(raw))])+struct.pack('<HH',len(part),65535-len(part))+part
 z+=struct.pack('>I',zlib.adler32(raw)&0xffffffff)
 def chunk(t,d):return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
 return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>2I5B',w,h,8,6,0,0,0))+chunk(b'IDAT',z)+chunk(b'IEND',b'')
def transformed(b,d,fy,dx,dy):
 w,h=12*d,14*d;out={}
 for k,p in enumerate(pp(b)):
  if not p[3]:assert p==(0,0,0,0);continue
  x=k%w+dx*d;y=(h-1-k//w if fy else k//w)+dy*d
  out[x,y]=p
 return out

def sample_map(q,d,s):
 # Sample virtual union on a grid anchored to the unshifted logical 12x14 canvas.
 # Include the surrounding logical margin only for clipping quantification.
 return {(x,y):q[( (2*x+1)*d//(2*s),(2*y+1)*d//(2*s))]
  for y in range(-14*s,28*s)for x in range(-12*s,24*s)
  if ((2*x+1)*d//(2*s),(2*y+1)*d//(2*s))in q}
def canvas(q,d):return bytes(c for y in range(14*d)for x in range(12*d)for c in q.get((x,y),(0,0,0,0)))
def stats(q):
 p=list(q.values());e=[sum(v[c]*v[3]for v in p)for c in range(3)]
 return {'supported_samples':len(p),'maximum_alpha':max([v[3]for v in p]or[0]),'RGB_range':[[min(v[c]for v in p),max(v[c]for v in p)]for c in range(3)]if p else None,'alpha_sum':sum(v[3]for v in p),'premultiplied_RGB_C_times_A':e,'weighted_luma_C_times_A_2126_7152_722':sum(a*b for a,b in zip(e,[2126,7152,722])),
  'bounds_exclusive':[min(x for x,y in q),min(y for x,y in q),max(x for x,y in q)+1,max(y for x,y in q)+1]if q else None}
def clipping(q,d):
 kept={k:v for k,v in q.items()if 0<=k[0]<12*d and 0<=k[1]<14*d};lost={k:v for k,v in q.items()if k not in kept}
 full,ks,ls=map(stats,[q,kept,lost]);return kept,lost,{'full_unbounded':full,'retained':ks,'clipped':ls,'clipped_alpha_fraction':ls['alpha_sum']/full['alpha_sum'],'clipped_luma_fraction':ls['weighted_luma_C_times_A_2126_7152_722']/full['weighted_luma_C_times_A_2126_7152_722']}
def runtime_over(bg,p):return tuple((bg[c]*(255-p[3])+p[c]*p[3]+127)//255 for c in range(3))
def run(out):
 out.mkdir(parents=True,exist_ok=True);spec=json.loads((ROOT/'inputs.json').read_text());inputs={};results=[]
 for e in spec['inputs']:
  b=(ROOT/e['rgba']).read_bytes();assert sha(b)==e['rgba_sha256']and len(b)==12*14*e['density']**2*4
  assert sha((ROOT/e['png']).read_bytes())==e['png_sha256'];inputs[e['source_id'],e['density']]=b
 for target,parts in spec['components'].items():
  for d in[4,8]:
   qs=[transformed(inputs[sid,d],d,fy,dx,dy)for sid,fy,dx,dy in parts]
   assert all(not(set(a)&set(b))for a,b in itertools.combinations(qs,2))
   full={k:v for q in qs for k,v in q.items()};kept,lost,st=clipping(full,d);raw=canvas(kept,d)
   hashes=[]
   for order in itertools.permutations(range(3)):
    q={k:v for i in order for k,v in qs[i].items()};assert q==full;hashes.append(sha(canvas(q,d)))
   assert len(set(hashes))==1
   stem=f'rear-multi-{target}-{d}-exact-clipped-union';(out/(stem+'.rgba')).write_bytes(raw);pb=png(raw,12*d,14*d);(out/(stem+'.png')).write_bytes(pb)
   native=[]
   for s in[1,2,4]:
    nq=sample_map(full,d,s);nk,nl,ns=clipping(nq,s)
    native.append({'scale':s,'stats':ns,'clipped_samples_xy_RGBA':[[*k,*v]for k,v in sorted(nl.items())],
     'retained_rgba_sha256':sha(canvas(nk,s)),
     'clipped_blend_effect_by_background':{name:{'changed_pixels':sum(runtime_over(bg,v)!=tuple(bg)for v in nl.values()),'maximum_absolute_channel_change':max([abs(runtime_over(bg,v)[c]-bg[c])for v in nl.values()for c in range(3)]or[0])}for name,bg in{'brown':[104,72,44],'cloud':[173,191,206]}.items()}})
   results.append({'target':int(target),'density':d,'parts':parts,'canvas':[12,14],'anchor':[0,0],
    'original_density_preserved':True,'rgba_sha256':sha(raw),'png_sha256':sha(pb),'rgba':stem+'.rgba','png':stem+'.png',
    'stats':st,'per_part_clipping':[clipping(q,d)[2]for q in qs],'overlap_authored_samples':0,'all_six_orders_byte_identical':True,
    'retained_RGBA_exact_from_single_component':True,'added_support_beyond_transformed_union':0,
    'clipped_samples_xy_RGBA':[[*k,*v]for k,v in sorted(lost.items())],'native':native})
 manifest={'schema':'rear-multi-p5-mode1-accepted-component-preview-v1','status':'OFFLINE_PREVIEW_ONLY_NOT_ART_ACCEPTANCE_OR_RUNTIME_QUALIFICATION','baseline':spec['published_baseline'],'tree':spec['published_tree'],
 'operation':'Whole 12x14 canvas flipY before integer logical translation, exact union clipped to original 12x14 canvas. Alpha supports are disjoint, so all source-over/max/overwrite orders on retained supports are identical. No additive or brightness adjustment.',
 'new_generation':False,'source_or_production_modified':False,'runtime_launched':False,'HDA_or_manifest_integration':False,'uploaded_or_published':False,
 'nearest_sampling':'floor((2*display_coordinate+1)*source_density/(2*display_scale))','runtime_blend':'floor((background*(255-alpha)+color*alpha+127)/255)',
 'clipping_warning':'This preview deliberately loses translated tail samples beyond the fixed original canvas. Whole-lobe multiset/energy preservation does not hold. Review native clipping before any integration.',
 'inputs':spec['inputs'],'results':results}
 (out/'component-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps([{'id':r['target'],'d':r['density'],'lost':r['stats']['clipped']['supported_samples'],'alpha_percent':100*r['stats']['clipped_alpha_fraction'],'luma_percent':100*r['stats']['clipped_luma_fraction'],'native_lost':{n['scale']:n['stats']['clipped']['supported_samples']for n in r['native']},'bounds':r['stats']['retained']['bounds_exclusive']}for r in results],indent=2))
 return manifest
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=ROOT/'output');args=ap.parse_args();run(args.output)
