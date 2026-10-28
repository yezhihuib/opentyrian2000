"""Pure contract tests; native sanitizer execution has a separate bound receipt."""
from pathlib import Path
import ast,unittest
HERE=Path(__file__).resolve().parent
class Shared170Bronze356BorrowAdapter(unittest.TestCase):
 def setUp(self):
  self.c=(HERE/'shared170_bronze356_borrow_native.c.inc').read_text()
  self.py=(HERE/'shared170_bronze356_borrow_validation.py').read_text()
 def test_real_provider_and_native_background_blitter(self):
  for marker in ('render_mirror_shapesy_layer1(game_screen','blit_background_row(game_screen','render_mirror_shapesy_end();','shapesy_bronze356.used&&!shapesy_platform_used','shapesy_borrow_ready()'):
   self.assertIn(marker,self.c)
  self.assertNotIn('shapesy_borrow.values[',self.c)
 def test_density8_only_and_two_actual_output_geometries(self):
  for marker in ('s_setup(8);','output_scale==2?"2x":"4x"','CHECK(init_scaler(scaler))','video_output_geometry(&geometry)&&geometry.scale==(int)output_scale','for(unsigned scale=2;scale<=4;scale+=2)'):
   self.assertIn(marker,self.c)
 def test_every_generated_provider_pixel_has_typed_sample(self):
  for marker in ('y<224','x<192','CHECK(p[3]==255&&color==want&&hd_owner[n])','shapesy_borrow_sample(serial,n,color)','!shapesy_borrow_sample(serial,n,color^1u)','!shapesy_borrow_sample(serial+1,n,color)'):
   self.assertIn(marker,self.c)
 def test_real_borrower_and_final_cached_output_oracles(self):
  for marker in ('s_birth(0,pose,102,62,0);quartet();','global_newshf_dual_preflight_state[0]==2','global_newshf_dual_shapesy_serial[0]==serial','global_newshf_shapesy_dependency==serial','CHECK(local_soft>0&&local_empty>0)','pixel(output,(96-24)*8+x,55*8+y)','cross_output_oracle(pose);global_newshf_check_cache();CHECK(ready&&last_output_valid);cross_output_oracle(pose);'):
   self.assertIn(marker,self.c)
 def test_provider_payload_failure_reaches_consumer_final_and_cache(self):
  for marker in ('for(unsigned cached=0;cached<2;cached++)','shapesy_bronze356.member.rgba[0]^=1','CHECK(!shapesy_borrow_check(serial))','global_newshf_check_cache();CHECK(!ready&&!last_output_valid)','else finish_invalid();'):
   self.assertIn(marker,self.c)
 def test_driver_binds_actual_inputs_and_labels_partial_sanitizer_scope(self):
  ast.parse(self.py)
  for marker in ("inventory(fresh/'hd-on-build/src')==source","'opentyr-test.o'","'sprite-sanitized.o'","'tyrian2-sanitized.o'",'source==inventory(r/\'src\')','final_output_cap_bytes=16000000','compile_transient_peak_forecast=50*1024**2','reserve=250*1024**2','private_original_stdin_persisted=False','non-sanitized','SDL/systemlibraries notinstrumented'):
   self.assertIn(marker,self.py)
if __name__=='__main__':unittest.main()
