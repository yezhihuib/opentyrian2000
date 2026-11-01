"""Pure native adapter checks; never compiler/native/game execution."""
import importlib.util,pathlib,struct,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
p=ROOT/'tests/enemy_vulcan70_native_validation.py';spec=importlib.util.spec_from_file_location('enemy70_native',p);n=importlib.util.module_from_spec(spec);spec.loader.exec_module(n)
class Adapter(unittest.TestCase):
 def inputs(self):
  h={i:bytes([i%256])*43036 for i in n.OLD_IDS};names={i:f'fixture-{i}.hda'for i in n.OLD_IDS}
  for i,pin in n.CANONICAL.items():
   names[i]='content/'+pin+'.hda';h[i]=(ROOT/'assets/hd/global-assets-v1'/names[i]).read_bytes()
  return h,{i:n.sha(b)for i,b in h.items()},names
 def test_inventory(self):
  self.assertEqual(sum(n.CASE_INVENTORY.values()),75);self.assertEqual(len(n.PACKS),12);self.assertEqual(n.IDS,n.OLD_IDS+(70,67))
 def test_wrapper_is_reversible_old8(self):
  sources,wrapped=n.source_bundle(ROOT);self.assertEqual(len(sources),6)
  old=n.reverse_shim(wrapped);self.assertEqual(n.sha(old),n.OLD_WRAPPER_SHA);self.assertEqual(n.outer_shim(old),wrapped)
  self.assertIn(b'--enemy-animated153',old);self.assertNotIn(b'--enemy-vulcan70',old)
 def test_reject_wrong_wrapper(self):
  for b in (b'int main(){}',b'',b'x'+n.TAIL):
   with self.assertRaises(ValueError):n.outer_shim(b)
   with self.assertRaises(ValueError):n.reverse_shim(b)
 def test_all_mutations_only70(self):
  raw=bytes(43036)
  for leaf in n.PACKS:
   for i in n.IDS:
    actual=n.fixture_bytes(raw,i,leaf)
    if i!=70 or leaf=='valid':self.assertEqual(actual,raw)
    elif leaf=='missing70':self.assertIsNone(actual)
    else:self.assertNotEqual(actual,raw)
 def test_fixture_closure_exact227(self):
  h,pins,names=self.inputs();out=n.fixture_payloads(h,pins,names);self.assertEqual(len(out),227)
  self.assertNotIn('enemy70-packs/missing70/'+names[70],out)
  for leaf in n.PACKS:self.assertEqual(out['enemy70-packs/'+leaf+'/'+names[67]],h[67])
 def test_canonical_pins_and_identity(self):
  h,pins,names=self.inputs()
  for i in (67,70):self.assertEqual(struct.unpack('<4s6I',h[i][:28]),(b'HDR1',80000+i,8,12,14,0,0))
  h[70]=bytes(43036);pins[70]=n.sha(h[70])
  with self.assertRaises(ValueError):n.fixture_payloads(h,pins,names)
 def test_names_and_membership_fail_closed(self):
  h,pins,names=self.inputs()
  for bad in ('../escape.hda','/escape.hda','content/renamed.hda'):
   q=dict(names);q[70]=bad
   with self.assertRaises(ValueError):n.fixture_payloads(h,pins,q)
  for d in (h,pins,names):
   q=dict(d);q.pop(67);args=[h,pins,names];args[[h,pins,names].index(d)]=q
   with self.assertRaises(ValueError):n.fixture_payloads(*args)
 def test_unbound_native_input_rejected(self):
  for old,data in ((bytes(98980),b''),(b'',bytes(100)),(bytearray(98980),b'')):
   with self.assertRaises(ValueError):n.native_input(old,data)
 def test_no_inherited_native_source_edits_required(self):
  source=(ROOT/'tests/enemy_vulcan70_native_additions.c.inc').read_text()
  self.assertIn('player_shot_create(7,0,120,90,120,90,227,1)',source)
  self.assertIn('CHECK(cases-initial_cases==75)',source)
  self.assertNotIn('global_vulcan_slots[0].role=true',source)
  self.assertIn('CHECK(cells==46&&nonzero==2674&&soft==400&&halo==110)',source)
if __name__=='__main__':unittest.main()
