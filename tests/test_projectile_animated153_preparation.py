"""Cheap preparation checks only; synthetic bytes never become production art."""
import importlib.util,pathlib,re,struct,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('animated153_transport',ROOT/'scripts/projectile_animated153_transport.py')
t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t)
class Preparation(unittest.TestCase):
 def fixture(self,i=153,color=120):
  p=bytearray(43008);p[:4]=bytes((color,0,0,255));return struct.pack('<4s6I',b'HDR1',1570000+i,8,12,14,0,0)+p
 def test_exact_per_frame_palette(self):
  self.assertEqual(t.PALETTE[153],{112,120,121,122,123,124,125})
  for i in (154,155):self.assertEqual(t.PALETTE[i],{112,119,120,121,122,123,124,125})
  with self.assertRaises(ValueError):t.validate_transport(1570153,bytes(self.fixture(153,119)),bytes([1]*168))
  for i in (154,155):self.assertEqual(t.validate_transport(1570000+i,bytes(self.fixture(i,119)),bytes([1]*168)),{0})
 def test_transparent_native_cells_structurally_valid_not_art_qualified(self):
  self.assertEqual(t.validate_transport(1570153,bytes(self.fixture()),bytes([1]*168)),{0})
 def test_bad_header_texels_support(self):
  b=bytes(self.fixture());mask=bytes([1]*168)
  for offset,value in ((0,0),(4,0),(8,4),(12,11),(16,13),(20,1),(24,1),(29,1),(30,1),(31,128),(32,112)):
   q=bytearray(b);q[offset]=value
   with self.subTest(offset=offset),self.assertRaises(ValueError):t.validate_transport(1570153,bytes(q),mask)
  for q in (b[:-1],b+b'\0'):
   with self.assertRaises(ValueError):t.validate_transport(1570153,q,mask)
  with self.assertRaises(ValueError):t.validate_transport(1570153,b,bytes(168))
 def test_metadata_exact_deterministic(self):
  row={'identity':1570153,'density':8,'encoding':t.ENCODING,'other':'ignored'}
  self.assertEqual(t.metadata(row),{k:row[k]for k in ('identity','density','encoding')})
  for key,bad in (('identity',True),('identity',1560007),('density',True),('density',4),('encoding','rgba')):
   q=dict(row);q[key]=bad
   with self.assertRaises(ValueError):t.metadata(q)
  for key in ('identity','density','encoding'):
   q=dict(row);del q[key]
   with self.assertRaises(ValueError):t.metadata(q)
 def test_member_width_and_append_only(self):
  s=(ROOT/'src/global_projectile91_mirror.inc').read_text();f=s.split('static unsigned global_projectile91_member(unsigned index)')[1].split('static Asset')[0]
  pairs=[(int(i),int(b))for i,b in re.findall(r'index==(\d+)\?(\d+)u',f)]
  ids=(91,145,61,101,120,139,168,169,162,260,166,94,7,45,153,154,155,70,20,21,105,106,124,125,112,113,226,227,244)
  self.assertEqual(pairs,[(i,1<<k)for k,i in enumerate(ids)]);self.assertIn('#if UINT_MAX < 536870911u',s)
  self.assertIn('static Uint8 *global_projectile91_owner,*global_projectile91_foreign;', (ROOT/'src/render_mirror.c').read_text())
 def test_candidate_art_scope(self):
  self.assertIn('#define CURRENT_PROJECTILE_ANIMATED153_ART_QUALIFIED 1',(ROOT/'src/current_projectile_animated153_payload_pins.h').read_text())
  s=(ROOT/'src/enemy_animated153_mirror.inc').read_text();self.assertIn('#if CURRENT_PROJECTILE_ANIMATED153_ART_QUALIFIED',s)
  self.assertIn('{(void)root;(void)index;return NULL;}',s)
 def test_finite_dispatch_generic_rejection(self):
  s=(ROOT/'src/render_mirror.c').read_text();self.assertIn('if(a->bank==ASSET_ENEMY_ANIMATED153)return false;',s)
  s=(ROOT/'src/global_projectile91_mirror.inc').read_text()
  self.assertIn('resource->bank==ASSET_ENEMY_ANIMATED153&&(index==153||index==154||index==155)',s)
 def test_source_gameplay_only_allowlist_change(self):
  import hashlib
  # Full-file public baseline digest, identical to qualified 715 bytes. No
  # private Git object is needed in a clean public checkout or source archive.
  original_sha256='9982362190cefcc4eee6143d76fce3072808e9bc9f8ac083b8a89a9faf76c2ff'
  old=b'|| sprite == 7 || sprite == 45)\n\t\t\t\t\t\t\t\tdraw_enemy_shot_sprite2(VGAScreen, enemyShot[z].sx, enemyShot[z].sy, spriteSheet8, sprite);'
  new=old.replace(b'|| sprite == 45)',b'|| sprite == 45 || sprite == 153 || sprite == 154 || sprite == 155 || sprite == 70 || widget_sonic_member_index(sprite) || orb_protron_protron_index(sprite))')
  policy=b'#include "enemy_widget_sonic_policy.h"\n#include "enemy_orb_protron_policy.h"\n'
  legacy=b'if (sprite == 105 || sprite == 106 || sprite == 124 || sprite == 125 || sprite == 20 || sprite == 21 || sprite == 214 || sprite == 215 || sprite == 216 || sprite == 226 || sprite == 227 || sprite == 244)'
  routed=b'if ((widget_sonic_member_index(sprite) && widget_sonic_legacy_intent()) || sprite == 214 || sprite == 215 || sprite == 216 || (orb_protron_protron_index(sprite) && widget_sonic_legacy_intent()))'
  def assert_original(raw):
   self.assertEqual(raw.count(policy),1);self.assertEqual(raw.count(routed),1)
   raw=raw.replace(policy,b'',1).replace(routed,legacy,1)
   self.assertEqual(raw.count(new),1)
   restored=raw.replace(new,old,1)
   self.assertEqual(hashlib.sha256(restored).hexdigest(),original_sha256)
  current=(ROOT/'src/tyrian2.c').read_bytes()
  assert_original(current)
  for label,changed in (('unintended source edit',current+b'\n'),('missing allowlist',current.replace(new,old)),('duplicated allowlist',current+new),('missing policy',current.replace(policy,b'')),('duplicated route',current+routed)):
   with self.subTest(label=label),self.assertRaises(AssertionError):assert_original(changed)
if __name__=='__main__':unittest.main()
