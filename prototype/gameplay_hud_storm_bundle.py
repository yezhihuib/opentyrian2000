"""Reconstruct the finite HSI1 sidecar from independently authored planes."""
from pathlib import Path
import json
import struct
from gameplay_hud_extension_bundles import checked_file, fnv, sha

FILENAME = 'gameplay-hud-storm-label-v1.hda'
SOURCE = 'assets/hd/artwork/gameplay-hud-storm-label-v1'


def build_bundle(repo):
    repo = Path(repo)
    family = json.loads((repo / 'assets/hd/manifest.json').read_text())['gameplay_hud_storm_label_v1']
    assert family['schema'] == 'finite-pic3-hsi1-storm-heading125-v1'
    assert family['source'] == SOURCE and family['filename'] == FILENAME
    assert family['ownership_half_open'] == [284, 82, 309, 87]
    assert family['original_icon_size'] == [25, 13] and family['densities'] == [4, 8]
    source = repo / SOURCE
    actual = {p.relative_to(source).as_posix() for p in source.rglob('*') if p.is_file()}
    assert actual == set(family['source_files'])
    for name, expected in family['source_files'].items():
        data = checked_file(source, name).read_bytes()
        assert {'bytes': len(data), 'sha256': sha(data)} == expected
    contract = json.loads(checked_file(source, 'generated/contract.json').read_text())
    assert contract['schema'] == 'storm-heading-palette-coverage-art-v1'
    assert contract['logical_size'] == [25, 5] and contract['original_icon_size'] == [25, 13]
    assert contract['ownership_local_half_open'] == [0, 0, 25, 5]
    assert contract['original_source_not_required'] is True
    pieces = []
    for density in (4, 8):
        n = 25 * 5 * density * density
        values, coverage = [checked_file(source, f'generated/storm-heading-{density}x-{kind}.bin').read_bytes()
                            for kind in ('index', 'coverage')]
        assert len(values) == len(coverage) == n
        assert all(192 <= value <= 207 if alpha else value == 0
                   for value, alpha in zip(values, coverage))
        pieces.extend((values, coverage))
    payload = b''.join(pieces)
    assert len(payload) == 20000 and fnv(payload) == 0x9ec4cfb118ff6182
    header = struct.pack('<4s9I7Q', b'HSI1', 1, 25, 5, 2, 20000, 25, 13, 230, 0,
                         0xe31bdc2ac030d21e, 0x72f4faf812d18989, 0xd6c645d37088c678,
                         0x14c1441f3d5dc0e2, fnv(payload), 0x5e80e83992be2927, 0)
    raw = header + payload
    assert len(raw) == 20096 and raw == checked_file(source, 'generated/' + FILENAME).read_bytes()
    receipt = {'bytes': len(raw), 'sha256': sha(raw)}
    assert receipt == family['bundle']
    packed = json.loads(checked_file(source, 'generated/resource.json').read_text())
    assert packed['file_bytes'] == len(raw) and packed['sha256'] == sha(raw)
    assert packed['payload_fnv1a64'] == f'{fnv(payload):016x}'
    return raw, receipt
