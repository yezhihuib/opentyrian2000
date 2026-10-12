"""Verify finite HUF1 artwork; hashes detect corruption, not asset authorship."""
from pathlib import Path
import json
import struct
from PIL import Image
from gameplay_hud_extension_bundles import checked_file, sha, fnv

FILENAME = 'gameplay-hud-font-v1.hda'
SOURCE = 'assets/hd/artwork/gameplay-hud-font-v1'
RESOURCE_SHA256 = '3c328c1537cf1e09529ae8805e98a8deb57a859ea80ba269cfea0b55cfae539e'
SOURCE_FILES = frozenset(('FILES.txt', 'README.md', 'SHA256SUMS', 'build_resource.py',
    'canonical/gameplay-hud-font-v1.hda', 'canonical/tiny-coverage-atlas-4x.alpha.bin',
    'canonical/tiny-coverage-atlas-4x.png', 'canonical/tiny-vector-atlas.svg', 'manifest.json',
    'proof/huf1-resource-proof.json', 'proof/metadata-normalization.json',
    'proof/relocated-build.json', 'proof/reproduction-report.json', 'reproduce.py',
    'requirements.txt', 'sources/glyph-vectors.json', 'sources/original-atlas-manifest.json',
    'sources/resource-contract.json', 'sources/source-font-metrics.json'))


def build_bundle(repo):
    repo = Path(repo)
    family = json.loads(checked_file(repo, 'assets/hd/manifest.json').read_text())['gameplay_hud_font_v1']
    assert family['schema'] == 'finite-gameplay-huf1-ascii86-v1'
    assert family['filename'] == FILENAME and family['source'] == SOURCE
    assert (family['geometry_glyphs'], family['eligible_ascii_glyphs'], family['authored_palette_role']) == (127, 86, 7)
    source = repo / SOURCE
    assert set(family['source_files']) == SOURCE_FILES
    assert {str(p.relative_to(source)) for p in source.rglob('*') if p.is_file()} == SOURCE_FILES
    for name, spec in family['source_files'].items():
        data = checked_file(source, name).read_bytes()
        assert {'bytes': len(data), 'sha256': sha(data)} == spec
    assert set(checked_file(source, 'FILES.txt').read_text().splitlines()) == SOURCE_FILES
    contract = json.loads(checked_file(source, 'sources/resource-contract.json').read_text())
    assert contract['struct_format'] == '<4s11I8Q'
    assert contract['u32_values'] == [1, 4, 512, 320, 127, 86, 32, 40, 4, 163840, 7]
    stamps = [int(value, 16) for value in contract['u64_values_hex']]
    assert stamps == [0x14c1441f3d5dc0e2, 0x5e80e83992be2927, 0x845b16939661b466,
        0x0908ca85cbf2a1e3, 0x2ed2973d82ce6f3d, 0x85cddeb8bd7ea09a, 0x68e8c2bab3c43d0d, 0]
    with Image.open(checked_file(source, 'canonical/tiny-coverage-atlas-4x.png')) as atlas:
        assert atlas.mode == 'RGBA' and atlas.size == (512, 320)
        alpha = atlas.getchannel('A').tobytes()
    assert alpha == checked_file(source, 'canonical/tiny-coverage-atlas-4x.alpha.bin').read_bytes()
    assert fnv(alpha) == stamps[5]
    metrics = json.loads(checked_file(source, 'sources/source-font-metrics.json').read_text())
    assert fnv(struct.pack('<256i', *metrics['font_ascii'])) == stamps[2]
    glyphs = sorted(metrics['tiny_font']['glyphs'], key=lambda g: g['sprite_id'])
    assert [g['sprite_id'] for g in glyphs] == list(range(127))
    assert all(1 <= g['width'] <= 6 and 1 <= g['height'] <= 8 and g['advance'] == g['width'] + 1 for g in glyphs)
    assert fnv(b''.join(struct.pack('<3H', g['width'], g['height'], g['advance']) for g in glyphs)) == stamps[3]
    eligible = {i for i in metrics['font_ascii'][:128] if i >= 0}
    assert eligible == set(range(86))
    assert fnv(bytes(255 if i in eligible else 0 for i in range(127))) == stamps[6]
    allowed = bytearray(len(alpha))
    for g in glyphs:
        x, y = (g['sprite_id'] % 16) * 32 + 4, (g['sprite_id'] // 16) * 40 + 4
        for row in range(y, y + g['height'] * 4):
            allowed[row * 512 + x:row * 512 + x + g['width'] * 4] = b'\1' * (g['width'] * 4)
    assert all(not value or allowed[i] for i, value in enumerate(alpha))
    raw = struct.pack('<4s11I8Q', b'HUF1', *contract['u32_values'], *stamps) + alpha
    assert raw == checked_file(source, 'canonical/' + FILENAME).read_bytes()
    receipt = {'bytes': len(raw), 'sha256': sha(raw)}
    assert receipt == {'bytes': 163952, 'sha256': RESOURCE_SHA256} == family['bundle']
    return raw, receipt
