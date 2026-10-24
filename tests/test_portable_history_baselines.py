#!/usr/bin/env python3
"""Exact historical oracles; no private commit or mutable-source fallback.

Set PORTABLE_HISTORY_PUBLIC_GIT_DIR to an isolated full-public object database
for the additional absence proof. Ordinary tests use this checkout's Git DB.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from portable_history_baselines import BaselineError, Provider

FIXTURE = ROOT / 'tests/fixtures/portable-history-v1'
MANIFEST_SHA256 = '2f10a46d70cb5fed377373f22f484b1c27f2a9cb1a969eab765cbf08407c9b02'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def blob_id(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def gitdir():
    override = os.environ.get('PORTABLE_HISTORY_PUBLIC_GIT_DIR')
    if override:
        return Path(override).resolve()
    return Path(subprocess.check_output(
        ['git', 'rev-parse', '--absolute-git-dir'], cwd=ROOT).decode().strip())


class PortableHistoryFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = gitdir()
        cls.manifest = json.loads((FIXTURE / 'manifest.json').read_bytes())
        cls.base, cls.name, cls.row = next(
            (base, name, row)
            for base, entry in cls.manifest['baselines'].items()
            for name, row in entry['preimages'].items()
            if row['storage'] == 'fixture')

    def test_fixed_complete_fixture_and_all_preimages(self):
        files = [p for p in FIXTURE.rglob('*') if p.is_file()]
        self.assertEqual(len(files), 32)
        self.assertEqual(sum(p.stat().st_size for p in files), 4120570)
        self.assertEqual(digest((FIXTURE / 'manifest.json').read_bytes()), MANIFEST_SHA256)
        provider = Provider(FIXTURE, self.db)
        count = 0
        public = set()
        for base, entry in self.manifest['baselines'].items():
            for name, row in entry['preimages'].items():
                raw = provider.preimage(base, name)
                self.assertEqual(len(raw), row['size'])
                self.assertEqual(digest(raw), row['sha256'])
                self.assertEqual(blob_id(raw), row['blob'])
                if row['storage'] == 'public-git-blob':
                    public.add(row['blob'])
                count += 1
        self.assertEqual(count, 155)
        self.assertEqual(len(public), 62)

    def test_all_complete_inventory_pins(self):
        provider = Provider(FIXTURE, self.db)
        count = 0
        for base, entry in self.manifest['baselines'].items():
            if entry['inventory']:
                rows = provider.inventory(base)
                raw = (json.dumps(rows, indent=2, sort_keys=True) + '\n').encode()
                self.assertEqual(digest(raw), entry['inventory'])
                self.assertTrue(rows)
                count += 1
        self.assertEqual(count, 5)

    def test_missing_extra_corrupt_symlink_and_descriptor_rejected(self):
        cases = ('missing', 'extra', 'changed-byte', 'symlink-file',
                 'symlink-directory', 'manifest-mode', 'manifest-path',
                 'manifest-sha', 'descriptor-byte')
        for case in cases:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as tmp:
                dest = Path(tmp) / 'fixture'
                shutil.copytree(FIXTURE, dest)
                path = dest / 'blobs' / self.row['blob']
                if case == 'missing':
                    path.unlink()
                elif case == 'extra':
                    (dest / 'unlisted.bin').write_bytes(b'x')
                elif case == 'changed-byte':
                    path.write_bytes(path.read_bytes() + b'x')
                elif case == 'symlink-file':
                    target = Path(tmp) / 'original'
                    path.rename(target)
                    path.symlink_to(target)
                elif case == 'symlink-directory':
                    target = Path(tmp) / 'original-blobs'
                    (dest / 'blobs').rename(target)
                    (dest / 'blobs').symlink_to(target, target_is_directory=True)
                elif case.startswith('manifest-'):
                    manifest = json.loads((dest / 'manifest.json').read_bytes())
                    rows = manifest['baselines'][self.base]['preimages']
                    if case == 'manifest-mode':
                        rows[self.name]['mode'] = '100755'
                    elif case == 'manifest-sha':
                        rows[self.name]['sha256'] = '0' * 64
                    else:
                        rows['wrong-path'] = rows.pop(self.name)
                    (dest / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
                else:
                    descriptor = next((dest / 'inventories').iterdir())
                    descriptor.write_bytes(descriptor.read_bytes() + b'x')
                with self.assertRaises(BaselineError):
                    provider = Provider(dest, self.db)
                    provider.preimage(self.base, self.name)
                    for base, entry in self.manifest['baselines'].items():
                        if entry['inventory']:
                            provider.inventory(base)

    def test_unknown_baseline_path_and_missing_public_blob_rejected(self):
        provider = Provider(FIXTURE, self.db)
        for base, name in [('HEAD', self.name), (self.base, 'src/unlisted.c'),
                           (self.base, '../manifest.json')]:
            with self.subTest(base=base, name=name), self.assertRaises(BaselineError):
                provider.preimage(base, name)
        for base in ('HEAD', next(b for b, entry in self.manifest['baselines'].items()
                                  if not entry['inventory'])):
            with self.subTest(inventory=base), self.assertRaises(BaselineError):
                provider.inventory(base)
        base, name = next((b, n) for b, entry in self.manifest['baselines'].items()
                          for n, row in entry['preimages'].items()
                          if row['storage'] == 'public-git-blob')
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run(['git', 'init', '--bare', '--quiet', tmp], check=True)
            with self.assertRaises(BaselineError):
                Provider(FIXTURE, tmp).preimage(base, name)

    def test_corrupt_public_blob_is_not_accepted(self):
        provider = Provider(FIXTURE, self.db)
        base, name = next((b, n) for b, entry in self.manifest['baselines'].items()
                          for n, row in entry['preimages'].items()
                          if row['storage'] == 'public-git-blob')
        with patch.object(provider, 'blob', return_value=b'not the pinned public blob'):
            with self.assertRaises(BaselineError):
                provider.preimage(base, name)

    @unittest.skipUnless(os.environ.get('PORTABLE_HISTORY_PUBLIC_GIT_DIR'),
                         'requires explicitly supplied isolated public-only Git DB')
    def test_private_commit_and_root_objects_are_absent(self):
        self.assertFalse((self.db / 'objects/info/alternates').exists())
        self.assertEqual(len(self.manifest['baselines']), 8)
        for base, entry in self.manifest['baselines'].items():
            for oid in (base, entry['tree']):
                with self.subTest(oid=oid):
                    result = subprocess.run(['git', '--git-dir=' + str(self.db),
                                             'cat-file', '-e', oid],
                                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    self.assertNotEqual(result.returncode, 0)


class PortableHistoryCandidateTests(unittest.TestCase):
    def test_symlink_parent_cannot_hide_tracked_descendant(self):
        raw = b'fixed historical preimage\n'
        expected = {'assets/d/a.bin': {'mode': '100644', 'blob': blob_id(raw),
                                      'sha256': digest(raw), 'size': len(raw)}}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'repo'
            root.mkdir()
            subprocess.run(['git', 'init', '--quiet', str(root)], check=True)
            (root / 'assets/d').mkdir(parents=True)
            (root / 'assets/d/a.bin').write_bytes(raw)
            subprocess.run(['git', 'add', 'assets/d/a.bin'], cwd=root, check=True)
            external = Path(tmp) / 'outside'
            (root / 'assets/d').rename(external)
            (root / 'assets/d').symlink_to(external, target_is_directory=True)
            # Even identical outside bytes and an ignored replacement cannot
            # silently satisfy the tracked original's inventory.
            (root / '.gitignore').write_text('assets/d\n')
            provider = Provider(FIXTURE, gitdir())
            with patch.object(provider, 'inventory', return_value=expected):
                with self.assertRaisesRegex(BaselineError, 'symlink candidate parent'):
                    provider.changed('fixed', root, ('assets',))

    def test_same_provider_rechecks_candidate_after_edit_and_restore(self):
        raw = b'fixed historical preimage\n'
        expected = {'assets/a.bin': {'mode': '100644', 'blob': blob_id(raw),
                                    'sha256': digest(raw), 'size': len(raw)}}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(['git', 'init', '--quiet', tmp], check=True)
            (root / 'assets').mkdir()
            path = root / 'assets/a.bin'
            path.write_bytes(raw)
            subprocess.run(['git', 'add', 'assets/a.bin'], cwd=root, check=True)
            provider = Provider(FIXTURE, gitdir())
            with patch.object(provider, 'inventory', return_value=expected):
                self.assertEqual(provider.changed('fixed', root, ('assets',)), set())
                path.write_bytes(raw + b'x')
                self.assertEqual(provider.changed('fixed', root, ('assets',)), {'assets/a.bin'})
                path.write_bytes(raw)
                self.assertEqual(provider.changed('fixed', root, ('assets',)), set())

    def test_exact_paths_modes_bytes_and_git_ignore_semantics(self):
        raw = b'fixed historical preimage\n'
        # This independent literal is not derived from current implementation/source.
        expected = {'assets/a.bin': {'mode': '100644', 'blob': blob_id(raw),
                                     'sha256': digest(raw), 'size': len(raw)}}
        cases = {
            'unchanged': set(),
            'changed-byte': {'assets/a.bin'},
            'missing': {'assets/a.bin'},
            'extra': {'assets/extra.bin'},
            'executable-mode': {'assets/a.bin'},
            'symlink-mode': {'assets/a.bin'},
            'renamed-path': {'assets/a.bin', 'assets/b.bin'},
            'ignored-pycache': set(),
            'unignored-pycache': {'assets/__pycache__/generated.pyc'},
            'tracked-ignored-change': {'assets/a.bin'},
            'autocrlf-clean': set(),
        }
        for case, changes in cases.items():
            with self.subTest(case=case), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                subprocess.run(['git', 'init', '--quiet', tmp], check=True)
                (root / 'assets').mkdir()
                path = root / 'assets/a.bin'
                path.write_bytes(raw)
                subprocess.run(['git', 'add', 'assets/a.bin'], cwd=root, check=True)
                if case == 'changed-byte':
                    path.write_bytes(raw + b'x')
                elif case == 'missing':
                    path.unlink()
                elif case == 'extra':
                    (root / 'assets/extra.bin').write_bytes(b'x')
                elif case == 'executable-mode':
                    path.chmod(0o755)
                elif case == 'symlink-mode':
                    path.unlink()
                    path.symlink_to('other')
                elif case == 'renamed-path':
                    path.rename(root / 'assets/b.bin')
                elif case in ('ignored-pycache', 'unignored-pycache'):
                    if case == 'ignored-pycache':
                        (root / '.gitignore').write_text('__pycache__/\n')
                    (root / 'assets/__pycache__').mkdir()
                    (root / 'assets/__pycache__/generated.pyc').write_bytes(b'cache')
                elif case == 'autocrlf-clean':
                    subprocess.run(['git', 'config', 'core.autocrlf', 'true'], cwd=root, check=True)
                    path.write_bytes(raw.replace(b'\n', b'\r\n'))
                elif case == 'tracked-ignored-change':
                    (root / '.gitignore').write_text('assets/a.bin\n')
                    path.write_bytes(raw + b'x')
                provider = Provider(FIXTURE, gitdir())
                with patch.object(provider, 'inventory', return_value=expected):
                    self.assertEqual(provider.changed('fixed', root, ('assets',)), changes)


if __name__ == '__main__':
    unittest.main()
