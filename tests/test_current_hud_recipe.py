"""Exact baseline replay and bounded synthetic authoring checks."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
import sys
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
spec = importlib.util.spec_from_file_location('current_hud_recipe', ROOT/'scripts/current_hud_recipe.py')
hud = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hud)


class HudRecipeTests(unittest.TestCase):
    def test_six_baselines(self):
        for key, contract in hud.CONTRACTS.items():
            with self.subTest(key=key):
                raw, pins = hud.render_resource(ROOT, key, hud.DEFAULT_SELECTION[key])
                self.assertEqual(hashlib.sha256(raw).hexdigest(), contract['baseline_sha256'])
                self.assertEqual(bool(pins), key == 'meters')

    def test_default_selection_is_independent(self):
        selection = hud.default_selection()
        selection['static'][0]['path'] = 'changed'
        self.assertNotEqual(selection, hud.default_selection())

    def test_invalid_source_and_shape(self):
        for record in ({'path':'../bad','sha256':'0'*64}, {'path':'/bad','sha256':'0'*64},
                       {'path':'assets/missing.png','sha256':'0'*64}):
            with self.subTest(record=record), self.assertRaises(ValueError):
                hud.render_resource(ROOT, 'static', [record])
        with self.assertRaises(ValueError):
            hud.render_resource(ROOT, 'components', [])
        selection = hud.default_selection()['font']
        selection[0]['sha256'] = '0'*64
        with self.assertRaises(ValueError):
            hud.render_resource(ROOT, 'font', selection)

    def fixture(self, root, key):
        records = hud.default_selection()[key]
        for record in records + list(hud.FIXED_INPUTS.values()):
            target = root/record['path']
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT/record['path']).read_bytes())
        return records

    def replace_png(self, root, record, change):
        path = root/record['path']
        with Image.open(path) as source:
            image = source.copy()
        change(image)
        image.save(path)
        record['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()

    def test_authored_tile_changes_but_structure_does_not(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            sources = self.fixture(root, 'components')
            old, _ = hud.render_resource(root, 'components', sources)
            self.replace_png(root,sources[0], lambda im: im.putpixel((0,0),(12,34,56,255)))
            new, _ = hud.render_resource(root, 'components', sources)
            self.assertNotEqual(new, old)
            self.assertEqual(new[:40],old[:40])
            self.assertEqual(new[48:64],old[48:64])
            self.replace_png(root,sources[0], lambda im: im.putpixel((0,0),(12,34,56,0)))
            with self.assertRaises(ValueError):
                hud.render_resource(root, 'components', sources)

    def test_static_mask_and_font_padding_are_not_authorable(self):
        for key in ('static','font'):
            with self.subTest(key=key), tempfile.TemporaryDirectory() as td:
                root=Path(td);sources=self.fixture(root,key)
                self.replace_png(root,sources[0], lambda im: im.putpixel((0,0),(0,0,0,255)))
                with self.assertRaises(ValueError):
                    hud.render_resource(root,key,sources)

    def test_symlinks_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); (root/'alias').symlink_to(ROOT/hud.DEFAULT_SELECTION['font'][0]['path'])
            with self.assertRaises(ValueError):
                hud.checked(root, {'path':'alias','sha256':hud.DEFAULT_SELECTION['font'][0]['sha256']})

    def test_meter_color_update_keeps_lookup_and_source_guards(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            records = self.fixture(root, 'meters')
            path = root/records[0]['path']
            colors = json.loads(path.read_text())
            colors['firepower']['116'] = [135,4,0]
            path.write_text(json.dumps(colors))
            records[0]['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
            new, pins = hud.render_resource(root, 'meters', records)
            old = (ROOT/hud.FIXED_INPUTS['meter_baseline']['path']).read_bytes()
            self.assertNotEqual(new[112:4336], old[112:4336])
            self.assertEqual(new[:64], old[:64])
            self.assertEqual(new[4336:], old[4336:])
            self.assertEqual(pins['HUD_METERS_LOOKUP_FNV'], 0x1d129d23c2edc134)

    def test_meter_json_validation_precedes_recipe(self):
        for colors in ({}, {'firepower':{}}, {'firepower':[], 'armor':{}, 'generator':{}}):
            with self.assertRaises(ValueError):
                hud.meter_payload(ROOT,json.dumps(colors).encode())


if __name__ == '__main__':
    unittest.main()
