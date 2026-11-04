"""Finite actual-byte extra epoch checks. No producer/native/game run.

TANK194_EXTRA_EPOCH_ROOT supplies a small current335 fixture. Optional
TANK194_V1_TEST_ROOT supplies an actual frozen public331 fixture for old-v1
positives; TANK194_EXTRA_V1_TEST_ROOT supplies actual frozen public332 inputs.
TANK194_POSES15_17_V1_TEST_ROOT supplies the actual frozen333 dependency,
which was unpublished when this epoch was prepared. No earlier receipt is synthesized
or passed to the new authority. TANK194_POSE89_V1_TEST_ROOT supplies the actual
frozen334 unpublished dependency. TANK194_POSE13_V1_TEST_ROOT supplies
the actual frozen335 pose13 dependency. Current topclip retains all eight material
contracts, including deliberate13 adaptation, but binds a different335-source epoch.
"""
from pathlib import Path
import copy,json,os,shutil,sys,tempfile,unittest
from unittest.mock import patch
ROOT=Path(os.environ.get('TANK194_EXTRA_EPOCH_ROOT',Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import current_tank194_source_bridge as B
import current_tank194_body_registration as OLD
import current_tank194_energy_authority as ENERGY
from verify_current_production import BUILD_INPUTS,source_manifest_digest

class ExtraEpoch(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.p=B.topclip_proof(ROOT);cls.previous=B.pose13_proof(ROOT)
  names=set(cls.p['source_sha256'])|B.topclip_input_paths(ROOT)|set(BUILD_INPUTS)|{B.BINDING,B.RUNTIME,'packaging/frontend-validation.json','packaging/global-validation.json'}
  names|={r['source_path']for r in cls.p['body_alias_rows']}
  names|={row['source_png']for row in ENERGY.APPROVED_SELECTION['resources']}
  cls.raw={n:OLD.regular(ROOT,n,4*1024*1024)for n in names}
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  for n,b in self.raw.items():self.put(n,b)
  self.manifest=json.loads(self.raw[B.RUNTIME])
 def put(self,n,b):
  p=self.root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
 def test_topclip_core_and_retained_header_each_raw_byte_required(self):
  for n in (self.p['core_path'],self.previous['extra_header_path']):
   with self.subTest(path=n):
    self.put(n,self.raw[n]+b'\n')
    with self.assertRaises(ValueError):B.project_topclip_sources(self.root)
    self.put(n,self.raw[n])
 def test_prior_epochs_reject_topclip335_and1139_without_fallback(self):
  with self.assertRaisesRegex(ValueError,'production epoch'):B.project_sources(self.root)
  with self.assertRaisesRegex(ValueError,'row count'):B.project_runtime_rows(self.root,self.manifest)
  with self.assertRaisesRegex(ValueError,'production epoch'):B.project_extra_sources(self.root)
  with self.assertRaises(ValueError):B.project_extra_runtime_rows(self.root,self.manifest)
  with self.assertRaisesRegex(ValueError,'production epoch'):B.project_poses15_17_sources(self.root)
  with self.assertRaises(ValueError):B.project_poses15_17_runtime_rows(self.root,self.manifest)
  with self.assertRaisesRegex(ValueError,'production epoch'):B.project_pose89_sources(self.root)
  with self.assertRaises(ValueError):B.project_pose89_runtime_rows(self.root,self.manifest)
  self.assertEqual(len(self.p['source_sha256']),335);self.assertEqual(len(self.previous['source_sha256']),335)
  self.assertNotEqual(self.p['source_sha256'],self.previous['source_sha256'])
  with self.assertRaisesRegex(ValueError,'production epoch'):B.project_pose13_sources(self.root)
  with self.assertRaises(ValueError):B.project_pose13_runtime_rows(self.root,self.manifest)
  with patch.object(ENERGY,'checked_source')as checked:
   with self.assertRaisesRegex(ValueError,'production epoch'):ENERGY.verify(self.root,copy.deepcopy(ENERGY.APPROVED_SELECTION))
   checked.assert_not_called()
   with self.assertRaisesRegex(ValueError,'production epoch'):ENERGY.verify_extra(self.root,copy.deepcopy(ENERGY.APPROVED_SELECTION))
   checked.assert_not_called()
   with self.assertRaisesRegex(ValueError,'production epoch'):ENERGY.verify_poses15_17(self.root,copy.deepcopy(ENERGY.APPROVED_SELECTION))
   checked.assert_not_called()
   with self.assertRaisesRegex(ValueError,'production epoch'):ENERGY.verify_pose89(self.root,copy.deepcopy(ENERGY.APPROVED_SELECTION))
   checked.assert_not_called()
   with self.assertRaisesRegex(ValueError,'production epoch'):ENERGY.verify_pose13(self.root,copy.deepcopy(ENERGY.APPROVED_SELECTION))
   checked.assert_not_called()
 def test_topclip_previous_descriptor_and_retained_material_are_raw_pinned(self):
  for n in (B.TOPCLIP_PROOF,B.POSE13_PROOF,self.previous['extra_material_proof_path']):
   self.put(n,self.raw[n]+b'\n')
   with self.assertRaises(ValueError):B.project_topclip_runtime_rows(self.root,self.manifest)
   self.put(n,self.raw[n])
 def test_all_eight_alias_payloads_required_before_removal(self):
  for row in self.p['body_alias_rows']:
   n=row['source_path'];raw=self.raw[n];self.put(n,raw[:30]+bytes([raw[30]^1])+raw[31:])
   with self.subTest(identity=row['identity']),self.assertRaises(ValueError):B.project_topclip_runtime_rows(self.root,self.manifest)
   self.put(n,raw)
 def test_projection_keeps_actual335_binding_and_old1130_rows(self):
  sources,_=B.project_topclip_sources(self.root);self.assertEqual(len(sources),329)
  result=B.project_topclip_runtime_rows(self.root,self.manifest)
  self.assertEqual(len(result),1131)
  binding=next(r for r in result if r['source_path']==B.BINDING)
  self.assertEqual(binding,next(r for r in self.manifest['files']if r['source_path']==B.BINDING))
  self.assertEqual(json.loads((self.root/B.BINDING).read_bytes())['source_sha256'],self.p['source_sha256'])
  fixed=[r for r in result if r['source_path']!=B.BINDING]
  self.assertEqual(source_manifest_digest(fixed),B.proof(self.root)['projected_nonbinding_rows_sha256'])
  self.assertEqual((self.root/B.BINDING).read_bytes(),self.raw[B.BINDING])
 def test_missing_retained_alias_or_false_closure_never_uses_prior_epoch(self):
  bad=copy.deepcopy(self.manifest);bad['files']=[r for r in bad['files']if r not in self.previous['extra_alias_rows']]
  with self.assertRaises(ValueError):B.project_topclip_runtime_rows(self.root,bad)
  for value in (None,True,2,3,4,5,6,7,9):
   bad=copy.deepcopy(self.manifest);bad['closure']['global_tank194_body_alias_files']=value
   with self.assertRaises(ValueError):B.project_topclip_runtime_rows(self.root,bad)
 def test_topclip_mode_dispatch_is_explicit_and_no_generation(self):
  import build_current_tank_shell as builder
  class Reached(Exception):pass
  self.put(builder.SELECTION,json.dumps(ENERGY.APPROVED_SELECTION).encode())
  with patch.object(builder,'source_blob',side_effect=AssertionError('No generation')),patch.object(ENERGY,'verify',side_effect=AssertionError('No v1 fallback')),patch.object(ENERGY,'verify_pose13',side_effect=AssertionError('No prior335 fallback')),patch.object(ENERGY,'verify_topclip',side_effect=Reached)as guard:
   with self.assertRaises(Reached):builder.derive(self.root,json.dumps(ENERGY.APPROVED_SELECTION).encode(),B.TOPCLIP_MODE)
   guard.assert_called_once()
 def test_actual_frozen_public331_v1_still_positive(self):
  name=os.environ.get('TANK194_V1_TEST_ROOT')
  if not name:self.skipTest('Set TANK194_V1_TEST_ROOT to actual frozen public331 inputs')
  root=Path(name);sources,_=B.project_sources(root)
  self.assertEqual(len(sources),329)
  rows=B.project_runtime_rows(root,json.loads((root/B.RUNTIME).read_bytes()));self.assertEqual(len(rows),1131)
  with patch.object(ENERGY,'checked_source')as checked:
   ENERGY.verify(root,copy.deepcopy(ENERGY.APPROVED_SELECTION));self.assertEqual(checked.call_count,1126)
  with self.assertRaises((ValueError,OSError)):B.project_topclip_sources(root)

 def test_actual_frozen_public332_extra_v1_still_positive(self):
  name=os.environ.get('TANK194_EXTRA_V1_TEST_ROOT')
  if not name:self.skipTest('Set TANK194_EXTRA_V1_TEST_ROOT to actual frozen public332 inputs')
  root=Path(name);sources,_=B.project_extra_sources(root)
  self.assertEqual(len(sources),329)
  rows=B.project_extra_runtime_rows(root,json.loads((root/B.RUNTIME).read_bytes()));self.assertEqual(len(rows),1131)
  with patch.object(ENERGY,'checked_source')as checked:
   ENERGY.verify_extra(root,copy.deepcopy(ENERGY.APPROVED_SELECTION));self.assertEqual(checked.call_count,1126)
  with self.assertRaises(ValueError):B.project_sources(root)
  with self.assertRaises((ValueError,OSError)):B.project_topclip_sources(root)

 def test_actual_frozen_unpublished333_poses15_17_v1_still_positive(self):
  name=os.environ.get('TANK194_POSES15_17_V1_TEST_ROOT')
  if not name:self.skipTest('Set TANK194_POSES15_17_V1_TEST_ROOT to actual frozen333 dependency inputs')
  root=Path(name);sources,_=B.project_poses15_17_sources(root)
  self.assertEqual(len(sources),329)
  rows=B.project_poses15_17_runtime_rows(root,json.loads((root/B.RUNTIME).read_bytes()));self.assertEqual(len(rows),1131)
  with patch.object(ENERGY,'checked_source')as checked:
   ENERGY.verify_poses15_17(root,copy.deepcopy(ENERGY.APPROVED_SELECTION));self.assertEqual(checked.call_count,1126)
  for project in (B.project_sources,B.project_extra_sources):
   with self.assertRaises(ValueError):project(root)
  with self.assertRaises((ValueError,OSError)):B.project_topclip_sources(root)

 def test_actual_frozen_unpublished334_pose89_v1_still_positive(self):
  name=os.environ.get('TANK194_POSE89_V1_TEST_ROOT')
  if not name:self.skipTest('Set TANK194_POSE89_V1_TEST_ROOT to actual frozen334 dependency inputs')
  root=Path(name);sources,_=B.project_pose89_sources(root)
  self.assertEqual(len(sources),329)
  rows=B.project_pose89_runtime_rows(root,json.loads((root/B.RUNTIME).read_bytes()));self.assertEqual(len(rows),1131)
  with patch.object(ENERGY,'checked_source')as checked:
   ENERGY.verify_pose89(root,copy.deepcopy(ENERGY.APPROVED_SELECTION));self.assertEqual(checked.call_count,1126)
  for project in (B.project_sources,B.project_extra_sources,B.project_poses15_17_sources):
   with self.assertRaises(ValueError):project(root)
  with self.assertRaises((ValueError,OSError)):B.project_topclip_sources(root)

 def test_actual_frozen_unpublished335_pose13_v1_still_positive(self):
  name=os.environ.get('TANK194_POSE13_V1_TEST_ROOT')
  if not name:self.skipTest('Set TANK194_POSE13_V1_TEST_ROOT to actual frozen335 pose13 inputs')
  root=Path(name);sources,_=B.project_pose13_sources(root)
  self.assertEqual(len(sources),329)
  receipt=json.loads((root/B.BINDING).read_bytes())
  self.assertEqual(len(receipt['source_sha256']),335)
  self.assertEqual(receipt['production_source_manifest_sha256'],B.POSE13_CURRENT_DIGEST)
  self.assertNotEqual(receipt['production_source_manifest_sha256'],B.TOPCLIP_CURRENT_DIGEST)
  rows=B.project_pose13_runtime_rows(root,json.loads((root/B.RUNTIME).read_bytes()));self.assertEqual(len(rows),1131)
  with patch.object(ENERGY,'checked_source')as checked:
   ENERGY.verify_pose13(root,copy.deepcopy(ENERGY.APPROVED_SELECTION));self.assertEqual(checked.call_count,1126)
  with self.assertRaises((ValueError,OSError)):B.project_topclip_sources(root)

if __name__=='__main__':unittest.main(verbosity=2)
