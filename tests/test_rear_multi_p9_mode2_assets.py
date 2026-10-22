# Counted adapter: imports register a case; the original oracle executes in isolation.
def main():
    #!/usr/bin/env python3
    """Verify reviewed generated rotations, exact additive binding and isolated rebuilds.

    Only accepted generated artwork is read. No original-game pixels, masks,
    indices, palettes, captures or runtime fixtures are required by this test.
    """
    from pathlib import Path
    from collections import Counter
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
    from rear_multi_p9_mode2_asset_projection import project_p9_mode2, FAMILY, PACKAGE, BASE

    ROOT = Path(__file__).resolve().parents[1]
    ART = ROOT / PACKAGE
    SHA = lambda b: hashlib.sha256(b).hexdigest()
    REVIEW = '34cc9eb9117a7311d77804f0a3617ee877033b7abb7dfa06022bc2211d1de6ba'
    OLD_ASSETS = '227dca6eff2d4ccb31fbcace85e382db670a75a8a3ef3aaf8e94e2ad562335c2'
    EXPECTED = {'README.md', 'build.py', 'inputs.json', 'binding.json', 'file-manifest.json',
                'output/build-receipt.json'}
    EXPECTED |= {f'accepted-generated/rear-multi-{i}-{d}.{ext}'
                 for i in [277, 278] for d in [4, 8] for ext in ['png', 'rgba']}
    EXPECTED |= {f'output/rear-multi-p9-{i}-{d}.{ext}'
                 for i in [298, 299] for d in [4, 8] for ext in ['png', 'rgba', 'hda']}
    assert len(EXPECTED) == 26
    assert {str(p.relative_to(ART)) for p in ART.rglob('*') if p.is_file()} == EXPECTED
    assert not any(p.is_symlink() for p in ART.rglob('*'))

    catalog = json.loads((ROOT / 'assets/hd/manifest.json').read_text())
    catalog_saved = copy.deepcopy(catalog)
    baseline, newpaths = project_p9_mode2(ROOT, catalog)
    assert catalog == catalog_saved and len(newpaths) == 38
    assert SHA((json.dumps(baseline, indent=2) + '\n').encode()) == BASE
    from accepted_later_changes import project_p9_asset_inventory
    old = {n: h for n,h in project_p9_asset_inventory(ROOT).items() if n not in newpaths | {'assets/hd/manifest.json'}}
    assert len(old) == 7187
    assert SHA(''.join(n + '\0' + h + '\n' for n, h in sorted(old.items())).encode()) == OLD_ASSETS
    assert all(p['count'] == len(p['files']) for p in catalog['packs'].values())
    assert project_p9_mode2(ROOT, baseline) == (baseline, set())
    binding = json.loads((ART / 'binding.json').read_text())
    inputs = json.loads((ART / 'inputs.json').read_text())
    receipt = json.loads((ART / 'output/build-receipt.json').read_text())
    assert SHA((ART / 'output/build-receipt.json').read_bytes()) == REVIEW
    assert binding['reviewed_build_receipt_sha256'] == REVIEW
    assert binding['phase_sequence'] == [277, 278, 295, 294, 77, 298, 299]
    assert binding['logical_size'] == [12, 14] and binding['anchor'] == [0, 0]
    assert inputs['baseline_commit'] == 'be3df38ee5b7c64627c86e0630faa894a8ee0f1e'
    assert inputs['baseline_tree'] == 'e798190fc72eef8d6bfc25b2770f21fb80dc1a24'
    assert receipt['mapping'] == binding['coordinate_mapping'] == {
        '298': ['y', '14*d-1-x'], '299': ['12*d-1-y', '14*d-1-x']}
    assert [(r['id'], r['density']) for r in inputs['inputs']] == [(277, 4), (277, 8), (278, 4), (278, 8)]
    assert [(r['id'], r['density']) for r in receipt['outputs']] == [(298, 4), (299, 4), (298, 8), (299, 8)]


    def fnv(raw):
        value = 14695981039346656037
        for b in raw:
            value = ((value ^ b) * 1099511628211) & ((1 << 64) - 1)
        return value


    def pixels(raw):
        return [tuple(raw[p:p + 4]) for p in range(0, len(raw), 4)]


    def stats(raw, d):
        values = pixels(raw)
        supported = [i for i, p in enumerate(values) if p[3]]
        xs = [i % (12 * d) for i in supported]
        ys = [i // (12 * d) for i in supported]
        return {
            'alpha_bounds_exclusive': [min(xs), min(ys), max(xs) + 1, max(ys) + 1],
            'alpha_sum': sum(p[3] for p in values),
            'alpha_nonzero_samples': len(supported),
            'fractional_alpha_samples': sum(0 < p[3] < 255 for p in values),
            'premultiplied_RGB_numerators': [sum(p[c] * p[3] for p in values) for c in range(3)],
            'transparent_black_canonical': all(p == (0, 0, 0, 0) for p in values if not p[3]),
        }


    def check_png(path, raw, d):
        with Image.open(path) as im:
            assert im.mode == 'RGBA' and im.size == (12 * d, 14 * d) and im.tobytes() == raw


    sources = {}
    for row in inputs['inputs']:
        i, d = row['id'], row['density']
        raw = (ART / row['rgba']).read_bytes()
        png = (ART / row['png']).read_bytes()
        assert len(raw) == 12 * 14 * d * d * 4
        assert SHA(raw) == row['rgba_sha256'] and f'{fnv(raw):016x}' == row['rgba_fnv1a64']
        assert SHA(png) == row['png_sha256']
        assert (ROOT / row['accepted_repo_png']).read_bytes() == png
        check_png(ART / row['png'], raw, d)
        for pack in [catalog['default_preview_pack'], catalog['default_debug_pack']]:
            hda = ROOT / 'assets/hd/packs' / pack / f'rear-multicannon-p1-bank8-{i}-{d}.hda'
            assert hda.read_bytes() == struct.pack('<4s6I', b'HDR1', 1310000 + i, d, 12, 14, 0, 0) + raw
            assert SHA(hda.read_bytes()) == row['accepted_hda_sha256']
        sources[i, d] = raw

    payloads, pins = {}, []
    for row in binding['resources']:
        i, d = row['source_id'], row['density']
        w, h = 12 * d, 14 * d
        raw = (ART / row['rgba']).read_bytes()
        hda = (ART / row['package_hda']).read_bytes()
        record = next(r for r in receipt['outputs'] if (r['id'], r['density']) == (i, d))
        assert row['accepted_source_id'] == record['source_id'] == 277
        assert row['role'] == record['role'] == 131 and row['key'] == record['key'] == 1310000 + i
        assert row['logical_size'] == record['logical_size'] == [12, 14]
        assert row['anchor'] == record['anchor'] == [0, 0]
        assert len(raw) == w * h * 4 and SHA(raw) == row['rgba_sha256'] == record['rgba_sha256']
        assert hda == struct.pack('<4s6I', b'HDR1', 1310000 + i, d, 12, 14, 0, 0) + raw
        assert SHA(hda) == row['hda_sha256'] == record['hda_sha256']
        assert SHA((ART / row['png']).read_bytes()) == row['png_sha256'] == record['png_sha256']
        check_png(ART / row['png'], raw, d)
        source = sources[277, d]
        # Inverse target-to-source lookup independently verifies every target cell.
        expected = bytearray()
        for y in range(h):
            for x in range(w):
                sx, sy = h - 1 - y, x if i == 298 else w - 1 - x
                expected += source[4 * (sy * w + sx):4 * (sy * w + sx + 1)] if 0 <= sx < w else bytes(4)
        assert raw == bytes(expected)
        assert Counter(pixels(raw)) == Counter(pixels(source))
        assert source[4 * w * w:] == bytes(4 * w * (h - w))
        assert record['mapped_source_samples'] == 144 * d * d
        assert record['clipped_transparent_black_samples'] == 24 * d * d
        assert record['clipped_nonzero_RGBA_samples'] == 0
        source_stats, output_stats = stats(source, d), stats(raw, d)
        assert source_stats == record['source_stats'] and output_stats == record['output_stats']
        assert output_stats['alpha_bounds_exclusive'] == [v * d for v in ([0, 3, 10, 14] if i == 298 else [2, 3, 12, 14])]
        assert output_stats['transparent_black_canonical'] is True
        for key in ['alpha_sum', 'alpha_nonzero_samples', 'fractional_alpha_samples', 'premultiplied_RGB_numerators']:
            assert output_stats[key] == source_stats[key]
        value = fnv(raw)
        assert f'0x{value:016x}' == row['rgba_fnv1a64'] and f'{value:016x}' == record['rgba_fnv1a64']
        payloads[i, d] = raw
        pins.append(value)
    for d in [4, 8]:
        w, h = 12 * d, 14 * d
        for left, right in [(sources[277, d], sources[278, d]), (payloads[298, d], payloads[299, d])]:
            assert all(left[4 * (y * w + x):4 * (y * w + x + 1)] ==
                       right[4 * (y * w + w - 1 - x):4 * (y * w + w - x)] for y in range(h) for x in range(w))
    macro = (ROOT / 'src/rear_multi_p1_pins.h').read_text().split('#define REAR_P1_RGBA_PINS ', 1)[1].split('\n', 1)[0]
    assert [int(s, 16) for s in re.findall(r'UINT64_C\(0x([0-9a-f]+)\)', macro)][38:42] == pins
    assert pins == [0x061487c852b091c4, 0xfe0fee22f015d496, 0xf997db7d88b22d04, 0xc832a79db1a7d312]
    for p in ART.rglob('*'):
        if p.is_file() and p.suffix in ['.json', '.py', '.md']:
            assert not re.search(r'/workspace/|/home/|sediment://|libfile_|file_000000|ghp_|github_pat_|data:image', p.read_text()), p

    with tempfile.TemporaryDirectory(prefix='rear-p9m2-generated-only-') as temp:
        t = Path(temp)
        core = t / 'core'
        core.mkdir()
        names = ['build.py', 'inputs.json'] + [r[k] for r in inputs['inputs'] for k in ['png', 'rgba']]
        for name in names:
            p = core / name
            p.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ART / name, p)
        def command(out):
            return [sys.executable, '-I', '-B', str(core / 'build.py'), '--output', str(out)]
        for run in range(2):
            out = t / f'rebuild-{run}'
            subprocess.run(command(out), check=True)
            assert {p.name for p in out.iterdir()} == {p.name for p in (ART / 'output').iterdir()}
            for p in out.iterdir():
                assert p.read_bytes() == (ART / 'output' / p.name).read_bytes(), p.name
            frozen = {p.name: SHA(p.read_bytes()) for p in out.iterdir()}
            assert subprocess.run(command(out), capture_output=True).returncode != 0
            assert {p.name: SHA(p.read_bytes()) for p in out.iterdir()} == frozen
        # Every required generated input is pinned and must reject corruption before output creation.
        for n, name in enumerate(names[2:]):
            p = core / name
            saved = p.read_bytes()
            p.write_bytes(bytes([saved[0] ^ 1]) + saved[1:])
            out = t / f'bad-input-{n}'
            assert subprocess.run(command(out), capture_output=True).returncode != 0 and not out.exists()
            p.write_bytes(saved)
        assert not any(p.name == '__pycache__' or p.suffix == '.pyc' for p in t.rglob('*'))
        # A compact fixture exercises projection rejection without changing working-tree assets.
        fixture = t / 'fixture'
        for name in newpaths:
            q = fixture / name
            q.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / name, q)
        assert project_p9_mode2(fixture, catalog) == (baseline, newpaths)
        def rejected(candidate):
            try:
                project_p9_mode2(fixture, candidate)
            except (AssertionError, KeyError, FileNotFoundError):
                return
            raise AssertionError('Tampered additive catalog/package unexpectedly accepted')
        for field in ['scope', 'runtime_qualification', 'reused_resources']:
            bad = copy.deepcopy(catalog)
            bad[FAMILY][field] += ' changed'
            rejected(bad)
        bad = copy.deepcopy(catalog)
        bad['packs'][catalog['default_preview_pack']]['count'] += 1
        rejected(bad)
        bad = copy.deepcopy(catalog)
        bad['source_pngs'][binding['resources'][0]['hda_sha256']]['RGBA_sha256'] = '0' * 64
        rejected(bad)
        row = binding['resources'][0]
        for name in [PACKAGE + '/build.py', PACKAGE + '/file-manifest.json', PACKAGE + '/' + row['rgba'],
                     row['catalog_source_png'], row['pack_paths'][0]]:
            q = fixture / name
            saved = q.read_bytes()
            q.write_bytes(bytes([saved[0] ^ 1]) + saved[1:])
            rejected(catalog)
            q.write_bytes(saved)
        for name in [PACKAGE + '/file-manifest.json', row['catalog_source_png'], row['pack_paths'][0]]:
            q = fixture / name
            saved = q.read_bytes()
            q.unlink()
            q.symlink_to(ROOT / name)
            rejected(catalog)
            q.unlink()
            q.write_bytes(saved)
        extra = fixture / PACKAGE / 'unexpected.bin'
        extra.write_bytes(b'unexpected')
        rejected(catalog)
        extra.unlink()
        assert project_p9_mode2(fixture, catalog) == (baseline, newpaths)

    print('Rear P9 mode2 assets PASS: 38 additive paths; 7187 old assets exact; exact catalog inverse; '
          'four independently verified coordinate transforms; sample/alpha/RGB energy conservation; '
          'full-canvas mirrors; RGBA/PNG/HDR1 payloads and source pins; two isolated relocated rebuilds; '
          'eight corrupt-input and bounded projection tamper controls. Runtime qualification is separate.')

def load_tests(loader,tests,pattern):
    from historical_oracle_support import suite
    return suite(__file__)

if __name__=='__main__':
    main()
