#!/usr/bin/env python3
"""Validate/reproduce the frozen V2 six-member overlapping entry-craft source.

The selected generated master and technical support masks supply all art. Optional
original data is read-only structural evidence, never an RGB art input. No game,
media capture, combat-state changes or runtime-visibility claim is made here.
"""
from pathlib import Path, PurePosixPath
import argparse
import collections
import hashlib
import json
import re
import struct
import subprocess
import sys

from PIL import Image

IDS = [81, 83, 85, 119, 121, 123]
ACTORS = list(range(468, 474))
OFFSETS = [0, 1, 19, 20]
POSITIONS = [(0, 0), (12, 0), (0, 14), (12, 14)]
PLACEMENTS = [[123, 48, 24], [81, 0, 0], [83, 24, 0], [85, 48, 0],
              [119, 0, 24], [121, 24, 24]]
TILES = {base + offset for base in IDS for offset in OFFSETS}
KEYS = {1020000 + tile for tile in TILES}
SOURCE = 'assets/hd/artwork/newsh4-entry6-v1'
FREEZE = '96c59e764ab2456d51476ba00f0c27e423fa4758469c512791c95d1e4dd87f04'
FILES_SHA = 'ed79a583d8e16a5eb3d29f86cd8b648f7977301e533f56ad0cc4fbe0ab2b74ed'
CONTRACT_SHA = '9a1e8d8da2a4439e41b9c462289ca132099efc4ab27bb627ef48badae9764153'
WHOLE_RGBA_SHA = '759468ad823dfbf077cc71afefb32f5779a93e51d97139745a4f8be511930afb'
COUNTS = [263, 351, 113, 365, 541, 135]
EMPTY_TILES = [86, 105, 124, 143]
ORIGINAL_HASHES = {
    'newsh4.shp': 'ab8881b4a26e723650780b19d5aed4ebfe410ea450d4bf7b80840628d61fd89b',
    'tyrian.hdt': 'fde8506326e7bb0916b38c362e33bf8a8a5affa561206c021af7f65b4a17745b',
    'tyrian1.lvl': '54cbb00b57b84aa992a70cfcb170cb1edeb59507873723630d60080ba8351352',
}
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


def safe_relative(value):
    path = PurePosixPath(value)
    require(value and not path.is_absolute() and '..' not in path.parts
            and path.as_posix() == value and '\\' not in value,
            'unsafe manifest path: ' + value)
    return path


def safe_output(value, repo):
    given = value.expanduser()
    require(given.is_absolute(), 'output must be absolute')
    require('..' not in given.parts, 'output traversal forbidden')
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
            and frozen['package'] == 'formal-newsh4-entry-six-v1'
            and frozen['selected_art'] == 'V2 only'
            and frozen['original_rgb_or_indices_included'] is False
            and frozen['technical_binary_source_alpha_included'] is True, 'source schema/scope')
    entries = frozen['files']
    require(len(entries) == 33, 'source inventory count')
    names = [row['path'] for row in entries]
    require(len(set(names)) == len(names), 'duplicate source inventory path')
    for name in names:
        safe_relative(name)
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
    match = re.fullmatch(r'enemy-newsh4-(\d+)-(\d+)\.hda', name)
    return match is not None and int(match[1]) in TILES


def verify_rejoin(source, logical, images, proof):
    union = Image.new('L', (72, 52))
    rejoin = Image.new('RGBA', (576, 416))
    owners, overlaps = {}, []
    for base, x, y in PLACEMENTS:
        union.paste(255, (x, y, x + 24, y + 28), logical[base])
        rejoin.alpha_composite(images[base], (x * 8, y * 8))
        for ly in range(28):
            for lx in range(24):
                if logical[base].getpixel((lx, ly)):
                    point = x + lx, y + ly
                    if point in owners:
                        overlaps.append({'x': point[0], 'y': point[1],
                                         'earlier_base': owners[point], 'later_base': base})
                    owners[point] = base
    require(proof['proposed_placements'] == proof['proposed_original_draw_order'] == PLACEMENTS
            and proof['proposed_assembly_size'] == [72, 52]
            and sum(mask.tobytes().count(255) for mask in logical.values()) == proof['summed_opaque'] == 1768
            and union.tobytes().count(255) == len(owners) == proof['union_opaque'] == 1635
            and overlaps == proof['overlapping_opaque_pixels'] and len(overlaps) == 133,
            'source-order independent-mask overlap mismatch')
    counts = collections.Counter((row['earlier_base'], row['later_base']) for row in overlaps)
    require(counts == {(123, 85): 3, (81, 119): 39, (83, 121): 91}, 'ordered overlap ownership mismatch')
    audit = load(source / 'proof/source-art-contract.json')['source_assembly']
    require(audit['source_order_placements'] == PLACEMENTS and audit['stride'] == [24, 24]
            and audit['vertical_envelope_overlap'] == 4 and list(union.getbbox()) == audit['opaque_bbox']
            and audit['overlap_order_counts'] == [{'earlier': a, 'later': b, 'count': n}
                                                  for (a, b), n in counts.items()],
            'source-assembly contract mismatch')
    master = Image.open(source / 'sources/generated-whole-selected-v2.png').convert('RGBA')
    require(master.size == (1330, 1182), 'generated master size')
    registered = Image.new('RGBA', (576, 416), (12, 8, 0, 255))
    registered.alpha_composite(master.crop((204, 259, 1034, 965)).resize((448, 384),
                                Image.Resampling.LANCZOS), (24, 16))
    registered.putalpha(union.resize(registered.size, Image.Resampling.NEAREST))
    rgba = bytearray(registered.tobytes())
    for i in range(0, len(rgba), 4):
        if rgba[i + 3] == 0:
            rgba[i:i + 4] = b'\0' * 4
    require(rejoin.tobytes() == rgba and sha(rgba) == WHOLE_RGBA_SHA,
            'selected V2 registration/source-order rejoin mismatch')
    receipt = load(source / 'output/rebuild-receipt.json')
    require(receipt['source_order_rejoin_byte_exact'] is True
            and receipt['whole_assembly_rgba_sha256'] == WHOLE_RGBA_SHA
            and receipt['summed_opaque_logical_cells'] == 1768
            and receipt['union_opaque_logical_cells'] == 1635
            and receipt['overlap_opaque_logical_cells'] == 133, 'frozen rejoin receipt mismatch')


# BEGIN validated boss full-composite coexistence

def validated_boss_full_composites(repo, manifest):
    """Exclude only fully validated boss86/124 bindings from the entry raw census.

    Their shared original entry quadrants remain empty. Numeric overlap alone,
    a manifest flag or a partial boss import never authorizes an exception.
    """
    if 'boss_whole_family_v2_inward_alpha' not in manifest:
        return set(), set(), set()
    import importlib.util
    spec = importlib.util.spec_from_file_location('boss_whole_art', repo / 'prototype/build-boss-whole-family-art.py')
    boss = importlib.util.module_from_spec(spec)
    old_bytecode = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(boss)
    finally:
        sys.dont_write_bytecode = old_bytecode
    require(boss.exact_json(manifest, boss.load(repo / 'assets/hd/manifest.json')),
            'boss compatibility requires the validated on-disk manifest')
    boss.validate(repo)
    hashes, packed, canonical = set(), set(), set()
    for base in [86, 124]:
        name = f'enemy-newsh4-{base}-8.hda'
        for pack in boss.DEFAULTS:
            entry = manifest['packs'][pack]['files'][name]
            hashes.add(entry['sha256'])
            packed.add(f'{pack}/{name}')
            canonical.add(entry['source_png'])
    return hashes, packed, canonical

# END validated boss full-composite coexistence


def validate_art_and_bindings(repo, source, manifest):
    boss_hashes, boss_packed, boss_canonical = validated_boss_full_composites(repo, manifest)
    family = manifest['newsh4_entry6_v1']
    expected_family = {
        'schema': 'newsh4-entry-six-v1', 'source': SOURCE, 'source_manifest_sha256': FREEZE,
        'source_contract_sha256': CONTRACT_SHA, 'density': 8,
        'logical_size': [24, 28], 'anchor': [6, 7], 'assembly_size': [72, 52], 'ids': IDS,
        'slots': list(range(410, 416)), 'actor_types': ACTORS, 'bank_id': 2, 'bank_role': 102,
        'runtime_components': OFFSETS, 'source_order_placements': PLACEMENTS,
        'vertical_stride': 24, 'row_envelope_overlap': 4,
        'summed_opaque_logical_cells': 1768, 'union_opaque_logical_cells': 1635,
        'overlap_opaque_logical_cells': 133, 'original_alpha_exact': True,
        'source_armor': 0, 'constructed_avail': 2, 'constructed_armor': 255,
        'preserve_recycled_scoreitem': True, 'excluded_boss_bases': [86, 124],
        'fallback': 'All six approved members required before any replacement; 8x-only selected-pack cached fallback is local to this family',
    }
    require({key: value for key, value in family.items() if key not in ['entries', 'runtime_status']}
            == expected_family, 'family metadata mismatch')
    contract = load(source / 'contract.json')
    for key, value in {
        'schema': 'newsh4-entry-six-art-v1', 'bank': 2, 'source_file': 'newsh4.shp',
        'source_sha256': ORIGINAL_HASHES['newsh4.shp'], 'key_namespace': 102,
        'bases': IDS, 'enemy_types': ACTORS, 'logical_component_size': [24, 28],
        'anchor': [6, 7], 'density': 8, 'pixel_size': [192, 224],
        'whole_assembly_size': [72, 52], 'source_order_placements': PLACEMENTS,
        'vertical_stride': 24, 'row_envelope_overlap': 4, 'summed_opaque_logical_cells': 1768,
        'union_opaque_logical_cells': 1635, 'overlap_opaque_logical_cells': 133,
        'registration_crop_halfopen': [204, 259, 1034, 965],
        'registration_target_halfopen_8x': [24, 16, 472, 400],
        'whole_registered_size_8x': [576, 416], 'matte_rgb': [12, 8, 0],
    }.items():
        require(contract[key] == value, 'contract scope mismatch: ' + key)
    expected = load(source / 'expected-hashes.json')
    require(set(expected['inputs']) == {f'masks/alpha-{base}-logical.png' for base in IDS}
            | {'sources/generated-whole-selected-v2.png', 'sources/prompt-initial.txt',
               'sources/prompt-tone-v2.txt', 'sources/provenance.json'}, 'generated-only inputs')
    for name, digest in expected['inputs'].items():
        require(sha((source / name).read_bytes()) == digest, 'generated input digest')
    logical = {}
    for base, count in zip(IDS, COUNTS):
        mask = Image.open(source / f'masks/alpha-{base}-logical.png')
        require(mask.mode == 'L' and mask.size == (24, 28) and set(mask.tobytes()) == {0, 255}
                and mask.tobytes().count(255) == count, 'logical support mask')
        logical[base] = mask.copy()
    proof = load(source / 'proof/source-composites.json')
    audit = load(source / 'proof/source-art-contract.json')
    require([row['base'] for row in proof['records']] == IDS
            and len(family['entries']) == len(expected['outputs']) == 6, 'exact six entries required')
    defaults = [manifest['default_preview_pack'], manifest['default_debug_pack']]
    require(len(set(defaults)) == 2, 'two distinct default packs required')
    for pack_name, pack in manifest['packs'].items():
        require(len(safe_relative(pack_name).parts) == 1, 'unsafe pack name')
        for name, row in pack['files'].items():
            require(len(safe_relative(name).parts) == 1, 'unsafe pack filename')
            safe_relative(row['source_png'])
    allowed = {f'enemy-newsh4-{base}-8.hda' for base in IDS}
    canonical_paths, images = set(), {}
    tile_counts = {}
    for k, (base, row, entry) in enumerate(zip(IDS, expected['outputs'], family['entries'])):
        name = f'enemy-newsh4-{base}-8'
        header = [1020000 + base, 8, 24, 28, 6, 7]
        raw = (source / 'output' / (name + '.hda')).read_bytes()
        png = (source / 'output' / (name + '.png')).read_bytes()
        require(row['base'] == base and row['key'] == header[0]
                and row['hda'] == name + '.hda' and row['png'] == name + '.png', 'canonical output identity')
        require(raw[:28] == b'HDR1' + struct.pack('<6I', *header)
                and len(raw) == 172060, 'HDR1 dimensions/anchor/key')
        require(sha(raw) == row['hda_sha256'] and sha(raw[28:]) == row['rgba_sha256']
                and sha(png) == row['png_sha256'], 'canonical bytes mismatch')
        im = Image.open(source / 'output' / (name + '.png'))
        require(im.mode == 'RGBA' and im.size == (192, 224)
                and im.tobytes() == raw[28:], 'PNG/RGBA/HDR1 disagreement')
        alpha = im.getchannel('A').tobytes()
        require(alpha == logical[base].resize(im.size, Image.Resampling.NEAREST).tobytes()
                and sha(alpha) == row['alpha_sha256']
                and alpha.count(255) == row['opaque_logical_cells'] * 64 == COUNTS[k] * 64,
                'piece alpha support mismatch')
        frame = proof['records'][k]
        require(frame['type'] == ACTORS[k] and frame['opaque_pixels'] == COUNTS[k]
                and frame['logical_size'] == [24, 28] and frame['anchor'] == [6, 7]
                and sha(logical[base].tobytes()) == frame['opacity_sha256']
                and list(logical[base].getbbox()) == frame['alpha_bbox'], 'source alpha proof mismatch')
        require({key: val for key, val in audit['per_component_originals'][k].items()
                 if key not in ['mask_path', 'indices_path']} == frame, 'source composite proof disagreement')
        require([part['id'] for part in frame['parts']] == [base + d for d in OFFSETS],
                'source quadrant order mismatch')
        for part, (x, y) in zip(frame['parts'], POSITIONS):
            mask = logical[base].crop((x, y, x + 12, y + 14)).tobytes()
            require(sha(mask) == part['opacity_sha256']
                    and mask.count(255) == part['opaque_pixels'], 'source quadrant alpha mismatch')
            tile_counts[part['id']] = part['opaque_pixels']
        require(all(raw[j:j + 3] == b'\0\0\0' for j in range(28, len(raw), 4)
                    if raw[j + 3] == 0), 'transparent RGB must be zero')
        require(entry == {'bank_role': 102, 'id': base, 'slot': 410 + k, 'anchor': [6, 7],
                          'rgba_fnv1a64': fnv1a(raw[28:])}, 'entry/FNV binding mismatch')
        images[base] = im.copy()
        canonical = f'assets/hd/source/{name}-{sha(raw)[:12]}.png'
        canonical_paths.add(canonical)
        no_symlinks(repo / canonical)
        require((repo / canonical).read_bytes() == png, 'canonical PNG mismatch: ' + canonical)
        require(manifest['source_pngs'][sha(raw)] == {'path': canonical, 'sha256': sha(png),
                                                   'RGBA_sha256': sha(raw[28:])}, 'source PNG index mismatch')
        for pack_name in defaults:
            packed = manifest['packs'][pack_name]['files'][name + '.hda']
            require(packed == {'header_u32': header, 'sha256': sha(raw),
                               'source_png': canonical, 'source_png_sha256': sha(png)}, 'packed metadata mismatch')
            path = repo / 'assets/hd/packs' / pack_name / (name + '.hda')
            no_symlinks(path)
            require(path.read_bytes() == raw, 'packed HDR1 mismatch: ' + str(path))
    require(len(tile_counts) == 24 and sorted(base for base, count in tile_counts.items() if count == 0)
            == EMPTY_TILES, 'exact 20 nonempty/4 empty source quadrants')
    reuse = audit['reuse']
    require([row['record'] for row in reuse if row['full_base_member']] == ACTORS
            and [(row['record'], row['base']) for row in reuse if not row['full_base_member']]
            == [(56, 86), (61, 124)]
            and all(cell['source_opaque_pixels'] == tile_counts[cell['id']] == 0
                    for row in reuse if not row['full_base_member'] for cell in row['shared_cells']),
            'boss overlap must be empty and full-composite family excluded')
    expected_hashes = {row['hda_sha256'] for row in expected['outputs']}
    png_hashes = {row['png_sha256'] for row in expected['outputs']}
    rgba_hashes = {row['rgba_sha256'] for row in expected['outputs']}
    indexed_family = set()
    for digest, entry in manifest['source_pngs'].items():
        safe_relative(entry['path'])
        match = re.fullmatch(r'enemy-newsh4-(\d+)-.*\.png', PurePosixPath(entry['path']).name)
        if (digest in expected_hashes or entry['sha256'] in png_hashes
                or entry['RGBA_sha256'] in rgba_hashes or (match and int(match[1]) in TILES)):
            if digest not in boss_hashes:
                indexed_family.add(digest)
    require(indexed_family == expected_hashes, 'widened source PNG index')
    verify_rejoin(source, logical, images, proof)
    for pack_name, pack in manifest['packs'].items():
        require(pack['count'] == len(pack['files']), 'pack count mismatch')
        relevant = {name for name, entry in pack['files'].items()
                    if (family_name(name) or entry['header_u32'][0] in KEYS)
                    and f'{pack_name}/{name}' not in boss_packed}
        require(relevant == (allowed if pack_name in defaults else set()),
                'widened pack, alias, quadrant or density: ' + pack_name)
    pack_root = repo / 'assets/hd/packs'
    actual = set()
    no_symlinks(pack_root)
    nodes = list(pack_root.rglob('*'))
    require(all(not path.is_symlink() and (path.is_file() or path.is_dir()) for path in nodes),
            'pack inventory symlink or special file forbidden')
    for path in nodes:
        if not path.is_file():
            continue
        with path.open('rb') as handle:
            header = handle.read(8)
        key_matches = len(header) == 8 and header[:4] == b'HDR1' and struct.unpack('<I', header[4:])[0] in KEYS
        if (family_name(path.name) or key_matches) and path.relative_to(pack_root).as_posix() not in boss_packed:
            actual.add(path.relative_to(pack_root).as_posix())
    require(actual == {f'{pack}/{name}' for pack in defaults for name in allowed},
            'widened on-disk pack inventory')
    actual_pngs = set()
    source_root = repo / 'assets/hd/source'
    no_symlinks(source_root)
    for path in source_root.rglob('*'):
        require(not path.is_symlink(), 'canonical source symlink forbidden')
        match = re.fullmatch(r'enemy-newsh4-(\d+)-.*\.png', path.name)
        if match and int(match[1]) in TILES and path.relative_to(repo).as_posix() not in boss_canonical:
            require(path.is_file(), 'canonical PNG must be regular file')
            actual_pngs.add(path.relative_to(repo).as_posix())
    require(actual_pngs == canonical_paths, 'widened canonical PNG inventory')
    life = load(source / 'proof/source-lifecycle.json')
    require(life['family'] == {'records': ACTORS, 'bank': 2, 'bases': IDS}
            and life['damage']['source_armor'] == 0 and life['damage']['constructed_armorleft'] == 255
            and life['damage']['enemyAvail'] == 2 and life['damage']['dlevel'] == -1
            and life['ground_filter']['explosiontype'] == life['ground_filter']['explonum'] == 0
            and life['reward_drop']['value'] == life['reward_drop']['eenemydie'] == 0
            and life['animation']['ani'] == 1 and life['animation']['animate'] == 0
            and 'recycled slot scoreitem unchanged' in life['state_inheritance_caveat']['scoreitem'],
            'frozen source lifecycle mismatch')
    return logical


def verify_originals(repo, source, original_dir, logical):
    given = original_dir.expanduser()
    no_symlinks(given)
    root = given.resolve()
    require(root != repo and repo not in root.parents and root not in repo.parents,
            'original data must stay outside repository')
    proof = load(source / 'proof/source-composites.json')
    audit = load(source / 'proof/source-art-contract.json')
    data = {}
    for name, digest in ORIGINAL_HASHES.items():
        no_symlinks(root / name)
        data[name] = (root / name).read_bytes()
        require(sha(data[name]) == digest, 'original-data identity mismatch: ' + name)
    original = data['newsh4.shp']
    require(sha(original) == proof['newsh4_sha256'], 'original RLE identity')
    tile_counts = {}
    for k, frame in enumerate(proof['records']):
        require(frame['base'] == IDS[k] and frame['type'] == ACTORS[k]
                and [part['id'] for part in frame['parts']] == [IDS[k] + v for v in OFFSETS],
                'original composite identity')
        support, indices = Image.new('L', (24, 28)), Image.new('L', (24, 28))
        for part, offset in zip(frame['parts'], POSITIONS):
            pos = struct.unpack_from('<H', original, 2 * (part['id'] - 1))[0]
            require(pos == part['offset'], 'RLE component offset mismatch')
            start, linear = pos, 0
            alpha, palette_indices = bytearray(168), bytearray(168)
            while original[pos] != 15:
                code = original[pos]
                pos += 1
                linear += code & 15
                count = code >> 4
                require(0 <= linear <= 168 and linear + count <= 168
                        and pos + count <= len(original), 'RLE exceeds 12x14/source')
                alpha[linear:linear + count] = b'\xff' * count
                palette_indices[linear:linear + count] = original[pos:pos + count]
                linear += count
                pos += count
            require(pos + 1 - start == part['encoded_bytes']
                    and alpha.count(255) == part['opaque_pixels']
                    and sha(original[start:pos + 1]) == part['encoded_sha256']
                    and sha(alpha) == part['opacity_sha256']
                    and sha(palette_indices) == part['indices_sha256']
                    and all(i for a, i in zip(alpha, palette_indices) if a), 'RLE source record mismatch')
            tile_counts[part['id']] = alpha.count(255)
            support.paste(Image.frombytes('L', (12, 14), bytes(alpha)), offset)
            indices.paste(Image.frombytes('L', (12, 14), bytes(palette_indices)), offset)
        require(list(support.getbbox()) == frame['alpha_bbox']
                and sha(support.tobytes()) == frame['opacity_sha256']
                and sha(indices.tobytes()) == frame['indices_sha256']
                and support.tobytes().count(255) == COUNTS[k]
                and support.tobytes() == logical[IDS[k]].tobytes(), 'original composite support mismatch')
    require(len(tile_counts) == 24 and sorted(t for t, count in tile_counts.items() if not count)
            == EMPTY_TILES, 'original empty source quadrants')
    reader_path = repo / 'src/episodes.c'
    no_symlinks(reader_path)
    reader_bytes = reader_path.read_bytes()
    require(sha(reader_bytes) == '640219b48d3081ee996ce66a66f61ad2fe185339fcfaf395808e02fcee0b29e0',
            'HDT reader source pin mismatch')
    reader = reader_bytes.decode()
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
    reuse, records = [], {}
    for record_id in list(range(851)) + list(range(1001, 1851)):
        record = {'id': record_id}
        for name, fmt, n in es:
            values = list(struct.unpack_from('<' + str(n) + fmt, hdt, pos))
            pos += n * struct.calcsize(fmt)
            record[name] = values[0] if n == 1 else values
        records[record_id] = record
        if record['shapebank'] == 2:
            selectors = collections.defaultdict(list)
            for index, base in enumerate(record['egraphic']):
                if 0 < base < 999:
                    selectors[base].append(f'egraphic[{index}]')
            if record['dani'] == 0 and 0 < record['dgr'] < 999:
                selectors[record['dgr']].append('direct damage dgr')
            for base, where in selectors.items():
                overlap = sorted({base + d for d in (OFFSETS if record['esize'] == 1 else [0])} & TILES)
                if overlap:
                    reuse.append({'record': record_id, 'base': base, 'selectors': where,
                                  'full_base_member': base in IDS,
                                  'shared_cells': [{'id': tile, 'source_opaque_pixels': tile_counts[tile]}
                                                   for tile in overlap]})
        if record_id in ACTORS:
            expected_record = dict(id=record_id, ani=1, tur=[0] * 3, freq=[0] * 3,
                xmove=0, ymove=0, xaccel=0, yaccel=0, xcaccel=0, ycaccel=-8,
                startx=0, starty=0, startxc=0, startyc=0, armor=0, esize=1,
                egraphic=[IDS[record_id - 468]] + [0] * 19, explosiontype=0, animate=0,
                shapebank=2, xrev=0, yrev=0, dgr=0, dlevel=-1, dani=0,
                elaunchfreq=0, elaunchtype=0, value=0, eenemydie=0)
            require(record == expected_record, 'original actor lifecycle record mismatch')
    require(len(records) == 1701 and reuse == audit['reuse'], 'all-HDT full-composite/boss reuse audit mismatch')
    require([row['record'] for row in reuse if row['full_base_member']] == ACTORS
            and [(r['record'], r['base']) for r in reuse if not r['full_base_member']] == [(56, 86), (61, 124)]
            and all(c['source_opaque_pixels'] == 0 for r in reuse if not r['full_base_member']
                    for c in r['shared_cells']), 'boss opaque dependency forbidden')
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
    expected_spawns = [dict(eventtime=5000, type=18, dat=ACTORS[IDS.index(base)], dat2=100 + x,
                           dat3=0, dat5=y - 24, dat6=0, dat4=0, index=848 + i)
                       for i, (base, x, y) in enumerate(PLACEMENTS)]
    require(spawns == expected_spawns, 'exact six event18 source-order spawns')
    require(not [event for event in events if event['type'] in [49, 50, 51, 52]],
            'custom bank spawn scope changed')
    require(not [e for e in events if 5000 <= e['eventtime'] < 5230
                 and e['type'] in [19, 20, 24, 25, 27, 31, 33, 39, 41, 45, 47, 49, 50, 51, 52, 55, 58, 59, 60, 68, 74, 85]],
            'unexpected source-lifetime mutator')
    return {'original_RLE_components': 24, 'nonempty_components': 20, 'empty_components': EMPTY_TILES,
            'original_alpha_cells': 1768, 'HDT_records_audited': len(records),
            'full_composite_users': ACTORS, 'excluded_boss_records': [56, 61],
            'boss_shared_cells_all_empty': True, 'level_events_decoded': len(events),
            'source_order_event18_spawns': len(spawns), 'source_lifecycle_records_verified': True,
            'preserve_recycled_scoreitem': True, 'original_RGB_art_inputs': False}


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
    manifest_path = repo / 'assets/hd/manifest.json'
    no_symlinks(manifest_path)
    logical = validate_art_and_bindings(repo, source, load(manifest_path))
    original_receipt = (verify_originals(repo, source, args.original_data, logical)
                        if args.original_data else None)
    subprocess.run([sys.executable, str(source / 'rebuild.py'), '--output', str(out)], check=True)
    expected = {row['path'][7:]: row for row in frozen['files'] if row['path'].startswith('output/')}
    require({path.name for path in out.iterdir()} == set(expected), 'rebuilt output inventory mismatch')
    for name, row in expected.items():
        path = out / name
        require(path.is_file() and not path.is_symlink() and path.stat().st_size == row['bytes']
                and sha(path.read_bytes()) == row['sha256'], 'rebuilt frozen output mismatch: ' + name)
    print(json.dumps({'status': 'PASS', 'source_manifest_sha256': FREEZE,
                      'source_FILES_sha256': FILES_SHA, 'source_files': 35,
                      'closed_frozen_import_inventory': True, 'generated_only_reproduction': True,
                      'exact_PNG_HDR1_pairs': 6, 'finite_default_packs': True,
                      'alpha_anchors_RGBA_FNV_verified': True, 'source_order_rejoin_verified': True,
                      'summed_opaque_cells': 1768, 'union_opaque_cells': 1635, 'ordered_overlaps': 133,
                      'original_data': original_receipt, 'game_runs': 0,
                      'runtime_acceptance': 'Not established by source validation.'}, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError, IndexError, struct.error, subprocess.SubprocessError) as exc:
        print('ERROR: ' + str(exc), file=sys.stderr)
        sys.exit(1)
