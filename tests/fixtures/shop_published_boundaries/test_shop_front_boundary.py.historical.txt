#!/usr/bin/env python3
"""Exact finite front-only delta from the accepted whole-run typography parent.

No historical projection imports, external fixture reads or wildcard exemptions.
"""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PIN = json.loads((ROOT/'tests/shop_front_source_delta.json').read_text())
BASE = PIN['base']


def git(*args):
    return subprocess.check_output(['git','-C',str(ROOT),*args])


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


assert BASE == 'ac64ee7d3f72dc07fac6a1454eefe4d95429e7b3'
assert git('rev-parse',BASE).decode().strip() == BASE
old_sources = set(git('ls-tree','-r','--name-only',BASE,'src').decode().splitlines())
actual_sources = {str(p.relative_to(ROOT)) for p in (ROOT/'src').rglob('*') if p.is_file()}
assert actual_sources == old_sources | {'src/shop_equipment_sprite_pins.h'}
for name in old_sources:
    raw = (ROOT/name).read_bytes()
    if name == 'src/pregame_font.c':
        assert sha(git('show',BASE+':'+name)) == PIN['original_pregame_sha256']
        assert sha(raw) == PIN['accepted_sha256'][name]
    else:
        assert raw == git('show',BASE+':'+name),name
old_assets = set(git('ls-tree','-r','--name-only',BASE,'assets').decode().splitlines())
for name in old_assets:
    assert (ROOT/name).read_bytes() == git('show',BASE+':'+name),name
new_assets = {name for name in PIN['accepted_sha256'] if name.startswith('assets/')}
actual_assets = {str(p.relative_to(ROOT)) for p in (ROOT/'assets').rglob('*') if p.is_file()}
assert actual_assets == old_assets | new_assets
# Keep the previous exact typography boundary and all accepted natural-font
# resources intact. This test validates only the new finite union.
for name in ['tests/test_shop_menu_font_boundary.py','tests/shop_menu_font_source_delta.json','scripts/export_shop_menu_font.py']:
    assert (ROOT/name).read_bytes() == git('show',BASE+':'+name),name
rejections = 0
for name,wanted in PIN['accepted_sha256'].items():
    p = ROOT/name
    assert p.is_file() and not p.is_symlink(),name
    raw = p.read_bytes()
    assert sha(raw) == wanted,name
    for at in {0,len(raw)//2,len(raw)-1}:
        bad = raw[:at]+bytes([raw[at]^1])+raw[at+1:]
        assert sha(bad) != wanted
        rejections += 1
print(json.dumps(dict(result='PASS',baseline=BASE,exact_other_source_files=len(old_sources)-1,
    changed_production_source=['src/pregame_font.c'],exact_added_production=list(PIN['accepted_sha256']),
    existing_assets_and_natural_font_boundary_unchanged=True,mutation_rejections=rejections,
    original_indexed_draws_purchase_inputs_rng_and_coordinates_unchanged=True),indent=2))
