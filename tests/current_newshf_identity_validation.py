#!/usr/bin/env python3
"""Finite current entry-prelude adapter for the frozen NEWSHF identity harness.

The identity-only harness is not whole-game, HD composition or session acceptance.
The extra native prefix matrix tests only entry rejection and hook ordering.
"""
import hashlib
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DRIVER_SHA = '8b86af41a83951ba6dbf39ac5f6f8a4741bc17bdfeee41020eb3c5295b89cf0c'
HARNESS_SHA = '6499e2dbc2c5cf0d5b6fe81a4723b1a5fffa1388b0d0db14146b72569c993216'
BEGIN_SHA = '5125c23e4cedeb3cf79ea9f26cd71fe5de511c4012a1c55210a57d17574a6491'
PREFIX = '''void render_mirror_begin(void)
{
#if defined(ENEMY_REUSE_HD_PROTOTYPE) && ENEMY_REUSE_HD_PROTOTYPE
 if(enemy_reuse_observe_requested()&&!enemy_reuse_observe_active()) {render_mirror_hud_reset();return;}
#endif
 render_mirror_newshf_validation_frame();
'''
NEXT = ' global_newshf_tick_begin();'

def validate_begin(begin):
    assert hashlib.sha256(begin.encode()).hexdigest() == BEGIN_SHA, 'Current begin changed: review finite lifecycle contract'
    assert begin.startswith(PREFIX + NEXT), 'Unexpected frame-hook prelude/order'
    assert begin.count('render_mirror_newshf_validation_frame();') == 1, 'Frame hook must occur exactly once'
    return PREFIX

def transformed(root, raw):
    assert hashlib.sha256(raw).hexdigest() == DRIVER_SHA, 'Historical identity driver changed'
    assert hashlib.sha256((root/'tests/newshf_identity_validation.c').read_bytes()).hexdigest() == HARNESS_SHA, 'Historical identity harness changed'
    source = raw.decode()
    marker = "ROOT = Path(__file__).resolve().parents[1]"
    assert source.count(marker) == 1
    source = source.replace(marker, f'ROOT = Path({str(root)!r})')
    marker = "assert begin.split('{',1)[1].lstrip().startswith('render_mirror_newshf_validation_frame();')"
    assert source.count(marker) == 1
    return source.replace(marker, '_validate_current_begin(begin)')

def main():
    root = ROOT
    if '--source-root' in sys.argv:
        i = sys.argv.index('--source-root')
        root = Path(sys.argv[i+1]).resolve()
        del sys.argv[i:i+2]
    raw = (root/'tests/newshf_identity_validation.py').read_bytes()
    source = transformed(root, raw)
    sys.path.insert(0, str(root/'tests'))
    exec(compile(source, str(root/'tests/newshf_identity_validation.py'), 'exec'),
         {'__name__':'__main__', '__file__':str(root/'tests/newshf_identity_validation.py'),
          '_validate_current_begin':validate_begin})

if __name__ == '__main__':
    main()
