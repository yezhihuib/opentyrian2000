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

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
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
 'enemy-newsh2-159-8.hda': {'sha256': '95299c134dc5e4eab1eb12dfe425205fdca069a93eb019fcad8905feb51b5684',
                            'header_u32': [1010159, 8, 24, 28, 6, 7],
                            'source_png': 'assets/hd/source/enemy-newsh2-159-8-95299c134dc5.png',
                            'source_png_sha256': '085c12d8b17e5e634fa4b3de859845bd022ab8876261b4a96db56c58dfc3916f'},
 'enemy-newsh2-161-8.hda': {'sha256': 'a1b512605f485ef4238e22e5d9cd2d15e3d937a5aa2eac7fab4c49b208425a0d',
                            'header_u32': [1010161, 8, 24, 28, 6, 7],
                            'source_png': 'assets/hd/source/enemy-newsh2-161-8-a1b512605f48.png',
                            'source_png_sha256': 'fa25e9d52e9c9a7d7ad35cb84246bc0d430f008d32160a24ae537bd6240c647d'},
 'enemy-newsh2-163-8.hda': {'sha256': '57ed11e6c01d414846bf7429805b92ed74673357488f133175e0a549024812ee',
                            'header_u32': [1010163, 8, 24, 28, 6, 7],
                            'source_png': 'assets/hd/source/enemy-newsh2-163-8-57ed11e6c01d.png',
                            'source_png_sha256': '652a7ba3c9fc4cb0836a19d38c8bbd64b1b72020215bbb9f805bf6611878d6de'},
 'enemy-newsh2-165-8.hda': {'sha256': '4b10683ba005d54a64be04501c076171580e1c99419a63c4da7a93bab8f2cb91',
                            'header_u32': [1010165, 8, 24, 28, 6, 7],
                            'source_png': 'assets/hd/source/enemy-newsh2-165-8-4b10683ba005.png',
                            'source_png_sha256': '9c4332fbaf819542c995815b4b18a3bba968dee5cf70c62d594a93d43a9ceb46'},
 'enemy-newsh2-167-8.hda': {'sha256': 'ce94f5992c37815ababde4dba95197726a8817df248efa6d6a6f3882b60a7110',
                            'header_u32': [1010167, 8, 24, 28, 6, 7],
                            'source_png': 'assets/hd/source/enemy-newsh2-167-8-ce94f5992c37.png',
                            'source_png_sha256': 'be2a4b76d35b407659b0c0bf996d94dd7a35fcbdecb391b34d05d4a01baad1f4'}}

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


def digest(data):
    return hashlib.sha256(data).hexdigest()


def independent_fnv(data):
    value = 0xcbf29ce484222325
    for byte in data:
        value ^= byte
        value *= 0x100000001b3
        value &= 0xffffffffffffffff
    return value


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

    def test_gameplay_manifest_unchanged(self):
        # The unchanged startup resources coexist with two later finite art
        # families. Validate their exact entries/bytes and complete default-pack
        # scope before comparing every remaining entry to the original pin.
        packs = json.loads(json.dumps(self.manifest['packs']))
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
