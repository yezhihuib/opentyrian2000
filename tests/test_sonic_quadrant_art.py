#!/usr/bin/env python3
"""Portable finite generated-art rebuild, catalog and corruption acceptance tests."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
ART = Path('assets/hd/artwork/player-sonic-quadrants-v1')
SHA = lambda data: hashlib.sha256(data).hexdigest()


def run(script, *args, ok=True):
    result = subprocess.run([sys.executable, str(script), *map(str, args)], capture_output=True, text=True)
    assert (result.returncode == 0) == ok, result.stdout + result.stderr


def main():
    catalog = json.loads((ROOT / 'assets/hd/manifest.json').read_text())
    contract = json.loads((ROOT / ART / 'contract.json').read_text())
    paths = [Path('assets/hd/manifest.json'), Path('prototype/build-sonic-quadrant-art.py'), Path('prototype/hd_pack_catalog.py')]
    paths += [ART / name for name in ['contract.json', 'rebuild.py']]
    paths += [ART / master['source'] for master in contract['masters']]
    images = {}
    for entry in contract['entries']:
        index = entry['id']
        images[index] = Image.open(ROOT / ART / f'output/bullet-{index}-8.png').copy()
        paths += [ART / f'output/bullet-{index}-8.{extension}' for extension in ('png', 'hda')]
        paths.append(Path(catalog['source_pngs'][entry['HDA_sha256']]['path']))
        paths += [Path('assets/hd/packs') / name / f'bullet-{index}-8.hda' for name in catalog['packs']]
    before = {str(path): SHA((ROOT / path).read_bytes()) for path in paths}
    assert ImageOps.mirror(images[105]).tobytes() == images[106].tobytes()
    assert ImageOps.mirror(images[124]).tobytes() == images[125].tobytes()
    assert ImageOps.flip(images[105]).tobytes() != images[124].tobytes()
    assert all(not any(images[index].tobytes()[:16*96*4][3::4]) for index in (105, 106))
    assert all(not any(images[index].tobytes()[88*96*4:][3::4]) for index in (124, 125))
    for scale in (2, 4):
        # Phase-aware mirrored-source correspondence. The counterpart coordinate
        # intentionally preserves the full-canvas mirror phase; it need not lie
        # on the right sprite renderer grid at native 2x/4x.
        for left, right in ((105, 106), (124, 125)):
            assert all(images[left].getpixel((x*8//scale, y*8//scale)) ==
                       images[right].getpixel((95-x*8//scale, y*8//scale))
                       for y in range(14*scale) for x in range(12*scale))
    with tempfile.TemporaryDirectory(prefix='sonic-quadrant-art-tests-') as temporary:
        work = Path(temporary)
        relocated = work / 'portable-source'
        for path in paths:
            (relocated / path).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / path, relocated / path)
        builder = relocated / 'prototype/build-sonic-quadrant-art.py'
        rebuild = relocated / ART / 'rebuild.py'
        run(builder, '--output', work / 'first')
        run(builder, '--output', work / 'second')
        for entry in contract['entries']:
            for extension in ('png', 'hda'):
                name = f"bullet-{entry['id']}-8.{extension}"
                assert (work / 'first' / name).read_bytes() == (work / 'second' / name).read_bytes()
        run(rebuild, '--output', work / 'first', ok=False)
        (work / 'linked-parent').symlink_to(work / 'first', target_is_directory=True)
        run(rebuild, '--output', work / 'linked-parent' / 'unsafe', ok=False)
        assert not (work / 'first' / 'unsafe').exists()
        source = relocated / ART / contract['masters'][0]['source']
        clean = source.read_bytes()
        source.write_bytes(clean + b'corrupt')
        run(rebuild, '--output', work / 'corrupt-source', ok=False)
        assert not (work / 'corrupt-source').exists()
        source.write_bytes(clean)
        runtime = relocated / 'assets/hd/packs' / catalog['default_preview_pack'] / 'bullet-105-8.hda'
        clean = runtime.read_bytes()
        runtime.write_bytes(clean[:-1] + bytes([clean[-1] ^ 1]))
        run(builder, ok=False)
        runtime.write_bytes(clean)
        changed = json.loads((relocated / 'assets/hd/manifest.json').read_text())
        optional_pack = changed['optional_packs']['asteroid1-ten-v1']
        optional_pack['files'][next(iter(optional_pack['files']))]['sha256'] = '0' * 64
        (relocated / 'assets/hd/manifest.json').write_text(json.dumps(changed))
        run(builder, ok=False)
        # Removing optional metadata for the default inverse must not hide edits.
        changed = json.loads((ROOT / 'assets/hd/manifest.json').read_text())
        changed['player_sonic_six_pair_v1']['scope'] += ' unauthorized change'
        (relocated / 'assets/hd/manifest.json').write_text(json.dumps(changed))
        run(builder, ok=False)
    assert before == {str(path): SHA((ROOT / path).read_bytes()) for path in paths}
    print('PASS: relocated Git-free exact double rebuild, mirrors/margins/mirror-phase correspondence, source/runtime/catalog corruption and unsafe-output rejection')


if __name__ == '__main__':
    main()
