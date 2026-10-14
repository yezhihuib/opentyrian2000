#!/usr/bin/env python3
"""Pinned, portable front-Multi renderer units. Never launches the game.

Only bounded renderer fixtures are materialized, outside both repositories.
--art-pins is a reviewed JSON object mapping exactly the eight IDs to SHA256s.
--prepare-only extracts sources and prepares fixtures, but does not compile/run.
No approval is inferred by this script; the caller must obtain source/art review.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import subprocess

HERE = Path(__file__).resolve().parent
PIN = '7df8368acb90a73b170b1238b3161eefddb7a8e1'
CONTRACT_SHA = 'dc4bbc3ad75913f7701eb7e9e21546c84c28f53941880599e606cb6b7689a23c'
IDS = [121, 122, 163, 164, 201, 202, 279, 280]
OLD_IDS = [252, 253, 254, 19, 171, 20, 21, 58, 60, 62, 165, 103, 59,
           214, 215, 216, 217, 31, 32, 33, 225, 244, 226, 67, 70]
REF_IDS = IDS + [58, 59, 67, 70]
ENEMY_IDS = [77, 58, 182, 163, 1, 183, 164]
SHA = lambda b: hashlib.sha256(b).hexdigest()
CHANGES = [
    ('static Asset assets[532];', 'static Asset assets[524];'),
    (' /* Normal front Multi: eight static player heads; Christmas art stays original. */\n'
     ' if(!xmas&&bank.data==spriteSheet8.data&&layout==ENTITY_TILE) {\n'
     '  static const unsigned int multi_ids[8]={121,122,163,164,201,202,279,280};\n'
     '  for(int i=0;i<8;i++)if(index==multi_ids[i]){slot=524+i;role=8;break;}\n }\n', ''),
    (' /* Front Multi shadows retain their original indexed silhouettes and origin. */\n'
     ' if(bank.data==spriteSheet8.data&&layout==ENTITY_TILE&&style==MIRROR_SHADOW&&\n'
     '    (index==121||index==122||index==163||index==164||index==201||index==202||index==279||index==280))return false;\n', ''),
    ('/* Slots 507..509 are rear534; slots 510..521 are Data513. */',
     '/* Slots 507..521 are reserved for the separately staged rear and Data families. */'),
]
FUNCTIONS = ['complete_turret_group', 'restore_classic_rect', 'palette_rgb',
             'blend_rgba', 'cloud_shadow_rgba', 'cloud_asset', 'darken_rgba',
             'decode_tile', 'read_asset', 'explosion_asset_slot', 'get_asset',
             'talon_frame', 'enemy_filter_rgba', 'explosion_asset_blend_rgba',
             'green_background_snapshot', 'green_background_peak', 'green_head_composite',
             'draw_asset_filtered', 'draw_asset', 'render_mirror_entity',
             'enemy_energy_slot', 'enemy_energy_family_ready', 'render_mirror_enemy_shot',
             'render_mirror_pixel', 'render_mirror_entity_end', 'render_mirror_unsupported',
             'draw_vulcan_shadow', 'render_mirror_shadow_begin', 'render_mirror_shadow_end']


def extract(source, name):
    match = re.search(r'^[A-Za-z_][^\n;{}]*\b' + name + r'\([^;{}]*\)\s*\{', source, re.M)
    assert match, name
    end = source.index('{', match.start()) + 1
    depth = 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[match.start():end] + '\n'


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args])


def source_scope(candidate, baseline):
    assert git(baseline, 'rev-parse', 'HEAD').decode().strip() == PIN
    names = git(baseline, 'ls-tree', '-r', '--name-only', PIN, '--', 'src').decode().splitlines()
    names = [n for n in names if Path(n).suffix in {'.c', '.h', '.inc'}]
    for root in (candidate, baseline):
        assert {str(p.relative_to(root)) for p in (root / 'src').rglob('*')
                if p.is_file() and p.suffix in {'.c', '.h', '.inc'}} == set(names)
    sources = {label: {n: (root / n).read_bytes() for n in names}
               for label, root in [('baseline', baseline), ('candidate', candidate)]}
    for name in names:
        pinned = git(baseline, 'show', PIN + ':' + name)
        assert sources['baseline'][name] == pinned, 'Unpinned baseline ' + name
        restored = sources['candidate'][name]
        if name == 'src/render_mirror.c':
            text = restored.decode()
            for before, after in CHANGES:
                assert text.count(before) == 1, 'Missing/ambiguous inverse: ' + before
                text = text.replace(before, after)
            restored = text.encode()
        assert restored == pinned, 'Unexpected production change ' + name
    return sources, {'baseline_commit': PIN, 'production_files': len(names),
                     'semantic_deltas': 3, 'comment_only_deltas': 1,
                     'exact_inverse': True,
                     'sha256': {n: SHA(v) for n, v in sources['candidate'].items()}}


def decode(bank, index):
    # Independent linear-cell RLE oracle, rather than production's x/y decoder.
    pos = struct.unpack_from('<H', bank, 2 * (index - 1))[0]
    cell = 0
    colors, mask = bytearray(168), bytearray(168)
    while bank[pos] != 15:
        code = bank[pos]
        pos += 1
        cell += code & 15
        for _ in range(code >> 4):
            assert 0 <= cell < 168 and not mask[cell]
            colors[cell], mask[cell] = bank[pos], 255
            pos += 1
            cell += 1
    return colors + mask


def bank_from(path, stamp):
    raw = path.read_bytes()
    assert SHA(raw) == stamp, 'Unpinned original data ' + str(path)
    count = struct.unpack_from('<H', raw)[0]
    offsets = list(struct.unpack_from('<' + str(count) + 'I', raw, 2)) + [len(raw)]
    assert count >= 8 and offsets == sorted(offsets)
    return raw[offsets[7]:offsets[8]]


def header(index, density=8, role=8, anchor=0):
    return struct.pack('<4s4I2i', b'HDR1', role * 10000 + index, density, 12, 14, anchor, 0)


def reduced(raw, index):
    rgba = raw[28:]
    return header(index, 4) + b''.join(rgba[(2*y*96+2*x)*4:(2*y*96+2*x)*4+4]
                                      for y in range(56) for x in range(48))


def mutated(raw, index, kind):
    raw = bytearray(raw)
    fields = {'role': (4, 1110000+index), 'id': (4, 80000+IDS[(IDS.index(index)+1) % 8]),
              'density': (8, 4), 'width': (12, 11), 'height': (16, 13),
              'anchor-x': (20, 1), 'anchor-y': (24, 1)}
    if kind == 'magic': raw[0] = 0
    if kind in fields:
        offset, value = fields[kind]
        struct.pack_into('<I', raw, offset, value)
    if kind == 'short-header': raw = raw[:27]
    if kind == 'truncated': raw = raw[:-1]
    if kind == 'extra': raw += b'X'
    return raw


def prepare_variants(work, full):
    names, validity, densities = [], [], []
    def add(name, missing=(), mutation=None, fallback=()):
        folder = work / name
        folder.mkdir()
        valid = [int(index not in missing and (not mutation or index != mutation[0]) or index in fallback)
                 for index in IDS]
        density = [4 if index in fallback else 8 for index in IDS]
        for path in full.iterdir():
            # Symlinks reuse frozen/old bytes. Only mutated finite fixtures are new.
            index = next((i for i in IDS if path.name == f'bullet-{i}-8.hda'), None)
            if index in missing: continue
            if (mutation and index == mutation[0]) or (name == 'invalid8-valid4' and index in IDS):
                (folder/path.name).write_bytes(mutated(path.read_bytes(), index, mutation[1] if mutation and index == mutation[0] else 'magic'))
            else:
                (folder/path.name).symlink_to(path.resolve())
        for index in fallback:
            (folder/f'bullet-{index}-4.hda').write_bytes(reduced((full/f'bullet-{index}-8.hda').read_bytes(), index))
        names.append(name); validity.append(valid); densities.append(density)
    for index in IDS:
        add(f'missing-{index}', missing=[index])
        for kind in ['magic', 'role', 'id', 'density', 'width', 'height', 'anchor-x', 'anchor-y',
                     'short-header', 'truncated', 'extra']:
            add(f'{kind}-{index}', mutation=(index, kind))
        add(f'only4-{index}', missing=[index], fallback=[index])
        add(f'invalid8-valid4-{index}', mutation=(index, 'magic'), fallback=[index])
    add('missing-all', missing=IDS)
    add('only4', missing=IDS, fallback=IDS)
    add('invalid8-valid4', mutation=(IDS[0], 'magic'), fallback=IDS)
    def array(rows): return ','.join('{' + ','.join(map(str, row)) + '}' for row in rows)
    return ('static const char *variants[]={' + ','.join(map(json.dumps, names)) + '};\n'
            'static const int variant_valid[][8]={' + array(validity) + '};\n'
            'static const int variant_density[][8]={' + array(densities) + '};\n'), names


def prepare_vulcan_variants(work, full):
    names, head_valid, shadow_valid = [], [], []
    for member, index in enumerate([67, 70]):
        for kind in ['missing', 'invalid', 'only4', 'invalid8-valid4', 'payload']:
            name = f'vulcan-{kind}-{index}'
            folder = work/name; folder.mkdir()
            for path in full.iterdir():
                if path.name != f'bullet-{index}-8.hda':
                    (folder/path.name).symlink_to(path.resolve())
                elif kind in ['invalid', 'invalid8-valid4']:
                    (folder/path.name).write_bytes(b'invalid')
                elif kind == 'payload':
                    raw = bytearray(path.read_bytes()); raw[31] ^= 1
                    (folder/path.name).write_bytes(raw)
            if kind in ['only4', 'invalid8-valid4']:
                (folder/f'bullet-{index}-4.hda').write_bytes(reduced((full/f'bullet-{index}-8.hda').read_bytes(), index))
            names.append(name)
            head_valid.append([int(k != member or kind in ['only4', 'invalid8-valid4', 'payload']) for k in range(2)])
            shadow_valid.append([int(k != member) for k in range(2)])
    def array(rows): return ','.join('{' + ','.join(map(str, row)) + '}' for row in rows)
    return ('static const char *vulcan_variants[]={' + ','.join(map(json.dumps, names)) + '};\n'
            'static const int vulcan_head_valid[][2]={' + array(head_valid) + '};\n'
            'static const int vulcan_shadow_valid[][2]={' + array(shadow_valid) + '};\n'), names


def integrated_resources(candidate, baseline, manifest, art, pins):
    raw = (candidate/'assets/hd/manifest.json').read_bytes()
    current = json.loads(raw)
    restored = json.loads(raw)
    family = restored.pop('player_front_multi_eight_v1')
    assert family['ids'] == IDS and family['role'] == 8 and family['density'] == 8
    assert family['logical_size'] == [12, 14] and family['anchor'] == [0, 0]
    assert family['entries'] == [{'id': index, 'slot': 524+k, 'HDA_sha256': pins[index]}
                                 for k, index in enumerate(IDS)]
    actual = {}
    for index in IDS:
        assert pins[index] not in manifest['source_pngs']
        del restored['source_pngs'][pins[index]]
    for kind in ['preview', 'debug']:
        name = manifest['default_'+kind+'_pack']
        assert current['default_'+kind+'_pack'] == name
        assert manifest['packs'][name]['count'] == 532 and current['packs'][name]['count'] == 540
        for index in IDS:
            filename = f'bullet-{index}-8.hda'
            assert current['packs'][name]['files'][filename]['sha256'] == pins[index]
            path = candidate/'assets/hd/packs'/name/filename
            assert path.read_bytes() == art[index]
            assert not path.with_name(f'bullet-{index}-4.hda').exists()
            actual[str(path)] = pins[index]
            del restored['packs'][name]['files'][filename]
            restored['packs'][name]['count'] -= 1
        # Sparse checkout has only new resources. Any materialized old file must
        # still be exactly its pinned Git blob, including pre-existing unlisted files.
        for path in (candidate/'assets/hd/packs'/name).rglob('*'):
            if path.is_file() and str(path) not in actual:
                relative = str(path.relative_to(candidate))
                assert path.read_bytes() == git(baseline, 'show', PIN+':'+relative)
    assert restored == manifest, 'Manifest has unrelated changes'
    original_raw = git(baseline, 'show', PIN+':assets/hd/manifest.json')
    assert (json.dumps(restored, indent=2, ensure_ascii=False)+'\n').encode() == original_raw
    return raw, actual


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['candidate', 'baseline', 'contract', 'art-dir', 'art-pins', 'normal-data', 'xmas-data', 'out']:
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    for key, value in vars(args).items():
        if isinstance(value, Path): setattr(args, key, value.resolve())
    assert not args.out.exists(), 'Use a fresh output directory'
    assert all(root != args.out and root not in args.out.parents
               for root in [args.candidate, args.baseline, args.art_dir])
    contract_raw = args.contract.read_bytes()
    assert SHA(contract_raw) == CONTRACT_SHA
    contract = json.loads(contract_raw)
    assert contract['baseline'] == PIN and contract['family']['ids'] == IDS
    pins_raw = args.art_pins.read_bytes()
    pins = {int(k): v for k, v in json.loads(pins_raw).items()}
    assert set(pins) == set(IDS) and all(re.fullmatch('[0-9a-f]{64}', s) for s in pins.values())
    sources, scope = source_scope(args.candidate, args.baseline)
    banks = [bank_from(args.normal_data, contract['data_sha256']['tyrian.shp']),
             bank_from(args.xmas_data, contract['data_sha256']['tyrianc.shp'])]
    art = {}
    for index in IDS:
        path = args.art_dir / f'bullet-{index}-8.hda'
        raw = path.read_bytes()
        assert SHA(raw) == pins[index] and raw[:28] == header(index) and len(raw) == 43036
        art[index] = raw
    manifest = json.loads(git(args.baseline, 'show', PIN + ':assets/hd/manifest.json'))
    manifest_raw, integrated_pins = integrated_resources(args.candidate, args.baseline, manifest, art, pins)
    harness = {p.name: p.read_bytes() for p in [Path(__file__), Path(__file__).with_suffix('.c')]}
    args.out.mkdir(parents=True)
    work = args.out/'fixtures'; work.mkdir()
    (work/'bank.bin').write_bytes(banks[0]); (work/'xmas-bank.bin').write_bytes(banks[1])
    pack_paths, resource_pins, reference = {}, {}, None
    for kind in ['preview', 'debug']:
        name = manifest['default_' + kind + '_pack']
        assert name == contract['packs'][kind]['name']
        old = work/(kind+'-baseline'); old.mkdir()
        full = work/(kind+'-candidate'); full.mkdir()
        raw_assets = {}
        for filename in ([f'bullet-{i}-8.hda' for i in OLD_IDS] +
                         [f'enemy-energy-{i}-8.hda' for i in ENEMY_IDS]):
            raw = git(args.baseline, 'show', PIN + ':assets/hd/packs/' + name + '/' + filename)
            assert SHA(raw) == manifest['packs'][name]['files'][filename]['sha256']
            (old/filename).write_bytes(raw); (full/filename).symlink_to(old/filename)
            raw_assets[filename] = raw
        for index in IDS:
            filename = f'bullet-{index}-8.hda'
            assert filename not in manifest['packs'][name]['files']
            (full/filename).symlink_to(args.candidate/'assets/hd/packs'/name/filename)
            raw_assets[filename] = art[index]
        for index in REF_IDS:
            raw = raw_assets[f'bullet-{index}-8.hda']
            assert raw[:28] == header(index, anchor=-1 if index == 59 else 0) and len(raw) == 43036
        ref = b''.join(bytes(decode(bank, index)) + raw_assets[f'bullet-{index}-8.hda'][28:]
                       for bank in banks for index in REF_IDS)
        ref += b''.join(bytes(decode(bank, index)) + raw_assets[f'enemy-energy-{index}-8.hda'][28:]
                        for bank in banks for index in [163, 164])
        if reference is None: reference = ref
        assert reference == ref, 'Default pack bounded resources differ'
        resource_pins[kind] = {name: SHA(raw) for name, raw in raw_assets.items()}
        pack_paths[kind] = {'baseline': old, 'candidate': full}
    (work/'reference.bin').write_bytes(reference)
    variants_inc, variants = prepare_variants(work, pack_paths['preview']['candidate'])
    vulcan_inc, vulcan_variants = prepare_vulcan_variants(work, pack_paths['preview']['candidate'])
    variants_inc += vulcan_inc
    reports = {}
    types = [r'typedef struct \{\s*bool initialized,valid;.*?\} Asset;',
             r'typedef struct \{\s*bool valid;\s*const Uint8 \*bank_data;.*?\} TalonBank;',
             r'static Asset assets\[\d+\];', r'static Asset talon_frames\[13\];',
             r'static bool enemy_energy_checked,enemy_energy_valid;', r'enum \{ ASSET_NEWSH2=.*?\};',
             r'typedef struct \{\s*bool live,entered;\s*SDL_Surface \*surface;.*?\} VulcanShadowCall;',
             r'static VulcanShadowCall vulcan_shadow;',
             r'static struct \{const Uint8 \*rgba;char path\[1024\];\} vulcan_shadow_resource\[2\];']
    for label in ['baseline', 'candidate']:
        directory = args.out/label; directory.mkdir()
        src = sources[label]; renderer = src['src/render_mirror.c'].decode()
        names = FUNCTIONS + re.findall(r'^static [^\n;{}]*\b(vulcan_shadow_[a-z_]+)\([^;{}]*\)\s*\{', renderer, re.M)
        helpers = {name: extract(renderer, name) for name in names}
        declarations = []
        for pattern in types:
            found = re.search(pattern, renderer, re.S)
            assert found, pattern
            declarations.append(found.group())
        (directory/'types.inc').write_text('\n'.join(declarations))
        prototypes = '\n'.join(s[:s.index('{')].strip() + ';' for s in helpers.values())
        (directory/'functions.inc').write_text(prototypes + '\n' + '\n'.join(helpers.values()))
        for filename, source, functions in [
            ('blitters.inc', 'src/sprite.c', ['blit_sprite2', 'blit_sprite2_darken']),
            ('wrappers.inc', 'src/entity_draw.c', ['draw_entity_sprite2', 'draw_enemy_shot_sprite2'])]:
            extracted = {n: extract(src[source].decode(), n) for n in functions}
            helpers.update(extracted); (directory/filename).write_text(''.join(extracted.values()))
        (directory/'variants.inc').write_text(variants_inc)
        reports[label] = {'function_sha256': {n: SHA(s.encode()) for n, s in helpers.items()}, 'builds': {}}
        if args.prepare_only: continue
        for config, flags in [('optimized', ['-O2']),
                              ('sanitized', ['-O1', '-g', '-fsanitize=address,undefined',
                                             '-fno-omit-frame-pointer', '-fno-pie', '-no-pie'])]:
            binary = directory/('test-' + config)
            command = [os.environ.get('CC', 'cc'), '-std=c99', '-Wall', '-Wextra', '-Werror',
                       '-Wno-misleading-indentation', *flags, '-DBASELINE=' + str(int(label == 'baseline')),
                       '-I' + str(directory), str(HERE/'test-front-multi-binding.c'), '-o', str(binary)]
            result = subprocess.run(command, capture_output=True, text=True)
            (directory/(config+'-compile.log')).write_text(result.stdout+result.stderr)
            if result.returncode: print(result.stderr)
            result.check_returncode()
            runs = {}
            env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',
                       UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
            for kind in ['preview', 'debug']:
                result = subprocess.run([str(binary), str(pack_paths[kind][label]), str(work)],
                                        env=env, capture_output=True, text=True, timeout=480)
                (directory/(config+'-'+kind+'.log')).write_text(result.stdout+result.stderr)
                print(label+'/'+config+'/'+kind+': '+result.stdout+result.stderr, flush=True)
                result.check_returncode(); runs[kind] = json.loads(result.stdout)
            reports[label]['builds'][config] = {'command': command, 'runs': runs}
    if not args.prepare_only:
        for config in ['optimized', 'sanitized']:
            for kind in ['preview', 'debug']:
                assert (reports['baseline']['builds'][config]['runs'][kind]['shadow_fingerprint'] ==
                        reports['candidate']['builds'][config]['runs'][kind]['shadow_fingerprint'])
    for label, root in [('baseline', args.baseline), ('candidate', args.candidate)]:
        assert all((root/name).read_bytes() == raw for name, raw in sources[label].items())
    assert all((HERE/name).read_bytes() == raw for name, raw in harness.items())
    assert all((args.art_dir/f'bullet-{index}-8.hda').read_bytes() == raw for index, raw in art.items())
    assert (args.candidate/'assets/hd/manifest.json').read_bytes() == manifest_raw
    assert all(SHA(Path(name).read_bytes()) == stamp for name, stamp in integrated_pins.items())
    report = {'status': 'PREPARED_NOT_EXECUTED' if args.prepare_only else 'PASS',
              'game_runs': 0, 'captures': 0, 'source_scope': scope, 'art_pins_sha256': SHA(pins_raw),
              'contract_sha256': SHA(contract_raw), 'art_sha256': pins, 'bounded_resource_sha256': resource_pins,
              'bank_sha256': list(map(SHA, banks)), 'variants': variants, 'vulcan_variants': vulcan_variants, 'results': reports,
              'manifest_exact_inverse': True, 'integrated_resource_sha256': integrated_pins,
              'harness_sha256': {n: SHA(raw) for n, raw in harness.items()},
              'sanitizers': [] if args.prepare_only else ['ASan', 'UBSan'], 'leak_detection': False,
              'limitations': ['Extracted-source unit only: no engine, screenshot, gameplay or aesthetic acceptance.',
                             'Only bounded default-pack resources materialized; full-pack manifest/physical inventory is separate.',
                             'Font/material integration paths are no-op or fail-if-entered stubs; real renderer/loader/RLE/shadow helpers execute.',
                             'LeakSanitizer disabled for the ptrace executor.']}
    (args.out/'result.json').write_text(json.dumps(report, indent=2)+'\n')
    print('Report:', args.out/'result.json')


if __name__ == '__main__': main()
