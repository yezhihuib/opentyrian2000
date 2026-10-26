"""One raw registration chain, accepted V2 contour, original state constraints."""
import io,json,os,shutil,struct,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import current_large_newshi_compatibility as c
import build_current_large_newshi as b
class LargeNewshiAuthoring(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)/'root';self.root.mkdir()
  for n in c.INPUTS:
   p=self.root/c.INPUT_ROOT/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/c.INPUT_ROOT/n,p)
  self.refresh()
 def refresh(self):self.raw=json.dumps(dict(schema=c.SCHEMA,version='synthetic-test-only',inputs={c.INPUT_ROOT+'/'+n:c.sha((self.root/c.INPUT_ROOT/n).read_bytes()) for n in c.INPUTS})).encode()
 def test_exact_accepted_master_and_ten_resources(self):
  _,pngs,blobs,rows=c.generate(self.root,self.raw)
  self.assertEqual(c.sha(pngs[c.INPUT_ROOT+'/derived/normal-master-v2.png']),'2ef027faa1cff76cc6a1269ba0943eac4de2ca4b77194348a297bbfacd5f9062')
  self.assertEqual([r['base'] for r in rows],[201,203,237,239,241,243,278,268,270,272])
  self.assertEqual([r['records'] for r in rows],[[302],[303],[304],[305],[306],[307],[308],[308],[308],[308]])
  assembly=np.zeros((672,768,4),dtype='uint8')
  for i,blob in blobs.items():
   self.assertEqual(struct.unpack('<4s6I',blob[:28]),(b'HDR1',i,8,24,28,6,7))
   self.assertEqual(blob,(ROOT/c.ROOT/c.name(i)).read_bytes())
  for i,(rec,base,x,y) in zip(c.IDS,c.PARTS):assembly[y*8:(y+28)*8,x*8:(x+24)*8]=np.frombuffer(blobs[i][28:],dtype='uint8').reshape(224,192,4)
  self.assertEqual(assembly.tobytes(),Image.open(io.BytesIO(pngs[c.INPUT_ROOT+'/derived/normal-master-v2.png'])).tobytes())
 def test_v2_local_alpha_only_and_noses_exact(self):
  final=c.generate(self.root,self.raw)[2];p=self.root/c.INPUT_ROOT/'registration-recipe.json';recipe=json.loads(p.read_bytes());recipe['contours']=[];p.write_text(json.dumps(recipe));self.refresh();before=c.generate(self.root,self.raw)[2]
  changed=zeroed=0
  for i in c.IDS:
   a=np.frombuffer(before[i][28:],dtype='uint8').reshape(224,192,4);v=np.frombuffer(final[i][28:],dtype='uint8').reshape(224,192,4)
   self.assertTrue(np.all(v[:,:,3]<=a[:,:,3]));self.assertTrue(np.array_equal(v[:,:,:3][v[:,:,3]>0],a[:,:,:3][v[:,:,3]>0]));self.assertFalse(np.any(v[:,:,:3][v[:,:,3]==0]))
   changed+=np.any(v!=a,axis=2).sum();zeroed+=((a[:,:,3]>0)&(v[:,:,3]==0)).sum()
   if i>=2100024:self.assertEqual(final[i],before[i])
  self.assertEqual(changed,484);self.assertEqual(zeroed,452)
 def test_every_original_mask_rehashed_mutation_rejected(self):
  for n in c.MASK_PINS:
   p=self.root/c.INPUT_ROOT/n;old=p.read_bytes();p.write_bytes(old+b'!');self.refresh()
   with self.subTest(mask=n),self.assertRaises(ValueError):c.generate(self.root,self.raw)
   p.write_bytes(old);self.refresh()
 def test_each_nose_own_mask_unchanged_cells_and_seam(self):
  blobs=c.generate(self.root,self.raw)[2];normal=np.frombuffer(blobs[2100024][28:],dtype='uint8').reshape(224,192,4)
  for i,base in zip(c.IDS[7:],(268,270,272)):
   piece=np.frombuffer(blobs[i][28:],dtype='uint8').reshape(224,192,4);mask=c.expand(np.array(Image.open(self.root/c.INPUT_ROOT/f'native-mask-{base}.png'))>0);diff=c.expand(np.array(Image.open(self.root/c.INPUT_ROOT/f'normal-difference-{base}.png'))>0)
   self.assertFalse(np.any(piece[:,:,3][~mask]));self.assertTrue(np.array_equal(piece[~diff],normal[~diff]));self.assertTrue(np.array_equal(piece[:40],normal[:40]))
 def test_open_raw_propagates_only_three_damaged_states(self):
  before=c.generate(self.root,self.raw)[2];p=self.root/c.INPUT_ROOT/'open-center-generated-v1.png';a=np.array(Image.open(p).convert('RGBA'));a[:,:,0]^=127;Image.fromarray(a).save(p);self.refresh();after=c.generate(self.root,self.raw)[2]
  for i in c.IDS[:7]:self.assertEqual(before[i],after[i])
  for i in c.IDS[7:]:self.assertNotEqual(before[i],after[i])
 def test_normal_raw_is_shared_by_all_ten_resources(self):
  before=c.generate(self.root,self.raw)[2];p=self.root/c.INPUT_ROOT/'normal-generated-v1.png';a=np.array(Image.open(p).convert('RGBA'));a[:,:,1]^=127;Image.fromarray(a).save(p);self.refresh();after=c.generate(self.root,self.raw)[2]
  for i in c.IDS:self.assertNotEqual(before[i],after[i])
 def test_unselected_raw_edit_and_extra_inputs_rejected(self):
  for n in ('normal-generated-v1.png','open-center-generated-v1.png','registration-recipe.json','generation-provenance.txt'):
   p=self.root/c.INPUT_ROOT/n;old=p.read_bytes();p.write_bytes(old+b'!')
   with self.assertRaises(ValueError):c.generate(self.root,self.raw)
   p.write_bytes(old)
  obj=json.loads(self.raw);obj['inputs']['user-reference.png']='0'*64
  with self.assertRaises(ValueError):c.generate(self.root,json.dumps(obj).encode())
  with self.assertRaises(ValueError):c.generate(self.root,b'{"schema":1,"schema":2}')
 def stage(self):
  request=Path(self.tmp.name)/'request.json';request.write_bytes(self.raw);dest=Path(self.tmp.name)/'stage';b.stage(self.root,request,dest);return dest
 def test_stage_apply_load(self):
  dest=self.stage();b.apply(self.root,dest);self.assertEqual(len(c.load(self.root)),10)
  (self.root/c.HEADER).write_bytes(b'bad')
  with self.assertRaises(ValueError):c.load(self.root)
 def test_tampered_stage_no_writes(self):
  dest=self.stage();(dest/'files'/c.HEADER).write_bytes(b'tampered')
  with self.assertRaises(ValueError):b.apply(self.root,dest)
  self.assertFalse((self.root/c.HEADER).exists())
 def test_stale_input_no_writes(self):
  dest=self.stage();(self.root/c.INPUT_ROOT/'normal-generated-v1.png').write_bytes(b'bad')
  with self.assertRaises(ValueError):b.apply(self.root,dest)
  self.assertFalse((self.root/c.HEADER).exists())
 def test_handled_apply_error_rolls_back(self):
  dest=self.stage();replace=os.replace;calls=[]
  def fail_once(path,target):
   calls.append(path)
   if len(calls)==3:raise OSError('synthetic handled write error')
   return replace(path,target)
  with patch('os.replace',fail_once),self.assertRaises(OSError):b.apply(self.root,dest)
  self.assertFalse((self.root/c.HEADER).exists())
  self.assertFalse((self.root/c.MAPPING).exists())
if __name__=='__main__':unittest.main()
