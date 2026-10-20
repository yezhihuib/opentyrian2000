"""Read-only finite default/optional HD pack catalog verification.

Only files named by the supplied catalog are read. Artwork is never rebuilt.
"""
from pathlib import Path, PurePosixPath
import hashlib
import json
import struct
from PIL import Image

ASTEROID1_OPTIONAL_CATALOG_SHA256 = '78f07289ba5ccab641980e044405c2128ce7d593a5687089c9a51dad27ba44ce'
ASTEROID1_BASES = (1, 3, 5, 7, 9, 13, 15, 31, 34, 39, 41, 43, 45, 47, 49, 51, 53, 77, 79, 81, 83, 85, 88, 89, 91, 95, 114, 121, 123, 127, 129, 131, 133, 152, 157, 159, 161, 169, 193, 195, 197, 199, 201, 203, 205, 207, 229, 231, 233, 235, 245, 267, 269, 271, 273, 281, 283)
ASTEROID1_NEWSHS_BASES = (11, 125, 153, 155, 157, 159, 161, 163, 191, 193, 195, 197, 199, 201, 229, 231, 233, 235, 277)
ASTEROID1_NEWSHP_BASES = (115, 117, 119, 121, 229, 231, 267, 269)
# Explicit family/base namespaces are the identity boundary. NEWSHS325 retains
# material108 while NEWSHS272/275/276 use136/137/138; source bank alone is unsafe.
# Tuples are logical bank, exact source filename, retained material, image bases.
ASTEROID1_FAMILY_ROLES = {
    'ten': (8, 'newshd.shp', 108, (13, 15, 31, 34, 49, 51, 53, 88, 89, 91)),
    'four': (8, 'newshd.shp', 108, (7, 9, 45, 47)),
    'common4': (8, 'newshd.shp', 108, (1, 3, 39, 41)),
    'random5': (8, 'newshd.shp', 108, (5,)),
    'goldwing': (8, 'newshd.shp', 108, (79, 81, 83)),
    'random43': (8, 'newshd.shp', 108, (43,)),
    'random85': (8, 'newshd.shp', 108, (85,)),
    'random123': (8, 'newshd.shp', 108, (123,)),
    'random95': (8, 'newshd.shp', 108, (95,)),
    'random114': (8, 'newshd.shp', 108, (114,)),
    'random133': (8, 'newshd.shp', 108, (133,)),
    'random152': (8, 'newshd.shp', 108, (152,)),
    'random286': (8, 'newshd.shp', 108, (229, 231, 233, 235)),
    'fork284': (8, 'newshd.shp', 108, (121,)),
    'capsule545': (8, 'newshd.shp', 108, (77,)),
    'paired287_288': (8, 'newshd.shp', 108, (245, 281, 283)),
    'firing325': (23, 'newshs.shp', 108, (11, 125, 277)),
    'ember269': (8, 'newshd.shp', 108, (267, 269, 271, 273)),
    'linked338': (20, 'newshp.shp', 135, (115, 117, 119, 121, 229, 231, 267, 269)),
    'pulsing272': (23, 'newshs.shp', 136, (229, 231, 233, 235)),
    'triple275': (23, 'newshs.shp', 137, (153, 155, 157, 159, 161, 163)),
    'columns276': (23, 'newshs.shp', 138, (191, 193, 195, 197, 199, 201)),
    'turret273': (8, 'newshd.shp', 139, (169, 193, 195, 197, 199, 201, 203, 205, 207)),
    'projectile304': (8, 'tyrian.shp', 140, (304,)),
    'firing270': (8, 'newshd.shp', 141, (127,129,131)),
    'enemy_orb112113': (8, 'tyrian.shp', 142, (112,113)),
    'clamshell285': (8, 'newshd.shp', 143, (157,159,161)),
    'fixture429': (201, 'shapesz.dat', 144, (429,430,439,440)),
}
SHA = lambda data: hashlib.sha256(data).hexdigest()


def verify_optional_inventory(manifest):
    optional = manifest.get('optional_packs', {})
    if not optional:
        return optional
    assert set(optional) == {'asteroid1-ten-v1'}, 'Unrecognized optional pack inventory'
    pack = optional['asteroid1-ten-v1']
    expected = ({f'enemy-newshd-{base}-8.hda' for base in ASTEROID1_BASES} |
                {f'enemy-newshs-{base}-8.hda' for base in ASTEROID1_NEWSHS_BASES} |
                {f'enemy-newshp-{base}-8.hda' for base in ASTEROID1_NEWSHP_BASES} |
                {'enemy-projectile304-304-8.hda'} | {f'enemy-orb112113-{base}-8.hda' for base in (112,113)} |
                {f'terrain-shapesz-{base}-8.hda' for base in (429,430,439,440)})
    assert pack['count'] == 91 and set(pack['files']) == expected, 'Optional pack must list all 91 exact bank-qualified images'
    families = pack['families']
    assert set(families) == set(ASTEROID1_FAMILY_ROLES), 'Optional family inventory changed'
    assert sum(len(row['source_records']) for row in families.values()) == 57
    # Keep earlier families byte-for-byte in metadata; 272/275 retain136/137 and276 independently adds138.
    assert families['firing325'] == {'image_bases': [11, 125, 277], 'source_records': [325],
                                      'logical_bank': 23, 'source_bank': 'newshs.shp'}
    assert families['ember269'] == {'image_bases': [267, 269, 271, 273], 'source_records': [269],
                                     'logical_bank': 8, 'source_bank': 'newshd.shp'}
    assert families['linked338'] == {'image_bases': list(ASTEROID1_NEWSHP_BASES),
                                    'source_records': [338, 339, 340, 341, 342],
                                    'logical_bank': 20, 'source_bank': 'newshp.shp', 'material_role': 135}
    assert families['pulsing272'] == {'image_bases': [229, 231, 233, 235], 'source_records': [272],
                                     'logical_bank': 23, 'source_bank': 'newshs.shp', 'material_role': 136}
    assert families['triple275'] == {'image_bases': [153, 155, 157, 159, 161, 163], 'source_records': [275],
                                     'logical_bank': 23, 'source_bank': 'newshs.shp', 'material_role': 137}
    assert families['columns276'] == {'image_bases': [191, 193, 195, 197, 199, 201], 'source_records': [276],
                                      'logical_bank': 23, 'source_bank': 'newshs.shp', 'material_role': 138}
    assert families['turret273'] == {'image_bases': [169,193,195,197,199,201,203,205,207], 'source_records': [273], 'logical_bank': 8, 'source_bank': 'newshd.shp', 'material_role': 139, 'source_weapons': [144], 'projectile_selectors': [304]}
    assert families['projectile304'] == {'image_bases': [304], 'source_records': [], 'logical_bank': 8, 'source_bank': 'tyrian.shp', 'source_subbank': 'player-shot-bank', 'source_role': 'enemy-shot', 'material_role': 140, 'source_bank_bytes': 32060, 'source_bank_sha256': '9bba1e94d38df61f152412c226bfd6df235e42027c9143c5961d4a5add853a68'}
    assert families['firing270'] == {'image_bases': [127, 129, 131], 'source_records': [270], 'logical_bank': 8, 'source_bank': 'newshd.shp', 'material_role': 141, 'source_weapons': [145, 146], 'projectile_selectors': [112, 113]}
    assert families['enemy_orb112113'] == {'image_bases': [112, 113], 'source_records': [], 'logical_bank': 8, 'source_bank': 'tyrian.shp', 'source_subbank': 'player-shot-bank', 'source_role': 'enemy-shot', 'material_role': 142, 'source_bank_bytes': 32060, 'source_bank_sha256': '9bba1e94d38df61f152412c226bfd6df235e42027c9143c5961d4a5add853a68'}
    assert families['clamshell285'] == {'image_bases': [157, 159, 161], 'source_records': [285], 'logical_bank': 8, 'source_bank': 'newshd.shp', 'material_role': 143, 'source_weapons': [24], 'classic_projectile_selectors': [91]}
    assert families['fixture429'] == {'image_bases': [429, 430, 439, 440], 'source_records': [], 'logical_bank': 201, 'source_bank': 'shapesz.dat', 'source_role': 'terrain-layer1', 'material_role': 144, 'source_bank_bytes': 318976, 'source_bank_sha256': '3ecc9b59c82e8e7d9c91889aac7d337ca28a59519c4970e256250e4603a9b248'}
    identities, roles, new_roles = set(), [], set()
    for name, (logical_bank, source_bank, material, bases) in ASTEROID1_FAMILY_ROLES.items():
        row = families[name]
        assert (row.get('logical_bank', 8), row.get('source_bank', 'newshd.shp'),
                row.get('material_role', 108), tuple(row['image_bases'])) == (
                    logical_bank, source_bank, material, bases), 'Family/base material allowlist mismatch'
        for base in bases:
            identity = (logical_bank, base)
            assert identity not in identities, 'Optional source-bank/base collision'
            identities.add(identity)
            filename = f'terrain-shapesz-{base}-8.hda' if name == 'fixture429' else 'enemy-projectile304-304-8.hda' if name == 'projectile304' else f'enemy-orb112113-{base}-8.hda' if name == 'enemy_orb112113' else f'enemy-{source_bank[:-4]}-{base}-8.hda'
            item = pack['files'][filename]
            header = item['header_u32']
            if name == 'fixture429':
                assert header == [1440000 + base, 8, 24, 28, 0, 0], 'Exact layer1 terrain HDR1 identity'
            elif name in ('projectile304', 'enemy_orb112113'):
                assert header == [material * 10000 + base, 8, 12, 14, 0, 0], 'Exact enemy projectile HDR1 identity'
            else:
                assert header == [material * 10000 + base, 8, 24, 28, 0, 0] or (
                logical_bank == 8 and header == [material * 10000 + base, 8, 12, 14, 0, 0]), 'Family/base HDR1 material mismatch'
            roles.append(header[0])
            if material in (135, 136, 137, 138, 139, 140, 141, 142, 143, 144):
                new_roles.add(header[0])
    assert identities == ({(8, base) for base in ASTEROID1_BASES} |
                          {(23, base) for base in ASTEROID1_NEWSHS_BASES} |
                          {(20, base) for base in ASTEROID1_NEWSHP_BASES} | {(8, 304), (8,112), (8,113)} |
                          {(201, base) for base in (429,430,439,440)})
    assert len(roles) == len(set(roles)) == 91, 'Optional role collision'
    default_roles = {item['header_u32'][0] for installed in manifest['packs'].values()
                     for item in installed['files'].values()}
    assert not (new_roles & default_roles), 'Optional private material collides with a default role'
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
