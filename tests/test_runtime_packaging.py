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
        self.assertEqual(groups['shop'], 12)
        self.assertEqual(groups['notice'], 11)
        self.assertEqual(groups['data-frame'], 1)
        self.assertEqual(groups['data-text'], 3)
        self.assertEqual(manifest['closure']['shop_files'], groups['shop'])
        self.assertEqual(groups['global-source-identity'], 49)
        self.assertEqual(groups['global-registry'], 1)
        self.assertEqual(groups['reconstructed-menu-runs'], 171)
        self.assertEqual(groups['shared-hud-exact-recovery'], 6)
        self.assertEqual(len(manifest['files']), 931)
        self.assertLess(sum(item['bytes'] for item in manifest['files']), PACK.RUNTIME_LIMIT)
        for name in ['settings-font-large-v1.hda', 'settings-font-medium-v1.hda', 'settings-font-tiny-v1.hda', 'title-menu-font-v1.hda', 'shop-generator-weapon16-v1.hda', 'shop-shield-option26-v1.hda']:
            self.assertIn('assets/startup/' + name, destinations)
        for name in ['ground101-world-material.g101.0', 'ground101-world-material.g101.1', 'forest13-world-material.fcan', 'forest13.policy', 'plateau-cap-world-material.pcap']:
            self.assertIn('assets/gameplay/' + name, destinations)
        self.assertFalse(any(x['source_path'].endswith(('.png', '.ttf', '.bin', '.py')) for x in manifest['files']))

    def test_shield_selection_pins_only_the_accepted_runtime_material(self):
        selection = json.loads((ROOT / 'packaging/runtime-selection-v1.json').read_text())
        self.assertIn('assets/shop-shield-v1', selection['shop_runtime_directories'])
        self.assertEqual(selection['shop_runtime_extension'], '.hda')
        manifest = PACK.load_manifest(ROOT / 'packaging/runtime-assets-v1.json')
        shield_rows = [item for item in manifest['files'] if item['source_path'].startswith('assets/shop-shield-v1/')]
        self.assertEqual(len(shield_rows), 1)
        material = shield_rows[0]
        self.assertEqual(material['source_path'], 'assets/shop-shield-v1/shop-shield-option26-v1.hda')
        self.assertEqual(material['destination'], 'assets/startup/shop-shield-option26-v1.hda')
        self.assertEqual(material['group'], 'shop')
        self.assertEqual(material['bytes'], 72992)
        self.assertEqual(material['revision'], 'reconstructed-local-unpublished')
        self.assertEqual(manifest['source_revision']['shield_integration'], 'local accepted source; no commit assigned')
        self.assertEqual(PACK.checked_source(ROOT / material['source_path'], material)['sha256'], material['sha256'])

    def test_data_text_closure_and_relocated_launcher_arguments(self):
        manifest = PACK.load_manifest(ROOT / 'packaging/runtime-assets-v1.json')
        rows = [r for r in manifest['files'] if r['group'] == 'data-text']
        self.assertEqual(len(rows), 3)
        for item in rows:
            self.assertEqual(item['source_path'], item['destination'])
            self.assertEqual(PACK.checked_source(ROOT / item['source_path'], item)['sha256'], item['sha256'])
        script = (ROOT / 'packaging/start-hd.ps1').read_text()
        self.assertIn("Join-Path $repoRoot 'assets/data-text-zh-CN-v1'", script)
        self.assertNotIn("Join-Path $root 'assets/data-text-zh-CN-v1'", script)
        self.assertIn('--data-text-assets=', script)

    def test_data_frame_optional_resource_closure(self):
        manifest = PACK.load_manifest(ROOT / 'packaging/runtime-assets-v1.json')
        rows = [r for r in manifest['files'] if r['group'] == 'data-frame']
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['source_path'], 'assets/data-frame-v1/data-frame-v1.hda')
        self.assertEqual(rows[0]['destination'], rows[0]['source_path'])
        self.assertEqual(rows[0]['bytes'], 4096128)
        self.assertEqual(PACK.checked_source(ROOT / rows[0]['source_path'], rows[0])['sha256'], rows[0]['sha256'])
        self.assertEqual(manifest['closure']['data_frame_files'], 1)
        for launcher in ('start-hd.sh', 'start-hd.ps1'):
            self.assertIn('--data-frame-assets=', (ROOT / 'packaging' / launcher).read_text())

    def test_data_portrait_optional_resource_closure(self):
        manifest = PACK.load_manifest(ROOT / 'packaging/runtime-assets-v1.json')
        rows = [r for r in manifest['files'] if r['group'] == 'data-portrait']
        self.assertEqual(len(rows), 18)
        self.assertEqual([r['source_path'] for r in rows], [f'assets/data-portrait-v1/face{f:02d}-v1.hda' for f in range(18)])
        self.assertEqual(sum(r['bytes'] for r in rows), 4420800)
        for row in rows:
            self.assertEqual(row['destination'], row['source_path'])
            self.assertEqual(PACK.checked_source(ROOT / row['source_path'], row)['sha256'], row['sha256'])
        self.assertEqual(manifest['closure']['data_portrait_files'], 18)
        for launcher in ('start-hd.sh', 'start-hd.ps1'):
            self.assertIn('--data-portrait-assets=', (ROOT / 'packaging' / launcher).read_text())

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
        self.assertEqual((effective / 'args.txt').read_text().splitlines(), ['--data=' + str(data), '--manual-hd-assets=' + str(package / 'assets/gameplay'), '--startup-assets=' + str(package / 'assets/startup'), '--common-menu-assets=' + str(package / 'assets/startup'), '--hud-assets=' + str(package / 'assets/shared-ui'), '--global-assets=' + str(package / 'assets/global'), '--data-text-assets=' + str(package / 'assets/data-text-zh-CN-v1'), '--data-frame-assets=' + str(package / 'assets/data-frame-v1'), '--data-portrait-assets=' + str(package / 'assets/data-portrait-v1'), '--sound=off'])

    def test_exact_global_registry_and_resource_closure(self):
        manifest = PACK.load_manifest(ROOT / 'packaging/runtime-assets-v1.json')
        selected = {r['destination']: r for r in manifest['files']}
        registry = json.loads((ROOT / 'assets/hd/global-assets-v1/registry.json').read_text())
        self.assertEqual(len(registry['resources']), 49)
        expected = {'assets/global/registry.json'}
        for resource in registry['resources']:
            destination = 'assets/global/' + resource['path']
            expected.add(destination)
            row = selected[destination]
            self.assertEqual(row['source_path'], 'assets/hd/global-assets-v1/' + resource['path'])
            self.assertEqual(row['bytes'], resource['bytes'])
            self.assertEqual(PACK.checked_source(ROOT / row['source_path'], row)['sha256'], resource['sha256'])
        self.assertEqual({p for p in selected if p.startswith('assets/global/')}, expected)
        self.assertIn('FRONTEND-VALIDATION.json', selected)
        self.assertIn('GLOBAL-VALIDATION.json', selected)
        for launcher in ('start-hd.sh', 'start-hd.ps1'):
            self.assertIn('--global-assets=', (ROOT / 'packaging' / launcher).read_text())

    def test_global_validation_binds_current_production_source(self):
        validation = json.loads((ROOT / 'packaging/global-validation.json').read_text())
        sources = {str(p.relative_to(ROOT)) for p in (ROOT / 'src').iterdir()
                   if p.is_file() and p.suffix in ('.c', '.h', '.inc')}
        self.assertEqual(set(validation['source_sha256']), sources)
        for source, digest in validation['source_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT / source).read_bytes()).hexdigest(), digest)
        manifest = PACK.load_manifest(ROOT / 'packaging/runtime-assets-v1.json')
        self.assertEqual(manifest['source_revision']['global_runtime_commit'], validation['production_commit'])
        self.assertEqual(manifest['source_revision']['global_registry_sha256'],
                         hashlib.sha256((ROOT / 'assets/hd/global-assets-v1/registry.json').read_bytes()).hexdigest())

    def test_global_selected_file_missing_corrupt_refuses_copy(self):
        manifest = PACK.load_manifest(ROOT / 'packaging/runtime-assets-v1.json')
        original = next(r for r in manifest['files'] if r['group'] == 'global-source-identity')
        self.content['files'] = [original]
        self.save()
        code, report = self.run_pack()
        self.assertEqual(code, 2)
        self.assertEqual(len(report['missing']), 1)
        target = self.source / original['source_path']
        target.parent.mkdir(parents=True)
        target.write_bytes(b'x' * original['bytes'])
        with self.assertRaises(ValueError):
            self.run_pack('--build', '--output', self.base / 'incomplete-global')
        self.assertFalse((self.base / 'incomplete-global').exists())

    def test_windows_project_covers_all_compile_units(self):
        import xml.etree.ElementTree as ET
        tree = ET.parse(ROOT / 'visualc/opentyrian.vcxproj')
        ns = {'m': 'http://schemas.microsoft.com/developer/msbuild/2003'}
        units = [Path(n.attrib['Include'].replace('\\', '/')).name
                 for n in tree.findall('.//m:ClCompile', ns) if 'Include' in n.attrib]
        self.assertEqual(len(units), len(set(units)))
        self.assertEqual(set(units), {p.name for p in (ROOT / 'src').glob('*.c')})
        # Global .inc files are compiled through render_mirror.c, never as units.
        self.assertIn('render_mirror.c', units)

    def test_manifest_rebuild_is_deterministic(self):
        output = self.base / 'rebuilt.json'
        subprocess.run([__import__('sys').executable, str(ROOT / 'scripts/rebuild_recovered_runtime_manifest.py'),
                        '--root', str(ROOT), '--output', str(output)], check=True, capture_output=True)
        self.assertEqual(output.read_bytes(), (ROOT / 'packaging/runtime-assets-v1.json').read_bytes())


if __name__ == '__main__':
    unittest.main()
