"""Bounded tests: copy only the 9-PNG source bundle, never game/runtime trees."""
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('newshf', ROOT/'scripts/check_newshf_phase_a.py')
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


class SourceContractTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.source = Path(self.tmp.name)/'source'
        shutil.copytree(check.DEFAULT, self.source)
        self.manifest = check.read_json(self.source/'manifest.json')

    def write(self):
        (self.source/'manifest.json').write_text(json.dumps(self.manifest))

    def reject(self):
        with self.assertRaises((ValueError, OSError, TypeError, KeyError)):
            check.check(self.source)

    def repin(self, index=0):
        item = self.manifest['art'][index]
        item['art_sha256'] = check.digest((self.source/item['file']).read_bytes())
        self.write()
        p = check.read_json(self.source/'provenance.json')
        for g in p['groups']:
            for pose in g['poses']:
                if pose['base'] == item['base']:
                    pose['selected_png_sha256'] = item['art_sha256']
        (self.source/'provenance.json').write_text(json.dumps(p))

    def test_frozen_report_and_read_only_determinism(self):
        before = {p.name: p.read_bytes() for p in self.source.iterdir()}
        report = check.check(self.source)
        self.assertEqual(report, check.check(self.source))
        self.assertEqual(report, check.read_json(self.source/'report.json'))
        self.assertFalse(report['original_bytes_verified'])
        self.assertFalse(report['runtime_accepted'])
        self.assertEqual(len(report['sources']), 9)
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.source.iterdir()})

    def test_missing_duplicate_and_extra_identity(self):
        original = copy.deepcopy(self.manifest)
        for variant in [original['art'][:-1], original['art']+[original['art'][0]],
                        [original['art'][0]]*9]:
            self.manifest['art'] = variant
            self.write(); self.reject()

    def test_immutable_identity(self):
        original = copy.deepcopy(self.manifest)
        for key, value in [('logical_bank', 11), ('logical_bank', 10.0), ('bank', 'newshj.shp'),
                           ('logical_size', [23,28]), ('logical_anchor', [5,7]),
                           ('density', 4), ('alpha', 'smooth'), ('bank_sha256', '0'*64)]:
            self.manifest = copy.deepcopy(original)
            self.manifest['identity'][key] = value
            self.write(); self.reject()
        for key in ('offset','sha256','bases','ani','animate','esize','size'):
            self.manifest = copy.deepcopy(original)
            self.manifest['identity']['records'][0][key] = None
            self.write(); self.reject()

    def test_paths_and_source_aliases(self):
        for filename in ['../escape.png', '/tmp/escape.png', 'sub/../x.png', self.manifest['art'][1]['file']]:
            self.manifest['art'][0]['file'] = filename
            self.write(); self.reject()
        self.manifest = check.read_json(check.DEFAULT/'manifest.json')
        self.manifest['art'][0]['source_id'] = 'spriteSheet10:125'
        self.write(); self.reject()

    def test_symlink(self):
        path = self.source/self.manifest['art'][0]['file']
        path.unlink(); path.symlink_to(check.DEFAULT/path.name)
        self.reject()

    def test_extra_and_nested_png(self):
        extra = self.source/'extra.png'; extra.write_bytes(b'x'); self.reject(); extra.unlink()
        extra = self.source/'extra.PNG'; extra.write_bytes(b'x'); self.reject(); extra.unlink()
        linked = self.source/'linked'; linked.symlink_to(check.DEFAULT, target_is_directory=True)
        self.reject(); linked.unlink()
        sub = self.source/'nested'; sub.mkdir()
        (sub/self.manifest['art'][0]['file']).write_bytes(b'x'); self.reject()

    def test_missing_hash_and_corrupt_png(self):
        path = self.source/self.manifest['art'][0]['file']
        path.unlink(); self.reject()
        path.write_bytes(b'not a png'); self.reject()
        self.repin(); self.reject()

    def test_geometry_alpha_and_mode(self):
        path = self.source/self.manifest['art'][0]['file']
        for im in [Image.new('RGBA', (191,224)), Image.new('RGB', (192,224)),
                   Image.new('RGBA',(192,224),(1,2,3,128)), Image.new('RGBA',(192,224))]:
            im.save(path); self.repin(); self.reject()
        with Image.open(check.DEFAULT/path.name) as im:
            im.putpixel((0,0),(10,0,0,0)); im.save(path)
        self.repin(); self.reject()

    def test_duplicate_pixels_even_with_different_png_encoding(self):
        src = self.source/self.manifest['art'][0]['file']
        dst = self.source/self.manifest['art'][1]['file']
        with Image.open(src) as im:
            im.save(dst, compress_level=0)
        self.repin(1); self.reject()

    def test_json_strictness(self):
        path = self.source/'manifest.json'
        for text in ['{"schema":1,"schema":1}', '{"schema":NaN}', 'not json', '[]']:
            path.write_text(text); self.reject()

    def test_art_revision_is_explicit_not_geometry_revision(self):
        path = self.source/self.manifest['art'][0]['file']
        with Image.open(path) as im:
            point = next((x,y) for y in range(im.height) for x in range(im.width) if im.getpixel((x,y))[3])
            r,g,b,a = im.getpixel(point); im.putpixel(point,((r+1)%256,g,b,a)); im.save(path)
        self.reject()  # stale digest
        self.repin()
        report = check.check(self.source)
        self.assertEqual(report['source_identity_sha256'], check.check()['source_identity_sha256'])
        self.assertNotEqual(report['manifest_sha256'], check.check()['manifest_sha256'])

    def test_provenance_drift_and_malformed(self):
        path = self.source/'provenance.json'
        original = check.read_json(path)
        for value in [None, [], {}, {'schema':1}]:
            path.write_text(json.dumps(value)); self.reject()
        p = copy.deepcopy(original); p['groups'][0]['poses'][0]['selected_png_sha256'] = '0'*64
        path.write_text(json.dumps(p)); self.reject()
        p = copy.deepcopy(original); p['groups'][0]['poses'][0]['resize'] = [0, 224]
        path.write_text(json.dumps(p)); self.reject()

    def test_optional_original_verification_rejects_wrong_bank(self):
        data = Path(self.tmp.name)/'data'; data.mkdir()
        (data/'newshf.shp').write_bytes(b'wrong')
        with self.assertRaisesRegex(ValueError, 'original bank pin'):
            check.check(self.source, data)


if __name__ == '__main__':
    unittest.main()
