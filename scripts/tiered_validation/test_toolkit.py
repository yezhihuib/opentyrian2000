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
if __name__=='__main__':unittest.main(verbosity=2)
