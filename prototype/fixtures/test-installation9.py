"""Finite bank1/newsh2 type32–41 installation oracle. Runs extracted C helpers, never the game.

Synthetic patterns exercise alpha/filter/ordering; optional approved PNGs verify
transport. Original game images and data are neither read nor copied into Git.
"""
from pathlib import Path
import argparse
import hashlib
import io
import json
import os
import re
import struct
import subprocess
import tempfile
import time
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARTWORK=ROOT/'assets/hd/artwork/purple-installation32-41-v2'
IDS = [169, 207, 245, 273, 275, 277, 279, 281, 283]
STONE_IDS = [1, 3, 5, 39, 41, 43, 7, 9, 11, 45, 47, 49]
OLD_IDS = [77, 79, 115, 117, 85, 87, 123, 125, 191, 193, 195, 197, 199, 201, 203, 205, 229, 231, 233, 235, 237, 239, 241, 243, 81, 83, 119, 121, 267, 269, 271, 49, 51, 89, 127, 153, 155, 157]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--source', type=Path, default=ROOT / 'src/render_mirror.c')
p.add_argument('--assets', type=Path, default=ROOT / 'assets/hd/packs/packed-blue-four-foundation-type10-death-effects-white-smoke-shield-green-v2-head-v1-test')
p.add_argument('--runtime-zip', type=Path, help='Optional frozen PNG package to compare byte-for-byte with HDA payloads')
p.add_argument('--alpha-contract', type=Path, default=(ARTWORK/'original-alpha-contract.json') if (ARTWORK/'original-alpha-contract.json').exists() else None, help='Support contract, checked against the independent embedded mask')
p.add_argument('--art-manifest', type=Path, default=(ARTWORK/'selected-manifest.json') if (ARTWORK/'selected-manifest.json').exists() else None, help='Canonical PNG/HDA records with repository-relative PNG paths')
p.add_argument('--actual-only', action='store_true', help='Run the complete actual-art pixel/partial/clipping suite without the generic product')
p.add_argument('--sanitize', action='store_true')
p.add_argument('--output', type=Path, help='Reports only; use an external directory')
a = p.parse_args()
output = a.output or Path(tempfile.mkdtemp(prefix='installation9-report-'))
output.mkdir(parents=True, exist_ok=True)
paths = {name: a.source.parent / name for name in ['render_mirror.c', 'tyrian2.c', 'sprite.c']}
sources = {name: path.read_bytes() for name, path in paths.items()}
s = sources['render_mirror.c'].decode()
started = time.monotonic()


def extract(name, source=s):
    m = re.search(r'^[^\n;]*\b' + name + r'\([^\n;]*\)\s*\{', source, re.M)
    assert m, name
    start = source.index('{', m.start())
    end, depth = start + 1, 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[m.start():end] + '\n'


def raw(base, density, role=101):
    alpha = [0, 1, 127, 128, 254, 255]
    pixels = bytes(v for y in range(28 * density) for x in range(24 * density)
                   for v in [(base * 7 + role * 3 + x * 3 + y) % 256,
                             (base * 11 + role * 5 + x + y * 5) % 256,
                             (base * 13 + role * 7 + x * 7 + y * 2) % 256,
                             alpha[(x + 2 * y + base) % 6]])
    return struct.pack('<4s6I', b'HDR1', role * 10000 + base, density, 24, 28, 0 if role == 201 else 6, 0 if role == 201 else 7) + pixels


def original(index):
    """Generated RLE tile for the original indexed wrapper parity test."""
    out = bytearray()
    for y in range(14):
        pos = x = 0
        while x < 12:
            if (x + y + index) % 5 == 0:
                x += 1
                continue
            first = x
            while x < 12 and (x + y + index) % 5 != 0:
                x += 1
            out.append(((x - first) << 4) | (first - pos))
            out.extend((index + 3 * k + 7 * y) % 240 + 1 for k in range(first, x))
            pos = x
        out.append(12 - pos)
    out.append(15)
    return out


temporary = tempfile.mkdtemp(prefix='installation9-unit-')
print('Retained work:',temporary,flush=True)
if True:
    t = Path(temporary)
    packs = t / 'packs'
    packs.mkdir()
    for name, density, ids in [('full8', 8, IDS), ('full4', 4, IDS),
                               ('all-bindings', 8, IDS + OLD_IDS)]:
        target = packs / name
        target.mkdir()
        for base in ids:
            (target / f'enemy-newsh2-{base}-{density}.hda').write_bytes(raw(base, density))
        if name == 'all-bindings':
            for base in STONE_IDS:
                (target / f'enemy-newshe-{base}-8.hda').write_bytes(raw(base, 8, 110))
    (packs / 'full8' / 'terrain-shapesz-169-8.hda').write_bytes(raw(169, 8, 201))
    # Exactly one available family component does not authorize missing siblings.
    for base in IDS:
        target = packs / f'only-{base}'
        target.mkdir()
        (target / f'enemy-newsh2-{base}-8.hda').write_bytes(raw(base, 8))
    for missing in IDS:
        target = packs / f'fallback-{missing}'
        target.mkdir()
        for base in IDS:
            (target / f'enemy-newsh2-{base}-8.hda').write_bytes(b'BAD1' if base == missing else raw(base, 8))
            (target / f'enemy-newsh2-{base}-4.hda').write_bytes(raw(base, 4))
    (packs / 'empty').mkdir()
    for missing in IDS:
        for bad in range(-1, 16):
            target = packs / f'invalid-{missing}-{bad}'
            target.mkdir()
            for base in IDS:
                name = f'enemy-newsh2-{base}-8.hda'
                if base != missing:
                    os.link(packs / 'full8' / name, target / name)
                    continue
                if bad == -1:
                    continue
                b = bytearray((packs / 'full8' / name).read_bytes())
                if 0 <= bad < 6:
                    struct.pack_into('<I', b, 4 + 4 * bad, struct.unpack_from('<I', b, 4 + 4 * bad)[0] + 1)
                elif bad == 6:
                    b[:4] = b'BAD1'
                elif bad == 7:
                    b = b[:28]
                elif bad == 8:
                    b = b[:-7]
                elif bad == 9:
                    b += b'X'
                elif bad in (10, 11, 12):
                    struct.pack_into('<I', b, 4, (109, 1, 110)[bad - 10] * 10000 + base)
                elif bad == 13:
                    struct.pack_into('<I', b, 20, 0xffffffff)
                elif bad == 14:
                    b = b[:27]
                elif bad == 15:
                    b = b''
                (target / name).write_bytes(b)
    target = packs / 'wrong-prefixes'
    target.mkdir()
    for base in IDS:
        for prefix in ['ship', 'talon-bank', 'enemy-newshe', 'terrain-shapesz']:
            (target / f'{prefix}-{base}-8.hda').write_bytes((packs / 'full8' / f'enemy-newsh2-{base}-8.hda').read_bytes())
    target = packs / 'actual8'
    target.mkdir()
    asset_report = []
    canonical = {row['id']:row for row in json.loads(a.art_manifest.read_text())} if a.art_manifest else {}
    if a.art_manifest: assert set(canonical) == set(IDS)
    approved = None
    if a.runtime_zip:
        from PIL import Image
        approved = zipfile.ZipFile(a.runtime_zip)
    for base in IDS:
        path = a.assets / f'enemy-newsh2-{base}-8.hda'
        b = path.read_bytes()
        assert len(b) == 172060
        assert struct.unpack_from('<4s6I', b) == (b'HDR1', 1010000 + base, 8, 24, 28, 6, 7)
        png_hash = None
        if canonical:
            from PIL import Image
            record = canonical[base]
            assert hashlib.sha256(b).hexdigest() == record['sha256']
            assert list(struct.unpack_from('<6I',b,4)) == record['header_u32']
            png_path = (ROOT/record['source_png']).resolve()
            assert png_path.is_relative_to(ROOT.resolve())
            png = png_path.read_bytes()
            assert hashlib.sha256(png).hexdigest() == record['source_png_sha256']
            im = Image.open(io.BytesIO(png)).convert('RGBA')
            assert im.size == (192,224) and im.tobytes() == b[28:]
            png_hash = hashlib.sha256(png).hexdigest()
        if approved:
            png = approved.read(f'frames8x/newsh2-base{base}-8.png')
            im = Image.open(io.BytesIO(png)).convert('RGBA')
            assert im.size == (192, 224) and im.tobytes() == b[28:]
            png_hash = hashlib.sha256(png).hexdigest()
        (target / path.name).write_bytes(b)
        (packs / f'actual-{base}.rgba').write_bytes(b[28:])
        asset_report.append({'id': base, 'slot': 303 + IDS.index(base),
                             'hda_sha256': hashlib.sha256(b).hexdigest(),
                             'rgba_sha256': hashlib.sha256(b[28:]).hexdigest(),
                             'approved_png_sha256': png_hash,
                             'approved_PNG_to_HDA_exact': bool(approved or canonical), 'alpha_values': sorted(set(b[31::4]))})
    if approved:
        approved.close()
    # Independent reviewed logical transparency contract. Never inferred from
    # the candidate payload and never silently skipped.
    expected_holes = {'169': [], '207': [[21, 14], [20, 15], [15, 20], [15, 21], [15, 22], [16, 22], [13, 23], [14, 23], [13, 24], [14, 24], [13, 25], [13, 26]], '245': [], '273': [[21, 14], [20, 15], [15, 20], [15, 21]], '275': [[21, 14], [20, 15], [15, 20], [15, 21]], '277': [[20, 15], [6, 18], [15, 20], [15, 21]], '279': [], '281': [], '283': [[21, 14], [20, 15], [15, 20], [15, 21], [12, 24], [12, 25], [12, 26], [12, 27]]}
    contract = json.loads(a.alpha_contract.read_text()) if a.alpha_contract else expected_holes
    assert set(contract) == set(expected_holes)
    assert all({tuple(v) for v in contract[k]} == {tuple(v) for v in expected_holes[k]} for k in expected_holes)
    contract_hash = hashlib.sha256(a.alpha_contract.read_bytes() if a.alpha_contract else json.dumps(expected_holes,sort_keys=True).encode()).hexdigest()
    for record in asset_report:
        base = record['id']; data = (packs/f'actual-{base}.rgba').read_bytes()
        holes = {tuple(v) for v in expected_holes[str(base)]}
        assert set(data[3::4]).issubset({0,255})
        for y in range(224):
            for x in range(192):
                assert data[4*(y*192+x)+3] == (0 if (x//8,y//8) in holes else 255)
        record['logical_alpha_holes'] = len(holes)
        record['alpha_contract_exact'] = True
    patterns = [r'typedef struct \{\s*bool initialized,valid;.*?\} Asset;',
                r'enum \{ ASSET_NEWSH2=.*?\};',
                r'typedef struct \{ Asset \*asset; int x,y; \} GreenHead;',
                r'typedef struct \{ Uint16 peak\[16\]\[14\]; \} GreenBackground;',
                r'typedef struct \{ SDL_Rect rect; int bank,index,style; bool live; \} HdRegion;',
                r'static Asset assets\[\d+\];',
                r'static struct \{const Uint8 \*data;unsigned int id;\} terrain_sources\[\d+\];']
    (t / 'types.inc').write_text('\n'.join(re.search(q, s, re.S).group() for q in patterns))
    names = ['palette_rgb', 'complete_turret_group', 'restore_classic_rect', 'blend_rgba',
             'cloud_asset', 'darken_rgba', 'read_asset', 'explosion_asset_slot',
             'enemy_filter_rgba', 'explosion_asset_blend_rgba', 'green_background_snapshot',
             'green_background_peak', 'green_head_composite', 'draw_asset_filtered',
             'scene_asset', 'render_mirror_enemy_tile', 'render_mirror_entity_end',
             'draw_asset', 'render_mirror_map_begin', 'cloud_terrain_slot',
             'ground_terrain_slot', 'plateau_terrain_slot', 'underlay_terrain_slot',
             'road_terrain_slot', 'terrain_holes_slot', 'stone_foundation_slot',
             'layer3_gray_slot','layer3_purple_slot', 'render_mirror_bind_terrain', 'render_mirror_terrain_row']
    (t / 'functions.inc').write_text('\n'.join(extract(n) for n in names))
    bank = bytearray(320 * 2)
    for index in range(1, 321):
        assert len(bank) < 65536
        struct.pack_into('<H', bank, (index - 1) * 2, len(bank))
        bank += original(index)
    (packs / 'synthetic-original-bank.bin').write_bytes(bank)
    (t / 'wrapper.inc').write_text(extract('blit_enemy', sources['tyrian2.c'].decode()))
    (t / 'blitters.inc').write_text(''.join(extract(name, sources['sprite.c'].decode())
                                         for name in ['blit_sprite2', 'blit_sprite2_filter']))
    results = []
    for stem in (['test-installation9'] if a.actual_only else ['test-installation9', 'test-installation9-wrapper']):
        (t / f'{stem}.c').write_bytes((HERE / f'{stem}.c').read_bytes())
        exe = t / stem
        command = ['cc', '-std=c99', '-O1', '-g', '-Wall', '-Wextra', '-Werror']
        if a.sanitize:
            command += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer']
        build = subprocess.run(command + [str(t / f'{stem}.c'), '-o', str(exe)], capture_output=True, text=True)
        (output / f'{stem}-build.log').write_text(build.stdout + build.stderr)
        assert build.returncode == 0, build.stderr
        env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',
                   UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
        run = subprocess.run([str(exe), str(packs)]+(['actual-only'] if a.actual_only else []), capture_output=True, text=True, env=env)
        (output / f'{stem}-result.log').write_text(run.stdout + run.stderr)
        print(run.stdout + run.stderr, flush=True)
        results.append({'test': stem, 'exit_code': run.returncode, 'stdout': run.stdout, 'stderr': run.stderr})
        if run.returncode:
            break
    report = {'source': str(a.source), 'source_hashes': {n: hashlib.sha256(b).hexdigest() for n, b in sources.items()},
              'retained_work': str(t), 'source_stable_during_test': all(b == paths[n].read_bytes() for n, b in sources.items()),
              'sanitize': a.sanitize, 'actual_only': a.actual_only, 'leak_sanitizer': 'disabled under ptrace',
              'results': results, 'elapsed_seconds': time.monotonic() - started,
              'assets': asset_report, 'sparse_alpha_contract_exact': True, 'canonical_manifest_checked': bool(canonical), 'approved_runtime_zip_sha256': hashlib.sha256(a.runtime_zip.read_bytes()).hexdigest() if a.runtime_zip else None,
              'alpha_contract_sha256': contract_hash, 'fixture_hashes': {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest() for name in ['test-installation9.py', 'test-installation9.c', 'test-installation9-wrapper.c']},
              'scope': 'Extracted actual renderer, original wrapper and indexed blitters; synthetic loader/RLE inputs and frozen approved PNG/HDA. No game execution, captures, or original game pixels.'}
    (output / 'result.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Report:', output / 'result.json')
    assert len(results) == (1 if a.actual_only else 2) and all(r['exit_code'] == 0 for r in results)
