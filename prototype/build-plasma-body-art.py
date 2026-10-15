#!/usr/bin/env python3
"""Verify frozen Plasma-body art and exact finite pack preservation; never run game."""
from pathlib import Path
from PIL import Image
import argparse, hashlib, json, subprocess, sys, tempfile

ROOT = Path(__file__).resolve().parents[1]
BASE = 'b1a8927fb9e892f87452813010cd206e069cc413'
ART = 'assets/hd/artwork/option-plasma-body-five-v1'
CONTRACT = '6afc9ddb8a96d66c532347adddf09b147de5efc6586e546dff5b9cc4f6d7e446'
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
        name = f"option-plasma-bank9-{e['id']}-8.hda"
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
    assert len(m['source_pngs']) == len(old['source_pngs']) + 5
    assert set(m['packs']) == set(old['packs'])
    for name, before in old['packs'].items():
        after = m['packs'][name]
        if name not in defaults:
            assert after == before
            continue
        assert before['count'] == len(before['files']) == 549
        assert after['count'] == len(after['files']) == 554
        assert after == {**before, 'count': 554, 'files': {**before['files'], **added}}
        prefix = 'assets/hd/packs/' + name + '/'
        prior = set(git('ls-tree', '-r', '--name-only', BASE, '--', prefix).decode().splitlines())
        current = {str(x.relative_to(ROOT)) for x in (ROOT / prefix).iterdir() if x.is_file()}
        assert len(prior) == 560 and current == prior | {prefix + n for n in added}
        assert len(current) == 565 and sum(x.endswith('.hda') for x in current) == 560
    # Verify baseline bytes independently of staging/commit state. The expected
    # new HDAs must remain valid after publication as well as while untracked.
    prior_blobs = {}
    for line in git('ls-tree', '-r', BASE, '--', 'assets/hd/packs').decode().splitlines():
        metadata, path = line.split('\t', 1)
        mode, kind, blob = metadata.split()
        assert mode == '100644' and kind == 'blob'
        prior_blobs[path] = blob
    for path, blob in prior_blobs.items():
        f = ROOT / path
        assert f.is_file() and not f.is_symlink()
        raw = f.read_bytes()
        assert hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest() == blob
    expected_additions = {'assets/hd/packs/' + pack + '/' + name for pack in defaults for name in added}
    actual = {str(f.relative_to(ROOT)) for f in (ROOT / 'assets/hd/packs').rglob('*') if f.is_file() or f.is_symlink()}
    assert actual == set(prior_blobs) | expected_additions
    assert not any(f.is_symlink() for f in (ROOT / 'assets/hd/packs').rglob('*'))
    changed = dict(m)
    changed.pop('option_plasma_body_five_v1')
    changed['packs'] = old['packs']
    changed['source_pngs'] = old['source_pngs']
    assert changed == old
    assert m['option_plasma_body_five_v1']['contract_sha256'] == CONTRACT
    if a.output:
        subprocess.run([sys.executable, str(art / 'rebuild.py'), '--output', str(a.output.absolute())], check=True)
    else:
        with tempfile.TemporaryDirectory(prefix='plasma-body-rebuild-') as d:
            subprocess.run([sys.executable, str(art / 'rebuild.py'), '--output', str(Path(d) / 'output')], check=True)
    print('PASS five frozen generated masters, exact RGBA/PNG/HDA, both default554-record/565-file packs, all old bytes and rollback packs preserved')

if __name__ == '__main__':
    main()
