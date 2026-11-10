#!/usr/bin/env python3
"""Reproducible ASTEROID2 input inventory, not a runtime completeness certificate.

Reads user-supplied original data locally; emits derived counts/identities/hashes,
never original map cells, lookup arrays, event streams, text or sprite pixels.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import struct

from preflight_fork284 import inspect_stream, parse_events, read_bounded

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    'tyrian1.lvl': '54cbb00b57b84aa992a70cfcb170cb1edeb59507873723630d60080ba8351352',
    'tyrian.hdt': 'fde8506326e7bb0916b38c362e33bf8a8a5affa561206c021af7f65b4a17745b',
    'shapesz.dat': '3ecc9b59c82e8e7d9c91889aac7d337ca28a59519c4970e256250e4603a9b248',
    'levels1.dat': '2c2f5b8509ac44442592580c329f2b3c48a4bf972df7d049a9f174cc2c81c427',
}
BANKS = "2478ABCDEFGHIJKLMNOPQRSTU5#V0@3^59'%"
CREATE_TYPES = {6, 7, 10, 15, 17, 18, 23, 32, 56}
KNOWN_TYPES = {2, 4, 5, 6, 7, 9, 10, 11, 12, 14, 15, 16, 19, 20, 21, 31, 33, 39, 45, 79}


def sha(data):
    return hashlib.sha256(data).hexdigest()


class Reader:
    def __init__(self, data, start=0, end=None):
        self.data, self.pos = data, start
        self.end = len(data) if end is None else end
        if not 0 <= start <= self.end <= len(data):
            raise ValueError('invalid section bounds')

    def take(self, size):
        if size < 0 or self.pos + size > self.end:
            raise ValueError('truncated input section')
        result = self.data[self.pos:self.pos + size]
        self.pos += size
        return result

    def unpack(self, fmt):
        return struct.unpack(fmt, self.take(struct.calcsize(fmt)))


def identity(data):
    reader, section = Reader(data), 0
    key = (204, 129, 63, 255, 71, 19, 25, 62, 1, 99)
    matches = []
    while reader.pos < reader.end:
        raw = reader.take(reader.unpack('<B')[0])
        line = bytes(v ^ key[i % 10] ^ (raw[i-1] if i else 0)
                     for i, v in enumerate(raw)).decode('latin1')
        if line.startswith('*'):
            section += 1
        if section == 6 and line.startswith(']L'):
            matches.append((line[13:22], int(line[25:])))
    if matches != [('ASTEROID2', 2)]:
        raise ValueError('Episode 1 script section 6 is not ASTEROID2 physical 2')
    return {'episode': 1, 'script_section': 6, 'physical_level': 2, 'name': 'ASTEROID2'}


def parse_level(data):
    raw = parse_events(data)  # validates ordered offsets and exact physical-2 header
    proof = inspect_stream(raw)
    count = struct.unpack_from('<H', data)[0]
    offsets = struct.unpack_from(f'<{count}i', data, 2)
    if count < 5:
        raise ValueError('missing map end offset')
    reader = Reader(data, offsets[2] + 8, offsets[3])
    n = reader.unpack('<H')[0]
    if n > 40:
        raise ValueError('random enemy list exceeds native capacity')
    random = reader.unpack(f'<{n}H')
    reader.take(2 + len(raw))
    if reader.pos != reader.end:
        raise ValueError('unexpected event section tail')
    reader = Reader(data, offsets[3], offsets[4])
    # Native loader reads LE words then explicitly SDL_Swap16: disk is BE.
    lookup = [reader.unpack('>128H') for _ in range(3)]
    if any(not 1 <= value <= 600 for row in lookup for value in row):
        raise ValueError('invalid shape lookup identity')
    cells = [reader.take(size) for size in (4200, 8400, 9000)]
    if any(value > 71 for row in cells for value in row):
        raise ValueError('map cell outside native 72-slot loader')
    if reader.pos != reader.end:
        raise ValueError('unexpected map section tail')
    return list(struct.iter_unpack('<HBhhbbbB', raw)), random, lookup, cells, proof


def parse_shapes(data):
    reader, blank = Reader(data), set()
    for shape in range(1, 601):
        flag = reader.unpack('<B')[0]
        if flag not in (0, 1):
            raise ValueError('invalid shape blank flag')
        if flag:
            blank.add(shape)
        else:
            reader.take(672)
    return blank  # native loader intentionally ignores the file trailer


def parse_hdt(data):
    head = Reader(data)
    reader = Reader(data, head.unpack('<i')[0])
    reader.take(14)  # itemNum[7]; native fixed array bounds, not these values
    weapons = {}
    for index in (*range(819), *range(1000, 1819)):
        raw = reader.take(80)
        weapons[index] = {'animation_frames': struct.unpack_from('<H', raw, 4)[0],
                          'multi': raw[3], 'positions': raw[6],
                          'graphics': list(struct.unpack_from('<8H', raw, 58))}
    # Native serialized field sizes, not C sizeof(struct), which includes padding.
    for count, size in ((61, 82), (55, 37), (7, 37), (19, 41), (38, 86), (12, 37)):
        reader.take(count * size)
    enemies = {}
    for index in (*range(851), *range(1001, 1851)):
        raw = reader.take(77)
        dgr, dlevel, dani = struct.unpack_from('<Hbb', raw, 66)
        launch, value, drop = struct.unpack_from('<HhH', raw, 71)
        enemies[index] = {'record': index, 'ani': raw[0], 'turrets': list(raw[1:4]),
                          'frequency': list(raw[4:7]), 'size': raw[20],
                          'graphics': list(struct.unpack_from('<20H', raw, 21)),
                          'explosiontype': raw[61], 'animate': raw[62], 'bank': raw[63],
                          'damage_graphic': dgr, 'damage_level': dlevel, 'damage_animation': dani,
                          'launch_frequency': raw[70], 'launch': launch, 'value': value, 'drop': drop}
    return enemies, weapons


def closure(seeds, enemies):
    result, edges, pending = set(), set(), list(seeds)
    while pending:
        index = pending.pop()
        if index in result:
            continue
        if index not in enemies:
            raise ValueError(f'undefined enemy record {index}')
        result.add(index)
        item = enemies[index]
        launch = item['launch'] if index > 1000 else item['launch'] % 1000
        for kind, target in (('launch', launch if item['launch_frequency'] else 0), ('drop', item['drop'])):
            if target:
                edges.add((index, kind, target))
                pending.append(target)
    return sorted(result), [list(edge) for edge in sorted(edges)]


def base_frames(item):
    if not 1 <= item['ani'] <= 20 or not 1 <= item['bank'] <= len(BANKS):
        raise ValueError('invalid native enemy animation/bank')
    normal = set(item['graphics'][:item['ani']])
    damage = set()
    if item['damage_animation']:
        start, end = item['damage_graphic'], abs(item['damage_animation'])
        if not 1 <= start <= end <= 20:
            raise ValueError('invalid damage animation range')
        damage.update(item['graphics'][start - 1:end])
    elif item['damage_graphic']:
        damage.add(item['damage_graphic'])
    # 999 is the native disappearance sentinel, not an image.
    return sorted(normal - {0, 999}), sorted(damage - {0, 999})


def bank_name(bank):
    return {21: 'coins-gems', 26: 'two-player'}.get(bank, 'newsh' + BANKS[bank - 1].lower())


def art_index(root):
    result = defaultdict(list)
    for path in sorted((root / 'assets/hd').rglob('*.hda')):
        match = re.fullmatch(r'(?:enemy-(newsh.)|terrain-(shapes.))-(\d+)-8.hda', path.name)
        if match:
            result[(match[1] or match[2], int(match[3]))].append(path.relative_to(root).as_posix())
        match = re.fullmatch(r'(?:bullet|enemy-projectile[^/]*|enemy-orb[^/]*|enemy-tank-shell)-(\d+)-8.hda', path.name)
        if match:
            result[('spriteSheet8', int(match[1]))].append(path.relative_to(root).as_posix())
        match = re.fullmatch(r'.*-bank11-(\d+)-8.hda', path.name)
        if match:
            result[('coins-gems', int(match[1]))].append(path.relative_to(root).as_posix())
    return result


def art_entry(bank, frame, index, root):
    files = []
    for name in index.get((bank, frame), []):
        path = root / name
        with path.open('rb') as stream:
            header = stream.read(28)
        files.append({'path': name, 'status': 'hda-header-present' if header[:4] == b'HDR1' else 'invalid-or-lfs-pointer'})
    return {'base': frame, 'files': files,
            'art_status': 'named-art-present' if any(f['status'] == 'hda-header-present' for f in files)
                          else 'no-valid-exact-per-tile-filename-found'}


def terrain_adapter(shape, root):
    reviewed = {372,380,390,367,368,376,378,386,387,388,
                361,362,363,364,365,371,373,374,375,381,382,383,366,340}
    path = Path('experimental/level2-family/src/b313_family_ground_mirror.inc')
    if shape in {339, 348}:
        return {'status': 'guarded-redvent-source-external-assets-required',
                'source': 'experimental/level2-family/src/b313_redvent_pair.inc', 'runtime_full_coverage': False}
    return {'status': 'guarded-adapter-source-present' if shape in reviewed and (root / path).is_file()
            else 'no-reviewed-family-adapter', 'runtime_full_coverage': False}


# Reviewed source associations are evidence of an adapter, never proof it admits
# all frames, damage states, births or lifetimes. Source hashes detect changes.
ADAPTERS = {
    'smallrocks': set(range(317, 325)), 'random_props': {135,136,260,261,263,265,266,268},
    'tank194': {194}, 'ember269': {269}, 'normal270': {270}, 'lamp272': {272},
    'turret273': {273}, 'triple275': {275}, 'fork284': {284}, 'late_actor': {282,285},
    'linked_prop287288': {287,288}, 'gray325': {325}, 'linked338_normal': {338,339,340,341,342},
    'longface573': {573,574,575,576}, 'b313_family_canvas': {313,314,315,316},
}


def adapter_evidence(record, root):
    paths = []
    for name, records in ADAPTERS.items():
        if record in records:
            path = Path('experimental/level2-family/src') / f'{name}_mirror.inc'
            if not (root / path).exists():
                path = path.with_name(f'{name}_family_mirror.inc')
            if (root / path).exists():
                paths.append({'path': path.as_posix(), 'sha256': sha((root / path).read_bytes())})
    archive = []
    archived_names = {'compound309270_asset_pins.inc': set(range(309,313)),
                      'tall_structure_pins.inc': set(range(326,332)) | set(range(343,349)),
                      'launcher271_family_pins.inc': {271,463}, 'firing_rock462_asset_pins.inc': {462}}
    for name, records in archived_names.items():
        if record in records:
            archive.extend(path.relative_to(root).as_posix() for path in sorted((root / 'experimental/late-level/sources').glob('*/' + name)))
    return {'status': 'guarded-adapter-source-present' if paths else
            'archived-source-only-not-current-adapter' if archive else 'no-reviewed-family-adapter',
            'sources': paths, 'archived_pin_tables': archive, 'runtime_full_coverage': False}


def assembly_resources(record, root):
    if record not in range(313,317):
        return []
    files = []
    for phase in range(3):
        path = Path(f'assets/hd/level2-family-v1/building/phase{phase}.argb32le')
        files.append({'path': path.as_posix(), 'status': 'present' if (root / path).is_file() else 'missing',
                      'representation': 'whole-four-actor-assembly-phase-not-a-terrain-tile'})
    return files


def audit(data_dir, root=ROOT):
    data = {}
    for name, pin in PINS.items():
        data[name] = read_bounded(Path(data_dir) / name, 16 * 1024 * 1024)
        if sha(data[name]) != pin:
            raise ValueError(f'{name}: pinned input SHA256 mismatch')
    level_identity = identity(data['levels1.dat'])
    events, random, lookup, cells, proof = parse_level(data['tyrian1.lvl'])
    blank = parse_shapes(data['shapesz.dat'])
    enemies, weapons = parse_hdt(data['tyrian.hdt'])
    counts = Counter(row[1] for row in events)
    if set(counts) - KNOWN_TYPES:
        raise ValueError('unreviewed event type in pinned level')
    scripted = Counter()
    drops, arcade = Counter(), Counter()
    for row in events:
        if row[1] in CREATE_TYPES:
            scripted[row[2]] += 1
        elif row[1] == 12:
            for index in range(row[2], row[2] + 4):
                scripted[index] += 1
        elif row[1] in (33, 45):
            (drops if row[1] == 33 else arcade)[row[2]] += 1
    groups = {'scripted': set(scripted), 'random_candidates': set(random),
              'normal_conditional_drops': set(drops), 'arcade_event45_only': set(arcade),
              'normal_random_special_drop': set(range(829,835)) if 533 in drops else set(),
              'low_armor_conditional': {560,561,562,563}}
    closures, edges = {}, []
    for name, seeds in groups.items():
        closures[name], group_edges = closure(seeds, enemies)
        edges.extend({'scope': name, 'from': edge[0], 'kind': edge[1], 'to': edge[2]} for edge in group_edges)
    art = art_index(root)
    families = []
    for index in sorted(set().union(*map(set, closures.values()))):
        item = enemies[index]
        normal, damaged = base_frames(item)
        bank = bank_name(item['bank'])
        families.append({'record': index, 'scopes': [name for name, ids in closures.items() if index in ids],
                         'scripted_creation_count': scripted[index], 'random_table_weight': random.count(index),
                         'bank_id': item['bank'], 'bank': bank, 'size': item['size'],
                         'normal_base_frames': normal, 'damage_base_frames': damaged,
                         'native_tile_offsets': [0,1,19,20] if item['size'] == 1 else [0],
                         'turret_weapons': [n for n in item['turrets'] if 0 < n < 251],
                         'special_turret_behaviors': [n for n in item['turrets'] if n >= 251],
                         'art': [art_entry(bank, n, art, root) for n in sorted(set(normal + damaged))],
                         'assembly_resources': assembly_resources(index, root),
                         'adapter': adapter_evidence(index, root)})
    terrain = []
    for layer, (lut, cell) in enumerate(zip(lookup, cells), 1):
        slots = Counter(cell)
        visible = Counter()
        null = 0
        for slot, count in slots.items():
            shape = lut[slot]
            if layer > 1 and (shape in blank or slot >= (71 if layer == 2 else 70)):
                null += count
            else:
                visible[shape] += count
        terrain.append({'layer': layer, 'cell_count': len(cell), 'cells_sha256': sha(cell),
                        'lookup_sha256': sha(struct.pack('>128H', *lut)),
                        'lookup_entries_decoded': len(lut), 'used_slots': len(slots), 'null_cells': null,
                        'shapes': [{'shape': shape, 'cells': count, 'blank': shape in blank,
                                    'art': art_entry('shapesz', shape, art, root),
                                    'adapter': terrain_adapter(shape, root)}
                                   for shape, count in sorted(visible.items())]})
    projectiles = []
    for wid in sorted({w for family in families for w in family['turret_weapons']}):
        weapon = weapons[wid]
        if not 1 <= weapon['positions'] <= 8:
            raise ValueError('invalid weapon position count')
        bases = sorted(set(weapon['graphics'][:weapon['positions']]))
        frames = defaultdict(set)
        for base in bases:
            bank, adjusted = ('spriteSheet12', base - 500) if base >= 500 else ('spriteSheet8', base)
            frames[bank].update(range(adjusted, adjusted + max(1, weapon['animation_frames'])))
        projectiles.append({'weapon': wid, 'source_records': [f['record'] for f in families if wid in f['turret_weapons']],
                            'native_base_graphics': bases, 'animation_frames': weapon['animation_frames'],
                            'required_sprite_indices': {bank: sorted(ids) for bank, ids in frames.items()},
                            'art_candidates_requiring_identity_review': {bank: [art_entry(bank, frame, art, root) for frame in sorted(ids)]
                                                                         for bank, ids in frames.items()},
                            'adapter_status': 'guarded-tank-origin-adapter-only' if wid in (2,3) else 'no-reviewed-general-level2-adapter',
                            'observed_in_runtime': False})
    bank_frames = defaultdict(set)
    for family in families:
        bank_frames[family['bank']].update(family['normal_base_frames'] + family['damage_base_frames'])
    return {'schema': 'asteroid2-actual-input-inventory-v1', 'identity': level_identity,
            'input_sha256': PINS, 'complete': False, 'events': {**proof, 'type_counts': dict(sorted(counts.items())),
            'scripted_creation_count': sum(scripted.values()), 'event33_drop_counts': dict(sorted(drops.items())),
            'event45_arcade_drop_counts': dict(sorted(arcade.items()))},
            'random_table_entries': len(random), 'random_distinct_records': len(set(random)),
            'terrain': terrain, 'families': families, 'conditional_closure_edges': edges,
            'bank_base_frame_union_including_conditional_scopes': {bank: sorted(frames) for bank, frames in sorted(bank_frames.items())},
            'enemy_projectiles': projectiles,
            'limitations': [
                'Static input reachability is not evidence that a draw occurred; RNG, kills, links, allocation and mode gates apply.',
                'Event45 arcade drops and normal random-special/low-armor branches are separate conditional scopes, not baseline observations.',
                'SuperTyrian/superArcade remappings and arbitrary player loadouts are not expanded into baseline requirements.',
                'Exact filename artwork matching is an availability hint only. Alternate names, composed canvases and aliases require separate identity review.',
                'Adapter source presence does not establish frame/damage/lifetime admission; runtime_full_coverage remains false.',
                'Player loadout, HUD/font/warning layers, explosions, collision effects and audio require separate runtime inventories.',
                'Normal base frames include declared aiming/animation slots; damaged frames are conditional. Native 999 disappearance is excluded.',
            ]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, required=True)
    parser.add_argument('--require-complete', action='store_true')
    args = parser.parse_args(argv)
    try:
        report = audit(args.data_dir)
    except (OSError, ValueError, struct.error) as error:
        parser.exit(2, f'inventory failed: {error}\n')
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if args.require_complete else 0


if __name__ == '__main__':
    raise SystemExit(main())
