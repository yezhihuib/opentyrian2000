#!/usr/bin/env python3
"""Derive finite real geometry edits from two independent lobe masters and four prior families."""
from pathlib import Path
import sys,json,hashlib
root=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve();out.mkdir(parents=True,exist_ok=False)
sys.path.insert(0,str(root/'scripts'))
import current_rear_lobes_compatibility as l
import current_rear281_compatibility as q
import current_rear1_compatibility as n
import current_rear39_compatibility as r
import current_rear_p7_compatibility as p
sha=lambda b:hashlib.sha256(b).hexdigest()
def fnv(b):
 h=14695981039346656037
 for c in b:h=((h^c)*1099511628211)&((1<<64)-1)
 return format(h,'016x')
modules=(l,q,n,r,p);bootstrap={};bindings={}
for m in modules:
 raw=(root/m.SELECTION).read_bytes();selected,pngs,blobs=m.generate(root,raw);bootstrap[m]=blobs
 names=[selected['recipe']['path']]+[row.get('source_json',row.get('source_svg')) for row in selected['masters']]
 for name in names:
  dest=out/'inputs'/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((root/name).read_bytes());bindings[name]=sha(dest.read_bytes())
 bindings[m.SELECTION]=sha(raw);bindings[str(Path(m.__file__).relative_to(root))]=sha(Path(m.__file__).read_bytes())
results={};edits=[]
for m,selector,old,new,key,label in ((l,203,b'C.63 4',b'C.66 4','source_json','lobes203'),(l,43,b'C3.66 1',b'C3.70 1','source_json','lobes43'),(q,281,b'C5.15 5.07',b'C5.10 5.07','source_json','rear281'),(n,1,b'C10.95 4',b'C10.85 4','source_json','rear1'),(r,39,b'11 5.25',b'10.9 5.25','source_json','rear39'),(p,294,b'Q8.9 1 9 1',b'Q8.8 1 8.9 1','source_svg','p7')):
 selected=json.loads((root/m.SELECTION).read_bytes());input_root=out/(label+'-input');input_root.mkdir();
 for name in [selected['recipe']['path']]+[x[key] for x in selected['masters']]:
  dest=input_root/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((root/name).read_bytes())
 row=next(row for row in selected['masters'] if row['selector']==selector);source=input_root/row[key];raw=(root/row[key]).read_bytes();assert raw.count(old)==(2 if m is p else 1)
 raw=raw.replace(old,new);source.write_bytes(raw);row['source_sha256']=sha(raw);selected['schema']=m.CANDIDATE_SCHEMA;selected.pop('resources')
 # Other independent lobe master remains original for each single-master test.
 for other in selected['masters']:
  if other is not row:(input_root/other[key]).write_bytes((root/other[key]).read_bytes())
 encoded=(json.dumps(selected,indent=2)+'\n').encode();(out/(label+'-candidate.json')).write_bytes(encoded)
 normalized,pngs,blobs=m.generate(input_root,encoded,True)
 expected=4 if m is l else len(blobs);assert sum(v!=bootstrap[m][k] for k,v in blobs.items())==expected
 results[label]=(m,blobs);edits.append({'module':m.__name__,'selector':selector,'old':old.decode(),'new':new.decode(),'edited_master_sha256':sha(raw)})
labels={k:(k,) for k in results};labels['both-edit']=('lobes203','lobes43');labels['all-edit']=tuple(results)
for label,changed in labels.items():
 directory=out/label;directory.mkdir();full={m:dict(bootstrap[m]) for m in modules};blobs={}
 for k in changed:
  m,edited=results[k]
  for pair,blob in edited.items():
   if blob!=bootstrap[m][pair]:full[m][pair]=blob
 for m in modules:
  for pair,blob in full[m].items():
   name=m.name(*pair);(directory/name).write_bytes(blob);blobs[name]=blob
 pins={m:{k:fnv(v[28:]) for k,v in full[m].items()} for m in modules}
 header=l.payload_header(pins[l],pins[p],pins[r],pins[n],pins[q]);(directory/'current_rear_multi_payload_pins.h').write_bytes(header)
 (directory/'receipt.json').write_text(json.dumps({'hda_sha256':{name:sha(v) for name,v in blobs.items()},'changed_pairs':[list(k) for m in modules for k,v in full[m].items() if v!=bootstrap[m][k]],'header_sha256':sha(header)},indent=2)+'\n')
bindings['src/current_rear_multi_payload_pins.h']=sha((root/'src/current_rear_multi_payload_pins.h').read_bytes())
(out/'source-bindings.json').write_text(json.dumps(bindings,indent=2)+'\n');(out/'edits.json').write_text(json.dumps(edits,indent=2)+'\n')
print('Independent geometry variants generated: each lobe master four; both eight; all families forty-six')
