#!/usr/bin/env python3
"""Exact source-preservation checks for the title-only typography observer."""
from pathlib import Path
import hashlib,re,struct,subprocess
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
BASE='e6fd18a8d53c31f90d15c0ac1bce9d0e927336ac'
def original(path):return subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT)
def main():
    assert struct.calcsize('<4s15I8Q')==128
    paths=('src/font.c','src/fonthand.c','src/font.h','src/fonthand.h','src/sprite.c','src/render_mirror.c','src/gameplay_hud_font.c','src/gameplay_hud_font.h','src/gameplay_hud_font_mirror.inc','src/keyboard.c','src/joystick.c','src/nortsong.c','src/mouse.c','src/mainint.c','src/menus.c','src/opentyr.c','src/palette.c','src/video.c','src/picload.c','src/params.c','src/startup_logos.c','src/startup_logos.h')
    for path in paths:
        actual=(ROOT/path).read_bytes()
        if path=='src/render_mirror.c' and actual!=original(path):
            # Exact independently tested0082cd5 small-family append only. A
            # changed renderer cannot hide behind this historical title guard.
            assert hashlib.sha256(actual).hexdigest()=='7a39ffd4959c307c23707ae63c41030cd92ef757375b95f680445ff4f3e85420'
            text=actual.decode().replace('static Asset assets[422];','static Asset assets[416];')
            for first,last in [('/* Approved type3 six-member small bank1 family,','bool render_mirror_enemy_tile('),(' /* Type3/type16 use one small tile at the original top-left, not a composite.',' /* Existing ground201..209 and rotor210..217 remain unchanged. */')]:
                assert text.count(first)==text.count(last)==1
                start=text.index(first);end=text.index(last,start);text=text[:start]+text[end:]
            actual=text.encode()
        assert actual==original(path),path
    text=(ROOT/'src/tyrian2.c').read_text();base=original('src/tyrian2.c').decode()
    stripped=re.sub(r'^[ \t]*title_layers_menu_text_(?:begin|done)\([^;\n]*\);\n','',text,flags=re.M)
    assert stripped==base
    assert text.count('title_layers_menu_text_begin(')==6 and text.count('title_layers_menu_text_done(')==6
    for match in re.finditer(r'title_layers_menu_text_begin\(([^;]+)\);\s*draw_font_hv\(([^;]+)\);\s*title_layers_menu_text_done\(\);',text):assert match[1]==match[2]
    assert len(re.findall(r'title_layers_menu_text_begin\(([^;]+)\);\s*draw_font_hv\(([^;]+)\);\s*title_layers_menu_text_done\(\);',text))==6
    source=(ROOT/'src/title_menu_font.inc').read_text();layer=(ROOT/'src/title_layers.c').read_text()
    for forbidden in ('SDL_PushEvent','SDL_RenderReadPixels','SDL_Delay','mt_rand','getenv(','setDelay','draw_font_','blit_sprite','VGAScreen->pixels ='):assert forbidden not in source
    assert 'if(!tm_render(destination))tl_plane(&state.menu);' in layer
    assert layer.index('if(!tm_render(destination))tl_plane(&state.menu);')<layer.index('tl_plane(&state.cursor);')
    assert 'menu_font.count=menu_font.base_count' in source
    assert 'else if(table==SMALL_FONT_SHAPES)tm_end()' in layer
    assert '#include "title_menu_font.inc"' in layer
    assert 'title_menu_font.inc' in (ROOT/'visualc/opentyrian.vcxproj').read_text()
    print('Title-only six exact draw brackets preserve all original tyrian2.c bytes; shared fonts, gameplay HUF1, inputs, timing and submenu files byte-exact')
    print('TMF1 finite128-byte protocol, replacement-before-cursor, base-prefix restore and table1 invalidation source gates passed')
if __name__=='__main__':main()
