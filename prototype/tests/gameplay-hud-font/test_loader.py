#!/usr/bin/env python3
"""Bounded HUF1 loader/source/sampler and intercepted I/O accounting tests."""
from pathlib import Path
import argparse
import os
import re
import subprocess
import tempfile

from fixtures import (FILENAME, GUARDS, HEADER, ROOT, compiler_flags,
                      fixture, rechecksum)

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sanitize', action='store_true')
    args = parser.parse_args()
    source = ROOT / 'src/gameplay_hud_font.c'
    text = source.read_text()
    for name, value in GUARDS.items():
        match = re.search(r'#define HUD_FONT_' + name + r'_FNV UINT64_C\(0x([0-9a-f]+)\)', text)
        assert match and int(match[1], 16) == value, ('production guard drift', name)
    common = [os.environ.get('CC', 'cc'), '-std=c99', '-O1', '-g', '-Wall',
              '-Wextra', '-Werror', '-I' + str(ROOT / 'src')]
    if args.sanitize:
        common += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-no-pie']
    env = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',
               UBSAN_OPTIONS='halt_on_error=1')

    def run(command):
        subprocess.run([str(value) for value in command], check=True, env=env, timeout=45)

    def compile_test(directory, guards):
        output = directory / 'test'
        run(common + compiler_flags(guards) + [HERE / 'test_loader.c', source, '-o', output])
        return output

    with tempfile.TemporaryDirectory(prefix='huf-loader-') as tmp:
        directory = Path(tmp)
        guards, raw = fixture(directory)
        bad = [b'', raw[:111], raw[:-1], raw + b'\0', raw * 2]
        for offset in range(HEADER.size):
            changed = bytearray(raw)
            changed[offset] ^= 1
            bad.append(changed)
        changed = bytearray(raw)
        changed[HEADER.size + (4 * 512 + 8)] ^= 1
        bad.append(changed)  # Valid in-box position, stale payload checksum.
        # Exercise padding in every cell, then the otherwise plausible used
        # rectangle of the final unused slot. Recompute checksums deliberately.
        for glyph_id in range(128):
            changed = bytearray(raw)
            offset = (glyph_id // 16) * 40 * 512 + (glyph_id % 16) * 32
            changed[HEADER.size + offset] = 1
            bad.append(rechecksum(changed))
        for x, y in ((4, 4), (27, 35), (31, 39)):
            changed = bytearray(raw)
            changed[HEADER.size + (7 * 40 + y) * 512 + 15 * 32 + x] = 1
            bad.append(rechecksum(changed))
        # Nonzero bottom/right maximum-extent padding even with a good checksum.
        for x, y in ((28, 4), (4, 36)):
            changed = bytearray(raw)
            changed[HEADER.size + y * 512 + x] = 1
            bad.append(rechecksum(changed))
        for i, data in enumerate(bad):
            folder = directory / ('bad-%d' % i)
            folder.mkdir()
            (folder / 'case').touch()
            (folder / FILENAME).write_bytes(data)
        for kind in ('missing', 'directory', 'fifo'):
            folder = directory / ('bad-%d' % len(bad))
            folder.mkdir()
            (folder / 'case').touch()
            filename = folder / FILENAME
            if kind == 'directory':
                filename.mkdir()
            elif kind == 'fifo':
                os.mkfifo(filename)
            bad.append(None)
        binary = compile_test(directory, guards)
        run([binary, directory])

        # Padding between verified actual bounds and the fixed 6x8 maximum
        # is deferred to capture because dimensions are intentionally not in HUF1.
        folder = directory / 'actual-padding'
        _, padding_raw = fixture(folder)
        changed = bytearray(padding_raw)
        glyph_id = 70  # Three logical pixels wide, while maximum is six.
        x = (glyph_id % 16) * 32 + 4 + 3 * 4
        y = (glyph_id // 16) * 40 + 4
        changed[HEADER.size + y * 512 + x] = 1
        (folder / FILENAME).write_bytes(rechecksum(changed))
        run([binary, folder, 'capture-reject'])

        for production in (False, True):
            definitions = [] if production else compiler_flags(guards)
            probes = ['-D' + name + '=font_test_' + name
                      for name in ('malloc', 'free', 'open', 'read', 'fstat', 'close')]
            run(common + definitions + probes + ['-c', source, '-o', directory / 'io.o'])
            run(common + ['-DHUD_FONT_TEST_IO', HERE / 'test_loader.c', directory / 'io.o',
                          '-o', directory / 'io'])
            run([directory / 'io', directory] + (['production'] if production else []))

        invalid_glyphs = [
            (0, 8, b'\x07'), (7, 8, b'\x07'), (6, 0, b'\x07'), (6, 9, b'\x07'),
            (6, 8, b''), (6, 8, b'\x07' * 105), (6, 8, b'\xff'),
            (6, 8, bytes([255, 7])), (6, 8, bytes([254]) * 9),
            (6, 8, b'\x07' * 49), (6, 8, bytes([7, 255, 6])),
        ]
        for number, glyph in enumerate(invalid_glyphs):
            folder = directory / ('invalid-rle-%d' % number)
            altered_guards, _ = fixture(folder, {0: glyph})
            altered_binary = compile_test(folder, altered_guards)
            run([altered_binary, folder, 'source-reject'])
        # Legal row skips, count skips (including zero), single transparent
        # pixels, and implicit transparent tails are all independently exercised.
        for number, data in enumerate((bytes([254]) * 8, bytes([255, 6]) * 8,
                                       bytes([255, 0, 253, 255, 5]) * 8, b'\x07')):
            folder = directory / ('valid-rle-%d' % number)
            altered_guards, _ = fixture(folder, {0: (6, 8, data)})
            altered_binary = compile_test(folder, altered_guards)
            run([altered_binary, folder])
        print('HUF1 PASS: %d resource rejections, 11 injected I/O failures, '
              '11 malformed and 4 valid independently pinned RLE fixtures.' % len(bad))


if __name__ == '__main__':
    main()
