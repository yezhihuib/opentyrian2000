"""Build and verify the finite, opt-in title TLV1 plus manufacturer MFG1 pack.

Only the frozen generated-only title source package is an artwork input. The
original decoded source and palette hashes are compatibility identities, never
original game pixels. MFG1 compatibility resources are copied byte-for-byte.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import struct
import subprocess
import sys
import tempfile

from PIL import Image

PACK = 'startup-title-v1'
SOURCE = 'assets/hd/artwork/title-screen-v1'
SCHEMA = 'finite-startup-title-tlv1-v1'
MANUFACTURER_PACK = 'startup-manufacturer-v1'
SOURCE_MANIFEST_SHA256 = 'd7bd240f1210d01c3d0e01a81ec5511fe02be7972014d6564e333c54306bd7cc'
HEADER = struct.Struct('<4s11I4Q')
PALETTE_FNV64 = '8f64628a08533287'
SOURCE_FILES = frozenset((
    'FILES.sha256', 'README.md', 'build.py', 'expected-hashes.json',
    'generation-provenance.json', 'manifest.json', 'requirements.txt',
    'source-compatibility.json',
    'canonical/pic4-canonical4x.png', 'canonical/tyrian146-canonical4x.png',
    'canonical/year151-canonical4x.png', 'masters/left-clearance-master.png',
    'masters/pic4-master.png', 'masters/right-clearance-master.png',
    'masters/tyrian146-master.png', 'masters/year151-master.png',
    'proof/offline-validation.json', 'proof/reproduction.json',
    'proof/tyrian-alpha-correction-boundary-mask4x.png',
))
# These identities are independently pinned by the reviewed source contract.
SPECS = (
    ('pic4', 'pic4', 'title-pic4-v1.hda', 4, 320, 200, 0, None,
     '9a3f7cb8ec37073e', '9c9baa40cbccf525', '0abb22518a6634df'),
    ('tyrian146', 'planet146', 'title-planet146-v1.hda', 146, 304, 121, 1,
     (4, 4, 1216, 484), '30f8dbf0554a03ae', '0cb7de8084912543', '623a5b10ca52dae3'),
    ('year151', 'planet151', 'title-planet151-v1.hda', 151, 162, 64, 1,
     (8, 8, 644, 252), '4562ec954d257998', 'ee71b0121c53f8df', 'df98d9dd374ce169'),
)
TITLE_FILES = frozenset(spec[2] for spec in SPECS)
MANUFACTURER_HASHES = {
    'startup-pic10-v1.hda': 'a885d023f89b0e214a81df1d02dbf62d6e36645820c1a15e9a0ad74a2c5e2c79',
    'startup-pic12-v1.hda': 'bd358e8006a99467e08bc8bf257e6ead51fe5f216c63c57088612ef5039c7669',
}
RUNTIME_FILES = TITLE_FILES | MANUFACTURER_HASHES.keys()
TITLE_BYTES = 7113968
MANUFACTURER_BYTES = 8192128


def sha(data):
    return hashlib.sha256(data).hexdigest()


def fnv64(data):
    value = 14695981039346656037
    for byte in data:
        value = ((value ^ byte) * 1099511628211) & 0xffffffffffffffff
    return f'{value:016x}'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def checked_file(root, name):
    root = Path(root)
    require(not any(p.is_symlink() for p in (root, *root.parents)),
            'Symlink input directory is not supported')
    root = root.resolve()
    relative = Path(name)
    require(not relative.is_absolute() and '..' not in relative.parts,
            'Uncontained manifest path')
    path = root / relative
    require(not any(p.is_symlink() for p in (path, *path.parents) if p != root),
            'Symlink input is not supported')
    require(path.is_file() and root in path.resolve().parents,
            'Missing or escaped file: ' + name)
    return path


def require_inventory(root, filenames, label):
    root = Path(root)
    require(root.is_dir() and not root.is_symlink(), 'Missing or symlinked ' + label)
    paths = list(root.rglob('*'))
    require(not any(path.is_symlink() for path in paths), 'Symlink in ' + label)
    expected_directories = {
        parent.as_posix() for name in filenames for parent in Path(name).parents
        if parent != Path('.')
    }
    require({p.relative_to(root).as_posix() for p in paths if p.is_file()} == set(filenames),
            label + ' differs from finite file inventory')
    require({p.relative_to(root).as_posix() for p in paths if p.is_dir()} == expected_directories,
            label + ' differs from finite directory inventory')
    require(all(p.is_file() or p.is_dir() for p in paths), 'Non-regular entry in ' + label)


def source_receipts(source):
    """Check all nineteen exact files before decoding or executing source inputs."""
    source = Path(source)
    require_inventory(source, SOURCE_FILES, 'Title source tree')
    raw_manifest = checked_file(source, 'manifest.json').read_bytes()
    require(sha(raw_manifest) == SOURCE_MANIFEST_SHA256, 'Frozen source manifest identity changed')
    manifest = json.loads(raw_manifest)
    require(manifest['schema'] == 'title-screen-generated-source-v1', 'Wrong source schema')
    records = manifest['files']
    require(len(records) == 17 and {r['path'] for r in records} == SOURCE_FILES - {'manifest.json', 'FILES.sha256'},
            'Source manifest inventory changed')
    receipts = {}
    for name in sorted(SOURCE_FILES):
        data = checked_file(source, name).read_bytes()
        receipts[name] = {'bytes': len(data), 'sha256': sha(data)}
    for record in records:
        require(receipts[record['path']] == {k: record[k] for k in ('bytes', 'sha256')},
                'Frozen source hash mismatch: ' + record['path'])
    require(manifest['file_count_excluding_manifest_and_FILES'] == len(records),
            'Source manifest count changed')
    require(manifest['total_bytes_excluding_manifest_and_FILES'] == sum(r['bytes'] for r in records),
            'Source manifest byte count changed')
    expected_sums = [receipts[name]['sha256'] + '  ' + name
                     for name in sorted(SOURCE_FILES - {'FILES.sha256'})]
    require(checked_file(source, 'FILES.sha256').read_bytes() ==
            ('\n'.join(expected_sums) + '\n').encode('ascii'),
            'FILES.sha256 differs from the frozen inventory')
    return receipts


def validate_rgba(payload, width, height, alpha_mode, bounds):
    """Reject hidden RGB, out-of-bounds support and nonopaque background pixels."""
    require(alpha_mode in (0, 1), 'Unsupported alpha mode')
    require(len(payload) == width * height * 4, 'Wrong canonical RGBA byte count')
    alpha = payload[3::4]
    if alpha_mode == 0:
        require(alpha == b'\xff' * (width * height), 'PIC4 must be entirely opaque')
    else:
        require(any(0 < value < 255 for value in alpha), 'Logo partial alpha was lost')
        x0, y0, x1, y1 = bounds
        require(0 <= x0 < x1 <= width and 0 <= y0 < y1 <= height, 'Invalid support bound')
        for y in range(height):
            row = alpha[y * width:(y + 1) * width]
            require(not any(row) if y < y0 or y >= y1 else not any(row[:x0]) and not any(row[x1:]),
                    'Logo alpha exceeds its registered support bound')
    require(all(payload[i:i + 3] == b'\0\0\0' for i in range(0, len(payload), 4)
                if payload[i + 3] == 0), 'Nonzero hidden RGB at alpha zero')


def build_resources(source):
    """Construct the three TLV1 resources directly from frozen canonical RGBA."""
    source = Path(source)
    source_receipts(source)
    expected = json.loads(checked_file(source, 'expected-hashes.json').read_text())
    contract = json.loads(checked_file(source, 'source-compatibility.json').read_text())
    require(contract['palette']['zero_based_palette_id'] == 8 and
            contract['palette']['RGB_fnv64'] == PALETTE_FNV64, 'Palette source identity changed')
    bundles = {}
    for asset, original, filename, identity, w, h, alpha_mode, bounds, indices, mask, payload_fnv in SPECS:
        spec = contract['assets'][original]
        require(spec['native_canvas_wh'] == [w, h] and spec['output_4x_canvas_wh'] == [w * 4, h * 4],
                'Source dimensions changed: ' + asset)
        require(spec['decoded_indices_fnv64'] == indices and spec['opaque_mask_fnv64'] == mask,
                'Original decoded source identity changed: ' + asset)
        if bounds is not None:
            require(spec['output_4x_reference_opaque_bbox_xyxy_half_open'] == list(bounds),
                    'Source support bound changed: ' + asset)
        png_name = 'canonical/' + asset + '-canonical4x.png'
        path = checked_file(source, png_name)
        stamp = expected['canonical'][asset]
        require(sha(path.read_bytes()) == stamp['png_sha256'], 'Canonical PNG identity changed: ' + asset)
        with Image.open(path) as image:
            require(image.mode == 'RGBA' and image.size == (w * 4, h * 4), 'Unexpected PNG mode or dimensions')
            payload = image.tobytes()
        validate_rgba(payload, w * 4, h * 4, alpha_mode, bounds)
        require(len(payload) == stamp['rgba_bytes'] and sha(payload) == stamp['rgba_sha256'] and
                sha(payload[3::4]) == stamp['alpha_sha256'], 'Canonical decoded identity changed: ' + asset)
        require(fnv64(payload) == payload_fnv == stamp['rgba_fnv64'], 'Canonical payload FNV mismatch: ' + asset)
        u32 = [1, 4, identity, w, h, 8, alpha_mode, len(payload), 0, 0, 0]
        u64 = [indices, mask, PALETTE_FNV64, payload_fnv]
        raw = HEADER.pack(b'TLV1', *u32, *(int(value, 16) for value in u64)) + payload
        receipt = {
            'bytes': len(raw), 'sha256': sha(raw), 'format': 'TLV1',
            'header_bytes': HEADER.size, 'header_u32': u32, 'asset_id': identity,
            'density': 4, 'logical_dimensions': [w, h], 'pixel_dimensions': [w * 4, h * 4],
            'palette_zero_based': 8, 'alpha_mode': alpha_mode, 'payload_bytes': len(payload),
            'decoded_indices_fnv64': indices, 'opacity_fnv64': mask,
            'palette_rgb_fnv64': PALETTE_FNV64, 'payload_fnv64': payload_fnv,
            'source_png': png_name, 'source_png_sha256': stamp['png_sha256'],
            'canonical_rgba_sha256': stamp['rgba_sha256'], 'alpha_sha256': stamp['alpha_sha256'],
            'alpha_support_bounds_4x': list(bounds) if bounds else [0, 0, w * 4, h * 4],
        }
        bundles[filename] = (raw, receipt)
    require(sum(len(raw) for raw, _ in bundles.values()) == TITLE_BYTES, 'Unexpected total TLV1 bytes')
    return bundles


def build_family(repo):
    """Compute an independent family receipt, preserving existing MFG1 records."""
    repo = Path(repo).resolve()
    manifest = json.loads(checked_file(repo, 'assets/hd/manifest.json').read_text())
    require(PACK not in manifest.get('packs', {}), 'TLV1/MFG1 must not enter the HDR1 pack loop')
    source = repo / SOURCE
    receipts = source_receipts(source)
    bundles = build_resources(source)
    family = manifest['startup_manufacturer_v1']
    require(family['pack'] == MANUFACTURER_PACK and family['count'] == 2 and
            set(family['files']) == set(MANUFACTURER_HASHES), 'Unexpected MFG1 compatibility family')
    original_root = repo / 'assets/hd/packs' / MANUFACTURER_PACK
    require_inventory(original_root, MANUFACTURER_HASHES, 'Original manufacturer runtime pack')
    for name, expected_sha in MANUFACTURER_HASHES.items():
        raw = checked_file(original_root, name).read_bytes()
        receipt = family['files'][name]
        require(len(raw) == receipt['bytes'] == 4096064 and
                sha(raw) == receipt['sha256'] == expected_sha and raw[:4] == b'MFG1',
                'Original manufacturer compatibility identity changed: ' + name)
        bundles[name] = (raw, receipt)
    result = {
        'schema': SCHEMA, 'source': SOURCE, 'pack': PACK,
        'count': len(RUNTIME_FILES), 'title_count': len(TITLE_FILES),
        'manufacturer_compatibility_count': len(MANUFACTURER_HASHES),
        'title_resource_bytes': TITLE_BYTES, 'manufacturer_compatibility_bytes': MANUFACTURER_BYTES,
        'manufacturer_compatibility_source_pack': MANUFACTURER_PACK,
        'source_manifest_sha256': SOURCE_MANIFEST_SHA256,
        'files': {name: receipt for name, (_, receipt) in sorted(bundles.items())},
        'source_files': receipts,
    }
    return bundles, result


def build_bundles(repo):
    """Verify the frozen family receipt and every packaged runtime byte."""
    repo = Path(repo).resolve()
    bundles, expected = build_family(repo)
    manifest = json.loads(checked_file(repo, 'assets/hd/manifest.json').read_text())
    require(manifest['startup_title_v1'] == expected, 'Title family differs from independent receipt')
    runtime_root = repo / 'assets/hd/packs' / PACK
    require_inventory(runtime_root, RUNTIME_FILES, 'Title runtime pack')
    for name, (raw, _) in bundles.items():
        require(checked_file(runtime_root, name).read_bytes() == raw,
                'Runtime bytes differ from frozen source: ' + name)
    return bundles


def verify_source_rebuild(repo):
    """Run the immutable builder relocated with only masters and hash inputs.

    Canonical PNGs, game files, source metadata and all proofs are deliberately
    absent from the relocated input. The builder must reproduce PNG and RGBA.
    """
    source = Path(repo).resolve() / SOURCE
    source_receipts(source)
    with tempfile.TemporaryDirectory(prefix='title-source-rebuild-') as temporary:
        base = Path(temporary)
        relocated = base / 'source'
        relocated.mkdir()
        for name in sorted({'build.py', 'expected-hashes.json'} |
                           {p for p in SOURCE_FILES if p.startswith('masters/')}):
            target = relocated / name
            target.parent.mkdir(exist_ok=True)
            shutil.copyfile(checked_file(source, name), target)
        output = base / 'rebuilt'
        result = subprocess.run([sys.executable, '-B', str(relocated / 'build.py'), '--output', str(output)],
                                check=True, capture_output=True, text=True)
        report = json.loads(result.stdout)
        require(report['status'] == 'PASS' and report['movement_positions'] == 29,
                'Relocated source builder did not pass')
        for asset, *_ in SPECS:
            filename = asset + '-canonical4x.png'
            original = checked_file(source, 'canonical/' + filename)
            require(checked_file(output, filename).read_bytes() == original.read_bytes(),
                    'Relocated PNG rebuild differs: ' + asset)
            with Image.open(original) as expected, Image.open(output / filename) as actual:
                require(actual.mode == expected.mode == 'RGBA' and actual.size == expected.size and
                        actual.tobytes() == expected.tobytes(), 'Relocated RGBA rebuild differs: ' + asset)
        require((output / 'tyrian-alpha-correction-boundary-mask4x.png').read_bytes() ==
                checked_file(source, 'proof/tyrian-alpha-correction-boundary-mask4x.png').read_bytes(),
                'Generated correction mask rebuild differs')
        return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify-rebuild', action='store_true',
                        help='also rebuild the immutable source in an isolated temporary directory')
    args = parser.parse_args()
    repo = Path(__file__).resolve().parent.parent
    bundles = build_bundles(repo)
    rebuilt = verify_source_rebuild(repo) if args.verify_rebuild else None
    print(json.dumps({
        'pack': PACK, 'verified_title_resources': len(TITLE_FILES),
        'verified_manufacturer_compatibility_copies': len(MANUFACTURER_HASHES),
        'verified_source_files': len(SOURCE_FILES), 'unique_TLV1_bytes': TITLE_BYTES,
        'MFG1_compatibility_copy_bytes': MANUFACTURER_BYTES,
        'total_runtime_bytes': sum(len(raw) for raw, _ in bundles.values()),
        'source_only_relocated_rebuild': bool(rebuilt),
        'all_runtime_RGBA_and_header_bytes_exact': True,
    }, indent=2))


if __name__ == '__main__':
    main()
