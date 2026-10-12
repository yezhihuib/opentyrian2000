#!/usr/bin/env python3
"""Validate/reproduce the frozen six late-spike source sprites and finite bindings.

Only the generated two-triplet master and technical support masks supply art.
Optional original data is read-only structural evidence, never an RGB input.
Source geometry and predicted spawn ticks do not establish runtime visibility.
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

IDS = [1, 3, 5, 7, 9, 11]
ACTORS = [23, 22, 21, 18, 19, 20]
OFFSETS = [0, 1, 19, 20]
POSITIONS = [(0, 0), (12, 0), (0, 14), (12, 14)]
TILES = {base + offset for base in IDS for offset in OFFSETS}
KEYS = {1010000 + tile for tile in TILES}
SOURCE = 'assets/hd/artwork/late-spike-v1'
FREEZE = '618dd16ebcecddb12bfe6fbfbd3d3327d9f03453ea965ee178026c6911ba564b'
FILES_SHA = 'f69abca8fc9e2a2335593bf48bcaa723892695828cdc05b608dcbe3eb0300c58'
CONTRACT_SHA = '6e4ce3085bac59d7b9256b937e34ee5604f10f176b2a316d91d53d528d2489e2'
COUNTS = [294, 267, 174, 186, 267, 294]
LAYOUTS = [[7, 9, 9, 9, 9, 9, 11], [1, 3, 3, 3, 3, 3, 3, 3, 5],
           [7, 9, 9, 9, 9, 9, 9, 11], [1, 3, 3, 3, 3, 3, 3, 3, 5]]
PREDICTED_TICKS = [6506, 6515, 6526, 6535]
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
    raw = (source / 'manifest.json').read_bytes()
    require(sha(raw) == FREEZE, 'source manifest freeze mismatch')
    frozen = json.loads(raw)
    require(frozen['schema'] == 'generated-source-package-manifest-v1'
            and frozen['package'] == 'formal-newsh2-late-six-v1'
            and frozen['generated_pixel_inputs_only'] is True
            and frozen['original_rgb_or_indices_included'] is False
            and frozen['technical_binary_source_alpha_included'] is True, 'source schema/scope')
    entries = frozen['files']
    require(len(entries) == 26, 'source inventory count')
    names = [row['path'] for row in entries]
    require(len(set(names)) == len(names), 'duplicate source inventory path')
    for name in names:
        p = PurePosixPath(name)
        require(not p.is_absolute() and '..' not in p.parts and p.as_posix() == name,
                'unsafe source inventory path')
    require({q.relative_to(source).as_posix() for q in nodes if q.is_file()}
            == set(names) | {'manifest.json', 'FILES.sha256'},
            'source inventory differs: missing or unlisted file')
    expected_dirs = {str(parent) for name in names for parent in PurePosixPath(name).parents
                     if str(parent) != '.'}
    require({q.relative_to(source).as_posix() for q in nodes if q.is_dir()}
            == expected_dirs, 'source inventory differs: unlisted directory')
    for row in entries:
        data = (source / row['path']).read_bytes()
        require(len(data) == row['bytes'] and sha(data) == row['sha256'],
                'source file mismatch: ' + row['path'])
    raw = (source / 'FILES.sha256').read_bytes()
    require(sha(raw) == FILES_SHA, 'source FILES.sha256 freeze mismatch')
    listed = {}
    for line in raw.decode().splitlines():
        digest, name = line.split('  ', 1)
        require(name not in listed, 'duplicate FILES.sha256 path')
        listed[name] = digest
    require(listed == {**{row['path']: row['sha256'] for row in entries},
                       'manifest.json': FREEZE}, 'source checksum inventory mismatch')
    require(sha((source / 'contract.json').read_bytes()) == CONTRACT_SHA, 'source contract freeze')
    return frozen


def fnv1a(data):
    stamp = 0xcbf29ce484222325
    for value in data:
        stamp = ((stamp ^ value) * 0x100000001b3) & 0xffffffffffffffff
    return f'{stamp:016x}'


def family_name(name):
    match = re.fullmatch(r'enemy-newsh2-(\d+)-(\d+)\.hda', name)
    return match is not None and int(match[1]) in TILES


def validate_art_and_bindings(repo, source, manifest):
    family = manifest['late_spike_v1']
    expected_family = {
        'schema': 'late-spike-six-v1', 'source': SOURCE, 'source_manifest_sha256': FREEZE,
        'source_contract_sha256': CONTRACT_SHA, 'density': 8,
        'logical_size': [24, 28], 'anchor': [6, 7], 'ids': IDS,
        'slots': list(range(404, 410)), 'actor_types': ACTORS, 'bank_id': 1,
        'bank_role': 101, 'runtime_components': OFFSETS, 'links': [7, 8, 9, 10],
        'row_actor_counts': [7, 9, 8, 9], 'opaque_logical_cells': 1482,
        'original_alpha_exact': True,
        'fallback': 'All six approved members required before any replacement; 8x-only selected-pack cached fallback is local to this family',
    }
    require({key: value for key, value in family.items() if key not in ['entries', 'runtime_status']}
            == expected_family, 'family metadata mismatch')
    contract = load(source / 'contract.json')
    for key, value in {
            'schema': 'newsh2-late-six-art-v1', 'bank': 1, 'source_file': 'newsh2.shp',
            'key_namespace': 101, 'bases': IDS,
            'enemy_type_by_base': {str(base): actor for base, actor in zip(IDS, ACTORS)},
            'component_logical_size': [24, 28], 'anchor': [6, 7], 'density': 8,
            'rgba_size': [192, 224], 'source_quadrant_offsets': OFFSETS,
            'source_quadrant_placement': [list(pos) for pos in POSITIONS],
            'opaque_logical_cells': 1482, 'technical_matte_rgb': [8, 8, 8],
            'whole_registered_size': [576, 224], 'layout_spacing': 24,
            'reused_middle_tiles': [3, 9],
            'source_layouts': [{'link': 7 + i, 'bases': row, 'predicted_first_tick': PREDICTED_TICKS[i]}
                               for i, row in enumerate(LAYOUTS)],
    }.items():
        require(contract[key] == value, 'contract scope mismatch: ' + key)
    expected = load(source / 'expected-hashes.json')
    require(set(expected['inputs']) == {'sources/generated-two-triplets.png', 'sources/prompt.txt',
                                       'masks/alpha-triplet-a-logical.png',
                                       'masks/alpha-triplet-b-logical.png'}, 'generated-only inputs')
    for name, digest in expected['inputs'].items():
        require(sha((source / name).read_bytes()) == digest, 'generated input digest')
    logical = []
    for letter in ['a', 'b']:
        mask = Image.open(source / f'masks/alpha-triplet-{letter}-logical.png')
        require(mask.mode == 'L' and mask.size == (72, 28)
                and set(mask.tobytes()) == {0, 255}, 'logical support mask')
        logical.extend(mask.crop((i * 24, 0, (i + 1) * 24, 28)) for i in range(3))
    require([im.tobytes().count(255) for im in logical] == COUNTS, 'per-source support count')
    proof = load(source / 'proof/source-contract.json')
    require([row['base_id'] for row in proof['frames']] == IDS
            and len(family['entries']) == len(expected['outputs']) == 6, 'exact six entries required')
    defaults = [manifest['default_preview_pack'], manifest['default_debug_pack']]
    require(len(set(defaults)) == 2, 'two distinct default packs required')
    allowed = {f'enemy-newsh2-{base}-8.hda' for base in IDS}
    canonical_paths, images = set(), []
    for k, (base, row, entry) in enumerate(zip(IDS, expected['outputs'], family['entries'])):
        name = f'enemy-newsh2-{base}-8'
        header = [1010000 + base, 8, 24, 28, 6, 7]
        raw = (source / 'output' / (name + '.hda')).read_bytes()
        png = (source / 'output' / (name + '.png')).read_bytes()
        require(row['base'] == base and row['key'] == header[0]
                and row['hda'] == name + '.hda' and row['png'] == name + '.png',
                'canonical output identity')
        require(raw[:28] == b'HDR1' + struct.pack('<6I', *header)
                and len(raw) == 172060, 'HDR1 dimensions/anchor/key')
        require(sha(raw) == row['hda_sha256'] and sha(raw[28:]) == row['rgba_sha256']
                and sha(png) == row['png_sha256'], 'canonical bytes mismatch')
        im = Image.open(source / 'output' / (name + '.png'))
        require(im.mode == 'RGBA' and im.size == (192, 224)
                and im.tobytes() == raw[28:], 'PNG/RGBA/HDR1 disagreement')
        alpha = im.getchannel('A').tobytes()
        require(alpha == logical[k].resize(im.size, Image.Resampling.NEAREST).tobytes()
                and sha(alpha) == row['alpha_sha256']
                and alpha.count(255) == row['opaque_logical_cells'] * 64 == COUNTS[k] * 64,
                'piece alpha support mismatch')
        frame = proof['frames'][k]
        require(frame['enemy_record_ids'] == [ACTORS[k]] and frame['opaque_pixels'] == COUNTS[k]
                and sha(logical[k].tobytes()) == frame['alpha_sha256'], 'source alpha proof mismatch')
        require(all(raw[j:j + 3] == b'\0\0\0' for j in range(28, len(raw), 4)
                    if raw[j + 3] == 0), 'transparent RGB must be zero')
        require(entry == {'bank_role': 101, 'id': base, 'slot': 404 + k, 'anchor': [6, 7],
                          'rgba_fnv1a64': fnv1a(raw[28:])}, 'entry/FNV binding mismatch')
        images.append(im)
        canonical = f'assets/hd/source/{name}-{sha(raw)[:12]}.png'
        canonical_paths.add(canonical)
        no_symlinks(repo / canonical)
        require((repo / canonical).read_bytes() == png, 'canonical PNG mismatch: ' + canonical)
        require(manifest['source_pngs'][sha(raw)] == {'path': canonical, 'sha256': sha(png),
                                                   'RGBA_sha256': sha(raw[28:])},
                'source PNG index mismatch')
        for pack_name in defaults:
            packed = manifest['packs'][pack_name]['files'][name + '.hda']
            require(packed == {'header_u32': header, 'sha256': sha(raw),
                               'source_png': canonical, 'source_png_sha256': sha(png)},
                    'packed metadata mismatch')
            path = repo / 'assets/hd/packs' / pack_name / (name + '.hda')
            no_symlinks(path)
            require(path.read_bytes() == raw, 'packed HDR1 mismatch: ' + str(path))
    indexed_family = set()
    expected_hashes = {row['hda_sha256'] for row in expected['outputs']}
    for digest, entry in manifest['source_pngs'].items():
        match = re.fullmatch(r'enemy-newsh2-(\d+)-.*\.png', PurePosixPath(entry['path']).name)
        if digest in expected_hashes or (match and int(match[1]) in TILES):
            indexed_family.add(digest)
    require(indexed_family == expected_hashes, 'widened source PNG index')
    # The opposed caps and middles were independently generated/registered, not flipped.
    for i, j in [(0, 5), (1, 4), (2, 3)]:
        require(images[i].transpose(Image.Transpose.FLIP_LEFT_RIGHT).tobytes()
                != images[j].tobytes(), 'literal mirrored art forbidden')
    receipt = load(source / 'output/rebuild-receipt.json')
    for group in range(2):
        assembly = Image.new('RGBA', (576, 224))
        for i in range(3):
            assembly.paste(images[group * 3 + i], (i * 192, 0))
        require(receipt['assemblies'][group] == {'triplet': 'ab'[group],
                'rgba_sha256': sha(assembly.tobytes()), 'partition_rejoin_exact': True},
                'two-triplet rejoin mismatch')
    for pack_name, pack in manifest['packs'].items():
        require(pack['count'] == len(pack['files']), 'pack count mismatch')
        relevant = {name for name, entry in pack['files'].items()
                    if family_name(name) or entry['header_u32'][0] in KEYS}
        require(relevant == (allowed if pack_name in defaults else set()),
                'widened pack, alias, quadrant or density: ' + pack_name)
    pack_root = repo / 'assets/hd/packs'
    actual = set()
    no_symlinks(pack_root)
    require(not any(path.is_symlink() for path in pack_root.rglob('*')), 'pack inventory symlink forbidden')
    for path in pack_root.rglob('*.hda'):
        # Read headers as well as filenames so an unindexed renamed family file cannot hide.
        with path.open('rb') as handle:
            header = handle.read(8)
        key_matches = len(header) == 8 and header[:4] == b'HDR1' and struct.unpack('<I', header[4:])[0] in KEYS
        if family_name(path.name) or key_matches:
            no_symlinks(path)
            actual.add(path.relative_to(pack_root).as_posix())
    require(actual == {f'{pack}/{name}' for pack in defaults for name in allowed},
            'widened on-disk pack inventory')
    actual_pngs = set()
    for path in (repo / 'assets/hd/source').glob('enemy-newsh2-*.png'):
        match = re.fullmatch(r'enemy-newsh2-(\d+)-.*\.png', path.name)
        if match and int(match[1]) in TILES:
            no_symlinks(path)
            actual_pngs.add(path.relative_to(repo).as_posix())
    require(actual_pngs == canonical_paths, 'widened canonical PNG inventory')
    life = load(source / 'proof/source-lifecycle.json')
    require(life['record_ids'] == sorted(ACTORS) and life['raw_armor'] == 50
            and life['filter']['enemyground'] is True
            and life['filter']['normal_player_shot_hit_palette_flash'] is True
            and life['filter']['ice_blue_filter'] is True
            and life['death']['removed_not_wreck'] is True and life['death']['explonum'] == 4,
            'frozen source lifecycle mismatch')
    return logical


def verify_originals(repo, source, original_dir, logical):
    root = original_dir.expanduser().resolve()
    require(root != repo and repo not in root.parents, 'original data must stay outside repository')
    proof = load(source / 'proof/source-contract.json')
    data = {}
    for name, digest in proof['original_sources_sha256'].items():
        data[name] = (root / name).read_bytes()
        require(sha(data[name]) == digest, 'original-data identity mismatch: ' + name)
    original = data['newsh2.shp']
    require(len(proof['frames']) == 6, 'original proof cardinality')
    for k, frame in enumerate(proof['frames']):
        require(frame['base_id'] == IDS[k] and frame['enemy_record_ids'] == [ACTORS[k]]
                and [part['id'] for part in frame['cells']] == [IDS[k] + v for v in OFFSETS],
                'original composite identity')
        support, indices = Image.new('L', (24, 28)), Image.new('L', (24, 28))
        for part, offset, delta in zip(frame['cells'], POSITIONS, OFFSETS):
            pos = struct.unpack_from('<H', original, 2 * (part['id'] - 1))[0]
            require(pos == part['offset'] and part['sprite_offset'] == delta
                    and part['local_xy'] == list(offset), 'RLE component offset mismatch')
            start, linear = pos, 0
            alpha, palette_indices = bytearray(168), bytearray(168)
            while original[pos] != 15:
                code = original[pos]
                pos += 1
                linear += code & 15
                count = code >> 4
                require(0 <= linear <= 168 and linear + count <= 168, 'RLE exceeds 12x14')
                alpha[linear:linear + count] = b'\xff' * count
                palette_indices[linear:linear + count] = original[pos:pos + count]
                linear += count
                pos += count
            require(pos + 1 - start == part['bytes']
                    and alpha.count(255) == part['opaque_pixels']
                    and sha(original[start:pos + 1]) == part['source_record_sha256']
                    and sum(a == 255 and i == 0 for a, i in zip(alpha, palette_indices))
                    == part['opaque_palette_zero'] == 0, 'RLE source record mismatch')
            support.paste(Image.frombytes('L', (12, 14), bytes(alpha)), offset)
            indices.paste(Image.frombytes('L', (12, 14), bytes(palette_indices)), offset)
        require(list(support.getbbox()) == frame['alpha_bbox_xyxy_exclusive']
                and sha(support.tobytes()) == frame['alpha_sha256']
                and sha(indices.tobytes()) == frame['indices_sha256']
                and support.tobytes().count(255) == COUNTS[k]
                and support.tobytes() == logical[k].tobytes(), 'original composite support mismatch')
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
    for record_id in list(range(851)) + list(range(1001, 1851)):
        record = {'id': record_id}
        count += 1
        for name, fmt, n in es:
            values = list(struct.unpack_from('<' + str(n) + fmt, hdt, pos))
            pos += n * struct.calcsize(fmt)
            record[name] = values[0] if n == 1 else values
        if record['shapebank'] == 1:
            bases = set(record['egraphic']) - {0, 999}
            if record['dani'] == 0 and record['dgr']:
                bases.add(record['dgr'])
            overlap = sorted(bases & set(IDS))
            if overlap:
                users.append({'id': record_id, 'matching_bases': overlap, 'record': record})
            components = {base + offset for base in bases
                          for offset in (OFFSETS if record['esize'] == 1 else [0])}
            overlap = sorted(components & TILES)
            if overlap:
                quadrant_users.append({'id': record_id, 'matching_tiles': overlap,
                    'matching_render_bases': sorted(base for base in bases
                        if {base + d for d in (OFFSETS if record['esize'] == 1 else [0])} & TILES)})
        if record_id in ACTORS:
            require(record == proof['records'][str(record_id)], 'original actor lifecycle record mismatch')
            require(record['armor'] == 50 and record['explosiontype'] == 8
                    and record['dani'] == record['dgr'] == record['dlevel'] == record['animate'] == 0
                    and record['xcaccel'] == (16 if record_id <= 20 else -16)
                    and record['value'] == (500 if record_id in [20, 23] else 0), 'source lifecycle values')
    require(count == proof['reuse_audit']['loaded_records'] == 1701
            and users == proof['reuse_audit']['bank_qualified_base_users']
            and quadrant_users == proof['reuse_audit']['quadrant_overlap_users']
            and [row['id'] for row in users] == sorted(ACTORS), 'all-HDT reuse audit mismatch')
    level = data['tyrian1.lvl']
    n = struct.unpack_from('<H', level)[0]
    pos = struct.unpack_from('<' + str(n) + 'i', level, 2)[16] + 8
    n = struct.unpack_from('<H', level, pos)[0]
    pos += 2 + 2 * n
    n = struct.unpack_from('<H', level, pos)[0]
    pos += 2
    events = [dict(zip(EVENT_FIELDS, struct.unpack_from('<HBhhbbbB', level, pos + i * 11)),
                   index=i + 1) for i in range(n)]
    require(len(events) == 1010, 'source event count')
    spawns = [event for event in events if event['type'] in [6, 7, 10, 12, 15, 17, 18, 23, 32, 56]
              and event['dat'] in ACTORS]
    require(len(spawns) == 33 and spawns == [{key: e[key] for key in [*EVENT_FIELDS, 'index']}
            for e in proof['all_family_spawn_events']], 'exact 33 family spawns')
    for i, (link, layout) in enumerate(zip(range(7, 11), LAYOUTS)):
        group = [event for event in spawns if event['dat4'] == link]
        ordered = sorted(group, key=lambda event: event['dat2'])
        assembly = proof['assemblies'][i]
        require(len(group) == len(layout) and assembly['enemy_count'] == len(layout)
                and [proof['records'][str(e['dat'])]['egraphic'][0] for e in ordered] == layout
                and [e['dat2'] for e in ordered] == list(range(ordered[0]['dat2'], ordered[-1]['dat2'] + 1, 24))
                and {e['eventtime'] for e in group} == {[4912, 4930, 4952, 4970][i]}
                and {e['type'] for e in group} == {[6, 6, 10, 10][i]}
                and assembly['scalar_predicted_spawn_tick'] == PREDICTED_TICKS[i],
                'four independent source rows mismatch')
    require(not [e for e in events if e['type'] in [49, 50, 51, 52]], 'custom bank spawn scope changed')
    return {'original_RLE_components': 24, 'original_alpha_cells': 1482,
            'HDT_records_audited': count, 'level_events_decoded': len(events),
            'family_spawns': len(spawns), 'row_actor_counts': [7, 9, 8, 9],
            'independent_links': [7, 8, 9, 10], 'source_lifecycle_records_verified': True,
            'predicted_ticks_are_not_runtime_evidence': True, 'original_RGB_art_inputs': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--original-data', type=Path)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    out = safe_output(args.output, repo)
    if args.original_data:
        original_root = args.original_data.expanduser().resolve()
        require(out != original_root and original_root not in out.parents and out not in original_root.parents,
                'output must not overlap original data')
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
    print(json.dumps({'status': 'PASS', 'source_manifest_sha256': FREEZE, 'source_files': 28,
                      'generated_only_reproduction': True, 'exact_PNG_HDR1_pairs': 6,
                      'finite_default_packs': True, 'alpha_anchors_RGBA_FNV_verified': True,
                      'original_data': original_receipt, 'game_runs': 0,
                      'runtime_acceptance': 'Not established by source validation.'}, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError, IndexError, struct.error, subprocess.SubprocessError) as exc:
        print('ERROR: ' + str(exc), file=sys.stderr)
        sys.exit(1)
