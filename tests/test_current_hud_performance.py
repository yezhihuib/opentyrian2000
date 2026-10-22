"""Checked-input invalidation for bounded pure HUD material reuse."""
import copy
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import current_hud_recipe as hud


class HUDMeterCacheTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.names = [hud.DEFAULT_SELECTION['meters'][0]['path']] + [hud.FIXED_INPUTS[key]['path'] for key in ('meter_recipe', 'meter_baseline')]
        cls.initial = {name: (ROOT / name).read_bytes() for name in cls.names}
        cls.data = cls.initial[cls.names[0]]
        hud._meter_sections.cache_clear()
        cls.sections = hud.meter_payload(ROOT, cls.data)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name, raw in self.initial.items():
            path = self.root / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw)

    def test_cached_sections_match_pinned_baseline_and_are_not_mutable_aliases(self):
        self.assertEqual(b''.join(self.sections), self.initial[self.names[2]][112:])
        sections = hud.meter_payload(self.root, self.data); sections[0] = b'bad'
        self.assertEqual(hud.meter_payload(self.root, self.data), self.sections)
        self.assertEqual(hud._meter_sections.cache_info().maxsize, 4)

    def test_every_warm_call_rechecks_recipe_and_baseline(self):
        with patch.object(hud, 'checked', wraps=hud.checked) as checked:
            for _ in range(2): self.assertEqual(hud.meter_payload(self.root, self.data), self.sections)
        self.assertEqual([call.args[1] for call in checked.call_args_list],
                         [hud.FIXED_INPUTS[key] for _ in range(2) for key in ('meter_recipe', 'meter_baseline')])

    def test_corrupt_fixed_inputs_with_same_size_and_mtime_are_rejected(self):
        for name in self.names[1:]:
            path = self.root / name; raw = path.read_bytes(); old = path.stat()
            changed = bytearray(raw); changed[-1] ^= 1; path.write_bytes(changed)
            os.utime(path, ns=(old.st_atime_ns, old.st_mtime_ns))
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'Source hash mismatch'):
                hud.meter_payload(self.root, self.data)
            path.write_bytes(raw)
        self.assertEqual(hud.meter_payload(self.root, self.data), self.sections)

    def test_new_rgb_values_invalidate_only_the_material_result(self):
        colors = json.loads(self.data); colors['firepower']['116'] = [135, 4, 0]
        before = hud._meter_sections.cache_info().misses
        sections = hud.meter_payload(self.root, json.dumps(colors).encode())
        self.assertEqual(hud._meter_sections.cache_info().misses, before + 1)
        self.assertNotEqual(sections[0], self.sections[0])
        self.assertEqual(sections[1:], self.sections[1:])
        self.assertEqual(hud.meter_payload(self.root, self.data), self.sections)

    def test_new_checked_recipe_bytes_invalidate_the_material_result(self):
        record = copy.deepcopy(hud.FIXED_INPUTS['meter_recipe'])
        path = self.root / record['path']; raw = path.read_bytes() + b'\n# bounded cache invalidation probe\n'
        path.write_bytes(raw)
        import hashlib
        record['sha256'] = hashlib.sha256(raw).hexdigest()
        before = hud._meter_sections.cache_info().misses
        with patch.dict(hud.FIXED_INPUTS, meter_recipe=record):
            self.assertEqual(hud.meter_payload(self.root, self.data), self.sections)
        self.assertEqual(hud._meter_sections.cache_info().misses, before + 1)

    def test_invalid_colors_are_rejected_after_warmup(self):
        for value in ([], [True, 4, 0], [256, 4, 0], [0, 0, 0]):
            colors = json.loads(self.data); colors['firepower']['116'] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                hud.meter_payload(self.root, json.dumps(colors).encode())

    def test_changed_selected_hash_and_unsafe_paths_are_rejected_after_warmup(self):
        record = copy.deepcopy(hud.DEFAULT_SELECTION['meters'][0]); path = self.root / record['path']
        path.write_bytes(self.data + b' ')
        with self.assertRaisesRegex(ValueError, 'Source hash mismatch'):
            hud.render_resource(self.root, 'meters', [record])
        for name in ('../outside.json', str(path.resolve())):
            record['path'] = name
            with self.subTest(name=name), self.assertRaises(ValueError):
                hud.render_resource(self.root, 'meters', [record])

    def test_warm_calls_reject_file_and_parent_symlink_checks(self):
        for name in self.names:
            target = self.root / name
            for link in (target, target.parent):
                with self.subTest(link=link), patch.object(Path, 'is_symlink', lambda path: path == link):
                    with self.assertRaises(ValueError):
                        hud.render_resource(self.root, 'meters', hud.DEFAULT_SELECTION['meters'])


if __name__ == '__main__': unittest.main()
