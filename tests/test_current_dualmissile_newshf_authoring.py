import json
from pathlib import Path
import shutil
import struct
import sys
import tempfile
import unittest
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import current_dualmissile_newshf_compatibility as c
import build_current_dualmissile_newshf as b

class DualmissileAuthoring(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.root=Path(self.tmp.name)/'root';self.root.mkdir()
  for n in c.INPUTS:
   p=self.root/c.INPUT_ROOT/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/c.INPUT_ROOT/n,p)
  self.refresh()
 def refresh(self):
  self.raw=json.dumps(dict(schema=c.SCHEMA,version='synthetic-test-only',inputs={c.INPUT_ROOT+'/'+n:c.sha((self.root/c.INPUT_ROOT/n).read_bytes()) for n in c.INPUTS})).encode()
 def test_exact_resource_and_two_consumers(self):
  _,pngs,blobs,rows=c.generate(self.root,self.raw);blob=blobs[c.IDS[0]]
  self.assertEqual(rows[0]['records'],[2,500]);self.assertEqual(rows[0]['base'],169)
  self.assertEqual(struct.unpack('<4s6I',blob[:28]),(b'HDR1',2100015,8,24,28,6,7))
  im=Image.frombytes('RGBA',(192,224),blob[28:]);self.assertEqual(im.crop((0,0,96,224)).tobytes(),im.crop((96,0,192,224)).tobytes())
  self.assertTrue(any(0<a<255 for a in blob[31::4]))
 def test_parent_approved_pixels_exact(self):
  expected=Image.open(ROOT/c.INPUT_ROOT/'single-master.png').convert('RGBA');pair=Image.new('RGBA',(192,224));pair.alpha_composite(expected);pair.alpha_composite(expected,(96,0))
  self.assertEqual(c.generate(self.root,self.raw)[2][c.IDS[0]][28:],pair.tobytes())
 def test_edit_propagates_to_both_identical_halves(self):
  before=c.generate(self.root,self.raw)[2][c.IDS[0]]
  p=self.root/c.INPUT_ROOT/'single-master.png';im=Image.open(p).convert('RGBA');x,y=48,120;old=im.getpixel((x,y));self.assertGreater(old[3],0);im.putpixel((x,y),((old[0]+1)%256,*old[1:]));im.save(p);self.refresh()
  after=c.generate(self.root,self.raw)[2][c.IDS[0]];self.assertNotEqual(before,after)
  a=Image.frombytes('RGBA',(192,224),after[28:]);self.assertEqual(a.crop((0,0,96,224)).tobytes(),a.crop((96,0,192,224)).tobytes())
 def test_unselected_edit_rejected(self):
  p=self.root/c.INPUT_ROOT/'single-master.png';p.write_bytes(b'bad')
  with self.assertRaises(ValueError):c.generate(self.root,self.raw)
 def test_rehashed_mask_mutation_rejected(self):
  Image.new('L',(12,28),255).save(self.root/c.INPUT_ROOT/'native-mask.png');self.refresh()
  with self.assertRaises(ValueError):c.generate(self.root,self.raw)
 def test_external_support_rejected(self):
  p=self.root/c.INPUT_ROOT/'single-master.png';im=Image.open(p).convert('RGBA');im.putpixel((0,0),(255,0,0,1));im.save(p);self.refresh()
  with self.assertRaises(ValueError):c.generate(self.root,self.raw)
 def test_empty_and_wrong_canvas_rejected(self):
  for size in [(96,224),(95,224)]:
   Image.new('RGBA',size).save(self.root/c.INPUT_ROOT/'single-master.png');self.refresh()
   with self.assertRaises(ValueError):c.generate(self.root,self.raw)
 def test_extra_input_and_duplicate_json_rejected(self):
  j=json.loads(self.raw);j['inputs']['bad']='0'*64
  with self.assertRaises(ValueError):c.generate(self.root,json.dumps(j).encode())
  with self.assertRaises(ValueError):c.generate(self.root,b'{"schema":1,"schema":2}')
 def test_stage_apply_and_load(self):
  request=Path(self.tmp.name)/'request.json';request.write_bytes(self.raw);dest=Path(self.tmp.name)/'stage';b.stage(self.root,request,dest);b.apply(self.root,dest)
  self.assertEqual(len(c.load(self.root)),1)
  p=self.root/c.HEADER;p.write_bytes(b'bad')
  with self.assertRaises(ValueError):c.load(self.root)
 def test_tampered_stage_has_no_writes(self):
  request=Path(self.tmp.name)/'request.json';request.write_bytes(self.raw);dest=Path(self.tmp.name)/'stage';b.stage(self.root,request,dest)
  (dest/'files'/c.HEADER).write_bytes(b'tampered')
  with self.assertRaises(ValueError):b.apply(self.root,dest)
  self.assertFalse((self.root/c.HEADER).exists())
 def test_stale_input_has_no_writes(self):
  request=Path(self.tmp.name)/'request.json';request.write_bytes(self.raw);dest=Path(self.tmp.name)/'stage';b.stage(self.root,request,dest)
  (self.root/c.INPUT_ROOT/'single-master.png').write_bytes(b'bad')
  with self.assertRaises(ValueError):b.apply(self.root,dest)
  self.assertFalse((self.root/c.HEADER).exists())

if __name__=='__main__':unittest.main()
