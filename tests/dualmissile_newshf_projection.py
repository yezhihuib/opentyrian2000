"""Exact dualmissile extension over qualified PRIVATE68d3571, not a public commit.

All new inputs are qualified and the one canonical master is rebuilt before
removing additions. Earlier immutable ledgers/preimages are never refreshed.
No Git history or original game data is required by this verifier.
"""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
PRIVATE_BASE='68d35712770281f72b0e55f96a764c5656bc8272'
LEDGER='tests/current_dualmissile_newshf_source_projection.json'
LEDGER_SHA256='6c9bbfc8f98c76ab9ed3b195e114133fe524a7f72fbb02883945ee5556bc043a'
FILES={'src/newshf_identity_validation.inc','src/global_newshf_mirror.inc','src/render_mirror.c','src/shapesy_platform_mirror.inc'}
ADDED={'src/newshf_dualmissile_pins.h','src/current_dualmissile_newshf_hd_assets.h'}
sha=lambda raw:hashlib.sha256(raw).hexdigest()
def ledger():
 raw=(ROOT/LEDGER).read_bytes();assert sha(raw)==LEDGER_SHA256,'dual ledger is not frozen'
 spec=json.loads(raw);assert spec['private_base']==PRIVATE_BASE
 assert set(spec['files'])==FILES and set(spec['added_sources'])==ADDED
 return spec

def inverse(name,raw,pin):
 assert sha(raw)==pin['current_sha256'],('unapproved dual current bytes',name)
 lines=raw.splitlines(keepends=True)
 for h in reversed(pin['hunks']):
  a,b=h['after_lines'];assert b''.join(lines[a:b])==h['after'].encode(),('dual hunk drift',name)
  lines[a:b]=h['before'].encode().splitlines(keepends=True)
 result=b''.join(lines);assert sha(result)==pin['previous_sha256'],('dual preimage drift',name)
 return result

def project_source(name,raw):
 pin=ledger()['files'].get(name)
 if pin is None:return raw
 if sha(raw)==pin['current_sha256']:return inverse(name,raw,pin)
 from shapesy_cyan_projection import project_if_current as cyan_project
 raw=cyan_project(name,raw)
 from turret_newshf_projection import project_if_current as turret_project
 return inverse(name,turret_project(name,raw),pin)

def project_if_current(name,raw):
 """Compose with an earlier inverse accepting either exact chain position.

Live-file qualification occurs in verified(), before older proofs hide paths.
This is not a fallback accepting arbitrary prior or mutated live input.
"""
 pin=ledger()['files'].get(name)
 if pin is None:return raw
 if sha(raw)==pin['previous_sha256']:return raw
 if sha(raw)==pin['current_sha256']:return inverse(name,raw,pin)
 from shapesy_cyan_projection import project_if_current as cyan_project
 raw=cyan_project(name,raw)
 from turret_newshf_projection import project_if_current as turret_project
 return inverse(name,turret_project(name,raw),pin)

def checked_read(root,name):
 p=root/name
 assert p.is_file() and not p.is_symlink() and not any(q.is_symlink() for q in p.parents),('unsafe dual input',name)
 from turret_newshf_projection import project_if_current as turret_project
 from shapesy_cyan_projection import project_if_current as cyan_project
 return turret_project(name,cyan_project(name,p.read_bytes()))

def qualified_paths(root=ROOT):
 spec=ledger();return set(spec['qualified'])|FILES|{LEDGER,'tests/dualmissile_newshf_projection.py'}

def verified(root=ROOT):
 from turret_newshf_projection import verified as turret_verified
 turret_verified(root)
 spec=ledger()
 for name,h in spec['qualified'].items():assert sha(checked_read(root,name))==h,('unqualified dual input',name)
 for name,pin in spec['files'].items():inverse(name,checked_read(root,name),pin)
 scripts=str(ROOT/'scripts')
 if scripts not in sys.path:sys.path.insert(0,scripts)
 import current_dualmissile_newshf_compatibility as c
 mapping=c.load(root)
 assert len(mapping)==1 and set(r['identity'] for r in mapping.values())=={2100015}
 assert all(r['records']==[2,500] and r['base']==169 for r in mapping.values())
 required=c.input_paths(root)|c.generated_paths()|{c.HEADER,c.MAPPING,c.ROOT+'/'+c.name(2100015)}|ADDED|FILES
 assert required<=set(spec['qualified'])|FILES
 assert {n:spec['qualified'][n] for n in ADDED}==spec['added_sources']
 for top in ('authoring-inputs/newshf-dualmissile','assets/hd/current-compat/newshf-dualmissile'):
  actual={p.relative_to(root).as_posix() for p in (root/top).rglob('*') if p.is_file() or p.is_symlink()}
  assert actual=={n for n in spec['qualified'] if n.startswith(top+'/')},('dual input directory closure drift',top)
 assets={n:{'sha256':h,'mode':'100644'} for n,h in spec['qualified'].items() if n.startswith('assets/')}
 assert set(assets)=={c.SELECTION,c.ROOT+'/'+c.name(2100015)},'dual asset scope drift'
 return dict(mapping=mapping,added_sources=spec['added_sources'],assets=assets,paths=qualified_paths(root))

def before_inventory(inventory,root=ROOT):
 from turret_newshf_projection import before_inventory as turret_before
 proof=verified(root);result=turret_before(inventory,root)
 for n,h in proof['added_sources'].items():assert result.pop(n)==h,('dual source addition drift',n)
 for n in FILES:
  raw=checked_read(root,n);assert result[n]==sha(raw),('dual live source inventory drift',n)
  result[n]=sha(project_source(n,raw))
 return result

def before_runtime(rows,root=ROOT):
 from turret_newshf_projection import before_runtime as turret_before
 rows=turret_before(rows,root)
 proof=verified(root);mapping=proof['mapping'];result=[];seen=set()
 import current_dualmissile_newshf_compatibility as c
 for row in rows:
  dest=row['destination']
  if dest not in mapping:result.append(row);continue
  q=mapping[dest];raw=checked_read(root,q['source_path'])
  expected=dict(destination=dest,source_path=q['source_path'],sha256=sha(raw),bytes=len(raw),git_blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),group='newshf-optin',revision=c.REVISION)
  assert row==expected and dest not in seen,('dual runtime row drift',dest)
  seen.add(dest)
 assert seen==set(mapping),'missing dual runtime row'
 return result


def drop_additions(inventory,root=ROOT):
 from turret_newshf_projection import drop_additions as turret_drop
 proof=verified(root);result=turret_drop(inventory,root)
 for n,h in proof['added_sources'].items():assert result.pop(n)==h,('dual source addition drift',n)
 return result
