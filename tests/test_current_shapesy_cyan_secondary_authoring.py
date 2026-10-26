"""Canonical cyan master, source-zero containment and five-output inverse."""
import io,json,struct,sys,unittest,tempfile,shutil
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import current_shapesy_cyan_secondary_compatibility as c
import build_current_shapesy_cyan_secondary as b
class CyanSecondaryAuthoring(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.raw=c.read(ROOT,c.SELECTION);cls.selected,cls.pngs,cls.blobs,cls.rows=c.generate(ROOT,cls.raw)
 def test_exact_master_and_inverse(self):
  master=self.pngs[c.INPUT_ROOT+'/derived/master-384x672.png'];self.assertEqual(c.sha(master),c.MASTER_PIN)
  assembled=Image.new('RGBA',(384,672))
  for i,x,y in ((172,192,0),(181,0,224),(182,192,224),(191,0,448),(192,192,448)):
   im=Image.open(io.BytesIO(self.pngs[c.png(i)]));assembled.paste(im,(x,y))
   self.assertEqual(struct.unpack('<4s6I',self.blobs[i][:28]),(b'HDR1',2030000+i,8,24,28,0,0))
   self.assertEqual(self.blobs[i][28:],im.tobytes());self.assertEqual(len(self.blobs[i]),172060)
  self.assertEqual(assembled.tobytes(),Image.open(io.BytesIO(master)).tobytes());self.assertEqual(c.load(ROOT),{r['destination']:r for r in self.rows})
 def test_source_zero_and_inward_boundary(self):
  a=np.array(Image.open(io.BytesIO(self.pngs[c.INPUT_ROOT+'/derived/master-384x672.png'])))
  native=np.array(Image.open(ROOT/c.INPUT_ROOT/'native-mask.png'))>0;mask=np.repeat(np.repeat(native,8,0),8,1)
  self.assertEqual(int(native.sum()),669);self.assertFalse(a[~mask].any());self.assertFalse(a[a[:,:,3]==0].any())
  missing=native & ~a[:,:,3].reshape(84,8,48,8).any(axis=(1,3))
  self.assertEqual(int(missing.sum()),38)
  self.assertFalse(a[:224,:192].any())
  self.assertEqual(c.IDS,(172,181,182,191,192))
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
 @contextmanager
 def fixture(self):
  with tempfile.TemporaryDirectory(prefix='cyan-secondary-authoring-') as tmp:
   top=Path(tmp);root=top/'source';root.mkdir()
   outputs=b.derive(ROOT,self.raw)
   names=set(b.plan(ROOT,self.raw,outputs)['inputs_sha256'])|set(outputs)
   for name in names:
    dst=root/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,dst)
   yield root,top/'stage',outputs
 def test_stage_apply_exact_and_no_old_family_outputs(self):
  with self.fixture() as (root,stage,outputs):
   before={n:(root/n).read_bytes() for n in outputs}
   receipt=b.stage(root,root/c.SELECTION,stage)
   self.assertEqual(set(outputs),{r['path'] for r in receipt['files']})
   self.assertTrue(all('shapesy-cyan-secondary' in n or 'shapesy_cyan_secondary' in n for n in outputs))
   self.assertEqual(b.apply(root,stage),receipt)
   self.assertEqual(before,{n:(root/n).read_bytes() for n in outputs})
   self.assertEqual(len(c.load(root)),5)
 def test_stage_corruption_rejected_without_writes(self):
  with self.fixture() as (root,stage,outputs):
   b.stage(root,root/c.SELECTION,stage)
   target=stage/'files'/c.HEADER;target.write_bytes(target.read_bytes()+b'changed')
   before={n:(root/n).read_bytes() for n in outputs}
   with self.assertRaises(ValueError):b.apply(root,stage)
   self.assertEqual(before,{n:(root/n).read_bytes() for n in outputs})
 def test_stale_input_rejected_without_writes(self):
  with self.fixture() as (root,stage,outputs):
   b.stage(root,root/c.SELECTION,stage)
   target=root/c.INPUT_ROOT/'prompt.txt';target.write_bytes(target.read_bytes()+b'changed')
   before={n:(root/n).read_bytes() for n in outputs}
   with self.assertRaises(ValueError):b.apply(root,stage)
   self.assertEqual(before,{n:(root/n).read_bytes() for n in outputs})
 def test_internal_stage_and_symlink_output_rejected(self):
  with self.fixture() as (root,stage,outputs):
   with self.assertRaises(ValueError):b.stage(root,root/c.SELECTION,root/'stage')
   b.stage(root,root/c.SELECTION,stage)
   target=root/c.HEADER;raw=target.read_bytes();target.unlink();foreign=stage.parent/'foreign';foreign.write_bytes(raw);target.symlink_to(foreign)
   with self.assertRaises(ValueError):b.apply(root,stage)
   self.assertEqual(foreign.read_bytes(),raw)
if __name__=='__main__':unittest.main()
