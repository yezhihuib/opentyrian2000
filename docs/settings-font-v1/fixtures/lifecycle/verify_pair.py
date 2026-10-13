#!/usr/bin/env python3
import pathlib,hashlib,json,csv
root=pathlib.Path(__file__).resolve().parent.parent
skip={'owner','lease_active','lease_frame','commands','generation','framebuffer_fnv64'}
def sha(b):return hashlib.sha256(b).hexdigest()
def verify(ref,cand,fallback):
 result={'candidate':cand.parent.name,'artifacts':{},'fallback_required':fallback}
 for n in ['indexed-palette-stream.bin','semantics.tsv']:
  left=(ref/n).read_bytes();right=(cand/n).read_bytes();assert left==right,(cand,n);result['artifacts'][n]={'bytes':len(left),'sha256':sha(left),'equal':True}
 rr=list(csv.DictReader((ref/'presentations.tsv').open(),delimiter='\t'));cr=list(csv.DictReader((cand/'presentations.tsv').open(),delimiter='\t'));assert len(rr)==len(cr)
 for i,(l,r) in enumerate(zip(rr,cr)):
  assert {k:v for k,v in l.items() if k not in skip}=={k:v for k,v in r.items() if k not in skip},(cand,i,'semantic')
  assert l['owner']=='classic'
  if fallback:assert r['owner']=='classic' and r['lease_active']=='0'
  if r['owner']=='classic':assert l['framebuffer_fnv64']==r['framebuffer_fnv64'],(cand,i,'fallback frame')
 result['presentations']=len(rr);result['enhanced']=sum(r['owner']=='settings' for r in cr);result['classic']=len(cr)-result['enhanced']
 for n in ['opentyrian.cfg','tyrian.cfg']:
  l=ref.parent/'config/opentyrian2000'/n;r=cand.parent/'config/opentyrian2000'/n;assert l.exists()==r.exists()
  if l.exists():assert l.read_bytes()==r.read_bytes();result['artifacts'][n]={'equal':True,'sha256':sha(l.read_bytes())}
 result['result']='PASS';return result

p=root/'settings-font-lifecycle-profiles-20261013';result=verify(p/'reference/output',p/'candidate/output',False)
(root/'settings-font-lifecycle-fixture-20261013/PAIR_REPORT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
