"""Finite authoring checks; no native/gameplay qualification."""
from pathlib import Path
import copy,sys,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import current_projectile_animated153_compatibility as c
class BananaAuthoring(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.selected,cls.pngs,cls.blobs=c.generate(ROOT,c.read(ROOT,c.SELECTION))
 def test_exact_products(self):
  self.assertEqual(set(self.blobs),set(c.PAIRS));self.assertEqual(len(c.load(ROOT)),3)
 def test_exact_exception(self):
  for s in c.SELECTORS:
   cells=c.validate_payload(ROOT,s,self.blobs[(1570000+s,8)][28:]);self.assertEqual(len(cells),73 if s==153 else 88 if s==154 else 76)
 def test_no_filled_exception(self):
  b=bytearray(self.blobs[(1570153,8)][28:]);off=4*(40*96);b[off:off+4]=bytes((112,0,0,255))
  with self.assertRaises(ValueError):c.validate_payload(ROOT,153,b)
 def test_no_new_holes(self):
  b=bytearray(self.blobs[(1570154,8)][28:]);off=next(i for i in range(0,len(b),4)if b[i+3]);b[off:off+4]=bytes(4)
  with self.assertRaises(ValueError):c.validate_payload(ROOT,154,b)
 def test_palette153_no119(self):
  b=bytearray(self.blobs[(1570153,8)][28:]);off=next(i for i in range(0,len(b),4)if b[i+3]);b[off]=119
  with self.assertRaises(ValueError):c.validate_payload(ROOT,153,b)
 def test_transparent_allzero(self):
  b=bytearray(self.blobs[(1570153,8)][28:]);off=next(i for i in range(0,len(b),4)if not b[i+3]);b[off]=112
  with self.assertRaises(ValueError):c.validate_payload(ROOT,153,b)
 def test_alpha_binary(self):
  b=bytearray(self.blobs[(1570155,8)][28:]);off=next(i for i in range(0,len(b),4)if b[i+3]);b[off+3]=254
  with self.assertRaises(ValueError):c.validate_payload(ROOT,155,b)
 def test_no_contract_relaxation(self):
  contract=copy.deepcopy(c.COVERAGE_SPEC);contract['members']['153']['covered_source_cells']=72
  with self.assertRaises(ValueError):c.validate_payload(ROOT,153,self.blobs[(1570153,8)][28:],contract)
 def test_metadata_and_namespace(self):
  rows=c.rows_for(self.selected,self.blobs)
  for row in rows:self.assertEqual(row['encoding'],c.ENCODING);self.assertEqual(row['density'],8)
  for bad in [1560153,1570156,True]:
   with self.assertRaises(ValueError):c.name(bad)
 def test_duplicate_json_rejected(self):
  with self.assertRaises(ValueError):c.parse(b'{"a":1,"a":2}')
if __name__=='__main__':unittest.main()
