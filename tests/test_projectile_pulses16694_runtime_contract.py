"""Nine finite source contracts, not executed C/native/gameplay qualification."""
from pathlib import Path
import hashlib,os,re,unittest
ROOT=Path(os.environ.get('PULSES16694_TEST_ROOT',str(Path(__file__).resolve().parents[1])))
PINS={'current_projectile_pulses16694_payload_pins.h': '898a2e8264649ed9bcd97be30f87f77b41c15a29ea3fe188e07f13bdf3f77854', 'enemy_pulses16694_mirror.inc': 'e6d0a7ff0e8dbc28fae4a5225e22ee56ddd318765638476c03f0a9bb537205bd', 'entity_draw.c': 'b9f77a2eee4c210015fbf9c9b15c3ce2e7e89d737b55a19cbf496ca5346f8a67', 'global_projectile91_mirror.inc': 'e7540314d2d55df44d3d615a3b830e6619c30fadd592c53a52db3fca842dd422', 'render_mirror.c': '506339c355b3ef303e8f76cee7180408d8e799d24d66eee468baa46744638be7', 'tyrian2.c': 'c037cad7761396c636c3a44b8d432832f49c8b362b0331f962225a2f388b0e2e'}
class Pulses16694RuntimeContract(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.s={name:(ROOT/'src'/name).read_text()for name in PINS}
 def test_exact_six_qualified_production_bytes(self):
  for n,p in PINS.items():self.assertEqual(hashlib.sha256((ROOT/'src'/n).read_bytes()).hexdigest(),p)
 def test_no_gameplay_diagnostic_in_production(self):
  for raw in self.s.values():
   for token in ('PULSES16694OBS1','pulses16694obs_','PULSES16694_SELECTOR','pulses16694-alpha.tsv'):self.assertNotIn(token,raw)
 def test_unsigned_finite_member_mask_keeps_owner_booleans(self):
  raw=self.s['global_projectile91_mirror.inc'];self.assertIn('unsigned global_projectile91_used_members',raw);self.assertIn('1024u',raw);self.assertIn('2048u',raw);self.assertIn('256u',raw);self.assertIn('512u',raw)
  self.assertIn('Uint8 *global_projectile91_owner',self.s['render_mirror.c']);self.assertNotRegex(raw,r'Uint8\s+global_projectile91_used_members')
 def test_all_ten_resources_remain_selected(self):
  raw=self.s['global_projectile91_mirror.inc']
  for selector in (91,145,61,101,120,139,168,169,162,260,166,94):self.assertRegex(raw,r'\b'+str(selector)+r'\b')
  for name in ('projectile91_resource','projectile145_resource','projectile61_resource','projectile_blue_triplet_resource','projectile_gold_pulse_resource','projectile_statics_resource','projectile_pulses16694_resource'):self.assertIn(name,raw)
 def test_independent_two_resources_and_payload_pins(self):
  raw=self.s['enemy_pulses16694_mirror.inc'];self.assertIn('projectile_pulses16694_resources[2]',raw);self.assertIn('bool checked,valid',raw);self.assertIn('char root[1024]',raw)
  for pin in ('0x80c10783a6cabbe2','0x131a3be7ed56665d'):self.assertIn(pin,self.s['current_projectile_pulses16694_payload_pins.h'])
 def test_standard_header_and_source_palette_are_closed(self):
  raw=self.s['enemy_pulses16694_mirror.inc']
  for token in ('1550166','1550094','12*14*8*8*4','projectile91_source(bank,91)','projectile_pulses16694_palette_matches'):self.assertIn(token,raw)
  self.assertIn('spriteSheet8',self.s['global_projectile91_mirror.inc']);self.assertIn('!xmas',self.s['global_projectile91_mirror.inc'])
 def test_role154_entity_dispatch_is_finite(self):
  raw=self.s['entity_draw.c'];self.assertIn('game_probe_scene_draw(155,index,x,y,0,ENTITY_NORMAL,mirrored)',raw);self.assertIn('index==166||index==94',raw)
  self.assertIn('ASSET_ENEMY_PULSES16694',self.s['render_mirror.c']);self.assertIn('normal15-output-scope',self.s['render_mirror.c']);self.assertIn('normal15-scene-font',self.s['render_mirror.c'])
  scripts={'scripts/package_runtime.py': 'e619f52bec2a026a5421868a6abd39fe30807693d20c01e5a2294efd2519a320', 'scripts/rebuild_recovered_runtime_manifest.py': '8cd773dd6ed9fc3ba8d813b59b838bf3b4b207c0f971d978c6aa87da473295ef'}
  for name,pin in scripts.items():self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),pin)
  package=(ROOT/'scripts/package_runtime.py').read_text();rebuild=(ROOT/'scripts/rebuild_recovered_runtime_manifest.py').read_text()
  self.assertLess(package.index('from current_projectile_gold_pulse_compatibility import validate_runtime_rows'),package.index('from current_projectile_pulses16694_compatibility import validate_runtime_rows'))
  self.assertLess(rebuild.index('from current_projectile_gold_pulse_compatibility import load'),rebuild.index('from current_projectile_pulses16694_compatibility import load'))
  self.assertIn('enemy-projectile-pulses16694-',rebuild);self.assertIn('(166,94)',rebuild.replace(' ',''))
 def test_original_player_wrappers_and_native_callback_preserved_by_pin(self):
  raw=self.s['global_projectile91_mirror.inc']
  for name in ('global_projectile91_pixel','global_projectile91_used_members','global_projectile91_finish_proof','global_projectile91_check_cache'):self.assertIn(name,raw)
  self.assertIn('sprite == 169 || sprite == 162 || sprite == 260 || sprite == 166 || sprite == 94)',self.s['tyrian2.c'])
  for name,pin in {'draw_player_shot_sprite2': '88a6d9c3e7fa4a0feefe5c928f7a5317a82cb4d3acc4d833511decf0b7219c8d', 'draw_player_shot_shadow_sprite2': '11d7ab8ffe139b44a969864e03bef6ade8904b0c66aefac6f078cee7760cc372'}.items():
   text=self.s['entity_draw.c'];start=text.index('void '+name+'(');op=text.index('{',start);level=0
   for end in range(op,len(text)):
    level+=(text[end]=='{')-(text[end]=='}')
    if level==0:break
   self.assertEqual(hashlib.sha256(text[start:end+1].encode()).hexdigest(),pin)
 def test_resource_shutdown_and_selected_only_include(self):
  self.assertIn('#include "enemy_pulses16694_mirror.inc"',self.s['render_mirror.c']);self.assertIn('projectile_pulses16694_shutdown()',self.s['global_projectile91_mirror.inc']);self.assertIn('projectile_pulses16694_shutdown',self.s['enemy_pulses16694_mirror.inc'])
if __name__=='__main__':unittest.main()
