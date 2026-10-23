"""Content-cache negatives without weakening any authoring/path checks."""
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_current_art as b


def reference(data):
    value = 14695981039346656037
    for byte in data:
        value = ((value ^ byte) * 1099511628211) & ((1 << 64) - 1)
    return f'{value:016x}'


def png(value, alpha=127):
    stream = io.BytesIO()
    Image.new('RGBA', (96, 112), (value, 17, 31, alpha)).save(stream, format='PNG', compress_level=0)
    return stream.getvalue()


class ContentFNVCacheTests(unittest.TestCase):
    def setUp(self):
        b._fnv_bytes.cache_clear()
        self.input_pins = patch('current_sidekick_body_compatibility.authoring_input_fingerprints', return_value={})
        self.input_pins.start()
        self.addCleanup(self.input_pins.stop)

    def test_vectors_and_reuse_are_exact(self):
        for raw in (b'', b'a', b'foobar', bytes(range(256)), bytes([255]) * 172032):
            self.assertEqual(b.fnv(raw), reference(raw))
            self.assertEqual(b.fnv(bytes(bytearray(raw))), reference(raw))
        self.assertEqual(b._fnv_bytes.cache_info().hits, 5)

    def test_mutable_and_iterable_inputs_retain_their_behavior(self):
        raw = bytearray(b'ab')
        self.assertEqual(b.fnv(raw), reference(raw))
        raw[-1] = 255
        self.assertEqual(b.fnv(raw), reference(raw))
        self.assertEqual(b.fnv(iter([0, 256, -1])), reference([0, 256, -1]))
        self.assertEqual(b._fnv_bytes.cache_info().currsize, 0)

    def test_cache_is_bounded_and_eviction_recomputes(self):
        for index in range(129):
            raw = index.to_bytes(2, 'little')
            self.assertEqual(b.fnv(raw), reference(raw))
        info = b._fnv_bytes.cache_info()
        self.assertEqual(info.currsize, 128)
        self.assertEqual(b.fnv(b'\0\0'), reference(b'\0\0'))
        self.assertEqual(b._fnv_bytes.cache_info().misses, info.misses + 1)

    def test_changed_bytes_with_same_size_and_mtime_are_observed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); source = root / 'source.png'; source.write_bytes(png(23))
            row = dict(identity=80058, source_png='source.png', source_sha256=b.sha(source.read_bytes()))
            old_payload = b.source_blob(root, row)[1]
            old_hash = b.fnv(old_payload); old_stat = source.stat()
            changed = png(87)
            self.assertEqual(len(changed), old_stat.st_size)
            source.write_bytes(changed); os.utime(source, ns=(old_stat.st_atime_ns, old_stat.st_mtime_ns))
            new_payload = b.source_blob(root, row)[1]
            self.assertNotEqual(b.fnv(new_payload), old_hash)
            self.assertEqual(b.fnv(new_payload), reference(new_payload))
            selection = dict(schema='opentyrian-current-vulcan-authoring-v1', version='test', resources=[])
            for identity in b.profile('vulcan')['ids']:
                selection['resources'].append(dict(row, identity=identity))
            with self.assertRaisesRegex(ValueError, 'Selected source changed'):
                b.selection(root, b.encoded(selection), 'vulcan')

    def test_warm_cache_does_not_accept_changed_path_or_corruption(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); source = root / 'source.png'; source.write_bytes(png(23))
            row = dict(identity=80058, source_png='source.png')
            payload = b.source_blob(root, row)[1]; b.fnv(payload)
            other = root / 'other.png'; other.write_bytes(png(87))
            self.assertEqual(b.fnv(b.source_blob(root, dict(row, source_png='other.png'))[1]), reference(b.source_blob(root, dict(row, source_png='other.png'))[1]))
            for path in ('../outside.png', str(source.resolve())):
                with self.subTest(path=path), self.assertRaises(ValueError):
                    b.source_blob(root, dict(row, source_png=path))
            source.write_bytes(b'not a PNG')
            with self.assertRaises(Exception):
                b.source_blob(root, row)
            source.unlink()
            with self.assertRaises(ValueError):
                b.source_blob(root, row)

    def test_warm_cache_still_runs_file_and_parent_symlink_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); directory = root / 'input'; directory.mkdir()
            source = directory / 'source.png'; source.write_bytes(png(23))
            row = dict(identity=80058, source_png='input/source.png')
            b.fnv(b.source_blob(root, row)[1])
            for link in (source, directory):
                with self.subTest(link=link), patch.object(Path, 'is_symlink', lambda path: path == link):
                    with self.assertRaisesRegex(ValueError, 'Symlink source'):
                        b.source_blob(root, row)

    @unittest.skipIf(os.name == 'nt', 'Windows native symlink creation was denied with WinError 1314; no retry')
    def test_native_file_and_parent_symlinks_after_cache_warmup(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); directory = root / 'input'; directory.mkdir()
            source = directory / 'source.png'; source.write_bytes(png(23))
            row = dict(identity=80058, source_png='input/source.png')
            payload = b.source_blob(root, row)[1]; b.fnv(payload)
            outside = root / 'outside.png'; outside.write_bytes(source.read_bytes()); source.unlink()
            try:
                source.symlink_to(outside)
            except OSError as error:
                self.skipTest('Native symlink creation unavailable: ' + str(error))
            with self.assertRaises(ValueError): b.source_blob(root, row)
            source.unlink(); directory.rmdir()
            target = root / 'real'; target.mkdir(); (target / 'source.png').write_bytes(png(23))
            directory.symlink_to(target, target_is_directory=True)
            with self.assertRaises(ValueError): b.source_blob(root, row)

    def test_warm_cache_does_not_bypass_stale_plan_preflight(self):
        # Exercise the real apply preflight independently of expensive derive.
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp); root = base / 'repo'; root.mkdir(); stage = base / 'stage'
            stage.mkdir(); selected = b.profile('pulse')['selection']; raw = b'{}'
            (stage / 'files' / selected).parent.mkdir(parents=True)
            (stage / 'files' / selected).write_bytes(raw)
            target = root / 'consumer'; target.write_bytes(b'old'); outputs = {'consumer': b'new'}
            plan = b.make_plan(root, outputs, raw); (stage / 'plan.json').write_bytes(b.encoded(plan))
            b.fnv(b'old'); b.fnv(b'new'); target.write_bytes(b'changed')
            with patch.object(b, 'derive', return_value=outputs):
                with self.assertRaisesRegex(ValueError, 'Stale or modified plan'):
                    b.apply(root, stage)
            self.assertEqual(target.read_bytes(), b'changed')
            self.assertFalse((root / 'consumer.pulse-tmp').exists())

    def test_transparent_phase_is_revalidated_after_cache_warmup(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); source = root / 'source.png'; source.write_bytes(png(23, alpha=0))
            row = dict(identity=1060268, source_png='source.png')
            b.fnv(b.source_blob(root, row)[1])
            source.write_bytes(png(23, alpha=1))
            with self.assertRaisesRegex(ValueError, 'must remain authored transparent'):
                b.source_blob(root, row)

    def test_warm_cache_does_not_bypass_staged_bytes_or_temp_preflight(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp); root = base / 'repo'; root.mkdir(); stage = base / 'stage'
            selected = b.profile('pulse')['selection']; raw = b'{}'
            (stage / 'files' / selected).parent.mkdir(parents=True)
            (stage / 'files' / selected).write_bytes(raw)
            target = root / 'consumer'; target.write_bytes(b'old'); outputs = {'consumer': b'new'}
            (stage / 'plan.json').write_bytes(b.encoded(b.make_plan(root, outputs, raw)))
            staged = stage / 'files/consumer'; staged.write_bytes(b'tampered')
            b.fnv(b'old'); b.fnv(b'new')
            with patch.object(b, 'derive', return_value=outputs):
                with self.assertRaisesRegex(ValueError, 'Modified staged bytes'):
                    b.apply(root, stage)
                staged.write_bytes(b'new'); (root / 'consumer.pulse-tmp').write_bytes(b'occupied')
                with self.assertRaisesRegex(ValueError, 'Unexpected temporary output'):
                    b.apply(root, stage)
            self.assertEqual(target.read_bytes(), b'old')
            self.assertEqual((root / 'consumer.pulse-tmp').read_bytes(), b'occupied')


if __name__ == '__main__':
    unittest.main()
