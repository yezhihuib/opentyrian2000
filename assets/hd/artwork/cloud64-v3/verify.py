#!/usr/bin/env python3
"""Independent pixel checks and fresh/relocated rebuilds, using only this package."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
from PIL import Image, __version__ as pillow_version

ROOT = Path(__file__).resolve().parent
W, H = 192, 224
STEM = 'terrain-shapesz-64-8'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def rgba(path):
    with Image.open(path) as im:
        assert im.mode == 'RGBA' and im.size == (W, H)
        return im.tobytes()


def smooth(t):
    t = min(1.0, max(0.0, t))
    return t * t * (3 - 2 * t)


def connected_components(data, threshold):
    active = {q for q in range(W * H) if data[4 * q + 3] >= threshold}
    count = len(active)
    components = []
    while active:
        seed = min(active)
        active.remove(seed)
        component, queue = [seed], [seed]
        for q in queue:
            x, y = q % W, q // W
            for n in ([q - 1] if x else []) + ([q + 1] if x + 1 < W else []) + ([q - W] if y else []) + ([q + W] if y + 1 < H else []):
                if n in active:
                    active.remove(n)
                    queue.append(n)
                    component.append(n)
        components.append(component)
    bottoms = [max((y for y in range(H) if data[4 * (y * W + x) + 3] >= threshold), default=-1) for x in range(W)]
    return components, {'components': len(components), 'opaque_count': count,
                        'bottom_min': min(bottoms), 'bottom_max': max(bottoms)}


def python_reference(prior, generated):
    """Separate implementation of the authored registration and 4-neighbor cleanup."""
    result = bytearray(prior)
    for y in range(128, 200):
        for x in range(1, 191):
            n = 4 * (y * W + x)
            gy = min(223, y + 20)
            gn = 4 * (gy * W + x)
            weight = smooth((y - 128) / 16.0) * smooth((200 - y) / 16.0) * smooth(min(x, 191 - x) / 24.0)
            if weight <= 0:
                continue
            alpha = generated[gn + 3]
            alpha = 255 if alpha >= 250 else 0 if alpha < 4 else alpha
            cy = gy
            while cy > 0 and generated[4 * (cy * W + x) + 3] < 240:
                cy -= 1
            cn = 4 * (cy * W + x)
            for c in range(3):
                value = generated[cn + c] if generated[gn + 3] < 240 else generated[gn + c]
                result[n + c] = math.floor(prior[n + c] * (1 - weight) + value * weight + 0.5)
            result[n + 3] = math.floor(prior[n + 3] * (1 - weight) + alpha * weight + 0.5)
    components, _ = connected_components(result, 1)
    removed = []
    for component in components:
        if not any(q < W for q in component):
            for q in component:
                removed.append({'x': q % W, 'y': q // W, 'previous_alpha': result[4 * q + 3]})
                result[4 * q + 3] = 0
    return bytes(result), removed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, help='Optional report file; writes only when requested')
    args = parser.parse_args()
    sys.dont_write_bytecode = True
    import rebuild
    inputs, _ = rebuild.read_inputs()
    prior, generated = inputs
    selected_path = ROOT / 'output' / (STEM + '.png')
    selected = rgba(selected_path)
    hda = (ROOT / 'runtime-overlay' / (STEM + '.hda')).read_bytes()
    assert sha(selected) == rebuild.RGBA_SHA
    assert sha(selected_path.read_bytes()) == rebuild.SELECTED_PNG_SHA
    assert sha(hda) == rebuild.HDA_SHA
    assert hda == b'HDR1' + struct.pack('<6I', *rebuild.HEADER) + selected
    reference, removed = python_reference(prior, generated)
    assert reference == selected
    assert removed == [{'x': 104, 'y': 176, 'previous_alpha': 4}]
    changed = [(q % W, q // W) for q in range(W * H) if prior[4 * q:4 * q + 4] != selected[4 * q:4 * q + 4]]
    assert len(changed) == 12987
    assert all(1 <= x <= 190 and 129 <= y <= 199 for x, y in changed)
    bbox = [min(x for x, y in changed), min(y for x, y in changed), max(x for x, y in changed) + 1, max(y for x, y in changed) + 1]
    assert bbox == [1, 129, 191, 200]
    author = json.loads((ROOT / 'verification/author-static-contract.json').read_text())
    topology = {}
    for threshold in (1, 16, 128, 240):
        _, stats = connected_components(selected, threshold)
        assert stats == author['alpha_threshold_topology'][str(threshold)]
        topology[str(threshold)] = stats
    source_pngs = sorted(str(p.relative_to(ROOT)) for p in (ROOT / 'source').rglob('*.png'))
    assert source_pngs == sorted(rebuild.INPUTS)
    assert not any(p.is_symlink() for p in ROOT.rglob('*'))
    runs = []
    with tempfile.TemporaryDirectory(prefix='cloud64 independent audit ') as temp:
        workspace = Path(temp)
        for label, relative in [('fresh', 'fresh'), ('relocated_with_spaces', 'relocated package with spaces')]:
            package = workspace / relative
            (package / 'source').mkdir(parents=True)
            # Deliberately omit selected outputs, author report, master image and all game data.
            for item in ['rebuild.py', 'source/register_bottom64.cpp'] + list(rebuild.INPUTS):
                shutil.copyfile(ROOT / item, package / item)
            out = workspace / (label + ' rebuilt output with spaces')
            env = {k: v for k, v in os.environ.items() if k not in ('TYRIAN_DATA_DIR', 'PYTHONPATH')}
            subprocess.run([sys.executable, str(package / 'rebuild.py'), '--output-dir', str(out)],
                           cwd=workspace, env=env, check=True, capture_output=True, text=True)
            rebuilt_png = out / 'output' / (STEM + '.png')
            rebuilt_hda = out / 'runtime-overlay' / (STEM + '.hda')
            assert rgba(rebuilt_png) == selected
            assert rebuilt_hda.read_bytes() == hda
            assert sorted(str(p.relative_to(out)) for p in out.rglob('*') if p.is_file()) == [
                'output/' + STEM + '.png', 'rebuild-result.json', 'runtime-overlay/' + STEM + '.hda']
            runs.append({'case': label, 'pass': True, 'package_input_files': 4,
                         'original_data_supplied_or_requested_by_rebuild': False,
                         'selected_outputs_supplied_to_rebuild': False,
                         'rgba_sha256': sha(rgba(rebuilt_png)), 'hda_sha256': sha(rebuilt_hda.read_bytes()),
                         'rebuilt_png_sha256': sha(rebuilt_png.read_bytes()),
                         'png_file_equals_selected': rebuilt_png.read_bytes() == selected_path.read_bytes()})
        # Mutated authored inputs must be rejected before output or compiler execution.
        source = package / 'source/generated64-bottom-reference.png'
        data = source.read_bytes()
        source.write_bytes(data + b'noncanonical')
        bad_out = workspace / 'must not be created'
        mutation = subprocess.run([sys.executable, str(package / 'rebuild.py'), '--output-dir', str(bad_out)],
                                  cwd=workspace, env=env, capture_output=True, text=True)
        assert mutation.returncode != 0 and 'Canonical input file SHA-256 mismatch' in mutation.stderr
        assert not bad_out.exists()
        source.unlink()
        source.symlink_to(ROOT / 'source/generated64-bottom-reference.png')
        symlink = subprocess.run([sys.executable, str(package / 'rebuild.py'), '--output-dir', str(bad_out)],
                                 cwd=workspace, env=env, capture_output=True, text=True)
        assert symlink.returncode != 0 and 'regular, package-owned file' in symlink.stderr
        assert not bad_out.exists()
    report = {
        'schema': 'cloud64-v3-independent-package-verification-v1', 'pass': True,
        'python': sys.version.split()[0], 'pillow': pillow_version,
        'source_png_count': 2, 'source_pngs': source_pngs, 'all_files_package_owned': True,
        'source_mutation_rejected': True, 'external_source_symlink_rejected': True,
        'selected_png_sha256': sha(selected_path.read_bytes()),
        'selected_rgba_sha256': sha(selected), 'selected_hda_sha256': sha(hda),
        'independent_python_reference_exact': True, 'detached_alpha_removed': removed,
        'changed_pixels': len(changed), 'changed_bbox_exclusive': bbox,
        'all_four_rgba_faces_unchanged': True, 'rows_0_127_and_200_223_exact': True,
        'alpha_threshold_topology': topology, 'rebuilds': runs,
        'runtime_checks': 'Not run by this verifier; see verification/runtime-status.json for bounded external evidence',
    }
    text = json.dumps(report, indent=2) + '\n'
    if args.report:
        args.report.write_text(text)
    print(text)


if __name__ == '__main__':
    main()
