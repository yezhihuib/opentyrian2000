"""Exact turret extension over qualified private d2937f0; old ledgers stay immutable.

Every new input and changed prior path is independently qualified before older
oracles see exact preimages. This proof never invokes an older proof recursively.
"""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
PRIVATE_BASE='d2937f0471de5f9b967dfdab4314aad213d5a928'
LEDGER='tests/current_turret_newshf_source_projection.json'
LEDGER_SHA256='f17a90d8c64bb87e41e132ed2a1f412b354ac8680103e0ed20e83e24b0a137e5'
SRC_FILES={'src/newshf_identity_validation.inc','src/global_newshf_mirror.inc'}
FILES=SRC_FILES|{'scripts/package_runtime.py','scripts/rebuild_recovered_runtime_manifest.py','scripts/shared_asset_special_sources.py','scripts/current_sidekick_body_compatibility.py','tests/dualmissile_newshf_projection.py','tests/shapesy_platform_projection.py','tests/accepted_later_changes.py','tests/shop_current_acceptance.py','tests/_projection_proof_context.py'}
ADDED={'src/newshf_turret_pins.h','src/current_turret_newshf_hd_assets.h'}
sha=lambda raw:hashlib.sha256(raw).hexdigest()
def ledger():
 raw=(ROOT/LEDGER).read_bytes();assert sha(raw)==LEDGER_SHA256,'turret ledger is not frozen'
 spec=json.loads(raw);assert spec['private_base']==PRIVATE_BASE
 assert set(spec['files'])==FILES and set(spec['added_sources'])==ADDED
 return spec

def inverse(name,raw,pin):
 assert sha(raw)==pin['current_sha256'],('unapproved turret current bytes',name)
 lines=raw.splitlines(keepends=True)
 for h in reversed(pin['hunks']):
  a,b=h['after_lines'];assert b''.join(lines[a:b])==h['after'].encode(),('turret hunk drift',name)
  lines[a:b]=h['before'].encode().splitlines(keepends=True)
 result=b''.join(lines);assert sha(result)==pin['previous_sha256'],('turret preimage drift',name)
 return result

def project_source(name,raw):
 if name not in FILES:return raw
 pin=ledger()['files'][name]
 if sha(raw)==pin['current_sha256']:return inverse(name,raw,pin)
 from shapesy_cyan_projection import project_if_current as cyan_project
 raw=cyan_project(name,raw)
 from large_newshi_projection import project_if_current as newer
 return inverse(name,newer(name,raw),ledger()['files'][name])

def project_if_current(name,raw):
 if name not in FILES:return raw
 pin=ledger()['files'][name]
 if sha(raw)==pin['previous_sha256']:return raw
 if sha(raw)==pin['current_sha256']:return inverse(name,raw,pin)
 from shapesy_cyan_projection import project_if_current as cyan_project
 raw=cyan_project(name,raw)
 from large_newshi_projection import project_if_current as newer
 return inverse(name,newer(name,raw),pin)

def checked_read(root,name):
 p=root/name
 assert p.is_file() and not p.is_symlink() and not any(q.is_symlink() for q in p.parents),('unsafe turret input',name)
 from large_newshi_projection import project_if_current as newer
 from shapesy_cyan_projection import project_if_current as cyan_project
 return newer(name,cyan_project(name,p.read_bytes()))

def qualified_paths(root=ROOT):
 spec=ledger();return set(spec['qualified'])|FILES|{LEDGER,'tests/turret_newshf_projection.py'}

def verified(root=ROOT):
 from large_newshi_projection import verified as newer_verified
 newer_verified(root)
 spec=ledger()
 for name,h in spec['qualified'].items():assert sha(checked_read(root,name))==h,('unqualified turret input',name)
 for name,pin in spec['files'].items():inverse(name,checked_read(root,name),pin)
 scripts=str(ROOT/'scripts')
 if scripts not in sys.path:sys.path.insert(0,scripts)
 import current_turret_newshf_compatibility as c
 mapping=c.load(root)
 assert len(mapping)==2 and set(r['identity'] for r in mapping.values())=={2100016,2100017}
 assert all(r['records']==[162,840] for r in mapping.values()) and {r['base'] for r in mapping.values()}=={39,41}
 required=c.input_paths(root)|c.generated_paths()|{c.HEADER,c.MAPPING}|{c.ROOT+'/'+c.name(i) for i in c.IDS}|ADDED
 assert required<=set(spec['qualified'])
 assert {n:spec['qualified'][n] for n in ADDED}==spec['added_sources']
 for top in ('authoring-inputs/newshf-turret','assets/hd/current-compat/newshf-turret'):
  actual={p.relative_to(root).as_posix() for p in (root/top).rglob('*') if p.is_file() or p.is_symlink()}
  assert actual=={n for n in spec['qualified'] if n.startswith(top+'/')},('turret input directory closure drift',top)
 assets={n:{'sha256':h,'mode':'100644'} for n,h in spec['qualified'].items() if n.startswith('assets/')}
 assert set(assets)=={c.SELECTION}|{c.ROOT+'/'+c.name(i) for i in c.IDS},'turret asset scope drift'
 return dict(mapping=mapping,added_sources=spec['added_sources'],assets=assets,paths=qualified_paths(root))

def before_inventory(inventory,root=ROOT):
 from large_newshi_projection import before_inventory as newer_before
 proof=verified(root);result=newer_before(inventory,root)
 for n,h in proof['added_sources'].items():assert result.pop(n)==h,('turret source addition drift',n)
 for n in SRC_FILES:
  raw=checked_read(root,n);assert result[n]==sha(raw),('turret live source inventory drift',n)
  result[n]=sha(project_source(n,raw))
 return result

def before_runtime(rows,root=ROOT):
 from large_newshi_projection import before_runtime as newer_before
 rows=newer_before(rows,root)
 proof=verified(root);mapping=proof['mapping'];result=[];seen=set()
 import current_turret_newshf_compatibility as c
 for row in rows:
  dest=row['destination']
  if dest not in mapping:result.append(row);continue
  q=mapping[dest];raw=checked_read(root,q['source_path'])
  expected=dict(destination=dest,source_path=q['source_path'],sha256=sha(raw),bytes=len(raw),git_blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),group='newshf-optin',revision=c.REVISION)
  assert row==expected and dest not in seen,('turret runtime row drift',dest);seen.add(dest)
 assert seen==set(mapping),'missing turret runtime row'
 return result

def drop_additions(inventory,root=ROOT):
 from large_newshi_projection import drop_additions as newer_drop
 proof=verified(root);result=newer_drop(inventory,root)
 for n,h in proof['added_sources'].items():assert result.pop(n)==h,('turret source addition drift',n)
 return result
