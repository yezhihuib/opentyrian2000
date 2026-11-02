"""Pure extraction/adapter contracts; no compiler, native fixtures or game runs."""
from pathlib import Path
import tempfile,unittest
from unittest.mock import patch
import tank_muzzle_native_validation as m

class TankMuzzleNativeAdapter(unittest.TestCase):
 def altered(self,needle,replacement,name='src/tyrian2.c'):
  original=Path.read_text;target=m.ROOT/name
  def read(p,*a,**kw):
   s=original(p,*a,**kw)
   if p==target:
    self.assertEqual(s.count(needle),1);s=s.replace(needle,replacement,1)
   return s
  return patch.object(Path,'read_text',read)
 def test_32_finite_setups_no_old_matrix(self):
  self.assertEqual(sum(m.CASE_INVENTORY.values()),32)
  self.assertEqual(m.CASE_INVENTORY['actual_Green_outside_oldtile_retirement_pixel_rect_normal_fade'],4)
  self.assertIn('No old46',m.SCOPE)
 def test_actual_extract_pins(self):
  e=m.extracts(m.ROOT);self.assertEqual({k:m.sha(v.encode())for k,v in e.items()},m.EXTRACT_PINS)
 def test_missing_allocation_rejected(self):
  with self.altered('tank_muzzle_allocate(b);','/* missing */'),self.assertRaises(ValueError):m.extracts(m.ROOT)
 def test_duplicate_birth_rejected(self):
  call='tank_muzzle_birth(b,i,temp3,j,tempPos);'
  with self.altered(call,call+call),self.assertRaises(ValueError):m.extracts(m.ROOT)
 def test_changed_sidecar_body_rejected(self):
  with self.altered('/* Render-only birth registration.','/* Render-only birth registration. Changed'),self.assertRaises(ValueError):m.extracts(m.ROOT)
 def test_changed_wrapper_rejected(self):
  text='void draw_tank147_muzzle_sprite2('
  with self.altered(text,'void  draw_tank147_muzzle_sprite2(', 'src/entity_draw.c'),self.assertRaises((ValueError,IndexError)):m.extracts(m.ROOT)
 def test_bank_crossing_guard_before_branch(self):
  route=m.extracts(m.ROOT)['route'];self.assertLess(route.index('tank_muzzle_draw('),route.index('sgr >= 500'));self.assertEqual(route.count('spriteSheet12'),1)
 def test_bundle_reversible_predecessor(self):
  sources,raw=m.source_bundle(m.ROOT);prior_sources,prior=m.old_helper(m.ROOT).source_bundle(m.ROOT)
  self.assertEqual(len(sources),len(prior_sources)+2)
  for k,v in prior_sources.items():self.assertEqual(sources[k],v)
  prefix=prior.replace(b'int main(',b'int inherited_tank_dispatch(',1)
  self.assertTrue(raw.startswith(prefix));self.assertEqual(raw.count(b'int main('),1)
  self.assertIn(b'--tank-muzzle',raw);self.assertIn(b'inherited_tank_dispatch(argc,argv)',raw)
 def test_tiny_exact_actual_route_lane_and_finite_scope(self):
  raw,pins=m.tiny_sources(m.ROOT);self.assertIn(m.extracts(m.ROOT)['route'].encode(),raw);self.assertIn(b'global_asset_directory[0]&&tank_shared_ordinary_allowed(147)',raw)
  self.assertEqual(m.TINY_CASES,153);self.assertIn(b'assert(cases==153)',raw)
  for name,digest in pins.items():self.assertEqual(m.sha((m.ROOT/name).read_bytes()),digest)
 def test_wrong_caller_raw_rejected_before_predecessor(self):
  with patch.object(m,'old_helper',side_effect=AssertionError('must reject first')):
   with self.assertRaises(ValueError):m.native_input(b'',b'',b'',b'',b'',b'',m.ROOT)
 def test_huf_bytes_exact_not_arbitrary_fixture(self):
  class Old:
   def fixture_payloads(self,*a):return {}
  with patch.object(m,'old_helper',return_value=Old()),patch.object(Path,'read_bytes',return_value=b'approved'):
   with self.assertRaises(ValueError):m.fixture_payloads({}, {}, {},b'changed',m.ROOT)
   self.assertEqual(m.fixture_payloads({}, {}, {},b'approved',m.ROOT),{'muzzle-font/gameplay-hud-font-v1.hda':b'approved'})
 def test_qualification_boundaries_and_strict_retirement(self):
  self.assertIn('Fresh tyrian2.o/entity_draw.o',m.PROVENANCE['support_object_exceptions'])
  self.assertIn('not inactive stub',m.PROVENANCE['font'])
  c=(m.ROOT/'tests/tank_muzzle_native_additions.c.inc').read_text()
  for text in ('sc==10&&hc==10','gc==40&&hc==40','global_projectile91_used_members==1073741824u','render_mirror_fade_step(7)','bolts745_oracle(7,160,80,&indexed,true)','cases-initial==32','!render_mirror_present(renderer,VGAScreenSeg,NULL)'):
   self.assertIn(text,c)

if __name__=='__main__':unittest.main()
