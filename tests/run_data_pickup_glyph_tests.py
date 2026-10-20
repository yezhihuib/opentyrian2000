#!/usr/bin/env python3
"""Bounded vector tests; optional actual blitter/compositor with private game data.
No game data is copied to the repository or generated deliverables.
SDL_CFLAGS/SDL_LIBS may select existing headers/runtime when pkg-config is absent.
"""
from pathlib import Path
import argparse, hashlib, json, os, re, resource, shlex, shutil, subprocess, tempfile
ROOT=Path(__file__).resolve().parents[1]
def extract(source,name):
    m=re.search(r'^[A-Za-z_][^\n;{}]*\b'+name+r'\([^;{}]*\)\s*\{',source,re.M)
    assert m,name
    i=source.index('{',m.start())+1;depth=1
    while depth:
        depth+=(source[i]=='{')-(source[i]=='}');i+=1
    return source[m.start():i]+'\n'
def limits():
    resource.setrlimit(resource.RLIMIT_AS,(512*1024*1024,)*2)
    resource.setrlimit(resource.RLIMIT_FSIZE,(32*1024*1024,)*2)
    resource.setrlimit(resource.RLIMIT_CPU,(60,)*2)
def run(cmd,**kw):
    subprocess.run(cmd,check=True,timeout=90,**kw)
def main(default_effect="data"):
    limits()
    effect=default_effect
    module="fixed_pickup_flash" if effect=="flash145" else "data_pickup_glyph"
    p=argparse.ArgumentParser();p.add_argument('--data-dir',type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
    if a.output:
        a.output.mkdir(exist_ok=False,parents=True);out=a.output.resolve()
    else:
        out=Path(tempfile.mkdtemp(prefix=effect+'-fixed-test-'))
    if shutil.disk_usage(out).free<4*1024**3:raise RuntimeError('Keep at least 4 GiB free before testing')
    cc=shlex.split(os.environ.get('CC','cc'));base=['-std=c99','-O1','-Wall','-Wextra','-Werror','-pedantic','-I'+str(ROOT/'src')]
    try:
        for san in ['', '-fsanitize=undefined']:
            exe=out/('unit-ubsan' if san else 'unit')
            run(cc+base+([san,'-fno-sanitize-recover=all'] if san else [])+[str(ROOT/('tests/'+module+'_test.c')),str(ROOT/('src/'+module+'.c')),'-lm','-o',str(exe)])
            run([str(exe)],preexec_fn=limits)
        receipt={'unit':'passed plain + UBSan','adapter':'not run (supply --data-dir)','runtime_gameplay':'not run; fixture is not a gameplay capture'}
        if a.data_dir:
            s=(ROOT/'src/render_mirror.c').read_text();sprite=(ROOT/'src/sprite.c').read_text();entity=(ROOT/'src/entity_draw.c').read_text()
            compositor=['complete_turret_group','restore_classic_rect','palette_rgb','blend_rgba','cloud_shadow_rgba','cloud_asset','darken_rgba','enemy_filter_rgba','explosion_asset_blend_rgba','green_background_snapshot','green_background_peak','green_head_composite','draw_asset_filtered','draw_asset']
            groups={'types':s[s.index('typedef struct {\n bool initialized,valid;'):s.index('/* Roads220')],
                    'compositor':'\n'.join(extract(s,n) for n in compositor),
                    'adapter':'\n'.join(extract(s,n) for n in ['decode_tile','cash25_surface_ready','render_mirror_data_value_begin','data_value_source_matches','data_value_draw','render_mirror_fixed_pickup_flash_begin','fixed_pickup_flash_source_matches','fixed_pickup_flash_surface_ready','fixed_pickup_flash_draw','explosion_asset_slot']),
                    'pixel':extract(s,'render_mirror_pixel'),
                    'blend':'\n'.join(extract(s,n) for n in ['explosion_blend_rgba','effect_ramp_monotone_to','effect_ramp_monotone','recognized_value_effect','recognized_contact_effect','have_supported_talon'])+(ROOT/'src/asteroid1_effect_blend_mirror.inc').read_text()+extract(s,'render_mirror_sprite2_blend_pixel'),
                    'blit':'\n'.join(extract(sprite,n) for n in ['blit_sprite2','blit_sprite2_blend']),
                    'wrapper':extract(entity,'draw_entity_sprite2'),
                    'end':extract(s,'render_mirror_entity_end')}
            prefix=extract(s,'render_mirror_entity').split(' if(fixed_value&&bank.data')[0]
            groups['entity']=prefix+' (void)fixed_value;(void)fixed_value75;(void)fixed_value50;(void)fixed_value100;(void)fixed_value250;return false;\n}\n'
            for name,body in groups.items():(out/('actual_'+name+'.inc')).write_text(body)
            # Integration assertions cover untouched lifecycle and the only production hook.
            t=(ROOT/'src/tyrian2.c').read_text();assert t.count('render_mirror_data_value_begin(')==1
            assert t.count('render_mirror_fixed_pickup_flash_begin(')==1
            assert 'explosions[j].deltaY, explosions[j].sprite, explosions[j].ttl' in t
            begin=extract(s,'render_mirror_begin');assert 'data_fixed_value=false;' in begin
            assert 'fixed_pickup_flash=false;' in begin
            assert 'data_fixed_value=false;' in groups['end']
            assert 'fixed_pickup_flash=false;' in groups['end']
            assert 'ASSET_DATA_VALUE' not in extract(s,'get_asset')
            assert 'ASSET_FIXED_PICKUP_FLASH' not in extract(s,'get_asset')
            cflags=shlex.split(os.environ.get('SDL_CFLAGS','')) or shlex.split(subprocess.check_output(['pkg-config','--cflags','sdl2'],text=True))
            libs=shlex.split(os.environ.get('SDL_LIBS','')) or shlex.split(subprocess.check_output(['pkg-config','--libs','sdl2'],text=True))
            for san in ['', '-fsanitize=undefined']:
                exe=out/('adapter-ubsan' if san else 'adapter')
                run(cc+base+(['-DFIXED_FLASH145'] if effect=='flash145' else [])+['-Wno-misleading-indentation','-I'+str(out)]+cflags+([san,'-fno-sanitize-recover=all'] if san else [])+[str(ROOT/'tests/data_pickup_glyph_adapter.c'),str(ROOT/'src/data_pickup_glyph.c'),str(ROOT/'src/fixed_pickup_flash.c')]+libs+['-lm','-o',str(exe)])
                run([str(exe),str(a.data_dir.resolve()),str(out), 'ubsan' if san else 'plain'],preexec_fn=limits,env={**os.environ,'SDL_VIDEODRIVER':'dummy','SDL_AUDIODRIVER':'dummy'})
            receipt.update(adapter='passed actual extracted production functions, plain + UBSan',extracted_sha256={k:hashlib.sha256(v.encode()).hexdigest() for k,v in groups.items()})
        (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
    finally:
        if not a.output:shutil.rmtree(out)
if __name__=='__main__':main()
