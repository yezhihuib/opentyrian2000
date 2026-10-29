#!/usr/bin/env python3
"""Pure tick150 triple source contracts; no compiler/game/build invocation.

Reads current61 and reconstructs the exact qualified308-source baseline through
the frozen61 inverse. No sibling checkout or Git history is needed at test time. These tests do not
constitute native runtime or differential evidence.
"""
from pathlib import Path
import ast
import importlib.util
import os
import re
import sys
import unittest

HERE = Path(__file__).resolve().parent
DEFAULT_ROOT = HERE.parent
ROOT = Path(os.environ.get('PROJECTILE61_STATIC_ROOT', str(DEFAULT_ROOT)))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'tests'))
spec = importlib.util.spec_from_file_location('projectile61_gameplay_differential_under_test', HERE / 'projectile61_gameplay_differential.py')
diff = importlib.util.module_from_spec(spec)
spec.loader.exec_module(diff)
import projectile61_gameplay_instrumentation as instr
from global_talon_reconstruction import extract
import projectile61_projection as source_projection


def compact(text):
    return re.sub(r'\s+', '', text)


class Projectile61DifferentialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.current = {name: (ROOT / 'src' / name).read_text() for name in sorted(instr.REQUIRED | instr.OPTIONAL)}
        cls.observed = instr.instrument(cls.current)
        # Strict61 inverse, then independently bind all three308-stage bytes.
        # sprite.c is unmodified, but is not accepted as an arbitrary live input.
        baseline = {}
        expected = source_projection.ledger()['base_source_inventory']
        for name in ('src/render_mirror.c', 'src/tyrian2.c', 'src/sprite.c'):
            raw = source_projection.checked_read(ROOT, name)
            previous = source_projection.project_source(name, raw)
            assert source_projection.sha(previous) == expected[name], ('projectile61 baseline source drift', name)
            baseline[name] = previous.decode()
        cls.base_renderer = baseline['src/render_mirror.c']
        cls.base_shots = baseline['src/tyrian2.c']
        cls.sprite = (ROOT / 'src/sprite.c').read_text()
        cls.base_sprite = baseline['src/sprite.c']

    def test_fixed_target_budget_and_padded_capture_names(self):
        self.assertEqual(diff.TICK, 150)
        self.assertEqual(diff.PEAK, 64 * 1024**2)
        self.assertEqual(diff.RESERVE, 250 * 1024**2)
        names = tuple(diff.capture_names())
        self.assertEqual(len(names), 3)
        self.assertEqual(set(names), {'classic-0150.bmp', 'display-0150.bmp', 'asset-debug-window-0150.bmp'})
        for name in names:
            self.assertEqual(Path(name).name, name)
            self.assertNotIn('*', name)

    def test_inclusive_budget_and_reserve_boundaries(self):
        self.assertTrue(diff.budget_ok(0, diff.RESERVE))
        self.assertTrue(diff.budget_ok(diff.PEAK, diff.RESERVE))
        self.assertTrue(diff.budget_ok(diff.PEAK - 1, diff.RESERVE + 1))
        self.assertFalse(diff.budget_ok(diff.PEAK + 1, diff.RESERVE))
        self.assertFalse(diff.budget_ok(diff.PEAK, diff.RESERVE - 1))
        self.assertFalse(diff.budget_ok(diff.PEAK + 1, diff.RESERVE - 1))

    def test_poisoned_parent_environment_is_scrubbed_without_mutation(self):
        poisoned = {
            'AIRCRAFT170_DIFFERENTIAL_POSE': '3', 'AIRCRAFT_FUTURE_CONTROL': 'true',
            'PROJECTILE145_FORCE_SHOT': '1', 'PROJECTILE61_FORCE_ACTOR': '795',
            'SHARED170_GUARD': 'cached-mutation', 'SHARED_FUTURE': '1',
            'TYRIAN_CYAN_BORROW': '1', 'TYRIAN_CYAN_BORROW_EXTRA': '1',
            'TYRIAN_GAME_PROBE_FORCE': '61', 'OT_CAPTURE': 'all',
            'PATH': '/unchanged/bin', 'KEEP_ME': 'untouched', 'HOME': '/old/home',
        }
        before = dict(poisoned)
        env, removed = diff.environment(poisoned, Path('/sysroot'), Path('/out'), Path('/tmpdir'))
        self.assertEqual(poisoned, before)
        controls = {key for key in poisoned if key.startswith(('AIRCRAFT', 'PROJECTILE', 'SHARED', 'TYRIAN_CYAN_BORROW', 'TYRIAN_GAME_PROBE', 'OT_'))}
        self.assertEqual(set(removed), controls)
        for key in controls:
            self.assertNotIn(key, env)  # Removed, not set to empty string or0.
        self.assertEqual(env['KEEP_ME'], 'untouched')
        self.assertEqual(env['PATH'], '/unchanged/bin')
        self.assertEqual(env['HOME'], '/out')
        self.assertEqual(env['XDG_CONFIG_HOME'], '/out/config')
        self.assertEqual(env['SDL_VIDEODRIVER'], 'dummy')
        self.assertEqual(env['SDL_AUDIODRIVER'], 'dummy')
        self.assertEqual(env['TMPDIR'], '/tmpdir')

    def test_current_renderer_dump_is_exactly_reversible(self):
        original = self.observed['render_mirror.c']
        modified = diff.renderer_text(original)
        self.assertEqual(modified.count(diff.DUMP), 1)
        self.assertEqual(modified.replace(diff.DUMP, '', 1), original)
        old_inner = extract(original, 'projectile61_observation_inner_finish')
        self.assertEqual(extract(modified, 'projectile61_observation_inner_finish'), old_inner)
        outer = extract(modified, 'render_mirror_finish')
        self.assertIn(diff.DUMP.strip(), outer)
        self.assertEqual(outer.count('projectile61_observation_inner_finish(kind,lightx,lighty);'), 1)

    def test_baseline_renderer_remains_baseline_without61_finish_observer(self):
        self.assertNotIn('projectile61_observation_inner_finish', self.base_renderer)
        self.assertNotIn('#include "enemy_projectile61_mirror.inc"', self.base_renderer)
        modified = diff.renderer_text(self.base_renderer)
        self.assertEqual(modified.replace(diff.DUMP, '', 1), self.base_renderer)
        self.assertNotIn('projectile61_observation_inner_finish', modified)
        self.assertNotIn('projectile61_resources', modified)
        self.assertEqual(modified.count(diff.DUMP), 1)

    def test_dump_is_unconditional_at_target_and_not_assert_guarded(self):
        c = compact(diff.DUMP)
        self.assertIn('game_probe_enabled&&game_probe_tick==150', c)
        self.assertIn('native-game-screen.index8', diff.DUMP)
        self.assertIn('native-vga-screen.index8', diff.DUMP)
        self.assertIn('native-palette.rgb', diff.DUMP)
        self.assertIn('surfaces[2]={game_screen,VGAScreenSeg}', c)
        self.assertIn('i<256', c)
        self.assertIn('bytes[3]', c)
        self.assertIn('fwrite', c)
        for forbidden in ('assert(', 'global_projectile91_', 'projectile61_resources', 'ready', 'last_output_valid', 'getenv(', 'SDL_Save', 'mt_rand('):
            self.assertNotIn(forbidden, diff.DUMP)
        self.assertNotIn('game_probe_tick>=', c)
        self.assertNotIn('game_probe_tick<=', c)

    def test_baseline_shot_transform_preserves_every_production_byte(self):
        modified = diff.baseline_shot_text(self.base_shots)
        restored = modified.replace(instr.SHOT_LOG + '\n', '', 1).replace('\n ' + instr.EMIT_CALL, '', 1).replace('\n ' + instr.DRAW_CALL, '', 1)
        self.assertEqual(restored, self.base_shots)
        self.assertIn(instr.DRAW_MARKER + '\n ' + instr.DRAW_CALL, modified)
        self.assertIn(instr.EMIT_MARKER + '\n ' + instr.EMIT_CALL, modified)
        before_line = next(line for line in self.base_shots.splitlines() if 'if (sprite == 112 || sprite == 113' in line)
        after_line = next(line for line in modified.splitlines() if 'if (sprite == 112 || sprite == 113' in line)
        self.assertEqual(before_line, after_line)
        self.assertNotIn('sprite == 61', after_line)
        self.assertEqual(modified.count(instr.SHOT_LOG), 1)

    def test_general_probe_filter_changes_only_tick150_exception(self):
        original = self.observed['game_probe.c']
        modified = diff.game_probe_text(self.current['game_probe.c'])
        before = extract(original, 'projectile61_tickzero_fprintf')
        after = extract(modified, 'projectile61_tickzero_fprintf')
        expected = before.replace('game_probe_tick!=0', 'game_probe_tick!=0&&game_probe_tick!=150')
        self.assertEqual(compact(after), compact(expected))
        self.assertEqual(modified.replace(after, before, 1), original)
        self.assertIn(instr.ADMISSION_LOG, modified)
        self.assertIn(instr.ADMISSION_DECL + '\n' + instr.ADMISSION_CALL, modified)
        self.assertEqual(modified.count(instr.ADMISSION_LOG), 1)
        self.assertIn('stream!=stdout&&stream!=stderr', compact(after))

    def test_actual_sprite_source_is_unchanged_and_transform_reversible(self):
        self.assertEqual(self.sprite, self.base_sprite)
        self.assertEqual(self.sprite.count(diff.BLEND_ORIGINAL), 1)
        modified = diff.sprite_text(self.sprite)
        self.assertEqual(modified.count(diff.BLEND_REPLACEMENT), 1)
        restored = modified.replace(diff.BLEND_REPLACEMENT, diff.BLEND_ORIGINAL, 1)
        restored = restored.replace('#include "asset_debug.h"\n#include "game_probe.h"', '#include "asset_debug.h"', 1)
        self.assertEqual(restored, self.sprite)

    def test_blend_log_has_exact_tick_and_retains_native_write_callback(self):
        c = compact(diff.BLEND_REPLACEMENT)
        native = '*pixels = (((*data & 0x0f) + (*pixels & 0x0f)) / 2) | (*data & 0xf0);'
        callback = 'render_mirror_sprite2_blend_pixel(surface,pixels,*data,sprite2s,index,x,y);'
        self.assertEqual(c.count(compact(native)), 1)
        self.assertEqual(c.count(compact(callback)), 1)
        self.assertIn('game_probe_enabled&&game_probe_tick==150', c)
        self.assertNotIn('game_probe_tick>=', c)
        self.assertNotIn('game_probe_tick<=', c)
        self.assertNotIn('assert(', c)
        self.assertNotIn('mt_rand(', c)
        self.assertLess(c.index(compact(native)), c.index('fprintf('))
        self.assertLess(c.index('fprintf('), c.index(compact(callback)))

    def test_capture_high_water_checked_before_exact_duplicate_removal(self):
        tree = ast.parse(Path(diff.__file__).read_text())
        main = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'main')
        variants = next(node for node in ast.walk(main) if isinstance(node, ast.For) and isinstance(node.target, ast.Name) and node.target.id == 'kind' and isinstance(node.iter, ast.Tuple) and [value.value for value in node.iter.elts] == ['present', 'missing', 'baseline'])
        body = variants.body

        def call_statement(node, function):
            return isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == function

        def attribute_call(node, name):
            return isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute) and node.value.func.attr == name

        write_zip = next(node for node in body if isinstance(node, ast.With) and any(isinstance(item.context_expr, ast.Call) and any(isinstance(arg, ast.Constant) and arg.value == 'w' for arg in item.context_expr.args) for item in node.items))
        capture_loop = next(node for node in write_zip.body if isinstance(node, ast.For))
        png_index = next(index for index, node in enumerate(capture_loop.body) if attribute_call(node, 'save'))
        zip_index = next(index for index, node in enumerate(capture_loop.body) if attribute_call(node, 'write'))
        self.assertTrue(call_statement(capture_loop.body[png_index + 1], 'measure'))
        self.assertTrue(call_statement(capture_loop.body[zip_index + 1], 'measure'))
        self.assertLess(png_index, zip_index)
        self.assertTrue(call_statement(body[body.index(write_zip) + 1], 'measure'))
        map_indices = [index for index, node in enumerate(body) if attribute_call(node, 'write_text') and any(isinstance(value, ast.Constant) and value.value == 'bmp-recovery-map.json' for value in ast.walk(node))]
        self.assertEqual(len(map_indices), 2)
        for index in map_indices:
            self.assertTrue(call_statement(body[index + 1], 'measure'))
        retained = next(node for node in body if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call) and any(keyword.arg == 'status' and isinstance(keyword.value, ast.Constant) and keyword.value.value == 'VERIFIED_LOSSLESS_DUPLICATES_RETAINED' for keyword in node.value.keywords))
        compacted = next(node for node in body if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) and node.value.value == 'VERIFIED_LOSSLESS_DUPLICATES_COMPACTED')
        unlinks = [node for node in ast.walk(main) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'unlink']
        self.assertEqual(len(unlinks), 1)
        self.assertLess(retained.lineno, body[map_indices[0]].lineno)
        self.assertLess(body[map_indices[0] + 1].end_lineno, unlinks[0].lineno)
        self.assertLess(unlinks[0].lineno, compacted.lineno)
        self.assertLess(compacted.lineno, body[map_indices[1]].lineno)

    def test_missing_or_duplicate_exact_markers_fail_closed(self):
        accepted = (AssertionError, ValueError, RuntimeError)
        pairs = (
            (diff.renderer_text, self.base_renderer, instr.FINISH_DECL + '\n{'),
            (diff.baseline_shot_text, self.base_shots, instr.EMIT_MARKER),
            (diff.baseline_shot_text, self.base_shots, instr.DRAW_MARKER),
            (diff.game_probe_text, self.current['game_probe.c'], instr.PROBE_MARKER),
            (diff.game_probe_text, self.current['game_probe.c'], instr.ADMISSION_DECL),
            (diff.sprite_text, self.sprite, diff.BLEND_ORIGINAL),
        )
        for transform, original, marker in pairs:
            self.assertEqual(original.count(marker), 1)
            for replacement in ('', marker + '\n' + marker):
                with self.subTest(transform=transform.__name__, duplicate=bool(replacement)):
                    changed = original.replace(marker, replacement, 1)
                    with self.assertRaises(accepted): transform(changed)


if __name__ == '__main__': unittest.main()
