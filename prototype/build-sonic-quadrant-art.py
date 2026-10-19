#!/usr/bin/env python3
"""Verify the finite Sonic105/106/124/125 artwork and additive catalog delta."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
from hd_pack_catalog import verify_optional_inventory

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'assets/hd/artwork/player-sonic-quadrants-v1'
SHA = lambda data: hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('sonic_quadrant_rebuild', ART / 'rebuild.py')
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    contract, payloads = builder.reconstruct(ART)
    catalog = json.loads((ROOT / 'assets/hd/manifest.json').read_text())
    # The default-catalog inverse excludes separately pinned optional packs.
    verify_optional_inventory(catalog)
    catalog.pop('optional_packs', None)
    family = catalog.pop('player_sonic_quadrants_v1')
    assert family['ids'] == [105, 106, 124, 125]
    assert family['contract_sha256'] == SHA((ART / 'contract.json').read_bytes())
    assert family['entries'] == [{key: entry[key] for key in ('id', 'slot', 'HDA_sha256')} for entry in contract['entries']]
    defaults = {catalog['default_preview_pack'], catalog['default_debug_pack']}
    assert set(catalog['packs']) == defaults
    for entry in contract['entries']:
        index = entry['id']
        png = (ART / f'output/bullet-{index}-8.png').read_bytes()
        hda = (ART / f'output/bullet-{index}-8.hda').read_bytes()
        assert SHA(png) == entry['PNG_sha256'] and hda == payloads[index][1]
        digest = entry['HDA_sha256']
        canonical = f'assets/hd/source/bullet-{index}-8-{digest[:12]}.png'
        assert (ROOT / canonical).read_bytes() == png
        assert catalog['source_pngs'].pop(digest) == {'path': canonical, 'sha256': SHA(png), 'RGBA_sha256': entry['RGBA_sha256']}
        expected = {'header_u32': entry['header_u32'], 'sha256': digest, 'source_png': canonical, 'source_png_sha256': SHA(png)}
        for name, pack in catalog['packs'].items():
            assert pack['count'] == len(pack['files'])
            assert pack['files'].pop(f'bullet-{index}-8.hda') == expected
            pack['count'] -= 1
            assert (ROOT / 'assets/hd/packs' / name / f'bullet-{index}-8.hda').read_bytes() == hda
    normalized = json.dumps(catalog, sort_keys=True, separators=(',', ':')).encode()
    assert SHA(normalized) == contract['catalog_without_quartet_normalized_sha256'], 'Existing catalog or prior17 Sonic mappings changed'
    if args.output:
        subprocess.run([sys.executable, str(ART / 'rebuild.py'), '--output', str(args.output)], check=True)
    else:
        with tempfile.TemporaryDirectory(prefix='sonic-quadrant-rebuild-') as temporary:
            subprocess.run([sys.executable, str(ART / 'rebuild.py'), '--output', str(Path(temporary) / 'rebuilt')], check=True)
    print('PASS: four authored Sonic quadrants, both default-pack bindings, exact additive catalog inverse; prior17 preserved')


if __name__ == '__main__':
    main()
