"""Synthetic observer-accounting tests, not actual gameplay evidence."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('level2_continuity', Path(__file__).with_name('check_level2_preview_continuity.py'))
continuity = importlib.util.module_from_spec(spec)
spec.loader.exec_module(continuity)


class ContinuityAccountingTests(unittest.TestCase):
    def rows(self, accepted, failed=None, ticks=None):
        failed = failed if failed is not None else [0]*len(accepted)
        ticks = ticks if ticks is not None else range(245, 245+len(accepted))
        return [dict(tick=str(t), accepted=str(a), failed=str(f))
                for t, a, f in zip(ticks, accepted, failed)]

    def test_initial_classic_frame_is_not_invented_hd(self):
        result = continuity.summarize(self.rows([0, 0, 1, 2]))
        self.assertEqual(result['hd_presents'], 2)
        self.assertEqual(result['classic_presents'], 2)
        self.assertEqual(result['mode_switches'], 1)
        self.assertEqual(result['runs'], [dict(first=245,last=246,hd=False), dict(first=247,last=248,hd=True)])

    def test_single_frame_fallback_counts_both_switches(self):
        result = continuity.summarize(self.rows([1, 2, 2, 3], [0, 0, 1, 0]))
        self.assertEqual(result['mode_switches'], 2)
        self.assertEqual(result['classic_presents'], 1)

    def test_unadmitted_nonfault_frame_is_still_classic(self):
        result = continuity.summarize(self.rows([0, 0], [0, 0]))
        self.assertEqual(result['hd_presents'], 0)
        self.assertEqual(result['classic_presents'], 2)

    def test_post_admission_failure_is_not_hd(self):
        result = continuity.summarize(self.rows([1, 2], [1, 0]))
        self.assertEqual(result['hd_presents'], 1)
        self.assertEqual(result['classic_presents'], 1)

    def test_independent_terrain_is_not_counted_as_actor_admission(self):
        rows = self.rows([1, 1, 2], [0, 1, 0])
        rows[1]['terrain_presenting'] = '1'
        result = continuity.summarize(rows)
        self.assertEqual(result['hd_presents'], 3)
        self.assertEqual(result['family_hd_presents'], 2)
        self.assertEqual(result['terrain_only_presents'], 1)
        self.assertEqual(result['mode_switches'], 0)
        self.assertEqual(result['family_mode_switches'], 2)

    def test_double_present_claim_is_rejected(self):
        rows = self.rows([1])
        rows[0]['terrain_presenting'] = '1'
        with self.assertRaisesRegex(ValueError, 'Two compositors'):
            continuity.summarize(rows)

    def test_tick_gap_does_not_become_contiguous_run(self):
        result = continuity.summarize(self.rows([1, 2], ticks=[245, 247]))
        self.assertEqual(len(result['runs']), 2)

    def test_backwards_counter_rejected(self):
        with self.assertRaisesRegex(ValueError, 'backwards'):
            continuity.summarize(self.rows([1, 0]))


if __name__ == '__main__':
    unittest.main()
