#!/usr/bin/env python3
"""Bounded analytic + actual original-blitter/compositor fixture; no gameplay claim."""
from pathlib import Path
import argparse,hashlib,json,os,resource,shlex,shutil,subprocess,tempfile
from run_data_pickup_glyph_tests import extract,limits,run
ROOT=Path(__file__).resolve().parents[1]
def main():
    limits();p=argparse.ArgumentParser();p.add_argument('--data-dir',type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
    out=a.output.resolve() if a.output else Path(tempfile.mkdtemp(prefix='secret-orb-test-'))
    if a.output:out.mkdir(parents=True,exist_ok=False)
    if shutil.disk_usage(out).free<4*1024**3:raise RuntimeError('Keep at least 4 GiB free')
    cc=shlex.split(os.environ.get('CC','cc'));flags=['-std=c99','-O1','-Wall','-Wextra','-Werror','-pedantic','-I'+str(ROOT/'src')]
    receipt={'unit':'not run','adapter':'not run (supply --data-dir)','natural_runtime':'not run; synthetic fixture is not natural hidden-route gameplay'}
    try:
        for san in ['', '-fsanitize=undefined']:
            suffix='ubsan' if san else 'plain';exe=out/('unit-'+suffix)
            run(cc+flags+([san,'-fno-sanitize-recover=all'] if san else [])+[str(ROOT/'tests/secret_exit_orb_test.c'),str(ROOT/'src/secret_exit_orb.c'),'-lm','-o',str(exe)]);run([str(exe)],preexec_fn=limits)
        receipt['unit']='passed plain + UBSan'
        if a.data_dir:
            original=a.data_dir/'newshp.shp';assert hashlib.sha256(original.read_bytes()).hexdigest()=='4bd9a72339e30440c172e385f258c8895b516ff84026a9a6b5a65ada4cf0ab90'
            s=(ROOT/'src/render_mirror.c').read_text();spr=(ROOT/'src/sprite.c').read_text();t=(ROOT/'src/tyrian2.c').read_text()
            comps=['complete_turret_group','restore_classic_rect','palette_rgb','blend_rgba','cloud_shadow_rgba','cloud_asset','darken_rgba','enemy_filter_rgba','explosion_asset_blend_rgba','green_background_snapshot','green_background_peak','green_head_composite','draw_asset_filtered']
            groups={'types':s[s.index('typedef struct {\n bool initialized,valid;'):s.index('/* Roads220')],
                    'compositor':'\n'.join(extract(s,n) for n in comps),
                    'adapter':'\n'.join(extract(s,n) for n in ['decode_tile','cash25_surface_ready','fixed_pickup_flash_surface_ready','secret_exit_orb_source_matches','secret_exit_orb_pickup']),
                    'pixel':extract(s,'render_mirror_pixel'),'blit':'\n'.join(extract(spr,n) for n in ['blit_sprite2','blit_sprite2_filter']),
                    'wrapper':extract(t,'blit_enemy'),'end':extract(s,'render_mirror_entity_end')}
            dispatch=extract(s,'render_mirror_enemy_tile');groups['dispatch']=dispatch.split(' if(bank.data&&bank.data==spriteSheet11.data)')[0]+' return false;\n}\n'
            # No replacement of original write ordering or any gameplay logic.
            assert groups['wrapper'].count('blit_sprite2_filter(')==1 and groups['wrapper'].count('blit_sprite2(')==1
            assert 'secret_exit_orb' not in extract(s,'get_asset')
            for name,body in groups.items():(out/('actual_'+name+'.inc')).write_text(body)
            cflags=shlex.split(os.environ.get('SDL_CFLAGS','')) or shlex.split(subprocess.check_output(['pkg-config','--cflags','sdl2'],text=True));libs=shlex.split(os.environ.get('SDL_LIBS','')) or shlex.split(subprocess.check_output(['pkg-config','--libs','sdl2'],text=True))
            for san in ['', '-fsanitize=undefined']:
                suffix='ubsan' if san else 'plain';exe=out/('adapter-'+suffix)
                run(cc+flags+['-Wno-misleading-indentation','-I'+str(out)]+cflags+([san,'-fno-sanitize-recover=all'] if san else [])+[str(ROOT/'tests/secret_exit_orb_adapter.c'),str(ROOT/'src/secret_exit_orb.c')]+libs+['-lm','-o',str(exe)])
                run([str(exe),str(a.data_dir.resolve()),str(out),suffix],preexec_fn=limits,env={**os.environ,'SDL_VIDEODRIVER':'dummy','SDL_AUDIODRIVER':'dummy'})
            receipt.update(adapter='passed actual extracted dispatch, admission, compositor, pixel ledger, original normal/filter blitters and blit_enemy, plain + UBSan',extracted_sha256={k:hashlib.sha256(v.encode()).hexdigest() for k,v in groups.items()})
        (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
    finally:
        if not a.output:shutil.rmtree(out)
if __name__=='__main__':main()
