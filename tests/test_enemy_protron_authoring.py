#!/usr/bin/env python3
"""Independent finite identity/recipe mutation checks; no renderer acceptance claim."""
import io
import json
from pathlib import Path
import struct
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import build_enemy_protron_p09 as b
import portable_history_baselines as history
from PIL import Image

class ProtronAuthoring(unittest.TestCase):
    def test_reproduction_and_private_identity(self):
        outputs=b.derive()
        self.assertEqual(set(outputs),{b.DIRECTORY+'/source227.png',b.DIRECTORY+'/enemy-protron-p09-227-8.hda',b.HEADER})
        for p,raw in outputs.items(): self.assertEqual(b.read(b.ROOT,p),raw)
        hda=outputs[b.DIRECTORY+'/enemy-protron-p09-227-8.hda']
        self.assertEqual(struct.unpack('<4s6I',hda[:28]),(b'HDR1',1470227,8,12,14,0,0))
        self.assertEqual(b.sha(hda),'9de332ec5d8d7f5c0e7eb56445aabebe22897b27a6fde1ee7f36da822076aac7')
        self.assertEqual(hda[28:],Image.open(io.BytesIO(outputs[b.DIRECTORY+'/source227.png'])).tobytes())
        self.assertNotEqual(struct.unpack_from('<I',hda,4)[0],80227)
    def test_mutated_recipe_rejected(self):
        for key,value in [('source_crop_xyxy',[1498,234,1839,569]),('composite_xy',[15,24]),('canvas_px',[96,96]),('alpha_operation','clip mask'),('png_sha256','0'*64),('unknown','unsafe')]:
            with self.subTest(key=key):
                recipe=dict(b.RECIPE);recipe[key]=value;old=b.read
                with patch.object(b,'read',side_effect=lambda r,p:json.dumps(recipe).encode() if p==b.DIRECTORY+'/recipe.json' else old(r,p)):
                    with self.assertRaisesRegex(ValueError,'recipe'): b.derive()
    def test_mutated_identity_rejected(self):
        for key,value in [('material_role',8),('material_identity',80227),('frame',226),('eligible_profiles',[[3,1,134,1,135]]),('source_indexed_sha256','0'*64),('player_eligibility',True)]:
            with self.subTest(key=key):
                identity=dict(b.IDENTITY);identity[key]=value;old=b.read
                with patch.object(b,'read',side_effect=lambda r,p:json.dumps(identity).encode() if p==b.DIRECTORY+'/identity.json' else old(r,p)):
                    with self.assertRaisesRegex(ValueError,'identity'): b.derive()
    def test_bad_master_rejected(self):
        old=b.read
        with patch.object(b,'read',side_effect=lambda r,p:b'bad-master' if p==b.MASTER else old(r,p)):
            with self.assertRaisesRegex(ValueError,'master'): b.derive()
    def test_old_art_byte_unchanged(self):
        import subprocess
        catalog=json.loads(b.read(b.ROOT,'assets/hd/manifest.json'))
        for frame in (225,226,244):
            name=f'bullet-{frame}-8.hda'
            for pack,entries in catalog['packs'].items():
                p='assets/hd/packs/'+pack+'/'+name
                for p in (p,entries['files'][name]['source_png']):
                    original=history.preimage('4810555b37ab12247690f383160e6bff433f41c6', p, b.ROOT)
                    self.assertEqual(b.read(b.ROOT,p),original,p)
        self.assertEqual(b.sha(b.read(b.ROOT,b.MASTER)),b.MASTER_SHA)
if __name__=='__main__':unittest.main()
