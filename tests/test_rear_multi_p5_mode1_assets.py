#!/usr/bin/env python3
"""Verify frozen triple bytes, independent clipping arithmetic and additive assets.

Only accepted/generated artwork is read. No original data, mask or palette.
"""
from pathlib import Path
from collections import Counter
from fractions import Fraction
import copy
import hashlib
import itertools
import json
import re
import shutil
import struct
import subprocess
import sys
import tempfile
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'assets/hd/artwork/player-rear-multicannon-p5-mode1-triples-v1'
SOURCE = ROOT / 'assets/hd/artwork/player-rear-multicannon-p1-six-v1/output'
FAMILY = 'player_rear_multicannon_p5_mode1_triples_v1'
BASE_CATALOG = '71e3e7a1a0afdfac7232573ed20be0111d891d33360b7884d1c8bd088731000a'
BASE_ASSETS = 'e6da230f979e84f1c3b5362a5aba2a7305ff1a862b70f97d1975304c94a5f55e'
CORE_SHA256 = '0c70902e5327892d8f4c00bc6cd9b2f3df844df339caef5554941d04210e964e'
FROZEN_INPUTS_SHA256 = '77011ca8a6341f1d655b74385e8ca86d91b35bb84d9cd18333a951280a958487'
COMPONENT_MANIFEST_SHA256 = '3f058e0cd432a9041298b095ac0911efa46a0a9cf8e06dba6ed67f82cb647fb1'
SHA = lambda data: hashlib.sha256(data).hexdigest()
APPROVED = {(3, 4): ('bb8382993564208f9aac6610728f35c17751e26106e11a632b5c57f388a8faed', '78c48990ef6ca08052b034c80d0b08f6f6f49d254e4b71c8a55dc7f3fa798cd8', 'a722bc55201148ede54e402892b8696392b7756ffd70999d06ba0b08430164d4', '0xb46a6834350f7c50'), (3, 8): ('d7b1a8bada8ea5534e388e79a736dea586cc6e7f28ec28994f002bbefc321745', '083e3bf03b124601a3273718f4b12f0b3003b4574400647e0f858fd49d43d160', 'f5c5162e2a4971b1ca05aa8ebaba029a50708f0f860e8a39a0558c79c59ac06c', '0x78180b46cf51908e'), (41, 4): ('b09a9bb38ab53b357be8caadca6807586255368d56ee2677abd509b5895df68b', 'c832a1267614335d4807a48ad06c44708677ebd4cf69516652066aebe36ef575', '5479580cd938935eb369446c279153f8408638f157dc553896e30530806cb148', '0x5dfd9280619f61ea'), (41, 8): ('f142ac3eb4ddf0b54a7b70ef86d50daeda5fbd2a80f81403286f5add38e2bd79', '47040ee657bfc71fcd46e23348521d20c83e87a9177788164becde85c3295a55', '75c3a8221c7b05762a5d7b68f54ea1a4d0e35efe393943a84a74e54e26ecf1bb', '0x8b30be3de1092cad')}

PARTS = {'3': [[1, True, -2, -5], [1, True, 0, -1], [1, False, -2, 5]],
         '41': [[39, False, 2, -3], [39, False, 0, 1], [39, True, 2, 3]]}
LOSS = {(3, 4): (26, 2646, 231, [597312, 125372, 8354]),
        (3, 8): (82, 11628, 255, [2630790, 557498, 36632]),
        (41, 4): (20, 1926, 215, [422218, 83868, 4456]),
        (41, 8): (64, 8390, 250, [1851628, 369776, 22716])}
EXPECTED = {'build.py', 'build_components.py', 'README.md', 'inputs.json', 'frozen-inputs.json',
            'binding.json', 'provenance.json', 'file-manifest.json', 'output/component-manifest.json'}
EXPECTED |= {f'output/rear-multi-{i}-{d}-exact-clipped-union.{ext}'
             for i, d in APPROVED for ext in ['png', 'rgba']}
assert {str(p.relative_to(ART)) for p in ART.rglob('*') if p.is_file()} == EXPECTED
assert not any(p.is_symlink() for p in ART.rglob('*'))
manifest = json.loads((ART / 'file-manifest.json').read_text())
assert set(manifest['files']) == EXPECTED - {'file-manifest.json'}
for name, pin in manifest['files'].items():
    assert SHA((ART / name).read_bytes()) == pin, name
    if name.endswith(('.json', '.py', '.md')):
        text = (ART / name).read_text()
        assert not re.search(r'/workspace/|/tmp/|/home/|sediment://|file_[A-Za-z0-9]|library_file|private-v\d|data:image', text), name
binding = json.loads((ART / 'binding.json').read_text())
pins = json.loads((ART / 'inputs.json').read_text())
frozen = json.loads((ART / 'frozen-inputs.json').read_text())
contract = json.loads((ART / 'output/component-manifest.json').read_text())
provenance = json.loads((ART / 'provenance.json').read_text())
assert binding['role'] == 131 and binding['logical_size'] == [12, 14] and binding['anchor'] == [0, 0]
assert binding['occupied_logical_bounds'] == [0, 1, 12, 13]
assert binding['components'] == pins['components'] == frozen['components'] == PARTS
assert binding['scope'] == pins['scope']
assert binding['runtime_qualification'] == provenance['runtime_qualification'] == 'DIAGNOSTIC_QUALIFICATION_REQUIRED_SEPARATELY'
assert binding['art_acceptance'] == provenance['art_acceptance'] == 'PASS_WITH_EXPLICITLY_ACCEPTED_TAIL_CLIPPING_DEVIATION'
assert binding['independent_art_review_sha256'] == provenance['independent_art_review_sha256'] == '172811696de7c704be3bb34e71dfd96293bde5d0d40aa6e66606697cf55ac39a'
assert provenance['published_input_baseline'] == {'commit': '4eeaf3a9fef3cb0f9ce1ac83ecc06cfb0194e3b4', 'tree': '575fdf66659881c99c4204791df02f85b8e291c2'}
assert provenance['ordinary_P5_acquisition_established'] is False
assert provenance['original_game_pixels_masks_palettes_or_captures_bundled'] is False
assert provenance['new_art_generated'] is False
assert binding['reviewed_cache_free_art_checkpoint_sha256'] == provenance['reviewed_cache_free_art_checkpoint_sha256'] == '37bedd05e3fb6a79aaddc26a314b845e331d85f67d4b9e57314e1807f2a477ee'
assert binding['sanitized_art_review_sha256'] == provenance['sanitized_art_review_sha256'] == '695e29364d8b8b934d430505c8b03cae2a5a8e924c39b0d8946448e2404f15a8'
assert provenance['original_component_geometry']['original_lobes_overlap'] is False
assert provenance['original_component_geometry']['original_coverage_mask_identity_claimed_for_generated_art'] is False
assert SHA((ART / 'build_components.py').read_bytes()) == CORE_SHA256
assert SHA((ART / 'frozen-inputs.json').read_bytes()) == FROZEN_INPUTS_SHA256
assert SHA((ART / 'output/component-manifest.json').read_bytes()) == COMPONENT_MANIFEST_SHA256
for key in ['inputs', 'builder', 'frozen_builder', 'frozen_inputs', 'frozen_component_manifest']:
    assert SHA((ART / binding[key]).read_bytes()) == binding[key + '_sha256']
assert set(pins['frozen_outputs_sha256']) == {Path(p).name for p in EXPECTED if p.startswith('output/')}
for name, pin in pins['frozen_outputs_sha256'].items():
    assert SHA((ART / 'output' / name).read_bytes()) == pin
for obj in [pins, binding]:
    assert [(r['accepted_source_id'], r['source_id'], r['density'], r['key']) for r in obj['resources']] == [
        (1, 3, 4, 1310003), (1, 3, 8, 1310003), (39, 41, 4, 1310041), (39, 41, 8, 1310041)]
assert [(r['target'], r['density']) for r in contract['results']] == list(APPROVED)


def stats(q):
    pixels = list(q.values())
    energy = [sum(p[c] * p[3] for p in pixels) for c in range(3)]
    return {'supported_samples': len(pixels), 'maximum_alpha': max([p[3] for p in pixels] or [0]),
            'RGB_range': [[min(p[c] for p in pixels), max(p[c] for p in pixels)] for c in range(3)] if pixels else None,
            'alpha_sum': sum(p[3] for p in pixels), 'premultiplied_RGB_C_times_A': energy,
            'weighted_luma_C_times_A_2126_7152_722': sum(a * b for a, b in zip(energy, [2126, 7152, 722])),
            'bounds_exclusive': [min(x for x, y in q), min(y for x, y in q), max(x for x, y in q) + 1, max(y for x, y in q) + 1] if q else None}


def split(q, density):
    inside = {xy: p for xy, p in q.items() if 0 <= xy[0] < 12 * density and 0 <= xy[1] < 14 * density}
    outside = {xy: p for xy, p in q.items() if xy not in inside}
    full, kept, lost = map(stats, [q, inside, outside])
    summary = {'full_unbounded': full, 'retained': kept, 'clipped': lost,
               'clipped_alpha_fraction': lost['alpha_sum'] / full['alpha_sum'],
               'clipped_luma_fraction': lost['weighted_luma_C_times_A_2126_7152_722'] / full['weighted_luma_C_times_A_2126_7152_722']}
    return inside, outside, summary


def rgba(q, density):
    return b''.join(bytes(q.get((x, y), (0, 0, 0, 0))) for y in range(14 * density) for x in range(12 * density))


accepted = {}
assert pins['accepted_inputs'] == provenance['accepted_inputs']
for row, old in zip(pins['accepted_inputs'], frozen['inputs']):
    i, d = row['source_id'], row['density']
    assert (i, d) == (old['source_id'], old['density'])
    for ext in ['png', 'rgba']:
        assert row[f'{ext}_repo_path'] == f'{SOURCE.relative_to(ROOT)}/rear-multi-{i}-{d}.{ext}'
        assert SHA((ROOT / row[f'{ext}_repo_path']).read_bytes()) == row[ext + '_sha256'] == old[ext + '_sha256']
    raw = (ROOT / row['rgba_repo_path']).read_bytes()
    with Image.open(ROOT / row['png_repo_path']) as im:
        assert im.mode == 'RGBA' and im.size == (12 * d, 14 * d) and im.tobytes() == raw
    accepted[i, d] = [tuple(raw[k:k + 4]) for k in range(0, len(raw), 4)]
    assert all(p[3] or p == (0, 0, 0, 0) for p in accepted[i, d])

catalog = json.loads((ROOT / 'assets/hd/manifest.json').read_text())
from rear_multi_p7_asset_projection import project_p7
catalog, p7_paths = project_p7(ROOT, catalog)
family = catalog[FAMILY]
packs = {catalog['default_preview_pack'], catalog['default_debug_pack']}
assert family['source'] == str(ART.relative_to(ROOT))
for name, key in [('binding.json', 'binding_sha256'), ('provenance.json', 'provenance_sha256'), ('file-manifest.json', 'art_file_manifest_sha256')]:
    assert family[key] == SHA((ART / name).read_bytes())
assert family['role'] == 131 and family['ids'] == [3, 41] and family['densities'] == [4, 8]
assert family['scope'] == binding['scope'] and family['runtime_qualification'] == binding['runtime_qualification']
assert family['art_acceptance'] == binding['art_acceptance']
assert family['reviewed_component_manifest_sha256'] == COMPONENT_MANIFEST_SHA256
new_paths = {str(ART.relative_to(ROOT) / name) for name in EXPECTED}
max_native_alpha, max_native_luma = 0, 0
for row, pin, case in zip(binding['resources'], pins['resources'], contract['results']):
    i, source_id, d = row['source_id'], row['accepted_source_id'], row['density']
    assert all(row[k] == v for k, v in pin.items())
    assert (case['target'], case['density']) == (i, d)
    assert row['parts'] == case['parts'] == PARTS[str(i)]
    assert tuple(row[k] for k in ['png_sha256', 'rgba_sha256', 'hda_sha256', 'rgba_fnv1a64']) == APPROVED[i, d]
    assert row['filename'] == f'rear-multicannon-p1-bank8-{i}-{d}.hda'
    raw, png = (ART / row['rgba']).read_bytes(), (ART / row['png']).read_bytes()
    assert SHA(raw) == row['rgba_sha256'] == case['rgba_sha256'] and SHA(png) == row['png_sha256'] == case['png_sha256']
    with Image.open(ART / row['png']) as im:
        assert im.mode == 'RGBA' and im.size == (12 * d, 14 * d) and im.tobytes() == raw
    pos, chunks = 8, []
    while pos < len(png):
        length = struct.unpack('>I', png[pos:pos + 4])[0]
        chunks.append(png[pos + 4:pos + 8]); pos += length + 12
    assert chunks == [b'IHDR', b'IDAT', b'IEND'] and pos == len(png)
    # Independent inverse-coordinate assembly scans virtual destination space,
    # unlike the frozen builder's forward transform of supported source samples.
    layers = []
    for sid, fy, dx, dy in row['parts']:
        layer = {}
        for y in range(-5 * d, 19 * d):
            for x in range(-2 * d, 14 * d):
                sx, sy = x - dx * d, y - dy * d
                if fy:
                    sy = 14 * d - 1 - sy
                if 0 <= sx < 12 * d and 0 <= sy < 14 * d:
                    pixel = accepted[sid, d][sy * 12 * d + sx]
                    if pixel[3]:
                        layer[x, y] = pixel
        layers.append(layer)
    assert all(not (set(a) & set(b)) for a, b in itertools.combinations(layers, 2))
    full = {xy: p for layer in layers for xy, p in layer.items()}
    kept, lost, metrics = split(full, d)
    assert rgba(kept, d) == raw
    assert metrics == case['stats']
    assert [split(layer, d)[2] for layer in layers] == case['per_part_clipping']
    assert [v['clipped']['supported_samples'] for v in case['per_part_clipping']] == [len(lost) // 2, 0, len(lost) // 2]
    assert metrics['retained']['bounds_exclusive'] == [0, d, 12 * d, 13 * d]
    assert Counter(full.values()) == Counter(p for p in accepted[source_id, d] * 3 if p[3])
    assert Counter(kept.values()) + Counter(lost.values()) == Counter(full.values())
    for order in itertools.permutations(range(3)):
        ordered = {xy: p for k in order for xy, p in layers[k].items()}
        assert rgba(ordered, d) == raw
    assert case['overlap_authored_samples'] == 0 and case['all_six_orders_byte_identical'] is True
    assert case['retained_RGBA_exact_from_single_component'] is True and case['added_support_beyond_transformed_union'] == 0
    assert [[*xy, *p] for xy, p in sorted(lost.items())] == case['clipped_samples_xy_RGBA']
    clipped = metrics['clipped']; count, alpha, maximum, energy = LOSS[i, d]
    assert (clipped['supported_samples'], clipped['alpha_sum'], clipped['maximum_alpha'], clipped['premultiplied_RGB_C_times_A']) == (count, alpha, maximum, energy)
    assert metrics['clipped_alpha_fraction'] <= 0.008123 and metrics['clipped_luma_fraction'] <= 0.004364
    assert all(204 <= p[0] <= 255 and 0 <= p[1] <= 57 and 0 <= p[2] <= 5 for p in lost.values())
    assert all((x < 0 if i == 3 else x >= 12 * d) for x, y in lost)
    for native in case['native']:
        s = native['scale']; sampled = {}
        for y in range(-14 * s, 28 * s):
            for x in range(-12 * s, 24 * s):
                sx = (Fraction(2 * x + 1, 2) * d / s).__floor__()
                sy = (Fraction(2 * y + 1, 2) * d / s).__floor__()
                if (sx, sy) in full:
                    sampled[x, y] = full[sx, sy]
        inside, outside, native_stats = split(sampled, s)
        assert native_stats == native['stats']
        assert SHA(rgba(inside, s)) == native['retained_rgba_sha256']
        assert [[*xy, *p] for xy, p in sorted(outside.items())] == native['clipped_samples_xy_RGBA']
        for name, bg in [('brown', (104, 72, 44)), ('cloud', (173, 191, 206))]:
            blends = [tuple((bg[c] * (255 - p[3]) + p[c] * p[3] + 127) // 255 for c in range(3)) for p in outside.values()]
            assert native['clipped_blend_effect_by_background'][name] == {
                'changed_pixels': sum(p != bg for p in blends),
                'maximum_absolute_channel_change': max([abs(p[c] - bg[c]) for p in blends for c in range(3)] or [0])}
        max_native_alpha = max(max_native_alpha, native_stats['clipped_alpha_fraction'])
        max_native_luma = max(max_native_luma, native_stats['clipped_luma_fraction'])
    fnv = 14695981039346656037
    for value in raw:
        fnv = ((fnv ^ value) * 1099511628211) & ((1 << 64) - 1)
    assert row['rgba_fnv1a64'] == f'0x{fnv:016x}'
    assert len(row['pack_paths']) == 2 and {Path(p).parent.name for p in row['pack_paths']} == packs
    for name in row['pack_paths']:
        path = ROOT / name; hda = path.read_bytes()
        assert len(hda) == row['hda_bytes'] == 28 + len(raw) and SHA(hda) == row['hda_sha256']
        assert struct.unpack('<4s6I', hda[:28]) == (b'HDR1', 1310000 + i, d, 12, 14, 0, 0)
        assert hda[28:] == raw
        assert catalog['packs'][path.parent.name]['files'][path.name] == {
            'sha256': row['hda_sha256'], 'header_u32': [1310000 + i, d, 12, 14, 0, 0],
            'source_png': row['catalog_source_png'], 'source_png_sha256': row['png_sha256']}
        new_paths.add(name)
    assert (ROOT / row['catalog_source_png']).read_bytes() == png
    assert catalog['source_pngs'][row['hda_sha256']] == {
        'path': row['catalog_source_png'], 'sha256': row['png_sha256'], 'RGBA_sha256': row['rgba_sha256']}
    new_paths.add(row['catalog_source_png'])
    for pack, value in catalog['packs'].items():
        assert value['count'] == len(value['files'])
        if pack not in packs:
            assert row['filename'] not in value['files'] and not (ROOT / 'assets/hd/packs' / pack / row['filename']).exists()
assert max_native_alpha == 0.009645608978359792 and max_native_luma == 0.005247730189331473
assert family['entries'] == [{'id': row['source_id'], 'density': row['density'], 'HDA_sha256': row['hda_sha256']} for row in binding['resources']]
assert len(catalog['source_pngs']) == 658 and sum(p['count'] for p in catalog['packs'].values()) == 3446
assert all(catalog['packs'][p]['count'] == 605 for p in packs)
assert len({r['path'] for r in catalog['source_pngs'].values()}) == 658
assert len({r['sha256'] for r in catalog['source_pngs'].values()}) == 654
physical_sources = [p for p in (ROOT / 'assets/hd/source').glob('*.png') if str(p.relative_to(ROOT)) not in p7_paths]
assert len(physical_sources) == 724 and len({SHA(p.read_bytes()) for p in physical_sources}) == 718
pack_sources = {r['source_png'] for p in catalog['packs'].values() for r in p['files'].values()}
assert len(pack_sources) == 617 and len({SHA((ROOT / p).read_bytes()) for p in pack_sources}) == 613
assert len(new_paths) == 29
inverse = copy.deepcopy(catalog); inverse.pop(FAMILY)
for row in binding['resources']:
    inverse['source_pngs'].pop(row['hda_sha256'])
    for pack in packs:
        inverse['packs'][pack]['files'].pop(row['filename']); inverse['packs'][pack]['count'] -= 1
assert SHA((json.dumps(inverse, indent=2) + '\n').encode()) == provenance['baseline_catalog_sha256'] == BASE_CATALOG
old_assets = {str(p.relative_to(ROOT)): SHA(p.read_bytes()) for p in (ROOT / 'assets').rglob('*')
              if p.is_file() and str(p.relative_to(ROOT)) not in new_paths | p7_paths | {'assets/hd/manifest.json'}}
assert len(old_assets) == provenance['old_non_manifest_assets'] == 7093
assert SHA(''.join(p + '\0' + h + '\n' for p, h in sorted(old_assets.items())).encode()) == provenance['old_assets_path_sha256_inventory_digest'] == BASE_ASSETS

with tempfile.TemporaryDirectory(prefix='rear-p5-triples-') as temporary:
    relocated = Path(temporary)
    local_art, local_source = relocated / ART.name, relocated / 'player-rear-multicannon-p1-six-v1/output'
    local_art.mkdir(); local_source.mkdir(parents=True)
    for name in ['build.py', 'build_components.py', 'inputs.json', 'frozen-inputs.json']:
        shutil.copy2(ART / name, local_art / name)
    for row in pins['accepted_inputs']:
        for kind in ['png', 'rgba']:
            shutil.copy2(ROOT / row[f'{kind}_repo_path'], local_source)
    assert len(list(local_source.iterdir())) == 8
    def command(out, hda, source=None):
        cmd = [sys.executable, '-I', '-B', str(local_art / 'build.py'), '--output', str(out), '--hda-output', str(hda)]
        return cmd + (['--source', str(source)] if source is not None else [])
    def rejected(out, hda, message, source=None):
        result = subprocess.run(command(out, hda, source), capture_output=True, text=True, cwd=relocated)
        assert result.returncode != 0 and message in result.stderr, result.stderr
    for index, source in [(1, None), (2, local_source)]:
        out, hda = relocated / f'art{index}', relocated / f'hda{index}'
        subprocess.run(command(out, hda, source), check=True, cwd=relocated)
        assert {p.name for p in out.iterdir()} == {p.name for p in (ART / 'output').iterdir()}
        assert {p.name for p in hda.iterdir()} == {row['filename'] for row in binding['resources']}
        for p in out.iterdir():
            assert p.read_bytes() == (ART / 'output' / p.name).read_bytes()
        for row in binding['resources']:
            assert (hda / row['filename']).read_bytes() == (ROOT / row['pack_paths'][0]).read_bytes()
        rejected(out, hda, 'must not exist')
        for p in out.iterdir():
            assert p.read_bytes() == (ART / 'output' / p.name).read_bytes()
    # Corrupt the final source of each type. Neither destination may be created.
    for kind in ['png', 'rgba']:
        bad = local_source / f'rear-multi-39-8.{kind}'
        original = bad.read_bytes(); bad.write_bytes(bytes([original[0] ^ 1]) + original[1:])
        out, hda = relocated / ('bad-art-' + kind), relocated / ('bad-hda-' + kind)
        rejected(out, hda, f'Accepted {kind.upper()} pin mismatch')
        assert not out.exists() and not hda.exists(); bad.write_bytes(original)
    # Corrupt immutable core/spec and approved generated payload pins independently.
    for name, message in [('build_components.py', 'Frozen builder pin mismatch'),
                          ('frozen-inputs.json', 'Frozen input specification pin mismatch')]:
        bad = local_art / name; original = bad.read_bytes(); bad.write_bytes(original + b' ')
        out, hda = relocated / ('bad-art-' + name), relocated / ('bad-hda-' + name)
        rejected(out, hda, message); assert not out.exists() and not hda.exists(); bad.write_bytes(original)
    spec_path = local_art / 'inputs.json'; original = spec_path.read_bytes()
    changed = json.loads(original); changed['resources'][-1]['hda_sha256'] = '0' * 64
    spec_path.write_text(json.dumps(changed))
    out, hda = relocated / 'bad-output-art', relocated / 'bad-output-hda'
    rejected(out, hda, 'Approved hda pin mismatch'); assert not out.exists() and not hda.exists()
    spec_path.write_bytes(original)
    for index, (out, hda, message) in enumerate([
        (relocated / 'same', relocated / 'same', 'must be separate'),
        (relocated / 'outer', relocated / 'outer/inner', 'must be separate'),
        (local_source / 'new', relocated / 'bad-hda-source', 'outside source and package'),
        (local_art / 'new', relocated / 'bad-hda-package', 'outside source and package')]):
        rejected(out, hda, message); assert not out.exists() and not hda.exists()
    dangling = relocated / 'dangling'; dangling.symlink_to(relocated / 'missing')
    rejected(dangling, relocated / 'bad-hda-link', 'must not exist')
    assert dangling.is_symlink() and not (relocated / 'bad-hda-link').exists()
    alias = relocated / 'source-alias'; alias.symlink_to(local_source, target_is_directory=True)
    rejected(alias / 'new', relocated / 'bad-hda-alias', 'outside source and package')
    assert not (local_source / 'new').exists() and not (relocated / 'bad-hda-alias').exists()
    assert not any(p.name == '__pycache__' or p.suffix == '.pyc' for p in relocated.rglob('*'))
print('Rear P5 mode1 assets PASS: four exact triples; inverse-coordinate pixels, clipped-alpha/energy/native metrics and six orders verified; eight HDR1 copies; 7093 old assets exact; additive catalog inverse; 3446 entries/658 mappings/724 source files/605 default packs; repeated relocated rebuild, corrupt-input/output rejection and unsafe-output checks. Diagnostic runtime remains separate.')
