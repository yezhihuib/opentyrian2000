"""Exact private terrain24 resources, with no original-data download or bundling.

This finite lane retains original-derived silhouettes/colors. Its 1008 runtime
mask bytes are reconstructible geometry, not merely hashes. It is not a public
redistribution clearance or a complete old-runtime qualification.
"""
import copy
import re
import struct
from pathlib import Path

import current_tank194_body_registration as checked

MODE = 'current-shapesz-terrain24-v1'
PROOF = 'packaging/terrain24-authoring-epoch-v1.json'
PROOF_SHA256 = '6761659d30fc4c90191521949a299bf7b1527180b924cabc2cd5a5a54aa38a4b'
PREFIX = 'assets/hd/current-terrain24/'
IDS = (340, 361, 362, 363, 364, 365, 366, 367, 368, 371, 372, 373, 374,
       375, 376, 378, 380, 381, 382, 383, 386, 387, 388, 390)
INCLUDES = ('src/private_ground_family.inc', 'src/private_cliff_family.inc',
            'src/private_corner366.inc', 'src/private_static340.inc')


def authority(root):
    raw = checked.regular(root, PROOF, 2 * 1024 * 1024)
    if checked.sha(raw) != PROOF_SHA256:
        raise ValueError('Unreviewed terrain24 epoch proof')
    proof = checked.object_bytes(raw)
    if (proof.get('schema') != 'opentyrian-terrain24-epoch-v1' or
            proof.get('epoch') != MODE or
            tuple(r['id'] for r in proof['resources']) != IDS):
        raise ValueError('Changed terrain24 membership')
    predecessor = proof['predecessor23']
    if checked.sha(checked.regular(root, predecessor['proof_path'], 2 * 1024 * 1024)) != predecessor['proof_sha256']:
        raise ValueError('Changed retained terrain23 predecessor proof')
    return proof


def rows_for(root):
    return copy.deepcopy(authority(root)['rows'])


def _cliff_masks(root, proof):
    for name, digest in proof['include_sha256'].items():
        if checked.sha(checked.regular(root, name)) != digest:
            raise ValueError('Changed terrain24 loader: ' + name)
    text = checked.regular(root, 'src/private_cliff_family.inc').decode('utf-8')
    match = re.search(r'private_cliff_masks\[12\]\[84\]=(\{.*?\});', text)
    if match is None:
        raise ValueError('Missing finite cliff masks')
    values = [int(v) for v in re.findall(r'\d+', match.group(1))]
    if len(values) != 1008 or any(v > 255 for v in values):
        raise ValueError('Malformed finite cliff masks')
    return {tile: bytes(values[n * 84:(n + 1) * 84])
            for n, tile in enumerate(proof['runtime_groups']['cliff12'])}


def load(root):
    proof = authority(root)
    masks = _cliff_masks(root, proof)
    result = {}
    for resource in proof['resources']:
        row = resource['row']
        raw = checked.regular(root, row['source_path'], 172060)
        if (len(raw) != row['bytes'] or checked.sha(raw) != row['sha256'] or
                checked.blob(raw) != row['git_blob']):
            raise ValueError('Changed terrain24 HDA bytes: ' + row['source_path'])
        expected = (b'HDR1', 2010000 + resource['id'], 8, 24, 28, 0, 0)
        if len(raw) != 172060 or struct.unpack('<4s4I2i', raw[:28]) != expected:
            raise ValueError('Wrong terrain24 HDA header')
        payload = raw[28:]
        if (checked.sha(payload) != resource['payload_sha256'] or
                checked.fnv(payload) != resource['payload_fnv64']):
            raise ValueError('Changed terrain24 payload')
        mask = masks.get(resource['id'])
        if mask is not None and checked.sha(mask) != resource['cliff_mask_sha256']:
            raise ValueError('Changed original-derived cliff mask')
        opaque = 0
        for y in range(224):
            for x in range(192):
                cell = (y // 8) * 24 + x // 8
                solid = mask is None or bool((mask[cell // 8] >> (cell % 8)) & 1)
                offset = 4 * (y * 192 + x)
                rgba = payload[offset:offset + 4]
                if rgba[3] != (255 if solid else 0) or (not solid and rgba[:3] != b'\0\0\0'):
                    raise ValueError('Changed terrain24 alpha/mask')
                opaque += solid
        if opaque != resource['native_nonzero_cells'] * 64:
            raise ValueError('Changed terrain24 coverage')
        result[row['destination']] = copy.deepcopy(row)
    if len(result) != 24:
        raise ValueError('Changed terrain24 resource count')
    return result


def marked_rows(manifest):
    """Cheap conservative markers only; never a validation/authorization result."""
    if type(manifest) is not dict:
        return False
    revision = manifest.get('source_revision', {})
    closure = manifest.get('closure', {})
    if ((type(revision) is dict and 'terrain24_epoch' in revision) or
            (type(closure) is dict and any(str(k).startswith('terrain24') for k in closure))):
        return True
    rows = manifest.get('files', [])
    if type(rows) is not list:
        return False
    names = {f'terrain-shapesz-{tile}-8.hda' for tile in IDS}
    for row in rows:
        if type(row) is not dict:
            continue
        if (row.get('revision') == MODE or
                type(row.get('identity')) is int and row['identity'] in {2010000 + i for i in IDS}):
            return True
        for key in ('source_path', 'destination'):
            value = row.get(key)
            if isinstance(value, str) and (value.casefold().startswith((PREFIX.casefold(), 'assets/hd/current-terrain23/')) or
                                         value.rsplit('/', 1)[-1].casefold() in names):
                return True
    return False


def validate_runtime_rows(root, manifest, required=False):
    if not required and not marked_rows(manifest):
        return
    rows = manifest.get('files') if type(manifest) is dict else None
    if type(rows) is not list or any(type(row) is not dict for row in rows):
        raise ValueError('Expected terrain24 runtime rows')
    expected = rows_for(root)
    selected = [row for row in rows if marked_rows({'files': [row]})]
    if (len(selected) != 24 or
            sorted(selected, key=lambda r: str(r.get('destination'))) != expected):
        raise ValueError('Missing, duplicate or changed terrain24 row')
    actual = load(root)
    if sorted(actual.values(), key=lambda r: r['destination']) != expected:
        raise ValueError('Changed terrain24 registered resources')


def epoch_marked_rows(manifest):
    """24-only markers; retained23 rows and includes do not select this epoch."""
    if type(manifest) is not dict:
        return False
    revision, closure = manifest.get('source_revision', {}), manifest.get('closure', {})
    if ((type(revision) is dict and 'terrain24_epoch' in revision) or
            (type(closure) is dict and any(str(k).startswith('terrain24') for k in closure))):
        return True
    rows = manifest.get('files', [])
    if type(rows) is not list:
        return False
    for row in rows:
        if type(row) is not dict:
            continue
        if (row.get('revision') == MODE or
                type(row.get('identity')) is int and row['identity'] == 2010340):
            return True
        for key in ('source_path', 'destination'):
            value = row.get(key)
            if isinstance(value, str) and (value.casefold().startswith(PREFIX.casefold()) or
                    value.rsplit('/', 1)[-1].casefold() == 'terrain-shapesz-340-8.hda'):
                return True
    return False
