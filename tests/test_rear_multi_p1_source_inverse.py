#!/usr/bin/env python3
"""Undo only the finite rear-head observer hooks; prove original source equality.
Contains original-source SHA256 and code edits, never original game payloads.
"""
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parents[1]
pins=json.loads((root/'tests/rear_multi_p1_source_projection.json').read_text())
for name,digest in pins['files'].items():
    data=(root/name).read_bytes()
    for before,after in reversed(pins['changes'].get(name,[])):
        assert data.count(after.encode())==1,(name,after)
        data=data.replace(after.encode(),before.encode())
    assert hashlib.sha256(data).hexdigest()==digest,name
m=(root/'src/render_mirror.c').read_text()
generic=m[m.index('static Asset *get_asset('):m.index('void render_mirror_player_pose(')]
assert 'ASSET_REAR_MULTI_P1' not in generic
assert 'rear_p1_' not in m[m.index('static bool normal15_indices_match'):m.index('void render_mirror_finish(')]
s=(root/'src/shots.c').read_text()
assert s.count('render_mirror_rear_p1_emit(')==1
assert s.count('draw_player_shot_sprite2(')==1
wrapper=(root/'src/entity_draw.c').read_text().split('void draw_player_shot_sprite2(',1)[1].split('/* The indexed original',1)[0]
assert wrapper.count('blit_sprite2(')==1
assert wrapper.count('game_probe_draw(')==1
assert wrapper.index('game_probe_draw(')<wrapper.index('blit_sprite2(')<wrapper.index('render_mirror_entity_end();')
print(f'Rear P1 inverse: all {len(pins["files"])} baseline source files byte-exact after removing listed observer hooks; generic role and Hard filter unchanged')
