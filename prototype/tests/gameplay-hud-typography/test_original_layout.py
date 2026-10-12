#!/usr/bin/env python3
"""Source-extracted original text layout versus a synthetic scalar oracle.

This is protocol-design evidence, not a renderer or an artwork test. It reads
only source files: no original sprite, bitmap, palette, or game data is loaded.
The C recorder observes blit commands, including origins outside the screen;
it intentionally does not implement raster clipping or reflow.
"""

import argparse
import os
from pathlib import Path
import re
import shlex
import subprocess
import tempfile


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def lexical_source(source):
    """Mask comments and quoted literals without changing source positions."""
    return re.sub(r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'',
                  lambda match: ' ' * len(match.group()), source, flags=re.S)


def extract_function(source, name):
    lexical = lexical_source(source)
    match = re.search(r'^(?:static\s+)?(?:inline\s+)?[\w *]+\b' + re.escape(name) +
                      r'\([^;{}]*\)\s*\{', lexical, re.M)
    assert match, 'Missing source function: ' + name
    end = lexical.index('{', match.start()) + 1
    depth = 1
    while depth and end < len(lexical):
        depth += (lexical[end] == '{') - (lexical[end] == '}')
        end += 1
    assert depth == 0, 'Unbalanced source function: ' + name
    return source[match.start():end].strip()


def extracted_source():
    source = (ROOT / 'src/fonthand.c').read_text()
    table = re.search(r'const\s+int\s+font_ascii\s*\[\s*256\s*\]\s*=\s*\{.*?\};',
                      source, re.S)
    assert table, 'Missing source font_ascii table'
    names = ('JE_outText', 'JE_textWidth', 'JE_textShade', 'JE_dString')
    functions = '\n\n'.join(extract_function(source, name) for name in names)

    # Bind constants to the actual headers rather than duplicating their values
    # in the test harness. The oracle also checks the expected table/shade IDs.
    constants = []
    for filename, defines in (
            ('sprite.h', ('FONT_SHAPES', 'SMALL_FONT_SHAPES', 'TINY_FONT')),
            ('fonthand.h', ('PART_SHADE', 'FULL_SHADE', 'DARKEN', 'TRICK', 'NO_SHADE'))):
        header = (ROOT / 'src' / filename).read_text()
        for name in defines:
            definition = re.search(r'^#define\s+' + name + r'\s+\d+\s*$', header, re.M)
            assert definition, 'Missing integer source constant: ' + name
            constants.append(definition.group())

    # Execute the original scalar pixel expression without importing the sprite
    # decoder or its pointer/clipping behavior. Its hue overflow is intentional.
    blit = extract_function((ROOT / 'src/sprite.c').read_text(), 'blit_sprite_hv_unsafe')
    shift = re.findall(r'\bhue\s*<<=\s*4\s*;', blit)
    expression = re.findall(r'\*pixels\s*=\s*hue\s*\|\s*\(\(\*data\s*&\s*0x0f\)\s*\+\s*value\)\s*;', blit)
    assert len(shift) == len(expression) == 1, 'Review changed unsafe hue/value expression'
    return '\n'.join(constants), table.group() + '\n\n' + functions, shift[0] + '\n' + expression[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sanitize', action='store_true', help='Run with ASan and UBSan')
    args = parser.parse_args()
    constants, layout, pixel = extracted_source()
    with tempfile.TemporaryDirectory(prefix='original-text-layout-') as directory:
        directory = Path(directory)
        (directory / 'source_constants.inc').write_text(constants)
        (directory / 'source_layout.inc').write_text(layout)
        (directory / 'source_pixel.inc').write_text(pixel)
        command = shlex.split(os.environ.get('CC', 'cc')) + [
            '-std=c99', '-O1', '-g', '-Wall', '-Wextra', '-Werror',
            '-I' + str(directory), str(HERE / 'test_original_layout.c'),
            '-o', str(directory / 'test')]
        if args.sanitize:
            command += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-no-pie']
        subprocess.run(command, check=True)
        environment = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',
                           UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
        subprocess.run([str(directory / 'test')], check=True, env=environment)
    print('PASS source extraction: font_ascii, 4 original layout functions, '
          '8 constants, and original unsafe pixel expression; ' +
          ('ASan/UBSan' if args.sanitize else 'normal') + '; no game assets')


if __name__ == '__main__':
    main()
