"""Bounded authoring/package checks; deliberately not a sparse-root full gate."""
from pathlib import Path
import copy, hashlib, io, json, shutil, struct, sys, tempfile, unittest
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import current_projectile145_compatibility as c
import current_projectile91_compatibility as old
from build_current_projectile145 import products

class Projectile145Authoring(unittest.TestCase):
 def test_exact_role_geometry_and_payload(self):
  rows=c.load(ROOT);self.assertEqual(set(rows),{'assets/gameplay/enemy-projectile145-145-8.hda'})
  blob=(ROOT/c.ROOT/c.name(c.IDS[0])).read_bytes()
  self.assertEqual(struct.unpack('<4s6I',blob[:28]),(b'HDR1',1500145,8,12,14,0,0))
  self.assertEqual(hashlib.sha256(blob[28:]).hexdigest(),'d5ac9ea2737a93926744581bdd78d80ec6340d8890b961686be0eacdfed0e204')
 def test_all_native_outside_pixels_zero(self):
  blob=(ROOT/c.ROOT/c.name(c.IDS[0])).read_bytes()[28:];self.assertEqual(c.MASK.count('1'),39)
  for y in range(112):
   for x in range(96):
    if c.MASK[(y//8)*12+x//8]=='0':self.assertEqual(blob[(y*96+x)*4:(y*96+x)*4+4],b'\0'*4)
 def test_real_generated_detail_not_nearest_neighbor(self):
  raw=(ROOT/c.ROOT/c.name(c.IDS[0])).read_bytes()[28:]
  varied=0
  for y in range(14):
   for x in range(12):
    colors={raw[((y*8+sy)*96+x*8+sx)*4:((y*8+sy)*96+x*8+sx)*4+4] for sy in range(8) for sx in range(8)}
    varied+=len(colors)>2
  self.assertGreater(varied,25)
  self.assertGreater(sum(0<a<255 for a in raw[3::4]),100)
 def test_direction_is_down_left(self):
  im=Image.open(ROOT/c.PREVIEW).convert('RGBA')
  pts=[(x,y) for y in range(112) for x in range(96) if im.getpixel((x,y))[3]>127]
  mx=sum(x for x,y in pts)/len(pts);my=sum(y for x,y in pts)/len(pts)
  self.assertLess(sum((x-mx)*(y-my) for x,y in pts),0)
  self.assertLess(min(x for x,y in pts),8);self.assertGreater(max(y for x,y in pts),88)
 def test_rebuild_exact(self):
  for name,data in products(ROOT).items():self.assertEqual((ROOT/name).read_bytes(),data)
 def test_member_identity_is_closed(self):
  for identity,density in [(1490091,8),(145,8),(1500145,4),(True,8),(1500145,True)]:
   with self.assertRaises(ValueError):c.name(identity,density)
 def test_selection_rejects_wrong_selector_path_and_hash(self):
  original=json.loads((ROOT/c.SELECTION).read_text())
  for key,value in [('selector',91),('source_png','../private-reference.png'),('source_sha256','0'*64)]:
   j=copy.deepcopy(original);j['masters'][0][key]=value
   with self.assertRaises((ValueError,OSError)):c.selection(ROOT,json.dumps(j).encode())
 def test_png_matches_transport(self):
  blob=(ROOT/c.ROOT/c.name(c.IDS[0])).read_bytes()
  with Image.open(ROOT/c.PREVIEW) as im:self.assertEqual(im.tobytes(),blob[28:])
 def runtime_row(self):
  rows=json.loads((ROOT/'packaging/runtime-assets-v1.json').read_text())['files']
  return next(r for r in rows if r['destination']=='assets/gameplay/'+c.name(c.IDS[0]))
 def test_finite_package_acceptance(self):
  c.validate_runtime_rows(ROOT,{'files':[self.runtime_row()]},True)
 def test_finite_package_negative_rows(self):
  row=self.runtime_row()
  cases=[[],[row,row]]
  for key,value in [('sha256','0'*64),('group','newshf-optin'),('revision','old'),('source_path','elsewhere/'+c.name(c.IDS[0])),('destination','assets/gameplay/ENEMY-PROJECTILE145-145-8.HDA')]:
   r=dict(row);r[key]=value;cases.append([r])
  for rows in cases:
   with self.assertRaises(ValueError):c.validate_runtime_rows(ROOT,{'files':rows},True)
 def test_unrelated_historical_manifest_needs_no_new_inputs(self):
  with tempfile.TemporaryDirectory() as t:c.validate_runtime_rows(Path(t),{'files':[]},False)
 def test_old91_derivation_unchanged_and_independent(self):
  rows=old.load(ROOT);self.assertEqual(set(rows),{'assets/gameplay/enemy-projectile91-91-8.hda'})
  self.assertEqual(next(iter(rows.values()))['sha256'],'2940279a66281c16838d4e070421a581ea0e4b5bb91cf85a1cbc532902933e4c')
 def test_missing_or_corrupt_new_resource_does_not_touch_old_art(self):
  # This is authoring independence; actual runtime admission is a separate C proof.
  with tempfile.TemporaryDirectory() as t:
   t=Path(t)
   for name in old.input_paths(ROOT):
    (t/name).parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,t/name)
   old.load(t)
   with self.assertRaises((ValueError,OSError)):c.load(t)
   for name in c.input_paths(ROOT):
    (t/name).parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,t/name)
   p=t/c.ROOT/c.name(c.IDS[0]);p.write_bytes(p.read_bytes()+b'bad')
   with self.assertRaises(ValueError):c.load(t)
   old.load(t)

if __name__=='__main__':unittest.main()
