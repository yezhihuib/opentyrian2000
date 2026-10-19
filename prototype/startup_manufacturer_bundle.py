"""Validate the generated-only manufacturer artwork and MFG1 subset of the current startup pack."""
from pathlib import Path
import hashlib
import json
import runpy

PACK = 'startup-title-settings-v1'
SOURCE = 'assets/hd/artwork/startup-manufacturer-v1'
SCHEMA = 'finite-startup-manufacturer-mfg1-v1'
SOURCE_FILES = frozenset((
    'FILES.txt', 'README.md', 'SHA256SUMS', 'build_previews.py', 'build_resource.py',
    'import.json', 'masters/pic10-xsiv-generated-master.png',
    'masters/pic12-eclipse-generated-master.png',
    'previews/pic10-candidate-native2x.png', 'previews/pic10-candidate-native4x.png',
    'previews/pic12-candidate-native2x.png', 'previews/pic12-candidate-native4x.png',
    'previews/validation.json', 'prompts.json', 'registration-review.json',
    'reproduction-proof.json', 'requirements.txt', 'source-compatibility.json',
    'provenance/pilot-FILES.txt', 'provenance/pilot-README.md',
    'provenance/pilot-SHA256SUMS', 'provenance/pilot-manifest.json',
))
RUNTIME_FILES = frozenset(('startup-pic10-v1.hda', 'startup-pic12-v1.hda'))
CURRENT_RUNTIME_FILES = RUNTIME_FILES | frozenset((
    'title-pic4-v1.hda', 'title-planet146-v1.hda', 'title-planet151-v1.hda',
    'title-menu-font-v1.hda', 'settings-font-large-v1.hda',
    'settings-font-medium-v1.hda', 'settings-font-tiny-v1.hda',
))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def checked_file(root, name):
    root = Path(root).resolve()
    relative = Path(name)
    require(not relative.is_absolute() and '..' not in relative.parts, 'Uncontained manifest path')
    path = root / relative
    require(path.is_file() and root in path.resolve().parents, 'Missing or escaped file: ' + name)
    require(not any(p.is_symlink() for p in (path, *path.parents) if p != root),
            'Symlink input is not supported')
    return path


def build_bundles(repo):
    """Rebuild from exact canonical PNGs and verify the independent manifest entry."""
    repo = Path(repo).resolve()
    manifest = json.loads(checked_file(repo, 'assets/hd/manifest.json').read_text())
    family = manifest['startup_manufacturer_v1']
    require(family['schema'] == SCHEMA and family['source'] == SOURCE and family['pack'] == PACK,
            'Unexpected manufacturer family')
    require(PACK not in manifest.get('packs', {}), 'MFG1 must not enter the HDR1 pack loop')
    require(family['count'] == 2 and set(family['files']) == RUNTIME_FILES,
            'Manufacturer pack must contain exactly PIC10 and PIC12')
    require(set(family['source_files']) == SOURCE_FILES, 'Unexpected manufacturer source inventory')
    source = repo / SOURCE
    require(source.is_dir() and not source.is_symlink(), 'Missing or symlinked source artwork directory')
    paths = list(source.rglob('*'))
    require(not any(path.is_symlink() for path in paths), 'Symlinks are not accepted in source artwork')
    require({path.relative_to(source).as_posix() for path in paths if path.is_file()} == SOURCE_FILES,
            'Manufacturer source tree differs from finite inventory')
    for name, receipt in family['source_files'].items():
        data = checked_file(source, name).read_bytes()
        require(receipt == {'bytes': len(data), 'sha256': sha(data)}, 'Source hash mismatch: ' + name)
    names = checked_file(source, 'FILES.txt').read_text().splitlines()
    require(names == sorted(SOURCE_FILES), 'FILES.txt is not the exact sorted source inventory')
    sums = checked_file(source, 'SHA256SUMS').read_text().splitlines()
    expected = [family['source_files'][name]['sha256'] + '  ' + name
                for name in sorted(SOURCE_FILES - {'SHA256SUMS'})]
    require(sums == expected, 'SHA256SUMS differs from the source inventory')
    # run_path does not write __pycache__ into the frozen source inventory.
    module = runpy.run_path(str(source / 'build_resource.py'))
    bundles = module['build_resources'](source)
    require(set(bundles) == RUNTIME_FILES, 'Unexpected generated runtime filenames')
    runtime_root = repo / 'assets/hd/packs' / PACK
    require(runtime_root.is_dir() and not runtime_root.is_symlink(), 'Missing or symlinked runtime pack')
    paths = list(runtime_root.iterdir())
    require({path.name for path in paths} == CURRENT_RUNTIME_FILES and
            all(path.is_file() and not path.is_symlink() for path in paths),
            'Current startup runtime directory differs from its finite inventory')
    for name, (raw, receipt) in bundles.items():
        require(family['files'][name] == receipt, 'Runtime receipt differs from frozen manifest: ' + name)
        path = checked_file(repo, 'assets/hd/packs/' + PACK + '/' + name)
        require(path.read_bytes() == raw, 'Runtime bytes differ from canonical image: ' + name)
    return bundles


# Exact historical recipes are projected only for pre-existing preservation
# tests. They remain archived metadata, never installed runtime dependencies.
RETIRED_GAMEPLAY_PACKS = (
    'packed-talon13-foundation-type10-explosion-v2-test',
    'packed-blue-four-foundation-type10-explosion-v2-test',
    'packed-talon13-foundation-type10-explosion-v2-large-air-v1-test',
    'packed-blue-four-foundation-type10-explosion-v2-large-air-v1-test',
    'packed-talon13-foundation-type10-explosion-v2-large-air-v1-impact-v1-test',
    'packed-blue-four-foundation-type10-explosion-v2-large-air-v1-impact-v1-test',
    'packed-talon13-foundation-type10-death-effects-v1-test',
    'packed-blue-four-foundation-type10-death-effects-v1-test',
    'packed-talon13-foundation-type10-death-effects-white-smoke-v1-test',
    'packed-blue-four-foundation-type10-death-effects-white-smoke-v1-test',
    'packed-talon13-foundation-type10-death-effects-white-smoke-shield-v1-test',
    'packed-blue-four-foundation-type10-death-effects-white-smoke-shield-v1-test',
    'packed-talon13-foundation-type10-death-effects-white-smoke-shield-green-v1-test',
    'packed-blue-four-foundation-type10-death-effects-white-smoke-shield-green-v1-test',
    'packed-talon13-foundation-type10-death-effects-white-smoke-shield-green-v2-test',
    'packed-blue-four-foundation-type10-death-effects-white-smoke-shield-green-v2-test',
)
ACTIVE_GAMEPLAY_PACKS = (
    'packed-talon13-foundation-type10-death-effects-white-smoke-shield-green-v2-head-v1-test',
    'packed-blue-four-foundation-type10-death-effects-white-smoke-shield-green-v2-head-v1-test',
)
RETIRED_GAMEPLAY_SHA256 = 'adec3a11fc1d08fe2e598039547352afda3c5291c3afed7ba332b259ea54024b'


def project_retired_resources_for_historical_checks(manifest):
    """Validate the finite retirement delta, then restore its historical view.

    Mutates only a caller-owned manifest copy. All archived receipts are pinned
    before projection; unknown archives, changed defaults and route edits fail.
    Existing historical whole-manifest/hash tests continue to verify everything
    else against their original published checkpoints.
    """
    archived = manifest.get('retired_packs')
    require(isinstance(archived, dict) and set(archived) == set(RETIRED_GAMEPLAY_PACKS),
            'Retired gameplay recipe inventory changed')
    encoded = json.dumps(archived, sort_keys=True, separators=(',', ':')).encode()
    require(sha(encoded) == RETIRED_GAMEPLAY_SHA256,
            'Retired gameplay recipe receipts changed')
    packs = manifest['packs']
    require(set(packs) == set(ACTIVE_GAMEPLAY_PACKS) and
            manifest['default_preview_pack'] == ACTIVE_GAMEPLAY_PACKS[0] and
            manifest['default_debug_pack'] == ACTIVE_GAMEPLAY_PACKS[1],
            'Active gameplay pack scope changed')
    locations = {
        'startup_manufacturer_v1': {'pack': 'startup-manufacturer-v1'},
        'startup_title_v1': {
            'pack': 'startup-title-v1',
            'manufacturer_compatibility_source_pack': 'startup-manufacturer-v1',
        },
        'startup_title_menu_v1': {
            'pack': 'startup-title-menu-v1',
            'compatibility_source_pack': 'startup-title-v1',
        },
    }
    if 'startup_settings_font_v1' in manifest:
        locations['startup_settings_font_v1'] = {
            'compatibility_source_pack': 'startup-title-menu-v1',
        }
    for family, fields in locations.items():
        for field in fields:
            require(manifest[family][field] == PACK,
                    'Current startup family route changed: ' + family + '.' + field)
    manifest['packs'] = {name: archived[name] for name in RETIRED_GAMEPLAY_PACKS}
    manifest['packs'].update({name: packs[name] for name in ACTIVE_GAMEPLAY_PACKS})
    del manifest['retired_packs']
    for family, fields in locations.items():
        manifest[family].update(fields)
