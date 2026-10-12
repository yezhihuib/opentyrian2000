#!/usr/bin/env python3
"""Test bounded HUL1 loading with temporary synthetic indices and artwork only."""
import argparse
import os
from pathlib import Path
import re
import shlex
import subprocess
import tempfile


PRODUCTION_GUARDS = {
    'PIC3': 0x14c1441f3d5dc0e2, 'PALETTE': 0x5e80e83992be2927,
    'TOP': 0x328ef0a75cce2260, 'MODE1': 0x55f78c15a1ce495a,
    'MODE2': 0xf7a97c521d045d18, 'OPTION18': 0xd36b9afd4df898cf,
    'OPTION19': 0xac3fca9154ec0310,
}


def fnv(data):
    value = 0xcbf29ce484222325
    for byte in data:
        value = ((value ^ byte) * 0x100000001b3) & ((1 << 64) - 1)
    return value


def synthetic_guards():
    source = bytes((i * 29 + i // 320 * 13) % 256 for i in range(64000))
    sprites = [bytes((i * 17 + state * 61) % 253 for i in range(80)) for state in range(2)]
    top = b''.join(source[y * 320 + 269:y * 320 + 276] for y in range(4, 7))
    modes = [b''.join(sprites[state][y * 10:y * 10 + 10] +
                      source[(y + 44) * 320 + 295:(y + 44) * 320 + 302] +
                      sprites[1 - state][y * 10:y * 10 + 10] for y in range(8))
             for state in range(2)]
    palette = bytes(c for i in range(256) for c in (i, 255 - i, i ^ 0x5a))
    return dict(zip(PRODUCTION_GUARDS, map(fnv, [source, palette, top, *modes, *sprites])))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sanitize', action='store_true', help='Enable ASan and UBSan')
    parser.add_argument('--leak-check', action='store_true', help='Enable LeakSanitizer where supported')
    parser.add_argument('--cc', default=os.environ.get('CC', 'cc'))
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    root = here.parents[2]
    loader = root / 'src/gameplay_hud_indicators.c'
    text = loader.read_text()
    for guard, expected in PRODUCTION_GUARDS.items():
        pattern = rf'#define HUD_INDICATORS_{guard}_FNV UINT64_C\(0x([0-9a-f]+)\)'
        match = re.search(pattern, text)
        assert match and int(match[1], 16) == expected, ('production guard drift', guard)
    with tempfile.TemporaryDirectory(prefix='hud-indicators-test-') as temporary:
        build = Path(temporary)
        probes = ['malloc', 'free', 'open', 'read', 'close', 'fstat']
        probe = build / 'allocation_probe.h'
        probe.write_text('#include <stddef.h>\n'
                         'void *hud_indicators_test_malloc(size_t size);\n'
                         'void hud_indicators_test_free(void *pointer);\n')
        flags = ['-std=c99', '-O1' if args.sanitize else '-O2', '-g', '-Wall',
                 '-Wextra', '-Werror', '-Wpedantic', '-I', str(root / 'src')]
        if args.sanitize:
            flags += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie']
        cc = shlex.split(args.cc)
        hooks = ['-include', str(probe)] + [f'-D{name}=hud_indicators_test_{name}' for name in probes]
        guards = [f'-DHUD_INDICATORS_{key}_FNV=UINT64_C(0x{value:016x})'
                  for key, value in synthetic_guards().items()]
        environment = os.environ.copy()
        if args.sanitize:
            environment['ASAN_OPTIONS'] = f'detect_leaks={int(args.leak_check)}:halt_on_error=1'
            environment['UBSAN_OPTIONS'] = 'halt_on_error=1:print_stacktrace=1'
        for production in (False, True):
            defines = [] if production else guards
            subprocess.run(cc + flags + hooks + defines + ['-c', str(loader), '-o', str(build / 'loader.o')],
                           check=True)
            executable = build / ('test_production_guards' if production else 'test_indicators')
            subprocess.run(cc + flags + [str(here / 'test_indicators.c'), str(build / 'loader.o'),
                           '-o', str(executable)], check=True)
            pack = build / ('production-pack' if production else 'synthetic-pack')
            pack.mkdir()
            subprocess.run([str(executable), str(pack)] + (['production'] if production else []),
                           check=True, env=environment, timeout=90)


if __name__ == '__main__':
    main()
