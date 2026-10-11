#!/usr/bin/env python3
"""Reconstruct the exact v3 baseline from canonical generated-only sources."""
from pathlib import Path
from PIL import Image
import hashlib
import json
import shutil
import struct
import subprocess

IDS = [150, 156, 157, 158, 159, 160, 166, 168, 169, 170, 176, 177, 178]
TONE_IDS = [150, 166, 168, 176, 177, 178]
FRINGE_IDS = [176, 177, 178]
ORDER = [[156, 157, 158], [166, 150, 168], [176, 177, 178]]
V3_CONTRACT_SHA = 'e6ea80bd049c507cc7a8c708287c51fd3bde9a61684321649667cede9267b6d7'
V3_MANIFEST_SHA = 'b733a687a181ab6f1d7ec8d5d6bafdd4af91cd4d9c4cc956de4293ad3ee0b26a'
V4_MANIFEST_SHA = '8b0d2ad2f11125657f5fea3739c5fae9368cc12a0e0e512919fc73ed5b936f3a'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def snapshot(root):
    return {p.relative_to(root).as_posix(): sha(p.read_bytes())
            for p in sorted(root.rglob('*')) if p.is_file()}


def rgba(path, size=(192, 224)):
    with Image.open(path) as image:
        require(image.size == size, 'Unexpected image dimensions: ' + str(path))
        return image.convert('RGBA').tobytes()


def hda(tile, raw):
    require(len(raw) == 172032, 'Unexpected RGBA length')
    return b'HDR1' + struct.pack('<6I', 2010000 + tile, 8, 24, 28, 0, 0) + raw


def reconstruct(package, work):
    """Return exact v3 raw pixels; no selected PNG/HDA is used as input."""
    source = package / 'source'
    contract_path = source / 'upstream-v3/rebuild-contract.json'
    require(sha(contract_path.read_bytes()) == V3_CONTRACT_SHA, 'Frozen v3 contract differs')
    contract = json.loads(contract_path.read_text())
    require(sha((source / 'upstream-v3/runtime-manifest.json').read_bytes()) == V3_MANIFEST_SHA,
            'Frozen v3 manifest differs')
    require(contract['ids'] == IDS and contract['override_ids'] == TONE_IDS and
            contract['foundation9_order'] == ORDER and contract['slots'] == list(range(290, 303)),
            'Frozen v3 family scope differs')
    require([r['id'] for r in contract['items']] == IDS, 'Frozen v3 item order differs')
    for filename, key in [('match_exposed_connector.cpp', 'native_helper_sha256'),
                          ('selected-crops.json', 'source_crop_provenance_sha256')]:
        require(sha((source / filename).read_bytes()) == contract[key], 'Input differs: ' + filename)
    crop_provenance = json.loads((source / 'selected-crops.json').read_text())
    require(sorted(map(int, crop_provenance)) == IDS, 'Source crop provenance scope differs')
    expected = {f'terrain-shapesz-{i}-8.png' for i in IDS}
    require({p.name for p in (source / 'generated-crops').iterdir()} == expected,
            'Authored source scope differs')
    originals = {}
    for row in contract['items']:
        tile = row['id']
        file = source / 'generated-crops' / f'terrain-shapesz-{tile}-8.png'
        raw = rgba(file)
        require(sha(file.read_bytes()) == row['source_png_sha256'] ==
                crop_provenance[str(tile)]['png_sha256'], f'Authored PNG differs: {tile}')
        require(sha(raw) == row['source_rgba_sha256'] == crop_provenance[str(tile)]['rgba_sha256'],
                f'Authored RGBA differs: {tile}')
        require(set(raw[3::4]) == {255}, f'Authored tile is not opaque: {tile}')
        originals[tile] = raw
    reference_path = package / contract['actor_reference']['path']
    reference = rgba(reference_path, (576, 16))
    require(sha(reference_path.read_bytes()) == contract['actor_reference']['file_sha256'] and
            sha(reference) == contract['actor_reference']['rgba_sha256'], 'Tone reference differs')
    require(set(reference[3::4]) == {255}, 'Tone reference is not opaque')
    foundation = Image.new('RGBA', (576, 672))
    for y, tiles in enumerate(ORDER):
        for x, tile in enumerate(tiles):
            foundation.paste(Image.frombytes('RGBA', (192, 224), originals[tile]), (x * 192, y * 224))
    work.mkdir(parents=True, exist_ok=True)
    assembled_path, reference_path, toned_path = [work / name for name in
        ('foundation9-before.rgba', 'actor-adjacent-strip16.rgba', 'foundation9-after.rgba')]
    assembled = foundation.tobytes()
    assembled_path.write_bytes(assembled)
    reference_path.write_bytes(reference)
    compiler = shutil.which('c++')
    require(compiler is not None, 'A C++17 compiler available as c++ is required')
    executable = work / 'match_exposed_connector'
    subprocess.run([compiler, '-O2', '-std=c++17', str(source / 'match_exposed_connector.cpp'),
                    '-o', str(executable)], check=True)
    helper = subprocess.run([str(executable), str(assembled_path), str(reference_path), str(toned_path)],
                            check=True, capture_output=True, text=True)
    toned = toned_path.read_bytes()
    require(len(toned) == 576 * 672 * 4, 'Connector helper output length differs')
    require(assembled[3::4] == toned[3::4], 'Connector helper changed alpha')
    require(assembled[:440 * 576 * 4] == toned[:440 * 576 * 4] and
            assembled[456 * 576 * 4:] == toned[456 * 576 * 4:], 'Connector helper exceeded row scope')
    toned_image = Image.frombytes('RGBA', (576, 672), toned)
    rebuilt = dict(originals)
    for y, tiles in enumerate(ORDER):
        for x, tile in enumerate(tiles):
            if tile in TONE_IDS:
                rebuilt[tile] = toned_image.crop((x * 192, y * 224, (x + 1) * 192,
                                                  (y + 1) * 224)).tobytes()
    for row in contract['items']:
        tile = row['id']
        require(sha(rebuilt[tile]) == row['selected_rgba_sha256'], f'Intermediate v3 RGBA differs: {tile}')
        require(sha(hda(tile, rebuilt[tile])) == row['selected_hda_sha256'],
                f'Intermediate v3 HDA differs: {tile}')
    return rebuilt, {'status': 'PASS', 'intermediate_v3_rgba_exact_count': 13,
                     'intermediate_v3_hda_exact_count': 13, 'native_helper_compiled_fresh': True,
                     'helper_stdout': helper.stdout.strip(), 'helper_stderr': helper.stderr.strip()}
