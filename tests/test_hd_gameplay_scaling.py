"""Bounded development-overlay fitting tests. No original game data is used."""
from pathlib import Path
import os
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
OVERLAY = ROOT / 'experimental/level2-family/src'


class HdGameplayScalingTests(unittest.TestCase):
    def test_real_sdl_output(self):
        result = subprocess.run(['bash', 'tests/run_hd_gameplay_scaling_tests.sh'],
                                cwd=ROOT, capture_output=True, text=True,
                                env=dict(os.environ), timeout=120)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('PASS: 26 output cases (14 fractional)', result.stdout)
        self.assertIn('synthetic SDL software output, no game run', result.stdout)

    def test_classic_scalers_not_overridden(self):
        self.assertFalse((OVERLAY / 'video_scale.c').exists())
        self.assertFalse((OVERLAY / 'video_scale.h').exists())
        source = (OVERLAY / 'hd_gameplay_scaling.h').read_text()
        self.assertEqual(source.count('static inline int video_hd_set_texture_scale('), 1)
        self.assertNotIn('SDL_RenderPresent', source)
        self.assertNotIn('SDL_RenderSet', source)

    def test_both_development_presenters_use_helper(self):
        for name, texture in [('render_mirror.c', 'texture'), ('common_pause.c', 'cp.texture')]:
            source = (OVERLAY / name).read_text()
            self.assertEqual(source.count('video_hd_set_texture_scale(' + texture + ',renderer,dst)'), 1)
            self.assertEqual(source.count('#include "hd_gameplay_scaling.h"'), 1)
            self.assertNotIn('SDL_SetTextureScaleMode(' + texture + ',SDL_ScaleModeNearest)', source)
            self.assertNotIn('video_hd_set_texture_scale', (ROOT / 'src' / name).read_text())

    def test_canonical_source_binding_preserved(self):
        result = subprocess.run(['python3', 'scripts/verify_current_production.py'],
                                cwd=ROOT, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('"status": "PASS"', result.stdout)


if __name__ == '__main__':
    unittest.main()
