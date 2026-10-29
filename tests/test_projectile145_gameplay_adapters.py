from pathlib import Path
import os,sys,unittest
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;sys.path.insert(0,str(HERE))
import projectile145_gameplay_observer as observer
import projectile145_gameplay_differential as diff
class Projectile145GameAdapters(unittest.TestCase):
 def test_native_sprite_original_assignment_and_callback_once(self):
  original=(ROOT/'src/sprite.c').read_text();modified=diff.sprite_text(original)
  self.assertEqual(modified.count('render_mirror_sprite2_blend_pixel(surface,pixels,*data,sprite2s,index,x,y);'),original.count('render_mirror_sprite2_blend_pixel(surface,pixels,*data,sprite2s,index,x,y);'))
  recovered=modified.replace(diff.BLEND_REPLACEMENT,diff.BLEND_ORIGINAL).replace('#include "asset_debug.h"\n#include "game_probe.h"','#include "asset_debug.h"');self.assertEqual(recovered,original)
 def test_renderer_native_dump_is_additive_only(self):
  text=(ROOT/'src/render_mirror.c').read_text();self.assertEqual(diff.renderer_text(text).replace(diff.DUMP,''),text)
  self.assertIn('if(game_probe_enabled&&game_probe_tick==1162)',diff.DUMP);self.assertNotIn('assert(',diff.DUMP)
 def test_asset_log_filter_is_output_only(self):
  text=(ROOT/'src/asset_debug.c').read_text();self.assertEqual(diff.asset_text(text).replace(observer.LOG_FILTER+'\n',''),text)
  self.assertIn('vfprintf(stream,format,args)',observer.LOG_FILTER);self.assertNotIn('game_probe_enabled=',observer.LOG_FILTER)
 def test_control_keys_scrubbed_without_parent_mutation(self):
  source={'AIRCRAFT170_DIFFERENTIAL_POSE':'3','SHARED170_FORCE':'1','TYRIAN_CYAN_BORROW_TEST':'1','PROJECTILE145_FORCE':'1','OT_TEST':'1','TYRIAN_GAME_PROBE':'1','KEEP':'x'}
  e=diff.environment(source,Path('/sysroot'),Path('/out'),Path('/tmp'));self.assertEqual(e['KEEP'],'x');self.assertEqual(len(source),7)
  self.assertFalse(set(source)-{'KEEP'}&set(e))
 def test_baseline_logging_has_no_145_admission_change(self):
  text=(ROOT/'src/tyrian2.c').read_text();modified=diff.baseline_shot_text(text)
  self.assertEqual(modified.count('==145'),text.count('==145'))
  self.assertEqual(modified.count('projectile145_actual_log('),3)
  self.assertNotIn('enemyShot[b].sgr = 145',modified)
 def test_footprint_exact_native_mask(self):
  sys.path.insert(0,str(ROOT/'scripts'));import current_projectile145_compatibility as art
  self.assertEqual(art.MASK.count('1'),39);self.assertEqual(len(art.MASK),168)
  text=Path(diff.__file__).read_text();self.assertIn('outside_native_mask_support',text);self.assertIn('assert opaque==130',text)
 def test_single_tick_triple_scope(self):
  text=Path(diff.__file__).read_text();self.assertIn("for kind in ('present','missing','baseline')",text);self.assertIn("'--render-ticks=1163'",text)
  self.assertIn("'--asset-debug-capture-start=1162'",text);self.assertIn("'--asset-debug-capture-count=1'",text)
if __name__=='__main__':unittest.main()
