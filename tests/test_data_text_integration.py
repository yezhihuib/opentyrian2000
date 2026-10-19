#!/usr/bin/env python3
"""Data-only source boundaries, release-resource pins and CLI/package closure."""
import hashlib
import json
from pathlib import Path
import unittest
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from data_translation_validation import validate_paragraphs
ROOT = Path(__file__).resolve().parents[1]
class DataTextIntegration(unittest.TestCase):
    def test_native_english_loader_is_unchanged(self):
        source=(ROOT/'src/game_menu.c').read_text()
        body=source[source.index('bool load_cube('):source.index('\nvoid JE_drawItem(',source.index('bool load_cube('))]
        self.assertEqual(hashlib.sha256(body.encode()).hexdigest(), '7f31d939412c24f27414388855f7730e4a470514e75c1c41fc91912090a1d3d2')
    def test_complete_occurrence_and_paragraph_coverage(self):
        directory=ROOT/'assets/data-text-zh-CN-v1'
        source=json.loads((directory/'source-catalog.json').read_text())['entries']
        translated=json.loads((directory/'data-text-zh-CN-v1.json').read_text())['entries']
        a={r['id']:r for r in source};b={r['id']:r for r in translated}
        self.assertEqual(len(a),149);self.assertEqual(set(a),set(b))
        for key,original in a.items():
            row=b[key]
            for field in ('episode','cube_index','source_sha256'):self.assertEqual(row[field],original[field])
            validate_paragraphs(original['paragraphs'],row['paragraphs'],key)
            self.assertEqual(row['placeholder'],original['placeholder'])
        self.assertEqual(a['ep5.cube12']['marker_label'],'07')
    def test_overlay_precedes_readback_and_cursor_follows_text(self):
        source=(ROOT/'src/video.c').read_text()
        text=source.index('data_text_present(main_window_renderer')
        cursor=source.index('data_text_cursor_present(main_window_renderer')
        readback=source.index('asset_debug_readback(main_window_renderer)',text)
        self.assertLess(text,cursor);self.assertLess(cursor,readback)
    def test_page_event_uses_viewport_capacity(self):
        source=(ROOT/'src/game_menu.c').read_text()
        self.assertIn('data_text_page(lastkey_scan == SDL_SCANCODE_PAGEUP ? -1 : 1)',source)
        self.assertNotIn('data_text_scroll(lastkey_scan == SDL_SCANCODE_PAGEUP ? -9 : 9)',source)
    def test_no_full_font_in_runtime(self):
        manifest=json.loads((ROOT/'packaging/runtime-assets-v1.json').read_text())
        rows=[r for r in manifest['files'] if r['group']=='data-text']
        self.assertEqual(len(rows),3)
        self.assertEqual({Path(r['source_path']).suffix for r in rows},{'.dct','.dzf','.hda'})
        self.assertLess(sum(r['bytes'] for r in rows),5*1024*1024)
if __name__=='__main__':unittest.main()
