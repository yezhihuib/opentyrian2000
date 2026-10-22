#!/usr/bin/env python3
"""Exact local typography delta from the accepted Talon parent.

Does not import historical projection modules or read their external fixtures.
No source/asset wildcard exemptions and no game launch.
"""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PIN = json.loads((ROOT / 'tests/shop_menu_font_source_delta.json').read_text())
BASE = PIN['base']


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args])


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


assert BASE == '1685561b2b5d6bd6264bd7756cc30cf7c7506c4f'
assert git('rev-parse', BASE).decode().strip() == BASE
tracked_sources = set(git('ls-tree', '-r', '--name-only', BASE, 'src').decode().splitlines())
actual_sources = {str(p.relative_to(ROOT)) for p in (ROOT / 'src').rglob('*') if p.is_file()}
assert actual_sources == tracked_sources | {'src/shop_menu_font_pins.h'}
for name in sorted(tracked_sources):
    raw = (ROOT / name).read_bytes()
    if name == 'src/pregame_font.c':
        assert digest(git('show', BASE + ':' + name)) == PIN['original_pregame_sha256']
        assert digest(raw) == PIN['accepted_sha256'][name]
    else:
        assert raw == git('show', BASE + ':' + name), name
old_assets = set(git('ls-tree', '-r', '--name-only', BASE, 'assets').decode().splitlines())
changed_assets = set(git('diff', '--name-only', BASE, '--', 'assets').decode().splitlines())
assert not changed_assets & old_assets, 'existing assets changed'
new_assets = {str(p.relative_to(ROOT)) for p in (ROOT / 'assets/shop-menu-font-v1').iterdir() if p.is_file()}
assert new_assets == {name for name in PIN['accepted_sha256'] if name.startswith('assets/')}
actual_assets = {str(p.relative_to(ROOT)) for p in (ROOT / 'assets').rglob('*') if p.is_file()}
assert actual_assets == old_assets | new_assets, 'unlisted asset added'
rejections = 0
for name, wanted in PIN['accepted_sha256'].items():
    path = ROOT / name
    assert path.is_file() and not path.is_symlink(), name
    raw = path.read_bytes()
    assert digest(raw) == wanted, name
    for at in {0, len(raw) // 2, len(raw) - 1}:
        bad = raw[:at] + bytes([raw[at] ^ 1]) + raw[at + 1:]
        assert digest(bad) != wanted
        rejections += 1
print(json.dumps(dict(result='PASS', baseline=BASE, exact_old_source_files=len(tracked_sources)-1,
    changed_production_source=['src/pregame_font.c'], exact_added_production=list(PIN['accepted_sha256']),
    unchanged_existing_assets=True, mutation_rejections=rejections,
    original_game_draw_input_purchase_rng_sources_unchanged=True), indent=2))
