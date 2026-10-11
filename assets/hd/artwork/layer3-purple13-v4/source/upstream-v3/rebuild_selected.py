#!/usr/bin/env python3
"""Reproduce frozen purple13 v3 using only generated source crops and a tiny tone reference."""
from pathlib import Path
from PIL import Image, __version__ as pillow_version
import argparse
import hashlib
import json
import platform
import runpy
import shutil
import struct
import subprocess
import sys

IDS = [150, 156, 157, 158, 159, 160, 166, 168, 169, 170, 176, 177, 178]
OVERRIDES = [150, 166, 168, 176, 177, 178]
ORDER = [[156, 157, 158], [166, 150, 168], [176, 177, 178]]
MANIFEST_SHA = 'b733a687a181ab6f1d7ec8d5d6bafdd4af91cd4d9c4cc956de4293ad3ee0b26a'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def snapshot(root):
    return {p.relative_to(root).as_posix(): sha(p.read_bytes())
            for p in sorted(root.rglob('*')) if p.is_file()}


def read_rgba(path, size=(192, 224)):
    with Image.open(path) as image:
        require(image.size == size, 'Unexpected image dimensions: ' + str(path))
        return image.convert('RGBA').tobytes()


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
    require(contract['ids'] == IDS and contract['override_ids'] == OVERRIDES and
            contract['foundation9_order'] == ORDER and contract['slots'] == list(range(290, 303)),
            'Finite family contract differs')
    require([r['id'] for r in contract['items']] == IDS and
            [r['slot'] for r in contract['items']] == list(range(290, 303)), 'Item order differs')
    require(contract['selected_manifest_sha256'] == MANIFEST_SHA ==
            sha((package / 'runtime-overlay/manifest.json').read_bytes()), 'Frozen manifest differs')
    for name, key in [('match_exposed_connector.cpp', 'native_helper_sha256'),
                      ('selected-crops.json', 'source_crop_provenance_sha256')]:
        require(sha((source / name).read_bytes()) == contract[key], 'Input differs: ' + name)
    crop_provenance = json.loads((source / 'selected-crops.json').read_text())
    require(sorted(map(int, crop_provenance)) == IDS, 'Source crop provenance scope differs')
    expected = {f'terrain-shapesz-{i}-8.png' for i in IDS}
    require({p.name for p in (source / 'generated-crops').iterdir()} == expected,
            'Authored source scope differs')
    require({p.name for p in (package / 'output').iterdir()} == expected, 'Selected PNG scope differs')
    require({p.name for p in (package / 'runtime-overlay').iterdir()} ==
            {'manifest.json'} | {f'terrain-shapesz-{i}-8.hda' for i in IDS}, 'Selected HDA scope differs')
    inventory_verified = False
    inventory = package / 'handoff-inventory.json'
    if inventory.exists():
        rows = json.loads(inventory.read_text())['files']
        require(len({r['path'] for r in rows}) == len(rows), 'Duplicate inventory paths')
        require({r['path'] for r in rows} == set(before) - {'handoff-inventory.json'},
                'Inventory file scope differs')
        for row in rows:
            file = package / row['path']
            require(file.stat().st_size == row['bytes'] and sha(file.read_bytes()) == row['sha256'],
                    'Inventory bytes or hash differs: ' + row['path'])
        inventory_verified = True
    compiler = shutil.which('c++')
    require(compiler is not None, 'A C++17 compiler available as c++ is required')
    for directory in ('work', 'output', 'runtime-overlay'):
        (output / directory).mkdir(parents=True)
    originals = {}
    for row in contract['items']:
        tile = row['id']
        file = source / 'generated-crops' / f'terrain-shapesz-{tile}-8.png'
        raw = read_rgba(file)
        require(sha(file.read_bytes()) == row['source_png_sha256'] ==
                crop_provenance[str(tile)]['png_sha256'], f'Authored PNG differs: {tile}')
        require(sha(raw) == row['source_rgba_sha256'] == crop_provenance[str(tile)]['rgba_sha256'],
                f'Authored RGBA differs: {tile}')
        require(set(raw[3::4]) == {255}, f'Authored tile is not opaque: {tile}')
        originals[tile] = raw
    reference_path = package / contract['actor_reference']['path']
    reference = read_rgba(reference_path, (576, 16))
    require(sha(reference_path.read_bytes()) == contract['actor_reference']['file_sha256'] and
            sha(reference) == contract['actor_reference']['rgba_sha256'], 'Tone reference differs')
    require(set(reference[3::4]) == {255}, 'Tone reference is not opaque')
    foundation = Image.new('RGBA', (576, 672))
    for y, tiles in enumerate(ORDER):
        for x, tile in enumerate(tiles):
            foundation.paste(Image.frombytes('RGBA', (192, 224), originals[tile]), (x * 192, y * 224))
    assembled_path = output / 'work/foundation9-before.rgba'
    reference_raw_path = output / 'work/actor-adjacent-strip16.rgba'
    toned_path = output / 'work/foundation9-after.rgba'
    assembled_path.write_bytes(foundation.tobytes())
    reference_raw_path.write_bytes(reference)
    executable = output / 'work/match_exposed_connector'
    subprocess.run([compiler, '-O2', '-std=c++17', str(source / 'match_exposed_connector.cpp'),
                    '-o', str(executable)], check=True)
    helper = subprocess.run([str(executable), str(assembled_path), str(reference_raw_path),
                             str(toned_path)], check=True, text=True, capture_output=True)
    toned = toned_path.read_bytes()
    require(len(toned) == 576 * 672 * 4, 'Native helper output length differs')
    # A second assembly-level oracle, independent of cropping, constrains the helper.
    assembled = foundation.tobytes()
    require(assembled[3::4] == toned[3::4], 'Native helper changed alpha')
    require(assembled[:440 * 576 * 4] == toned[:440 * 576 * 4] and
            assembled[456 * 576 * 4:] == toned[456 * 576 * 4:], 'Native helper exceeded row scope')
    toned_image = Image.frombytes('RGBA', (576, 672), toned)
    rebuilt = dict(originals)
    for y, tiles in enumerate(ORDER):
        for x, tile in enumerate(tiles):
            if tile in OVERRIDES:
                rebuilt[tile] = toned_image.crop((x * 192, y * 224, (x + 1) * 192,
                                                  (y + 1) * 224)).tobytes()
    results = []
    for row in contract['items']:
        tile = row['id']
        stem = f'terrain-shapesz-{tile}-8'
        raw = rebuilt[tile]
        committed_png = package / 'output' / (stem + '.png')
        committed_hda = package / 'runtime-overlay' / (stem + '.hda')
        require(sha(committed_png.read_bytes()) == row['selected_png_sha256'],
                f'Frozen selected PNG file hash differs: {tile}')
        require(read_rgba(committed_png) == raw and sha(raw) == row['selected_rgba_sha256'],
                f'Rebuilt selected decoded RGBA differs: {tile}')
        png = output / 'output' / (stem + '.png')
        if tile in OVERRIDES:
            Image.frombytes('RGBA', (192, 224), raw).save(png)
        else:
            shutil.copyfile(source / 'generated-crops' / (stem + '.png'), png)
            require(png.read_bytes() == committed_png.read_bytes(),
                    f'Unchanged source/selected PNG differs: {tile}')
        payload = b'HDR1' + struct.pack('<6I', 2010000 + tile, 8, 24, 28, 0, 0) + raw
        require(payload == committed_hda.read_bytes() and sha(payload) == row['selected_hda_sha256'],
                f'Rebuilt HDA differs: {tile}')
        (output / 'runtime-overlay' / (stem + '.hda')).write_bytes(payload)
        results.append({'id': tile, 'slot': row['slot'], 'source_png_and_rgba_hashes_verified': True,
                        'committed_selected_png_hash_verified': True,
                        'selected_png_sha256': row['selected_png_sha256'],
                        'regenerated_png_sha256': sha(png.read_bytes()),
                        'regenerated_png_file_exact': png.read_bytes() == committed_png.read_bytes(),
                        'rgba_sha256': sha(raw), 'rgba_exact': True,
                        'hda_sha256': sha(payload), 'hda_file_exact': True})
    shutil.copyfile(package / 'runtime-overlay/manifest.json', output / 'runtime-overlay/manifest.json')
    scope = runpy.run_path(str(source / 'verify_scope.py'))['verify'](package, output)
    (output / 'scope-verification.json').write_text(json.dumps(scope, indent=2) + '\n')
    require(snapshot(package) == before, 'Rebuild changed source package')
    report = {'status': 'PASS', 'tiles': 13, 'decoded_rgba_exact_count': 13,
              'hda_file_exact_count': 13, 'committed_selected_png_hashes_verified_count': 13,
              'regenerated_png_file_exact_count': sum(r['regenerated_png_file_exact'] for r in results),
              'unchanged_seven_source_and_selected_pngs_exact': True,
              'native_helper_compiled_fresh': True, 'actor_reference_rgba_verified': True,
              'source_package_unchanged': True, 'package_inventory_verified': inventory_verified,
              'finite_six_roi_scope_passed': True, 'runtime_acceptance': 'PENDING; no game run',
              'environment': {'python': platform.python_version(), 'pillow': pillow_version,
                              'compiler': subprocess.run([compiler, '--version'], check=True, text=True,
                                                         capture_output=True).stdout.splitlines()[0],
                              'platform': platform.platform()},
              'helper_stdout': helper.stdout.strip(), 'helper_stderr': helper.stderr.strip(),
              'items': results}
    (output / 'rebuild-verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'items'}, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print('Rebuild failed: ' + str(error), file=sys.stderr)
        sys.exit(1)
