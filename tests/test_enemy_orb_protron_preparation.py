"""Finite cheap contracts only; no native/game or artwork generation."""
from pathlib import Path
import hashlib,re,struct,unittest
ROOT=Path(__file__).resolve().parents[1]
IDS=(112, 113, 226, 227)
OLD=(91, 145, 61, 101, 120, 139, 168, 169, 162, 260, 166, 94, 7, 45, 153, 154, 155, 70, 20, 21, 105, 106, 124, 125)
SPECS={112: (1420112, '84546804885d7c602449fe0c4783d1873e60f30a8abde3e3095356fc3d8bd720', 'assets/hd/current-compat/enemy-orb/enemy-orb112113-112-8.hda'), 113: (1420113, '20a9b6480d91a324a4ca375e79f596504103a80f165512fa33d8c5ffeeac7fba', 'assets/hd/current-compat/enemy-orb/enemy-orb112113-113-8.hda'), 226: (80226, '231a78b2ebc6a2410da297d05703b4c548f38926e7bd6e6b28c4fe6c4fa7071c', 'assets/hd/current-compat/protron/bullet-226-8.hda'), 227: (1470227, '9de332ec5d8d7f5c0e7eb56445aabebe22897b27a6fde1ee7f36da822076aac7', 'assets/hd/current-compat/protron/enemy-protron-p09-227-8.hda')}
MASKS={112: '000000000000000000000000000000000000000000000000000011111000000111111100000111111100000111111100000111111100000111111100000011111000000000000000000000000000000000000000', 113: '000000000000000000000000000000000000000000000000000011111000000111111100000111111100000111111100000111111100000111111100000011111000000000000000000000000000000000000000', 226: '000000000000000000000000000000000000000000000000000011100000000111110000000111110000000111110000000011100000000000000000000000000000000000000000000000000000000000000000', 227: '000000000000000000000000000000000000000111110000001111111000001111111000001111111000001111111000001111111000000111110000000000000000000000000000000000000000000000000000'}
PALETTES={112: {112: 2097152, 114: 5308416, 117: 10356736, 118: 12192768, 122: 15436312, 124: 16501552, 119: 13833216, 123: 15969828, 127: 16777203, 121: 15163660}, 113: {112: 2097152, 115: 7144448, 116: 8782848, 120: 14629888, 121: 15163660, 125: 16770876, 126: 16776086, 122: 15436312, 127: 16777203, 124: 16501552}, 226: {140: 12247011, 138: 10144719, 143: 15728639, 137: 9092807, 136: 8237754, 135: 7186098, 132: 5079698, 134: 6396582}, 227: {130: 3697021, 139: 10933207, 138: 10144719, 134: 6396582, 143: 15728639, 141: 13364203, 135: 7186098, 137: 9092807, 132: 5079698, 133: 5607070, 131: 4289930, 129: 2907509}}
STATS={112: (45, 2819, 2819, 0), 113: (45, 2849, 2849, 0), 226: (21, 1263, 1263, 0), 227: (45, 2552, 2552, 2)}
UNIONS={112: 2880, 113: 2880, 226: 1344, 227: 2882}
UNCHANGED={'src/entity_draw.c': 'e16290b936f6212c7ce3b6a63d758c6b66ec9a0af269ebccd2cac889c83b4529', 'src/asteroid1_enemy_orb112113_mirror.inc': '7d3f8ccaf7c96d60c066b8cb48c0e451acce67632cea0db9bbb7df05fc8ff096', 'src/enemy_reuse_mirror.inc': 'ed4dce9e3183c7d5dd31962217849ecebfa46e3fa23cc5f8afd50bc06cf34858', 'src/enemy_widget_sonic_policy.h': '1ad42113a0b865be93909abe47810e50d25203f4f58c727f47c91d3e07237f06', 'src/enemy_widget_sonic_mirror.inc': '63f13d0004a8790810b8ab5fc60f33d191b5d25cec1cc87d24d69b1b2429483b', 'src/global_vulcan_mirror.inc': '7f07c65ae3628e81a6b0c58f322c799fc9678679ed2f1a5619d6a6acfe652c1f', 'src/current_enemy_orb_payload_pins.h': '90c8d67b5ea3ee0153fa5c9f40141fdf572b0a1cc5927b2b4c656b8d84e7f9f8', 'src/current_protron_payload_pins.h': 'bf982da11154061bdf56683270ef23a12200f014a060cfcf6482b97d31de88fb', 'assets/hd/global-assets-v1/registry.json': 'b224adfc0b12aee5a4753e32aa12e30c8594eb4237727a983148776239162860'}
DRAW_SHA='b5f6363262b6032efbe43df1c5a569ce0df187118cd6794a8ff67f2606d611fd'
TYRIAN_SHA='a4a30937d1432b42bee3452c2e819331aeb340b00baba4cbdfd613986f642976'
def function(s,name):
 start=s.index(name+'(');start=s.rfind('\n',0,start)+1;op=s.index('{',start);depth=0
 for end in range(op,len(s)):
  depth+=(s[end]=='{')-(s[end]=='}')
  if not depth:return s[start:end+1]
 raise ValueError('Unclosed function')
class OrbProtronPreparation(unittest.TestCase):
 def src(self,name):return(ROOT/'src'/name).read_text()
 def test_old24_append_only_28bits(self):
  body=function(self.src('global_projectile91_mirror.inc'),'global_projectile91_member');pairs=[(int(a),int(b))for a,b in re.findall(r'index==(\d+)\?(\d+)u',body)];self.assertEqual(pairs[:28],list(zip(OLD+IDS,[1<<n for n in range(28)])));self.assertEqual(sum(b for a,b in pairs[:28]),268435455)
 def test_width_and_boolean_owner_separate(self):
  s=self.src('global_projectile91_mirror.inc');self.assertIn('UINT_MAX < 2147483647u',s);self.assertIn('static Uint8 *global_projectile91_owner',self.src('render_mirror.c'));self.assertNotIn('uint8_t global_projectile91_used_members',s)
 def test_only227_adds_sparse_contribution(self):
  s=self.src('global_projectile91_mirror.inc');line=next(x for x in s.splitlines()if x.startswith('static const unsigned global_projectile91_sparse_rgba_members='));bits=list(map(int,re.findall(r'(\d+)u',line)));self.assertEqual(bits,[1<<n for n in range(17,24)]+[1<<27,1<<29,1<<30]);self.assertIn('global_projectile91_used_members&global_projectile91_sparse_rgba_members',s)
 def test_exact_material_headers_and_bytes(self):
  for i,(identity,pin,path)in SPECS.items():
   raw=(ROOT/path).read_bytes();self.assertEqual(hashlib.sha256(raw).hexdigest(),pin);self.assertEqual(raw,(ROOT/'assets/hd/global-assets-v1/content'/(pin+'.hda')).read_bytes());self.assertEqual(struct.unpack('<4s6I',raw[:28]),(b'HDR1',identity,8,12,14,0,0))
 def test_exact_native_union_alpha_and_two_halo_points(self):
  for i,(identity,pin,path)in SPECS.items():
   a=(ROOT/path).read_bytes()[28:];mask=MASKS[i];alpha=a[3::4];outside=[(n%96,n//96,v)for n,v in enumerate(alpha)if v and mask[n//96//8*12+n%96//8]=='0'];self.assertEqual((sum(c=='1'for c in mask),sum(v!=0 for v in alpha),sum(0<v<255 for v in alpha),len(outside)),STATS[i]);self.assertEqual(outside,[(23,31,2),(64,72,1)]if i==227 else[]);self.assertEqual(sum(mask[n//96//8*12+n%96//8]=='1'or v!=0 for n,v in enumerate(alpha)),UNIONS[i])
 def test_per_phase_palette_not_family_union(self):
  s=self.src('enemy_orb_protron_mirror.inc')
  for i,wanted in PALETTES.items():
   body=s.split('if(index==%d){'%i,1)[1].split('return true;}',1)[0];indices=list(map(int,re.search(r'indices\[\d+\]=\{([^}]+)',body)[1].split(',')));colors=[int(x,16)for x in re.search(r'colors\[\d+\]=\{([^}]+)',body)[1].split(',')];self.assertEqual(dict(zip(indices,colors)),wanted)
 def test_strict_independent_four_root_leases(self):
  s=self.src('enemy_orb_protron_mirror.inc');self.assertIn('resources[5]',s)
  for token in ('REAR_REGULAR','st.st_size','REAR_READ(fd,&extra,1)==0','REAR_CLOSE(fd)','strcmp(enemy_orb_protron_resources[k].root,root)','a->bank!=enemy_orb_protron_specs[k].identity/10000u','a->index!=index','a->density!=8','asteroid1_stamp(a->rgba','v[0]==enemy_orb_protron_specs[k].identity'):self.assertIn(token,s)
  self.assertNotIn('80000u+',s);self.assertNotIn('enemy_orb112113_family_ready',s)
 def test_policy_keeps_separate_legacy_regimes(self):
  s=self.src('enemy_orb_protron_policy.h');self.assertIn('if(orb_protron_orb_index(index))return !asteroid_hd_enabled;',s);self.assertIn('if(orb_protron_protron_index(index))return !widget_sonic_legacy_intent();',s);self.assertIn('if(enemy_reuse_observe_requested())return false;',s)
 def test_global_intent_authoritative_no_wrong_orb_fallback(self):
  s=function(self.src('render_mirror.c'),'render_mirror_enemy_shot');a=s.index('if(orb_protron_member_index(index)');b=s.index('/* These shared enemy roles',a);body=s[a:b];self.assertIn('!(orb_protron_orb_index(index)&&asteroid_hd_enabled)',body);self.assertIn('if(global_asset_directory[0])',body);self.assertIn('if(!orb_protron_ordinary_allowed(index))return false;',body);self.assertIn('return global_projectile91_draw(surface,x,y,bank,index)>0;',body);self.assertIn('if(orb_protron_protron_index(index))return false;',body);self.assertGreater(s.index('Asset *a=&assets[218+'),b);self.assertIn('a->valid=read_asset(a,4)',s)
 def test_per_used_palette_resource_and_intent(self):
  s=self.src('global_projectile91_mirror.inc')
  for n,i in enumerate(IDS,24):
   self.assertIn('global_projectile91_used_members&%du'%(1<<n),s);self.assertIn('orb_protron_ordinary_allowed(%d)&&enemy_orb_protron_resource(global_asset_directory,%d)!=NULL'%(i,i),s);self.assertIn('enemy_orb_protron_palette_matches(%d)'%i,s)
 def test_whole_bank_source_and_shutdown(self):
  s=self.src('enemy_orb_protron_mirror.inc');self.assertIn('orb_protron_ordinary_allowed(index)&&projectile91_source(bank,91)',s);self.assertIn('enemy_orb_protron_shutdown();',self.src('global_projectile91_mirror.inc'));self.assertIn('i<5;i++)free(enemy_orb_protron_resources[i].member.rgba)',s)
 def test_existing_rgba_draw_body_unchanged(self):self.assertEqual(hashlib.sha256(function(self.src('global_projectile91_mirror.inc'),'global_projectile91_draw').encode()).hexdigest(),DRAW_SHA)
 def test_old_renderers_players_and_payload_pins_unchanged(self):
  for name,pin in UNCHANGED.items():self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),pin,name)
 def test_original_tyrian2_exact_inverse_no_game_changes(self):
  s=self.src('tyrian2.c');changes=[('#include "enemy_orb_protron_policy.h"\n',''),('|| (orb_protron_protron_index(sprite) && widget_sonic_legacy_intent()))','|| sprite == 226 || sprite == 227 || sprite == 244)'),('|| widget_sonic_member_index(sprite) || orb_protron_protron_index(sprite))','|| widget_sonic_member_index(sprite))')]
  for a,b in changes:self.assertEqual(s.count(a),1);s=s.replace(a,b,1)
  self.assertEqual(hashlib.sha256(s.encode()).hexdigest(),TYRIAN_SHA)
if __name__=='__main__':unittest.main()
