from pathlib import Path
import copy,json,tempfile,unittest
import tiered_selection as t
import prepare_profile as prepare
import run_validation as run

def fixture():
 full={'ordered_test_ids':['new.C.test_a','old.C.test_b'],'original_provenance_sha256':'fixture','segments':[{'index':0,'kind':'phase','name':'global','call':'binding','test_ids':[]},{'index':1,'kind':'module','name':'new','slice':[0,1],'test_ids':['new.C.test_a']},{'index':2,'kind':'module','name':'old','slice':[1,2],'test_ids':['old.C.test_b']}]}
 p={'schema':'reviewed-batch-selection/v1','source_binding':{'commit':'explicit-reviewed-example'},'impact_review':{'status':'REVIEWED_EXPLICIT_SELECTION','justification':'Explicit fixture partition; no inferred dependency.'},'policy':{'automatic_full_run':False,'failure_fallback':False,'unknown_binding':'STOP_FULL_REQUIRED_OR_REVIEWED_PROFILE'},'required_segments':['global','new'],'deferred_segments':['old'],'deferral_reasons':{'old':{'reason':'Fixture','coverage_not_exercised':'old negative probes','full_triggers':['old input change']}},'new_test_ids':['new.C.test_a']}
 p=prepare.prepare(full,p,Path(__file__));return full,p
class Toolkit(unittest.TestCase):
 def test_prepare_never_approves(self):
  f,p=fixture();self.assertEqual(p['impact_review']['status'],'DRAFT_REQUIRES_INDEPENDENT_REVIEW')
  with self.assertRaises(t.FullRequired):t.select(f,p,t.digest(p),p['source_binding'])
 def test_reviewed_partition_and_explicit_full(self):
  f,p=fixture();p['impact_review']['status']='REVIEWED_EXPLICIT_SELECTION'
  self.assertEqual(t.select(f,p,t.digest(p),p['source_binding'])['ordered_test_ids'],['new.C.test_a'])
  self.assertEqual(t.select(f,p,t.digest(p),p['source_binding'],'full')['ordered_test_ids'],f['ordered_test_ids'])
 def test_unknown_input_never_full(self):
  f,p=fixture();p['impact_review']['status']='REVIEWED_EXPLICIT_SELECTION'
  with self.assertRaises(t.FullRequired):t.select(f,p,t.digest(p),{'commit':'changed'})
 def test_unknown_partition_refused(self):
  f,p=fixture();p['deferred_segments']=['*']
  with self.assertRaises(t.FullRequired):prepare.prepare(f,p,Path(__file__))
 def test_launcher_modes_and_new_directory(self):
  f,p=fixture();p['impact_review']['status']='REVIEWED_EXPLICIT_SELECTION';plan=t.select(f,p,t.digest(p),p['source_binding'])
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);(root/'plan.json').write_bytes(t.canonical(plan));m={'validation_mode':'batch','files':{'plan.json':t.file_sha(root/'plan.json')}};(root/'protocol-manifest.json').write_bytes(t.canonical(m));sha=t.file_sha(root/'protocol-manifest.json')
   run.checked_plan(root,sha,'daily',root/'new')
   with self.assertRaises(ValueError):run.checked_plan(root,sha,'full',root/'new')
   with self.assertRaises(ValueError):run.checked_plan(root,'0'*64,'daily',root/'new')
   (root/'new').mkdir()
   with self.assertRaises(ValueError):run.checked_plan(root,sha,'daily',root/'new')
 def test_template_has_no_live_authority(self):
  p=json.loads(Path(__file__).with_name('selection-policy.template.json').read_bytes())
  self.assertNotEqual(p['impact_review']['status'],'REVIEWED_EXPLICIT_SELECTION');self.assertFalse(p['policy']['automatic_full_run'])
class ExecutionPreflight(unittest.TestCase):
 def plan(self,mode='batch'):
  full,profile=fixture();profile['impact_review']['status']='REVIEWED_EXPLICIT_SELECTION'
  return t.select(full,profile,t.digest(profile),profile['source_binding'],mode)
 def test_daily_and_full_preserve_inputs(self):
  for mode in ('batch','full'):
   plan=self.plan(mode);before=copy.deepcopy(plan);t.validate_execution_plan(plan);self.assertEqual(plan,before)
 def test_missing_kind_rejected_as_domain_error(self):
  # Public-schema version of the real preparation incident: required kind absent.
  plan=self.plan();del plan['segments'][1]['kind']
  with self.assertRaisesRegex(t.FullRequired,'kind missing/unknown'):t.validate_execution_plan(plan)
 def test_unknown_private_kind_and_schema_rejected(self):
  for kind in ('methods','current_composite','unknown'):
   plan=self.plan();plan['segments'][1]['kind']=kind
   with self.assertRaises(t.FullRequired):t.validate_execution_plan(plan)
  plan=self.plan();plan['tier_selection']['schema']='tier-selection-result/v99'
  with self.assertRaises(t.FullRequired):t.validate_execution_plan(plan)
 def test_missing_and_wrong_typed_fields(self):
  for key in ('segments','ordered_test_ids','full_ordered_test_ids','tier_selection','scope'):
   for value in (None,False,7):
    plan=self.plan();plan[key]=value
    with self.subTest(key=key,value=value),self.assertRaises(t.FullRequired):t.validate_execution_plan(plan)
 def test_segment_indices_and_names(self):
  for key,value in (('index',True),('index',2),('name','global'),('name','')):
   plan=self.plan();plan['segments'][1][key]=value
   with self.subTest(key=key,value=value),self.assertRaises(t.FullRequired):t.validate_execution_plan(plan)
 def test_original_slice_not_renumbered_selected_slice(self):
  full,profile=fixture();profile['required_segments']=['global','old'];profile['deferred_segments']=['new'];profile['deferral_reasons']={'new':profile['deferral_reasons']['old']};profile['new_test_ids']=[]
  profile=prepare.prepare(full,profile,Path(__file__));profile['impact_review']['status']='REVIEWED_EXPLICIT_SELECTION'
  plan=t.select(full,profile,t.digest(profile),profile['source_binding']);self.assertEqual(plan['segments'][1]['slice'],[1,2]);t.validate_execution_plan(plan)
  plan['segments'][1]['slice']=[0,1]
  with self.assertRaises(t.FullRequired):t.validate_execution_plan(plan)
 def test_invalid_slice_shape_and_boolean_bounds(self):
  for bounds in (None,[],[0],[False,1],[-1,1],[0,99],[1,1]):
   plan=self.plan();plan['segments'][1]['slice']=bounds
   with self.subTest(bounds=bounds),self.assertRaises(t.FullRequired):t.validate_execution_plan(plan)
 def test_method_partition_order_and_duplicates(self):
  for key,value in (('ordered_test_ids',['new.C.test_a','new.C.test_a']),('ordered_test_ids',['old.C.test_b']),('full_ordered_test_ids',['new.C.test_a'])):
   plan=self.plan();plan[key]=value
   with self.subTest(key=key),self.assertRaises(t.FullRequired):t.validate_execution_plan(plan)
  plan=self.plan();plan['tier_selection']['deferred_test_ids']=['new.C.test_a']
  with self.assertRaises(t.FullRequired):t.validate_execution_plan(plan)
 def test_counts_bool_and_stale_rejected(self):
  for key in ('selected_count','full_count','deferred_count','additional_count','total_executed_method_count'):
   for value in (True,-1,999):
    plan=self.plan();plan['tier_selection'][key]=value
    with self.subTest(key=key,value=value),self.assertRaises(t.FullRequired):t.validate_execution_plan(plan)
 def test_phase_call_and_no_method_slice(self):
  for key,value in (('call',None),('call',''),('slice',[0,1]),('test_ids',['new.C.test_a'])):
   plan=self.plan();plan['segments'][0][key]=value
   with self.subTest(key=key),self.assertRaises(t.FullRequired):t.validate_execution_plan(plan)
 def test_v2_additional_methods_and_overlap(self):
  full,profile=fixture();profile['schema']='reviewed-batch-selection/v2';profile['required_segments']=['new'];profile['deferred_segments']=['global','old'];profile['deferral_reasons']['global']=copy.deepcopy(profile['deferral_reasons']['old'])
  profile['phase_replacement']={'implementation':'current-state-once/v1','name':'current-state-once-v1','call':'current_state_once','retained_guarantees':['fixture'],'lost_guarantees':['fixture'],'full_triggers':['fixture']}
  profile['additional_methods']=[{'id':'test_shop_current_acceptance.ShopCurrentAcceptance.'+name,'method_source_sha256':'0'*64}for name in ('test_current_replay_masks_and_bounds','test_semantic_guard_mutations_rejected_without_hash_gate','test_current_compile_inventory')]
  profile=prepare.prepare(full,profile,Path(__file__));profile['impact_review']['status']='REVIEWED_EXPLICIT_SELECTION';plan=t.select(full,profile,t.digest(profile),profile['source_binding']);self.assertEqual(t.validate_execution_plan(plan)['additional_count'],3)
  for invalid_pin in ('z'*64,'F'*64,'0'*63):
   bad=copy.deepcopy(plan);bad['tier_selection']['additional_methods'][0]['method_source_sha256']=invalid_pin
   with self.subTest(pin=invalid_pin),self.assertRaises(t.FullRequired):t.validate_execution_plan(bad)
  plan['tier_selection']['additional_methods'][0]['id']='new.C.test_a'
  with self.assertRaises(t.FullRequired):t.validate_execution_plan(plan)
 def test_legal_empty_plan_preserved(self):
  full,profile=fixture();full['ordered_test_ids']=[];full['segments']=[];profile.update(required_segments=[],deferred_segments=[],deferral_reasons={},new_test_ids=[])
  profile=prepare.prepare(full,profile,Path(__file__));profile['impact_review']['status']='REVIEWED_EXPLICIT_SELECTION';plan=t.select(full,profile,t.digest(profile),profile['source_binding']);self.assertEqual(t.validate_execution_plan(plan)['segments'],0)
 def test_bad_plan_stops_before_any_controller_process_or_output(self):
  import contextlib,io
  from unittest.mock import patch
  plan=self.plan();del plan['segments'][1]['kind']
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);(root/'plan.json').write_bytes(t.canonical(plan));manifest={'validation_mode':'batch','files':{'plan.json':t.file_sha(root/'plan.json')}};(root/'protocol-manifest.json').write_bytes(t.canonical(manifest))
   argv=['run_validation.py','--protocol',str(root),'--approved-manifest-sha',t.file_sha(root/'protocol-manifest.json'),'--campaign',str(root/'attempt')]
   out=io.StringIO();err=io.StringIO()
   with patch.object(run.sys,'argv',argv),patch.object(run.subprocess,'run',side_effect=AssertionError('controller started')) as process,contextlib.redirect_stdout(out),contextlib.redirect_stderr(err):
    self.assertEqual(run.main(),2);process.assert_not_called()
   self.assertFalse((root/'attempt').exists());self.assertFalse(json.loads(err.getvalue())['tests_started']);self.assertEqual(out.getvalue(),'')

if __name__=='__main__':unittest.main(verbosity=2)
