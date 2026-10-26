"""Canonical cyan master, source-zero containment and four-output inverse."""
import io,json,struct,sys,unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import current_shapesy_cyan_compatibility as c
class CyanAuthoring(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.raw=c.read(ROOT,c.SELECTION);cls.selected,cls.pngs,cls.blobs,cls.rows=c.generate(ROOT,cls.raw)
 def test_exact_master_and_inverse(self):
  master=self.pngs[c.INPUT_ROOT+'/derived/master-384x448.png'];self.assertEqual(c.sha(master),c.MASTER_PIN)
  assembled=Image.new('RGBA',(384,448))
  for i,x,y in ((111,0,0),(112,192,0),(121,0,224),(122,192,224)):
   im=Image.open(io.BytesIO(self.pngs[c.png(i)]));assembled.paste(im,(x,y))
   self.assertEqual(struct.unpack('<4s6I',self.blobs[i][:28]),(b'HDR1',2030000+i,8,24,28,0,0))
   self.assertEqual(self.blobs[i][28:],im.tobytes());self.assertEqual(len(self.blobs[i]),172060)
  self.assertEqual(assembled.tobytes(),Image.open(io.BytesIO(master)).tobytes());self.assertEqual(c.load(ROOT),{r['destination']:r for r in self.rows})
 def test_source_zero_and_inward_boundary(self):
  a=np.array(Image.open(io.BytesIO(self.pngs[c.INPUT_ROOT+'/derived/master-384x448.png'])))
  native=np.array(Image.open(ROOT/c.INPUT_ROOT/'native-mask.png'))>0;mask=np.repeat(np.repeat(native,8,0),8,1)
  self.assertEqual(int(native.sum()),521);self.assertFalse(a[~mask].any());self.assertFalse(a[a[:,:,3]==0].any())
  missing=native & ~a[:,:,3].reshape(56,8,48,8).any(axis=(1,3))
  self.assertEqual({(int(x),int(y)) for y,x in np.argwhere(missing)},{(37,14),(37,19)})
  self.assertGreater(len(np.unique(a[:,:,3])),2)
 def test_every_input_and_selection_mutation_rejected(self):
  original=c.read
  for n in c.INPUTS:
   p=c.INPUT_ROOT+'/'+n
   def changed(root,path):return original(root,path)+(b'INVALID' if path==p else b'')
   with self.subTest(path=p),patch.object(c,'read',changed),self.assertRaises(ValueError):c.generate(ROOT,self.raw)
  for mut in (lambda x:x.update(schema='wrong'),lambda x:x['inputs'].pop(next(iter(x['inputs']))),lambda x:x['inputs'].update({'foreign':'0'*64})):
   j=json.loads(self.raw);mut(j)
   with self.assertRaises(ValueError):c.generate(ROOT,json.dumps(j).encode())
 def test_each_derived_transport_and_header_is_checked(self):
  original=c.read
  for p in c.generated_paths()|{c.HEADER,c.SOURCE_HEADER,c.MAPPING}|{c.ROOT+'/'+c.name(i) for i in c.IDS}:
   def changed(root,path):return original(root,path)+(b'INVALID' if path==p else b'')
   with self.subTest(path=p),patch.object(c,'read',changed),self.assertRaises((ValueError,json.JSONDecodeError)):c.load(ROOT)
if __name__=='__main__':unittest.main()
