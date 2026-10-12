#!/usr/bin/env python3
"""Run bounded HUC1 loader tests using only temporary synthetic data."""
import argparse
import os
from pathlib import Path
import shlex
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sanitize', action='store_true', help='Enable ASan and UBSan')
    parser.add_argument('--leak-check', action='store_true', help='Enable LeakSanitizer where supported')
    parser.add_argument('--cc', default=os.environ.get('CC', 'cc'))
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    root = here.parents[2]
    with tempfile.TemporaryDirectory(prefix='hud-components-test-') as temporary:
        build = Path(temporary)
        flags = ['-std=c99', '-O1' if args.sanitize else '-O2', '-g', '-Wall',
                 '-Wextra', '-Werror', '-Wpedantic', '-I', str(root / 'src'), '-I', str(here)]
        if args.sanitize:
            flags += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-fno-pie', '-no-pie']
        cc = shlex.split(args.cc)
        probes = ['malloc', 'free', 'open', 'read', 'close', 'fstat']
        subprocess.run(cc + flags + ['-include', str(here / 'allocation_probe.h')] +
                       [f'-D{name}=hud_components_test_{name}' for name in probes] +
                       ['-c', str(root / 'src/gameplay_hud_components.c'), '-o', str(build / 'loader.o')],
                       check=True)
        subprocess.run(cc + flags + [str(here / 'test_components.c'), str(build / 'loader.o'),
                       '-o', str(build / 'test_components')], check=True)
        pack = build / 'synthetic-pack'
        pack.mkdir()
        environment = os.environ.copy()
        if args.sanitize:
            environment['ASAN_OPTIONS'] = f'detect_leaks={int(args.leak_check)}:halt_on_error=1'
            environment['UBSAN_OPTIONS'] = 'halt_on_error=1:print_stacktrace=1'
        subprocess.run([str(build / 'test_components'), str(pack)], check=True, env=environment,
                       timeout=90)


if __name__ == '__main__':
    main()
