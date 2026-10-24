"""Fail-closed controls for separate historical and current frontend proofs."""
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import accepted_later_changes as projection
from frontend_history_support import (
    ROOT, FIXTURES, INDEX_SHA256, PUBLIC, NativeSources, production_inventory,
    validate_production_map, verify_bytes, git,
)


class FrontendHistorySupportTests(unittest.TestCase):
    def test_original_native_source_inventory_and_bytes(self):
        for kind, count in [('pregame', 148), ('settings', 140)]:
            source = NativeSources(kind)
            self.assertEqual(len(source.paths()), count)
            for name in source.paths():
                self.assertTrue(source.read(name), name)
            with self.assertRaises(KeyError):
                source.read('src/unlisted.c')

    def test_native_index_and_exception_bytes_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory)
            shutil.copytree(FIXTURES, destination, dirs_exist_ok=True)
            for kind in ('pregame', 'settings'):
                path = destination/(kind+'-native-render_mirror.c')
                path.write_bytes(path.read_bytes()+b'\n')
                with self.assertRaises(AssertionError):
                    NativeSources(kind, fixtures=destination).read('src/render_mirror.c')
            index = destination/'index.json'
            index.write_bytes(index.read_bytes()+b' ')
            with self.assertRaises(AssertionError):
                NativeSources('pregame', fixtures=destination)
            with self.assertRaises(AssertionError):
                verify_bytes(b'{}', INDEX_SHA256)

    def test_resource_anchors_equal_original_published_receipt(self):
        receipt = json.loads(git(ROOT, 'show', '4597e39c75b949d8f4e1f22bbc6117b432294132:docs/pregame-font-v1/COEXISTENCE-RECEIPT.json'))
        resources = NativeSources('pregame').index['resources']
        self.assertEqual(resources, receipt['coexistence']['startup_resources'])
        self.assertEqual(len(resources), 9)

    def test_current_mutations_inside_and_outside_later_change_set(self):
        inventory = production_inventory()
        # Renderer changed since the historical stage; mtrand.c did not.
        names = ['src/render_mirror.c', 'src/mtrand.c']
        later = set(git(ROOT, 'diff', '--name-only', '916b7aa8', '775b6b77', '--', 'src').decode().splitlines())
        self.assertIn(names[0], later)
        self.assertNotIn(names[1], later)
        for name in names:
            current = (ROOT/name).read_bytes()
            # The comparator pins PUBLIC, not today's renderer. Only the
            # existing exact, newest-first inverse supplies historical bytes.
            raw = projection.project_source('render-boundaries', name, current)
            self.assertEqual(raw, git(ROOT, 'show', PUBLIC+':'+name))
            pin = {name: inventory[name]}
            validate_production_map({name: (pin[name][0], raw)}, pin)
            for offset in (0, len(raw)//2, len(raw)-1):
                damaged = raw[:offset]+bytes([raw[offset]^1])+raw[offset+1:]
                with self.assertRaises(AssertionError):
                    validate_production_map({name: (pin[name][0], damaged)}, pin)
            with self.assertRaises(AssertionError):
                validate_production_map({name: ('100755', raw)}, pin)
            with self.assertRaises(AssertionError):
                validate_production_map({}, pin)
            with self.assertRaises(AssertionError):
                validate_production_map({name: (pin[name][0], raw), 'src/extra.c': ('100644', b'')}, pin)

    def test_unprojected_current_renderer_is_not_historical_input(self):
        name = 'src/render_mirror.c'
        raw = (ROOT/name).read_bytes()
        pin = {name: production_inventory()[name]}
        self.assertNotEqual(raw, git(ROOT, 'show', PUBLIC+':'+name))
        with self.assertRaisesRegex(AssertionError, 'Unapproved current production bytes/mode'):
            validate_production_map({name: (pin[name][0], raw)}, pin)

    def test_current_drift_rejected_by_projection_or_comparison(self):
        inventory = production_inventory()
        for name in ('src/render_mirror.c', 'src/mtrand.c'):
            raw = (ROOT/name).read_bytes()
            pin = {name: inventory[name]}
            for offset in (0, len(raw)//2, len(raw)-1):
                damaged = raw[:offset]+bytes([raw[offset]^1])+raw[offset+1:]
                with self.subTest(path=name, offset=offset), self.assertRaises(AssertionError):
                    old = projection.project_source('render-boundaries', name, damaged)
                    validate_production_map({name: (pin[name][0], old)}, pin)

    def test_partial_projection_cannot_be_reused_as_current_or_historical(self):
        name = 'src/render_mirror.c'
        raw = (ROOT/name).read_bytes()
        pin = {name: production_inventory()[name]}
        partial = projection.project_source('charge-body', name, raw)
        self.assertNotEqual(partial, raw)
        self.assertNotEqual(partial, git(ROOT, 'show', PUBLIC+':'+name))
        with self.assertRaises(AssertionError):
            projection.project_source('render-boundaries', name, partial)
        with self.assertRaises(AssertionError):
            validate_production_map({name: (pin[name][0], partial)}, pin)


if __name__ == '__main__':
    unittest.main()
