"""Two independent editable orb masters feed ordinary and opt-in contracts.

Fixed mask transcribed from approved public output, then authenticated against
original-bank decoder. No original game data is a build input or redistributed.
"""
import json
import struct
from current_plasma_projectile_compatibility import sha, parse, read, image, is_hash
from current_craft267_compatibility import path

ORDINARY_IDS = (80112, 80113)
OPTIN_IDS = (1420112, 1420113)
IDS = ORDINARY_IDS + OPTIN_IDS
PAIRS = tuple((i, 8) for i in IDS)
SELECTION = 'assets/hd/authoring/enemy-orb-current.json'
MAPPING = 'packaging/current-enemy-orb-compatibility.json'
HEADER = 'src/current_enemy_orb_payload_pins.h'
ROOT = 'assets/hd/current-compat/enemy-orb'
INPUT_ROOT = 'authoring-inputs/enemy-orb-current'
SCHEMA = 'opentyrian-current-enemy-orb-authoring-v1'
CANDIDATE_SCHEMA = 'opentyrian-current-enemy-orb-candidate-v1'
MASK = '000000000000000000000000000000000000000000000000000011111000000111111100000111111100000111111100000111111100000111111100000011111000000000000000000000000000000000000000'


def name(identity, density=8):
    if type(identity) is not int or type(density) is not int or (identity, density) not in PAIRS:
        raise ValueError('Unknown orb identity/density')
    return (f'bullet-{identity-80000}-8.hda' if identity in ORDINARY_IDS else
            f'enemy-orb112113-{identity-1420000}-8.hda')


def selection(root, raw, candidate=False):
    selected = parse(raw)
    if (not isinstance(selected, dict) or set(selected) != {'schema', 'version', 'masters'} or
            selected['schema'] != (CANDIDATE_SCHEMA if candidate else SCHEMA)):
        raise ValueError('Invalid orb selection schema/fields')
    if not isinstance(selected['version'], str) or not 1 <= len(selected['version']) <= 128:
        raise ValueError('Invalid orb version')
    if not isinstance(selected['masters'], list) or len(selected['masters']) != 2:
        raise ValueError('Expected two independent orb masters')
    paths = set()
    for selector, row in zip((112, 113), selected['masters']):
        if (not isinstance(row, dict) or set(row) != {'selector', 'source_png', 'source_sha256'} or
                type(row['selector']) is not int or row['selector'] != selector or not is_hash(row['source_sha256'])):
            raise ValueError('Invalid orb master identity/order/hash')
        source = row['source_png']
        # Fixed isolated source namespace excludes generated transports and all
        # other authoring families; identity-specific file names prevent aliasing.
        if source != f'{INPUT_ROOT}/orb-{selector}.png' or source in paths:
            raise ValueError('Expected independent authoritative orb master path')
        paths.add(source)
        if path(root, source).stat().st_nlink != 1:
            raise ValueError('Orb master must not be hardlinked')
        if sha(read(root, source)) != row['source_sha256']:
            raise ValueError('Orb master changed')
    return selected


def generate(root, raw, candidate=False):
    selected = selection(root, raw, candidate)
    blobs = {}
    for row in selected['masters']:
        selector = row['selector']
        original = image(read(root, row['source_png']), (96, 112)).tobytes()
        masked = bytearray(original)
        occupied = set()
        for y in range(112):
            for x in range(96):
                cell = (y//8)*12+x//8
                p = (y*96+x)*4
                if MASK[cell] == '0':
                    masked[p:p+4] = b'\0\0\0\0'
                elif original[p+3]:
                    occupied.add(cell)
        if len(occupied) != 45:
            raise ValueError('Orb master does not cover every fixed mask cell')
        for identity, payload in ((80000+selector, original), (1420000+selector, masked)):
            blobs[(identity, 8)] = struct.pack('<4s6I', b'HDR1', identity, 8, 12, 14, 0, 0) + payload
    return dict(selected, schema=SCHEMA), {}, {pair: blobs[pair] for pair in PAIRS}


def payload_header(pins):
    if set(pins) != set(PAIRS):
        raise ValueError('Expected four orb payload pins')
    lines = ['/* Generated opt-in orb payload-only pins; eligibility and geometry stay fixed. */',
             '#ifndef CURRENT_ENEMY_ORB_PAYLOAD_PINS_H', '#define CURRENT_ENEMY_ORB_PAYLOAD_PINS_H']
    for identity in OPTIN_IDS:
        value = pins[(identity, 8)]
        import re
        if not isinstance(value, str) or not re.fullmatch('[0-9a-f]{16}', value):
            raise ValueError('Invalid orb payload pin')
        lines.append(f'#define CURRENT_ENEMY_ORB_{identity}_PAYLOAD_FNV UINT64_C(0x{value})')
    return ('\n'.join(lines)+'\n#endif\n').encode()


def input_paths(root):
    selected = selection(root, read(root, SELECTION, 128*1024))
    return {SELECTION, MAPPING, HEADER} | {r['source_png'] for r in selected['masters']} | {ROOT+'/'+name(i) for i in IDS}


def load(root):
    from build_current_art import fnv
    selected, _, blobs = generate(root, read(root, SELECTION, 128*1024))
    rows, result, pins = [], {}, {}
    for (identity, density), blob in blobs.items():
        source, destination = ROOT+'/'+name(identity), 'assets/gameplay/'+name(identity)
        if read(root, source) != blob:
            raise ValueError('Orb transport does not match current master and fixed contract')
        row = dict(identity=identity, density=density, source_path=source, destination=destination, sha256=sha(blob))
        rows.append(row); result[destination] = row; pins[(identity, density)] = fnv(blob[28:])
    expected = dict(schema='opentyrian-current-enemy-orb-compatibility-v1', selection=SELECTION, version=selected['version'], files=rows)
    if json.dumps(parse(read(root, MAPPING)), sort_keys=True) != json.dumps(expected, sort_keys=True):
        raise ValueError('Stale orb compatibility mapping')
    if read(root, HEADER) != payload_header(pins):
        raise ValueError('Stale orb payload pins')
    return result
