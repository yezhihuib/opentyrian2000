#!/usr/bin/env python3
"""Live SHOP boundary and immutable published-stage proof; see fixture README."""
import unittest
from shop_published_boundary import check_inventory, check_pin_assets, published_source, sha

class PublishedShopBoundary(unittest.TestCase):
    def test_live_inventory_and_original_assets(self):
        check_inventory()
        check_pin_assets('menu_font')

    def test_published_source_boundary(self):
        pin = check_pin_assets('menu_font')
        source = published_source('menu', 'src/pregame_font.c')
        # The intermediate private menu-only source is unavailable. The next
        # independently published front stage has an existing original accepted
        # source pin, retains these exact menu assets, and bounds every menu lease.
        front_pin = check_pin_assets('front')
        self.assertEqual(pin['accepted_sha256']['src/pregame_font.c'], front_pin['original_pregame_sha256'])
        self.assertEqual(sha(source), front_pin['accepted_sha256']['src/pregame_font.c'])
        text = source.decode()
        for invariant in ('static void load_menu_run(unsigned r)', 'sf.menu_run[r]',
                          'if(!menu)for(unsigned r=0;r<7;r++)load_menu_run(r);',
                          'if(r<7&&sf.menu_run[r]&&!strcmp(plain,menu_spec[r].text))',
                          'memcmp(h,"SMR1",4)', 'hash(data,size)!=s->payload_hash'):
            self.assertIn(invariant, text)
        for invariant in ('if(!replay_matches())', 'SF_EVENTS=40000'):
            self.assertIn(invariant, text)

    def test_original_private_tree_proof(self):
        from shop_published_boundary import replay_original_historical_contract
        replay_original_historical_contract('menu_font_boundary')

if __name__ == '__main__':
    unittest.main()
