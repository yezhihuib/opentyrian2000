"""Real frozen public assets plus synthetic PE fixtures; no Windows/game launch.

Set OPENTYRIAN_FROZEN_PACKAGE to the extracted verified 562e8fc input package
for the package integration group. Supervision tests run harmless Python only.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('preview', ROOT / 'scripts/preview_level2_frozen.py')
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)
PACKAGE = os.environ.get('OPENTYRIAN_FROZEN_PACKAGE')


def put(root, name, raw):
    target = root / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)
    return {'bytes': len(raw), 'sha256': p.sha(raw)}


def pe(dll=False):
    raw = bytearray(256)
    raw[:2] = b'MZ'
    struct.pack_into('<I', raw, 60, 128)
    raw[128:132] = b'PE\0\0'
    struct.pack_into('<H', raw, 132, 0x8664)
    struct.pack_into('<H', raw, 150, 0x2000 if dll else 0)
    return bytes(raw)


@unittest.skipUnless(PACKAGE, 'Requires explicitly supplied frozen 562e8fc package')
class PackageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='preview 中文 ')
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.source = self.base / 'old-runtime'
        self.source.mkdir()
        self.data = self.base / 'original'
        self.data.mkdir()
        package = Path(PACKAGE)
        files = {}
        for name in ['tools/' + n for n in p.TOOL_PINS] + [p.FAMILY_MANIFEST]:
            files[name] = put(self.source, name, (package / name).read_bytes())
        for row in json.loads((package / 'tools/HD-ASSET-PINS.json').read_text())['files']:
            files[row['path']] = put(self.source, row['path'], (package / row['path']).read_bytes())
        for name in ('opentyrian2000-level2.exe', 'SDL2.dll', 'SDL2_net.dll'):
            files['bin/' + name] = put(self.source, 'bin/' + name, pe(name.endswith('.dll')))
        stage = {'schema': 1, 'status': 'STAGED_NOT_BUILT', 'translation_units': 112, 'source_digest': p.SOURCE_DIGEST}
        stage_raw = json.dumps(stage).encode()
        files['trust/STAGE.json'] = put(self.source, 'trust/STAGE.json', stage_raw)
        build = {'status': 'BUILT_NOT_RUN', 'exit_code': 0, 'pe_machine': 'AMD64',
                 'inputs_unchanged_after_build': True, 'source_digest': p.SOURCE_DIGEST,
                 'stage_sha256': p.sha(stage_raw), 'binary': {'sha256': p.sha(pe())}}
        build_raw = json.dumps(build).encode()
        files['trust/BUILD-WINDOWS.json'] = put(self.source, 'trust/BUILD-WINDOWS.json', build_raw)
        data = {n: put(self.data, n, b'original fixture') for n in ('tyrian1.lvl', 'tyrian.hdt', 'tyrian.cdt', 'tyrian.snd', 'voices.snd', 'music.mus', 'palette.dat')}
        receipt = {'schema': 'opentyrian-windows-classic-runtime-v1', 'mode': 'hd', 'public_candidates': True,
                   'source_digest': p.SOURCE_DIGEST, 'stage_sha256': p.sha(stage_raw), 'build_sha256': p.sha(build_raw),
                   'files': files, 'data_directory': str(self.data), 'data_files': data}
        raw = json.dumps(receipt).encode()
        (self.source / 'RUNTIME.json').write_bytes(raw)
        self.args = argparse.Namespace(runtime=str(self.source), trust_sha256=p.sha(raw), output=str(self.base / 'preview'), prepare=False)

    def prepare(self):
        self.args.prepare = True
        r = p.prepare(self.args)
        return argparse.Namespace(root=self.args.output, trust_sha256=r['preview_sha256'], launch=False, observer_present=False)

    def test_default_no_write_or_launch(self):
        env, cwd = dict(os.environ), os.getcwd()
        with patch.object(p.subprocess, 'Popen') as launch:
            result = p.prepare(self.args)
            launch.assert_not_called()
        self.assertEqual(result['status'], 'CHECK_ONLY')
        self.assertFalse(Path(self.args.output).exists())
        self.assertEqual(dict(os.environ), env)
        self.assertEqual(os.getcwd(), cwd)
        self.assertEqual(result['argv'][-7:], list(p.PREVIEW_ARGS))

    def test_old_profile_never_imported_and_standalone_check(self):
        for n in ('tyrian.sav', 'opentyrian.cfg', 'launch-start.json', 'unrelated.dll'):
            (self.source / n).write_bytes(b'PRIVATE EXISTING INPUT')
        before = {n.name: n.read_bytes() for n in self.source.iterdir() if n.is_file()}
        args = self.prepare()
        root = Path(args.root)
        self.assertFalse((root / 'tyrian.sav').exists())
        self.assertEqual((root / 'opentyrian.cfg').read_bytes(), p.CONFIG)
        self.assertEqual(before, {n.name: n.read_bytes() for n in self.source.iterdir() if n.is_file()})
        shutil.rmtree(self.source)
        command = [sys.executable, str(root / 'preview_level2_frozen.py'), 'run', '--root', str(root), '--trust-sha256', args.trust_sha256]
        r = subprocess.run(command, capture_output=True, text=True, cwd=self.base)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout)['status'], 'CHECK_ONLY')
        self.assertFalse(any(root.rglob('__pycache__')))
        self.assertEqual(len(p.environment(root)), 23)
        self.assertNotIn('PLAYER_SHIP_FAMILY_ENABLE', p.environment(root))

    def test_existing_output_and_symlink_refused(self):
        out = Path(self.args.output)
        out.mkdir()
        with self.assertRaisesRegex(ValueError, 'Output must be new'):
            p.prepare(self.args)
        out.rmdir()
        out.symlink_to(self.source, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'Symlink/reparse'):
            p.prepare(self.args)

    def test_bad_source_and_asset_rejected_before_writes(self):
        old = self.args.trust_sha256
        self.args.trust_sha256 = '0' * 64
        with self.assertRaises(ValueError):
            p.prepare(self.args)
        self.args.trust_sha256 = old
        (self.source / 'assets/hd/current-compat/talon/ship-233-8.hda').write_bytes(b'bad')
        with self.assertRaises(ValueError):
            p.prepare(self.args)
        self.assertFalse(Path(self.args.output).exists())

    def test_tampered_tool_and_build_refused(self):
        (self.source / 'tools/launch_level2_family.py').write_text('raise RuntimeError("never execute")')
        with self.assertRaises(ValueError):
            p.prepare(self.args)
        self.assertFalse(Path(self.args.output).exists())

    def test_prepared_changes_and_reentry_refused(self):
        args = self.prepare()
        root = Path(args.root)
        self.assertEqual(p.run(args)['status'], 'CHECK_ONLY')
        config = root / 'opentyrian.cfg'
        config.write_bytes(b'other settings')
        with self.assertRaises(ValueError):
            p.run(args)
        config.write_bytes(p.CONFIG)
        (root / 'preview-start.json').write_text('{}')
        with self.assertRaisesRegex(ValueError, 'Unexpected/preexisting'):
            p.run(args)

    def test_launch_requires_windows_and_present_person(self):
        args = self.prepare()
        args.launch = True
        with patch.object(p.subprocess, 'Popen') as child:
            with self.assertRaisesRegex(ValueError, 'person'):
                p.run(args)
            args.observer_present = True
            with patch.object(p, 'WINDOWS', False):
                with self.assertRaisesRegex(ValueError, 'Windows launch only'):
                    p.run(args)
            child.assert_not_called()

    def test_changed_original_data_refused(self):
        args = self.prepare()
        (self.data / 'tyrian1.lvl').write_bytes(b'changed')
        with self.assertRaises(ValueError):
            p.run(args)


class SupervisorTests(unittest.TestCase):
    def test_environment_is_allowlisted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            e = p.child_environment(root, {'sYsTeMrOoT': str(root), 'sDl_VideoDriver': 'dummy', 'PATH': 'evil', 'NORMAL270_ENABLE': '1', 'USERPROFILE': 'private'})
            self.assertEqual(set(e), {'SYSTEMROOT', 'PATH'} | set(p.environment(root)))
            self.assertNotIn('evil', e['PATH'])

    def execute(self, code, **kw):
        with tempfile.TemporaryDirectory() as tmp:
            result = p.supervise([sys.executable, '-c', code], Path(tmp), dict(os.environ), **kw)
            return result, (Path(tmp) / 'preview-output.log').stat().st_size

    def test_clean_exit_and_literal_argument_dispatch(self):
        r, size = self.execute('print("harmless stub")')
        self.assertEqual(r['status'], 'EXITED')
        self.assertEqual(r['exit_code'], 0)
        self.assertGreater(size, 0)

    def test_wall_timeout_kills_and_reaps(self):
        r, _ = self.execute('import time; time.sleep(10)', seconds=0.1)
        self.assertEqual(r['status'], 'STOPPED')
        self.assertEqual(r['stop_reason'], 'wall-time-budget')
        self.assertLess(r['elapsed_seconds'], 3)

    def test_output_overflow_is_bounded(self):
        r, size = self.execute('import sys,time; sys.stdout.write("x"*100000); sys.stdout.flush(); time.sleep(10)', output_limit=1024)
        self.assertEqual(r['status'], 'STOPPED')
        self.assertEqual(size, 1024)

    def test_fast_exit_cannot_hide_output_failure(self):
        for code in ('import sys; sys.stdout.write("x"*100000)',
                     'import pathlib; pathlib.Path("native.json").write_bytes(b"x"*100000)'):
            with self.subTest(code=code):
                r, _ = self.execute(code, output_limit=1024)
                self.assertEqual(r['status'], 'STOPPED')
                self.assertIsNotNone(r['stop_reason'])

    def test_logging_error_cannot_return_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'preview-output.log').write_text('existing')
            result = p.supervise([sys.executable, '-c', 'pass'], root, dict(os.environ))
            self.assertEqual(result['status'], 'STOPPED')
            self.assertTrue(result['output_errors'])
            self.assertEqual((root / 'preview-output.log').read_text(), 'existing')

    def test_admission_requires_native_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'preview-output.log').write_text('Menu only')
            self.assertFalse(p.assess_preview(root)['preview_target_reached'])
            (root / 'preview-output.log').write_text('Asset debug target reached at tick245 eventLoc19 in 1ms\nControlled scene completed 600 logic ticks\n')
            (root / 'building313-family-canvas.json').write_text('{"accepted_frames":218}')
            self.assertEqual(p.assess_preview(root), {'preview_target_reached': True, 'hd_accepted_frames': 218, 'completed_600_ticks': True})

    def test_direct_diagnostic_output_is_counted(self):
        r, _ = self.execute('import pathlib,time; pathlib.Path("native.tsv").write_bytes(b"x"*100000); time.sleep(10)', output_limit=1024)
        self.assertEqual(r['stop_reason'], 'diagnostic-output-budget')


if __name__ == '__main__':
    unittest.main()
