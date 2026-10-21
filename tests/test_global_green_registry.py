#!/usr/bin/env python3
"""Byte-exact green head/trail reuse and separate source/weapon provenance."""
import hashlib,json,struct,subprocess,sys,tempfile,unittest
from pathlib import Path
from approved_pulse_art_revision import project_previous_art
ROOT=Path(__file__).resolve().parents[1]
def fnv64(data):
 h=14695981039346656037
 for b in data:h=((h^b)*1099511628211)&((1<<64)-1)
 return h
class GreenRegistryTests(unittest.TestCase):
 def setUp(self):
  self.r=json.loads((ROOT/'assets/hd/global-assets-v1/registry.json').read_text());self.f=self.r['families'][13]
 def test_scope_and_independent_sources(self):
  f=self.f;self.assertEqual(f['name'],'green-energy-head-and-trail');self.assertEqual(f['resources'],list(range(80214,80218))+list(range(1060078,1060085)))
  s=f['source_identity'];self.assertEqual(s['head_source']['bank_bytes'],32060);self.assertEqual(s['smoke_source']['bank_bytes'],17810)
  self.assertEqual([t['index'] for t in s['head_source']['tiles']],list(range(214,218)));self.assertEqual([t['index'] for t in s['smoke_source']['tiles']],list(range(78,85)))
  self.assertEqual(s['head_source']['logical_bank'],8);self.assertEqual(s['smoke_source']['logical_bank'],6)
  self.assertNotEqual(s['head_source']['physical_source_sha256'],s['smoke_source']['physical_source_sha256'])
  pal=s['palette'];self.assertEqual((pal['first_index'],pal['count'],pal['block_index']),(0,256,5));self.assertEqual(hashlib.sha256(bytes.fromhex(''.join(pal['rgb_hex']))).hexdigest(),pal['rgb_sha256'])
  for recid,packed,r in zip([71,1071],[71,890],s['weapon_records']):
   self.assertEqual((r['record_index'],r['packed_index'],r['record_bytes']),(recid,packed,80));self.assertEqual(r['record_fnv64_variants'],['75782e3c7d7b8cae']*3)
   self.assertEqual([v['physical_source'] for v in r['variants']],['tyrian.hdt','tyrian4.lvl','tyrian5.lvl'])
  h=f['draw_semantics']['head_contract'];self.assertEqual(h['animation_length'],4);self.assertEqual(h['origin'],'shotX+1,shotY')
  smoke=f['draw_semantics']['smoke_contract'];self.assertEqual((smoke['input_types'],smoke['initial_sprite'],smoke['initial_ttl']),([12],76,7));self.assertFalse(smoke['fixedPosition']);self.assertFalse(smoke['followPlayer'])
 def test_unchanged_previous_and_eleven_resources(self):
  baseline=json.loads(subprocess.check_output(['git','show','d5b08f5d9cde1dea43819daaa8a52bc8f211e20b:assets/hd/global-assets-v1/registry.json'],cwd=ROOT))
  self.assertEqual(project_previous_art(self.r['resources'][:109]),baseline['resources']);self.assertEqual(self.r['families'][:13],baseline['families']);self.assertEqual(len(self.r['resources']),120);self.assertEqual(len(self.r['families']),14)
  m=json.loads((ROOT/'assets/hd/manifest.json').read_text())
  for identity,r in zip(self.f['resources'],self.r['resources'][109:120]):
   p=ROOT/'assets/hd/global-assets-v1'/r['path'];b=p.read_bytes();self.assertFalse(p.is_symlink());self.assertEqual(len(b),43036);self.assertEqual(b[:4],b'HDR1')
   self.assertEqual(list(struct.unpack('<6I',b[4:28])),[identity,8,12,14,0,0]);self.assertEqual(hashlib.sha256(b).hexdigest(),r['sha256']);self.assertEqual(f'{fnv64(b[28:]):016x}',r['payload_fnv64']);self.assertEqual(r['path'],'content/'+r['sha256']+'.hda')
   prov=r['provenance'];self.assertEqual(b,(ROOT/'assets/hd/packs'/prov['pack']/prov['file']).read_bytes());old=m['packs'][prov['pack']]['files'][prov['file']];self.assertEqual(r['sha256'],old['sha256']);self.assertEqual(hashlib.sha256((ROOT/prov['source_png']).read_bytes()).hexdigest(),old['source_png_sha256'])
 def test_generated_header_exact(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'pins.h';subprocess.run([sys.executable,str(ROOT/'scripts/build_global_registry_header.py'),'--registry',str(ROOT/'assets/hd/global-assets-v1/registry.json'),'--output',str(p)],check=True,capture_output=True);self.assertEqual(p.read_bytes(),(ROOT/'src/global_asset_registry.h').read_bytes())
 def test_generator_rejects_wrong_family_identity(self):
  with tempfile.TemporaryDirectory() as d:
   d=Path(d);r=self.r;r['families'][13]['name']='moving-white-smoke';p=d/'bad.json';p.write_text(json.dumps(r));v=subprocess.run([sys.executable,str(ROOT/'scripts/build_global_registry_header.py'),'--registry',str(p),'--output',str(d/'pins.h')],capture_output=True)
   self.assertNotEqual(v.returncode,0);self.assertFalse((d/'pins.h').exists())
if __name__=='__main__':unittest.main()
