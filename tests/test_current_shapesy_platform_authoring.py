#!/usr/bin/env python3
"""Finite Y authoring semantics and deterministic resource reconstruction."""
import importlib.util
import io
import json
from pathlib import Path
import sys
import unittest
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import current_shapesy_platform_compatibility as c

class ShapesYAuthoring(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=c.read(ROOT,c.SELECTION)
        cls.selected,cls.pngs,cls.blobs,cls.rows=c.generate(ROOT,cls.raw)

    def test_exact_source_family_and_reproducibility(self):
        self.assertEqual(len(c.IDS),28)
        self.assertFalse(set(c.IDS)&set(range(1,29)))
        self.assertNotIn(356,c.IDS)
        second=c.generate(ROOT,self.raw)
        self.assertEqual((self.pngs,self.blobs,self.rows),second[1:])
        self.assertEqual(len(c.load(ROOT)),28)
        self.assertEqual(sum(1 for i in c.IDS for v in Image.open(io.BytesIO(self.pngs[c.png(i)])).getchannel('A').resize((24,28),Image.Resampling.NEAREST).tobytes() if v==0),5261)

    def image(self,i):return Image.open(io.BytesIO(self.pngs[c.png(i)])).copy()

    def test_protected_water_and_alpha_rejects(self):
        for i in c.IDS:
            im=self.image(i);c.check_pixels(i,im)
            with self.subTest(i=i,case='density'):
                with self.assertRaises(ValueError):c.check_pixels(i,im.resize((96,112)))
            with self.subTest(i=i,case='RGB'):
                with self.assertRaises(ValueError):c.check_pixels(i,im.convert('RGB'))
            im.putpixel((0,0),(1,2,3,127))
            with self.subTest(i=i,case='partialalpha'):
                with self.assertRaises(ValueError):c.check_pixels(i,im)
        im=self.image(375)
        p=next((x,y) for y in range(224) for x in range(192) if im.getpixel((x,y))[3]==0)
        im.putpixel(p,(2,0,0,0))
        with self.assertRaises(ValueError):c.check_pixels(375,im)
        im=self.image(375);im.putpixel(p,(0,0,0,255))
        with self.assertRaises(ValueError):c.check_pixels(375,im)

    def test_zero333_semantics(self):
        im=self.image(333)
        for y in range(72,80):
            for x in range(72,80):self.assertEqual(im.getpixel((x,y)),(0,0,0,255))
        for value in ((0,0,0,0),(1,0,0,255)):
            bad=im.copy();bad.putpixel((72,72),value)
            with self.assertRaises(ValueError):c.check_pixels(333,bad)

    def test_selection_tamper(self):
        for mutator in (lambda d:d.update(schema='wrong'),lambda d:d['inputs'].pop(next(iter(d['inputs']))),lambda d:d['inputs'].update({'outside.png':'0'*64})):
            data=json.loads(self.raw);mutator(data)
            with self.assertRaises((ValueError,AssertionError)):
                c.generate(ROOT,json.dumps(data).encode())

    def test_role_anchor_and_dimensions(self):
        import struct
        for i,raw in self.blobs.items():
            self.assertEqual(struct.unpack('<4s6I',raw[:28]),(b'HDR1',2020000+i,8,24,28,0,0))
            self.assertEqual(len(raw),172060)

if __name__=='__main__':unittest.main()
