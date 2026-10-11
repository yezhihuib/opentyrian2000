#!/usr/bin/env python3
"""Rebuild exact purple13 v3, then apply three generated fringe strips for v4."""
from pathlib import Path
from PIL import Image, __version__ as pillow_version
import argparse
import json
import platform
import runpy
import shutil
import subprocess
import sys

common = runpy.run_path(str(Path(__file__).resolve().with_name('reconstruct_v3.py')))
IDS, FRINGE_IDS, TONE_IDS = [common[k] for k in ('IDS', 'FRINGE_IDS', 'TONE_IDS')]
require, sha, rgba, hda, snapshot = [common[k] for k in ('require', 'sha', 'rgba', 'hda', 'snapshot')]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-root', type=Path, required=True)
    args = parser.parse_args()
    package = Path(__file__).resolve().parent.parent
    source = package / 'source'
    output = args.output_root.resolve()
    require(not output.exists(), 'Output root must be a new directory')
    require(output != package and package not in output.parents,
            'Output root must be outside the immutable source package')
    require(not any(p.is_symlink() for p in package.rglob('*')), 'Package cannot contain symlinks')
    before = snapshot(package)
    contract = json.loads((source / 'rebuild-contract.json').read_text())
    require(contract['v3_contract_sha256'] == common['V3_CONTRACT_SHA'] and
            contract['v3_manifest_sha256'] == common['V3_MANIFEST_SHA'], 'Baseline contract differs')
    require(contract['selected_manifest_sha256'] == common['V4_MANIFEST_SHA'] ==
            sha((package / 'runtime-overlay/manifest.json').read_bytes()), 'Frozen v4 manifest differs')
    require({f.name for f in (package / 'output').iterdir()} ==
            {f'terrain-shapesz-{i}-8.png' for i in IDS}, 'Selected PNG scope differs')
    require({f.name for f in (package / 'runtime-overlay').iterdir()} ==
            {'manifest.json'} | {f'terrain-shapesz-{i}-8.hda' for i in IDS}, 'Selected HDA scope differs')
    require({f.name for f in source.glob('generated-fringe-*.png')} ==
            {f'generated-fringe-terrain-{i}.png' for i in FRINGE_IDS}, 'Fringe PNG source scope differs')
    inventory_verified = False
    inventory = package / 'handoff-inventory.json'
    if inventory.exists():
        inventory_data = json.loads(inventory.read_text())
        rows = inventory_data['files']
        require(len({r['path'] for r in rows}) == len(rows), 'Duplicate inventory paths')
        require({r['path'] for r in rows} == set(before) - {'handoff-inventory.json'}, 'Inventory file scope differs')
        require(len(rows) == inventory_data['file_count_excluding_inventory'] and
                sum(r['bytes'] for r in rows) == inventory_data['total_bytes_excluding_inventory'],
                'Inventory totals differ')
        for row in rows:
            file = package / row['path']
            require(file.stat().st_size == row['bytes'] and sha(file.read_bytes()) == row['sha256'],
                    'Inventory bytes or hash differs: ' + row['path'])
        inventory_verified = True
    for directory in ('work', 'output', 'runtime-overlay'):
        (output / directory).mkdir(parents=True)
    baseline, baseline_report = common['reconstruct'](package, output / 'work/v3')
    require(sha((source / 'apply_fringe_strip.cpp').read_bytes()) == contract['native_fringe_helper_sha256'],
            'Frozen fringe helper differs')
    compiler = shutil.which('c++')
    require(compiler is not None, 'A C++17 compiler available as c++ is required')
    executable = output / 'work/apply_fringe_strip'
    subprocess.run([compiler, '-O2', '-std=c++17', str(source / 'apply_fringe_strip.cpp'),
                    '-o', str(executable)], check=True)
    require([r['id'] for r in contract['fringe_strips']] == FRINGE_IDS, 'Fringe source scope differs')
    rebuilt = dict(baseline)
    for row in contract['fringe_strips']:
        tile = row['id']
        expected_path = f'source/generated-fringe-terrain-{tile}.png'
        require(row['path'] == expected_path and row['pixel_size'] == [192, 16], 'Strip path or geometry differs')
        strip_path = package / expected_path
        strip = rgba(strip_path, (192, 16))
        require(sha(strip_path.read_bytes()) == row['file_sha256'] and sha(strip) == row['rgba_sha256'],
                f'Canonical fringe strip differs: {tile}')
        original_raw, strip_raw, result_raw = [output / 'work' / f'{tile}-{suffix}.rgba'
                                              for suffix in ('v3', 'strip', 'v4')]
        original_raw.write_bytes(baseline[tile]); strip_raw.write_bytes(strip)
        subprocess.run([str(executable), str(original_raw), str(strip_raw), str(result_raw)], check=True)
        raw = result_raw.read_bytes()
        require(len(raw) == 172032, f'Fringe output length differs: {tile}')
        require(raw[:208 * 192 * 4] == baseline[tile][:208 * 192 * 4] and
                raw[3::4] == baseline[tile][3::4], f'Fringe helper exceeded scope: {tile}')
        rebuilt[tile] = raw
    results = []
    for row in contract['items']:
        tile = row['id']; stem = f'terrain-shapesz-{tile}-8'
        require(sha(baseline[tile]) == row['v3_rgba_sha256'], f'Intermediate v3 differs: {tile}')
        raw = rebuilt[tile]
        committed_png = package / 'output' / (stem + '.png')
        committed_hda = package / 'runtime-overlay' / (stem + '.hda')
        require(sha(committed_png.read_bytes()) == row['selected_png_sha256'], f'Frozen selected PNG hash differs: {tile}')
        require(rgba(committed_png) == raw and sha(raw) == row['selected_rgba_sha256'], f'Rebuilt RGBA differs: {tile}')
        if tile not in FRINGE_IDS:
            require(sha(committed_png.read_bytes()) == row['v3_png_sha256'] and raw == baseline[tile],
                    f'Committed unchanged v3 PNG differs: {tile}')
        png = output / 'output' / (stem + '.png')
        if tile in TONE_IDS:
            Image.frombytes('RGBA', (192, 224), raw).save(png)
        else:
            shutil.copyfile(source / 'generated-crops' / (stem + '.png'), png)
        require(rgba(png) == raw, f'Generated PNG RGBA differs: {tile}')
        payload = hda(tile, raw)
        require(payload == committed_hda.read_bytes() and sha(payload) == row['selected_hda_sha256'],
                f'Rebuilt HDA differs: {tile}')
        (output / 'runtime-overlay' / (stem + '.hda')).write_bytes(payload)
        results.append({'id': tile, 'slot': row['slot'], 'intermediate_v3_rgba_and_hda_exact': True,
                        'committed_selected_png_hash_verified': True, 'selected_png_sha256': row['selected_png_sha256'],
                        'regenerated_png_sha256': sha(png.read_bytes()),
                        'regenerated_png_file_exact': png.read_bytes() == committed_png.read_bytes(),
                        'rgba_sha256': sha(raw), 'rgba_exact': True, 'hda_sha256': sha(payload), 'hda_file_exact': True})
    shutil.copyfile(package / 'runtime-overlay/manifest.json', output / 'runtime-overlay/manifest.json')
    scope = runpy.run_path(str(source / 'verify_scope.py'))['verify'](package, output, baseline)
    (output / 'scope-verification.json').write_text(json.dumps(scope, indent=2) + '\n')
    require(snapshot(package) == before, 'Rebuild changed source package')
    report = {'status': 'PASS', 'tiles': 13, 'decoded_rgba_exact_count': 13, 'hda_file_exact_count': 13,
              'committed_selected_png_hashes_verified_count': 13,
              'regenerated_png_file_exact_count': sum(r['regenerated_png_file_exact'] for r in results),
              'unchanged_v3_committed_png_and_hda_exact_count': 10, 'v4_changed_tiles': FRINGE_IDS,
              'native_helpers_compiled_fresh_count': 2, 'source_package_unchanged': True,
              'package_inventory_verified': inventory_verified, 'finite_three_roi_scope_passed': True,
              'runtime_acceptance': contract['runtime_acceptance'],
              'runtime_evidence_reexecuted_by_builder': False,
              'environment': {'python': platform.python_version(), 'pillow': pillow_version,
                              'compiler': subprocess.run([compiler, '--version'], check=True, text=True,
                                                         capture_output=True).stdout.splitlines()[0],
                              'platform': platform.platform()},
              'v3_reconstruction': baseline_report, 'items': results}
    (output / 'rebuild-verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'items'}, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print('Rebuild failed: ' + str(error), file=sys.stderr)
        sys.exit(1)
