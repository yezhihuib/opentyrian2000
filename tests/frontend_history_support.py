"""Separate immutable historical proofs from a strict current production gate.

No current file is substituted for historical data; no private Git responses are
fabricated. Historical snapshots remain untouched and are deleted after use.
"""
from contextlib import contextmanager
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess
import sys
import tarfile
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).parent/'fixtures/frontend-native-history-v1'
INDEX_SHA256 = 'd2e0bb9c2f8bbf364270e33ace561c1909d5341ba1773eeee49170d4f1c2ef82'
PUBLIC = '775b6b77163723c6cae727bafce1d53746a5bd60'
PUBLIC_TREE = '9306469adfc3a8897d11ab02d705757a0a8e77b8'
STAGES = {
    'test_pregame_coexistence.py': ('916b7aa8a4a837c695d6cef4b1e9da133db27ef1', 'fa5130a2644d00d27dc8c5652f1705210207f8d4'),
    'test_pregame_font_integration.py': ('916b7aa8a4a837c695d6cef4b1e9da133db27ef1', 'fa5130a2644d00d27dc8c5652f1705210207f8d4'),
    'test_settings_integration.py': ('a4974da93ee75fb18c7ad5827ea42a6b02d1b74d', 'd85c0fd64cdd26c1fe3c60a1deee05732b1bb8c7'),
}
PRODUCTION = ('src', 'assets', 'visualc')


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])


def verify_bytes(raw, digest, size=None):
    assert hashlib.sha256(raw).hexdigest() == digest, 'Pinned historical content changed'
    if size is not None:
        assert len(raw) == size, 'Pinned historical size changed'
    return raw


class NativeSources:
    def __init__(self, kind, repo=ROOT, fixtures=FIXTURES):
        self.repo, self.fixtures = Path(repo), Path(fixtures)
        raw = verify_bytes((self.fixtures/'index.json').read_bytes(), INDEX_SHA256)
        self.kind = kind
        self.index = json.loads(raw)[kind]

    def paths(self):
        return list(self.index['sources'])

    def read(self, name):
        row = self.index['sources'][name]
        raw = ((self.fixtures/row['fixture']).read_bytes() if 'fixture' in row
               else git(self.repo, 'show', row['published_source']))
        return verify_bytes(raw, row['sha256'], row['bytes'])

    def resource_sha256(self, name):
        return self.index['resources'][name]

    def provenance(self):
        return {
            'native_label': self.index['original_native_label'],
            'archive': self.index['archive'],
            'archive_sha256': self.index['archive_sha256'],
            'source_files': len(self.paths()),
            'proof': ('original Git object recovered and source archive verified' if self.kind == 'settings'
                      else 'archive-backed content proof; c923 Git object unavailable'),
            'resource_anchor': ('4597e39c75b949d8f4e1f22bbc6117b432294132:docs/pregame-font-v1/COEXISTENCE-RECEIPT.json'
                                if self.kind == 'pregame' else None),
        }


def production_inventory(repo=ROOT):
    assert git(repo, 'rev-parse', PUBLIC+'^{tree}').decode().strip() == PUBLIC_TREE
    entries = {}
    for row in git(repo, 'ls-tree', '-rz', PUBLIC, *PRODUCTION).split(b'\0'):
        if row:
            meta, name = row.split(b'\t', 1)
            mode, kind, blob = meta.decode().split()
            assert kind == 'blob' and mode in ('100644', '100755')
            entries[name.decode()] = (mode, blob)
    return entries


def validate_production_map(actual, expected):
    assert set(actual) == set(expected), 'Unapproved added/removed production paths'
    for name, (mode, raw) in actual.items():
        blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        assert (mode, blob) == expected[name], 'Unapproved current production bytes/mode: '+name


def current_production_proof(repo=ROOT):
    repo = Path(repo)
    expected = production_inventory(repo)
    actual_paths = {str(p.relative_to(repo)) for top in PRODUCTION
                    for p in (repo/top).rglob('*') if p.is_file() or p.is_symlink()}
    assert actual_paths == set(expected), 'Unapproved added/removed current production paths'
    total = 0
    for name, pin in expected.items():
        p = repo/name
        assert p.is_file() and not p.is_symlink(), 'Nonregular current production file: '+name
        raw = p.read_bytes()
        mode = '100755' if p.stat().st_mode & 0o111 else '100644'
        validate_production_map({name: (mode, raw)}, {name: pin})
        total += len(raw)
    return {'result': 'PASS', 'scope': 'current production bytes, modes and exact path inventory',
            'published_anchor': PUBLIC, 'published_tree': PUBLIC_TREE,
            'files': len(expected), 'bytes': total,
            'runtime_claim': 'No new native runtime claim; existing runtime oracles remain separate.'}


@contextmanager
def historical_snapshot(name, repo=ROOT):
    commit, tree = STAGES[name]
    assert git(repo, 'rev-parse', commit+'^{tree}').decode().strip() == tree
    subprocess.run(['git', '-C', str(repo), 'merge-base', '--is-ancestor', commit, PUBLIC], check=True)
    with tempfile.TemporaryDirectory(prefix='frontend-history-') as directory:
        root = Path(directory)
        process = subprocess.Popen(['git', '-C', str(repo), 'archive', commit], stdout=subprocess.PIPE)
        try:
            with tarfile.open(fileobj=process.stdout, mode='r|') as archive:
                for member in archive:
                    target = root/member.name
                    assert target.resolve().is_relative_to(root), 'Unsafe historical archive path'
                    if member.isdir():
                        target.mkdir(parents=True, exist_ok=True)
                    else:
                        assert member.isfile(), 'Nonregular historical archive entry'
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_bytes(archive.extractfile(member).read())
                        target.chmod(member.mode)
            assert process.wait() == 0, 'Historical archive failed'
            # Read-only Git queries resolve published ancestors from the existing object DB.
            gitdir = git(repo, 'rev-parse', '--absolute-git-dir').decode().strip()
            (root/'.git').write_text('gitdir: '+gitdir+'\n')
            yield root
        finally:
            process.stdout.close()
            if process.poll() is None:
                process.terminate()
                process.wait()


def historical_proof(name, repo=ROOT):
    with historical_snapshot(name, repo) as snapshot:
        receipt = snapshot/'oracle-receipt.json'
        result = subprocess.run([sys.executable, str(Path(__file__).with_name('frontend_history_oracles.py')),
                                 str(snapshot), name, str(repo), str(receipt)], capture_output=True, text=True)
        assert result.returncode == 0, result.stdout+'\n'+result.stderr
        report = json.loads(receipt.read_text())
        assert report['result'] == 'PASS'
        report['proof_scope'] = 'immutable historical source/art oracle, not current-tree runtime'
        report['historical_stage'] = STAGES[name][0]
        return report


class HistoricalFrontendOracle(unittest.TestCase):
    def __init__(self, name):
        super().__init__('runTest')
        self.name = name

    def id(self):
        return self.name.removesuffix('.py')+'.CliOracle.test_cli_oracle'

    def runTest(self):
        self.assertEqual(historical_proof(self.name)['result'], 'PASS')


class CurrentFrontendProductionOracle(HistoricalFrontendOracle):
    def id(self):
        return self.name.removesuffix('.py')+'.CurrentProductionOracle.test_exact_published_production'

    def runTest(self):
        self.assertEqual(current_production_proof()['result'], 'PASS')


def paired_suite(name):
    return unittest.TestSuite([HistoricalFrontendOracle(name), CurrentFrontendProductionOracle(name)])


def main(name):
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    current = current_production_proof()
    report = historical_proof(name)
    report['current_production_proof'] = current
    report['proof_scope'] = 'paired immutable historical oracle and strict current production gate'
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))
