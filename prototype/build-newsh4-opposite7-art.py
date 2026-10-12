#!/usr/bin/env python3
"""Validate and reproduce the frozen opposite/link2 seven-piece art package.

Only the generated master and technical support mask feed the immutable builder.
Optional original data is read-only source evidence, never an RGB art input. This
script does not run the game or establish moving/hit/ice/removal acceptance.
"""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import re
import struct
import subprocess
import sys

from PIL import Image

IDS = [231, 233, 235, 267, 269, 271, 273]
ACTORS = list(range(73, 80))
OFFSETS = [0, 1, 19, 20]
TILES = {base + offset for base in IDS for offset in OFFSETS}
SOURCE = 'assets/hd/artwork/newsh4-opposite7-v1'
FREEZE = 'fce309722a55c0f62ab563af15ff7af41b9a739d09b3099878753030ec5774bd'
FILES_SHA = 'a8a51edbb45209a7b632b6b9b861f4bbb92f5bbcf941b19e64b37d8f28afbef4'
COUNTS = [110, 201, 229, 263, 295, 425, 504]
EVENT_FIELDS = ['eventtime', 'type', 'dat', 'dat2', 'dat3', 'dat5', 'dat6', 'dat4']


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text())


def no_symlinks(path):
    require(not any(p.is_symlink() for p in [path, *path.parents]),
            'symlink path forbidden: ' + str(path))


def safe_output(value, repo):
    given = value.expanduser()
    require(given.is_absolute(), 'output must be absolute')
    no_symlinks(given)
    out = given.resolve()
    require(not out.exists(), 'output must be fresh')
    require(out.parent.is_dir(), 'output parent must exist')
    require(out != repo and repo not in out.parents and out not in repo.parents,
            'output must be outside repository')
    return out


def inventory(source):
    no_symlinks(source)
    nodes = list(source.rglob('*'))
    require(all(not q.is_symlink() and (q.is_file() or q.is_dir()) for q in nodes),
            'source symlink or special file forbidden')
    manifest_bytes = (source / 'manifest.json').read_bytes()
    require(sha(manifest_bytes) == FREEZE, 'source manifest freeze mismatch')
    frozen = json.loads(manifest_bytes)
    require(frozen['schema'] == 'newsh4-opposite7-art-freeze-v1', 'source schema')
    entries = frozen['files']
    require(len(entries) == frozen['file_count_excluding_manifest_and_FILES'] == 27,
            'source inventory count')
    names = [row['path'] for row in entries]
    require(len(set(names)) == len(names), 'duplicate source inventory path')
    for name in names:
        p = PurePosixPath(name)
        require(not p.is_absolute() and '..' not in p.parts and p.as_posix() == name,
                'unsafe source inventory path')
    expected_files = set(names) | {'manifest.json', 'FILES.sha256'}
    require({q.relative_to(source).as_posix() for q in nodes if q.is_file()}
            == expected_files, 'source inventory differs: missing or unlisted file')
    expected_dirs = {str(parent) for name in names for parent in PurePosixPath(name).parents
                     if str(parent) != '.'}
    require({q.relative_to(source).as_posix() for q in nodes if q.is_dir()}
            == expected_dirs, 'source inventory differs: unlisted directory')
    for row in entries:
        data = (source / row['path']).read_bytes()
        require(len(data) == row['bytes'] and sha(data) == row['sha256'],
                'source file mismatch: ' + row['path'])
    require(sum(row['bytes'] for row in entries) == frozen['bytes_excluding_manifest_and_FILES'],
            'source byte total mismatch')
    checksum_bytes = (source / 'FILES.sha256').read_bytes()
    require(sha(checksum_bytes) == FILES_SHA, 'source FILES.sha256 freeze mismatch')
    listed = {}
    for line in checksum_bytes.decode().splitlines():
        digest, name = line.split('  ', 1)
        require(name not in listed, 'duplicate FILES.sha256 path')
        listed[name] = digest
    require(listed == {**{row['path']: row['sha256'] for row in entries},
                       'manifest.json': FREEZE}, 'source checksum inventory mismatch')
    return frozen


def fnv1a(data):
    stamp = 0xcbf29ce484222325
    for value in data:
        stamp = ((stamp ^ value) * 0x100000001b3) & 0xffffffffffffffff
    return f'{stamp:016x}'


def family_name(name):
    match = re.fullmatch(r'enemy-newsh4-(\d+)-(\d+)\.hda', name)
    return match is not None and int(match[1]) in TILES


def validate_art_and_bindings(repo, source, manifest):
    family = manifest['newsh4_opposite7_v1']
    expected_family = {
        'source': SOURCE, 'source_manifest_sha256': FREEZE, 'density': 8,
        'logical_size': [24, 28], 'assembly_size': [168, 28], 'ids': IDS,
        'slots': list(range(389, 396)), 'actor_types': ACTORS, 'bank_id': 2,
        'link': 2, 'runtime_components': OFFSETS, 'excluded_actor_types': list(range(66, 73)),
    }
    for key, value in expected_family.items():
        require(family[key] == value, 'family metadata mismatch: ' + key)
    contract = load(source / 'contract.json')
    scope = contract['scope']
    require(contract['schema'] == 'newsh4-opposite7-art-v1', 'contract schema')
    for key, value in {'bank': 2, 'source_sheet': 'newsh4.shp', 'records': ACTORS,
                       'bases': IDS, 'link': 2, 'density': 8, 'canvas': [24, 28],
                       'anchor': [6, 7], 'assembly': [168, 28], 'namespace': 102,
                       'quadrants': OFFSETS, 'key_formula': '1020000+base'}.items():
        require(scope[key] == value, 'contract scope mismatch: ' + key)
    require(contract['alpha']['per_piece'] == COUNTS
            and contract['alpha']['logical_owned_cells'] == 2027
            and contract['alpha']['technical_matte_RGB'] == [12, 8, 0]
            and contract['alpha']['outside_RGBA'] == [0, 0, 0, 0]
            and contract['alpha']['original_RGB_in_outputs'] is False, 'contract alpha')
    expected = load(source / 'expected-hashes.json')
    require(expected['outputs'] == contract['canonical_outputs'], 'canonical output metadata')
    require(set(expected['inputs']) == {'sources/generated-whole.png',
                                       'masks/alpha-assembly-logical.png'}, 'generated-only inputs')
    for name, digest in expected['inputs'].items():
        require(sha((source / name).read_bytes()) == digest, 'generated input digest')
    logical = Image.open(source / 'masks/alpha-assembly-logical.png')
    require(logical.mode == 'L' and logical.size == (168, 28)
            and set(logical.tobytes()) == {0, 255}
            and logical.tobytes().count(255) == 2027, 'logical support mask')
    mask = logical.resize((1344, 224), Image.Resampling.NEAREST)
    require(len(family['entries']) == len(expected['outputs']) == 7, 'exact seven entries required')
    defaults = [manifest['default_preview_pack'], manifest['default_debug_pack']]
    require(len(set(defaults)) == 2, 'two distinct default packs required')
    allowed = {f'enemy-newsh4-{base}-8.hda' for base in IDS}
    canonical_paths = set()
    assembly = Image.new('RGBA', (1344, 224))
    for k, (base, row, entry) in enumerate(zip(IDS, expected['outputs'], family['entries'])):
        name = f'enemy-newsh4-{base}-8'
        header = [1020000 + base, 8, 24, 28, 6, 7]
        raw = (source / 'output' / (name + '.hda')).read_bytes()
        png = (source / 'output' / (name + '.png')).read_bytes()
        require(row['base'] == base and row['hda'] == name + '.hda'
                and row['png'] == name + '.png', 'canonical output identity')
        require(raw[:28] == b'HDR1' + struct.pack('<6I', *header)
                and len(raw) == row['hda_bytes'] == 172060, 'HDR1 dimensions/anchor/key')
        require(sha(raw) == row['hda_sha256'] and sha(raw[28:]) == row['rgba_sha256']
                and sha(png) == row['png_sha256'], 'canonical bytes mismatch')
        im = Image.open(source / 'output' / (name + '.png'))
        require(im.mode == 'RGBA' and im.size == (192, 224)
                and im.tobytes() == raw[28:], 'PNG/RGBA/HDR1 disagreement')
        alpha = im.getchannel('A').tobytes()
        require(alpha == mask.crop((k * 192, 0, (k + 1) * 192, 224)).tobytes()
                and sha(alpha) == row['alpha_sha256']
                and alpha.count(255) == COUNTS[k] * 64, 'piece alpha support mismatch')
        require(all(raw[j:j + 3] == b'\0\0\0' for j in range(28, len(raw), 4)
                    if raw[j + 3] == 0), 'transparent RGB must be zero')
        require(entry == {'kind': 'actor', 'bank_role': 102, 'id': base,
                          'enemy_type': 73 + k, 'slot': 389 + k, 'anchor': [6, 7],
                          'rgba_fnv1a64': fnv1a(raw[28:])}, 'entry/FNV binding mismatch')
        assembly.paste(im, (k * 192, 0))
        canonical = f'assets/hd/source/{name}-{sha(raw)[:12]}.png'
        canonical_paths.add(canonical)
        no_symlinks(repo / canonical)
        require((repo / canonical).read_bytes() == png, 'canonical PNG mismatch: ' + canonical)
        indexed = manifest['source_pngs'][sha(raw)]
        require(indexed['path'] == canonical and indexed['sha256'] == sha(png)
                and indexed['RGBA_sha256'] == sha(raw[28:]), 'source PNG index mismatch')
        for pack_name in defaults:
            packed = manifest['packs'][pack_name]['files'][name + '.hda']
            require(packed['header_u32'] == header and packed['sha256'] == sha(raw)
                    and packed['source_png'] == canonical
                    and packed['source_png_sha256'] == sha(png), 'packed metadata mismatch')
            path = repo / 'assets/hd/packs' / pack_name / (name + '.hda')
            no_symlinks(path)
            require(path.read_bytes() == raw, 'packed HDR1 mismatch: ' + str(path))
    require(sha(assembly.tobytes()) == load(source / 'proof/offline-pilot.json')['rgba_sha256'],
            'rejoined assembly mismatch')
    for pack_name, pack in manifest['packs'].items():
        require(pack['count'] == len(pack['files']), 'pack count mismatch')
        relevant = set()
        for name, entry in pack['files'].items():
            header = entry['header_u32']
            if family_name(name) or header[0] in {1020000 + tile for tile in TILES}:
                relevant.add(name)
        require(relevant == (allowed if pack_name in defaults else set()),
                'widened pack, alias, quadrant or density: ' + pack_name)
    # Also reject unindexed files; checking the manifest alone misses stray 4x assets.
    pack_root = repo / 'assets/hd/packs'
    actual = set()
    for path in pack_root.rglob('enemy-newsh4-*.hda'):
        if family_name(path.name):
            no_symlinks(path)
            actual.add(path.relative_to(pack_root).as_posix())
    require(actual == {f'{pack}/{name}' for pack in defaults for name in allowed},
            'widened on-disk pack inventory')
    actual_pngs = set()
    for path in (repo / 'assets/hd/source').glob('enemy-newsh4-*.png'):
        match = re.fullmatch(r'enemy-newsh4-(\d+)-.*\.png', path.name)
        if match and int(match[1]) in TILES:
            actual_pngs.add(path.relative_to(repo).as_posix())
    require(actual_pngs == canonical_paths, 'widened canonical PNG inventory')
    return logical


def verify_originals(repo, source, original_dir, logical):
    root = original_dir.expanduser().resolve()
    require(root != repo and repo not in root.parents, 'original data must stay outside repository')
    proof = load(source / 'proof/source-composites.json')
    audit = load(source / 'proof/source-audit.json')
    data = {}
    for name, digest in audit['provenance']['data_sha256'].items():
        data[name] = (root / name).read_bytes()
        require(sha(data[name]) == digest, 'original-data identity mismatch: ' + name)
    original = data['newsh4.shp']
    require(sha(original) == proof['newsh4_sha256'], 'original RLE identity')
    require(len(proof['records']) == 7 and len(audit['tiles']) == 28, 'original proof cardinality')
    tiles = {tile['id']: tile for tile in audit['tiles']}
    for k, record in enumerate(proof['records']):
        require(record['base'] == IDS[k] and record['type'] == ACTORS[k]
                and [p['id'] for p in record['parts']] == [IDS[k] + v for v in OFFSETS],
                'original composite identity')
        component, composite_indices = Image.new('L', (24, 28)), Image.new('L', (24, 28))
        for part, offset in zip(record['parts'], [(0, 0), (12, 0), (0, 14), (12, 14)]):
            pos = struct.unpack_from('<H', original, 2 * (part['id'] - 1))[0]
            require(pos == part['offset'], 'RLE offset mismatch')
            start, linear = pos, 0
            support, indices = bytearray(168), bytearray(168)
            while original[pos] != 15:
                code = original[pos]
                pos += 1
                linear += code & 15
                count = code >> 4
                require(0 <= linear <= 168 and linear + count <= 168, 'RLE exceeds 12x14')
                support[linear:linear + count] = bytes([255]) * count
                indices[linear:linear + count] = original[pos:pos + count]
                linear += count
                pos += count
            require(pos + 1 - start == part['record_bytes']
                    and support.count(255) == part['opaque_pixels']
                    and sha(indices) == part['indices_sha256']
                    and sha(support) == part['opacity_sha256'], 'RLE record mismatch')
            tile = tiles[part['id']]
            require(tile['source_offset'] == start and tile['source_length'] == pos + 1 - start
                    and sha(original[start:pos + 1]) == tile['source_sha256']
                    and tile['nonzero_pixels'] == tile['opaque_pixels'] == support.count(255)
                    and all(indices[i] for i in range(168) if support[i]), 'RLE nonzero/source proof')
            component.paste(Image.frombytes('L', (12, 14), bytes(support)), offset)
            composite_indices.paste(Image.frombytes('L', (12, 14), bytes(indices)), offset)
        require(list(component.getbbox()) == record['alpha_bbox']
                and sha(component.tobytes()) == record['mask_sha256']
                and sha(composite_indices.tobytes()) == record['index_sha256']
                and component.tobytes().count(255) == COUNTS[k]
                and component.tobytes() == logical.crop((k * 24, 0, (k + 1) * 24, 28)).tobytes(),
                'original composite support mismatch')
    require(tiles[231]['opaque_pixels'] == 0 and tiles[232]['opaque_pixels'] == 2,
            'blank-first-quadrant and two-cell second-quadrant gate')
    reader = (repo / 'src/episodes.c').read_text()
    formats = {'u8': 'B', 's8': 'b', 'u16': 'H', 's16': 'h'}

    def schema(var):
        pattern = r'fread_(u8|s8|u16|s16)_die\(\s*&?' + var + r'\[i\]\.(\w+),\s*(\d+),\s*f\)'
        return [(m[2], formats[m[1]], int(m[3])) for m in re.finditer(pattern, reader)]

    ws, es = schema('weapons'), schema('enemyDat')
    require(len(es) == 28 and ws, 'HDT reader schema mismatch')
    hdt = data['tyrian.hdt']
    pos = (struct.unpack_from('<i', hdt)[0] + 14
           + 1638 * sum(n * struct.calcsize(fmt) for _, fmt, n in ws) + 61 * 82
           + sum(n * size for n, size in [(55, 37), (7, 37), (19, 41), (38, 86), (12, 37)]))
    users, quadrant_users, count = [], [], 0
    frozen_records = {r['id']: r for r in audit['records']}
    for record_id in list(range(851)) + list(range(1001, 1851)):
        record, start = {'id': record_id}, pos
        count += 1
        for name, fmt, n in es:
            values = list(struct.unpack_from('<' + str(n) + fmt, hdt, pos))
            pos += n * struct.calcsize(fmt)
            record[name] = values[0] if n == 1 else values
        if record['shapebank'] == 2:
            bases = set(record['egraphic']) - {0}
            if not record['dani'] and record['dgr']:
                bases.add(record['dgr'])
            overlap = sorted(bases & set(IDS))
            if overlap:
                users.append({'record_id': record_id, 'base_ids': overlap})
            components = {base + offset for base in bases
                          for offset in (OFFSETS if record['esize'] == 1 else [0])}
            overlap = sorted(components & TILES)
            if overlap:
                quadrant_users.append({'record_id': record_id, 'tile_ids': overlap})
        if record_id in ACTORS:
            frozen = frozen_records[record_id]
            require(record == {key: value for key, value in frozen.items() if key != 'audit_sprite'},
                    'original actor lifecycle record mismatch')
            require(start == frozen['audit_sprite']['raw_record_offset']
                    and pos - start == frozen['audit_sprite']['raw_record_size'] == 77,
                    'original actor table offset')
            require(record['armor'] == 50 and record['explosiontype'] == 24
                    and record['dani'] == record['dgr'] == record['dlevel'] == 0
                    and record['value'] == (1000 if record_id == 79 else 0), 'source lifecycle values')
    require(count == audit['provenance']['full_enemy_record_count'] == 1701
            and users == audit['reuse']['all_hdt_enemy_users_of_base_ids_in_bank2']
            and quadrant_users == audit['reuse']['all_hdt_enemy_users_of_any_target_quadrant_in_bank2']
            and [row['record_id'] for row in users] == ACTORS, 'all-HDT reuse audit mismatch')
    level = data['tyrian1.lvl']
    n = struct.unpack_from('<H', level)[0]
    pos = struct.unpack_from('<' + str(n) + 'i', level, 2)[16] + 8
    n = struct.unpack_from('<H', level, pos)[0]
    pos += 2 + 2 * n
    n = struct.unpack_from('<H', level, pos)[0]
    pos += 2
    events = [dict(zip(EVENT_FIELDS, struct.unpack_from('<HBhhbbbB', level, pos + i * 11)),
                   index=i + 1) for i in range(n)]
    require(len(events) == audit['provenance']['event_count'] == 1010, 'source event count')

    def event_fields(event):
        return {key: event[key] for key in [*EVENT_FIELDS, 'index']}

    spawns = [event for event in events if event['type'] in [6, 7, 10, 12, 15, 17, 18, 23, 32, 56]
              and event['dat'] in ACTORS]
    require(len(spawns) == 21 and spawns == [event_fields(event) for group in audit['groups']
                                           for event in group['events']], 'exact 21 link2 spawns')
    require([group['eventtime'] for group in audit['groups']] == [3525, 3863, 3928],
            'opposite group times')
    accelerations = []
    for group in audit['groups']:
        group_spawns = [event for event in spawns if event['eventtime'] == group['eventtime']]
        require(sorted(event['dat'] for event in group_spawns) == ACTORS
                and all(event['type'] == 7 and event['dat4'] == 2 for event in group_spawns),
                'link2 spawn membership')
        for dt, accel in [(5, -2), (15, 2)]:
            found = [event for event in events if event['eventtime'] == group['eventtime'] + dt
                     and event['type'] == 20 and event['dat4'] == 2]
            require(len(found) == 1 and {key: found[0][key] for key in EVENT_FIELDS}
                    == dict(eventtime=group['eventtime'] + dt, type=20, dat=accel,
                            dat2=0, dat3=0, dat5=0, dat6=0, dat4=2), 'link2 acceleration direction')
            accelerations += found
    require(accelerations == [event_fields(event) for event in audit['relevant_mutator_events']
                              if event['dat4'] == 2], 'link2 acceleration source audit')
    require([event for event in events if event['eventtime'] >= 3500 and event['dat4'] == 2]
            == sorted(spawns + accelerations, key=lambda event: event['index']),
            'unexpected late link2 lifecycle override')
    require(not [event for event in events if event['eventtime'] >= 3500
                 and event['type'] in [25, 47] and event['dat4'] in [0, 2]],
            'unexpected late armor override')
    life = audit['lifecycle']
    require(life['source_armor'] == 50 and life['enemyground'] is True and life['explonum'] == 12
            and life['hurt_or_wreck_sprite'] is None, 'frozen lifecycle proof mismatch')
    return {'original_RLE_components': 28, 'empty_231': True, 'two_cell_232': True,
            'HDT_records_audited': count, 'level_events_decoded': len(events),
            'link2_spawns': len(spawns), 'link2_acceleration_events': len(accelerations),
            'source_lifecycle_verified': True, 'original_RGB_art_inputs': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--original-data', type=Path)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    out = safe_output(args.output, repo)
    source = repo / SOURCE
    frozen = inventory(source)
    logical = validate_art_and_bindings(repo, source, load(repo / 'assets/hd/manifest.json'))
    original_receipt = (verify_originals(repo, source, args.original_data, logical)
                        if args.original_data else None)
    subprocess.run([sys.executable, str(source / 'rebuild.py'), '--output', str(out)], check=True)
    expected = {row['path'][7:]: row for row in frozen['files'] if row['path'].startswith('output/')}
    require({path.name for path in out.iterdir()} == set(expected), 'rebuilt output inventory mismatch')
    for name, row in expected.items():
        path = out / name
        require(path.is_file() and not path.is_symlink() and path.stat().st_size == row['bytes']
                and sha(path.read_bytes()) == row['sha256'], 'rebuilt frozen output mismatch: ' + name)
    print(json.dumps({'status': 'PASS', 'source_manifest_sha256': FREEZE, 'source_files': 29,
                      'generated_only_reproduction': True, 'exact_PNG_HDR1_pairs': 7,
                      'finite_default_packs': True, 'alpha_anchors_RGBA_FNV_verified': True,
                      'original_data': original_receipt, 'game_runs': 0,
                      'runtime_acceptance': 'Not established by this source validation.'}, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError, struct.error, subprocess.SubprocessError) as exc:
        print('ERROR: ' + str(exc), file=sys.stderr)
        sys.exit(1)
