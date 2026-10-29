#!/usr/bin/env python3
"""Pure source-transform contracts only; no C compilation or game execution."""
from pathlib import Path
import importlib.util
import os
import re
import sys
import unittest

HERE = Path(__file__).resolve().parent
DEFAULT_ROOT = HERE.parent if (HERE.parent / 'src').is_dir() else HERE.parents[1] / 'projectile61-private-sparse'
ROOT = Path(os.environ.get('PROJECTILE61_STATIC_ROOT', str(DEFAULT_ROOT)))
sys.path.insert(0, str(ROOT / 'tests'))
spec = importlib.util.spec_from_file_location('projectile61_gameplay_instrumentation', HERE / 'projectile61_gameplay_instrumentation.py')
obs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(obs)
from global_talon_reconstruction import extract


class Projectile61InstrumentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.texts = {name: (ROOT / 'src' / name).read_text() for name in sorted(obs.REQUIRED | obs.OPTIONAL)}
        cls.modified = obs.instrument(cls.texts)

    def test_input_unchanged_same_keys_and_four_output_only_tus(self):
        before = dict(self.texts)
        out = obs.instrument(self.texts)
        self.assertEqual(self.texts, before)
        self.assertEqual(set(out), set(before))
        self.assertEqual({name[:-2] for name in out if out[name] != before[name]}, set(obs.INSTRUMENTED_TUS))
        self.assertEqual(set(obs.FRESH_TUS) - set(obs.INSTRUMENTED_TUS), {'entity_draw'})

    def test_three_text_mode_keeps_optional_asset_absent(self):
        three = {name: text for name, text in self.texts.items() if name != 'asset_debug.c'}
        self.assertEqual(set(obs.instrument(three)), set(three))

    def test_all_derivatives_reconstruct_exact_original(self):
        restored = dict(self.modified)
        restored['game_probe.c'] = restored['game_probe.c'].replace(obs.ADMISSION_LOG + '\n' + obs.LOG_FILTER + '\n', '', 1).replace('\n' + obs.ADMISSION_CALL, '', 1)
        restored['asset_debug.c'] = restored['asset_debug.c'].replace(obs.LOG_FILTER + '\n', '', 1)
        restored['tyrian2.c'] = restored['tyrian2.c'].replace(obs.SHOT_LOG + '\n', '', 1).replace('\n ' + obs.EMIT_CALL, '', 1).replace('\n ' + obs.DRAW_CALL, '', 1)
        original = extract(self.texts['render_mirror.c'], 'render_mirror_finish')
        renamed = original.replace(obs.FINISH_DECL, obs.RENAMED_FINISH_DECL, 1)
        restored['render_mirror.c'] = restored['render_mirror.c'].replace(renamed + '\n' + obs.FINISH_OBSERVER, original, 1)
        self.assertEqual(restored, self.texts)

    def test_native_emit_reads_actual_fields_and_draw_logs_after_dispatch(self):
        text = self.modified['tyrian2.c']
        self.assertIn(obs.EMIT_MARKER + '\n ' + obs.EMIT_CALL, text)
        self.assertIn('b,temp3,i,enemy[i].enemytype,enemy[i].linknum', obs.EMIT_CALL)
        self.assertIn(obs.DRAW_MARKER + '\n ' + obs.DRAW_CALL, text)
        self.assertEqual(text.count('draw_enemy_shot_sprite2(VGAScreen, enemyShot[z].sx, enemyShot[z].sy, spriteSheet8, sprite);'), 1)
        self.assertIn('index!=61', obs.SHOT_LOG)
        self.assertNotIn('enemy[i].enemytype =', obs.SHOT_LOG + obs.EMIT_CALL + obs.DRAW_CALL)

    def test_admission_bypasses_large_log_filter_and_keeps_actual_boolean(self):
        probe = self.modified['game_probe.c']
        self.assertLess(probe.index(obs.ADMISSION_LOG), probe.index(obs.LOG_FILTER))
        self.assertIn('role!=151||index!=61', obs.ADMISSION_LOG)
        self.assertIn('role,index,x,y,part,style,mirrored', obs.ADMISSION_CALL)
        self.assertIn('actual61-admission.tsv', obs.ADMISSION_LOG)

    def test_finish_calls_exact_production_body_once_before_readonly_witness(self):
        self.assertEqual(obs.FINISH_OBSERVER.count('projectile61_observation_inner_finish(kind,lightx,lighty);'), 1)
        self.assertLess(obs.FINISH_OBSERVER.index('projectile61_observation_inner_finish(kind,lightx,lighty);'), obs.FINISH_OBSERVER.index('for(unsigned slot=0;'))
        for forbidden in ('global_projectile91_check_cache(', 'projectile61_ready_at(', 'projectile61_resource(', 'render_mirror_begin(', 'mt_rand(', 'getenv(', 'SDL_Save', '.bmp', '.png', 'assert('):
            self.assertNotIn(forbidden, obs.FINISH_OBSERVER + obs.SHOT_LOG + obs.ADMISSION_LOG)
        for state in ('enemyShot[', 'enemyShotAvail[', 'rgb_palette[', 'global_projectile91_owner['):
            self.assertIsNone(re.search(re.escape(state) + r'[^;\n]*\]\s*(?:\+\+|--|=(?!=)|\+=|-=)', obs.FINISH_OBSERVER))

    def test_internal8_per_pixel_clip_crop_and_actual_final_native_baseline(self):
        c = obs.FINISH_OBSERVER
        self.assertIn('game_probe_density==8', c)
        self.assertIn('px<24*8||px>=288*8||py<0||py>=184*8', c)
        self.assertIn('[px-24*8]', c)
        self.assertIn('(py/8)*VGAScreenSeg->pitch+px/8-24', c)
        self.assertIn('mask[(ay/8)*12+ax/8]', c)
        self.assertIn('if(pixel[3]!=255)continue;', c)
        self.assertIn('if(got==want&&got!=classic)witness++;', c)
        self.assertIn('if(!global_projectile91_owner[n])continue;', c)
        self.assertNotIn('x+12<=288', c)

    def test_real_resource_source_and_palette_contracts(self):
        c = obs.FINISH_OBSERVER
        for required in ('a->bank==ASSET_ENEMY_PROJECTILE61', 'a->index==61', '(global_projectile91_used_members&4u)', '!global_projectile91_fault', 'global_projectile91_cached', 'spriteSheet8.size==32060', '0x2b63027f74aaa21e', 'occupied==74&&left==37&&right==37', 'rgb_palette[113+c]', 'actual61-palette.tsv', 'for(unsigned c=0;c<256;c++)'):
            self.assertIn(required, c)
        self.assertIn('0x380000,0x510000,0x6d0400,0x860400,0x9e0800,0xba0c00,0xd31400,0xdf3c00,0xe7610c,0xeb8a18,0xf3ae24,0xfbcb30', c)

    def test_windows_no_assert_wrapped_diagnostics_and_tickzero_filter(self):
        self.assertEqual((obs.FIRST, obs.LAST), (140, 260))
        for c in (obs.SHOT_LOG, obs.ADMISSION_LOG, obs.FINISH_OBSERVER):
            self.assertIn('game_probe_tick<140||game_probe_tick>260', c)
            self.assertNotIn('assert(', c)
        self.assertIn("stream!=stdout&&stream!=stderr&&game_probe_tick!=0&&strchr(format,'%')", obs.LOG_FILTER)
        self.assertIn('vfprintf(stream,format,args)', obs.LOG_FILTER)
        self.assertNotIn('game_probe_tick>=140', obs.LOG_FILTER)

    def test_missing_duplicate_marker_and_double_application_rejected(self):
        for key, marker in (('game_probe.c', obs.PROBE_MARKER), ('game_probe.c', obs.ADMISSION_DECL), ('asset_debug.c', obs.ASSET_MARKER), ('tyrian2.c', obs.SHOT_DECL), ('tyrian2.c', obs.EMIT_MARKER), ('tyrian2.c', obs.DRAW_MARKER)):
            for replacement in ('', marker + '\n' + marker):
                changed = dict(self.texts)
                changed[key] = changed[key].replace(marker, replacement, 1)
                with self.subTest(key=key, marker=marker, duplicate=bool(replacement)):
                    with self.assertRaises(ValueError): obs.instrument(changed)
        with self.assertRaises(ValueError): obs.instrument(self.modified)

    def test_consumed_diagnostic_return_and_unknown_input_rejected(self):
        for statement in ('return fprintf(f,"%u",x);', 'int code = fprintf(f,"%u",x);', 'if ( fprintf(f,"%u",x)) branch();'):
            changed = dict(self.texts)
            changed['asset_debug.c'] += '\n' + statement
            with self.subTest(statement=statement):
                with self.assertRaises(ValueError): obs.instrument(changed)
        with self.assertRaises(ValueError): obs.instrument({**self.texts, 'sprite.c': ''})
        with self.assertRaises(ValueError): obs.instrument({'game_probe.c': self.texts['game_probe.c']})


if __name__ == '__main__': unittest.main()
