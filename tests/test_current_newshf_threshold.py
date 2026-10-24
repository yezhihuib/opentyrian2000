"""Byte-exact differential oracle for binary NEWSHF163/167 alpha only.

The old scalar algorithm is retained here as an independent, deliberately slow
reference. No time-based pass threshold and no mutable-input cache are used.
"""
import io
import json
import tempfile
from pathlib import Path
import random
import sys
import unittest
from unittest.mock import patch
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import current_newshf_compatibility as c


def scalar_threshold(im):
    raw = bytearray(im.tobytes())
    for offset in range(0, len(raw), 4):
        if raw[offset+3] < 128:
            raw[offset:offset+4] = b'\0\0\0\0'
        else:
            raw[offset+3] = 255
    return Image.frombytes('RGBA', im.size, bytes(raw))


class AircraftThresholdTests(unittest.TestCase):
    def equal(self, im):
        before = im.tobytes()
        actual = c.threshold(im)
        expected = scalar_threshold(im)
        self.assertEqual(actual.mode, 'RGBA')
        self.assertEqual(actual.size, im.size)
        self.assertEqual(actual.tobytes(), expected.tobytes())
        self.assertEqual(im.tobytes(), before)
        self.assertIsNot(actual, im)
        return actual

    def test_every_alpha_with_rgb_edges_and_deterministic_samples(self):
        rng = random.Random(163167)
        colors = [(r,g,b) for r in (0,1,127,128,254,255)
                  for g in (0,1,127,128,254,255)
                  for b in (0,1,127,128,254,255)]
        colors += [tuple(rng.randrange(256) for _ in range(3)) for _ in range(256)]
        raw = bytes(v for alpha in range(256) for rgb in colors for v in (*rgb, alpha))
        actual = self.equal(Image.frombytes('RGBA', (len(colors),256), raw))
        for alpha in range(256):
            for col,rgb in enumerate(colors):
                self.assertEqual(actual.getpixel((col,alpha)),
                                 (*rgb,255) if alpha >= 128 else (0,0,0,0))

    def test_hidden_rgb_and_alpha_boundary_are_not_blended(self):
        pixels = [(255,17,253,a) for a in (0,1,126,127,128,129,254,255)]
        im = Image.new('RGBA',(len(pixels),1)); im.putdata(pixels)
        result = self.equal(im)
        self.assertEqual([result.getpixel((x,0)) for x in range(len(pixels))], [(0,0,0,0)]*4+[(255,17,253,255)]*4)

    def test_random_images_and_repeated_input_mutation_are_fresh(self):
        rng = random.Random(0xA1FA)
        for size in ((1,1),(1,17),(19,1),(17,31),(256,256)):
            im = Image.frombytes('RGBA',size,rng.randbytes(size[0]*size[1]*4))
            original = im.tobytes(); self.equal(im)
            im.putpixel((0,0),(11,22,33,127)); result = self.equal(im)
            self.assertEqual(result.getpixel((0,0)),(0,0,0,0))
            im.putpixel((0,0),(11,22,33,128)); result = self.equal(im)
            self.assertEqual(result.getpixel((0,0)),(11,22,33,255))
            im.frombytes(original); self.equal(im)

    def test_actual_master_pixels_and_png_encoding_equal(self):
        for selector in c.SELECTORS:
            with Image.open(ROOT/c.INPUT_ROOT/f'master-{selector}.png') as opened:
                im = opened.convert('RGBA')
            actual = self.equal(im); expected = scalar_threshold(im)
            a,b = io.BytesIO(),io.BytesIO()
            actual.save(a,format='PNG',optimize=False)
            expected.save(b,format='PNG',optimize=False)
            self.assertEqual(a.getvalue(),b.getvalue())

    def test_full_generation_and_nine_resource_mapping_equal(self):
        raw = c.read(ROOT,c.SELECTION,128*1024)
        actual = c.generate(ROOT,raw)
        actual_rows = c.load(ROOT)
        with patch.object(c,'threshold',side_effect=scalar_threshold):
            expected = c.generate(ROOT,raw)
            expected_rows = c.load(ROOT)
        self.assertEqual(actual,expected)
        self.assertEqual(actual_rows,expected_rows)
        self.assertEqual(c.payload_header(list(actual_rows.values())),
                         c.read(ROOT,c.HEADER))
        self.assertEqual(len(actual_rows),9)

    def test_real_candidate_edits_match_scalar_through_resize_and_encoding(self):
        selected = json.loads(c.read(ROOT,c.SELECTION,128*1024))
        selected['schema'] = c.CANDIDATE_SCHEMA
        selected.pop('resources')
        selected['version'] = 'threshold-differential-candidate'
        with tempfile.TemporaryDirectory(prefix='aircraft-alpha-edit-') as folder:
            root = Path(folder)
            for relative in [selected['recipe']['path']] + [r['source_png'] for r in selected['masters']]:
                path = root/relative
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_bytes(c.read(ROOT,relative))
            for row in selected['masters']:
                path = root/row['source_png']
                with Image.open(path) as opened:
                    im = opened.convert('RGBA')
                # Cross the hard alpha boundary inside all three physical
                # columns, so Lanczos interpolation and hidden RGB are tested.
                for x0 in (200,900,1600):
                    for y in range(320,336):
                        for x in range(x0,x0+16):
                            im.putpixel((x,y),(x%256,y%256,(x+y)%256,(x+y)%256))
                stream = io.BytesIO(); im.save(stream,format='PNG')
                path.write_bytes(stream.getvalue())
                row['source_sha256'] = c.sha(stream.getvalue())
            raw = json.dumps(selected).encode()
            actual = c.generate(root,raw,True)
            with patch.object(c,'threshold',side_effect=scalar_threshold):
                expected = c.generate(root,raw,True)
            self.assertEqual(actual,expected)
            original = c.generate(ROOT,c.read(ROOT,c.SELECTION,128*1024))[2]
            self.assertEqual({i for i in original if original[i] != actual[2][i]},set(c.EDIT_IDS))

    def test_168_soft_alpha_is_not_thresholded(self):
        calls = []
        original = c.threshold
        def record(im):
            calls.append(im.size)
            return original(im)
        with patch.object(c,'threshold',side_effect=record):
            rows = c.load(ROOT)
        self.assertEqual(calls[:2],[(2011,782),(2012,782)])
        self.assertEqual(len(calls),8)  # two masters and six resized pieces
        legacy = c.legacy.load(ROOT)
        for destination,row in rows.items():
            if row['record'] == 168:
                self.assertEqual(row,legacy[destination])
                raw = c.read(ROOT,row['source_path'])
                self.assertTrue(any(0 < a < 255 for a in raw[31::4]))


if __name__ == '__main__':
    unittest.main()
