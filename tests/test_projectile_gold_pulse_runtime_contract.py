"""Static finite C/package connection checks only, not native/game proof."""
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
class GoldRuntimeContract(unittest.TestCase):
 def text(self,n):return (ROOT/'src'/n).read_text()
 def test_01_enemy_role_and_original_blit_once(self):
  s=self.text('entity_draw.c').split('void draw_enemy_shot_sprite2(',1)[1].split('/* Original sidekick',1)[0]
  self.assertEqual(s.count('blit_sprite2(target,x,y,bank,index);'),1);self.assertEqual(s.count('render_mirror_entity_end();'),1);self.assertIn('game_probe_scene_draw(153,index,x,y,0,ENTITY_NORMAL,mirrored)',s)
  generic=self.text('render_mirror.c').split('static Asset *get_asset(',1)[1].split('\n}',1)[0];self.assertNotIn('ASSET_ENEMY_GOLD_PULSE',generic)
 def test_02_original_animation_dispatch_only(self):
  self.assertIn('sprite == 168 || sprite == 169)',self.text('tyrian2.c'))
  for token in ('enemyShot[','JE_newEnemy','mt_rand','shotMultiPos','enemyShotAvail['):self.assertNotIn(token,self.text('enemy_gold_pulse_mirror.inc'))
 def test_03_eight_distinct_bits_used_dependency(self):
  s=self.text('global_projectile91_mirror.inc');self.assertIn('index==91?1u:index==145?2u:index==61?4u:index==101?8u:index==120?16u:index==139?32u:index==168?64u:index==169?128u:0u',s)
  for i,b in [(168,64),(169,128)]:
   self.assertIn(f'(!(global_projectile91_used_members&{b}u)||projectile_gold_pulse_palette_matches({i}))',s);self.assertIn(f'(!(global_projectile91_used_members&{b}u)||projectile_gold_pulse_resource(global_asset_directory,{i})!=NULL)',s)
  self.assertIn('global_projectile91_used_members|=member;',s)
 def test_04_independent_payload_epochs(self):
  s=self.text('enemy_gold_pulse_mirror.inc');self.assertIn('projectile_gold_pulse_resources[2]',s);self.assertIn('GoldPulseResource *r=&projectile_gold_pulse_resources[slot];',s);self.assertIn('if(!r->checked)',s);self.assertIn('if(!r->valid||strcmp(r->root,root))return NULL;',s)
 def test_05_normal_shared_source_xmas_and_density(self):
  self.assertIn('projectile_gold_pulse_slot(index)>=0&&projectile91_source(bank,91)',self.text('enemy_gold_pulse_mirror.inc'));self.assertIn('game_probe_density==8&&!xmas&&',self.text('global_projectile91_mirror.inc'));self.assertIn('game_probe_density!=8',self.text('enemy_gold_pulse_mirror.inc'))
 def test_06_exact_HDA_payload_and_read_end(self):
  s=self.text('enemy_gold_pulse_mirror.inc')
  for i in (1530168,1530169):self.assertIn(f'CURRENT_PROJECTILE_GOLD_PULSE_{i}_PAYLOAD_FNV',s)
  self.assertIn('v[0]==ASSET_ENEMY_GOLD_PULSE*10000+index&&v[1]==8&&v[2]==12&&v[3]==14&&!v[4]&&!v[5]',s);self.assertIn('REAR_READ(fd,&extra,1)==0',s);self.assertIn('asteroid1_stamp(a->rgba,(size_t)12*14*8*8*4)!=projectile_gold_pulse_pins[slot]',s)
 def test_07_shared_five_palette_not_unique_unused_color(self):
  s=self.text('enemy_gold_pulse_mirror.inc');self.assertIn('indices[]={123,124,125,126,127}',s);self.assertIn('colors[]={0xf3ae24,0xfbcb30,0xffe73c,0xfffb96,0xfffff3}',s);self.assertIn('(rgb_palette[indices[i]]&0xffffffu)!=colors[i]',s)
 def test_08_original_underlay_and_full_cache_guards(self):
  s=self.text('global_projectile91_mirror.inc')
  for token in ('global_projectile91_used_colors[i]&&','for(unsigned i=0;i<256;i++)','global_projectile91_contributed','projectile_gold_pulse_shutdown();'):self.assertIn(token,s)
 def test_09_package_and_rebuilder_register_exact_two(self):
  p=(ROOT/'scripts/package_runtime.py').read_text();r=(ROOT/'scripts/rebuild_recovered_runtime_manifest.py').read_text()
  self.assertIn('from current_projectile_gold_pulse_compatibility import validate_runtime_rows',p);self.assertIn('from current_projectile_gold_pulse_compatibility import load',r)
  self.assertIn("expected_gold={'assets/gameplay/enemy-projectile-gold-pulse-'+str(i)+'-8.hda' for i in (168,169)}",r)
if __name__=='__main__':unittest.main()
