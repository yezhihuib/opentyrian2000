"""Finite, public-20f08096 based linked-family extension; no Git at verification."""
from pathlib import Path
import hashlib
import json
ROOT=Path(__file__).resolve().parents[1]
LEDGER='tests/current_linked_newshf_source_projection.json'
LEDGER_SHA256='28cf2c35b06d9a97491813b75f3963b06dfbfc2d20e23032acd4f682bf8f7d4e'
PUBLIC_BASE='20f08096b32652b6f3b22a48826f5bcb4ff6f44a'
sha=lambda b:hashlib.sha256(b).hexdigest()
def ledger():
 raw=(ROOT/LEDGER).read_bytes()
 assert sha(raw)==LEDGER_SHA256,'linked NEWSHF receipt changed or not frozen'
 spec=json.loads(raw)
 assert spec['public_base']==PUBLIC_BASE
 assert set(spec['files'])=={'src/newshf_identity_validation.inc','src/global_newshf_mirror.inc'}
 assert set(spec['added_sources'])=={'src/newshf_linked_pins.h','src/current_linked_newshf_hd_assets.h'}
 return spec

def project_source(name,raw):
 pin=ledger()['files'].get(name)
 if pin is None:return raw
 assert sha(raw)==pin['current_sha256'],('unapproved linked NEWSHF source',name)
 lines=raw.splitlines(keepends=True)
 for edit in reversed(pin['hunks']):
  start,end=edit['after_lines']
  assert b''.join(lines[start:end])==edit['after'].encode(),('linked inverse hunk drift',name)
  lines[start:end]=edit['before'].encode().splitlines(keepends=True)
 restored=b''.join(lines)
 assert sha(restored)==pin['previous_sha256'],('linked public preimage drift',name)
 return restored

def verified(root=ROOT):
 import sys
 spec=ledger()
 # Check immutable qualification before importing/running the authored recipe.
 for name,digest in spec['qualified'].items():
  p=root/name
  assert p.is_file() and not p.is_symlink(),('nonregular linked input',name)
  assert not any(q.is_symlink() for q in p.parents),('symlink linked input ancestor',name)
  assert sha(p.read_bytes())==digest,('unqualified linked input',name)
 scripts=str(ROOT/'scripts')
 if scripts not in sys.path:sys.path.insert(0,scripts)
 import current_linked_newshf_compatibility as c
 for name in spec['files']:project_source(name,c.read(root,name))
 mapping=c.load(root)
 assert len(mapping)==6 and len({r['identity'] for r in mapping.values()})==6
 names={'scripts/register_linked_newshf.py','authoring-inputs/newshf-linked/registration.json','authoring-inputs/newshf-linked/raw/cold-whole-v2.png','authoring-inputs/newshf-linked/raw/bottom-firing-whole-v1.png','authoring-inputs/newshf-linked/raw/middle-alternate-whole-v1.png','authoring-inputs/newshf-linked/raw/generation-provenance.txt'}|c.input_paths(root)|{'scripts/current_linked_newshf_compatibility.py','scripts/build_current_linked_newshf.py','scripts/check_linked_newshf_pins.py'}|set(spec['added_sources'])|{c.MAPPING}|{r['source_path'] for r in mapping.values()}|{r['source_png'] for r in mapping.values()}
 assert set(spec['qualified'])==names,'linked qualified scope drift'
 return dict(mapping=mapping,added_sources=spec['added_sources'],paths=names,
  assets={n:{'sha256':spec['qualified'][n],'mode':'100644'} for n in names if n.startswith('assets/')})

def before_inventory(inventory,root=ROOT):
 result=dict(inventory);proof=verified(root)
 for name,digest in proof['added_sources'].items():assert result.pop(name)==digest
 for name in ledger()['files']:
  raw=(root/name).read_bytes();assert result[name]==sha(raw)
  result[name]=sha(project_source(name,raw))
 return result

def before_runtime(rows,root=ROOT):
 proof=verified(root);mapping=proof['mapping'];seen=set();result=[]
 for row in rows:
  dest=row['destination']
  if dest not in mapping:result.append(row);continue
  current=mapping[dest];raw=(root/current['source_path']).read_bytes()
  expected=dict(destination=dest,source_path=current['source_path'],sha256=sha(raw),bytes=len(raw),git_blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),group='newshf-optin',revision='current-single-source-linked-newshf-six')
  assert row==expected and dest not in seen,'linked runtime drift';seen.add(dest)
 assert seen==set(mapping),'missing linked runtime consumer'
 return result
