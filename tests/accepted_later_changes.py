"""Fail-closed inverses of named, already published later changes.

The original feature oracle and its old digests are not rebased. Each inverse
first verifies the *entire* accepted current blob, then every finite hunk, then
the old blob. A future legitimate source change requires a reviewed new ledger.
No unknown byte, path, or wildcard is exempted by this historical projection.
"""
from pathlib import Path
import copy, hashlib, json
ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT/'tests/fixtures/accepted-later-changes-v1'
PINS = {
 'data-source.json': '3bfbfea80342efbf8ad53e38957260fcdf674db5a57c732f3702e502324cc011',
 'rear-p1-source.json': '2f8fed7183dcf1087b93cc7bceb79ac189ac0209835f8108c8aa0cdc0b931ff3',
 'storm-source.json': '188f57d604004af08ec191cc6bddf2b7d07ea65b1f60348073f7e0263f8783a1',
}
def sha(raw): return hashlib.sha256(raw).hexdigest()
def load(name):
 raw=(FIXTURES/name).read_bytes()
 assert sha(raw)==PINS[name], ('changed accepted-history ledger',name)
 return json.loads(raw)
def project_source(label,name,raw):
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

PINS['p9-stage-catalog.json']='565303b7f5b4f2cf726214a61e2f95148f4ed0ba816a81939ad6bc4c2b62d4d3'
PINS['p9-assets.json']='b9517fdb740cb265799870947654f96a19c77c2b946fb807835e969ea535d77f'
def canonical(obj):return json.dumps(obj,sort_keys=True,separators=(',',':')).encode()
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
 current={}
 for p in (root/'assets').rglob('*'):
  assert not p.is_symlink(),('asset symlink',str(p))
  if p.is_file() and p.relative_to(root).as_posix()!='assets/hd/manifest.json':
   current[p.relative_to(root).as_posix()]={'sha256':sha(p.read_bytes()),'mode':'100755' if p.stat().st_mode&0o111 else '100644'}
 return project_p9_inventory(current)

def project_p9_inventory(current):
 current=copy.deepcopy(current)
 ledger=load('p9-assets.json')
 assert sha(canonical(current))==ledger['current_inventory_sha256'],'unapproved current asset inventory'
 for name,edit in ledger['asset_edits'].items():
  assert current.get(name)==edit['after'],('unapproved later asset',name)
  if edit['before'] is None:current.pop(name)
  else:current[name]=edit['before']
 return {name:row['sha256'] for name,row in current.items()}

PINS['current-source-inventory.json']='2a30fb3cb89ae39b8537c3a34717c3e414c4891ee8a41185ac61bb2844a7c6a5'
def validate_current_sources(root=ROOT):
 ledger=load('current-source-inventory.json')
 assert not any(p.is_symlink() for p in (root/'src').rglob('*')),'source symlink rejected'
 actual={p.relative_to(root).as_posix():sha(p.read_bytes()) for p in (root/'src').rglob('*') if p.is_file() and p.suffix in ledger['extensions']}
 validate_source_inventory(actual)

def validate_source_inventory(actual):
 assert actual==load('current-source-inventory.json')['files'],'unapproved current source inventory (added, removed or modified source)'

def validate_current_catalog(catalog):
 assert sha(canonical(catalog))==load('p9-assets.json')['catalog_after_sha256'],'unapproved live catalog (including historical reversion)'
