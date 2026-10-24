"""Finite single-master Protron input and four current transports.

Player 225/226/244 and private enemy 227 share three independent raw cells.
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

IDS = (80225, 80244, 80226, 1470227)
PAIRS = tuple((identity, 8) for identity in IDS)
SELECTION = 'assets/hd/authoring/protron-current.json'
MAPPING = 'packaging/current-protron-compatibility.json'
HEADER = 'src/current_protron_payload_pins.h'
ROOT = 'assets/hd/current-compat/protron'
INPUT_ROOT = 'authoring-inputs/protron-current'
SCHEMA = 'opentyrian-current-protron-authoring-v1'
CANDIDATE_SCHEMA = 'opentyrian-current-protron-candidate-v1'
MASK_ROOT = 'assets/hd/artwork/player-protron-three-v1/masks'
MASKS = {
    80225: (MASK_ROOT + '/mask-bank8-225.png', '4c72ae0d6f230521b2db5e4fd558b4949cd0f62d40c390b22fa6dd5baa24b5c4'),
    80244: (MASK_ROOT + '/mask-bank8-244.png', 'f3d7ab1e51003b4325fbd9608f268bae604d9b06a070e6ebf9b64fb04daf14a5'),
    80226: (MASK_ROOT + '/mask-bank8-226.png', '3e1ed2ab41c36e5c1151c4880eff5d179d8b3fdee72138f0c7fd4a690adacc0f'),
}
RECIPE = {
    'schema': 'protron-fixed-recipe-v1', 'master_size': [2011, 782],
    'cells': {'225': [187,272,458,544], '244': [651,38,1373,762], '226': [1498,234,1839,569]},
    'canvas': [96,112], 'logical_size': [12,14], 'density': 8, 'anchor': [0,0],
    'resample': 'Pillow-LANCZOS-straight-RGBA-alpha-composite',
    'pieces': [
        {'identity':80225, 'cell':'225', 'size':[32,32], 'xy':[32,40], 'alpha':'frozen-source-support'},
        {'identity':80244, 'cell':'244', 'size':[88,88], 'xy':[0,8], 'alpha':'frozen-source-support'},
        {'identity':80226, 'cell':'226', 'size':[40,40], 'xy':[24,32], 'alpha':'frozen-source-support'},
        {'identity':1470227, 'cell':'244', 'size':[56,56], 'xy':[16,24], 'alpha':'preserve-no-mask'},
    ],
    'mask_policy': 'NEAREST-support; gaussian_filter(float-support,2); clip((blur-.5)/.35,0,1); minimum(alpha,round(soft*255))*support',
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def parse(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate Protron JSON key: ' + key)
            result[key] = value
        return result

    def invalid(value):
        raise ValueError('Non-finite Protron JSON number: ' + value)

    if len(raw) > 128 * 1024:
        raise ValueError('Oversize Protron JSON')
    return json.loads(raw, object_pairs_hook=unique, parse_constant=invalid)


def read(root, name, limit=16 * 1024 * 1024):
    p = path(root, name)
    if not p.is_file() or not stat.S_ISREG(p.lstat().st_mode) or p.stat().st_size > limit:
        raise ValueError('Missing/oversize regular Protron input: ' + name)
    return p.read_bytes()


def name(identity, density):
    if type(identity) is not int or type(density) is not int or (identity, density) not in PAIRS:
        raise ValueError('Unknown Protron projectile identity/density')
    return 'enemy-protron-p09-227-8.hda' if identity == 1470227 else f'bullet-{identity - 80000}-8.hda'


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
        raise ValueError('Invalid Protron candidate/installed schema or fields')
    if not isinstance(selected['version'], str) or not 1 <= len(selected['version']) <= 128:
        raise ValueError('Invalid Protron version')
    for key, path_key, hash_key, suffix in (
            ('master', 'source_png', 'source_sha256', '.png'), ('recipe', 'path', 'sha256', '.json')):
        row = selected[key]
        if not isinstance(row, dict) or set(row) != {path_key, hash_key} or not is_hash(row[hash_key]):
            raise ValueError('Invalid Protron ' + key + ' record')
        source = row[path_key]
        if source != INPUT_ROOT + ('/master.png' if key == 'master' else '/recipe.json'):
            raise ValueError('Expected the single current Protron ' + key + ' path')
        if sha(read(root, source)) != row[hash_key]:
            raise ValueError('Selected Protron ' + key + ' changed')
    if not candidate:
        if not isinstance(selected['resources'], list) or len(selected['resources']) != 4:
            raise ValueError('Expected four derived Protron pieces')
        for (identity, density), row in zip(PAIRS, selected['resources']):
            if (not isinstance(row, dict) or set(row) != {'identity', 'density', 'source_png', 'source_sha256'} or
                    type(row['identity']) is not int or type(row['density']) is not int or
                    (row['identity'], row['density']) != (identity, density) or
                    row['source_png'] != png(identity, density) or not is_hash(row['source_sha256'])):
                raise ValueError('Invalid derived Protron identity/density/path/order/hash')
    return selected


def image(raw, size=(2011, 782)):
    """Decode only bounded, complete, single-frame, CRC-valid straight RGBA8 PNG."""
    if len(raw) > 16 * 1024 * 1024 or raw[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('Expected bounded Protron PNG')
    offset = 8
    kinds = []
    while offset < len(raw):
        if offset + 12 > len(raw):
            raise ValueError('Truncated Protron PNG chunk')
        length = struct.unpack('>I', raw[offset:offset + 4])[0]
        end = offset + 12 + length
        if end > len(raw):
            raise ValueError('Truncated Protron PNG data')
        kind = raw[offset + 4:offset + 8]
        body = raw[offset + 8:end - 4]
        if zlib.crc32(kind + body) & 0xffffffff != struct.unpack('>I', raw[end - 4:end])[0]:
            raise ValueError('Protron PNG CRC mismatch')
        if not kinds and (kind != b'IHDR' or body != struct.pack('>IIBBBBB', *size, 8, 6, 0, 0, 0)):
            raise ValueError('Unexpected Protron PNG dimensions/straight RGBA8 encoding')
        if (kind in (b'acTL', b'fcTL', b'fdAT') or
                (kind not in (b'IHDR', b'PLTE', b'IDAT', b'IEND') and not kind[0] & 32)):
            raise ValueError('Animated/unknown critical Protron PNG chunk')
        kinds.append(kind)
        offset = end
        if kind == b'IEND':
            if length or offset != len(raw):
                raise ValueError('Trailing Protron PNG data')
            break
    if kinds.count(b'IHDR') != 1 or kinds.count(b'IEND') != 1 or b'IDAT' not in kinds:
        raise ValueError('Expected complete Protron PNG')
    try:
        with Image.open(io.BytesIO(raw)) as decoded:
            decoded.verify()
        with Image.open(io.BytesIO(raw)) as decoded:
            if decoded.format != 'PNG' or decoded.mode != 'RGBA' or decoded.size != size or getattr(decoded, 'n_frames', 1) != 1:
                raise ValueError('Expected single straight RGBA Protron PNG')
            return decoded.copy()
    except (OSError, SyntaxError) as exc:
        raise ValueError('Malformed Protron PNG') from exc


def recipe(raw):
    result = parse(raw)
    # JSON comparison distinguishes bool/float substitutions in fixed integers.
    if json.dumps(result, sort_keys=True) != json.dumps(RECIPE, sort_keys=True):
        raise ValueError('Fixed Protron recipe identity/geometry/resize changed')
    return result


def generate(root, raw, candidate=False):
    selected = selection(root, raw, candidate)
    master = image(read(root, selected['master']['source_png']))
    recipe(read(root, selected['recipe']['path'], 128 * 1024))
    import numpy as np
    from scipy.ndimage import gaussian_filter
    pngs, blobs, rows = {}, {}, []
    for ordinal, (identity, density) in enumerate(PAIRS):
        spec = RECIPE['pieces'][ordinal]
        piece = Image.new('RGBA', (96,112))
        piece.alpha_composite(master.crop(RECIPE['cells'][spec['cell']]).resize(tuple(spec['size']), Image.Resampling.LANCZOS), tuple(spec['xy']))
        if identity in MASKS:
            mask_path, mask_sha = MASKS[identity]
            raw_mask = read(root, mask_path)
            if sha(raw_mask) != mask_sha:
                raise ValueError('Frozen Protron support mask changed')
            with Image.open(io.BytesIO(raw_mask)) as decoded:
                support = np.array(decoded.resize((96,112), Image.Resampling.NEAREST)) > 0
            a = np.array(piece)
            soft = np.clip((gaussian_filter(support.astype(float), 2)-.5)/.35, 0, 1)
            a[:,:,3] = np.minimum(a[:,:,3], np.round(soft*255))*support
            piece = Image.fromarray(a)
        stream = io.BytesIO()
        piece.save(stream, format='PNG', optimize=False)
        encoded = stream.getvalue()
        source = png(identity, density)
        if not candidate:
            row = selected['resources'][ordinal]
            current = read(root, source)
            if sha(current) != row['source_sha256'] or current != encoded:
                raise ValueError('Derived Protron PNG does not match master+fixed recipe: ' + source)
        pngs[source] = encoded
        rows.append(dict(identity=identity, density=density, source_png=source, source_sha256=sha(encoded)))
        blobs[(identity, density)] = struct.pack('<4s6I', b'HDR1', identity, density, 12, 14, 0, 0) + piece.tobytes()
    return dict(selected, schema=SCHEMA, resources=rows), pngs, blobs


def input_paths(root):
    """Exactly ten selected paths; no historical/provenance/authoring tree glob."""
    selected = selection(root, read(root, SELECTION, 128 * 1024))
    paths = {SELECTION, selected['master']['source_png'], selected['recipe']['path']} | generated_paths() | {row[0] for row in MASKS.values()}
    if len(paths) != 10:
        raise ValueError('Protron input path collision')
    return paths


def payload_header(pins):
    lines = ['/* Generated Protron projectile payload-only pins. Do not edit.',
             ' * Fixed renderer eligibility, geometry, density and blend remain unchanged. */',
             '#ifndef CURRENT_PROTRON_PAYLOAD_PINS_H',
             '#define CURRENT_PROTRON_PAYLOAD_PINS_H']
    if set(pins) != set(PAIRS):
        raise ValueError('Expected four Protron payload pins')
    for identity, density in PAIRS:
        value = pins[(identity, density)]
        if not isinstance(value, str) or re.fullmatch('[0-9a-f]{16}', value) is None:
            raise ValueError('Invalid Protron payload pin')
        lines.append(f'#define CURRENT_PROTRON_{identity}_D{density}_PAYLOAD_FNV UINT64_C(0x{value})')
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
            raise ValueError('Protron HDA does not match master+fixed recipe: ' + source)
        row = dict(identity=identity, density=density, source_path=source, destination=destination, sha256=sha(blob))
        rows.append(row)
        result[destination] = row
        pins[(identity, density)] = fnv(blob[28:])
    expected = dict(schema='opentyrian-current-protron-compatibility-v1', selection=SELECTION,
                    version=selected['version'], files=rows)
    if json.dumps(mapping, sort_keys=True) != json.dumps(expected, sort_keys=True):
        raise ValueError('Invalid/stale Protron compatibility mapping')
    if read(root, HEADER) != payload_header(pins):
        raise ValueError('Stale Protron payload pins')
    return result
