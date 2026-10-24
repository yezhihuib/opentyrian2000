"""Finite four-master Guided input and four independent current transports.

Each independent static identity has its own source; no animation or mirroring.
Identity, geometry, density, split, and resize are fixed; no executable recipe.
"""
import hashlib
import io
import json
import re
import stat
import struct
import zlib

from PIL import Image
from current_craft267_compatibility import path

IDS = (80019, 80171, 80020, 80021)
SELECTORS = (19, 171, 20, 21)
ENEMY_PAIRS = ((80020, 8), (80021, 8))
PAIRS = tuple((identity, 8) for identity in IDS)
SELECTION = 'assets/hd/authoring/guided-current.json'
MAPPING = 'packaging/current-guided-compatibility.json'
HEADER = 'src/current_guided_payload_pins.h'
ROOT = 'assets/hd/current-compat/guided'
INPUT_ROOT = 'authoring-inputs/guided-current'
SCHEMA = 'opentyrian-current-guided-authoring-v1'
CANDIDATE_SCHEMA = 'opentyrian-current-guided-candidate-v1'
RECIPE = {'schema': 'guided-fixed-recipe-v1', 'canvas': [96, 112], 'logical_size': [12, 14], 'density': 8, 'anchor': [0, 0], 'resample': 'Pillow-LANCZOS-straight-RGBA-paste-without-mask', 'pieces': [{'selector': 19, 'source_size': [1160, 1355], 'crop': [74, 180, 1086, 1173], 'size': [82, 82], 'xy': [7, 15], 'identity': 80019}, {'selector': 171, 'source_size': [1160, 1355], 'crop': [160, 260, 1001, 1098], 'size': [82, 82], 'xy': [7, 15], 'identity': 80171}, {'selector': 20, 'source_size': [1060, 1484], 'crop': [99, 151, 956, 1352], 'size': [46, 62], 'xy': [29, 29], 'identity': 80020}, {'selector': 21, 'source_size': [938, 1677], 'crop': [130, 116, 811, 1589], 'size': [44, 76], 'xy': [30, 22], 'identity': 80021}], 'alpha': 'preserve-without-original-mask-or-threshold', 'relationship': 'four-independent-static-identities'}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def parse(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate Guided JSON key: ' + key)
            result[key] = value
        return result

    def invalid(value):
        raise ValueError('Non-finite Guided JSON number: ' + value)

    if len(raw) > 128 * 1024:
        raise ValueError('Oversize Guided JSON')
    return json.loads(raw, object_pairs_hook=unique, parse_constant=invalid)


def read(root, name, limit=16 * 1024 * 1024):
    p = path(root, name)
    if not p.is_file() or not stat.S_ISREG(p.lstat().st_mode) or p.stat().st_size > limit:
        raise ValueError('Missing/oversize regular Guided input: ' + name)
    return p.read_bytes()


def name(identity, density):
    if type(identity) is not int or type(density) is not int or (identity, density) not in PAIRS:
        raise ValueError('Unknown Guided projectile identity/density')
    return f'bullet-{identity - 80000}-8.hda'


def png(identity, density):
    return INPUT_ROOT + '/derived/' + name(identity, density).removesuffix('.hda') + '.png'


def generated_paths():
    return {png(identity, density) for identity, density in PAIRS}


def is_hash(value):
    return isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value) is not None


def selection(root, raw, candidate=False):
    selected = parse(raw)
    keys = {'schema', 'version', 'masters', 'recipe'} | (set() if candidate else {'resources'})
    schema = CANDIDATE_SCHEMA if candidate else SCHEMA
    if not isinstance(selected, dict) or set(selected) != keys or selected['schema'] != schema:
        raise ValueError('Invalid Guided candidate/installed schema or fields')
    if not isinstance(selected['version'], str) or not 1 <= len(selected['version']) <= 128:
        raise ValueError('Invalid Guided version')
    if not isinstance(selected['masters'], list) or len(selected['masters']) != 4:
        raise ValueError('Expected four independent Guided masters')
    for selector, row in zip(SELECTORS, selected['masters']):
        if (not isinstance(row, dict) or set(row) != {'selector','source_png','source_sha256'} or
                type(row['selector']) is not int or row['selector'] != selector or
                row['source_png'] != INPUT_ROOT + f'/master-{selector}.png' or not is_hash(row['source_sha256'])):
            raise ValueError('Invalid Guided master identity/path/hash/order')
        if sha(read(root, row['source_png'])) != row['source_sha256']:
            raise ValueError('Selected Guided master changed')
    row = selected['recipe']
    if (not isinstance(row, dict) or set(row) != {'path','sha256'} or
            row['path'] != INPUT_ROOT + '/recipe.json' or not is_hash(row['sha256']) or
            sha(read(root, row['path'])) != row['sha256']):
        raise ValueError('Invalid/changed Guided recipe record')
    if not candidate:
        if not isinstance(selected['resources'], list) or len(selected['resources']) != 4:
            raise ValueError('Expected four derived Guided pieces')
        for (identity, density), row in zip(PAIRS, selected['resources']):
            if (not isinstance(row, dict) or set(row) != {'identity', 'density', 'source_png', 'source_sha256'} or
                    type(row['identity']) is not int or type(row['density']) is not int or
                    (row['identity'], row['density']) != (identity, density) or
                    row['source_png'] != png(identity, density) or not is_hash(row['source_sha256'])):
                raise ValueError('Invalid derived Guided identity/density/path/order/hash')
    return selected


def image(raw, size):
    """Decode only bounded, complete, single-frame, CRC-valid straight RGBA8 PNG."""
    if len(raw) > 16 * 1024 * 1024 or raw[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('Expected bounded Guided PNG')
    offset = 8
    kinds = []
    while offset < len(raw):
        if offset + 12 > len(raw):
            raise ValueError('Truncated Guided PNG chunk')
        length = struct.unpack('>I', raw[offset:offset + 4])[0]
        end = offset + 12 + length
        if end > len(raw):
            raise ValueError('Truncated Guided PNG data')
        kind = raw[offset + 4:offset + 8]
        body = raw[offset + 8:end - 4]
        if zlib.crc32(kind + body) & 0xffffffff != struct.unpack('>I', raw[end - 4:end])[0]:
            raise ValueError('Guided PNG CRC mismatch')
        if not kinds and (kind != b'IHDR' or body != struct.pack('>IIBBBBB', *size, 8, 6, 0, 0, 0)):
            raise ValueError('Unexpected Guided PNG dimensions/straight RGBA8 encoding')
        if (kind in (b'acTL', b'fcTL', b'fdAT') or
                (kind not in (b'IHDR', b'PLTE', b'IDAT', b'IEND') and not kind[0] & 32)):
            raise ValueError('Animated/unknown critical Guided PNG chunk')
        kinds.append(kind)
        offset = end
        if kind == b'IEND':
            if length or offset != len(raw):
                raise ValueError('Trailing Guided PNG data')
            break
    if kinds.count(b'IHDR') != 1 or kinds.count(b'IEND') != 1 or b'IDAT' not in kinds:
        raise ValueError('Expected complete Guided PNG')
    try:
        with Image.open(io.BytesIO(raw)) as decoded:
            decoded.verify()
        with Image.open(io.BytesIO(raw)) as decoded:
            if decoded.format != 'PNG' or decoded.mode != 'RGBA' or decoded.size != size or getattr(decoded, 'n_frames', 1) != 1:
                raise ValueError('Expected single straight RGBA Guided PNG')
            return decoded.copy()
    except (OSError, SyntaxError) as exc:
        raise ValueError('Malformed Guided PNG') from exc


def recipe(raw):
    result = parse(raw)
    # JSON comparison distinguishes bool/float substitutions in fixed integers.
    if json.dumps(result, sort_keys=True) != json.dumps(RECIPE, sort_keys=True):
        raise ValueError('Fixed Guided recipe identity/geometry/resize changed')
    return result


def generate(root, raw, candidate=False):
    selected = selection(root, raw, candidate)
    recipe(read(root, selected['recipe']['path'], 128 * 1024))
    pieces = {}
    for row, spec in zip(selected['masters'], RECIPE['pieces']):
        master = image(read(root, row['source_png']), tuple(spec['source_size']))
        piece = Image.new('RGBA', (96,112))
        piece.paste(master.crop(tuple(spec['crop'])).resize(tuple(spec['size']), Image.Resampling.LANCZOS), tuple(spec['xy']))
        pieces[spec['identity']] = piece
    pngs, blobs, rows = {}, {}, []
    for ordinal, (identity, density) in enumerate(PAIRS):
        piece = pieces[identity]
        stream = io.BytesIO()
        piece.save(stream, format='PNG', optimize=False)
        encoded = stream.getvalue()
        source = png(identity, density)
        if not candidate:
            row = selected['resources'][ordinal]
            current = read(root, source)
            if sha(current) != row['source_sha256'] or current != encoded:
                raise ValueError('Derived Guided PNG does not match masters+fixed recipe: ' + source)
        pngs[source] = encoded
        rows.append(dict(identity=identity, density=density, source_png=source, source_sha256=sha(encoded)))
        blobs[(identity, density)] = struct.pack('<4s6I', b'HDR1', identity, density, 12, 14, 0, 0) + piece.tobytes()
    return dict(selected, schema=SCHEMA, resources=rows), pngs, blobs


def input_paths(root):
    """Exactly fourteen selected and canonical paths, never historical tree globs."""
    selected = selection(root, read(root, SELECTION, 128 * 1024))
    paths = {SELECTION, selected['recipe']['path']} | generated_paths() | {r['source_png'] for r in selected['masters']} | {ROOT + '/' + name(*pair) for pair in PAIRS}
    if len(paths) != 14:
        raise ValueError('Guided input path collision')
    return paths


def payload_header(pins):
    lines = ['/* Generated Guided projectile payload-only pins. Do not edit.',
             ' * Fixed renderer eligibility, geometry, density and blend remain unchanged. */',
             '#ifndef CURRENT_GUIDED_PAYLOAD_PINS_H',
             '#define CURRENT_GUIDED_PAYLOAD_PINS_H']
    if set(pins) != set(PAIRS):
        raise ValueError('Expected four Guided payload pins')
    # Only the existing enemy 20/21 consumers have compiled payload pins.
    # Player 19/171/20/21 loader eligibility is deliberately not broadened.
    for identity, density in ENEMY_PAIRS:
        value = pins[(identity, density)]
        if not isinstance(value, str) or re.fullmatch('[0-9a-f]{16}', value) is None:
            raise ValueError('Invalid Guided payload pin')
        lines.append(f'#define CURRENT_GUIDED_{identity}_D{density}_PAYLOAD_FNV UINT64_C(0x{value})')
    return ('\n'.join(lines) + '\n#endif\n').encode()


def load(root):
    from build_current_art import fnv
    selected, _, blobs = generate(root, read(root, SELECTION, 128 * 1024))
    mapping = parse(read(root, MAPPING, 128 * 1024))
    rows, result, pins = [], {}, {}
    for (identity, density), blob in blobs.items():
        source = ROOT + '/' + name(identity, density)
        destination = 'assets/gameplay/' + name(identity, density)
        if read(root, source) != blob:
            raise ValueError('Guided HDA does not match master+fixed recipe: ' + source)
        row = dict(identity=identity, density=density, source_path=source, destination=destination, sha256=sha(blob))
        rows.append(row)
        result[destination] = row
        pins[(identity, density)] = fnv(blob[28:])
    expected = dict(schema='opentyrian-current-guided-compatibility-v1', selection=SELECTION,
                    version=selected['version'], files=rows)
    if json.dumps(mapping, sort_keys=True) != json.dumps(expected, sort_keys=True):
        raise ValueError('Invalid/stale Guided compatibility mapping')
    if read(root, HEADER) != payload_header(pins):
        raise ValueError('Stale Guided payload pins')
    return result
