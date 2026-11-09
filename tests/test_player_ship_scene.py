"""Synthetic receipt tests for the scene checker, not gameplay evidence.

No original game data, screenshots or engine executable is needed. Tiny colored
marks model permitted image differences solely to test comparator boundaries.
"""
import csv
import importlib.util
from pathlib import Path
import tempfile
import unittest

try:
    from PIL import Image
except ImportError:
    Image = None

spec = importlib.util.spec_from_file_location('ship_scene_checker', Path(__file__).with_name('check_player_ship_scene.py'))
scene = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scene)


@unittest.skipIf(Image is None, 'requires Pillow')
class SceneComparisonTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.out = Path(self.temporary.name)
        self.scale = 2
        self.ticks = 240
        self.fields = ['tick', *scene.STATE_FIELDS, 'ship_accepted', 'ship_style', 'ship_pose']
        self.rows = {}
        for mode in ('on', 'off'):
            (self.out/mode).mkdir()
            self.rows[mode] = []
            for tick in range(self.ticks):
                row = {field: '0' for field in self.fields}
                row.update(tick=str(tick), x='100', y='100', inv=str(max(99-tick, 0)),
                           ship_accepted='1', ship_style='1' if tick < 100 else '0',
                           ship_pose=str((229, 231, 233, 235, 237)[tick % 5]))
                self.rows[mode].append(row)
        self.write_rows()
        self.write_images()

    def write_rows(self):
        for mode, rows in self.rows.items():
            with (self.out/mode/'state.csv').open('w', newline='') as stream:
                writer = csv.DictWriter(stream, fieldnames=self.fields)
                writer.writeheader()
                writer.writerows(rows)

    def frame(self, mode, tick):
        return self.out/mode/f'frame-{tick:04d}-{tick:04d}.ppm'

    def write_images(self):
        for mode in ('on', 'off'):
            for tick in scene.CAPTURE_TICKS:
                if tick >= self.ticks:
                    continue
                image = Image.new('RGB', (320*self.scale, 200*self.scale))
                if mode == 'on' and tick in (20, 40, 90, 99):
                    # Exact native ship anchor and output crop, no extra offsets.
                    image.putpixel(((100-5-24)*self.scale, (100-7)*self.scale), (255, 0, 0))
                image.save(self.frame(mode, tick))

    def compare(self):
        return scene.compare(self.out, self.ticks, self.scale)

    def test_correct_synthetic_receipt_passes_at_both_scales(self):
        for scale in (2, 4):
            with self.subTest(scale=scale):
                self.scale = scale
                self.write_images()
                report = self.compare()
                self.assertEqual(report['native_state_comparisons'], 3120)
                self.assertEqual(report['translucent_poses'], [229, 231, 233, 235, 237])
                self.assertEqual(len(report['captures']), 10)
                self.assertEqual([r['tick'] for r in report['captures'] if r['difference_bounds']], [20, 40, 90, 99])

    def test_missing_capture_in_both_modes_is_not_a_pass(self):
        for mode in ('on', 'off'):
            self.frame(mode, 20).unlink()
        with self.assertRaisesRegex(AssertionError, 'scheduled Present capture'):
            self.compare()

    def test_only_identical_tick_one_capture_is_not_a_pass(self):
        for mode in ('on', 'off'):
            for image in (self.out/mode).glob('frame-*.ppm'):
                if image != self.frame(mode, 1):
                    image.unlink()
        with self.assertRaisesRegex(AssertionError, 'scheduled Present capture'):
            self.compare()

    def test_duplicate_scheduled_tick_is_rejected(self):
        for mode in ('on', 'off'):
            (self.out/mode/'frame-0020-9999.ppm').write_bytes(self.frame(mode, 20).read_bytes())
        with self.assertRaisesRegex(AssertionError, 'scheduled Present capture'):
            self.compare()

    def test_constant_invulnerability_does_not_prove_transition(self):
        for rows in self.rows.values():
            for row in rows:
                row['inv'] = '50'
        self.write_rows()
        with self.assertRaisesRegex(AssertionError, '1-to-0'):
            self.compare()

    def test_blended_frame_after_transition_is_rejected(self):
        self.rows['on'][100]['ship_style'] = '1'
        self.write_rows()
        with self.assertRaisesRegex(AssertionError, 'opaque ship'):
            self.compare()

    def test_native_state_difference_is_rejected(self):
        self.rows['on'][37]['shots'] = 'changed'
        self.write_rows()
        with self.assertRaisesRegex(AssertionError, 'Native state changed at 37: shots'):
            self.compare()

    def test_each_outside_envelope_edge_is_rejected(self):
        left, top = (100-5-24)*self.scale, (100-7)*self.scale
        right, bottom = left+24*self.scale, top+28*self.scale
        original = self.frame('on', 20).read_bytes()
        for point in ((left-1, top), (right, top), (left, top-1), (left, bottom)):
            with self.subTest(point=point):
                self.frame('on', 20).write_bytes(original)
                with Image.open(self.frame('on', 20)) as image:
                    image.putpixel(point, (255, 255, 255))
                    image.save(self.frame('on', 20))
                with self.assertRaisesRegex(AssertionError, 'outside the translucent ship'):
                    self.compare()

    def test_inside_bottom_right_edge_is_accepted(self):
        with Image.open(self.frame('on', 20)) as image:
            image.putpixel(((100-5-24+24)*self.scale-1, (100-7+28)*self.scale-1), (255, 255, 255))
            image.save(self.frame('on', 20))
        self.compare()

    def test_required_visible_difference_is_not_optional(self):
        self.frame('on', 20).write_bytes(self.frame('off', 20).read_bytes())
        with self.assertRaisesRegex(AssertionError, 'visible translucent ship improvement'):
            self.compare()


class SceneInstrumentationTests(unittest.TestCase):
    def sources(self):
        return {
            'opentyr.c': '#ifdef NDEBUG\n\tif (!isNetworkGame && !game_probe_enabled)',
            'mainint.c': '\t\t\t\t/* keyboard input */',
            'tyrian2.c': '\tb313_facts_snapshot("tick_end",0);',
            'game_probe.c': '/* synthetic source stand-in */\n',
        }

    def test_instrumentation_does_not_mutate_input_mapping(self):
        sources = self.sources()
        before = dict(sources)
        result = scene.instrument(sources)
        self.assertEqual(sources, before)
        self.assertIn('original_test_input();', result['mainint.c'])
        self.assertIn('original_test_end()', result['tyrian2.c'])
        self.assertIn('void original_test_state(FILE *f)', result['game_probe.c'])

    def test_missing_or_duplicate_hooks_are_refused(self):
        for filename in ('opentyr.c', 'mainint.c', 'tyrian2.c'):
            for count in (0, 2):
                with self.subTest(filename=filename, copies=count):
                    sources = self.sources()
                    sources[filename] *= count
                    with self.assertRaisesRegex(ValueError, 'Source hook changed: ' + filename):
                        scene.instrument(sources)


if __name__ == '__main__':
    unittest.main()
