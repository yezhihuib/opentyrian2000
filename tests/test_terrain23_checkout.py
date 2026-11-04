"""Finite actual Git clean/checkout tests for new terrain23 paths only.

The fixed historical2269-path oracle is imported unchanged. This creates only
an isolated temporary Git repository, never edits the user's/public Git state,
and does not claim that absent old runtime resources have been tested.
"""
import hashlib
from pathlib import Path
import shutil
import tempfile
import unittest

import test_checkout_byte_preservation as historical

ROOT = Path(__file__).resolve().parents[1]
BASE_POLICY_BYTES = 136347
BASE_POLICY_SHA256 = 'ef6822f7c9024ef2dc2533b283619e83c70f3eb9a878278e4f45b28a9207f31a'
SCOPE_COUNT = 48
SCOPE_SHA256 = '42c3f675b32af6b49ae46e12ad3a5dbaa4c031eca802929396f2e3548f225b79'
BEGIN = '# BEGIN TERRAIN23 EXACT BYTE-PRESERVATION PATHS'
END = '# END TERRAIN23 EXACT BYTE-PRESERVATION PATHS'


def paths_for(policy):
    if hashlib.sha256(policy[:BASE_POLICY_BYTES]).hexdigest() != BASE_POLICY_SHA256:
        raise ValueError('Existing byte-preservation policy changed')
    historical.protected_paths(policy)
    lines = policy.decode().splitlines()
    if lines.count(BEGIN) != 1 or lines.count(END) != 1:
        raise ValueError('Missing unique terrain23 byte policy')
    rows = lines[lines.index(BEGIN) + 1:lines.index(END)]
    if any(not row.startswith('/') or not row.endswith(' -text') for row in rows):
        raise ValueError('Nonliteral terrain23 byte policy')
    paths = [row[1:-6] for row in rows]
    if (paths != sorted(set(paths)) or len(paths) != SCOPE_COUNT or
            hashlib.sha256(('\n'.join(paths) + '\n').encode()).hexdigest() != SCOPE_SHA256):
        raise ValueError('Changed finite terrain23 byte policy scope')
    return paths


class Terrain23Checkout(unittest.TestCase):
    def test_all_new_actual_files_clean_and_checkout_three_modes(self):
        if shutil.which('git') is None:
            self.skipTest('Git unavailable')
        policy = (ROOT / '.gitattributes').read_bytes()
        paths = paths_for(policy)
        before = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths}
        for mode in historical.MODES:
            with self.subTest(autocrlf=mode), tempfile.TemporaryDirectory(prefix='terrain23-checkout-') as tmp:
                work = Path(tmp)
                template = work / 'empty-template'; template.mkdir()
                historical.git(work, 'init', '--quiet', '--template=' + str(template))
                for attr in ROOT.rglob('.gitattributes'):
                    target = work / attr.relative_to(ROOT)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(attr.read_bytes())
                for path in paths:
                    raw = (ROOT / path).read_bytes()
                    target = work / path; target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(raw)
                    historical.git(work, 'add', '--', path, mode=mode)
                    oid = historical.git(work, 'rev-parse', ':' + path, mode=mode).decode().strip()
                    self.assertEqual(oid, historical.object_id(raw, len(oid)), (mode, path))
                    self.assertEqual(historical.git(work, 'cat-file', '--filters', '--path=' + path, oid, mode=mode), raw, (mode, path))
                    self.assertEqual(historical.git(work, 'cat-file', 'blob', oid, mode=mode), raw, (mode, path))
        self.assertEqual(before, {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths})

    def test_policy_missing_duplicate_and_old_change_rejected(self):
        policy = (ROOT / '.gitattributes').read_bytes()
        first = ('/' + paths_for(policy)[0] + ' -text\n').encode()
        for altered in (policy.replace(first, b'', 1), policy.replace(first, first + first, 1), b'!' + policy[1:]):
            with self.assertRaises(ValueError):
                paths_for(altered)


if __name__ == '__main__':
    unittest.main()
