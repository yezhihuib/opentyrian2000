#!/usr/bin/env python3
"""Read-only selected V2/V5/PIC3 resource checks; no screenshots or resource copies."""
import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent / 'gameplay-hud'))
from test_renderer import fnv


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('legacy', 'corner', 'data'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    old = (args.legacy / 'gameplay-hud-v1.hda').read_bytes()
    new = (args.corner / 'gameplay-hud-v1.hda').read_bytes()
    assert hashlib.sha256(old).hexdigest() == '4ff6cd95d4c3ec5b7e4825e38a5242fc96c1cd305987a873bea4a55fa5a04482'
    assert hashlib.sha256(new).hexdigest() == '98cd6cfefa02a9ae79b75a65e02dd2566d3dec1492552f20b042b3c61c19cd17'
    assert len(old) == len(new) == 4160064
    oldmask, mask = old[64:64064], new[64:64064]
    region = {y * 320 + x for y in range(184, 200) for x in range(248, 269)}
    assert mask == bytes(255 if i in region else oldmask[i] for i in range(64000))
    assert mask.count(255) == 6853 and sum(bool(oldmask[i]) for i in region) == 150
    assert fnv(mask) == 0xb0f84ef16e11c6a2 and fnv(new[64064:]) == 0xa23eeb19e1a9e125
    for y in range(800):
        for x in range(1280):
            logical = y // 4 * 320 + x // 4
            start = 64064 + 4 * (y * 1280 + x)
            if oldmask[logical] or logical not in region:
                assert new[start:start + 4] == old[start:start + 4]
    # Same PCX run encoding as JE_loadPic; decode in RAM only, never export data.
    raw = (args.data / 'tyrian.pic').read_bytes()
    start, end = struct.unpack_from('<2I', raw, 2 + 2 * 4)
    assert 0 <= start < end <= len(raw)
    encoded = raw[start:end]
    source = bytearray()
    cursor = 0
    while len(source) < 64000:
        value = encoded[cursor]
        cursor += 1
        if value & 0xc0 == 0xc0:
            count = value & 0x3f
            assert count
            source.extend([encoded[cursor]] * count)
            cursor += 1
        else:
            source.append(value)
        assert len(source) <= 64000
    source_region = bytes(source[i] for i in sorted(region))
    assert fnv(source) == 0x14c1441f3d5dc0e2
    assert fnv(source_region) == 0xca5548b4cdd8767a and source_region.count(0) == 46
    assert hashlib.sha256(source_region).hexdigest() == '0c25d658f16177ade5667a76d652375f4a28f42a59a518d542d1946c94b3df50'
    samples = 0
    with tempfile.TemporaryDirectory(prefix='hud-corner-resource-') as temporary:
        library = Path(temporary) / 'hud.so'
        subprocess.run([os.environ.get('CC', 'cc'), '-std=c99', '-Wall', '-Wextra', '-Werror',
                        '-shared', '-fPIC', '-O2', str(ROOT / 'src/gameplay_hud.c'), '-o', str(library)], check=True)
        api = ctypes.CDLL(str(library))
        api.gameplay_hud_load.argtypes = [ctypes.c_char_p]
        api.gameplay_hud_load.restype = ctypes.c_bool
        for name in ('gameplay_hud_capture', 'gameplay_hud_prepare_corner'):
            call = getattr(api, name)
            call.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.c_int]
            call.restype = ctypes.c_bool
        api.gameplay_hud_sample.argtypes = [ctypes.c_int] * 5 + [ctypes.c_uint8]
        api.gameplay_hud_sample.restype = ctypes.c_void_p
        current = (ctypes.c_uint8 * 64000).from_buffer_copy(source)
        assert api.gameplay_hud_load(os.fsencode(args.legacy.resolve()))
        assert api.gameplay_hud_capture(current, 320)
        assert not api.gameplay_hud_prepare_corner(current, 320)
        api.gameplay_hud_shutdown()
        assert api.gameplay_hud_load(os.fsencode(args.corner.resolve()))
        assert api.gameplay_hud_capture(current, 320)
        assert not api.gameplay_hud_sample(248, 184, 0, 0, 4, source[184 * 320 + 248])
        assert api.gameplay_hud_prepare_corner(current, 320)
        for density in (4, 8):
            for i in range(64000):
                x, y = i % 320, i // 320
                pointer = api.gameplay_hud_sample(x, y, 0, 0, density, source[i])
                assert bool(pointer) == bool(mask[i])
                # Every corner subpixel, plus every other owned cell's origin.
                offsets = [(sx, sy) for sy in range(density) for sx in range(density)] if i in region else [(0, 0)]
                if not pointer:
                    continue
                for sx, sy in offsets:
                    pointer = api.gameplay_hud_sample(x, y, sx, sy, density, source[i])
                    start = 64064 + 4 * ((y * 4 + sy // (density // 4)) * 1280 + x * 4 + sx // (density // 4))
                    assert ctypes.string_at(pointer, 4) == new[start:start + 4]
                    samples += 1
        current[190 * 320 + 248] ^= 1
        assert not api.gameplay_hud_prepare_corner(current, 320)
        for i in region:
            assert not api.gameplay_hud_sample(i % 320, i // 320, 0, 0, 4, current[i])
        api.gameplay_hud_shutdown()
    print(json.dumps({
        'status': 'selected_V2_read_only_source_and_resource_checks_passed',
        'visual_runtime_gate': 'pending',
        'resource_sha256': hashlib.sha256(new).hexdigest(),
        'full_pic3_fnv1a64': f'{fnv(source):016x}',
        'corner_region_fnv1a64': f'{fnv(source_region):016x}',
        'mask_fnv1a64': f'{fnv(mask):016x}',
        'source_zero_cells_in_corner': 46,
        'whole_mask_cells': 6853,
        'unchanged_old_owned_cells': 6667,
        'unchanged_old_corner_cells': 150,
        'outside_corner_changes': 0,
        'exact_rgba_samples': samples,
        'original_V5_load_and_capture_passed': True,
        'atomic_corner_mismatch_passed': True,
        'screenshots': 0,
        'resource_copies': 0,
    }, indent=2))


if __name__ == '__main__':
    main()
