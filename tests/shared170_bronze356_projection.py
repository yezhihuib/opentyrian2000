"""One exact shared170 + opaque bronze356 extension over qualified private35de.

Both independently editable producer closures are proved once by this local
node. No older proof is called here; each old oracle sees exact35de preimages.
"""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
PRIVATE_BASE='35de2e1d009fa6cfe4cc512dfdc2261bd6fa28f1'
LEDGER='tests/current_shared170_bronze356_source_projection.json'
LEDGER_SHA256='fb6bc1599f626404289ada38538f937dcc4bbaad1835b954cbf6b2b8d10e4b40'
SRC_FILES={'src/global_newshf_mirror.inc','src/newshf_identity_validation.inc','src/shapesy_platform_mirror.inc'}
FILES=SRC_FILES|{'scripts/package_runtime.py','scripts/rebuild_recovered_runtime_manifest.py','scripts/shared_asset_special_sources.py','tests/aircraft169_newshf_projection.py','tests/test_aircraft169_newshf_projection.py','tests/test_interceptor166_newshf_projection.py','tests/test_fighter165_newshf_projection.py','tests/test_scout164_newshf_projection.py','tests/test_shapesy_cyan_secondary_projection.py','tests/test_shapesy_cyan_projection.py','tests/test_shapesy_platform_projection.py','tests/accepted_later_changes.py','tests/shop_current_acceptance.py','tests/_projection_proof_context.py'}
ADDED={'src/newshf_aircraft170_pins.h','src/current_aircraft170_newshf_hd_assets.h','src/current_shapesy_bronze356_hd_assets.h','src/current_shapesy_bronze356_source.h'}
sha=lambda raw:hashlib.sha256(raw).hexdigest()
def ledger():
 raw=(ROOT/LEDGER).read_bytes();assert sha(raw)==LEDGER_SHA256,'combined170/356 ledger is not frozen'
 spec=json.loads(raw);assert spec['private_base']==PRIVATE_BASE
 assert set(spec['files'])==FILES and set(spec['added_sources'])==ADDED
 return spec

def inverse(name,raw,pin):
 assert sha(raw)==pin['current_sha256'],('unapproved combined170/356 current bytes',name)
 lines=raw.splitlines(keepends=True)
 for h in reversed(pin['hunks']):
  a,b=h['after_lines'];assert b''.join(lines[a:b])==h['after'].encode(),('combined170/356 hunk drift',name)
  lines[a:b]=h['before'].encode().splitlines(keepends=True)
 result=b''.join(lines);assert sha(result)==pin['previous_sha256'],('combined170/356 preimage drift',name)
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
 assert p.is_file() and not p.is_symlink() and not any(q.is_symlink() for q in p.parents),('unsafe combined170/356 input',name)
 return p.read_bytes()

def qualified_paths(root=ROOT):
 spec=ledger();return set(spec['qualified'])|FILES|{LEDGER,'tests/shared170_bronze356_projection.py'}

def verified(root=ROOT):
 spec=ledger()
 for name,h in spec['qualified'].items():assert sha(checked_read(root,name))==h,('unqualified combined170/356 input',name)
 for name,pin in spec['files'].items():inverse(name,checked_read(root,name),pin)
 scripts=str(ROOT/'scripts')
 if scripts not in sys.path:sys.path.insert(0,scripts)
 import current_aircraft170_newshf_compatibility as aircraft
 import current_shapesy_bronze356_compatibility as bronze
 from verify_current_production import source_inventory
 expected=dict(spec['base_source_inventory']);expected.update(spec['added_sources'])
 expected.update({n:spec['files'][n]['current_sha256'] for n in SRC_FILES})
 assert source_inventory(root)==expected,'combined170/356 whole source directory drift'
 # Each producer is actually derived once; no stored mapping replaces a load.
 aircraft_mapping=aircraft.load(root);bronze_mapping=bronze.load(root)
 assert len(aircraft_mapping)==3 and {r['identity'] for r in aircraft_mapping.values()}==set(aircraft.IDS)
 assert len(bronze_mapping)==1 and {r['identity'] for r in bronze_mapping.values()}=={2020356}
 assert not set(aircraft_mapping)&set(bronze_mapping),'combined170/356 destination collision'
 mapping=dict(aircraft_mapping,**bronze_mapping)
 required=set(ADDED);asset_names=set()
 for c in (aircraft,bronze):
  required|=c.input_paths(root)|c.generated_paths()|{c.HEADER,c.MAPPING}|{c.ROOT+'/'+c.name(i) for i in c.IDS}
  asset_names|={c.SELECTION}|{c.ROOT+'/'+c.name(i) for i in c.IDS}
  for top in (c.INPUT_ROOT,c.ROOT):
   actual={p.relative_to(root).as_posix() for p in (root/top).rglob('*') if p.is_file() or p.is_symlink()}
   assert actual=={n for n in spec['qualified'] if n.startswith(top+'/')},('combined170/356 input directory closure drift',top)
 assert required<=set(spec['qualified'])
 assert {n:spec['qualified'][n] for n in ADDED}==spec['added_sources']
 assets={n:{'sha256':h,'mode':'100644'} for n,h in spec['qualified'].items() if n.startswith('assets/')}
 assert set(assets)==asset_names,'combined170/356 asset scope drift'
 runtime_meta={d:('newshf-optin',aircraft.REVISION) for d in aircraft_mapping}
 runtime_meta.update({d:('gameplay',bronze.REVISION) for d in bronze_mapping})
 return dict(mapping=mapping,runtime_meta=runtime_meta,added_sources=spec['added_sources'],assets=assets,paths=qualified_paths(root))

def before_inventory(inventory,root=ROOT):
 from verify_current_production import source_inventory
 proof=verified(root);result=dict(inventory)
 assert result==source_inventory(root),'combined170/356 passed source inventory drift'
 for n,h in proof['added_sources'].items():assert result.pop(n)==h,('combined170/356 source addition drift',n)
 for n in SRC_FILES:
  raw=checked_read(root,n);assert result[n]==sha(raw),('combined170/356 live source inventory drift',n)
  result[n]=sha(project_source(n,raw))
 return result

def before_runtime(rows,root=ROOT):
 proof=verified(root);mapping=proof['mapping'];result=[];seen=set()
 for row in rows:
  dest=row['destination']
  if dest not in mapping:result.append(row);continue
  q=mapping[dest];raw=checked_read(root,q['source_path']);group,revision=proof['runtime_meta'][dest]
  expected=dict(destination=dest,source_path=q['source_path'],sha256=sha(raw),bytes=len(raw),git_blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),group=group,revision=revision)
  assert row==expected and dest not in seen,('combined170/356 runtime row drift',dest);seen.add(dest)
 assert seen==set(mapping),'missing combined170/356 runtime row'
 return result

def drop_additions(inventory,root=ROOT):
 proof=verified(root);result=dict(inventory)
 for n,h in proof['added_sources'].items():assert result.pop(n)==h,('combined170/356 source addition drift',n)
 return result
