"""Pure adapter tests; no compiler, native/game invocation or fixture writes."""
import importlib.util,pathlib,struct,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
p=ROOT/'tests/widget_sonic_native_validation.py';spec=importlib.util.spec_from_file_location('ws_native',p);n=importlib.util.module_from_spec(spec);spec.loader.exec_module(n)
class Adapter(unittest.TestCase):
 def inputs(self):
  h={i:bytes([i%256])*43036 for i in n.OLD_IDS};names={i:f'fixture-{i}.hda'for i in n.OLD_IDS}
  for i,pin in n.CANONICAL.items():names[i]='content/'+pin+'.hda';h[i]=(ROOT/'assets/hd/global-assets-v1'/names[i]).read_bytes()
  return h,{i:n.sha(b)for i,b in h.items()},names
 def test_exact_inventory_off_scope(self):
  self.assertEqual(sum(n.CASE_INVENTORY.values()),86);self.assertEqual(n.CASE_INVENTORY['current24_complete_oracles'],24);self.assertEqual(len(n.IDS),25);self.assertEqual(len(n.PACKS),21);self.assertIn('DEFERRED',n.MACRO_ON_PIXEL_SCOPE)
 def test_old_nine_dispatches_reversible(self):
  sources,wrapped=n.source_bundle(ROOT);old=n.reverse_shim(wrapped,ROOT);self.assertEqual(len(sources),6);self.assertEqual(n.outer_shim(old,ROOT),wrapped)
  self.assertIn(b'--enemy-vulcan70',old);self.assertIn(b'--enemy-animated153',old);self.assertNotIn(b'--widget-sonic',old)
 def test_changed_wrappers_refused(self):
  for raw in (b'',b'int main(){}',b'x'+n.TAIL):
   with self.assertRaises(ValueError):n.outer_shim(raw,ROOT)
   with self.assertRaises(ValueError):n.reverse_shim(raw,ROOT)
 def test_finite_fixture519(self):
  h,pins,names=self.inputs();out=n.fixture_payloads(h,pins,names);self.assertEqual(len(out),519)
  for i in n.NEW_IDS:self.assertNotIn('widget-sonic-packs/missing'+str(i)+'/'+names[i],out)
  for leaf in n.PACKS:
   for i in n.OLD_IDS+(70,67):self.assertEqual(out['widget-sonic-packs/'+leaf+'/'+names[i]],h[i])
 def test_mutations_exactly_one_authorized_member(self):
  raw=bytes(43036)
  for leaf in n.PACKS:
   changed=[i for i in n.IDS if n.fixture_bytes(raw,i,leaf)!=raw];self.assertEqual(len(changed),0 if leaf=='valid'else 1)
 def test_canonical_identity_and_pins(self):
  h,pins,names=self.inputs()
  for i in n.CANONICAL:self.assertEqual(struct.unpack('<4s6I',h[i][:28]),(b'HDR1',80000+i,8,12,14,0,0))
  h[20]=bytes(43036);pins[20]=n.sha(h[20])
  with self.assertRaises(ValueError):n.fixture_payloads(h,pins,names)
 def test_membership_path_and_boolean_reject(self):
  h,pins,names=self.inputs()
  for bad in ('../bad.hda','/bad.hda','content/renamed.hda'):
   q=dict(names);q[20]=bad
   with self.assertRaises(ValueError):n.fixture_payloads(h,pins,q)
  q=dict(h);q.pop(67)
  with self.assertRaises(ValueError):n.fixture_payloads(q,pins,names)
  with self.assertRaises(ValueError):n.fixture_bytes(bytes(43036),True,'valid')
 def test_input_unbound_rejected(self):
  for b in (b'',bytes(98980),bytes(99142),bytearray(99142)):
   with self.assertRaises(ValueError):n.native_input(b,b'')
 def test_tiny_exact_source_provenance(self):
  raw,pins=n.tiny_sources(ROOT);self.assertEqual(len(pins),4);self.assertIn(b'#include "enemy_widget_sonic_policy.h"',raw);self.assertIn(b'global_projectile91_source_matches(Sprite2_array bank)',raw);self.assertIn(b'global_projectile91_check_cache(void)',raw)
  self.assertIn(b'widget_sonic_member_index(sprite) && widget_sonic_legacy_intent()',raw);self.assertIn(b'assert(checks==160)',raw);self.assertIn(b'NOT full ON session/pixels',raw)
  for p,pin in pins.items():self.assertEqual(n.sha((ROOT/p).read_bytes()),pin)
 def test_macro_closure_is_not_83_false_reuse(self):
  self.assertEqual(len(n.MACRO_SENSITIVE_OLD_OBJECTS),26);self.assertEqual(n.SYNTAX_TUS,('src/render_mirror.c','src/tyrian2.c','src/entity_draw.c'))
 def test_native_finite_count_and_real_routes(self):
  raw=(ROOT/'tests/widget_sonic_native_additions.c.inc').read_text();self.assertIn('CHECK(cases-initial==86)',raw);self.assertIn('enemy70_old17();',raw);self.assertIn('enemy70_player_birth(&x,&y)',raw);self.assertIn('render_mirror_fade_step(7)',raw);self.assertIn('MIRROR_OUTPUT_UNSUPPORTED',raw);self.assertNotIn('global_vulcan_owner[z]=',raw)
if __name__=='__main__':unittest.main()
