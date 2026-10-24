"""Finite three-master regular Missile input and three shared current transports.

Identities 80031/80032/80033 are shared by existing player, sidekick and shadow consumers.
Identity, geometry, density, split, and resize are fixed; no executable recipe.
"""
import hashlib
import base64
import io
import os
import subprocess
import tempfile
from pathlib import Path
import json
import re
import stat
import struct
import zlib

from PIL import Image
from current_craft267_compatibility import path

IDS = (80031, 80032, 80033)
SELECTORS = (31, 32, 33)
SHADOW_PAIRS = tuple((identity, 8) for identity in IDS)
PAIRS = tuple((identity, 8) for identity in IDS)
SELECTION = 'assets/hd/authoring/missile-current.json'
MAPPING = 'packaging/current-missile-compatibility.json'
HEADER = 'src/current_missile_payload_pins.h'
ROOT = 'assets/hd/current-compat/missile'
INPUT_ROOT = 'authoring-inputs/missile-current'
SCHEMA = 'opentyrian-current-missile-authoring-v1'
CANDIDATE_SCHEMA = 'opentyrian-current-missile-candidate-v1'
RECIPE = {'schema': 'missile-fixed-recipe-v1', 'canvas': [96, 112], 'logical_size': [12, 14], 'density': 8, 'anchor': [0, 0], 'resample': 'ImageMagick-7.1.1-43-Q16-Lanczos-straight-RGBA-composite', 'pieces': [{'selector': 31, 'source_size': [1160, 1355], 'crop': [417, 114, 744, 1199], 'size': [56, 104], 'xy': [24, 8], 'identity': 80031}, {'selector': 32, 'source_size': [1006, 1564], 'crop': [210, 72, 797, 1370], 'size': [72, 112], 'xy': [16, 0], 'identity': 80032}, {'selector': 33, 'source_size': [1006, 1564], 'crop': [91, 17, 876, 1517], 'size': [72, 112], 'xy': [8, 0], 'identity': 80033}], 'alpha': 'preserve-including-hidden-RGB-no-threshold', 'relationship': 'three-independent-static-upgrade-designs-not-animation'}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def parse(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate Missile JSON key: ' + key)
            result[key] = value
        return result

    def invalid(value):
        raise ValueError('Non-finite Missile JSON number: ' + value)

    if len(raw) > 128 * 1024:
        raise ValueError('Oversize Missile JSON')
    return json.loads(raw, object_pairs_hook=unique, parse_constant=invalid)


def read(root, name, limit=16 * 1024 * 1024):
    p = path(root, name)
    if not p.is_file() or not stat.S_ISREG(p.lstat().st_mode) or p.stat().st_size > limit:
        raise ValueError('Missing/oversize regular Missile input: ' + name)
    return p.read_bytes()


def name(identity, density):
    if type(identity) is not int or type(density) is not int or (identity, density) not in PAIRS:
        raise ValueError('Unknown Missile projectile identity/density')
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
        raise ValueError('Invalid Missile candidate/installed schema or fields')
    if not isinstance(selected['version'], str) or not 1 <= len(selected['version']) <= 128:
        raise ValueError('Invalid Missile version')
    if not isinstance(selected['masters'], list) or len(selected['masters']) != 3:
        raise ValueError('Expected three Missile masters')
    for selector, row in zip(SELECTORS, selected['masters']):
        if (not isinstance(row, dict) or set(row) != {'selector','source_png','source_sha256'} or
                type(row['selector']) is not int or row['selector'] != selector or
                row['source_png'] != INPUT_ROOT + f'/master-{selector}.png' or not is_hash(row['source_sha256'])):
            raise ValueError('Invalid Missile master identity/path/hash/order')
        if sha(read(root, row['source_png'])) != row['source_sha256']:
            raise ValueError('Selected Missile master changed')
    row = selected['recipe']
    if (not isinstance(row, dict) or set(row) != {'path','sha256'} or
            row['path'] != INPUT_ROOT + '/recipe.json' or not is_hash(row['sha256']) or
            sha(read(root, row['path'])) != row['sha256']):
        raise ValueError('Invalid/changed Missile recipe record')
    if not candidate:
        if not isinstance(selected['resources'], list) or len(selected['resources']) != 3:
            raise ValueError('Expected three derived Missile pieces')
        for (identity, density), row in zip(PAIRS, selected['resources']):
            if (not isinstance(row, dict) or set(row) != {'identity', 'density', 'source_png', 'source_sha256'} or
                    type(row['identity']) is not int or type(row['density']) is not int or
                    (row['identity'], row['density']) != (identity, density) or
                    row['source_png'] != png(identity, density) or not is_hash(row['source_sha256'])):
                raise ValueError('Invalid derived Missile identity/density/path/order/hash')
    return selected


def image(raw, size):
    """Decode only bounded, complete, single-frame, CRC-valid straight RGBA8 PNG."""
    if len(raw) > 16 * 1024 * 1024 or raw[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('Expected bounded Missile PNG')
    offset = 8
    kinds = []
    while offset < len(raw):
        if offset + 12 > len(raw):
            raise ValueError('Truncated Missile PNG chunk')
        length = struct.unpack('>I', raw[offset:offset + 4])[0]
        end = offset + 12 + length
        if end > len(raw):
            raise ValueError('Truncated Missile PNG data')
        kind = raw[offset + 4:offset + 8]
        body = raw[offset + 8:end - 4]
        if zlib.crc32(kind + body) & 0xffffffff != struct.unpack('>I', raw[end - 4:end])[0]:
            raise ValueError('Missile PNG CRC mismatch')
        if not kinds and (kind != b'IHDR' or body != struct.pack('>IIBBBBB', *size, 8, 6, 0, 0, 0)):
            raise ValueError('Unexpected Missile PNG dimensions/straight RGBA8 encoding')
        if (kind in (b'acTL', b'fcTL', b'fdAT') or
                (kind not in (b'IHDR', b'PLTE', b'IDAT', b'IEND') and not kind[0] & 32)):
            raise ValueError('Animated/unknown critical Missile PNG chunk')
        kinds.append(kind)
        offset = end
        if kind == b'IEND':
            if length or offset != len(raw):
                raise ValueError('Trailing Missile PNG data')
            break
    if kinds.count(b'IHDR') != 1 or kinds.count(b'IEND') != 1 or b'IDAT' not in kinds:
        raise ValueError('Expected complete Missile PNG')
    try:
        with Image.open(io.BytesIO(raw)) as decoded:
            decoded.verify()
        with Image.open(io.BytesIO(raw)) as decoded:
            if decoded.format != 'PNG' or decoded.mode != 'RGBA' or decoded.size != size or getattr(decoded, 'n_frames', 1) != 1:
                raise ValueError('Expected single straight RGBA Missile PNG')
            return decoded.copy()
    except (OSError, SyntaxError) as exc:
        raise ValueError('Malformed Missile PNG') from exc


def recipe(raw):
    result = parse(raw)
    # JSON comparison distinguishes bool/float substitutions in fixed integers.
    if json.dumps(result, sort_keys=True) != json.dumps(RECIPE, sort_keys=True):
        raise ValueError('Fixed Missile recipe identity/geometry/resize changed')
    return result


# Executable selection is not a user-supplied recipe field. A precise tool profile
# is mandatory; missing/incompatible tools fail closed, never approximate pixels.
MAGICK = '/usr/bin/magick'
MAGICK_VERSION = 'Version: ImageMagick 7.1.1-43 Q16 x86_64 22550 https://imagemagick.org'


def tool_environment():
    # Do not inherit ImageMagick configuration, delegate or profile overrides.
    return {'PATH': '/usr/bin:/bin', 'LANG': 'C', 'LC_ALL': 'C',
            'MAGICK_THREAD_LIMIT': '1', 'MAGICK_MEMORY_LIMIT': '128MiB',
            'MAGICK_MAP_LIMIT': '128MiB', 'MAGICK_DISK_LIMIT': '128MiB',
            'MAGICK_TIME_LIMIT': '20', 'MAGICK_WIDTH_LIMIT': '4096',
            'MAGICK_HEIGHT_LIMIT': '4096', 'MAGICK_LIST_LENGTH_LIMIT': '4'}


def run_magick(argv, data=None):
    # Fixed argument vectors only; input PNG travels over stdin, not a filename
    # interpreted as a command, URL or image specification. Capture to files
    # rather than an unbounded in-memory PIPE; enforce the result-size limit
    # after completion. This is not a live disk-output cap.
    try:
        with tempfile.TemporaryDirectory(prefix='missile-magick-') as tmp:
            with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
                env = tool_environment()
                env['MAGICK_TEMPORARY_PATH'] = tmp
                result = subprocess.run([MAGICK, *argv], input=data, stdout=out,
                    stderr=err, cwd=tmp, env=env, timeout=30, check=False)
                if out.tell() > 128 * 1024 or err.tell() > 128 * 1024:
                    raise ValueError('Oversize Missile ImageMagick output')
                out.seek(0); raw = out.read()
                if result.returncode:
                    raise ValueError('Missile ImageMagick conversion failed')
                return raw
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValueError('Required Missile ImageMagick tool unavailable or timed out') from exc


def check_tool():
    raw = run_magick(['-version'])
    lines = raw.decode('ascii', errors='strict').splitlines()
    if not lines or lines[0] != MAGICK_VERSION:
        raise ValueError('Required exact Missile ImageMagick 7.1.1-43 Q16 profile missing')
    # Fixed synthetic profile covers Lanczos, source-over alpha and hidden RGB.
    # Version text alone is not a cross-platform byte-equivalence guarantee.
    raw = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAUAAAAHCAYAAADAp4fuAAAAbUlEQVR4nGNkYGBgULUOZlS1Dq6D0Yw71ef/h3LgEiw71ef/v6f+6f9O9fmMqurBTarqn+oYtUvvNiBpZYSrVFWf33RPPbjunvWn//fU5zMyzD0szXjoX179c8uDDTwlIv8M16f/Zwx7tQvDdgCP7jNTZoPckAAAAABJRU5ErkJggg==')
    encoded, rgba = transform(raw, {'source_size': [5,7], 'crop': [0,0,5,7], 'size': [9,13], 'xy': [3,4]})
    if sha(encoded) != '73061c7fac06bbceba618ebe37b04c2abc18f38000af2bb8f4b2bc8343738014' or sha(rgba) != '6984c4c392a3109ed7c42c2e60a7b24ef7676669b1439f11185e0f27db1f4905':
        raise ValueError('Missile ImageMagick fixed golden profile mismatch')


def transform(raw, spec):
    image(raw, tuple(spec['source_size']))  # strict bounded PNG before native decoder
    x0, y0, x1, y1 = spec['crop']
    width, height = spec['size']; x, y = spec['xy']
    encoded = run_magick(['-size', '96x112', 'xc:none', '(', 'PNG:-',
        '-crop', f'{x1-x0}x{y1-y0}+{x0}+{y0}', '+repage', '-filter', 'Lanczos',
        '-resize', f'{width}x{height}!', ')', '-geometry', f'+{x}+{y}',
        '-composite', '-strip', 'PNG32:-'], raw)
    piece = image(encoded, (96,112))
    return encoded, piece.tobytes()


def generate(root, raw, candidate=False):
    selected = selection(root, raw, candidate)
    recipe(read(root, selected['recipe']['path'], 128 * 1024))
    check_tool()
    pngs, blobs, rows = {}, {}, []
    for ordinal, (row, spec) in enumerate(zip(selected['masters'], RECIPE['pieces'])):
        encoded, rgba = transform(read(root, row['source_png']), spec)
        identity, density = spec['identity'], 8
        source = png(identity, density)
        if not candidate:
            resource = selected['resources'][ordinal]
            current = read(root, source)
            if sha(current) != resource['source_sha256'] or current != encoded:
                raise ValueError('Derived Missile PNG does not match masters+fixed recipe: ' + source)
        pngs[source] = encoded
        rows.append(dict(identity=identity, density=density, source_png=source, source_sha256=sha(encoded)))
        blobs[(identity, density)] = struct.pack('<4s6I', b'HDR1', identity, density, 12, 14, 0, 0) + rgba
    return dict(selected, schema=SCHEMA, resources=rows), pngs, blobs


def input_paths(root):
    """Exactly eleven selected and canonical paths, never historical tree globs."""
    selected = selection(root, read(root, SELECTION, 128 * 1024))
    paths = {SELECTION, selected['recipe']['path']} | generated_paths() | {r['source_png'] for r in selected['masters']} | {ROOT + '/' + name(*pair) for pair in PAIRS}
    if len(paths) != 11:
        raise ValueError('Missile input path collision')
    return paths


def payload_header(pins):
    lines = ['/* Generated Missile projectile payload-only pins. Do not edit.',
             ' * Fixed renderer eligibility, geometry, density and blend remain unchanged. */',
             '#ifndef CURRENT_MISSILE_PAYLOAD_PINS_H',
             '#define CURRENT_MISSILE_PAYLOAD_PINS_H']
    if set(pins) != set(PAIRS):
        raise ValueError('Expected three Missile payload pins')
    # Only the existing player/sidekick shadow consumer has this payload pin.
    # Original source pins, slot, density and eligibility remain unchanged.
    for identity, density in SHADOW_PAIRS:
        value = pins[(identity, density)]
        if not isinstance(value, str) or re.fullmatch('[0-9a-f]{16}', value) is None:
            raise ValueError('Invalid Missile payload pin')
        lines.append(f'#define CURRENT_MISSILE_{identity}_D{density}_PAYLOAD_FNV UINT64_C(0x{value})')
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
            raise ValueError('Missile HDA does not match master+fixed recipe: ' + source)
        row = dict(identity=identity, density=density, source_path=source, destination=destination, sha256=sha(blob))
        rows.append(row)
        result[destination] = row
        pins[(identity, density)] = fnv(blob[28:])
    expected = dict(schema='opentyrian-current-missile-compatibility-v1', selection=SELECTION,
                    version=selected['version'], files=rows)
    if json.dumps(mapping, sort_keys=True) != json.dumps(expected, sort_keys=True):
        raise ValueError('Invalid/stale Missile compatibility mapping')
    if read(root, HEADER) != payload_header(pins):
        raise ValueError('Stale Missile payload pins')
    return result
