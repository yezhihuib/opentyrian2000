"""Fixed NEWSH2 base267 compatibility; no new runtime eligibility or payload pin."""
import hashlib
import json
import re
import stat
import struct
import zlib
from pathlib import Path

from package_runtime import relative_path

IDENTITY = 1010267
NAME = 'enemy-newsh2-267-8.hda'
SELECTION = 'assets/hd/authoring/craft267-current.json'
MAPPING = 'packaging/current-craft267-compatibility.json'
CANONICAL = 'assets/hd/current-compat/craft267/' + NAME
DESTINATION = 'assets/gameplay/' + NAME
HEADER = b'HDR1' + struct.pack('<6I', IDENTITY, 8, 24, 28, 6, 7)
SIZE = 28 + 192 * 224 * 4


def sha(data):
    return hashlib.sha256(data).hexdigest()


def path(root, name):
    result = root / relative_path(name)
    # Python 3.11 is_symlink does not reject every Windows junction/reparse point.
    ancestors = [root, *root.parents]
    cursor = root
    for part in result.relative_to(root).parts:
        cursor = cursor / part
        ancestors.append(cursor)
    for q in ancestors:
        try:
            info = q.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT:
            raise ValueError('Symlink/reparse-point input is not accepted: ' + str(q))
    return result


def read(root, name):
    p = path(root, name)
    if not p.is_file() or not stat.S_ISREG(p.lstat().st_mode):
        raise ValueError('Missing regular input: ' + name)
    return p.read_bytes()


def parse(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate JSON key: ' + key)
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=unique)


def selection(root, raw):
    j = parse(raw)
    if not isinstance(j, dict) or set(j) != {'schema', 'version', 'resources'} or j['schema'] != 'opentyrian-current-craft267-authoring-v1':
        raise ValueError('Invalid craft267 selection schema/fields')
    if not isinstance(j['version'], str) or not 1 <= len(j['version']) <= 128:
        raise ValueError('Invalid craft267 version')
    if not isinstance(j['resources'], list) or len(j['resources']) != 1:
        raise ValueError('Expected exactly one craft267 source')
    row = j['resources'][0]
    if not isinstance(row, dict) or set(row) != {'identity', 'source_png', 'source_sha256'} or type(row['identity']) is not int or row['identity'] != IDENTITY:
        raise ValueError('Only NEWSH2 base267 / HDA1010267 is authorized')
    if not isinstance(row['source_png'], str) or not row['source_png'].endswith('.png') or row['source_png'].startswith('assets/hd/current-compat/'):
        raise ValueError('Expected an independent source PNG')
    if not isinstance(row['source_sha256'], str) or not re.fullmatch('[0-9a-f]{64}', row['source_sha256']):
        raise ValueError('Invalid source SHA256')
    if sha(read(root, row['source_png'])) != row['source_sha256']:
        raise ValueError('Selected craft267 source changed')
    return j


def source_blob(root, row):
    from PIL import Image
    import io
    if type(row['identity']) is not int or row['identity'] != IDENTITY:
        raise ValueError('Unknown craft267 identity')
    raw = read(root, row['source_png'])
    if len(raw) > 16 * 1024 * 1024 or raw[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('Expected bounded PNG')
    # Pillow accepts trailing data and some non-RGBA8 encodings. Reject both.
    offset = 8
    kinds = []
    while offset < len(raw):
        if offset + 12 > len(raw):
            raise ValueError('Truncated PNG chunk')
        length = struct.unpack('>I', raw[offset:offset+4])[0]
        end = offset + 12 + length
        if end > len(raw):
            raise ValueError('Truncated PNG data')
        kind = raw[offset+4:offset+8]
        body = raw[offset+8:end-4]
        if zlib.crc32(kind + body) & 0xffffffff != struct.unpack('>I', raw[end-4:end])[0]:
            raise ValueError('Invalid PNG CRC')
        if not kinds and (kind != b'IHDR' or body[:10] != struct.pack('>II', 192, 224) + b'\x08\x06'):
            raise ValueError('Expected 192x224 straight RGBA8 PNG')
        kinds.append(kind)
        offset = end
        if kind == b'IEND':
            if length or offset != len(raw):
                raise ValueError('Trailing PNG data')
            break
    if kinds.count(b'IHDR') != 1 or kinds.count(b'IEND') != 1 or b'acTL' in kinds:
        raise ValueError('Expected one complete nonanimated PNG')
    with Image.open(io.BytesIO(raw)) as im:
        im.verify()
    with Image.open(io.BytesIO(raw)) as im:
        if im.format != 'PNG' or im.mode != 'RGBA' or im.size != (192, 224) or getattr(im, 'n_frames', 1) != 1:
            raise ValueError('Expected single 192x224 straight RGBA8 PNG')
        return HEADER + im.tobytes()


def load(root):
    j = parse(read(root, MAPPING))
    if not isinstance(j, dict) or set(j) != {'schema', 'selection', 'version', 'files'} or j['schema'] != 'opentyrian-current-craft267-compatibility-v1' or j['selection'] != SELECTION:
        raise ValueError('Invalid craft267 mapping authority')
    if not isinstance(j['version'], str) or not 1 <= len(j['version']) <= 128:
        raise ValueError('Invalid craft267 mapping version')
    if not isinstance(j['files'], list) or len(j['files']) != 1:
        raise ValueError('Expected exactly one craft267 consumer')
    row = j['files'][0]
    if not isinstance(row, dict) or set(row) != {'identity', 'source_path', 'destination', 'sha256'} or type(row['identity']) is not int or row['identity'] != IDENTITY or row['source_path'] != CANONICAL or row['destination'] != DESTINATION:
        raise ValueError('Invalid craft267 consumer/identity')
    raw = read(root, CANONICAL)
    if len(raw) != SIZE or raw[:28] != HEADER or sha(raw) != row['sha256']:
        raise ValueError('Stale/malformed craft267 canonical HDA')
    return {DESTINATION: row}
