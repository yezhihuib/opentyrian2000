#!/usr/bin/env python3
"""Finite title source/package tests. No engine, render, capture or aggregate build."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'prototype'))
from type3_small_coexistence import project_type3_small_family
spec = importlib.util.spec_from_file_location('title_layer_bundle', ROOT / 'prototype/title_layer_bundle.py')
bundle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bundle)
sys.modules[spec.name] = bundle

# Independent protocol pins, deliberately not imported from the producer.
EXPECTED = {
    'title-pic4-v1.hda': ('pic4', 4, 320, 200, 0, None,
        0x9a3f7cb8ec37073e, 0x9c9baa40cbccf525, 0x0abb22518a6634df,
        4096080, '0149d26dd7c860f497089f27d5650dec7af21846ad92cc8269a66b5375592c31'),
    'title-planet146-v1.hda': ('tyrian146', 146, 304, 121, 1, (4, 4, 1216, 484),
        0x30f8dbf0554a03ae, 0x0cb7de8084912543, 0x623a5b10ca52dae3,
        2354256, 'ff126712e87c052b2176365b228a8248d5ec7e04386e5d233614405e51537b05'),
    'title-planet151-v1.hda': ('year151', 151, 162, 64, 1, (8, 8, 644, 252),
        0x4562ec954d257998, 0xee71b0121c53f8df, 0x0df98d9dd374ce169,
        663632, '325c3602bce555f3b8023dd6b6167099d540fc828bf9e84c3bd21b85d0787357'),
}
SOURCE_MANIFEST = 'd7bd240f1210d01c3d0e01a81ec5511fe02be7972014d6564e333c54306bd7cc'


# Finite opposite-family receipts are pinned independently of mutable manifests.
OPPOSITE7 = {'source': 'assets/hd/artwork/newsh4-opposite7-v1',
 'source_manifest_sha256': 'fce309722a55c0f62ab563af15ff7af41b9a739d09b3099878753030ec5774bd',
 'density': 8,
 'logical_size': [24, 28],
 'assembly_size': [168, 28],
 'ids': [231, 233, 235, 267, 269, 271, 273],
 'slots': [389, 390, 391, 392, 393, 394, 395],
 'actor_types': [73, 74, 75, 76, 77, 78, 79],
 'bank_id': 2,
 'link': 2,
 'runtime_components': [0, 1, 19, 20],
 'excluded_actor_types': [66, 67, 68, 69, 70, 71, 72],
 'entries': [{'kind': 'actor',
              'bank_role': 102,
              'id': 231,
              'enemy_type': 73,
              'slot': 389,
              'anchor': [6, 7],
              'rgba_fnv1a64': '7772ad387ba647e1'},
             {'kind': 'actor',
              'bank_role': 102,
              'id': 233,
              'enemy_type': 74,
              'slot': 390,
              'anchor': [6, 7],
              'rgba_fnv1a64': '46ec9cc03cb2a64d'},
             {'kind': 'actor',
              'bank_role': 102,
              'id': 235,
              'enemy_type': 75,
              'slot': 391,
              'anchor': [6, 7],
              'rgba_fnv1a64': '6cf67a53c0c3c617'},
             {'kind': 'actor',
              'bank_role': 102,
              'id': 267,
              'enemy_type': 76,
              'slot': 392,
              'anchor': [6, 7],
              'rgba_fnv1a64': '3b6f6b5a0675dfab'},
             {'kind': 'actor',
              'bank_role': 102,
              'id': 269,
              'enemy_type': 77,
              'slot': 393,
              'anchor': [6, 7],
              'rgba_fnv1a64': '4e35f12d37d40aa1'},
             {'kind': 'actor',
              'bank_role': 102,
              'id': 271,
              'enemy_type': 78,
              'slot': 394,
              'anchor': [6, 7],
              'rgba_fnv1a64': '4fb033fc9820579f'},
             {'kind': 'actor',
              'bank_role': 102,
              'id': 273,
              'enemy_type': 79,
              'slot': 395,
              'anchor': [6, 7],
              'rgba_fnv1a64': '638ffb21f4fcc1dc'}]}
OPPOSITE7_FILES = {'enemy-newsh4-231-8.hda': {'sha256': '76740ae794198be75ba5d91f66f833a11204a5af2ebe5aea5123d25e75abf19f',
                            'header_u32': [1020231, 8, 24, 28, 6, 7],
                            'source_png': 'assets/hd/source/enemy-newsh4-231-8-76740ae79419.png',
                            'source_png_sha256': 'e2cee96271b7b15aaa258a65e7c46218f538ffbdfa9807ddc450da5094bb4990'},
 'enemy-newsh4-233-8.hda': {'sha256': 'd775e0a19addd5387751d4d6f968b5f1496ab163b1b4fde66676da63a0c97aba',
                            'header_u32': [1020233, 8, 24, 28, 6, 7],
                            'source_png': 'assets/hd/source/enemy-newsh4-233-8-d775e0a19add.png',
                            'source_png_sha256': 'ae60fa466453c8098b34371bec92cf2d83dbfbd3b37a7f09e200e990db7d6a38'},
 'enemy-newsh4-235-8.hda': {'sha256': 'dcfbceba15dc235a1a159c8f4776fb6999ee0cf2b119e42f464016af59c5d3fb',
                            'header_u32': [1020235, 8, 24, 28, 6, 7],
                            'source_png': 'assets/hd/source/enemy-newsh4-235-8-dcfbceba15dc.png',
                            'source_png_sha256': '45aa3307069848b75db8e6866448c18188d8def8445363955115aacdd85a9b1b'},
 'enemy-newsh4-267-8.hda': {'sha256': '80422d5d07e88de6dac735b89a5923623319dd35d4559923d88e04487e3a5554',
                            'header_u32': [1020267, 8, 24, 28, 6, 7],
                            'source_png': 'assets/hd/source/enemy-newsh4-267-8-80422d5d07e8.png',
                            'source_png_sha256': '5bd9c613f4570b25672f9be484dd91437d750e0c85aa91ff91e71dca57228206'},
 'enemy-newsh4-269-8.hda': {'sha256': '807c5e983a9bdbcfc029467e0967efc91b29c668801c38611ab03097445d302c',
                            'header_u32': [1020269, 8, 24, 28, 6, 7],
                            'source_png': 'assets/hd/source/enemy-newsh4-269-8-807c5e983a9b.png',
                            'source_png_sha256': '2956f1059155fb6661c36e8f8f2b7e582ca61e9e0f72d65ec874f16f74187089'},
 'enemy-newsh4-271-8.hda': {'sha256': 'e6f159a02dfadab3c883d04c5d17418ba0c3b5f66f322f1fadd72e83d6ddec92',
                            'header_u32': [1020271, 8, 24, 28, 6, 7],
                            'source_png': 'assets/hd/source/enemy-newsh4-271-8-e6f159a02dfa.png',
                            'source_png_sha256': 'd6eac8e74ec26b8d5a058195c258ca1c5cc53718072ec76ab2fb12d1d5291c4e'},
 'enemy-newsh4-273-8.hda': {'sha256': '85f4fe5fd01dc69c857c039b4c589cbf4becd29c696cef2503f79b647a2e92fe',
                            'header_u32': [1020273, 8, 24, 28, 6, 7],
                            'source_png': 'assets/hd/source/enemy-newsh4-273-8-85f4fe5fd01d.png',
                            'source_png_sha256': '8e5ad4402891610c1fd8fedda4f5cff071463693b3d1c4f4bf0453d0827a56bc'}}
OPPOSITE7_PNGS = {'76740ae794198be75ba5d91f66f833a11204a5af2ebe5aea5123d25e75abf19f': {'path': 'assets/hd/source/enemy-newsh4-231-8-76740ae79419.png',
                                                                      'sha256': 'e2cee96271b7b15aaa258a65e7c46218f538ffbdfa9807ddc450da5094bb4990',
                                                                      'RGBA_sha256': 'bce31d3bdc1c026757e64cdd9349f832a4b50a8ede48a66e5d33432cfc58588d'},
 'd775e0a19addd5387751d4d6f968b5f1496ab163b1b4fde66676da63a0c97aba': {'path': 'assets/hd/source/enemy-newsh4-233-8-d775e0a19add.png',
                                                                      'sha256': 'ae60fa466453c8098b34371bec92cf2d83dbfbd3b37a7f09e200e990db7d6a38',
                                                                      'RGBA_sha256': 'b24b7901d4e4795b75efb206ec3cbeb208bbfb73ccb65a64094567b611ee0258'},
 'dcfbceba15dc235a1a159c8f4776fb6999ee0cf2b119e42f464016af59c5d3fb': {'path': 'assets/hd/source/enemy-newsh4-235-8-dcfbceba15dc.png',
                                                                      'sha256': '45aa3307069848b75db8e6866448c18188d8def8445363955115aacdd85a9b1b',
                                                                      'RGBA_sha256': '0d0bffef2bc5dc36634ee57996ddc8155015408a07739e3d4f3a935a4dc6da0d'},
 '80422d5d07e88de6dac735b89a5923623319dd35d4559923d88e04487e3a5554': {'path': 'assets/hd/source/enemy-newsh4-267-8-80422d5d07e8.png',
                                                                      'sha256': '5bd9c613f4570b25672f9be484dd91437d750e0c85aa91ff91e71dca57228206',
                                                                      'RGBA_sha256': '01b5cdbcad2395bb15d5fef855f2996d6cf9350252b87400d620f2528530d26f'},
 '807c5e983a9bdbcfc029467e0967efc91b29c668801c38611ab03097445d302c': {'path': 'assets/hd/source/enemy-newsh4-269-8-807c5e983a9b.png',
                                                                      'sha256': '2956f1059155fb6661c36e8f8f2b7e582ca61e9e0f72d65ec874f16f74187089',
                                                                      'RGBA_sha256': '4b033ca269be237a0fa7c23a4f0f3a9dce80b0f97efbe1caeb2c9c390d848835'},
 'e6f159a02dfadab3c883d04c5d17418ba0c3b5f66f322f1fadd72e83d6ddec92': {'path': 'assets/hd/source/enemy-newsh4-271-8-e6f159a02dfa.png',
                                                                      'sha256': 'd6eac8e74ec26b8d5a058195c258ca1c5cc53718072ec76ab2fb12d1d5291c4e',
                                                                      'RGBA_sha256': '60109281e71cd09cc4d96122f08504cb900a2f5d3fc69a8833e4d2753fbd60f2'},
 '85f4fe5fd01dc69c857c039b4c589cbf4becd29c696cef2503f79b647a2e92fe': {'path': 'assets/hd/source/enemy-newsh4-273-8-85f4fe5fd01d.png',
                                                                      'sha256': '8e5ad4402891610c1fd8fedda4f5cff071463693b3d1c4f4bf0453d0827a56bc',
                                                                      'RGBA_sha256': '7813fd611d11b30eb6f4f51eb3c23eb5bd30a1c05eeebe1b7f00d449636448ab'}}


# Exact type15 eight-heading append, independent of mutable manifest receipts.
TYPE15 = {'schema': 'enemy-type15-eightheading-v1',
 'source': 'assets/hd/artwork/type15-eightheading-v1',
 'source_inventory_sha256': '17780d02fef4c08636d22651c1299e3641234d0b992f7283fe32e64d92ca67d9',
 'import_sha256': 'ee659ea7365f457250ddb15fd11f95c0ddb6ca31f80f51156b98adf0f6b6e383',
 'bank_id': 1,
 'bank_role': 101,
 'enemy_type': 15,
 'ids': [39, 41, 43, 45, 91, 93, 129, 131],
 'slots': [396, 397, 398, 399, 400, 401, 402, 403],
 'density': 8,
 'logical_size': [24, 28],
 'anchor': [6, 7],
 'runtime_components': [0, 1, 19, 20],
 'selector_order': [91, 45, 93, 39, 43, 129, 41, 131],
 'selector_headings': ['NW', 'N', 'NE', 'W', 'E', 'SW', 'S', 'SE'],
 'selection': 'Original event-selected headings; animate0, no automatic rotation',
 'source_only_nonpresented_base': 91,
 'original_alpha_exact': True,
 'fallback': 'All eight approved members required before any replacement; 8x-only selected-pack '
             'cached fallback is local to this family',
 'entries': [{'id': 39,
              'bank_role': 101,
              'slot': 396,
              'anchor': [6, 7],
              'rgba_fnv1a64': '63fd993042755636'},
             {'id': 41,
              'bank_role': 101,
              'slot': 397,
              'anchor': [6, 7],
              'rgba_fnv1a64': 'f6583f60603839a3'},
             {'id': 43,
              'bank_role': 101,
              'slot': 398,
              'anchor': [6, 7],
              'rgba_fnv1a64': '4cd47c32a4b23eaa'},
             {'id': 45,
              'bank_role': 101,
              'slot': 399,
              'anchor': [6, 7],
              'rgba_fnv1a64': 'e9d34663cade254d'},
             {'id': 91,
              'bank_role': 101,
              'slot': 400,
              'anchor': [6, 7],
              'rgba_fnv1a64': 'baa804b312e1f561'},
             {'id': 93,
              'bank_role': 101,
              'slot': 401,
              'anchor': [6, 7],
              'rgba_fnv1a64': '0fcf5a0c3f773e03'},
             {'id': 129,
              'bank_role': 101,
              'slot': 402,
              'anchor': [6, 7],
              'rgba_fnv1a64': '047bb0296b21548b'},
             {'id': 131,
              'bank_role': 101,
              'slot': 403,
              'anchor': [6, 7],
              'rgba_fnv1a64': '6db63fa17b194c7e'}]}
TYPE15_FILES = {'enemy-newsh2-39-8.hda': {'sha256': '05ef7518703365fb05f86ac746679c547a45f8a5b45070ccd0729ae56afdb789',
                           'header_u32': [1010039, 8, 24, 28, 6, 7],
                           'source_png': 'assets/hd/source/enemy-newsh2-39-8-05ef75187033.png',
                           'source_png_sha256': 'ac206bb564bec2580d4c855e1f19d6bc345d6b61f0ad0d5a3b376785371f92fd'},
 'enemy-newsh2-41-8.hda': {'sha256': 'd4163c85bdc7ee1939e9d660b740d6e2d55aa89782f3e3f5924e268023347858',
                           'header_u32': [1010041, 8, 24, 28, 6, 7],
                           'source_png': 'assets/hd/source/enemy-newsh2-41-8-d4163c85bdc7.png',
                           'source_png_sha256': '86f4e17e7ea612354bb5269042823f903ecb6752caac327e51685788ef0c5253'},
 'enemy-newsh2-43-8.hda': {'sha256': 'a9ddb87c4e992f35f979bd72b74224e222391143685698a328c6ac232a782024',
                           'header_u32': [1010043, 8, 24, 28, 6, 7],
                           'source_png': 'assets/hd/source/enemy-newsh2-43-8-a9ddb87c4e99.png',
                           'source_png_sha256': '062b51b9bd0e69ecd120d2dc52ba76b8cf0aa46a644064c415ea07244dd0b3c2'},
 'enemy-newsh2-45-8.hda': {'sha256': '7d1b67817748f18a872e0fd3e7d406fcc9368ff24cd4d21821b4a9738b2742ed',
                           'header_u32': [1010045, 8, 24, 28, 6, 7],
                           'source_png': 'assets/hd/source/enemy-newsh2-45-8-7d1b67817748.png',
                           'source_png_sha256': 'e2ba6c708dfa1f65800b16200406bc305696c845d465cb3ca163d8ca28664c56'},
 'enemy-newsh2-91-8.hda': {'sha256': 'b155c5acbd304177806891b3016b424b68cfaebfcb5d59e7859974a64cea4782',
                           'header_u32': [1010091, 8, 24, 28, 6, 7],
                           'source_png': 'assets/hd/source/enemy-newsh2-91-8-b155c5acbd30.png',
                           'source_png_sha256': 'c33fa6d349db74237335c669f26e4a31dce8b9bfab74d64d62374e6744aff2aa'},
 'enemy-newsh2-93-8.hda': {'sha256': 'b4dc068e25d0de509ae4dee737846ae379e3ca73a7a10561b8c5e274620547a0',
                           'header_u32': [1010093, 8, 24, 28, 6, 7],
                           'source_png': 'assets/hd/source/enemy-newsh2-93-8-b4dc068e25d0.png',
                           'source_png_sha256': 'a3b93abe0d4ec98de786c3bfc4a9b3ebc35ebc3a7d7c0011baf7f0787d001e01'},
 'enemy-newsh2-129-8.hda': {'sha256': 'd8c12921aacc495d6185f8cb3675a7b6cee2203b44892196c77919152f530772',
                            'header_u32': [1010129, 8, 24, 28, 6, 7],
                            'source_png': 'assets/hd/source/enemy-newsh2-129-8-d8c12921aacc.png',
                            'source_png_sha256': 'e9c663f122d929d58c2a68d99e345a3b0491ade6d2a364862189a8135b6406b2'},
 'enemy-newsh2-131-8.hda': {'sha256': '95b80dffe530d276e446bb3716afeb2799dd2fe9f5db4c0f2f867750a0dbdbb0',
                            'header_u32': [1010131, 8, 24, 28, 6, 7],
                            'source_png': 'assets/hd/source/enemy-newsh2-131-8-95b80dffe530.png',
                            'source_png_sha256': '387117cae5b8e1f453c0d583875239f22bd950610b51aae4a8f017e06eb36ed0'}}
TYPE15_PNGS = {'05ef7518703365fb05f86ac746679c547a45f8a5b45070ccd0729ae56afdb789': {'path': 'assets/hd/source/enemy-newsh2-39-8-05ef75187033.png',
                                                                      'sha256': 'ac206bb564bec2580d4c855e1f19d6bc345d6b61f0ad0d5a3b376785371f92fd',
                                                                      'RGBA_sha256': '7e3217226aa7251e6a579f8846b8746a133a6059eb296321d50971a313a65f6a'},
 'd4163c85bdc7ee1939e9d660b740d6e2d55aa89782f3e3f5924e268023347858': {'path': 'assets/hd/source/enemy-newsh2-41-8-d4163c85bdc7.png',
                                                                      'sha256': '86f4e17e7ea612354bb5269042823f903ecb6752caac327e51685788ef0c5253',
                                                                      'RGBA_sha256': '1de777936b538f15d01ed4db3abb982a1619511f961b4c97277b66b7efee847f'},
 'a9ddb87c4e992f35f979bd72b74224e222391143685698a328c6ac232a782024': {'path': 'assets/hd/source/enemy-newsh2-43-8-a9ddb87c4e99.png',
                                                                      'sha256': '062b51b9bd0e69ecd120d2dc52ba76b8cf0aa46a644064c415ea07244dd0b3c2',
                                                                      'RGBA_sha256': '0be4f0c0a31b00e2e1bae39ee4ee15811366942285a3b422504ab798a0ea33ed'},
 '7d1b67817748f18a872e0fd3e7d406fcc9368ff24cd4d21821b4a9738b2742ed': {'path': 'assets/hd/source/enemy-newsh2-45-8-7d1b67817748.png',
                                                                      'sha256': 'e2ba6c708dfa1f65800b16200406bc305696c845d465cb3ca163d8ca28664c56',
                                                                      'RGBA_sha256': '515febe276a5424acf5bfd3c785dfd3fe6a6b5e0d61841007617df984ce8ef43'},
 'b155c5acbd304177806891b3016b424b68cfaebfcb5d59e7859974a64cea4782': {'path': 'assets/hd/source/enemy-newsh2-91-8-b155c5acbd30.png',
                                                                      'sha256': 'c33fa6d349db74237335c669f26e4a31dce8b9bfab74d64d62374e6744aff2aa',
                                                                      'RGBA_sha256': '1799a631ff2f09c28f81df3cb56cdd32274002f619c094e94dcdb5deb950c12b'},
 'b4dc068e25d0de509ae4dee737846ae379e3ca73a7a10561b8c5e274620547a0': {'path': 'assets/hd/source/enemy-newsh2-93-8-b4dc068e25d0.png',
                                                                      'sha256': 'a3b93abe0d4ec98de786c3bfc4a9b3ebc35ebc3a7d7c0011baf7f0787d001e01',
                                                                      'RGBA_sha256': 'f47e26ba64b9928c0f7606152a080e5dee00fc2207f90ccff820bc2b8b30619f'},
 'd8c12921aacc495d6185f8cb3675a7b6cee2203b44892196c77919152f530772': {'path': 'assets/hd/source/enemy-newsh2-129-8-d8c12921aacc.png',
                                                                      'sha256': 'e9c663f122d929d58c2a68d99e345a3b0491ade6d2a364862189a8135b6406b2',
                                                                      'RGBA_sha256': '5f6c221ac670921adebee2ca67bd958abcf398e6ad4568fcb419c96bd0ae1230'},
 '95b80dffe530d276e446bb3716afeb2799dd2fe9f5db4c0f2f867750a0dbdbb0': {'path': 'assets/hd/source/enemy-newsh2-131-8-95b80dffe530.png',
                                                                      'sha256': '387117cae5b8e1f453c0d583875239f22bd950610b51aae4a8f017e06eb36ed0',
                                                                      'RGBA_sha256': '71d3b1b35cf73bbc719c349a15bbebc1dc3370593ca8cbe6d2935c36605f0f68'}}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def independent_fnv(data):
    result = 0xcbf29ce484222325
    for byte in data:
        result ^= byte
        result = (result * 0x100000001b3) % (1 << 64)
    return result


def project_type15_family(test, manifest):
    """Validate the complete finite append before removing it from a copy."""
    packs = manifest['packs']
    present = ('enemy_type15_eightheading_v1' in manifest or
               any(name in pack['files'] for pack in packs.values() for name in TYPE15_FILES) or
               any(stamp in manifest['source_pngs'] for stamp in TYPE15_PNGS))
    if not present:
        return
    test.assertIn('enemy_type15_eightheading_v1', manifest)
    family = manifest.pop('enemy_type15_eightheading_v1')
    test.assertEqual({k: v for k, v in family.items() if k != 'runtime_status'}, TYPE15)
    source = ROOT / TYPE15['source']
    test.assertEqual(sha((source / 'inventory.json').read_bytes()), TYPE15['source_inventory_sha256'])
    test.assertEqual(sha((source / 'IMPORT.json').read_bytes()), TYPE15['import_sha256'])
    defaults = {manifest['default_preview_pack'], manifest['default_debug_pack']}
    test.assertEqual(len(defaults), 2)
    # No alias or duplicate source-index entry may hide beside the eight pins.
    stems = tuple(f'enemy-newsh2-{identity}-8-' for identity in TYPE15['ids'])
    test.assertEqual({stamp for stamp, item in manifest['source_pngs'].items()
                      if Path(item['path']).name.startswith(stems)}, set(TYPE15_PNGS))
    for stamp, expected in TYPE15_PNGS.items():
        test.assertIn(stamp, manifest['source_pngs'])
        test.assertEqual(manifest['source_pngs'].pop(stamp), expected)
    for filename, expected in TYPE15_FILES.items():
        test.assertEqual({name for name, pack in packs.items() if filename in pack['files']}, defaults)
        png = ROOT / expected['source_png']
        test.assertEqual(sha(png.read_bytes()), expected['source_png_sha256'])
        with Image.open(png) as image:
            test.assertEqual((image.mode, image.size), ('RGBA', (192, 224)))
            rgba = image.tobytes()
        test.assertEqual(sha(rgba), TYPE15_PNGS[expected['sha256']]['RGBA_sha256'])
        for name in defaults:
            pack = packs[name]
            test.assertEqual(pack['count'], len(pack['files']))
            test.assertEqual(pack['files'].pop(filename), expected)
            raw = (ROOT / 'assets/hd/packs' / name / filename).read_bytes()
            test.assertEqual(sha(raw), expected['sha256'])
            test.assertEqual(raw[:28], b'HDR1' + struct.pack('<6I', *expected['header_u32']))
            test.assertEqual(raw[28:], rgba)
            pack['count'] -= 1

# Exact frozen six-member append; complete validation precedes projection.
LATE_SPIKE = {'schema': 'late-spike-six-v1',
 'source': 'assets/hd/artwork/late-spike-v1',
 'source_manifest_sha256': '618dd16ebcecddb12bfe6fbfbd3d3327d9f03453ea965ee178026c6911ba564b',
 'source_contract_sha256': '6e4ce3085bac59d7b9256b937e34ee5604f10f176b2a316d91d53d528d2489e2',
 'bank_id': 1,
 'bank_role': 101,
 'ids': [1, 3, 5, 7, 9, 11],
 'actor_types': [23, 22, 21, 18, 19, 20],
 'slots': [404, 405, 406, 407, 408, 409],
 'density': 8,
 'logical_size': [24, 28],
 'anchor': [6, 7],
 'runtime_components': [0, 1, 19, 20],
 'links': [7, 8, 9, 10],
 'row_actor_counts': [7, 9, 8, 9],
 'opaque_logical_cells': 1482,
 'original_alpha_exact': True,
 'fallback': 'All six approved members required before any replacement; 8x-only selected-pack '
             'cached fallback is local to this family',
 'entries': [{'id': 1,
              'bank_role': 101,
              'slot': 404,
              'anchor': [6, 7],
              'rgba_fnv1a64': 'a200c71744dfb67d'},
             {'id': 3,
              'bank_role': 101,
              'slot': 405,
              'anchor': [6, 7],
              'rgba_fnv1a64': '16563f2a13fd9d20'},
             {'id': 5,
              'bank_role': 101,
              'slot': 406,
              'anchor': [6, 7],
              'rgba_fnv1a64': 'a61fd6d4144d8607'},
             {'id': 7,
              'bank_role': 101,
              'slot': 407,
              'anchor': [6, 7],
              'rgba_fnv1a64': '41e6f49abb0f073e'},
             {'id': 9,
              'bank_role': 101,
              'slot': 408,
              'anchor': [6, 7],
              'rgba_fnv1a64': '7431a5a306d38062'},
             {'id': 11,
              'bank_role': 101,
              'slot': 409,
              'anchor': [6, 7],
              'rgba_fnv1a64': '57fb1ddb756b7bd3'}]}
LATE_SPIKE_FILES = {'enemy-newsh2-1-8.hda': {'sha256': '12d0e796610fd19d143ded9f14780f1174e74fb8de116914c0ce9c6d8f9e7056',
                          'header_u32': [1010001, 8, 24, 28, 6, 7],
                          'source_png': 'assets/hd/source/enemy-newsh2-1-8-12d0e796610f.png',
                          'source_png_sha256': '8afe42200a811bdd5c08ffd5f5c0ecb3be798dfe2c5e1d41c9c1f6cbbcbc3f2a'},
 'enemy-newsh2-3-8.hda': {'sha256': '05d5d8933937d6a43036e6aed32f42eaa56734912732319b2628b298169d22e1',
                          'header_u32': [1010003, 8, 24, 28, 6, 7],
                          'source_png': 'assets/hd/source/enemy-newsh2-3-8-05d5d8933937.png',
                          'source_png_sha256': '67b0c0a5e3c7aa66b36fc0c6b7976d541362cd2894f63b3258c46edcce208cf3'},
 'enemy-newsh2-5-8.hda': {'sha256': '35c2ccfaaeb7fdf4d07822fcf546ac62fa6902cbf2af0ceeeab0ad58e39a2a16',
                          'header_u32': [1010005, 8, 24, 28, 6, 7],
                          'source_png': 'assets/hd/source/enemy-newsh2-5-8-35c2ccfaaeb7.png',
                          'source_png_sha256': '9fb1ed718ae2df0d9d49e252ed5ec765a4a2f6a6c4d6868ea5e4233862752fbd'},
 'enemy-newsh2-7-8.hda': {'sha256': '79eafc3e09c23aa0abfa5d2f690a10743feaaa2ddfb52468e5fe17e1c3cec206',
                          'header_u32': [1010007, 8, 24, 28, 6, 7],
                          'source_png': 'assets/hd/source/enemy-newsh2-7-8-79eafc3e09c2.png',
                          'source_png_sha256': '2c9e5a02a72a38a0751c70d54106fa61ac91f84373b1ae77da08f5509fccbdd0'},
 'enemy-newsh2-9-8.hda': {'sha256': 'd6d887db8394c4281b71c61e87822eace10a315e17eb0cc864e985c522af642d',
                          'header_u32': [1010009, 8, 24, 28, 6, 7],
                          'source_png': 'assets/hd/source/enemy-newsh2-9-8-d6d887db8394.png',
                          'source_png_sha256': '65885a03d14eaae92748a58cd7956c32fe325391d11f4175bf6931585dd7a5f9'},
 'enemy-newsh2-11-8.hda': {'sha256': '9261575e58075da2fc8c717a405dfbf6f1ae2d881f4a0b3f722d26c80f49fd20',
                           'header_u32': [1010011, 8, 24, 28, 6, 7],
                           'source_png': 'assets/hd/source/enemy-newsh2-11-8-9261575e5807.png',
                           'source_png_sha256': 'fabc6d16e95b4b01538e8945f4b4172e42c683f1d1797e3e9dedef0a11963574'}}
LATE_SPIKE_PNGS = {'12d0e796610fd19d143ded9f14780f1174e74fb8de116914c0ce9c6d8f9e7056': {'path': 'assets/hd/source/enemy-newsh2-1-8-12d0e796610f.png',
                                                                      'sha256': '8afe42200a811bdd5c08ffd5f5c0ecb3be798dfe2c5e1d41c9c1f6cbbcbc3f2a',
                                                                      'RGBA_sha256': '388c688b822c91bb812e4d3fae8a35db689c1763e8efefb3c6a3947946f4dbc8'},
 '05d5d8933937d6a43036e6aed32f42eaa56734912732319b2628b298169d22e1': {'path': 'assets/hd/source/enemy-newsh2-3-8-05d5d8933937.png',
                                                                      'sha256': '67b0c0a5e3c7aa66b36fc0c6b7976d541362cd2894f63b3258c46edcce208cf3',
                                                                      'RGBA_sha256': '8e214f3bd0f788d095700153624c4a47f998a39641262679cb341881060a3e5f'},
 '35c2ccfaaeb7fdf4d07822fcf546ac62fa6902cbf2af0ceeeab0ad58e39a2a16': {'path': 'assets/hd/source/enemy-newsh2-5-8-35c2ccfaaeb7.png',
                                                                      'sha256': '9fb1ed718ae2df0d9d49e252ed5ec765a4a2f6a6c4d6868ea5e4233862752fbd',
                                                                      'RGBA_sha256': '6429eda4001547f8362578927c3008c893e4cd49e8f829fb53f6714fe638a4ff'},
 '79eafc3e09c23aa0abfa5d2f690a10743feaaa2ddfb52468e5fe17e1c3cec206': {'path': 'assets/hd/source/enemy-newsh2-7-8-79eafc3e09c2.png',
                                                                      'sha256': '2c9e5a02a72a38a0751c70d54106fa61ac91f84373b1ae77da08f5509fccbdd0',
                                                                      'RGBA_sha256': '6e08509b266ff3094be5ddd42108108a585cf3f5c763f488b83c633f5490b772'},
 'd6d887db8394c4281b71c61e87822eace10a315e17eb0cc864e985c522af642d': {'path': 'assets/hd/source/enemy-newsh2-9-8-d6d887db8394.png',
                                                                      'sha256': '65885a03d14eaae92748a58cd7956c32fe325391d11f4175bf6931585dd7a5f9',
                                                                      'RGBA_sha256': '4f21c35069c159014fca138e19f3c67008be8132759326159a232e8699cc1bd2'},
 '9261575e58075da2fc8c717a405dfbf6f1ae2d881f4a0b3f722d26c80f49fd20': {'path': 'assets/hd/source/enemy-newsh2-11-8-9261575e5807.png',
                                                                      'sha256': 'fabc6d16e95b4b01538e8945f4b4172e42c683f1d1797e3e9dedef0a11963574',
                                                                      'RGBA_sha256': '6532dc4acec66bd536dfce3f36fc6b1052cdfe6b4bb0a9fdc158d2c8b909a68b'}}

def project_late_spike_family(test, manifest):
    """Validate the complete finite append before removing it from a copy."""
    packs = manifest['packs']
    present = ('late_spike_v1' in manifest or
               any(name in pack['files'] for pack in packs.values() for name in LATE_SPIKE_FILES) or
               any(stamp in manifest['source_pngs'] for stamp in LATE_SPIKE_PNGS))
    if not present:
        return
    test.assertIn('late_spike_v1', manifest)
    family = manifest.pop('late_spike_v1')
    test.assertEqual({k: v for k, v in family.items() if k != 'runtime_status'}, LATE_SPIKE)
    source = ROOT / LATE_SPIKE['source']
    test.assertEqual(sha((source / 'manifest.json').read_bytes()), LATE_SPIKE['source_manifest_sha256'])
    test.assertEqual(sha((source / 'contract.json').read_bytes()), LATE_SPIKE['source_contract_sha256'])
    defaults = {manifest['default_preview_pack'], manifest['default_debug_pack']}
    test.assertEqual(len(defaults), 2)
    # No alias or duplicate source-index entry may hide beside the eight pins.
    stems = tuple(f'enemy-newsh2-{identity}-8-' for identity in LATE_SPIKE['ids'])
    test.assertEqual({stamp for stamp, item in manifest['source_pngs'].items()
                      if Path(item['path']).name.startswith(stems)}, set(LATE_SPIKE_PNGS))
    for stamp, expected in LATE_SPIKE_PNGS.items():
        test.assertIn(stamp, manifest['source_pngs'])
        test.assertEqual(manifest['source_pngs'].pop(stamp), expected)
    for filename, expected in LATE_SPIKE_FILES.items():
        test.assertEqual({name for name, pack in packs.items() if filename in pack['files']}, defaults)
        png = ROOT / expected['source_png']
        test.assertEqual(sha(png.read_bytes()), expected['source_png_sha256'])
        with Image.open(png) as image:
            test.assertEqual((image.mode, image.size), ('RGBA', (192, 224)))
            rgba = image.tobytes()
        test.assertEqual(sha(rgba), LATE_SPIKE_PNGS[expected['sha256']]['RGBA_sha256'])
        for name in defaults:
            pack = packs[name]
            test.assertEqual(pack['count'], len(pack['files']))
            test.assertEqual(pack['files'].pop(filename), expected)
            raw = (ROOT / 'assets/hd/packs' / name / filename).read_bytes()
            test.assertEqual(sha(raw), expected['sha256'])
            test.assertEqual(raw[:28], b'HDR1' + struct.pack('<6I', *expected['header_u32']))
            test.assertEqual(raw[28:], rgba)
            pack['count'] -= 1


# Exact frozen entry-craft append; prior pinned entries remain unchanged.
NEWSH4_ENTRY6 = {'schema': 'newsh4-entry-six-v1',
 'source': 'assets/hd/artwork/newsh4-entry6-v1',
 'source_manifest_sha256': '96c59e764ab2456d51476ba00f0c27e423fa4758469c512791c95d1e4dd87f04',
 'source_contract_sha256': '9a1e8d8da2a4439e41b9c462289ca132099efc4ab27bb627ef48badae9764153',
 'density': 8,
 'logical_size': [24, 28],
 'anchor': [6, 7],
 'assembly_size': [72, 52],
 'ids': [81, 83, 85, 119, 121, 123],
 'slots': [410, 411, 412, 413, 414, 415],
 'actor_types': [468, 469, 470, 471, 472, 473],
 'bank_id': 2,
 'bank_role': 102,
 'runtime_components': [0, 1, 19, 20],
 'source_order_placements': [[123, 48, 24],
                             [81, 0, 0],
                             [83, 24, 0],
                             [85, 48, 0],
                             [119, 0, 24],
                             [121, 24, 24]],
 'vertical_stride': 24,
 'row_envelope_overlap': 4,
 'summed_opaque_logical_cells': 1768,
 'union_opaque_logical_cells': 1635,
 'overlap_opaque_logical_cells': 133,
 'original_alpha_exact': True,
 'source_armor': 0,
 'constructed_avail': 2,
 'constructed_armor': 255,
 'preserve_recycled_scoreitem': True,
 'excluded_boss_bases': [86, 124],
 'fallback': 'All six approved members required before any replacement; '
             '8x-only selected-pack cached fallback is local to this family',
 'entries': [{'bank_role': 102,
              'id': 81,
              'slot': 410,
              'anchor': [6, 7],
              'rgba_fnv1a64': 'd568531aec92422c'},
             {'bank_role': 102,
              'id': 83,
              'slot': 411,
              'anchor': [6, 7],
              'rgba_fnv1a64': 'bf0fa10dfdd98241'},
             {'bank_role': 102,
              'id': 85,
              'slot': 412,
              'anchor': [6, 7],
              'rgba_fnv1a64': '095506cac33b7e8e'},
             {'bank_role': 102,
              'id': 119,
              'slot': 413,
              'anchor': [6, 7],
              'rgba_fnv1a64': '568183ac9f82133c'},
             {'bank_role': 102,
              'id': 121,
              'slot': 414,
              'anchor': [6, 7],
              'rgba_fnv1a64': 'bd0f65394c14826d'},
             {'bank_role': 102,
              'id': 123,
              'slot': 415,
              'anchor': [6, 7],
              'rgba_fnv1a64': 'd3f58ab88accaf9d'}]}
NEWSH4_ENTRY6_FILES = {'enemy-newsh4-81-8.hda': {'sha256': 'd78b6ba515aba9ef724bf1acefc494695b2933c3242e4d9877d121790c2f82ee',
                           'header_u32': [1020081, 8, 24, 28, 6, 7],
                           'source_png': 'assets/hd/source/enemy-newsh4-81-8-d78b6ba515ab.png',
                           'source_png_sha256': '11501a276a5c8aa75f8bd6f79a309b900f8391af0f3343a84402068157ce200f'},
 'enemy-newsh4-83-8.hda': {'sha256': 'e5c0a248adc1a809229edd587b6f17b336bd1a7fb4c378d7763d2f228c416469',
                           'header_u32': [1020083, 8, 24, 28, 6, 7],
                           'source_png': 'assets/hd/source/enemy-newsh4-83-8-e5c0a248adc1.png',
                           'source_png_sha256': '2272fbde064bf7ffaadc456c998ca33bd48cd1517cc4aea68d210c2d6ca9b832'},
 'enemy-newsh4-85-8.hda': {'sha256': 'a6b713aa635127db3823983b0570b1ed84b279a3c6be9a5771d79dfe0bcd78f7',
                           'header_u32': [1020085, 8, 24, 28, 6, 7],
                           'source_png': 'assets/hd/source/enemy-newsh4-85-8-a6b713aa6351.png',
                           'source_png_sha256': 'ce5485a8ec6cc54cd8f8e469b9fbd4d6ac78d8b12208bc7511946397c6074a53'},
 'enemy-newsh4-119-8.hda': {'sha256': '19c097ad5174af544b505d48664c74bb6c3e7cc6d3ce12923c11196aebab6ccf',
                            'header_u32': [1020119, 8, 24, 28, 6, 7],
                            'source_png': 'assets/hd/source/enemy-newsh4-119-8-19c097ad5174.png',
                            'source_png_sha256': '97235d1dc7c2db7b12734a6063e6e93f24352cda376b86769513364fa8684eaf'},
 'enemy-newsh4-121-8.hda': {'sha256': '32deb03acb4403f8c655480ca6e96f3854c7c98260241f6c38a47b4c87a1d949',
                            'header_u32': [1020121, 8, 24, 28, 6, 7],
                            'source_png': 'assets/hd/source/enemy-newsh4-121-8-32deb03acb44.png',
                            'source_png_sha256': '23309e94a8991cb60c1e8cb14d61b0b50a38fcf985404740986727ee741dbfda'},
 'enemy-newsh4-123-8.hda': {'sha256': 'cb8dcc2ff7fe9a5cee036cb1c4ccf381db6cf9d272cb8f30f62d2c4efaee10d7',
                            'header_u32': [1020123, 8, 24, 28, 6, 7],
                            'source_png': 'assets/hd/source/enemy-newsh4-123-8-cb8dcc2ff7fe.png',
                            'source_png_sha256': '7190bc9759884556e44e475aa5132196d7dce67e4480104c8bee5de7b01c0516'}}
NEWSH4_ENTRY6_PNGS = {'d78b6ba515aba9ef724bf1acefc494695b2933c3242e4d9877d121790c2f82ee': {'path': 'assets/hd/source/enemy-newsh4-81-8-d78b6ba515ab.png',
                                                                      'sha256': '11501a276a5c8aa75f8bd6f79a309b900f8391af0f3343a84402068157ce200f',
                                                                      'RGBA_sha256': 'ba540e76525c3d3c195f2bccb02ae292b2498aaf06c84333169ec581bb378a9c'},
 'e5c0a248adc1a809229edd587b6f17b336bd1a7fb4c378d7763d2f228c416469': {'path': 'assets/hd/source/enemy-newsh4-83-8-e5c0a248adc1.png',
                                                                      'sha256': '2272fbde064bf7ffaadc456c998ca33bd48cd1517cc4aea68d210c2d6ca9b832',
                                                                      'RGBA_sha256': 'af3660e983649de1d3cba25d383a2070a143c7074900b8cbc994300c4fd605f7'},
 'a6b713aa635127db3823983b0570b1ed84b279a3c6be9a5771d79dfe0bcd78f7': {'path': 'assets/hd/source/enemy-newsh4-85-8-a6b713aa6351.png',
                                                                      'sha256': 'ce5485a8ec6cc54cd8f8e469b9fbd4d6ac78d8b12208bc7511946397c6074a53',
                                                                      'RGBA_sha256': '84bbe1014d5231dcb9bb7f59788b224d70b7ea0bf64eded43c699f4e29e36b4e'},
 '19c097ad5174af544b505d48664c74bb6c3e7cc6d3ce12923c11196aebab6ccf': {'path': 'assets/hd/source/enemy-newsh4-119-8-19c097ad5174.png',
                                                                      'sha256': '97235d1dc7c2db7b12734a6063e6e93f24352cda376b86769513364fa8684eaf',
                                                                      'RGBA_sha256': '3b0031b1e4f157e577f97cb9626d080f9e94dfbf1b019b1cf076fbfab98b23ee'},
 '32deb03acb4403f8c655480ca6e96f3854c7c98260241f6c38a47b4c87a1d949': {'path': 'assets/hd/source/enemy-newsh4-121-8-32deb03acb44.png',
                                                                      'sha256': '23309e94a8991cb60c1e8cb14d61b0b50a38fcf985404740986727ee741dbfda',
                                                                      'RGBA_sha256': '29c751affe8475127803800fe43e3682c46aa0da0c4c36ee112cd8337fbccbd9'},
 'cb8dcc2ff7fe9a5cee036cb1c4ccf381db6cf9d272cb8f30f62d2c4efaee10d7': {'path': 'assets/hd/source/enemy-newsh4-123-8-cb8dcc2ff7fe.png',
                                                                      'sha256': '7190bc9759884556e44e475aa5132196d7dce67e4480104c8bee5de7b01c0516',
                                                                      'RGBA_sha256': 'e787e60ce85ba69e760c027f69bf61243a7ddf756c99d0261a38c6ded3f84972'}}

def project_newsh4_entry6_family(test, manifest):
    """Validate the complete finite append before removing it from a copy."""
    packs = manifest['packs']
    present = ('newsh4_entry6_v1' in manifest or
               any(name in pack['files'] for pack in packs.values() for name in NEWSH4_ENTRY6_FILES) or
               any(stamp in manifest['source_pngs'] for stamp in NEWSH4_ENTRY6_PNGS))
    if not present:
        return
    test.assertIn('newsh4_entry6_v1', manifest)
    family = manifest.pop('newsh4_entry6_v1')
    test.assertEqual({k: v for k, v in family.items() if k != 'runtime_status'}, NEWSH4_ENTRY6)
    source = ROOT / NEWSH4_ENTRY6['source']
    test.assertEqual(sha((source / 'manifest.json').read_bytes()), NEWSH4_ENTRY6['source_manifest_sha256'])
    test.assertEqual(sha((source / 'contract.json').read_bytes()), NEWSH4_ENTRY6['source_contract_sha256'])
    defaults = {manifest['default_preview_pack'], manifest['default_debug_pack']}
    test.assertEqual(len(defaults), 2)
    # No alias or duplicate source-index entry may hide beside the six pins.
    stems = tuple(f'enemy-newsh4-{identity}-8-' for identity in NEWSH4_ENTRY6['ids'])
    test.assertEqual({stamp for stamp, item in manifest['source_pngs'].items()
                      if Path(item['path']).name.startswith(stems)}, set(NEWSH4_ENTRY6_PNGS))
    for stamp, expected in NEWSH4_ENTRY6_PNGS.items():
        test.assertIn(stamp, manifest['source_pngs'])
        test.assertEqual(manifest['source_pngs'].pop(stamp), expected)
    for filename, expected in NEWSH4_ENTRY6_FILES.items():
        test.assertEqual({name for name, pack in packs.items() if filename in pack['files']}, defaults)
        png = ROOT / expected['source_png']
        test.assertEqual(sha(png.read_bytes()), expected['source_png_sha256'])
        with Image.open(png) as image:
            test.assertEqual((image.mode, image.size), ('RGBA', (192, 224)))
            rgba = image.tobytes()
        test.assertEqual(sha(rgba), NEWSH4_ENTRY6_PNGS[expected['sha256']]['RGBA_sha256'])
        for name in defaults:
            pack = packs[name]
            test.assertEqual(pack['count'], len(pack['files']))
            test.assertEqual(pack['files'].pop(filename), expected)
            raw = (ROOT / 'assets/hd/packs' / name / filename).read_bytes()
            test.assertEqual(sha(raw), expected['sha256'])
            test.assertEqual(raw[:28], b'HDR1' + struct.pack('<6I', *expected['header_u32']))
            test.assertEqual(raw[28:], rgba)
            pack['count'] -= 1


class TitlePackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = ROOT / 'assets/hd/artwork/title-screen-v1'
        cls.runtime = ROOT / 'assets/hd/packs/startup-title-v1'
        cls.manifest = json.loads((ROOT / 'assets/hd/manifest.json').read_text())
        cls.bundles = bundle.build_bundles(ROOT)
        cls.family = cls.manifest['startup_title_v1']

    def test_exact_headers_hashes_and_canonical_payloads(self):
        self.assertEqual(struct.calcsize('<4s11I4Q'), 80)
        for filename, (asset, identity, w, h, alpha, bounds, indices, mask, payload_fnv, size, digest) in EXPECTED.items():
            with self.subTest(filename=filename):
                raw = (self.runtime / filename).read_bytes()
                fields = struct.unpack('<4s11I4Q', raw[:80])
                self.assertEqual(fields, (b'TLV1', 1, 4, identity, w, h, 8, alpha,
                                          w * h * 64, 0, 0, 0,
                                          indices, mask, 0x8f64628a08533287, payload_fnv))
                self.assertEqual(len(raw), size)
                self.assertEqual(sha(raw), digest)
                self.assertEqual(independent_fnv(raw[80:]), payload_fnv)
                with Image.open(self.source / 'canonical' / (asset + '-canonical4x.png')) as image:
                    self.assertEqual(image.mode, 'RGBA')
                    self.assertEqual(image.size, (w * 4, h * 4))
                    self.assertEqual(raw[80:], image.tobytes())
                self.assertEqual(self.family['files'][filename]['header_u32'], list(fields[1:12]))

    def test_opaque_background_straight_alpha_and_exact_support(self):
        for filename, (_, _, w, h, alpha_mode, bounds, *_) in EXPECTED.items():
            payload = (self.runtime / filename).read_bytes()[80:]
            image = Image.frombytes('RGBA', (w * 4, h * 4), payload)
            alpha = image.getchannel('A')
            if alpha_mode == 0:
                self.assertEqual(alpha.getextrema(), (255, 255))
            else:
                self.assertTrue(any(0 < value < 255 for value in alpha.tobytes()))
                self.assertEqual(alpha.getbbox(), bounds)
                for y in range(h * 4):
                    row = alpha.tobytes()[y * w * 4:(y + 1) * w * 4]
                    outside = row if y < bounds[1] or y >= bounds[3] else row[:bounds[0]] + row[bounds[2]:]
                    self.assertFalse(any(outside))
            self.assertTrue(all(payload[i:i + 3] == b'\0\0\0'
                                for i in range(0, len(payload), 4) if payload[i + 3] == 0))

    def test_frozen_source_inventory_and_generated_raster_scope(self):
        self.assertEqual(sha((self.source / 'manifest.json').read_bytes()), SOURCE_MANIFEST)
        self.assertEqual(len(self.family['source_files']), 19)
        actual = {p.relative_to(self.source).as_posix() for p in self.source.rglob('*') if p.is_file()}
        self.assertEqual(actual, set(self.family['source_files']))
        self.assertEqual({name for name in actual if name.endswith('.png')}, {
            'canonical/pic4-canonical4x.png', 'canonical/tyrian146-canonical4x.png',
            'canonical/year151-canonical4x.png', 'masters/left-clearance-master.png',
            'masters/pic4-master.png', 'masters/right-clearance-master.png',
            'masters/tyrian146-master.png', 'masters/year151-master.png',
            'proof/tyrian-alpha-correction-boundary-mask4x.png',
        })
        for name, receipt in self.family['source_files'].items():
            raw = (self.source / name).read_bytes()
            self.assertEqual(receipt, {'bytes': len(raw), 'sha256': sha(raw)})
        source_manifest = json.loads((self.source / 'manifest.json').read_text())
        self.assertEqual(len(source_manifest['files']), 17)
        self.assertEqual(source_manifest['total_bytes_excluding_manifest_and_FILES'], 8997880)
        self.assertIn('alpha only from two generated component masters', (self.source / 'README.md').read_text())
        self.assertIn('Original game image pixels', (self.source / 'README.md').read_text())
        self.assertEqual((self.source / 'requirements.txt').read_text().strip(), 'Pillow==12.3.0')

    def test_late_spike_coexistence_guard_rejects_mutations(self):
        original = self.manifest
        self.assertIn('late_spike_v1', original)
        for case in ('missing-base1', 'foreign-bank-header', 'wrong-size-header',
                     'unexpected-member', 'changed-member', 'changed-png-receipt',
                     'missing-png-index', 'changed-png-index', 'changed-rgba-index',
                     'duplicate-png-index', 'foreign-pack', 'changed-family-metadata',
                     'changed-row-counts', 'extra-family-field', 'missing-family'):
            with self.subTest(case=case):
                changed = json.loads(json.dumps(original))
                pack = changed['packs'][changed['default_preview_pack']]
                filename = 'enemy-newsh2-1-8.hda'
                receipt = pack['files'][filename]
                stamp = receipt['sha256']
                if case == 'missing-base1':
                    del pack['files'][filename]
                    pack['count'] -= 1
                elif case == 'foreign-bank-header':
                    receipt['header_u32'][0] = 1020001
                elif case == 'wrong-size-header':
                    receipt['header_u32'][2] += 1
                elif case == 'unexpected-member':
                    pack['files']['enemy-newsh2-13-8.hda'] = dict(receipt)
                    pack['count'] += 1
                elif case == 'changed-member':
                    receipt['sha256'] = '0' * 64
                elif case == 'changed-png-receipt':
                    receipt['source_png_sha256'] = '0' * 64
                elif case == 'missing-png-index':
                    del changed['source_pngs'][stamp]
                elif case == 'changed-png-index':
                    changed['source_pngs'][stamp]['sha256'] = '0' * 64
                elif case == 'changed-rgba-index':
                    changed['source_pngs'][stamp]['RGBA_sha256'] = '0' * 64
                elif case == 'duplicate-png-index':
                    changed['source_pngs']['0' * 64] = dict(changed['source_pngs'][stamp])
                elif case == 'foreign-pack':
                    other = next(value for name, value in changed['packs'].items()
                                 if name not in {changed['default_preview_pack'], changed['default_debug_pack']})
                    other['files'][filename] = dict(receipt)
                    other['count'] += 1
                elif case == 'changed-family-metadata':
                    changed['late_spike_v1']['bank_role'] = 102
                elif case == 'changed-row-counts':
                    changed['late_spike_v1']['row_actor_counts'].reverse()
                elif case == 'extra-family-field':
                    changed['late_spike_v1']['unapproved'] = True
                else:
                    del changed['late_spike_v1']
                self.manifest = changed
                try:
                    with self.assertRaises(AssertionError):
                        self.test_existing_manifest_fields_and_bytes_unchanged_from_baseline()
                finally:
                    self.manifest = original

    def test_late_spike_coexistence_guard_rejects_changed_artwork_bytes(self):
        # Intercept reads only: shared historical assets are never mutated.
        filename = 'enemy-newsh2-1-8.hda'
        targets = [ROOT / LATE_SPIKE_FILES[filename]['source_png'],
                   ROOT / 'assets/hd/packs' / self.manifest['default_preview_pack'] / filename,
                   ROOT / LATE_SPIKE['source'] / 'manifest.json',
                   ROOT / LATE_SPIKE['source'] / 'contract.json']
        read_bytes = Path.read_bytes
        for target in targets:
            with self.subTest(path=target):
                def changed_bytes(path):
                    raw = read_bytes(path)
                    return raw[:-1] + bytes([raw[-1] ^ 1]) if path == target else raw
                with mock.patch.object(Path, 'read_bytes', changed_bytes):
                    with self.assertRaises(AssertionError):
                        self.test_existing_manifest_fields_and_bytes_unchanged_from_baseline()

    def test_newsh4_entry6_coexistence_guard_rejects_mutations(self):
        original = self.manifest
        self.assertIn('newsh4_entry6_v1', original)
        for case in ('missing-base81', 'foreign-bank-header', 'wrong-size-header',
                     'unexpected-member', 'changed-member', 'changed-png-receipt',
                     'missing-png-index', 'changed-png-index', 'changed-rgba-index',
                     'duplicate-png-index', 'foreign-pack', 'changed-family-metadata',
                     'changed-source-order', 'extra-family-field', 'missing-family'):
            with self.subTest(case=case):
                changed = json.loads(json.dumps(original))
                pack = changed['packs'][changed['default_preview_pack']]
                filename = 'enemy-newsh4-81-8.hda'
                receipt = pack['files'][filename]
                stamp = receipt['sha256']
                if case == 'missing-base81':
                    del pack['files'][filename]
                    pack['count'] -= 1
                elif case == 'foreign-bank-header':
                    receipt['header_u32'][0] = 1010081
                elif case == 'wrong-size-header':
                    receipt['header_u32'][2] += 1
                elif case == 'unexpected-member':
                    pack['files']['enemy-newsh4-86-8.hda'] = dict(receipt)
                    pack['count'] += 1
                elif case == 'changed-member':
                    receipt['sha256'] = '0' * 64
                elif case == 'changed-png-receipt':
                    receipt['source_png_sha256'] = '0' * 64
                elif case == 'missing-png-index':
                    del changed['source_pngs'][stamp]
                elif case == 'changed-png-index':
                    changed['source_pngs'][stamp]['sha256'] = '0' * 64
                elif case == 'changed-rgba-index':
                    changed['source_pngs'][stamp]['RGBA_sha256'] = '0' * 64
                elif case == 'duplicate-png-index':
                    changed['source_pngs']['0' * 64] = dict(changed['source_pngs'][stamp])
                elif case == 'foreign-pack':
                    other = next(value for name, value in changed['packs'].items()
                                 if name not in {changed['default_preview_pack'], changed['default_debug_pack']})
                    other['files'][filename] = dict(receipt)
                    other['count'] += 1
                elif case == 'changed-family-metadata':
                    changed['newsh4_entry6_v1']['bank_role'] = 101
                elif case == 'changed-source-order':
                    changed['newsh4_entry6_v1']['source_order_placements'].reverse()
                elif case == 'extra-family-field':
                    changed['newsh4_entry6_v1']['unapproved'] = True
                else:
                    del changed['newsh4_entry6_v1']
                self.manifest = changed
                try:
                    with self.assertRaises(AssertionError):
                        self.test_existing_manifest_fields_and_bytes_unchanged_from_baseline()
                finally:
                    self.manifest = original

    def test_newsh4_entry6_coexistence_guard_rejects_changed_artwork_bytes(self):
        # Intercept reads only: shared historical assets are never mutated.
        filename = 'enemy-newsh4-81-8.hda'
        targets = [ROOT / NEWSH4_ENTRY6_FILES[filename]['source_png'],
                   ROOT / 'assets/hd/packs' / self.manifest['default_preview_pack'] / filename,
                   ROOT / NEWSH4_ENTRY6['source'] / 'manifest.json',
                   ROOT / NEWSH4_ENTRY6['source'] / 'contract.json']
        read_bytes = Path.read_bytes
        for target in targets:
            with self.subTest(path=target):
                def changed_bytes(path):
                    raw = read_bytes(path)
                    return raw[:-1] + bytes([raw[-1] ^ 1]) if path == target else raw
                with mock.patch.object(Path, 'read_bytes', changed_bytes):
                    with self.assertRaises(AssertionError):
                        self.test_existing_manifest_fields_and_bytes_unchanged_from_baseline()

    def test_type15_coexistence_guard_rejects_mutations(self):
        original = self.manifest
        self.assertIn('enemy_type15_eightheading_v1', original)
        for case in ('missing-base91', 'foreign-bank-header', 'wrong-size-header',
                     'unexpected-member', 'changed-member', 'changed-png-receipt',
                     'missing-png-index', 'changed-png-index', 'changed-rgba-index',
                     'duplicate-png-index', 'foreign-pack', 'changed-family-metadata',
                     'changed-selector-order', 'extra-family-field', 'missing-family'):
            with self.subTest(case=case):
                changed = json.loads(json.dumps(original))
                pack = changed['packs'][changed['default_preview_pack']]
                filename = 'enemy-newsh2-91-8.hda'
                receipt = pack['files'][filename]
                stamp = receipt['sha256']
                if case == 'missing-base91':
                    del pack['files'][filename]
                    pack['count'] -= 1
                elif case == 'foreign-bank-header':
                    receipt['header_u32'][0] = 1020091
                elif case == 'wrong-size-header':
                    receipt['header_u32'][2] += 1
                elif case == 'unexpected-member':
                    pack['files']['enemy-newsh2-133-8.hda'] = dict(receipt)
                    pack['count'] += 1
                elif case == 'changed-member':
                    receipt['sha256'] = '0' * 64
                elif case == 'changed-png-receipt':
                    receipt['source_png_sha256'] = '0' * 64
                elif case == 'missing-png-index':
                    del changed['source_pngs'][stamp]
                elif case == 'changed-png-index':
                    changed['source_pngs'][stamp]['sha256'] = '0' * 64
                elif case == 'changed-rgba-index':
                    changed['source_pngs'][stamp]['RGBA_sha256'] = '0' * 64
                elif case == 'duplicate-png-index':
                    changed['source_pngs']['0' * 64] = dict(changed['source_pngs'][stamp])
                elif case == 'foreign-pack':
                    other = next(value for name, value in changed['packs'].items()
                                 if name not in {changed['default_preview_pack'], changed['default_debug_pack']})
                    other['files'][filename] = dict(receipt)
                    other['count'] += 1
                elif case == 'changed-family-metadata':
                    changed['enemy_type15_eightheading_v1']['bank_role'] = 102
                elif case == 'changed-selector-order':
                    changed['enemy_type15_eightheading_v1']['selector_order'].reverse()
                elif case == 'extra-family-field':
                    changed['enemy_type15_eightheading_v1']['unapproved'] = True
                else:
                    del changed['enemy_type15_eightheading_v1']
                self.manifest = changed
                try:
                    with self.assertRaises(AssertionError):
                        self.test_existing_manifest_fields_and_bytes_unchanged_from_baseline()
                finally:
                    self.manifest = original

    def test_type15_coexistence_guard_rejects_changed_artwork_bytes(self):
        # Intercept reads only: shared historical assets are never mutated.
        filename = 'enemy-newsh2-91-8.hda'
        targets = [ROOT / TYPE15_FILES[filename]['source_png'],
                   ROOT / 'assets/hd/packs' / self.manifest['default_preview_pack'] / filename,
                   ROOT / TYPE15['source'] / 'inventory.json',
                   ROOT / TYPE15['source'] / 'IMPORT.json']
        read_bytes = Path.read_bytes
        for target in targets:
            with self.subTest(path=target):
                def changed_bytes(path):
                    raw = read_bytes(path)
                    return raw[:-1] + bytes([raw[-1] ^ 1]) if path == target else raw
                with mock.patch.object(Path, 'read_bytes', changed_bytes):
                    with self.assertRaises(AssertionError):
                        self.test_existing_manifest_fields_and_bytes_unchanged_from_baseline()

    def test_existing_manifest_fields_and_bytes_unchanged_from_baseline(self):
        baseline = subprocess.check_output(['git', 'show', 'aba8650:assets/hd/manifest.json'], cwd=ROOT)
        without_title = json.loads(json.dumps(self.manifest))
        from settings_font_coexistence import project_settings_family
        project_settings_family(self, without_title)
        project_type3_small_family(self, without_title)
        project_newsh4_entry6_family(self, without_title)
        project_late_spike_family(self, without_title)
        added_menu = without_title.pop('startup_title_menu_v1', None)
        if added_menu is not None:
            sys.path.insert(0, str(ROOT / 'prototype'))
            from title_menu_font_bundle import build_family as menu_family, build_bundles as menu_bundles
            try:
                _, expected_menu = menu_family(ROOT)
                menu_bundles(ROOT)
            except ValueError as error:
                self.fail(str(error))
            self.assertEqual(added_menu, expected_menu)
        project_type15_family(self, without_title)
        opposite = without_title.pop('newsh4_opposite7_v1', None)
        if opposite is not None:
            self.assertEqual({k: v for k, v in opposite.items() if k != 'runtime_status'}, OPPOSITE7)
            self.assertTrue(all(digest in without_title['source_pngs'] for digest in OPPOSITE7_PNGS))
            for key in ['default_preview_pack', 'default_debug_pack']:
                name = without_title[key]
                pack = without_title['packs'][name]
                self.assertEqual(pack['count'], len(pack['files']))
                for filename, expected in OPPOSITE7_FILES.items():
                    receipt = pack['files'].pop(filename)
                    self.assertEqual(receipt, expected)
                    self.assertEqual(sha((ROOT / 'assets/hd/packs' / name / filename).read_bytes()), receipt['sha256'])
                    self.assertEqual(sha((ROOT / receipt['source_png']).read_bytes()), receipt['source_png_sha256'])
                    self.assertEqual(without_title['source_pngs'].get(receipt['sha256'], OPPOSITE7_PNGS[receipt['sha256']]), OPPOSITE7_PNGS[receipt['sha256']])
                    without_title['source_pngs'].pop(receipt['sha256'], None)
                    pack['count'] -= 1
        # A later finite bank2 family may coexist with this title checkpoint.
        # Pin every added receipt to its reviewed source commit before removal;
        # unknown fields, resources, packs and changes to older entries fail.
        added = without_title.pop('newsh4_long7_v1', None)
        if added is not None:
            # Recovery: the original local20cae6e object was never published.
            # Use its published family checkpoint, with the entire manifest
            # pinned; no arbitrary branch/tip or weakened family projection.
            frozen_bytes = subprocess.check_output([
                'git', 'show', '67656d1:assets/hd/manifest.json'], cwd=ROOT)
            self.assertEqual(sha(frozen_bytes), 'c7ca4c55b65fc2d856b2eb85055626596cb7c35940a62bfe9e9a04a564b9559d')
            frozen = json.loads(frozen_bytes)
            self.assertEqual({k: v for k, v in added.items() if k != 'runtime_status'},
                             {k: v for k, v in frozen['newsh4_long7_v1'].items() if k != 'runtime_status'})
            self.assertTrue(all(frozen['packs'][frozen['default_preview_pack']]['files'][f'enemy-newsh4-{i}-8.hda']['sha256'] in without_title['source_pngs'] for i in [153, 155, 157, 159, 191, 193, 195]))
            for key in ['default_preview_pack', 'default_debug_pack']:
                name = without_title[key]
                pack = without_title['packs'][name]
                self.assertEqual(pack['count'], len(pack['files']))
                for identity in [153, 155, 157, 159, 191, 193, 195]:
                    filename = f'enemy-newsh4-{identity}-8.hda'
                    receipt = pack['files'].pop(filename)
                    self.assertEqual(receipt, frozen['packs'][name]['files'][filename])
                    self.assertEqual(sha((ROOT / 'assets/hd/packs' / name / filename).read_bytes()), receipt['sha256'])
                    self.assertEqual(without_title['source_pngs'].get(receipt['sha256'],
                                     frozen['source_pngs'][receipt['sha256']]), frozen['source_pngs'][receipt['sha256']])
                    without_title['source_pngs'].pop(receipt['sha256'], None)
                    pack['count'] -= 1
        del without_title['startup_title_v1']
        self.assertEqual(without_title, json.loads(baseline))
        self.assertEqual((json.dumps(without_title, indent=2) + '\n').encode(), baseline)
        self.assertNotIn('startup-title-v1', self.manifest['packs'])
        self.assertEqual(self.family['count'], 5)
        self.assertEqual(self.family['title_count'], 3)
        self.assertEqual(self.family['manufacturer_compatibility_count'], 2)

    def test_finite_gameplay_coexistence_guard_rejects_mutations(self):
        if 'newsh4_long7_v1' not in self.manifest:
            self.skipTest('Finite gameplay family is absent')
        original = self.manifest
        for case in ['extra-member', 'changed-member', 'count', 'source-png', 'opposite7-member', 'opposite7-png', 'old-title-neighbor']:
            with self.subTest(case=case):
                changed = json.loads(json.dumps(original))
                pack = changed['packs'][changed['default_preview_pack']]
                if case == 'extra-member':
                    pack['files']['enemy-newsh4-197-8.hda'] = dict(pack['files']['enemy-newsh4-195-8.hda'])
                    pack['count'] += 1
                elif case == 'changed-member':
                    pack['files']['enemy-newsh4-157-8.hda']['header_u32'][0] += 1
                elif case == 'count':
                    pack['count'] += 1
                elif case == 'source-png':
                    del changed['source_pngs'][pack['files']['enemy-newsh4-157-8.hda']['sha256']]
                elif case == 'opposite7-member':
                    pack['files']['enemy-newsh4-273-8.hda']['header_u32'][0] += 1
                elif case == 'opposite7-png':
                    del changed['source_pngs'][pack['files']['enemy-newsh4-231-8.hda']['sha256']]
                else:
                    changed['linked31_installation_v1']['original_relative_actor_y'] = 99
                self.manifest = changed
                try:
                    with self.assertRaises(AssertionError):
                        self.test_existing_manifest_fields_and_bytes_unchanged_from_baseline()
                finally:
                    self.manifest = original

    def test_original_mfg1_family_source_and_pack_are_unchanged(self):
        paths = ['assets/hd/artwork/startup-manufacturer-v1',
                 'assets/hd/packs/startup-manufacturer-v1', 'prototype/startup_manufacturer_bundle.py']
        subprocess.run(['git', 'diff', '--exit-code', '1df1d87', '--', *paths], cwd=ROOT, check=True,
                       capture_output=True)
        original = self.manifest['startup_manufacturer_v1']
        for name, receipt in original['files'].items():
            source = ROOT / 'assets/hd/packs/startup-manufacturer-v1' / name
            copy = self.runtime / name
            self.assertEqual(source.read_bytes(), copy.read_bytes())
            self.assertEqual(self.family['files'][name], receipt)
            self.assertEqual(sha(copy.read_bytes()), receipt['sha256'])
            self.assertEqual(copy.read_bytes()[:4], b'MFG1')

    def test_independent_family_receipt_and_separate_byte_accounting(self):
        bundles, receipt = bundle.build_family(ROOT)
        self.assertEqual(receipt, self.family)
        self.assertEqual(bundles, self.bundles)
        title_total = sum(len(raw) for name, (raw, _) in bundles.items() if name in EXPECTED)
        copies_total = sum(len(raw) for name, (raw, _) in bundles.items() if name not in EXPECTED)
        self.assertEqual(title_total, 7113968)
        self.assertEqual(copies_total, 8192128)
        self.assertEqual(title_total, self.family['title_resource_bytes'])
        self.assertEqual(copies_total, self.family['manufacturer_compatibility_bytes'])
        self.assertEqual(len(list(self.runtime.iterdir())), 5)

    def test_source_only_relocated_rebuild_is_exact(self):
        report = bundle.verify_source_rebuild(ROOT)
        self.assertEqual(report['status'], 'PASS')
        self.assertEqual(report['movement_positions'], 29)
        self.assertEqual(report['output_files'], 11)
        self.assertEqual(len(report['assets']), 3)

    def test_source_builder_rejects_unsafe_output_paths_without_changes(self):
        before = bundle.source_receipts(self.source)
        with tempfile.TemporaryDirectory(prefix='title-path-guards-') as temporary:
            existing = Path(temporary) / 'exists'
            existing.mkdir()
            link = Path(temporary) / 'link'
            link.symlink_to(existing, target_is_directory=True)
            candidates = ['relative-output', str(existing), str(self.source / 'unsafe-output'),
                          str(self.source.parent), str(link / 'output'), str(Path(temporary) / 'absent' / 'output')]
            for output in candidates:
                with self.subTest(output=output):
                    result = subprocess.run([sys.executable, '-B', str(self.source / 'build.py'), '--output', output],
                                            capture_output=True, text=True)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn('ValueError', result.stderr)
            self.assertFalse((self.source / 'unsafe-output').exists())
        self.assertEqual(before, bundle.source_receipts(self.source))

    def test_source_inventory_hash_and_symlink_fail_closed(self):
        with tempfile.TemporaryDirectory(prefix='title-source-rejections-') as temporary:
            target = Path(temporary) / 'source'
            shutil.copytree(self.source, target)
            for name in ('README.md', 'build.py', 'canonical/pic4-canonical4x.png', 'FILES.sha256', 'manifest.json'):
                with self.subTest(changed=name):
                    path = target / name
                    previous = path.read_bytes()
                    path.write_bytes(previous + b'\n')
                    with self.assertRaises(ValueError):
                        bundle.source_receipts(target)
                    path.write_bytes(previous)
            sums = target / 'FILES.sha256'
            saved_sums = sums.read_bytes()
            sums.write_bytes(saved_sums.rstrip(b'\n'))
            with self.assertRaisesRegex(ValueError, 'FILES.sha256'):
                bundle.source_receipts(target)
            sums.write_bytes(saved_sums)
            extra = target / 'reference-original.png'
            extra.write_bytes(b'not permitted')
            with self.assertRaises(ValueError):
                bundle.source_receipts(target)
            extra.unlink()
            empty = target / 'extra-directory'
            empty.mkdir()
            with self.assertRaises(ValueError):
                bundle.source_receipts(target)
            empty.rmdir()
            path = target / 'README.md'
            saved = path.read_bytes()
            path.unlink()
            with self.assertRaises(ValueError):
                bundle.source_receipts(target)
            path.symlink_to(self.source / 'README.md')
            with self.assertRaises(ValueError):
                bundle.source_receipts(target)
            path.unlink()
            path.write_bytes(saved)
            symlink_root = Path(temporary) / 'source-link'
            symlink_root.symlink_to(target, target_is_directory=True)
            with self.assertRaises(ValueError):
                bundle.source_receipts(symlink_root)
            self.assertEqual(bundle.source_receipts(target), self.family['source_files'])

    def test_checked_file_rejects_escape_absolute_and_nonregular(self):
        with tempfile.TemporaryDirectory(prefix='title-path-rejections-') as temporary:
            root = Path(temporary)
            for name in ('../outside', '/etc/passwd', '.'):
                with self.subTest(path=name), self.assertRaises(ValueError):
                    bundle.checked_file(root, name)
            if hasattr(os, 'mkfifo'):
                os.mkfifo(root / 'pipe')
                with self.assertRaises(ValueError):
                    bundle.checked_file(root, 'pipe')
                with self.assertRaises(ValueError):
                    bundle.require_inventory(root, {'pipe'}, 'test tree')

    def test_alpha_policy_rejects_hidden_rgb_opaque_and_support_errors(self):
        # A small straight-alpha logo keeps partial coverage and clean padding.
        pixels = bytearray(4 * 4 * 4)
        pixels[4 * 5:4 * 5 + 4] = b'\x20\x40\x60\x80'
        bundle.validate_rgba(bytes(pixels), 4, 4, 1, (1, 1, 3, 3))
        hidden = bytearray(pixels)
        hidden[0] = 1
        with self.assertRaisesRegex(ValueError, 'hidden RGB'):
            bundle.validate_rgba(bytes(hidden), 4, 4, 1, (1, 1, 3, 3))
        outside = bytearray(pixels)
        outside[3] = 1
        with self.assertRaisesRegex(ValueError, 'support bound'):
            bundle.validate_rgba(bytes(outside), 4, 4, 1, (1, 1, 3, 3))
        no_partial = bytearray(pixels)
        no_partial[4 * 5 + 3] = 255
        with self.assertRaisesRegex(ValueError, 'partial alpha'):
            bundle.validate_rgba(bytes(no_partial), 4, 4, 1, (1, 1, 3, 3))
        with self.assertRaisesRegex(ValueError, 'entirely opaque'):
            bundle.validate_rgba(bytes(pixels), 4, 4, 0, None)
        with self.assertRaisesRegex(ValueError, 'Unsupported alpha mode'):
            bundle.validate_rgba(bytes(pixels), 4, 4, 2, (1, 1, 3, 3))
        with self.assertRaisesRegex(ValueError, 'byte count'):
            bundle.validate_rgba(bytes(pixels[:-1]), 4, 4, 1, (1, 1, 3, 3))

    def test_runtime_inventory_bytes_and_manifest_receipt_fail_closed(self):
        # Isolate final on-disk checks from the already-tested expensive producer.
        with tempfile.TemporaryDirectory(prefix='title-runtime-rejections-') as temporary:
            repo = Path(temporary)
            runtime = repo / 'assets/hd/packs/startup-title-v1'
            runtime.parent.mkdir(parents=True)
            shutil.copytree(self.runtime, runtime)
            manifest_path = repo / 'assets/hd/manifest.json'
            manifest_path.write_text(json.dumps(self.manifest))
            with mock.patch.object(bundle, 'build_family', return_value=(self.bundles, self.family)):
                for name in self.bundles:
                    with self.subTest(runtime=name):
                        path = runtime / name
                        original = path.read_bytes()
                        path.write_bytes(original[:-1] + bytes([original[-1] ^ 1]))
                        with self.assertRaisesRegex(ValueError, 'Runtime bytes'):
                            bundle.build_bundles(repo)
                        path.write_bytes(original)
                extra = runtime / 'extra.hda'
                extra.write_bytes(b'')
                with self.assertRaises(ValueError):
                    bundle.build_bundles(repo)
                extra.unlink()
                path = runtime / 'title-pic4-v1.hda'
                original = path.read_bytes()
                path.unlink()
                with self.assertRaises(ValueError):
                    bundle.build_bundles(repo)
                path.symlink_to(self.runtime / path.name)
                with self.assertRaises(ValueError):
                    bundle.build_bundles(repo)
                path.unlink()
                path.write_bytes(original)
                malformed = json.loads(json.dumps(self.manifest))
                malformed['startup_title_v1']['count'] = 3
                manifest_path.write_text(json.dumps(malformed))
                with self.assertRaisesRegex(ValueError, 'independent receipt'):
                    bundle.build_bundles(repo)

    def test_aggregate_title_block_verifies_and_outputs_only_five_files(self):
        # Execute only the real title-family block, never the aggregate rebuild.
        text = (ROOT / 'prototype/build-hd-assets.py').read_text()
        block = text[text.index('title_count=0\n'):text.index('title_menu_count=0\n')]
        with tempfile.TemporaryDirectory(prefix='title-aggregate-block-') as temporary:
            namespace = {'repo': ROOT, 'manifest': self.manifest,
                         'a': SimpleNamespace(output=True), 'output': Path(temporary)}
            exec(compile(block, 'build-hd-assets.py:title-family-only', 'exec'), namespace)
            self.assertEqual(namespace['title_count'], 3)
            self.assertEqual(namespace['title_source_count'], 19)
            self.assertEqual(namespace['title_compatibility_count'], 2)
            output = Path(temporary) / 'startup-title-v1'
            self.assertEqual({p.name for p in output.iterdir()}, set(self.bundles))
            for name, (raw, _) in self.bundles.items():
                self.assertEqual((output / name).read_bytes(), raw)
            self.assertEqual({p.name for p in Path(temporary).iterdir()}, {'startup-title-v1'})


if __name__ == '__main__':
    unittest.main(verbosity=2)
