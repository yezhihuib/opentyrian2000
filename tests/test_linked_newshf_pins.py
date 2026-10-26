import sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import check_linked_newshf_pins as pins
class LinkedPins(unittest.TestCase):
 def test_frozen(self):self.assertEqual(pins.verify(ROOT)['status'],'PASS')
 def test_drift(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'src').mkdir();(root/'src/newshf_linked_pins.h').write_bytes((ROOT/'src/newshf_linked_pins.h').read_bytes()+b' ')
   with self.assertRaises(AssertionError):pins.verify(root)
 def test_symlink(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'src').mkdir();(root/'src/newshf_linked_pins.h').symlink_to(ROOT/'src/newshf_linked_pins.h')
   with self.assertRaises(AssertionError):pins.verify(root)
if __name__=='__main__':unittest.main()
