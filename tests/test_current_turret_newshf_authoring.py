import json,shutil,struct,sys,tempfile,unittest
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import current_turret_newshf_compatibility as c
import build_current_turret_newshf as b
class TurretAuthoring(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)/'root';self.root.mkdir()
  for n in c.INPUTS:
   p=self.root/c.INPUT_ROOT/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/c.INPUT_ROOT/n,p)
  self.refresh()
 def refresh(self):self.raw=json.dumps(dict(schema=c.SCHEMA,version='synthetic-test-only',inputs={c.INPUT_ROOT+'/'+n:c.sha((self.root/c.INPUT_ROOT/n).read_bytes()) for n in c.INPUTS})).encode()
 def test_exact_two_resources_consumers_and_geometry(self):
  _,_,blobs,rows=c.generate(self.root,self.raw)
  self.assertEqual([r['base'] for r in rows],[39,41]);self.assertTrue(all(r['records']==[162,840] for r in rows))
  for i,blob in blobs.items():self.assertEqual(struct.unpack('<4s6I',blob[:28]),(b'HDR1',i,8,24,28,6,7));self.assertEqual(set(blob[31::4]),{255})
 def test_master_plus_overlay_exact_and_limited(self):
  cold=Image.open(self.root/c.INPUT_ROOT/'cold-master.png').convert('RGBA');overlay=Image.open(self.root/c.INPUT_ROOT/'hot-overlay.png').convert('RGBA');cold=c.compose_cold(self.root,cold);hot=Image.alpha_composite(cold,overlay)
  blobs=c.generate(self.root,self.raw)[2];self.assertEqual(blobs[c.IDS[0]][28:],cold.tobytes());self.assertEqual(blobs[c.IDS[1]][28:],hot.tobytes())
  mask=Image.open(self.root/c.INPUT_ROOT/'native-hot-mask.png').convert('L').resize(cold.size,Image.Resampling.NEAREST)
  self.assertTrue(all(a==b or m for a,b,m in zip(cold.getdata(),hot.getdata(),mask.getdata())))
 def test_master_edit_propagates_both_states(self):
  before=c.generate(self.root,self.raw)[2];p=self.root/c.INPUT_ROOT/'cold-master.png';im=Image.open(p).convert('RGBA');v=im.getpixel((100,140));im.putpixel((100,140),((v[0]+1)%256,*v[1:]));im.save(p);self.refresh();after=c.generate(self.root,self.raw)[2]
  for i in c.IDS:self.assertNotEqual(before[i],after[i])
 def test_overlay_edit_changes_only_hot(self):
  before=c.generate(self.root,self.raw)[2];p=self.root/c.INPUT_ROOT/'hot-overlay.png';im=Image.open(p).convert('RGBA');im.putpixel((80,88),(0,255,0,255));im.save(p);self.refresh();after=c.generate(self.root,self.raw)[2]
  self.assertEqual(before[c.IDS[0]],after[c.IDS[0]]);self.assertNotEqual(before[c.IDS[1]],after[c.IDS[1]])
 def test_unselected_edit_rejected(self):
  (self.root/c.INPUT_ROOT/'cold-master.png').write_bytes(b'bad')
  with self.assertRaises(ValueError):c.generate(self.root,self.raw)
 def test_rehashed_mask_mutation_rejected(self):
  Image.new('L',(24,28),255).save(self.root/c.INPUT_ROOT/'native-hot-mask.png');self.refresh()
  with self.assertRaises(ValueError):c.generate(self.root,self.raw)
 def test_external_hot_support_rejected(self):
  p=self.root/c.INPUT_ROOT/'hot-overlay.png';im=Image.open(p).convert('RGBA');im.putpixel((0,0),(255,0,0,1));im.save(p);self.refresh()
  with self.assertRaises(ValueError):c.generate(self.root,self.raw)
 def test_transparency_and_wrong_canvas_rejected(self):
  for size in [(192,224),(191,224)]:
   Image.new('RGBA',size).save(self.root/c.INPUT_ROOT/'cold-master.png');self.refresh()
   with self.assertRaises(ValueError):c.generate(self.root,self.raw)
 def test_extra_input_duplicate_json_rejected(self):
  j=json.loads(self.raw);j['inputs']['bad']='0'*64
  with self.assertRaises(ValueError):c.generate(self.root,json.dumps(j).encode())
  with self.assertRaises(ValueError):c.generate(self.root,b'{"schema":1,"schema":2}')
 def test_stage_apply_load(self):
  request=Path(self.tmp.name)/'request.json';request.write_bytes(self.raw);dest=Path(self.tmp.name)/'stage';b.stage(self.root,request,dest);b.apply(self.root,dest);self.assertEqual(len(c.load(self.root)),2)
  (self.root/c.HEADER).write_bytes(b'bad')
  with self.assertRaises(ValueError):c.load(self.root)
 def test_tampered_stage_no_writes(self):
  request=Path(self.tmp.name)/'request.json';request.write_bytes(self.raw);dest=Path(self.tmp.name)/'stage';b.stage(self.root,request,dest);(dest/'files'/c.HEADER).write_bytes(b'tampered')
  with self.assertRaises(ValueError):b.apply(self.root,dest)
  self.assertFalse((self.root/c.HEADER).exists())
 def test_stale_input_no_writes(self):
  request=Path(self.tmp.name)/'request.json';request.write_bytes(self.raw);dest=Path(self.tmp.name)/'stage';b.stage(self.root,request,dest);(self.root/c.INPUT_ROOT/'cold-master.png').write_bytes(b'bad')
  with self.assertRaises(ValueError):b.apply(self.root,dest)
  self.assertFalse((self.root/c.HEADER).exists())
 def test_immutable_composition_rehashed_mutations_rejected(self):
  for name in ('pod-composition-mask8x.png','native-peripheral-source.png'):
   raw=(self.root/c.INPUT_ROOT/name).read_bytes();(self.root/c.INPUT_ROOT/name).write_bytes(raw+b'!');self.refresh()
   with self.assertRaises(ValueError):c.generate(self.root,self.raw)
   (self.root/c.INPUT_ROOT/name).write_bytes(raw);self.refresh()
 def test_exact_original_periphery_and_full_opacity(self):
  cold=Image.frombytes('RGBA',(192,224),c.generate(self.root,self.raw)[2][c.IDS[0]][28:])
  matte=Image.open(self.root/c.INPUT_ROOT/'pod-composition-mask8x.png').convert('L')
  original=Image.open(self.root/c.INPUT_ROOT/'native-peripheral-source.png').convert('RGBA').resize(cold.size,Image.Resampling.NEAREST)
  for a,b,w in zip(cold.getdata(),original.getdata(),matte.getdata()):
   self.assertEqual(a[3],255)
   if w==0:self.assertEqual(a,b)
if __name__=='__main__':unittest.main()
