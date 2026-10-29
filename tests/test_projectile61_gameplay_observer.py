"""Pure observer driver contracts, not game execution."""
import importlib.util
from pathlib import Path
import sys,unittest
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P))
import projectile61_gameplay_observer as D
class ObserverContracts(unittest.TestCase):
 def test_budget(self):
  self.assertEqual(D.PEAK+D.RESERVE,314572800)
  self.assertTrue(D.budget_ok(D.PEAK,D.RESERVE,D.LOG_CAP))
  self.assertFalse(D.budget_ok(D.PEAK+1,D.RESERVE,0))
  self.assertFalse(D.budget_ok(0,D.RESERVE-1,0))
  self.assertFalse(D.budget_ok(0,D.RESERVE,D.LOG_CAP+1))
 def test_poisoned_parent_is_not_mutated(self):
  parent={'PATH':'/usr/bin','AIRCRAFT170_DIFFERENTIAL_POSE':'3','PROJECTILE61_FORCE':'1','SHARED_ACTOR':'2','TYRIAN_GAME_PROBE_FORCE':'7','OT_ACTOR':'4'};before=dict(parent)
  env,removed=D.environment(parent,Path('/s'),Path('/o'),Path('/t'))
  self.assertEqual(parent,before);self.assertEqual(set(removed),set(parent)-{'PATH'})
  self.assertFalse(set(removed)&set(env));self.assertEqual(env['SDL_RENDER_DRIVER'],'software')
 def fixture(self):
  emit={'kind':'emit','weapon':'131','index':'61','slot':'2','tick':'151'}
  draw={'kind':'draw','weapon':'-1','index':'61','slot':'2','tick':'152','x':'100','y':'50'}
  final={'tick':'152','slot':'2','x':'100','y':'50','ready':'1','last_valid':'1','cached':'1','fault':'0','member_mask':'4','opaque_authored_not_classic':'1'}
  final.update({key:'1' for key in ('resource_valid','metadata_ok','palette12_ok','normal_bank_ok','native_mask_ok','layout_ok')})
  final.update(density='8',role='151',index='61',opaque_authored_total='246',opaque_owned='1',opaque_visible_supported='246',opaque_outside_native_mask='0')
  admitted={'tick':'152','x':'100','y':'50','role':'151','index':'61','mirrored':'1'}
  return [emit,draw],[final],[admitted]
 def test_four_way_actual_nonvacuous_join(self):
  a,f,r=self.fixture();self.assertEqual(len(D.classify_observation(a,f,r)[3]),1)
 def test_absent_or_wrong_admission_never_passes(self):
  a,f,r=self.fixture();self.assertFalse(D.classify_observation(a,f,[])[3])
  r[0]['mirrored']='0';self.assertFalse(D.classify_observation(a,f,r)[3])
 def test_geometry_and_slot_are_not_source_event_claims(self):
  a,f,r=self.fixture();a[1]['slot']='9';self.assertFalse(D.classify_observation(a,f,r)[3])
  a,f,r=self.fixture();r[0]['x']='101';self.assertFalse(D.classify_observation(a,f,r)[3])
  a,f,r=self.fixture();a[0]['tick']='153';self.assertFalse(D.classify_observation(a,f,r)[3])
 def test_classic_or_faulted_frame_never_passes(self):
  for key,val in [('opaque_authored_not_classic','0'),('fault','1'),('ready','0'),('member_mask','3'),('palette12_ok','0'),('metadata_ok','0'),('normal_bank_ok','0'),('opaque_outside_native_mask','1'),('opaque_authored_total','247'),('opaque_owned','0')]:
   a,f,r=self.fixture();f[0][key]=val;self.assertFalse(D.classify_observation(a,f,r)[3])
 def test_correct_five_TU_scope(self):
  self.assertEqual(set(D.UNITS),{'render_mirror','tyrian2','entity_draw','game_probe','asset_debug'})
  self.assertEqual(len(D.CHANGED),4);self.assertEqual(len(D.ADDED),2)
 def test_production_unchanged_and_historical_failure_retained(self):
  s=(P/'projectile61_gameplay_observer.py').read_text()
  for expected in ["f['status']=='FAIL_BINDING_RETAINED'",'ACCEPTED_FUNCTIONAL_RESULTS_WITH_RAW_INDEX_STAT_CACHE_DEVIATION',"len(borrowed)==81", "SHA(dep)==pin['sha256']", "inv(a.baseline/'src')==old", "len(report['fresh_depfile_sha256'])==5",'FAIL_AFTER_RECEIPT_BUDGET_RETAINED']:
   self.assertIn(expected,s)
 def test_explicit_bounded_scene_without_capture(self):
  s=(P/'projectile61_gameplay_observer.py').read_text()
  for value in ['--asset-debug-episode=2','--asset-debug-level=9','--render-ticks=261','--render-no-capture','--no-xmas','--render-test=8','NO_CONFIRMED_61_WINDOW']:
   self.assertIn(value,s)
  self.assertNotIn('--asset-debug-capture',s)
if __name__=='__main__':unittest.main()
