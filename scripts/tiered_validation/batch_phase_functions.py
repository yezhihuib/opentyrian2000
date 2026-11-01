"""New current-state-only contract, NOT the historical four-phase proof.

No historical inverse projection or exhaustive SHOP mutations run here.
Source bytes/modes/membership are bound by an independently approved deployment
profile. Packaging uses the original default current manifest, never overrides.
"""
from pathlib import Path
import contextlib,hashlib,io,json,sys,unittest,inspect

def configure(source_root):
 global root
 root=Path(source_root)

def _execute(root,profile,production_verify,package_main):
 if root.resolve()!=profile.root:raise ValueError('Current phase profile root mismatch')
 profile.verify_full(root)
 catalog_path='assets/hd/manifest.json'
 raw=(root/catalog_path).read_bytes()
 if hashlib.sha256(raw).hexdigest()!=profile.data['worktree'][catalog_path]['sha256']:raise ValueError('Current catalog bytes changed')
 catalog=json.loads(raw)
 if catalog.get('schema')!='opentyrian-accepted-hd-runtime-v1':raise ValueError('Current HD catalog schema mismatch')
 receipt=json.loads((root/'packaging/current-production-validation.json').read_bytes())
 source_files=production_verify(root,receipt)
 manifest_raw=(root/'packaging/runtime-assets-v1.json').read_bytes()
 manifest=json.loads(manifest_raw)
 if hashlib.sha256(manifest_raw).hexdigest()!=profile.data['worktree']['packaging/runtime-assets-v1.json']['sha256']:raise ValueError('Current packaging manifest changed')
 output=io.StringIO();entered=set();previous=sys.getprofile()
 def trace(frame,event,arg):
  if event=='call':
   module=frame.f_globals.get('__name__','');name=frame.f_code.co_name
   if module.startswith('current_') and name in ('load','validate_runtime_rows'):entered.add(module+'.'+name)
 if previous is not None:raise ValueError('Unexpected profiler in current-state phase')
 try:
  sys.setprofile(trace)
  with contextlib.redirect_stdout(output):
   result=package_main(['--source-root',str(root),'--platform','linux'])
 finally:sys.setprofile(previous)
 if result!=0:raise ValueError('Current default packaging dry-run failed: '+str(result))
 report=json.loads(output.getvalue())
 if report.get('schema')!='opentyrian-runtime-preflight-v1' or report.get('mode')!='dry-run' or report.get('assets_complete') is not True or report.get('source_unchanged') is not True or report.get('missing')!=[]:raise ValueError('Incomplete current packaging report')
 if report['verified_files']!=report['expected_files'] or report['expected_files']!=len(manifest['files']):raise ValueError('Current package selection incompletely verified')
 if report.get('verified_payload_bytes')!=report.get('expected_payload_bytes') or report.get('expected_payload_bytes')!=sum(row['bytes'] for row in manifest['files']):raise ValueError('Current package payload count mismatch')
 if report.get('executable_included') is not False or report.get('platform')!='linux':raise ValueError('Unexpected packaging scope')
 # The independent full map guards absent/extra assets, all bytes and modes,
 # not merely the subset selected by the runtime manifest.
 profile.verify_full(root)
 return dict(contract='current-state-once/v1',source_files=source_files,catalog_sha256=hashlib.sha256(raw).hexdigest(),
  source_asset_members=sum(n.startswith(('src/','assets/')) for n in profile.data['worktree']),
  package_report=report,packaging_manifest_sha256=hashlib.sha256(manifest_raw).hexdigest(),producer_calls_entered=sorted(entered),historical_inverse_projection=False,exhaustive_shop_mutations=False,
  coverage='CURRENT_BYTES_MODES_MEMBERSHIP_PRODUCTION_BINDING_DEFAULT_RUNTIME_SELECTION_ONLY')

def current_state_once():
 from deployment_profile import PROFILE
 from verify_current_production import verify
 from package_runtime import main
 result=_execute(root,PROFILE,verify,main)
 result['additional_static_shop_guards']=run_additional_shop(root)
 PROFILE.verify_full(root)
 return result


ADDITIONAL_METHODS=(
 'test_current_replay_masks_and_bounds',
 'test_semantic_guard_mutations_rejected_without_hash_gate',
 'test_current_compile_inventory',
)

def run_additional_shop(source_root):
 import test_shop_current_acceptance as shop_tests
 if Path(shop_tests.__file__).resolve()!=source_root/'tests/test_shop_current_acceptance.py' or shop_tests.ROOT.resolve()!=source_root:raise ValueError('Wrong SHOP guard source')
 cases=[shop_tests.ShopCurrentAcceptance(name) for name in ADDITIONAL_METHODS]
 ids=[case.id() for case in cases]
 provenance=[dict(id=case.id(),method_source_sha256=hashlib.sha256(inspect.getsource(getattr(type(case),case._testMethodName)).encode()).hexdigest()) for case in cases]
 class Result(unittest.TextTestResult):
  def __init__(self,*a,**kw):super().__init__(*a,**kw);self.started=[];self.successful=[]
  def startTest(self,test):self.started.append(test.id());return super().startTest(test)
  def addSuccess(self,test):self.successful.append(test.id());return super().addSuccess(test)
 result=unittest.TextTestRunner(stream=sys.stderr,verbosity=2,resultclass=Result).run(unittest.TestSuite(cases))
 if result.started!=ids or result.successful!=ids or result.testsRun!=3 or not result.wasSuccessful() or result.skipped or result.expectedFailures or result.unexpectedSuccesses:raise ValueError('Additional static SHOP guards failed or skipped')
 return dict(scope='ADDITIONAL_STATIC_GUARDS_NOT_VISUAL_OR_RUNTIME_ACCEPTANCE',started_test_ids=result.started,successful_test_ids=result.successful,method_provenance=provenance)
