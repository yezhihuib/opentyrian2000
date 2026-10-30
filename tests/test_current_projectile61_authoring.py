"""Bounded authoring/package checks; deliberately not a sparse-root full gate."""
from pathlib import Path
import copy, hashlib, io, json, shutil, struct, sys, tempfile, unittest
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import current_projectile61_compatibility as c
import current_projectile91_compatibility as old
import current_projectile145_compatibility as prior
from build_current_projectile61 import products


def qualified61_source(name):
 # Preserve this historical source assertion against exact qualified310 bytes.
 # No sibling checkout/Git/history fallback or arbitrary cached caller map.
 import projectile_blue_triplet_projection as newest
 raw=newest.project_source(name,newest.checked_read(ROOT,name))
 assert newest.sha(raw)==newest.ledger()['base_source_inventory'][name],('qualified61 source drift',name)
 return raw.decode()


class Projectile61Authoring(unittest.TestCase):
 def test_exact_role_geometry_and_payload(self):
  rows=c.load(ROOT);self.assertEqual(set(rows),{'assets/gameplay/enemy-projectile61-61-8.hda'})
  blob=(ROOT/c.ROOT/c.name(c.IDS[0])).read_bytes()
  self.assertEqual(struct.unpack('<4s6I',blob[:28]),(b'HDR1',1510061,8,12,14,0,0))
  self.assertEqual(hashlib.sha256(blob[28:]).hexdigest(),'8f4d0ebc154383ece77d49e9818ce60c4e7f0239765c1b02e26e09028a7435a1')
 def test_all_native_outside_pixels_zero(self):
  blob=(ROOT/c.ROOT/c.name(c.IDS[0])).read_bytes()[28:];self.assertEqual(c.MASK.count('1'),74)
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
 def test_twin_lobes_and_downward_bright_heads(self):
  with Image.open(ROOT/c.PREVIEW) as src:im=src.convert('RGBA')
  self.assertFalse(any(im.crop((32,0,64,112)).tobytes()))
  for x in (0,64):
   top=sum(sum(v[:3])*v[3] for v in im.crop((x,8,x+32,32)).getdata())
   bottom=sum(sum(v[:3])*v[3] for v in im.crop((x,64,x+32,96)).getdata())
   self.assertGreater(bottom,top)
  for y in range(14):
   for x in range(12):
    if c.MASK[y*12+x]=='1':self.assertTrue(any(im.crop((x*8,y*8,x*8+8,y*8+8)).getchannel('A').tobytes()))
 def test_rebuild_exact(self):
  for name,data in products(ROOT).items():self.assertEqual((ROOT/name).read_bytes(),data)
 def test_member_identity_is_closed(self):
  for identity,density in [(1490091,8),(1500145,8),(61,8),(1510061,4),(True,8),(1510061,True)]:
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
  for key,value in [('sha256','0'*64),('group','newshf-optin'),('revision','old'),('source_path','elsewhere/'+c.name(c.IDS[0])),('destination','assets/gameplay/ENEMY-PROJECTILE61-61-8.HDA')]:
   r=dict(row);r[key]=value;cases.append([r])
  for rows in cases:
   with self.assertRaises(ValueError):c.validate_runtime_rows(ROOT,{'files':rows},True)
 def test_unrelated_historical_manifest_needs_no_new_inputs(self):
  with tempfile.TemporaryDirectory() as t:c.validate_runtime_rows(Path(t),{'files':[]},False)
 def test_old91_derivation_unchanged_and_independent(self):
  rows=old.load(ROOT);self.assertEqual(set(rows),{'assets/gameplay/enemy-projectile91-91-8.hda'})
  self.assertEqual(next(iter(rows.values()))['sha256'],'2940279a66281c16838d4e070421a581ea0e4b5bb91cf85a1cbc532902933e4c')
  previous=prior.load(ROOT);self.assertEqual(next(iter(previous.values()))['sha256'],'e4863397d4d7e9874e96e642ce6596c90e99009014b746491016c0423e099c83')
 def test_missing_or_corrupt_new_resource_does_not_touch_old_art(self):
  # This is authoring independence; actual runtime admission is a separate C proof.
  with tempfile.TemporaryDirectory() as t:
   t=Path(t)
   for name in old.input_paths(ROOT)|prior.input_paths(ROOT):
    (t/name).parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,t/name)
   old.load(t);prior.load(t)
   with self.assertRaises((ValueError,OSError)):c.load(t)
   for name in c.input_paths(ROOT):
    (t/name).parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,t/name)
   p=t/c.ROOT/c.name(c.IDS[0]);p.write_bytes(p.read_bytes()+b'bad')
   with self.assertRaises(ValueError):c.load(t)
   old.load(t);prior.load(t)

 def test_finite_source_dispatch_draft(self):
  owner=qualified61_source('src/global_projectile91_mirror.inc')
  self.assertIn('index==91?1u:index==145?2u:index==61?4u:0u',owner)
  self.assertIn('global_projectile91_used_members&4u',owner)
  self.assertIn('&&!xmas&&',owner)
  self.assertIn('sprite == 145 || sprite == 61)',qualified61_source('src/tyrian2.c'))
  self.assertIn('game_probe_scene_draw(151,index,x,y,0,ENTITY_NORMAL,mirrored)',qualified61_source('src/entity_draw.c'))
 def test_finite_palette_and_complete_normal_bank_guard_draft(self):
  text=(ROOT/'src/enemy_projectile61_mirror.inc').read_text()
  self.assertIn('return index==61&&projectile91_source(bank,91);',text)
  self.assertIn('113,114,115,116,117,118,119,120,121,122,123,124',text)
  self.assertIn('game_probe_density!=8',text)

if __name__=='__main__':unittest.main()
