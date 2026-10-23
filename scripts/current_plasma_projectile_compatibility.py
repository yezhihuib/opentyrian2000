"""Finite single-master Plasma Storm projectile inputs and six current transports.

These are projectile pieces, not the five bank9 Plasma sidekick body sources.
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

IDS = (1300022, 1300023, 1300024)
PAIRS = tuple((identity, density) for identity in IDS for density in (4, 8))
GEOMETRY = {1300022: (62, 24, 0), 1300023: (65, 28, 24), 1300024: (62, 23, 52)}
SELECTION = 'assets/hd/authoring/plasma-projectile-current.json'
MAPPING = 'packaging/current-plasma-projectile-compatibility.json'
HEADER = 'src/current_plasma_projectile_payload_pins.h'
ROOT = 'assets/hd/current-compat/plasma-projectile'
INPUT_ROOT = 'authoring-inputs/plasma-projectile-current'
SCHEMA = 'opentyrian-current-plasma-projectile-authoring-v1'
CANDIDATE_SCHEMA = 'opentyrian-current-plasma-projectile-candidate-v1'
RECIPE = {
    'schema': 'plasma-projectile-fixed-recipe-v1',
    'master_size': [1167, 1347],
    'resize_to': [520, 600],
    'resample': 'Pillow-LANCZOS-RGBA',
    'pieces': [
        {'identity': identity, 'logical_size': [width, height],
         'logical_y': y, 'anchor': [0, 0]}
        for identity, (width, height, y) in GEOMETRY.items()
    ],
    'densities': [4, 8],
    'density4': 'resize-each-density8-piece-by-half',
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def parse(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate Plasma JSON key: ' + key)
            result[key] = value
        return result

    def invalid(value):
        raise ValueError('Non-finite Plasma JSON number: ' + value)

    if len(raw) > 128 * 1024:
        raise ValueError('Oversize Plasma JSON')
    return json.loads(raw, object_pairs_hook=unique, parse_constant=invalid)


def read(root, name, limit=16 * 1024 * 1024):
    p = path(root, name)
    if not p.is_file() or not stat.S_ISREG(p.lstat().st_mode) or p.stat().st_size > limit:
        raise ValueError('Missing/oversize regular Plasma input: ' + name)
    return p.read_bytes()


def name(identity, density):
    if type(identity) is not int or type(density) is not int or (identity, density) not in PAIRS:
        raise ValueError('Unknown Plasma projectile identity/density')
    return f'option-plasma-projectile-{identity - 1300000}-{density}.hda'


def png(identity, density):
    return INPUT_ROOT + '/derived/' + name(identity, density).removesuffix('.hda') + '.png'


def generated_paths():
    return {png(identity, density) for identity, density in PAIRS}


def is_hash(value):
    return isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value) is not None


def selection(root, raw, candidate=False):
    selected = parse(raw)
    keys = {'schema', 'version', 'master', 'recipe'} | (set() if candidate else {'resources'})
    schema = CANDIDATE_SCHEMA if candidate else SCHEMA
    if not isinstance(selected, dict) or set(selected) != keys or selected['schema'] != schema:
        raise ValueError('Invalid Plasma candidate/installed schema or fields')
    if not isinstance(selected['version'], str) or not 1 <= len(selected['version']) <= 128:
        raise ValueError('Invalid Plasma version')
    for key, path_key, hash_key, suffix in (
            ('master', 'source_png', 'source_sha256', '.png'), ('recipe', 'path', 'sha256', '.json')):
        row = selected[key]
        if not isinstance(row, dict) or set(row) != {path_key, hash_key} or not is_hash(row[hash_key]):
            raise ValueError('Invalid Plasma ' + key + ' record')
        source = row[path_key]
        if (not isinstance(source, str) or not source.startswith('authoring-inputs/') or
                not source.endswith(suffix) or source.casefold().startswith(INPUT_ROOT + '/derived/') or
                source.casefold().startswith('authoring-inputs/charge-body-current/derived/')):
            raise ValueError('Expected independent Plasma ' + key + ' input')
        if sha(read(root, source)) != row[hash_key]:
            raise ValueError('Selected Plasma ' + key + ' changed')
    if not candidate:
        if not isinstance(selected['resources'], list) or len(selected['resources']) != 6:
            raise ValueError('Expected six derived Plasma pieces')
        for (identity, density), row in zip(PAIRS, selected['resources']):
            if (not isinstance(row, dict) or set(row) != {'identity', 'density', 'source_png', 'source_sha256'} or
                    type(row['identity']) is not int or type(row['density']) is not int or
                    (row['identity'], row['density']) != (identity, density) or
                    row['source_png'] != png(identity, density) or not is_hash(row['source_sha256'])):
                raise ValueError('Invalid derived Plasma identity/density/path/order/hash')
    return selected


def image(raw, size=(1167, 1347)):
    """Decode only bounded, complete, single-frame, CRC-valid straight RGBA8 PNG."""
    if len(raw) > 16 * 1024 * 1024 or raw[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('Expected bounded Plasma PNG')
    offset = 8
    kinds = []
    while offset < len(raw):
        if offset + 12 > len(raw):
            raise ValueError('Truncated Plasma PNG chunk')
        length = struct.unpack('>I', raw[offset:offset + 4])[0]
        end = offset + 12 + length
        if end > len(raw):
            raise ValueError('Truncated Plasma PNG data')
        kind = raw[offset + 4:offset + 8]
        body = raw[offset + 8:end - 4]
        if zlib.crc32(kind + body) & 0xffffffff != struct.unpack('>I', raw[end - 4:end])[0]:
            raise ValueError('Plasma PNG CRC mismatch')
        if not kinds and (kind != b'IHDR' or body != struct.pack('>IIBBBBB', *size, 8, 6, 0, 0, 0)):
            raise ValueError('Unexpected Plasma PNG dimensions/straight RGBA8 encoding')
        if (kind in (b'acTL', b'fcTL', b'fdAT') or
                (kind not in (b'IHDR', b'PLTE', b'IDAT', b'IEND') and not kind[0] & 32)):
            raise ValueError('Animated/unknown critical Plasma PNG chunk')
        kinds.append(kind)
        offset = end
        if kind == b'IEND':
            if length or offset != len(raw):
                raise ValueError('Trailing Plasma PNG data')
            break
    if kinds.count(b'IHDR') != 1 or kinds.count(b'IEND') != 1 or b'IDAT' not in kinds:
        raise ValueError('Expected complete Plasma PNG')
    try:
        with Image.open(io.BytesIO(raw)) as decoded:
            decoded.verify()
        with Image.open(io.BytesIO(raw)) as decoded:
            if decoded.format != 'PNG' or decoded.mode != 'RGBA' or decoded.size != size or getattr(decoded, 'n_frames', 1) != 1:
                raise ValueError('Expected single straight RGBA Plasma PNG')
            return decoded.copy()
    except (OSError, SyntaxError) as exc:
        raise ValueError('Malformed Plasma PNG') from exc


def recipe(raw):
    result = parse(raw)
    # JSON comparison distinguishes bool/float substitutions in fixed integers.
    if json.dumps(result, sort_keys=True) != json.dumps(RECIPE, sort_keys=True):
        raise ValueError('Fixed Plasma recipe identity/geometry/resize changed')
    return result


def generate(root, raw, candidate=False):
    selected = selection(root, raw, candidate)
    master = image(read(root, selected['master']['source_png']))
    recipe(read(root, selected['recipe']['path'], 128 * 1024))
    fitted = master.resize((520, 600), Image.Resampling.LANCZOS)
    pngs, blobs, rows = {}, {}, []
    for ordinal, (identity, density) in enumerate(PAIRS):
        width, height, y = GEOMETRY[identity]
        piece = fitted.crop((0, y * 8, width * 8, (y + height) * 8))
        if density == 4:
            piece = piece.resize((width * 4, height * 4), Image.Resampling.LANCZOS)
        stream = io.BytesIO()
        piece.save(stream, format='PNG', optimize=False)
        encoded = stream.getvalue()
        source = png(identity, density)
        if not candidate:
            row = selected['resources'][ordinal]
            current = read(root, source)
            if sha(current) != row['source_sha256'] or current != encoded:
                raise ValueError('Derived Plasma PNG does not match master+fixed recipe: ' + source)
        pngs[source] = encoded
        rows.append(dict(identity=identity, density=density, source_png=source, source_sha256=sha(encoded)))
        blobs[(identity, density)] = struct.pack('<4s6I', b'HDR1', identity, density, width, height, 0, 0) + piece.tobytes()
    return dict(selected, schema=SCHEMA, resources=rows), pngs, blobs


def input_paths(root):
    """Exactly nine selected paths; no historical/provenance/authoring tree glob."""
    selected = selection(root, read(root, SELECTION, 128 * 1024))
    paths = {SELECTION, selected['master']['source_png'], selected['recipe']['path']} | generated_paths()
    if len(paths) != 9:
        raise ValueError('Plasma input path collision')
    return paths


def payload_header(pins):
    lines = ['/* Generated Plasma projectile payload-only pins. Do not edit.',
             ' * Fixed renderer eligibility, geometry, density and blend remain unchanged. */',
             '#ifndef CURRENT_PLASMA_PROJECTILE_PAYLOAD_PINS_H',
             '#define CURRENT_PLASMA_PROJECTILE_PAYLOAD_PINS_H']
    if set(pins) != set(PAIRS):
        raise ValueError('Expected six Plasma payload pins')
    for identity, density in PAIRS:
        value = pins[(identity, density)]
        if not isinstance(value, str) or re.fullmatch('[0-9a-f]{16}', value) is None:
            raise ValueError('Invalid Plasma payload pin')
        lines.append(f'#define CURRENT_PLASMA_PROJECTILE_{identity}_D{density}_PAYLOAD_FNV UINT64_C(0x{value})')
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
            raise ValueError('Plasma HDA does not match master+fixed recipe: ' + source)
        row = dict(identity=identity, density=density, source_path=source, destination=destination, sha256=sha(blob))
        rows.append(row)
        result[destination] = row
        pins[(identity, density)] = fnv(blob[28:])
    expected = dict(schema='opentyrian-current-plasma-projectile-compatibility-v1', selection=SELECTION,
                    version=selected['version'], files=rows)
    if json.dumps(mapping, sort_keys=True) != json.dumps(expected, sort_keys=True):
        raise ValueError('Invalid/stale Plasma compatibility mapping')
    if read(root, HEADER) != payload_header(pins):
        raise ValueError('Stale Plasma payload pins')
    return result
