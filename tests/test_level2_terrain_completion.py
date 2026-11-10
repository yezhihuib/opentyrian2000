"""Synthetic resource regression tests; optional TYRIAN_DATA enables pinned replay."""
import json
import os
from pathlib import Path
import struct
import sys
import tempfile
import unittest
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_level2_terrain_completion as build
import audit_level2_terrain_completion as audit


class GeometryTests(unittest.TestCase):
    def test_empty_ragged_duplicate_and_invalid_ids(self):
        for rows in [(), ((),), ((1,), (2, 3)), ((1, 1),), ((0,),), ((601,),), ((True,),)]:
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                build.crop_group(Image.new('RGB', (384, 224)), rows)

    def test_crop_uses_one_shared_canvas(self):
        rgb = np.arange(448*384*3, dtype=np.uint8).reshape(448,384,3)
        parts = build.crop_group(Image.fromarray(rgb), ((2,3),(4,5)))
        joined = np.concatenate([np.concatenate([parts[2],parts[3]],axis=1),
                                 np.concatenate([parts[4],parts[5]],axis=1)],axis=0)
        np.testing.assert_array_equal(rgb, joined)

    def test_exact_binary_coverage_and_hidden_rgb_zero(self):
        source = bytes([0,1,255,0]*168)
        rgb = np.full((224,192,3), 177, dtype=np.uint8)
        rgba = build.apply_coverage(rgb,source)
        mask=np.repeat(np.repeat(np.frombuffer(source,dtype=np.uint8).reshape(28,24)!=0,8,0),8,1)
        np.testing.assert_array_equal(rgba[:,:,3],mask*255)
        self.assertFalse(np.any(rgba[~mask,:3]))
        self.assertTrue(np.all(rgba[mask,:3]==177))
        payload=build.hda(299,rgba)
        self.assertEqual(len(payload),172060)
        self.assertEqual(struct.unpack('<4s4I2i',payload[:28]),(b'HDR1',2010299,8,24,28,0,0))
        self.assertEqual(payload[28:],rgba.tobytes())

    def test_wrong_pixel_geometry_and_dtype(self):
        for rgb,source in [(np.zeros((28,24,3),dtype=np.uint8),bytes(672)),
                           (np.zeros((224,192,3)),bytes(672)),
                           (np.zeros((224,192,3),dtype=np.uint8),bytes(671))]:
            with self.assertRaises(ValueError): build.apply_coverage(rgb,source)
        for rgba in [np.zeros((224,192,4)),np.zeros((28,24,4),dtype=np.uint8)]:
            with self.assertRaises(ValueError): build.hda(299,rgba)

    def test_malformed_native_layout(self):
        for raw in [b'',b'\2',b'\0'+bytes(671),bytes([1])*600,bytes(318976)]:
            with self.subTest(size=len(raw)),self.assertRaises(ValueError): build.decode_shapes(raw)

    def test_join_orientation_and_invalid_direction(self):
        a=np.arange(24).reshape(2,3,4);b=a+100
        np.testing.assert_array_equal(a[:,-1],audit.edges(a,b,'R')[0])
        np.testing.assert_array_equal(b[0,:],audit.edges(a,b,'D')[1])
        with self.assertRaises(ValueError):audit.edges(a,b,'unknown')


class InputTests(unittest.TestCase):
    def test_identity_size_and_symlink_rejection(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'input';p.write_bytes(b'hello');pin=build.sha(b'hello')
            self.assertEqual(build.checked(p,pin,5),b'hello')
            for actual,size in [('bad',5),(pin,4)]:
                with self.assertRaises(ValueError):build.checked(p,actual,size)
            link=Path(td)/'link';link.symlink_to(p)
            with self.assertRaises(ValueError):build.checked(link,pin)
            with self.assertRaises(ValueError):build.checked(Path(td),pin)

    def test_existing_and_overlapping_output_preserved(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);existing=root/'existing';existing.mkdir()
            sentinel=existing/'keep';sentinel.write_text('safe')
            with self.assertRaises(ValueError):build.build(root,existing)
            self.assertEqual(sentinel.read_text(),'safe')
            with self.assertRaisesRegex(ValueError,'overlaps'):build.build(root,root/'new')
            self.assertFalse((root/'new').exists())

    def test_bad_input_creates_no_output(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);data=root/'data';data.mkdir();(data/'shapesz.dat').write_bytes(bytes(318976))
            with self.assertRaises(ValueError):build.build(data,root/'new')
            self.assertFalse((root/'new').exists())

    def test_candidate_missing_manifest_members_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            (Path(td)/'MANIFEST.json').write_text(json.dumps({'ids':list(build.IDS),'tiles':[]}))
            with self.assertRaisesRegex(ValueError,'manifest'):audit.validate_candidate(td,{})


@unittest.skipUnless(os.environ.get('TYRIAN_DATA'),'TYRIAN_DATA not set; pinned original replay not run')
class PinnedReplayTests(unittest.TestCase):
    def test_two_builds_reproduce_committed_resources_and_audit(self):
        data=Path(os.environ['TYRIAN_DATA'])
        with tempfile.TemporaryDirectory() as td:
            first=Path(td)/'first';second=Path(td)/'second'
            build.build(data,first);build.build(data,second)
            for path in first.iterdir():
                self.assertEqual(path.read_bytes(),(second/path.name).read_bytes(),path.name)
                self.assertEqual(path.read_bytes(),(audit.PACK/path.name).read_bytes(),path.name)
            report=audit.audit(data,first)
            self.assertEqual(report['validated_candidate_resources'],38)
            self.assertTrue(report['all_nonblank_resources_found'])
            self.assertEqual(report['distinct_audited_directed_joins'],361)
            self.assertEqual(report['audited_join_occurrences'],3447)
            self.assertTrue(all(e['all_member_occurrences_in_complete_assembly'] for e in report['assembly_evidence']))
            self.assertFalse(report['visual_scene_review_complete'])
            self.assertEqual(json.loads(json.dumps(report)),json.loads((audit.PACK/'NEIGHBOR-AUDIT.json').read_text()))
            manifest_path=first/'MANIFEST.json'
            manifest=json.loads(manifest_path.read_text())
            original_manifest=manifest_path.read_bytes()
            hda=first/'terrain-shapesz-299-8.hda';raw=bytearray(hda.read_bytes());raw[-1]^=255;hda.write_bytes(raw)
            with self.assertRaisesRegex(ValueError,'identity mismatch'):audit.audit(data,first)
            # Even refreshing the outer hash cannot hide wrong alpha geometry.
            entry=next(e for e in manifest['tiles'] if e['id']==299)
            entry['hda_sha256']=build.sha(raw)
            manifest_path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError,'coverage'):audit.audit(data,first)
            # A valid hash also cannot hide a malformed HDA identity header.
            raw=bytearray((second/hda.name).read_bytes());raw[4]^=1;hda.write_bytes(raw)
            entry['hda_sha256']=build.sha(raw);manifest_path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError,'Malformed HDA'):audit.audit(data,first)
            hda.write_bytes((second/hda.name).read_bytes());manifest_path.write_bytes(original_manifest)
            png=first/'terrain-shapesz-299-8.png';png.write_bytes(b'bad png')
            with self.assertRaisesRegex(ValueError,'identity mismatch'):audit.audit(data,first)


if __name__=='__main__':unittest.main()
