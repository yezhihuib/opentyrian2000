#!/usr/bin/env python3
"""Compare bounded fixture evidence. No launch or source mutation."""
import argparse,csv,hashlib,json,pathlib
p=argparse.ArgumentParser();p.add_argument('reference',type=pathlib.Path);p.add_argument('candidate',type=pathlib.Path);p.add_argument('--out',type=pathlib.Path,required=True);a=p.parse_args();report={'schema':'settings-actual-pair-v1'}
for n in ['indexed-palette-stream.bin','semantics.tsv']:
 left=(a.reference/n).read_bytes();right=(a.candidate/n).read_bytes();report[n]={'equal':left==right,'reference_bytes':len(left),'candidate_bytes':len(right),'reference_sha256':hashlib.sha256(left).hexdigest(),'candidate_sha256':hashlib.sha256(right).hexdigest()}
 if left!=right:raise SystemExit(f'A/B mismatch: {n}')
def rows(d):return list(csv.DictReader((d/'presentations.tsv').open(),delimiter='\t'))
r,c=rows(a.reference),rows(a.candidate);assert len(r)==len(c) and len(c)<=256
ignore={'owner','lease_active','lease_frame','commands','generation'}
for i,(old,new) in enumerate(zip(r,c)):
 assert {k:v for k,v in old.items() if k not in ignore}=={k:v for k,v in new.items() if k not in ignore},('semantic present mismatch',i)
 assert old['owner']=='classic',('unexpected reference owner',i)
report['presentations']=len(c);report['captures']=[]
for old,new in zip(r,c):
 if new['image']=='-':continue
 name=new['image'];classic='classic' in name
 assert new['owner']==('classic' if classic else 'settings'),('unexpected candidate owner',name,new['owner'])
 if not classic:assert new['lease_active']=='1' and new['lease_frame']=='1' and int(new['commands'])>0
 left=(a.reference/(name+'.bmp')).read_bytes();right=(a.candidate/(name+'.bmp')).read_bytes()
 assert (left==right)==classic,('expected raster equality/difference',name)
 report['captures'].append({'name':name,'owner':new['owner'],'width':int(new['width']),'height':int(new['height']),'byte_equal':left==right})
assert len(report['captures'])<=10
report['saved_configuration']={}
for name in ['opentyrian.cfg','tyrian.cfg']:
 left=a.reference.parent/'config/opentyrian2000'/name;right=a.candidate.parent/'config/opentyrian2000'/name
 assert left.exists()==right.exists(),('configuration presence mismatch',name)
 if left.exists():
  lb=left.read_bytes();rb=right.read_bytes();assert lb==rb,('saved configuration mismatch',name);report['saved_configuration'][name]={'equal':True,'bytes':len(lb),'sha256':hashlib.sha256(lb).hexdigest()}
report['result']='PASS';report['visual_review']='PENDING';report['wall_time_equality']='Not asserted; original wait call stream compared.';a.out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
