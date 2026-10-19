#!/usr/bin/env python3
"""Packaging-only tests. Never load gameplay/source-projection fixtures."""
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('runtime_packaging', ROOT / 'scripts/package_runtime.py')
PACK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PACK)


def row(source, destination, data):
    return {'source_path': source, 'destination': destination, 'bytes': len(data), 'git_blob': hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest(), 'sha256': hashlib.sha256(data).hexdigest(), 'group': 'fixture'}


class PackagingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='runtime-packaging-test-')
        self.base = Path(self.temp.name)
        self.source = self.base / 'source'
        self.source.mkdir()
        (self.source / 'assets').mkdir()
        self.data = b'unchanged runtime pixels\0' * 17
        (self.source / 'assets/art.hda').write_bytes(self.data)
        self.manifest = self.base / 'manifest.json'
        self.content = {'schema': 'opentyrian-runtime-package-v1', 'source_revision': {'fixture': 'fixed'}, 'external_dependencies': {'data': 'external'}, 'files': [row('assets/art.hda', 'assets/gameplay/art.hda', self.data)]}
        self.save()

    def tearDown(self):
        self.temp.cleanup()

    def save(self):
        self.manifest.write_text(json.dumps(self.content))

    def run_pack(self, *extra):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = PACK.main(['--source-root', str(self.source), '--manifest', str(self.manifest), *map(str, extra)])
        return code, json.loads(output.getvalue())

    def test_dry_run_does_not_copy_or_change_source(self):
        code, report = self.run_pack()
        self.assertEqual(code, 0)
        self.assertTrue(report['assets_complete'])
        self.assertEqual((self.source / 'assets/art.hda').read_bytes(), self.data)
        self.assertEqual(sorted(p.name for p in self.base.iterdir()), ['manifest.json', 'source'])

    def test_missing_refuses_build_before_output(self):
        (self.source / 'assets/art.hda').rename(self.source / 'assets/art.dev')
        code, report = self.run_pack()
        self.assertEqual(code, 2)
        self.assertEqual(len(report['missing']), 1)
        with self.assertRaises(ValueError):
            self.run_pack('--build', '--output', self.base / 'out')
        self.assertFalse((self.base / 'out').exists())

    def test_corrupt_content_is_incomplete(self):
        (self.source / 'assets/art.hda').write_bytes(b'x' * len(self.data))
        code, report = self.run_pack()
        self.assertEqual(code, 2)
        self.assertIn('fingerprint mismatch', report['missing'][0]['errors'][0])

    def test_traversal_duplicate_and_oversize_refused(self):
        for change in ['../escape', '/absolute', 'assets\\windows', 'assets//odd']:
            with self.subTest(change=change):
                self.content['files'][0]['destination'] = change
                self.save()
                with self.assertRaises(ValueError): self.run_pack()
        self.content['files'][0]['destination'] = 'safe'
        self.content['files'].append(dict(self.content['files'][0]))
        self.save()
        with self.assertRaises(ValueError): self.run_pack()
        self.content['files'] = [self.content['files'][0]]
        self.content['files'][0]['bytes'] = 65 * PACK.MIB
        self.save()
        with self.assertRaises(ValueError): self.run_pack()

    def test_windows_paths_devices_and_generated_name_collisions_refused(self):
        invalid = ['C:/escape', 'C:relative', '//server/share', r'\\server\share', 'file:stream', 'a/CON', 'aux.txt', 'COM1.log', 'lpt9', 'a/trailing.', 'a/trailing ', 'a/b?c', 'a/line\nfeed', 'RUNTIME-INVENTORY.json', 'runtime-status.JSON', 'incomplete', 'COPY-VERIFIED.txt', 'INCOMPLETE/child', 'runtime-status.json/child']
        for destination in invalid:
            with self.subTest(destination=destination):
                self.content['files'][0]['destination'] = destination
                self.save()
                with self.assertRaises(ValueError): self.run_pack()
        self.content['files'][0]['destination'] = 'Folder/Art.hda'
        second = dict(self.content['files'][0], destination='folder/art.HDA')
        self.content['files'].append(second)
        self.save()
        with self.assertRaises(ValueError): self.run_pack()
        self.content['files'][1]['destination'] = 'Folder/Art.hda/child'
        self.save()
        with self.assertRaises(ValueError): self.run_pack()

    def test_explicit_executable_destination_collision_refused(self):
        self.content['files'][0]['destination'] = 'OpenTyrian2000.EXE'
        self.save()
        with self.assertRaises(ValueError):
            self.run_pack('--executable', self.source / 'assets/art.hda', '--platform', 'windows')

    def test_symlink_source_and_output_inside_source_refused(self):
        real = self.source / 'assets/art.hda'
        real.rename(self.base / 'real.hda')
        real.symlink_to(self.base / 'real.hda')
        with self.assertRaises(ValueError): self.run_pack()
        real.unlink()
        shutil.copyfile(self.base / 'real.hda', real)
        with self.assertRaises(ValueError): self.run_pack('--build', '--output', self.source / 'out')
        self.assertFalse((self.source / 'out').exists())

    def test_existing_output_is_never_overwritten(self):
        out = self.base / 'out'
        out.mkdir()
        with self.assertRaises(ValueError): self.run_pack('--build', '--output', out)
        self.assertEqual(list(out.iterdir()), [])

    def test_verified_copies_and_zip_are_deterministic(self):
        for i in [1, 2]:
            code, report = self.run_pack('--build', '--output', self.base / f'out{i}', '--zip', self.base / f'out{i}.zip')
            self.assertEqual(code, 0)
            self.assertFalse(report['runtime_ready'])
            self.assertFalse((self.base / f'out{i}/INCOMPLETE').exists())
            self.assertEqual((self.base / f'out{i}/assets/gameplay/art.hda').read_bytes(), self.data)
        self.assertEqual((self.base / 'out1.zip').read_bytes(), (self.base / 'out2.zip').read_bytes())
        with zipfile.ZipFile(self.base / 'out1.zip') as archive:
            self.assertTrue(all(x.date_time == (1980, 1, 1, 0, 0, 0) for x in archive.infolist()))
            self.assertIsNone(archive.testzip())

    def test_current_manifest_covers_each_loader_group(self):
        manifest = PACK.load_manifest(ROOT / 'packaging/runtime-assets-v1.json')
        groups = {}
        destinations = {x['destination'] for x in manifest['files']}
        for item in manifest['files']: groups[item['group']] = groups.get(item['group'], 0) + 1
        self.assertEqual(groups['gameplay'], 637)
        self.assertEqual(groups['startup'], 9)
        self.assertEqual(groups['shop'], 11)
        self.assertEqual(groups['notice'], 5)
        for name in ['settings-font-large-v1.hda', 'settings-font-medium-v1.hda', 'settings-font-tiny-v1.hda', 'title-menu-font-v1.hda', 'shop-generator-weapon16-v1.hda']:
            self.assertIn('assets/startup/' + name, destinations)
        for name in ['ground101-world-material.g101.0', 'ground101-world-material.g101.1', 'forest13-world-material.fcan', 'forest13.policy', 'plateau-cap-world-material.pcap']:
            self.assertIn('assets/gameplay/' + name, destinations)
        self.assertFalse(any(x['source_path'].endswith(('.png', '.ttf')) for x in manifest['files']))

    def test_launcher_uses_actual_engine_user_directory_function(self):
        compiler = shutil.which('cc')
        if not compiler:
            self.skipTest('C compiler unavailable for exact engine-directory witness')
        source = (ROOT / 'src/config.c').read_text()
        begin = source.index('const char *get_user_directory(void)')
        end = source.index('\n}\n', begin) + 3
        harness = self.base / 'user-directory.c'
        harness.write_text('#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n' + source[begin:end] + '\nint main(void) { puts(get_user_directory()); return 0; }\n')
        package = self.base / 'actual-path-package'
        package.mkdir()
        subprocess.run([compiler, '-std=c99', '-Wall', '-Wextra', '-Werror', str(harness), '-o', str(package / 'opentyrian2000')], check=True)
        launcher = package / 'start-hd.sh'
        shutil.copyfile(ROOT / 'packaging/start-hd.sh', launcher)
        launcher.chmod(0o755)
        data = self.base / 'actual-path-data'
        data.mkdir()
        (data / 'tyrian1.lvl').write_bytes(b'fixture')
        profile = self.base / 'actual-path-profile'
        env = dict(__import__('os').environ, OPENTYRIAN_HD_PROFILE=str(profile), XDG_CONFIG_HOME=str(self.base / 'ordinary-xdg'))
        result = subprocess.run([str(launcher), str(data)], env=env, check=True, capture_output=True, text=True)
        self.assertEqual(result.stdout.strip(), str(profile / 'opentyrian2000'))
        self.assertTrue((profile / 'opentyrian2000/opentyrian.cfg').is_file())
        self.assertFalse((self.base / 'ordinary-xdg').exists())

    def test_linux_launcher_keeps_existing_marked_profile_and_quotes_paths(self):
        package = self.base / 'package with spaces'
        package.mkdir()
        launcher = package / 'start-hd.sh'
        shutil.copyfile(ROOT / 'packaging/start-hd.sh', launcher)
        launcher.chmod(0o755)
        executable = package / 'opentyrian2000'
        executable.write_text('#!/bin/sh\nconfig_dir=$XDG_CONFIG_HOME/opentyrian2000\nprintf \"%s\\\\n\" \"$@\" > \"$config_dir/args.txt\"\nprintf \"%s\\\\n\" \"$config_dir\" > \"$config_dir/effective-path.txt\"\n')
        executable.chmod(0o755)
        data = self.base / 'original data'
        data.mkdir()
        (data / 'tyrian1.lvl').write_bytes(b'fixture')
        profile = self.base / 'profile'
        ordinary = self.base / 'ordinary-config'
        (ordinary / 'opentyrian2000').mkdir(parents=True)
        (ordinary / 'opentyrian2000/opentyrian.cfg').write_text('ordinary profile must survive\n')
        env = dict(__import__('os').environ, OPENTYRIAN_HD_PROFILE=str(profile), XDG_CONFIG_HOME=str(ordinary))
        subprocess.run([str(launcher), str(data)], env=env, check=True)
        effective = profile / 'opentyrian2000'
        config = effective / 'opentyrian.cfg'
        config.write_text('existing settings must survive\n')
        (effective / 'save.sav').write_bytes(b'personal save')
        subprocess.run([str(launcher), str(data), '--sound=off'], env=env, check=True)
        self.assertEqual((effective / 'effective-path.txt').read_text().strip(), str(effective))
        self.assertEqual((ordinary / 'opentyrian2000/opentyrian.cfg').read_text(), 'ordinary profile must survive\n')
        self.assertEqual(config.read_text(), 'existing settings must survive\n')
        self.assertEqual((effective / 'save.sav').read_bytes(), b'personal save')
        self.assertEqual((effective / 'args.txt').read_text().splitlines(), ['--data=' + str(data), '--manual-hd-assets=' + str(package / 'assets/gameplay'), '--startup-assets=' + str(package / 'assets/startup'), '--sound=off'])


if __name__ == '__main__':
    unittest.main()
