#!/usr/bin/env python3
"""Portable, bounded ASan/UBSan binding oracle; never runs the game."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import struct
import subprocess

HERE = Path(__file__).resolve().parent
FUNCTIONS = ['decode_tile', 'read_asset', 'explosion_asset_slot', 'get_asset',
             'talon_frame', 'render_mirror_entity', 'render_mirror_entity_end']
PATTERNS = [r'typedef struct \{\s*bool initialized,valid;.*?\} Asset;',
            r'typedef struct \{\s*bool valid;\s*const Uint8 \*bank_data;.*?\} TalonBank;',
            r'static Asset assets\[\d+\];', r'static Asset talon_frames\[13\];']
RENDERER_CHANGES = [
    ('static Asset assets[336];', 'static Asset assets[333];'),
    (' /* Regular Missile Launcher: three static physical player heads. */\n'
     ' if(bank.data==spriteSheet8.data&&layout==ENTITY_TILE&&index>=31&&index<=33) {slot=333+(int)index-31;role=8;}\n', ''),
    (' /* Regular Missile Launcher shadows retain their original indexed silhouettes and origin. */\n'
     ' if(bank.data==spriteSheet8.data&&layout==ENTITY_TILE&&index>=31&&index<=33&&style==MIRROR_SHADOW)return false;\n', ''),
]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def extract(source, name):
    match = re.search(r'^[A-Za-z_][^\n;{}]*\b' + name + r'\([^;{}]*\)\s*\{', source, re.M)
    assert match, name
    start = source.index('{', match.start())
    end, depth = start + 1, 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[match.start():end] + '\n'


def check_scope(candidate, baseline):
    """Only compare the renderer and entity wrapper; not the entire source tree."""
    sources = {}
    for label, root in [('candidate', candidate), ('baseline', baseline)]:
        sources[label] = {name: (root / 'src' / name).read_bytes()
                          for name in ('render_mirror.c', 'entity_draw.c')}
    restored = sources['candidate']['render_mirror.c'].decode('utf-8')
    for old, new in RENDERER_CHANGES:
        assert restored.count(old) == 1, 'Expected exactly one renderer patch fragment: ' + old
        restored = restored.replace(old, new)
    assert restored.encode('utf-8') == sources['baseline']['render_mirror.c'], 'Unexpected renderer changes'
    assert sources['candidate']['entity_draw.c'] == sources['baseline']['entity_draw.c'], 'Entity wrapper changed'
    scope = dict(exact_renderer_changes=3, reverse_candidate_renderer_to_baseline='byte-identical',
                 entity_draw='byte-identical',
                 inspected_files=['src/render_mirror.c', 'src/entity_draw.c'],
                 scope_note='This check does not assert that other source files are unchanged.')
    return sources, scope


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('candidate', 'baseline', 'pack', 'out'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    candidate, baseline, pack, out = (getattr(args, name).resolve()
                                      for name in ('candidate', 'baseline', 'pack', 'out'))
    if out.exists():
        parser.error('--out must be a new, non-existing directory')
    if any(out == root or root in out.parents for root in (HERE, candidate, baseline, pack)):
        parser.error('--out must be outside the test package and all supplied source/asset directories')
    if not all(root.is_dir() for root in (candidate, baseline, pack)):
        parser.error('--candidate, --baseline, and --pack must be existing directories')
    sources, scope = check_scope(candidate, baseline)
    out.mkdir(parents=True, exist_ok=False)
    work = out / 'runtime'
    work.mkdir()
    headers = []
    for missing in range(31, 34):
        directory = work / f'missing-{missing}'
        directory.mkdir()
        for sprite_id in range(31, 34):
            if sprite_id != missing:
                name = f'bullet-{sprite_id}-8.hda'
                (directory / name).symlink_to(pack / name)
    density4 = work / 'density4'
    density4.mkdir()
    for sprite_id in range(31, 34):
        raw = (pack / f'bullet-{sprite_id}-8.hda').read_bytes()
        header = (80000 + sprite_id, 8, 12, 14, 0, 0)
        assert raw[:4] == b'HDR1' and struct.unpack('<6I', raw[4:28]) == header
        assert len(raw) == 28 + 96 * 112 * 4
        headers.append(dict(id=sprite_id, sha256=sha(raw), header=list(header), bytes=len(raw)))
        directory = work / f'invalid-{sprite_id}'
        directory.mkdir()
        # Deliberately invalid synthetic header; no authored artwork is copied.
        (directory / f'bullet-{sprite_id}-8.hda').write_bytes(
            b'HDR1' + struct.pack('<6I', 80000 + sprite_id, 8, 12, 14, 1, 0))
        (density4 / f'bullet-{sprite_id}-4.hda').write_bytes(
            b'HDR1' + struct.pack('<6I', 80000 + sprite_id, 4, 12, 14, 0, 0)
            + bytes([17, 33, 65, 128]) * (48 * 56))
    reports = []
    for label, is_baseline in [('candidate', False), ('baseline', True)]:
        source = sources[label]['render_mirror.c'].decode('utf-8')
        entity = sources[label]['entity_draw.c'].decode('utf-8')
        directory = out / label
        directory.mkdir()
        definitions = []
        for pattern in PATTERNS:
            match = re.search(pattern, source, re.S)
            assert match, pattern
            definitions.append(match.group())
        extracted = {name: extract(source, name) for name in FUNCTIONS}
        extracted['draw_entity_sprite2'] = extract(entity, 'draw_entity_sprite2')
        (directory / 'production-types.inc').write_text('\n'.join(definitions) + '\n')
        (directory / 'production-helpers.inc').write_text('\n'.join(extracted[name] for name in FUNCTIONS))
        (directory / 'production-entity.inc').write_text(extracted['draw_entity_sprite2'])
        command = [os.environ.get('CC', 'cc'), '-std=c99', '-O1', '-g', '-Wall', '-Wextra',
                   '-Werror', '-Wno-misleading-indentation', '-fsanitize=address,undefined',
                   '-fno-omit-frame-pointer', '-fno-pie', '-no-pie',
                   '-DBASELINE=' + str(int(is_baseline)), '-I' + str(directory),
                   str(HERE / 'test-regular-missile-binding.c'), '-o', str(directory / 'test')]
        compiled = subprocess.run(command, cwd=out, capture_output=True, text=True)
        (directory / 'compile.log').write_text(compiled.stdout + compiled.stderr)
        compiled.check_returncode()
        environment = dict(os.environ, ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',
                           UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
        run = subprocess.run([str(directory / 'test'), str(pack), str(work)], cwd=out,
                             env=environment, capture_output=True, text=True, timeout=90)
        (directory / 'run.log').write_text(run.stdout + run.stderr)
        print(label + ': ' + run.stdout.strip(), flush=True)
        if run.returncode:
            print(run.stderr, flush=True)
        run.check_returncode()
        result = json.loads(run.stdout)
        result.update(label=label, renderer_sha256=sha(source.encode('utf-8')),
                      entity_sha256=sha(entity.encode('utf-8')), compile_command=command,
                      exit_code=run.returncode, stderr=run.stderr,
                      production_function_sha256={name: sha(text.encode('utf-8'))
                                                  for name, text in extracted.items()})
        reports.append(result)
    report = dict(status='passed', sanitizers=['address', 'undefined'], leak_detection=False,
                  source_scope_verification=scope, authored_target_headers=headers, runs=reports,
                  extracted_functions=FUNCTIONS + ['draw_entity_sprite2'],
                  limitations=[
                      'Leak detection is disabled for ptrace-based executors; ASan/UBSan remain enabled.',
                      'draw_asset and original blits are recorders; no pixel, visibility or aesthetic claim.',
                      'No game process, capture, source edit, full asset copy, or publication.',
                      'Only renderer and entity-wrapper scope is checked, not all source files.',
                      'Generated helpers, binaries, synthetic fixtures, and receipts are confined to --out.'])
    (out / 'result.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Report: ' + str(out / 'result.json'))


if __name__ == '__main__':
    main()
