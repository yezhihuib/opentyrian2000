"""Cheap finite contract checks, not native or scene qualification."""
from pathlib import Path
import hashlib,re,struct,unittest
ROOT=Path(__file__).resolve().parents[1]
IDS=(20,21,105,106,124,125)
OLD=(91,145,61,101,120,139,168,169,162,260,166,94,7,45,153,154,155,70)
RLES={20: '0c0c0c0c357679760454767b7d7b7603547b7f7e7f7b03547d7e7f7e7d03547b7d7e7d7b0354787b7d7b7803357679760f', 21: '0c0c0c357679760454767b7d7b7603547b7f7e7f7b03547d7e7f7e7d03547d7e7f7e7d03547d7e7f7e7d03547b7d7e7d7b0354787b7d7b7803357679760f', 105: '0c0c48c5c8c8c60056c6c9c8c6c30164c6c7cccac8c40293c6cacecdcbcac8c6c50082c6cacfcdc8c6c4c20262c9cececbc7c40491c6cdcfcdcbc9c6c3c202b1cacfcfcfcdcbcac9c8c6c400a0c5cdcfcecdcac7c5c4c30280c8cecfcecbc8c6c40490cacfcfcfcccac8c5c403c0cacfcfcfcecbcac8c7c6c5c50f', 106: '0c0c40c6c8c8c50851c3c6c8c9c60662c4c8caccc7c60490c5c6c8cacbcdcecac60382c2c4c6c8cdcfcac60264c4c7cbcecec90292c2c3c6c9cbcdcfcdc601b0c4c6c8c9cacbcdcfcfcfca01a2c3c4c5c7cacdcecfcdc50084c4c6c8cbcecfcec80093c4c5c8cacccfcfcfca00c0c5c5c6c7c8cacbcecfcfcfca0f', 124: '90cacfcfcecdcbc8c5c40380c8cecfcecccac7c404a0c5cdcfcecdcbc7c5c4c302b1cacfcfcfcdcbcac9c8c6c40091c6cdcfcdcac8c6c3c20262c9cececac7c40482c6cacfcdc8c6c4c20293c6cacecdcbcac8c6c50064c6c7cccac8c40256c6c9c8c6c30148c5c8c8c60f', 125: '93c4c5c8cbcdcecfcfca0084c4c7cacccecfcec800a2c3c4c5c7cbcdcecfcdc500b0c4c6c8c9cacbcdcfcfcfca0192c2c3c6c8cacdcfcdc60164c4c7cacecec90282c2c4c6c8cdcfcac60290c5c6c8cacbcdcecac60362c4c8caccc7c60451c3c6c8c9c60640c6c8c8c50f'}
STATS={20: (31, 2299, 2299, 332), 21: (41, 3131, 3129, 507), 105: (97, 5728, 5417, 286), 106: (97, 5728, 5417, 286), 124: (85, 4169, 4116, 218), 125: (85, 4169, 4116, 218)}
UNCHANGED={'src/entity_draw.c': 'e16290b936f6212c7ce3b6a63d758c6b66ec9a0af269ebccd2cac889c83b4529', 'src/enemy_vulcan70_mirror.inc': 'cf166af9221e9543ca684a89c270e47ceafa401952f72989d043bb57e750ef1f', 'src/global_vulcan_mirror.inc': '7f07c65ae3628e81a6b0c58f322c799fc9678679ed2f1a5619d6a6acfe652c1f', 'src/enemy_reuse_mirror.inc': 'ed4dce9e3183c7d5dd31962217849ecebfa46e3fa23cc5f8afd50bc06cf34858', 'src/current_guided_payload_pins.h': '40bb129b5e74080c354c0e5bfa2811dde41b6e1d6810c1fe628eccad255df97c', 'src/current_sonic_payload_pins.h': '82611c0977733cc9fb0d6daad744b607dec9ab6b32de5e8e6c077355570f86a3', 'assets/hd/global-assets-v1/registry.json': 'b224adfc0b12aee5a4753e32aa12e30c8594eb4237727a983148776239162860'}
def function(s,name):
 start=s.index(name+'(');start=s.rfind('\n',0,start)+1;op=s.index('{',start);depth=0
 for end in range(op,len(s)):
  depth+=(s[end]=='{')-(s[end]=='}')
  if not depth:return s[start:end+1]
 raise ValueError('unclosed function')
def decode(raw):
 data=bytes.fromhex(raw);p=o=0;mask=[0]*168;indices=[0]*168
 while data[o]!=15:
  c=data[o];o+=1;p+=c&15;n=c>>4
  for k in range(n):mask[p+k]=1;indices[p+k]=data[o+k]
  p+=n;o+=n
 if o+1!=len(data):raise ValueError('trailing RLE')
 return mask,indices
class WidgetSonicPreparation(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.shared=(ROOT/'src/global_projectile91_mirror.inc').read_text();cls.loader=(ROOT/'src/enemy_widget_sonic_mirror.inc').read_text();cls.policy=(ROOT/'src/enemy_widget_sonic_policy.h').read_text();cls.render=(ROOT/'src/render_mirror.c').read_text();cls.game=(ROOT/'src/tyrian2.c').read_text()
 def test_append_only_24_members_and_bits(self):
  pairs=[(int(a),int(b))for a,b in re.findall(r'index==(\d+)\?(\d+)u',function(self.shared,'global_projectile91_member'))];self.assertEqual(pairs[:24],[(i,1<<k)for k,i in enumerate(OLD+IDS)]);self.assertEqual(sum(b for _,b in pairs[:18]),262143);self.assertEqual(sum(b for _,b in pairs[:24]),16777215)
 def test_24bit_guard_boolean_owners_unchanged(self):
  self.assertIn('#if UINT_MAX < 536870911u',self.shared);self.assertIn('static unsigned global_projectile91_used_members',self.shared);self.assertIn('static Uint8 *global_projectile91_owner,*global_projectile91_foreign;',self.render);self.assertEqual(8388607&8388608,0)
 def test_exact_seven_sparse_contributors(self):
  for name,want in [('sparse_rgba_members',sum(1<<k for k in range(17,24))+(1<<27)),('widget_sonic_members',sum(1<<k for k in range(18,24)))]:
   expr=re.search(r'global_projectile91_'+name+r'=([^;]+);',self.shared)[1];bits=[int(x)for x in re.findall(r'(\d+)u',expr)];self.assertEqual(sum(bits),want);self.assertEqual(len(bits),8 if name.startswith('sparse')else 6)
  f=function(self.shared,'global_projectile91_final_pixel');self.assertIn('(global_projectile91_used_members&global_projectile91_sparse_rgba_members)&&!shared_count&&hd_count',f);self.assertLess(f.index('global_projectile91_cache_decline();return;'),f.index('bool changed=false;'))
 def test_shared_rgba_algorithm_unchanged(self):
  self.assertEqual(hashlib.sha256(function(self.shared,'global_projectile91_draw').encode()).hexdigest(),"b5f6363262b6032efbe43df1c5a569ce0df187118cd6794a8ff67f2606d611fd")
 def test_canonical_player_legacy_and_entity_bytes_unchanged(self):
  for name,pin in UNCHANGED.items():self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),pin,name)
 def test_original_rle_palette_and_halo_contract(self):
  for i in IDS:
   mask,indices=decode(RLES[i]);family='guided'if i<100 else'sonic';raw=(ROOT/f'assets/hd/current-compat/{family}/bullet-{i}-8.hda').read_bytes();self.assertEqual(struct.unpack('<4s6I',raw[:28]),(b'HDR1',80000+i,8,12,14,0,0));rgba=raw[28:];nz=soft=outside=0
   for n in range(10752):
    a=rgba[4*n+3];nz+=a>0;soft+=0<a<255;outside+=bool(a and not mask[(n//96//8)*12+n%96//8])
   self.assertEqual((sum(mask),nz,soft,outside),STATS[i]);self.assertEqual({x for x,m in zip(indices,mask)if m},set((118,120,121,123,125,126,127))if i<100 else set(range(194,208)))
 def test_exact_palette_contract_not_all256_hash(self):
  self.assertIn('warm_indices[7]={118,120,121,123,125,126,127}',self.loader);self.assertIn('rgb_palette[194+i]',self.loader);self.assertNotIn('5e80e83992be2927',self.loader)
 def test_independent_finite_leases_and_strict_headers(self):
  self.assertIn('enemy_widget_sonic_resources[6]',self.loader);self.assertIn('v[0]==80000u+enemy_widget_sonic_specs[k].index',self.loader)
  for text in ('REAR_REGULAR','REAR_READ(fd,&extra,1)==0','if(REAR_CLOSE(fd))ok=false','a->bank!=8','a->index!=index','a->density!=8','strcmp(enemy_widget_sonic_resources[k].root,root)','enemy_widget_sonic_specs[k].payload'):self.assertIn(text,self.loader)
  self.assertNotIn('global_vulcan_rgba',self.loader);self.assertNotIn('enemy_reuse_resources',self.loader);self.assertNotIn('game_probe_assets',self.loader)
 def test_source_bank_and_lane_intent_closed(self):
  self.assertIn('!widget_sonic_legacy_intent()&&projectile91_source(bank,91)',self.loader);self.assertIn('global_projectile91_used_members&global_projectile91_widget_sonic_members',function(self.shared,'global_projectile91_source_matches'));self.assertIn('!widget_sonic_legacy_intent()',function(self.shared,'global_projectile91_source_matches'))
 def test_legacy_requested_not_active_and_macrooff(self):
  self.assertIn('game_probe_enabled||enemy_reuse_observe_requested()||enemy_reuse_probe_requested()',self.policy);self.assertNotIn('observe_active()',self.policy);self.assertNotIn('probe_generation()',self.policy);self.assertIn('#else\n return false;',self.policy);self.assertIn('!defined(RENDER_MIRROR_DISABLED)',self.policy)
 def test_one_routing_branch_and_direct_admission_gate(self):
  text='if ((widget_sonic_member_index(sprite) && widget_sonic_legacy_intent()) || sprite == 214 || sprite == 215 || sprite == 216 || (orb_protron_protron_index(sprite) && widget_sonic_legacy_intent()))';self.assertEqual(self.game.count(text),1);self.assertIn('|| sprite == 70 || widget_sonic_member_index(sprite) || orb_protron_protron_index(sprite))',self.game);self.assertIn('if(widget_sonic_member_index(index)&&widget_sonic_legacy_intent())return false;',function(self.render,'render_mirror_enemy_shot'))
 def test_used_resource_palette_checks_and_shutdown(self):
  for i,k in zip(IDS,range(18,24)):
   self.assertIn(f'(!(global_projectile91_used_members&{1<<k}u)||enemy_widget_sonic_resource(global_asset_directory,{i})!=NULL)',self.shared);self.assertIn(f'(!(global_projectile91_used_members&{1<<k}u)||enemy_widget_sonic_palette_matches({i}))',self.shared)
  self.assertIn('enemy_widget_sonic_shutdown();',function(self.shared,'global_projectile91_shutdown'))
if __name__=='__main__':unittest.main()
