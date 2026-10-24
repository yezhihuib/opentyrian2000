"""Public-source-only checks for current Front Multi payload extraction.

The old ten-row prototype remains frozen. These tests never load original game
source/data and do not claim gameplay, visual or platform acceptance.
"""
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import accepted_later_changes as history
import run_sonic_quadrant_shadow_tests as shadow

ROOT = Path(__file__).resolve().parents[1]
# Independent, historical bootstrap payload oracle, not read from the header.
BOOTSTRAP = {
    121: 0x769aa8931a65a717, 122: 0x761a0ae775198a5a,
    163: 0xa99cb87d5291eb77, 164: 0x6b0a01101b3bca0f,
    201: 0x8d51f656ce22bf04, 202: 0x64cfd4d0e05f13a3,
    279: 0xd4ada839dcc2ebb5, 280: 0xca10e502fd370f78,
}

# Independent reviewed order, including the three current-payload inverses which
# do not go through _project_source_once. Do not derive this oracle from the
# implementation under test.
REVIEWED_SOURCE_INVERSES = (
    'current-guided', 'current-sonic', 'normal-observer-surface', 'current-protron',
    'enemy-controlled-probe', 'enemy-reuse-observe', 'enemy-proof-dedup',
    'enemy-protron-reuse', 'enemy-green-reuse', 'enemy-reuse',
    'newshf-compositor', 'newshf-identity', 'enemy-orb', 'front-multi',
    'plasma-projectile', 'charge-body', 'render-boundaries', 'storm',
)
FRONT_CURRENT_SOURCES = frozenset({
    'src/render_mirror.c', 'src/enemy_reuse_probe.h',
    'src/enemy_reuse_probe.inc',
})


class FrontMultiShadowBoundary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / 'src/render_mirror.c').read_text()
        cls.header = (ROOT / 'src/hd_front_multi_current.h').read_text()

    def test_exact_45_rows_and_independent_eight_source_slot_payload_oracle(self):
        rows = shadow.verify_front_multi_rows(self.source)
        self.assertEqual(len(rows), 45)
        old = history.project_source('front-multi', 'src/render_mirror.c', self.source.encode()).decode()
        self.assertEqual(len(shadow.verify_front_multi_rows(old, payloads=BOOTSTRAP)), 45)
        # Bootstrap remains independently asserted in the immutable inverse;
        # legitimate future current pixels need not equal these old pixels.
        self.assertEqual(shadow.shadow_pin_rows(old)[2:10],
            [f' {{{i},{slot},UINT64_C(0x{stamp:016x}),UINT64_C(0x{BOOTSTRAP[i]:016x}),0,0}}'
             for i, slot, stamp in shadow.FRONT_MULTI_PINS])

    def test_unknown_macro_missing_duplicate_and_extra_header_pin_rejected(self):
        token = 'HD_FRONT_MULTI_CURRENT_PAYLOAD_80121_HASH'
        for source in (self.source.replace(token, 'HD_FRONT_MULTI_CURRENT_PAYLOAD_80999_HASH'),
                       self.source.replace(token, 'UNRESOLVED_SHADOW_PAYLOAD')):
            with self.subTest(source=source[:32]), self.assertRaises(AssertionError):
                shadow.shadow_pin_rows(source)
        line = next(line for line in self.header.splitlines(True) if line.startswith('#define ' + token + ' '))
        for header in (self.header.replace(line, ''), self.header + line,
                       self.header + line.replace('80121', '80999')):
            with self.subTest(header=header[-100:]), self.assertRaises(AssertionError):
                shadow.shadow_pin_rows(self.source, front_header=header)

    def test_changed_slot_stamp_payload_coverage_or_row_count_rejected(self):
        mutations = {
            'slot': ('{121,524,', '{121,525,'),
            'stamp': ('0xba0e9fed90289c7a', '0xba0e9fed90289c7b'),
            'payload-literal': ('HD_FRONT_MULTI_CURRENT_PAYLOAD_80121_HASH', 'UINT64_C(0x0000000000000000)'),
            'coverage': ('HD_FRONT_MULTI_CURRENT_PAYLOAD_80121_HASH,0,0}', 'HD_FRONT_MULTI_CURRENT_PAYLOAD_80121_HASH,532,0}'),
            'declared-count': ('vulcan_shadow_pins[45]', 'vulcan_shadow_pins[44]'),
        }
        row = next(line for line in self.source.splitlines(True) if line.startswith(' {121,524,'))
        for label, source in [(label, self.source.replace(a, b, 1)) for label, (a, b) in mutations.items()] + [('missing-row', self.source.replace(row, '')), ('duplicate-row', self.source.replace(row, row + row))]:
            with self.subTest(label=label), self.assertRaises(AssertionError):
                shadow.verify_front_multi_rows(source)
        bad = self.header.replace(f'0x{shadow.front_multi_payloads()[121]:016x}', '0x0000000000000000', 1)
        self.assertNotEqual(bad, self.header)
        with self.assertRaisesRegex(AssertionError, 'oracle mismatch'):
            shadow.verify_front_multi_rows(self.source, front_header=bad)

    def test_current_payload_change_is_not_bootstrap_repinning(self):
        payloads = shadow.front_multi_payloads(); payloads[121] ^= 1
        current = shadow.front_multi_payloads()[121]
        header = self.header.replace(f'0x{current:016x}', f'0x{payloads[121]:016x}', 1)
        with self.assertRaisesRegex(AssertionError, 'oracle mismatch'):
            shadow.verify_front_multi_rows(self.source, front_header=header)
        self.assertEqual(len(shadow.verify_front_multi_rows(self.source, front_header=header, payloads=payloads)), 45)
        old = history.project_source('front-multi', 'src/render_mirror.c', self.source.encode()).decode()
        original_read = Path.read_text
        def current_header(path, *args, **kwargs):
            return header if path == ROOT / 'src' / shadow.FRONT_MULTI_HEADER else original_read(path, *args, **kwargs)
        with patch.object(shadow, 'front_multi_payloads', return_value=payloads), patch.object(Path, 'read_text', current_header):
            self.assertEqual(len(shadow.compare_previous_shadow_pins(self.source, old, 13)), 45)
        self.assertEqual(history.sha(history.project_source('front-multi', 'src/render_mirror.c', self.source.encode())),
                         '3dd046ceb4bb64467e6cfa6272d61c1a97576a836676fc6035081b30c7935961')

    def test_extracted_header_and_mutant_copy_contract(self):
        with tempfile.TemporaryDirectory(prefix='front-shadow-extract-') as directory:
            out = Path(directory)
            shadow.units(out, self.source)
            self.assertEqual((out / shadow.FRONT_MULTI_HEADER).read_text(), self.header)
            self.assertIn('#include "hd_front_multi_current.h"', (out / 'types.inc').read_text())
            # Exercise actual mutant creation/copy without a private bank.
            for name in ('reference.bin',): (out / name).write_bytes(b'')
            def check(folder, *args, **kwargs):
                self.assertEqual((folder / shadow.FRONT_MULTI_HEADER).read_text(), self.header)
                self.assertEqual(len(shadow.shadow_pin_rows((folder / 'types.inc').read_text())), 45)
                return {'expected_rejection': True}
            with patch.object(shadow, 'build_run', side_effect=check):
                self.assertEqual(len(shadow.mutants(out, self.source, [], '', '')), 6)


class FrontMultiHistoryBoundary(unittest.TestCase):
    def test_exact_two_hunks_and_newest_first_without_git(self):
        ledger = history.load('front-multi-source.json')
        self.assertEqual(ledger['integration_base'], 'b3efaf4eb87375ece2f1f1535bec98812cb819da')
        self.assertEqual(ledger['generated_header'], history.FRONT_MULTI_HEADER)
        self.assertEqual(set(ledger['files']), {'src/render_mirror.c'})
        pin = ledger['files']['src/render_mirror.c']
        self.assertEqual(len(pin['hunks']), 2)
        self.assertEqual(pin['hunks'][0]['before'], '')
        self.assertEqual(pin['hunks'][0]['after'], '#include "hd_front_multi_current.h"\n')
        before, after = pin['hunks'][1]['before'], pin['hunks'][1]['after']
        macros = re.findall(r'HD_FRONT_MULTI_CURRENT_PAYLOAD_\d+_HASH', after)
        self.assertEqual(macros, [f'HD_FRONT_MULTI_CURRENT_PAYLOAD_{80000+i}_HASH' for i in BOOTSTRAP])
        for i, macro in zip(BOOTSTRAP, macros): after = after.replace(macro, f'UINT64_C(0x{BOOTSTRAP[i]:016x})')
        self.assertEqual(before, after)
        raw = (ROOT / 'src/render_mirror.c').read_bytes()
        calls = []
        def recorded(function, label=None):
            def invoke(*args, **kwargs):
                result = function(*args, **kwargs)
                # Record completed inverses, so nested current-protron records
                # after its Sonic and normal-observer prerequisites.
                calls.append(label if label is not None else args[0])
                return result
            return invoke
        with patch.object(history.subprocess, 'check_output', side_effect=AssertionError('Git history forbidden')):
            with patch.object(history, '_project_source_once', side_effect=recorded(history._project_source_once)), \
                 patch.object(history, 'project_current_guided_source', side_effect=recorded(history.project_current_guided_source, 'current-guided')), \
                 patch.object(history, 'project_current_sonic_source', side_effect=recorded(history.project_current_sonic_source, 'current-sonic')), \
                 patch.object(history, 'project_current_protron_source', side_effect=recorded(history.project_current_protron_source, 'current-protron')):
                restored = history.project_source('storm', 'src/render_mirror.c', raw)
                self.assertEqual(tuple(calls), REVIEWED_SOURCE_INVERSES)
                self.assertEqual(history.sha(restored),
                    'c163d61c258454168b3d0c69660b4e41f708841552506a0b704ab674bc367a4a')
        # The Front hunk offsets belong to the Front-era blob, not today's
        # renderer. Strip reviewed newer layers before testing partial reverts.
        front = history.project_source('enemy-orb', 'src/render_mirror.c', raw)
        self.assertEqual(history.sha(front),
            '1019185ecff1de969355b60b179d43c7dd3aeb6fded2f84dc2edd40f74d85d1b')
        self.assertEqual(history.sha(history._project_source_once('front-multi', 'src/render_mirror.c', front)),
            '3dd046ceb4bb64467e6cfa6272d61c1a97576a836676fc6035081b30c7935961')
        for hunk in pin['hunks']:
            lines = front.splitlines(keepends=True); a, b = hunk['after_lines']
            self.assertEqual(b''.join(lines[a:b]), hunk['after'].encode())
            lines[a:b] = hunk['before'].encode().splitlines(keepends=True)
            with self.assertRaises(AssertionError): history._project_source_once('front-multi', 'src/render_mirror.c', b''.join(lines))
        for changed in (raw + b'\n', raw[:-1]):
            with self.assertRaises(AssertionError):
                history.project_source('front-multi', 'src/render_mirror.c', changed)
        for name in ('current-source-inventory.json', 'plasma-projectile-source.json', 'charge-body-source.json', 'p9-assets.json'):
            self.assertEqual(history.sha((history.FIXTURES / name).read_bytes()), history.PINS[name])
        with patch.object(Path, 'read_bytes', return_value=(history.FIXTURES / 'front-multi-source.json').read_bytes() + b' '):
            with self.assertRaises(AssertionError): history.load('front-multi-source.json')

    def test_exact_nine_outputs_and_source_binding(self):
        proof = history.verified_front_multi_current()
        self.assertEqual(set(proof['assets']), {history.FRONT_MULTI_SELECTION} | {history.FRONT_MULTI_ROOT + '/' + name for name in history.FRONT_MULTI_NAMES})
        self.assertEqual(len(proof['assets']), 9)
        self.assertEqual(len(proof['source_pngs']), 8)
        self.assertFalse(set(proof['assets']) & set(history.load('p9-assets.json')['verified_current_outputs']))
        self.assertNotIn(history.FRONT_MULTI_HEADER, history.load('current-source-inventory.json')['files'])


class FrontMultiCurrentGenerationBoundary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import sys
        sys.path.insert(0, str(ROOT / 'scripts'))
        import current_front_multi_compatibility as compat
        cls.compat = compat
        cls.temp = tempfile.TemporaryDirectory(prefix='front-multi-projection-')
        cls.root = Path(cls.temp.name)
        paths = compat.input_paths(ROOT) | {compat.MAPPING, compat.HEADER, 'packaging/current-production-validation.json', 'packaging/runtime-assets-v1.json'} | {compat.ROOT + '/' + name for name in history.FRONT_MULTI_NAMES}
        paths |= FRONT_CURRENT_SOURCES | history.sonic_runtime_input_paths(ROOT) | history.guided_runtime_input_paths(ROOT)
        if len(paths) != 54: raise AssertionError('unexpected historical Front Multi fixture closure')
        paths |= history.newshf_runtime_input_paths(ROOT)
        cls.baseline = {name: (ROOT / name).read_bytes() for name in paths}
        if set(cls.baseline) != paths: raise AssertionError('incomplete finite Front Multi fixture closure')

    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()

    def setUp(self):
        for name, raw in self.baseline.items():
            path = self.root / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw)

    def test_all_54_inputs_outputs_header_mapping_runtime_and_binding_reject_tampering(self):
        self.assertEqual(len(history.verified_front_multi_current(self.root)['assets']), 9)
        for name, raw in self.baseline.items():
            path = self.root / name
            try:
                path.write_bytes(raw + b'broken')
                with self.subTest(path=name), self.assertRaises((AssertionError, ValueError, OSError)):
                    history.verified_front_multi_current(self.root)
            finally: path.write_bytes(raw)

    def test_missing_current_source_inputs_are_rejected(self):
        self.assertEqual(len(history.verified_front_multi_current(self.root)['assets']), 9)
        for name in sorted(FRONT_CURRENT_SOURCES):
            path = self.root / name
            try:
                path.unlink()
                with self.subTest(path=name), self.assertRaises((AssertionError, ValueError, OSError)):
                    history.verified_front_multi_current(self.root)
            finally: path.write_bytes(self.baseline[name])

    def test_coherent_current_edit_changes_payload_without_repinning_history(self):
        import io
        from PIL import Image
        from verify_current_production import source_manifest_digest
        encoded = lambda value: (json.dumps(value, indent=2) + '\n').encode()
        before = history.verified_front_multi_current(self.root)
        frozen = {name: (history.FIXTURES / name).read_bytes() for name in history.PINS}
        selected = json.loads((self.root / self.compat.SELECTION).read_bytes())
        selected['version'] = 'front-multi-projection-current-edit'
        row = selected['resources'][0]; path = self.root / row['source_png']
        with Image.open(path) as old: frame = old.copy()
        r,g,b,a = frame.getpixel((48,56)); frame.putpixel((48,56), (r^1,g,b,a))
        buffer = io.BytesIO(); frame.save(buffer, format='PNG'); path.write_bytes(buffer.getvalue())
        row['source_sha256'] = history.sha(path.read_bytes())
        selected, blobs = self.compat.generate(self.root, encoded(selected))
        (self.root / self.compat.SELECTION).write_bytes(encoded(selected))
        mapping = json.loads((self.root / self.compat.MAPPING).read_bytes()); mapping['version'] = selected['version']
        runtime_path = self.root / 'packaging/runtime-assets-v1.json'; runtime = json.loads(runtime_path.read_bytes())
        runtime_rows = {row['destination']: row for row in runtime['files']}
        def rebind(row, raw):
            row.update(bytes=len(raw), sha256=history.sha(raw), git_blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest())
        pins = {}
        for row in mapping['files']:
            blob = blobs[row['identity']]; (self.root / row['source_path']).write_bytes(blob)
            row['sha256'] = history.sha(blob); rebind(runtime_rows[row['destination']], blob)
            pins[row['identity']] = f'{shadow.base.fnv(blob[28:]):016x}'
        (self.root / self.compat.MAPPING).write_bytes(encoded(mapping))
        header = self.root / self.compat.HEADER; header.write_bytes(self.compat.payload_header(pins))
        binding_path = self.root / 'packaging/current-production-validation.json'; binding = json.loads(binding_path.read_bytes())
        binding['source_sha256'][self.compat.HEADER] = history.sha(header.read_bytes())
        binding['production_source_manifest_sha256'] = source_manifest_digest(binding['source_sha256'])
        binding_path.write_bytes(encoded(binding)); rebind(runtime_rows['CURRENT-PRODUCTION-VALIDATION.json'], binding_path.read_bytes())
        runtime['source_revision']['current_production_source_manifest_sha256'] = binding['production_source_manifest_sha256']
        runtime_path.write_bytes(encoded(runtime))
        after = history.verified_front_multi_current(self.root)
        self.assertNotEqual(before['header_sha256'], after['header_sha256'])
        self.assertEqual(set(before['assets']), set(after['assets']))
        self.assertEqual(frozen, {name: (history.FIXTURES / name).read_bytes() for name in history.PINS})
        # Current output pins are intentional; a stale header or stale binding
        # must fail even when every HDA, mapping and selected PNG agrees.
        current_header = header.read_bytes(); header.write_bytes(self.baseline[self.compat.HEADER])
        with self.assertRaisesRegex(ValueError, 'payload pins'): history.verified_front_multi_current(self.root)
        header.write_bytes(current_header)
        binding_path.write_bytes(self.baseline['packaging/current-production-validation.json'])
        with self.assertRaisesRegex(AssertionError, 'production header binding'): history.verified_front_multi_current(self.root)

    def test_unrelated_binding_and_runtime_scope_changes_are_rejected(self):
        for case in ('header-binding', 'renderer-binding', 'source-digest', 'runtime-header', 'runtime-source', 'runtime-count'):
            self.setUp()
            binding_path = self.root / 'packaging/current-production-validation.json'
            binding = json.loads(binding_path.read_bytes())
            runtime_path = self.root / 'packaging/runtime-assets-v1.json'; runtime = json.loads(runtime_path.read_bytes())
            if case == 'header-binding': binding['source_sha256'][self.compat.HEADER] = '0'*64
            elif case == 'renderer-binding': binding['source_sha256']['src/render_mirror.c'] = '0'*64
            elif case == 'source-digest': binding['production_source_manifest_sha256'] = '0'*64
            elif case == 'runtime-header': next(row for row in runtime['files'] if row['destination'] == 'CURRENT-PRODUCTION-VALIDATION.json')['sha256'] = '0'*64
            elif case == 'runtime-source': runtime['source_revision']['current_production_source_manifest_sha256'] = '0'*64
            else: runtime['files'].append(copy.deepcopy(runtime['files'][0]))
            if case in ('header-binding', 'renderer-binding', 'source-digest'):
                binding_path.write_text(json.dumps(binding))
            else:
                runtime_path.write_text(json.dumps(runtime))
            reason = {'header-binding':'production header binding', 'renderer-binding':'renderer binding',
                      'source-digest':'source manifest digest', 'runtime-header':'runtime source binding',
                      'runtime-source':'runtime source digest', 'runtime-count':'destination scope'}[case]
            with self.subTest(case=case), self.assertRaisesRegex(AssertionError, reason):
                history.verified_front_multi_current(self.root)


if __name__ == '__main__': unittest.main()
