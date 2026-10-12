#!/usr/bin/env python3
"""Compile real HUF1 integration and source writers against synthetic SDL/assets."""
from pathlib import Path
import argparse,os,subprocess,sys,tempfile
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'gameplay-hud'))
from test_renderer import extract,INDICATOR_FUNCTIONS,FIXED_FUNCTIONS
sys.path.insert(0,str(HERE));from fixtures import make,flags
p=argparse.ArgumentParser();p.add_argument('--sanitize',action='store_true');p.add_argument('--quick',action='store_true');a=p.parse_args()
src=(ROOT/'src/render_mirror.c').read_text();sprite=(ROOT/'src/sprite.c').read_text();font=(ROOT/'src/fonthand.c').read_text()
base=['components_owned','components_source_matches','components_cached_indices_match','components_clear_cached','components_reset','components_check_mode','components_start','components_begin','render_mirror_hud_shield_wiped','render_mirror_hud_shield_drawn','components_compose','hud_source_matches','hud_cached_indices_match','hud_clear_cached','hud_frame_reset','render_mirror_hud_reset','render_mirror_hud_shutdown','hud_runtime_compatible','hud_check_mode','render_mirror_hud_start','render_mirror_hud_suspend','hud_begin','hud_compose','render_mirror_begin','render_mirror_finish','render_mirror_fade_start','render_mirror_fade_step','render_mirror_present','render_mirror_release_texture']
writers=['blend_rgba','cloud_shadow_rgba','darken_rgba','brightness_rgba','complete_turret_group','restore_classic_rect','render_mirror_pixel','render_mirror_rect','render_mirror_brightness_pixel','cloud_asset','explosion_asset_slot','enemy_filter_rgba','explosion_asset_blend_rgba','green_background_snapshot','green_background_peak','green_head_composite','draw_asset_filtered','explosion_blend_rgba','have_supported_talon','render_mirror_sprite2_blend_pixel','cloud_terrain_slot','ground_terrain_slot','plateau_terrain_slot','underlay_terrain_slot','road_terrain_slot','terrain_holes_slot','stone_foundation_slot','layer3_gray_slot','layer3_purple_slot','layer3_circuit_slot','layer3_mechanical_slot','grass_sand_slot','forest_terrain_slot','render_mirror_terrain_row','render_mirror_terrain_pixel']
assert src.index('font_before_effect(r);',src.index('static void restore_classic_rect'))>src.index('} while(changed);',src.index('static void restore_classic_rect'))
body=extract(src,'draw_asset_filtered');assert body.index('font_before_effect((SDL_Rect){x-1,y-1,14,16})')<body.index('green_background_snapshot(')
assert 'font_before_effect((SDL_Rect){x,y,1,1});' in extract(src,'render_mirror_sprite2_blend_pixel')
assert extract(src,'render_mirror_finish').index('font_prepare_finish();')<extract(src,'render_mirror_finish').index('upscale(output,VGAScreenSeg);')
with tempfile.TemporaryDirectory(prefix='huf-renderer-') as tmp:
 d=Path(tmp);values,raw=make(d)
 parts=[(HERE/'writer_scaffold.inc').read_text()]+[extract(src,n) for n in ['palette_rgb','upscale','render_mirror_unsupported']+FIXED_FUNCTIONS+INDICATOR_FUNCTIONS+base+writers]
 parts += [extract(sprite,n) for n in ('blit_sprite','blit_sprite_hv_unsafe','blit_sprite_dark')]
 parts += [extract(font,n) for n in ('JE_outText','JE_textShade')]
 parts += [extract((ROOT/'src/mainint.c').read_text(),'JE_drawTextWindow')]
 (d/'production.inc').write_text('\n'.join(parts))
 common=[os.environ.get('CC','cc'),'-std=c99','-O1','-g','-Wall','-Wextra','-Wno-unused-parameter','-Wno-unused-variable','-Wno-unused-function','-Wno-misleading-indentation','-I'+str(d),'-I'+str(ROOT/'src')]
 if a.sanitize:common+=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-no-pie']
 cmd=common+flags(values)+[str(HERE/'test_renderer.c')]+[str(ROOT/'src'/n) for n in ('gameplay_hud.c','gameplay_hud_components.c','gameplay_hud_indicators.c','gameplay_hud_fixed_text.c','gameplay_hud_font.c')]+['-o',str(d/'test')]
 subprocess.run(cmd,check=True);subprocess.run([str(d/'test'),str(d)]+(['quick'] if a.quick else []),check=True,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1'))
