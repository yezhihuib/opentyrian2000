"""Read-only finite default/optional HD pack catalog verification.

Only files named by the supplied catalog are read. Artwork is never rebuilt.
"""
from pathlib import Path, PurePosixPath
import hashlib
import json
import struct
from PIL import Image

ASTEROID1_OPTIONAL_CATALOG_SHA256 = '6a86d6582a6b6531aaf67e75d14d6a32886a496d7525899a059e6e76db05c118'
ASTEROID1_BASES = (1, 3, 5, 7, 9, 13, 15, 31, 34, 39, 41, 43, 45, 47, 49, 51, 53, 77, 79, 81, 83, 85, 88, 89, 91, 95, 114, 121, 123, 133, 152, 229, 231, 233, 235)
SHA = lambda data: hashlib.sha256(data).hexdigest()


def verify_optional_inventory(manifest):
    optional = manifest.get('optional_packs', {})
    if not optional:
        return optional
    assert set(optional) == {'asteroid1-ten-v1'}, 'Unrecognized optional pack inventory'
    pack = optional['asteroid1-ten-v1']
    expected = {f'enemy-newshd-{base}-8.hda' for base in ASTEROID1_BASES}
    assert pack['count'] == 35 and set(pack['files']) == expected, 'Optional pack must list all 35 exact images'
    families = pack['families']
    assert set(families) == {'ten', 'four', 'common4', 'random5', 'random43', 'random85', 'random123', 'random95', 'random114', 'random133', 'random152', 'random286', 'goldwing', 'fork284', 'capsule545'}
    assert sum(len(row['source_records']) for row in families.values()) == 42
    assert {base for row in families.values() for base in row['image_bases']} == set(ASTEROID1_BASES)
    normalized = json.dumps(optional, sort_keys=True, separators=(',', ':')).encode()
    assert SHA(normalized) == ASTEROID1_OPTIONAL_CATALOG_SHA256, 'Frozen optional catalog changed'
    return optional


def relative(value):
    path = PurePosixPath(value)
    assert value and not path.is_absolute() and str(path) == value
    assert '..' not in path.parts and '\\' not in value and ':' not in value
    return path


def verify_pack_catalog(manifest, root, *, output=None, defaults=True, optional=True, asset_roots=()):
    root = Path(root)
    roots = [root] + [Path(path) for path in asset_roots]
    def resource(path):
        # Existing files are authoritative: corruption never selects a fallback.
        for base in roots:
            candidate = base / path
            if candidate.exists() or candidate.is_symlink():
                return candidate
        raise FileNotFoundError(f'Missing catalog resource: {path}')
    default_names = {manifest['default_preview_pack'], manifest['default_debug_pack']}
    assert len(default_names) == 2 and set(manifest['packs']) == default_names, 'Exactly two installed default packs required'
    extra = verify_optional_inventory(manifest)
    assert not (default_names & set(extra)), 'Default and optional pack names overlap'
    result = {'verified_pack_count': 0, 'verified_HDA_entries': 0,
              'verified_optional_pack_count': 0, 'verified_optional_HDA_entries': 0,
              'verified_exact_source_pngs': 0, 'verified_optional_source_pngs': 0,
              'default_pack_counts': [manifest['packs'][manifest[key]]['count'] for key in ('default_preview_pack', 'default_debug_pack')],
              'optional_pack_counts': {name: pack['count'] for name, pack in extra.items()},
              'optional_catalog_sha256': SHA(json.dumps(extra, sort_keys=True, separators=(',', ':')).encode()) if extra else None}
    for namespace, packs, enabled in [('default', manifest['packs'], defaults), ('optional', extra, optional)]:
        if not enabled:
            continue
        payloads = {}
        count = 0
        for name, pack in packs.items():
            relative(name)
            assert '/' not in name and len(pack['files']) == pack['count'], f'Pack count mismatch: {name}'
            if output is not None:
                (output / name).mkdir()
            for filename, item in pack['files'].items():
                relative(filename)
                assert '/' not in filename and filename.endswith('.hda')
                source = resource(relative(item['source_png']))
                assert SHA(source.read_bytes()) == item['source_png_sha256'], f'Source PNG fingerprint mismatch: {item["source_png"]}'
                header = item['header_u32']
                assert len(header) == 6 and all(isinstance(value, int) and 0 <= value <= 0xffffffff for value in header)
                assert 1 <= header[1] <= 8 and 1 <= header[2] <= 320 and 1 <= header[3] <= 200
                if str(source) not in payloads:
                    with Image.open(source) as image:
                        assert image.mode == 'RGBA' and image.size == (header[1] * header[2], header[1] * header[3])
                        payloads[str(source)] = image.tobytes()
                raw = b'HDR1' + struct.pack('<6I', *header) + payloads[str(source)]
                assert SHA(raw) == item['sha256'], f'Header/payload fingerprint mismatch: {filename}'
                runtime = resource(Path('assets/hd/packs') / name / filename)
                assert runtime.read_bytes() == raw, f'Runtime HDR1 mismatch: {name}/{filename}'
                if output is not None:
                    (output / name / filename).write_bytes(raw)
                count += 1
        prefix = '' if namespace == 'default' else 'optional_'
        result[f'verified_{prefix}pack_count'] = len(packs)
        result['verified_HDA_entries' if namespace == 'default' else 'verified_optional_HDA_entries'] = count
        result['verified_exact_source_pngs' if namespace == 'default' else 'verified_optional_source_pngs'] = len(payloads)
    return result
