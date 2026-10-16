#!/usr/bin/env python3
"""Verify bounded down77 art, unchanged accepted inputs, packs and fresh rebuild.

Reads generated assets only. No original-game data, masks or captures are used.
"""
from pathlib import Path
import hashlib
import json
import re
import shutil
import struct
import subprocess
import sys
import tempfile
from PIL import Image

root = Path(__file__).resolve().parents[1]
art = root / 'assets/hd/artwork/player-rear-multicannon-p4-mode1-down77-v1'
old = root / 'assets/hd/artwork/player-rear-multicannon-p1-six-v1/output'
sha = lambda b: hashlib.sha256(b).hexdigest()
reviewed = '244ba2c777b396b2b3bfbba1fd6543821719cc7872767755f85854f2e8fde2c9'
approved = {
    4: ('611c9ef986c93eeb2bbd90ea51ef55d9f97986c24c9c89714eeee7875d399084',
        '346271300e8e6f9739a88882dad83ddc01c067bcd6e1c1f89176783f345dffc6'),
    8: ('8d397c99b1f3f96a2e4cb98dac7988c6477102a6b3ef3110fa2e4ac5ca15b55d',
        '73fe11a2f4926504850b406552c9a720919306a15a7313b2c5eff09c8df15362'),
}
manifest = json.loads((art / 'file-manifest.json').read_text())
expected_package = {'README.md', 'build.py', 'inputs.json', 'binding.json',
                    'file-manifest.json', 'output/transform-contract.json'}
expected_package |= {f'output/rear-multi-p4-77-{d}.{ext}'
                     for d in [4, 8] for ext in ['png', 'rgba']}
assert {str(p.relative_to(art)) for p in art.rglob('*') if p.is_file()} == expected_package
assert set(manifest['files']) == expected_package - {'file-manifest.json'}
for name, pin in manifest['files'].items():
    assert not (art / name).is_symlink() and sha((art / name).read_bytes()) == pin, name
binding = json.loads((art / 'binding.json').read_text())
pins = json.loads((art / 'inputs.json').read_text())
contract = json.loads((art / 'output/transform-contract.json').read_text())
assert binding['role'] == 131 and binding['logical_size'] == [12, 14]
assert binding['anchor'] == [0, 0] and binding['reviewed_export_sha256'] == reviewed
assert pins['reviewed_export_sha256'] == contract['reviewed_export_sha256'] == reviewed
assert binding['scope'] == pins['scope'] == contract['scope']
for key in ['inputs', 'builder', 'transform_contract']:
    assert sha((art / binding[key]).read_bytes()) == binding[key + '_sha256']
assert all(value is False for value in contract['constraints'].values())
assert [a['density'] for a in pins['resources']] == [4, 8]
assert [a['density'] for a in binding['resources']] == [4, 8]
assert [a['density'] for a in contract['resources']] == [4, 8]
catalog = json.loads((root / 'assets/hd/manifest.json').read_text())
family = catalog['player_rear_multicannon_p4_mode1_down77_v1']
assert family['source'] == str(art.relative_to(root))
assert family['binding_sha256'] == sha((art / 'binding.json').read_bytes())
assert family['art_file_manifest_sha256'] == sha((art / 'file-manifest.json').read_bytes())
assert family['reviewed_export_sha256'] == reviewed and family['scope'] == binding['scope']
assert family['ids'] == [77] and family['densities'] == [4, 8] and family['role'] == 131
packs = {catalog['default_preview_pack'], catalog['default_debug_pack']}
stamps = []
for a, pin, transformed in zip(binding['resources'], pins['resources'], contract['resources']):
    d = a['density']
    assert all(a[k] == v and transformed[k] == v for k, v in pin.items())
    assert a['source_id'] == 77 and a['accepted_source_id'] == 1 and a['key'] == 1310077
    assert a['role'] == 131 and a['logical_size'] == [12, 14] and a['anchor'] == [0, 0]
    assert a['filename'] == f'rear-multicannon-p1-bank8-77-{d}.hda'
    assert a['png_sha256'] == approved[d][0] and a['rgba_sha256'] == approved[d][1]
    raw = (art / a['rgba']).read_bytes()
    assert len(raw) == 12 * 14 * d * d * 4 and sha(raw) == a['rgba_sha256']
    assert sha((art / a['png']).read_bytes()) == a['png_sha256']
    with Image.open(art / a['png']) as im:
        assert im.mode == 'RGBA' and im.size == (12 * d, 14 * d) and im.tobytes() == raw
    source = (old / f'rear-multi-1-{d}.rgba').read_bytes()
    assert sha(source) == pin['source_rgba_sha256']
    assert sha((old / f'rear-multi-1-{d}.png').read_bytes()) == pin['source_png_sha256']
    w, h = 12 * d, 14 * d
    # Independent inverse mapping, rather than the builder's transpose or forward loop.
    expected = bytearray(len(raw))
    for y in range(h):
        for x in range(w):
            sx, sy = y - 2 * d, h - 1 - x - 2 * d
            if 0 <= sx < w and 0 <= sy < h:
                dst, src = 4 * (y * w + x), 4 * (sy * w + sx)
                expected[dst:dst + 4] = source[src:src + 4]
    assert bytes(expected) == raw
    assert sum(source[3::4]) == sum(raw[3::4])
    assert sorted(source[p:p + 4] for p in range(0, len(source), 4) if any(source[p:p + 4])) == sorted(
        raw[p:p + 4] for p in range(0, len(raw), 4) if any(raw[p:p + 4]))
    for c in range(3):
        assert sum(source[p + c] * source[p + 3] for p in range(0, len(source), 4)) == sum(
            raw[p + c] * raw[p + 3] for p in range(0, len(raw), 4))
    assert any(0 < a < 255 for a in raw[3::4])
    checks = transformed['checks']
    assert checks['full_RGBA_coordinate_mapping_equal'] is True
    assert checks['clipped_nonzero_RGBA_samples'] == 0
    assert checks['all_supported_source_RGBA_samples_preserved'] is True
    assert checks['full_density_alpha_RGB_energy_exact'] is True
    stamp = 14695981039346656037
    for byte in raw:
        stamp = ((stamp ^ byte) * 1099511628211) & ((1 << 64) - 1)
    assert a['rgba_fnv1a64'] == f'0x{stamp:016x}'
    stamps.append(stamp)
    assert len(a['pack_paths']) == 2
    assert {Path(n).parent.name for n in a['pack_paths']} == packs
    for name in a['pack_paths']:
        path = root / name
        hda = path.read_bytes()
        assert len(hda) == a['hda_bytes'] and sha(hda) == a['hda_sha256']
        assert struct.unpack('<4s6I', hda[:28]) == (b'HDR1', 1310077, d, 12, 14, 0, 0)
        assert hda[28:] == raw
        row = catalog['packs'][path.parent.name]['files'][path.name]
        assert row == {'sha256': a['hda_sha256'], 'header_u32': [1310077, d, 12, 14, 0, 0],
                       'source_png': a['catalog_source_png'], 'source_png_sha256': a['png_sha256']}
        assert (root / row['source_png']).read_bytes() == (art / a['png']).read_bytes()
    assert catalog['source_pngs'][a['hda_sha256']] == {
        'path': a['catalog_source_png'], 'sha256': a['png_sha256'], 'RGBA_sha256': a['rgba_sha256']}
    for pack, value in catalog['packs'].items():
        assert value['count'] == len(value['files'])
        if pack not in packs:
            assert a['filename'] not in value['files']
            assert not (root / 'assets/hd/packs' / pack / a['filename']).exists()
assert family['entries'] == [{'id': 77, 'density': a['density'], 'HDA_sha256': a['hda_sha256']}
                             for a in binding['resources']]
runtime = (root / 'src/rear_multi_p1_pins.h').read_text().split('#define REAR_P1_RGBA_PINS ', 1)[1].split('\n', 1)[0]
values = [int(x, 16) for x in re.findall(r'UINT64_C\(0x([0-9a-f]+)\)', runtime)]
assert len(values) == 18 and values[16:] == stamps
with tempfile.TemporaryDirectory(prefix='rear-p4-mode1-art-') as temporary:
    relocated = Path(temporary)
    local_art = relocated / art.name
    local_source = relocated / 'player-rear-multicannon-p1-six-v1/output'
    local_art.mkdir()
    local_source.mkdir(parents=True)
    for name in ['build.py', 'inputs.json']:
        shutil.copy2(art / name, local_art / name)
    for d in [4, 8]:
        for ext in ['png', 'rgba']:
            shutil.copy2(old / f'rear-multi-1-{d}.{ext}', local_source)
    out, hda = relocated / 'art', relocated / 'hda'
    command = [sys.executable, str(local_art / 'build.py'), '--output', str(out), '--hda-output', str(hda)]
    subprocess.run(command, check=True)
    assert {p.name for p in out.iterdir()} == {p.name for p in (art / 'output').iterdir()}
    assert {p.name for p in hda.iterdir()} == {a['filename'] for a in binding['resources']}
    for p in out.iterdir():
        assert p.read_bytes() == (art / 'output' / p.name).read_bytes()
    for a in binding['resources']:
        assert (hda / a['filename']).read_bytes() == (root / a['pack_paths'][0]).read_bytes()
    # Fail safely without altering either an existing destination or bad inputs.
    fail = subprocess.run(command, capture_output=True, text=True)
    assert fail.returncode != 0 and 'must not exist' in fail.stderr
    broken = local_source / 'rear-multi-1-4.rgba'
    broken.write_bytes(b'\1' + broken.read_bytes()[1:])
    bad_out, bad_hda = relocated / 'rejected-art', relocated / 'rejected-hda'
    fail = subprocess.run([sys.executable, str(local_art / 'build.py'), '--output', str(bad_out),
                           '--hda-output', str(bad_hda)], capture_output=True, text=True)
    assert fail.returncode != 0 and 'Accepted RGBA pin mismatch' in fail.stderr
    assert not bad_out.exists() and not bad_hda.exists()
print('Rear P4 mode1: exact approved down77 d4/d8, unchanged R2 inputs, RGBA/alpha/energy preservation, four HDR1 copies, catalog/runtime pins, relocated rebuild and safe input rejection PASS')
