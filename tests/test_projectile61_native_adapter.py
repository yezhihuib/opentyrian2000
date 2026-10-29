"""Pure adapter contracts only; these do not execute native rendering."""
import ast
import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('projectile61_native_validation', HERE / 'projectile61_native_validation.py')
D = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(D)


class Projectile61NativeAdapter(unittest.TestCase):
    def test_budget_edges(self):
        self.assertEqual(D.PEAK + D.RESERVE, 396361728)
        self.assertTrue(D.budget_ok(D.PEAK, D.RESERVE))
        self.assertFalse(D.budget_ok(D.PEAK + 1, D.RESERVE))
        self.assertFalse(D.budget_ok(0, D.RESERVE - 1))
        self.assertTrue(D.budget_ok(D.FINAL_CAP, D.RESERVE, True))
        self.assertFalse(D.budget_ok(D.FINAL_CAP + 1, D.RESERVE, True))

    def test_dependency_continuations_and_escaped_names(self):
        self.assertEqual(D.dependency_tokens('obj/a.o: src/a.c \\\n /root/a\\ b.h\n'), ['src/a.c', '/root/a b.h'])
        with self.assertRaises(AssertionError):
            D.dependency_tokens('not a dependency rule')

    def test_parent_environment_unchanged_and_control_flags_removed(self):
        parent = {'PATH': '/usr/bin', 'AIRCRAFT170_DIFFERENTIAL_POSE': '3',
                  'PROJECTILE145_NATURAL_TICK': '1', 'OT_CONTROL': 'poison',
                  'TYRIAN_CYAN_BORROW': 'poison', 'SHARED_CONTROL': 'poison'}
        snapshot = dict(parent)
        env = D.sanitized_env(parent, Path('/s'), Path('/t'))
        self.assertEqual(parent, snapshot)
        self.assertEqual(env['PATH'], '/usr/bin')
        self.assertFalse(any(k.startswith(('AIRCRAFT', 'PROJECTILE', 'OT_', 'SHARED', 'TYRIAN_CYAN_BORROW')) for k in env))
        self.assertEqual(env['ASAN_OPTIONS'], 'detect_leaks=0:halt_on_error=1')
        self.assertEqual(env['TMPDIR'], '/t')

    def test_native_stdout_nonvacuity(self):
        output = ('61_TO_TALON copied=7 cached=0\n61_TO_TALON copied=9 cached=1\n'
                  'PASS shared61 native lifecycle: 157 cases 11 assertions; internal8 only; not gameplay/full build\n')
        self.assertEqual(D.parse_native61_stdout(output), (157, 11))
        for invalid in (output.replace('copied=7', 'copied=0'),
                        output.replace('cached=1', 'cached=0'),
                        output.replace('157 cases', '156 cases'),
                        output + output, output.splitlines()[-1]):
            with self.assertRaises(AssertionError):
                D.parse_native61_stdout(invalid)

    def test_exact_inherited_harness_include_and_separate_entry(self):
        self.assertEqual(D.WRAPPER.count('#include "inherited145_harness.c"'), 1)
        self.assertIn('#define main inherited145_main', D.WRAPPER)
        self.assertIn('return inherited145_main(argc-1,argv+1)', D.WRAPPER)
        self.assertIn('argc==7', D.WRAPPER)
        self.assertIn('argc==10', D.WRAPPER)
        self.assertIn('CHECK(xn==32404)', D.WRAPPER)
        self.assertIn('CHECK(fgetc(stdin)==EOF)', D.WRAPPER)
        self.assertEqual(D.LEGACY_SHA, '8925fb11215446339f067124fa7223ec48dc7c86459e303d3803477773b2d9ac')

    def test_exact_rebuild_scope(self):
        self.assertEqual(D.REBUILD, {'render_mirror', 'entity_draw', 'tyrian2', 'opentyr'})
        self.assertEqual(D.CHANGED, {'render_mirror.c', 'global_projectile91_mirror.inc', 'entity_draw.c', 'tyrian2.c'})
        self.assertEqual(D.ADDED, {'enemy_projectile61_mirror.inc', 'current_projectile61_payload_pins.h'})

    def test_frozen_baseline_failure_not_relabelled(self):
        source = (HERE / 'projectile61_native_validation.py').read_text()
        self.assertIn("fresh['status']=='FAIL_BINDING_RETAINED'", source)
        self.assertIn('ACCEPTED_FUNCTIONAL_RESULTS_WITH_RAW_INDEX_STAT_CACHE_DEVIATION', source)
        self.assertIn("(q/'inherited107.stdout').read_text()==fresh['native_stdout']", source)
        self.assertIn("hashlib.sha256(old_stdin).hexdigest()==fresh['stdin_sha256']", source)

    def test_after_receipt_budget_and_actual_dependency_guards(self):
        source = (HERE / 'projectile61_native_validation.py').read_text()
        ast.parse(source)
        self.assertIn('FAIL_BUDGET_AFTER_RECEIPT', source)
        self.assertIn('used+4096,free-4096,True', source)
        self.assertIn("len(report['fresh_dependency_files_sha256'])==1", source)
        self.assertIn("current_headers[str(dp)]==h", source)
        self.assertIn("SHA(dep)==pin['sha256']", source)
        self.assertIn('writer_errors', source)
        self.assertIn("SHA(obj)==entry['sha256']", source)
        self.assertIn("actual==entry['dependency_sha256']", source)
        self.assertIn("arg.replace(str(a.reuse_proof),str(q))", source)
        self.assertIn("[0,0,0,-15]", source)

    def test_companion_has_real_mixed_and_transfer_calls(self):
        source = (HERE / 'projectile61_native_additions.c.inc').read_text()
        for text in ('global_projectile91_used_members==7u', 'CHECK(common>0',
                     'CHECK(copied>0)', 'talon_tile();', '61_TO_TALON copied=%u cached=%u',
                     'oracle61(110,80,under,true)', 'christmas_bytes==32404',
                     'global_projectile91_used_colors[113]', 'valid_root=only61'):
            self.assertIn(text, source)
        self.assertNotIn('memset(global_projectile91_owner', source)

    def test_fixed_transfer_geometry_is_not_runtime_search(self):
        source = (HERE / 'projectile61_native_additions.c.inc').read_text()
        transfer = source.split('static void transfer61(void)', 1)[1].split('static void lifecycle61(', 1)[0]
        self.assertIn('blit_sprite2x2(classic,107,78,spriteSheet9,233)', transfer)
        self.assertIn('blit_sprite2x2(game_screen,107,78,spriteSheet9,233)', transfer)
        self.assertNotIn('108,78', transfer)
        self.assertIn('CHECK(copied>0)', transfer)
        self.assertIn('copied==267&&soft_copied==231', transfer)
        self.assertIn('*at(canvas,960,648)==witness_rgb', transfer)
        self.assertIn('*at(output,960-24*8,648)==witness_rgb', transfer)


if __name__ == '__main__':
    unittest.main()
