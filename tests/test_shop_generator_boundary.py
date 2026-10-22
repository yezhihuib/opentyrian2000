#!/usr/bin/env python3
"""Live SHOP boundary and immutable published-stage proof; see fixture README."""
import unittest
from shop_published_boundary import check_inventory, check_pin_assets, published_source, sha

class PublishedShopBoundary(unittest.TestCase):
    def test_live_inventory_and_original_assets(self):
        check_inventory()
        check_pin_assets('generator')

    def test_published_source_boundary(self):
        pin = check_pin_assets('generator')
        source = published_source('generator', 'src/pregame_font.c')
        self.assertEqual(sha(source), pin['accepted_sha256']['src/pregame_font.c'])

    def test_original_private_tree_proof(self):
        from shop_published_boundary import replay_original_historical_contract
        replay_original_historical_contract('generator_boundary')

if __name__ == '__main__':
    unittest.main()
