#!/usr/bin/env python3
"""Validate and reproduce the frozen six 12x14 type3 sprite sources.

Only generated artwork and technical masks supply pixels. Optional original game
files are read-only structural evidence. This does not run a game or capture any
native output, and does not establish runtime, type16, boss or ram acceptance.
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

IDS = [171, 190, 209, 228, 247, 266]
COUNTS = [98, 82, 82, 74, 82, 82]
CYCLE = [base for base in IDS for _ in range(2)]
KEYS = {1010000 + base for base in IDS}
SOURCE = 'assets/hd/artwork/type3-small-six-v1'
FREEZE = '5012962c54ab3fd0b22cc8a2534fddee272704fa73447e267ffeb4938f787c33'
CONTRACT_SHA = '9c8934790afb66ba2431be75ba68b20a22ad58b522c8db85661a849288cd8686'
RECEIPT_SHA = '579b6e46b7187912658326ee13d9a773dd6175f4a3063cbeabacc9c99e50147d'
DEFAULTS = ['packed-talon13-foundation-type10-death-effects-white-smoke-shield-green-v2-head-v1-test',
            'packed-blue-four-foundation-type10-death-effects-white-smoke-shield-green-v2-head-v1-test']
ORIGINAL_HASHES = {
    'newsh2.shp': '8773ebcae4be992ecfbb476c0797b0bef4d43faa4c99449890bfaa28c8d9cbcc',
    'tyrian.hdt': 'fde8506326e7bb0916b38c362e33bf8a8a5affa561206c021af7f65b4a17745b',
    'tyrian1.lvl': '54cbb00b57b84aa992a70cfcb170cb1edeb59507873723630d60080ba8351352',
}
READERS = {'src/episodes.c': '640219b48d3081ee996ce66a66f61ad2fe185339fcfaf395808e02fcee0b29e0',
           'src/tyrian2.c': '0a042621d599fdba15f89012c9bb1007327cd6f5df0e0a41865ea61c08856d02'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON key: ' + key)
        result[key] = value
    return result


def read_regular(path):
    no_symlinks(path)
    require(path.is_file(), 'regular file required: ' + str(path))
    return path.read_bytes()


def load(path):
    return json.loads(read_regular(path).decode(), object_pairs_hook=unique_object)


def exact_json(actual, expected):
    # JSON booleans/floats must not masquerade as integer header/scope fields.
    return json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True)


def no_symlinks(path):
    require(not any(p.is_symlink() for p in [path, *path.parents]),
            'symlink path forbidden: ' + str(path))


def safe_relative(value):
    require(isinstance(value, str), 'unsafe manifest path type')
    path = PurePosixPath(value)
    require(value and value != '.' and not path.is_absolute() and '..' not in path.parts
            and path.as_posix() == value and '\\' not in value and '\0' not in value,
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


def original_root(value, repo):
    given = value.expanduser()
    require(given.is_absolute(), 'original data must be absolute')
    require('..' not in given.parts, 'original data traversal forbidden')
    no_symlinks(given)
    root = given.resolve()
    require(root.is_dir(), 'original data directory missing')
    require(root != repo and repo not in root.parents and root not in repo.parents,
            'original data must stay outside repository')
    return root


def inventory(source):
    no_symlinks(source)
    nodes = list(source.rglob('*'))
    require(all(not q.is_symlink() and (q.is_file() or q.is_dir()) for q in nodes),
            'source symlink or special file forbidden')
    raw = (source / 'inventory.json').read_bytes()
    require(sha(raw) == FREEZE, 'source inventory freeze mismatch')
    frozen = load(source / 'inventory.json')
    names = set(frozen['inputs'])
    expected_inputs = {'README.md', 'contract.json', 'rebuild.py',
        'proof/REPORT.md', 'proof/alpha-verification.json', 'proof/art-input-contract.json',
        'proof/source-record-proof.json', 'proof/verification.json',
        'sources/generated-six-frame.png', 'sources/initial-prompt.txt', 'sources/prompt.txt'}
    expected_inputs.update(f'masks/alpha-{base}.png' for base in IDS)
    require(names == expected_inputs and len(names) == 17, 'source input inventory scope')
    require([row['base'] for row in frozen['outputs']] == IDS, 'source output inventory scope')
    expected_outputs = {f'output/enemy-newsh2-{base}-8.{ext}': row[ext.upper() + '_SHA256']
                        for base, row in zip(IDS, frozen['outputs']) for ext in ['hda', 'png']}
    expected = dict(frozen['inputs'], **expected_outputs,
                    **{'inventory.json': FREEZE, 'output/rebuild-receipt.json': RECEIPT_SHA})
    for name in expected:
        safe_relative(name)
    require({q.relative_to(source).as_posix() for q in nodes if q.is_file()} == set(expected),
            'source inventory differs: missing or unlisted file')
    expected_dirs = {str(p) for name in expected for p in PurePosixPath(name).parents if str(p) != '.'}
    require({q.relative_to(source).as_posix() for q in nodes if q.is_dir()} == expected_dirs,
            'source inventory differs: unlisted directory')
    for name, digest in expected.items():
        require(sha((source / name).read_bytes()) == digest, 'source file mismatch: ' + name)
    require(frozen['inputs']['proof/art-input-contract.json'] == CONTRACT_SHA,
            'art input contract freeze mismatch')
    receipt = load(source / 'output/rebuild-receipt.json')
    require(receipt == {'pass': True, 'outputs': frozen['outputs']}, 'frozen rebuild receipt mismatch')
    return frozen


def fnv1a(data):
    stamp = 0xcbf29ce484222325
    for value in data:
        stamp = ((stamp ^ value) * 0x100000001b3) & 0xffffffffffffffff
    return f'{stamp:016x}'


def family_name(name, png=False):
    pattern = r'enemy-newsh2-(\d+)-.*\.png' if png else r'enemy-newsh2-(\d+)-(\d+)\.hda'
    match = re.fullmatch(pattern, name)
    return match is not None and int(match[1]) in IDS


def validate_art_and_bindings(repo, source, manifest, frozen):
    family = manifest['type3_small_six_v1']
    expected_family = {
        'schema': 'type3-small-six-v1', 'source': SOURCE, 'source_inventory_sha256': FREEZE,
        'source_contract_sha256': CONTRACT_SHA, 'density': 8, 'logical_size': [12, 14],
        'anchor': [0, 0], 'ids': IDS, 'slots': list(range(416, 422)), 'bank_id': 1, 'bank_role': 101,
        'runtime_components': [0], 'source_cycle': CYCLE, 'reused_types': [3, 16],
        'opaque_logical_cells': 500, 'original_alpha_exact': True,
        'fallback': 'All six approved members required before any replacement; 8x-only selected-pack cached fallback is local to this family',
    }
    require(exact_json({key: value for key, value in family.items() if key not in ['entries', 'runtime_status']},
                       expected_family), 'family metadata mismatch')
    require(len(family['entries']) == 6, 'exact six entries required')
    contract = load(source / 'contract.json')
    for key, value in {'schema': 'formal-type3-small-six-v1', 'bank': 'newsh2.shp', 'bank_id': 1,
        'asset_namespace': 101, 'ids': IDS, 'logical_size': [12, 14], 'pixel_size': [96, 112],
        'density': 8, 'anchor': [0, 0], 'draw_part': 0, 'source_cycle': CYCLE,
        'reused_records': [3, 16], 'technical_matte_RGB': [8, 6, 2]}.items():
        require(contract[key] == value, 'source contract scope mismatch: ' + key)
    audit = load(source / 'proof/art-input-contract.json')
    require(audit['shape_bank'] == 1 and audit['renderer_role'] == 101
            and audit['frame_ids'] == IDS and audit['source_egraphic_order'] == CYCLE
            and audit['logical_size'] == [12, 14] and audit['anchor'] == [0, 0]
            and audit['alpha_unique_shapes'] == 3 and audit['reuse']['direct_base_users'] == [3, 16]
            and audit['reuse']['any_source_tile_overlap_users'] == [3, 16]
            and audit['reuse']['type16_in_first_level_closure'] is False, 'source proof scope mismatch')
    require([manifest['default_preview_pack'], manifest['default_debug_pack']] == DEFAULTS,
            'two established default packs required')
    for pack_name, pack in manifest['packs'].items():
        require(len(safe_relative(pack_name).parts) == 1, 'unsafe pack name')
        for name, row in pack['files'].items():
            require(len(safe_relative(name).parts) == 1, 'unsafe pack filename')
            safe_relative(row['source_png'])
    logical, canonical_paths, outputs = {}, set(), []
    for k, (base, count, row, entry) in enumerate(zip(IDS, COUNTS, frozen['outputs'], family['entries'])):
        name = f'enemy-newsh2-{base}-8'
        raw = (source / 'output' / (name + '.hda')).read_bytes()
        png = (source / 'output' / (name + '.png')).read_bytes()
        header = [1010000 + base, 8, 12, 14, 0, 0]
        require(len(raw) == 43036 and raw[:28] == b'HDR1' + struct.pack('<6I', *header),
                'HDR1 dimensions/anchor/key/EOF mismatch')
        require(sha(raw) == row['HDA_SHA256'] and sha(raw[28:]) == row['RGBA_SHA256']
                and sha(png) == row['PNG_SHA256'], 'frozen PNG/RGBA/HDA hashes mismatch')
        with Image.open(source / 'output' / (name + '.png')) as im:
            require(im.mode == 'RGBA' and im.size == (96, 112) and im.tobytes() == raw[28:],
                    'PNG/RGBA/HDR1 disagreement')
            alpha = im.getchannel('A').tobytes()
        with Image.open(source / f'masks/alpha-{base}.png') as mask:
            require(mask.mode == 'L' and mask.size == (12, 14) and set(mask.tobytes()) == {0, 255}
                    and mask.tobytes().count(255) == count, 'logical support mask mismatch')
            logical[base] = mask.copy()
        proof = audit['records'][k]
        require(proof['id'] == base and sha(logical[base].tobytes()) == proof['alpha_sha256']
                and proof['opaque_pixels'] == count and list(logical[base].getbbox()) == row['source_bbox']
                == proof['alpha_bbox_xyxy'], 'source alpha proof mismatch')
        require(alpha == logical[base].resize((96, 112), Image.Resampling.NEAREST).tobytes()
                and alpha.count(255) == count * 64, 'piece alpha support mismatch')
        # Complete RGBA identity above deliberately includes the nonzero technical
        # matte under transparency. Normalizing transparent RGB would corrupt it.
        transparent = sum(raw[j + 3] == 0 and raw[j:j + 3] != b'\0\0\0'
                          for j in range(28, len(raw), 4))
        require(transparent == (168 - count) * 64, 'frozen transparent matte mismatch')
        require(exact_json(entry, {'id': base, 'slot': 416 + k, 'HDA_sha256': sha(raw),
                                  'RGBA_FNV1a64': fnv1a(raw[28:])}), 'entry/FNV binding mismatch')
        canonical = f'assets/hd/source/{name}-{sha(raw)[:12]}.png'
        canonical_paths.add(canonical)
        no_symlinks(repo / canonical)
        require(read_regular(repo / canonical) == png, 'canonical PNG mismatch: ' + canonical)
        require(manifest['source_pngs'][sha(raw)] == {'path': canonical, 'sha256': sha(png),
                'RGBA_sha256': sha(raw[28:])}, 'source PNG index mismatch')
        for pack_name in DEFAULTS:
            packed = manifest['packs'][pack_name]['files'][name + '.hda']
            require(exact_json(packed, {'header_u32': header, 'sha256': sha(raw), 'source_png': canonical,
                                      'source_png_sha256': sha(png)}), 'packed metadata mismatch')
            path = repo / 'assets/hd/packs' / pack_name / (name + '.hda')
            no_symlinks(path)
            require(read_regular(path) == raw, 'packed HDR1 mismatch: ' + str(path))
        outputs.append(dict(row, RGBA_FNV1a64=fnv1a(raw[28:]), opaque_logical_cells=count))
    require(len({mask.tobytes() for mask in logical.values()}) == 3, 'three unique alpha masks required')
    hashes = {row['HDA_SHA256'] for row in frozen['outputs']}
    png_hashes = {row['PNG_SHA256'] for row in frozen['outputs']}
    rgba_hashes = {row['RGBA_SHA256'] for row in frozen['outputs']}
    indexed = set()
    for digest, entry in manifest['source_pngs'].items():
        safe_relative(entry['path'])
        if (digest in hashes or entry['sha256'] in png_hashes or entry['RGBA_sha256'] in rgba_hashes
                or family_name(PurePosixPath(entry['path']).name, png=True)):
            indexed.add(digest)
    require(indexed == hashes, 'widened source PNG index')
    allowed = {f'enemy-newsh2-{base}-8.hda' for base in IDS}
    for pack_name, pack in manifest['packs'].items():
        require(pack['count'] == len(pack['files']), 'pack count mismatch')
        relevant = {name for name, entry in pack['files'].items()
                    if family_name(name) or entry['header_u32'][0] in KEYS}
        require(relevant == (allowed if pack_name in DEFAULTS else set()), 'widened pack alias or density')
    pack_root, actual = repo / 'assets/hd/packs', set()
    no_symlinks(pack_root)
    for path in pack_root.rglob('*'):
        require(not path.is_symlink() and (path.is_file() or path.is_dir()),
                'pack inventory symlink or special file forbidden')
        if path.is_file():
            with path.open('rb') as handle:
                header = handle.read(8)
            key_matches = len(header) == 8 and header[:4] == b'HDR1' and struct.unpack('<I', header[4:])[0] in KEYS
            if family_name(path.name) or key_matches:
                actual.add(path.relative_to(pack_root).as_posix())
    require(actual == {f'{pack}/{name}' for pack in DEFAULTS for name in allowed},
            'widened on-disk pack inventory')
    source_root, actual_pngs = repo / 'assets/hd/source', set()
    no_symlinks(source_root)
    for path in source_root.rglob('*'):
        require(not path.is_symlink() and (path.is_file() or path.is_dir()),
                'canonical source symlink or special file forbidden')
        if family_name(path.name, png=True):
            require(path.is_file(), 'canonical PNG must be regular file')
            actual_pngs.add(path.relative_to(repo).as_posix())
    require(actual_pngs == canonical_paths, 'widened canonical PNG inventory')
    return logical, outputs


def verify_originals(repo, source, root, logical):
    data = {}
    for name, digest in ORIGINAL_HASHES.items():
        path = root / name
        no_symlinks(path)
        require(path.is_file(), 'original data must be regular file: ' + name)
        data[name] = path.read_bytes()
        require(sha(data[name]) == digest, 'original-data identity mismatch: ' + name)
    audit = load(source / 'proof/art-input-contract.json')
    original = data['newsh2.shp']
    for base, proof in zip(IDS, audit['records']):
        pos = struct.unpack_from('<H', original, 2 * (base - 1))[0]
        require(pos == proof['offset'], 'RLE offset mismatch')
        start, linear = pos, 0
        alpha, indices = bytearray(168), bytearray(168)
        while True:
            require(pos < len(original), 'RLE missing terminator')
            code = original[pos]
            pos += 1
            if code == 15:
                break
            linear += code & 15
            count = code >> 4
            require(0 <= linear <= 168 and linear + count <= 168 and pos + count <= len(original),
                    'RLE exceeds 12x14/source')
            alpha[linear:linear + count] = b'\xff' * count
            indices[linear:linear + count] = original[pos:pos + count]
            linear += count
            pos += count
        require(pos - start == proof['record_bytes'] and sha(original[start:pos]) == proof['source_record_sha256']
                and sha(alpha) == proof['alpha_sha256'] and sha(indices) == proof['index_sha256']
                and alpha.count(255) == proof['opaque_pixels'] and bytes(alpha) == logical[base].tobytes()
                and all(index for a, index in zip(alpha, indices) if a), 'RLE source record mismatch')
    for name, digest in READERS.items():
        no_symlinks(repo / name)
        require(sha(read_regular(repo / name)) == digest, 'source reader pin mismatch: ' + name)
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
    records, bases, overlaps, launches, drops, dormant = {}, [], [], [], [], []
    for record_id in list(range(851)) + list(range(1001, 1851)):
        record = {'id': record_id}
        for name, fmt, n in es:
            values = list(struct.unpack_from('<' + str(n) + fmt, hdt, pos))
            pos += n * struct.calcsize(fmt)
            record[name] = values[0] if n == 1 else values
        records[record_id] = record
        if record['shapebank'] == 1:
            selectors = {base for base in record['egraphic'] if 0 < base < 999}
            if record['dani'] == 0 and 0 < record['dgr'] < 999:
                selectors.add(record['dgr'])
            matches = sorted(selectors & set(IDS))
            tiles = {base + offset for base in selectors
                     for offset in ([0, 1, 19, 20] if record['esize'] == 1 else [0])}
            shared = sorted(tiles & set(IDS))
            if matches:
                bases.append({'id': record_id, 'matches': matches, 'record': record})
            if shared:
                overlaps.append({'id': record_id, 'matching_source_tiles': shared, 'base_matches': matches})
        launch = record['elaunchtype'] if record_id > 1000 else record['elaunchtype'] % 1000
        if record['elaunchfreq'] == 0 and launch in [3, 16]:
            dormant.append({'record': record_id, 'target': launch, 'frequency': 0})
        if record['elaunchfreq'] > 0 and launch in [3, 16]:
            launches.append({'id': record_id, 'target': launch, 'record': record})
        if record['eenemydie'] in [3, 16]:
            drops.append({'id': record_id, 'target': record['eenemydie'], 'record': record})
    proof = load(source / 'proof/source-record-proof.json')
    require(len(records) == proof['record_count'] == 1701 and bases == proof['base_users']
            and overlaps == proof['tile_overlap_users'] and launches == proof['launch_users']
            and drops == proof['drop_users'] == [], 'all-HDT reuse/lifecycle audit mismatch')
    require([row['id'] for row in bases] == [3, 16] and [row['id'] for row in overlaps] == [3, 16]
            and [(r['id'], r['target'], r['record']['elaunchfreq']) for r in launches] == [(53, 3, 90)],
            'finite type3/type16 reuse or boss53 launch mismatch')
    require(dormant == [{'record': 803, 'target': 3, 'frequency': 0}],
            'dormant launch selector mismatch')
    level = data['tyrian1.lvl']
    n = struct.unpack_from('<H', level)[0]
    pos = struct.unpack_from('<' + str(n) + 'i', level, 2)[16] + 8
    n = struct.unpack_from('<H', level, pos)[0]
    pos += 2 + 2 * n
    n = struct.unpack_from('<H', level, pos)[0]
    pos += 2
    fields = ['eventtime', 'type', 'dat', 'dat2', 'dat3', 'dat5', 'dat6', 'dat4']
    events = [dict(zip(fields, struct.unpack_from('<HBhhbbbB', level, pos + i * 11)), index=i + 1)
              for i in range(n)]
    require(n == 1010 and not [e for e in events if e['type'] in [49, 50, 51, 52]],
            'first-level event/custom sprite scope mismatch')
    spawn_types = [6, 7, 10, 12, 15, 17, 18, 23, 32, 56]
    for target, name in [(3, 'first_level_type3_spawns'), (53, 'first_level_boss_launcher_spawns')]:
        expected = [{k: v for k, v in row.items() if k != 'scalar_predicted_tick'} for row in proof[name]]
        require([e for e in events if e['type'] in spawn_types and e['dat'] == target] == expected,
                'first-level spawn source mismatch')
    # Conservative closure includes every scheduled spawn (four records for event
    # 12), event-assigned drops/launches/replacements, then all table drop/launch
    # edges regardless of runtime availability. No time/visibility is simulated.
    closure = {e['dat'] + off for e in events if e['type'] in spawn_types
               for off in (range(4) if e['type'] == 12 else [0])}
    closure.update(e['dat'] for e in events if e['type'] in [33, 45, 58, 59, 68])
    closure.discard(0)
    while True:
        expanded = set(closure)
        for record_id in closure:
            require(record_id in records, 'closure references unloaded enemy record')
            r = records[record_id]
            launch = r['elaunchtype'] if record_id > 1000 else r['elaunchtype'] % 1000
            expanded.update(value for value in [launch if r['elaunchfreq'] else 0, r['eenemydie']] if value)
        if expanded == closure:
            break
        closure = expanded
    require(3 in closure and 53 in closure and 16 not in closure
            and proof['first_level_type16_present'] is False, 'type16 first-level closure mismatch')
    return {'original_RLE_sprites': 6, 'opaque_logical_cells': COUNTS, 'unique_masks': 3,
            'HDT_records_audited': len(records), 'direct_and_composite_overlap_users': [3, 16],
            'source_lifecycle_records_verified': True, 'default_death_drop_users': [],
            'launcher': {'record': 53, 'target': 3, 'frequency': 90},
            'dormant_launch_selectors': dormant,
            'first_level_events_decoded': len(events), 'conservative_first_level_closure': sorted(closure),
            'type16_in_first_level_closure': False, 'original_RGB_art_inputs': False,
            'runtime_or_predicted_tick_validation': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--original-data', type=Path)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    out = safe_output(args.output, repo)
    root = original_root(args.original_data, repo) if args.original_data else None
    if root:
        require(out != root and root not in out.parents and out not in root.parents,
                'output must not overlap original data')
    source = repo / SOURCE
    frozen = inventory(source)
    manifest_path = repo / 'assets/hd/manifest.json'
    no_symlinks(manifest_path)
    logical, outputs = validate_art_and_bindings(repo, source, load(manifest_path), frozen)
    original_receipt = verify_originals(repo, source, root, logical) if root else None
    # Execute only the SHA-pinned, generated-only frozen recipe after validating
    # every input, binding and output path. Its positional CLI is preserved.
    result = subprocess.run([sys.executable, str(source / 'rebuild.py'), str(out)],
                            capture_output=True, text=True, timeout=90)
    require(result.returncode == 0, 'frozen rebuild failed: ' + result.stdout + result.stderr)
    expected = {p.name: p.read_bytes() for p in (source / 'output').iterdir()}
    require({p.name for p in out.iterdir()} == set(expected), 'rebuilt output inventory mismatch')
    for name, raw in expected.items():
        path = out / name
        require(not path.is_symlink() and path.is_file() and path.read_bytes() == raw,
                'rebuilt frozen output mismatch: ' + name)
    print(json.dumps({'status': 'PASS', 'source_inventory_sha256': FREEZE,
        'source_contract_sha256': CONTRACT_SHA, 'frozen_files': 31, 'frozen_inputs': 17,
        'closed_frozen_inventory': True, 'generated_only_reproduction': True,
        'exact_PNG_RGBA_HDR1_pairs': 6, 'finite_two_default_packs': True,
        'alpha_anchors_RGBA_FNV_verified': True, 'transparent_RGB_preserved_exactly': True,
        'opaque_logical_cells': COUNTS, 'unique_alpha_masks': 3, 'outputs': outputs,
        'original_data': original_receipt, 'game_runs': 0, 'captures': 0, 'native_output': False,
        'runtime_acceptance': 'Not established; type16, boss-spawn, ram and full-level excluded.'}, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError, IndexError, struct.error, subprocess.SubprocessError) as exc:
        print('ERROR: ' + str(exc), file=sys.stderr)
        sys.exit(1)
