#!/usr/bin/env python3
"""Bounded additive skin boundary and deterministic local resource validation."""
from pathlib import Path
import hashlib
import json
import struct
import subprocess
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = '8218c1f8a2ca046b6c461f3da1006ee76cf1b203'
asset = ROOT / 'assets/shop-frame-v1'
manifest = json.loads((asset / 'shop-frame-metal-v1.json').read_text())
resource = (asset / 'shop-frame-metal-v1.hda').read_bytes()
assert len(resource) == manifest['file_bytes'] == 1276948
assert hashlib.sha256(resource).hexdigest() == manifest['file_sha256']
for key in ['source', 'layout_mask']:
    row = manifest[key]
    assert hashlib.sha256((asset / row['file']).read_bytes()).hexdigest() == row['sha256']
assert resource[:4] == b'PMF1'
fields = struct.unpack_from('<15I', resource, 4)
assert fields == (1, 320, 200, 4, 1280, 800, 2492, 314221, 1276820, 4, 1, 0, 0, 0, 0)
assert struct.unpack_from('<QQ', resource, 64) == (0x45a77a2246c174b9, 0x1c6687307999bd82)
assert resource[88:128] == bytes(40)
with tempfile.TemporaryDirectory(prefix='shop-frame-export-') as temp:
    output = Path(temp) / 'shop-frame-metal-v1.hda'
    subprocess.run(['python3', str(ROOT / 'scripts/export_shop_frame.py'), '--out', str(output)], check=True, stdout=subprocess.DEVNULL)
    assert output.read_bytes() == resource

# Original menu, sprite data owners, input, state and RNG production files stay
# byte-exact against the frozen parent. The file list is explicit: no unrelated
# historical test fixtures are inspected.
for name in ['src/game_menu.c', 'src/pregame_font.h', 'src/sprite.c',
             'src/video.c', 'src/player.c', 'src/keyboard.c', 'src/mtrand.c',
             'src/selector_font.c', 'src/settings_font.c', 'src/load_font.c',
             'Makefile', 'visualc/opentyrian.vcxproj']:
    assert (ROOT / name).read_bytes() == subprocess.check_output(['git', 'show', BASE + ':' + name], cwd=ROOT), name
source = (ROOT / 'src/pregame_font.c').read_text()
assert 'SF_EVENTS=40000' in source
assert 'sf.count>sf.static_count' in source
assert 'sf.metal&&(!sf.product||sf.category==2||sf.category==5)' in source
assert source.count('sf.metal_blocked[p]=1') == 1
assert 'sf.metal_blocked[p]=0' not in source
assert 'if(!replay_matches())' in source
ns = {'m': 'http://schemas.microsoft.com/developer/msbuild/2003'}
tree = ET.parse(ROOT / 'visualc/opentyrian.vcxproj')
c = [x.attrib['Include'] for x in tree.findall('.//m:ClCompile', ns) if 'Include' in x.attrib]
assert len(c) == len(set(c))
assert {Path(x.replace('\\', '/')).name for x in c} == {x.name for x in (ROOT / 'src').glob('*.c')}
print('PASS: reproducible optional PMF1; original menu/input/state/RNG/font owners byte-exact; no new C module; Windows inventory complete')
