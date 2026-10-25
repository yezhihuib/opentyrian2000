#!/usr/bin/env python3
"""Derive finite real master geometry edits without changing the source repository."""
from pathlib import Path
import sys,json,hashlib
root=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve();out.mkdir(parents=True,exist_ok=False)
sys.path.insert(0,str(root/'scripts'))
import current_rear281_compatibility as q
import current_rear1_compatibility as n
import current_rear39_compatibility as r
import current_rear_p7_compatibility as p
sha=lambda b:hashlib.sha256(b).hexdigest()
def fnv(b):
 h=14695981039346656037
 for c in b:h=((h^c)*1099511628211)&((1<<64)-1)
 return format(h,'016x')
modules=(q,n,r,p);bootstrap={};bindings={}
for m in modules:
 raw=(root/m.SELECTION).read_bytes();selected,pngs,blobs=m.generate(root,raw);bootstrap[m]=blobs
 for name in (selected['recipe']['path'],selected['masters'][0].get('source_json',selected['masters'][0].get('source_svg'))):
  dest=out/'inputs'/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((root/name).read_bytes());bindings[name]=sha(dest.read_bytes())
 bindings[m.SELECTION]=sha(raw)
 bindings[str(Path(m.__file__).relative_to(root))]=sha(Path(m.__file__).read_bytes())
results={};edits=[]
for m,old,new,key in ((q,b'C5.15 5.07',b'C5.10 5.07','source_json'),(n,b'C10.95 4',b'C10.85 4','source_json'),(r,b'11 5.25',b'10.9 5.25','source_json'),(p,b'Q8.9 1 9 1',b'Q8.8 1 8.9 1','source_svg')):
 selected=json.loads((root/m.SELECTION).read_bytes());source=out/'inputs'/selected['masters'][0][key];raw=source.read_bytes();assert raw.count(old)==(2 if m is p else 1)
 raw=raw.replace(old,new);source.write_bytes(raw);selected['masters'][0]['source_sha256']=sha(raw);selected['schema']=m.CANDIDATE_SCHEMA;selected.pop('resources')
 encoded=(json.dumps(selected,indent=2)+'\n').encode();(out/(m.__name__+'-candidate.json')).write_bytes(encoded)
 normalized,pngs,blobs=m.generate(out/'inputs',encoded,True);assert all(blobs[k]!=bootstrap[m][k] for k in blobs)
 results[m]=blobs;edits.append({'module':m.__name__,'old':old.decode(),'new':new.decode(),'edited_master_sha256':sha(raw)})
for label,changed in [('rear281-edit',(q,)),('rear281-rear1-edit',(q,n)),('rear281-rear1-rear39-edit',(q,n,r)),('all-edit',(q,n,r,p))]:
 directory=out/label;directory.mkdir();full={m:(results[m] if m in changed else bootstrap[m]) for m in modules};blobs={}
 for m in modules:
  for pair,blob in full[m].items():
   name=m.name(*pair);(directory/name).write_bytes(blob);blobs[name]=blob
 header=q.payload_header({k:fnv(v[28:]) for k,v in full[q].items()},{k:fnv(v[28:]) for k,v in full[p].items()},{k:fnv(v[28:]) for k,v in full[r].items()},{k:fnv(v[28:]) for k,v in full[n].items()})
 (directory/'current_rear_multi_payload_pins.h').write_bytes(header)
 (directory/'receipt.json').write_text(json.dumps({'hda_sha256':{name:sha(v) for name,v in blobs.items()},'changed_pairs':[list(k) for m in modules for k,v in full[m].items() if v!=bootstrap[m][k]],'header_sha256':sha(header)},indent=2)+'\n')
bindings['src/current_rear_multi_payload_pins.h']=sha((root/'src/current_rear_multi_payload_pins.h').read_bytes())
(out/'source-bindings.json').write_text(json.dumps(bindings,indent=2)+'\n');(out/'edits.json').write_text(json.dumps(edits,indent=2)+'\n')
print('Independent geometry variants generated: Rear281 twenty; +Rear1 twenty-eight; +Rear39 thirty-four; all thirty-eight')
