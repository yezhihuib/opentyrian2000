#!/usr/bin/env python3
"""Source/package checks only: never compile, invoke or require the game."""
from pathlib import Path
import hashlib
import json
import os
import runpy
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'prototype'))
from type3_small_coexistence import project_type3_small_family
sys.path.insert(0, str(ROOT / 'prototype'))
from startup_manufacturer_bundle import build_bundles, PACK, SOURCE, SOURCE_FILES, RUNTIME_FILES

API = runpy.run_path(str(ROOT / SOURCE / 'build_resource.py'))
HEADER = struct.Struct('<4s7I4Q')
FROZEN = {
    10: ('a885d023f89b0e214a81df1d02dbf62d6e36645820c1a15e9a0ad74a2c5e2c79',
         0x720d8ce9dda3f5f4, 0xb50ac0b9e5f1a73d, 0x46944845146f2d39),
    12: ('bd358e8006a99467e08bc8bf257e6ead51fe5f216c63c57088612ef5039c7669',
         0x98d7341da720b7ab, 0x20261a06b61711d5, 0x3d97f250a0cae51a),
}


# Exact published round inserts, type4, and coordinated linked31 additions.
# Only these finite pinned entries project out of the historical gameplay pin.
FROZEN_GAMEPLAY_ADDITIONS = {'terrain-shapesz-190-8.hda': {'sha256': '023700d1ad415753564e2f2598c493df9fcc5f56a3112b33cd0056957cd46e70',
                               'header_u32': [2010190, 8, 24, 28, 0, 0],
                               'source_png': 'assets/hd/source/terrain-shapesz-190-8-023700d1ad41.png',
                               'source_png_sha256': 'dbdbdce20f9a67a779fa6448e4de6e5985afa9ec3728e55a3bff31aa184e0e37'},
 'terrain-shapesz-200-8.hda': {'sha256': 'bde737956fc39f626064af9aba6b2b418bfec02829b9e6e70b300e232455ba07',
                               'header_u32': [2010200, 8, 24, 28, 0, 0],
                               'source_png': 'assets/hd/source/terrain-shapesz-200-8-bde737956fc3.png',
                               'source_png_sha256': '851c3f94970f7165667ebe52ac0b07ab665d79dd295b4a2b5dcee10d4f93f4d1'},
 'enemy-newsh2-159-8.hda': {'sha256': '516844423ddf715fe7ecef00a01d55bb214873ad6e52a722dff5fb77378baa85',
                            'header_u32': [1010159, 8, 24, 28, 6, 7],
                            'source_png': 'assets/hd/source/enemy-newsh2-159-8-516844423ddf.png',
                            'source_png_sha256': '075817a626879b5aed993641b933bc976a4856e69f513bb39637b5b92f837e32'},
 'enemy-newsh2-161-8.hda': {'sha256': 'f51ff7b9f800929c38f1c921a09080d137d5cdc98f289fac7d51644e143bc78c',
                            'header_u32': [1010161, 8, 24, 28, 6, 7],
                            'source_png': 'assets/hd/source/enemy-newsh2-161-8-f51ff7b9f800.png',
                            'source_png_sha256': 'a69f731342bcf3ee1a27a20e1c4d108ec1ca0da904ca21417e13fef7553419ee'},
 'enemy-newsh2-163-8.hda': {'sha256': '09f805d16d5c12dd005fcb3fea62291d9fa7eb8dbbbddac96830fb42f454f3cc',
                            'header_u32': [1010163, 8, 24, 28, 6, 7],
                            'source_png': 'assets/hd/source/enemy-newsh2-163-8-09f805d16d5c.png',
                            'source_png_sha256': '280c42e5ba9220b2c56063d77192d3c72093a474be9ceba56b5a8a75a22c9720'},
 'enemy-newsh2-165-8.hda': {'sha256': 'b3ce6d5081153b4c9a35623427cabf6625a376fcbe00de3c1e8c072691b5d5a9',
                            'header_u32': [1010165, 8, 24, 28, 6, 7],
                            'source_png': 'assets/hd/source/enemy-newsh2-165-8-b3ce6d508115.png',
                            'source_png_sha256': 'e987f9796fae333de42b5c093a60e821a43ba173452c1f0e4322aea93f1c4a5c'},
 'enemy-newsh2-167-8.hda': {'sha256': '6838553744899c8fe66124f1132bb325512db1c2050c0e8eb77276714c73dcdd',
                            'header_u32': [1010167, 8, 24, 28, 6, 7],
                            'source_png': 'assets/hd/source/enemy-newsh2-167-8-683855374489.png',
                            'source_png_sha256': 'd2e49070473ae9442fe5c7765c15efc0f4889b7d2346400c74cede2107ab28a4'}}

# Exact eight-member append; both banks are one coordinated family.
FROZEN_GAMEPLAY_ADDITIONS.update({'terrain-shapesz-161-8.hda': {'sha256': 'b8f9e85e0a03929bafe35c250cdff070e1c5b59a61c09d4b183adb38dcb23bcc',
                               'header_u32': [2010161, 8, 24, 28, 0, 0],
                               'source_png': 'assets/hd/source/terrain-shapesz-161-8-b8f9e85e0a03.png',
                               'source_png_sha256': '6129b2ad37c7dc9e4851f96eb34cde95e9db93f9ba10e7a3ccbfeaed14ce8b18'},
 'terrain-shapesz-162-8.hda': {'sha256': '9d98cfb0cf5fc155018236736838568f6a71aab9177bcec161e933b3cd5a5939',
                               'header_u32': [2010162, 8, 24, 28, 0, 0],
                               'source_png': 'assets/hd/source/terrain-shapesz-162-8-9d98cfb0cf5f.png',
                               'source_png_sha256': 'd8010c24c9f62595295e6f5eabb0dd85a5f7f7a49021238f9741f5afa59fedf0'},
 'terrain-shapesz-171-8.hda': {'sha256': '556d093db425aba78f0446b018bb821775cd53e8126ce98f37d9d3371563b7ec',
                               'header_u32': [2010171, 8, 24, 28, 0, 0],
                               'source_png': 'assets/hd/source/terrain-shapesz-171-8-556d093db425.png',
                               'source_png_sha256': '9bfb9ae75296702fe8d1f0c8c261f7830433d61082dc3a248535ff820bc65909'},
 'terrain-shapesz-172-8.hda': {'sha256': 'dcdc10baff0a2da9f44bc182ff840f7a219310398520cf63da88045f4f36f4c6',
                               'header_u32': [2010172, 8, 24, 28, 0, 0],
                               'source_png': 'assets/hd/source/terrain-shapesz-172-8-dcdc10baff0a.png',
                               'source_png_sha256': '9281e7f69cb58f2a5c1a3c7511cd806e80d10490d152e0c00f9f2b464a669765'},
 'enemy-newsh2-15-8.hda': {'sha256': 'c20471f23e2f368fbdb8dd78bea37051f6c4be2e268b0d1fc9a114f92ef423da',
                           'header_u32': [1010015, 8, 24, 28, 6, 7],
                           'source_png': 'assets/hd/source/enemy-newsh2-15-8-c20471f23e2f.png',
                           'source_png_sha256': 'a8ac87a3c05c6b54824862c0f60b0515117193f24d8dd9e028cb800b3aaecb59'},
 'enemy-newsh2-17-8.hda': {'sha256': '3b8eb8da5f98b7cfea217478038427ad85e79e03e96268a14b0f986587b952cb',
                           'header_u32': [1010017, 8, 24, 28, 6, 7],
                           'source_png': 'assets/hd/source/enemy-newsh2-17-8-3b8eb8da5f98.png',
                           'source_png_sha256': '135dbe6e7a579cdc1a7b13f67b5b46515c7af1217ccce08eb75e3a6c754b5e96'},
 'enemy-newsh2-53-8.hda': {'sha256': '8612e05561aaca1a9e26df9414436aa97a8b9fa3f7b6fe58c057f8c137684e3c',
                           'header_u32': [1010053, 8, 24, 28, 6, 7],
                           'source_png': 'assets/hd/source/enemy-newsh2-53-8-8612e05561aa.png',
                           'source_png_sha256': 'a002c33cdaf7629088fa113d15a351b9b815f3ae24c7e4a4819336678dff2c25'},
 'enemy-newsh2-55-8.hda': {'sha256': '6a99ec193f4ff580fa5832a8584978efea3378d3173078442f121893736b418f',
                           'header_u32': [1010055, 8, 24, 28, 6, 7],
                           'source_png': 'assets/hd/source/enemy-newsh2-55-8-6a99ec193f4f.png',
                           'source_png_sha256': '88242ad2a6c2c251abb5cb4bdde791b9ae5ff1d37f78e1ee352d6d0b922b23ac'}})


# Exact seven-member bank2 append; no previous gameplay pin is relaxed.
FROZEN_GAMEPLAY_ADDITIONS.update({'enemy-newsh4-153-8.hda': {'sha256': 'd89711791d4266a106687b27f9e8ad4010fc31b4a870418761d7f48237f3825a',
                            'header_u32': [1020153, 8, 24, 28, 6, 7],
                            'source_png': 'assets/hd/source/enemy-newsh4-153-8-d89711791d42.png',
                            'source_png_sha256': 'e16b6c5d799c13c2348407888ead1e1585eb7e2d92e22ff105b72ccec46653a5'},
 'enemy-newsh4-155-8.hda': {'sha256': '7f178909b53826e234ec07dca2b20b1626bc82238472df2720cbe87017741782',
                            'header_u32': [1020155, 8, 24, 28, 6, 7],
                            'source_png': 'assets/hd/source/enemy-newsh4-155-8-7f178909b538.png',
                            'source_png_sha256': '84055718b9df6971fe53dacb2ab1b0c13897d4c4764842aa3a87e8bb20996ec6'},
 'enemy-newsh4-157-8.hda': {'sha256': '1c4773c33e549f389038e97fa9bcb8d7c422f5cb2d09cf19085560e3ed6ce124',
                            'header_u32': [1020157, 8, 24, 28, 6, 7],
                            'source_png': 'assets/hd/source/enemy-newsh4-157-8-1c4773c33e54.png',
                            'source_png_sha256': 'a8a28b7381c86bf4580905ca802a49c71c7d85d61d7609bab36da96f357830ba'},
 'enemy-newsh4-159-8.hda': {'sha256': '860b79d9fd1b0e4d5efed8e81819ea33558f8c48d6f420923b11b007d1f011d9',
                            'header_u32': [1020159, 8, 24, 28, 6, 7],
                            'source_png': 'assets/hd/source/enemy-newsh4-159-8-860b79d9fd1b.png',
                            'source_png_sha256': '0fc5eed45e9e9ba9dbd01279421db0473f4b51ddc38ec695fe164bef42e9deca'},
 'enemy-newsh4-191-8.hda': {'sha256': 'a2103ee891632976f7e9a365aa04841e4769e84079a2123cec77310be227cb5f',
                            'header_u32': [1020191, 8, 24, 28, 6, 7],
                            'source_png': 'assets/hd/source/enemy-newsh4-191-8-a2103ee89163.png',
                            'source_png_sha256': '75be686f4730a2c2272d2040b24bcec665cd8eb2a8d647e5fc2d262a0c799703'},
 'enemy-newsh4-193-8.hda': {'sha256': '7774492351928616b1aced51b511d336ce183d84516998b6c47c65e51f2108a2',
                            'header_u32': [1020193, 8, 24, 28, 6, 7],
                            'source_png': 'assets/hd/source/enemy-newsh4-193-8-777449235192.png',
                            'source_png_sha256': '7b35aff0d3f8d6282e961cc64db19615baa459fbb8187ab291984e53928c4675'},
 'enemy-newsh4-195-8.hda': {'sha256': '3324bbcf029c7c0aa0ca7cac8407f8634cb9c1614c9aff6bf8a0a71d866e6efd',
                            'header_u32': [1020195, 8, 24, 28, 6, 7],
                            'source_png': 'assets/hd/source/enemy-newsh4-195-8-3324bbcf029c.png',
                            'source_png_sha256': '19cb7a37c8c6e52dbfe60459e33fa4c9c5ec137cd7a976492a749e3035c5f3c6'}})


# Exact opposite/link2 seven-member append, independent of the left family.
FROZEN_GAMEPLAY_ADDITIONS.update({'enemy-newsh4-231-8.hda': {'sha256': '76740ae794198be75ba5d91f66f833a11204a5af2ebe5aea5123d25e75abf19f',
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
                            'source_png_sha256': '8e5ad4402891610c1fd8fedda4f5cff071463693b3d1c4f4bf0453d0827a56bc'}})


# Exact type15 eight-heading append, independent of mutable manifest receipts.
TYPE15 = {'schema': 'enemy-type15-eightheading-v1',
 'source': 'assets/hd/artwork/type15-eightheading-smooth-contour-v2',
 'source_inventory_sha256': '9bc7fa0d06d4f6077ee48a993d2ac3f511b56e3cf22d95e9a83765a800cf10cc',
 'import_sha256': '93c0e208876a4ac9aed47256f370cfebf577123913cc43226cc311a24d5e1299',
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
 'selection': 'Original event-selected headings; animate0, no automatic '
              'rotation',
 'source_only_nonpresented_base': 91,
 'original_alpha_exact': False,
 'fallback': 'All eight approved members required before any replacement; '
             '8x-only selected-pack cached fallback is local to this family',
 'entries': [{'id': 39,
              'bank_role': 101,
              'slot': 396,
              'anchor': [6, 7],
              'rgba_fnv1a64': 'cc3d8be70ed2e620'},
             {'id': 41,
              'bank_role': 101,
              'slot': 397,
              'anchor': [6, 7],
              'rgba_fnv1a64': '80d5e7bb507fe084'},
             {'id': 43,
              'bank_role': 101,
              'slot': 398,
              'anchor': [6, 7],
              'rgba_fnv1a64': '3228caecc8f7abe8'},
             {'id': 45,
              'bank_role': 101,
              'slot': 399,
              'anchor': [6, 7],
              'rgba_fnv1a64': '33f828b2c95baa5a'},
             {'id': 91,
              'bank_role': 101,
              'slot': 400,
              'anchor': [6, 7],
              'rgba_fnv1a64': '452516abee3a1d95'},
             {'id': 93,
              'bank_role': 101,
              'slot': 401,
              'anchor': [6, 7],
              'rgba_fnv1a64': 'c8296a713b1af965'},
             {'id': 129,
              'bank_role': 101,
              'slot': 402,
              'anchor': [6, 7],
              'rgba_fnv1a64': '1f937a94539eb9cb'},
             {'id': 131,
              'bank_role': 101,
              'slot': 403,
              'anchor': [6, 7],
              'rgba_fnv1a64': 'b01b2fcfaa46aaf0'}],
 'source_inventory': 'SHA256SUMS.json',
 'art_revision': 'smooth-contour-v2',
 'contour_contract': 'Exact approved fractional outer contours and genuine '
                     'apertures inside original24x28 rectangles; original '
                     'indexed alpha, collision, registration and source events '
                     'unchanged.'}
TYPE15_FILES = {'enemy-newsh2-39-8.hda': {'sha256': 'faa362385a6b7f67e7926df162d9b5df4df41aa492709562841e410fd77e2d6d',
                           'header_u32': [1010039, 8, 24, 28, 6, 7],
                           'source_png': 'assets/hd/source/enemy-newsh2-39-8-faa362385a6b.png',
                           'source_png_sha256': '1a9706c98ce9625370e0e06e9cd4afdfc2c377880d20646caf99b81b0a2103b6'},
 'enemy-newsh2-41-8.hda': {'sha256': '8d2f73e32e39be13e440ba8639f471ca1877dc476ac03b5ee60771741c2f515f',
                           'header_u32': [1010041, 8, 24, 28, 6, 7],
                           'source_png': 'assets/hd/source/enemy-newsh2-41-8-8d2f73e32e39.png',
                           'source_png_sha256': '654d63279d28307f4bc6ec48f95c42633e58ee32ec5f12403349be62f3a61b58'},
 'enemy-newsh2-43-8.hda': {'sha256': '5874d9c67472bb9afa8e6be64480d33b0502ad4c035f8c985bb77ef7cfa00d66',
                           'header_u32': [1010043, 8, 24, 28, 6, 7],
                           'source_png': 'assets/hd/source/enemy-newsh2-43-8-5874d9c67472.png',
                           'source_png_sha256': '5eb06edb895431f007747ca8385a9bbe29cd568c2c745a02a85d2b3ca0fba8ae'},
 'enemy-newsh2-45-8.hda': {'sha256': '3a20918ae6fffb966c9fc857a04a9b75a5554c961e622f6f7851db2d871f8af5',
                           'header_u32': [1010045, 8, 24, 28, 6, 7],
                           'source_png': 'assets/hd/source/enemy-newsh2-45-8-3a20918ae6ff.png',
                           'source_png_sha256': '827d70f332df47b5b637fa91b9cc757cbd326a7ee7bcaa061e116d55592b1f2c'},
 'enemy-newsh2-91-8.hda': {'sha256': 'e2c3aaa833db864ae73b4cd611305043ddcefd89dda19d22a1b1d5d577b2c29f',
                           'header_u32': [1010091, 8, 24, 28, 6, 7],
                           'source_png': 'assets/hd/source/enemy-newsh2-91-8-e2c3aaa833db.png',
                           'source_png_sha256': 'cec3bf6abf3e17e9d0ea450855c4ea494511936f6cb47ff85692fc67a717f54b'},
 'enemy-newsh2-93-8.hda': {'sha256': 'c816a59f906bbf63af3707d7b183c7be8c39136613f60c0a9f8b4423d2622164',
                           'header_u32': [1010093, 8, 24, 28, 6, 7],
                           'source_png': 'assets/hd/source/enemy-newsh2-93-8-c816a59f906b.png',
                           'source_png_sha256': 'd257c40c17b0d90ed314080afcf17d9b21881aa8d0dc88cfcfe22dc9c93b6aea'},
 'enemy-newsh2-129-8.hda': {'sha256': '0369d6e3fdbe602f8e5caa51fa3834a434a1abd28c267674d4b7aa98005e3e56',
                            'header_u32': [1010129, 8, 24, 28, 6, 7],
                            'source_png': 'assets/hd/source/enemy-newsh2-129-8-0369d6e3fdbe.png',
                            'source_png_sha256': '30b038078611fad06ad421700e4f25d6c9b09b9accc48afb14f57ed394e4152b'},
 'enemy-newsh2-131-8.hda': {'sha256': '7590d16a0c2378bca3d2ffb66c0279ede2c73ffcbc61383e83d582cdd03ad904',
                            'header_u32': [1010131, 8, 24, 28, 6, 7],
                            'source_png': 'assets/hd/source/enemy-newsh2-131-8-7590d16a0c23.png',
                            'source_png_sha256': 'a69466bc91e960184b25e549237fefdd7ea05190839519a2405ebe5aa755dc0b'}}
TYPE15_PNGS = {'faa362385a6b7f67e7926df162d9b5df4df41aa492709562841e410fd77e2d6d': {'path': 'assets/hd/source/enemy-newsh2-39-8-faa362385a6b.png',
                                                                      'sha256': '1a9706c98ce9625370e0e06e9cd4afdfc2c377880d20646caf99b81b0a2103b6',
                                                                      'RGBA_sha256': '63e9458a8a2f22037dbb78d5998827cab7bf0dc66125e47232f6877fdee8cddb'},
 '8d2f73e32e39be13e440ba8639f471ca1877dc476ac03b5ee60771741c2f515f': {'path': 'assets/hd/source/enemy-newsh2-41-8-8d2f73e32e39.png',
                                                                      'sha256': '654d63279d28307f4bc6ec48f95c42633e58ee32ec5f12403349be62f3a61b58',
                                                                      'RGBA_sha256': 'c1b8ffb8458ea985c005bf2705b650836655a41e9d01ccfc217deecd4b5e9d1c'},
 '5874d9c67472bb9afa8e6be64480d33b0502ad4c035f8c985bb77ef7cfa00d66': {'path': 'assets/hd/source/enemy-newsh2-43-8-5874d9c67472.png',
                                                                      'sha256': '5eb06edb895431f007747ca8385a9bbe29cd568c2c745a02a85d2b3ca0fba8ae',
                                                                      'RGBA_sha256': '929217d265e8e7b8bc89f49db20dd99a003aa3c0e4deff149788284a4c767606'},
 '3a20918ae6fffb966c9fc857a04a9b75a5554c961e622f6f7851db2d871f8af5': {'path': 'assets/hd/source/enemy-newsh2-45-8-3a20918ae6ff.png',
                                                                      'sha256': '827d70f332df47b5b637fa91b9cc757cbd326a7ee7bcaa061e116d55592b1f2c',
                                                                      'RGBA_sha256': '50c2a1d850bf2a3a5c9fe78680828d10b7e3356ecdde570dbfac1a32eb8598d1'},
 'e2c3aaa833db864ae73b4cd611305043ddcefd89dda19d22a1b1d5d577b2c29f': {'path': 'assets/hd/source/enemy-newsh2-91-8-e2c3aaa833db.png',
                                                                      'sha256': 'cec3bf6abf3e17e9d0ea450855c4ea494511936f6cb47ff85692fc67a717f54b',
                                                                      'RGBA_sha256': 'a22c54c824774371977cdab300fb6b9a2fdd7928e1c5cee903db62e9363a0f9e'},
 'c816a59f906bbf63af3707d7b183c7be8c39136613f60c0a9f8b4423d2622164': {'path': 'assets/hd/source/enemy-newsh2-93-8-c816a59f906b.png',
                                                                      'sha256': 'd257c40c17b0d90ed314080afcf17d9b21881aa8d0dc88cfcfe22dc9c93b6aea',
                                                                      'RGBA_sha256': 'e0211943ebbb71735c3a1e6f8854fd2c1a97116d3a7c5a280ce6d58ec2fced58'},
 '0369d6e3fdbe602f8e5caa51fa3834a434a1abd28c267674d4b7aa98005e3e56': {'path': 'assets/hd/source/enemy-newsh2-129-8-0369d6e3fdbe.png',
                                                                      'sha256': '30b038078611fad06ad421700e4f25d6c9b09b9accc48afb14f57ed394e4152b',
                                                                      'RGBA_sha256': 'fdc725fca3d9544d623d1f09641fd723a69e784ef74c2beb79b51fcfe0375074'},
 '7590d16a0c2378bca3d2ffb66c0279ede2c73ffcbc61383e83d582cdd03ad904': {'path': 'assets/hd/source/enemy-newsh2-131-8-7590d16a0c23.png',
                                                                      'sha256': 'a69466bc91e960184b25e549237fefdd7ea05190839519a2405ebe5aa755dc0b',
                                                                      'RGBA_sha256': 'e70d53786f196218978c0b771b95f384628c5eb93c5e8c92f9b4d3c4122c6c21'}}
TYPE15_HISTORICAL_PNGS = {'05ef7518703365fb05f86ac746679c547a45f8a5b45070ccd0729ae56afdb789': {'path': 'assets/hd/source/enemy-newsh2-39-8-05ef75187033.png',
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

def digest(data):
    return hashlib.sha256(data).hexdigest()


def independent_fnv(data):
    value = 0xcbf29ce484222325
    for byte in data:
        value ^= byte
        value *= 0x100000001b3
        value &= 0xffffffffffffffff
    return value


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
    test.assertEqual(digest((source / 'SHA256SUMS.json').read_bytes()), TYPE15['source_inventory_sha256'])
    test.assertEqual(digest((source / 'IMPORT.json').read_bytes()), TYPE15['import_sha256'])
    imported = json.loads((source / 'IMPORT.json').read_text())
    test.assertEqual({e['path'] for e in imported['files']}, {str(q.relative_to(source)) for q in source.rglob('*') if q.is_file() and q.name != 'IMPORT.json'})
    for e in imported['files']:
        test.assertEqual(digest((source / e['path']).read_bytes()), e['sha256'])
    for historical in TYPE15_HISTORICAL_PNGS.values():
        test.assertEqual(digest((ROOT / historical['path']).read_bytes()), historical['sha256'])
    defaults = {manifest['default_preview_pack'], manifest['default_debug_pack']}
    test.assertEqual(len(defaults), 2)
    # No alias or duplicate source-index entry may hide beside the eight pins.
    stems = tuple(f'enemy-newsh2-{identity}-8-' for identity in TYPE15['ids'])
    test.assertEqual({stamp for stamp, item in manifest['source_pngs'].items()
                      if Path(item['path']).name.startswith(stems)}, set(TYPE15_PNGS) | set(TYPE15_HISTORICAL_PNGS))
    for stamp, expected in {**TYPE15_HISTORICAL_PNGS, **TYPE15_PNGS}.items():
        test.assertIn(stamp, manifest['source_pngs'])
        test.assertEqual(manifest['source_pngs'].pop(stamp), expected)
    for filename, expected in TYPE15_FILES.items():
        test.assertEqual({name for name, pack in packs.items() if filename in pack['files']}, defaults)
        png = ROOT / expected['source_png']
        test.assertEqual(digest(png.read_bytes()), expected['source_png_sha256'])
        with Image.open(png) as image:
            test.assertEqual((image.mode, image.size), ('RGBA', (192, 224)))
            rgba = image.tobytes()
        test.assertEqual(digest(rgba), TYPE15_PNGS[expected['sha256']]['RGBA_sha256'])
        for name in defaults:
            pack = packs[name]
            test.assertEqual(pack['count'], len(pack['files']))
            test.assertEqual(pack['files'].pop(filename), expected)
            raw = (ROOT / 'assets/hd/packs' / name / filename).read_bytes()
            test.assertEqual(digest(raw), expected['sha256'])
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
    test.assertEqual(digest((source / 'manifest.json').read_bytes()), LATE_SPIKE['source_manifest_sha256'])
    test.assertEqual(digest((source / 'contract.json').read_bytes()), LATE_SPIKE['source_contract_sha256'])
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
        test.assertEqual(digest(png.read_bytes()), expected['source_png_sha256'])
        with Image.open(png) as image:
            test.assertEqual((image.mode, image.size), ('RGBA', (192, 224)))
            rgba = image.tobytes()
        test.assertEqual(digest(rgba), LATE_SPIKE_PNGS[expected['sha256']]['RGBA_sha256'])
        for name in defaults:
            pack = packs[name]
            test.assertEqual(pack['count'], len(pack['files']))
            test.assertEqual(pack['files'].pop(filename), expected)
            raw = (ROOT / 'assets/hd/packs' / name / filename).read_bytes()
            test.assertEqual(digest(raw), expected['sha256'])
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
    test.assertEqual(digest((source / 'manifest.json').read_bytes()), NEWSH4_ENTRY6['source_manifest_sha256'])
    test.assertEqual(digest((source / 'contract.json').read_bytes()), NEWSH4_ENTRY6['source_contract_sha256'])
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
        test.assertEqual(digest(png.read_bytes()), expected['source_png_sha256'])
        with Image.open(png) as image:
            test.assertEqual((image.mode, image.size), ('RGBA', (192, 224)))
            rgba = image.tobytes()
        test.assertEqual(digest(rgba), NEWSH4_ENTRY6_PNGS[expected['sha256']]['RGBA_sha256'])
        for name in defaults:
            pack = packs[name]
            test.assertEqual(pack['count'], len(pack['files']))
            test.assertEqual(pack['files'].pop(filename), expected)
            raw = (ROOT / 'assets/hd/packs' / name / filename).read_bytes()
            test.assertEqual(digest(raw), expected['sha256'])
            test.assertEqual(raw[:28], b'HDR1' + struct.pack('<6I', *expected['header_u32']))
            test.assertEqual(raw[28:], rgba)
            pack['count'] -= 1


class ManufacturerPackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundles = build_bundles(ROOT)
        cls.manifest = json.loads((ROOT / 'assets/hd/manifest.json').read_text())

    def call(self, script, *args, cwd, success=True, optimize=False):
        result = subprocess.run(
            [sys.executable, *(['-O'] if optimize else []), str(script), *map(str, args)],
            cwd=cwd, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'),
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode == 0, success, result.stdout + result.stderr)
        return result

    def test_exact_rgba_and_header(self):
        self.assertEqual(HEADER.size, 64)
        self.assertEqual(set(self.bundles), RUNTIME_FILES)
        for pic, (expected_sha, indices, palette, stamp) in FROZEN.items():
            with self.subTest(pic=pic):
                raw, receipt = self.bundles[f'startup-pic{pic}-v1.hda']
                self.assertEqual(len(raw), 4096064)
                self.assertEqual(digest(raw), expected_sha)
                self.assertEqual(HEADER.unpack_from(raw), (
                    b'MFG1', 1, 4, pic, pic + 10, 320, 200, 4096000,
                    indices, palette, stamp, 0,
                ))
                png = ROOT / SOURCE / f'previews/pic{pic}-candidate-native4x.png'
                with Image.open(png) as image:
                    self.assertEqual((image.mode, image.size), ('RGB', (1280, 800)))
                    self.assertEqual(raw[64:], image.convert('RGBA').tobytes())
                self.assertEqual(raw[67::4], b'\xff' * 1024000)
                self.assertEqual(independent_fnv(raw[64:]), stamp)
                self.assertEqual(receipt['sha256'], expected_sha)

    def test_fnv_convention(self):
        self.assertEqual(API['fnv'](b''), 14695981039346656037)
        self.assertEqual(API['fnv'](b'hello'), 0xa430d84680aabd0b)

    def test_malformed_headers_are_rejected(self):
        for name, (raw, _) in self.bundles.items():
            words = list(HEADER.unpack_from(raw))
            mutations = {
                'magic': (0, b'HDR1'), 'version': (1, 2), 'density': (2, 8),
                'title-not-manufacturer': (3, 4), 'palette': (4, 0),
                'width': (5, 0xffffffff), 'height': (6, 0xffffffff),
                'payload-length': (7, 0xffffffff), 'index-guard': (8, 0),
                'palette-guard': (9, 0), 'payload-fnv': (10, 0), 'reserved': (11, 1),
            }
            for label, (at, value) in mutations.items():
                with self.subTest(name=name, field=label):
                    changed = words.copy()
                    changed[at] = value
                    with self.assertRaises(ValueError):
                        API['validate_resource'](HEADER.pack(*changed) + raw[64:])
            with self.assertRaises(ValueError):
                API['validate_resource'](raw, 12 if words[3] == 10 else 10)

    def test_size_corruption_and_transparency_are_rejected(self):
        for name, (raw, _) in self.bundles.items():
            for size in (0, 1, 63, 64, 4096063):
                with self.subTest(name=name, truncated=size), self.assertRaises(ValueError):
                    API['validate_resource'](raw[:size])
            with self.assertRaises(ValueError):
                API['validate_resource'](raw + b'\x00')
            corrupt = bytearray(raw)
            corrupt[64] ^= 1
            with self.assertRaises(ValueError):
                API['validate_resource'](corrupt)
            # Even a recomputed checksum cannot authorize alpha holes.
            corrupt = bytearray(raw)
            corrupt[67] = 254
            struct.pack_into('<Q', corrupt, 48, independent_fnv(corrupt[64:]))
            with self.assertRaises(ValueError):
                API['validate_resource'](corrupt)

    def test_gameplay_manifest_guard_rejects_widening(self):
        original = self.manifest
        target = original['default_debug_pack']
        for case in ('unknown-entry', 'old-entry-change', 'known-entry-change', 'partial-family', 'linked31-partial', 'linked31-change', 'newsh4-partial', 'newsh4-change', 'opposite7-partial', 'opposite7-change', 'wrong-count'):
            with self.subTest(case=case):
                changed = json.loads(json.dumps(original))
                pack = changed['packs'][target]
                if case == 'unknown-entry':
                    pack['files']['unapproved-extra.hda'] = dict(next(iter(pack['files'].values())))
                    pack['count'] += 1
                elif case == 'old-entry-change':
                    name = next(name for name in pack['files'] if name not in FROZEN_GAMEPLAY_ADDITIONS)
                    pack['files'][name]['sha256'] = '0' * 64
                elif case == 'known-entry-change':
                    pack['files']['enemy-newsh2-163-8.hda']['sha256'] = '0' * 64
                elif case == 'partial-family':
                    del pack['files']['enemy-newsh2-163-8.hda']
                    pack['count'] -= 1
                elif case == 'linked31-partial':
                    del pack['files']['enemy-newsh2-15-8.hda']
                    pack['count'] -= 1
                elif case == 'newsh4-partial':
                    del pack['files']['enemy-newsh4-153-8.hda']
                    pack['count'] -= 1
                elif case == 'newsh4-change':
                    pack['files']['enemy-newsh4-155-8.hda']['sha256'] = '0' * 64
                elif case == 'opposite7-partial':
                    del pack['files']['enemy-newsh4-231-8.hda']
                    pack['count'] -= 1
                elif case == 'opposite7-change':
                    pack['files']['enemy-newsh4-273-8.hda']['sha256'] = '0' * 64
                elif case == 'linked31-change':
                    pack['files']['terrain-shapesz-161-8.hda']['sha256'] = '0' * 64
                else:
                    pack['count'] += 1
                self.manifest = changed
                try:
                    with self.assertRaises(AssertionError):
                        self.test_gameplay_manifest_unchanged()
                finally:
                    self.manifest = original

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
                        self.test_gameplay_manifest_unchanged()
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
                        self.test_gameplay_manifest_unchanged()

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
                        self.test_gameplay_manifest_unchanged()
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
                        self.test_gameplay_manifest_unchanged()

    def _assert_type15_v2_projection(self):
        # Exercise the complete C gate directly, before the independently
        # failing historical settings-manifest check can short-circuit it.
        current = json.loads(json.dumps(self.manifest))
        project_type15_family(self, current)
        prior = json.loads(subprocess.check_output(
            ['git', 'show', 'f3bcc061d8a136e257e9c36d40629b4f948a1708:assets/hd/manifest.json'], cwd=ROOT))
        prior.pop('enemy_type15_eightheading_v1')
        for key in ('default_preview_pack', 'default_debug_pack'):
            pack = prior['packs'][prior[key]]
            for identity in TYPE15['ids']:
                entry = pack['files'].pop(f'enemy-newsh2-{identity}-8.hda')
                pack['count'] -= 1
                prior['source_pngs'].pop(entry['sha256'], None)
        self.assertEqual(current, prior)

    def test_type15_v2_complete_guard_passes(self):
        self._assert_type15_v2_projection()

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
                        self._assert_type15_v2_projection()
                finally:
                    self.manifest = original

    def test_type15_coexistence_guard_rejects_changed_artwork_bytes(self):
        # Intercept reads only: shared historical assets are never mutated.
        filename = 'enemy-newsh2-91-8.hda'
        targets = [ROOT / TYPE15_FILES[filename]['source_png'],
                   ROOT / 'assets/hd/packs' / self.manifest['default_preview_pack'] / filename,
                   ROOT / TYPE15['source'] / 'SHA256SUMS.json',
                   ROOT / TYPE15['source'] / 'IMPORT.json']
        read_bytes = Path.read_bytes
        for target in targets:
            with self.subTest(path=target):
                def changed_bytes(path):
                    raw = read_bytes(path)
                    return raw[:-1] + bytes([raw[-1] ^ 1]) if path == target else raw
                with mock.patch.object(Path, 'read_bytes', changed_bytes):
                    with self.assertRaises(AssertionError):
                        self._assert_type15_v2_projection()

    def test_gameplay_manifest_unchanged(self):
        # The unchanged startup resources coexist with reviewed finite art
        # families. Validate their exact entries/bytes and complete default-pack
        # scope before comparing every remaining entry to the original pin.
        without_type15 = json.loads(json.dumps(self.manifest))
        from settings_font_coexistence import project_settings_family
        project_settings_family(self, without_type15)
        project_type3_small_family(self, without_type15)
        project_newsh4_entry6_family(self, without_type15)
        project_late_spike_family(self, without_type15)
        project_type15_family(self, without_type15)
        packs = without_type15['packs']
        defaults = {self.manifest['default_preview_pack'], self.manifest['default_debug_pack']}
        self.assertEqual(len(defaults), 2)
        groups = [
            ('terrain_layer3_mechanical_round_inserts_v1', [190, 200], [367, 368], 'terrain-shapesz'),
            ('enemy_type4_fivepose_v1', [159, 161, 163, 165, 167], [369, 370, 371, 372, 373], 'enemy-newsh2'),
            ('newsh4_long7_v1', [153, 155, 157, 159, 191, 193, 195], list(range(382, 389)), 'enemy-newsh4'),
            ('newsh4_opposite7_v1', [231, 233, 235, 267, 269, 271, 273], list(range(389, 396)), 'enemy-newsh4'),
        ]
        for family, ids, slots, prefix in groups:
            names = [f'{prefix}-{sprite_id}-8.hda' for sprite_id in ids]
            present = any(name in pack['files'] for pack in packs.values() for name in names)
            if not present:
                self.assertNotIn(family, self.manifest)
                continue
            self.assertEqual(self.manifest[family]['ids'], ids)
            self.assertEqual(self.manifest[family]['slots'], slots)
            for name in names:
                expected = FROZEN_GAMEPLAY_ADDITIONS[name]
                self.assertEqual({key for key, pack in packs.items() if name in pack['files']}, defaults)
                for key in defaults:
                    pack = packs[key]
                    self.assertEqual(pack['count'], len(pack['files']))
                    self.assertEqual(pack['files'][name], expected)
                    raw = (ROOT / 'assets/hd/packs' / key / name).read_bytes()
                    self.assertEqual(digest(raw), expected['sha256'])
                    self.assertEqual(raw[:28], b'HDR1' + struct.pack('<6I', *expected['header_u32']))
                    self.assertEqual(digest((ROOT / expected['source_png']).read_bytes()), expected['source_png_sha256'])
                    del pack['files'][name]
                    pack['count'] -= 1
        linked_ids = [161, 162, 171, 172, 15, 17, 53, 55]
        linked_names = [('terrain-shapesz' if i < 4 else 'enemy-newsh2') + f'-{sprite_id}-8.hda'
                        for i, sprite_id in enumerate(linked_ids)]
        linked_present = any(name in pack['files'] for pack in packs.values() for name in linked_names)
        if linked_present:
            family = self.manifest['linked31_installation_v1']
            self.assertEqual(family['entries'], [
                {'kind': 'terrain' if i < 4 else 'actor', 'bank_role': 201 if i < 4 else 101,
                 'id': sprite_id, 'slot': 374 + i, 'anchor': [0, 0] if i < 4 else [6, 7]}
                for i, sprite_id in enumerate(linked_ids)])
            for name in linked_names:
                expected = FROZEN_GAMEPLAY_ADDITIONS[name]
                self.assertEqual({key for key, pack in packs.items() if name in pack['files']}, defaults)
                for key in defaults:
                    pack = packs[key]
                    self.assertEqual(pack['count'], len(pack['files']))
                    self.assertEqual(pack['files'][name], expected)
                    raw = (ROOT / 'assets/hd/packs' / key / name).read_bytes()
                    self.assertEqual(digest(raw), expected['sha256'])
                    self.assertEqual(raw[:28], b'HDR1' + struct.pack('<6I', *expected['header_u32']))
                    self.assertEqual(digest((ROOT / expected['source_png']).read_bytes()), expected['source_png_sha256'])
                    del pack['files'][name]
                    pack['count'] -= 1
        else:
            self.assertNotIn('linked31_installation_v1', self.manifest)
        self.assertNotIn(PACK, packs)
        self.assertEqual(digest(json.dumps(packs, sort_keys=True, separators=(',', ':')).encode()),
                         'e21f03ac25ac166c432e8270357830aba12d1621dbdd2d8063c5823c2c2b7b4b')
        self.assertEqual(len(packs), 18)
        self.assertEqual(sum(len(pack['files']) for pack in packs.values()), 2982)
        self.assertEqual(len({item['source_png'] for pack in packs.values() for item in pack['files'].values()}), 387)
        self.assertEqual([packs[self.manifest[key]]['count'] for key in
                          ('default_preview_pack', 'default_debug_pack')], [371, 375])
        self.assertEqual(self.manifest['default_preview_pack'],
                         'packed-talon13-foundation-type10-death-effects-white-smoke-shield-green-v2-head-v1-test')
        self.assertEqual(self.manifest['default_debug_pack'],
                         'packed-blue-four-foundation-type10-death-effects-white-smoke-shield-green-v2-head-v1-test')

    def test_original_pixel_files_excluded_and_provenance_exact(self):
        source = ROOT / SOURCE
        imported = json.loads((source / 'import.json').read_text())
        self.assertEqual(len(imported['omitted_files']), 4)
        imported_names = {path.relative_to(source).as_posix() for path in source.rglob('*') if path.is_file()}
        self.assertEqual(imported_names, SOURCE_FILES)
        for entry in imported['omitted_files']:
            self.assertNotIn(entry['pilot_path'], imported_names)
            self.assertFalse(any(path.name == Path(entry['pilot_path']).name for path in source.rglob('*.png')))
        for entry in imported['copied_files']:
            data = (source / entry['imported_path']).read_bytes()
            self.assertEqual((len(data), digest(data)), (entry['bytes'], entry['sha256']))

    def test_fresh_standalone_and_master_only_relocation(self):
        source = ROOT / SOURCE
        before = {name: digest((source / name).read_bytes()) for name in SOURCE_FILES}
        with tempfile.TemporaryDirectory(prefix='manufacturer-source-only-') as tmp:
            root = Path(tmp)
            cwd = root / 'unrelated working directory'
            cwd.mkdir()
            canonical = root / 'canonical output with spaces'
            self.call(source / 'build_resource.py', '--output', canonical, cwd=cwd)
            # No canonical images, original game files, prior HDA files, or repo
            # modules are copied into this independently relocated source tree.
            relocated = root / 'relocated generated masters with spaces'
            relocated.mkdir()
            shutil.copytree(source / 'masters', relocated / 'masters')
            for name in ('build_resource.py', 'build_previews.py', 'requirements.txt'):
                shutil.copyfile(source / name, relocated / name)
            self.assertFalse((relocated / 'previews').exists())
            output = root / 'relocated resource output'
            self.call(relocated / 'build_resource.py', '--from-masters', '--output', output, cwd=cwd)
            for name, (raw, _) in self.bundles.items():
                self.assertEqual((canonical / name).read_bytes(), raw)
                self.assertEqual((output / name).read_bytes(), raw)
            self.call(relocated / 'build_resource.py', '--validate',
                      *(output / name for name in sorted(RUNTIME_FILES)), cwd=cwd, optimize=True)
            preview_output = root / 'fresh regenerated preview output'
            self.call(relocated / 'build_previews.py', '--output', preview_output, cwd=cwd)
            for name in SOURCE_FILES:
                if name.startswith('previews/'):
                    self.assertEqual((preview_output / Path(name).name).read_bytes(), (source / name).read_bytes())
            # Source tree and existing output cannot be used as output targets.
            for invalid in (output, relocated, relocated / 'nested output'):
                self.call(relocated / 'build_resource.py', '--from-masters', '--output', invalid,
                          cwd=cwd, success=False)
            corrupt = root / 'corrupt.hda'
            corrupt.write_bytes(next(iter(self.bundles.values()))[0][:-1])
            self.call(relocated / 'build_resource.py', '--validate', corrupt,
                      cwd=cwd, success=False, optimize=True)
        self.assertEqual(before, {name: digest((source / name).read_bytes()) for name in SOURCE_FILES})

    def test_relocated_inventory_and_corrupt_input_rejections(self):
        with tempfile.TemporaryDirectory(prefix='manufacturer-repo-check-') as tmp:
            repo = Path(tmp) / 'relocated repository with spaces'
            source = repo / SOURCE
            shutil.copytree(ROOT / SOURCE, source)
            pack = repo / 'assets/hd/packs' / PACK
            shutil.copytree(ROOT / 'assets/hd/packs' / PACK, pack)
            manifest_path = repo / 'assets/hd/manifest.json'
            manifest_path.write_text(json.dumps(self.manifest))
            self.assertEqual(build_bundles(repo), self.bundles)
            unexpected = source / 'unexpected.txt'
            unexpected.write_text('not frozen artwork')
            with self.assertRaises(ValueError):
                build_bundles(repo)
            unexpected.unlink()
            png = source / 'previews/pic10-candidate-native4x.png'
            original = png.read_bytes()
            png.write_bytes(original[:-1] + bytes([original[-1] ^ 1]))
            with self.assertRaises(ValueError):
                build_bundles(repo)
            png.write_bytes(original)
            moved = repo / 'outside-image.png'
            png.rename(moved)
            png.symlink_to(moved)
            with self.assertRaises(ValueError):
                build_bundles(repo)
            png.unlink()
            moved.rename(png)
            runtime = pack / 'startup-pic10-v1.hda'
            original = runtime.read_bytes()
            changed = bytearray(original)
            changed[64] ^= 1
            # Binary-valid but unreviewed pixels must still fail package checks.
            struct.pack_into('<Q', changed, 48, independent_fnv(changed[64:]))
            API['validate_resource'](changed)
            runtime.write_bytes(changed)
            with self.assertRaises(ValueError):
                build_bundles(repo)
            runtime.write_bytes(original)
            extra_runtime = pack / 'startup-pic4-v1.hda'
            extra_runtime.write_bytes(original)
            with self.assertRaises(ValueError):
                build_bundles(repo)


if __name__ == '__main__':
    unittest.main(verbosity=2)
