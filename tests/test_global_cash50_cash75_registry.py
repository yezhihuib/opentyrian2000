#!/usr/bin/env python3
"""Byte-exact approved Cash50/75 reuse and native two-role registry proof."""
import hashlib,json,re,struct,subprocess,sys,tempfile,unittest
from historical_global_fixtures import registry_at
from pathlib import Path
from approved_pulse_art_revision import project_previous_art
ROOT=Path(__file__).resolve().parents[1]
def fnv64(data):
 h=14695981039346656037
 for b in data:h=((h^b)*1099511628211)&((1<<64)-1)
 return h
class Cash50Cash75RegistryTests(unittest.TestCase):
 def setUp(self):
  self.r=json.loads((ROOT/'assets/hd/global-assets-v1/registry.json').read_text())
 def test_exact_scope_and_native_fixed_initializer(self):
  source=(ROOT/'src/varz.c').read_text();start=source.index('} explosion_data[');end=source.index('};',start)
  rows=[tuple(map(int,m)) for m in re.findall(r'\{\s*(\d+)\s*,\s*(\d+)\s*\}',source[start:end])]
  for f,value,record,lo,popup,typ,prefix,vid in [(self.r['families'][8],50,392,26,204,37,1160000,1170204),(self.r['families'][9],75,393,20,223,38,1140000,1150223)]:
   with self.subTest(value=value):
    self.assertEqual(f['name'],f'cash{value}-body-and-value')
    self.assertEqual(f['resources'],[prefix+i for i in range(lo,lo+6)]+[vid])
    s=f['source_identity'];self.assertEqual(s['bank_bytes'],29032);self.assertEqual(s['logical_bank'],11)
    self.assertEqual([t['index'] for t in s['tiles']],list(range(lo,lo+6)))
    self.assertEqual(s['value_source']['bank_bytes'],17810);self.assertEqual([t['index'] for t in s['value_source']['tiles']],[popup])
    e=s['enemy_identity'];self.assertEqual(e['record_index'],record);self.assertEqual(e['record_bytes'],77)
    self.assertEqual([v['physical_source'] for v in e['variants']],['tyrian.hdt','tyrian4.lvl','tyrian5.lvl'])
    self.assertEqual(len(set(v['record_sha256'] for v in e['variants'])),1)
    self.assertEqual(e['record_fnv64_variants'],sorted(set(v['record_fnv64'] for v in e['variants'])))
    p=s['palette'];self.assertEqual(hashlib.sha256(bytes.fromhex(''.join(p['rgb_hex']))).hexdigest(),p['rgb_sha256'])
    b=f['draw_semantics']['body_contract'];self.assertEqual(b['record_index'],record);self.assertEqual(b['source_indices'],list(range(lo,lo+6)));self.assertEqual(b['part'],0);self.assertTrue(b['scoreitem'])
    v=f['draw_semantics']['value_contract'];self.assertEqual((v['type'],v['index'],v['sprite']),(typ,popup,popup-1));self.assertEqual(rows[typ],(popup-1,8));self.assertEqual(v['ttl_at_draw'],list(range(8,0,-1)));self.assertTrue(v['fixedPosition']);self.assertFalse(v['followPlayer']);self.assertEqual(v['deltaY'],0)
 def test_all_fourteen_resources_byte_identical(self):
  manifest=json.loads((ROOT/'assets/hd/manifest.json').read_text())
  resources=self.r['resources'][75:89];self.assertEqual(len(resources),14)
  for r in resources:
   with self.subTest(identity=r['identity']):
    path=ROOT/'assets/hd/global-assets-v1'/r['path'];self.assertFalse(path.is_symlink());b=path.read_bytes()
    self.assertEqual(len(b),43036);self.assertEqual(hashlib.sha256(b).hexdigest(),r['sha256']);self.assertEqual(r['path'],'content/'+r['sha256']+'.hda');self.assertEqual(b[:4],b'HDR1')
    self.assertEqual(list(struct.unpack('<6I',b[4:28])),[r['identity'],8,12,14,0,0]);self.assertEqual(f'{fnv64(b[28:]):016x}',r['payload_fnv64'])
    p=r['provenance'];self.assertEqual(b,(ROOT/'assets/hd/packs'/p['pack']/p['file']).read_bytes());approval=manifest['packs'][p['pack']]['files'][p['file']];self.assertEqual(approval['sha256'],r['sha256']);self.assertEqual(hashlib.sha256((ROOT/p['source_png']).read_bytes()).hexdigest(),approval['source_png_sha256'])
 def test_previous_eight_families_and_75_resources_unchanged(self):
  baseline=registry_at('42453a546c79bcb0de6fc4c09b8370adf90660f8')
  self.assertEqual(self.r['families'][:8],baseline['families']);self.assertEqual(project_previous_art(self.r['resources'][:75]),baseline['resources']);self.assertEqual(len(self.r['resources']),120);self.assertEqual(len(self.r['families']),14)
  self.assertEqual(len(set(r['identity'] for r in self.r['resources'])),120)
 def test_generated_header_exact(self):
  with tempfile.TemporaryDirectory() as d:
   target=Path(d)/'pins.h';subprocess.run([sys.executable,str(ROOT/'scripts/build_global_registry_header.py'),'--registry',str(ROOT/'assets/hd/global-assets-v1/registry.json'),'--output',str(target)],check=True,capture_output=True)
   self.assertEqual(target.read_bytes(),(ROOT/'src/global_asset_registry.h').read_bytes())
if __name__=='__main__':unittest.main()
