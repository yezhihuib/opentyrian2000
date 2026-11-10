"""Cross-build guard and input tests. These do not claim a Windows runtime pass."""
import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('level2_mingw', ROOT / 'scripts/build_level2_mingw.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class Level2MinGWTests(unittest.TestCase):
    def test_complete_overlay_input_snapshot(self):
        files, origins, units, defines = module.source_inputs(ROOT)
        self.assertEqual(len(units), 112)
        self.assertEqual(len(set(units)), 112)
        self.assertIn('src/b313_platform.h', files)
        self.assertEqual(origins['src/tyrian2.c'], 'experimental/level2-family/src/tyrian2.c')
        self.assertIn('B313_FAMILY_CANVAS_DIAGNOSTIC', defines)
        for name, origin in origins.items():
            self.assertEqual(files[name], (ROOT / origin).read_bytes())
        self.assertIn('visualc/resources.rc', files)
        self.assertIn('visualc/tyrian2000.ico', files)
        self.assertFalse(any(name.endswith(('.sav', '.cfg', '.lvl', '.shp')) for name in files))

    def test_build_directory_must_be_new_and_outside_checkout(self):
        with tempfile.TemporaryDirectory() as temp:
            fresh = Path(temp) / 'new'
            self.assertEqual(module.fresh_destination(ROOT, fresh), fresh)
            self.assertFalse(fresh.exists())
            for invalid in (Path(temp), ROOT, ROOT / 'never-created-mingw-stage'):
                with self.assertRaises(ValueError):
                    module.fresh_destination(ROOT, invalid)

    def test_reject_symlink_into_repo(self):
        with tempfile.TemporaryDirectory() as temp:
            alias = Path(temp) / 'checkout-alias'
            alias.symlink_to(ROOT, target_is_directory=True)
            with self.assertRaises(ValueError):
                module.fresh_destination(ROOT, alias / 'must-not-write')

    def test_pe_machine_and_optional_header_are_checked(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'fixture.exe'
            raw = bytearray(96)
            raw[:2] = b'MZ'; struct.pack_into('<I', raw, 60, 64)
            raw[64:68] = b'PE\0\0'; struct.pack_into('<H', raw, 68, 0x8664)
            struct.pack_into('<H', raw, 88, 0x20b)
            path.write_bytes(raw)
            self.assertEqual(module.validate_pe_x64(path), 'AMD64')
            for mutated in (b'', b'not windows', raw[:80]):
                path.write_bytes(mutated)
                with self.assertRaises(ValueError):
                    module.validate_pe_x64(path)
            struct.pack_into('<H', raw, 68, 0x14c); path.write_bytes(raw)
            with self.assertRaises(ValueError):
                module.validate_pe_x64(path)
            struct.pack_into('<H', raw, 68, 0x8664)
            struct.pack_into('<H', raw, 88, 0x10b); path.write_bytes(raw)
            with self.assertRaises(ValueError):
                module.validate_pe_x64(path)

    def test_windows_data_text_path_is_not_msvc_only(self):
        source = (ROOT / 'src/data_text.c').read_text()
        self.assertNotIn('_MSC_VER', source)
        self.assertEqual(source.count('#ifdef _WIN32'), 3)
        self.assertIn('int fd=open(path,O_RDONLY|O_NONBLOCK);', source)
        self.assertIn('_fstat(_fileno(f),&info)', source)

    def test_non_system_dependencies_are_not_silently_allowed(self):
        self.assertIn('bcrypt.dll', module.SYSTEM_DLLS)
        for name in ('sdl2.dll', 'sdl2_net.dll', 'libwinpthread-1.dll', 'libcrypto-3-x64.dll'):
            self.assertNotIn(name, module.SYSTEM_DLLS)


if __name__ == '__main__':
    unittest.main()
