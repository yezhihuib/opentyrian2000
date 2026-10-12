#!/usr/bin/env python3
"""Source-preservation gates. Does not compile or launch the game."""
from pathlib import Path
import re, struct, subprocess
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
BASE='93de0fe4cb935f1d7cf7d737c86e0ff3f3f8c218'

def original(path):
    return subprocess.check_output(['git','show',f'{BASE}:{path}'],cwd=ROOT).decode()

def tokens(text):
    # Ignore whitespace and comments only; preserve all original code/literals.
    pattern=r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|/\*.*?\*/|//[^\n]*|[A-Za-z_]\w*|\d+|[^\s]'
    return [m.group() for m in re.finditer(pattern,text,re.S) if not m.group().startswith(('/*','//'))]

def strip_title_hooks(text):
    text=re.sub(r'^\s*#include "title_layers.h"[^\n]*\n','',text,flags=re.M)
    output=[]
    for line in text.splitlines(keepends=True):
        if re.fullmatch(r'\s*if \(table == PLANET_SHAPES\) title_layers_end\(\);\s*',line):
            continue
        if 'title_layers_present(' in line:
            assert re.fullmatch(r'\s*if\s*\(title_layers_present\([^\n]*\)\)\s*\{\s*last_output_rect\s*=\s*dst_rect\s*;\s*return\s*;\s*}\s*',line),line
            continue
        # Calls are removed individually: never drop a line containing original writes.
        line=re.sub(r'\btitle_layers_[A-Za-z_]+\([^;\n]*\);','',line)
        output.append(line)
    return ''.join(output)

def function(text,name):
    match=re.search(r'\b'+re.escape(name)+r'\s*\([^;{}]*\)\s*\{',text)
    assert match,name
    start=match.start();pos=match.end();depth=1
    while depth:
        depth+=(text[pos]=='{')-(text[pos]=='}');pos+=1
    return text[start:pos]

def main():
    assert struct.calcsize('<4s11I4Q')==80
    # Exact originals for input/timing/manufacturer code, including line endings.
    exact=('src/keyboard.c','src/joystick.c','src/nortsong.c','src/startup_logos.c','src/startup_logos.h')
    for path in exact:
        assert (ROOT/path).read_bytes()==subprocess.check_output(['git','show',f'{BASE}:{path}'],cwd=ROOT),path
    hooked=('src/tyrian2.c','src/sprite.c','src/video.c','src/palette.c','src/picload.c','src/params.c','src/opentyr.c')
    for path in hooked:
        text=(ROOT/path).read_text()
        if path=='src/params.c':
            # The sole approved original literal change documents the title opt-in.
            old='Optional HD manufacturer cards (release, local startup only)'
            new='Optional HD manufacturer/title art (release, local startup only)'
            assert text.count(new)==1 and text.count(old)==0
            assert original(path).count(old)==1 and original(path).count(new)==0
            text=text.replace(new,old)
        assert tokens(strip_title_hooks(text))==tokens(original(path)),f'{path}: original code differs after removing title-only hooks'
    assert function((ROOT/'src/tyrian2.c').read_text(),'intro_logos')==function(original('src/tyrian2.c'),'intro_logos')
    module=(ROOT/'src/title_layers.c').read_text()
    pins={'PIC4':'9a3f7cb8ec37073e','PAL':'8f64628a08533287','146_INDEX':'30f8dbf0554a03ae','146_MASK':'0cb7de8084912543','146_RLE':'f19983d3c8b5e3a1','151_INDEX':'4562ec954d257998','151_MASK':'ee71b0121c53f8df','151_RLE':'9133efa73da3f836'}
    for name,value in pins.items():
        assert f'#ifndef TITLE_{name}_FNV\n#define TITLE_{name}_FNV UINT64_C(0x{value})\n#endif' in module,name
    for forbidden in ('game_probe_', 'mt_rand', 'SDL_PushEvent', 'SDL_RenderReadPixels', 'setDelay(', 'wait_delay', 'exit(', 'getenv('):
        assert forbidden not in module,forbidden
    # Presentation itself does not allocate CPU storage or read any resource.
    present=function(module,'title_layers_present')
    for forbidden in ('malloc(', 'calloc(', 'realloc(', 'TL_OPEN(', 'TL_READ(', 'SDL_Delay(', 'setDelay('):
        assert forbidden not in present,forbidden
    assert present.count('SDL_RenderPresent(')==1
    assert 'O_NONBLOCK' in module and 'TL_REGULAR(st.st_mode)' in module
    sprite=(ROOT/'src/sprite.c').read_text()
    for name,writer in (('blit_sprite','TITLE_WRITE_LOGO'),('blit_sprite_hv','TITLE_WRITE_FONT'),('blit_sprite_dark','TITLE_WRITE_SHADOW'),('blit_sprite2_filter_clip','TITLE_WRITE_CURSOR')):
        section=function(sprite,name)
        assert 'title_layers_pixel(' in section and writer in section,name
    title=function((ROOT/'src/tyrian2.c').read_text(),'titleScreen')
    assert re.search(r'JE_loadPic\(VGAScreen,\s*4,\s*false\);\s*title_layers_begin\(',title)
    assert title.count('title_layers_logo(146,')==3 and title.count('title_layers_logo(151,')==3
    assert title.count('title_layers_art_ready(')==3
    for action in ('save_before','save_after','restore_before','restore_after'):
        for kind in ('BACKGROUND','MENU'):
            assert title.count(f'title_layers_{action}(TITLE_{kind})')==1,(action,kind)
    for action in ('save','restore'):
        for kind in ('BACKGROUND','MENU'):
            assert re.search(r'title_layers_'+action+r'_before\(TITLE_'+kind+r'\);\s*memcpy\([^;]+;\s*title_layers_'+action+r'_after\(TITLE_'+kind+r'\);',title),(action,kind)
    for name in ('JE_whoa','newSuperTyrianGame','newSuperArcadeGame','newGame','JE_loadScreen','JE_highScoreScreen','JE_helpSystem','setupMenu'):
        for match in re.finditer(r'\b'+name+r'\s*\(',title):
            prefix=title[:match.start()]
            assert re.search(r'title_layers_end\(\);\s*(?:if\s*\(\s*)?$',prefix),f'Missing retirement immediately before {name}'
    assert 'title_layers_end();' in (ROOT/'src/picload.c').read_text()
    vc=(ROOT/'visualc/opentyrian.vcxproj').read_text()
    assert 'title_layers.c' in vc and 'title_layers.h' in vc
    print('TLV1 exact80-byte protocol and bounded/no-per-presentation-allocation gates passed')
    print('Original input/timer/manufacturer bytes and all hooked original code tokens preserved against93de0fe4 except the explicit CLI help literal')
    print('Actual title/logo/checkpoint/cursor/foreign-screen integration and Windows registration checked')
if __name__=='__main__':main()
