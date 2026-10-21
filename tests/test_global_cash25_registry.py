#!/usr/bin/env python3
"""Exact approved cash25 resource reuse and two-source registry invariants."""
import hashlib
import json
import re
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from approved_pulse_art_revision import project_previous_art
ROOT = Path(__file__).resolve().parents[1]

def fnv64(data):
    value = 14695981039346656037
    for byte in data:
        value = ((value ^ byte) * 1099511628211) & ((1 << 64) - 1)
    return value

class Cash25RegistryTests(unittest.TestCase):
    def setUp(self):
        self.registry = json.loads((ROOT / 'assets/hd/global-assets-v1/registry.json').read_text())
        self.family = self.registry['families'][7]

    def test_exact_body_and_value_role_scope(self):
        f = self.family
        self.assertEqual(f['name'], 'cash25-body-and-value')
        self.assertEqual(f['resources'], list(range(1120007,1120013))+[1130185])
        source = f['source_identity']
        self.assertEqual(source['bank_bytes'],29032)
        self.assertEqual([t['index'] for t in source['tiles']],list(range(7,13)))
        self.assertEqual(source['value_source']['bank_bytes'],17810)
        self.assertEqual([t['index'] for t in source['value_source']['tiles']],[185])
        self.assertEqual(source['enemy_identity']['record_index'],391)
        self.assertEqual(source['enemy_identity']['record_bytes'],77)
        self.assertEqual(source['enemy_identity']['record_fnv64_variants'],['a6033f1c8ab03dd3'])
        variants=source['enemy_identity']['variants']
        self.assertEqual([v['physical_source'] for v in variants],['tyrian.hdt','tyrian4.lvl','tyrian5.lvl'])
        self.assertEqual(len(set(v['record_sha256'] for v in variants)),1)
        contract=f['draw_semantics']
        self.assertEqual(contract['body_contract']['record_index'],391)
        self.assertEqual(contract['body_contract']['part'],0)
        value=contract['value_contract']
        self.assertEqual((value['type'],value['index'],value['sprite']),(36,185,184))
        self.assertTrue(value['fixedPosition'])
        self.assertFalse(value['followPlayer'])
        self.assertEqual(value['deltaY'],0)
        self.assertEqual(value['ttl_at_draw'],list(range(8,0,-1)))
        pal=source['palette']
        self.assertEqual(pal['indices'],list(range(20,32))+[137,138,141,142,144,161])
        self.assertEqual(hashlib.sha256(bytes.fromhex(''.join(pal['rgb_hex']))).hexdigest(),pal['rgb_sha256'])

    def test_fixed_type_matches_actual_native_table_not_comments(self):
        source=(ROOT/'src/varz.c').read_text()
        start=source.index('} explosion_data[')
        end=source.index('};',start)
        rows=[tuple(map(int,m)) for m in re.findall(r'\{\s*(\d+)\s*,\s*(\d+)\s*\}',source[start:end])]
        value=self.family['draw_semantics']['value_contract']
        self.assertEqual(rows[value['type']],(value['sprite'],8))
        self.assertEqual(value['type'],36)

    def test_seven_resources_are_exact_existing_approved_bytes(self):
        resources=self.registry['resources'][68:75]
        manifest=json.loads((ROOT/'assets/hd/manifest.json').read_text())
        self.assertEqual(len(resources),7)
        for n,r in enumerate(resources):
            p=ROOT/'assets/hd/global-assets-v1'/r['path']
            self.assertFalse(p.is_symlink())
            b=p.read_bytes()
            self.assertEqual(len(b),43036)
            self.assertEqual(hashlib.sha256(b).hexdigest(),r['sha256'])
            self.assertEqual(r['path'],'content/'+r['sha256']+'.hda')
            self.assertEqual(b[:4],b'HDR1')
            self.assertEqual(list(struct.unpack('<6I',b[4:28])),[1120007+n if n<6 else 1130185,8,12,14,0,0])
            self.assertEqual(f'{fnv64(b[28:]):016x}',r['payload_fnv64'])
            provenance=r['provenance']
            old=ROOT/'assets/hd/packs'/provenance['pack']/provenance['file']
            self.assertEqual(b,old.read_bytes())
            approval=manifest['packs'][provenance['pack']]['files'][provenance['file']]
            self.assertEqual(approval['sha256'],r['sha256'])
            self.assertEqual(hashlib.sha256((ROOT/provenance['source_png']).read_bytes()).hexdigest(),approval['source_png_sha256'])

    def test_previous_seven_families_and_resources_unchanged(self):
        base=json.loads(subprocess.check_output(['git','show','ee1e98cfc6b8c00cb9a1837e4aa2c3a9aca2b0e5:assets/hd/global-assets-v1/registry.json'],cwd=ROOT))
        self.assertEqual(self.registry['families'][:7],base['families'])
        self.assertEqual(project_previous_art(self.registry['resources'][:68]),base['resources'])
        self.assertEqual(len(self.registry['families']),14)
        self.assertEqual(len(self.registry['resources']),120)

    def test_generator_reproduces_checked_in_header(self):
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/'pins.h'
            subprocess.run([sys.executable,str(ROOT/'scripts/build_global_registry_header.py'),'--registry',str(ROOT/'assets/hd/global-assets-v1/registry.json'),'--output',str(output)],check=True,capture_output=True)
            self.assertEqual(output.read_bytes(),(ROOT/'src/global_asset_registry.h').read_bytes())

if __name__=='__main__':
    unittest.main()
