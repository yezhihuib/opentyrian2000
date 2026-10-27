"""Exact fighter165 NEWSHF extension over qualified private ca1d78f2; old ledgers stay immutable.

Every new input and changed prior path is independently qualified before older
oracles see exact preimages. This proof never invokes an older proof recursively.
"""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
PRIVATE_BASE='ca1d78f229a325d2624daebbef7996e0d79e3a6c'
LEDGER='tests/current_fighter165_newshf_source_projection.json'
LEDGER_SHA256='5af69306936734bf004ac8586bca8ff5794ce800459a8724ec898942ddb93eca'
SRC_FILES={'src/global_newshf_mirror.inc','src/newshf_identity_validation.inc'}
FILES=SRC_FILES|{'tests/scout164_newshf_projection.py','tests/test_scout164_newshf_projection.py','tests/test_shapesy_cyan_secondary_projection.py','tests/test_shapesy_cyan_projection.py','tests/test_shapesy_platform_projection.py','tests/accepted_later_changes.py','tests/shop_current_acceptance.py','tests/_projection_proof_context.py','scripts/package_runtime.py','scripts/rebuild_recovered_runtime_manifest.py','scripts/shared_asset_special_sources.py','scripts/current_sidekick_body_compatibility.py'}
ADDED={'src/newshf_fighter165_pins.h','src/current_fighter165_newshf_hd_assets.h'}
sha=lambda raw:hashlib.sha256(raw).hexdigest()
def ledger():
 raw=(ROOT/LEDGER).read_bytes();assert sha(raw)==LEDGER_SHA256,'fighter165 NEWSHF ledger is not frozen'
 spec=json.loads(raw);assert spec['private_base']==PRIVATE_BASE
 assert set(spec['files'])==FILES and set(spec['added_sources'])==ADDED
 return spec

def inverse(name,raw,pin):
 assert sha(raw)==pin['current_sha256'],('unapproved fighter165 NEWSHF current bytes',name)
 lines=raw.splitlines(keepends=True)
 for h in reversed(pin['hunks']):
  a,b=h['after_lines'];assert b''.join(lines[a:b])==h['after'].encode(),('fighter165 NEWSHF hunk drift',name)
  lines[a:b]=h['before'].encode().splitlines(keepends=True)
 result=b''.join(lines);assert sha(result)==pin['previous_sha256'],('fighter165 NEWSHF preimage drift',name)
 return result

def project_source(name,raw):
 from interceptor166_newshf_projection import project_if_current as newer
 if name not in FILES:return newer(name,raw)
 return inverse(name,newer(name,raw),ledger()['files'][name])

def project_if_current(name,raw):
 from interceptor166_newshf_projection import project_if_current as newer
 if name not in FILES:return newer(name,raw)
 pin=ledger()['files'][name]
 if sha(raw)==pin['previous_sha256']:return raw
 return inverse(name,newer(name,raw),pin)

def checked_read(root,name):
 p=root/name
 assert p.is_file() and not p.is_symlink() and not any(q.is_symlink() for q in p.parents),('unsafe fighter165 NEWSHF input',name)
 from interceptor166_newshf_projection import project_if_current as newer
 return newer(name,p.read_bytes())

def qualified_paths(root=ROOT):
 from interceptor166_newshf_projection import qualified_paths as newer_paths
 spec=ledger();return newer_paths(root)|set(spec['qualified'])|FILES|{LEDGER,'tests/fighter165_newshf_projection.py'}

def verified(root=ROOT):
 from interceptor166_newshf_projection import verified as newer_verified, before_inventory as newer_before
 newer_verified(root)
 spec=ledger()
 for name,h in spec['qualified'].items():assert sha(checked_read(root,name))==h,('unqualified fighter165 NEWSHF input',name)
 for name,pin in spec['files'].items():inverse(name,checked_read(root,name),pin)
 scripts=str(ROOT/'scripts')
 if scripts not in sys.path:sys.path.insert(0,scripts)
 import current_fighter165_newshf_compatibility as c
 from verify_current_production import source_inventory
 expected=dict(spec['base_source_inventory']);expected.update(spec['added_sources'])
 expected.update({n:spec['files'][n]['current_sha256'] for n in SRC_FILES})
 assert newer_before(source_inventory(root),root)==expected,'cyan whole source directory drift'
 mapping=c.load(root)
 assert len(mapping)==3 and set(r['identity'] for r in mapping.values())==set(c.IDS)
 required=c.input_paths(root)|c.generated_paths()|{c.HEADER,c.MAPPING}|{c.ROOT+'/'+c.name(i) for i in c.IDS}|ADDED
 assert required<=set(spec['qualified'])
 assert {n:spec['qualified'][n] for n in ADDED}==spec['added_sources']
 for top in ('authoring-inputs/newshf-fighter165','assets/hd/current-compat/newshf-fighter165'):
  actual={p.relative_to(root).as_posix() for p in (root/top).rglob('*') if p.is_file() or p.is_symlink()}
  assert actual=={n for n in spec['qualified'] if n.startswith(top+'/')},('fighter165 NEWSHF input directory closure drift',top)
 assets={n:{'sha256':h,'mode':'100644'} for n,h in spec['qualified'].items() if n.startswith('assets/')}
 assert set(assets)=={c.SELECTION}|{c.ROOT+'/'+c.name(i) for i in c.IDS},'fighter165 NEWSHF asset scope drift'
 return dict(mapping=mapping,added_sources=spec['added_sources'],assets=assets,paths=qualified_paths(root))

def before_inventory(inventory,root=ROOT):
 from verify_current_production import source_inventory
 from interceptor166_newshf_projection import before_inventory as newer_before
 proof=verified(root);result=newer_before(inventory,root)
 for n,h in proof['added_sources'].items():assert result.pop(n)==h,('fighter165 NEWSHF source addition drift',n)
 for n in SRC_FILES:
  raw=checked_read(root,n);assert result[n]==sha(raw),('fighter165 NEWSHF live source inventory drift',n)
  result[n]=sha(project_source(n,raw))
 return result

def before_runtime(rows,root=ROOT):
 from interceptor166_newshf_projection import before_runtime as newer_before
 rows=newer_before(rows,root)
 proof=verified(root);mapping=proof['mapping'];result=[];seen=set()
 import current_fighter165_newshf_compatibility as c
 for row in rows:
  dest=row['destination']
  if dest not in mapping:result.append(row);continue
  q=mapping[dest];raw=checked_read(root,q['source_path'])
  expected=dict(destination=dest,source_path=q['source_path'],sha256=sha(raw),bytes=len(raw),git_blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),group='newshf-optin',revision=c.REVISION)
  assert row==expected and dest not in seen,('fighter165 NEWSHF runtime row drift',dest);seen.add(dest)
 assert seen==set(mapping),'missing fighter165 NEWSHF runtime row'
 return result

def drop_additions(inventory,root=ROOT):
 from interceptor166_newshf_projection import before_inventory as newer_before
 proof=verified(root);result=newer_before(inventory,root)
 for n,h in proof['added_sources'].items():assert result.pop(n)==h,('fighter165 NEWSHF source addition drift',n)
 return result
