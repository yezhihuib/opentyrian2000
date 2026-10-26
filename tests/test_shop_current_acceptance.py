"""Current-only acceptance: originals remain independently runnable and fail closed."""
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET
from collections import Counter
import difflib
import re
from shop_current_acceptance import (ROOT, INVENTORY, check_current_inventory,
    check_names, verify_bytes, check_live_guards, check_menu_lease, check_original_menu_lease)
from shop_published_boundary import fixture, check_pin_assets, published_source, stage_spec, project_bytes

class ShopCurrentAcceptance(unittest.TestCase):
    def test_committed_current_inventory(self):
        check_current_inventory()

    def test_frame_format_provenance_and_reproducible_export(self):
        asset = ROOT / 'assets/shop-frame-v1'
        manifest = json.loads((asset/'shop-frame-metal-v1.json').read_bytes())
        raw = (asset/'shop-frame-metal-v1.hda').read_bytes()
        self.assertEqual(len(raw), 1276948)
        self.assertEqual(len(raw), manifest['file_bytes'])
        verify_bytes(raw, manifest['file_sha256'], 'PMF1')
        for key in ('source', 'layout_mask'):
            row = manifest[key]
            verify_bytes((asset/row['file']).read_bytes(), row['sha256'], key)
        self.assertEqual(raw[:4], b'PMF1')
        self.assertEqual(struct.unpack_from('<15I',raw,4), (1,320,200,4,1280,800,2492,314221,1276820,4,1,0,0,0,0))
        self.assertEqual(struct.unpack_from('<QQ',raw,64), (0x45a77a2246c174b9,0x1c6687307999bd82))
        self.assertEqual(raw[88:128], bytes(40))
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'frame.hda'
            subprocess.run(['python3',str(ROOT/'scripts/export_shop_frame.py'),'--out',str(out)],check=True,stdout=subprocess.DEVNULL)
            self.assertEqual(raw,out.read_bytes())

    def test_front_original_resource_and_source_contract(self):
        pin=check_pin_assets('front')
        verify_bytes(published_source('front','src/pregame_font.c'),pin['accepted_sha256']['src/pregame_font.c'],'front accepted source')

    def test_generator_original_resource_and_source_contract(self):
        pin=check_pin_assets('generator')
        verify_bytes(published_source('generator','src/pregame_font.c'),pin['accepted_sha256']['src/pregame_font.c'],'generator accepted source')

    def test_menu_original_assets_and_current_bounded_leases(self):
        check_pin_assets('menu_font')
        check_original_menu_lease(published_source('menu','src/pregame_font.c').decode())
        check_menu_lease((ROOT/'src/pregame_font.c').read_text())

    def test_product_original_observer_delta_and_current_tail(self):
        parent=fixture('product-parent-game_menu.c.txt').decode()
        stage=published_source('product','src/game_menu.c').decode()
        calls=[]
        for line in difflib.unified_diff(parent.splitlines(True),stage.splitlines(True),n=0):
            if line.startswith(('+++','---','@@')): continue
            self.assertFalse(line.startswith('-'), 'original menu line removed')
            if line.startswith('+') and line[1:].strip():
                call=line[1:].strip()
                self.assertRegex(call,r'^pregame_font_[a-z_]+\([^;]*\);$')
                self.assertFalse(any(token in call for token in ('++','--','+=','-=','->cash')))
                calls.append(call.split('(')[0])
        self.assertEqual(Counter(calls),Counter(pregame_font_product_begin=1,pregame_font_run_begin=8,pregame_font_run_end=8,pregame_font_product_update_begin=2,pregame_font_product_update_end=2,pregame_font_cursor_erased=1))
        check_live_guards((ROOT/'src/pregame_font.c').read_text())

    def test_current_replay_masks_and_bounds(self):
        check_live_guards((ROOT/'src/pregame_font.c').read_text())

    def test_frame_protected_owners_reviewed_finite_public_delta(self):
        from shop_current_acceptance import reviewed_frame_owner
        for name in stage_spec('frame')['files']:
            reviewed_frame_owner(name,(ROOT/name).read_bytes())
        for name in ('src/sprite.c','visualc/opentyrian.vcxproj'):
            raw=(ROOT/name).read_bytes()
            for bad in (raw+b'\nunreviewed\n',raw[:-1],raw.replace(b'enemy_reuse',b'enemy_reusz',1)):
                with self.assertRaisesRegex(AssertionError,'current identity drift'):
                    reviewed_frame_owner(name,bad)

    def test_current_compile_inventory(self):
        ns={'m':'http://schemas.microsoft.com/developer/msbuild/2003'}
        tree=ET.parse(ROOT/'visualc/opentyrian.vcxproj')
        rows=[x.attrib['Include'] for x in tree.findall('.//m:ClCompile',ns) if 'Include' in x.attrib]
        self.assertEqual(len(rows),len(set(rows)))
        self.assertEqual({Path(x.replace('\\','/')).name for x in rows},{x.name for x in (ROOT/'src').glob('*.c')})

    def test_original_specs_byte_exact(self):
        for name in ('frame_integration','front_boundary','generator_boundary','menu_font_boundary','product_font_integration'):
            self.assertIn(b'BASE',fixture('test_shop_'+name+'.py.historical.txt'))

    def test_resource_mutations_rejected_by_real_identity_validator(self):
        for kind in ('front','generator','menu_font'):
            pin=check_pin_assets(kind)
            for name,wanted in pin['accepted_sha256'].items():
                if not name.startswith('assets/'): continue
                raw=(ROOT/name).read_bytes()
                for at in {0,len(raw)//2,len(raw)-1}:
                    with self.subTest(name=name,offset=at), self.assertRaisesRegex(AssertionError,'current identity drift'):
                        verify_bytes(raw[:at]+bytes([raw[at]^1])+raw[at+1:],wanted,name)

    def test_current_path_mutations_rejected(self):
        expected=json.loads(INVENTORY.read_bytes())['files']
        actual={n for n in expected if n.startswith(('src/','assets/'))}
        for bad in (actual|{'src/unreviewed.c'},actual|{'assets/unreviewed.hda'},actual-{'src/game_menu.c'}):
            with self.assertRaisesRegex(AssertionError,'current path inventory drift'):
                check_names(bad,expected)

    def test_semantic_guard_mutations_rejected_without_hash_gate(self):
        source=(ROOT/'src/pregame_font.c').read_text()
        for value in ('SF_EVENTS=65536','SF_CAP=16*1024*1024','sf.event_count==SF_EVENTS','sf.count>sf.static_count','if(!replay_matches())','p/SF_W>=185','sf.product&&sf.run_role==PREGAME_CASH'):
            self.assertIn(value,source)
            with self.subTest(guard=value),self.assertRaises(AssertionError):
                check_live_guards(source.replace(value,'MUTATED',1))
        for value in ('common_menu_runs_generation(sf.fixed_family)!=sf.fixed_generation','sf.fixed_count==PF_FIXED_SLOTS','strcmp(plain,run.text)'):
            with self.subTest(lease=value),self.assertRaises(AssertionError):
                check_menu_lease(source.replace(value,'MUTATED',1))

    def test_retained_current_projection_mutations(self):
        count=0
        for stage in ('front','generator','menu','product'):
            for name,spec in stage_spec(stage)['files'].items():
                raw=(ROOT/name).read_bytes(); project_bytes(raw,spec)
                positions={0,len(raw)//2,len(raw)-1}
                for edit in spec['inverse_edits']:
                    if edit['end']>edit['start']:positions|={edit['start'],(edit['start']+edit['end'])//2,edit['end']-1}
                for at in positions:
                    with self.assertRaisesRegex(AssertionError,'unreviewed current'):
                        project_bytes(raw[:at]+bytes([raw[at]^1])+raw[at+1:],spec)
                    count+=1
        self.assertGreater(count,100)

if __name__=='__main__': unittest.main()
