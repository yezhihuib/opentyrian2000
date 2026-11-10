#!/usr/bin/env python3
"""Compile the real native blitter with the pure building clip contract."""
from pathlib import Path
import os
import shlex
import unittest
import subprocess
import tempfile
ROOT = Path(__file__).resolve().parents[1]


class BuildingVerticalClipTests(unittest.TestCase):
    def test_native_clip_contract(self):
        source = (ROOT / 'src/sprite.c').read_text()
        start = source.index('void blit_sprite2(SDL_Surface *surface,')
        end = source.index('\nvoid blit_sprite2_clip(', start)
        with tempfile.TemporaryDirectory(prefix='b313-vertical-') as tmp:
            tmp = Path(tmp)
            (tmp / 'b313_native_blit.inc').write_text(source[start:end])
            canvas = (ROOT / 'experimental/level2-family/src/b313_family_canvas_mirror.inc').read_text()
            begin = canvas.index(' if(fc_native_call){')
            finish = canvas.index(' if(suppress){', begin)
            (tmp / 'b313_native_guard.inc').write_text(canvas[begin:finish])
            exe = tmp / 'test'
            subprocess.run(shlex.split(os.environ.get('CC', 'cc')) + ['-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
                            '-fsanitize=undefined', '-fno-sanitize-recover=all', '-I'+str(tmp),
                            '-I'+str(ROOT/'experimental/level2-family/src'),
                            str(ROOT/'tests/test_b313_vertical_clip.c'),
                            str(ROOT/'experimental/level2-family/src/b313_family_plan.c'), '-o', str(exe)], check=True)
            subprocess.run([str(exe)], check=True)


if __name__ == "__main__":
    unittest.main()
