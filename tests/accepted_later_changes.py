"""Fail-closed inverses of named, already published later changes.

The original feature oracle and its old digests are not rebased. Each inverse
first verifies the entire accepted current blob, then every finite hunk, then
the old blob. The two generated payload headers and thirty-one fixed current asset outputs
require a fresh exact current-generation proof before their finite projection.
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
 'charge-body-source.json': 'c066932af771eb3a834c7becbeb59c6b0eac668d8da51df09d034d7247211e92',
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

def project_source(label,name,raw):
 # Newest first; generated payload values never relax executable source bytes.
 raw=_project_source_once('plasma-projectile',name,raw)
 if label=='plasma-projectile':return raw
 raw=_project_source_once('charge-body',name,raw)
 if label=='charge-body':return raw
 raw=_project_source_once('render-boundaries',name,raw)
 if label=='render-boundaries':return raw
 return _project_source_once(label,name,raw)

def corrected_source_paths():
 return sorted(set(load('plasma-projectile-source.json')['files'])|set(load('charge-body-source.json')['files'])|set(load('render-boundaries-source.json')['files']))

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
 assert verify(root,binding)==253,'unexpected current production source scope'
 expected_sources=dict(load('current-source-inventory.json')['files'])
 expected_sources[SIDEKICK_HEADER]=sha(header);expected_sources.update(PRODUCTION_NON_CODE)
 expected_sources[PLASMA_HEADER]=verified_plasma_projectile_current(root)['header_sha256']
 for name in corrected_source_paths():
  raw=builder.read(root,name)
  assert sha(project_source('render-boundaries',name,raw))==expected_sources[name],('reviewed correction historical source mismatch',name)
  expected_sources[name]=sha(raw)
 assert binding['source_sha256']==expected_sources,'unapproved non-target production source binding'
 runtime=json.loads(builder.read(root,builder.RUNTIME));runtime_rows={r['destination']:r for r in runtime['files']}
 assert len(runtime_rows)==len(runtime['files'])==1015,'unexpected current runtime destination scope'
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

PLASMA_SELECTION='assets/hd/authoring/plasma-projectile-current.json'
PLASMA_ROOT='assets/hd/current-compat/plasma-projectile'
PLASMA_HEADER='src/current_plasma_projectile_payload_pins.h'
PLASMA_MAPPING='packaging/current-plasma-projectile-compatibility.json'
PLASMA_PAIRS=tuple((identity,density) for identity in (1300022,1300023,1300024) for density in (4,8))
PLASMA_NAMES=tuple('option-plasma-projectile-%d-%d.hda'%(identity-1300000,density) for identity,density in PLASMA_PAIRS)

def verified_plasma_projectile_current(root=ROOT):
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
 runtime_rows={r['destination']:r for r in runtime['files']}
 assert len(runtime_rows)==len(runtime['files'])==1015,'unexpected current runtime destination scope'
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

CRAFT267_SELECTION='assets/hd/authoring/craft267-current.json'
CRAFT267_CANONICAL='assets/hd/current-compat/craft267/enemy-newsh2-267-8.hda'
CRAFT267_DESTINATION='assets/gameplay/enemy-newsh2-267-8.hda'
CRAFT267_README='assets/hd/README.md'

def verified_craft267_current(root=ROOT):
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
 runtime=builder.parse(builder.read(root,builder.RUNTIME));rows={r['destination']:r for r in runtime['files']}
 assert len(rows)==len(runtime['files'])==1015,'unexpected current runtime destination scope'
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
 runtime=json.loads(builder.read(root,builder.RUNTIME));rows={r['destination']:r for r in runtime['files']}
 assert len(rows)==len(runtime['files'])==1015,'unexpected current runtime destination scope'
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
 runtime=json.loads(builder.read(root,builder.RUNTIME));runtime_rows={r['destination']:r for r in runtime['files']}
 assert len(runtime_rows)==len(runtime['files'])==1015,'unexpected current runtime destination scope'
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
 current=copy.deepcopy(current)
 ledger=load('p9-assets.json')
 plasma=verified_plasma_projectile_current(root)['assets']
 assert set(plasma)=={PLASMA_SELECTION}|{PLASMA_ROOT+'/'+name for name in PLASMA_NAMES} and len(plasma)==7,'unapproved Plasma projectile output scope'
 for name,row in plasma.items():
  assert row['mode']=='100644' and current.get(name)==row,('unverified Plasma projectile current output',name)
  del current[name]
 mint_front=verified_mint_front_current(root)['assets']
 assert set(mint_front)=={MF_SELECTION}|{MF_ROOT+'/'+name for name in MF_NAMES} and len(mint_front)==5,'unapproved Mint/Front output scope'
 for name,row in mint_front.items():
  assert row['mode']=='100644' and current.get(name)==row,('unverified Mint/Front current output',name)
  del current[name]
 charge=verified_charge_current(root)['assets']
 assert set(charge)=={CHARGE_SELECTION}|{CHARGE_ROOT+'/'+name for name in CHARGE_NAMES} and len(charge)==10,'unapproved Charge output scope'
 for name,row in charge.items():
  assert row['mode']=='100644' and current.get(name)==row,('unverified Charge current output',name)
  del current[name]
 verified=verified_sidekick_current(root);craft=verified_craft267_current(root)
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
 assert set(actual)==set(expected)|{PLASMA_HEADER},'unapproved current source paths'
 projected=dict(actual)
 for name in corrected_source_paths():
  projected[name]=sha(project_source('render-boundaries',name,(root/name).read_bytes()))
 assert {p:h for p,h in projected.items() if p not in (SIDEKICK_HEADER,PLASMA_HEADER)}=={p:h for p,h in expected.items() if p not in (SIDEKICK_HEADER,PLASMA_HEADER)},'unapproved non-target source bytes'
 # Keep every source path. Only the two named generated headers are derived
 # from their exact current proofs; executable bytes use the pinned inverse.
 expected=dict(expected);expected[SIDEKICK_HEADER]=verified_sidekick_current(root)['header_sha256']
 expected[PLASMA_HEADER]=verified_plasma_projectile_current(root)['header_sha256']
 assert projected==expected,'unapproved current source inventory (added, removed or modified source)'

def validate_source_inventory(actual):
 assert actual==load('current-source-inventory.json')['files'],'unapproved current source inventory (added, removed or modified source)'

def validate_current_catalog(catalog):
 assert sha(canonical(catalog))==load('p9-assets.json')['catalog_after_sha256'],'unapproved live catalog (including historical reversion)'
