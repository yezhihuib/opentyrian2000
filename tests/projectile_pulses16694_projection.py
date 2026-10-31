"""Exact pulses16694 extension over qualified statics; old ledgers stay fixed."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
PRIVATE_BASE='1836d49e46b5ec13f2761ca6c15d6ab5cac28bf8'
LEDGER='tests/current_projectile_pulses16694_source_projection.json'
LEDGER_SHA256='3cd854b1bd9f2fce600a2ec849939a25fcfc09c236c4b9a104784b81d3d75564'
SRC_FILES={'src/entity_draw.c','src/global_projectile91_mirror.inc','src/render_mirror.c','src/tyrian2.c'}
FILES=SRC_FILES|{'packaging/runtime-assets-v1.json','scripts/package_runtime.py','scripts/rebuild_recovered_runtime_manifest.py','tests/_projection_proof_context.py','tests/accepted_later_changes.py','tests/projectile_statics_projection.py','tests/shop_current_acceptance.py','tests/test_aircraft169_newshf_projection.py','tests/test_fighter165_newshf_projection.py','tests/test_interceptor166_newshf_projection.py','tests/test_projectile145_projection.py','tests/test_projectile61_projection.py','tests/test_projectile_blue_triplet_projection.py','tests/test_projectile_gold_pulse_projection.py','tests/test_projectile_statics_projection.py','tests/test_projectile_statics_runtime_contract.py','tests/test_scout164_newshf_projection.py','tests/test_shapesy_cyan_projection.py','tests/test_shapesy_cyan_secondary_projection.py','tests/test_shapesy_platform_projection.py','tests/test_shared170_bronze356_projection.py'}
ADDED={'src/current_projectile_pulses16694_payload_pins.h','src/enemy_pulses16694_mirror.inc'}
sha=lambda raw:hashlib.sha256(raw).hexdigest()
def ledger():
 raw=(ROOT/LEDGER).read_bytes();assert sha(raw)==LEDGER_SHA256,'projectile_pulses16694 ledger is not frozen'
 spec=json.loads(raw);assert spec['private_base']==PRIVATE_BASE
 assert set(spec['files'])==FILES and set(spec['added_sources'])==ADDED
 return spec

def inverse(name,raw,pin):
 assert sha(raw)==pin['current_sha256'],('unapproved projectile_pulses16694 current bytes',name)
 lines=raw.splitlines(keepends=True)
 for h in reversed(pin['hunks']):
  a,b=h['after_lines'];assert b''.join(lines[a:b])==h['after'].encode(),('projectile_pulses16694 hunk drift',name)
  lines[a:b]=h['before'].encode().splitlines(keepends=True)
 result=b''.join(lines);assert sha(result)==pin['previous_sha256'],('projectile_pulses16694 preimage drift',name)
 return result

def project_source(name,raw):
 if name not in FILES:return raw
 return inverse(name,raw,ledger()['files'][name])

def project_if_current(name,raw):
 if name not in FILES:return raw
 pin=ledger()['files'][name]
 if sha(raw)==pin['previous_sha256']:return raw
 return inverse(name,raw,pin)

def checked_read(root,name):
 p=root/name
 assert p.is_file() and not p.is_symlink() and not any(q.is_symlink() for q in p.parents),('unsafe projectile_pulses16694 input',name)
 return p.read_bytes()

def qualified_paths(root=ROOT):
 spec=ledger();return set(spec['qualified'])|FILES|{LEDGER,'tests/projectile_pulses16694_projection.py'}

def verified(root=ROOT):
 spec=ledger()
 for name,h in spec['qualified'].items():assert sha(checked_read(root,name))==h,('unqualified projectile_pulses16694 input',name)
 for name,pin in spec['files'].items():inverse(name,checked_read(root,name),pin)
 scripts=str(ROOT/'scripts')
 if scripts not in sys.path:sys.path.insert(0,scripts)
 import current_projectile_pulses16694_compatibility as c
 from verify_current_production import source_inventory
 expected=dict(spec['base_source_inventory']);expected.update(spec['added_sources'])
 expected.update({n:spec['files'][n]['current_sha256'] for n in SRC_FILES})
 assert source_inventory(root)==expected,'projectile_pulses16694 whole source directory drift'
 mapping=c.load(root)
 assert len(mapping)==2 and {r['identity'] for r in mapping.values()}=={1550166,1550094}
 assert {r['density'] for r in mapping.values()}=={8}
 required=c.input_paths(root)|{c.HEADER,c.MAPPING}|{c.ROOT+'/'+c.name(i) for i in c.IDS}|ADDED
 assert required<=set(spec['qualified'])
 assert {n:spec['qualified'][n] for n in ADDED}==spec['added_sources']
 for top in (c.INPUT_ROOT,c.ROOT):
  actual={p.relative_to(root).as_posix() for p in (root/top).rglob('*') if p.is_file() or p.is_symlink()}
  assert actual=={n for n in spec['qualified'] if n.startswith(top+'/')},('projectile_pulses16694 input directory closure drift',top)
 assets={n:{'sha256':h,'mode':'100644'} for n,h in spec['qualified'].items() if n.startswith('assets/')}
 assert set(assets)=={c.SELECTION}|{c.png(i) for i in c.IDS}|{c.ROOT+'/'+c.name(i) for i in c.IDS},'projectile_pulses16694 asset scope drift'
 return dict(mapping=mapping,added_sources=spec['added_sources'],assets=assets,paths=qualified_paths(root))

def before_inventory(inventory,root=ROOT):
 from verify_current_production import source_inventory
 proof=verified(root);result=dict(inventory)
 assert result==source_inventory(root),'projectile_pulses16694 passed source inventory drift'
 for n,h in proof['added_sources'].items():assert result.pop(n)==h,('projectile_pulses16694 source addition drift',n)
 for n in SRC_FILES:
  raw=checked_read(root,n);assert result[n]==sha(raw),('projectile_pulses16694 live source inventory drift',n)
  result[n]=sha(project_source(n,raw))
 return result

def before_runtime(rows,root=ROOT):
 proof=verified(root);mapping=proof['mapping'];result=[];seen=set()
 import current_projectile_pulses16694_compatibility as c
 for row in rows:
  dest=row['destination']
  if dest not in mapping:result.append(row);continue
  q=mapping[dest];raw=checked_read(root,q['source_path'])
  expected=dict(destination=dest,source_path=q['source_path'],sha256=sha(raw),bytes=len(raw),git_blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),group='gameplay',revision=c.REVISION)
  assert row==expected and dest not in seen,('projectile_pulses16694 runtime row drift',dest);seen.add(dest)
 assert seen==set(mapping),'missing projectile_pulses16694 runtime row'
 return result

def drop_additions(inventory,root=ROOT):
 proof=verified(root);result=dict(inventory)
 for n,h in proof['added_sources'].items():assert result.pop(n)==h,('projectile_pulses16694 source addition drift',n)
 return result
