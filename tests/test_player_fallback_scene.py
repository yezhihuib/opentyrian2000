"""Synthetic comparator boundary tests, not native gameplay evidence."""
import csv
import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest
from PIL import Image

spec = importlib.util.spec_from_file_location('player_fallback_scene',Path(__file__).with_name('check_player_fallback_scene.py'))
scene = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scene)


class PlayerFallbackSceneTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.out = Path(self.temp.name)
        self.ticks, self.scale = 240, 2
        self.states, self.frames = {}, {}
        records = []
        for mode in ('on','off'):
            (self.out/mode).mkdir()
            self.states[mode], self.frames[mode] = [], []
            local_count = 0
            for tick in range(self.ticks):
                active = tick in (100,140)
                local_count += active and mode == 'on'
                state = dict.fromkeys(scene.STATE_FIELDS,'0')
                state.update(tick=str(tick),x='105',y='107',inv=str(max(99-tick,0)),
                             family_presents=str(tick+1),terrain_presents='0',
                             local_presents=str(local_count),presents=str(tick+1))
                self.states[mode].append(state)
                row = dict(tick=str(tick),family=str(int(not active)),terrain=str(int(active)),
                           legacy_ship=str(int(tick>=100 and not active)),legacy_pose='233',
                           local=str(int(active and mode=='on')),local_pose='233',local_callbacks='266',
                           local_cells=str(int(active)),local_reason='0',inside_pixels=str(4*active),
                           candidate_mismatches='0',outside_hash='same',
                           inside_hash='changed' if active and mode=='on' else 'original',
                           local_presents=str(local_count-active*(mode=='on')))
                self.frames[mode].append(row)
                if mode == 'on':
                    records.append(struct.pack('=IiiI',tick,100 if active else 0,100 if active else 0,int(active))+
                                   (b'\x01'+b'\x00'*671 if active else b'\x00'*672))
            for tick in scene.CAPTURE_TICKS:
                if tick >= self.ticks:
                    continue
                image = Image.new('RGB',(640,400))
                if mode=='on' and tick in (100,140):
                    image.putpixel(((100-24)*2,100*2),(255,0,0))
                image.save(self.out/mode/f'frame-{tick:04d}.ppm')
        (self.out/'on/ownership.bin').write_bytes(b''.join(records))
        self.write_rows()

    def write_rows(self):
        for name, mapping in (('state.csv',self.states),('player-present.csv',self.frames)):
            for mode, rows in mapping.items():
                with (self.out/mode/name).open('w',newline='') as stream:
                    writer = csv.DictWriter(stream,fieldnames=rows[0].keys())
                    writer.writeheader()
                    writer.writerows(rows)

    def compare(self):
        return scene.compare(self.out,self.ticks,self.scale)

    def test_valid_owned_cell_comparison(self):
        report = self.compare()
        self.assertEqual(report['independent_ship_frames'],2)
        self.assertEqual(report['combined_ship_frames']-report['baseline_ship_frames'],2)
        self.assertEqual(report['candidate_pixel_mismatches'],0)

    def test_native_state_change_rejected(self):
        self.states['on'][140]['rng']='changed'
        self.write_rows()
        with self.assertRaisesRegex(AssertionError,'Native state'):
            self.compare()

    def test_foreign_pixels_rejected(self):
        self.frames['on'][140]['outside_hash']='changed'
        self.write_rows()
        with self.assertRaisesRegex(AssertionError,'outside owned cells'):
            self.compare()

    def test_candidate_pixel_mismatch_rejected(self):
        self.frames['on'][140]['candidate_mismatches']='1'
        self.write_rows()
        with self.assertRaisesRegex(AssertionError,'Invalid independent player'):
            self.compare()

    def test_missing_both_captures_rejected(self):
        for mode in ('on','off'):
            (self.out/mode/'frame-0100.ppm').unlink()
        with self.assertRaisesRegex(AssertionError,'scheduled window capture'):
            self.compare()

    def test_unowned_hole_difference_rejected(self):
        path = self.out/'on/frame-0100.ppm'
        with Image.open(path) as image:
            image.putpixel(((100-24+1)*2,100*2),(255,0,0))
            image.save(path)
        with self.assertRaisesRegex(AssertionError,'outside exact native ownership'):
            self.compare()

    def test_malformed_ownership_rejected(self):
        path=self.out/'on/ownership.bin'
        data=bytearray(path.read_bytes())
        data[100*scene.MASK_RECORD_BYTES+16]=2
        path.write_bytes(data)
        with self.assertRaisesRegex(AssertionError,'Invalid ownership evidence'):
            self.compare()


if __name__ == '__main__':
    unittest.main()
