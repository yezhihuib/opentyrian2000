"""Small static integration checks; no runtime, native callback or game proof."""
from pathlib import Path
import hashlib,re,unittest
ROOT=Path(__file__).resolve().parents[1]
class BlueTripletRuntimeContract(unittest.TestCase):
 def text(self,name):
  import projectile_gold_pulse_projection as newest
  path='src/'+name;raw=newest.project_source(path,(ROOT/path).read_bytes())
  assert newest.sha(raw)==newest.ledger()['base_source_inventory'][path],('qualified blue source drift',path)
  return raw.decode()
 def test_enemy_only_dispatch_has_original_blit_once(self):
  s=self.text('entity_draw.c').split('void draw_enemy_shot_sprite2(',1)[1].split('/* Original sidekick',1)[0]
  self.assertEqual(s.count('blit_sprite2(target,x,y,bank,index);'),1)
  self.assertEqual(s.count('render_mirror_entity_end();'),1)
  self.assertIn('game_probe_scene_draw(152,index,x,y,0,ENTITY_NORMAL,mirrored)',s)
  s=self.text('render_mirror.c')
  self.assertEqual(s.count('ASSET_ENEMY_BLUE_TRIPLET=152'),1)
  self.assertIn('if(index==145||index==61||index==101||index==120||index==139)',s)
  # New role is not installed into the generic/player asset switch.
  generic=s.split('static Asset *get_asset(',1)[-1].split('\n}',1)[0]
  self.assertNotIn('ASSET_ENEMY_BLUE_TRIPLET',generic)
 def test_original_three_independent_shot_dispatch(self):
  s=self.text('tyrian2.c');self.assertIn('sprite == 61 || sprite == 101 || sprite == 120 || sprite == 139)',s)
  # No new batching, coordinate adjustment or creation helper in the loader.
  loader=self.text('enemy_blue_triplet_mirror.inc')
  for forbidden in ['enemyShot[','JE_newEnemy','mt_rand','shotMultiPos','enemyShotAvail[']:
   self.assertNotIn(forbidden,loader)
 def test_six_distinct_bits_and_used_dependency_guards(self):
  s=self.text('global_projectile91_mirror.inc')
  self.assertIn('index==91?1u:index==145?2u:index==61?4u:index==101?8u:index==120?16u:index==139?32u:0u',s)
  for index,bit in [(101,8),(120,16),(139,32)]:
   self.assertIn(f'(!(global_projectile91_used_members&{bit}u)||projectile_blue_triplet_palette_matches({index}))',s)
   self.assertIn(f'(!(global_projectile91_used_members&{bit}u)||projectile_blue_triplet_resource(global_asset_directory,{index})!=NULL)',s)
  self.assertIn('global_projectile91_used_members|=member;',s)
  self.assertIn('if(global_projectile91_used_members&member)global_projectile91_fail();return 0;',s)
 def test_optional_resources_have_independent_epochs(self):
  s=self.text('enemy_blue_triplet_mirror.inc')
  self.assertIn('projectile_blue_triplet_resources[3]',s)
  self.assertIn('BlueTripletResource *r=&projectile_blue_triplet_resources[slot];',s)
  self.assertIn('if(!r->checked)',s)
  self.assertIn('if(!r->valid||strcmp(r->root,root))return NULL;',s)
  self.assertIn('r->valid=false;return NULL;',s)
  self.assertNotIn('for(unsigned i=0;i<3;i++)projectile_blue_triplet_load',s)
 def test_full_normal_bank_and_explicit_christmas_decline(self):
  self.assertIn('projectile_blue_triplet_slot(index)>=0&&projectile91_source(bank,91)',self.text('enemy_blue_triplet_mirror.inc'))
  self.assertIn('game_probe_density==8&&!xmas&&',self.text('global_projectile91_mirror.inc'))
  self.assertIn('game_probe_density!=8',self.text('enemy_blue_triplet_mirror.inc'))
 def test_exact_headers_and_per_member_payload_checks(self):
  s=self.text('enemy_blue_triplet_mirror.inc')
  for identity in [1520101,1520120,1520139]:self.assertIn(f'CURRENT_PROJECTILE_BLUE_TRIPLET_{identity}_PAYLOAD_FNV',s)
  self.assertIn('v[0]==ASSET_ENEMY_BLUE_TRIPLET*10000+index&&v[1]==8&&v[2]==12&&v[3]==14&&!v[4]&&!v[5]',s)
  self.assertIn('REAR_READ(fd,&extra,1)==0',s)
  self.assertIn('a->bank!=ASSET_ENEMY_BLUE_TRIPLET||a->index!=index',s)
  self.assertIn('asteroid1_stamp(a->rgba,(size_t)12*14*8*8*4)!=projectile_blue_triplet_pins[slot]',s)
 def test_actual_palette_sets_remain_member_specific(self):
  s=self.text('enemy_blue_triplet_mirror.inc')
  expected={101:[138,140,141,142,143,145,146,147,148,149,150,151,152,153,154,155,156,157,159],120:[140,145,149,153,156,159],139:[138,140,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159]}
  for index,values in expected.items():
   body=s.split(f'case {index}: {{',1)[1].split('return true;',1)[0]
   self.assertIn('indices[]={'+','.join(map(str,values))+'}',body)
   self.assertIn('(rgb_palette[indices[i]]&0xffffffu)!=colors[i]',body)
 def test_underlay_and_cached_full_palette_unchanged(self):
  s=self.text('global_projectile91_mirror.inc')
  self.assertIn('global_projectile91_used_colors[i]&&',s)
  self.assertIn('for(unsigned i=0;i<256;i++)',s)
  self.assertIn('global_projectile91_contributed',s)
  self.assertIn('projectile_blue_triplet_shutdown();',s)
 def test_package_hook_is_alias_aware_not_generic_role_alias(self):
  s=(ROOT/'scripts/package_runtime.py').read_text()
  self.assertIn('from current_projectile_blue_triplet_compatibility import validate_runtime_rows as blue_triplet_validate',s)
  self.assertIn("blue_triplet_validate(roots[0],manifest,manifest_path.resolve()==(roots[0]/'packaging/runtime-assets-v1.json').resolve())",s)
if __name__=='__main__':unittest.main()
