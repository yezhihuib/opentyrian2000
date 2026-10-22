"""Mutation controls: changed later code cannot be erased by historical projection."""
import unittest
import json
from shop_published_boundary import ROOT, fixture, project_bytes, stage_spec, check_inventory_names

class ShopProjectionControls(unittest.TestCase):
    def test_all_inverse_spans_reject_mutation_before_projection(self):
        tested = 0
        for stage in ('frame', 'front', 'generator', 'menu', 'product'):
            for name, spec in stage_spec(stage)['files'].items():
                raw = (ROOT / name).read_bytes()
                project_bytes(raw, spec)
                positions = {0, len(raw)//2, len(raw)-1}
                for edit in spec['inverse_edits']:
                    if edit['end'] > edit['start']:
                        positions |= {edit['start'], (edit['start']+edit['end'])//2, edit['end']-1}
                for at in positions:
                    bad = raw[:at] + bytes([raw[at] ^ 1]) + raw[at+1:]
                    with self.subTest(stage=stage, name=name, offset=at):
                        with self.assertRaisesRegex(AssertionError, 'unreviewed current'):
                            project_bytes(bad, spec)
                    tested += 1
        self.assertGreater(tested, 100)

    def test_new_logic_and_truncated_source_rejected(self):
        spec = stage_spec('front')['files']['src/pregame_font.c']
        raw = (ROOT / 'src/pregame_font.c').read_bytes()
        for bad in (raw+b'\nvoid unreviewed_logic(void) {}\n', raw[:-1], raw.replace(b'if(!replay_matches())', b'if(0)', 1)):
            self.assertNotEqual(raw, bad)
            with self.assertRaisesRegex(AssertionError, 'unreviewed current'):
                project_bytes(bad, spec)

    def test_added_or_removed_inventory_paths_rejected(self):
        expected = json.loads(fixture('current-inventory.json'))['files']
        actual = {p for p in expected if p.startswith(('src/', 'assets/'))}
        check_inventory_names(actual, expected)
        for bad in (actual | {'src/unreviewed.c'}, actual | {'assets/unreviewed.hda'}, actual - {'src/game_menu.c'}):
            with self.assertRaisesRegex(AssertionError, 'inventory drift'):
                check_inventory_names(bad, expected)

    def test_original_historical_specs_preserved(self):
        for name in ('frame_integration', 'front_boundary', 'generator_boundary',
                     'menu_font_boundary', 'product_font_integration'):
            self.assertIn(b'BASE', fixture('test_shop_'+name+'.py.historical.txt'))

if __name__ == '__main__':
    unittest.main()
