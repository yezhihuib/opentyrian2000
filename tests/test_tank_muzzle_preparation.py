"""Finite Tank muzzle registration source/geometry contracts; no private inputs."""
import hashlib,re,struct,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
import sys
sys.path.insert(0,str(ROOT/'scripts'))
import current_tank_muzzle_source_bridge as bridge
import current_warning_source_bridge as warning_bridge
from current_tank_muzzle_source_bridge import BASE_PINS,INVERSE,restore

def availability_write_targets(text):
 return re.findall(r'enemyShotAvail\s*\[([^\]]+)\]\s*=(?!=)',text)
class TankMuzzlePreparationTests(unittest.TestCase):
 def src(self,n):return (ROOT/'src'/n).read_text()
 def test_six_exact_inverse_original_pins(self):
  for n in INVERSE:
   with self.subTest(path=n):restore(n,(ROOT/n).read_text())
 def test_inverse_missing_duplicate_unrelated_rejected(self):
  for n,pairs in INVERSE.items():
   s=(ROOT/n).read_text();new,old=pairs[0]
   for bad in (s.replace(new,old,1),s+new,s+'\n/* unrelated */\n'):
    with self.subTest(path=n),self.assertRaises(ValueError):restore(n,bad)
 def test_birth_finite_actual_actor_bank_not_table_guess(self):
  s=self.src('tyrian2.c')
  for text in ('enemytype!=194','size!=1','enemycycle<1','enemycycle>20','enemycycle-1]!=93','enemySpriteSheetIds[k]==20','weapon!=3||turret!=2||phase!=0','shot->sgr!=147','shot->sxm!=3||shot->sym!=3','weapons[weapon].aim'):
   self.assertIn(text,s)
 def test_all_simulation_availability_writes_hooked(self):
  s=self.src('tyrian2.c');self.assertEqual(s.count('enemyShotAvail[b] = !enemyShotAvail[b];'),1);self.assertEqual(s.count('enemyShotAvail[z] = true;'),2);self.assertEqual(s.count('enemyShotAvail[i] = 1;'),1)
  self.assertEqual(s.count('tank_muzzle_allocate(b);'),1);self.assertEqual(s.count('tank_muzzle_birth(b,i,temp3,j,tempPos);'),1);self.assertEqual(s.count('tank_muzzle_retire(z);'),2);self.assertEqual(s.count('memset(tank_muzzle_shots, 0, sizeof(tank_muzzle_shots));'),1)
 def test_availability_write_inventory_rejects_new_assignment(self):
  s=self.src('tyrian2.c');expected=['b','i','z','z'];self.assertEqual(availability_write_targets(s),expected)
  self.assertNotEqual(availability_write_targets(s+'\nenemyShotAvail[q] = 1;'),expected)
 def test_generation_birth_motion_and_poison(self):
  s=self.src('tyrian2.c')
  for t in ('generation<UINT64_MAX','birth_generation==tank_muzzle_shots[slot].generation','age>=1&&age<=255','tank_muzzle_shots[slot].x+3*age','tank_muzzle_shots[slot].y+3*age','if(tank_muzzle_shots[slot].rejected)return -1;','rejected=true;return -1;'):
   self.assertIn(t,s)
  reject=s.split('if (muzzle_registration < 0)',1)[1].split('else if (muzzle_registration > 0)',1)[0]
  self.assertIn('spriteSheet8, sprite)',reject);self.assertNotIn('render_mirror_enemy_shot(',reject);self.assertLess(s.index('int muzzle_registration = tank_muzzle_draw('),s.index('if (enemyShot[z].sgr >= 500)'))
 def test_typed_wrapper_original_indexed_call_once(self):
  s=self.src('entity_draw.c').split('void draw_tank147_muzzle_sprite2',1)[1].split('/* The indexed original',1)[0]
  self.assertEqual(s.count('blit_sprite2(target,x,y,bank,147);'),1);self.assertEqual(s.count('render_mirror_entity_end();'),1);self.assertNotIn('x+1',s);self.assertNotIn('y-1',s)
 def test_legacy_shadow_and_off_contract(self):
  s=self.src('render_mirror.c').split('bool render_mirror_tank147_muzzle',1)[1].split('/* Enemy-only',1)[0]
  self.assertLess(s.index('return render_mirror_enemy_shot'),s.index('render_mirror_shadow_end();'));self.assertLess(s.index('render_mirror_shadow_end();'),s.index('global_projectile91_observed_preflight();'))
  self.assertIn('if(!render_mirror_tank147_muzzle_lane())',s);self.assertIn('return global_asset_directory[0]&&tank_shared_ordinary_allowed(147);',self.src('render_mirror.c'));self.assertIn('if (!render_mirror_tank147_muzzle_lane()) muzzle_registration = 0;',self.src('tyrian2.c'));self.assertIn('#define render_mirror_tank147_muzzle(...) false',self.src('render_mirror.h'))
 def test_original_call_coordinate_and_single_union_blend(self):
  s=self.src('global_projectile91_mirror.inc')
  self.assertIn('global_projectile91_call.x=x;global_projectile91_call.y=y;',s);self.assertIn('int rx=ax-(tank_muzzle?d:0),ry=ay+(tank_muzzle?d:0);',s);self.assertIn('bool native=ax<12*d&&ay>=0&&',s);self.assertIn('if(!a[3]&&!native)continue;',s)
 def test_complete_viewport_and_font_envelope(self):
  s=self.src('global_projectile91_mirror.inc');self.assertIn('tank_muzzle&&(index!=147||x<24||x>275||y<1||y>170)',s);self.assertIn('font_before_effect(tank_muzzle?(SDL_Rect){x,y-1,13,15}',s)
  self.assertLess(s.index('if(tank_muzzle&&'),s.index('unsigned member=global_projectile91_member(index);',s.index('static int global_projectile91_draw_registered')))
 def test_density4_remains_rejected(self):
  self.assertIn('if(d!=8||!game_screen',self.src('global_projectile91_mirror.inc'))
 def test_generic_draw_registration_false(self):
  self.assertIn('return global_projectile91_draw_registered(surface,x,y,bank,index,false);',self.src('global_projectile91_mirror.inc'))
 def test_no_new_gameplay_struct_or_asset_change(self):
  s=self.src('tyrian2.c');side=s.split('static struct { bool valid,rejected;',1)[1].split('boss_bar_t boss_bar',1)[0]
  self.assertNotIn('enemyShot[slot].sx=',side);self.assertNotIn('enemyShot[slot].sy=',side);self.assertIn('const EnemyShotType *shot=&enemyShot[slot];',side)
 def source_inventory_without_generated_header(self):
  return {p.relative_to(ROOT).as_posix():sha(p.read_bytes())for p in sorted((ROOT/'src').rglob('*'))if p.is_file()and p.name!='current_tank_shell_payload_pins.h'}
 def test_projection_exact_current_six_real_reads(self):
  sources=self.source_inventory_without_generated_header();seen=[]
  def read(name):seen.append(name);return(ROOT/name).read_bytes()
  projected=bridge.project(sources,read)
  self.assertEqual(seen,list(warning_bridge.COMBINED_PINS)+[n for n in bridge.MUZZLE_PINS if n not in warning_bridge.COMBINED_PINS]);self.assertEqual(bridge.inventory_digest(projected),bridge.BASE_SOURCE_DIGEST)
  self.assertEqual({n for n in sources if sources[n]!=projected[n]},set(bridge.MUZZLE_PINS)|set(warning_bridge.COMBINED_PINS));self.assertEqual(bridge.inventory_digest(sources),warning_bridge.COMBINED_SOURCE_DIGEST)
 def test_projection_unknown_mixed_missing_inventory_fail_before_io(self):
  sources=self.source_inventory_without_generated_header();name=next(iter(bridge.MUZZLE_PINS))
  missing=dict(sources);del missing[name]
  mixed=dict(sources);mixed[name]=bridge.BASE_PINS[name]
  changed=dict(sources);changed[name]='0'*64
  for bad in (missing,mixed,changed,dict(sources,unexpected='0'*64)):
   with self.subTest(inventory=len(bad)),self.assertRaises(ValueError):bridge.project(bad,lambda n:self.fail('Rejected inventory must not read source'))
 def test_projection_actual_bytes_cannot_hide_behind_valid_inventory(self):
  sources=self.source_inventory_without_generated_header()
  for target in dict.fromkeys((*warning_bridge.COMBINED_PINS,*bridge.MUZZLE_PINS)):
   with self.subTest(path=target),self.assertRaisesRegex(ValueError,'Changed (muzzle|WARNING) source bytes'):
    bridge.project(sources,lambda name:(ROOT/name).read_bytes()+(b'\n'if name==target else b''))
if __name__=='__main__':unittest.main()
