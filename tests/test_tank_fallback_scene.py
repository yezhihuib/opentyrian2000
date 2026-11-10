"""Synthetic tank comparator tests, not native gameplay evidence."""
import csv
import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest
from PIL import Image

spec=importlib.util.spec_from_file_location('tank_scene',Path(__file__).with_name('check_tank_fallback_scene.py'))
scene=importlib.util.module_from_spec(spec)
spec.loader.exec_module(scene)


class TankFallbackSceneTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.out=Path(self.temp.name)
        self.ticks,self.scale=240,2
        self.states,self.frames,self.slots={},{},{}
        masks=[]
        for mode in ('on','off'):
            (self.out/mode).mkdir()
            self.states[mode],self.frames[mode],self.slots[mode]=[],[],[]
            count=0
            for tick in range(self.ticks):
                active=tick in (100,140)
                count+=active and mode=='on'
                state=dict.fromkeys(scene.STATE_FIELDS,'0')
                state.update(tick=str(tick),family_presents=str(tick+1),terrain_presents='0',
                             player_presents='0',tank_presents=str(count),presents=str(tick+1))
                self.states[mode].append(state)
                legacy=3 if tick>=100 and not active else 0
                self.frames[mode].append(dict(tick=str(tick),family=str(int(not active)),terrain=str(int(active)),
                    player_legacy='0',player_local='0',legacy_mask=str(legacy),
                    local_mask=str(3 if active and mode=='on' else 0),eligible_mask=str(3 if tick>=100 and mode=='on' else 0),
                    local_cells=str(2 if active and mode=='on' else 0),inside_pixels=str(8 if active else 0),
                    candidate_mismatches='0',outside_hash='same',inside_hash='changed' if active and mode=='on' else 'original',
                    local_presents=str(count-int(active and mode=='on'))))
                for slot in range(25):
                    eligible=mode=='on' and tick>=100 and slot<2
                    self.slots[mode].append(dict(tick=str(tick),slot=str(slot+75),epoch='1' if eligible else '0',
                        token=str(slot+10) if eligible else '0',generation='1' if eligible else '0',eligible=str(int(eligible)),
                        legacy=str((legacy>>slot)&1),local=str(int(active and mode=='on' and slot<2)),pose=str(slot%8),
                        x=str(100+slot*10) if eligible else '0',y='100' if eligible else '0',cells='1' if eligible else '0',
                        reason='0',denied='0',callbacks='160'))
                if mode=='on':
                    owners=bytearray(64000)
                    if active:
                        owners[100*320+100]=1
                        owners[100*320+110]=2
                    masks.append(struct.pack('=IIII',tick,3 if active else 0,2 if active else 0,64000)+owners)
            for tick in scene.CAPTURE_TICKS:
                if tick>=self.ticks:
                    continue
                image=Image.new('RGB',(640,400))
                if mode=='on' and tick in (100,140):
                    image.putpixel(((100-24)*2,200),(255,0,0))
                    image.putpixel(((110-24)*2,200),(255,0,0))
                image.save(self.out/mode/f'frame-{tick:04d}.ppm')
        (self.out/'on/ownership.bin').write_bytes(b''.join(masks))
        self.write_rows()

    def write_rows(self):
        for name,mapping in (('state.csv',self.states),('tank-present.csv',self.frames),('tank-slots.csv',self.slots)):
            for mode,rows in mapping.items():
                with (self.out/mode/name).open('w',newline='') as stream:
                    writer=csv.DictWriter(stream,fieldnames=rows[0].keys())
                    writer.writeheader();writer.writerows(rows)

    def compare(self):
        return scene.compare(self.out,self.ticks,self.scale)

    def test_two_slot_qualified_comparison(self):
        report=self.compare()
        self.assertEqual(report['independent_tank_frames'],2)
        self.assertEqual(report['independent_tank_draws'],4)
        self.assertEqual(report['qualified_tank_switches'],{'on':0,'off':6})

    def test_native_change_rejected(self):
        self.states['on'][140]['rng']='changed';self.write_rows()
        with self.assertRaisesRegex(AssertionError,'Native state'):
            self.compare()

    def test_player_admission_change_rejected(self):
        self.frames['on'][140]['player_local']='1';self.write_rows()
        with self.assertRaisesRegex(AssertionError,'Existing admission'):
            self.compare()

    def test_outside_pixel_change_rejected(self):
        self.frames['on'][140]['outside_hash']='changed';self.write_rows()
        with self.assertRaisesRegex(AssertionError,'outside tank cells'):
            self.compare()

    def test_candidate_mismatch_rejected(self):
        self.frames['on'][140]['candidate_mismatches']='1';self.write_rows()
        with self.assertRaisesRegex(AssertionError,'Invalid independent tank'):
            self.compare()

    def test_same_lifetime_required_for_switch_count(self):
        for tick in range(101,self.ticks):
            self.slots['on'][tick*25]['generation']='2'
        self.write_rows()
        report=self.compare()
        self.assertEqual(report['qualified_tank_switches']['off'],5)

    def test_missing_capture_rejected(self):
        for mode in ('on','off'):
            (self.out/mode/'frame-0100.ppm').unlink()
        with self.assertRaisesRegex(AssertionError,'scheduled window capture'):
            self.compare()

    def test_unowned_hole_rejected(self):
        path=self.out/'on/frame-0100.ppm'
        with Image.open(path) as image:
            image.putpixel(((101-24)*2,200),(255,0,0));image.save(path)
        with self.assertRaisesRegex(AssertionError,'outside exact tank ownership'):
            self.compare()


if __name__=='__main__':
    unittest.main()
