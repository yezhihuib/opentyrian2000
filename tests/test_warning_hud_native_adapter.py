"""Pure preparation contracts. No compiler/native/game/fixture writes."""
from pathlib import Path
import ast,hashlib,re,types,unittest
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'tests/warning_hud_native_validation.py';helper=types.ModuleType('warning_helper');helper.__file__=str(p);exec(compile(p.read_bytes(),str(p),'exec'),helper.__dict__)
class WarningAdapter(unittest.TestCase):
 def test_inventory_finite44(self):
  self.assertEqual(sum(helper.CASE_INVENTORY.values()),44);self.assertEqual(helper.CASE_INVENTORY['brightness_0_to_7_at_4x_and_8x'],16);self.assertEqual(helper.CASE_INVENTORY['final_same_index_pixel_rect_ordinary_fade'],8);self.assertIn('SDL',helper.SCOPE)
 def test_bundle_actual_production(self):
  files,pins=helper.source_bundle(ROOT);self.assertEqual(len(files),18);self.assertEqual(len(pins['production_functions']),83)
  self.assertEqual(files['gameplay_hud_font_mirror.inc'],(ROOT/'src/gameplay_hud_font_mirror.inc').read_bytes())
  for family in helper.FAMILIES:
   for ext in('.c','.h'):self.assertEqual(files[family+ext],(ROOT/'src'/(family+ext)).read_bytes())
  self.assertNotIn(b'stage_suite(argv[1]);',files['warning_hud_native_additions.c.inc']);self.assertIn(b'static int historical_hud_main_not_run(',files['warning-hud-wrapper.c'])
 def test_draw_extraction_not_command_replay(self):
  files,pins=helper.source_bundle(ROOT);wrapper=files['warning-hud-wrapper.c'].decode()
  for rel,name in [('src/sprite.c','blit_sprite_hv_unsafe'),('src/fonthand.c','JE_outText'),('src/sprite.h','sprite'),('src/sprite.h','sprite_exists')]:
   body=helper.extract((ROOT/rel).read_text(),name);self.assertIn(body,wrapper);self.assertEqual(helper.sha(body.encode()),pins['actual_draw_functions'][name])
  companion=files['warning_hud_native_additions.c.inc'].decode();self.assertIn('JE_outText(game_screen,140,178,"WARNING",7,(int)value)',companion);self.assertNotIn('FontCommand c=',companion)
 def test_conditional_reset_verbatim_boundary(self):
  src=(ROOT/'src/render_mirror.c').read_text();body=helper.extract(src,'render_mirror_hud_reset');self.assertIn('#else',body);self.assertIn(body,src);self.assertTrue(body.endswith('\n}\n'));self.assertNotIn('bool render_mirror_set_hud_assets',body)
  with self.assertRaises(ValueError):helper.extract(src+body,'render_mirror_hud_reset')
  with self.assertRaises(ValueError):helper.extract(src.replace('#else\n if(manual_hd_enabled||asteroid_hd_enabled||shared_hud_lease||shared_hud_frame)', '#else\n#else\n if(manual_hd_enabled||asteroid_hd_enabled||shared_hud_lease||shared_hud_frame)'),'render_mirror_hud_reset')
 def test_exact_declared_disabled_scope(self):
  files,_=helper.source_bundle(ROOT);s=files['warning-hud-wrapper.c'].decode();self.assertIn('global_projectile91_requested(void){return false;}',s);self.assertIn('global_projectile91_pre_final_pixel',s);self.assertIn('global_talon_cached',s)
  for marker in('#define global_newshf_frame false\n','#define enemy_reuse_shutdown()'):
   src=(ROOT/'src/render_mirror.c').read_text();a=src.index(marker);off=src[a:src.index('#endif',a)];self.assertIn(off,s)
  self.assertIn('static void blit_sprite_dark',s);self.assertIn('CHECK(false)',s)
 def test_independent_alpha_native_oracle(self):
  s=(ROOT/'tests/warning_hud_native_additions.c.inc').read_text();body=s[s.index('static void warning_expected_begin'):s.index('static void warning_draw')]
  self.assertIn('warning_decode(id,v,mask)',body);self.assertIn('v[y*s->width+x]&15',body);self.assertIn('warning_atlas[ay*512+ax]',body);self.assertNotIn('hud_font_alpha(',body);self.assertNotIn('font_blend(',body);self.assertNotIn('hud_sprite_decode(',body);self.assertIn('advance==35',body)
  self.assertIn('x<2*d||x>=36*d||y>=6*d',s);self.assertIn('116*d+x',s)
 def test_public_final_fade_and_separate_isolation(self):
  s=(ROOT/'tests/warning_hud_native_additions.c.inc').read_text();self.assertIn('render_mirror_fade_step(7)',s);self.assertIn('render_mirror_pixel(VGAScreenSeg,p,value,MIRROR_NORMAL)',s);self.assertIn('render_mirror_rect(VGAScreenSeg,&r)',s);self.assertIn('font_clear_cached(16)',s);self.assertIn('font_persistent[0].valid&&font_persistent[1].valid',s);self.assertIn('memset(game_screen->pixels,7,64000);warning_copy_world();render_mirror_begin()',s)
 def test_raw_input_fail_closed(self):
  for args in[(b'',b'',b''),(None,b'',b''),(bytearray(),b'',b'')]:
   with self.assertRaises(ValueError):helper.native_input(*args)
  self.assertEqual(set(helper.RAW_PINS),{'tyrian.pic','palette.dat','tyrian.shp'})
 def test_huf_original_identity_and_bounded_fixture_plan(self):
  p=helper.fixture_plan(ROOT);self.assertEqual(len(p['resources']),6);self.assertEqual(set(p['negative_roots']),{'missing','corrupt'});self.assertEqual(p['negative_roots']['missing']['omit'],'gameplay-hud-font-v1.hda');self.assertLess(len(bytes.fromhex(p['negative_roots']['corrupt']['bytes_hex'])),112)
 def test_inactive_symbol_closure_rejects_each_omission(self):
  files,pins=helper.source_bundle(ROOT);inventory=pins['symbol_inventory'];self.assertEqual(inventory['unresolved'],[]);self.assertGreater(len(inventory['calls']),500)
  functions=('shapesy_frame_reset','cyan_frame_reset','shapesy_shutdown','cyan_shutdown','shapesy_frame_check','cyan_frame_check','shapesy_present_geometry','cyan_present_geometry','projectile91_shutdown')
  wrapper=files['warning-hud-wrapper.c'].decode()
  for name in functions:
   pattern=r'^static (?:void|bool) '+name+r'\([^\n]*\n';mutated,count=re.subn(pattern,'',wrapper,flags=re.M);self.assertEqual(count,1,name)
   changed=dict(files);changed['warning-hud-wrapper.c']=mutated.encode()
   with self.assertRaisesRegex(ValueError,'Unbound finite C calls'):helper.symbol_inventory(changed)
  for name in('render_mirror_newshf_validation_reset','render_mirror_newshf_validation_frame'):
   changed=dict(files);changed['warning-hud-wrapper.c']=re.sub(r'^#define '+name+r'[^\n]*\n','',wrapper,flags=re.M).encode()
   with self.assertRaisesRegex(ValueError,'Unbound finite C calls'):helper.symbol_inventory(changed)
  changed=dict(files);changed['warning-hud-wrapper.c']=wrapper.replace('static bool shapesy_clear_proof;','').encode()
  with self.assertRaisesRegex(ValueError,'Missing finite bool storage'):helper.symbol_inventory(changed)
  for prefix in('shapesy','cyan'):
   self.assertIn('static bool '+prefix+'_frame_check(void){return true;}',wrapper);self.assertIn('static bool '+prefix+'_present_geometry(SDL_Renderer *r,const SDL_Rect *d){return true;}',wrapper)
  self.assertIn('shapesy_frame_reset(void){shapesy_clear_proof=false;}',wrapper)
  header=(ROOT/'src/render_mirror.h').read_text();a=header.index('#define render_mirror_newshf_validation_reset(');self.assertIn(header[a:header.index('#endif',a)],wrapper)
  changed=dict(files);changed['warning_hud_native_additions.c.inc']+=b'\nstatic void never_called(void){unbound_new_runtime_call();}\n'
  with self.assertRaisesRegex(ValueError,'unbound_new_runtime_call'):helper.symbol_inventory(changed)
 def test_recursive_quote_include_closure(self):
  files,pins=helper.source_bundle(ROOT);graph=pins['quoted_include_closure'];self.assertEqual(len(graph['roots']),7);self.assertEqual(len(graph['all_reachable']),18)
  self.assertEqual(files['current_hud_payload_pins.h'],(ROOT/'src/current_hud_payload_pins.h').read_bytes());self.assertEqual(pins['payload_pin_header_sha256'],helper.sha(files['current_hud_payload_pins.h']))
  self.assertIn('current_hud_payload_pins.h',graph['quoted_edges']['gameplay_hud_meters.c'])
  for omitted in('current_hud_payload_pins.h','production.inc','gameplay_hud_font.h'):
   changed=dict(files);del changed[omitted]
   with self.assertRaisesRegex(ValueError,'Unbound quote include'):helper.quoted_include_closure(changed)
  changed=dict(files);changed['current_hud_payload_pins.h']+=b'\n#include "missing_recursive.h"\n'
  with self.assertRaisesRegex(ValueError,'missing_recursive'):helper.quoted_include_closure(changed)
  changed=dict(files);changed['gameplay_hud_meters.c']+=b'\n#include "../src/current_hud_payload_pins.h"\n'
  with self.assertRaisesRegex(ValueError,'Unbound quote include'):helper.quoted_include_closure(changed)
  changed=dict(files);changed['unexpected.h']=b'/* unused */'
  with self.assertRaisesRegex(ValueError,'Unreachable'):helper.quoted_include_closure(changed)
 def test_helpers_have_no_implicit_execute_or_write(self):
  tree=ast.parse((ROOT/'tests/warning_hud_native_validation.py').read_text());calls=[x for x in ast.walk(tree)if isinstance(x,ast.Call)]
  self.assertFalse(any(isinstance(x.func,ast.Attribute)and x.func.attr in('run','Popen','write_bytes','write_text','mkdir','system')for x in calls));self.assertEqual(helper.base_module(ROOT).ROOT,ROOT)
if __name__=='__main__':unittest.main(verbosity=2)
