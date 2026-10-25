"""Fail-closed inverses of named, reviewed later changes.

The original feature oracle and its old digests are not rebased. Each inverse
first verifies the entire accepted current blob, then every finite hunk, then
the old blob. The two generated payload headers and thirty-one fixed current asset outputs
require a fresh exact current-generation proof before their finite projection.
A third generated header and exactly nine Front Multi outputs are separately
derived; its two-hunk inverse precedes Plasma. All historical ledgers stay fixed.
The local default-off NEWSHF compositor adds a separate newest exact inverse,
one fixed executable module and nine independently derived HDR1 resources.
This is a local binding proof, not publication or gameplay acceptance.
All other source bytes and the historical asset inventory remain fixed.
The reviewed render-boundary correction has its own exact two-file inverse;
current source bindings keep its real bytes, while older oracles see their
original source through that explicit projection. The later five-file Charge
inverse is applied exactly once before that correction. Its ten current asset
paths have an independent master/recipe derivation proof, not a rebased P9 ledger.
The five Mint/Front current paths have a separate four-source pixel proof; their
existing historical transports and three independent Mint phases stay frozen.
Plasma projectile adds one fixed generated header and seven derived asset paths,
with a two-hunk exact source inverse before Charge; all old fixtures stay frozen.
Guided adds four independent current masters and a two-source P04-only payload
inverse before Sonic. Exactly four existing runtime rows project back to their
frozen transports; Sonic's exact quartet and every old destination remain.
"""
from pathlib import Path
import copy, hashlib, json, os, subprocess, sys
ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT/'tests/fixtures/accepted-later-changes-v1'
PINS = {
 'normal-observer-surface-source.json': '40aed98872b92637089127134e24d81946bcd53d5298f17a894addcb8233da0f',
 'enemy-controlled-probe-source.json': 'd28e5a9d59bc471337b5fd7175b4ea87c8932d19d5503b9300b0733ebd543da2',
 'enemy-reuse-observe-source.json': 'e8fdb1d7c8e2a38f13e6cdebc3cf226b0de87758e16488c946de2c21fc9f7538',
 'enemy-proof-dedup-source.json': '91639f4b2aab64ebf1b7c40e76ccdc13e95460129af08507e8f6fe0f4caa5d9b',
 'enemy-protron-reuse-source.json': '5f82aa5edc9c9e3b1698f6480488e975101b392ffae0e741540e5c9cafccac6a',
 'enemy-green-reuse-source.json': '8c1c462965c780c0199132790a851f31575ef24f2966332bbc36c5936ceba2ba',
 'newshf168-soft-alpha-source.json': '668ce6cdff20bc65d649c3b283c9aef36f8dbcabe5efb520ad4e57a1fb301853',
 'enemy-reuse-source.json': '76e19c7b8bc2ec2fcf8644935c32306e38a334db9e8ddbc520841af0954fb6a0',
 'newshf-compositor-source.json': 'f423c5fa1f582c45027345124ace1d8efec049aeed23f7e92bfc5b6010f5754d',
 'newshf-identity-source.json': 'a402237cceeec01e05ca92249c1125e964bc1e8b984de95d81b523e134a5a787',
 'enemy-orb-source.json': '0a6f1105dd410c417dc56eff06aca9efcbca600419f22b53afc203c6dd645d05',
 'data-source.json': '3bfbfea80342efbf8ad53e38957260fcdf674db5a57c732f3702e502324cc011',
 'rear-p1-source.json': '2f8fed7183dcf1087b93cc7bceb79ac189ac0209835f8108c8aa0cdc0b931ff3',
 'storm-source.json': '188f57d604004af08ec191cc6bddf2b7d07ea65b1f60348073f7e0263f8783a1',
 'render-boundaries-source.json': '1bac028508e047cb862989d08ef7613b46652c6aea32c71d8bcbc6c78ff9ac30',
 'charge-body-source.json': 'c066932af771eb3a834c7becbeb59c6b0eac668d8da51df09d034d7247211e92',
 'front-multi-source.json': '6863a514933e5b97fea60de5a19e6a03381ee6617d2a76fe2425c65f5b6d023d',
 'plasma-projectile-source.json': '91f475377244bfe4c43f3281ba9399979556db6e037ab1db4d2e07194e96b2b0',
}
def sha(raw): return hashlib.sha256(raw).hexdigest()
def load(name):
 raw=(FIXTURES/name).read_bytes()
 assert sha(raw)==PINS[name], ('changed accepted-history ledger',name)
 return json.loads(raw)
def _project_source_once(label,name,raw):
 # A single finite inverse: whole input, every hunk, and whole result are pinned.
 pin=load(label+'-source.json')['files'].get(name)
 if pin is None:return raw
 assert sha(raw)==pin['current_sha256'],(label,name,'not the accepted published current blob')
 lines=raw.splitlines(keepends=True)
 for edit in reversed(pin['hunks']):
  a,b=edit['after_lines']
  assert b''.join(lines[a:b])==edit['after'].encode(),(name,'inverse hunk drift')
  lines[a:b]=edit['before'].encode().splitlines(keepends=True)
 restored=b''.join(lines)
 assert sha(restored)==pin['previous_sha256'],(name,'historical result drift')
 return restored

CURRENT_REAR_LOBES_LEDGER_SHA='54215d6f5abcf6290a1e8e817b3b9684a2bcbaab9286484fb571ad4d54aca2a4'
def current_rear_lobes_ledger():
 raw=(ROOT/'tests/current_rear_lobes_source_projection.json').read_bytes()
 assert sha(raw)==CURRENT_REAR_LOBES_LEDGER_SHA,'changed current REAR_LOBES inverse ledger'
 return json.loads(raw)

def verified_current_rear_lobes(root=ROOT):
 """Fresh eight-output proof including the composed P7/39/1/281/lobes shared header."""
 scripts=str(ROOT/'scripts')
 if scripts not in sys.path:sys.path.insert(0,scripts)
 import current_rear_lobes_compatibility as c
 mapping=c.load(root)
 assert current_rear_lobes_ledger()['files']=={},'Rear lobes has no C source inverse hunks'
 names=c.input_paths(root)|{c.MAPPING}
 assets={n:{'sha256':sha(c.read(root,n)),'mode':'100644'} for n in names if n.startswith('assets/')}
 assert len(assets)==9,'unapproved current REAR_LOBES asset scope'
 return dict(assets=assets,paths=names-{c.MAPPING},mapping=mapping,header_sha256=sha(c.read(root,c.HEADER)))

def before_current_rear_lobes_runtime(rows,root=ROOT):
 return _before_current_rear_lobes_runtime(rows,root,_proofs=None)

def _before_current_rear_lobes_runtime(rows,root=ROOT, *, _proofs):
 assert isinstance(rows,list) and len(rows)==1029,'unexpected REAR_LOBES runtime scope / destination scope'
 assert len({row['destination'] for row in rows})==1029,'duplicate REAR_LOBES runtime destination scope'
 proof=_current_projection_proof('rear_lobes',root,_proofs)
 old={r['destination']:r for r in current_rear_lobes_ledger()['runtime_before']}
 assert set(old)==set(proof['mapping']) and len(old)==8
 result=copy.deepcopy(rows);seen=set()
 for index,row in enumerate(result):
  destination=row['destination']
  if destination not in old:continue
  selected=proof['mapping'][destination];raw=(root/selected['source_path']).read_bytes()
  expected=dict(old[destination],source_path=selected['source_path'],sha256=sha(raw),bytes=len(raw),git_blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),revision='current-single-source-rear-lobes')
  assert row==expected,('unapproved current REAR_LOBES runtime row',destination)
  assert destination not in seen;seen.add(destination);result[index]=old[destination]
 assert seen==set(old),'missing current REAR_LOBES runtime row'
 return result

CURRENT_REAR281_LEDGER_SHA='6444f810f8bf54983e51042442a091bf3d44c01674b7054e590fb5eeefdb576b'
def current_rear281_ledger():
 raw=(ROOT/'tests/current_rear281_source_projection.json').read_bytes()
 assert sha(raw)==CURRENT_REAR281_LEDGER_SHA,'changed current REAR281 inverse ledger'
 return json.loads(raw)

def verified_current_rear281(root=ROOT):
 """Fresh twenty-output proof including the composed P7/39/1/281 shared header."""
 scripts=str(ROOT/'scripts')
 if scripts not in sys.path:sys.path.insert(0,scripts)
 import current_rear281_compatibility as c
 mapping=c.load(root)
 assert current_rear281_ledger()['files']=={},'Rear281 has no C source inverse hunks'
 names=c.input_paths(root)|{c.MAPPING}
 assets={n:{'sha256':sha(c.read(root,n)),'mode':'100644'} for n in names if n.startswith('assets/')}
 assert len(assets)==21,'unapproved current REAR281 asset scope'
 return dict(assets=assets,paths=names-{c.MAPPING},mapping=mapping,header_sha256=sha(c.read(root,c.HEADER)))

def before_current_rear281_runtime(rows,root=ROOT):
 return _before_current_rear281_runtime(rows,root,_proofs=None)

def _before_current_rear281_runtime(rows,root=ROOT, *, _proofs):
 rows=_before_current_rear_lobes_runtime(rows,root,_proofs=_proofs)
 assert isinstance(rows,list) and len(rows)==1029,'unexpected REAR281 runtime scope / destination scope'
 assert len({row['destination'] for row in rows})==1029,'duplicate REAR281 runtime destination scope'
 proof=_current_projection_proof('rear281',root,_proofs)
 old={r['destination']:r for r in current_rear281_ledger()['runtime_before']}
 assert set(old)==set(proof['mapping']) and len(old)==20
 result=copy.deepcopy(rows);seen=set()
 for index,row in enumerate(result):
  destination=row['destination']
  if destination not in old:continue
  selected=proof['mapping'][destination];raw=(root/selected['source_path']).read_bytes()
  expected=dict(old[destination],source_path=selected['source_path'],sha256=sha(raw),bytes=len(raw),git_blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),revision='current-single-source-rear281')
  assert row==expected,('unapproved current REAR281 runtime row',destination)
  assert destination not in seen;seen.add(destination);result[index]=old[destination]
 assert seen==set(old),'missing current REAR281 runtime row'
 return result

CURRENT_REAR1_LEDGER_SHA='213fd181fc91ba4fba344d4e1e7dd75ef9dc1b6e6512c17c34cbf853e18f2b63'
def current_rear1_ledger():
 raw=(ROOT/'tests/current_rear1_source_projection.json').read_bytes()
 assert sha(raw)==CURRENT_REAR1_LEDGER_SHA,'changed current REAR1 inverse ledger'
 return json.loads(raw)

def verified_current_rear1(root=ROOT):
 """Fresh eight-output proof including the composed P7/39/1 shared header."""
 scripts=str(ROOT/'scripts')
 if scripts not in sys.path:sys.path.insert(0,scripts)
 import current_rear1_compatibility as c
 mapping=c.load(root)
 assert current_rear1_ledger()['files']=={},'Rear1 has no C source inverse hunks'
 names=c.input_paths(root)|{c.MAPPING}
 assets={n:{'sha256':sha(c.read(root,n)),'mode':'100644'} for n in names if n.startswith('assets/')}
 assert len(assets)==9,'unapproved current REAR1 asset scope'
 return dict(assets=assets,paths=names-{c.MAPPING},mapping=mapping,header_sha256=sha(c.read(root,c.HEADER)))

def before_current_rear1_runtime(rows,root=ROOT):
 return _before_current_rear1_runtime(rows,root,_proofs=None)

def _before_current_rear1_runtime(rows,root=ROOT, *, _proofs):
 rows=_before_current_rear281_runtime(rows,root,_proofs=_proofs)
 assert isinstance(rows,list) and len(rows)==1029,'unexpected REAR1 runtime scope / destination scope'
 assert len({row['destination'] for row in rows})==1029,'duplicate REAR1 runtime destination scope'
 proof=_current_projection_proof('rear1',root,_proofs)
 old={r['destination']:r for r in current_rear1_ledger()['runtime_before']}
 assert set(old)==set(proof['mapping']) and len(old)==8
 result=copy.deepcopy(rows);seen=set()
 for index,row in enumerate(result):
  destination=row['destination']
  if destination not in old:continue
  selected=proof['mapping'][destination];raw=(root/selected['source_path']).read_bytes()
  expected=dict(old[destination],source_path=selected['source_path'],sha256=sha(raw),bytes=len(raw),git_blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),revision='current-single-source-rear1')
  assert row==expected,('unapproved current REAR1 runtime row',destination)
  assert destination not in seen;seen.add(destination);result[index]=old[destination]
 assert seen==set(old),'missing current REAR1 runtime row'
 return result

CURRENT_REAR39_LEDGER_SHA='ecdcaa893a6df956cb1a5f287f8e39119597262ee2dbc4239faaee27c7a87806'
def current_rear39_ledger():
 raw=(ROOT/'tests/current_rear39_source_projection.json').read_bytes()
 assert sha(raw)==CURRENT_REAR39_LEDGER_SHA,'changed current REAR39 inverse ledger'
 return json.loads(raw)

def verified_current_rear39(root=ROOT):
 """Fresh six-output proof including the composed P7/39/1 shared header."""
 scripts=str(ROOT/'scripts')
 if scripts not in sys.path:sys.path.insert(0,scripts)
 import current_rear39_compatibility as c
 mapping=c.load(root)
 assert current_rear39_ledger()['files']=={},'Rear39 has no C source inverse hunks'
 names=c.input_paths(root)|{c.MAPPING}
 assets={n:{'sha256':sha(c.read(root,n)),'mode':'100644'} for n in names if n.startswith('assets/')}
 assert len(assets)==7,'unapproved current REAR39 asset scope'
 return dict(assets=assets,paths=names-{c.MAPPING},mapping=mapping,header_sha256=sha(c.read(root,c.HEADER)))

def rear39_runtime_input_paths(root=ROOT):
 import current_rear39_compatibility as c
 import current_rear_p7_compatibility as p7
 import current_rear1_compatibility as rear1
 import current_rear281_compatibility as rear281
 import current_rear_lobes_compatibility as rear_lobes
 return c.input_paths(root)|{c.MAPPING,c.HEADER}|p7.input_paths(root)|{p7.MAPPING}|rear1.input_paths(root)|{rear1.MAPPING}|rear281.input_paths(root)|{rear281.MAPPING}|rear_lobes.input_paths(root)|{rear_lobes.MAPPING}|set(current_rear_p7_ledger()['files'])

def before_current_rear39_runtime(rows,root=ROOT):
 return _before_current_rear39_runtime(rows,root,_proofs=None)

def _before_current_rear39_runtime(rows,root=ROOT, *, _proofs):
 rows=_before_current_rear1_runtime(rows,root,_proofs=_proofs)
 assert isinstance(rows,list) and len(rows)==1029,'unexpected REAR39 runtime scope / destination scope'
 assert len({row['destination'] for row in rows})==1029,'duplicate REAR39 runtime destination scope'
 proof=_current_projection_proof('rear39',root,_proofs)
 old={r['destination']:r for r in current_rear39_ledger()['runtime_before']}
 assert set(old)==set(proof['mapping']) and len(old)==6
 result=copy.deepcopy(rows);seen=set()
 for index,row in enumerate(result):
  destination=row['destination']
  if destination not in old:continue
  selected=proof['mapping'][destination];raw=(root/selected['source_path']).read_bytes()
  expected=dict(old[destination],source_path=selected['source_path'],sha256=sha(raw),bytes=len(raw),git_blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),revision='current-single-source-rear39')
  assert row==expected,('unapproved current REAR39 runtime row',destination)
  assert destination not in seen;seen.add(destination);result[index]=old[destination]
 assert seen==set(old),'missing current REAR39 runtime row'
 return result

CURRENT_REAR_P7_HEADER='src/current_rear_multi_payload_pins.h'
CURRENT_REAR_P7_LEDGER_SHA='e2f7e4866031c1facede68da9fef24dadaf9faf1b0d783a8b0b9ba31c59b29f1'
def current_rear_p7_ledger():
 raw=(ROOT/'tests/current_rear_p7_source_projection.json').read_bytes()
 assert sha(raw)==CURRENT_REAR_P7_LEDGER_SHA,'changed current REAR_P7 inverse ledger'
 return json.loads(raw)

def project_current_rear_p7_source(name,raw):
 pin=current_rear_p7_ledger()['files'].get(name)
 if pin is None:return raw
 assert sha(raw)==pin['current_sha256'],('unapproved current REAR_P7 compositor module',name)
 lines=raw.splitlines(keepends=True)
 for edit in reversed(pin['hunks']):
  a,b=edit['after_lines']
  assert b''.join(lines[a:b])==edit['after'].encode(),('current REAR_P7 hunk drift',name)
  lines[a:b]=edit['before'].encode().splitlines(keepends=True)
 result=b''.join(lines)
 assert sha(result)==pin['previous_sha256'],('current REAR_P7 inverse drift',name)
 return result

def verified_current_rear_p7(root=ROOT):
 """Four independently derived Rear P7 transports; old source/slot/eligibility remain fixed."""
 scripts=str(ROOT/'scripts')
 if scripts not in sys.path:sys.path.insert(0,scripts)
 import current_rear_p7_compatibility as c
 for name in current_rear_p7_ledger()['files']:
  project_current_rear_p7_source(name,c.read(root,name))
 mapping=c.load(root)
 selected=c.selection(root,c.read(root,c.SELECTION))
 names={c.SELECTION,c.MAPPING,selected['recipe']['path']}|c.generated_paths()|{v['source_path'] for v in mapping.values()}
 names|={row['source_svg'] for row in selected['masters']}
 assets={n:{'sha256':sha(c.read(root,n)),'mode':'100644'} for n in names if n.startswith('assets/')}
 assert len(assets)==5,'unapproved current REAR_P7 asset scope'
 return dict(assets=assets,paths=names-{c.MAPPING},mapping=mapping,header_sha256=sha(c.read(root,c.HEADER)))

def before_current_rear_p7_inventory(inventory,root=ROOT):
 return _before_current_rear_p7_inventory(inventory,root,_proofs=None)

def _before_current_rear_p7_inventory(inventory,root=ROOT, *, _proofs):
 result=dict(inventory)
 assert result.pop(CURRENT_REAR_P7_HEADER)==_current_projection_proof('rear_p7',root,_proofs)['header_sha256']
 for name in current_rear_p7_ledger()['files']:
  raw=(root/name).read_bytes()
  assert result.get(name)==sha(raw),('unapproved current REAR_P7 inventory',name)
  result[name]=sha(project_current_rear_p7_source(name,raw))
 return result

def rear_p7_runtime_input_paths(root=ROOT):
 scripts=str(ROOT/'scripts')
 if scripts not in sys.path:sys.path.insert(0,scripts)
 import current_rear_p7_compatibility as c
 return rear39_runtime_input_paths(root)

def before_current_rear_p7_runtime(rows,root=ROOT):
 return _before_current_rear_p7_runtime(rows,root,_proofs=None)

def _before_current_rear_p7_runtime(rows,root=ROOT, *, _proofs):
 rows=_before_current_rear39_runtime(rows,root,_proofs=_proofs)
 assert isinstance(rows,list) and len(rows)==1029,'unexpected REAR_P7 runtime scope / destination scope'
 assert len({row['destination'] for row in rows})==1029,'duplicate REAR_P7 runtime destination scope'
 proof=_current_projection_proof('rear_p7',root,_proofs)
 old={r['destination']:r for r in current_rear_p7_ledger()['runtime_before']}
 assert set(old)==set(proof['mapping']) and len(old)==4
 result=copy.deepcopy(rows);seen=set()
 for index,row in enumerate(result):
  destination=row['destination']
  if destination not in old:continue
  selected=proof['mapping'][destination];raw=(root/selected['source_path']).read_bytes()
  expected=dict(old[destination],source_path=selected['source_path'],sha256=sha(raw),bytes=len(raw),git_blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),revision='current-single-source-rear-p7')
  assert row==expected,('unapproved current REAR_P7 runtime row',destination)
  assert destination not in seen;seen.add(destination);result[index]=old[destination]
 assert seen==set(old),'missing current REAR_P7 runtime row'
 return result

CURRENT_MISSILE_HEADER='src/current_missile_payload_pins.h'
CURRENT_MISSILE_LEDGER_SHA='a038d826417fd853fe2588a5f131312e50b3fd58422ce83968f39ddec28ec81f'
def current_missile_ledger():
 raw=(ROOT/'tests/current_missile_source_projection.json').read_bytes()
 assert sha(raw)==CURRENT_MISSILE_LEDGER_SHA,'changed current MISSILE inverse ledger'
 return json.loads(raw)

def project_current_missile_source(name,raw):
 raw=project_current_rear_p7_source(name,raw)
 pin=current_missile_ledger()['files'].get(name)
 if pin is None:return raw
 assert sha(raw)==pin['current_sha256'],('unapproved current MISSILE compositor module',name)
 lines=raw.splitlines(keepends=True)
 for edit in reversed(pin['hunks']):
  a,b=edit['after_lines']
  assert b''.join(lines[a:b])==edit['after'].encode(),('current MISSILE hunk drift',name)
  lines[a:b]=edit['before'].encode().splitlines(keepends=True)
 result=b''.join(lines)
 assert sha(result)==pin['previous_sha256'],('current MISSILE inverse drift',name)
 return result

def verified_current_missile(root=ROOT):
 """Three independently derived regular Missile transports; old source/slot/eligibility remain fixed."""
 scripts=str(ROOT/'scripts')
 if scripts not in sys.path:sys.path.insert(0,scripts)
 import current_missile_compatibility as c
 for name in current_missile_ledger()['files']:
  project_current_missile_source(name,c.read(root,name))
 mapping=c.load(root)
 selected=c.selection(root,c.read(root,c.SELECTION))
 names={c.SELECTION,c.MAPPING,selected['recipe']['path']}|c.generated_paths()|{v['source_path'] for v in mapping.values()}
 names|={row['source_png'] for row in selected['masters']}
 assets={n:{'sha256':sha(c.read(root,n)),'mode':'100644'} for n in names if n.startswith('assets/')}
 assert len(assets)==4,'unapproved current MISSILE asset scope'
 return dict(assets=assets,paths=names-{c.MAPPING},mapping=mapping,header_sha256=sha(c.read(root,c.HEADER)))

def before_current_missile_inventory(inventory,root=ROOT):
 return _before_current_missile_inventory(inventory,root,_proofs=None)

def _before_current_missile_inventory(inventory,root=ROOT, *, _proofs):
 result=_before_current_rear_p7_inventory(inventory,root,_proofs=_proofs)
 assert result.pop(CURRENT_MISSILE_HEADER)==_current_projection_proof('missile',root,_proofs)['header_sha256']
 for name in current_missile_ledger()['files']:
  raw=(root/name).read_bytes()
  assert result.get(name)==sha(raw),('unapproved current MISSILE inventory',name)
  result[name]=sha(project_current_missile_source(name,raw))
 return result

def missile_runtime_input_paths(root=ROOT):
 scripts=str(ROOT/'scripts')
 if scripts not in sys.path:sys.path.insert(0,scripts)
 import current_missile_compatibility as c
 return c.input_paths(root)|{c.MAPPING,c.HEADER}|set(current_missile_ledger()['files'])|rear_p7_runtime_input_paths(root)

def before_current_missile_runtime(rows,root=ROOT):
 return _before_current_missile_runtime(rows,root,_proofs=None)

def _before_current_missile_runtime(rows,root=ROOT, *, _proofs):
 rows=_before_current_rear_p7_runtime(rows,root,_proofs=_proofs)
 assert isinstance(rows,list) and len(rows)==1029,'unexpected MISSILE runtime scope / destination scope'
 assert len({row['destination'] for row in rows})==1029,'duplicate MISSILE runtime destination scope'
 proof=_current_projection_proof('missile',root,_proofs)
 old={r['destination']:r for r in current_missile_ledger()['runtime_before']}
 assert set(old)==set(proof['mapping']) and len(old)==3
 result=copy.deepcopy(rows);seen=set()
 for index,row in enumerate(result):
  destination=row['destination']
  if destination not in old:continue
  selected=proof['mapping'][destination];raw=(root/selected['source_path']).read_bytes()
  expected=dict(old[destination],source_path=selected['source_path'],sha256=sha(raw),bytes=len(raw),git_blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),revision='current-single-source-missile')
  assert row==expected,('unapproved current MISSILE runtime row',destination)
  assert destination not in seen;seen.add(destination);result[index]=old[destination]
 assert seen==set(old),'missing current MISSILE runtime row'
 return result

CURRENT_MINT27_HEADER='src/current_mint27_payload_pins.h'
CURRENT_MINT27_LEDGER_SHA='91a57c01370bf49fb1818748a2621da91ba252b8576c667bf05a116689bc5fe9'
def current_mint27_ledger():
 raw=(ROOT/'tests/current_mint27_source_projection.json').read_bytes()
 assert sha(raw)==CURRENT_MINT27_LEDGER_SHA,'changed current MINT27 inverse ledger'
 return json.loads(raw)

def project_current_mint27_source(name,raw):
 raw=project_current_missile_source(name,raw)
 pin=current_mint27_ledger()['files'].get(name)
 if pin is None:return raw
 assert sha(raw)==pin['current_sha256'],('unapproved current MINT27 compositor module',name)
 lines=raw.splitlines(keepends=True)
 for edit in reversed(pin['hunks']):
  a,b=edit['after_lines']
  assert b''.join(lines[a:b])==edit['after'].encode(),('current MINT27 hunk drift',name)
  lines[a:b]=edit['before'].encode().splitlines(keepends=True)
 result=b''.join(lines)
 assert sha(result)==pin['previous_sha256'],('current MINT27 inverse drift',name)
 return result

def verified_current_mint27(root=ROOT):
 """One derived Mint27 transport; old source/slot/eligibility remain fixed."""
 scripts=str(ROOT/'scripts')
 if scripts not in sys.path:sys.path.insert(0,scripts)
 import current_mint27_compatibility as c
 for name in current_mint27_ledger()['files']:
  project_current_mint27_source(name,c.read(root,name))
 mapping=c.load(root)
 selected=c.selection(root,c.read(root,c.SELECTION))
 names={c.SELECTION,c.MAPPING,selected['recipe']['path']}|c.generated_paths()|{v['source_path'] for v in mapping.values()}
 names|={row['source_png'] for row in selected['masters']}
 assets={n:{'sha256':sha(c.read(root,n)),'mode':'100644'} for n in names if n.startswith('assets/')}
 assert len(assets)==2,'unapproved current MINT27 asset scope'
 return dict(assets=assets,paths=names-{c.MAPPING},mapping=mapping,header_sha256=sha(c.read(root,c.HEADER)))

def before_current_mint27_inventory(inventory,root=ROOT):
 return _before_current_mint27_inventory(inventory,root,_proofs=None)

def _before_current_mint27_inventory(inventory,root=ROOT, *, _proofs):
 result=_before_current_missile_inventory(inventory,root,_proofs=_proofs)
 assert result.pop(CURRENT_MINT27_HEADER)==_current_projection_proof('mint27',root,_proofs)['header_sha256']
 for name in current_mint27_ledger()['files']:
  raw=(root/name).read_bytes()
  assert result.get(name)==sha(project_current_missile_source(name,raw)),('unapproved current MINT27 inventory',name)
  result[name]=sha(project_current_mint27_source(name,raw))
 return result

def mint27_runtime_input_paths(root=ROOT):
 scripts=str(ROOT/'scripts')
 if scripts not in sys.path:sys.path.insert(0,scripts)
 import current_mint27_compatibility as c
 return c.input_paths(root)|{c.MAPPING,c.HEADER}|set(current_mint27_ledger()['files'])|missile_runtime_input_paths(root)

def before_current_mint27_runtime(rows,root=ROOT):
 return _before_current_mint27_runtime(rows,root,_proofs=None)

def _before_current_mint27_runtime(rows,root=ROOT, *, _proofs):
 rows=_before_current_missile_runtime(rows,root,_proofs=_proofs)
 assert isinstance(rows,list) and len(rows)==1029,'unexpected MINT27 runtime scope / destination scope'
 assert len({row['destination'] for row in rows})==1029,'duplicate MINT27 runtime destination scope'
 proof=_current_projection_proof('mint27',root,_proofs)
 old={r['destination']:r for r in current_mint27_ledger()['runtime_before']}
 assert set(old)==set(proof['mapping']) and len(old)==1
 result=copy.deepcopy(rows);seen=set()
 for index,row in enumerate(result):
  destination=row['destination']
  if destination not in old:continue
  selected=proof['mapping'][destination];raw=(root/selected['source_path']).read_bytes()
  expected=dict(old[destination],source_path=selected['source_path'],sha256=sha(raw),bytes=len(raw),git_blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),revision='current-single-source-mint27')
  assert row==expected,('unapproved current MINT27 runtime row',destination)
  assert destination not in seen;seen.add(destination);result[index]=old[destination]
 assert seen==set(old),'missing current MINT27 runtime row'
 return result

CURRENT_NEWSHF_HEADER='src/current_newshf_hd_assets.h'
CURRENT_NEWSHF_LEDGER_SHA='2ef518ee9adc0e6d1feff204b98325ad74bdf9cffaf5e5991c9dbf73c1bec83e'
def current_newshf_ledger():
 raw=(ROOT/'tests/current_newshf_source_projection.json').read_bytes()
 assert sha(raw)==CURRENT_NEWSHF_LEDGER_SHA,'changed current NEWSHF inverse ledger'
 return json.loads(raw)

def project_current_newshf_source(name,raw):
 raw=project_current_mint27_source(name,raw)
 pin=current_newshf_ledger()['files'].get(name)
 if pin is None:return raw
 assert sha(raw)==pin['current_sha256'],('unapproved current NEWSHF compositor module',name)
 lines=raw.splitlines(keepends=True)
 for edit in reversed(pin['hunks']):
  a,b=edit['after_lines']
  assert b''.join(lines[a:b])==edit['after'].encode(),('current NEWSHF hunk drift',name)
  lines[a:b]=edit['before'].encode().splitlines(keepends=True)
 result=b''.join(lines)
 assert sha(result)==pin['previous_sha256'],('current NEWSHF inverse drift',name)
 return result

def verified_current_newshf(root=ROOT):
 """Six master-derived poses; legacy nine and fixed 168 remain independently proven."""
 scripts=str(ROOT/'scripts')
 if scripts not in sys.path:sys.path.insert(0,scripts)
 import current_newshf_compatibility as c
 for name in current_newshf_ledger()['files']:
  project_current_newshf_source(name,c.read(root,name))
 mapping=c.load(root)
 selected=c.selection(root,c.read(root,c.SELECTION))
 names={c.SELECTION,c.MAPPING,selected['recipe']['path']}|c.generated_paths()|{c.ROOT+'/'+c.name(i) for i in c.EDIT_IDS}
 names|={row['source_png'] for row in selected['masters']}
 assets={n:{'sha256':sha(c.read(root,n)),'mode':'100644'} for n in names if n.startswith('assets/')}
 assert len(assets)==7,'unapproved current NEWSHF asset scope'
 return dict(assets=assets,paths=names-{c.MAPPING},mapping=mapping,header_sha256=sha(c.read(root,c.HEADER)))

def before_current_newshf_inventory(inventory,root=ROOT):
 return _before_current_newshf_inventory(inventory,root,_proofs=None)

def _before_current_newshf_inventory(inventory,root=ROOT, *, _proofs):
 result=_before_current_mint27_inventory(inventory,root,_proofs=_proofs)
 assert result.pop(CURRENT_NEWSHF_HEADER)==_current_projection_proof('newshf',root,_proofs)['header_sha256']
 for name in current_newshf_ledger()['files']:
  raw=(root/name).read_bytes()
  assert result.get(name)==sha(raw),('unapproved current NEWSHF inventory',name)
  result[name]=sha(project_current_newshf_source(name,raw))
 return result

def newshf_runtime_input_paths(root=ROOT):
 scripts=str(ROOT/'scripts')
 if scripts not in sys.path:sys.path.insert(0,scripts)
 import current_newshf_compatibility as c
 return c.input_paths(root)|{c.MAPPING,c.HEADER}|set(current_newshf_ledger()['files'])|mint27_runtime_input_paths(root)

def before_current_newshf_runtime(rows,root=ROOT):
 return _before_current_newshf_runtime(rows,root,_proofs=None)

def _before_current_newshf_runtime(rows,root=ROOT, *, _proofs):
 rows=_before_current_mint27_runtime(rows,root,_proofs=_proofs)
 assert isinstance(rows,list) and len(rows)==1029,'unexpected NEWSHF runtime scope / destination scope'
 assert len({row['destination'] for row in rows})==1029,'duplicate NEWSHF runtime destination scope'
 proof=_current_projection_proof('newshf',root,_proofs)
 old={r['destination']:r for r in current_newshf_ledger()['runtime_before']}
 assert set(old)==set(proof['mapping']) and len(old)==9
 result=copy.deepcopy(rows);seen=set()
 for index,row in enumerate(result):
  destination=row['destination']
  if destination not in old:continue
  selected=proof['mapping'][destination];raw=(root/selected['source_path']).read_bytes()
  expected=dict(old[destination],source_path=selected['source_path'],sha256=sha(raw),bytes=len(raw),git_blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest())
  assert row==expected,('unapproved current NEWSHF runtime row',destination)
  assert destination not in seen;seen.add(destination);result[index]=old[destination]
 assert seen==set(old),'missing current NEWSHF runtime row'
 return result

CURRENT_GUIDED_HEADER='src/current_guided_payload_pins.h'
CURRENT_GUIDED_LEDGER_SHA='9a9cd92b8c4ed133fea453a86a958280619a73a51ccf88371b7291d9e1ea108a'
def current_guided_ledger():
 raw=(ROOT/'tests/current_guided_source_projection.json').read_bytes()
 assert sha(raw)==CURRENT_GUIDED_LEDGER_SHA,'changed current Guided inverse ledger'
 return json.loads(raw)

def project_current_guided_source(name,raw):
 raw=project_current_newshf_source(name,raw)
 pin=current_guided_ledger()['files'].get(name)
 if pin is None:return raw
 assert sha(raw)==pin['current_sha256'],('unapproved current Guided source',name)
 lines=raw.splitlines(keepends=True)
 for edit in reversed(pin['hunks']):
  a,b=edit['after_lines']
  assert b''.join(lines[a:b])==edit['after'].encode(),('current Guided hunk drift',name)
  lines[a:b]=edit['before'].encode().splitlines(keepends=True)
 result=b''.join(lines)
 assert sha(result)==pin['previous_sha256'],('current Guided inverse drift',name)
 return result

def verified_current_guided(root=ROOT):
 """Four independent finite masters/four current outputs; no historical output exemption."""
 scripts=str(ROOT/'scripts')
 if scripts not in sys.path:sys.path.insert(0,scripts)
 import current_guided_compatibility as c
 # load already rederives every PNG/HDA and validates mapping and header.
 # Enumerating its finite paths must not regenerate all four masters again.
 # This selection guard is not a filesystem transaction: inputs must remain
 # static during a proof. Each invocation still reads and validates fresh bytes.
 selection_raw=c.read(root,c.SELECTION,128*1024)
 mapping=c.load(root)
 if c.read(root,c.SELECTION,128*1024)!=selection_raw:
  raise ValueError('Guided selection changed during current proof')
 selected=c.selection(root,selection_raw)
 names={c.SELECTION,c.MAPPING,selected['recipe']['path']}|c.generated_paths()|{v['source_path'] for v in mapping.values()}
 names|={row['source_png'] for row in selected['masters']}
 assets={n:{'sha256':sha(c.read(root,n)),'mode':'100644'} for n in names if n.startswith('assets/')}
 return dict(assets=assets,paths=names-{c.MAPPING},mapping=mapping,header_sha256=sha(c.read(root,c.HEADER)))

def before_current_guided_inventory(inventory,root=ROOT):
 result=before_current_newshf_inventory(inventory,root)
 assert result.pop(CURRENT_GUIDED_HEADER)==verified_current_guided(root)['header_sha256']
 for name in current_guided_ledger()['files']:
  raw=project_current_newshf_source(name,(root/name).read_bytes())
  assert result.get(name)==sha(raw),('unapproved current Guided inventory',name)
  result[name]=sha(project_current_guided_source(name,(root/name).read_bytes()))
 return result

def before_current_guided_runtime(rows,root=ROOT):
 return _before_current_guided_runtime(rows,root,_proofs=None)

def _before_current_guided_runtime(rows,root=ROOT, *, _proofs):
 """Replace exactly four current Guided rows after the finite aircraft projection."""
 rows=_before_current_newshf_runtime(rows,root,_proofs=_proofs)
 assert isinstance(rows,list) and len(rows)==1029,'unexpected Guided runtime scope / destination scope'
 destinations={row['destination'] for row in rows}
 assert len(destinations)==1029,'duplicate Guided runtime destination scope'
 historical=destinations-SONIC_RUNTIME_DESTINATIONS
 assert len(historical)==1025 and sha(('\n'.join(sorted(historical))+'\n').encode())==PRE_SONIC_RUNTIME_DESTINATIONS_SHA,'unapproved Guided runtime destination scope'
 proof=_current_projection_proof('guided',root,_proofs)
 old={r['destination']:r for r in current_guided_ledger()['runtime_before']}
 assert set(old)==set(proof['mapping']) and len(old)==4
 result=copy.deepcopy(rows);seen=set()
 for index,row in enumerate(result):
  destination=row['destination']
  if destination not in old:continue
  selected=proof['mapping'][destination];raw=(root/selected['source_path']).read_bytes()
  expected=dict(old[destination],source_path=selected['source_path'],sha256=sha(raw),bytes=len(raw),git_blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),revision='current-single-source-guided')
  assert row==expected,('unapproved current Guided runtime row',destination)
  assert destination not in seen;seen.add(destination);result[index]=old[destination]
 assert seen==set(old),'missing current Guided runtime row'
 return result

CURRENT_SONIC_HEADER='src/current_sonic_payload_pins.h'
CURRENT_SONIC_LEDGER_SHA='913fd3a46f2baa0c74f8ad1df75c9aaee74a9d9b188b9d12eaac31f7da610b71'
def current_sonic_ledger():
 raw=(ROOT/'tests/current_sonic_source_projection.json').read_bytes()
 assert sha(raw)==CURRENT_SONIC_LEDGER_SHA,'changed current Sonic inverse ledger'
 return json.loads(raw)

def project_current_sonic_source(name,raw):
 raw=project_current_guided_source(name,raw)
 pin=current_sonic_ledger()['files'].get(name)
 if pin is None:return raw
 assert sha(raw)==pin['current_sha256'],('unapproved current Sonic source',name)
 lines=raw.splitlines(keepends=True)
 for edit in reversed(pin['hunks']):
  a,b=edit['after_lines']
  assert b''.join(lines[a:b])==edit['after'].encode(),('current Sonic hunk drift',name)
  lines[a:b]=edit['before'].encode().splitlines(keepends=True)
 result=b''.join(lines)
 assert sha(result)==pin['previous_sha256'],('current Sonic inverse drift',name)
 return result

def verified_current_sonic(root=ROOT):
 """Two finite masters/four current outputs; no historical output exemption."""
 scripts=str(ROOT/'scripts')
 if scripts not in sys.path:sys.path.insert(0,scripts)
 import current_sonic_compatibility as c
 mapping=c.load(root)
 selected,pngs,blobs=c.generate(root,c.read(root,c.SELECTION))
 names={c.SELECTION,c.MAPPING,selected['recipe']['path']}|set(pngs)|{v['source_path'] for v in mapping.values()}
 names|={row['source_png'] for row in selected['masters']}
 assets={n:{'sha256':sha(c.read(root,n)),'mode':'100644'} for n in names if n.startswith('assets/')}
 return dict(assets=assets,paths=names-{c.MAPPING},mapping=mapping,header_sha256=sha(c.read(root,c.HEADER)))

SONIC_RUNTIME_DESTINATIONS = frozenset(
 'assets/gameplay/bullet-%d-8.hda'%i for i in (105,106,124,125))
# Public0135605's exact pre-extension destination set. Payloads remain current;
# this pin only prevents an unknown extra/replacement path from hiding in the
# old 1025 rows while another feature's narrow historical proof runs.
PRE_SONIC_RUNTIME_DESTINATIONS_SHA = '94b0488ae713e32cb306a6f3215762607b64da0813a3972f087187775ee2f84d'

def guided_runtime_input_paths(root=ROOT):
 scripts=str(ROOT/'scripts')
 if scripts not in sys.path:sys.path.insert(0,scripts)
 import current_guided_compatibility as c
 return c.input_paths(root)|{c.MAPPING,c.HEADER}

def sonic_runtime_input_paths(root=ROOT):
 scripts=str(ROOT/'scripts')
 if scripts not in sys.path:sys.path.insert(0,scripts)
 import current_sonic_compatibility as c
 return c.input_paths(root)|{c.MAPPING,c.HEADER}

def before_sonic_runtime(rows,root=ROOT):
 return _before_sonic_runtime(rows,root,_proofs=None)

def _before_sonic_runtime(rows,root=ROOT, *, _proofs):
 """Project only the exact derived quartet, not arbitrary package additions.

 This current-runtime entry point deliberately requires all 1029 rows. Passing
 an already-projected/old 1025-row selection is a missing-quartet error, not an
 implicit legacy mode. Historical comparison callers apply this once, first.
 """
 rows=_before_current_guided_runtime(rows,root,_proofs=_proofs)
 assert isinstance(rows,list) and len(rows)==1029,'unexpected runtime scope / destination scope for Sonic projection'
 by_destination={row['destination']:row for row in rows}
 assert len(by_destination)==len(rows),'duplicate runtime destination scope'
 scripts=str(ROOT/'scripts')
 if scripts not in sys.path:sys.path.insert(0,scripts)
 import current_sonic_compatibility as c
 assert c.IDS==(80105,80106,80124,80125) and c.ROOT=='assets/hd/current-compat/sonic','unapproved Sonic runtime family'
 mapping=c.load(root)
 assert set(mapping)==SONIC_RUNTIME_DESTINATIONS,'unapproved Sonic runtime mapping scope'
 for destination,selected in mapping.items():
  raw=c.read(root,selected['source_path'])
  expected=dict(source_path=selected['source_path'],destination=destination,
   group='gameplay',revision='current-single-source-sonic',bytes=len(raw),
   git_blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),sha256=sha(raw))
  assert by_destination.get(destination)==expected,('unapproved Sonic runtime row',destination)
 result=copy.deepcopy([row for row in rows if row['destination'] not in SONIC_RUNTIME_DESTINATIONS])
 assert len(result)==1025,'unexpected historical runtime scope after Sonic projection'
 destinations=('\n'.join(sorted(row['destination'] for row in result))+'\n').encode()
 assert sha(destinations)==PRE_SONIC_RUNTIME_DESTINATIONS_SHA,'unapproved historical runtime destination scope'
 return result

def before_current_sonic_inventory(inventory,root=ROOT):
 result=before_current_guided_inventory(inventory,root)
 assert result.pop(CURRENT_SONIC_HEADER)==verified_current_sonic(root)['header_sha256']
 for name in current_sonic_ledger()['files']:
  raw=project_current_guided_source(name,(root/name).read_bytes())
  assert result.get(name)==sha(raw),('unapproved current Sonic inventory',name)
  result[name]=sha(project_current_sonic_source(name,(root/name).read_bytes()))
 return result

CURRENT_PROTRON_HEADER='src/current_protron_payload_pins.h'
CURRENT_PROTRON_LEDGER_SHA='5dc523d31223971348edbb48f1a2883c235599db8401dece121a9f3aac14c0cd'
def current_protron_ledger():
 raw=(ROOT/'tests/current_protron_source_projection.json').read_bytes()
 assert sha(raw)==CURRENT_PROTRON_LEDGER_SHA,'changed current Protron inverse ledger'
 return json.loads(raw)

def project_normal_observer_source(name,raw):
 return _project_source_once('normal-observer-surface',name,project_current_sonic_source(name,raw))

def project_current_protron_source(name,raw):
 raw=project_normal_observer_source(name,raw)
 pin=current_protron_ledger()['files'].get(name)
 if pin is None:return raw
 assert sha(raw)==pin['current_sha256'],('unapproved current Protron source',name)
 lines=raw.splitlines(keepends=True)
 for edit in reversed(pin['hunks']):
  a,b=edit['after_lines']
  assert b''.join(lines[a:b])==edit['after'].encode(),('current Protron hunk drift',name)
  lines[a:b]=edit['before'].encode().splitlines(keepends=True)
 result=b''.join(lines)
 assert sha(result)==pin['previous_sha256'],('current Protron inverse drift',name)
 return result

def verified_current_protron(root=ROOT):
 """Separate current proof; never relax the frozen selected-B reproducer."""
 scripts=str(ROOT/'scripts')
 if scripts not in sys.path:sys.path.insert(0,scripts)
 import current_protron_compatibility as c
 mapping=c.load(root)
 selected,pngs,blobs=c.generate(root,c.read(root,c.SELECTION))
 names={c.SELECTION,c.MAPPING,selected['master']['source_png'],selected['recipe']['path']}|set(pngs)|{v['source_path'] for v in mapping.values()}
 assets={n:{'sha256':sha(c.read(root,n)),'mode':'100644'} for n in names if n.startswith('assets/')}
 return dict(assets=assets,paths=names-{c.MAPPING},mapping=mapping,header_sha256=sha(c.read(root,c.HEADER)))

def before_normal_observer_inventory(inventory,root=ROOT):
 """Exact reviewed three-source phase/session inverse; no generated authority."""
 result=before_current_sonic_inventory(inventory,root)
 for name,pin in load('normal-observer-surface-source.json')['files'].items():
  raw=project_current_sonic_source(name,(root/name).read_bytes())
  assert result.get(name)==sha(raw),('unapproved normal observer inventory',name)
  result[name]=sha(_project_source_once('normal-observer-surface',name,raw))
 return result

def before_current_protron_inventory(inventory,root=ROOT):
 result=before_normal_observer_inventory(inventory,root)
 assert result.pop(CURRENT_PROTRON_HEADER)==verified_current_protron(root)['header_sha256']
 for name,pin in current_protron_ledger()['files'].items():
  raw=(root/name).read_bytes()
  assert result[name]==sha(project_normal_observer_source(name,raw))
  result[name]=sha(project_current_protron_source(name,raw))
 return result

def before_current_protron_runtime(rows,root=ROOT):
 """Only the four verified current transports revert; all other rows survive."""
 proof=verified_current_protron(root);result=before_sonic_runtime(rows,root)
 old={r['destination']:r for r in current_protron_ledger()['runtime_before']}
 assert set(old)==set(proof['mapping'])
 seen=set()
 for index,row in enumerate(result):
  dest=row['destination']
  if dest not in old:continue
  selected=proof['mapping'][dest];raw=(root/selected['source_path']).read_bytes()
  expected=dict(old[dest],source_path=selected['source_path'],sha256=sha(raw),bytes=len(raw),git_blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest(),revision='current-single-source-protron-private-enemy-p09' if dest.endswith('enemy-protron-p09-227-8.hda') else 'current-single-source-protron')
  assert row==expected,('unapproved current Protron runtime row',dest)
  assert dest not in seen;seen.add(dest);result[index]=old[dest]
 assert seen==set(old)
 return result

def project_source(label,name,raw):
 # Newest first; generated payload values never relax executable source bytes.
 if label=='current-rear-p7':return project_current_rear_p7_source(name,raw)
 if label=='current-missile':return project_current_missile_source(name,raw)
 if label=='current-mint27':return project_current_mint27_source(name,raw)
 if label=='current-newshf':return project_current_newshf_source(name,raw)
 if label=='current-guided':return project_current_guided_source(name,raw)
 if label=='current-sonic':return project_current_sonic_source(name,raw)
 if label=='normal-observer-surface':return project_normal_observer_source(name,raw)
 raw=project_current_protron_source(name,raw)
 if label=='current-protron':return raw
 raw=_project_source_once('enemy-controlled-probe',name,raw)
 if label=='enemy-controlled-probe':return raw
 raw=_project_source_once('enemy-reuse-observe',name,raw)
 if label=='enemy-reuse-observe':return raw
 raw=_project_source_once('enemy-proof-dedup',name,raw)
 if label=='enemy-proof-dedup':return raw
 raw=_project_source_once('enemy-protron-reuse',name,raw)
 if label=='enemy-protron-reuse':return raw
 raw=_project_source_once('enemy-green-reuse',name,raw)
 if label=='enemy-green-reuse':return raw
 raw=_project_source_once('enemy-reuse',name,raw)
 if label=='enemy-reuse':return raw
 raw=_project_source_once('newshf-compositor',name,raw)
 if label=='newshf-compositor':return raw
 raw=_project_source_once('newshf-identity',name,raw)
 if label=='newshf-identity':return raw
 raw=_project_source_once('enemy-orb',name,raw)
 if label=='enemy-orb':return raw
 raw=_project_source_once('front-multi',name,raw)
 if label=='front-multi':return raw
 raw=_project_source_once('plasma-projectile',name,raw)
 if label=='plasma-projectile':return raw
 raw=_project_source_once('charge-body',name,raw)
 if label=='charge-body':return raw
 raw=_project_source_once('render-boundaries',name,raw)
 if label=='render-boundaries':return raw
 return _project_source_once(label,name,raw)

def corrected_source_paths():
 return sorted(set(current_rear_p7_ledger()['files'])|((set(load('enemy-controlled-probe-source.json')['files'])|set(load('enemy-reuse-observe-source.json')['files']))-set(load('enemy-reuse-source.json')['added_sources']))|set(load('enemy-reuse-source.json')['files'])|set(load('newshf-compositor-source.json')['files'])|set(load('newshf-identity-source.json')['files'])|set(load('enemy-orb-source.json')['files'])|set(load('front-multi-source.json')['files'])|set(load('plasma-projectile-source.json')['files'])|set(load('charge-body-source.json')['files'])|set(load('render-boundaries-source.json')['files']))


PROTRON_HEADER='src/current_enemy_protron_payload_pins.h'
def verified_protron_current(root=ROOT):
 """Finite derivative proof, immutable identity and independent selected pixels."""
 scripts=str(ROOT/'scripts')
 if scripts not in sys.path:sys.path.insert(0,scripts)
 import build_enemy_protron_p09 as p
 assert p.DIRECTORY=='assets/hd/enemy-protron-p09-v1' and p.HEADER==PROTRON_HEADER
 outputs=p.derive(root)
 for name,raw in outputs.items():assert p.read(root,name)==raw,('unverified P09 output',name)
 assets={name:{'sha256':sha(raw),'mode':'100644'} for name,raw in outputs.items() if name!=PROTRON_HEADER}
 for filename,expected in [('identity.json',p.IDENTITY),('recipe.json',p.RECIPE)]:
  name=p.DIRECTORY+'/'+filename;raw=p.read(root,name);assert json.loads(raw)==expected
  assets[name]={'sha256':sha(raw),'mode':'100644'}
 assert len(assets)==4
 return {'assets':assets,'header_sha256':sha(outputs[PROTRON_HEADER])}

def verified_enemy_probe_sources(root=ROOT):
 """Two exact controlled-probe modules; not a directory/hash exemption."""
 added=load('enemy-controlled-probe-source.json')['added_sources']
 assert set(added)=={'src/enemy_reuse_probe.h','src/enemy_reuse_probe.inc'}
 for name,digest in added.items():
  path=root/name
  assert not path.is_symlink() and path.is_file() and sha(path.read_bytes())==digest,('unapproved controlled probe module',name)
 return dict(added)

def before_controlled_probe_inventory(inventory,root=ROOT):
 """Project only the exact reviewed additions/deltas; retain all other pins."""
 result=before_current_protron_inventory(inventory,root)
 for name,digest in verified_enemy_probe_sources(root).items():
  assert result.get(name)==digest,('unapproved controlled probe inventory',name)
  result.pop(name)
 for name,pin in load('enemy-controlled-probe-source.json')['files'].items():
  raw=project_current_protron_source(name,(root/name).read_bytes())
  assert result.get(name)==sha(raw)==pin['current_sha256'],('unapproved controlled probe inventory',name)
  result[name]=sha(_project_source_once('enemy-controlled-probe',name,raw))
 return result

def verified_enemy_observe_sources(root=ROOT):
 """Exactly two default-off observer modules; no source-path wildcard."""
 added=load('enemy-reuse-observe-source.json')['added_sources']
 assert set(added)=={'src/enemy_reuse_observe.h','src/enemy_reuse_observe.inc'}
 for name,digest in added.items():
  path=root/name
  assert not path.is_symlink() and path.is_file(),('unapproved observer module',name)
  assert sha(project_normal_observer_source(name,path.read_bytes()))==digest,('unapproved observer module',name)
 return {name:sha((root/name).read_bytes()) for name in added}

def verified_enemy_reuse_sources(root=ROOT):
 """Exactly three independent enemy semantic modules, never player aliases."""
 ledger=load('enemy-reuse-source.json')
 assert set(ledger['files'])=={'src/entity_draw.c','src/entity_draw.h','src/render_mirror.c','src/render_mirror.h','src/sprite.c','src/tyrian2.c'},'unapproved enemy reuse hook scope'
 added=ledger['added_sources']
 assert set(added)=={'src/enemy_reuse_identity.c','src/enemy_reuse_identity.h','src/enemy_reuse_mirror.inc'},'unapproved enemy reuse source scope'
 green=load('enemy-green-reuse-source.json')
 assert set(green['files'])=={'src/enemy_reuse_identity.c','src/enemy_reuse_identity.h','src/enemy_reuse_mirror.inc','src/tyrian2.c','src/render_mirror.c'},'unapproved green enemy source scope'
 current={}
 for name,digest in added.items():
  path=root/name
  assert not path.is_symlink() and path.is_file(),('unapproved enemy reuse module',name)
  raw=path.read_bytes()
  current[name]=sha(raw)
  raw=project_current_protron_source(name,raw)
  raw=_project_source_once('enemy-controlled-probe',name,raw)
  raw=_project_source_once('enemy-reuse-observe',name,raw)
  raw=_project_source_once('enemy-proof-dedup',name,raw)
  raw=_project_source_once('enemy-protron-reuse',name,raw)
  assert sha(raw)==green['files'][name]['current_sha256'],('unapproved green enemy module',name)
  assert sha(_project_source_once('enemy-green-reuse',name,raw))==digest,('unapproved historical enemy reuse module',name)
 return current

def verified_newshf_identity_sources(root=ROOT):
 """Two exact prototype modules, never a wildcard source/history exclusion."""
 ledger=load('newshf-identity-source.json')
 assert set(ledger['files'])=={'src/render_mirror.c','src/render_mirror.h','src/sprite.c','src/tyrian2.c'},'unapproved NEWSHF observer hook scope'
 added=ledger['added_sources']
 assert set(added)=={'src/newshf_identity_validation.inc','src/newshf_prototype_pins.h'},'unapproved NEWSHF prototype module scope'
 for name,digest in added.items():
  path=root/name
  assert not path.is_symlink() and path.is_file(),('unapproved NEWSHF prototype module',name)
  raw=path.read_bytes()
  pin=load('newshf-compositor-source.json')['files'].get(name)
  assert sha(raw)==(pin['current_sha256'] if pin else digest),('unapproved NEWSHF prototype module',name)
  assert sha(_project_source_once('newshf-compositor',name,raw))==digest,('unapproved NEWSHF prototype module',name)
 return dict(added)

NEWSHF_HEADER='src/newshf_hd_assets.h'
NEWSHF_ROOT='assets/hd/newshf-v1'
NEWSHF_MANIFEST=NEWSHF_ROOT+'/manifest.json'
NEWSHF_IDS=tuple(range(2100000,2100009))
NEWSHF_NAMES=tuple(f'newshf-role{i}-8.hda' for i in NEWSHF_IDS)
NEWSHF_PAIRS=((163,125),(163,123),(163,127),(167,3),(167,1),(167,5),(168,55),(168,17),(168,93))
# Independent finite artwork-policy authority; original source identity stays binary.
NEWSHF168_SOFT_POLICY={'alpha': 'straight-rgba8-zero-transparent-rgb', 'bases': [55, 17, 93], 'record': 168, 'revision': 'newshf168-v4-max-canvas-soft-alpha-v1', 'selected_png_sha256': {'17': 'e02d8f0b3c622aa7fd846406f5df30dc6ac0a4af1eed70a1103fec19dac1955b', '55': '9cfc7d7b8c2b20917bd58898cf21fbb76ad2841e371158f37316aab3f8818e70', '93': 'c0f68d1715b31fa314f9ba65dbb910bc7c7edc3f6ad4bb4f2958da032e6f61b5'}}

def verified_newshf_compositor_sources(root=ROOT):
 """One exact executable module; generated header has independent pixel proof."""
 added=load('newshf-compositor-source.json')['added_sources']
 assert set(added)=={'src/global_newshf_mirror.inc'},'unapproved NEWSHF compositor module scope'
 soft=load('newshf168-soft-alpha-source.json')
 assert set(soft['files'])=={'src/global_newshf_mirror.inc'},'unapproved NEWSHF soft-alpha module scope'
 current={}
 for name,digest in added.items():
  path=root/name
  assert not path.is_symlink() and path.is_file(),('unapproved NEWSHF compositor module',name)
  current[name]=sha(path.read_bytes())
  raw=project_current_newshf_source(name,path.read_bytes())
  assert sha(raw)==soft['files'][name]['current_sha256'],('unapproved NEWSHF compositor module',name)
  assert sha(_project_source_once('newshf168-soft-alpha',name,raw))==digest,('unapproved NEWSHF compositor historical module',name)
 return current

def verified_newshf_current(root=ROOT):
 return _verified_newshf_current(root,_proofs=None)

def _verified_newshf_current(root=ROOT, *, _proofs):
 """Independently bind nine PNG payloads, fixed roles, transports and package rows.

 Generated payload bytes may follow a deliberate repinned source art edit. They
 can never redefine bank identity, role, dimensions, anchor or consumer paths.
 """
 import io,struct
 from PIL import Image
 scripts=str(ROOT/'scripts')
 if scripts not in sys.path:sys.path.insert(0,scripts)
 import build_newshf_hd as builder
 assert builder.IDS==NEWSHF_IDS and builder.PAIRS==NEWSHF_PAIRS,'unapproved NEWSHF identity roles'
 assert builder.HEADER==NEWSHF_HEADER and builder.OUTPUT==NEWSHF_ROOT and builder.MANIFEST==NEWSHF_MANIFEST,'unapproved NEWSHF generated paths'
 loaded=builder.load(root)
 expected_destinations={'assets/global/newshf/'+name for name in NEWSHF_NAMES}
 assert set(loaded)==expected_destinations,'unapproved NEWSHF consumers'
 source='authoring-inputs/enemies/newshf-phase-a/'
 selected=json.loads((root/(source+'manifest.json')).read_bytes())
 assert len(selected['art'])==9,'unapproved NEWSHF pose count'
 outputs={};declarations=[]
 runtime=json.loads((root/'packaging/runtime-assets-v1.json').read_bytes())
 runtime['files']=_before_sonic_runtime(runtime['files'],root,_proofs=_proofs)
 runtime_rows={r['destination']:r for r in runtime['files']}
 assert len(runtime_rows)==len(runtime['files'])==1025,'unapproved NEWSHF runtime scope'
 for identity,pair,name,art in zip(NEWSHF_IDS,NEWSHF_PAIRS,NEWSHF_NAMES,selected['art']):
  record,base=pair
  assert (art['record'],art['base'])==pair and art['source_id']==f'newshf.shp:base:{base}','unapproved NEWSHF source association'
  assert art['file']==f'enemy-{record}-v1-bbox-fit-base{base}.png','unapproved NEWSHF master path'
  path=root/(source+art['file']);assert not path.is_symlink() and path.is_file(),'invalid NEWSHF master'
  png=path.read_bytes();assert sha(png)==art['art_sha256'],'stale NEWSHF selected source'
  with Image.open(io.BytesIO(png)) as image:
   assert image.format=='PNG' and image.mode=='RGBA' and image.size==(192,224) and getattr(image,'n_frames',1)==1,'unapproved NEWSHF geometry'
   payload=image.tobytes()
  if record==168 and selected.get('schema')==2:
   assert selected.get('art_policy')==NEWSHF168_SOFT_POLICY,'unapproved NEWSHF soft-alpha policy'
   assert sha(png)==NEWSHF168_SOFT_POLICY['selected_png_sha256'][str(base)],'unselected NEWSHF168 soft-alpha revision'
   assert all(payload[i+3] or payload[i:i+3]==b'\0\0\0' for i in range(0,len(payload),4)),'hidden NEWSHF168 transparent RGB'
  else:
   assert all(payload[i] in (0,255) for i in range(3,len(payload),4)),'nonbinary NEWSHF alpha'
  blob=struct.pack('<4s6I',b'HDR1',identity,8,24,28,6,7)+payload
  path=NEWSHF_ROOT+'/'+name;destination='assets/global/newshf/'+name
  assert (root/path).read_bytes()==blob,'stale NEWSHF master/transport'
  value=14695981039346656037
  for byte in payload:value=((value^byte)*1099511628211)&0xffffffffffffffff
  declarations.append(f' {{{identity}u,{len(blob)}u,8u,24u,28u,6,7,"newshf/{name}",UINT64_C(0x{value:016x})}},')
  outputs[path]={'sha256':sha(blob),'mode':'100644'}
  row=dict(source_path=path,destination=destination,group='newshf-optin',revision='current-single-source-newshf-nine',bytes=len(blob),sha256=sha(blob),git_blob=hashlib.sha1(b'blob '+str(len(blob)).encode()+b'\0'+blob).hexdigest())
  assert runtime_rows[destination]==row,'stale NEWSHF runtime member'
 header=('/* Generated by scripts/build_newshf_hd.py; unchanged selected pixels. */\n'
  '#ifndef NEWSHF_HD_ASSETS_H\n#define NEWSHF_HD_ASSETS_H\n#include "global_asset_registry.h"\n'
  'enum { NEWSHF_HD_RESOURCE_COUNT = 9 };\n'
  'static const GlobalAssetResource newshf_hd_resources[NEWSHF_HD_RESOURCE_COUNT] = {\n'+
  '\n'.join(declarations)+'\n};\n#endif\n').encode()
 assert (root/NEWSHF_HEADER).read_bytes()==header,'stale NEWSHF generated header'
 manifest=(root/NEWSHF_MANIFEST).read_bytes()
 outputs[NEWSHF_MANIFEST]={'sha256':sha(manifest),'mode':'100644'}
 binding=json.loads((root/'packaging/current-production-validation.json').read_bytes())
 assert len(_before_current_newshf_inventory(binding['source_sha256'],root,_proofs=_proofs))==268+len(verified_enemy_probe_sources(root)) and binding['source_sha256'].get(NEWSHF_HEADER)==sha(header),'stale NEWSHF source binding'
 return dict(assets=outputs,header_sha256=sha(header))

PINS['p9-stage-catalog.json']='565303b7f5b4f2cf726214a61e2f95148f4ed0ba816a81939ad6bc4c2b62d4d3'
PINS['p9-assets.json']='1b83129e300efeb77fe0e143882a456b91e6083817fb80f442ea6d9740513ff7'
def canonical(obj):return json.dumps(obj,sort_keys=True,separators=(',',':')).encode()

SIDEKICK_HEADER='src/current_sidekick_body_payload_pins.h'
SIDEKICK_SELECTION='assets/hd/authoring/sidekick-body-current.json'
SIDEKICK_IDS=(1260152,1290224,1290243,1290262,1290281,1290300)
SIDEKICK_NAMES=('option-marlo-bank9-152-8.hda','option-plasma-bank9-224-8.hda','option-plasma-bank9-243-8.hda','option-plasma-bank9-262-8.hda','option-plasma-bank9-281-8.hda','option-plasma-bank9-300-8.hda')
SIDEKICK_ROOT='assets/hd/current-compat/sidekick-body'
PRODUCTION_NON_CODE={
 'src/third_party/dr_mp3-LICENSE':'dd1c647e6f767f8ff4b2dfae0fed314726600a01e0cf1ef556afddd5fa96ff15',
 'src/third_party/dr_mp3-PROVENANCE.md':'8a5f3ff084155e583b7e0c74a943ad8bfb9249178e915da32f4b7e9133ba045e',
}

def verified_sidekick_current(root=ROOT):
 return _verified_sidekick_current(root,_proofs=None)

def _verified_sidekick_current(root=ROOT, *, _proofs):
 """Derive the six approved-role outputs from current PNG bytes, never hashes alone.

 This is build/package consistency, not artwork approval or runtime C enforcement.
 Only the fixed selection and six transport paths may enter asset projection.
 """
 scripts=str(ROOT/'scripts')
 if scripts not in sys.path:sys.path.insert(0,scripts)
 import build_current_sidekick_body as builder
 import current_sidekick_body_compatibility as compat
 assert compat.IDS==SIDEKICK_IDS and compat.HEADER==SIDEKICK_HEADER
 assert compat.SELECTION==SIDEKICK_SELECTION and compat.ROOT==SIDEKICK_ROOT
 raw=builder.read(root,SIDEKICK_SELECTION);selected=builder.selection(root,raw)
 loaded=compat.load(root);outputs={SIDEKICK_SELECTION:{'sha256':sha(raw),'mode':'100644'}}
 rows=[];pins={};blobs={};sources={}
 for identity,name,row in zip(SIDEKICK_IDS,SIDEKICK_NAMES,selected['resources']):
  blob,payload=builder.source_blob(root,row);source=SIDEKICK_ROOT+'/'+name
  assert builder.read(root,source)==blob,('current PNG/HDA mismatch',identity)
  entry=dict(identity=identity,source_path=source,destination='assets/gameplay/'+name,sha256=sha(blob))
  assert loaded[entry['destination']]==entry,('current compatibility mismatch',identity)
  rows.append(entry);pins[identity]=compat.fnv(payload);blobs[entry['destination']]=blob
  sources[row['source_png']]=row['source_sha256']
  outputs[source]={'sha256':sha(blob),'mode':'100644'}
 expected_mapping=dict(schema='opentyrian-current-sidekick-body-compatibility-v1',selection=SIDEKICK_SELECTION,version=selected['version'],files=rows)
 assert builder.read(root,compat.MAPPING)==builder.encoded(expected_mapping),'current selection/mapping mismatch'
 header=compat.payload_header(pins)
 assert builder.read(root,SIDEKICK_HEADER)==header,'current PNG/generated-header mismatch'
 # Generated source binding and the declared runtime consumers must also be
 # current; coherent image bytes alone cannot bless a stale package plan.
 from verify_current_production import verify
 binding_raw=builder.read(root,builder.BINDING);binding=json.loads(binding_raw)
 verify(root,binding)
 assert len(_before_current_newshf_inventory(binding['source_sha256'],root,_proofs=_proofs))==268+len(verified_enemy_probe_sources(root)),'unexpected current production source scope'
 expected_sources=dict(load('current-source-inventory.json')['files'])
 expected_sources[SIDEKICK_HEADER]=sha(header);expected_sources.update(PRODUCTION_NON_CODE)
 expected_sources.update(verified_newshf_identity_sources(root))
 expected_sources.update(verified_newshf_compositor_sources(root))
 expected_sources.update(verified_enemy_reuse_sources(root))
 expected_sources.update(verified_enemy_observe_sources(root))
 expected_sources.update(verified_enemy_probe_sources(root))
 expected_sources[PROTRON_HEADER]=verified_protron_current(root)['header_sha256']
 expected_sources[CURRENT_PROTRON_HEADER]=_current_projection_proof('protron',root,_proofs)['header_sha256']
 expected_sources[CURRENT_REAR_P7_HEADER]=_current_projection_proof('rear_p7',root,_proofs)['header_sha256']
 expected_sources[CURRENT_MISSILE_HEADER]=_current_projection_proof('missile',root,_proofs)['header_sha256']
 expected_sources[CURRENT_MINT27_HEADER]=_current_projection_proof('mint27',root,_proofs)['header_sha256']
 expected_sources[CURRENT_NEWSHF_HEADER]=_current_projection_proof('newshf',root,_proofs)['header_sha256']
 expected_sources[CURRENT_GUIDED_HEADER]=_current_projection_proof('guided',root,_proofs)['header_sha256']
 expected_sources[CURRENT_SONIC_HEADER]=_current_projection_proof('sonic',root,_proofs)['header_sha256']
 expected_sources[NEWSHF_HEADER]=_verified_newshf_current(root,_proofs=_proofs)['header_sha256']
 expected_sources[ORB_HEADER]=_verified_enemy_orb_current(root,_proofs=_proofs)['header_sha256']
 expected_sources[PLASMA_HEADER]=_verified_plasma_projectile_current(root,_proofs=_proofs)['header_sha256']
 # Preserve the existing non-target-source authority rejection before the
 # Front proof's runtime-binding check. Its actual header is derived below.
 expected_sources[FRONT_MULTI_HEADER]=sha(builder.read(root,FRONT_MULTI_HEADER))
 for name in corrected_source_paths():
  raw=builder.read(root,name)
  assert sha(project_source('render-boundaries',name,raw))==expected_sources[name],('reviewed correction historical source mismatch',name)
  expected_sources[name]=sha(raw)
 assert binding['source_sha256']==expected_sources,'unapproved non-target production source binding'
 assert expected_sources[FRONT_MULTI_HEADER]==_verified_front_multi_current(root,_proofs=_proofs)['header_sha256'],'unverified Front Multi production header'
 runtime=json.loads(builder.read(root,builder.RUNTIME))
 runtime['files']=_before_sonic_runtime(runtime['files'],root,_proofs=_proofs)
 runtime_rows={r['destination']:r for r in runtime['files']}
 assert len(runtime_rows)==len(runtime['files'])==1025,'unexpected current runtime destination scope'
 def blob_row(source,destination,group,revision,data):
  import hashlib
  oid=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
  return dict(source_path=source,destination=destination,group=group,revision=revision,bytes=len(data),git_blob=oid,sha256=sha(data))
 for row in rows:
  destination=row['destination']
  assert runtime_rows.get(destination)==blob_row(row['source_path'],destination,'gameplay','current-single-source-sidekick-body',blobs[destination]),('stale current runtime body',destination)
 assert runtime_rows.get('CURRENT-PRODUCTION-VALIDATION.json')==blob_row(builder.BINDING,'CURRENT-PRODUCTION-VALIDATION.json','current-production-validation','reconstructed-local-unpublished',binding_raw),'stale current runtime source binding'
 assert runtime['source_revision']['current_production_source_manifest_sha256']==binding['production_source_manifest_sha256'],'stale current runtime source digest'
 return dict(assets=outputs,header_sha256=sha(header),source_pngs=sources)

ORB_SELECTION='assets/hd/authoring/enemy-orb-current.json'
ORB_ROOT='assets/hd/current-compat/enemy-orb'
ORB_HEADER='src/current_enemy_orb_payload_pins.h'
ORB_IDS=(80112,80113,1420112,1420113)
ORB_NAMES=('bullet-112-8.hda','bullet-113-8.hda','enemy-orb112113-112-8.hda','enemy-orb112113-113-8.hda')
ORB_MASK='000000000000000000000000000000000000000000000000000011111000000111111100000111111100000111111100000111111100000111111100000011111000000000000000000000000000000000000000'

def verified_enemy_orb_current(root=ROOT):
 return _verified_enemy_orb_current(root,_proofs=None)

def _verified_enemy_orb_current(root=ROOT, *, _proofs):
 """Independent two-master/four-contract proof before any history projection."""
 import io,struct
 from PIL import Image
 scripts=str(ROOT/'scripts')
 if scripts not in sys.path:sys.path.insert(0,scripts)
 import current_enemy_orb_compatibility as compat
 assert compat.IDS==ORB_IDS and compat.SELECTION==ORB_SELECTION and compat.ROOT==ORB_ROOT and compat.HEADER==ORB_HEADER,'unapproved orb scope'
 assert compat.MASK==ORB_MASK and ORB_MASK.count('1')==45,'unapproved orb support'
 loaded=compat.load(root);raw=compat.read(root,ORB_SELECTION);selected=json.loads(raw)
 assert set(selected)=={'schema','version','masters'} and selected['schema']=='opentyrian-current-enemy-orb-authoring-v1','unapproved orb selection'
 assert len(selected['masters'])==2,'unapproved orb master count'
 payloads={}
 for selector,record in zip((112,113),selected['masters']):
  assert set(record)=={'selector','source_png','source_sha256'} and type(record['selector']) is int and record['selector']==selector,'unapproved orb identity/order'
  assert record['source_png']==f'authoring-inputs/enemy-orb-current/orb-{selector}.png','unapproved orb authoring input'
  png=compat.read(root,record['source_png']);assert sha(png)==record['source_sha256'],'stale orb source'
  with Image.open(io.BytesIO(png)) as image:
   assert image.format=='PNG' and image.mode=='RGBA' and image.size==(96,112) and getattr(image,'n_frames',1)==1,'unapproved orb PNG geometry'
   original=image.tobytes()
  masked=bytearray(original);occupied=set()
  for y in range(112):
   for x in range(96):
    cell=(y//8)*12+x//8;offset=(y*96+x)*4
    if ORB_MASK[cell]=='0':masked[offset:offset+4]=b'\0'*4
    elif original[offset+3]:occupied.add(cell)
  assert len(occupied)==45,'orb source misses original support'
  payloads[80000+selector]=original;payloads[1420000+selector]=bytes(masked)
 outputs={ORB_SELECTION:{'sha256':sha(raw),'mode':'100644'}};rows=[];pins={}
 runtime=json.loads(compat.read(root,'packaging/runtime-assets-v1.json'))
 runtime['files']=_before_sonic_runtime(runtime['files'],root,_proofs=_proofs)
 runtime_rows={r['destination']:r for r in runtime['files']}
 assert len(runtime_rows)==len(runtime['files'])==1025,'unapproved orb runtime scope'
 assert set(loaded)=={'assets/gameplay/'+name for name in ORB_NAMES},'unapproved orb consumers'
 for identity,name in zip(ORB_IDS,ORB_NAMES):
  payload=payloads[identity];blob=struct.pack('<4s6I',b'HDR1',identity,8,12,14,0,0)+payload
  source=ORB_ROOT+'/'+name;destination='assets/gameplay/'+name
  assert compat.read(root,source)==blob,'stale orb master/transport'
  row=dict(identity=identity,density=8,source_path=source,destination=destination,sha256=sha(blob))
  assert loaded[destination]==row,'stale orb mapping row'
  rows.append(row);outputs[source]={'sha256':sha(blob),'mode':'100644'}
  value=14695981039346656037
  for byte in payload:value=((value^byte)*1099511628211)&0xffffffffffffffff
  pins[identity,8]=f'{value:016x}'
  if identity<100000:
   oid=hashlib.sha1(b'blob '+str(len(blob)).encode()+b'\0'+blob).hexdigest()
   expected=dict(source_path=source,destination=destination,group='gameplay',revision='current-single-source-enemy-orb',bytes=len(blob),git_blob=oid,sha256=sha(blob))
   assert runtime_rows.get(destination)==expected,'stale orb runtime selection'
  else:assert destination not in runtime_rows,'opt-in orb leaked into default runtime'
 expected=dict(schema='opentyrian-current-enemy-orb-compatibility-v1',selection=ORB_SELECTION,version=selected['version'],files=rows)
 assert compat.read(root,'packaging/current-enemy-orb-compatibility.json')==(json.dumps(expected,indent=2)+'\n').encode(),'stale orb mapping'
 header=compat.payload_header(pins);assert compat.read(root,ORB_HEADER)==header,'stale orb generated header'
 binding=json.loads(compat.read(root,'packaging/current-production-validation.json'))
 assert len(_before_current_newshf_inventory(binding['source_sha256'],root,_proofs=_proofs))==268+len(verified_enemy_probe_sources(root)) and binding['source_sha256'].get(ORB_HEADER)==sha(header),'stale orb source binding'
 for name,pin in load('enemy-orb-source.json')['files'].items():
  assert binding['source_sha256'].get(name)==pin['current_sha256'],'stale orb source inverse binding'
 assert len(outputs)==5,'unapproved orb asset projection'
 return dict(assets=outputs,header_sha256=sha(header))

PLASMA_SELECTION='assets/hd/authoring/plasma-projectile-current.json'
PLASMA_ROOT='assets/hd/current-compat/plasma-projectile'
PLASMA_HEADER='src/current_plasma_projectile_payload_pins.h'
PLASMA_MAPPING='packaging/current-plasma-projectile-compatibility.json'
PLASMA_PAIRS=tuple((identity,density) for identity in (1300022,1300023,1300024) for density in (4,8))
PLASMA_NAMES=tuple('option-plasma-projectile-%d-%d.hda'%(identity-1300000,density) for identity,density in PLASMA_PAIRS)

def verified_plasma_projectile_current(root=ROOT):
 return _verified_plasma_projectile_current(root,_proofs=None)

def _verified_plasma_projectile_current(root=ROOT, *, _proofs):
 """Derive six fixed transports and payload pins from one master/recipe.

 Only the selection plus six HDA paths are projected from the old asset census.
 The historical master and transports remain protected by the old immutable
 inventory, while the current authoring master must live outside assets.
 """
 import io,struct
 from PIL import Image
 scripts=str(ROOT/'scripts')
 if scripts not in sys.path:sys.path.insert(0,scripts)
 import current_plasma_projectile_compatibility as compat
 assert compat.PAIRS==PLASMA_PAIRS and compat.SELECTION==PLASMA_SELECTION
 assert compat.ROOT==PLASMA_ROOT and compat.HEADER==PLASMA_HEADER and compat.MAPPING==PLASMA_MAPPING
 loaded=compat.load(root)
 raw=(root/PLASMA_SELECTION).read_bytes();selected=json.loads(raw)
 assert set(selected)=={'schema','version','master','recipe','resources'},'unapproved Plasma projectile selection fields'
 assert selected['schema']=='opentyrian-current-plasma-projectile-authoring-v1','unapproved Plasma projectile schema'
 inputs=compat.input_paths(root)
 assert len(inputs)==9 and {p for p in inputs if p.startswith('assets/')}=={PLASMA_SELECTION},'unapproved Plasma projectile authoring input scope'
 expected_destinations={'assets/gameplay/'+name for name in PLASMA_NAMES}
 assert set(loaded)==expected_destinations,'unapproved Plasma projectile consumers'
 assert [(r['identity'],r['density']) for r in selected['resources']]==list(PLASMA_PAIRS),'unapproved Plasma projectile output order'
 outputs={PLASMA_SELECTION:{'sha256':sha(raw),'mode':'100644'}};rows=[];pins={}
 runtime=json.loads((root/'packaging/runtime-assets-v1.json').read_bytes())
 runtime['files']=_before_sonic_runtime(runtime['files'],root,_proofs=_proofs)
 runtime_rows={r['destination']:r for r in runtime['files']}
 assert len(runtime_rows)==len(runtime['files'])==1025,'unexpected current runtime destination scope'
 for (identity,density),name,record in zip(PLASMA_PAIRS,PLASMA_NAMES,selected['resources']):
  assert set(record)=={'identity','density','source_png','source_sha256'},'unapproved Plasma projectile resource fields'
  png=(root/record['source_png']).read_bytes()
  assert sha(png)==record['source_sha256'],'current Plasma projectile PNG hash mismatch'
  w,h={1300022:(62,24),1300023:(65,28),1300024:(62,23)}[identity]
  with Image.open(io.BytesIO(png)) as image:
   assert image.format=='PNG' and image.mode=='RGBA' and image.size==(w*density,h*density) and getattr(image,'n_frames',1)==1,'current Plasma projectile PNG geometry mismatch'
   payload=image.tobytes();blob=struct.pack('<4s6I',b'HDR1',identity,density,w,h,0,0)+payload
  source=PLASMA_ROOT+'/'+name;destination='assets/gameplay/'+name
  assert (root/source).read_bytes()==blob,('current Plasma projectile PNG/HDA mismatch',identity,density)
  row=dict(identity=identity,density=density,source_path=source,destination=destination,sha256=sha(blob))
  assert loaded[destination]==row,('current Plasma projectile compatibility mismatch',destination)
  rows.append(row)
  value=14695981039346656037
  for byte in payload:value=((value^byte)*1099511628211)&0xffffffffffffffff
  pins[identity,density]=f'{value:016x}'
  oid=hashlib.sha1(b'blob '+str(len(blob)).encode()+b'\0'+blob).hexdigest()
  expected=dict(source_path=source,destination=destination,group='gameplay',revision='current-single-source-plasma-projectile',bytes=len(blob),git_blob=oid,sha256=sha(blob))
  assert runtime_rows.get(destination)==expected,('stale current Plasma projectile runtime body',destination)
  outputs[source]={'sha256':sha(blob),'mode':'100644'}
 expected=dict(schema='opentyrian-current-plasma-projectile-compatibility-v1',selection=PLASMA_SELECTION,version=selected['version'],files=rows)
 assert (root/PLASMA_MAPPING).read_bytes()==(json.dumps(expected,indent=2)+'\n').encode(),'current Plasma projectile selection/mapping mismatch'
 header=compat.payload_header(pins)
 assert (root/PLASMA_HEADER).read_bytes()==header,'current Plasma projectile/generated-header mismatch'
 assert len(outputs)==7,'unapproved Plasma projectile asset scope'
 return dict(assets=outputs,header_sha256=sha(header))

FRONT_MULTI_SELECTION='assets/hd/authoring/front-multi-current.json'
FRONT_MULTI_ROOT='assets/hd/current-compat/front-multi'
FRONT_MULTI_HEADER='src/hd_front_multi_current.h'
FRONT_MULTI_MAPPING='packaging/current-front-multi-compatibility.json'
FRONT_MULTI_IDS=(80121,80122,80163,80164,80201,80202,80279,80280)
FRONT_MULTI_NAMES=('bullet-121-8.hda','bullet-122-8.hda','bullet-163-8.hda','bullet-164-8.hda','bullet-201-8.hda','bullet-202-8.hda','bullet-279-8.hda','bullet-280-8.hda')

def verified_front_multi_current(root=ROOT):
 return _verified_front_multi_current(root,_proofs=None)

def _verified_front_multi_current(root=ROOT, *, _proofs):
 """Independently decode eight selected sources, then admit exactly nine assets.

 No historical master, source image or transport is an exemption. Full actual
 source bytes are checked separately by verified_sidekick_current and
 validate_current_sources; this proof also binds its generated header and
 current runtime manifest to the production binding, rather than hashes alone.
 """
 import io,struct
 from PIL import Image
 scripts=str(ROOT/'scripts')
 if scripts not in sys.path:sys.path.insert(0,scripts)
 import current_front_multi_compatibility as compat
 assert compat.IDS==FRONT_MULTI_IDS and compat.SELECTION==FRONT_MULTI_SELECTION
 assert compat.ROOT==FRONT_MULTI_ROOT and compat.HEADER==FRONT_MULTI_HEADER and compat.MAPPING==FRONT_MULTI_MAPPING
 loaded=compat.load(root)
 raw=compat.read(root,FRONT_MULTI_SELECTION);selected=json.loads(raw)
 assert set(selected)=={'schema','version','resources'} and selected['schema']=='opentyrian-current-front-multi-authoring-v1','unapproved Front Multi selection contract'
 inputs=compat.input_paths(root)
 assert len(inputs)==9 and {p for p in inputs if p.startswith('assets/')}=={FRONT_MULTI_SELECTION},'unapproved Front Multi authoring input scope'
 assert [r['identity'] for r in selected['resources']]==list(FRONT_MULTI_IDS),'unapproved Front Multi output order'
 assert set(loaded)=={'assets/gameplay/'+name for name in FRONT_MULTI_NAMES},'unapproved Front Multi consumers'
 outputs={FRONT_MULTI_SELECTION:{'sha256':sha(raw),'mode':'100644'}};rows=[];pins={};sources={}
 runtime=json.loads(compat.read(root,'packaging/runtime-assets-v1.json'))
 runtime['files']=_before_sonic_runtime(runtime['files'],root,_proofs=_proofs)
 runtime_rows={r['destination']:r for r in runtime['files']}
 assert len(runtime_rows)==len(runtime['files'])==1025,'unexpected current runtime destination scope'
 for identity,name,record in zip(FRONT_MULTI_IDS,FRONT_MULTI_NAMES,selected['resources']):
  assert set(record)=={'identity','source_png','source_sha256'} and type(record['identity']) is int,'unapproved Front Multi resource fields'
  png=compat.read(root,record['source_png']);assert sha(png)==record['source_sha256'],'current Front Multi PNG hash mismatch'
  with Image.open(io.BytesIO(png)) as image:
   assert image.format=='PNG' and image.mode=='RGBA' and image.size==(96,112) and getattr(image,'n_frames',1)==1,'current Front Multi PNG geometry mismatch'
   payload=image.tobytes();blob=struct.pack('<4s6I',b'HDR1',identity,8,12,14,0,0)+payload
  source=FRONT_MULTI_ROOT+'/'+name;destination='assets/gameplay/'+name
  assert compat.read(root,source)==blob,('current Front Multi PNG/HDA mismatch',identity)
  row=dict(identity=identity,source_path=source,destination=destination,sha256=sha(blob))
  assert loaded[destination]==row,('current Front Multi compatibility mismatch',destination)
  rows.append(row);sources[record['source_png']]=record['source_sha256']
  value=14695981039346656037
  for byte in payload:value=((value^byte)*1099511628211)&0xffffffffffffffff
  pins[identity]=f'{value:016x}'
  oid=hashlib.sha1(b'blob '+str(len(blob)).encode()+b'\0'+blob).hexdigest()
  expected=dict(source_path=source,destination=destination,group='gameplay',revision='current-single-source-front-multi',bytes=len(blob),git_blob=oid,sha256=sha(blob))
  assert runtime_rows.get(destination)==expected,('stale current Front Multi runtime body',destination)
  outputs[source]={'sha256':sha(blob),'mode':'100644'}
 expected=dict(schema='opentyrian-current-front-multi-compatibility-v1',selection=FRONT_MULTI_SELECTION,version=selected['version'],files=rows)
 assert compat.read(root,FRONT_MULTI_MAPPING)==(json.dumps(expected,indent=2)+'\n').encode(),'current Front Multi selection/mapping mismatch'
 header=compat.payload_header(pins)
 assert compat.read(root,FRONT_MULTI_HEADER)==header,'current Front Multi/generated-header mismatch'
 binding_raw=compat.read(root,'packaging/current-production-validation.json');binding=json.loads(binding_raw)
 from verify_current_production import source_manifest_digest
 assert len(_before_current_newshf_inventory(binding['source_sha256'],root,_proofs=_proofs))==268+len(verified_enemy_probe_sources(root)) and binding['source_sha256'].get(FRONT_MULTI_HEADER)==sha(header),'stale Front Multi production header binding'
 renderer=compat.read(root,'src/render_mirror.c')
 assert binding['source_sha256'].get('src/render_mirror.c')==sha(renderer) and sha(project_source('newshf-identity','src/render_mirror.c',renderer))==load('front-multi-source.json')['files']['src/render_mirror.c']['current_sha256'],'stale Front Multi renderer binding'
 assert binding['production_source_manifest_sha256']==source_manifest_digest(binding['source_sha256']),'stale Front Multi source manifest digest'
 oid=hashlib.sha1(b'blob '+str(len(binding_raw)).encode()+b'\0'+binding_raw).hexdigest()
 expected=dict(source_path='packaging/current-production-validation.json',destination='CURRENT-PRODUCTION-VALIDATION.json',group='current-production-validation',revision='reconstructed-local-unpublished',bytes=len(binding_raw),git_blob=oid,sha256=sha(binding_raw))
 assert runtime_rows.get('CURRENT-PRODUCTION-VALIDATION.json')==expected,'stale Front Multi runtime source binding'
 assert runtime['source_revision']['current_production_source_manifest_sha256']==binding['production_source_manifest_sha256'],'stale Front Multi runtime source digest'
 assert len(outputs)==9 and len(sources)==8,'unapproved Front Multi asset scope'
 return dict(assets=outputs,header_sha256=sha(header),source_pngs=sources)

CRAFT267_SELECTION='assets/hd/authoring/craft267-current.json'
CRAFT267_CANONICAL='assets/hd/current-compat/craft267/enemy-newsh2-267-8.hda'
CRAFT267_DESTINATION='assets/gameplay/enemy-newsh2-267-8.hda'
CRAFT267_README='assets/hd/README.md'

def verified_craft267_current(root=ROOT):
 return _verified_craft267_current(root,_proofs=None)

def _verified_craft267_current(root=ROOT, *, _proofs):
 """One fixed legacy identity; derive pixels before admitting its two outputs."""
 scripts=str(ROOT/'scripts')
 if scripts not in sys.path:sys.path.insert(0,scripts)
 import build_current_craft267 as builder
 import current_craft267_compatibility as compat
 assert compat.IDENTITY==1010267 and compat.SELECTION==CRAFT267_SELECTION
 assert compat.CANONICAL==CRAFT267_CANONICAL and compat.DESTINATION==CRAFT267_DESTINATION
 raw=builder.read(root,CRAFT267_SELECTION);selected=builder.selection(root,raw)
 blob=builder.source_blob(root,selected['resources'][0])
 assert builder.read(root,CRAFT267_CANONICAL)==blob,'current craft267 PNG/HDA mismatch'
 row=dict(identity=1010267,source_path=CRAFT267_CANONICAL,destination=CRAFT267_DESTINATION,sha256=sha(blob))
 assert compat.load(root)=={CRAFT267_DESTINATION:row},'current craft267 compatibility mismatch'
 expected=dict(schema='opentyrian-current-craft267-compatibility-v1',selection=CRAFT267_SELECTION,version=selected['version'],files=[row])
 assert builder.read(root,compat.MAPPING)==builder.encoded(expected),'current craft267 selection/mapping mismatch'
 runtime=builder.parse(builder.read(root,builder.RUNTIME))
 runtime['files']=_before_sonic_runtime(runtime['files'],root,_proofs=_proofs)
 rows={r['destination']:r for r in runtime['files']}
 assert len(rows)==len(runtime['files'])==1025,'unexpected current runtime destination scope'
 oid=hashlib.sha1(b'blob '+str(len(blob)).encode()+b'\0'+blob).hexdigest()
 expected=dict(source_path=CRAFT267_CANONICAL,destination=CRAFT267_DESTINATION,group='gameplay',revision='current-single-source-craft267',bytes=len(blob),git_blob=oid,sha256=sha(blob))
 assert rows.get(CRAFT267_DESTINATION)==expected,'stale current craft267 runtime body'
 source=selected['resources'][0]
 return dict(assets={CRAFT267_SELECTION:{'sha256':sha(raw),'mode':'100644'},CRAFT267_CANONICAL:{'sha256':sha(blob),'mode':'100644'}},source_pngs={source['source_png']:source['source_sha256']})

CHARGE_SELECTION='assets/hd/authoring/charge-body-current.json'
CHARGE_ROOT='assets/hd/current-compat/charge-body'
CHARGE_IDS=(1450258,1450259,1450260,1450277,1450278,1450279,1450296,1450297,1450298)
CHARGE_NAMES=tuple('option-charge-bank9-%d-8.hda'%(identity-1450000) for identity in CHARGE_IDS)

def verified_charge_current(root=ROOT):
 return _verified_charge_current(root,_proofs=None)

def _verified_charge_current(root=ROOT, *, _proofs):
 """Prove nine derived bodies from the one editable master/recipe, then ten paths.

 This proof is independent of the immutable old P9 nine-output ledger. Original
 game references are not inputs, and no authoring input becomes an assets waiver.
 """
 scripts=str(ROOT/'scripts')
 if scripts not in sys.path:sys.path.insert(0,scripts)
 import build_current_sidekick_body as builder
 import current_sidekick_body_compatibility as compat
 assert compat.CHARGE_IDS==CHARGE_IDS and compat.CHARGE_SELECTION==CHARGE_SELECTION
 assert compat.CHARGE_ROOT==CHARGE_ROOT
 assert compat.CHARGE_MAPPING=='packaging/current-charge-body-compatibility.json'
 assert tuple(compat.charge_name(i) for i in CHARGE_IDS)==CHARGE_NAMES
 # charge_load recomputes all nine RGBA payloads and checks derived PNGs, HDA,
 # selector SHAs and the complete mapping; independent PNG hashes never suffice.
 loaded=compat.charge_load(root)
 raw=builder.read(root,CHARGE_SELECTION)
 inputs=compat.charge_input_paths(root)
 assert len(inputs)==12 and {p for p in inputs if p.startswith('assets/')}=={CHARGE_SELECTION},'unapproved Charge authoring asset inputs'
 expected_destinations={'assets/gameplay/'+name for name in CHARGE_NAMES}
 assert set(loaded)==expected_destinations,'unapproved Charge consumer scope'
 outputs={CHARGE_SELECTION:{'sha256':sha(raw),'mode':'100644'}}
 runtime=json.loads(builder.read(root,builder.RUNTIME))
 runtime['files']=_before_sonic_runtime(runtime['files'],root,_proofs=_proofs)
 rows={r['destination']:r for r in runtime['files']}
 assert len(rows)==len(runtime['files'])==1025,'unexpected current runtime destination scope'
 for identity,name in zip(CHARGE_IDS,CHARGE_NAMES):
  source=CHARGE_ROOT+'/'+name;destination='assets/gameplay/'+name
  blob=builder.read(root,source)
  expected=dict(identity=identity,source_path=source,destination=destination,sha256=sha(blob))
  assert loaded[destination]==expected,('unapproved Charge compatibility row',destination)
  oid=hashlib.sha1(b'blob '+str(len(blob)).encode()+b'\0'+blob).hexdigest()
  expected=dict(source_path=source,destination=destination,group='gameplay',revision='current-single-source-charge-body',bytes=len(blob),git_blob=oid,sha256=sha(blob))
  assert rows.get(destination)==expected,('stale current Charge runtime body',destination)
  outputs[source]={'sha256':sha(blob),'mode':'100644'}
 assert len(outputs)==10,'unapproved Charge asset scope'
 return dict(assets=outputs)

MF_SELECTION='assets/hd/authoring/mint-front-body-current.json'
MF_ROOT='assets/hd/current-compat/mint-front-body'
MF_IDS=(1270112,1270131,1270150,1280083)
MF_NAMES=('option-mint-bank9-112-8.hda','option-mint-bank9-131-8.hda','option-mint-bank9-150-8.hda','option-frontblaster-bank10-83-8.hda')
MF_MAPPING='packaging/current-mint-front-body-compatibility.json'

def verified_mint_front_current(root=ROOT):
 return _verified_mint_front_current(root,_proofs=None)

def _verified_mint_front_current(root=ROOT, *, _proofs):
 """Verify exactly four independent current sources, then project five assets.

 Current pixels are not pinned to the historical bootstrap. Decode each selected
 PNG independently and bind its exact fixed-role HDR1 transport, mapping and
 existing runtime destination. No source PNG is an asset-inventory exemption.
 """
 import io,struct
 from PIL import Image
 scripts=str(ROOT/'scripts')
 if scripts not in sys.path:sys.path.insert(0,scripts)
 import build_current_sidekick_body as builder
 import current_sidekick_body_compatibility as compat
 assert compat.MF_IDS==MF_IDS and compat.MF_SELECTION==MF_SELECTION
 assert compat.MF_ROOT==MF_ROOT and compat.MF_MAPPING==MF_MAPPING
 loaded=compat.mf_load(root)
 raw=builder.read(root,MF_SELECTION);selected=json.loads(raw)
 assert set(selected)=={'schema','version','resources'} and selected['schema']=='opentyrian-current-mint-front-body-authoring-v1','unapproved Mint/Front selection contract'
 assert isinstance(selected['version'],str) and 1<=len(selected['version'])<=128,'invalid Mint/Front version'
 assert isinstance(selected['resources'],list) and len(selected['resources'])==4,'unapproved Mint/Front source count'
 expected_destinations={'assets/gameplay/'+name for name in MF_NAMES}
 assert set(loaded)==expected_destinations,'unapproved Mint/Front consumer scope'
 outputs={MF_SELECTION:{'sha256':sha(raw),'mode':'100644'}};rows=[];sources={}
 runtime=json.loads(builder.read(root,builder.RUNTIME))
 runtime['files']=_before_sonic_runtime(runtime['files'],root,_proofs=_proofs)
 runtime_rows={r['destination']:r for r in runtime['files']}
 assert len(runtime_rows)==len(runtime['files'])==1025,'unexpected current runtime destination scope'
 for identity,name,record in zip(MF_IDS,MF_NAMES,selected['resources']):
  assert set(record)=={'identity','source_png','source_sha256'} and type(record['identity']) is int and record['identity']==identity,'unapproved Mint/Front identity/fields/order'
  source_png=record['source_png']
  assert isinstance(source_png,str) and source_png.startswith('authoring-inputs/') and source_png.endswith('.png') and source_png not in sources,'Mint/Front requires four independent authoring inputs'
  png=builder.read(root,source_png)
  assert sha(png)==record['source_sha256'],'current Mint/Front selected PNG mismatch'
  w,h=(24,28) if identity==1280083 else (12,14)
  with Image.open(io.BytesIO(png)) as image:
   assert image.format=='PNG' and image.mode=='RGBA' and image.size==(w*8,h*8) and getattr(image,'n_frames',1)==1,'current Mint/Front PNG geometry mismatch'
   blob=struct.pack('<4s6I',b'HDR1',identity,8,w,h,0,0)+image.tobytes()
  source=MF_ROOT+'/'+name;destination='assets/gameplay/'+name
  assert builder.read(root,source)==blob,('current Mint/Front PNG/HDA mismatch',identity)
  row=dict(identity=identity,source_path=source,destination=destination,sha256=sha(blob))
  assert loaded[destination]==row,('current Mint/Front compatibility mismatch',identity)
  rows.append(row);sources[source_png]=record['source_sha256']
  oid=hashlib.sha1(b'blob '+str(len(blob)).encode()+b'\0'+blob).hexdigest()
  expected=dict(source_path=source,destination=destination,group='gameplay',revision='current-single-source-mint-front-body',bytes=len(blob),git_blob=oid,sha256=sha(blob))
  assert runtime_rows.get(destination)==expected,('stale current Mint/Front runtime body',destination)
  outputs[source]={'sha256':sha(blob),'mode':'100644'}
 expected=dict(schema='opentyrian-current-mint-front-body-compatibility-v1',selection=MF_SELECTION,version=selected['version'],files=rows)
 assert builder.read(root,MF_MAPPING)==builder.encoded(expected),'current Mint/Front selection/mapping mismatch'
 assert len(outputs)==5 and len(sources)==4,'unapproved Mint/Front asset scope'
 return dict(assets=outputs,source_pngs=sources)

def project_craft267_readme(current,root,ledger):
 """Undo exactly the reviewed complete README blob and its single line hunk."""
 edit=ledger['craft267_readme_inverse']
 assert edit['path']==CRAFT267_README and edit['mode']=='100644' and edit['after_lines']==[21,22],'unapproved craft267 README inverse scope'
 assert current.get(CRAFT267_README)=={'sha256':edit['current_sha256'],'mode':'100644'},'unapproved craft267 README inventory'
 raw=(root/CRAFT267_README).read_bytes()
 assert sha(raw)==edit['current_sha256'],'unapproved craft267 README blob'
 lines=raw.splitlines(keepends=True);a,b=edit['after_lines']
 assert b''.join(lines[a:b])==edit['after'].encode(),'craft267 README inverse hunk drift'
 lines[a:b]=edit['before'].encode().splitlines(keepends=True)
 restored=b''.join(lines)
 assert sha(restored)==edit['previous_sha256'],'craft267 README historical result drift'
 row={'sha256':sha(restored),'mode':'100644'}
 assert row==ledger['asset_edits'][CRAFT267_README]['after'],'craft267 README original ledger mismatch'
 current[CRAFT267_README]=row


def parse_git_asset_modes(raw):
 modes={}
 for record in raw.split(b'\0'):
  if not record:continue
  metadata,path=record.split(b'\t',1);mode,oid,stage=metadata.decode().split();name=path.decode('utf-8')
  assert stage=='0' and mode in ('100644','100755'),('unsupported Git asset entry',name,mode,stage)
  assert name.startswith('assets/') and name not in modes,('invalid/duplicate Git asset path',name)
  modes[name]=mode
 return modes

def git_asset_modes(root):
 # Current index only: no private historical Git objects and no cached mode verdicts.
 top=subprocess.check_output(['git','-C',str(root),'rev-parse','--show-toplevel']).decode().strip()
 assert Path(top).resolve()==Path(root).resolve(),'asset inventory requires the repository root'
 return parse_git_asset_modes(subprocess.check_output(['git','-C',str(root),'ls-files','--stage','-z','--','assets']))

def asset_file_mode(path,name,modes,windows=None):
 assert name in modes,('asset absent from Git index',name)
 mode=modes[name];assert mode in ('100644','100755'),('unsupported Git asset mode',name,mode)
 if windows is None:windows=os.name=='nt'
 if not windows:
  assert ('100755' if path.stat().st_mode&0o111 else '100644')==mode,('working-tree/Git mode mismatch',name)
 return mode

def current_asset_inventory(root=ROOT):
 assert not (root/'assets').is_symlink(),'asset root symlink'
 modes=git_asset_modes(root);current={}
 for p in (root/'assets').rglob('*'):
  assert not p.is_symlink(),('asset symlink',str(p))
  if p.is_file() and p.relative_to(root).as_posix()!='assets/hd/manifest.json':
   name=p.relative_to(root).as_posix()
   current[name]={'sha256':sha(p.read_bytes()),'mode':asset_file_mode(p,name,modes)}
 assert set(current)==set(modes)-{'assets/hd/manifest.json'},'Git/working asset path mismatch'
 return current
def project_p9_catalog(catalog):
 ledger=load('p9-assets.json');digest=sha(canonical(catalog))
 # The old oracle also checks an already-projected catalogue for idempotence.
 if digest==ledger['catalog_before_sha256']:return copy.deepcopy(catalog)
 # Later family projections call us with an older catalog after P9 removal.
 if 'player_rear_multicannon_p9_mode2_rotations_v1' not in catalog:
  assert digest==ledger['catalog_no_p9_sha256'],'unapproved family-free catalog'
  return copy.deepcopy(catalog)
 assert digest==ledger['catalog_after_sha256'],'unapproved later catalog bytes'
 result=copy.deepcopy(catalog)
 for edit in reversed(ledger['catalog_edits']):
  obj=result
  for key in edit['path'][:-1]:obj=obj[key]
  key=edit['path'][-1]
  if edit.get('after_exists',True):assert key in obj and obj[key]==edit['after'],edit['path']
  else:assert key not in obj,edit['path']
  if edit.get('before_exists',True):obj[key]=copy.deepcopy(edit['before'])
  else:del obj[key]
 assert sha(canonical(result))==ledger['catalog_before_sha256'],'nonexact historical catalog result'
 original=load('p9-stage-catalog.json')
 assert result==original
 return original # Preserve the historical JSON member order, also covered by the old byte digest.

def project_p9_asset_inventory(root):
 """Check every later path against a finite published ledger; return old hashes.

Original feature inventory digests still verify every unchanged historical path.
Retired paths are explicitly absent, never a prefix/wildcard exclusion.
 """
 validate_current_catalog(json.loads((root/'assets/hd/manifest.json').read_text()))
 return project_p9_inventory(current_asset_inventory(root),root)

def project_p9_inventory(current,root=ROOT):
 from _projection_proof_context import _ProjectionProofContext
 context=_ProjectionProofContext(root,ROOT)
 try:
  result=_project_p9_inventory(current,root,_proofs=context)
  context.finish()
  return result
 finally:
  context.close()

def _project_p9_inventory(current,root=ROOT, *, _proofs):
 current=copy.deepcopy(current)
 for name,row in _current_projection_proof('rear_lobes',root,_proofs)['assets'].items():
  assert current.get(name)==row,('unverified current Rear lobes output',name)
  del current[name]
 for name,row in _current_projection_proof('rear281',root,_proofs)['assets'].items():
  assert current.get(name)==row,('unverified current Rear281 output',name)
  del current[name]
 for name,row in _current_projection_proof('rear39',root,_proofs)['assets'].items():
  assert current.get(name)==row,('unverified current Rear39 output',name)
  del current[name]
 for name,row in _current_projection_proof('rear1',root,_proofs)['assets'].items():
  assert current.get(name)==row,('unverified current Rear1 output',name)
  del current[name]
 for name,row in _current_projection_proof('rear_p7',root,_proofs)['assets'].items():
  assert current.pop(name)==row,('unverified current Rear P7 output',name)
 for name,row in _current_projection_proof('missile',root,_proofs)['assets'].items():
  assert current.pop(name)==row,('unverified current Missile output',name)
 for name,row in _current_projection_proof('mint27',root,_proofs)['assets'].items():
  assert current.pop(name)==row,('unverified current Mint27 output',name)
 for name,row in _current_projection_proof('newshf',root,_proofs)['assets'].items():
  assert current.pop(name)==row,('unverified current NEWSHF output',name)
 for name,row in _current_projection_proof('guided',root,_proofs)['assets'].items():
  assert current.pop(name)==row,('unverified current Guided output',name)
 for name,row in _current_projection_proof('sonic',root,_proofs)['assets'].items():
  assert current.pop(name)==row,('unverified current Sonic output',name)
 for name,row in _current_projection_proof('protron',root,_proofs)['assets'].items():
  assert current.pop(name)==row,('unverified current Protron output',name)
 for name,row in verified_protron_current(root)['assets'].items():
  assert current.get(name)==row,('unverified P09 current output',name)
  del current[name]
 newshf=_verified_newshf_current(root,_proofs=_proofs)['assets']
 assert set(newshf)=={NEWSHF_MANIFEST}|{NEWSHF_ROOT+'/'+name for name in NEWSHF_NAMES},'unapproved NEWSHF output scope'
 for name,row in newshf.items():
  assert row['mode']=='100644' and current.get(name)==row,('unverified NEWSHF current output',name)
  del current[name]
 ledger=load('p9-assets.json')
 orb=_verified_enemy_orb_current(root,_proofs=_proofs)['assets']
 assert set(orb)=={ORB_SELECTION}|{ORB_ROOT+'/'+name for name in ORB_NAMES} and len(orb)==5,'unapproved orb output scope'
 for name,row in orb.items():
  assert row['mode']=='100644' and current.get(name)==row,('unverified orb current output',name)
  del current[name]
 front_multi=_verified_front_multi_current(root,_proofs=_proofs)['assets']
 assert set(front_multi)=={FRONT_MULTI_SELECTION}|{FRONT_MULTI_ROOT+'/'+name for name in FRONT_MULTI_NAMES} and len(front_multi)==9,'unapproved Front Multi output scope'
 for name,row in front_multi.items():
  assert row['mode']=='100644' and current.get(name)==row,('unverified Front Multi current output',name)
  del current[name]
 plasma=_verified_plasma_projectile_current(root,_proofs=_proofs)['assets']
 assert set(plasma)=={PLASMA_SELECTION}|{PLASMA_ROOT+'/'+name for name in PLASMA_NAMES} and len(plasma)==7,'unapproved Plasma projectile output scope'
 for name,row in plasma.items():
  assert row['mode']=='100644' and current.get(name)==row,('unverified Plasma projectile current output',name)
  del current[name]
 mint_front=_verified_mint_front_current(root,_proofs=_proofs)['assets']
 assert set(mint_front)=={MF_SELECTION}|{MF_ROOT+'/'+name for name in MF_NAMES} and len(mint_front)==5,'unapproved Mint/Front output scope'
 for name,row in mint_front.items():
  assert row['mode']=='100644' and current.get(name)==row,('unverified Mint/Front current output',name)
  del current[name]
 charge=_verified_charge_current(root,_proofs=_proofs)['assets']
 assert set(charge)=={CHARGE_SELECTION}|{CHARGE_ROOT+'/'+name for name in CHARGE_NAMES} and len(charge)==10,'unapproved Charge output scope'
 for name,row in charge.items():
  assert row['mode']=='100644' and current.get(name)==row,('unverified Charge current output',name)
  del current[name]
 verified=_verified_sidekick_current(root,_proofs=_proofs);craft=_verified_craft267_current(root,_proofs=_proofs)
 proof=dict(verified['assets']);assert not set(proof)&set(craft['assets']),'current output collision'
 proof.update(craft['assets']);reviewed=ledger['verified_current_outputs']
 assert set(proof)==set(reviewed) and len(proof)==9,'unapproved current output scope'
 for name,row in proof.items():
  assert reviewed[name]['mode']=='100644' and row['mode']=='100644',('unapproved current output mode',name)
  assert current.get(name)==row,('unverified current output',name)
  del current[name]
 sources=dict(verified['source_pngs']);sources.update(craft['source_pngs'])
 for name,digest in sources.items():
  if name.startswith('assets/'):
   assert current.get(name)=={'sha256':digest,'mode':'100644'},('current PNG absent from asset inventory',name)
 project_craft267_readme(current,root,ledger)
 # The complete original current set and hashes stay at the old pinned digest.
 assert sha(canonical(current))==ledger['current_inventory_sha256'],'unapproved current asset inventory'
 for name,edit in ledger['asset_edits'].items():
  assert current.get(name)==edit['after'],('unapproved later asset',name)
  if edit['before'] is None:current.pop(name)
  else:current[name]=edit['before']
 return {name:row['sha256'] for name,row in current.items()}

PINS['current-source-inventory.json']='2eb0ccfa979da5fe7808a449887011f8ad4fd793dc80ed0a13079080ad360a9a'
def validate_current_sources(root=ROOT):
 ledger=load('current-source-inventory.json')
 assert not any(p.is_symlink() for p in (root/'src').rglob('*')),'source symlink rejected'
 actual={p.relative_to(root).as_posix():sha(p.read_bytes()) for p in (root/'src').rglob('*') if p.is_file() and p.suffix in ledger['extensions']}
 expected=load('current-source-inventory.json')['files']
 added=verified_newshf_identity_sources(root)
 compositor=verified_newshf_compositor_sources(root)
 reuse=verified_enemy_reuse_sources(root)
 observe=verified_enemy_observe_sources(root)
 probe=verified_enemy_probe_sources(root)
 assert set(actual)==set(expected)|{PLASMA_HEADER,FRONT_MULTI_HEADER,ORB_HEADER,NEWSHF_HEADER,PROTRON_HEADER,CURRENT_PROTRON_HEADER,CURRENT_SONIC_HEADER,CURRENT_GUIDED_HEADER,CURRENT_NEWSHF_HEADER,CURRENT_MINT27_HEADER,CURRENT_MISSILE_HEADER,CURRENT_REAR_P7_HEADER}|set(added)|set(compositor)|set(reuse)|set(observe)|set(probe),'unapproved current source paths'
 projected=dict(actual)
 assert projected.pop(CURRENT_REAR_P7_HEADER)==verified_current_rear_p7(root)['header_sha256']
 assert projected.pop(CURRENT_MISSILE_HEADER)==verified_current_missile(root)['header_sha256']
 assert projected.pop(CURRENT_MINT27_HEADER)==verified_current_mint27(root)['header_sha256']
 assert projected.pop(CURRENT_NEWSHF_HEADER)==verified_current_newshf(root)['header_sha256']
 assert projected.pop(CURRENT_GUIDED_HEADER)==verified_current_guided(root)['header_sha256']
 assert projected.pop(CURRENT_SONIC_HEADER)==verified_current_sonic(root)['header_sha256']
 assert projected.pop(CURRENT_PROTRON_HEADER)==verified_current_protron(root)['header_sha256']
 for name,digest in probe.items():
  assert projected.pop(name)==digest,('unapproved controlled probe source',name)
 for name,digest in observe.items():
  assert projected.pop(name)==digest,('unapproved observer source',name)
 assert projected.pop(PROTRON_HEADER)==verified_protron_current(root)['header_sha256']
 for name,digest in reuse.items():
  assert projected.pop(name)==digest,('unapproved enemy reuse module',name)
 for name,digest in compositor.items():
  assert projected.pop(name)==digest,('unapproved NEWSHF compositor source',name)
 for name in corrected_source_paths():
  projected[name]=sha(project_source('render-boundaries',name,(root/name).read_bytes()))
 for name,digest in added.items():
  assert projected.pop(name)==digest,('unapproved NEWSHF prototype source',name)
 assert {p:h for p,h in projected.items() if p not in (SIDEKICK_HEADER,PLASMA_HEADER,FRONT_MULTI_HEADER,ORB_HEADER,NEWSHF_HEADER)}=={p:h for p,h in expected.items() if p not in (SIDEKICK_HEADER,PLASMA_HEADER,FRONT_MULTI_HEADER,ORB_HEADER,NEWSHF_HEADER)},'unapproved non-target source bytes'
 # Keep every source path. Only the finite named generated headers are derived
 # from their exact current proofs; executable bytes use the pinned inverse.
 expected=dict(expected);expected[SIDEKICK_HEADER]=verified_sidekick_current(root)['header_sha256']
 expected[PLASMA_HEADER]=verified_plasma_projectile_current(root)['header_sha256']
 expected[FRONT_MULTI_HEADER]=verified_front_multi_current(root)['header_sha256']
 expected[ORB_HEADER]=verified_enemy_orb_current(root)['header_sha256']
 expected[NEWSHF_HEADER]=verified_newshf_current(root)['header_sha256']
 assert projected==expected,'unapproved current source inventory (added, removed or modified source)'

def validate_source_inventory(actual):
 assert actual==load('current-source-inventory.json')['files'],'unapproved current source inventory (added, removed or modified source)'

def validate_current_catalog(catalog):
 assert sha(canonical(catalog))==load('p9-assets.json')['catalog_after_sha256'],'unapproved live catalog (including historical reversion)'

def _current_projection_proof(family,root,context):
 validators={
  'guided':verified_current_guided,
  'mint27':verified_current_mint27,
  'missile':verified_current_missile,
  'newshf':verified_current_newshf,
  'protron':verified_current_protron,
  'rear_lobes':verified_current_rear_lobes,
  'rear281':verified_current_rear281,
  'rear1':verified_current_rear1,
  'rear39':verified_current_rear39,
  'rear_p7':verified_current_rear_p7,
  'sonic':verified_current_sonic,
 }
 validator=validators[family]
 if context is None:return validator(root)
 if Path(root).absolute()!=context.root:
  context.close()
  raise ValueError('projection proof context root mismatch')
 return context.get(family,validator)

