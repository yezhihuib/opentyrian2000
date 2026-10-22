# Counted adapter: imports register a case; the original oracle executes in isolation.
def main():
    #!/usr/bin/env python3
    """Verify reviewed density8-only 182/183, unchanged old assets and additive catalog.

    Uses generated assets only. No original-game pixels, masks or captures are read.
    """
    from pathlib import Path
    import copy
    import hashlib
    import json
    import shutil
    import struct
    import subprocess
    import sys
    import tempfile
    from PIL import Image

    root = Path(__file__).resolve().parents[1]
    art = root / 'assets/hd/artwork/player-rear-multicannon-p4-mode2-down-diagonals-v1'
    old = root / 'assets/hd/artwork/player-front-multi-eight-v1/output'
    sha = lambda b: hashlib.sha256(b).hexdigest()
    reviewed = '244ba2c777b396b2b3bfbba1fd6543821719cc7872767755f85854f2e8fde2c9'
    approved = {
        182: ('85fe7b765089b72f23f1eaaf0449be40f1687fdbb77445fa2c4cb1a26fa7bd65',
              '94ee0b55b1642e1781e72ccf1d0f1570670821fca66e3bcf97a692f06f3bda1c',
              'b8d65e2ebae36ffef0ab7aa849fa5086134db521590ee6753ff379f525d9ebb9',
              '0x888f7807cb7fb1b7'),
        183: ('40c0b2f889e29b8916b2e36f89dce9060a27ba70595f040f519b169a910f252c',
              'c195101ad4685602590f93270b8fc9e14b6b2ab92ed5fc69fd90119298b1cbce',
              'f420cffc0378b55e957699461fc98727ef26519ea13ac86cb7b7816383e7c873',
              '0x79d684e2a12caa1f'),
    }
    manifest = json.loads((art / 'file-manifest.json').read_text())
    expected_package = {'README.md', 'build.py', 'inputs.json', 'binding.json',
                        'provenance.json', 'file-manifest.json', 'output/transform-contract.json'}
    expected_package |= {f'output/rear-multi-p4-{i}-8.{ext}'
                         for i in [182, 183] for ext in ['png', 'rgba']}
    assert {str(p.relative_to(art)) for p in art.rglob('*') if p.is_file()} == expected_package
    assert set(manifest['files']) == expected_package - {'file-manifest.json'}
    for name, pin in manifest['files'].items():
        assert not (art / name).is_symlink() and sha((art / name).read_bytes()) == pin, name
    binding = json.loads((art / 'binding.json').read_text())
    pins = json.loads((art / 'inputs.json').read_text())
    contract = json.loads((art / 'output/transform-contract.json').read_text())
    provenance = json.loads((art / 'provenance.json').read_text())
    assert binding['role'] == 131 and binding['logical_size'] == [12, 14]
    assert binding['anchor'] == [0, 0] and binding['reviewed_export_sha256'] == reviewed
    assert pins['reviewed_export_sha256'] == contract['reviewed_export_sha256'] == reviewed
    assert provenance['reviewed_generated_only_export']['sha256'] == reviewed
    assert provenance['original_game_pixels_masks_palettes_or_captures_bundled'] is False
    assert provenance['published_input_baseline'] == {
        'commit': '3b398429ffa4f3e9250d1bd02cc22dab16fc28ad',
        'tree': '136ea6b0e3418a60b4634974939130ea6969a38f'}
    assert binding['scope'] == pins['scope'] == contract['scope']
    for key in ['inputs', 'builder', 'transform_contract']:
        assert sha((art / binding[key]).read_bytes()) == binding[key + '_sha256']
    assert all(value is False for value in contract['constraints'].values())
    assert contract['transform'] == 'whole_canvas_flip_y'
    assert contract['translation_logical_xy'] == [0, 0]
    for obj in [pins, binding, contract]:
        assert [(a['accepted_source_id'], a['source_id'], a['density'], a['key'])
                for a in obj['resources']] == [(163, 182, 8, 1310182), (164, 183, 8, 1310183)]
    catalog = json.loads((root / 'assets/hd/manifest.json').read_text())
    from rear_multi_p7_asset_projection import project_p7
    from rear_multi_p7_mode2_asset_projection import project_p7_mode2
    from rear_multi_p9_mode2_asset_projection import project_p9_mode2
    catalog, p9_mode2_paths = project_p9_mode2(root, catalog)
    catalog, p7_mode2_paths = project_p7_mode2(root, catalog)
    p7_mode2_paths |= p9_mode2_paths
    catalog, p7_paths = project_p7(root, catalog)
    p7_paths |= p7_mode2_paths
    family_name = 'player_rear_multicannon_p4_mode2_down_diagonals_v1'
    family = catalog[family_name]
    assert family['source'] == str(art.relative_to(root))
    assert family['binding_sha256'] == sha((art / 'binding.json').read_bytes())
    assert family['art_file_manifest_sha256'] == sha((art / 'file-manifest.json').read_bytes())
    assert family['provenance_sha256'] == sha((art / 'provenance.json').read_bytes())
    assert family['reviewed_export_sha256'] == reviewed and family['scope'] == binding['scope']
    assert family['ids'] == [182, 183] and family['densities'] == [8] and family['role'] == 131
    assert 'historical mode1' in family['historical_down77_scope']
    packs = {catalog['default_preview_pack'], catalog['default_debug_pack']}
    new_paths = {str(art.relative_to(root) / name) for name in expected_package}
    for a, pin, transformed in zip(binding['resources'], pins['resources'], contract['resources']):
        i, source_id = a['source_id'], a['accepted_source_id']
        assert all(a[k] == v and transformed[k] == v for k, v in pin.items())
        assert a['role'] == 131 and a['logical_size'] == [12, 14] and a['anchor'] == [0, 0]
        assert a['filename'] == f'rear-multicannon-p1-bank8-{i}-8.hda'
        assert tuple(a[k] for k in ['png_sha256', 'rgba_sha256', 'hda_sha256', 'rgba_fnv1a64']) == approved[i]
        raw = (art / a['rgba']).read_bytes()
        png = (art / a['png']).read_bytes()
        assert len(raw) == 96 * 112 * 4 and sha(raw) == a['rgba_sha256']
        assert sha(png) == a['png_sha256']
        with Image.open(art / a['png']) as im:
            assert im.mode == 'RGBA' and im.size == (96, 112) and im.tobytes() == raw
        source_path = root / pin['source_png_repo_path']
        assert source_path == old / f'bullet-{source_id}-8.png'
        assert sha(source_path.read_bytes()) == pin['source_png_sha256']
        with Image.open(source_path) as im:
            assert im.mode == 'RGBA' and im.size == (96, 112)
            source = im.tobytes()
        assert sha(source) == pin['source_rgba_sha256']
        # Independent row reversal, without Pillow transpose or builder's pixel mapping.
        assert raw == b''.join(source[y * 384:(y + 1) * 384] for y in range(111, -1, -1))
        assert sorted(source[p:p + 4] for p in range(0, len(source), 4)) == sorted(
            raw[p:p + 4] for p in range(0, len(raw), 4))
        assert sorted(source[3::4]) == sorted(raw[3::4])
        assert any(0 < alpha < 255 for alpha in raw[3::4])
        for c in range(3):
            assert sum(source[p + c] * source[p + 3] for p in range(0, len(source), 4)) == sum(
                raw[p + c] * raw[p + 3] for p in range(0, len(raw), 4))
        checks = transformed['checks']
        assert checks['full_RGBA_coordinate_mapping_equal'] is True
        assert checks['mapped_source_samples'] == 10752 and checks['clipped_source_samples'] == 0
        assert checks['all_source_RGBA_samples_preserved'] is True
        assert checks['full_density_alpha_RGB_energy_exact'] is True
        stamp = 14695981039346656037
        for byte in raw:
            stamp = ((stamp ^ byte) * 1099511628211) & ((1 << 64) - 1)
        assert a['rgba_fnv1a64'] == f'0x{stamp:016x}'
        assert len(a['pack_paths']) == 2
        assert {Path(n).parent.name for n in a['pack_paths']} == packs
        for name in a['pack_paths']:
            path = root / name
            hda = path.read_bytes()
            assert len(hda) == a['hda_bytes'] == 43036 and sha(hda) == a['hda_sha256']
            assert struct.unpack('<4s6I', hda[:28]) == (b'HDR1', 1310000 + i, 8, 12, 14, 0, 0)
            assert hda[28:] == raw
            row = catalog['packs'][path.parent.name]['files'][path.name]
            assert row == {'sha256': a['hda_sha256'], 'header_u32': [1310000 + i, 8, 12, 14, 0, 0],
                           'source_png': a['catalog_source_png'], 'source_png_sha256': a['png_sha256']}
            assert (root / row['source_png']).read_bytes() == png
            new_paths.add(name)
        assert catalog['source_pngs'][a['hda_sha256']] == {
            'path': a['catalog_source_png'], 'sha256': a['png_sha256'], 'RGBA_sha256': a['rgba_sha256']}
        new_paths.add(a['catalog_source_png'])
        for pack, value in catalog['packs'].items():
            assert value['count'] == len(value['files'])
            if pack not in packs:
                assert a['filename'] not in value['files']
                assert not (root / 'assets/hd/packs' / pack / a['filename']).exists()
            # Exact availability: no new dedicated163/164, no d4 diagonal, no generic182/183.
            for forbidden in [f'rear-multicannon-p1-bank8-{i}-4.hda',
                              f'rear-multicannon-p1-bank8-{source_id}-4.hda',
                              f'rear-multicannon-p1-bank8-{source_id}-8.hda',
                              f'bullet-{source_id}-4.hda', f'bullet-{i}-4.hda', f'bullet-{i}-8.hda']:
                assert forbidden not in value['files']
                assert not (root / 'assets/hd/packs' / pack / forbidden).exists()
    assert family['entries'] == [{'id': a['source_id'], 'density': 8, 'HDA_sha256': a['hda_sha256']}
                                 for a in binding['resources']]

    # Explicitly retain generic163/164 HDA headers/payloads and both accepted77 densities.
    old_hda_pins = {
        'bullet-163-8.hda': ('f8428cf165a109387b33ebc70669adcb45bdf92b8d171d482a5c07efe8ad7687', 80163, 8),
        'bullet-164-8.hda': ('1db3c3883bc1980bb2a41c00e72122280d180682d5754d35378cec47a0fdaaf5', 80164, 8),
        'rear-multicannon-p1-bank8-77-4.hda': ('bf3629986d6d977a4032c8dbb58ddcf89d476c606efe0b6e6f198b998340bc4a', 1310077, 4),
        'rear-multicannon-p1-bank8-77-8.hda': ('54c1fb786e1724bad5f47326fab8ce6fce325e2197a8861675682a8912bd8678', 1310077, 8),
    }
    for pack in packs:
        for name, (pin, key, density) in old_hda_pins.items():
            hda = (root / 'assets/hd/packs' / pack / name).read_bytes()
            assert sha(hda) == pin
            assert struct.unpack('<4s6I', hda[:28]) == (b'HDR1', key, density, 12, 14, 0, 0)
            assert catalog['packs'][pack]['files'][name]['sha256'] == pin

    # Later P5 twins are an explicitly bounded additive family. Remove only those
    # verified additions before retaining this historical P4 inverse and inventory.
    later_paths = set(p7_paths)
    inverse = copy.deepcopy(catalog)
    # The later P5 mode1 triples are a separately verified, exact additive family.
    # Strip only its bounded 29 new paths before preserving the historical hashes.
    triple_name = 'player_rear_multicannon_p5_mode1_triples_v1'
    if triple_name in inverse:
        triple = inverse.pop(triple_name)
        assert triple['source'] == 'assets/hd/artwork/player-rear-multicannon-p5-mode1-triples-v1'
        assert triple['ids'] == [3, 41] and triple['densities'] == [4, 8] and triple['role'] == 131
        assert triple['reviewed_component_manifest_sha256'] == '3f058e0cd432a9041298b095ac0911efa46a0a9cf8e06dba6ed67f82cb647fb1'
        triple_art = root / triple['source']
        triple_binding = json.loads((triple_art / 'binding.json').read_text())
        triple_manifest = json.loads((triple_art / 'file-manifest.json').read_text())
        assert sha((triple_art / 'binding.json').read_bytes()) == triple['binding_sha256']
        assert sha((triple_art / 'file-manifest.json').read_bytes()) == triple['art_file_manifest_sha256']
        triple_expected = {'build.py', 'build_components.py', 'README.md', 'inputs.json', 'frozen-inputs.json',
                           'binding.json', 'provenance.json', 'output/component-manifest.json'}
        triple_expected |= {f'output/rear-multi-{i}-{d}-exact-clipped-union.{ext}'
                            for i in [3, 41] for d in [4, 8] for ext in ['png', 'rgba']}
        assert set(triple_manifest['files']) == triple_expected
        assert {str(p.relative_to(triple_art)) for p in triple_art.rglob('*') if p.is_file()} == triple_expected | {'file-manifest.json'}
        for name, pin in triple_manifest['files'].items():
            assert sha((triple_art / name).read_bytes()) == pin
            later_paths.add(str(triple_art.relative_to(root) / name))
        later_paths.add(str(triple_art.relative_to(root) / 'file-manifest.json'))
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
        assert len(later_paths) == 29 + len(p7_paths)
        assert sha((json.dumps(inverse, indent=2) + '\n').encode()) == '71e3e7a1a0afdfac7232573ed20be0111d891d33360b7884d1c8bd088731000a'
    later_name = 'player_rear_multicannon_p5_mode2_twins_v1'
    if later_name in inverse:
        later = inverse.pop(later_name)
        assert later['ids'] == [277, 278] and later['densities'] == [4, 8] and later['role'] == 131
        assert later['reviewed_export_sha256'] == 'cd83131544d3d7163327e089bac6fa6fbd51535da800b4115fe58361b238a2dc'
        later_art = root / later['source']
        later_binding = json.loads((later_art / 'binding.json').read_text())
        later_manifest = json.loads((later_art / 'file-manifest.json').read_text())
        assert sha((later_art / 'binding.json').read_bytes()) == later['binding_sha256']
        assert sha((later_art / 'file-manifest.json').read_bytes()) == later['art_file_manifest_sha256']
        assert [(a['source_id'], a['density']) for a in later_binding['resources']] == [(277, 4), (277, 8), (278, 4), (278, 8)]
        for name, pin in later_manifest['files'].items():
            assert sha((later_art / name).read_bytes()) == pin
            later_paths.add(str(later_art.relative_to(root) / name))
        later_paths.add(str(later_art.relative_to(root) / 'file-manifest.json'))
        for a in later_binding['resources']:
            assert inverse['source_pngs'].pop(a['hda_sha256']) == {'path': a['catalog_source_png'], 'sha256': a['png_sha256'], 'RGBA_sha256': a['rgba_sha256']}
            later_paths.add(a['catalog_source_png'])
            for pack in packs:
                row = inverse['packs'][pack]['files'].pop(a['filename'])
                assert row['sha256'] == a['hda_sha256'] and row['header_u32'] == [1310000 + a['source_id'], a['density'], 12, 14, 0, 0]
                inverse['packs'][pack]['count'] -= 1
                later_paths.add(str(Path('assets/hd/packs') / pack / a['filename']))
        assert sha((json.dumps(inverse, indent=2) + '\n').encode()) == 'f1ceac8430b7419a62d62d957081bf630339150c6efd80615cdfae7eea4013b9'
    # Pure-addition P4 inverse: no historical binding/scope prose was rewritten.
    inverse.pop(family_name)
    for a in binding['resources']:
        inverse['source_pngs'].pop(a['hda_sha256'])
        for pack in packs:
            inverse['packs'][pack]['files'].pop(a['filename'])
            inverse['packs'][pack]['count'] -= 1
    assert sha((json.dumps(inverse, indent=2) + '\n').encode()) == 'a0acd4f9bbf2f258cfd2b4168d0bd7cfba224848b012ffddf0c0d747de0239f9'
    from accepted_later_changes import project_p9_asset_inventory
    old_assets = {n: h for n,h in project_p9_asset_inventory(root).items() if n not in new_paths | later_paths | {'assets/hd/manifest.json'}}
    assert len(old_assets) == provenance['old_non_manifest_assets'] == 7048
    old_inventory_hash = sha(''.join(p + '\0' + h + '\n' for p, h in sorted(old_assets.items())).encode())
    assert old_inventory_hash == provenance['old_assets_path_sha256_inventory_digest'] == '0fb686ecaa7d78d35579c37431d569e262079bc74cae1644276747083e6a945f'

    with tempfile.TemporaryDirectory(prefix='rear-p4-mode2-art-') as temporary:
        relocated = Path(temporary)
        local_art = relocated / art.name
        local_source = relocated / 'player-front-multi-eight-v1/output'
        local_art.mkdir()
        local_source.mkdir(parents=True)
        for name in ['build.py', 'inputs.json']:
            shutil.copy2(art / name, local_art / name)
        for i in [163, 164]:
            shutil.copy2(old / f'bullet-{i}-8.png', local_source)
        out, hda = relocated / 'art', relocated / 'hda'
        command = [sys.executable, str(local_art / 'build.py'), '--output', str(out), '--hda-output', str(hda)]
        subprocess.run(command, check=True)
        assert {p.name for p in out.iterdir()} == {p.name for p in (art / 'output').iterdir()}
        assert {p.name for p in hda.iterdir()} == {a['filename'] for a in binding['resources']}
        for p in out.iterdir():
            assert p.read_bytes() == (art / 'output' / p.name).read_bytes()
        for a in binding['resources']:
            assert (hda / a['filename']).read_bytes() == (root / a['pack_paths'][0]).read_bytes()
        # Reject an existing destination before writing anything.
        fail = subprocess.run(command, capture_output=True, text=True)
        assert fail.returncode != 0 and 'must not exist' in fail.stderr
        for p in out.iterdir():
            assert p.read_bytes() == (art / 'output' / p.name).read_bytes()
        # Reject a corrupt source before creating either destination.
        broken = local_source / 'bullet-163-8.png'
        broken.write_bytes(b'\1' + broken.read_bytes()[1:])
        bad_out, bad_hda = relocated / 'rejected-art', relocated / 'rejected-hda'
        fail = subprocess.run([sys.executable, str(local_art / 'build.py'), '--output', str(bad_out),
                               '--hda-output', str(bad_hda)], capture_output=True, text=True)
        assert fail.returncode != 0 and 'Accepted PNG pin mismatch' in fail.stderr
        assert not bad_out.exists() and not bad_hda.exists()
    print('Rear P4 mode2: approved density8-only182/183, exact flip/RGBA/alpha/energy, four HDR1 copies, unchanged generic163/164 and77, all7048 old assets, additive catalog inverse, relocated rebuild and safe rejection PASS')

def load_tests(loader,tests,pattern):
    from historical_oracle_support import suite
    return suite(__file__)

if __name__=='__main__':
    main()
