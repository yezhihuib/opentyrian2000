"""Bounded adapter contracts; actual game execution has its own frozen receipt."""
from pathlib import Path
import ast, hashlib, importlib.util, os, unittest
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('six_shared170_guards',HERE/'shared170_bronze356_game_guards.py')
driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver)

class Shared170Bronze356GameGuards(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  old=HERE/'aircraft169_aircraft_diagnostics.py'
  if not old.exists():old=Path(os.environ['SHARED170_SOURCE_ROOT'])/'tests/aircraft169_aircraft_diagnostics.py'
  cls.old=old.read_text();cls.adapted=driver.adapt(cls.old)
  cls.code=(HERE/'shared170_bronze356_game_guards.py').read_text()
 def test_exact_historical_identity_and_no_historical_write(self):
  self.assertEqual(hashlib.sha256(self.old.encode()).hexdigest(),driver.OLD_SHA)
  ast.parse(self.adapted)
  self.assertIn("original_driver_sha256=OLD_SHA",self.code)
  self.assertNotIn("old.write_text",self.code)
  with self.assertRaises(AssertionError):driver.adapt(self.old+'\n')
 def test_only_six_serial_controlled_modes(self):
  self.assertEqual(driver.MODES,('baseline-pose1','baseline-pose2','baseline-pose3','final-bronze-rgba','cached-bronze-rgba','cached-transfer-aircraft42'))
  for needle in ("modes=list(APPROVED_MODES)","result.append(run(modes[0]))","mode.startswith('baseline-pose') else 1"):
   self.assertIn(needle,self.adapted)
  for needle in ("'--density','8'","'--start','356','--end','358'","'--jobs','1'",'original97_rerun=False'):
   self.assertIn(needle,self.code)
 def test_bronze_mask_requires_real_admission_and_exact_authored_rgb(self):
  for needle in ('diagnostic_bronze_place(first,x,y);','diagnostic_bronze_mark(x+(int)tile*24,y,a->rgba);'):
   self.assertIn(needle,self.adapted)
  for needle in ('p[3]==255&&hd_owner[n]','==want','diagnostic_bronze_mask[n]=1','diagnostic_bronze_original','shapesy_bronze356_sources_valid()'):
   self.assertIn(needle,driver.BRONZE_HELPERS)
  self.assertNotIn('hd_owner[n]=',driver.BRONZE_HELPERS)
  self.assertIn("assets/hd/current-compat/shapesy-bronze356",self.adapted)
  self.assertIn("assert (pack/'terrain-shapesy-356-8.hda').is_file()",self.adapted)
  self.assertEqual(driver.BRONZE_HELPERS.count('shapesy_world_reset();'),2)
  self.assertNotIn('shapesy_map_reset()',driver.BRONZE_HELPERS)
 def test_recursive_same_pixel_chain_and_nonvacuous_mutation(self):
  self.assertEqual(self.adapted.count('diagnostic_bronze_mask[n]&&shapesy_borrow_sample(serial,n,color)'),2)
  for needle in ('actual356 secondary cyan170 recursive intersection','diagnostic_chain_pixels>0','actual356 provider valid before recursive corruption','shapesy_bronze356.member.rgba[0]^=1','genuine sealed cyan source before mutation','cached mutation rejected','final mutation rejected'):
   self.assertIn(needle,self.adapted)
  self.assertNotIn('shapesy_resources.members[0].rgba[0]^=1;',self.adapted)
 def test_transfer_targets_same170_chain_actor_and_unselected_phase42(self):
  for needle in ('profile==21&&global_newshf_cyan_pixels[slot]&&diagnostic_bronze_actor[slot]','diagnostic_actor_slot[i]==slot+1&&diagnostic_chain_mask[i]&&global_talon_owner[i]','copied>0','actual Talon transfer draw','UINT64_C(0x70000000000)','phase>=40&&phase<=42'):
   self.assertIn(needle,self.adapted)
  self.assertIn('cached-transfer-aircraft42',driver.MODES)
  for needle in ('!global_newshf_owner[n]||diagnostic_actor_slot[n]!=slot+1||!diagnostic_chain_mask[n]','mask[(ay/8)*24+ax/8]','rgba[4*(ay*192+ax)+3]>=255','diagnostic_transfer_position(slot,&x,&y);'):
   self.assertIn(needle,driver.BRONZE_HELPERS+self.adapted)
 def test_new_family_pack_explicit_header_and_complete_payload_pins(self):
  self.assertEqual({p[0] for p in driver.PACK_PINS.values()},{2020356,2100040,2100041,2100042})
  self.assertIn('verify_guard_pack(pack)',self.adapted)
  for needle in ("struct.unpack('<4s6I',b[:28])","hashlib.sha256(b).hexdigest()==file_sha","hashlib.sha256(b[28:]).hexdigest()==payload_sha",'len(b)==172060'):
   self.assertIn(needle,self.code)
 def test_budget_closure_environment_and_failure_retention(self):
  self.assertEqual(driver.PEAK+driver.RESERVE,396361728)
  for needle in ('free>=PEAK+RESERVE','available<RESERVE','minimum_sampled_free','source_unchanged','objects_unchanged','data_unchanged','pack_unchanged','producer_unchanged','index_unchanged','primary_closure_unchanged','removed_parent_control_environment','sanitizer_claim=False'):
   self.assertIn(needle,self.code)
  self.assertNotIn('shutil.rmtree',self.code)
  self.assertIn('actual copied ownership',self.adapted)

if __name__=='__main__':unittest.main()
