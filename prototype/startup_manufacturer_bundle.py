"""Validate the generated-only manufacturer artwork and separate MFG1 pack."""
from pathlib import Path
import hashlib
import json
import runpy

PACK = 'startup-manufacturer-v1'
SOURCE = 'assets/hd/artwork/' + PACK
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
    require({path.name for path in runtime_root.iterdir()} == RUNTIME_FILES,
            'Manufacturer runtime directory contains unexpected files')
    for name, (raw, receipt) in bundles.items():
        require(family['files'][name] == receipt, 'Runtime receipt differs from frozen manifest: ' + name)
        path = checked_file(repo, 'assets/hd/packs/' + PACK + '/' + name)
        require(path.read_bytes() == raw, 'Runtime bytes differ from canonical image: ' + name)
    return bundles
