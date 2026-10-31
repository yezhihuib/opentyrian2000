"""Pure finite 166/94 fixture/source/schema helpers. Import is inert.
No process, game, compiler, producer CLI or filesystem writes. Production HDA
and fixture functions return bytes in RAM only; caller owns measured materialization.
The five inherited processes and all their generated source bytes are unchanged.
"""
from pathlib import Path
import hashlib, io, json, re, stat, struct, types
PULSES = (166, 94)
IDS = (91, 145, 61, 101, 120, 139, 168, 169, 162, 260, 166, 94)
HDA_NAMES = {i: (f'enemy-projectile{i}-{i}-8.hda' if i in (91,145,61) else
    f'enemy-projectile-blue-triplet-{i}-8.hda' if i in (101,120,139) else
    f'enemy-projectile-gold-pulse-{i}-8.hda' if i in (168,169) else
    f'enemy-projectile-statics-{i}-8.hda' if i in (162,260) else
    f'enemy-projectile-pulses16694-{i}-8.hda') for i in IDS}
PACK_NAMES = (('valid',) + tuple(n+str(i) for i in IDS for n in ('missing','bad')) +
    ('only166','only94','old-only') + tuple(n+str(i) for i in PULSES for n in ('header','short','trailing')) +
    tuple(n+str(i) for i in PULSES for n in ('magic','density','width','height','anchorx','anchory')))
STATICS_HELPER_SHA = '88f2d4ccb4fbca8be4d00b11d501cf8cfb076a70cc9355bf887d045ffa4fa90a'
STATICS_COMPANION_SHA = '6886018f5bc62216ae48797ae888fbd169fcdbee3d42107856872b536d4e866e'
STATICS_WRAPPER_SHA = '8b7443e8d55e57d66a89b3f472ccca1c732697118da1489bae197f829881004c'
TAIL = (b'\n#include "projectile_pulses16694_native_additions.c.inc"\n'
        b'int main(int argc,char **argv)\n{\n'
        b' if(argc>=2&&!strcmp(argv[1],"--enemy-pulses16694"))return pulses16694_main(argc,argv);\n'
        b' return inherited_statics_dispatch(argc,argv);\n}\n')
SOURCE_PINS = {'inherited145_harness.c': '8925fb11215446339f067124fa7223ec48dc7c86459e303d3803477773b2d9ac', 'accepted_projectile61_native_additions.c.inc': '5f80d681e84a6dff20873f7f05bb3a02e3fd0f22013edf2b5fbf133d36c51cfe', 'accepted61_wrapper.c': '59bfbe4d8e3bb8db4403eaabb199d8ff2f09b2eb2047769f39069c93dff7f4eb', 'projectile61_native_additions.c.inc': 'd894e392ce315b855d5a764fbb526b6d6568a14f223e7e577a4ebf303ecbf67a', 'projectile_blue_triplet_native_additions.c.inc': 'cf38a2c8582bf9c3299a84721d37dae83402b938c859a2489ad382844a9a6084', 'harness.c': 'd39e3b9633eff3abfc70604f96895f21184fa87ad7f344ffa64f2b7705b353e1'}
STDOUT_PINS = {'inherited107_stdout': ('56b267d7cf607164010655de7fbd79fa42d3dc4518865434c2c4b705280856b2', 236), 'inherited61_stdout': ('bbc4b539205c19faa66ec7ada0c755d80907950e9ab91b554633c77fe261bcf4', 165), 'new_blue_stdout': ('833b3944bde9933444f4102716403b9868e1cefec4a077daeecd8535bef5208e', 631), 'gold251_stdout': ('a1f762926d2fb3bbc2499c5d7dc87f94cd20e239189f69af3646dcc58c4459d5', 973)}
DATA_PINS = {'tyrian.shp': '80cae98e073be6d7f710495920b71497bb23f108ea6631d6faf352c4729474f0', 'tyrianc.shp': 'e980f02021395d39b86491acdc2ecd6dd47ea2a9f859fe3928f81b75e244fd7d', 'palette.dat': 'f628396306805387f07f72c4ccf0fdee9ca84b8e70ae23ba4ec58ec5fb362da0'}
STDOUT_PINS = {**STDOUT_PINS, 'statics449_stdout': ('fc00c7f5120d9670fc500e8692e418798b93029c7af261ae0f3629ce50f92aef',1577)}
PINS = {166: {'png_sha256': 'af41c280b551a3c2e0b440a3f114145dc7e6bf206fd61039411f6807cd7e2750', 'hda_sha256': 'e14f6cc59d8f0773fa20b840c4ea453bb6c2afebcc4e27806c927c2f9751fb89', 'rgba_sha256': '8850072a95b19fdd57acd6c432c2a4ee65f65b5c6d359547a9cd62411ebb8703', 'fnv1a64': '80c10783a6cabbe2', 'native_cells': 97, 'native_mask': '000000000000000011111000000111111100001111111110011111111111011111111111011111111111011111111111011111111111001111111110000111111100000011111000000000000000000000000000', 'max_alpha_matrix': [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 76, 122, 141, 128, 76, 0, 0, 0], [0, 0, 0, 169, 237, 252, 252, 252, 249, 196, 0, 0], [0, 0, 174, 252, 253, 253, 253, 252, 252, 252, 187, 0], [0, 82, 245, 252, 253, 252, 252, 252, 252, 252, 250, 77], [0, 114, 251, 252, 252, 252, 252, 252, 252, 252, 252, 132], [0, 128, 252, 252, 252, 252, 252, 252, 252, 253, 252, 157], [0, 120, 252, 252, 252, 252, 252, 252, 252, 252, 252, 139], [0, 67, 240, 252, 252, 252, 252, 252, 252, 252, 247, 63], [0, 0, 171, 251, 252, 252, 253, 252, 252, 252, 161, 0], [0, 0, 0, 183, 244, 252, 252, 252, 251, 154, 0, 0], [0, 0, 0, 0, 73, 129, 147, 133, 66, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], 'high_ge200': 69, 'low_1_199': 28, 'zero': 0, 'alpha0_rgb_nonzero': 0, 'max_alpha': 253, 'native_alpha0': 420, 'nonzero': 5788, 'opaque255': 0, 'outside_nonzero': 0, 'soft': 5788, 'palette_indices': [33, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159]}, 94: {'png_sha256': '2e229012e33f26d6104ca746d83c35e3eb3f9108d2f2690073387c1d19eccacc', 'hda_sha256': 'cf6f70641746a3b8eb91d61d5c414af7545e748f6583351972aa76c46f813f93', 'rgba_sha256': '207b4f8a9890486490345820de0c0d589a7e7532f6aeb4687294e85e8aa6485e', 'fnv1a64': '131a3be7ed56665d', 'native_cells': 108, 'native_mask': '000001100000000001100000000011110000001111111100001111111100011111111110011111111110011111111110011111111110011111111110011111111110011111111110001111111100000111111000', 'max_alpha_matrix': [[0, 0, 0, 0, 0, 255, 255, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 254, 255, 0, 0, 0, 0, 0], [0, 0, 0, 0, 252, 253, 253, 252, 0, 0, 0, 0], [0, 0, 56, 253, 253, 253, 253, 253, 253, 68, 0, 0], [0, 0, 252, 253, 253, 253, 253, 253, 253, 253, 0, 0], [0, 252, 253, 253, 253, 253, 253, 253, 253, 253, 251, 0], [0, 253, 253, 253, 253, 253, 253, 253, 253, 253, 253, 0], [0, 255, 253, 253, 253, 253, 253, 253, 253, 253, 255, 0], [0, 255, 253, 253, 253, 253, 253, 253, 253, 253, 255, 0], [0, 255, 253, 253, 253, 253, 253, 253, 253, 253, 255, 0], [0, 255, 253, 253, 253, 253, 252, 253, 253, 253, 255, 0], [0, 179, 253, 253, 253, 253, 253, 253, 253, 254, 216, 0], [0, 0, 247, 253, 253, 253, 253, 253, 253, 251, 0, 0], [0, 0, 0, 115, 252, 253, 252, 252, 119, 0, 0, 0]], 'high_ge200': 103, 'low_1_199': 5, 'zero': 0, 'alpha0_rgb_nonzero': 0, 'max_alpha': 255, 'native_alpha0': 424, 'nonzero': 6488, 'opaque255': 40, 'outside_nonzero': 0, 'soft': 6448, 'palette_indices': [114, 115, 116, 117, 119, 120, 121, 122, 123, 124, 125, 126, 127]}}
GROUPS = (('full_tile_native_patterns', 4), ('full_tile_hd_underlay', 2), ('bounds', 22), ('pair_orders_zero_isolation', 42), ('all12_same_origin_dependency', 24), ('all12_two_row_dependency', 24), ('missing_bad', 48), ('singletons_oldonly', 4), ('malformed_headers_lengths', 18), ('readiness_root_epochs', 4), ('unused_memory_payload_ready', 8), ('palette_admission_shared', 60), ('palette_direct_final_cache', 66), ('palette_composite_preflight', 29), ('used_resource_direct_final_cache', 52), ('source_scope_direct_final_cache', 24), ('layout_direct_final_cache', 32), ('callbacks', 12), ('cold_warm_scope', 44), ('Talon_transfer', 4), ('Talon_underlay_direct', 8), ('lifecycle', 7), ('later_native_final_writers', 8), ('fade_high_bits', 8), ('player_generic_aliases', 8), ('all12_fade_lease', 4), ('legacy_reject_own_foreign', 12))
TRANSFER = {166:(1176,1176,133),94:(1081,1081,56)}

STATICS = (162, 260)
GOLD = (168, 169)
COVERAGE_SHA = '6dac9390092d62f44e36497a9b0336ba23158b5ce84951f3e5b5677653bbada5'
ASSET_DIRECTORY = 'assets/hd/current-compat/projectile-pulses16694'
COVERAGE_PATH = 'authoring-inputs/projectile-pulses16694-current/coverage-contract.json'
COVERAGE_SPEC = {'schema': 'enemy-pulses16694-selected-coverage-v1', 'members': {'166': {'native_mask': '000000000000000011111000000111111100001111111110011111111111011111111111011111111111011111111111011111111111001111111110000111111100000011111000000000000000000000000000', 'native_occupied_cells': 97, 'max_alpha_matrix': [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 76, 122, 141, 128, 76, 0, 0, 0], [0, 0, 0, 169, 237, 252, 252, 252, 249, 196, 0, 0], [0, 0, 174, 252, 253, 253, 253, 252, 252, 252, 187, 0], [0, 82, 245, 252, 253, 252, 252, 252, 252, 252, 250, 77], [0, 114, 251, 252, 252, 252, 252, 252, 252, 252, 252, 132], [0, 128, 252, 252, 252, 252, 252, 252, 252, 253, 252, 157], [0, 120, 252, 252, 252, 252, 252, 252, 252, 252, 252, 139], [0, 67, 240, 252, 252, 252, 252, 252, 252, 252, 247, 63], [0, 0, 171, 251, 252, 252, 253, 252, 252, 252, 161, 0], [0, 0, 0, 183, 244, 252, 252, 252, 251, 154, 0, 0], [0, 0, 0, 0, 73, 129, 147, 133, 66, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]], 'cell_distribution': {'high_ge200': 69, 'low_1_199': 28, 'zero': 0}, 'pixels': {'nonzero': 5788, 'soft': 5788, 'opaque255': 0, 'native_alpha0': 420, 'max_alpha': 253, 'outside_nonzero': 0, 'alpha0_rgb_nonzero': 0}, 'png_sha256': 'af41c280b551a3c2e0b440a3f114145dc7e6bf206fd61039411f6807cd7e2750', 'hda_sha256': 'e14f6cc59d8f0773fa20b840c4ea453bb6c2afebcc4e27806c927c2f9751fb89', 'payload_sha256': '8850072a95b19fdd57acd6c432c2a4ee65f65b5c6d359547a9cd62411ebb8703', 'payload_fnv': '80c10783a6cabbe2', 'palette_indices': [33, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159]}, '94': {'native_mask': '000001100000000001100000000011110000001111111100001111111100011111111110011111111110011111111110011111111110011111111110011111111110011111111110001111111100000111111000', 'native_occupied_cells': 108, 'max_alpha_matrix': [[0, 0, 0, 0, 0, 255, 255, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 254, 255, 0, 0, 0, 0, 0], [0, 0, 0, 0, 252, 253, 253, 252, 0, 0, 0, 0], [0, 0, 56, 253, 253, 253, 253, 253, 253, 68, 0, 0], [0, 0, 252, 253, 253, 253, 253, 253, 253, 253, 0, 0], [0, 252, 253, 253, 253, 253, 253, 253, 253, 253, 251, 0], [0, 253, 253, 253, 253, 253, 253, 253, 253, 253, 253, 0], [0, 255, 253, 253, 253, 253, 253, 253, 253, 253, 255, 0], [0, 255, 253, 253, 253, 253, 253, 253, 253, 253, 255, 0], [0, 255, 253, 253, 253, 253, 253, 253, 253, 253, 255, 0], [0, 255, 253, 253, 253, 253, 252, 253, 253, 253, 255, 0], [0, 179, 253, 253, 253, 253, 253, 253, 253, 254, 216, 0], [0, 0, 247, 253, 253, 253, 253, 253, 253, 251, 0, 0], [0, 0, 0, 115, 252, 253, 252, 252, 119, 0, 0, 0]], 'cell_distribution': {'high_ge200': 103, 'low_1_199': 5, 'zero': 0}, 'pixels': {'nonzero': 6488, 'soft': 6448, 'opaque255': 40, 'native_alpha0': 424, 'max_alpha': 255, 'outside_nonzero': 0, 'alpha0_rgb_nonzero': 0}, 'png_sha256': '2e229012e33f26d6104ca746d83c35e3eb3f9108d2f2690073387c1d19eccacc', 'hda_sha256': 'cf6f70641746a3b8eb91d61d5c414af7545e748f6583351972aa76c46f813f93', 'payload_sha256': '207b4f8a9890486490345820de0c0d589a7e7532f6aeb4687294e85e8aa6485e', 'payload_fnv': '131a3be7ed56665d', 'palette_indices': [114, 115, 116, 117, 119, 120, 121, 122, 123, 124, 125, 126, 127]}}}
CAPTURE_PRODUCTION_FILES = {'src/asset_debug.c': {'file_sha256': 'ea6de19bf2e983a83096fd441216b21a8d611d529b13b2bde1f9878122c0a298', 'functions': {'void asset_debug_parse(int *argc,char **argv)': {'body': 'void asset_debug_parse(int *argc,char **argv)\n{\n int out=1;bool custom_tick=false,custom_episode=false,custom_level=false;\n for(int i=1;i<*argc;i++){\n  const char *s=argv[i];\n  if(!strncmp(s,"--asset-debug=",14)){asset_debug_enabled=true;s+=14;if(!strcmp(s,"blue")){preset_target=890;preset_kind=1;}else if(!strcmp(s,"turret")){preset_target=232;preset_kind=2;}else if(!strcmp(s,"type10")){preset_target=150;preset_kind=3;}else if(!strcmp(s,"custom")){}else{fprintf(stderr,"Asset debug: unknown preset\\n");exit(2);}}\n  else if(!strncmp(s,"--asset-debug-episode=",22)){episode=number(s+22,1,EPISODE_MAX,"episode");custom_episode=true;}\n  else if(!strncmp(s,"--asset-debug-level=",20)){level=number(s+20,1,255,"level");custom_level=true;}\n  else if(!strncmp(s,"--asset-debug-tick=",19)){target=number(s+19,0,5999,"tick");custom_tick=true;}\n  else if(!strncmp(s,"--asset-debug-event=",20))target_event=number(s+20,1,65534,"event ordinal");\n  else if(!strncmp(s,"--asset-debug-control=",22))control_path=s+22;\n  else if(!strcmp(s,"--asset-debug-reference"))reference=true;\n  else if(!strcmp(s,"--asset-debug-running"))paused=false;\n  else if(!strcmp(s,"--asset-debug-capture"))capture=true;\n  else if(!strncmp(s,"--asset-debug-capture-start=",28))capture_start=number(s+28,0,5999,"capture start");\n  else if(!strncmp(s,"--asset-debug-capture-count=",28))capture_count=number(s+28,1,120,"capture count");\n  else if(!strcmp(s,"--asset-debug-window-only"))window_only=true;\n  else if(!strcmp(s,"--asset-debug-explosion-log"))explosion_log_enabled=true;\n  else if(!strcmp(s,"--asset-debug-index-only"))index_only=true;\n  else argv[out++]=argv[i];\n }\n if(!asset_debug_enabled&&(custom_tick||custom_episode||custom_level||target_event||control_path||reference||capture||capture_start!=UINT32_MAX||capture_count!=36||window_only||explosion_log_enabled||index_only||!paused)){fprintf(stderr,"Asset debug options require --asset-debug=preset\\n");exit(2);}\n if(asset_debug_enabled&&target_event&&custom_tick){fprintf(stderr,"Asset debug: select a tick or event, not both\\n");exit(2);}\n if((capture_start!=UINT32_MAX||capture_count!=36||window_only)&&!capture){fprintf(stderr,"Asset debug capture bounds/window-only require --asset-debug-capture\\n");exit(2);}\n if(!custom_tick)target=preset_target;\n argv[out]=NULL;*argc=out;started=SDL_GetPerformanceCounter();fast=!reference;\n}', 'sha256': '6855c0d17f10998ea86b6effabba68d8aeac700a61fdd52dd66c2aa66c446994'}}}, 'src/game_probe.c': {'file_sha256': '1821fc281c91d70a69e5dbcb6cf0292aa3cb57abfc85697e5aee67b17df9b34d', 'functions': {'bool game_probe_capture_disabled(void)': {'body': 'bool game_probe_capture_disabled(void){return no_capture;}', 'sha256': 'd74ed40828a89e13ea94cf34cd29458fdd2bc7fe25968090af4e5fab8f1726ab'}, 'bool game_probe_capture_tick(void)': {'body': 'bool game_probe_capture_tick(void)\n{\n if(!game_probe_enabled||no_capture)return false;\n if(asset_debug_enabled)return asset_debug_capture_tick()&&!asset_debug_window_only();\n if(game_probe_blend_capture&&game_probe_tick>=192&&game_probe_tick<=212)return true;\n if(game_probe_tick>=128&&game_probe_tick<=360&&game_probe_tick%8==0)return true;\n if(last_scene_hit_tick!=UINT32_MAX&&game_probe_tick>=last_scene_hit_tick&&game_probe_tick-last_scene_hit_tick<=2)return true;\n if(banking_scene&&(capture_pose_change||(game_probe_tick>=164&&game_probe_tick<=356&&game_probe_tick%4==0)))return true;\n static const unsigned int samples[]={0,3,7,13,14,99,100,120,179,188,293,359,515,534,599};\n for(unsigned int i=0;i<sizeof(samples)/sizeof(samples[0]);i++) if(game_probe_tick==samples[i])return true;\n if(last_enemy_hit_tick!=UINT32_MAX&&game_probe_tick>=last_enemy_hit_tick&&game_probe_tick-last_enemy_hit_tick<=2)return true;\n return game_probe_tick==tick_limit-1;\n}', 'sha256': 'c9d8f5bf206194ec07bade474914ff696e17be0e9ec970aa71a9f23f261dbdb8'}, 'void game_probe_parse(int *argc, char **argv)': {'body': 'void game_probe_parse(int *argc, char **argv)\n{\n enemy_reuse_observe_parse(argc,argv);\n /* Inspect the untouched arguments: asset_debug_parse consumes its options. */\n bool manual_requested=false,asteroid_requested=false,diagnostic_requested=false;\n for(int i=1;i<*argc;i++) {\n  if(strncmp(argv[i],"--manual-hd-assets=",19)==0)manual_requested=true;\n  if(strncmp(argv[i],"--asteroid-hd-assets=",21)==0)asteroid_requested=true;\n  if(strncmp(argv[i],"--render-",9)==0||strncmp(argv[i],"--asset-debug",13)==0)diagnostic_requested=true;\n }\n if(asteroid_requested&&(manual_requested||diagnostic_requested)) {\n  fprintf(stderr,"Asteroid HD assets cannot be combined with manual, render or asset-debug options\\n");exit(2);\n }\n if(manual_requested&&diagnostic_requested) {\n  fprintf(stderr,"Manual HD assets cannot be combined with render or asset-debug options\\n");exit(2);\n }\n asset_debug_parse(argc,argv);\n if(asset_debug_enabled){game_probe_enabled=true;game_probe_density=8;game_probe_local_blend=true;game_probe_known_blend=true;game_probe_scene_assets=3;enemy_hit_scene=true;tick_limit=6000;}\n int out=1;\n bool explicit_ticks=false;\n for(int i=1;i<*argc;i++) {\n#if defined(ENEMY_REUSE_HD_PROTOTYPE) && ENEMY_REUSE_HD_PROTOTYPE && !defined(RENDER_MIRROR_DISABLED)\n  if(strncmp(argv[i],"--render-enemy-reuse-session=",29)==0) {\n   if(probe_requested||strcmp(argv[i]+29,"original-events-v1")) {fprintf(stderr,"Invalid or duplicate enemy reuse probe contract\\n");exit(2);}\n   probe_requested=true;continue;\n  }\n#endif\n  if(strncmp(argv[i],"--hud-assets=",13)==0) {\n   if(!argv[i][13] || !render_mirror_set_hud_assets(argv[i]+13)) {\n    fprintf(stderr,"Shared HUD assets require a valid nonempty directory\\n");exit(2);\n   }\n   /* Display resolution only: never grants scene or probe authority. */\n   game_probe_density=8;\n  } else if(strncmp(argv[i],"--global-assets=",16)==0) {\n   if(!argv[i][16] || !render_mirror_set_global_assets(argv[i]+16)) {\n    fprintf(stderr,"Global assets require a valid nonempty directory\\n");exit(2);\n   }\n   game_probe_density=8;\n  } else if(strncmp(argv[i],"--manual-hd-assets=",19)==0) {\n   if(!argv[i][19]) {fprintf(stderr,"Manual HD assets require a nonempty directory\\n");exit(2);}\n   manual_hd_enabled=true;game_probe_assets=argv[i]+19;\n   game_probe_density=8;game_probe_local_blend=true;game_probe_known_blend=true;game_probe_scene_assets=3;\n  } else if(strncmp(argv[i],"--asteroid-hd-assets=",21)==0) {\n   if(!argv[i][21]) {fprintf(stderr,"Asteroid HD assets require a nonempty directory\\n");exit(2);}\n   asteroid_hd_enabled=true;game_probe_assets=argv[i]+21;\n   game_probe_density=8;game_probe_local_blend=true;game_probe_known_blend=false;game_probe_scene_assets=1;\n  } else if(strncmp(argv[i],"--render-test=",14)==0) {\n   const char *mode=argv[i]+14; game_probe_enabled=true;\n   if(strcmp(mode,"classic")==0) game_probe_density=1;\n   else if(strcmp(mode,"4")==0) game_probe_density=4;\n   else if(strcmp(mode,"8")==0) game_probe_density=8;\n   else if(strcmp(mode,"missing")==0) { game_probe_density=8; game_probe_missing=true; }\n   else if(strcmp(mode,"repeat")==0) { game_probe_density=8; game_probe_repeat=true; }\n   else if(strcmp(mode,"invalid")==0) { game_probe_density=8; game_probe_invalid=true; }\n   else if(strcmp(mode,"coverage-fault")==0) { game_probe_density=8; game_probe_coverage_fault=true; }\n   else if(strcmp(mode,"skip")==0) { game_probe_density=8; game_probe_skip=true; }\n   else if(strcmp(mode,"local")==0) { game_probe_density=8; game_probe_local_blend=true; }\n   else { fprintf(stderr,"Invalid --render-test mode\\n"); exit(2); }\n  } else if(strncmp(argv[i],"--render-ticks=",15)==0) {\n   explicit_ticks=true;\n   char *end=NULL; unsigned long v=strtoul(argv[i]+15,&end,10);\n   if(!end||*end||v<60||v>6000) { fprintf(stderr,"Render ticks must be 60..6000\\n");exit(2); }\n   tick_limit=(unsigned int)v;\n  } else if(strncmp(argv[i],"--render-front-port=",20)==0) {\n   preview_port[FRONT_WEAPON]=preview_number(argv[i]+20,0,47,"front port");loadout_selected=true;\n  } else if(strncmp(argv[i],"--render-rear-port=",19)==0) {\n   preview_port[REAR_WEAPON]=preview_number(argv[i]+19,0,47,"rear port");loadout_selected=true;\n  } else if(strncmp(argv[i],"--render-front-power=",21)==0) {\n   preview_power[FRONT_WEAPON]=preview_number(argv[i]+21,1,11,"front power");loadout_selected=true;\n  } else if(strncmp(argv[i],"--render-rear-power=",20)==0) {\n   preview_power[REAR_WEAPON]=preview_number(argv[i]+20,1,11,"rear power");loadout_selected=true;\n  } else if(strncmp(argv[i],"--render-rear-mode=",19)==0) {\n   preview_rear_mode=preview_number(argv[i]+19,1,2,"rear mode");loadout_selected=true;\n  } else if(strncmp(argv[i],"--render-left-sidekick=",23)==0||strncmp(argv[i],"--render-right-sidekick=",24)==0) {\n   unsigned int mount=argv[i][9]==\'l\'?LEFT_SIDEKICK:RIGHT_SIDEKICK;\n   unsigned int id=preview_number(argv[i]+(mount==LEFT_SIDEKICK?23:24),0,3,"sidekick");\n   if(id!=0&&id!=3){fprintf(stderr,"Weapon preview: sidekick must be 0 or 3\\n");exit(2);}\n   preview_sidekick[mount]=id;sidekicks_selected=true;\n  } else if(strncmp(argv[i],"--render-sidekick-input=",24)==0) {\n   if(strcmp(argv[i]+24,"charge-stages")){fprintf(stderr,"Weapon preview: invalid sidekick input preset\\n");exit(2);}\n   charge_stages=true;\n  } else if(strcmp(argv[i],"--render-no-capture")==0) no_capture=true;\n  else if(strncmp(argv[i],"--render-assets=",16)==0) game_probe_assets=argv[i]+16;\n  else if(strcmp(argv[i],"--render-local-blend")==0) game_probe_local_blend=true;\n  else if(strcmp(argv[i],"--render-original-reference")==0) game_probe_original_reference=true;\n  else if(strcmp(argv[i],"--render-known-explosion-blend")==0) game_probe_known_blend=true;\n  else if(strcmp(argv[i],"--render-capture-blend")==0) game_probe_blend_capture=true;\n  else if(strcmp(argv[i],"--render-talon-bank=13")==0) render_mirror_set_talon_banking(true);\n  else if(strcmp(argv[i],"--render-talon-bank=5")==0) render_mirror_set_talon_banking(false);\n  else if(strncmp(argv[i],"--render-scene-assets=",22)==0) {\n   const char *scope=argv[i]+22;\n   if(strcmp(scope,"off")==0)game_probe_scene_assets=0;\n   else if(strcmp(scope,"enemy")==0)game_probe_scene_assets=1;\n   else if(strcmp(scope,"terrain")==0)game_probe_scene_assets=2;\n   else if(strcmp(scope,"all")==0)game_probe_scene_assets=3;\n   else {fprintf(stderr,"Invalid render scene asset scope\\n");exit(2);}\n  }\n  else if(strncmp(argv[i],"--render-scene=",15)==0) {\n   const char *scene=argv[i]+15;\n   enemy_hit_scene=fade_cycle_scene=banking_scene=false;\n   if(strcmp(scene,"v1")==0) {}\n   else if(strcmp(scene,"enemy-hit")==0)enemy_hit_scene=true;\n   else if(strcmp(scene,"fade-cycle")==0)fade_cycle_scene=true;\n   else if(strcmp(scene,"banking")==0)banking_scene=true;\n   else {fprintf(stderr,"Invalid render scene\\n");exit(2);}\n  }\n  else argv[out++]=argv[i];\n }\n if(charge_stages) {\n  if(explicit_ticks){fprintf(stderr,"Weapon preview: charge-stages is fixed at 90 ticks; omit --render-ticks\\n");exit(2);}\n  tick_limit=90;\n }\n if((loadout_selected||sidekicks_selected||charge_stages||no_capture)&&!game_probe_enabled) {\n  fprintf(stderr,"Weapon preview options require --render-test or --asset-debug\\n");exit(2);\n }\n probe_parse_contract();\n argv[out]=NULL; *argc=out;\n}', 'sha256': '9d7fd7adca1c88b4729c7ca6fc2b81cc7c5a42ca47a4494867127e0a80999dc5'}}}}
NORMAL15_PALETTE_FUNCTION = b'static bool normal15_palette(void)\n{\n uint64_t hash=UINT64_C(14695981039346656037);\n for(unsigned i=0;i<256;i++)for(int shift=16;shift>=0;shift-=8) {\n  hash^=(rgb_palette[i]>>shift)&255u;hash*=UINT64_C(1099511628211);\n }\n return hash==UINT64_C(0x5e80e83992be2927);\n}'
PULSES_STDOUT_PIN = ('888b7d8a3c5ab2b50ca1bd676f8724620e2e1e6aab3917e47527398a3e5dcf96', 2907)
PULSES_COMPANION_SHA = '69e1933ddb17b3948688be5ce3e2b0f39ddee6821f6d41bbb0a6acd4a95e7322'
CAPTURE_NEW = b' if(argc>=2&&!strcmp(argv[1],"--enemy-pulses16694")) {\n  const bool saved_enabled=game_probe_enabled;\n  const int saved_density=game_probe_density;\n  const unsigned saved_tick=game_probe_tick, saved_scene=game_probe_scene_assets;\n  const uint64_t saved_rng=mt_state_fingerprint();\n  const char *saved_assets=game_probe_assets,*saved_reject=reject_reason;\n  SDL_Surface *saved_canvas=canvas,*saved_output=output;\n  Uint8 *saved_owner=global_projectile91_owner,*saved_foreign=global_projectile91_foreign;\n  const unsigned saved_used=global_projectile91_used_members;\n  const bool saved_flags[]={manual_hd_enabled,asteroid_hd_enabled,game_probe_missing,game_probe_repeat,game_probe_invalid,game_probe_coverage_fault,game_probe_skip,game_probe_local_blend,game_probe_original_reference,game_probe_known_blend,game_probe_blend_capture,asset_debug_enabled,ready,last_output_valid,global_projectile91_cached,global_projectile91_contributed};\n  char positive_mode[]="--render-test=8";\n  char *positive_argv[]={argv[0],positive_mode,NULL};int positive_argc=2;\n  if(saved_tick!=0||saved_enabled||saved_density!=1||asset_debug_enabled||game_probe_capture_disabled())abort();\n  game_probe_parse(&positive_argc,positive_argv);\n  if(positive_argc!=1||positive_argv[0]!=argv[0]||positive_argv[1]!=NULL||!game_probe_enabled||game_probe_density!=8||game_probe_tick!=saved_tick||game_probe_capture_disabled()||!game_probe_capture_tick())abort();\n  char capture_mode[]="--render-test=8",capture_flag[]="--render-no-capture";\n  char *capture_argv[]={argv[0],capture_mode,capture_flag,NULL};int capture_argc=3;\n  game_probe_parse(&capture_argc,capture_argv);\n  if(capture_argc!=1||capture_argv[0]!=argv[0]||capture_argv[1]!=NULL||!game_probe_enabled||game_probe_density!=8||game_probe_tick!=saved_tick||!game_probe_capture_disabled()||game_probe_capture_tick())abort();\n  game_probe_enabled=saved_enabled;game_probe_density=saved_density;\n  const bool actual_flags[]={manual_hd_enabled,asteroid_hd_enabled,game_probe_missing,game_probe_repeat,game_probe_invalid,game_probe_coverage_fault,game_probe_skip,game_probe_local_blend,game_probe_original_reference,game_probe_known_blend,game_probe_blend_capture,asset_debug_enabled,ready,last_output_valid,global_projectile91_cached,global_projectile91_contributed};\n  if(game_probe_enabled!=saved_enabled||game_probe_density!=saved_density||game_probe_tick!=saved_tick||mt_state_fingerprint()!=saved_rng||game_probe_scene_assets!=saved_scene||game_probe_assets!=saved_assets||reject_reason!=saved_reject||canvas!=saved_canvas||output!=saved_output||global_projectile91_owner!=saved_owner||global_projectile91_foreign!=saved_foreign||global_projectile91_used_members!=saved_used||memcmp(saved_flags,actual_flags,sizeof(saved_flags))||!game_probe_capture_disabled())abort();\n  return pulses16694_main(argc,argv);\n }\n'
CAPTURE_OLD = b' if(argc>=2&&!strcmp(argv[1],"--enemy-pulses16694"))return pulses16694_main(argc,argv);\n'
ORIGINAL_WRAPPER_SHA = '9667e48bcf1ad27c7f038259d5d1620d818de45f837e36c99cfec91bc703bd78'
CAPTURE_WRAPPER_SHA = '80776b35739f5751f465af4329771dc9a8f3d7fd60572c536fd3266f0430536e'
PALETTE5_FNV = 6809697970556905767
PALETTE5_RGB_SHA = 'd4c24a49efb588abd6dc1ffd0f0d1279a498c422cdd26fba4fc921b07f8c159f'
PALETTE5_LE32_SHA = 'ba249050344157b75e14a846649cc634b098ba448071ba44ecae8647aff01c7c'
PALETTE_FILE_SHA = 'f628396306805387f07f72c4ccf0fdee9ca84b8e70ae23ba4ec58ec5fb362da0'
PULSES_STDIN_SHA = '723d7a7a431b202419c12cce25e7298c2db9e9c5d88ac42cb7dc95fe51fcb463'


def reject_constant(value):
    raise AssertionError(('Non-finite JSON constant', value))


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        assert key not in result, ('Duplicate JSON key', key)
        result[key] = value
    return result


def no_link_path(path, leaf_file=True):
    """Reject symlink/reparse components without resolving to another root."""
    path = Path(path).absolute()
    for current in reversed((path, *path.parents)):
        info = current.lstat()
        assert not stat.S_ISLNK(info.st_mode), str(current)
        assert not getattr(info, 'st_file_attributes', 0) & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0), str(current)
        if current != path or not leaf_file:
            assert stat.S_ISDIR(info.st_mode), str(current)
    return path


def installed_path(root, relative):
    """Closed consumers use canonical POSIX relative paths under an explicit root."""
    assert type(relative) is str and relative and '\\' not in relative and '\x00' not in relative
    assert not relative.startswith('/') and all(part not in ('', '.', '..') for part in relative.split('/'))
    base = no_link_path(root, leaf_file=False)
    path = base.joinpath(*relative.split('/'))
    no_link_path(path)
    assert path.is_relative_to(base)
    return path


def SHA(raw):
    assert type(raw) is bytes
    return hashlib.sha256(raw).hexdigest()


def regular_bytes(path, maximum=16 * 1024 * 1024):
    """Read one independent regular input, reject symlinks and hardlinks."""
    assert type(maximum) is int and maximum >= 0
    path = no_link_path(path)
    before = path.lstat()
    assert stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and not path.is_symlink(), str(path)
    assert 0 <= before.st_size <= maximum
    raw = path.read_bytes()
    no_link_path(path)
    after = path.lstat()
    assert (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_mode, before.st_nlink) == (
        after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_mode, after.st_nlink), str(path)
    assert len(raw) == before.st_size
    return raw


def pinned_json(path, pin):
    raw = regular_bytes(path)
    assert SHA(raw) == pin, str(path)
    return json.loads(raw, object_pairs_hook=unique_object, parse_constant=reject_constant)


def fnv1a64(raw):
    assert type(raw) is bytes
    value = 0xcbf29ce484222325
    for byte in raw:
        value = ((value ^ byte) * 0x100000001b3) & 0xffffffffffffffff
    return value


def rgba_statistics(rgba, native_mask):
    """Inspect all10752 pixels, including native-alpha0 and outside support."""
    assert type(rgba) is bytes and len(rgba) == 43008
    assert type(native_mask) is str and len(native_mask) == 168 and set(native_mask) <= {'0', '1'}
    result = dict(nonzero=0, soft=0, opaque255=0, native_alpha0=0,
                  outside_nonzero=0, alpha0_rgb_nonzero=0,
                  native_cells=native_mask.count('1'), high_ge200=0, low_1_199=0, zero=0)
    maxima = [0] * 168
    for index in range(10752):
        r, g, b, a = rgba[4 * index:4 * index + 4]
        cell = (index // 96 // 8) * 12 + (index % 96) // 8
        maxima[cell] = max(maxima[cell], a)
        result['nonzero'] += a != 0
        result['soft'] += 0 < a < 255
        result['opaque255'] += a == 255
        result['native_alpha0'] += native_mask[cell] == '1' and a == 0
        result['outside_nonzero'] += native_mask[cell] == '0' and any((r, g, b, a))
        result['alpha0_rgb_nonzero'] += a == 0 and any((r, g, b))
    for cell, alpha in enumerate(maxima):
        if native_mask[cell] == '1':
            result['high_ge200' if alpha >= 200 else 'low_1_199' if alpha else 'zero'] += 1
    result['max_alpha_matrix'] = [maxima[y * 12:(y + 1) * 12] for y in range(14)]
    return result


def strict_stdout_lines(stdout):
    assert type(stdout) is bytes and stdout.endswith(b'\n') and b'\r' not in stdout
    text = stdout.decode('ascii', errors='strict')
    assert '\x00' not in text
    return text[:-1].split('\n')


def exact_equal(actual, expected):
    assert type(actual) is type(expected), (type(actual),type(expected))
    if type(expected) is dict:
        assert actual.keys() == expected.keys()
        for key in expected: exact_equal(actual[key],expected[key])
    elif type(expected) in (list,tuple):
        assert len(actual)==len(expected)
        for a,b in zip(actual,expected): exact_equal(a,b)
    else: assert actual==expected


def statics_helper(root):
    path=installed_path(root,'tests/projectile_statics_native_validation.py')
    raw=regular_bytes(path)
    assert SHA(raw)==STATICS_HELPER_SHA
    companion=regular_bytes(installed_path(root,'tests/projectile_statics_native_additions.c.inc'))
    assert SHA(companion)==STATICS_COMPANION_SHA
    result=types.ModuleType('frozen_statics_native_helpers');result.__file__=str(path)
    exec(compile(raw,str(path),'exec'),result.__dict__)
    return result


def outer_shim(raw):
    assert type(raw) is bytes and SHA(raw)==STATICS_WRAPPER_SHA
    assert raw.count(b'int main(')==1 and b'inherited_statics_dispatch' not in raw
    result=raw.replace(b'int main(',b'int inherited_statics_dispatch(',1)+TAIL
    assert reverse_shim(result)==raw
    return result


def reverse_shim(raw):
    assert type(raw) is bytes and raw.endswith(TAIL)
    body=raw[:-len(TAIL)]
    assert body.count(b'int inherited_statics_dispatch(')==1 and b'int main(' not in body
    result=body.replace(b'int inherited_statics_dispatch(',b'int main(',1)
    assert SHA(result)==STATICS_WRAPPER_SHA
    return result


def source_bundle(root):
    old=statics_helper(root);sources,statics=old.source_bundle(root)
    assert type(sources) is dict and set(sources)==set(SOURCE_PINS)
    for name,raw in sources.items():assert SHA(raw)==SOURCE_PINS[name]
    assert len(sources['harness.c'])==262
    capture_production_contract(root)
    derived=capture_wrapper(outer_shim(statics))
    assert old.gold_helper(root).reverse_shim(old.reverse_shim(reverse_shim(reverse_capture_wrapper(derived))))==sources['harness.c']
    return sources,derived


def native_inputs(root,data):
    old,new=statics_helper(root).native_inputs(root,data)
    assert SHA(old)=='7dedf7066696fc278f5fbb8dfb1462e7b6ac290cb5d08ae5260a6cdabc1ecca7'
    assert SHA(new)=='a9739298f031cafbfefb3befd359750872f6caafe69ebf5c7cf948544713830b'
    return old,new


def registered_rgba(selector, root):
    assert type(selector) is int and selector in PULSES
    import PIL
    from PIL import Image
    assert PIL.__version__=='12.3.0'
    raw=regular_bytes(installed_path(root,f'{ASSET_DIRECTORY}/projectile-pulses16694-{selector}-registered.png'),128*1024)
    assert SHA(raw)==PINS[selector]['png_sha256']
    with Image.open(io.BytesIO(raw)) as image:
        assert image.format=='PNG' and image.mode=='RGBA' and image.size==(96,112) and getattr(image,'n_frames',1)==1
        image.load();rgba=image.tobytes()
    assert SHA(rgba)==PINS[selector]['rgba_sha256']
    assert f'{fnv1a64(rgba):016x}'==PINS[selector]['fnv1a64']
    return rgba


def validate_hda(raw,selector):
    assert type(selector) is int and selector in PULSES
    assert type(raw) is bytes and len(raw)==43036
    assert raw[:28]==struct.pack('<4s6I',b'HDR1',1550000+selector,8,12,14,0,0)
    assert SHA(raw)==PINS[selector]['hda_sha256'] and SHA(raw[28:])==PINS[selector]['rgba_sha256']
    assert f'{fnv1a64(raw[28:]):016x}'==PINS[selector]['fnv1a64']
    return True


def hda_payload(selector,rgba):
    assert type(selector) is int and selector in PULSES
    assert type(rgba) is bytes and len(rgba)==43008 and SHA(rgba)==PINS[selector]['rgba_sha256']
    result=struct.pack('<4s6I',b'HDR1',1550000+selector,8,12,14,0,0)+rgba
    validate_hda(result,selector)
    return result


def registration(root):
    """Installed coverage and exact pixels only; no external receipt or fallback."""
    raw=regular_bytes(installed_path(root,COVERAGE_PATH),64*1024)
    assert SHA(raw)==COVERAGE_SHA
    coverage=json.loads(raw,object_pairs_hook=unique_object,parse_constant=reject_constant)
    exact_equal(coverage,COVERAGE_SPEC)
    members=[]
    for selector in PULSES:
        pin=PINS[selector];rgba=registered_rgba(selector,root);stats=rgba_statistics(rgba,pin['native_mask'])
        for key,value in stats.items():exact_equal(value,pin[key])
        assert max(rgba[3::4])==pin['max_alpha']
        hda=regular_bytes(installed_path(root,f'{ASSET_DIRECTORY}/{HDA_NAMES[selector]}'),43036)
        validate_hda(hda,selector);assert hda[28:]==rgba
        members.append(dict(pin,selector=selector,statistics=stats))
    return {'schema':'enemy-pulses16694-fixed-registration-v1','members':members,'coverage_sha256':SHA(raw),
        'scope':'Installed fixed registration/HDA contract only; no new native, gameplay, fresh or fullgate.'}


def registered_hdas(root):
    registration(root)
    result={}
    for selector in PULSES:
        raw=regular_bytes(installed_path(root,f'{ASSET_DIRECTORY}/{HDA_NAMES[selector]}'),43036)
        validate_hda(raw,selector);result[selector]=raw
    return result


def fixture_bytes(raw, selector, leaf):
    assert type(raw) is bytes and len(raw) == 43036
    assert type(selector) is int and selector in IDS and type(leaf) is str and leaf in PACK_NAMES
    if leaf == 'old-only' and selector in PULSES:
        return None
    if leaf.startswith('only') and selector != int(leaf[4:]):
        return None
    if leaf == 'missing' + str(selector):
        return None
    result = bytearray(raw)
    if leaf == 'bad' + str(selector):
        result[128] ^= 1
    if leaf == 'header' + str(selector):
        result[4] ^= 1
    if leaf == 'magic' + str(selector):
        result[0] ^= 1
    for field, offset, value in (('density', 8, 4), ('width', 12, 11), ('height', 16, 13),
                                 ('anchorx', 20, 1), ('anchory', 24, 1)):
        if leaf == field + str(selector):
            struct.pack_into('<I', result, offset, value)
    if leaf == 'short' + str(selector):
        result = result[:-1]
    if leaf == 'trailing' + str(selector):
        result += b'!'
    return bytes(result)

def fixture_schema():
    """Exact finite new pack membership, independent of payload production."""
    sentinel = bytes(43036)
    return {leaf: tuple(i for i in IDS if fixture_bytes(sentinel, i, leaf) is not None) for leaf in PACK_NAMES}


def validate_fixture_arguments(hdas,metadata):
    assert type(hdas) is dict and all(type(i) is int for i in hdas) and set(hdas)==set(IDS)
    assert all(type(raw) is bytes and len(raw)==43036 for raw in hdas.values())
    assert type(metadata) is dict and set(metadata)=={'schema','members','coverage_sha256','scope'}
    assert metadata['schema']=='enemy-pulses16694-fixed-registration-v1' and metadata['coverage_sha256']==COVERAGE_SHA
    assert type(metadata['members']) is list and len(metadata['members'])==2
    for i,row in zip(PULSES,metadata['members']):
        assert type(row) is dict and set(row)==set(PINS[i])|{'selector','statistics'}
        exact_equal(row['selector'],i)
        for key,value in PINS[i].items():exact_equal(row[key],value)
        validate_hda(hdas[i],i);exact_equal(row['statistics'],rgba_statistics(hdas[i][28:],PINS[i]['native_mask']))
    return True


def fixture_payloads(root,hdas,metadata):
    validate_fixture_arguments(hdas,metadata)
    old=statics_helper(root)
    result=old.fixture_payloads(root,{i:hdas[i] for i in old.IDS},old.registration(root))
    assert len(result)==725
    new={}
    for leaf in PACK_NAMES:
        for selector in IDS:
            raw=fixture_bytes(hdas[selector],selector,leaf)
            if raw is not None:new[f'pulses16694-packs/{leaf}/{HDA_NAMES[selector]}']=raw
    assert len(new)==516 and len(PACK_NAMES)==46 and not set(result)&set(new)
    result={**result,**new};assert len(result)==1241
    assert all(type(name) is str and not Path(name).is_absolute() and '..' not in Path(name).parts for name in result)
    return result


def verify_legacy_stdout(actual):
    assert type(actual) is dict and set(actual)==set(STDOUT_PINS)
    for name,raw in actual.items():
        pin,size=STDOUT_PINS[name]
        assert type(raw) is bytes and len(raw)==size and SHA(raw)==pin,('Original1329 stdout changed',name)
        strict_stdout_lines(raw)
    return {'cases':1329,'assertions':141598648,'process_cases':[107,157,365,251,449],
        'scope':'Five inherited byte-exact controlled native process contracts.'}


def expected_body_lines():
    """Only schema arithmetic; this is not a substitute for actual C stdout."""
    result=[]
    for name,count in GROUPS:
        if name=='Talon_transfer':
            for selector in PULSES:
                copied,soft,zero=TRANSFER[selector]
                for cached in (0,1):result.append(f'PULSES16694_TO_TALON selector={selector} copied={copied} soft={soft} alpha0={zero} cached={cached}')
        if name=='legacy_reject_own_foreign':
            for context in range(3):
                for selector in PULSES:
                    for mixed in (0,1):
                        kept=({166:3008,94:3409}[selector] if mixed else {166:6208,94:6912}[selector])
                        dropped={166:3200,94:3503}[selector] if mixed else 0
                        clears=17 if mixed and selector==94 else 0
                        result.append(f'PULSES16694_LEGACY context={context} selector={selector} mixed={mixed} kept={kept} dropped={dropped} opaque_clears={clears}')
        result.append(f'PULSES16694_GROUP name={name} cases={count}')
    return result


def parse_pulses_stdout(stdout):
    assert GROUPS and len(set(name for name,_ in GROUPS))==len(GROUPS)
    assert all(type(count) is int and count>0 for _,count in GROUPS)
    lines=strict_stdout_lines(stdout);body=expected_body_lines()
    assert len(lines)==len(body)+1 and lines[:-1]==body,'Exact ordered groups/transfer/legacy witnesses required'
    match=re.fullmatch(r'PASS enemy pulses16694 native lifecycle: ([1-9][0-9]*) cases ([1-9][0-9]*) assertions; internal8 only; not gameplay/full build',lines[-1])
    assert match and int(match[1])==sum(count for _,count in GROUPS)
    return {'cases':int(match[1]),'assertions':int(match[2]),'groups':[{'name':name,'cases':count} for name,count in GROUPS],
        'transfers':[s for s in body if s.startswith('PULSES16694_TO_TALON ')],
        'legacy_final':[s for s in body if s.startswith('PULSES16694_LEGACY ')],
        'scope':'Controlled internal8 production-TU, including INTERNAL guard-state fixture, not natural glyph/night/game/fresh/fullgate.'}


def capture_production_contract(root):
    """Bind actual current-root parser/gate files and complete definitions."""
    result={}
    for relative,row in CAPTURE_PRODUCTION_FILES.items():
        raw=regular_bytes(installed_path(root,relative))
        assert SHA(raw)==row['file_sha256']
        for marker,entry in row['functions'].items():
            body=entry['body'].encode()
            assert raw.count(body)==1 and SHA(body)==entry['sha256'] and body.startswith(marker.encode())
        result[relative]=SHA(raw)
    return result


def capture_wrapper(raw):
    assert type(raw) is bytes and SHA(raw)==ORIGINAL_WRAPPER_SHA and raw.count(CAPTURE_OLD)==1
    result=raw.replace(CAPTURE_OLD,CAPTURE_NEW,1)
    assert SHA(result)==CAPTURE_WRAPPER_SHA and reverse_capture_wrapper(result)==raw
    return result


def reverse_capture_wrapper(raw):
    assert type(raw) is bytes and SHA(raw)==CAPTURE_WRAPPER_SHA and raw.count(CAPTURE_NEW)==1
    result=raw.replace(CAPTURE_NEW,CAPTURE_OLD,1)
    assert SHA(result)==ORIGINAL_WRAPPER_SHA and len(result)==979
    return result


def production_palette_contract(root):
    source=regular_bytes(installed_path(root,'src/render_mirror.c'))
    match=re.search(rb'static bool normal15_palette\(void\)\n\{.*?\n\}',source,re.S)
    assert match is not None and match[0]==NORMAL15_PALETTE_FUNCTION
    assert b'0x5e80e83992be2927' in match[0]
    return SHA(match[0])


def fnv_rgb24(raw):
    assert type(raw) is bytes and len(raw)==768
    return fnv1a64(raw)


def checked_palette5_rgb(raw):
    assert type(raw) is bytes and len(raw)==768 and SHA(raw)==PALETTE5_RGB_SHA
    assert fnv_rgb24(raw)==PALETTE5_FNV
    return raw


def pulses_native_input(root,data,new_input):
    """Only the sixth process receives full palette5. Old two byte streams stay unchanged."""
    assert type(new_input) is bytes and len(new_input)==98980
    assert SHA(new_input)=='a9739298f031cafbfefb3befd359750872f6caafe69ebf5c7cf948544713830b'
    production_palette_contract(root)
    palette=regular_bytes(installed_path(data,'palette.dat'),18432)
    assert len(palette)==18432 and SHA(palette)==PALETTE_FILE_SHA
    source=palette[3840:4608]
    assert len(source)==768 and max(source)<64
    rgb=checked_palette5_rgb(bytes((v<<2)|(v>>4) for v in source))
    le=b''.join(int.from_bytes(rgb[i:i+3],'big').to_bytes(4,'little') for i in range(0,768,3))
    assert SHA(le)==PALETTE5_LE32_SHA and len(le)==1024
    assert bytes(v for i in range(0,1024,4) for v in int.from_bytes(le[i:i+4],'little').to_bytes(3,'big'))==rgb
    result=new_input[:32060]+le+new_input[33084:]
    assert len(result)==98980 and result[:32060]==new_input[:32060] and result[33084:]==new_input[33084:]
    assert SHA(result)==PULSES_STDIN_SHA
    return result,{'scope':'sixth process only; original five stdin unchanged','bytes':len(result),'sha256':SHA(result),
        'original_new_input_sha256':SHA(new_input),'palette_file_sha256':SHA(palette),'palette_source_byte_range':[3840,4608],
        'stdin_replacement_byte_range':[32060,33084],'palette_rgb24_sha256':SHA(rgb),'palette_le32_sha256':SHA(le),
        'production_fnv_rgb24':f'{fnv_rgb24(rgb):016x}','changed_bytes':sum(a!=b for a,b in zip(new_input,result)),
        'prefix_sha256':SHA(result[:32060]),'suffix_sha256':SHA(result[33084:])}


def verify_pulses_stdout(stdout):
    result=parse_pulses_stdout(stdout)
    assert (SHA(stdout),len(stdout))==PULSES_STDOUT_PIN
    assert result['cases']==578 and result['assertions']==143860156
    return result
