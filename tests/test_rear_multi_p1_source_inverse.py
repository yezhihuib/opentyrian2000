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
assert s.count('render_mirror_rear_p1_create_begin(')==1
assert s.count('render_mirror_rear_p1_create_end(')==4
create=s.split('JE_integer player_shot_create(',1)[1]
assert create.count('return ')==4
assert 'render_mirror_rear_p1_emit(rear_p1_call, multi_i, shot_id,' in create
assert create.index('render_mirror_rear_p1_create_begin(')<create.index('// Bounds check')
assert create.index('shotRepeat[bay_i] = weapon->shotrepeat;')<create.index('render_mirror_rear_p1_emit(')<create.index('game_probe_shot_emit(')
assert s.count('draw_player_shot_sprite2(')==1
wrapper=(root/'src/entity_draw.c').read_text().split('void draw_player_shot_sprite2(',1)[1].split('/* The dedicated rear shadow',1)[0]
assert wrapper.count('blit_sprite2(')==1
assert wrapper.count('game_probe_draw(')==1
assert wrapper.index('game_probe_draw(')<wrapper.index('blit_sprite2(')<wrapper.index('render_mirror_entity_end();')
print(f'Rear P1/P2 inverse: all {len(pins["files"])} baseline source files byte-exact after removing listed observer hooks; generic role and Hard filter unchanged')

shadow=(root/'src/entity_draw.c').read_text().split('void draw_player_shot_shadow_sprite2(',1)[1].split('/* The indexed original',1)[0]
assert shadow.count('blit_sprite2_darken(')==1 and shadow.count('game_probe_draw(')==1
assert shadow.index('game_probe_draw(')<shadow.index('blit_sprite2_darken(')<shadow.index('render_mirror_entity_end();')
assert 'draw_entity_sprite2(target,x,y,bank,index,ENTITY_SHADOW,ENTITY_TILE);' in shadow
assert s.count('draw_player_shot_shadow_sprite2(')==1
pilot=(root/'src/rear_multi_p11_shadow.inc').read_text()
assert 'rear_p1_state.birth[slot].record!=264' in pilot
assert 'lvlFileNum!=9' in pilot and 'game_probe_density!=8' in pilot
assert 'rear_p1_asset(v->index)' in pilot and 'shadowYDist' in pilot
print('Record264 shadow observer inverse and single original darken wrapper: PASS')
