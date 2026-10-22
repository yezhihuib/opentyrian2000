# Counted adapter: imports register a case; the original oracle executes in isolation.
def main():
    from accepted_later_changes import validate_current_sources
    validate_current_sources()
    #!/usr/bin/env python3
    """Remove this pilot's observer-only integrations and prove byte-for-byte baseline.
    The frozen projection contains source hashes, never original game asset bytes.
    """
    from pathlib import Path
    import hashlib,json
    ROOT=Path(__file__).resolve().parents[1]
    pins=json.loads((ROOT/'tests/storm_source_projection.json').read_text())
    changes={
    'src/render_mirror.c':[
     ('#include "gameplay_hud_font.h"\n#include "gameplay_hud_storm.h"','#include "gameplay_hud_font.h"'),
     ('/* Independent heading observer and texture-only compositor. */\n#include "gameplay_hud_storm_mirror.inc"\n\n',''),
     (' hud_storm_reset();\n font_reset();',' font_reset();'),
     ('hud_fixed_text_shutdown();font_shutdown();hud_storm_shutdown();','hud_fixed_text_shutdown();font_shutdown();'),
     ('\n storm_start(decoded_pic3);',''),
     ('\n hud_storm_suspend();',''),
     ('\n storm_resume();',''),
     ('\n storm_pixel(surface,address);',''),
     ('\n storm_rect(s,rect);',''),
     ('\n hud_storm_fade_palette(rgb_palette);',''),
     ('\n storm_present(pixels,pitch);','')],
    'src/render_mirror.h':[
     ('\n#define render_mirror_hud_storm_begin(...) ((void)0)\n#define render_mirror_hud_storm_end(...) ((void)0)\n#define render_mirror_hud_storm_source_reset(...) ((void)0)',''),
     ('\nvoid render_mirror_hud_storm_begin(SDL_Surface *,unsigned slot,unsigned option,unsigned icon,int x,int y);\nvoid render_mirror_hud_storm_end(SDL_Surface *,unsigned slot);\nvoid render_mirror_hud_storm_source_reset(unsigned table);','')],
    'src/varz.c':[
     ('\t\trender_mirror_hud_storm_begin(VGAScreenSeg, i, this_player->items.sidekick[i], this_option->icongr, 284, y);\n',''),
     ('\n\t\trender_mirror_hud_storm_end(VGAScreenSeg, i);','')],
    'src/sprite.c':[('\n\trender_mirror_hud_storm_source_reset(table);','')]
    }
    for name,digest in pins['files'].items():
        from accepted_later_changes import project_source
        data=project_source("storm",name,(ROOT/name).read_bytes())
        if name in changes:
            s=data.decode()
            for before,after in changes[name]:
                assert s.count(before)==1,(name,before)
                s=s.replace(before,after)
            data=s.encode()
        assert hashlib.sha256(data).hexdigest()==digest,name
    m=(ROOT/'src/render_mirror.c').read_text()
    pixel=m[m.index('void render_mirror_pixel('):m.index('void render_mirror_rect(')]
    assert pixel.index(' storm_pixel(surface,address);')<pixel.index(' if((!active&&!shared_hud_frame&&')
    assert m.index(' storm_rect(s,rect);')<m.index(' if((!active&&!shared_hud_frame&&',m.index('void render_mirror_rect('))
    assert m.index(' storm_present(pixels,pitch);')<m.index(' SDL_UnlockTexture(texture);')
    assert m.index(' storm_present(pixels,pitch);')>m.index('SDL_LockTexture(texture,NULL,&pixels,&pitch)')
    print(f'STORM source-inverse: all {len(pins["files"])} original source files restored byte-for-byte; original INDEX8 writers/order unchanged')

def load_tests(loader,tests,pattern):
    from historical_oracle_support import suite
    return suite(__file__)

if __name__=='__main__':
    main()
