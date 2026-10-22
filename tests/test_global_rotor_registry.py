#!/usr/bin/env python3
"""Byte-exact eight-pose rotor reuse and native record/quadrant source pins."""
import hashlib,json,struct,subprocess,sys,tempfile,unittest
from historical_global_fixtures import registry_at
from pathlib import Path
from approved_pulse_art_revision import project_previous_art
ROOT=Path(__file__).resolve().parents[1]
def fnv64(data):
 h=14695981039346656037
 for b in data:h=((h^b)*1099511628211)&((1<<64)-1)
 return h
class RotorRegistryTests(unittest.TestCase):
 def setUp(self):self.r=json.loads((ROOT/'assets/hd/global-assets-v1/registry.json').read_text())
 def test_scope_and_source(self):
  f=self.r['families'][12];self.assertEqual(f['name'],'rotor-enemy-5-and-11');self.assertEqual(f['resources'],[1010000+i for i in range(229,244,2)])
  s=f['source_identity'];self.assertEqual(s['shape_table_id'],1);self.assertEqual(s['physical_source'],'NEWSH2')
  self.assertEqual([t['index'] for t in s['tiles']],sorted(set(i+p for i in range(229,244,2) for p in [0,1,19,20])))
  self.assertEqual([r['record_index'] for r in s['enemy_records']],[5,11]);self.assertEqual(s['palette']['count'],256);self.assertEqual(s['palette']['block_index'],5);self.assertEqual(hashlib.sha256(bytes.fromhex(''.join(s['palette']['rgb_hex']))).hexdigest(),s['palette']['rgb_sha256'])
  for r in s['enemy_records']:
   self.assertEqual(r['record_bytes'],77);self.assertEqual([v['physical_source'] for v in r['variants']],['tyrian.hdt','tyrian4.lvl','tyrian5.lvl'])
   self.assertEqual(r['record_fnv64_variants'],sorted(set(v['record_fnv64'] for v in r['variants'])))
  b=f['draw_semantics']['body_contract'];self.assertEqual(b['forward'],list(range(229,244,2)));self.assertEqual(b['reverse'],list(range(243,228,-2)));self.assertEqual(b['parts'],[0,1,19,20]);self.assertEqual(b['size'],1)
 def test_unchanged_previous_and_eight_resources(self):
  baseline=registry_at('d418bc85e3033936a1f8d263679aeaba0e3640b7')
  self.assertEqual(project_previous_art(self.r['resources'][:101]),baseline['resources']);self.assertEqual(self.r['families'][:12],baseline['families']);self.assertGreaterEqual(len(self.r['resources']),109);self.assertGreaterEqual(len(self.r['families']),13)
  m=json.loads((ROOT/'assets/hd/manifest.json').read_text())
  for i,r in zip(range(229,244,2),self.r['resources'][101:109]):
   p=ROOT/'assets/hd/global-assets-v1'/r['path'];b=p.read_bytes();self.assertFalse(p.is_symlink());self.assertEqual(len(b),172060);self.assertEqual(b[:4],b'HDR1')
   self.assertEqual(list(struct.unpack('<6I',b[4:28])),[1010000+i,8,24,28,6,7]);self.assertEqual(hashlib.sha256(b).hexdigest(),r['sha256']);self.assertEqual(f'{fnv64(b[28:]):016x}',r['payload_fnv64'])
   prov=r['provenance'];self.assertEqual(b,(ROOT/'assets/hd/packs'/prov['pack']/prov['file']).read_bytes());old=m['packs'][prov['pack']]['files'][prov['file']];self.assertEqual(r['sha256'],old['sha256']);self.assertEqual(hashlib.sha256((ROOT/prov['source_png']).read_bytes()).hexdigest(),old['source_png_sha256'])
 def test_generated_header_exact(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'pins.h';subprocess.run([sys.executable,str(ROOT/'scripts/build_global_registry_header.py'),'--registry',str(ROOT/'assets/hd/global-assets-v1/registry.json'),'--output',str(p)],check=True,capture_output=True);self.assertEqual(p.read_bytes(),(ROOT/'src/global_asset_registry.h').read_bytes())
if __name__=='__main__':unittest.main()
