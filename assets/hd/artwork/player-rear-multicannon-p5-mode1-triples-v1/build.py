#!/usr/bin/env python3
"""Rebuild frozen accepted triples and HDR1 resources, using only generated art.

Python 3 standard library only. Both output directories must be fresh and
separate, outside the source and package directories. No original game input.
"""
from pathlib import Path
import argparse
import contextlib
import hashlib
import io
import json
import struct
import tempfile

ROOT = Path(__file__).resolve().parent
SOURCE_FAMILY = 'assets/hd/artwork/player-rear-multicannon-p1-six-v1/output'
CORE_SHA256 = '0c70902e5327892d8f4c00bc6cd9b2f3df844df339caef5554941d04210e964e'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def fnv(data):
    value = 14695981039346656037
    for byte in data:
        value = ((value ^ byte) * 1099511628211) & ((1 << 64) - 1)
    return f'0x{value:016x}'


def build(source, output, hda_output):
    # lexists-equivalent check includes dangling symlinks. Resolve parent aliases
    # before overlap checks; never overwrite any pre-existing destination.
    require(all(not p.exists() and not p.is_symlink() for p in [output, hda_output]),
            'Both output directories must not exist')
    source_abs, out_abs, hda_abs = source.resolve(), output.resolve(), hda_output.resolve()
    require(out_abs != hda_abs and out_abs not in hda_abs.parents and hda_abs not in out_abs.parents,
            'Output directories must be separate')
    for destination in [out_abs, hda_abs]:
        for protected in [source_abs, ROOT.resolve()]:
            require(destination != protected and protected not in destination.parents
                    and destination not in protected.parents,
                    'Output directories must be outside source and package directories')
    pins = json.loads((ROOT / 'inputs.json').read_text())
    require([(r['accepted_source_id'], r['source_id'], r['density'], r['key'])
             for r in pins['resources']] == [(1, 3, 4, 1310003), (1, 3, 8, 1310003),
                                            (39, 41, 4, 1310041), (39, 41, 8, 1310041)],
            'Only reviewed 3/41 density4/8 triples are supported')
    core_bytes = (ROOT / 'build_components.py').read_bytes()
    frozen_bytes = (ROOT / 'frozen-inputs.json').read_bytes()
    require(sha(core_bytes) == CORE_SHA256 == pins['frozen_builder_sha256'], 'Frozen builder pin mismatch')
    require(sha(frozen_bytes) == pins['frozen_inputs_sha256'], 'Frozen input specification pin mismatch')
    frozen = json.loads(frozen_bytes)
    require(pins['components'] == frozen['components'], 'Component transforms mismatch')
    require(len(pins['accepted_inputs']) == 4, 'Accepted input count mismatch')
    source_files = {}
    for row, frozen_row in zip(pins['accepted_inputs'], frozen['inputs']):
        accepted, density = row['source_id'], row['density']
        require((accepted, density) == (frozen_row['source_id'], frozen_row['density']), 'Accepted input identity mismatch')
        stem = f'rear-multi-{accepted}-{density}'
        for extension in ['png', 'rgba']:
            name = f'{stem}.{extension}'
            require(row[f'{extension}_repo_path'] == f'{SOURCE_FAMILY}/{name}', 'Accepted source path mismatch')
            require(frozen_row[extension] == f'accepted/{name}', 'Frozen source path mismatch')
            data = (source / name).read_bytes()
            require(sha(data) == row[extension + '_sha256'] == frozen_row[extension + '_sha256'],
                    f'Accepted {extension.upper()} pin mismatch')
            source_files[name] = data
        raw = source_files[stem + '.rgba']
        require(len(raw) == 12 * 14 * density * density * 4, 'Accepted RGBA size mismatch')
        require(all(raw[o + 3] or not any(raw[o:o + 4]) for o in range(0, len(raw), 4)),
                'Hidden zero-alpha RGB found')
    # Keep the reviewed core byte-exact. Its historical preview manifest is also
    # reproduced byte-exact; publication/runtime state lives in binding.json.
    # exec avoids importing a sibling module and creating cache files in artwork.
    namespace = {'__name__': 'frozen_component_builder', '__file__': str(ROOT / 'build_components.py')}
    exec(compile(core_bytes, str(ROOT / 'build_components.py'), 'exec'), namespace)
    with tempfile.TemporaryDirectory(prefix='rear-triple-build-') as temporary:
        staging = Path(temporary)
        (staging / 'accepted').mkdir()
        for name, data in source_files.items():
            (staging / 'accepted' / name).write_bytes(data)
        (staging / 'inputs.json').write_bytes(frozen_bytes)
        namespace['ROOT'] = staging
        with contextlib.redirect_stdout(io.StringIO()):
            namespace['run'](staging / 'output')
        art_files = {p.name: p.read_bytes() for p in (staging / 'output').iterdir()}
    require(set(art_files) == set(pins['frozen_outputs_sha256']), 'Unexpected output files')
    for name, data in art_files.items():
        require(sha(data) == pins['frozen_outputs_sha256'][name], 'Frozen output pin mismatch')
    hda_files = {}
    for row in pins['resources']:
        target, density = row['source_id'], row['density']
        stem = f'rear-multi-{target}-{density}-exact-clipped-union'
        raw, png = art_files[stem + '.rgba'], art_files[stem + '.png']
        hda = struct.pack('<4s6I', b'HDR1', row['key'], density, 12, 14, 0, 0) + raw
        for kind, data in [('png', png), ('rgba', raw), ('hda', hda)]:
            require(sha(data) == row[kind + '_sha256'], f'Approved {kind} pin mismatch')
        require(fnv(raw) == row['rgba_fnv1a64'], 'Approved FNV pin mismatch')
        hda_files[f'rear-multicannon-p1-bank8-{target}-{density}.hda'] = hda
    # Validate every input/output pin before creating either requested directory.
    output.mkdir(parents=True)
    hda_output.mkdir(parents=True)
    for name, data in art_files.items():
        (output / name).write_bytes(data)
    for name, data in hda_files.items():
        (hda_output / name).write_bytes(data)
    print('PASS: four fixed-canvas reviewed triple PNG/RGBA/HDR1 resources; exact accepted tail clipping retained.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT.parent / 'player-rear-multicannon-p1-six-v1/output')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--hda-output', type=Path, required=True)
    args = parser.parse_args()
    build(args.source, args.output, args.hda_output)
