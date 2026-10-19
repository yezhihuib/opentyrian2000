#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Validate the complete optional Data translation and export a bounded CJK atlas.

Build-time dependencies: Pillow and fontTools. Runtime requires only SDL2.
Original game files are never written. Translation input is kept as UTF-8 JSON.
DZF1 is a 64-byte little-endian header, sorted glyph records, then alpha8 pixels.
"""
from pathlib import Path
from data_translation_validation import validate_paragraphs
import argparse
import hashlib
import json
import math
import struct
import sys

import PIL
from PIL import Image, ImageDraw, ImageFont, features
from fontTools.ttLib import TTFont

FORMAT = 'DZF1'
HEADER = struct.Struct('<4s11IQQ')
RECORD = struct.Struct('<IHH')
FONT_SHA256 = 'b76b0433203017ca80401b2ee0dd69350349871c4b19d504c34dbdd80541690a'
FONT_DEFAULT = Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
FONT_INDEX = 2
FONT_PX, CELL_W, CELL_H, ATLAS_W, BASELINE, PEN_X = 36, 40, 48, 2048, 36, 2
COLUMNS = ATLAS_W // CELL_W
MAX_HEIGHT = 4096
MAX_GLYPHS = COLUMNS * (MAX_HEIGHT // CELL_H)
UI_TEXT = ('简体中文 英文 F6: Chinese / English Read % '
           'Scroll: Up/Down PgUp/PgDn Home/End English fallback '
           'F6：切换英文 / 简体中文')


def fnv1a64(data):
    value = 14695981039346656037
    for byte in data:
        value = ((value ^ byte) * 1099511628211) & 0xffffffffffffffff
    return value


def die(message):
    raise ValueError(message)


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def validate_catalog(source, paths, allow_partial=False):
    originals = {entry['id']: entry for entry in source['entries']}
    if len(originals) != len(source['entries']):
        die('Duplicate source IDs')
    translations = {}
    for path in paths:
        document = read_json(path)
        if document.get('language') != 'zh-CN':
            die(f'{path}: language must be zh-CN')
        for entry in document.get('entries', []):
            identity = entry.get('id')
            if identity not in originals:
                die(f'{path}: unknown source identity {identity!r}')
            if identity in translations:
                die(f'{path}: duplicate translation {identity}')
            original = originals[identity]
            for key in ('episode', 'cube_index', 'source_sha256'):
                if entry.get(key) != original[key]:
                    die(f'{identity}: source binding differs in {key}')
            for key in ('title', 'header'):
                if not isinstance(entry.get(key), str):
                    die(f'{identity}: {key} must be a string')
                if original[key].strip() and not entry[key].strip():
                    die(f'{identity}: nonempty source {key} has empty translation')
            paragraphs = entry.get('paragraphs')
            validate_paragraphs(original['paragraphs'], paragraphs, identity)
            text = entry['title'] + entry['header'] + ''.join(paragraphs)
            if any(ord(c) < 32 or ord(c) == 127 or 0xd800 <= ord(c) <= 0xdfff for c in text):
                die(f'{identity}: control/surrogate character in translation')
            # Each source field/paragraph is a standalone emphasis run.
            for field in [entry['title'], entry['header'], *paragraphs]:
                if field.count('~') % 2:
                    die(f'{identity}: unbalanced emphasis marker in a field/paragraph')
            # Bounds are generous for this catalog, but prevent accidental blobs.
            if len(entry['title'].encode()) > 2048 or len(entry['header'].encode()) > 1024:
                die(f'{identity}: oversized title/header')
            if sum(len(p.encode()) for p in paragraphs) > 65536:
                die(f'{identity}: oversized body')
            translations[identity] = {
                'id': identity, 'episode': original['episode'],
                'cube_index': original['cube_index'],
                'source_sha256': original['source_sha256'],
                'source_fnv1a64': original['source_fnv1a64'],
                'placeholder': original['placeholder'],
                'title': entry['title'], 'header': entry['header'],
                'paragraphs': paragraphs,
            }
    missing = set(originals) - set(translations)
    if missing and not allow_partial:
        die('Missing translations: ' + ', '.join(sorted(missing)))
    ordered = [translations[e['id']] for e in source['entries'] if e['id'] in translations]
    return {'schema': 'tyrian-data-zh-CN-v1', 'language': 'zh-CN',
            'source_files': [{k: v for k, v in info.items() if k != 'appendix'} for info in source['source_files']], 'entries': ordered}, sorted(missing)


def font_names(font):
    result = {}
    for name_id, key in [(0, 'copyright'), (1, 'family'), (2, 'style'),
                         (5, 'version'), (7, 'trademark'), (13, 'license'),
                         (14, 'license_url')]:
        values = []
        for entry in font['name'].names:
            if entry.nameID == name_id:
                value = entry.toUnicode()
                if value not in values:
                    values.append(value)
        result[key] = values
    return result


def alpha_font(font_path, codepoints):
    source_bytes = font_path.read_bytes()
    digest = hashlib.sha256(source_bytes).hexdigest()
    if digest != FONT_SHA256:
        die(f'Font SHA256 mismatch: {digest}')
    face = TTFont(str(font_path), fontNumber=FONT_INDEX, lazy=True)
    cmap, names = face.getBestCmap(), font_names(face)
    missing = [cp for cp in codepoints if cp not in cmap or cmap[cp] == '.notdef']
    face.close()
    if missing:
        die('Missing glyphs: ' + ', '.join(f'U+{cp:04X}' for cp in missing))
    font = ImageFont.truetype(str(font_path), FONT_PX, index=FONT_INDEX,
                             layout_engine=ImageFont.Layout.BASIC)
    rows = math.ceil(len(codepoints) / COLUMNS)
    height = rows * CELL_H
    if not codepoints or len(codepoints) > MAX_GLYPHS or height > MAX_HEIGHT:
        die(f'Atlas capacity exceeded: {len(codepoints)} > {MAX_GLYPHS}')
    atlas = Image.new('L', (ATLAS_W, height))
    draw = ImageDraw.Draw(atlas)
    records, advances, report = bytearray(), {}, []
    for index, cp in enumerate(codepoints):
        char = chr(cp)
        left, top, right, bottom = font.getbbox(char, anchor='ls')
        if PEN_X + left < 0 or PEN_X + right > CELL_W or BASELINE + top < 0 or BASELINE + bottom > CELL_H:
            die(f'U+{cp:04X}: glyph bbox {(left, top, right, bottom)} clips the {CELL_W}x{CELL_H} cell')
        advance = max(1, round(font.getlength(char)))
        if advance > CELL_W:
            die(f'U+{cp:04X}: advance {advance} exceeds cell')
        x, y = index % COLUMNS * CELL_W, index // COLUMNS * CELL_H
        draw.text((x + PEN_X, y + BASELINE), char, font=font, fill=255, anchor='ls')
        records += RECORD.pack(cp, advance, 0)
        advances[cp] = advance
        report.append({'codepoint': f'U+{cp:04X}', 'char': char,
                       'advance': advance, 'bbox': [left, top, right, bottom]})
    alpha = atlas.tobytes()
    payload = bytes(records) + alpha
    header = HEADER.pack(b'DZF1', 1, ATLAS_W, height, CELL_W, CELL_H,
                         len(codepoints), COLUMNS, BASELINE, FONT_PX,
                         RECORD.size, len(alpha), fnv1a64(payload), 0)
    assert len(header) == 64
    return header + payload, atlas, advances, report, names


def reference_reflow(text, advances, width):
    """Coverage-only CJK reference wrap. Runtime may improve punctuation breaks.

    Whitespace and ~ emphasis markers have no semantic glyph coverage. Latin
    runs that exceed the viewport are safely broken into Unicode codepoints.
    """
    lines, line, used = [], [], 0
    for char in text:
        if char == '~':
            continue
        if char == '\n':
            lines.append(''.join(line)); line, used = [], 0
            continue
        advance = advances[ord(char)]
        if line and used + advance > width:
            lines.append(''.join(line)); line, used = [], 0
        line.append(char); used += advance
    lines.append(''.join(line))
    before = ''.join(c for c in text if c != '~' and not c.isspace())
    after = ''.join(c for line in lines for c in line if not c.isspace())
    if before != after:
        die('Reference reflow omitted or reordered glyphs')
    if any(sum(advances[ord(c)] for c in line) > width for line in lines):
        die('Reference reflow exceeded width')
    return lines


def license_text(path, names):
    text = path.read_text(encoding='utf-8')
    start = text.index('License: SIL-1.1\n', text.index('Files: debian/*')) + len('License: SIL-1.1\n')
    end = text.index('\nLicense: GPL-3+', start)
    lines = []
    for line in text[start:end].splitlines():
        line = line[1:] if line.startswith(' ') else line
        lines.append('' if line == '.' else line)
    notices = '\n'.join(names['copyright'])
    return (notices + '\n\nAdditional distribution copyright notice: '\
            '2010-2012 Google Corporation (Debian fonts-noto-cjk copyright).\n\n' +
            '\n'.join(lines).strip() + '\n')


def export(args):
    source = read_json(args.source)
    merged, missing = validate_catalog(source, args.translations, args.allow_partial)
    texts = [UI_TEXT, ''.join(chr(cp) for cp in range(32, 127))]
    for entry in merged['entries']:
        texts += [entry['title'], entry['header'], *entry['paragraphs']]
    codepoints = sorted({ord(char) for text in texts for char in text if char != '~'} | set(range(32, 127)))
    blob, atlas, advances, glyphs, names = alpha_font(args.font, codepoints)
    layouts = []
    for entry in merged['entries']:
        body = '\n\n'.join(entry['paragraphs'])
        lines = reference_reflow(body, advances, args.body_width)
        titles = reference_reflow(entry['title'], advances, 472)
        layouts.append({'id': entry['id'], 'placeholder': entry['placeholder'],
                        'body_lines': len(lines), 'body_width_px': args.body_width,
                        'body_glyphs': sum(not c.isspace() and c != '~' for c in body),
                        'list_title_lines_at_472px': len(titles),
                        'body_layout_has_no_omissions': True,
                        'body_layout_max_width_px': max((sum(advances[ord(c)] for c in line) for line in lines), default=0)})
    args.out.mkdir(parents=True, exist_ok=True)
    name = 'data-text-zh-CN-v1'
    (args.out / f'{name}.dzf').write_bytes(blob)
    (args.out / f'{name}.json').write_text(json.dumps(merged, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (args.out / 'LICENSE-Data-Font-OFL.txt').write_text(license_text(args.license_source, names), encoding='utf-8')
    manifest = {
        'format': FORMAT, 'header_bytes': HEADER.size,
        'header_struct': '<4s11IQQ',
        'header_fields': ['magic', 'version', 'width', 'height', 'cell_width', 'cell_height', 'glyph_count', 'columns', 'baseline', 'font_px', 'record_bytes', 'alpha_bytes', 'payload_fnv1a64', 'reserved_zero'],
        'record_struct': '<IHH', 'record_fields': ['unicode_codepoint', 'advance_px', 'reserved_zero'],
        'glyph_order': 'strictly ascending Unicode codepoint',
        'glyph_cell_xy': ['ordinal % columns * cell_width', 'ordinal // columns * cell_height'],
        'glyph_pen_origin': [PEN_X, BASELINE],
        'runtime_note': 'Blit whole cells; alpha8 blending. No SDL_ttf/FreeType runtime dependency. ~ toggles emphasis, not a glyph.',
        'width': atlas.width, 'height': atlas.height, 'glyph_count': len(codepoints),
        'atlas_file': f'{name}.dzf', 'atlas_bytes': len(blob),
        'atlas_sha256': hashlib.sha256(blob).hexdigest(),
        'atlas_fnv1a64': f'{fnv1a64(blob):016x}',
        'payload_fnv1a64': f'{fnv1a64(blob[HEADER.size:]):016x}',
        'font_source': {'filename': args.font.name, 'ttc_index': FONT_INDEX,
                        'sha256': FONT_SHA256, 'upstream': 'https://github.com/notofonts/noto-cjk',
                        'license': 'SIL Open Font License 1.1', 'metadata': names},
        'rasterizer': {'pillow': PIL.__version__, 'freetype': features.version('freetype2'),
                       'layout_engine': 'Pillow BASIC', 'font_px': FONT_PX},
        'catalog': {'entries': len(merged['entries']), 'complete': not missing,
                    'missing': missing, 'source_entries': len(source['entries']),
                    'title_body_glyph_coverage': 'complete',
                    'translation_inputs': [{'filename': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()} for path in args.translations]},
        'longest_layout': max(layouts, key=lambda entry: entry['body_lines']) if layouts else None,
        'layouts': layouts, 'glyphs': glyphs,
    }
    (args.out / f'{name}-font-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    provenance = ('Optional Tyrian Data text font atlas\n\n'
                  f'Source: {args.font.name}, TTC face {FONT_INDEX}, Noto Sans CJK SC Regular\n'
                  f'Source SHA256: {FONT_SHA256}\n'
                  'Upstream: https://github.com/notofonts/noto-cjk\n'
                  f"Copyright: {'; '.join(names['copyright'])}\n"
                  'License: SIL Open Font License Version 1.1. See LICENSE-Data-Font-OFL.txt.\n'
                  'This atlas is a rasterized derivative for optional Data text only.\n'
                  'The source font is not required at runtime.\n'
                  f'Rasterizer: Pillow {PIL.__version__}, FreeType {features.version("freetype2")}, BASIC shaping\n'
                  f'Atlas: {len(codepoints)} glyphs, {atlas.width}x{atlas.height}, alpha8, cells40x48, baseline36\n'
                  f'Atlas SHA256: {manifest["atlas_sha256"]}\n'
                  f'Atlas FNV1a64: {manifest["atlas_fnv1a64"]}\n')
    (args.out / 'DATA-FONT-PROVENANCE.txt').write_text(provenance, encoding='utf-8')
    if args.preview:
        atlas.save(args.out / f'{name}-atlas-preview.png')
    print(json.dumps({key: manifest[key] for key in ('format', 'glyph_count', 'width', 'height', 'atlas_bytes', 'atlas_sha256', 'atlas_fnv1a64', 'catalog', 'longest_layout')}, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--translations', type=Path, nargs='+', required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--font', type=Path, default=FONT_DEFAULT)
    parser.add_argument('--license-source', type=Path, default=Path('/usr/share/doc/fonts-noto-cjk/copyright'))
    parser.add_argument('--allow-partial', action='store_true', help='Development smoke test only; complete release builds omit this')
    parser.add_argument('--preview', action='store_true')
    parser.add_argument('--body-width', type=int, default=584, help='Runtime body width at 4x output, default584')
    try:
        export(parser.parse_args())
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as error:
        print(f'Data font export failed: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
