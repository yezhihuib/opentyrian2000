#!/usr/bin/env python3
"""Validate generated RFR3 files, not runtime integration."""
from pathlib import Path
import argparse,hashlib,json,struct

def fnv(b):
 h=14695981039346656037
 for n in b:h=((h^n)*1099511628211)&0xffffffffffffffff
 return h

def validate(root):
 manifest=json.loads((root/'reconstructed-manifest.json').read_text());rows=manifest['resources'];assert len(rows)==171 and not manifest['original_byte_identity']
 totals=[0]*6
 for r in rows:
  b=(root/r['filename']).read_bytes();assert len(b)==r['bytes'];assert hashlib.sha256(b).hexdigest()==r['sha256'];assert fnv(b)==r['file_fnv64'];assert fnv(b[:64])==r['header_fnv64']
  expected=(b'RFR3',3,64,r['width'],r['height'],r['dx'],r['dy'],r['advance256'],r['planes'],r['role_profile'],r['text_fnv64'],r['payload_fnv64'],r['font_prefix64'])
  assert struct.unpack('<4s4I2i3I3Q',b[:64])==expected
  assert fnv(r['text'].encode('ascii'))==r['text_fnv64'];assert fnv(b[64:])==r['payload_fnv64']
  n=r['width']*r['height'];assert len(b)==64+n*r['planes'];alpha=b[64:64+n];roles=b[64+n:64+2*n]
  assert all((a==0)==(c==0) for a,c in zip(alpha,roles));assert all(c==0 or r['role_min']<=c<=r['role_max'] for c in roles)
  assert 0<r['width']<=528 and 0<r['height']<=74
  if r['planes']==3:assert r['family']==1 and all(s>=a for s,a in zip(b[64+2*n:],alpha))
  else:assert r['family']!=1
  # One full canonical-pixel transparent border preserves bounded support.
  for plane in [alpha]+([b[64+2*n:]] if r['planes']==3 else []):
   w=r['width'];h=r['height'];assert not any(plane[:w]+plane[-w:]);assert all(plane[y*w]==plane[y*w+w-1]==0 for y in range(h))
  totals[r['family']]+=len(b)
 assert totals==[397036,297787,220696,282680,448500,1656492]
 return {'status':'resource_validation_passed_not_runtime_validation','runs':len(rows),'family_file_bytes':totals,'total_file_bytes':sum(totals),'header_payload_sha_and_fnv_verified':True,'transparent_border_verified':True,'role_support_verified':True,'main_true_contour_ge_face_verified':True,'original_byte_identity':False}
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parent);parser.add_argument('--receipt',type=Path);a=parser.parse_args();result=validate(a.root)
 if a.receipt:a.receipt.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2))
