"""Finite source contracts only; not native execution or scene qualification."""
from pathlib import Path
import hashlib,re,unittest
ROOT=Path(__file__).resolve().parents[1]
OLD_IDS=(91,145,61,101,120,139,168,169,162,260,166,94)
# Immutable old payload/resource code, not pins of a changing shared TU.
OLD_FILES={'src/current_plasma_projectile_payload_pins.h': 'e8c6f7497df9a88d3653675136af8c9c727d85eba2328eddb03b2f69f2d89283', 'src/current_projectile_blue_triplet_payload_pins.h': '857978d85a52b73a8c0a8bd9ba318a13da715db12d3ffd168e22f35a778874c8', 'src/current_projectile145_payload_pins.h': '1e340c2733faa1f3d813ba63d158c1e030df84732ccaf0b7d40aa905eae96f34', 'src/current_projectile_pulses16694_payload_pins.h': '898a2e8264649ed9bcd97be30f87f77b41c15a29ea3fe188e07f13bdf3f77854', 'src/current_projectile61_payload_pins.h': 'ae692f06789a8b0d8f7dab518cb06e5f86dc563bdb07778497e5701d3dfe2916', 'src/current_projectile_gold_pulse_payload_pins.h': '2e13023af89d7c627a65d3d3fa16996edc301be643862733d8925013513bb133', 'src/current_projectile_statics_payload_pins.h': '2b859dba5213af576fc2aadf76ddacabc59df3fc5e1ca1a8da863ddf2d93f90b', 'src/current_projectile91_payload_pins.h': '6f3cc6accda71244820e84e3d9fcdc434a100b630b52843cf0e7000731682779', 'src/enemy_projectile61_mirror.inc': '575dce9cd0968b1be999ffe97aba1ec9756d58f9dd098d2e7059aa6b897b1fc1', 'src/enemy_projectile91_mirror.inc': '64fe9cc941ddc6d2bd71bf4b34a25154b9bd86695af60023e56f1c2a39d2f497', 'src/enemy_projectile145_mirror.inc': '97eac301c1ebd8b8aae6ebaf7dee31260010aa84f87f23398229cf2ccd60e402', 'src/enemy_blue_triplet_mirror.inc': '28b1df9e56a2d90715ba9de6ef01cb249ae9a429990b1a3b151597c6d37e14fe', 'src/enemy_pulses16694_mirror.inc': 'e6d0a7ff0e8dbc28fae4a5225e22ee56ddd318765638476c03f0a9bb537205bd'}

def function(text,name):
 start=text.index(name+'(');start=text.rfind('\n',0,start)+1;op=text.index('{',start);depth=0
 for end in range(op,len(text)):
  depth+=(text[end]=='{')-(text[end]=='}')
  if not depth:return text[start:end+1]
 raise AssertionError('Unclosed function')

class Bolts745RuntimeContract(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.shared=(ROOT/'src/global_projectile91_mirror.inc').read_text();cls.loader=(ROOT/'src/enemy_bolts745_mirror.inc').read_text();cls.render=(ROOT/'src/render_mirror.c').read_text();cls.entity=(ROOT/'src/entity_draw.c').read_text();cls.game=(ROOT/'src/tyrian2.c').read_text()
 def test_append_only_member_bits(self):
  f=function(self.shared,'global_projectile91_member');pairs=re.findall(r'index==(\d+)\?(\d+)u',f)
  self.assertEqual([(int(i),int(b))for i,b in pairs],[(i,1<<k)for k,i in enumerate((*OLD_IDS,7,45,153,154,155,70,20,21,105,106,124,125,112,113,226,227))])
 def test_old_resource_files_unchanged(self):
  for name,pin in OLD_FILES.items():self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),pin,name)
 def test_new_independent_member_state(self):
  for token in ('resources[2]','indices[2]={7,45}','index==7?0:index==45?1:-1','bool checked,valid','char root[1024]','strcmp(r->root,root)','r->valid=false;return NULL;','projectile91_source(bank,91)'):self.assertIn(token,self.loader)
 def test_namespace_and_generic_exclusion(self):
  self.assertIn('ASSET_ENEMY_BOLTS745=156',self.render)
  self.assertIn('if(a->bank==ASSET_ENEMY_BOLTS745)return false;',function(self.render,'read_asset'))
  self.assertIn('ASSET_ENEMY_BOLTS745*10000+index',self.loader)
 def test_exact_transport_geometry_and_payload_pin(self):
  for token in ('12*14*8*8*4','st_size==(long)(28+bytes)','REAR_READ(fd,&extra,1)==0','v[1]==8&&v[2]==12&&v[3]==14&&!v[4]&&!v[5]','asteroid1_stamp(rgba,bytes)==projectile_bolts745_pins[slot]','a->w!=12||a->h!=14||a->anchor_x||a->anchor_y||a->density!=8'):self.assertIn(token,self.loader)
 def test_dynamic_index_resolution_old_rgba_branch(self):
  draw=function(self.shared,'global_projectile91_draw')
  self.assertIn('resource->bank==ASSET_ENEMY_BOLTS745&&(index==7||index==45)',draw);self.assertIn('rgb_palette[a[0]]&0xffffffu',draw);self.assertIn('global_projectile91_use_color(a[0]);',draw)
  self.assertIn('}else *p=blend_rgba(*p,a,(int)alpha);',draw)
  self.assertNotIn('0xffe73c',self.loader);self.assertNotIn('0xffe73c',draw)
 def test_palette_admission_distinct_from_temporal_integrity(self):
  self.assertEqual(function(self.loader,'projectile_bolts745_palette_matches').split('\n')[-1],'{return projectile_bolts745_slot(index)>=0;}')
  for token in ('global_projectile91_underlay_matches()','global_projectile91_output_palette','memcmp(global_projectile91_output_palette,rgb_palette','global_projectile91_fade_step_valid'):self.assertIn(token,self.shared)
 def test_role_only_dispatch(self):
  self.assertIn('index==7||index==45',function(self.render,'render_mirror_enemy_shot'))
  self.assertIn('game_probe_scene_draw(156,index,x,y,0,ENTITY_NORMAL,mirrored)',function(self.entity,'draw_enemy_shot_sprite2'))
  self.assertIn('|| sprite == 7 || sprite == 45 || sprite == 153 || sprite == 154 || sprite == 155 || sprite == 70 || widget_sonic_member_index(sprite) || orb_protron_protron_index(sprite))',self.game)
 def test_retained_layout_source_and_fault_gates(self):
  for token in ('!xmas','surface!=game_screen','surface!=VGAScreen','global_projectile91_source_matches(spriteSheet8)','global_projectile91_surface_matches()','global_projectile91_call.live','global_projectile91_call.mask','global_projectile91_used_members&member','global_projectile91_finish_proof','global_projectile91_check_cache'):self.assertIn(token,self.shared)
 def test_canonical_argb_masks_shifts_losses(self):
  f=function(self.shared,'global_projectile91_argb_format')
  for token in ('Rmask==0x00ff0000u','Gmask==0x0000ff00u','Bmask==0x000000ffu','Amask==0xff000000u','Rshift==16','Gshift==8','!f->Bshift','Ashift==24','!f->Rloss&&!f->Gloss&&!f->Bloss&&!f->Aloss'):self.assertIn(token,f)
  self.assertIn('global_projectile91_argb_format(v->format)',function(self.shared,'global_projectile91_layout'))
  self.assertIn('global_projectile91_argb_format(s->format)',function(self.shared,'global_projectile91_fade_buffer_layout'))
 def test_shutdown_extension(self):
  self.assertIn('projectile_bolts745_shutdown();',function(self.shared,'global_projectile91_shutdown'))
  self.assertIn('#include "enemy_bolts745_mirror.inc"',self.render)
 def test_no_assisted_fixture_in_production(self):
  for raw in (self.shared,self.loader,self.render,self.entity,self.game):
   self.assertNotIn('invulnerable = 2000',raw);self.assertNotIn('BOLTS745OBS',raw)
if __name__=='__main__':unittest.main()
