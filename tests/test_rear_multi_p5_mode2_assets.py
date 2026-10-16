#!/usr/bin/env python3
"""Check selected P5 twins, exact rational assembly, additive catalog and rebuild.

Generated assets only. No original-game payload, mask, palette or capture read.
"""
from pathlib import Path
from fractions import Fraction
import copy
import hashlib
import json
import re
import shutil
import struct
import subprocess
import sys
import tempfile
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'assets/hd/artwork/player-rear-multicannon-p5-mode2-twins-v1'
SOURCE = ROOT / 'assets/hd/artwork/player-rear-multicannon-p1-six-v1/output'
FAMILY = 'player_rear_multicannon_p5_mode2_twins_v1'
REVIEWED = 'cd83131544d3d7163327e089bac6fa6fbd51535da800b4115fe58361b238a2dc'
BASE_CATALOG = 'f1ceac8430b7419a62d62d957081bf630339150c6efd80615cdfae7eea4013b9'
BASE_ASSETS = '77d5921e2a0fa6aa1dc8af331c28a049521ea0d5ebabc0436d4ee0c4b6f6a499'
SHA = lambda data: hashlib.sha256(data).hexdigest()
APPROVED = {
    (277, 4): ('96d2afe30ca79ad058e205e0783de8c9b6d50c2204c1f26734f82584271c4cec',
               '45ba353dbc163224e0b183e142f7a4c8ac1f71a36274dfb5524fed51443480ed',
               '2117c701f4dbc007155c6376a6af3cd8dc17b5372adacb4d540ab3438e23146f',
               '0xf03f8f745a244970'),
    (277, 8): ('72721e9e06c9c6d268766f95d9ac65e28482a080fe9abef2ced08c8dced0463b',
               '75b03b20070976edcb7ad330aec1f8754ae47eef70c88f7307efacb92608fdf6',
               '8a226ac49239196257380a40bb5b8019b4df58b1e373d0959743e52eb093e756',
               '0x3df2a878cda365e6'),
    (278, 4): ('3e65188e0c8fc823e60fa7e05809d672a87c481dda45dc0e58e33314f7e7725c',
               'e111cb772f63599ee7588fd9bfd743b14c0dd27d04ea9be0fd90dd700ebc05c8',
               '70752a39adebdd43468383f9c7775e8962569986ecf7237d539005679f4b6a84',
               '0x3fae8a76be180e70'),
    (278, 8): ('e6a45a6bb6c877cae3ab8873e441575b3d64ce2feacf788c8950ee1111cfe41b',
               'd9c8d8468785ac51d3d5d47c0a8069640225a01bf331501eaa004272746e0757',
               '0f039fb1520344a503a9cd1dbafa1aeab2e065f796f5dc6831e919e3cee365d4',
               '0xb953b3abd4a3fcde'),
}
EXPECTED = {'build.py', 'README.md', 'inputs.json', 'binding.json', 'provenance.json',
            'file-manifest.json', 'overlap-analysis.json', 'output/composite-contract.json'}
EXPECTED |= {f'output/rear-multi-{i}-{d}-lower_over_upper.{ext}'
             for i, d in APPROVED for ext in ['png', 'rgba']}
assert {str(p.relative_to(ART)) for p in ART.rglob('*') if p.is_file()} == EXPECTED
manifest = json.loads((ART / 'file-manifest.json').read_text())
assert set(manifest['files']) == EXPECTED - {'file-manifest.json'}
for name, pin in manifest['files'].items():
    assert not (ART / name).is_symlink() and SHA((ART / name).read_bytes()) == pin, name
    if name.endswith(('.json', '.py', '.md')):
        text = (ART / name).read_text()
        assert not re.search(r'/workspace/|/tmp/|/home/|sediment://|file_[A-Za-z0-9]|library_file|private-v\d|data:image', text), name
binding = json.loads((ART / 'binding.json').read_text())
pins = json.loads((ART / 'inputs.json').read_text())
contract = json.loads((ART / 'output/composite-contract.json').read_text())
analysis = json.loads((ART / 'overlap-analysis.json').read_text())
provenance = json.loads((ART / 'provenance.json').read_text())
assert binding['role'] == 131 and binding['logical_size'] == [12, 14] and binding['anchor'] == [0, 0]
assert binding['selected_order'] == pins['selected_order'] == contract['selected_order'] == analysis['selected_order'] == 'lower_over_upper'
assert binding['layer_order_back_to_front_logical_xy'] == contract['layer_order_back_to_front_logical_xy'] == analysis['layer_order_back_to_front_logical_xy'] == [[0, 0], [0, 4]]
assert analysis['original_layer_order_observable'] is False
assert binding['runtime_qualification'] == contract['runtime_qualification'] == provenance['runtime_qualification'] == 'DIAGNOSTIC_QUALIFICATION_RECORDED_SEPARATELY'
assert binding['scope'] == pins['scope'] == contract['scope']
assert binding['reviewed_export_sha256'] == pins['reviewed_export_sha256'] == contract['reviewed_export_sha256'] == REVIEWED
assert provenance['reviewed_generated_only_export']['sha256'] == REVIEWED
assert provenance['reviewed_generated_only_export']['selection_manifest_sha256'] == binding['reviewed_selection_sha256'] == '2d24d6e573547bf940b4dbc3752ae7bdefe0a0e1e8a472525838a6177a8ea6a1'
assert provenance['reviewed_generated_only_export']['arithmetic_manifest_sha256'] == analysis['reviewed_arithmetic_manifest_sha256'] == '254f0854f8bfd45884ed8dbb607bec3fd65b2ae1f623f3baf266cf10bd1721b1'
assert provenance['reviewed_generated_only_export']['independent_art_review_sha256'] == binding['independent_art_review_sha256'] == '6e9ce7d3b620d30e8f6af57d65cae5662aa1a2312d81e1e6560ce18cae14e53a'
assert provenance['published_input_baseline'] == {'commit': '1dc8fe136bab12f45e8107bbe6a9a5fa9ffdafaf', 'tree': '3803418ae6423c323c203ea9f07f076d392314d2'}
assert provenance['ordinary_P5_purchase_or_actual_game_PASS_claimed'] is False
assert provenance['original_game_pixels_masks_palettes_or_captures_bundled'] is False
for key in ['inputs', 'builder', 'composite_contract', 'overlap_analysis']:
    assert SHA((ART / binding[key]).read_bytes()) == binding[key + '_sha256']
assert all(value is False for value in contract['constraints'].values())
for obj in [pins, binding, contract]:
    assert [(r['accepted_source_id'], r['source_id'], r['density'], r['key']) for r in obj['resources']] == [
        (281, 277, 4, 1310277), (281, 277, 8, 1310277), (282, 278, 4, 1310278), (282, 278, 8, 1310278)]


def rounded(value):
    # Independent Fraction implementation, rather than builder integer formula.
    return (value + Fraction(1, 2)).numerator // (value + Fraction(1, 2)).denominator


def over(back, front):
    alpha = Fraction(front[3], 255) + Fraction(back[3], 255) * (1 - Fraction(front[3], 255))
    if not alpha:
        return bytes(4)
    return bytes([rounded((front[c] * Fraction(front[3], 255)
                          + back[c] * Fraction(back[3], 255) * (1 - Fraction(front[3], 255))) / alpha)
                  for c in range(3)] + [rounded(alpha * 255)])


catalog = json.loads((ROOT / 'assets/hd/manifest.json').read_text())
family = catalog[FAMILY]
packs = {catalog['default_preview_pack'], catalog['default_debug_pack']}
assert family['source'] == str(ART.relative_to(ROOT))
for name, key in [('binding.json', 'binding_sha256'), ('provenance.json', 'provenance_sha256'), ('file-manifest.json', 'art_file_manifest_sha256')]:
    assert family[key] == SHA((ART / name).read_bytes())
assert family['role'] == 131 and family['ids'] == [277, 278] and family['densities'] == [4, 8]
assert family['scope'] == binding['scope'] and family['runtime_qualification'] == 'DIAGNOSTIC_QUALIFICATION_RECORDED_SEPARATELY'
new_paths = {str(ART.relative_to(ROOT) / name) for name in EXPECTED}
for row, pin, transformed, case in zip(binding['resources'], pins['resources'], contract['resources'], analysis['analysis']):
    i, accepted, d = row['source_id'], row['accepted_source_id'], row['density']
    assert all(row[k] == v and transformed[k] == v for k, v in pin.items())
    assert (case['target_id'], case['source_id'], case['density']) == (i, accepted, d)
    assert tuple(row[k] for k in ['png_sha256', 'rgba_sha256', 'hda_sha256', 'rgba_fnv1a64']) == APPROVED[i, d]
    assert row['filename'] == f'rear-multicannon-p1-bank8-{i}-{d}.hda'
    raw, png = (ART / row['rgba']).read_bytes(), (ART / row['png']).read_bytes()
    assert SHA(raw) == row['rgba_sha256'] and SHA(png) == row['png_sha256']
    with Image.open(ART / row['png']) as im:
        assert im.mode == 'RGBA' and im.size == (12 * d, 14 * d) and im.tobytes() == raw
    # Only PNG structure/image chunks; no metadata or embedded source content.
    pos, chunks = 8, []
    while pos < len(png):
        length = struct.unpack('>I', png[pos:pos + 4])[0]
        chunks.append(png[pos + 4:pos + 8]); pos += length + 12
    assert chunks == [b'IHDR', b'IDAT', b'IEND'] and pos == len(png)
    source_raw = (ROOT / pin['source_rgba_repo_path']).read_bytes()
    source_png = (ROOT / pin['source_png_repo_path']).read_bytes()
    assert SHA(source_raw) == pin['source_rgba_sha256'] and SHA(source_png) == pin['source_png_sha256']
    assert Path(pin['source_png_repo_path']).parent == SOURCE.relative_to(ROOT)
    assert Path(pin['source_rgba_repo_path']).parent == SOURCE.relative_to(ROOT)
    with Image.open(ROOT / pin['source_png_repo_path']) as im:
        assert im.mode == 'RGBA' and im.size == (12 * d, 14 * d) and im.tobytes() == source_raw
    assert len(raw) == len(source_raw) == 12 * 14 * d * d * 4
    assert not any(source_raw[-12 * d * 4 * 4 * d:])
    upper = [source_raw[o:o + 4] for o in range(0, len(source_raw), 4)]
    lower = [bytes(4)] * (12 * d * 4 * d) + upper[:-(12 * d * 4 * d)]
    independent = b''.join(over(back, front) for back, front in zip(upper, lower))
    reverse = b''.join(over(front, back) for back, front in zip(upper, lower))
    assert raw == independent
    overlaps = [k for k, (a, b) in enumerate(zip(upper, lower)) if a[3] and b[3]]
    singles = [k for k, (a, b) in enumerate(zip(upper, lower)) if bool(a[3]) != bool(b[3])]
    assert len(overlaps) == case['overlap_sample_count'] == transformed['checks']['overlap_sample_count'] == 5
    assert case['nonoverlap_supported_samples_preserved_exact'] == len(singles)
    for k in singles:
        assert raw[4 * k:4 * k + 4] == (upper[k] if upper[k][3] else lower[k])
    for p in case['overlap']:
        x, y = p['xy']; k = y * 12 * d + x
        assert k in overlaps and list(upper[k]) == p['upper_RGBA'] and list(lower[k]) == p['lower_RGBA']
        assert list(raw[k * 4:k * 4 + 4]) == p['orders']['lower_over_upper']['output_RGBA']
        assert list(reverse[k * 4:k * 4 + 4]) == p['orders']['upper_over_lower']['output_RGBA']
    assert all(bool(raw[4 * k + 3]) == bool(a[3] or b[3]) for k, (a, b) in enumerate(zip(upper, lower)))
    assert sum(raw[3::4]) == case['aggregate']['lower_over_upper']['stats']['alpha_sum'] == (205342 if d == 4 else 837512)
    assert sum(raw[3::4]) - 2 * sum(source_raw[3::4]) == (-22 if d == 4 else -12)
    delta = [sum(raw[o + c] * raw[o + 3] - 2 * source_raw[o + c] * source_raw[o + 3]
                 for o in range(0, len(raw), 4)) for c in range(3)]
    assert delta == ([-4492, -831, 45] if d == 4 else [-2480, -462, 22])
    assert transformed['checks']['premultiplied_RGB_delta_vs_two_copies'] == delta
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
            assert row['filename'] not in value['files']
            assert not (ROOT / 'assets/hd/packs' / pack / row['filename']).exists()
assert family['entries'] == [{'id': row['source_id'], 'density': row['density'], 'HDA_sha256': row['hda_sha256']} for row in binding['resources']]
inverse = copy.deepcopy(catalog)
later_paths = set()
# The later P5 mode1 triples are a separately verified, exact additive family.
# Strip only its bounded 29 new paths before preserving the historical hashes.
triple_name = 'player_rear_multicannon_p5_mode1_triples_v1'
if triple_name in inverse:
    triple = inverse.pop(triple_name)
    assert triple['source'] == 'assets/hd/artwork/player-rear-multicannon-p5-mode1-triples-v1'
    assert triple['ids'] == [3, 41] and triple['densities'] == [4, 8] and triple['role'] == 131
    assert triple['reviewed_component_manifest_sha256'] == '3f058e0cd432a9041298b095ac0911efa46a0a9cf8e06dba6ed67f82cb647fb1'
    triple_art = ROOT / triple['source']
    triple_binding = json.loads((triple_art / 'binding.json').read_text())
    triple_manifest = json.loads((triple_art / 'file-manifest.json').read_text())
    assert SHA((triple_art / 'binding.json').read_bytes()) == triple['binding_sha256']
    assert SHA((triple_art / 'file-manifest.json').read_bytes()) == triple['art_file_manifest_sha256']
    triple_expected = {'build.py', 'build_components.py', 'README.md', 'inputs.json', 'frozen-inputs.json',
                       'binding.json', 'provenance.json', 'output/component-manifest.json'}
    triple_expected |= {f'output/rear-multi-{i}-{d}-exact-clipped-union.{ext}'
                        for i in [3, 41] for d in [4, 8] for ext in ['png', 'rgba']}
    assert set(triple_manifest['files']) == triple_expected
    assert {str(p.relative_to(triple_art)) for p in triple_art.rglob('*') if p.is_file()} == triple_expected | {'file-manifest.json'}
    for name, pin in triple_manifest['files'].items():
        assert SHA((triple_art / name).read_bytes()) == pin
        later_paths.add(str(triple_art.relative_to(ROOT) / name))
    later_paths.add(str(triple_art.relative_to(ROOT) / 'file-manifest.json'))
    assert [(r['source_id'], r['density']) for r in triple_binding['resources']] == [(3, 4), (3, 8), (41, 4), (41, 8)]
    for row in triple_binding['resources']:
        i, d = row['source_id'], row['density']
        assert row['filename'] == f'rear-multicannon-p1-bank8-{i}-{d}.hda'
        assert row['catalog_source_png'] == f"assets/hd/source/rear-multicannon-p1-bank8-{i}-{d}-{row['hda_sha256'][:12]}.png"
        assert inverse['source_pngs'].pop(row['hda_sha256']) == {'path': row['catalog_source_png'], 'sha256': row['png_sha256'], 'RGBA_sha256': row['rgba_sha256']}
        later_paths.add(row['catalog_source_png'])
        for pack in packs:
            entry = inverse['packs'][pack]['files'].pop(row['filename'])
            assert entry['sha256'] == row['hda_sha256'] and entry['header_u32'] == [1310000 + i, d, 12, 14, 0, 0]
            inverse['packs'][pack]['count'] -= 1
            later_paths.add(str(Path('assets/hd/packs') / pack / row['filename']))
    assert len(later_paths) == 29
    assert SHA((json.dumps(inverse, indent=2) + '\n').encode()) == '71e3e7a1a0afdfac7232573ed20be0111d891d33360b7884d1c8bd088731000a'
assert len(inverse['source_pngs']) == 654 and sum(p['count'] for p in inverse['packs'].values()) == 3438
assert all(inverse['packs'][p]['count'] == 601 for p in packs)
assert len({r['path'] for r in inverse['source_pngs'].values()}) == 654
assert len({r['sha256'] for r in inverse['source_pngs'].values()}) == 650
physical_sources = [p for p in (ROOT / 'assets/hd/source').glob('*.png') if str(p.relative_to(ROOT)) not in later_paths]
assert len(physical_sources) == 720 and len({SHA(p.read_bytes()) for p in physical_sources}) == 714
pack_sources = {r['source_png'] for p in inverse['packs'].values() for r in p['files'].values()}
assert len(pack_sources) == 613 and len({SHA((ROOT / p).read_bytes()) for p in pack_sources}) == 609
assert len(new_paths) == 28

# Existing diagonal density policy and bytes must stay exact.
for pack in packs:
    for i, expected in [(182, 'b8d65e2ebae36ffef0ab7aa849fa5086134db521590ee6753ff379f525d9ebb9'),
                        (183, 'f420cffc0378b55e957699461fc98727ef26519ea13ac86cb7b7816383e7c873')]:
        assert SHA((ROOT / 'assets/hd/packs' / pack / f'rear-multicannon-p1-bank8-{i}-8.hda').read_bytes()) == expected
        assert f'rear-multicannon-p1-bank8-{i}-4.hda' not in catalog['packs'][pack]['files']
        assert not (ROOT / 'assets/hd/packs' / pack / f'rear-multicannon-p1-bank8-{i}-4.hda').exists()

# Pure-addition inverse preserves every previous field, including historical prose.
inverse.pop(FAMILY)
for row in binding['resources']:
    inverse['source_pngs'].pop(row['hda_sha256'])
    for pack in packs:
        inverse['packs'][pack]['files'].pop(row['filename'])
        inverse['packs'][pack]['count'] -= 1
assert SHA((json.dumps(inverse, indent=2) + '\n').encode()) == provenance['baseline_catalog_sha256'] == BASE_CATALOG
old_assets = {str(p.relative_to(ROOT)): SHA(p.read_bytes()) for p in (ROOT / 'assets').rglob('*')
              if p.is_file() and str(p.relative_to(ROOT)) not in new_paths | later_paths | {'assets/hd/manifest.json'}}
assert len(old_assets) == provenance['old_non_manifest_assets'] == 7065
assert SHA(''.join(p + '\0' + h + '\n' for p, h in sorted(old_assets.items())).encode()) == provenance['old_assets_path_sha256_inventory_digest'] == BASE_ASSETS

with tempfile.TemporaryDirectory(prefix='rear-p5-twins-') as temporary:
    relocated = Path(temporary)
    local_art, local_source = relocated / ART.name, relocated / 'player-rear-multicannon-p1-six-v1/output'
    local_art.mkdir(); local_source.mkdir(parents=True)
    for name in ['build.py', 'inputs.json']:
        shutil.copy2(ART / name, local_art / name)
    for row in pins['resources']:
        for kind in ['png', 'rgba']:
            shutil.copy2(ROOT / row[f'source_{kind}_repo_path'], local_source)
    assert len(list(local_source.iterdir())) == 8
    out, hda = relocated / 'art', relocated / 'hda'
    command = [sys.executable, '-I', str(local_art / 'build.py'), '--output', str(out), '--hda-output', str(hda)]
    subprocess.run(command, check=True, cwd=relocated)
    assert {p.name for p in out.iterdir()} == {p.name for p in (ART / 'output').iterdir()}
    assert {p.name for p in hda.iterdir()} == {row['filename'] for row in binding['resources']}
    for p in out.iterdir():
        assert p.read_bytes() == (ART / 'output' / p.name).read_bytes()
    for row in binding['resources']:
        assert (hda / row['filename']).read_bytes() == (ROOT / row['pack_paths'][0]).read_bytes()
    failed = subprocess.run(command, capture_output=True, text=True, cwd=relocated)
    assert failed.returncode != 0 and 'must not exist' in failed.stderr
    for p in out.iterdir():
        assert p.read_bytes() == (ART / 'output' / p.name).read_bytes()
    # Mutate the last input, so rejection proves no earlier output was written.
    for kind in ['png', 'rgba']:
        bad_input = local_source / f'rear-multi-282-8.{kind}'
        original = bad_input.read_bytes(); bad_input.write_bytes(bytes([original[0] ^ 1]) + original[1:])
        bad_out, bad_hda = relocated / ('rejected-art-' + kind), relocated / ('rejected-hda-' + kind)
        failed = subprocess.run([sys.executable, '-I', str(local_art / 'build.py'), '--output', str(bad_out),
                                 '--hda-output', str(bad_hda)], capture_output=True, text=True, cwd=relocated)
        assert failed.returncode != 0 and f'Accepted {kind.upper()} pin mismatch' in failed.stderr
        assert not bad_out.exists() and not bad_hda.exists()
        bad_input.write_bytes(original)
    for bad_out, bad_hda in [(relocated / 'same', relocated / 'same'),
                             (relocated / 'outer', relocated / 'outer/inner')]:
        failed = subprocess.run([sys.executable, '-I', str(local_art / 'build.py'), '--output', str(bad_out),
                                 '--hda-output', str(bad_hda)], capture_output=True, text=True, cwd=relocated)
        assert failed.returncode != 0 and 'must be separate' in failed.stderr
        assert not bad_out.exists() and not bad_hda.exists()
print('Rear P5 mode2 assets PASS: four selected twins; independent rational pixel equality; eight HDR1 copies; 7065 old assets exact; additive catalog inverse; historical3438 entries/654 source mappings/720 source files/601 default packs preserved after exact later-family projection; isolated relocated rebuild and corrupt-input rejection. Diagnostic runtime remains separately qualified.')
