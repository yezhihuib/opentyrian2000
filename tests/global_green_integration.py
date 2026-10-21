#!/usr/bin/env python3
"""Exact native-statement projection; intentionally not a renderer correctness proof."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BASE = 'd5b08f5d9cde1dea43819daaa8a52bc8f211e20b'
EXCLUDED = {'src/render_mirror.c', 'src/render_mirror.h', 'src/global_asset_registry.h'}
NEW_SOURCE = {'src/global_green_identity.inc', 'src/global_green_mirror.inc'}
OWNER_FILES = {'src/global_' + family + '_mirror.inc' for family in (
    'cash25', 'hitflare', 'pulse', 'rotor', 'shield', 'small_explosion',
    'smoke', 'talon', 'vulcan')}

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)

def remove_exact(data, line, count=1):
    assert data.count(line) == count, (line, count, data.count(line))
    return data.replace(line, b'')

paths = git('ls-tree', '-r', '--name-only', BASE, 'src').decode().splitlines()
checked = {}
for name in paths:
    if name in EXCLUDED:
        continue
    prior = git('show', BASE + ':' + name)
    now = (ROOT / name).read_bytes()
    if name == 'src/shots.c':
        # Preserve CRLF and every native byte; only these nine observer lines go.
        for line, count in [
            ('\t\t\trender_mirror_green_trail_begin(shot_id);', 1),
            ('\t\t\trender_mirror_green_trail_end();', 1),
            ('\tuint64_t green_call = render_mirror_green_create_begin(portNum, bay_i, wpNum, playerNum, PX, PY, mouseX, mouseY);', 1),
            ('\t\trender_mirror_green_create_end(green_call);', 4),
            ('\t\trender_mirror_green_shot_allocated(shot_id);', 1),
            ('\t\trender_mirror_green_shot_initialized(green_call, shot_id, portNum, bay_i, wpNum, playerNum, shotMultiPos[bay_i]);', 1),
        ]:
            # Match complete lines, not a suffix of a more-indented line.
            needle = line.encode() + b'\r\n'
            lines = now.splitlines(keepends=True)
            assert lines.count(needle) == count, (name, line)
            now = b''.join(part for part in lines if part != needle)
    if name == 'src/varz.c':
        for line in [
            '\t\t\t\trender_mirror_green_smoke_allocated(i,type,x,y,deltaY,fixedPosition,followPlayer);\n',
            '\t\t\t\trender_mirror_green_smoke_initialized(i, type);\n',
        ]:
            now = remove_exact(now, line.encode())
    if name in OWNER_FILES:
        now = remove_exact(now, b'  if(global_green_owner)global_green_owner[n]=global_green_foreign[n]=0;\n')
    if name == 'src/entity_draw.c':
        # Restore only the three dispatch insertions. The entire result, including
        # every original indexed blit and fallback, must equal the original file.
        for style in ('ENTITY_NORMAL', 'ENTITY_SHADOW'):
            inserted = (' int global=render_mirror_global_green_head(target,x,y,bank,index,' + style + ',slot,raw);\n'
                        ' if(global<0)global=render_mirror_global_vulcan(target,x,y,bank,index,' + style + ',slot,raw);\n').encode()
            original = (' int global=render_mirror_global_vulcan(target,x,y,bank,index,' + style + ',slot,raw);\n').encode()
            assert now.count(inserted) == 1
            now = now.replace(inserted, original)
        inserted = (b' int admitted=render_mirror_global_green_smoke(target,x,y,bank,index,style,slot);\n'
                    b' if(admitted<0)admitted=render_mirror_global_cash25_value(target,x,y,bank,index,style,slot);\n')
        original = b' int admitted=render_mirror_global_cash25_value(target,x,y,bank,index,style,slot);\n'
        assert now.count(inserted) == 1
        now = now.replace(inserted, original)
    assert now == prior, name
    checked[name] = hashlib.sha256(prior).hexdigest()
current = {str(p.relative_to(ROOT)) for p in (ROOT / 'src').rglob('*') if p.is_file() and p.suffix in ('.c', '.h', '.inc')}
assert current - set(paths) == NEW_SOURCE, sorted(current - set(paths))
art = {}
for name in git('ls-tree', '-r', '--name-only', BASE, 'assets').decode().splitlines():
    if name == 'assets/hd/global-assets-v1/registry.json':
        continue
    prior = git('show', BASE + ':' + name)
    assert (ROOT / name).read_bytes() == prior, name
    art[name] = hashlib.sha256(prior).hexdigest()
print(json.dumps({'status': 'PASS', 'base': BASE,
                  'protected_source_files': len(checked), 'protected_asset_files': len(art),
                  'excluded_renderer_files': sorted(EXCLUDED),
                  'new_observer_files': sorted(NEW_SOURCE),
                  'source_sha256': checked, 'asset_sha256': art}, indent=2))
