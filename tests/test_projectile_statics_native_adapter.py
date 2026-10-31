"""Focused pure tests. No native/compiler/game/registration producer invocation."""
from pathlib import Path
import ast
import hashlib
import importlib.util
import json
import os
import re
import struct
import tempfile
import types
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
TMP = os.environ.get('OPENTYRIAN_TEST_TMPDIR')
HELPER = HERE / 'projectile_statics_native_validation.py'
spec = importlib.util.spec_from_file_location('statics_pure_under_test', HELPER)
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)


class PinsAndLineage(unittest.TestCase):
    def test_import_inert_even_when_named_main(self):
        raw = HELPER.read_bytes()
        module = types.ModuleType('__main__')
        module.__file__ = str(HELPER)
        with mock.patch.object(Path, 'read_bytes', side_effect=AssertionError('Import read')), \
                mock.patch.object(Path, 'write_bytes', side_effect=AssertionError('Import write')), \
                mock.patch.object(os, 'system', side_effect=AssertionError('Import process')):
            exec(compile(raw, str(HELPER), 'exec'), module.__dict__)
        self.assertEqual(module.IDS, h.IDS)
        self.assertFalse(hasattr(module, 'main'))

    def test_no_process_or_producer_imports(self):
        tree = ast.parse(HELPER.read_text())
        names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names.update(item.name.split('.')[0] for item in node.names)
            if isinstance(node, ast.ImportFrom):
                names.add((node.module or '').split('.')[0])
        self.assertFalse(names & {'subprocess', 'ctypes', 'multiprocessing', 'register'})

    def test_fnv_empty(self):
        self.assertEqual(h.fnv1a64(b''), 0xcbf29ce484222325)

    def test_fnv_a(self):
        self.assertEqual(h.fnv1a64(b'a'), 0xaf63dc4c8601ec8c)

    def test_fnv_foobar(self):
        self.assertEqual(h.fnv1a64(b'foobar'), 0x85944171f73967e8)

    def test_byte_only_hash_primitives(self):
        for value in ('a', bytearray(b'a'), memoryview(b'a')):
            with self.subTest(type=type(value)):
                with self.assertRaises(AssertionError):
                    h.fnv1a64(value)
                with self.assertRaises(AssertionError):
                    h.SHA(value)

    def test_six_current_sources_and_two_inverses(self):
        old, derived = h.source_bundle(ROOT)
        self.assertEqual(len(old), 6)
        self.assertEqual({name: h.SHA(raw) for name, raw in old.items()}, h.SOURCE_PINS)
        gold = h.reverse_shim(derived)
        self.assertEqual(h.SHA(gold), h.GOLD_WRAPPER_SHA)
        original = h.gold_helper(ROOT).reverse_shim(gold)
        self.assertEqual(original, old['harness.c'])
        self.assertEqual(len(original), 262)
        self.assertEqual(h.SHA((ROOT / 'tests/projectile_gold_pulse_native_additions.c.inc').read_bytes()), h.GOLD_COMPANION_SHA)

    def test_wrapper_only_single_final_main_renamed(self):
        old, derived = h.source_bundle(ROOT)
        gold = h.gold_helper(ROOT).outer_shim(old['harness.c'])
        expected = gold.replace(b'int main(', b'int inherited_gold_dispatch(', 1) + h.TAIL
        self.assertEqual(derived, expected)
        self.assertEqual(derived.count(b'int main('), 1)
        self.assertEqual(derived.count(b'int inherited_gold_dispatch('), 1)

    def test_reverse_rejects_modified_body_and_tail(self):
        _, derived = h.source_bundle(ROOT)
        for bad in (derived + b'\n', derived[:-1], derived.replace(b'inherited_gold_dispatch', b'changed_gold_dispatch', 1),
                    derived.replace(b'--gold-pulse', b'--gold-pulsx', 1)):
            with self.assertRaises(AssertionError):
                h.reverse_shim(bad)

    def test_outer_rejects_non_gold_source(self):
        for raw in (b'int main(){}', b'', h.TAIL):
            with self.assertRaises(AssertionError):
                h.outer_shim(raw)

    def test_original_native_inputs_preserved(self):
        # Historical method retained with a portable explicit-data contract.
        # Actual DATA->stdin bytes are separately checked in preparation/fresh.
        blue = h.gold_helper(ROOT).blue_helper(ROOT)
        self.assertEqual(h.DATA_PINS, blue.DATA_SHA)
        self.assertEqual(blue.OLD_STDIN_SHA, '7dedf7066696fc278f5fbb8dfb1462e7b6ac290cb5d08ae5260a6cdabc1ecca7')
        self.assertEqual(blue.NEW_STDIN_SHA, 'a9739298f031cafbfefb3befd359750872f6caafe69ebf5c7cf948544713830b')
        with tempfile.TemporaryDirectory(prefix='statics-data-empty-', dir=TMP) as directory:
            with self.assertRaises(OSError):
                h.native_inputs(ROOT, Path(directory))
        signature = __import__('inspect').signature(h.native_inputs)
        self.assertTrue(all(parameter.default is parameter.empty for parameter in signature.parameters.values()))

    def test_source314_and_index_readonly_design_pins(self):
        # Historical name retained. Portable root may contain316 sources and
        # have no .git; exact9 old consumers replace private N/index reads.
        self.assertEqual(len(h.NATIVE_CONSUMERS), 9)
        before = {name: h.regular_bytes(h.installed_path(ROOT, name)) for name in h.NATIVE_CONSUMERS}
        self.assertEqual({name: h.SHA(raw) for name, raw in before.items()}, h.NATIVE_CONSUMERS)
        self.assertEqual(h.verify_native_consumers(ROOT), h.NATIVE_CONSUMERS)
        h.source_bundle(ROOT)
        self.assertEqual(before, {name: h.regular_bytes(h.installed_path(ROOT, name)) for name in h.NATIVE_CONSUMERS})
        self.assertEqual(h.SHA((HERE / 'projectile_statics_native_additions.c.inc').read_bytes()), h.STATICS_COMPANION_SHA)


class RegistrationAndPayload(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.metadata = h.registration(ROOT)
        cls.rgba = {i: h.registered_rgba(i, ROOT) for i in h.STATICS}

    def test_exact_independent_registration_and_backup(self):
        self.assertEqual(self.metadata['schema'], 'enemy-statics-fixed-registration-v1')
        self.assertEqual([m['selector'] for m in self.metadata['members']], [162, 260])
        self.assertEqual(self.metadata['coverage_sha256'], h.COVERAGE_SHA)
        self.assertEqual(set(self.metadata), {'schema', 'members', 'coverage_sha256', 'scope'})
        self.assertEqual(self.metadata['members'][0]['opaque255'], 12)
        self.assertEqual(self.metadata['members'][1]['opaque255'], 1)

    def test_actual_rgba_fulltile_support_soft_opaque_and_alpha0(self):
        for selector, rgba in self.rgba.items():
            pin = h.PINS[selector]
            stats = h.rgba_statistics(rgba, pin['native_mask'])
            for key in ('native_cells', 'nonzero', 'soft', 'opaque255', 'native_alpha0', 'high_ge200', 'low_1_199', 'zero'):
                self.assertEqual(stats[key], pin[key], (selector, key))
            self.assertEqual(stats['outside_nonzero'], 0)
            self.assertEqual(stats['alpha0_rgb_nonzero'], 0)
            self.assertEqual(stats['nonzero'] + (10752 - stats['nonzero']), 10752)

    def test_hda_memory_only_exact_header_and_independent_pins(self):
        for selector, rgba in self.rgba.items():
            raw = h.hda_payload(selector, rgba)
            self.assertEqual(len(raw), 43036)
            self.assertEqual(struct.unpack('<4s6I', raw[:28]), (b'HDR1', 1540000 + selector, 8, 12, 14, 0, 0))
            self.assertEqual(raw[28:], rgba)
            self.assertEqual(h.SHA(raw), h.PINS[selector]['hda_sha256'])
            self.assertTrue(h.validate_hda(raw, selector))

    def test_hda_rejects_each_header_field(self):
        for selector, rgba in self.rgba.items():
            raw = h.hda_payload(selector, rgba)
            for offset in (0, 4, 8, 12, 16, 20, 24):
                bad = bytearray(raw)
                bad[offset] ^= 1
                with self.subTest(selector=selector, offset=offset):
                    with self.assertRaises(AssertionError):
                        h.validate_hda(bytes(bad), selector)

    def test_hda_rejects_payload_short_trailing_and_swap(self):
        for selector, rgba in self.rgba.items():
            raw = h.hda_payload(selector, rgba)
            changed = bytearray(raw)
            changed[128] ^= 1
            for value in (raw[:-1], raw + b'!', bytes(changed)):
                with self.assertRaises(AssertionError):
                    h.validate_hda(value, selector)
            with self.assertRaises(AssertionError):
                h.validate_hda(raw, h.STATICS[1 - h.STATICS.index(selector)])

    def test_hda_rejects_reprocessed_rgba(self):
        for selector, rgba in self.rgba.items():
            changed = bytearray(rgba)
            changed[100] ^= 1
            with self.assertRaises(AssertionError):
                h.hda_payload(selector, bytes(changed))

    def test_statistics_detects_hidden_rgb_and_outside_support(self):
        raw = bytearray(43008)
        raw[0:4] = bytes((1, 2, 3, 0))
        raw[4:8] = bytes((9, 8, 7, 255))
        stats = h.rgba_statistics(bytes(raw), '0' * 168)
        self.assertEqual(stats['outside_nonzero'], 2)
        self.assertEqual(stats['alpha0_rgb_nonzero'], 1)
        self.assertEqual(stats['opaque255'], 1)

    def test_statistics_counts_native_alpha0_not_alpha_support(self):
        raw = bytearray(43008)
        raw[:4] = bytes((4, 5, 6, 1))
        stats = h.rgba_statistics(bytes(raw), '1' + '0' * 167)
        self.assertEqual(stats['native_cells'], 1)
        self.assertEqual(stats['native_alpha0'], 63)
        self.assertEqual(stats['soft'], 1)
        self.assertEqual(stats['low_1_199'], 1)

    def test_statistics_rejects_shape_and_mask(self):
        for rgba, mask in ((b'', '0' * 168), (bytes(43008), '0' * 167), (bytes(43008), 'x' * 168)):
            with self.assertRaises(AssertionError):
                h.rgba_statistics(rgba, mask)

    def test_regular_input_rejects_symlink_hardlink_and_oversize(self):
        with tempfile.TemporaryDirectory(prefix='pure-small-', dir=TMP) as directory:
            p = Path(directory) / 'one'
            p.write_bytes(b'ok')
            self.assertEqual(h.regular_bytes(p, 2), b'ok')
            with self.assertRaises(AssertionError):
                h.regular_bytes(p, 1)
            symlink = Path(directory) / 'symlink'
            symlink.symlink_to(p.name)
            with self.assertRaises(AssertionError):
                h.regular_bytes(symlink)
            link = Path(directory) / 'hardlink'
            os.link(p, link)
            for entry in (p, link):
                with self.assertRaises(AssertionError):
                    h.regular_bytes(entry)


class FiniteFixtures(unittest.TestCase):
    def setUp(self):
        self.raw = struct.pack('<4s6I', b'HDR1', 1540162, 8, 12, 14, 0, 0) + bytes(43008)

    def test_exact42_leaves390_newfiles(self):
        schema = h.fixture_schema()
        self.assertEqual(tuple(schema), h.PACK_NAMES)
        self.assertEqual(len(schema), 42)
        self.assertEqual(sum(map(len, schema.values())), 390)
        self.assertEqual(tuple(schema)[30:], tuple(prefix + str(i) for i in h.STATICS for prefix in ('magic', 'density', 'width', 'height', 'anchorx', 'anchory')))
        self.assertEqual(set(schema['valid']), set(h.IDS))

    def test_singleton_and_oldonly_membership(self):
        schema = h.fixture_schema()
        self.assertEqual(schema['only162'], (162,))
        self.assertEqual(schema['only260'], (260,))
        self.assertEqual(schema['old-only'], h.IDS[:8])

    def test_every_missing_independently_preserves_other_nine(self):
        schema = h.fixture_schema()
        for selector in h.IDS:
            self.assertEqual(schema['missing' + str(selector)], tuple(i for i in h.IDS if i != selector))
            self.assertIsNone(h.fixture_bytes(self.raw, selector, 'missing' + str(selector)))

    def test_payload_corruption_is_single_byte_only(self):
        for selector in h.IDS:
            raw = h.fixture_bytes(self.raw, selector, 'bad' + str(selector))
            self.assertEqual([j for j, (a, b) in enumerate(zip(raw, self.raw)) if a != b], [128])
            self.assertEqual(raw[:28], self.raw[:28])

    def test_malformed_headers_are_fixed_independent_leaves(self):
        fields = (('header', 4, 1540163), ('magic', 0, None), ('density', 8, 4), ('width', 12, 11),
                  ('height', 16, 13), ('anchorx', 20, 1), ('anchory', 24, 1))
        for selector in h.STATICS:
            for prefix, offset, value in fields:
                raw = h.fixture_bytes(self.raw, selector, prefix + str(selector))
                self.assertEqual(raw[28:], self.raw[28:])
                if value is not None:
                    self.assertEqual(struct.unpack_from('<I', raw, offset)[0], value)
                else:
                    self.assertEqual(raw[0], self.raw[0] ^ 1)
                other = h.STATICS[1 - h.STATICS.index(selector)]
                self.assertEqual(h.fixture_bytes(self.raw, other, prefix + str(selector)), self.raw)

    def test_short_and_trailing_exact_bytes(self):
        for selector in h.STATICS:
            self.assertEqual(h.fixture_bytes(self.raw, selector, 'short' + str(selector)), self.raw[:-1])
            self.assertEqual(h.fixture_bytes(self.raw, selector, 'trailing' + str(selector)), self.raw + b'!')

    def test_inputs_not_mutated(self):
        before = h.SHA(self.raw)
        for leaf in h.PACK_NAMES:
            for selector in h.IDS:
                result = h.fixture_bytes(self.raw, selector, leaf)
                self.assertTrue(result is None or type(result) is bytes)
        self.assertEqual(h.SHA(self.raw), before)

    def test_fixture_rejects_unsupported_or_nonbytes(self):
        for raw, selector, leaf in ((self.raw, 92, 'valid'), (self.raw, 162, '../valid'), (bytearray(self.raw), 162, 'valid'),
                                    (self.raw[:-1], 162, 'valid'), (self.raw, True, 'valid')):
            with self.assertRaises(AssertionError):
                h.fixture_bytes(raw, selector, leaf)

    def test_fixture_pipeline_preserves_synthetic335_byte_exact(self):
        # The prior producer is mocked: no actual fixture materialization and
        # no inherited actual fixture producer is called by this pure test.
        metadata = h.registration(ROOT)
        payloads = {i: self.raw for i in h.IDS}
        for selector in h.STATICS:
            payloads[selector] = h.hda_payload(selector, h.registered_rgba(selector, ROOT))
        old = {f'old-synthetic/{k}': f'original-{k}'.encode('ascii') for k in range(335)}
        old_before = dict(old)
        gold = types.SimpleNamespace(IDS=h.IDS[:8],
            registration=mock.Mock(return_value={'synthetic': True}),
            fixture_payloads=mock.Mock(return_value=old))
        with mock.patch.object(h, 'gold_helper', return_value=gold):
            result = h.fixture_payloads(ROOT, payloads, metadata)
        self.assertEqual(len(result), 725)
        self.assertEqual(old, old_before)
        self.assertEqual({key: result[key] for key in old}, old_before)
        new = {key: value for key, value in result.items() if key not in old}
        self.assertEqual(len(new), 390)
        self.assertTrue(all(key.startswith('statics-packs/') for key in new))
        gold.fixture_payloads.assert_called_once_with(ROOT, {i: payloads[i] for i in h.IDS[:8]}, {'synthetic': True})

    def test_fixture_pipeline_rejects_missing_inputs_and_metadata_drift(self):
        metadata = h.registration(ROOT)
        with self.assertRaises(AssertionError):
            h.fixture_payloads(ROOT, {}, metadata)
        with self.assertRaises(AssertionError):
            h.fixture_payloads(ROOT, {i: self.raw for i in h.IDS}, dict(metadata, schema='changed'))

    def test_names_are_finite_and_collisionfree(self):
        self.assertEqual(len(set(h.HDA_NAMES.values())), 10)
        self.assertTrue(all('/' not in name and '..' not in name for name in h.HDA_NAMES.values()))
        paths = [f'statics-packs/{leaf}/{h.HDA_NAMES[i]}' for leaf, members in h.fixture_schema().items() for i in members]
        self.assertEqual(len(paths), len(set(paths)))
        self.assertTrue(all(not Path(p).is_absolute() and '..' not in Path(p).parts for p in paths))


class CompanionSourceContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.code = (HERE / 'projectile_statics_native_additions.c.inc').read_text()

    def test_finite_ids_roots_and_unsigned_bits(self):
        ids = re.search(r'statics_ids\[10\]=\{([^}]+)\}', self.code)
        self.assertEqual(tuple(map(int, ids[1].split(','))), h.IDS)
        roots = re.search(r'statics_root_names\[\]=\{([^}]+)\}', self.code)
        self.assertEqual(tuple(re.findall(r'"([^"\\]+)"', roots[1])), h.PACK_NAMES)
        self.assertIn('return 1u<<k', self.code)
        self.assertNotRegex(self.code, r'Uint8\s+(?:bits|member|used_members)\b')
        self.assertIn('global_projectile91_owner[n]<=1&&global_projectile91_foreign[n]<=1', self.code)

    def test_groups_match_independent_branch_arithmetic(self):
        expected = (
            ('full_tile_native_patterns', 2*2), ('full_tile_hd_underlay', 2), ('bounds', 2*(7+4)),
            ('pair_orders_zero_isolation', ((10*9//2)-(8*7//2))*2),
            ('all10_same_origin_dependency', 10*2), ('all10_two_row_dependency', 10*2),
            ('missing_bad', 10*2*2), ('singletons_oldonly', 2+2), ('malformed_headers_lengths', 2*9),
            ('readiness_root_epochs', 2+2), ('unused_memory_payload_ready', 2*2*2),
            ('palette_admission_shared', 12*2), ('palette_direct_final_cache', (5+11)*2+2*2+2),
            ('palette_composite_preflight', 12), ('used_resource_direct_final_cache', 2*13*2),
            ('source_scope_direct_final_cache', 12*2), ('layout_direct_final_cache', 2*8*2),
            ('callbacks', 2*6), ('cold_warm_scope', 2*11*2), ('Talon_transfer', 2*2),
            ('Talon_underlay_direct', 2*2*2), ('lifecycle', 2*2+3),
            ('later_native_final_writers', 2*4), ('fade_high_bits', 2*4))
        observed = tuple((name, int(count)) for name, count in re.findall(r'statics_group\("([a-zA-Z0-9_]+)",b,(\d+)\)', self.code))
        self.assertEqual(observed, expected)
        self.assertEqual(h.GROUPS, expected)
        self.assertEqual(len(observed), 24)

    def test_fixed_two_row_sentinels_and_zero_common(self):
        self.assertIn('40+48*(int)(k%5)', self.code)
        self.assertIn('60+40*(int)(k/5)', self.code)
        self.assertIn('alpha_common==0&&native_common==0', self.code)
        self.assertNotRegex(self.code, r'(?:alpha_common|native_common)\s*>\s*0')
        self.assertNotIn('common==100', self.code)
        self.assertNotRegex(self.code, r'40\s*\+\s*\(?int\)?k\s*\*\s*28')
        self.assertTrue('if((first==162&&last==61)||(first==61&&last==162))CHECK(intersection==0)' in self.code, 'Explicit162/61 zero-isolation branch')

    def test_fulltile_metadata_and_actual_callback_counts(self):
        self.assertIn('ay<112', self.code)
        self.assertIn('ax<96', self.code)
        self.assertIn('cells==24&&soft==1380&&opaque==12&&clear==9360&&zero_native==144', self.code)
        self.assertIn('cells==86&&soft==5216&&opaque==1&&clear==5535&&zero_native==287', self.code)
        self.assertIn('global_projectile91_call.left==(s?86u:24u)', self.code)
        for field in ('initialized', 'valid', 'bank', 'index', 'w', 'h', 'anchor_x', 'anchor_y', 'density', 'rgba'):
            self.assertRegex(self.code, r'a->' + field + r'\b')

    def test_exact_talon_predictions_and_original_resource_retirement(self):
        for text in ('expected[2]={526,1122}', 'soft_expected[2]={521,1122}', 'zeros[2]={35,6}',
                     'wx[2]={58,59}', 'wy[2]={36,17}', '{{244,177,55,254},{231,62,14,253}}',
                     'copied>0', 'global_talon_foreign[wn]', 'if(cached)global_projectile91_check_cache();else finish()'):
            self.assertIn(text, self.code)
        self.assertIn('statics_asset(id)->rgba[100]^=1', self.code)
        self.assertIn('global_projectile91_used_members==statics_bit(id)', self.code)

    def test_positive_fade_and_legitimate_complete_owner_revocation(self):
        for text in ('render_mirror_pixel(VGAScreenSeg,p,src[j],MIRROR_NORMAL)',
                     'for(unsigned i=0;i<10752;i++)CHECK(!global_projectile91_owner[',
                     'CHECK(global_projectile91_fade_step_valid(7));render_mirror_fade_step(7)',
                     'v+(0-v)/7', 'statics_output_expected(want,110,80)'):
            self.assertTrue(text in self.code, text)
        self.assertNotIn('if(!global_projectile91_cached)', self.code)

    def test_no_legacy_redefinition_or_animation_fixture(self):
        self.assertIsNone(re.search(r'(?m)^static\s+[^;\n{}(=]*\b(?:gold|blue)_[a-zA-Z0-9_]+\s*[=(\[]', self.code), 'Legacy declaration in new companion')
        self.assertNotRegex(self.code, r'static[^;\n]*statics_animation\s*\(')
        self.assertNotIn('enemyShot[0].animate=', self.code)
        self.assertIn('No controlled animation/emission fixture', self.code)
        self.assertIn('blue_draw_bank(id,x,y,spriteSheet8)', self.code)
        self.assertIn('blue_player_classic(id)', self.code)


class StdoutContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Literal expected stdout, not a historical process/file consumer.
        cls.old = {'inherited107_stdout': b'PASS inherited91 native lifecycle: 37 cases 81611 assertions\n145_TO_TALON copied=376 cached=0\n145_TO_TALON copied=376 cached=1\nPASS shared145 native lifecycle: 70 new cases 141992 new assertions; internal8 only; not gameplay/full build\n', 'inherited61_stdout': b'61_TO_TALON copied=267 cached=0\n61_TO_TALON copied=267 cached=1\nPASS shared61 native lifecycle: 157 cases 822291 assertions; internal8 only; not gameplay/full build\n', 'new_blue_stdout': b'BLUE101_ZERO_NATIVE pattern=0 draw=384 finish=384 cache=384\nBLUE101_ZERO_NATIVE pattern=1 draw=384 finish=384 cache=384\nBLUE101_ZERO_HD prior=120 draw=384 finish=384 cache=384\nBLUE_TO_TALON selector=101 copied=1756 soft=1721 cached=0\nBLUE_TO_TALON selector=101 copied=1756 soft=1721 cached=1\nBLUE_TO_TALON selector=120 copied=1864 soft=1864 cached=0\nBLUE_TO_TALON selector=120 copied=1864 soft=1864 cached=1\nBLUE_TO_TALON selector=139 copied=1481 soft=1454 cached=0\nBLUE_TO_TALON selector=139 copied=1481 soft=1454 cached=1\nPASS blue triplet native lifecycle: 365 cases 11162937 assertions; internal8 only; not gameplay/full build\n', 'gold251_stdout': b'GOLD_GROUP name=full_tile_native_patterns cases=4\nGOLD_GROUP name=bounds cases=18\nGOLD_GROUP name=pair_orders cases=26\nGOLD_GROUP name=all8_early_dependency cases=16\nGOLD_GROUP name=missing_bad cases=32\nGOLD_GROUP name=singletons_oldonly cases=4\nGOLD_GROUP name=malformed_gold cases=6\nGOLD_GROUP name=unused_memory_payload_ready cases=8\nGOLD_GROUP name=palette cases=40\nGOLD_GROUP name=used_resource_shared cases=64\nGOLD_GROUP name=callbacks cases=8\nGOLD_GROUP name=cold_scope cases=10\nGOLD_TO_TALON selector=168 copied=974 soft=974 alpha0=86 cached=0\nGOLD_TO_TALON selector=168 copied=974 soft=974 alpha0=86 cached=1\nGOLD_TO_TALON selector=169 copied=735 soft=735 alpha0=85 cached=0\nGOLD_TO_TALON selector=169 copied=735 soft=735 alpha0=85 cached=1\nGOLD_GROUP name=Talon_transfer cases=4\nGOLD_GROUP name=lifecycle cases=5\nGOLD_GROUP name=controlled_animation cases=6\nPASS gold pulse native lifecycle: 251 cases 38046959 assertions; internal8 only; not gameplay/full build\n'}

    def test_original880_bytes_and_counts(self):
        result = h.verify_legacy_stdout(self.old)
        self.assertEqual(result['cases'], 880)
        self.assertEqual(result['assertions'], 50255790)
        self.assertEqual(result['process_cases'], [107, 157, 365, 251])

    def test_originals_reject_crlf_and_missing_lf(self):
        for key in self.old:
            for value in (self.old[key].replace(b'\n', b'\r\n'), self.old[key][:-1], self.old[key] + b'\n'):
                actual = dict(self.old, **{key: value})
                with self.assertRaises(AssertionError):
                    h.verify_legacy_stdout(actual)

    def test_originals_reject_text_keys_and_zeroed_summary(self):
        for key in self.old:
            actual = dict(self.old, **{key: self.old[key].decode('ascii')})
            with self.assertRaises(AssertionError):
                h.verify_legacy_stdout(actual)
        with self.assertRaises(AssertionError):
            h.verify_legacy_stdout({**self.old, 'other': b''})
        actual = dict(self.old)
        actual.pop('gold251_stdout')
        with self.assertRaises(AssertionError):
            h.verify_legacy_stdout(actual)

    def test_strict_lines_never_normalizes(self):
        self.assertEqual(h.strict_stdout_lines(b'one\ntwo\n'), ['one', 'two'])
        for value in ('one\n', b'one\r\n', b'one', b'one\x00\n', b''):
            with self.assertRaises(AssertionError):
                h.strict_stdout_lines(value)
        with self.assertRaises(UnicodeDecodeError):
            h.strict_stdout_lines(b'\xff\n')

    @staticmethod
    def statics_stdout(assertions=91342858):
        lines = []
        for name, count in h.GROUPS:
            if name == 'Talon_transfer':
                for selector in h.STATICS:
                    copied, soft, zero = h.TRANSFER[selector]
                    for cached in (0, 1):
                        lines.append(f'STATICS_TO_TALON selector={selector} copied={copied} soft={soft} alpha0={zero} cached={cached}')
            lines.append(f'STATICS_GROUP name={name} cases={count}')
        lines.append(f'PASS enemy statics native lifecycle: {sum(n for _, n in h.GROUPS)} cases {assertions} assertions; internal8 only; not gameplay/full build')
        return ('\n'.join(lines) + '\n').encode('ascii')

    def test_new_parser_frozen_schema_and_positive_assertions(self):
        result = h.parse_statics_stdout(self.statics_stdout())
        self.assertEqual(result['cases'], sum(n for _, n in h.GROUPS))
        self.assertEqual(result['assertions'], 91342858)
        self.assertEqual(len(result['groups']), 24)
        self.assertEqual(len(result['transfers']), 4)
        for n in (0, -1, 123456):
            with self.assertRaises(AssertionError):
                h.parse_statics_stdout(self.statics_stdout(n))

    def test_new_parser_rejects_case_count_group_order_and_duplicates(self):
        raw = self.statics_stdout()
        first, second, tail = raw.split(b'\n', 2)
        for bad in (second+b'\n'+first+b'\n'+tail, first+b'\n'+raw,
                    raw.replace(b'cases=4', b'cases=5', 1), raw.replace(f': {sum(n for _, n in h.GROUPS)} cases'.encode(), b': 1 cases', 1)):
            with self.assertRaises(AssertionError):
                h.parse_statics_stdout(bad)

    def test_new_parser_rejects_every_transfer_field_mutation(self):
        raw = self.statics_stdout()
        for before, after in ((b'selector=162', b'selector=260'), (b'copied=526', b'copied=0'),
                              (b'soft=521', b'soft=526'), (b'alpha0=35', b'alpha0=0'), (b'cached=0', b'cached=2')):
            with self.assertRaises(AssertionError):
                h.parse_statics_stdout(raw.replace(before, after, 1))

    def test_new_parser_rejects_text_crlf_blank_extra_and_missing_lf(self):
        raw = self.statics_stdout()
        for bad in (raw.decode('ascii'), raw.replace(b'\n', b'\r\n'), raw+b'\n', raw[:-1], raw+b'anything\n'):
            with self.assertRaises(AssertionError):
                h.parse_statics_stdout(bad)


class PortableBoundaryContracts(unittest.TestCase):
    def test_no_external_defaults_receipts_or_process_entry(self):
        source = HELPER.read_text()
        for forbidden in ('/workspace/', 'ART_ROOT', 'BACKUP_PATH', 'backup_library_file_id',
                          'registration-receipt.json', 'native-reference-evidence.json', 'def main(', "if __name__"):
            self.assertNotIn(forbidden, source)
        import inspect
        for name in ('registration', 'registered_hdas', 'registered_rgba', 'native_inputs', 'source_bundle'):
            self.assertTrue(all(p.default is p.empty for p in inspect.signature(getattr(h, name)).parameters.values()))

    def test_c_companion_actual_exercised_bytes_preserved(self):
        self.assertEqual(h.SHA((HERE / 'projectile_statics_native_additions.c.inc').read_bytes()),
                         '6886018f5bc62216ae48797ae888fbd169fcdbee3d42107856872b536d4e866e')

    def test_installed_paths_reject_traversal_and_ambiguity(self):
        for relative in ('../escape', '/absolute', './tests/x', 'tests//x', 'tests/../x',
                         'tests/./x', 'tests\\x', 'tests/x\x00', ''):
            with self.subTest(relative=relative), self.assertRaises(AssertionError):
                h.installed_path(ROOT, relative)

    def test_installed_paths_reject_parent_symlink(self):
        with tempfile.TemporaryDirectory(prefix='statics-links-', dir=TMP) as directory:
            base = Path(directory)
            (base / 'real').mkdir()
            (base / 'real/file').write_bytes(b'x')
            (base / 'alias').symlink_to('real', target_is_directory=True)
            with self.assertRaises(AssertionError):
                h.installed_path(base, 'alias/file')
            with self.assertRaises(AssertionError):
                h.regular_bytes(base / 'alias/file')
            with self.assertRaises(AssertionError):
                h.installed_path(base / 'alias', 'file')

    def test_json_duplicate_and_nonfinite_rejected(self):
        for raw in (b'{"schema":1,"schema":2}', b'{"x":NaN}', b'{"x":Infinity}', b'{"x":-Infinity}'):
            with mock.patch.object(h, 'regular_bytes', return_value=raw), self.assertRaises(AssertionError):
                h.pinned_json('synthetic', h.SHA(raw))

    def test_registration_unknown_duplicate_shape_and_bool_rejected(self):
        import copy
        good = json.loads((ROOT / h.COVERAGE_PATH).read_bytes())
        malformed = []
        value = copy.deepcopy(good); value['extra'] = 1; malformed.append(value)
        value = copy.deepcopy(good); value['members']['163'] = value['members']['162']; malformed.append(value)
        value = copy.deepcopy(good); value['members']['260']['pixels']['opaque255'] = True; malformed.append(value)
        value = copy.deepcopy(good); value['members']['162']['max_alpha_matrix'][0][0] = False; malformed.append(value)
        value = copy.deepcopy(good); value['members']['162']['extra'] = 0; malformed.append(value)
        for value in malformed:
            with mock.patch.object(h, 'pinned_json', return_value=value), self.assertRaises(AssertionError):
                h.registration(ROOT)

    def test_installed_registration_and_hda_require_current_root(self):
        with tempfile.TemporaryDirectory(prefix='statics-empty-', dir=TMP) as directory:
            for function in (h.registration, h.registered_hdas, h.source_bundle, h.gold_helper):
                with self.subTest(function=function.__name__), self.assertRaises(OSError):
                    function(Path(directory))

    def test_registered_hdas_equal_installed_bytes_not_regenerated(self):
        actual = h.registered_hdas(ROOT)
        self.assertEqual(set(actual), {162, 260})
        for selector, raw in actual.items():
            self.assertEqual(raw, (ROOT / h.ASSET_DIRECTORY / h.HDA_NAMES[selector]).read_bytes())
            self.assertEqual(raw[28:], h.registered_rgba(selector, ROOT))

    def test_opaque255_cannot_be_silently_all_soft(self):
        for selector, opaque in ((162, 12), (260, 1)):
            rgba = h.registered_rgba(selector, ROOT)
            self.assertEqual(max(rgba[3::4]), 255)
            self.assertEqual(rgba[3::4].count(255), opaque)
            changed = bytearray(rgba)
            offset = next(i for i in range(3, len(changed), 4) if changed[i] == 255)
            changed[offset] = 254
            stats = h.rgba_statistics(bytes(changed), h.PINS[selector]['native_mask'])
            self.assertEqual(stats['opaque255'], opaque - 1)
            self.assertEqual(stats['soft'], h.PINS[selector]['soft'] + 1)
            with self.assertRaises(AssertionError):
                h.hda_payload(selector, bytes(changed))

    def test_finite_unsigned_ten_member_masks_no_byte_truncation(self):
        bits = {selector: 1 << k for k, selector in enumerate(h.IDS)}
        self.assertEqual((bits[162], bits[260], bits[162] | bits[260]), (256, 512, 768))
        self.assertEqual(sum(bits.values()), 1023)
        for selector in h.IDS:
            self.assertEqual(1023 & ~bits[selector], sum(value for key, value in bits.items() if key != selector))
        code = (HERE / 'projectile_statics_native_additions.c.inc').read_text()
        self.assertIn('global_projectile91_used_members==1023u', code)
        self.assertIn('global_projectile91_member(id)==(s?512u:256u)', code)
        self.assertNotRegex(code, r'global_projectile91_used_members\s*&\s*255(?:u)?\b')

    def test_native_stdout_29_lines_exact_assertion_and_hash(self):
        raw = StdoutContracts.statics_stdout()
        self.assertEqual(len(h.strict_stdout_lines(raw)), 29)
        self.assertEqual((h.SHA(raw), len(raw)), h.STATICS_STDOUT_PIN)
        self.assertEqual(h.parse_statics_stdout(raw)['assertions'], 91342858)
        for number in (1, 91342857, 91342859):
            with self.assertRaises(AssertionError):
                h.parse_statics_stdout(StdoutContracts.statics_stdout(number))

    def test_fixture_metadata_duplicate_selector_rejected(self):
        metadata = h.registration(ROOT)
        payloads = {selector: bytes(43036) for selector in h.IDS}
        for selector in h.STATICS:
            payloads[selector] = h.hda_payload(selector, h.registered_rgba(selector, ROOT))
        value = dict(metadata, members=metadata['members'] + [metadata['members'][0]])
        with self.assertRaises(AssertionError):
            h.fixture_payloads(ROOT, payloads, value)
        value = dict(metadata, coverage_sha256='0' * 64)
        with self.assertRaises(AssertionError):
            h.fixture_payloads(ROOT, payloads, value)

    def test_registration_rejects_wrong_mode_size_and_multiframe(self):
        import io
        from PIL import Image
        malformed = []
        for mode, size in (('RGB', (96, 112)), ('RGBA', (95, 112))):
            output = io.BytesIO(); Image.new(mode, size).save(output, format='PNG'); malformed.append(output.getvalue())
        output = io.BytesIO(); first = Image.new('RGBA', (96, 112)); second = Image.new('RGBA', (96, 112), (1, 2, 3, 4))
        first.save(output, format='PNG', save_all=True, append_images=[second]); malformed.append(output.getvalue())
        for raw in malformed:
            with mock.patch.object(h, 'regular_bytes', return_value=raw), \
                    mock.patch.object(h, 'SHA', return_value=h.PINS[162]['png_sha256']), self.assertRaises(AssertionError):
                h.registered_rgba(162, ROOT)


if __name__ == '__main__':
    unittest.main(verbosity=2)
