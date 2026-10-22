#!/usr/bin/env python3
"""Original observer-only annotation contract, projected from guarded live bytes."""
from collections import Counter
import difflib
import re
import unittest
from shop_published_boundary import ROOT, check_inventory, fixture, published_source

class ShopProductFontIntegration(unittest.TestCase):
    def test_observer_only_delta_and_live_tail(self):
        check_inventory()
        parent = fixture('product-parent-game_menu.c.txt').decode()
        stage = published_source('product', 'src/game_menu.c').decode()
        diff = ''.join(difflib.unified_diff(parent.splitlines(True), stage.splitlines(True), n=0))
        added=[]
        for line in diff.splitlines():
         if line.startswith(('+++','---','@@','diff ','index ')):continue
         assert not line.startswith('-'),('original menu line removed',line)
         if line.startswith('+') and line[1:].strip():
          call=line[1:].strip();assert re.fullmatch(r'pregame_font_[a-z_]+\([^;]*\);',call),call
          assert not any(token in call for token in ('++','--','+=','-=','->cash')),call
          added.append(call.split('(')[0])
        assert Counter(added)==Counter(pregame_font_product_begin=1,pregame_font_run_begin=8,pregame_font_run_end=8,pregame_font_product_update_begin=2,pregame_font_product_update_end=2,pregame_font_cursor_erased=1)
        source=(ROOT/'src/pregame_font.c').read_text()
        assert 'SF_EVENTS=40000' in published_source('product', 'src/pregame_font.c').decode()
        assert 'sf.event_count==SF_EVENTS' in source
        assert 'SF_CAP=16*1024*1024' in source
        assert 'SF_EVENTS=65536' in source and 'if(!replay_matches())' in source
        assert 'sf.count>sf.static_count' in source and 'p/SF_W>=185' in source
        assert 'sf.product&&sf.run_role==PREGAME_CASH' in source

    def test_original_private_tree_proof(self):
        from shop_published_boundary import replay_original_historical_contract
        replay_original_historical_contract('product_font_integration')

if __name__ == '__main__':
    unittest.main()
