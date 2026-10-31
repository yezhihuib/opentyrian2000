"""Nine finite source contracts, not executed C/native/gameplay qualification."""
from pathlib import Path
import hashlib,os,re,unittest
ROOT=Path(os.environ.get('STATICS_TEST_ROOT',str(Path(__file__).resolve().parents[1])))
PINS={'entity_draw.c':'177c22892477630908be83ef011013b0490dcd5d343f4c0d68846e70acd51182','global_projectile91_mirror.inc':'0e0088a93502ff55fb086c9a52c841bb3593cb61fd7a44b567ce57771dd5762a','render_mirror.c':'387710a63568932245a7f9f1e87fea004bb28c60fabb487d3dd63ecdcc4a4f19','tyrian2.c':'240a6d6c05d114d34d41d20235ebc1f730ac96f34863a1b4ce01fbbb86a63e19','enemy_statics_mirror.inc':'2aca7e11a03882eea6543640b735a0919fec82462165c24476c2dd231a027c18','current_projectile_statics_payload_pins.h':'2b859dba5213af576fc2aadf76ddacabc59df3fc5e1ca1a8da863ddf2d93f90b'}
class StaticsRuntimeContract(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.s={name:(ROOT/'src'/name).read_text()for name in PINS}
 def test_exact_six_qualified_production_bytes(self):
  for n,p in PINS.items():self.assertEqual(hashlib.sha256((ROOT/'src'/n).read_bytes()).hexdigest(),p)
 def test_no_gameplay_diagnostic_in_production(self):
  for raw in self.s.values():
   for token in ('STATICSOBS1','staticsobs_','STATICS_SELECTOR','statics-alpha.tsv'):self.assertNotIn(token,raw)
 def test_unsigned_finite_member_mask_keeps_owner_booleans(self):
  raw=self.s['global_projectile91_mirror.inc'];self.assertIn('unsigned global_projectile91_used_members',raw);self.assertIn('256u',raw);self.assertIn('512u',raw)
  self.assertIn('Uint8 *global_projectile91_owner',self.s['render_mirror.c']);self.assertNotRegex(raw,r'Uint8\s+global_projectile91_used_members')
 def test_all_ten_resources_remain_selected(self):
  raw=self.s['global_projectile91_mirror.inc']
  for selector in (91,145,61,101,120,139,168,169,162,260):self.assertRegex(raw,r'\b'+str(selector)+r'\b')
  for name in ('projectile91_resource','projectile145_resource','projectile61_resource','projectile_blue_triplet_resource','projectile_gold_pulse_resource','projectile_statics_resource'):self.assertIn(name,raw)
 def test_independent_two_resources_and_payload_pins(self):
  raw=self.s['enemy_statics_mirror.inc'];self.assertIn('projectile_statics_resources[2]',raw);self.assertIn('bool checked,valid',raw);self.assertIn('char root[1024]',raw)
  for pin in ('0x97621110c318d6a5','0xfa2ac27b3212b610'):self.assertIn(pin,self.s['current_projectile_statics_payload_pins.h'])
 def test_standard_header_and_source_palette_are_closed(self):
  raw=self.s['enemy_statics_mirror.inc']
  for token in ('1540162','1540260','12*14*8*8*4','projectile91_source(bank,91)','projectile_statics_palette_matches'):self.assertIn(token,raw)
  self.assertIn('spriteSheet8',self.s['global_projectile91_mirror.inc']);self.assertIn('!xmas',self.s['global_projectile91_mirror.inc'])
 def test_role154_entity_dispatch_is_finite(self):
  raw=self.s['entity_draw.c'];self.assertIn('game_probe_scene_draw(154,index,x,y,0,ENTITY_NORMAL,mirrored)',raw);self.assertIn('index==162||index==260',raw)
  self.assertIn('ASSET_ENEMY_STATICS',self.s['render_mirror.c'])
  scripts={'scripts/package_runtime.py': '1552397638791511a70bbe94c0c19455225258ac05aff072ae0defa6432bb50d', 'scripts/rebuild_recovered_runtime_manifest.py': '91d7aeeeff91c98be25f07edfa199049ed7457d4d2d71190752dc45e6115af47'}
  for name,pin in scripts.items():self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),pin)
  package=(ROOT/'scripts/package_runtime.py').read_text();rebuild=(ROOT/'scripts/rebuild_recovered_runtime_manifest.py').read_text()
  self.assertLess(package.index('from current_projectile_gold_pulse_compatibility import validate_runtime_rows'),package.index('from current_projectile_statics_compatibility import validate_runtime_rows'))
  self.assertLess(rebuild.index('from current_projectile_gold_pulse_compatibility import load'),rebuild.index('from current_projectile_statics_compatibility import load'))
  self.assertIn('enemy-projectile-statics-',rebuild);self.assertIn('(162,260)',rebuild.replace(' ',''))
 def test_original_player_wrappers_and_native_callback_preserved_by_pin(self):
  raw=self.s['global_projectile91_mirror.inc']
  for name in ('global_projectile91_pixel','global_projectile91_used_members','global_projectile91_finish_proof','global_projectile91_check_cache'):self.assertIn(name,raw)
  self.assertIn('sprite == 169 || sprite == 162 || sprite == 260)',self.s['tyrian2.c'])
  for name,pin in {'draw_player_shot_sprite2': '88a6d9c3e7fa4a0feefe5c928f7a5317a82cb4d3acc4d833511decf0b7219c8d', 'draw_player_shot_shadow_sprite2': '11d7ab8ffe139b44a969864e03bef6ade8904b0c66aefac6f078cee7760cc372'}.items():
   text=self.s['entity_draw.c'];start=text.index('void '+name+'(');op=text.index('{',start);level=0
   for end in range(op,len(text)):
    level+=(text[end]=='{')-(text[end]=='}')
    if level==0:break
   self.assertEqual(hashlib.sha256(text[start:end+1].encode()).hexdigest(),pin)
 def test_resource_shutdown_and_selected_only_include(self):
  self.assertIn('#include "enemy_statics_mirror.inc"',self.s['render_mirror.c']);self.assertIn('projectile_statics_shutdown()',self.s['global_projectile91_mirror.inc']);self.assertIn('projectile_statics_shutdown',self.s['enemy_statics_mirror.inc'])
if __name__=='__main__':unittest.main()
