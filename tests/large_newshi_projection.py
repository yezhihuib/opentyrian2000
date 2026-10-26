"""Exact large NEWSHI extension over qualified private a3eb7e2; old ledgers stay immutable.

Every new input and changed prior path is independently qualified before older
oracles see exact preimages. This proof never invokes an older proof recursively.
"""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
PRIVATE_BASE='a3eb7e215c53dfdecfb86b366fb1b0272400448b'
LEDGER='tests/current_large_newshi_source_projection.json'
LEDGER_SHA256='14f49fb6da1cb0dbfa96c77d434a01f60fb4cc474ed7e8ba9e2125b324ccad36'
SRC_FILES={'src/newshf_identity_validation.inc','src/global_newshf_mirror.inc'}
FILES=SRC_FILES|{'scripts/package_runtime.py','scripts/rebuild_recovered_runtime_manifest.py','scripts/shared_asset_special_sources.py','scripts/current_sidekick_body_compatibility.py','tests/turret_newshf_projection.py','tests/accepted_later_changes.py','tests/shop_current_acceptance.py','tests/_projection_proof_context.py'}
ADDED={'src/newshi_large_pins.h','src/current_large_newshi_hd_assets.h'}
sha=lambda raw:hashlib.sha256(raw).hexdigest()
def ledger():
 raw=(ROOT/LEDGER).read_bytes();assert sha(raw)==LEDGER_SHA256,'large NEWSHI ledger is not frozen'
 spec=json.loads(raw);assert spec['private_base']==PRIVATE_BASE
 assert set(spec['files'])==FILES and set(spec['added_sources'])==ADDED
 return spec

def inverse(name,raw,pin):
 assert sha(raw)==pin['current_sha256'],('unapproved large NEWSHI current bytes',name)
 lines=raw.splitlines(keepends=True)
 for h in reversed(pin['hunks']):
  a,b=h['after_lines'];assert b''.join(lines[a:b])==h['after'].encode(),('large NEWSHI hunk drift',name)
  lines[a:b]=h['before'].encode().splitlines(keepends=True)
 result=b''.join(lines);assert sha(result)==pin['previous_sha256'],('large NEWSHI preimage drift',name)
 return result

def project_source(name,raw):
 if name not in FILES:return raw
 from shapesy_cyan_projection import project_if_current as newer
 return inverse(name,newer(name,raw),ledger()['files'][name])

def project_if_current(name,raw):
 if name not in FILES:return raw
 pin=ledger()['files'][name]
 if sha(raw)==pin['previous_sha256']:return raw
 from shapesy_cyan_projection import project_if_current as newer
 return inverse(name,newer(name,raw),pin)

def checked_read(root,name):
 p=root/name
 assert p.is_file() and not p.is_symlink() and not any(q.is_symlink() for q in p.parents),('unsafe large NEWSHI input',name)
 from shapesy_cyan_projection import project_if_current as newer
 return newer(name,p.read_bytes())

def qualified_paths(root=ROOT):
 spec=ledger();return set(spec['qualified'])|FILES|{LEDGER,'tests/large_newshi_projection.py'}

def verified(root=ROOT):
 from shapesy_cyan_projection import verified as newer_verified
 newer_verified(root)
 spec=ledger()
 for name,h in spec['qualified'].items():assert sha(checked_read(root,name))==h,('unqualified large NEWSHI input',name)
 for name,pin in spec['files'].items():inverse(name,checked_read(root,name),pin)
 scripts=str(ROOT/'scripts')
 if scripts not in sys.path:sys.path.insert(0,scripts)
 import current_large_newshi_compatibility as c
 mapping=c.load(root)
 assert len(mapping)==10 and set(r['identity'] for r in mapping.values())==set(range(2100018,2100028))
 assert [(r['records'],r['base']) for r in mapping.values()]==[([rec],base) for rec,base,x,y in c.PARTS]+[([308],base) for base in (268,270,272)]
 required=c.input_paths(root)|c.generated_paths()|{c.HEADER,c.MAPPING}|{c.ROOT+'/'+c.name(i) for i in c.IDS}|ADDED
 assert required<=set(spec['qualified'])
 assert {n:spec['qualified'][n] for n in ADDED}==spec['added_sources']
 for top in ('authoring-inputs/newshi-large','assets/hd/current-compat/newshi-large'):
  actual={p.relative_to(root).as_posix() for p in (root/top).rglob('*') if p.is_file() or p.is_symlink()}
  assert actual=={n for n in spec['qualified'] if n.startswith(top+'/')},('large NEWSHI input directory closure drift',top)
 assets={n:{'sha256':h,'mode':'100644'} for n,h in spec['qualified'].items() if n.startswith('assets/')}
 assert set(assets)=={c.SELECTION}|{c.ROOT+'/'+c.name(i) for i in c.IDS},'large NEWSHI asset scope drift'
 return dict(mapping=mapping,added_sources=spec['added_sources'],assets=assets,paths=qualified_paths(root))

def before_inventory(inventory,root=ROOT):
 from shapesy_cyan_projection import before_inventory as newer_before
 proof=verified(root);result=newer_before(inventory,root)
 for n,h in proof['added_sources'].items():assert result.pop(n)==h,('large NEWSHI source addition drift',n)
 for n in SRC_FILES:
  raw=checked_read(root,n);assert result[n]==sha(raw),('large NEWSHI live source inventory drift',n)
  result[n]=sha(project_source(n,raw))
 return result

def before_runtime(rows,root=ROOT):
 from shapesy_cyan_projection import before_runtime as newer_before
 rows=newer_before(rows,root)
 proof=verified(root);mapping=proof['mapping'];result=[];seen=set()
 import current_large_newshi_compatibility as c
 for row in rows:
  dest=row['destination']
  if dest not in mapping:result.append(row);continue
  q=mapping[dest];raw=checked_read(root,q['source_path'])
  expected=dict(destination=dest,source_path=q['source_path'],sha256=sha(raw),bytes=len(raw),git_blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),group='newshf-optin',revision=c.REVISION)
  assert row==expected and dest not in seen,('large NEWSHI runtime row drift',dest);seen.add(dest)
 assert seen==set(mapping),'missing large NEWSHI runtime row'
 return result

def drop_additions(inventory,root=ROOT):
 from shapesy_cyan_projection import drop_additions as newer_drop
 proof=verified(root);result=newer_drop(inventory,root)
 for n,h in proof['added_sources'].items():assert result.pop(n)==h,('large NEWSHI source addition drift',n)
 return result
