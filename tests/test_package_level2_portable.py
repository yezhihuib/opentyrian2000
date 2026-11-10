import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import stat
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('portable', ROOT / 'scripts/package_level2_portable.py')
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)


def pe(dll=False, imported='KERNEL32.dll'):
    raw = bytearray(1024)
    raw[:2] = b'MZ'
    struct.pack_into('<I', raw, 60, 64)
    raw[64:68] = b'PE\0\0'
    struct.pack_into('<HH', raw, 68, 0x8664, 1)
    struct.pack_into('<HH', raw, 84, 240, 2 | (0x2000 if dll else 0))
    struct.pack_into('<H', raw, 88, 0x20b)
    struct.pack_into('<I', raw, 88 + 108, 16)
    struct.pack_into('<II', raw, 88 + 120, 0x1000, 40)
    struct.pack_into('<III', raw, 328 + 12, 0x1000, 512, 512)
    struct.pack_into('<I', raw, 512 + 12, 0x1080)
    raw[640:640 + len(imported)] = imported.encode()
    return bytes(raw)


class PathsAndIdentity(unittest.TestCase):
    def test_relative_path_boundaries(self):
        for name in ('assets/a.hda', 'bin/SDL2.dll', "newsh'.shp", 'newsh#.shp'):
            self.assertEqual(p.relative_path(name), name)
        for name in ('', '.', '..', '../a', '/abs', 'a//b', 'a/./b', 'a/../b', 'a\\b',
                     'C:/a', 'NUL', 'com1.dll', 'x/AUX.hda', 'x ', 'x.', 'bad\n', '中文'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                p.relative_path(name)
        with self.assertRaises(ValueError):
            p.relative_path('dir/data.shp', flat=True)

    def test_casefold_and_directory_collision(self):
        for names in (['a', 'A'], ['a', 'a/b'], ['a/b', 'A'], ['x', '../x']):
            with self.assertRaises(ValueError):
                p.validate_names(names)
        p.validate_names(['a/b', 'a/c', 'other'])

    def test_plain_path_rejects_symlink_components(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'real').mkdir()
            (root / 'alias').symlink_to(root / 'real', target_is_directory=True)
            (root / 'dangling').symlink_to(root / 'absent')
            for name in ('alias/child', 'dangling', 'real/../child'):
                with self.assertRaises(ValueError):
                    p.plain_path(root / name)

    def test_read_file_boundaries_and_hash(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target = root / 'file'
            target.write_bytes(b'abc')
            self.assertEqual(p.checked_file(target, p.identity('file', b'abc')), b'abc')
            for row in ({'bytes': True, 'sha256': p.sha(b'abc')},
                        {'bytes': 3, 'sha256': '0' * 64}, {'bytes': 2, 'sha256': p.sha(b'abc')}):
                with self.assertRaises(ValueError):
                    p.checked_file(target, row)
            with self.assertRaises(ValueError):
                p.read_file(target, limit=2)
            with self.assertRaises(ValueError):
                p.read_file(root)

    def test_fresh_output_rejects_overlap_existing_and_missing_parent(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            repo = root / 'repo'
            repo.mkdir()
            p.fresh_output(root / 'out', root / 'out.zip', [repo])
            for out, arc in ((repo / 'out', root / 'x.zip'), (root, root / 'x.zip'),
                             (root / 'out', root / 'out/a.zip'), (root / 'same', root / 'same'),
                             (root / 'missing/out', root / 'x.zip'), (repo, root / 'x.zip')):
                with self.assertRaises(ValueError):
                    p.fresh_output(out, arc, [repo])

    def test_strict_json(self):
        for raw in (b'{"a":1,"a":2}', b'{"a":NaN}', b'{"a":Infinity}'):
            with self.assertRaises(ValueError):
                p.load_json(raw)


class PEValidation(unittest.TestCase):
    def test_x64_executable_and_dll(self):
        self.assertEqual(p.pe_image(pe(), dll=False), ['KERNEL32.dll'])
        self.assertEqual(p.pe_image(pe(True), dll=True), ['KERNEL32.dll'])

    def test_wrong_role_is_not_extension_based(self):
        for raw, dll in ((pe(), True), (pe(True), False)):
            with self.assertRaises(ValueError):
                p.pe_image(raw, dll=dll)

    def test_malformed_non_pe_and_wrong_arch(self):
        for raw in (b'\x7fELF' + bytes(1000), pe()[:60], pe()[:700]):
            with self.assertRaises(ValueError):
                p.pe_image(raw, dll=False)
        for offset, value in ((68, 0x14c), (88, 0x10b), (86, 0)):
            raw = bytearray(pe())
            struct.pack_into('<H', raw, offset, value)
            with self.assertRaises(ValueError):
                p.pe_image(bytes(raw), dll=False)

    def test_import_traversal_and_delay_import_rejected(self):
        with self.assertRaises(ValueError):
            p.pe_image(pe(imported='../bad.dll'), dll=False)
        raw = bytearray(pe())
        struct.pack_into('<I', raw, 88 + 112 + 13 * 8, 123)
        with self.assertRaises(ValueError):
            p.pe_image(bytes(raw), dll=False)


class PackagePolicy(unittest.TestCase):
    def test_readme_fresh_local_extraction_and_bootstrap_boundary(self):
        readme = (ROOT / 'packaging/level2-portable-README.txt').read_text()
        self.assertIn('新建的空文件夹', readme)
        self.assertIn('两者不能互相包含', readme)
        self.assertIn('不要覆盖或合并到已有目录', readme)
        self.assertIn('不要使用网络共享', readme)
        self.assertIn('在启动器开始核验前加载', readme)
        self.assertIn('没有宣称通过原生 Windows', readme)

    def test_pinned_manifests_and_original_hash_only(self):
        for name, digest in p.MANIFEST_PINS.items():
            self.assertEqual(p.sha((ROOT / name).read_bytes()), digest)
        original = p.load_json((ROOT / p.ORIGINAL_PINS).read_bytes())
        self.assertFalse(original['original_bytes_included'])
        self.assertEqual(len(original['files']), 74)
        for row in original['files']:
            self.assertEqual(set(row), {'path', 'bytes', 'sha256'})
            p.relative_path(row['path'], flat=True)
            self.assertIn(Path(row['path']).suffix, p.DATA_EXTENSIONS)
            self.assertNotIn(Path(row['path']).suffix, {'.exe', '.sav', '.cfg', '.box'})

    def test_exact_public_assets_and_hud(self):
        rows = p.load_json((ROOT / p.ASSET_PINS).read_bytes())['files']
        self.assertEqual(len(rows), 103)
        for row in rows + [p.HUD]:
            p.checked_file(ROOT / row['path'], row)
        p.validate_names(row['path'] for row in rows + [p.HUD])

    def test_controls_derive_from_current_public_launcher(self):
        # Existing Python interpreter is a harmless executable existence input.
        controls = p.verify_controls(ROOT, Path(sys.executable))
        self.assertEqual(len(controls), 53)
        self.assertNotIn('LAMP272_TOP_CLIP_ENABLE', controls)
        self.assertNotIn('PLAYER_SHIP_FAMILY_INVULNERABLE_ENABLE', controls)

    def test_generated_header_matches_native_contract(self):
        controls = p.load_json((ROOT / p.CONTROL_PINS).read_bytes())
        rows = [p.identity(p.GAME, b'game'), p.identity('bin/SDL2.dll', b'dll')]
        original = p.load_json((ROOT / p.ORIGINAL_PINS).read_bytes())['files']
        header = p.make_header(rows, original, controls, 'bundle', 'a' * 40).decode()
        self.assertIn('#define PREVIEW_GAME_EXE L"bin/opentyrian-level2.exe"', header)
        self.assertIn('PREVIEW_SOURCE_COMMIT', header)
        self.assertNotIn('typedef', header)
        self.assertEqual(header.count('static const Preview'), 3)
        self.assertIn('PREVIEW_ENV_COUNT', header)

    def test_default_and_check_only_never_assemble(self):
        arguments = ['--build-dir', '/build', '--build-sha256', 'a' * 64,
                     '--source-revision', 'b' * 40, '--dependencies', '/deps',
                     '--dependencies-sha256', 'c' * 64, '--output', '/new', '--zip', '/new.zip']
        plan = {'bundle_id': 'test', 'payload': [], 'originals': [], 'controls': {}}
        for suffix in ([], ['--check-only']):
            with patch.object(p, 'make_plan', return_value=plan), patch.object(p, 'assemble') as assemble:
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(p.main(arguments + suffix), 0)
                assemble.assert_not_called()

    def test_check_only_failure_does_not_create_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            out, arc = root / 'new', root / 'new.zip'
            args = argparse.Namespace(repo=ROOT, build_dir=root, dependencies=root,
                source_revision='0' * 40, output=out, zip=arc)
            with self.assertRaises(ValueError):
                p.make_plan(args)
            self.assertFalse(out.exists())
            self.assertFalse(arc.exists())

    def test_reproducible_zip_and_exact_tree(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            files = {'README.txt': b'hello', 'bin/game.exe': b'fake fixture'}
            bundle = root / 'bundle'
            bundle.mkdir()
            for name, raw in files.items():
                p.write_new(bundle / name, raw)
            p.inspect_tree(bundle, files)
            for name in ('one.zip', 'two.zip'):
                p.write_zip(root / name, files)
            self.assertEqual((root / 'one.zip').read_bytes(), (root / 'two.zip').read_bytes())
            with zipfile.ZipFile(root / 'one.zip') as z:
                self.assertEqual(z.namelist(), sorted(files))
                self.assertTrue(all(i.date_time == (1980, 1, 1, 0, 0, 0) for i in z.infolist()))
                self.assertTrue(all(stat.S_ISREG(i.external_attr >> 16) for i in z.infolist()))
            (bundle / 'unapproved.sav').write_bytes(b'private')
            with self.assertRaises(ValueError):
                p.inspect_tree(bundle, files)
            with self.assertRaises(FileExistsError):
                p.write_zip(root / 'one.zip', files)

    def test_source_module_no_pycache_writes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'module.py').write_text('VALUE = 5\n')
            self.assertEqual(p.source_module(root, 'module.py').VALUE, 5)
            self.assertEqual({f.name for f in root.iterdir()}, {'module.py'})


if __name__ == '__main__':
    unittest.main()
