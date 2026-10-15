#!/usr/bin/env python3
"""Verify frozen Mint-body art and exact finite pack preservation; never run game."""
from pathlib import Path
from PIL import Image
import argparse, hashlib, json, subprocess, sys, tempfile

ROOT = Path(__file__).resolve().parents[1]
BASE = '8b71966b59315b7ee67163e160925e0d60a0ae39'
ART = 'assets/hd/artwork/option-mint-body-three-v1'
CONTRACT = 'b8a51b0d2d240b633a1cd1c3d136040583b1091797c287dbde4be25ab54aca49'
SHA = lambda b: hashlib.sha256(b).hexdigest()

def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args])

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path)
    a = p.parse_args()
    art = ROOT / ART
    craw = (art / 'contract.json').read_bytes()
    assert SHA(craw) == CONTRACT
    c = json.loads(craw)
    m = json.loads((ROOT / 'assets/hd/manifest.json').read_text())
    old = json.loads(git('show', BASE + ':assets/hd/manifest.json'))
    defaults = {m['default_preview_pack'], m['default_debug_pack']}
    assert defaults == {old['default_preview_pack'], old['default_debug_pack']}
    added = {}
    for e in c['entries']:
        name = f"option-mint-bank9-{e['id']}-8.hda"
        png = (art / 'output' / name.replace('.hda', '.png')).read_bytes()
        raw = (art / 'output' / name).read_bytes()
        assert SHA(raw) == e['HDA_sha256'] and len(raw) == 43036
        assert SHA(png) == e['PNG_sha256'] and SHA(raw[28:]) == e['RGBA_sha256']
        im = Image.open(art / 'output' / name.replace('.hda', '.png'))
        assert im.mode == 'RGBA' and im.size == (96, 112) and im.tobytes() == raw[28:]
        assert SHA((art / e['source']).read_bytes()) == e['source_sha256']
        canonical = f"assets/hd/source/{name[:-4]}-{e['HDA_sha256'][:12]}.png"
        assert (ROOT / canonical).read_bytes() == png
        assert m['source_pngs'][e['HDA_sha256']] == {'path': canonical, 'sha256': e['PNG_sha256'], 'RGBA_sha256': e['RGBA_sha256']}
        added[name] = {'header_u32': e['header_u32'], 'sha256': e['HDA_sha256'], 'source_png': canonical, 'source_png_sha256': e['PNG_sha256']}
        for pack in defaults:
            assert (ROOT / 'assets/hd/packs' / pack / name).read_bytes() == raw
    for h, item in old['source_pngs'].items():
        assert m['source_pngs'][h] == item
    assert len(m['source_pngs']) == len(old['source_pngs']) + 3
    assert set(m['packs']) == set(old['packs'])
    for name, before in old['packs'].items():
        after = m['packs'][name]
        if name not in defaults:
            assert after == before
            continue
        assert before['count'] == len(before['files']) == 545
        assert after['count'] == len(after['files']) == 548
        assert after == {**before, 'count': 548, 'files': {**before['files'], **added}}
        prefix = 'assets/hd/packs/' + name + '/'
        prior = set(git('ls-tree', '-r', '--name-only', BASE, '--', prefix).decode().splitlines())
        current = {str(x.relative_to(ROOT)) for x in (ROOT / prefix).iterdir() if x.is_file()}
        assert len(prior) == 556 and current == prior | {prefix + n for n in added}
        assert len(current) == 559 and sum(x.endswith('.hda') for x in current) == 554
    # Every pre-existing pack file, including six unlisted HDA and five auxiliaries,
    # is checked by Git's byte comparison rather than by a manifest-only count.
    assert not git('diff', BASE, '--name-only', '--', 'assets/hd/packs').strip()
    changed = dict(m)
    changed.pop('option_mint_body_three_v1')
    changed['packs'] = old['packs']
    changed['source_pngs'] = old['source_pngs']
    assert changed == old
    assert m['option_mint_body_three_v1']['contract_sha256'] == CONTRACT
    if a.output:
        subprocess.run([sys.executable, str(art / 'rebuild.py'), '--output', str(a.output.absolute())], check=True)
    else:
        with tempfile.TemporaryDirectory(prefix='mint-body-rebuild-') as d:
            subprocess.run([sys.executable, str(art / 'rebuild.py'), '--output', str(Path(d) / 'output')], check=True)
    print('PASS three generated masters, exact RGBA/PNG/HDA, both default548-record/559-file packs, all old bytes and rollback packs preserved')

if __name__ == '__main__':
    main()
