#!/usr/bin/env python3
"""Pinned, standalone front-Multi smooth-shadow source units. Never launches the game.

Supply your own original tyrian.shp and tyrianc.shp explicitly. Only bounded
bank8 and test resources are prepared in a fresh external output directory;
no original data files, full packs or runtime captures are copied into the repo.
--prepare-only extracts fixtures/functions without compiling or executing tests.
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
BASE = '043b9536edb819877bb9b6a08a0780fc6e07a16d'
RENDERER_SHA = 'cc54f1096e118c4a8388e6a9c4e0db4347cfc713621e94fa4b5566c8ed7fe0df'
IDS = [67, 70, 121, 122, 163, 164, 201, 202, 279, 280]
CONTROLS = [58, 59, 225, 244, 226]
OLD_IDS = [252,253,254,19,171,20,21,58,60,62,165,103,59,214,215,216,217,31,32,33,225,244,226,67,70]
ENEMIES = [77,58,182,163,1,183,164]
DATA_PINS = ['80cae98e073be6d7f710495920b71497bb23f108ea6631d6faf352c4729474f0',
             'e980f02021395d39b86491acdc2ecd6dd47ea2a9f859fe3928f81b75e244fd7d']
BANK_PINS = ['9bba1e94d38df61f152412c226bfd6df235e42027c9143c5961d4a5add853a68',
             '26eb4fe91672bcef4bc88d7162d5f531144ad98eba64f5c0314e35fec85241e4']
FUNCTIONS = ['complete_turret_group', 'restore_classic_rect', 'palette_rgb', 'blend_rgba', 'cloud_shadow_rgba', 'cloud_asset', 'darken_rgba', 'decode_tile', 'read_asset', 'explosion_asset_slot', 'get_asset', 'talon_frame', 'enemy_filter_rgba', 'explosion_asset_blend_rgba', 'green_background_snapshot', 'green_background_peak', 'green_head_composite', 'draw_asset_filtered', 'draw_asset', 'render_mirror_entity', 'enemy_energy_slot', 'enemy_energy_family_ready', 'render_mirror_enemy_shot', 'render_mirror_pixel', 'render_mirror_entity_end', 'render_mirror_unsupported', 'upscale', 'render_mirror_begin', 'render_mirror_finish', 'render_mirror_fade_start', 'render_mirror_fade_step', 'render_mirror_present', 'render_mirror_shadow_begin', 'render_mirror_shadow_end']
UNCHANGED = ['get_asset','draw_asset','draw_asset_filtered','darken_rgba','blend_rgba',
             'cloud_shadow_rgba','render_mirror_shadow_end','vulcan_shadow_pixel',
             'render_mirror_pixel','render_mirror_enemy_shot','enemy_energy_family_ready']
HARNESS_PINS = {'test-front-multi-shadow.c': 'a093981081b0cbca61194c7b8837368960442d40473a4acfed7a15bed537cc28', 'test-front-multi-shadow-present.c': 'f3f23a9d21793c432706b5b6ee5093e60fbb2e2f2bc13938a9c3198359d0353e'}
SHA = lambda data: hashlib.sha256(data).hexdigest()


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])


def extract(source, name):
    match = re.search(r'^[A-Za-z_][^\n;{}]*\b' + name + r'\([^;{}]*\)\s*\{', source, re.M)
    assert match, name
    end = source.index('{', match.start()) + 1
    depth = 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[match.start():end] + '\n'


def decode(bank, index):
    # Independent linear-cell oracle; production separately uses x/y RLE decode.
    pos = struct.unpack_from('<H', bank, 2*(index-1))[0]
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
    return bytes(colors + mask)


def bank_from(path, stamp, bank_stamp):
    raw = path.read_bytes()
    assert SHA(raw) == stamp, 'Unexpected original input: ' + path.name
    count = struct.unpack_from('<H', raw)[0]
    offsets = list(struct.unpack_from('<' + str(count) + 'I', raw, 2)) + [len(raw)]
    assert count >= 9 and offsets == sorted(offsets)
    bank = raw[offsets[7]:offsets[8]]
    assert SHA(bank) == bank_stamp
    return bank


def source_scope(candidate, baseline):
    names = git(baseline, 'ls-tree', '-r', '--name-only', BASE, '--', 'src').decode().splitlines()
    names = [n for n in names if Path(n).suffix in {'.c', '.h', '.inc'}]
    actual = {str(p.relative_to(candidate)) for p in (candidate/'src').rglob('*')
              if p.is_file() and p.suffix in {'.c', '.h', '.inc'}}
    assert actual == set(names), 'Unexpected production source inventory'
    sources = {name: (candidate/name).read_bytes() for name in names}
    originals = {name: git(baseline, 'show', BASE + ':' + name) for name in names}
    assert [n for n in names if sources[n] != originals[n]] == ['src/render_mirror.c']
    renderer = sources['src/render_mirror.c'].decode()
    assert SHA(sources['src/render_mirror.c']) == RENDERER_SHA, 'Renderer is not the reviewed source'
    for name in UNCHANGED:
        assert extract(renderer, name) == extract(originals['src/render_mirror.c'].decode(), name), name
    return sources, {'baseline_tree': BASE, 'production_files_checked': len(names),
                     'changed_production_files': ['src/render_mirror.c'],
                     'renderer_sha256': RENDERER_SHA, 'unchanged_functions': UNCHANGED,
                     'production_sha256': {n: SHA(data) for n, data in sources.items()}}


def resource(candidate, baseline, relative):
    frozen = git(baseline, 'show', BASE + ':' + relative)
    path = candidate/relative
    if path.exists():
        assert path.read_bytes() == frozen, 'Frozen resource changed: ' + relative
    return frozen


def prepare_variants(work, full):
    variants, valid = [], []
    for index in IDS:
        for kind in ['missing','invalid','role','id','density','width','height',
                     'anchor-x','anchor-y','truncated','extra','only4','invalid8-valid4','payload']:
            name = f'{kind}-{index}'
            folder = work/name
            folder.mkdir()
            variants.append(name)
            valid.append([int(other != index) for other in IDS])
            for path in full.iterdir():
                if path.name != f'bullet-{index}-8.hda':
                    (folder/path.name).symlink_to(path)
                    continue
                raw = bytearray(path.read_bytes())
                if kind in ['missing', 'only4']:
                    continue
                if kind in ['invalid', 'invalid8-valid4']:
                    raw[0] = 0
                if kind == 'payload':
                    raw[31] ^= 1
                fields = {'role': (4,1110000+index), 'id': (4,80000+IDS[(IDS.index(index)+1)%len(IDS)]),
                          'density': (8,4), 'width': (12,11), 'height': (16,13),
                          'anchor-x': (20,1), 'anchor-y': (24,1)}
                if kind in fields:
                    struct.pack_into('<I', raw, *fields[kind])
                if kind == 'truncated':
                    raw = raw[:-1]
                if kind == 'extra':
                    raw += b'X'
                (folder/path.name).write_bytes(raw)
            if kind in ['only4','invalid8-valid4']:
                raw = (full/f'bullet-{index}-8.hda').read_bytes()[28:]
                h = struct.pack('<4s4I2i', b'HDR1', 80000+index, 4, 12, 14, 0, 0)
                rgba = b''.join(raw[(2*y*96+2*x)*4:(2*y*96+2*x)*4+4] for y in range(56) for x in range(48))
                (folder/f'bullet-{index}-4.hda').write_bytes(h+rgba)
    (work/'missing-all').mkdir()
    variants.append('missing-all')
    valid.append([0]*len(IDS))
    declarations = 'static const char *variants[]={' + ','.join(map(json.dumps, variants)) + '};\n'
    declarations += 'static const int variant_valid[][10]={' + ','.join('{' + ','.join(map(str,row)) + '}' for row in valid) + '};\n'
    return declarations, variants


def production_extracts(sources):
    s = sources['src/render_mirror.c'].decode()
    patterns = [r'typedef struct \{\s*bool initialized,valid;.*?\} Asset;',
                r'typedef struct \{\s*bool valid;\s*const Uint8 \*bank_data;.*?\} TalonBank;',
                r'static Asset assets\[\d+\];', r'static Asset talon_frames\[13\];',
                r'static bool enemy_energy_checked,enemy_energy_valid;', r'enum \{ ASSET_NEWSH2=.*?\};']
    result = {'types.inc': '\n'.join(re.search(q,s,re.S).group() for q in patterns)}
    patterns = [r'typedef struct \{\s*bool live,entered;\s*SDL_Surface \*surface;.*?\} VulcanShadowCall;',
                r'static VulcanShadowCall vulcan_shadow;',
                r'static struct \{const Uint8 \*rgba;char path\[1024\];\} vulcan_shadow_resource\[10\];',
                r'static const struct \{unsigned int index;int slot;uint64_t source,rgba;\} vulcan_shadow_pins\[10\]=\{.*?\n\};']
    result['shadow-types.inc'] = '\n'.join(re.search(q,s,re.S).group() for q in patterns)
    extras = re.findall(r'^static [^\n;{}]*\b(vulcan_shadow_[a-z_]+)\([^;{}]*\)\s*\{',s,re.M)
    helpers = {n: extract(s,n) for n in FUNCTIONS + ['draw_vulcan_shadow'] + extras}
    result['functions.inc'] = '\n'.join(v[:v.index('{')].strip()+';' for v in helpers.values())+'\n'+'\n'.join(helpers.values())
    result['blitters.inc'] = ''.join(extract(sources['src/sprite.c'].decode(),n) for n in ['blit_sprite2','blit_sprite2_darken'])
    result['wrappers.inc'] = ''.join(extract(sources['src/entity_draw.c'].decode(),n) for n in ['draw_entity_sprite2','draw_enemy_shot_sprite2'])
    return result, {n: SHA(v.encode()) for n,v in helpers.items()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, default=HERE.parent)
    parser.add_argument('--baseline', type=Path, help='Git repository containing the pinned baseline tree; defaults to candidate')
    parser.add_argument('--normal-data', type=Path, required=True, help='Explicit external original tyrian.shp')
    parser.add_argument('--xmas-data', type=Path, required=True, help='Explicit external original tyrianc.shp')
    parser.add_argument('--out', type=Path, required=True, help='Fresh output directory outside repositories')
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    args.baseline = args.baseline or args.candidate
    for key,value in vars(args).items():
        if isinstance(value,Path):
            setattr(args,key,value.resolve())
    assert not args.out.exists(), 'Use a fresh output directory'
    for root in [args.candidate,args.baseline]:
        assert root != args.out and root not in args.out.parents, 'Output must be external'
    sources,scope = source_scope(args.candidate,args.baseline)
    banks = [bank_from(path,pin,bpin) for path,pin,bpin in zip([args.normal_data,args.xmas_data],DATA_PINS,BANK_PINS)]
    manifest_raw = resource(args.candidate,args.baseline,'assets/hd/manifest.json')
    manifest = json.loads(manifest_raw)
    filenames = [f'bullet-{i}-8.hda' for i in sorted(set(OLD_IDS+IDS))] + [f'enemy-energy-{i}-8.hda' for i in ENEMIES]
    packs,resource_pins = {},{}
    for kind in ['preview','debug']:
        pack_name = manifest['default_'+kind+'_pack']
        packs[kind] = {}
        for name in filenames:
            raw = resource(args.candidate,args.baseline,'assets/hd/packs/'+pack_name+'/'+name)
            assert SHA(raw) == manifest['packs'][pack_name]['files'][name]['sha256']
            packs[kind][name] = raw
        resource_pins[kind] = {name:SHA(raw) for name,raw in packs[kind].items()}
    assert packs['preview'] == packs['debug'], 'Bounded default-pack resources differ'
    harness = {name:(HERE/name).read_bytes() for name in ['test-front-multi-shadow.c','test-front-multi-shadow-present.c']}
    assert {name: SHA(raw) for name, raw in harness.items()} == HARNESS_PINS, 'Unreviewed C harness changes'
    args.out.mkdir()
    shared = args.out/'fixtures'
    shared.mkdir()
    for name,bank in zip(['bank.bin','xmas-bank.bin'],banks):
        (shared/name).write_bytes(bank)
    full = shared/'preview'
    full.mkdir()
    for name,raw in packs['preview'].items():
        (full/name).write_bytes(raw)
    debug = shared/'debug'
    debug.mkdir()
    for name in filenames:
        (debug/name).symlink_to(full/name)
    variants_inc,variants = prepare_variants(shared,full)
    ref = b''.join(decode(bank,i)+packs['preview'][f'bullet-{i}-8.hda'][28:] for bank in banks for i in IDS)
    ref += b''.join(decode(banks[0],i)+packs['preview'][f'bullet-{i}-8.hda'][28:] for i in CONTROLS)
    ref += b''.join(decode(banks[0],i)+packs['preview'][f'enemy-energy-{i}-8.hda'][28:] for i in [163,164])
    extra = decode(banks[0],58)+packs['preview']['enemy-energy-58-8.hda'][28:]
    extracts,function_pins = production_extracts(sources)
    reports = {}
    for label,filename,reference in [('primary','test-front-multi-shadow.c',ref),('presentation','test-front-multi-shadow-present.c',ref+extra)]:
        directory = args.out/label
        directory.mkdir()
        work = directory/'fixtures'
        work.mkdir()
        for name in ['bank.bin','xmas-bank.bin']+variants:
            (work/name).symlink_to(shared/name)
        (work/'reference.bin').write_bytes(reference)
        for name,text in extracts.items():
            (directory/name).write_text(text)
        (directory/'variants.inc').write_text(variants_inc)
        reports[label] = {'harness_sha256':SHA(harness[filename]),'reference_sha256':SHA(reference),
                          'extracted_sha256':{name:SHA(text.encode()) for name,text in extracts.items()},'builds':{}}
        if args.prepare_only:
            continue
        for config,flags in [('optimized',['-O2']),('sanitized',['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie'])]:
            binary = directory/('test-'+config)
            suppress = ['-Wno-unused-function','-Wno-unused-const-variable'] if label == 'presentation' else []
            command = [os.environ.get('CC','cc'),'-std=c99','-Wall','-Wextra','-Werror','-Wno-misleading-indentation',*suppress,*flags,'-I'+str(directory),str(HERE/filename),'-o',str(binary)]
            result = subprocess.run(command,capture_output=True,text=True)
            (directory/(config+'-compile.log')).write_text(result.stdout+result.stderr)
            if result.returncode:
                print(result.stderr,flush=True)
            result.check_returncode()
            runs = {}
            for kind,pack in [('preview',full),('debug',debug)]:
                env = dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
                result = subprocess.run([str(binary),str(pack),str(work)],env=env,capture_output=True,text=True,timeout=600)
                (directory/(config+'-'+kind+'.log')).write_text(result.stdout+result.stderr)
                print(label+'/'+config+'/'+kind+': '+result.stdout+result.stderr,flush=True)
                result.check_returncode()
                runs[kind] = json.loads(result.stdout)
            reports[label]['builds'][config] = {'flags':flags,'runs':runs}
    assert all((args.candidate/name).read_bytes() == data for name,data in sources.items())
    assert all((HERE/name).read_bytes() == data for name,data in harness.items())
    report = {'status':'PREPARED_NOT_EXECUTED' if args.prepare_only else 'PASS',
              'game_runs':0,'captures':0,'full_pack_copies':0,'source_scope':scope,
              'original_data_sha256':DATA_PINS,'bank_sha256':BANK_PINS,
              'bounded_resource_sha256':resource_pins,'function_sha256':function_pins,
              'variants':variants,'results':reports,'sanitizers':[] if args.prepare_only else ['ASan','UBSan'],
              'limitations':['Exact extracted-source units, not engine or visual acceptance.',
                             'HUD/font/material integrations use no-op or fail-if-entered stubs.',
                             'LeakSanitizer disabled for ptrace; ASan and UBSan stay enabled.',
                             'Normal mode is !xmas plus selected-tile semantic identity, not whole-bank provenance.']}
    (args.out/'result.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['status'] + ': ' + str(args.out/'result.json'))


if __name__ == '__main__':
    main()
