"""Finite two-PNG authoring/authority units; never full derive/build/native/game.
PNG fixtures are the two checked-in selected inputs. Only ~0.3 MiB is copied to a
private TemporaryDirectory. Authority units read actual source/registry/build/runtime inputs once, then
mutate actual finite source/metadata copies. All digests and authority readers
remain real. Only unrelated checked_source calls are spies, not160MB asset reads.
"""
import copy,hashlib,io,json,struct,sys,tempfile,unittest
from contextlib import ExitStack,contextmanager
from pathlib import Path
from unittest import mock
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import build_current_tank_shell as builder
import current_tank_shell_compatibility as compatibility
import current_enemy_tank_shared_aliases as aliases
import current_tank194_energy_authority as authority
import current_tank_energy_authority as legacy_authority
import current_tank194_source_bridge as body_bridge
import current_tank194_body_registration as body_registration
import current_tank_muzzle_source_bridge as muzzle_bridge
import current_warning_source_bridge as warning_bridge

def digest(raw):return hashlib.sha256(raw).hexdigest()
def encode(value):return (json.dumps(value,sort_keys=True,indent=2)+'\n').encode()
def independent_fnv(raw):
 value=0xcbf29ce484222325
 for byte in raw:value=((value^byte)*0x100000001b3)&0xffffffffffffffff
 return '%016x'%value

class GuardReached(RuntimeError):pass

class TankEnergyAuthoringTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  # Caller may supply a small actual-byte repository fixture via ROOT; no
  # machine-specific paths or historical Git objects are required.
  cls.authority_sources=authority.source_inventory(ROOT)
  body_proof=body_bridge.pose89_proof(ROOT)
  names={authority.REGISTRY,authority.RUNTIME,authority.BINDING,*authority.BUILD_INPUTS,*cls.authority_sources,
         'packaging/frontend-validation.json','packaging/global-validation.json'}
  names|=body_bridge.pose89_input_paths(ROOT)|{row['source_path']for row in body_proof['body_alias_rows']}
  cls.authority_raw={name:authority.read(ROOT,name)for name in names}
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(prefix='tank-energy-unit-');self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
  self.selected=copy.deepcopy(authority.APPROVED_SELECTION);self.blobs={};self.mapping=[];self.pins={};self.hashes={}
  for row in self.selected['resources']:
   raw=(ROOT/row['source_png']).read_bytes();self.assertEqual(digest(raw),row['source_sha256']);self.put(row['source_png'],raw)
   blob,payload=builder.source_blob(self.root,row);identity=row['identity'];self.blobs[identity]=blob;self.pins[identity]=independent_fnv(payload);self.hashes[identity]=digest(blob)
   self.assertEqual(self.hashes[identity],authority.APPROVED_HDA[identity-1220000]);source=compatibility.ROOT+'/'+compatibility.name(identity)
   self.put(source,blob);self.put(aliases.PREFIX+self.hashes[identity]+'.hda',blob)
   self.mapping.append(dict(identity=identity,source_path=source,destination='assets/gameplay/'+compatibility.name(identity),sha256=self.hashes[identity]))
  self.put(compatibility.SELECTION,encode(self.selected));self.put(compatibility.MAPPING,encode(dict(schema='opentyrian-current-tank-shell-compatibility-v1',selection=compatibility.SELECTION,version=self.selected['version'],files=self.mapping)))
  self.put(compatibility.HEADER,compatibility.payload_header(self.pins,self.hashes))
  # Only dispatch-to-authority tests read this tiny placeholder registry. They
  # deliberately stop at the mocked historical/current guard, before derive.
  self.registry={'resources':[]};self.put(builder.REGISTRY,encode(self.registry))
 def put(self,path,raw):
  p=self.root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
 def runtime_rows(self):
  manual=[{k:v for k,v in row.items()if k!='identity'}for row in self.mapping]
  return {'files':manual+aliases.rows_for(self.root)}
 @contextmanager
 def no_build(self):
  with mock.patch.object(builder.subprocess,'run',side_effect=AssertionError('No build allowed'))as run, mock.patch.object(builder.subprocess,'Popen',side_effect=AssertionError('No process allowed')):
   yield run

 def test_selected_png_exact_canonical_alias_and_pins(self):
  loaded=compatibility.load(self.root);generated=aliases.generate(self.root);self.assertEqual(len(loaded),2);self.assertEqual(len(generated),2)
  for row in self.selected['resources']:
   identity=row['identity'];png=(self.root/row['source_png']).read_bytes()
   with Image.open(io.BytesIO(png))as im:
    self.assertEqual((im.format,im.mode,im.size),('PNG','RGBA',(96,112)));pixels=im.tobytes()
   expected=b'HDR1'+struct.pack('<6I',identity,8,12,14,0,0)+pixels
   source=compatibility.ROOT+'/'+compatibility.name(identity);self.assertEqual((self.root/source).read_bytes(),expected);self.assertEqual(self.blobs[identity],expected)
   self.assertEqual(generated[aliases.PREFIX+digest(expected)+'.hda'],expected);self.assertEqual(digest(expected),authority.APPROVED_HDA[identity-1220000]);self.assertEqual(compatibility.fnv(expected[28:]),independent_fnv(pixels));self.assertNotEqual(compatibility.fnv(expected),compatibility.fnv(expected[28:]))
  self.assertEqual(len(aliases.load(self.root)),2);aliases.validate_runtime_rows(self.root,self.runtime_rows(),required=True)
 def test_energy_sha_header_and_historical_without_png_contract(self):
  # Both explicit energy mapping versions retain strict PNG origin and SHA pins.
  for version in ('approved-tank-energy-pulse-v2','approved-tank-energy-pulse-v3'):
   selected=copy.deepcopy(self.selected);selected['version']=version
   mapping=dict(schema='opentyrian-current-tank-shell-compatibility-v1',selection=compatibility.SELECTION,version=version,files=self.mapping)
   self.put(compatibility.SELECTION,encode(selected));self.put(compatibility.MAPPING,encode(mapping));self.put(compatibility.HEADER,compatibility.payload_header(self.pins,self.hashes))
   self.assertEqual(len(compatibility.load(self.root)),2)
   self.put(compatibility.HEADER,compatibility.payload_header(self.pins))
   with self.assertRaisesRegex(ValueError,'payload pins'):compatibility.load(self.root)
  mapping=json.loads((self.root/compatibility.MAPPING).read_bytes());mapping['version']='approved-tank-energy-pulse-v999';self.put(compatibility.MAPPING,encode(mapping));self.put(compatibility.HEADER,compatibility.payload_header(self.pins,self.hashes))
  with self.assertRaisesRegex(ValueError,'payload pins'):compatibility.load(self.root)
  # Legal synthetic historical HDA/map/header fixture, not a claim that these
  # new pixels are old artwork. Historical contract requires no PNG authority.
  mapping['version']='approved-tank-shell-pair-v1';self.put(compatibility.MAPPING,encode(mapping));self.put(compatibility.HEADER,compatibility.payload_header(self.pins))
  (self.root/compatibility.SELECTION).unlink()
  for row in self.selected['resources']:(self.root/row['source_png']).unlink()
  with mock.patch.object(builder,'selection',side_effect=AssertionError('Historical PNG lookup forbidden')),mock.patch.object(builder,'source_blob',side_effect=AssertionError('Historical PNG decode forbidden')):
   self.assertEqual(len(compatibility.load(self.root)),2)
 def test_self_consistent_hda_map_header_tamper_still_rejects_png_mismatch(self):
  identity=compatibility.IDS[0];bad=bytearray(self.blobs[identity]);bad[128]^=1;bad=bytes(bad)
  self.put(self.mapping[0]['source_path'],bad);self.mapping[0]['sha256']=digest(bad);self.pins[identity]=independent_fnv(bad[28:]);self.hashes[identity]=digest(bad)
  self.put(compatibility.MAPPING,encode(dict(schema='opentyrian-current-tank-shell-compatibility-v1',selection=compatibility.SELECTION,version=self.selected['version'],files=self.mapping)));self.put(compatibility.HEADER,compatibility.payload_header(self.pins,self.hashes));self.put(aliases.PREFIX+digest(bad)+'.hda',bad)
  for version in ('approved-tank-energy-pulse-v2','approved-tank-energy-pulse-v3'):
   selected=copy.deepcopy(self.selected);selected['version']=version;self.put(compatibility.SELECTION,encode(selected))
   self.put(compatibility.MAPPING,encode(dict(schema='opentyrian-current-tank-shell-compatibility-v1',selection=compatibility.SELECTION,version=version,files=self.mapping)))
   with self.assertRaisesRegex(ValueError,'selected PNG'):compatibility.load(self.root)
   with self.assertRaisesRegex(ValueError,'selected PNG'):aliases.generate(self.root)
 def test_selection_source_hash_change_is_rejected(self):
  changed=copy.deepcopy(self.selected);changed['resources'][0]['source_sha256']='0'*64;self.put(compatibility.SELECTION,encode(changed))
  with self.assertRaisesRegex(ValueError,'source changed'):builder.selection(self.root,encode(changed))
  with self.assertRaisesRegex(ValueError,'source changed'):compatibility.load(self.root)
 def test_alias_metadata_mutations_fail_closed(self):
  base=self.runtime_rows()
  for field,value in [('identity',True),('density',True),('identity',80146),('density',4),('encoding','indexed'),('revision','unknown'),('canonical_source','other'),('bytes',1),('git_blob','0'*40),('destination','assets/global/wrong.hda')]:
   with self.subTest(field=field,value=value):
    rows=copy.deepcopy(base);rows['files'][-1][field]=value
    with self.assertRaises(ValueError):aliases.validate_runtime_rows(self.root,rows,required=True)
 def test_duplicate_and_obsolete_alias_collision_are_rejected(self):
  rows=self.runtime_rows();rows['files'].append(copy.deepcopy(rows['files'][-1]))
  with self.assertRaisesRegex(ValueError,'exactly two'):aliases.validate_runtime_rows(self.root,rows,required=True)
  # Exact role header at an obsolete filename is still an identity collision;
  # this synthetic collision is not a claim about historical artwork bytes.
  old=authority.OLD_ALIASES[0];self.put(old,self.blobs[compatibility.IDS[0]]);rows=self.runtime_rows();rows['files'].append(dict(source_path=old,destination='assets/global/obsolete.hda',sha256=digest(self.blobs[compatibility.IDS[0]])))
  with self.assertRaisesRegex(ValueError,'exactly two'):aliases.validate_runtime_rows(self.root,rows,required=True)
  with self.assertRaisesRegex(ValueError,'deletion refused'):authority.obsolete(self.root)
  # Tiny current-byte fixture tests the identity/name association independently
  # of any historical hash spelling. All full hashes and headers stay real.
  names=tuple(aliases.PREFIX+self.hashes[i]+'.hda'for i in compatibility.IDS)
  with mock.patch.object(authority,'OLD_ALIASES',names):self.assertEqual(authority.obsolete(self.root),list(names))
  with mock.patch.object(authority,'OLD_ALIASES',names[::-1]):
   with self.assertRaisesRegex(ValueError,'deletion refused'):authority.obsolete(self.root)
 def test_manual_consumer_identity_cannot_hide_alias_metadata(self):
  rows=self.runtime_rows();rows['files'][0]['identity']=1220146
  with self.assertRaisesRegex(ValueError,'manual identity collision'):aliases.validate_runtime_rows(self.root,rows,required=True)
 def test_unknown_authority_does_not_fall_back(self):
  with self.no_build()as run,mock.patch.object(builder,'verify_authority',side_effect=AssertionError('Historical fallback forbidden')):
   for mode in ('automatic','current-tank-energy-v2'):
    with self.assertRaisesRegex(ValueError,'Unknown Tank authority'):builder.derive(self.root,encode(self.selected),authority=mode)
   run.assert_not_called()
 def test_historical_default_and_explicit_route_reach_original_guard(self):
  with self.no_build()as run,mock.patch.object(builder,'verify_authority',side_effect=GuardReached('historical'))as guard,mock.patch.object(authority,'verify_pose89',side_effect=AssertionError('Current fallback forbidden')):
   for kw in({},dict(authority='historical')):
    with self.assertRaisesRegex(GuardReached,'historical'):builder.derive(self.root,encode(self.selected),**kw)
   self.assertEqual(guard.call_count,2);guard.assert_called_with(self.root,self.registry);run.assert_not_called()
 def test_explicit_current_route_reaches_current_guard_only(self):
  with self.no_build()as run,mock.patch.object(builder,'verify_authority',side_effect=AssertionError('Historical guard forbidden')),mock.patch.object(authority,'verify_pose89',side_effect=GuardReached('current'))as guard:
   with self.assertRaisesRegex(GuardReached,'current'):builder.derive(self.root,encode(self.selected),authority=body_bridge.POSE89_MODE)
   guard.assert_called_once_with(self.root,self.selected);run.assert_not_called()

 @contextmanager
 def authority_unit(self,mutation=None):
  """Real current334 bytes and guards; only unrelated asset reads are spies."""
  raw=copy.deepcopy(self.authority_raw)
  if mutation=='source':raw[next(name for name in self.authority_sources if name!=compatibility.HEADER)]+=b'\n'
  elif mutation=='muzzle_bytes':raw[next(iter(muzzle_bridge.MUZZLE_PINS))]+=b'\n'
  elif mutation=='mixed_epoch':raw[next(iter(body_bridge.proof(ROOT)['new_source_sha256']))]+=b'\n'
  elif mutation=='registry':raw[authority.REGISTRY]+=b' changed'
  elif mutation=='build':raw[authority.BUILD_INPUTS[0]]+=b' changed'
  elif mutation=='runtime':
   runtime=json.loads(raw[authority.RUNTIME]);mutable=set(authority.CANONICAL)|set(authority.OLD_ALIASES)|set(authority.NEW_ALIASES)|{authority.BINDING}
   row=next(row for row in runtime['files']if row['source_path']not in mutable and row.get('revision')!=body_registration.REVISION)
   row['destination']='assets/unreviewed.bin';raw[authority.RUNTIME]=encode(runtime)
  for name,data in raw.items():self.put(name,data)
  with mock.patch.object(body_bridge,'source_inventory',wraps=body_bridge.source_inventory)as inventory,mock.patch.object(authority,'checked_source')as checked:
   yield inventory,checked
 def test_fixed_authority_unit_valid_checks_all_unrelated_rows(self):
  with self.authority_unit()as(inventory,checked):
   authority.verify_pose89(self.root,copy.deepcopy(self.selected));inventory.assert_called_once_with(self.root);self.assertEqual(checked.call_count,1126)
 def test_fixed_source_authority_mutation_rejected(self):
  with self.authority_unit('source')as(_,checked):
   with self.assertRaisesRegex(ValueError,'production epoch'):authority.verify_pose89(self.root,self.selected)
   checked.assert_not_called()
  with self.authority_unit()as(inventory,_):
   selected=copy.deepcopy(self.selected);selected['version']='unreviewed'
   with self.assertRaisesRegex(ValueError,'Unreviewed Tank energy selection'):authority.verify_pose89(self.root,selected)
   inventory.assert_not_called()
 def test_fixed_registry_authority_mutation_rejected(self):
  with self.authority_unit('registry')as(_,checked):
   with self.assertRaisesRegex(ValueError,'registry changed'):authority.verify_pose89(self.root,self.selected)
   checked.assert_not_called()
 def test_fixed_build_authority_mutation_rejected(self):
  with self.authority_unit('build')as(_,checked):
   with self.assertRaisesRegex(ValueError,'Build inputs changed'):authority.verify_pose89(self.root,self.selected)
   checked.assert_not_called()
 def test_fixed_runtime_rows_authority_mutation_rejected(self):
  with self.authority_unit('runtime')as(_,checked):
   with self.assertRaisesRegex(ValueError,'runtime row changed'):authority.verify_pose89(self.root,self.selected)
   checked.assert_not_called()

 def test_registered_epoch_actual_six_bytes_mutation_rejected(self):
  with self.authority_unit('muzzle_bytes')as(_,checked):
   with self.assertRaisesRegex(ValueError,'production epoch'):authority.verify_pose89(self.root,self.selected)
   checked.assert_not_called()
  # The stage/apply plan binds the newly imported authority bridge as bytes,
  # not merely as an available script in the staging directory.
  import current_sidekick_body_compatibility as sidekick
  names=('scripts/build_current_tank_shell.py','scripts/current_tank_shell_compatibility.py','scripts/current_tank_energy_authority.py','scripts/current_enemy_tank_shared_aliases.py','scripts/current_tank_muzzle_source_bridge.py','scripts/current_warning_source_bridge.py','scripts/current_tank194_source_bridge.py','scripts/current_tank194_energy_authority.py','scripts/current_tank194_body_registration.py','scripts/current_tank194_extra_registration.py','scripts/current_tank194_poses15_17_registration.py','scripts/current_tank194_pose89_registration.py')
  for name in names:self.put(name,(ROOT/name).read_bytes())
  for bridge_name in names[-6:]:
   with mock.patch.object(sidekick,'authoring_input_fingerprints',side_effect=lambda root:{}):
    plan=builder.make_plan(self.root,{},encode(self.selected),body_bridge.POSE89_MODE)
    self.assertEqual(plan['inputs_sha256'][bridge_name],digest((self.root/bridge_name).read_bytes()))
    original=(self.root/bridge_name).read_bytes();self.put(bridge_name,original+b'\n')
    changed=builder.make_plan(self.root,{},encode(self.selected),body_bridge.POSE89_MODE)
    self.assertNotEqual(plan['inputs_sha256'][bridge_name],changed['inputs_sha256'][bridge_name])
    self.put(bridge_name,original)
 def test_mixed_epoch_rejected_and_historical_digest_branch_unchanged(self):
  with self.authority_unit('mixed_epoch')as(_,checked):
   with self.assertRaisesRegex(ValueError,'production epoch'):authority.verify_pose89(self.root,self.selected)
   checked.assert_not_called()
  # Old v3 must reject actual current334. Its historical branch still accepts
  # only the exact bytes produced by the reviewed body -> warning -> muzzle inverses.
  with self.authority_unit():
   with self.assertRaisesRegex(ValueError,'production epoch'):legacy_authority.verify(self.root,self.selected)
   rows=body_bridge.project_pose89_runtime_rows(self.root,json.loads((self.root/authority.RUNTIME).read_bytes()))
   sources,restored=body_bridge.project_pose89_sources(self.root);del sources[compatibility.HEADER]
   warn_sources,warn_raw=warning_bridge.project(sources,lambda n:restored[n]if n in restored else(self.root/n).read_bytes())
   all_restored=dict(restored);all_restored.update(warn_raw)
   for name in muzzle_bridge.MUZZLE_PINS:
    raw=all_restored[name]if name in all_restored else(self.root/name).read_bytes()
    all_restored[name]=muzzle_bridge.restore(name,raw.decode()).encode()
   for name,raw in all_restored.items():self.put(name,raw)
   for name in list(body_bridge.proof(ROOT)['new_source_sha256'])+[body_bridge.extra_proof(ROOT)['extra_header_path'],body_bridge.poses15_17_proof(ROOT)['extra_header_path'],body_bridge.pose89_proof(ROOT)['extra_header_path']]:(self.root/name).unlink()
   runtime=json.loads((self.root/authority.RUNTIME).read_bytes());runtime['files']=rows;self.put(authority.RUNTIME,encode(runtime))
   with mock.patch.object(legacy_authority,'checked_source')as checked,mock.patch.object(muzzle_bridge,'project',side_effect=AssertionError('Historical branch must not project')):
    legacy_authority.verify(self.root,self.selected);self.assertEqual(checked.call_count,1126)

 def test_old_v3_dispatch_remains_explicit_and_separate(self):
  with self.no_build()as run,mock.patch.object(builder,'verify_authority',side_effect=AssertionError('Historical fallback forbidden')),mock.patch.object(authority,'verify_pose89',side_effect=AssertionError('Body fallback forbidden')),mock.patch.object(legacy_authority,'verify',side_effect=GuardReached('old-v3'))as guard:
   with self.assertRaisesRegex(GuardReached,'old-v3'):builder.derive(self.root,encode(self.selected),authority=legacy_authority.MODE)
   guard.assert_called_once_with(self.root,self.selected);run.assert_not_called()

if __name__=='__main__':unittest.main(verbosity=2)
