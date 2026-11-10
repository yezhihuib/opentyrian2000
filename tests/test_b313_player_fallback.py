#!/usr/bin/env python3
"""Actual fallback includes, native blitter/writer and SDL software, ASan/UBSan.

The five authored HDA files are real. Native RLE is independently encoded from
frozen archived callback records. Scope, original-bank pin and palette admission
are explicit fixture dependencies, not original-game or whole-level acceptance.
No game, profile, original input, repository fixture, or display capture is written.
"""
from pathlib import Path
import os
import re
import shlex
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'experimental/level2-family/src'
ARCHIVE = ROOT / 'experimental/late-level/sources/03c5968bda89ae17'


def function(source, name):
    match = re.search(r'^(?:static )?[^\n]+?\b' + re.escape(name) + r'\(', source, re.M)
    if match is None:
        raise AssertionError('Missing production function: ' + name)
    opening = source.index('{', match.start())
    depth, end = 1, opening + 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[match.start():end]


class PlayerFallbackTests(unittest.TestCase):
    def test_real_hooks_preserve_independent_order_and_shared_proofs(self):
        mirror = (SRC / 'render_mirror.c').read_text()
        canvas = (SRC / 'b313_family_canvas_mirror.inc').read_text()
        terrain = (SRC / 'b313_terrain_fallback_mirror.inc').read_text()
        player = (SRC / 'b313_player_fallback_mirror.inc').read_text()
        pose = function(mirror, 'render_mirror_player_pose')
        self.assertLess(pose.index('pf_pose('), pose.index('ps_pose('))
        body = function((SRC / 'global_talon_mirror.inc').read_text(), 'render_mirror_global_player_ship')
        self.assertLess(body.index('pf_body('), body.index('ps_body('))
        end = function(canvas, 'family_entity_end')
        self.assertLess(end.index('pf_end()'), end.index('ps_end()'))
        pixel = function(canvas, 'family_pixel')
        self.assertLess(pixel.index('tf_pixel('), pixel.index('if(!fc.frame_active||fc.frame_failed)return;'))
        self.assertIn('if(!tracked&&!b313_family_writer_pixel(s,address))', pixel)
        independent = function(terrain, 'tf_pixel')
        self.assertEqual(independent.count('b313_family_writer_pixel('), 1)
        self.assertLess(independent.index('b313_family_writer_pixel('), independent.index('pf_pixel('))
        self.assertLess(independent.index('pf_pixel('), independent.index('tf.expected[off]=*address'))
        self.assertLess(independent.index('pf_pixel('), independent.index('tf.mask[off]=0'))
        self.assertNotIn('b313_family_writer_pixel(', player)
        self.assertNotIn('fc.frame_failed', player)
        self.assertNotRegex(re.sub(r'/\*.*?\*/', '', player, flags=re.S), r'\bps\.(?:active|draw)\b')
        present = function(terrain, 'tf_present')
        self.assertLess(present.index('SDL_LockTexture('), present.index('pf_compose()'))
        self.assertLess(present.index('if(!current)'), present.index('pf_compose()'))
        self.assertLess(present.index('pf_compose()'), present.index('family_static_hud_compose_surface('))
        self.assertLess(present.index('pf_present_begin('), present.index('asset_debug_readback('))
        self.assertLess(present.index('SDL_RenderPresent('), present.index('pf_present_end()'))
        self.assertIn('pf_shared_fail()', function(terrain, 'tf_fail'))
        self.assertIn('pf_reset()', function(terrain, 'tf_reset'))
        self.assertIn('pf_release()', function(terrain, 'tf_release'))
        legacy_first = function(mirror, 'render_mirror_present')
        self.assertLess(legacy_first.index('family_present(renderer,src,dst)'), legacy_first.index('tf_present(renderer,src,dst)'))
        self.assertIn('if(family_present(renderer,src,dst)){tf_reset();', legacy_first)

    def test_actual_includes_native_writer_and_software_present(self):
        pkg = shlex.split(os.environ.get('PKG_CONFIG', 'pkg-config'))
        flags = shlex.split(subprocess.check_output(pkg + ['--cflags', 'sdl2'], text=True))
        libs = shlex.split(subprocess.check_output(pkg + ['--libs', 'sdl2'], text=True))
        oracle = (ARCHIVE / 'player_ship_native.inc').read_text()
        oracle = oracle[:oracle.index('static const PlayerShipSpec *ps_spec')]
        oracle = oracle[oracle.index('static const PlayerShipWrite'):]
        oracle = re.sub(r'typedef struct \{.*?\} PlayerShipSpec;', '', oracle, flags=re.S)
        oracle = oracle.replace('ps_native_', 'oracle_native_').replace('ps_specs', 'oracle_specs')
        with tempfile.TemporaryDirectory(prefix='b313-player-fallback-') as temp:
            directory = Path(temp)
            (directory / 'player_fallback_oracle.inc').write_text(oracle)
            (directory / 'player_fallback_native.inc').write_text(
                function((SRC / 'sprite.c').read_text(), 'blit_sprite2'))
            (directory / 'player_fallback_helpers.inc').write_text(
                function((ROOT / 'src/asteroid1_ten_mirror.inc').read_text(), 'asteroid1_stamp') + '\n' +
                function((SRC / 'render_mirror.c').read_text(), 'blend_rgba'))
            asset_root = ROOT / 'assets/hd/current-compat/talon'
            bad_roots = [str(directory / 'missing-directory'), '']
            for kind in ('missing', 'magic', 'dimensions', 'truncated', 'payload', 'trailing'):
                bad = directory / kind
                bad.mkdir()
                for index in (229, 231, 233, 235, 237):
                    data = bytearray((asset_root / f'ship-{index}-8.hda').read_bytes())
                    if index == 237:  # Non-selected material still has to pass the cache load.
                        if kind == 'missing':
                            continue
                        if kind == 'magic':
                            data[0] ^= 1
                        elif kind == 'dimensions':
                            data[12] ^= 1
                        elif kind == 'truncated':
                            data.pop()
                        elif kind == 'payload':
                            data[-17] ^= 1
                        elif kind == 'trailing':
                            data.append(0)
                    (bad / f'ship-{index}-8.hda').write_bytes(data)
                bad_roots.append(str(bad))
            executable = directory / 'test'
            command = shlex.split(os.environ.get('CC', 'cc')) + [
                '-std=c11', '-O1', '-g', '-Wall', '-Wextra', '-Werror',
                '-DB313_FAMILY_CANVAS_DIAGNOSTIC=1',
                '-fsanitize=address,undefined', '-fno-sanitize-recover=all',
                '-fno-omit-frame-pointer', '-no-pie',
                '-I' + str(directory), '-I' + str(SRC), '-I' + str(ROOT / 'src'),
            ] + flags + [
                str(ROOT / 'tests/test_b313_player_fallback.c'),
                str(SRC / 'b313_family_writer.c'), '-o', str(executable),
            ] + libs
            subprocess.run(command, check=True)
            subprocess.run([str(executable), str(asset_root)] + bad_roots,
                           check=True, env={**os.environ, 'SDL_VIDEODRIVER': 'dummy',
                                          'ASAN_OPTIONS': 'detect_leaks=0:halt_on_error=1',
                                          'UBSAN_OPTIONS': 'halt_on_error=1'})


if __name__ == '__main__':
    unittest.main()
