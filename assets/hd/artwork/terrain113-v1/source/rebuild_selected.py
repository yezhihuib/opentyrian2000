#!/usr/bin/env python3
"""Rebuild only terrain113 from authored RGBA and frozen perimeter constraints."""
from pathlib import Path
from PIL import Image, __version__ as pillow_version
import argparse
import hashlib
import json
import platform
import struct
import subprocess
import zlib


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(path.read_text())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-root', type=Path, required=True,
                        help='New directory; existing paths are never overwritten')
    parser.add_argument('--compiler', default='c++')
    args = parser.parse_args()
    source = Path(__file__).resolve().parent
    package = source.parent
    output = args.output_root.resolve()
    require(not output.exists(), 'Output directory already exists')
    require(package != output and package not in output.parents,
            'Use an output directory outside the source package')
    contract = read_json(source / 'rebuild-contract.json')
    width, height = contract['width'], contract['height']
    require((width, height) == (192, 224), 'Unexpected tile dimensions')
    for relative, expected in contract['inputs'].items():
        require(sha((source / relative).read_bytes()) == expected,
                f'Input hash mismatch: {relative}')
    crop = Image.open(source / 'generated-crops/terrain-shapesz-113-8.png').convert('RGBA')
    generated = crop.tobytes()
    alpha = crop.getchannel('A').tobytes()
    require(crop.size == (width, height), 'Authored crop dimensions differ')
    require(sha(generated) == contract['generated_rgba_sha256'], 'Authored RGBA differs')
    require(sha(alpha) == contract['alpha_sha256'], 'Approved alpha differs')
    require(set(alpha) == {0, 255} and alpha.count(0) == 448, 'Binary alpha count differs')
    logical_holes = 0
    for ly in range(28):
        for lx in range(24):
            block = [alpha[y * width + x]
                     for y in range(ly * 8, (ly + 1) * 8)
                     for x in range(lx * 8, (lx + 1) * 8)]
            require(len(set(block)) == 1, 'Alpha is not exact 8x logical occupancy')
            logical_holes += block[0] == 0
    require(logical_holes == 7, 'Logical transparency count differs')
    perimeter_alpha = (alpha[:width] + alpha[-width:]
                       + alpha[::width] + alpha[width - 1::width])
    require(set(perimeter_alpha) == {255}, 'Outer perimeter is not opaque')

    constraints = read_json(source / 'frozen-edge-constraints.json')
    require(sorted(map(int, constraints['tiles'])) == contract['frozen_ids'],
            'Frozen neighbor IDs differ')
    require((constraints['width'], constraints['height']) == (width, height),
            'Frozen constraint dimensions differ')
    for folder in ['work', 'output', 'runtime-overlay']:
        (output / folder).mkdir(parents=True, exist_ok=True)
    work = output / 'work'
    (work / '113.rgba').write_bytes(generated)
    frozen_inputs = {}
    for tile, data in constraints['tiles'].items():
        # Only these exact perimeter samples enter the native harmonic solver.
        # Interior pixels are disposable zeros, never original or accepted art.
        rgba = bytearray(b'\x00\x00\x00\xff' * (width * height))
        seen = {}
        positions = {
            'top': [(x, 0) for x in range(width)],
            'bottom': [(x, height - 1) for x in range(width)],
            'left': [(0, y) for y in range(height)],
            'right': [(width - 1, y) for y in range(height)],
        }
        for side, points in positions.items():
            values = bytes.fromhex(data[f'{side}_rgb_hex'])
            require(len(values) == len(points) * 3, f'Invalid {tile} {side} length')
            for n, point in enumerate(points):
                rgb = values[n * 3:n * 3 + 3]
                require(point not in seen or seen[point] == rgb,
                        f'Inconsistent corner for frozen neighbor {tile}')
                seen[point] = rgb
                x, y = point
                index = (y * width + x) * 4
                rgba[index:index + 3] = rgb
        path = work / f'{tile}.rgba'
        path.write_bytes(rgba)
        frozen_inputs[tile] = sha(rgba)

    binary = output / 'register_edges'
    subprocess.run([args.compiler, '-O2', '-std=c++17',
                    str(source / 'register_terrain_edges.cpp'), '-o', str(binary)], check=True)
    registration = subprocess.run([str(binary), str(work),
                                   str(source / 'registered-edge-pairs.txt')],
                                  check=True, text=True, capture_output=True)
    print(registration.stdout, end='')
    require(sha((work / '113.rgba').read_bytes()) == sha(generated), 'Authored input changed')
    for tile, expected in frozen_inputs.items():
        require(sha((work / f'{tile}.rgba').read_bytes()) == expected,
                f'Frozen neighbor {tile} changed')
    result = (work / '113-registered.rgba').read_bytes()
    require(len(result) == width * height * 4, 'Registered RGBA length differs')
    require(result[3::4] == alpha, 'Registration changed alpha')
    require(all(result[i:i + 3] == b'\x00\x00\x00'
                for i in range(0, len(result), 4) if result[i + 3] == 0),
            'Transparent output RGB is not canonical zero')
    png = output / 'output/terrain-shapesz-113-8.png'
    # Same Pillow wrapper as the selected candidate. Encoding is independently
    # reported because Pillow/zlib versions may differ; pixels and HDA must not.
    Image.frombytes('RGBA', (width, height), result).save(png)
    require(Image.open(png).convert('RGBA').tobytes() == result, 'PNG decode differs')
    hda_bytes = b'HDR1' + struct.pack('<6I', 2010113, 8, 24, 28, 0, 0) + result
    require(len(hda_bytes) == 172060, 'HDA length differs')
    hda = output / 'runtime-overlay/terrain-shapesz-113-8.hda'
    hda.write_bytes(hda_bytes)
    actual = {'png_sha256': sha(png.read_bytes()), 'rgba_sha256': sha(result),
              'hda_sha256': sha(hda_bytes)}
    expected = contract['selected']
    require(actual['rgba_sha256'] == expected['rgba_sha256'], 'Selected RGBA mismatch')
    require(actual['hda_sha256'] == expected['hda_sha256'], 'Selected HDA mismatch')
    edge_reports = []
    buffers = {113: result}
    buffers.update({int(tile): (work / f'{tile}.rgba').read_bytes() for tile in frozen_inputs})
    for pair in contract['edge_pairs']:
        a, b = buffers[pair['a']], buffers[pair['b']]
        if pair['direction'] == 'right':
            points = [((y * width + width - 1) * 4, y * width * 4) for y in range(height)]
        else:
            require(pair['direction'] == 'down', 'Invalid pair direction')
            points = [(((height - 1) * width + x) * 4, x * 4) for x in range(width)]
        deltas = [abs(a[ia + c] - b[ib + c]) for ia, ib in points for c in range(3)]
        maximum, mean = max(deltas), sum(deltas) / len(deltas)
        require(maximum == pair['max_RGB'] and abs(mean - pair['mean_abs_RGB']) < 1e-12,
                f"Border audit differs: {pair['direction']} {pair['a']} {pair['b']}")
        edge_reports.append(dict(pair, recomputed_max_RGB=maximum, recomputed_mean_abs_RGB=mean))
    report = {
        'status': 'passed',
        'approval_scope': 'Deterministic offline source rebuild; runtime approval remains pending',
        'decoded_rgba_and_hda_exact': True,
        'png_file_exact': actual['png_sha256'] == expected['png_sha256'],
        'committed_png_sha256': expected['png_sha256'],
        'actual': actual,
        'alpha_exact': True,
        'zero_alpha_hd_pixels': alpha.count(0),
        'zero_alpha_logical_pixels': logical_holes,
        'outer_perimeter_opaque': True,
        'frozen_neighbor_inputs_unchanged': True,
        'baseline_checkout_or_asset_pack_required': False,
        'frozen_full_raster_inputs_required': False,
        'native_registration_stdout': registration.stdout.strip(),
        'edge_pairs': edge_reports,
        'environment': {
            'python': platform.python_version(), 'pillow': pillow_version,
            'zlib_runtime': zlib.ZLIB_RUNTIME_VERSION,
            'compiler': subprocess.check_output([args.compiler, '--version'], text=True).splitlines()[0],
        },
    }
    (output / 'rebuild-verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'png_file_exact': report['png_file_exact'], **actual}))


if __name__ == '__main__':
    main()
