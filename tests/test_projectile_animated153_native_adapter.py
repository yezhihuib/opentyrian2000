"""Pure adapter tests: not native execution."""
import importlib.util,pathlib,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
p=ROOT/'tests/projectile_animated153_native_validation.py';spec=importlib.util.spec_from_file_location('animated153_native_validation',p);n=importlib.util.module_from_spec(spec);spec.loader.exec_module(n)
class Adapter(unittest.TestCase):
 def test_inventory(self):self.assertEqual(sum(n.CASE_INVENTORY.values()),141);self.assertEqual(len(n.PACKS),34)
 def test_mutations_only_selected_member(self):
  b=bytes(43036)
  for i in n.NEW:
   for kind in n.KINDS:
    leaf=kind+str(i);q=n.fixture_bytes(b,i,leaf)
    if kind=='missing':self.assertIsNone(q)
    else:self.assertNotEqual(q,b)
    for other in n.IDS:
     if other!=i:self.assertEqual(n.fixture_bytes(b,other,leaf),b)
 def test_exact_fixture_closure(self):
  h={i:bytes([i%256])*43036 for i in n.IDS};pins={i:n.sha(b)for i,b in h.items()};names={i:f'fixture-{i}.hda'for i in n.IDS}
  out=n.fixture_payloads(h,pins,names);self.assertEqual(len(out),575)
  pins[155]='0'*64
  with self.assertRaises(ValueError):n.fixture_payloads(h,pins,names)
 def test_exact_old_wrapper_roundtrip(self):
  old=n.old_helper(ROOT,'158d5ef10020396f1aec1a03a4dc6791eee7c1944be127b868c67b89abf11cdc')
  sources,wrapper=old.source_bundle(ROOT);self.assertEqual(len(sources),6)
  self.assertEqual(n.reverse_shim(n.outer_shim(wrapper)),wrapper)
 def test_reject_wrong_shim(self):
  with self.assertRaises(ValueError):n.outer_shim(b'int main(){}')
  with self.assertRaises(ValueError):n.reverse_shim(b'int main(){}')
if __name__=='__main__':unittest.main()
