"""Finite actual-byte extra epoch checks. No producer/native/game run.

TANK194_EXTRA_EPOCH_ROOT supplies a small current332 fixture. Optional
TANK194_V1_TEST_ROOT supplies an actual frozen public331 fixture for old-v1
positives; its receipt is never synthesized or passed to the new authority.
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
  cls.p=B.extra_proof(ROOT)
  names=set(cls.p['source_sha256'])|B.extra_input_paths(ROOT)|set(BUILD_INPUTS)|{B.BINDING,B.RUNTIME,'packaging/frontend-validation.json','packaging/global-validation.json'}
  names|={r['source_path']for r in cls.p['body_alias_rows']}
  names|={row['source_png']for row in ENERGY.APPROVED_SELECTION['resources']}
  cls.raw={n:OLD.regular(ROOT,n,4*1024*1024)for n in names}
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  for n,b in self.raw.items():self.put(n,b)
  self.manifest=json.loads(self.raw[B.RUNTIME])
 def put(self,n,b):
  p=self.root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
 def test_extra_core_and_header_each_raw_byte_required(self):
  for n in (self.p['core_path'],self.p['extra_header_path']):
   with self.subTest(path=n):
    self.put(n,self.raw[n]+b'\n')
    with self.assertRaises(ValueError):B.project_extra_sources(self.root)
    self.put(n,self.raw[n])
 def test_v1_rejects_actual332_and1135_without_fallback(self):
  with self.assertRaisesRegex(ValueError,'production epoch'):B.project_sources(self.root)
  with self.assertRaisesRegex(ValueError,'row count'):B.project_runtime_rows(self.root,self.manifest)
  with patch.object(ENERGY,'checked_source')as checked:
   with self.assertRaisesRegex(ValueError,'production epoch'):ENERGY.verify(self.root,copy.deepcopy(ENERGY.APPROVED_SELECTION))
   checked.assert_not_called()
 def test_extra_descriptor_and_material_proof_are_raw_pinned(self):
  for n in (B.EXTRA_PROOF,self.p['extra_material_proof_path']):
   self.put(n,self.raw[n]+b'\n')
   with self.assertRaises(ValueError):B.project_extra_runtime_rows(self.root,self.manifest)
   self.put(n,self.raw[n])
 def test_all_four_alias_payloads_required_before_removal(self):
  for row in self.p['body_alias_rows']:
   n=row['source_path'];raw=self.raw[n];self.put(n,raw[:30]+bytes([raw[30]^1])+raw[31:])
   with self.subTest(identity=row['identity']),self.assertRaises(ValueError):B.project_extra_runtime_rows(self.root,self.manifest)
   self.put(n,raw)
 def test_projection_keeps_actual332_binding_and_old1130_rows(self):
  result=B.project_extra_runtime_rows(self.root,self.manifest)
  self.assertEqual(len(result),1131)
  binding=next(r for r in result if r['source_path']==B.BINDING)
  self.assertEqual(binding,next(r for r in self.manifest['files']if r['source_path']==B.BINDING))
  self.assertEqual(json.loads((self.root/B.BINDING).read_bytes())['source_sha256'],self.p['source_sha256'])
  fixed=[r for r in result if r['source_path']!=B.BINDING]
  self.assertEqual(source_manifest_digest(fixed),B.proof(self.root)['projected_nonbinding_rows_sha256'])
  self.assertEqual((self.root/B.BINDING).read_bytes(),self.raw[B.BINDING])
 def test_missing_extra_pair_or_false_closure_never_uses_v1(self):
  bad=copy.deepcopy(self.manifest);bad['files']=[r for r in bad['files']if r not in self.p['extra_alias_rows']]
  with self.assertRaises(ValueError):B.project_extra_runtime_rows(self.root,bad)
  for value in (None,True,2,3,5):
   bad=copy.deepcopy(self.manifest);bad['closure']['global_tank194_body_alias_files']=value
   with self.assertRaises(ValueError):B.project_extra_runtime_rows(self.root,bad)
 def test_extra_mode_dispatch_is_explicit_and_no_generation(self):
  import build_current_tank_shell as builder
  class Reached(Exception):pass
  self.put(builder.SELECTION,json.dumps(ENERGY.APPROVED_SELECTION).encode())
  with patch.object(builder,'source_blob',side_effect=AssertionError('No generation')),patch.object(ENERGY,'verify',side_effect=AssertionError('No v1 fallback')),patch.object(ENERGY,'verify_extra',side_effect=Reached)as guard:
   with self.assertRaises(Reached):builder.derive(self.root,json.dumps(ENERGY.APPROVED_SELECTION).encode(),B.EXTRA_MODE)
   guard.assert_called_once()
 def test_actual_frozen_public331_v1_still_positive(self):
  name=os.environ.get('TANK194_V1_TEST_ROOT')
  if not name:self.skipTest('Set TANK194_V1_TEST_ROOT to actual frozen public331 inputs')
  root=Path(name);sources,_=B.project_sources(root)
  self.assertEqual(len(sources),329)
  rows=B.project_runtime_rows(root,json.loads((root/B.RUNTIME).read_bytes()));self.assertEqual(len(rows),1131)
  with patch.object(ENERGY,'checked_source')as checked:
   ENERGY.verify(root,copy.deepcopy(ENERGY.APPROVED_SELECTION));self.assertEqual(checked.call_count,1126)
  with self.assertRaises((ValueError,OSError)):B.project_extra_sources(root)

if __name__=='__main__':unittest.main(verbosity=2)
