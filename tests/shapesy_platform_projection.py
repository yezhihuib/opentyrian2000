"""Finite PUBLIC7d ShapesY extension; no Git or original game data at verification.

The current family must independently regenerate before its paths are removed
from an older oracle. Frozen earlier ledgers and their expected hashes stay fixed.
"""
from pathlib import Path
import copy
import hashlib
import importlib.util
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_BASE = '7d94cf87740566e40c91043dcf2ebe2fb4e0e67b'
LEDGER = 'tests/current_shapesy_platform_source_projection.json'
LEDGER_SHA256 = 'b8ec82c1c5afe091f45489bb844f3e44b1a8a5c11f10f9a5b433aa66c572e331'
FILES = {'src/render_mirror.c', 'src/render_mirror.h', 'src/backgrnd.c',
         'src/video.c', 'src/video.h'}
ADDED = {'src/shapesy_platform_mirror.inc', 'src/current_shapesy_platform_source.h',
         'src/current_shapesy_platform_hd_assets.h', 'src/current_shapesy_contour_materials.h'}
CONTOUR_GENERATOR = 'prototype/build-shapesy-contour-materials.py'
CONTOUR_HEADER = 'src/current_shapesy_contour_materials.h'
CATALOG = 'assets/hd/manifest.json'
IDS = (321,322,323,324,325,326,331,332,333,334,336,341,342,343,346,
       351,352,353,354,361,362,363,364,365,374,375,384,385)
PACKS = ('packed-talon13-foundation-type10-death-effects-white-smoke-shield-green-v2-head-v1-test',
         'packed-blue-four-foundation-type10-death-effects-white-smoke-shield-green-v2-head-v1-test')
ASSETS = {'assets/hd/authoring/shapesy-platform-current.json'} | {
    f'assets/hd/source/terrain-shapesy-{i}-8.png' for i in IDS} | {
    f'assets/hd/packs/{pack}/terrain-shapesy-{i}-8.hda' for pack in PACKS for i in IDS}
sha = lambda raw: hashlib.sha256(raw).hexdigest()
canonical = lambda obj: json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()


def ledger():
    raw = (ROOT / LEDGER).read_bytes()
    assert sha(raw) == LEDGER_SHA256, 'ShapesY qualification ledger changed or not frozen'
    spec = json.loads(raw)
    assert spec['public_base'] == PUBLIC_BASE
    assert set(spec['files']) == FILES, 'ShapesY changed-source scope drift'
    assert set(spec['added_sources']) == ADDED, 'ShapesY added-source scope drift'
    assert set(spec['asset_edits']) == {CATALOG}, 'ShapesY existing-asset edit scope drift'
    assert set(spec['asset_additions']) == ASSETS and len(ASSETS) == 85, 'ShapesY added-asset scope drift'
    return spec


def inverse(name, raw, pin):
    assert sha(raw) == pin['current_sha256'], ('unapproved ShapesY current blob', name)
    lines = raw.splitlines(keepends=True)
    for edit in reversed(pin['hunks']):
        a, b = edit['after_lines']
        assert b''.join(lines[a:b]) == edit['after'].encode(), ('ShapesY inverse hunk drift', name)
        lines[a:b] = edit['before'].encode().splitlines(keepends=True)
    restored = b''.join(lines)
    assert sha(restored) == pin['previous_sha256'], ('ShapesY PUBLIC7d preimage drift', name)
    return restored


def project_source(name, raw):
    # Only this inverse owns these paths; linked stages may already have
    # restored their unrelated inputs to an older exact chain position.
    if name in FILES | ADDED:
        from dualmissile_newshf_projection import project_if_current
        raw = project_if_current(name, raw)
    pin = ledger()['files'].get(name)
    return raw if pin is None else inverse(name, raw, pin)


def project_asset(name, raw):
    pin = ledger()['asset_edits'].get(name)
    return raw if pin is None else inverse(name, raw, pin)


def qualified_paths(root=ROOT):
    spec = ledger()
    return set(spec['qualified']) | set(spec['files']) | set(spec['asset_edits'])


def checked_read(root, name):
    path = root / name
    assert path.is_file() and not path.is_symlink(), ('nonregular ShapesY input', name)
    assert not any(p.is_symlink() for p in path.parents), ('symlink ShapesY ancestor', name)
    from dualmissile_newshf_projection import project_if_current
    return project_if_current(name, path.read_bytes())


def verified(root=ROOT):
    from dualmissile_newshf_projection import verified as dual_verified
    dual_verified(root)
    spec = ledger()
    for name, digest in spec['qualified'].items():
        assert sha(checked_read(root,name)) == digest, ('unqualified ShapesY input', name)
    for name in spec['files']:
        project_source(name, checked_read(root,name))
    for name in spec['asset_edits']:
        project_asset(name, checked_read(root,name))
    scripts = str(ROOT / 'scripts')
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    import current_shapesy_platform_compatibility as c
    mapping = c.load(root)
    assert len(mapping) == 28 and set(mapping) == {
        f'assets/gameplay/terrain-shapesy-{i}-8.hda' for i in IDS}, 'ShapesY runtime closure drift'
    # Qualify every input first, then independently reconstruct the new material
    # header before older source oracles may remove it from their inventories.
    path = root / CONTOUR_GENERATOR
    loader = importlib.util.spec_from_file_location('qualified_shapesy_contour_materials', path)
    assert loader and loader.loader, 'Missing ShapesY contour material generator'
    generator = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(generator)
    contour_inputs = {p.relative_to(root).as_posix() for p in generator.input_paths(root)}
    assert contour_inputs <= set(spec['qualified']), 'Unqualified contour generator dependency'
    rebuilt = generator.generate(root)
    assert rebuilt == checked_read(root, CONTOUR_HEADER), 'ShapesY contour material reconstruction drift'
    names = c.input_paths(root) | {c.MAPPING, c.HEADER} | ADDED | {
        'scripts/current_shapesy_platform_compatibility.py',
        'scripts/build_current_shapesy_platform.py',
        'prototype/build-shapesy-platform-art.py',
        'scripts/current_guided_compatibility.py', 'scripts/build_newshf_hd.py',
        'scripts/build_current_art.py', 'scripts/build_current_craft267.py',
        'scripts/current_craft267_compatibility.py'}
    names |= set(spec['asset_additions']) | contour_inputs | {CONTOUR_GENERATOR}
    assert set(spec['qualified']) == names, 'ShapesY qualified path closure drift'
    assets = {n: {'sha256': spec['qualified'][n], 'mode': '100644'}
              for n in spec['asset_additions']}
    assert all(n.startswith('assets/') for n in assets)
    assert not set(assets) & set(spec['asset_edits'])
    assert {n: spec['qualified'][n] for n in ADDED} == spec['added_sources']
    return dict(mapping=mapping, added_sources={n: sha((root/n).read_bytes()) for n in spec['added_sources']}, assets=assets,
                paths=names, asset_edits=spec['asset_edits'])


def before_inventory(inventory, root=ROOT):
    from dualmissile_newshf_projection import before_inventory as dual_before
    result = dual_before(inventory, root)
    proof = verified(root)
    for name, digest in ledger()['added_sources'].items():
        assert result.pop(name) == digest, ('ShapesY added source inventory drift', name)
    for name in FILES:
        raw = checked_read(root, name)
        assert result[name] == sha(raw), ('ShapesY changed source inventory drift', name)
        result[name] = sha(project_source(name, raw))
    return result


def before_runtime(rows, root=ROOT):
    from dualmissile_newshf_projection import before_runtime as dual_before
    rows = dual_before(rows, root)
    mapping = verified(root)['mapping']
    seen, result = set(), []
    for row in rows:
        destination = row['destination']
        if destination not in mapping:
            result.append(row)
            continue
        current = mapping[destination]
        raw = (root / current['source_path']).read_bytes()
        expected = dict(destination=destination, source_path=current['source_path'],
            sha256=sha(raw), bytes=len(raw),
            git_blob=hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest(),
            group='gameplay', revision='current-single-source-shapesy-platform-28')
        assert row == expected and destination not in seen, 'ShapesY runtime row drift'
        seen.add(destination)
    assert seen == set(mapping), 'Missing ShapesY runtime consumer'
    return result


def project_catalog(catalog):
    spec = ledger()
    assert sha(canonical(catalog)) == spec['catalog_current_sha256'], 'Unapproved live ShapesY catalog'
    result = copy.deepcopy(catalog)
    for pack in (result['default_preview_pack'], result['default_debug_pack']):
        for i in IDS:
            del result['packs'][pack]['files'][f'terrain-shapesy-{i}-8.hda']
        result['packs'][pack]['count'] -= len(IDS)
    assert sha(canonical(result)) == spec['catalog_previous_sha256'], 'ShapesY catalog PUBLIC7d preimage drift'
    return result
