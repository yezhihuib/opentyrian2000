"""Actual Git checkout/clean regression; no Windows compiler claim.

Run with Python and Git installed. By default the repository containing this
file supplies both policy and blobs. --repo can supply a byte-equivalent Git
object source when reviewing an isolated policy patch without a full checkout.
No source repository configuration, index, working files or objects are written.
"""
import argparse
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT
BEGIN = '# BEGIN EXACT BYTE-PRESERVATION PATHS'
END = '# END EXACT BYTE-PRESERVATION PATHS'
EXISTING = (
    'assets/hd/artwork/gameplay-hud-v5/ownership-audit-safe-static-310.tsv',
    'assets/hd/artwork/gameplay-hud-indicators-v1/placement-state.csv',
    'assets/hd/artwork/gameplay-hud-labels-shield-v1/build_assets.py',
    'tests/fixtures/portable-history-v1/manifest.json',
)
LATE_NUL = (
    'assets/hd/artwork/gameplay-hud-corner-v2/corner-4x.rgba',
    'assets/shop-frame-v1/static-metal-support-320x200.bin',
)
MODES = ('true', 'false', 'input')


def environment():
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    env.update(GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull,
               GIT_CONFIG_SYSTEM=os.devnull, GIT_ATTR_NOSYSTEM='1',
               GIT_OPTIONAL_LOCKS='0')
    return env


def git(root, *args, data=None, mode='false'):
    cmd = ['git', '-c', 'core.autocrlf=' + mode, '-c', 'core.safecrlf=false',
           '-c', 'core.attributesFile=' + os.devnull, '-C', str(root), *args]
    p = subprocess.run(cmd, input=data, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, env=environment())
    if p.returncode:
        raise AssertionError((cmd, p.returncode, p.stderr.decode(errors='replace')))
    return p.stdout


def object_id(raw, width):
    h = hashlib.sha1() if width == 40 else hashlib.sha256()
    h.update(('blob %d\0' % len(raw)).encode('ascii'))
    h.update(raw)
    return h.hexdigest()


def snapshot(root):
    paths = []
    for name in ('config', 'index'):
        p = Path(os.fsdecode(git(root, 'rev-parse', '--git-path', name)).strip())
        paths.append(p if p.is_absolute() else root / p)
    result = {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
              if p.exists() else None for p in paths}
    for relative in ('src/tyrian2.c', 'scripts/current_warning_source_bridge.py',
                     'packaging/current-production-validation.json'):
        result[relative] = hashlib.sha256((root / relative).read_bytes()).hexdigest()
    result['HEAD'] = git(root, 'rev-parse', 'HEAD').decode().strip()
    result['tree'] = git(root, 'rev-parse', 'HEAD^{tree}').decode().strip()
    result['status'] = git(root, 'status', '--porcelain=v1', '-uno').decode()
    return result


def protected_paths(policy):
    # Independent fixed scope anchor: deleting a rule must not silently reduce coverage.
    if hashlib.sha256(policy[:716]).hexdigest() != '50ca67bf38c6c7aedc42c94b9c9a344e5a3d46261faf174d7488f1f85f841b83':
        raise ValueError('Original attributes prefix changed')
    lines = policy.decode('utf-8').splitlines()
    if lines.count(BEGIN) != 1 or lines.count(END) != 1:
        raise ValueError('Missing unique exact policy block')
    paths = []
    for line in lines[lines.index(BEGIN) + 1:lines.index(END)]:
        if not line.startswith('/') or not line.endswith(' -text'):
            raise ValueError('Only root-anchored -text literals permitted')
        p = line[1:-6]
        if any(c in p for c in '*?[]\\\r\n\t ') or '..' in Path(p).parts:
            raise ValueError('Nonliteral protected path')
        paths.append(p)
    if paths != sorted(set(paths)):
        raise ValueError('Policy must be sorted and unique')
    result = sorted(set(paths) | set(EXISTING))
    digest = hashlib.sha256(('\n'.join(result) + '\n').encode('utf-8')).hexdigest()
    if len(result) != 2245 or digest != '9aaf93e2153c448fe1952c73b766141e30e7b688dd94876d6936df13cf467f8c':
        raise ValueError('Protected path scope changed')
    return result


class CheckoutBytePreservation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if shutil.which('git') is None:
            raise unittest.SkipTest('Git is required for actual filter tests')
        cls.before = snapshot(SOURCE)
        cls.policy = (ROOT / '.gitattributes').read_bytes()
        cls.paths = protected_paths(cls.policy)
        cls.tree = {}
        for record in git(SOURCE, 'ls-tree', '-r', '-z', 'HEAD').split(b'\0'):
            if not record:
                continue
            meta, path = record.split(b'\t', 1)
            mode, kind, oid = meta.decode().split()
            cls.tree[os.fsdecode(path)] = (mode, kind, oid)
        for p in cls.paths:
            if p not in cls.tree or cls.tree[p][1] != 'blob':
                raise AssertionError('Protected path not in current Git tree: ' + p)
        cls.temp = tempfile.TemporaryDirectory(prefix='git-byte-policy-')
        cls.work = Path(cls.temp.name)
        empty_template = cls.work / 'empty-template'
        empty_template.mkdir()
        git(cls.work, 'init', '--quiet', '--template=' + str(empty_template))
        objects = Path(os.fsdecode(git(SOURCE, 'rev-parse', '--git-path', 'objects')).strip())
        if not objects.is_absolute():
            objects = SOURCE / objects
        (cls.work / '.git/objects/info/alternates').write_text(
            objects.resolve().as_posix() + '\n', encoding='utf-8')
        git(cls.work, 'update-ref', 'HEAD', cls.before['HEAD'])
        (cls.work / '.gitattributes').write_bytes(cls.policy)
        cls.nested = [p for p in cls.tree if p.endswith('/.gitattributes')]
        for p in cls.nested:
            target = cls.work / p
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(git(SOURCE, 'cat-file', 'blob', cls.tree[p][2]))
        if (cls.work / '.git/info/attributes').exists():
            raise AssertionError('Unexpected info attributes')

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()
        if snapshot(SOURCE) != cls.before:
            raise AssertionError('Source config/index/HEAD/tree/status changed')

    def test_all_exact_paths_actual_filters_three_modes(self):
        block = self.policy.decode('utf-8').splitlines()
        first = block[block.index(BEGIN) + 1]
        mutations = (
            self.policy.replace((first + '\n').encode(), b'', 1),
            self.policy.replace(END.encode(), b'/README.md -text\n' + END.encode(), 1),
            self.policy.replace((first + '\n').encode(), ((first + '\n') * 2).encode(), 1),
        )
        for mutated in mutations:
            with self.assertRaises(ValueError):
                protected_paths(mutated)
        for mode in MODES:
            for p in self.paths:
                oid = self.tree[p][2]
                raw = git(self.work, 'cat-file', '--filters', '--path=' + p, oid, mode=mode)
                self.assertEqual(object_id(raw, len(oid)), oid, (mode, p))

    def test_actual_late_nul_binary_filters_three_modes(self):
        for p in LATE_NUL:
            oid = self.tree[p][2]
            raw = git(SOURCE, 'cat-file', 'blob', oid)
            self.assertGreater(raw.index(b'\0'), 512)
            self.assertLess(raw.index(b'\0'), 8000)
            for mode in MODES:
                filtered = git(self.work, 'cat-file', '--filters', '--path=' + p, oid, mode=mode)
                self.assertEqual(filtered, raw, (mode, p))

    def test_real_add_clean_roundtrip_and_unprotected_readme(self):
        historic = min((p for p in self.tree if p.startswith('tests/fixtures/portable-history-v1/blobs/')),
                       key=lambda p: int(git(SOURCE, 'cat-file', '-s', self.tree[p][2])))
        representatives = ['Makefile', 'src/nortsong.h', 'src/palette.c', historic]
        for mode in MODES:
            for p in representatives:
                oid = self.tree[p][2]
                raw = git(SOURCE, 'cat-file', 'blob', oid)
                if p == 'src/nortsong.h':
                    self.assertIn(b'\r\n', raw)
                    self.assertNotIn(b'\n', raw.replace(b'\r\n', b''))
                if p == 'src/palette.c':
                    self.assertIn(b'\r\n', raw)
                    self.assertIn(b'\n', raw.replace(b'\r\n', b''))
                target = self.work / p
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw)
                git(self.work, 'add', '--', p, mode=mode)
                self.assertEqual(git(self.work, 'rev-parse', ':' + p).decode().strip(), oid, (mode, p))
                checked = git(self.work, 'cat-file', '--filters', '--path=' + p, oid, mode=mode)
                self.assertEqual(checked, raw)
                target.unlink()
            binary = b'\0binary\r\nline\n\xff'
            p = 'assets/hd/byte-policy-control.hda'
            target = self.work / p
            target.write_bytes(binary)
            git(self.work, 'add', '--', p, mode=mode)
            oid = git(self.work, 'rev-parse', ':' + p).decode().strip()
            self.assertEqual(git(self.work, 'cat-file', 'blob', oid), binary)
            self.assertEqual(git(self.work, 'cat-file', '--filters', '--path=' + p, oid, mode=mode), binary)
            target.unlink()
            plain = b'Unrelated README control\nsecond line\n'
            oid = git(self.work, 'hash-object', '-w', '--stdin', data=plain).decode().strip()
            checked = git(self.work, 'cat-file', '--filters', '--path=README.md', oid, mode=mode)
            self.assertEqual(checked, plain.replace(b'\n', b'\r\n') if mode == 'true' else plain)
            target = self.work / 'README.md'
            target.write_bytes(checked)
            git(self.work, 'add', '--', 'README.md', mode=mode)
            self.assertEqual(git(self.work, 'rev-parse', ':README.md').decode().strip(), oid)
            target.unlink()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path, default=ROOT)
    args, rest = parser.parse_known_args()
    SOURCE = args.repo.resolve()
    unittest.main(argv=[__file__, *rest])
