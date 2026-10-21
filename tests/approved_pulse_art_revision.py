"""Narrow projection for historical unchanged-resource assertions.
The approval is pinned, validates full new rows, and permits only five Pulse
art payload/provenance revisions. It never projects family/source identity.
"""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
APPROVAL_SHA256='7fd82f64f875cb68f550c08db736b7e25f1ab365c2c704df252838774263ae5f'
IDS=(80058,80059,80060,80062,80165)
def approval():
 p=ROOT/'packaging/pulse-art-approved-v2.json';raw=p.read_bytes()
 if hashlib.sha256(raw).hexdigest()!=APPROVAL_SHA256:raise ValueError('Pulse art approval fingerprint changed')
 j=json.loads(raw)
 if j['schema']!='opentyrian-approved-pulse-art-revision-v2' or tuple(x['identity'] for x in j['revisions'])!=IDS:raise ValueError('Unexpected Pulse art revision scope')
 for x in j['revisions']:
  old,new=x['previous'],x['current']
  if old['identity']!=x['identity'] or new['identity']!=x['identity']:raise ValueError('Pulse identity changed')
  for key in set(old)|set(new):
   if key not in ('path','sha256','payload_fnv64','provenance') and old.get(key)!=new.get(key):raise ValueError('Non-art Pulse field changed')
 return j

def project_previous_art(resources):
 allowed={x['identity']:x for x in approval()['revisions']};result=[]
 for row in resources:
  item=allowed.get(row['identity'])
  if item:
   if row!=item['current']:raise ValueError('Unapproved Pulse row mutation: '+str(row['identity']))
   result.append(item['previous'])
  else:result.append(row)
 return result
