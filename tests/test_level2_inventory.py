"""Offline synthetic parser tests; optional pinned-data integration via TYRIAN_DATA."""
import importlib.util
import os
from pathlib import Path
import struct
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import audit_level2_inventory as inventory


def synthetic_level():
    event = struct.pack('<cc3HHHH', b'D', b'Z', 1, 1, 1, 1, 317, 731) + bytes(731 * 11)
    maps = struct.pack('>128H', *([361] * 128)) * 3 + bytes(21600)
    offsets = (26, 27, 28, 28 + len(event), 28 + len(event) + len(maps), 29 + len(event) + len(maps))
    return struct.pack('<H6i', 6, *offsets) + b'xx' + event + maps + b'x'


class ParserTests(unittest.TestCase):
    def parse_synthetic(self, data):
        with patch.object(inventory, 'inspect_stream', return_value={'event_count': 731}):
            return inventory.parse_level(data)

    def test_full_three_maps_and_big_endian_lookup(self):
        events, random, lookup, cells, _ = self.parse_synthetic(synthetic_level())
        self.assertEqual(len(events), 731)
        self.assertEqual(random, (317,))
        self.assertEqual(lookup[0][0], 361)
        self.assertEqual([len(row) for row in cells], [4200,8400,9000])

    def test_truncation_and_bad_offsets(self):
        data = synthetic_level()
        for bad in (b'', b'\x06', data[:25], data[:-2]):
            with self.subTest(length=len(bad)), self.assertRaises(ValueError):
                self.parse_synthetic(bad)
        bad = bytearray(data)
        struct.pack_into('<i', bad, 2 + 3 * 4, 28)
        with self.assertRaises(ValueError):
            self.parse_synthetic(bad)

    def test_lookup_and_cell_bounds(self):
        original = synthetic_level()
        start = struct.unpack_from('<i', original, 14)[0]
        for offset, value in ((start, 255), (start + 768, 72)):
            bad = bytearray(original)
            bad[offset] = value
            with self.assertRaises(ValueError):
                self.parse_synthetic(bad)

    def test_event_pin_rejects_synthetic_stream(self):
        with self.assertRaisesRegex(ValueError, 'stream hash'):
            inventory.parse_level(synthetic_level())

    def test_shapes_blanks_and_truncation(self):
        self.assertEqual(inventory.parse_shapes(bytes([1]) * 600), set(range(1,601)))
        with self.assertRaises(ValueError):
            inventory.parse_shapes(bytes([1]) * 599)
        with self.assertRaises(ValueError):
            inventory.parse_shapes(bytes([2]) * 600)
        with self.assertRaises(ValueError):
            inventory.parse_shapes(bytes([0]))

    def test_hdt_serialized_offsets(self):
        prefix = 4 + 14 + 1638 * 80 + 61 * 82 + 55 * 37 + 7 * 37 + 19 * 41 + 38 * 86 + 12 * 37
        raw = bytearray(prefix + 1701 * 77)
        struct.pack_into('<i', raw, 0, 4)
        raw[prefix + 284 * 77] = 1
        raw[prefix + 284 * 77 + 63] = 8
        struct.pack_into('<H', raw, prefix + 284 * 77 + 21, 121)
        enemies, weapons = inventory.parse_hdt(raw)
        self.assertEqual(len(enemies), 1701)
        self.assertEqual(len(weapons), 1638)
        self.assertEqual(enemies[284]['graphics'][0], 121)
        self.assertEqual(enemies[284]['bank'], 8)
        self.assertNotIn(851, enemies)
        self.assertIn(1001, enemies)
        for bad in (b'', raw[:-1], struct.pack('<i', -1)):
            with self.assertRaises(ValueError):
                inventory.parse_hdt(bad)

    def test_damage_frames_are_not_damage_record_numbers(self):
        item = {'ani': 4, 'bank': 23, 'graphics': [203,203,279,279,999,281] + [0]*14,
                'damage_animation': -6, 'damage_graphic': 6}
        self.assertEqual(inventory.base_frames(item), ([203,279], [281]))
        item.update(damage_animation=0, damage_graphic=273)
        self.assertEqual(inventory.base_frames(item)[1], [273])

    def test_closure_terminates_cycles_and_respects_launch_frequency(self):
        enemies = {1: {'launch': 1002, 'launch_frequency': 1, 'drop': 0},
                   2: {'launch': 1, 'launch_frequency': 1, 'drop': 3},
                   3: {'launch': 999, 'launch_frequency': 0, 'drop': 0}}
        ids, edges = inventory.closure([1], enemies)
        self.assertEqual(ids, [1,2,3])
        self.assertIn([1,'launch',2], edges)
        with self.assertRaises(ValueError):
            inventory.closure([4], enemies)

    def test_script_identity(self):
        def encrypt(line):
            key = [204,129,63,255,71,19,25,62,1,99]
            encrypted = bytearray()
            for i, value in enumerate(line.encode()):
                encrypted.append(value ^ key[i % 10] ^ (encrypted[-1] if i else 0))
            return bytes([len(encrypted)]) + encrypted
        raw = encrypt('*') * 6 + encrypt(']L[ 9999 008 ASTEROID202 02')
        self.assertEqual(inventory.identity(raw)['script_section'], 6)
        with self.assertRaises(ValueError):
            inventory.identity(raw[:-1])
        with self.assertRaises(ValueError):
            inventory.identity(encrypt('*') * 5 + encrypt(']L[ 9999 008 ASTEROID202 02'))

    def test_input_hash_gate(self):
        with patch.object(inventory, 'read_bounded', return_value=b'wrong'):
            with self.assertRaisesRegex(ValueError, 'SHA256 mismatch'):
                inventory.audit(Path('/unused'))


@unittest.skipUnless(os.environ.get('TYRIAN_DATA'), 'set TYRIAN_DATA for private pinned input integration')
class PinnedIntegration(unittest.TestCase):
    def test_actual_asteroid2(self):
        report = inventory.audit(Path(os.environ['TYRIAN_DATA']))
        self.assertEqual(report['events']['event_count'], 731)
        self.assertEqual(report['events']['scripted_creation_count'], 371)
        self.assertEqual(report['random_table_entries'], 33)
        self.assertEqual(report['random_distinct_records'], 17)
        self.assertEqual([row['cell_count'] for row in report['terrain']], [4200,8400,9000])
        self.assertEqual([row['null_cells'] for row in report['terrain']], [0,8400,9000])
        self.assertEqual(len(report['terrain'][0]['shapes']), 63)
        families = {row['record']: row for row in report['families']}
        self.assertEqual(families[284]['normal_base_frames'], [121])
        self.assertEqual(families[271]['normal_base_frames'], [275,277,279])
        self.assertEqual(families[463]['normal_base_frames'], [191])
        self.assertEqual(families[551]['normal_base_frames'], [171,190,209])
        self.assertEqual(families[602]['scopes'], ['arcade_event45_only'])
        self.assertNotIn('scripted', families[829]['scopes'])
        self.assertFalse(report['complete'])


if __name__ == '__main__':
    unittest.main()
