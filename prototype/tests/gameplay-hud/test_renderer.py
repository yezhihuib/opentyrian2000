#!/usr/bin/env python3
"""Synthetic production-helper renderer oracle. Requires no SDL/game data/art."""
import argparse
import os
from pathlib import Path
import re
import struct
import subprocess
import tempfile
from run_tests import checked_points

ROOT = Path(__file__).resolve().parents[3]
FIXED_FUNCTIONS = ['fixed_text_owned','fixed_text_source_matches','fixed_text_cached_indices_match','fixed_text_clear_cached','fixed_text_reset','fixed_text_check_mode','fixed_text_start','fixed_text_begin','fixed_text_compose']
INDICATOR_FUNCTIONS = ['hud_sprite_decode', 'indicator_cell', 'indicator_position', 'indicator_overlap', 'indicators_owned', 'indicators_source_matches', 'indicators_cached_indices_match', 'indicators_underlay_matches', 'indicators_clear_cached', 'indicators_reset', 'indicators_decode_modes', 'indicators_check_mode', 'indicators_start', 'indicators_begin', 'render_mirror_hud_mode_drawn', 'indicators_compose', 'indicators_fade_underlay']

BASE = 'a49e46e5f8880b98cfb41028b6389e97d0636433'

def extract(source, name):
    match = re.search(r'^(?:static )?(?:Uint32|unsigned int|int|void|bool) ' + name + r'\([^\n]*\)\s*\{', source, re.M)
    if not match:
        raise AssertionError('Missing production function: ' + name)
    start = source.index('{', match.start())
    end, depth = start + 1, 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[match.start():end] + '\n'

def fnv(data):
    h = 14695981039346656037
    for b in data:
        h = ((h ^ b) * 1099511628211) & ((1 << 64) - 1)
    return h

def fixture(path, expanded=False):
    mask = bytearray(64000)
    source = bytearray([7])*64000
    points = [(264, 0), (319, 0), (280, 109), (0, 184)]
    if expanded:
        points = checked_points(Path(__file__).with_name('approved-rails.spans'),310,
            '903328448558ea0a8b7ea1e895339602736664bad73b0828b8ace4b3732263d2')
        for x,count in [(285,6),(296,5)]:
            for y in range(138,138+count*6,6):
                for yy in range(y-1,y+6):
                    for xx in range(x-1,x+6):
                        if not (x<=xx<x+5 and y<=yy<y+5): source[yy*320+xx]=0
        (path/'source.indices').write_bytes(source)
        (path/'synthetic.mask').write_bytes(bytes(255 if (x,y) in points else 0 for y in range(200) for x in range(320)))
    for x,y in points:
        mask[y*320+x] = 255
    rgba = bytearray(4096000)
    for y in range(200):
        for x in range(320):
            for sy in range(4):
                for sx in range(4):
                    i = ((y*4+sy)*1280+x*4+sx)*4
                    rgba[i:i+4] = bytes(((x*13+sx*3)%256,(y*7+sy*5)%256,(sx+sy*4)*9,mask[y*320+x]))
    header = struct.pack('<4s8I3QI', b'HUD1',1,320,200,4,0,0,64000,4096000,fnv(source),fnv(mask),fnv(rgba),0)
    assert len(header) == 64
    (path/'gameplay-hud-v1.hda').write_bytes(header+mask+rgba)

def check_hooks():
    pic = (ROOT/'src/picload.c').read_text()
    game = (ROOT/'src/tyrian2.c').read_text()
    modal = (ROOT/'src/mainint.c').read_text()
    video = (ROOT/'src/video.c').read_text()
    assert pic.index('render_mirror_hud_reset();') < pic.index('PCXnumber--;')
    assert 'render_mirror_hud_start' not in pic
    start = game.index('JE_loadPic(VGAScreen, twoPlayerMode ? 6 : 3, false);')
    assert start < game.index('render_mirror_hud_start(VGAScreen);',start) < game.index('JE_drawOptions();',start)
    assert 'if (!twoPlayerMode && !galagaMode)' in game[start:game.index('JE_drawOptions();',start)]
    assert re.search(r'start_level:\s*render_mirror_hud_reset\(\);',game)
    assert re.search(r'render_mirror_hud_reset\(\);\s*JE_loadMap\(\);',game)
    assert 'if(asset_debug_before_tick()) {render_mirror_hud_reset();return;}' in game
    assert 'if (game_probe_end_tick()) {render_mirror_hud_reset();return;}' in game
    for name in ('JE_pauseGame','JE_doInGameSetup','JE_inGameHelp'):
        assert re.search(r'void '+name+r'\(void\)\s*\{\s*render_mirror_hud_suspend\(\);',modal)
    assert re.search(r'void deinit_video\(void\)\s*\{\s*render_mirror_hud_shutdown\(\);',video)
    assert video.index('render_mirror_hud_shutdown();') < video.index('SDL_FreeSurface(VGAScreenSeg);')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sanitize',action='store_true')
    args = parser.parse_args()
    check_hooks()
    common = ['palette_rgb','upscale','render_mirror_unsupported','render_mirror_begin','render_mirror_finish','render_mirror_fade_start','render_mirror_fade_step','render_mirror_present','render_mirror_release_texture']
    hud = ['components_owned','components_source_matches','components_cached_indices_match','components_clear_cached','components_reset','components_check_mode','components_start','components_begin','render_mirror_hud_shield_wiped','render_mirror_hud_shield_drawn','components_compose','hud_source_matches','hud_cached_indices_match','hud_clear_cached','hud_frame_reset','render_mirror_hud_reset','render_mirror_hud_shutdown','hud_sprite_decode','hud_runtime_compatible','hud_check_mode','render_mirror_hud_start','render_mirror_hud_suspend','hud_begin','hud_compose']
    sources = {'baseline':subprocess.check_output(['git','show',BASE+':src/render_mirror.c'],cwd=ROOT,text=True),'candidate':(ROOT/'src/render_mirror.c').read_text()}
    with tempfile.TemporaryDirectory(prefix='hud-renderer-') as directory:
        path = Path(directory)
        fixture(path)
        (path/'expanded').mkdir()
        fixture(path/'expanded', True)
        outputs = {}
        for variant,source in sources.items():
            # HUD definitions precede begin/finish; declarations remain in harness.
            names = common[:3] + (FIXED_FUNCTIONS+INDICATOR_FUNCTIONS+[n for n in hud if n!='hud_sprite_decode'] if variant=='candidate' else []) + common[3:]
            (path/'production.inc').write_text('\n'.join(extract(source,n) for n in names))
            executable = path/variant
            command = [os.environ.get('CC','cc'),'-std=c99','-O1','-g','-Wall','-Wextra','-Wno-unused-parameter','-Wno-unused-variable','-Wno-unused-function','-Wno-misleading-indentation','-I'+str(path),'-I'+str(ROOT/'src')]
            if variant=='baseline': command += ['-DBASELINE_RENDERER']
            if args.sanitize: command += ['-fsanitize=address,undefined','-fno-omit-frame-pointer','-no-pie']
            command += [str(Path(__file__).with_suffix('.c')),str(ROOT/'src/gameplay_hud.c'),str(ROOT/'src/gameplay_hud_components.c'),str(ROOT/'src/gameplay_hud_meters.c'),str(ROOT/'src/gameplay_hud_indicators.c'),str(ROOT/'src/gameplay_hud_fixed_text.c'),str(ROOT/'src/gameplay_hud_font.c'),'-o',str(executable)]
            subprocess.run(command,check=True)
            env=dict(os.environ)
            if args.sanitize:
                env.setdefault('ASAN_OPTIONS','detect_leaks=0:halt_on_error=1')
                env.setdefault('UBSAN_OPTIONS','halt_on_error=1:print_stacktrace=1')
            outputs[variant]=subprocess.check_output([str(executable),str(path)],env=env,text=True)
            print(variant+': '+outputs[variant].strip())
        baseline = re.search(r'BASELINE ([0-9a-f]+)',outputs['baseline']).group(1)
        candidate = re.search(r'BASELINE ([0-9a-f]+)',outputs['candidate']).group(1)
        assert baseline==candidate,(baseline,candidate)
        print('No-asset C/H outputs and fade states match pre-HUD production exactly; lifecycle hook assertions passed.')

if __name__=='__main__': main()
