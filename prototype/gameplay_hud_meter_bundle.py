"""Validate the finite HUM2 resource and its generated-only source inventory."""
from pathlib import Path
import json
import struct
from gameplay_hud_extension_bundles import checked_file, sha, fnv

FILENAME = 'gameplay-hud-meters-v2.hda'
SOURCE = 'assets/hd/artwork/gameplay-hud-meters-v2'
RESOURCE_SHA256 = '3f8d9c35a3a9791d554a3c46f3431289c8ecd68b57419747ce3a40c225dafa4c'
SOURCE_FILES = frozenset(('FILES.txt', 'README.md', 'SHA256SUMS', 'build_resource.py',
    'canonical/gameplay-hud-meters-v2.hda', 'canonical/meter-scope-1390.mask',
    'contract.json', 'manifest.json', 'materials.py', 'proof/portable-path-checks.json',
    'proof/relocated-build.json', 'requirements.txt', 'selected-rgb.json'))


def build_bundle(repo):
    repo = Path(repo)
    family = json.loads(checked_file(repo, 'assets/hd/manifest.json').read_text())['gameplay_hud_meters_v2']
    assert family['schema'] == 'finite-gameplay-hum2-raster-history-v2'
    assert family['filename'] == FILENAME and family['source'] == SOURCE
    source = repo / SOURCE
    assert set(family['source_files']) == SOURCE_FILES
    assert {str(p.relative_to(source)) for p in source.rglob('*') if p.is_file()} == SOURCE_FILES
    for name, spec in family['source_files'].items():
        data = checked_file(source, name).read_bytes()
        assert {'bytes': len(data), 'sha256': sha(data)} == spec
    assert set(checked_file(source, 'FILES.txt').read_text().splitlines()) == SOURCE_FILES
    raw = checked_file(source, 'canonical/' + FILENAME).read_bytes()
    assert len(raw) == 621920 and sha(raw) == RESOURCE_SHA256
    words = struct.unpack('<4s11I8Q', raw[:112])
    assert words[:12] == (b'HUM2', 2, 112, 4, 320, 200, 4224, 51840, 120832, 444912, 944, 222456)
    stamps = (0x14c1441f3d5dc0e2, 0x5e80e83992be2927, 0x92ce2a65c65f67db,
        0x33f13810daec0125, 0xc4231771a5413868, 0x1d129d23c2edc134,
        0xfcc77c108870c9db, 0)
    assert words[12:] == stamps
    payload = raw[112:]
    assert fnv(payload) == stamps[6]
    at = 0
    sections = []
    for size, stamp in zip((4224, 51840, 120832, 444912), stamps[2:6]):
        section = payload[at:at + size]
        assert len(section) == size and fnv(section) == stamp
        sections.append(section)
        at += size
    assert at == len(payload)
    assert all(set(section[3::4]) == {255} for section in sections[:3])
    lookup = struct.unpack('<222456H', sections[3])
    assert max(lookup) == 943 and min(lookup) == 0
    for index in range(13):
        for height in range(1, 93):
            start = index * 17112 + 2 * height * (height - 1)
            assert start + 4 * height <= len(lookup)
    scope = bytearray(64000)
    for x, y, right, bottom in ((289,17,311,20), (289,38,311,41), (269,12,277,104), (307,137,316,195)):
        for yy in range(y, bottom):
            scope[yy * 320 + x:yy * 320 + right] = bytes([255]) * (right - x)
    assert sum(bool(v) for v in scope) == 1390
    assert scope == checked_file(source, 'canonical/meter-scope-1390.mask').read_bytes()
    receipt = {'bytes': len(raw), 'sha256': sha(raw)}
    assert receipt == family['bundle']
    return raw, receipt
