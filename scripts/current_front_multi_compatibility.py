"""Eight independent Front Multi sources; fixed existing role8 transports only.

No resampling, phase merging, new density, geometry or renderer eligibility.
Historical rear derivatives retain their frozen 163/164 source dependency.
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

IDS = (80121, 80122, 80163, 80164, 80201, 80202, 80279, 80280)
SELECTION = 'assets/hd/authoring/front-multi-current.json'
MAPPING = 'packaging/current-front-multi-compatibility.json'
HEADER = 'src/hd_front_multi_current.h'
ROOT = 'assets/hd/current-compat/front-multi'
INPUT_ROOT = 'authoring-inputs/front-multi-current'
SCHEMA = 'opentyrian-current-front-multi-authoring-v1'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def parse(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate Front Multi JSON key: ' + key)
            result[key] = value
        return result

    def invalid(value):
        raise ValueError('Non-finite Front Multi JSON number: ' + value)

    if len(raw) > 128 * 1024:
        raise ValueError('Oversize Front Multi JSON')
    return json.loads(raw, object_pairs_hook=unique, parse_constant=invalid)


def read(root, name, limit=16 * 1024 * 1024):
    p = path(root, name)
    if not p.is_file() or not stat.S_ISREG(p.lstat().st_mode) or p.stat().st_size > limit:
        raise ValueError('Missing/oversize regular Front Multi input: ' + name)
    return p.read_bytes()


def name(identity):
    if type(identity) is not int or identity not in IDS:
        raise ValueError('Unknown Front Multi identity')
    return f'bullet-{identity - 80000}-8.hda'


def is_hash(value):
    return isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value) is not None


def selection(root, raw):
    selected = parse(raw)
    if not isinstance(selected, dict) or set(selected) != {'schema', 'version', 'resources'} or selected['schema'] != SCHEMA:
        raise ValueError('Invalid Front Multi selection schema/fields')
    if not isinstance(selected['version'], str) or not 1 <= len(selected['version']) <= 128:
        raise ValueError('Invalid Front Multi version')
    if not isinstance(selected['resources'], list) or len(selected['resources']) != 8:
        raise ValueError('Expected eight independent Front Multi sources')
    from current_sidekick_body_compatibility import CHARGE_IDS, charge_png
    from current_plasma_projectile_compatibility import generated_paths
    generated = generated_paths() | {charge_png(identity) for identity in CHARGE_IDS}
    aliases = {name.casefold() for name in generated}
    seen, files = set(), []
    for identity, row in zip(IDS, selected['resources']):
        if (not isinstance(row, dict) or set(row) != {'identity', 'source_png', 'source_sha256'} or
                type(row['identity']) is not int or row['identity'] != identity):
            raise ValueError('Invalid Front Multi identity/fields/order')
        source = row['source_png']
        if (not isinstance(source, str) or not source.startswith('authoring-inputs/') or
                not source.endswith('.png') or not is_hash(row['source_sha256'])):
            raise ValueError('Expected independent authoring-inputs Front Multi PNG and SHA256')
        if source.casefold() in aliases or '/derived/' in source.casefold():
            raise ValueError('Generated artwork is not an independent Front Multi source')
        source_bytes = read(root, source)
        candidate = path(root, source)
        if candidate.stat().st_nlink != 1:
            raise ValueError('Hardlinked Front Multi source is not independent artwork')
        if source.casefold() in seen or any(candidate.samefile(other) for other in files):
            raise ValueError('Front Multi sources must have eight independent paths')
        # Hardlinks to generated outputs are aliases too, even under a new name.
        if any(candidate.samefile(path(root, name)) for name in generated if path(root, name).is_file()):
            raise ValueError('Generated source alias is not independent artwork')
        if sha(source_bytes) != row['source_sha256']:
            raise ValueError('Selected Front Multi source changed')
        seen.add(source.casefold())
        files.append(candidate)
    return selected


def image(raw, size=(96, 112)):
    """Decode only bounded, complete, single-frame, CRC-valid straight RGBA8 PNG."""
    if len(raw) > 16 * 1024 * 1024 or raw[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('Expected bounded Front Multi PNG')
    offset = 8
    kinds = []
    compressed = []
    while offset < len(raw):
        if offset + 12 > len(raw):
            raise ValueError('Truncated Front Multi PNG chunk')
        length = struct.unpack('>I', raw[offset:offset + 4])[0]
        end = offset + 12 + length
        if end > len(raw):
            raise ValueError('Truncated Front Multi PNG data')
        kind = raw[offset + 4:offset + 8]
        body = raw[offset + 8:end - 4]
        if not all(65 <= byte <= 90 or 97 <= byte <= 122 for byte in kind) or kind[2] & 32:
            raise ValueError('Invalid Front Multi PNG chunk type/reserved bit')
        if zlib.crc32(kind + body) & 0xffffffff != struct.unpack('>I', raw[end - 4:end])[0]:
            raise ValueError('Front Multi PNG CRC mismatch')
        if not kinds and (kind != b'IHDR' or body != struct.pack('>IIBBBBB', *size, 8, 6, 0, 0, 0)):
            raise ValueError('Unexpected Front Multi PNG dimensions/straight RGBA8 encoding')
        # Deliberately bounded normalized PNG dialect: no executable or opaque
        # metadata streams. Optional palette and physical-density metadata are
        # validated explicitly, rather than relying on Pillow's permissiveness.
        if kind not in (b'IHDR', b'PLTE', b'pHYs', b'IDAT', b'IEND'):
            raise ValueError('Unsupported Front Multi PNG chunk')
        if kind == b'PLTE' and (b'PLTE' in kinds or b'IDAT' in kinds or not 3 <= length <= 768 or length % 3):
            raise ValueError('Invalid Front Multi PNG palette/order')
        if kind == b'pHYs' and (b'pHYs' in kinds or b'IDAT' in kinds or length != 9 or body[-1] not in (0, 1)):
            raise ValueError('Invalid Front Multi PNG physical-density metadata/order')
        if kind == b'IDAT':
            if b'IDAT' in kinds and kinds[-1] != b'IDAT':
                raise ValueError('Noncontiguous Front Multi PNG data chunks')
            compressed.append(body)
        kinds.append(kind)
        offset = end
        if kind == b'IEND':
            if length or offset != len(raw):
                raise ValueError('Trailing Front Multi PNG data')
            break
    if kinds.count(b'IHDR') != 1 or kinds.count(b'IEND') != 1 or b'IDAT' not in kinds:
        raise ValueError('Expected complete Front Multi PNG')
    # Decode only one exact-sized zlib stream, without accepting compressed
    # suffixes, extra scanlines or a decompression bomb before Pillow opens it.
    expected = size[1] * (1 + size[0] * 4)
    try:
        stream = zlib.decompressobj()
        scanlines = stream.decompress(b''.join(compressed), expected + 1)
        if (not stream.eof or stream.unused_data or stream.unconsumed_tail or len(scanlines) != expected or
                any(scanlines[row * (1 + size[0] * 4)] > 4 for row in range(size[1]))):
            raise ValueError('Invalid Front Multi PNG compressed stream/scanlines')
    except zlib.error as exc:
        raise ValueError('Malformed Front Multi PNG compressed stream') from exc
    try:
        with Image.open(io.BytesIO(raw)) as decoded:
            decoded.verify()
        with Image.open(io.BytesIO(raw)) as decoded:
            if decoded.format != 'PNG' or decoded.mode != 'RGBA' or decoded.size != size or getattr(decoded, 'n_frames', 1) != 1:
                raise ValueError('Expected single straight RGBA Front Multi PNG')
            return decoded.copy()
    except (OSError, SyntaxError) as exc:
        raise ValueError('Malformed Front Multi PNG') from exc


def generate(root, raw):
    selected = selection(root, raw)
    blobs = {}
    for row in selected['resources']:
        pixels = image(read(root, row['source_png'])).tobytes()
        blobs[row['identity']] = struct.pack('<4s6I', b'HDR1', row['identity'], 8, 12, 14, 0, 0) + pixels
    return selected, blobs


def input_paths(root):
    """Exactly nine selected paths, never an artwork/provenance tree glob."""
    selected = selection(root, read(root, SELECTION, 128 * 1024))
    paths = {SELECTION} | {row['source_png'] for row in selected['resources']}
    if len(paths) != 9:
        raise ValueError('Front Multi input path collision')
    return paths


def payload_header(pins):
    lines = ['/* Generated Front Multi payload-only pins. Do not edit.',
             ' * Existing shadow eligibility, geometry and density remain unchanged. */',
             '#ifndef HD_FRONT_MULTI_CURRENT_H', '#define HD_FRONT_MULTI_CURRENT_H']
    if set(pins) != set(IDS):
        raise ValueError('Expected eight Front Multi payload pins')
    for identity in IDS:
        value = pins[identity]
        if not isinstance(value, str) or re.fullmatch('[0-9a-f]{16}', value) is None:
            raise ValueError('Invalid Front Multi payload pin')
        lines.append(f'#define HD_FRONT_MULTI_CURRENT_PAYLOAD_{identity}_HASH UINT64_C(0x{value})')
    return ('\n'.join(lines) + '\n#endif\n').encode()


def load(root):
    from build_current_art import fnv
    selected, blobs = generate(root, read(root, SELECTION, 128 * 1024))
    mapping = parse(read(root, MAPPING, 128 * 1024))
    rows, result, pins = [], {}, {}
    for identity, blob in blobs.items():
        source = ROOT + '/' + name(identity)
        destination = 'assets/gameplay/' + name(identity)
        if read(root, source) != blob:
            raise ValueError('Front Multi HDA does not match selected PNG: ' + source)
        row = dict(identity=identity, source_path=source, destination=destination, sha256=sha(blob))
        rows.append(row)
        result[destination] = row
        pins[identity] = fnv(blob[28:])
    expected = dict(schema='opentyrian-current-front-multi-compatibility-v1', selection=SELECTION,
                    version=selected['version'], files=rows)
    if json.dumps(mapping, sort_keys=True) != json.dumps(expected, sort_keys=True):
        raise ValueError('Invalid/stale Front Multi compatibility mapping')
    if read(root, HEADER) != payload_header(pins):
        raise ValueError('Stale Front Multi payload pins')
    return result
