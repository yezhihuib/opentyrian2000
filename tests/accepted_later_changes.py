"""Fail-closed inverses of named, already published later changes.

The original feature oracle and its old digests are not rebased. Each inverse
first verifies the entire accepted current blob, then every finite hunk, then
the old blob. The one generated sidekick header and seven current asset outputs
require a fresh exact current-generation proof before their finite projection.
All other source bytes and the historical asset inventory remain fixed.
The reviewed render-boundary correction has its own exact two-file inverse;
current source bindings keep its real bytes, while older oracles see their
original source through that explicit projection.
"""
from pathlib import Path
import copy, hashlib, json, os, subprocess, sys
ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT/'tests/fixtures/accepted-later-changes-v1'
PINS = {
 'data-source.json': '3bfbfea80342efbf8ad53e38957260fcdf674db5a57c732f3702e502324cc011',
 'rear-p1-source.json': '2f8fed7183dcf1087b93cc7bceb79ac189ac0209835f8108c8aa0cdc0b931ff3',
 'storm-source.json': '188f57d604004af08ec191cc6bddf2b7d07ea65b1f60348073f7e0263f8783a1',
 'render-boundaries-source.json': '1bac028508e047cb862989d08ef7613b46652c6aea32c71d8bcbc6c78ff9ac30',
}
def sha(raw): return hashlib.sha256(raw).hexdigest()
def load(name):
 raw=(FIXTURES/name).read_bytes()
 assert sha(raw)==PINS[name], ('changed accepted-history ledger',name)
 return json.loads(raw)
def project_source(label,name,raw):
 # Only this fixed reviewed correction is undone before the older feature's
 # inverse. Whole current blob, every hunk and whole previous blob stay pinned.
 if label!='render-boundaries':raw=project_source('render-boundaries',name,raw)
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
PINS['p9-assets.json']='636a4f71bbd1210f261093023e61ab021eed602ac7ec324b1d7e281213ae3bf1'
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
 assert verify(root,binding)==252,'unexpected current production source scope'
 expected_sources=dict(load('current-source-inventory.json')['files'])
 expected_sources[SIDEKICK_HEADER]=sha(header);expected_sources.update(PRODUCTION_NON_CODE)
 for name,pin in load('render-boundaries-source.json')['files'].items():
  raw=builder.read(root,name)
  assert sha(project_source('render-boundaries',name,raw))==expected_sources[name],('render correction historical source mismatch',name)
  expected_sources[name]=sha(raw)
 assert binding['source_sha256']==expected_sources,'unapproved non-target production source binding'
 runtime=json.loads(builder.read(root,builder.RUNTIME));runtime_rows={r['destination']:r for r in runtime['files']}
 assert len(runtime_rows)==len(runtime['files'])==1006,'unexpected current runtime destination scope'
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
 current=copy.deepcopy(current)
 ledger=load('p9-assets.json')
 verified=verified_sidekick_current(root);proof=verified['assets'];reviewed=ledger['verified_current_outputs']
 assert set(proof)==set(reviewed) and len(proof)==7,'unapproved current output scope'
 for name,row in proof.items():
  assert reviewed[name]['mode']=='100644' and row['mode']=='100644',('unapproved current output mode',name)
  assert current.get(name)==row,('unverified current output',name)
  del current[name]
 for name,digest in verified['source_pngs'].items():
  if name.startswith('assets/'):
   assert current.get(name)=={'sha256':digest,'mode':'100644'},('current PNG absent from asset inventory',name)
 # The complete pre-sidekick current set and hashes stay at the old pinned digest.
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
 assert set(actual)==set(expected),'unapproved current source paths'
 projected=dict(actual)
 for name in load('render-boundaries-source.json')['files']:
  projected[name]=sha(project_source('render-boundaries',name,(root/name).read_bytes()))
 assert {p:h for p,h in projected.items() if p!=SIDEKICK_HEADER}=={p:h for p,h in expected.items() if p!=SIDEKICK_HEADER},'unapproved non-target source bytes'
 # Keep every source path. Only this one generated value is derived from the
 # same strict current proof used before the seven-path asset projection.
 expected=dict(expected);expected[SIDEKICK_HEADER]=verified_sidekick_current(root)['header_sha256']
 assert projected==expected,'unapproved current source inventory (added, removed or modified source)'

def validate_source_inventory(actual):
 assert actual==load('current-source-inventory.json')['files'],'unapproved current source inventory (added, removed or modified source)'

def validate_current_catalog(catalog):
 assert sha(canonical(catalog))==load('p9-assets.json')['catalog_after_sha256'],'unapproved live catalog (including historical reversion)'
