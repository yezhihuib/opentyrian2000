"""Executable portable policy tests and native cross-build gates.

Host tests do not emulate Win32 or imply a Windows/GPU acceptance pass.
Set LEVEL2_MINGW_CC and LEVEL2_MINGW_OBJDUMP to run the real PE link/import gate.
"""
from pathlib import Path
import ctypes
import json
import os
import re
import shutil
import struct
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / 'tools/level2_preview_launcher_policy.h'
SOURCE = ROOT / 'tools/level2_preview_launcher.c'
HASH = b'0' * 64
GAME = 'bin/opentyrian-level2.exe'
REQUIRED = ['tyrian1.lvl', 'tyrian.hdt', 'tyrian.cdt', 'tyrian.snd', 'voices.snd', 'music.mus', 'palette.dat']


class File(ctypes.Structure):
    _fields_ = [('path', ctypes.c_wchar_p), ('sha256', ctypes.c_char_p), ('size', ctypes.c_ulonglong)]


class Env(ctypes.Structure):
    _fields_ = [('name', ctypes.c_wchar_p), ('value', ctypes.c_wchar_p)]


def reviewed_controls():
    section = POLICY.read_text().split('preview_reviewed_env[] = {', 1)[1].split('};', 1)[0]
    return re.findall(r'\{L"([^"]+)", L"([^"]+)"\}', section)


def native_fixture_header():
    payload = [GAME, 'bin/SDL2.dll', 'bin/SDL2_net.dll', 'assets/hd/example.hda']
    def entries(items):
        return ',\n'.join('{L"%s", "%s", 1ULL}' % (p, HASH.decode()) for p in items)
    return ('#define PREVIEW_GAME_EXE L"' + GAME + '"\n'
            '#define PREVIEW_BUNDLE_ID L"test-only-do-not-distribute"\n'
            '#define PREVIEW_SOURCE_COMMIT L"test-fixture"\n'
            'static const PreviewFile preview_payload[] = {' + entries(payload) + '};\n'
            '#define PREVIEW_PAYLOAD_COUNT (sizeof(preview_payload)/sizeof(preview_payload[0]))\n'
            'static const PreviewFile preview_original[] = {' + entries(REQUIRED) + '};\n'
            '#define PREVIEW_ORIGINAL_COUNT (sizeof(preview_original)/sizeof(preview_original[0]))\n'
            '#define preview_env preview_reviewed_env\n'
            '#define PREVIEW_ENV_COUNT PREVIEW_REVIEWED_ENV_COUNT\n')


class LauncherPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cc = shutil.which('cc')
        if not cc:
            raise unittest.SkipTest('Host C compiler unavailable; executable policy tests not run')
        cls.temp = tempfile.TemporaryDirectory(prefix='level2-policy-')
        folder = Path(cls.temp.name)
        wrapper = folder / 'test.c'
        wrapper.write_text('''#include "level2_preview_launcher_policy.h"
int process_length_ok(size_t a, size_t b) { return preview_process_path_fits(a, b); }
size_t volume_ok(const wchar_t *s) { return preview_volume_root_length(s); }
int path_ok(const wchar_t *s, int flat) { return preview_relative_path(s, flat); }
int digest_ok(const char *s) { return preview_digest_valid(s); }
int original_ok(const wchar_t *s) { return preview_original_path(s); }
int payload_ok(const wchar_t *s) { return preview_payload_path(s, L"bin/opentyrian-level2.exe"); }
int env_ok(const PreviewEnv *e, size_t n) { return preview_environment_valid(e, n); }
int inventory_ok(const PreviewFile *f, size_t n, int original) {
    return preview_inventory_valid(f, n, original, L"bin/opentyrian-level2.exe");
}
''')
        output = folder / 'policy.so'
        subprocess.run([cc, '-std=c11', '-shared', '-fPIC', '-Wall', '-Wextra', '-Werror',
                        '-I' + str(POLICY.parent), str(wrapper), '-o', str(output)], check=True, capture_output=True)
        cls.lib = ctypes.CDLL(str(output))
        for name in ('path_ok', 'original_ok', 'payload_ok', 'volume_ok'):
            getattr(cls.lib, name).argtypes = [ctypes.c_wchar_p] + ([ctypes.c_int] if name == 'path_ok' else [])
        cls.lib.process_length_ok.argtypes = [ctypes.c_size_t, ctypes.c_size_t]
        cls.lib.digest_ok.argtypes = [ctypes.c_char_p]
        cls.lib.env_ok.argtypes = [ctypes.POINTER(Env), ctypes.c_size_t]
        cls.lib.inventory_ok.argtypes = [ctypes.POINTER(File), ctypes.c_size_t, ctypes.c_int]

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_only_strict_local_volume_guid_identities(self):
        root = '\\\\?\\Volume{01234567-89ab-cdef-0123-456789abcdef}\\'
        for path in (root, root + 'Tyrian Data', root + '中文\\session'):
            self.assertEqual(self.lib.volume_ok(path), 49)
        for path in (None, '', 'C:\\Tyrian', '\\\\?\\C:\\Tyrian', '\\\\server\\share\\',
                     '\\\\?\\UNC\\server\\share\\', root[:-1], root.replace('89ab', 'zzzz'),
                     root.replace('Volume{', 'Device{'), root.replace('-89ab', '_89ab')):
            self.assertEqual(self.lib.volume_ok(path), 0)

    def test_process_and_legacy_asset_path_length_boundaries(self):
        for directory, relative in ((3, 25), (100, 158), (259, 0), (234, 24)):
            self.assertEqual(self.lib.process_length_ok(directory, relative), 1)
        for directory, relative in ((260, 0), (100, 159), (259, 1), (3, 260), (2**32, 1)):
            self.assertEqual(self.lib.process_length_ok(directory, relative), 0)

    def test_relative_ascii_paths(self):
        for path in (GAME, 'assets/hd/current-compat/tank-shell/body.hda', 'newsh#.shp', "newsh'.shp", 'shapes).dat'):
            with self.subTest(path=path):
                self.assertEqual(self.lib.path_ok(path, 0), 1)
        self.assertEqual(self.lib.path_ok('tyrian.hdt', 1), 1)
        self.assertEqual(self.lib.path_ok('data/tyrian.hdt', 1), 0)

    def test_traversal_streams_unicode_and_device_names_rejected(self):
        for path in (None, '', '.', '..', '../x', 'a/../x', '/x', '//x', 'C:/x', 'a\\b',
                     'a//b', 'a/', 'a/.', 'a/b.', 'a/b ', 'a b', '中文/file', 'a:stream',
                     'a\nfile', 'a*', 'a?', 'a|b', 'a"b', '<x>', 'CON', 'NUL.txt',
                     'a/COM1.bin', 'a/lpt9.hda', 'a/aux.txt', 'prn', 'x' * 512):
            with self.subTest(path=path):
                self.assertEqual(self.lib.path_ok(path, 0), 0)
        for path in ('console.hda', 'com10.hda', 'lpt0.hda', 'a/conifer.hda'):
            self.assertEqual(self.lib.path_ok(path, 0), 1)

    def test_original_inventory_cannot_import_profiles_or_code(self):
        for path in REQUIRED + ['newsh#.shp', "newsh'.shp", 'shapes).dat', 'tyrian.pic']:
            self.assertEqual(self.lib.original_ok(path), 1)
        for path in ('tyrian.cfg', 'opentyrian.cfg', 'tyrian.sav', 'tyrian2.exe', 'SDL2.dll',
                     'startup.bat', 'settings.ini', 'readme.txt', 'data/tyrian.hdt', 'data.lnk'):
            self.assertEqual(self.lib.original_ok(path), 0)

    def test_only_reviewed_payload_locations(self):
        for path in (GAME, 'bin/SDL2.dll', 'bin/SDL2_net.dll', 'assets/hd/pack/file.hda'):
            self.assertEqual(self.lib.payload_ok(path), 1)
        for path in ('evil.exe', 'opentyrian.cfg', 'sessions/existing/file', 'bin/evil.dll',
                     'data/tyrian.lvl', 'assets/no-hd/file', 'assets/hd/../x', 'assets/hd'):
            self.assertEqual(self.lib.payload_ok(path), 0)

    def test_sha256_is_exact_lowercase_hex(self):
        self.assertEqual(self.lib.digest_ok(HASH), 1)
        for value in (None, b'', b'0' * 63, b'0' * 65, b'g' * 64, b'A' * 64):
            self.assertEqual(self.lib.digest_ok(value), 0)

    def test_exact_current_controls_and_no_debug_overrides(self):
        controls = reviewed_controls()
        self.assertEqual(len(controls), 53)
        self.assertEqual(len(dict(controls)), 53)
        names = dict(controls)
        self.assertEqual(names['BUILDING313_TANK_FALLBACK_ENABLE'], '1')
        self.assertEqual(names['BUILDING313_FAMILY_HUD_ENABLE'], '1')
        self.assertEqual(names['TANK194_FAMILY_ASSET_DIR'], 'assets/hd/artwork/type15-eightheading-smooth-contour-v2/output')
        self.assertEqual(self.lib.env_ok((Env * len(controls))(*[Env(*x) for x in controls]), len(controls)), 1)
        self.assertEqual(self.lib.env_ok((Env * len(controls))(*[Env(*x) for x in reversed(controls)]), len(controls)), 1)
        for changed in (controls[:23], controls[:-1], controls + [('SDL_VIDEODRIVER', 'dummy')],
                        controls[:-1] + [('ASSET_DEBUG', '1')], controls[:-1] + [controls[0]],
                        [(controls[0][0], '0')] + controls[1:],
                        [(controls[0][0].lower(), controls[0][1])] + controls[1:]):
            self.assertEqual(self.lib.env_ok((Env * len(changed))(*[Env(*x) for x in changed]), len(changed)), 0)

    def test_current_packager_manifests_match_native_contract(self):
        controls = json.loads((ROOT / 'packaging/level2-preview-controls.json').read_text())
        self.assertEqual(controls, dict(reviewed_controls()))
        manifest = json.loads((ROOT / 'packaging/level2-original-data-hashes.json').read_text())
        self.assertIs(manifest['original_bytes_included'], False)
        rows = [File(x['path'], x['sha256'].encode(), x['bytes']) for x in manifest['files']]
        self.assertEqual(len(rows), 74)
        self.assertEqual(self.lib.inventory_ok((File * len(rows))(*rows), len(rows), 1), 1)

    def test_inventory_uniqueness_file_ancestors_and_mandatory_entries(self):
        def valid(names, originals=False, sizes=None, hashes=None):
            rows = [File(p, (hashes or {}).get(i, HASH), (sizes or {}).get(i, 1)) for i, p in enumerate(names)]
            return self.lib.inventory_ok((File * len(rows))(*rows), len(rows), originals)
        payload = [GAME, 'bin/SDL2.dll', 'bin/SDL2_net.dll', 'assets/hd/test.hda']
        self.assertEqual(valid(payload), 1)
        self.assertEqual(valid(REQUIRED, True), 1)
        for names in ([], payload[1:], payload[:-2], payload + ['bin/EVIL.dll'],
                      payload + ['assets/hd/TEST.hda'], payload + ['assets/hd/test.hda/child'],
                      payload + ['assets/hd'], payload + ['assets/hd/test.hda:Zone.Identifier']):
            self.assertEqual(valid(names), 0)
        for names in (REQUIRED[:-1], REQUIRED + ['tyrian.cfg'], REQUIRED + ['TYRIAN.HDT'], REQUIRED + ['setup.exe']):
            self.assertEqual(valid(names, True), 0)
        self.assertEqual(valid(payload, sizes={0: 0}), 0)
        self.assertEqual(valid(payload, hashes={0: b'x' * 64}), 0)
        self.assertEqual(self.lib.inventory_ok(None, 0, 0), 0)


class LauncherSourceContractTests(unittest.TestCase):
    """Guard against accidentally reviving the former scripted preview runner."""
    def test_native_lifecycle_and_no_global_state_changes(self):
        code = SOURCE.read_text()
        for token in ('GetModuleFileNameW', 'CreateFileW', 'CopyFileW(source, target, TRUE)',
                      'BCryptHashData', 'BCryptGenRandom', 'FILE_FLAG_OPEN_REPARSE_POINT',
                      'FILE_SHARE_READ', ':Zone.Identifier', 'CREATE_NEW', 'PROC_THREAD_ATTRIBUTE_HANDLE_LIST',
                      'CREATE_UNICODE_ENVIRONMENT', 'CreateProcessW', 'WaitForSingleObject(process.hProcess, INFINITE)',
                      '--data=data --level2-preview=asteroid2-v1 --no-xmas --no-joystick'):
            self.assertIn(token, code)
        for forbidden in ('SetEnvironmentVariable', 'GetEnvironmentStrings', 'SetCurrentDirectory', 'TerminateProcess',
                          'ShellExecute', 'DeleteFile', 'RemoveDirectory', 'Unblock-File', 'powershell',
                          '--asset-debug', '--render-ticks', '--probe', 'SendInput(', 'keybd_event('):
            self.assertNotIn(forbidden, code)
        self.assertLess(code.index('if (app->check_only) {\n        display_message'), code.index('if (!prepare_session(app)'))
        self.assertIn('app->scale = 4;', code)
        self.assertIn('L"--scale=2"', code)

    def test_overlap_uses_locked_physical_identity_before_writes(self):
        code = SOURCE.read_text()
        for token in ('GetFinalPathNameByHandleW', 'FILE_NAME_NORMALIZED | VOLUME_NAME_GUID',
                      'GetDriveTypeW(root)', 'CompareStringOrdinal',
                      'a.dwVolumeSerialNumber != b.dwVolumeSerialNumber',
                      'a.nFileIndexHigh != b.nFileIndexHigh', 'a.nFileIndexLow != b.nFileIndexLow',
                      'is_ancestor(app->data_identity, app->root_identity)',
                      'copy_inventory(app, app->root_identity', 'copy_inventory(app, app->data_identity'):
            self.assertIn(token, code)
        self.assertNotIn('is_ancestor(app->data,', code)
        self.assertNotIn('is_ancestor(sessions, app->data)', code)
        actual_launch = code[code.index('static int fresh_session('):code.index('static int prepare_session(')]
        self.assertLess(actual_launch.index('validate_locations(app)'), actual_launch.index('make_directory(app, sessions'))
        self.assertIn('directory_identity(app, sessions)', actual_launch)
        self.assertIn('join_path(app, app->root_identity, L"sessions")', actual_launch)

    def test_only_verified_nonverbatim_dos_paths_reach_createprocess(self):
        code = SOURCE.read_text()
        for token in ('FILE_NAME_NORMALIZED | VOLUME_NAME_DOS', 'QueryDosDeviceW(drive, drive_target',
                      'QueryDosDeviceW(volume, volume_target', 'directory_identity(app, extended)',
                      'session_paths_fit(app, n)', 'environment, app->process_session, &startup.StartupInfo',
                      'join_path(app, app->process_session, PREVIEW_GAME_EXE)'):
            self.assertIn(token, code)
        launch = code[code.index('static int run_game('):code.index('static wchar_t *choose_original_data(')]
        self.assertNotIn('environment, app->session,', launch)
        self.assertLess(launch.index('FlushFileBuffers'), launch.index('checked_directory = process_directory'))
        self.assertLess(launch.index('checked_directory = process_directory'), launch.index('if (!CreateProcessW'))
        prepare = code[code.index('static int prepare_session('):code.index('static int env_compare(')]
        self.assertLess(prepare.index('app->process_session = process_directory'), prepare.index('copy_inventory'))
        fresh = code[code.index('static int fresh_session('):code.index('static int prepare_session(')]
        self.assertLess(fresh.index('preflight_process_paths(app)'), fresh.index('make_directory(app, sessions'))

    def test_mingw_pe_links_without_non_os_imports(self):
        cc = os.environ.get('LEVEL2_MINGW_CC') or shutil.which('x86_64-w64-mingw32-gcc')
        objdump = os.environ.get('LEVEL2_MINGW_OBJDUMP') or shutil.which('x86_64-w64-mingw32-objdump')
        if not cc or not objdump:
            self.skipTest('MinGW not configured; real Windows cross-link/import gate not run')
        with tempfile.TemporaryDirectory(prefix='level2-pe-') as temp:
            folder = Path(temp)
            header = folder / 'manifest.h'
            header.write_text(native_fixture_header())
            output = folder / 'Start-Level2-Preview.exe'
            result = subprocess.run([cc, '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror', '-municode', '-mwindows',
                                     '-static-libgcc', '-Wl,--no-insert-timestamp',
                                     '-DPREVIEW_MANIFEST_HEADER="' + str(header) + '"', str(SOURCE), '-o', str(output),
                                     '-lbcrypt', '-lshell32', '-lole32'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            raw = output.read_bytes()
            offset = struct.unpack_from('<I', raw, 60)[0]
            self.assertEqual(raw[offset:offset+4], b'PE\0\0')
            self.assertEqual(struct.unpack_from('<H', raw, offset + 4)[0], 0x8664)
            self.assertEqual(struct.unpack_from('<H', raw, offset + 24)[0], 0x20b)
            details = subprocess.check_output([objdump, '-p', str(output)], text=True)
            imports = {name.lower() for name in re.findall(r'DLL Name:\s*(\S+)', details)}
            self.assertIn('bcrypt.dll', imports)
            self.assertIn('shell32.dll', imports)
            self.assertIn('ole32.dll', imports)
            self.assertLessEqual(imports, {'bcrypt.dll', 'kernel32.dll', 'msvcrt.dll', 'shell32.dll', 'user32.dll', 'ole32.dll', 'advapi32.dll'})
            self.assertNotIn('libwinpthread-1.dll', imports)


if __name__ == '__main__':
    unittest.main()
