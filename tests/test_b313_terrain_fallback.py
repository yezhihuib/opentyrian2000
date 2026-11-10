#!/usr/bin/env python3
"""Exercise the actual fallback transaction and native writer under SDL software."""
from pathlib import Path
import os
import shlex
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def extract_block(source, marker):
    begin = source.index(marker)
    brace = source.index('{', begin)
    depth = 1
    end = brace + 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[begin:end]


class TerrainFallbackTests(unittest.TestCase):
    def test_integration_keeps_observation_after_actor_failure(self):
        canvas = (ROOT / 'experimental/level2-family/src/b313_family_canvas_mirror.inc').read_text()
        pixel = canvas.split('static void family_pixel(SDL_Surface *s,Uint8 *address,int style)', 1)[1].split('static void family_rect(', 1)[0]
        self.assertLess(pixel.index('tf_pixel(s,address,style)'), pixel.index('if(!fc.frame_active||fc.frame_failed)return;'))
        self.assertIn('if(!tracked&&!b313_family_writer_pixel(s,address))', pixel)
        render = (ROOT / 'experimental/level2-family/src/render_mirror.c').read_text()
        present = render.split('bool render_mirror_present(', 1)[1]
        self.assertLess(present.index('family_present(renderer,src,dst)'), present.index('tf_present(renderer,src,dst)'))
        self.assertLess(present.index('tf_present(renderer,src,dst)'), present.index('return family_static_hud_present(renderer,src,dst)'))
        self.assertIn('if(family_present(renderer,src,dst)){tf_reset();', present)

    def test_known_blend_is_only_scene_effect_exception(self):
        canvas = (ROOT / 'experimental/level2-family/src/b313_family_canvas_mirror.inc').read_text()
        lines = canvas.splitlines()
        calls = [line for line in lines if 'family_scene_fault(' in line and not line.startswith('static void family_scene_fault')]
        self.assertEqual(len(calls), 2)  # Generic wrapper delegation plus one targeted blend branch.
        blend = extract_block(canvas, 'if(style==MIRROR_BLEND&&hd_owner[n]')
        self.assertIn('if(style==MIRROR_BLEND&&hd_owner[n]', blend)
        self.assertIn('!terrain_retire)', blend)
        self.assertIn('family_scene_fault(FC_EFFECT)', blend)
        effects = [line for line in lines if 'family_scene_fault(FC_EFFECT)' in line]
        self.assertEqual(len(effects), 1)
        self.assertIn(effects[0].strip(), blend)
        self.assertIn('if(style!=MIRROR_NORMAL&&style!=MIRROR_SHADOW&&style!=MIRROR_BLEND){family_fault(FC_EFFECT);return;}', canvas)
        self.assertIn('if(*address!=(Uint8)((before&240)|((before&15)/2))){family_fault(FC_EFFECT);return;}', canvas)
        pixel = canvas.split('static void family_pixel(SDL_Surface *s,Uint8 *address,int style)', 1)[1].split('static void family_rect(', 1)[0]
        self.assertLess(pixel.index('tf_pixel(s,address,style)'), pixel.index('family_scene_fault(FC_EFFECT)'))

    def test_transaction_and_adversarial_sequences(self):
        pkg = shlex.split(os.environ.get('PKG_CONFIG', 'pkg-config'))
        flags = shlex.split(subprocess.check_output(pkg + ['--cflags', 'sdl2'], text=True))
        libs = shlex.split(subprocess.check_output(pkg + ['--libs', 'sdl2'], text=True))
        with tempfile.TemporaryDirectory(prefix='b313-terrain-fallback-') as directory:
            directory = Path(directory)
            canvas = (ROOT / 'experimental/level2-family/src/b313_family_canvas_mirror.inc').read_text()
            (directory / 'b313_fault_helpers.inc').write_text(
                extract_block(canvas, 'static void family_scene_fault(unsigned reason)') + '\n' +
                extract_block(canvas, 'static void family_fault(unsigned reason)'))
            lines = canvas.splitlines()
            unknown = next(line for line in lines if line.strip().startswith('if(style!=MIRROR_NORMAL&&style!=MIRROR_SHADOW&&style!=MIRROR_BLEND)'))
            blend = extract_block(canvas, 'if(style==MIRROR_BLEND&&hd_owner[n]')
            shadow = next(line for line in lines if 'if(*address!=(Uint8)((before&240)|((before&15)/2)))' in line)
            (directory / 'b313_effect_branches.inc').write_text(unknown + '\n' + blend + '\n if(style==MIRROR_SHADOW){' + shadow + '}\n')
            executable = directory / 'test'
            command = shlex.split(os.environ.get('CC', 'cc')) + [
                '-std=c11', '-O1', '-g', '-Wall', '-Wextra', '-Werror',
                '-DB313_FAMILY_CANVAS_DIAGNOSTIC=1',
                '-I' + str(directory),
                '-fsanitize=address,undefined', '-fno-sanitize-recover=all',
                '-fno-omit-frame-pointer', '-no-pie',
                '-I' + str(ROOT / 'experimental/level2-family/src'),
                '-I' + str(ROOT / 'src'),
            ] + flags + [
                str(ROOT / 'tests/test_b313_terrain_fallback.c'),
                str(ROOT / 'experimental/level2-family/src/b313_family_writer.c'),
                '-o', str(executable),
            ] + libs
            subprocess.run(command, check=True)
            subprocess.run([str(executable)], check=True, env={
                **os.environ, 'SDL_VIDEODRIVER': 'dummy',
                'ASAN_OPTIONS': 'detect_leaks=0:halt_on_error=1',
                'UBSAN_OPTIONS': 'halt_on_error=1',
            })


if __name__ == '__main__':
    unittest.main()
