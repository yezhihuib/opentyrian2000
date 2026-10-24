#!/usr/bin/env python3
"""Finite current Protron macro extraction, never a historical hash rebase."""
import copy
import subprocess
import unittest
from unittest.mock import patch
import accepted_later_changes as a


class CurrentProtronProjectionTests(unittest.TestCase):
    def test_only_two_source_files_and_exact_inverse(self):
        ledger = a.current_protron_ledger()
        self.assertEqual(set(ledger['files']), {'src/render_mirror.c', 'src/enemy_reuse_mirror.inc'})
        for name, pin in ledger['files'].items():
            raw = (a.ROOT / name).read_bytes()
            old = subprocess.check_output(['git', 'show', ledger['integration_base'] + ':' + name], cwd=a.ROOT)
            self.assertEqual(a.project_current_protron_source(name, raw), old)
            self.assertEqual(a.sha(old), pin['previous_sha256'])
            for bad in (old, raw + b'\n', raw[:-1]):
                with self.assertRaises(AssertionError):
                    a.project_current_protron_source(name, bad)
            # Source stamp and shadow coverage are not generated or relaxed.
            self.assertNotIn('coverage', ''.join(h['after'] for h in pin['hunks']))

    def test_every_hunk_and_result_are_required(self):
        ledger = a.current_protron_ledger()
        for name, pin in ledger['files'].items():
            raw = (a.ROOT / name).read_bytes()
            for field in ('after', 'before'):
                bad = copy.deepcopy(ledger)
                bad['files'][name]['hunks'][0][field] += '\n'
                with patch.object(a, 'current_protron_ledger', return_value=bad):
                    with self.assertRaises(AssertionError):
                        a.project_current_protron_source(name, raw)

    def test_older_source_oracles_remain_exact(self):
        for name in a.current_protron_ledger()['files']:
            raw = (a.ROOT / name).read_bytes()
            for label in ('enemy-controlled-probe', 'enemy-proof-dedup', 'enemy-protron-reuse', 'render-boundaries'):
                if name not in a.load(label + '-source.json')['files']:
                    continue
                restored = a.project_source(label, name, raw)
                self.assertEqual(a.sha(restored), a.load(label + '-source.json')['files'][name]['previous_sha256'])


if __name__ == '__main__':
    unittest.main()
