"""Finite WARNING face-only integration contracts; no original game bytes."""
from pathlib import Path
import hashlib,unittest,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import current_tank_muzzle_source_bridge as muzzle_bridge
import current_warning_source_bridge as warning_bridge
def digest(raw):return hashlib.sha256(raw.encode()if isinstance(raw,str)else raw).hexdigest()
BASE_PINS={'src/gameplay_hud_font_mirror.inc': 'f895ef13ae4e0bc8bb6cf1460ae93acf0c99c762560ee48dbb3d2fbf1725e044', 'src/render_mirror.c': '748929771f5626045966fb9d881c4ded3e3d94c1145ab68288ca3956a963b084', 'src/render_mirror.h': '8887258ab85aed28867b41eef28728a89a4759c786dfc3cf0f725eb9739d410e', 'src/tyrian2.c': '36b756eb60ccad63b76cf194fb9dc3f30dc5c536be07fc9aaa41c971ede48911', 'src/gameplay_hud_font.c': '02237476b400f8d7b78e5331000bff4d8cbb5d1f22108f907b388240c74f4221', 'src/gameplay_hud_font.h': 'e960503ca8b7a87e2083fe2f96fb54f06d1a53a2b7d1258ed88a84df93e5a29f', 'src/fonthand.c': '1d6c63d81e02538272a9225f70c26731c86a2048640a41e5857096cdeb03825e', 'src/mainint.c': '77e7104e907dd83c935f21cc03aaf887b19182f25a2735006c651ac52767a6c8', 'src/global_projectile91_mirror.inc': 'd9a8df1a9c4b1978ce82b645742030942623758c4d228475785a6bbae8e2330e'}
FONT_INVERSE=[(' int d=font_density;\n for(unsigned which=0;which<FONT_SCENE_COUNT;which++) {\n  FontScene *r=font_scenes+which;if(!r->output_live)continue;\n', ' int d=font_density;\n for(unsigned which=0;which<2;which++) {\n  FontScene *r=font_scenes+which;if(!r->output_live)continue;\n'), (' if(!font_history||!font_output_generation)return;\n for(unsigned i=0;i<FONT_SCENE_COUNT;i++){FontScene *r=font_scenes+i;if(!r->output_live)continue;\n  memcpy(font_saved_under+r->offset,font_under+r->offset,r->used*4);memcpy(font_saved_lower_owner+r->offset,font_lower_owner+r->offset,r->used);memcpy(font_saved_owner+r->offset,font_owner+r->offset,r->used);}\n', ' if(!font_history||!font_output_generation)return;\n for(unsigned i=0;i<2;i++){FontScene *r=font_scenes+i;if(!r->output_live)continue;\n  memcpy(font_saved_under+r->offset,font_under+r->offset,r->used*4);memcpy(font_saved_lower_owner+r->offset,font_lower_owner+r->offset,r->used);memcpy(font_saved_owner+r->offset,font_owner+r->offset,r->used);}\n'), (' bool retained=false;\n for(unsigned i=0;i<FONT_SCENE_COUNT;i++) {\n  FontScene *r=font_scenes+i;r->output_live=accepted&&r->canvas_live&&font_scene_owned(r,font_owner);r->canvas_live=false;\n', ' bool retained=false;\n for(unsigned i=0;i<2;i++) {\n  FontScene *r=font_scenes+i;r->output_live=accepted&&r->canvas_live&&font_scene_owned(r,font_owner);r->canvas_live=false;\n'), (' bool retained=false;\n for(unsigned i=0;i<FONT_SCENE_COUNT;i++) {\n  FontScene *r=font_scenes+i;if(!r->canvas_live)continue;\n', ' bool retained=false;\n for(unsigned i=0;i<2;i++) {\n  FontScene *r=font_scenes+i;if(!r->canvas_live)continue;\n'), (' int d=font_density;\n for(unsigned i=0;i<FONT_SCENE_COUNT;i++)if(font_shared_rejected&(1u<<i)) {\n  FontScene *r=font_scenes+i;\n', ' int d=font_density;\n for(unsigned i=0;i<2;i++)if(font_shared_rejected&(1u<<i)) {\n  FontScene *r=font_scenes+i;\n'), ('{\n for(unsigned i=0;i<FONT_SCENE_COUNT;i++) {\n  FontScene *r=font_scenes+i;\n', '{\n for(unsigned i=0;i<2;i++) {\n  FontScene *r=font_scenes+i;\n'), ('{\n if(font_history)for(unsigned i=0;i<FONT_SCENE_COUNT;i++)font_strip_scene(i);\n font_clear_cached(31);if(font_gameplay)font_suspended=true;\n}\n', '{\n if(font_history)for(unsigned i=0;i<2;i++)font_strip_scene(i);\n font_clear_cached(15);if(font_gameplay)font_suspended=true;\n}\n'), (' font_context=-1;font_glyph_active=false;font_output_generation=font_saved_generation=0;\n for(unsigned i=0;i<FONT_SCENE_COUNT;i++) {\n  FontScene *r=font_scenes+i;\n', ' font_context=-1;font_glyph_active=false;font_output_generation=font_saved_generation=0;\n for(unsigned i=0;i<2;i++) {\n  FontScene *r=font_scenes+i;\n'), ('{\n if(font_history)for(unsigned i=0;i<FONT_SCENE_COUNT;i++)font_strip_scene(i);\n font_clear_cached(31);font_gameplay=font_suspended=false;font_context=-1;font_glyph_active=false;\n ++font_generation;if(!font_generation)++font_generation;\n', '{\n if(font_history)for(unsigned i=0;i<2;i++)font_strip_scene(i);\n font_clear_cached(15);font_gameplay=font_suspended=false;font_context=-1;font_glyph_active=false;\n ++font_generation;if(!font_generation)++font_generation;\n'), (' if(x>=320||y>=200)return;\n for(unsigned i=0;i<FONT_SCENE_COUNT;i++) {\n  FontScene *r=font_scenes+i;\n', ' if(x>=320||y>=200)return;\n for(unsigned i=0;i<2;i++) {\n  FontScene *r=font_scenes+i;\n'), (' bool saved=memchr(font_psaved_owner,1,FONT_PERSIST_CELLS)!=NULL;\n for(unsigned i=0;i<FONT_SCENE_COUNT;i++)saved=saved||font_scene_owned(font_scenes+i,font_saved_owner);\n if(!saved)font_saved_generation=0;\n', ' bool saved=memchr(font_psaved_owner,1,FONT_PERSIST_CELLS)!=NULL;\n for(unsigned i=0;i<2;i++)saved=saved||font_scene_owned(font_scenes+i,font_saved_owner);\n if(!saved)font_saved_generation=0;\n'), (' if(!verified){ready=false;last_output_valid=false;have_fade_saved=false;fade_mode=0;}\n for(unsigned which=0;which<FONT_SCENE_COUNT;which++) {\n  FontScene *r=font_scenes+which;if(!(bits&(4u<<which))||!r->output_live)continue;\n', ' if(!verified){ready=false;last_output_valid=false;have_fade_saved=false;fade_mode=0;}\n for(unsigned which=0;which<2;which++) {\n  FontScene *r=font_scenes+which;if(!(bits&(4u<<which))||!r->output_live)continue;\n'), ("}\n/* bits1=level,2=message,4=cash,8=name,16=warning. Never remove another field's history. */\nstatic void font_clear_cached(unsigned bits)\n", "}\n/* bits1=level,2=message,4=cash,8=name. Never remove another field's history. */\nstatic void font_clear_cached(unsigned bits)\n"), (' if(have_fade_saved&&(font_saved_generation!=font_generation||memcmp(font_powner,font_psaved_owner,FONT_PERSIST_CELLS)))return false;\n for(unsigned i=0;i<FONT_SCENE_COUNT;i++)if(font_scenes[i].output_live) {\n  const FontScene *r=font_scenes+i;int d=font_density;\n', ' if(have_fade_saved&&(font_saved_generation!=font_generation||memcmp(font_powner,font_psaved_owner,FONT_PERSIST_CELLS)))return false;\n for(unsigned i=0;i<2;i++)if(font_scenes[i].output_live) {\n  const FontScene *r=font_scenes+i;int d=font_density;\n'), ('{\n return font_history&&(font_output_generation||font_saved_generation||font_scenes[0].output_live||font_scenes[1].output_live||font_scenes[2].output_live||\n  memchr(font_powner,1,FONT_PERSIST_CELLS)||memchr(font_psaved_owner,1,FONT_PERSIST_CELLS));\n', '{\n return font_history&&(font_output_generation||font_saved_generation||font_scenes[0].output_live||font_scenes[1].output_live||\n  memchr(font_powner,1,FONT_PERSIST_CELLS)||memchr(font_psaved_owner,1,FONT_PERSIST_CELLS));\n'), ('}\n/* Old full-shade callers retain their finite two-context contract. */\nvoid render_mirror_text_begin(SDL_Surface *surface,unsigned kind,int x,int y,const char *text,unsigned hue,int value)\n{\n if(kind>1){if(font_context>=0)font_strip_scene((unsigned)font_context);return;}\n font_scene_begin(surface,kind,x,y,text,hue,value,true);\n}\n/* Face-only observation of the original fixed WARNING call, never a draw. */\nvoid render_mirror_text_warning_begin(SDL_Surface *surface,int value)\n{font_scene_begin(surface,2,140,178,"WARNING",7,value,false);}\nvoid render_mirror_text_glyph_begin(SDL_Surface *surface,int x,int y,unsigned table,unsigned id,bool black,unsigned hue,int value)\n', '}\nvoid render_mirror_text_glyph_begin(SDL_Surface *surface,int x,int y,unsigned table,unsigned id,bool black,unsigned hue,int value)\n'), ('  box.w>(kind?141:101)||box.h>(kind?10:8))return;\n if(kind==2&&(box.x!=140||box.y!=178||box.w!=34||box.h!=6||font_command_count!=7))return;\n if(!font_allocate())return;\n', '  box.w>(kind?141:101)||box.h>(kind?10:8))return;\n if(!font_allocate())return;\n'), (' font_shared_rejected&=~(1u<<kind);\n SDL_Rect box;if(!font_plan(x,y,text,hue,value,kind==2?7:20,full,&box)||!box.w||box.x<24||box.y<0||box.x+box.w>288||box.y+box.h>184||\n  box.w>(kind?141:101)||box.h>(kind?10:8))return;\n', ' font_shared_rejected&=~(1u<<kind);\n SDL_Rect box;if(!font_plan(x,y,text,hue,value,20,true,&box)||!box.w||box.x<24||box.y<0||box.x+box.w>288||box.y+box.h>184||\n  box.w>(kind?141:101)||box.h>(kind?10:8))return;\n'), (' if((kind==0&&(x!=30||y!=175||hue!=2||value!=4))||(kind==1&&(x!=28||(y!=8&&y!=28)||hue!=2||value!=6)))return;\n if(kind==2&&(isNetworkGame||x!=140||y!=178||hue!=7||value<0||value>7||!text||strcmp(text,"WARNING")))return;\n if(kind==0)for(unsigned i=0;i<=20&&text&&text[i];i++)if(text[i]<\'0\'||text[i]>\'9\')return;\n', " if((kind==0&&(x!=30||y!=175||hue!=2||value!=4))||(kind==1&&(x!=28||(y!=8&&y!=28)||hue!=2||value!=6)))return;\n if(kind==0)for(unsigned i=0;i<=20&&text&&text[i];i++)if(text[i]<'0'||text[i]>'9')return;\n"), (' if(!font_gameplay||font_suspended||!hud_font_ready()||(!active&&!shared_hud_frame)||reject_reason||surface!=game_screen||suppress||\n  game_probe_original_reference||!font_source_matches()||!font_runtime_source()||!hud_font_palette_matches(rgb_palette)||full!=(kind!=2))return;\n if((kind==0&&(x!=30||y!=175||hue!=2||value!=4))||(kind==1&&(x!=28||(y!=8&&y!=28)||hue!=2||value!=6)))return;\n', ' if(!font_gameplay||font_suspended||!hud_font_ready()||(!active&&!shared_hud_frame)||reject_reason||surface!=game_screen||suppress||\n  game_probe_original_reference||!font_source_matches()||!font_runtime_source()||!hud_font_palette_matches(rgb_palette)||kind>1)return;\n if((kind==0&&(x!=30||y!=175||hue!=2||value!=4))||(kind==1&&(x!=28||(y!=8&&y!=28)||hue!=2||value!=6)))return;\n'), (' if(font_context>=0)font_strip_scene((unsigned)font_context);\n if(kind>=FONT_SCENE_COUNT)return;\n /* A rejected replacement must not leave the prior warning run visible. */\n if(kind==2&&font_scenes[2].canvas_live)font_strip_scene(2);\n if(!font_gameplay||font_suspended||!hud_font_ready()||(!active&&!shared_hud_frame)||reject_reason||surface!=game_screen||suppress||\n', ' if(font_context>=0)font_strip_scene((unsigned)font_context);\n if(!font_gameplay||font_suspended||!hud_font_ready()||(!active&&!shared_hud_frame)||reject_reason||surface!=game_screen||suppress||\n'), ('}\nstatic void font_scene_begin(SDL_Surface *surface,unsigned kind,int x,int y,const char *text,unsigned hue,int value,bool full)\n{\n', '}\nvoid render_mirror_text_begin(SDL_Surface *surface,unsigned kind,int x,int y,const char *text,unsigned hue,int value)\n{\n'), (' if(style!=MIRROR_NORMAL){font_before_effect((SDL_Rect){x,y,1,1});return false;}\n for(unsigned i=0;i<FONT_SCENE_COUNT;i++) {\n  FontScene *r=font_scenes+i;if(!r->canvas_live||x<r->rect.x||x>=r->rect.x+r->rect.w||y<r->rect.y||y>=r->rect.y+r->rect.h)continue;\n', ' if(style!=MIRROR_NORMAL){font_before_effect((SDL_Rect){x,y,1,1});return false;}\n for(unsigned i=0;i<2;i++) {\n  FontScene *r=font_scenes+i;if(!r->canvas_live||x<r->rect.x||x>=r->rect.x+r->rect.w||y<r->rect.y||y>=r->rect.y+r->rect.h)continue;\n'), (' if(!font_gameplay||!font_history)return;\n for(unsigned i=0;i<FONT_SCENE_COUNT;i++)if(font_scenes[i].canvas_live&&font_intersects(font_scenes[i].rect,footprint))font_strip_scene(i);\n}\n', ' if(!font_gameplay||!font_history)return;\n for(unsigned i=0;i<2;i++)if(font_scenes[i].canvas_live&&font_intersects(font_scenes[i].rect,footprint))font_strip_scene(i);\n}\n'), (' font_scenes[1].offset=808*64;font_scenes[1].logical_offset=808;\n font_scenes[2].offset=2218*64;font_scenes[2].logical_offset=2218;\n return true;\n', ' font_scenes[1].offset=808*64;font_scenes[1].logical_offset=808;\n return true;\n'), (' if(!font_history)return false;\n for(unsigned i=0;i<FONT_SCENE_COUNT;i++)if(font_scene_owned(font_scenes+i,font_owner))return true;\n return memchr(font_powner,1,FONT_PERSIST_CELLS)!=NULL;\n', ' if(!font_history)return false;\n for(unsigned i=0;i<2;i++)if(font_scene_owned(font_scenes+i,font_owner))return true;\n return memchr(font_powner,1,FONT_PERSIST_CELLS)!=NULL;\n'), ('typedef struct {bool valid,poison,seen,blank,inflight,expect_erase;char text[256];} FontPersistent;\nstatic FontScene font_scenes[FONT_SCENE_COUNT];\nstatic FontPersistent font_persistent[2];\n', 'typedef struct {bool valid,poison,seen,blank,inflight,expect_erase;char text[256];} FontPersistent;\nstatic FontScene font_scenes[2];\nstatic FontPersistent font_persistent[2];\n'), (' * Original font routines and indexed writes remain the source of authority. */\nenum { FONT_SCENE_COUNT=3,FONT_SCENE_CELLS=2422,FONT_PIXELS=FONT_SCENE_CELLS*64,FONT_PERSIST_CELLS=2208,\n FONT_HISTORY_BYTES=FONT_PIXELS*20+FONT_SCENE_CELLS+FONT_PERSIST_CELLS*4 };\n', ' * Original font routines and indexed writes remain the source of authority. */\nenum { FONT_SCENE_CELLS=2218,FONT_PIXELS=FONT_SCENE_CELLS*64,FONT_PERSIST_CELLS=2208,\n FONT_HISTORY_BYTES=FONT_PIXELS*20+FONT_SCENE_CELLS+FONT_PERSIST_CELLS*4 };\n')]
TANK_PROJECTILE_INVERSE=[('/* SPDX-License-Identifier: GPL-2.0-or-later\n'
  ' * Finite shared normal '
  'bank8/{91,145,61,101,120,139,168,169,162,260,166,94,7,45,153,154,155,70,20,21,105,106,124,125,112,113,226,227,244,146,147} '
  'enemy-shot owner; independent payloads.\n'
  ' * Included after decode_tile; no level/episode/map predicate grants this owner. */\n'
  'static bool global_projectile91_cached;\n'
  '/* Survives ownership transfer (for example to antialiased HUD glyphs). */\n'
  'static bool global_projectile91_contributed;\n'
  '/* Contribution provenance persists even after all pixels transfer to another\n'
  " * owner. Optional members never gate a different, unused member's admission. */\n"
  '#if UINT_MAX < 2147483647u\n'
  '#error "Shared projectile member mask requires at least 31 unsigned value bits"\n'
  '#endif\n'
  'static unsigned global_projectile91_used_members;\n'
  '/* Exact finite contributors whose canonical RGBA extends outside native cells:\n'
  ' * Vulcan70, Widget20/21, Sonic105/106/124/125 Protron227 and tank146/147 only. Not a generic '
  'spill grant. */\n'
  'static const unsigned '
  'global_projectile91_sparse_rgba_members=131072u|262144u|524288u|1048576u|2097152u|4194304u|8388608u|134217728u|536870912u|1073741824u;\n'
  'static const unsigned '
  'global_projectile91_widget_sonic_members=262144u|524288u|1048576u|2097152u|4194304u|8388608u;\n'
  'static unsigned global_projectile91_member(unsigned index)\n'
  '{return '
  'index==91?1u:index==145?2u:index==61?4u:index==101?8u:index==120?16u:index==139?32u:index==168?64u:index==169?128u:index==162?256u:index==260?512u:index==166?1024u:index==94?2048u:index==7?4096u:index==45?8192u:index==153?16384u:index==154?32768u:index==155?65536u:index==70?131072u:index==20?262144u:index==21?524288u:index==105?1048576u:index==106?2097152u:index==124?4194304u:index==125?8388608u:index==112?16777216u:index==113?33554432u:index==226?67108864u:index==227?134217728u:index==244?268435456u:index==146?536870912u:index==147?1073741824u:0u;}\n'
  'static Asset *global_projectile91_member_resource(unsigned index)\n'
  '{return '
  'tank_shared_member_index(index)?enemy_tank_shared_resource(global_asset_directory,index):orb_protron_member_index(index)?enemy_orb_protron_resource(global_asset_directory,index):widget_sonic_member_index(index)?enemy_widget_sonic_resource(global_asset_directory,index):index==70?enemy_vulcan70_resource(global_asset_directory):index==91?projectile91_resource(global_asset_directory):index==145?projectile145_resource(global_asset_directory):index==61?projectile61_resource(global_asset_directory):(index==168||index==169)?projectile_gold_pulse_resource(global_asset_directory,index):(index==162||index==260)?projectile_statics_resource(global_asset_directory,index):(index==166||index==94)?projectile_pulses16694_resource(global_asset_directory,index):(index==7||index==45)?projectile_bolts745_resource(global_asset_directory,index):(index==153||index==154||index==155)?projectile_animated153_resource(global_asset_directory,index):projectile_blue_triplet_resource(global_asset_directory,index);}\n'
  'static bool global_projectile91_member_palette(unsigned index)\n'
  '{return '
  'tank_shared_member_index(index)?enemy_tank_shared_palette_matches(index):orb_protron_member_index(index)?enemy_orb_protron_palette_matches(index):widget_sonic_member_index(index)?enemy_widget_sonic_palette_matches(index):index==70?enemy_vulcan70_palette_matches():index==91?projectile91_palette_matches():index==145?projectile145_palette_matches():index==61?projectile61_palette_matches():(index==168||index==169)?projectile_gold_pulse_palette_matches(index):(index==162||index==260)?projectile_statics_palette_matches(index):(index==166||index==94)?projectile_pulses16694_palette_matches(index):(index==7||index==45)?projectile_bolts745_palette_matches(index):(index==153||index==154||index==155)?projectile_animated153_palette_matches(index):projectile_blue_triplet_palette_matches(index);}\n'
  'static bool global_projectile91_member_source(Sprite2_array bank,unsigned index)\n'
  '{return '
  'tank_shared_member_index(index)?enemy_tank_shared_source(bank,index):orb_protron_member_index(index)?enemy_orb_protron_source(bank,index):widget_sonic_member_index(index)?enemy_widget_sonic_source(bank,index):index==70?enemy_vulcan70_source(bank,index):index==91?projectile91_source(bank,index):index==145?projectile145_source(bank,index):index==61?projectile61_source(bank,index):(index==168||index==169)?projectile_gold_pulse_source(bank,index):(index==162||index==260)?projectile_statics_source(bank,index):(index==166||index==94)?projectile_pulses16694_source(bank,index):(index==7||index==45)?projectile_bolts745_source(bank,index):(index==153||index==154||index==155)?projectile_animated153_source(bank,index):projectile_blue_triplet_source(bank,index);}\n'
  '\n'
  'static size_t global_projectile91_capacity;\n'
  'static Uint32 '
  'global_projectile91_output_palette[256],global_projectile91_underlay_palette[256];\n',
  '/* SPDX-License-Identifier: GPL-2.0-or-later\n'
  ' * Finite shared normal '
  'bank8/{91,145,61,101,120,139,168,169,162,260,166,94,7,45,153,154,155,70,20,21,105,106,124,125,112,113,226,227,244} '
  'enemy-shot owner; independent payloads.\n'
  ' * Included after decode_tile; no level/episode/map predicate grants this owner. */\n'
  'static bool global_projectile91_cached;\n'
  '/* Survives ownership transfer (for example to antialiased HUD glyphs). */\n'
  'static bool global_projectile91_contributed;\n'
  '/* Contribution provenance persists even after all pixels transfer to another\n'
  " * owner. Optional members never gate a different, unused member's admission. */\n"
  '#if UINT_MAX < 536870911u\n'
  '#error "Shared projectile member mask requires at least 29 unsigned value bits"\n'
  '#endif\n'
  'static unsigned global_projectile91_used_members;\n'
  '/* Exact finite contributors whose canonical RGBA extends outside native cells:\n'
  ' * Vulcan70, Widget20/21, Sonic105/106/124/125 and Protron227 only. Not a generic spill grant. '
  '*/\n'
  'static const unsigned '
  'global_projectile91_sparse_rgba_members=131072u|262144u|524288u|1048576u|2097152u|4194304u|8388608u|134217728u;\n'
  'static const unsigned '
  'global_projectile91_widget_sonic_members=262144u|524288u|1048576u|2097152u|4194304u|8388608u;\n'
  'static unsigned global_projectile91_member(unsigned index)\n'
  '{return '
  'index==91?1u:index==145?2u:index==61?4u:index==101?8u:index==120?16u:index==139?32u:index==168?64u:index==169?128u:index==162?256u:index==260?512u:index==166?1024u:index==94?2048u:index==7?4096u:index==45?8192u:index==153?16384u:index==154?32768u:index==155?65536u:index==70?131072u:index==20?262144u:index==21?524288u:index==105?1048576u:index==106?2097152u:index==124?4194304u:index==125?8388608u:index==112?16777216u:index==113?33554432u:index==226?67108864u:index==227?134217728u:index==244?268435456u:0u;}\n'
  'static Asset *global_projectile91_member_resource(unsigned index)\n'
  '{return '
  'orb_protron_member_index(index)?enemy_orb_protron_resource(global_asset_directory,index):widget_sonic_member_index(index)?enemy_widget_sonic_resource(global_asset_directory,index):index==70?enemy_vulcan70_resource(global_asset_directory):index==91?projectile91_resource(global_asset_directory):index==145?projectile145_resource(global_asset_directory):index==61?projectile61_resource(global_asset_directory):(index==168||index==169)?projectile_gold_pulse_resource(global_asset_directory,index):(index==162||index==260)?projectile_statics_resource(global_asset_directory,index):(index==166||index==94)?projectile_pulses16694_resource(global_asset_directory,index):(index==7||index==45)?projectile_bolts745_resource(global_asset_directory,index):(index==153||index==154||index==155)?projectile_animated153_resource(global_asset_directory,index):projectile_blue_triplet_resource(global_asset_directory,index);}\n'
  'static bool global_projectile91_member_palette(unsigned index)\n'
  '{return '
  'orb_protron_member_index(index)?enemy_orb_protron_palette_matches(index):widget_sonic_member_index(index)?enemy_widget_sonic_palette_matches(index):index==70?enemy_vulcan70_palette_matches():index==91?projectile91_palette_matches():index==145?projectile145_palette_matches():index==61?projectile61_palette_matches():(index==168||index==169)?projectile_gold_pulse_palette_matches(index):(index==162||index==260)?projectile_statics_palette_matches(index):(index==166||index==94)?projectile_pulses16694_palette_matches(index):(index==7||index==45)?projectile_bolts745_palette_matches(index):(index==153||index==154||index==155)?projectile_animated153_palette_matches(index):projectile_blue_triplet_palette_matches(index);}\n'
  'static bool global_projectile91_member_source(Sprite2_array bank,unsigned index)\n'
  '{return '
  'orb_protron_member_index(index)?enemy_orb_protron_source(bank,index):widget_sonic_member_index(index)?enemy_widget_sonic_source(bank,index):index==70?enemy_vulcan70_source(bank,index):index==91?projectile91_source(bank,index):index==145?projectile145_source(bank,index):index==61?projectile61_source(bank,index):(index==168||index==169)?projectile_gold_pulse_source(bank,index):(index==162||index==260)?projectile_statics_source(bank,index):(index==166||index==94)?projectile_pulses16694_source(bank,index):(index==7||index==45)?projectile_bolts745_source(bank,index):(index==153||index==154||index==155)?projectile_animated153_source(bank,index):projectile_blue_triplet_source(bank,index);}\n'
  '\n'
  'static size_t global_projectile91_capacity;\n'
  'static Uint32 '
  'global_projectile91_output_palette[256],global_projectile91_underlay_palette[256];\n'),
 ('        '
  '(!(global_projectile91_used_members&33554432u)||enemy_orb_protron_palette_matches(113))&&\n'
  '        '
  '(!(global_projectile91_used_members&67108864u)||enemy_orb_protron_palette_matches(226))&&\n'
  '        '
  '(!(global_projectile91_used_members&134217728u)||enemy_orb_protron_palette_matches(227))&&\n'
  '        '
  '(!(global_projectile91_used_members&268435456u)||enemy_orb_protron_palette_matches(244))&&\n'
  '        '
  '(!(global_projectile91_used_members&536870912u)||enemy_tank_shared_palette_matches(146))&&\n'
  '        '
  '(!(global_projectile91_used_members&1073741824u)||enemy_tank_shared_palette_matches(147));}\n'
  'static bool global_projectile91_underlay_matches(void)\n'
  '{\n'
  ' for(unsigned i=0;i<256;i++)if(global_projectile91_used_colors[i]&&\n',
  '        '
  '(!(global_projectile91_used_members&33554432u)||enemy_orb_protron_palette_matches(113))&&\n'
  '        '
  '(!(global_projectile91_used_members&67108864u)||enemy_orb_protron_palette_matches(226))&&\n'
  '        '
  '(!(global_projectile91_used_members&134217728u)||enemy_orb_protron_palette_matches(227))&&\n'
  '        '
  '(!(global_projectile91_used_members&268435456u)||enemy_orb_protron_palette_matches(244));}\n'
  'static bool global_projectile91_underlay_matches(void)\n'
  '{\n'
  ' for(unsigned i=0;i<256;i++)if(global_projectile91_used_colors[i]&&\n'),
 ('        '
  '(!(global_projectile91_used_members&33554432u)||(orb_protron_ordinary_allowed(113)&&enemy_orb_protron_resource(global_asset_directory,113)!=NULL))&&\n'
  '        '
  '(!(global_projectile91_used_members&67108864u)||(orb_protron_ordinary_allowed(226)&&enemy_orb_protron_resource(global_asset_directory,226)!=NULL))&&\n'
  '        '
  '(!(global_projectile91_used_members&134217728u)||(orb_protron_ordinary_allowed(227)&&enemy_orb_protron_resource(global_asset_directory,227)!=NULL))&&\n'
  '        '
  '(!(global_projectile91_used_members&268435456u)||(orb_protron_ordinary_allowed(244)&&enemy_orb_protron_resource(global_asset_directory,244)!=NULL))&&\n'
  '        '
  '(!(global_projectile91_used_members&536870912u)||(tank_shared_ordinary_allowed(146)&&enemy_tank_shared_resource(global_asset_directory,146)!=NULL))&&\n'
  '        '
  '(!(global_projectile91_used_members&1073741824u)||(tank_shared_ordinary_allowed(147)&&enemy_tank_shared_resource(global_asset_directory,147)!=NULL));}\n'
  'static bool global_projectile91_disjoint(const SDL_Surface *a,const SDL_Surface *b)\n'
  '{\n'
  ' uintptr_t x=(uintptr_t)a->pixels,y=(uintptr_t)b->pixels;\n',
  '        '
  '(!(global_projectile91_used_members&33554432u)||(orb_protron_ordinary_allowed(113)&&enemy_orb_protron_resource(global_asset_directory,113)!=NULL))&&\n'
  '        '
  '(!(global_projectile91_used_members&67108864u)||(orb_protron_ordinary_allowed(226)&&enemy_orb_protron_resource(global_asset_directory,226)!=NULL))&&\n'
  '        '
  '(!(global_projectile91_used_members&134217728u)||(orb_protron_ordinary_allowed(227)&&enemy_orb_protron_resource(global_asset_directory,227)!=NULL))&&\n'
  '        '
  '(!(global_projectile91_used_members&268435456u)||(orb_protron_ordinary_allowed(244)&&enemy_orb_protron_resource(global_asset_directory,244)!=NULL));}\n'
  'static bool global_projectile91_disjoint(const SDL_Surface *a,const SDL_Surface *b)\n'
  '{\n'
  ' uintptr_t x=(uintptr_t)a->pixels,y=(uintptr_t)b->pixels;\n'),
 ('static void global_projectile91_shutdown(void)\n'
  '{\n'
  ' global_projectile91_reset();\n'
  ' '
  'projectile91_shutdown();projectile145_shutdown();projectile61_shutdown();projectile_blue_triplet_shutdown();projectile_gold_pulse_shutdown();projectile_statics_shutdown();projectile_pulses16694_shutdown();projectile_bolts745_shutdown();projectile_animated153_shutdown();enemy_vulcan70_shutdown();enemy_widget_sonic_shutdown();enemy_orb_protron_shutdown();enemy_tank_shared_shutdown();\n'
  ' '
  'free(global_projectile91_owner);free(global_projectile91_foreign);global_projectile91_owner=global_projectile91_foreign=NULL;global_projectile91_capacity=0;\n'
  '}\n'
  'static void global_projectile91_frame_begin(void)\n',
  'static void global_projectile91_shutdown(void)\n'
  '{\n'
  ' global_projectile91_reset();\n'
  ' '
  'projectile91_shutdown();projectile145_shutdown();projectile61_shutdown();projectile_blue_triplet_shutdown();projectile_gold_pulse_shutdown();projectile_statics_shutdown();projectile_pulses16694_shutdown();projectile_bolts745_shutdown();projectile_animated153_shutdown();enemy_vulcan70_shutdown();enemy_widget_sonic_shutdown();enemy_orb_protron_shutdown();\n'
  ' '
  'free(global_projectile91_owner);free(global_projectile91_foreign);global_projectile91_owner=global_projectile91_foreign=NULL;global_projectile91_capacity=0;\n'
  '}\n'
  'static void global_projectile91_frame_begin(void)\n')]
def restore_font(raw):
 for current,prior in FONT_INVERSE:
  if raw.count(current)!=1:raise ValueError('Changed finite WARNING hunk')
  raw=raw.replace(current,prior,1)
 if digest(raw)!=BASE_PINS['src/gameplay_hud_font_mirror.inc']:raise ValueError('Unrelated font code changed')
 return raw
def one(raw,a,b):
 if raw.count(a)!=1:raise ValueError('Changed exact WARNING insertion')
 return raw.replace(a,b,1)
def body(raw,name):
 at=raw.index(name+'(');start=raw.index('{',at);depth=1;end=start+1
 while depth:
  depth+=(raw[end]=='{')-(raw[end]=='}');end+=1
 return raw[start:end]
class WarningPreparation(unittest.TestCase):
 def src(self,n):return(ROOT/'src'/n).read_text()
 def test_scene_capacity_and_independent_offsets(self):
  s=self.src('gameplay_hud_font_mirror.inc');self.assertIn('FONT_SCENE_COUNT=3,FONT_SCENE_CELLS=2422',s);self.assertIn('font_scenes[2].offset=2218*64;font_scenes[2].logical_offset=2218;',s);self.assertIn('FontPersistent font_persistent[2]',s);self.assertEqual((2422-2218)*(64*20+1),261324)
 def test_full_font_inverse_preserves_old_contract(self):restore_font(self.src('gameplay_hud_font_mirror.inc'))
 def test_inverse_rejects_unrelated_or_missing_duplicate_hunks(self):
  s=self.src('gameplay_hud_font_mirror.inc');a,b=FONT_INVERSE[0]
  for bad in (s+'\n/*unrelated*/',s.replace(a,'',1),s+a):
   with self.assertRaises(ValueError):restore_font(bad)
 def test_scene_lifecycle_and_persistent_loop_separation(self):
  s=self.src('gameplay_hud_font_mirror.inc');self.assertEqual(s.count('font_clear_cached(31)'),2);self.assertNotIn('font_clear_cached(15)',s)
  for line in s.splitlines():
   if 'i<2;' in line:self.assertTrue('font_copy_indices' in line or 'font_compose_persistent' in line,line)
   if 'which<2' in line:self.assertIn('bits&(1u<<which)',line)
  self.assertIn('font_scenes[2].output_live',body(s,'font_cached'))
 def test_fixed_wrapper_and_old_generic_kind_boundary(self):
  s=self.src('gameplay_hud_font_mirror.inc');self.assertIn('font_scene_begin(surface,2,140,178,"WARNING",7,value,false);',body(s,'render_mirror_text_warning_begin'));self.assertIn('if(kind>1)',body(s,'render_mirror_text_begin'));self.assertIn('font_scene_begin(surface,kind,x,y,text,hue,value,true);',body(s,'render_mirror_text_begin'))
 def test_precise_face_only_admission(self):
  b=body(self.src('gameplay_hud_font_mirror.inc'),'font_scene_begin')
  for part in ('kind>=FONT_SCENE_COUNT','full!=(kind!=2)','isNetworkGame||x!=140||y!=178||hue!=7||value<0||value>7','strcmp(text,"WARNING")','kind==2?7:20,full','box.x!=140||box.y!=178||box.w!=34||box.h!=6||font_command_count!=7','box.y+box.h>184'):self.assertIn(part,b)
 def test_rejected_replacement_retires_old_warning_first(self):
  b=body(self.src('gameplay_hud_font_mirror.inc'),'font_scene_begin');self.assertLess(b.index('font_strip_scene(2)'),b.index('!font_gameplay'));self.assertLess(b.index('kind>=FONT_SCENE_COUNT'),b.index('font_scenes[2]'))
 def test_original_plan_alpha_blend_and_pixel_observer_unchanged(self):
  s=self.src('gameplay_hud_font_mirror.inc');old=restore_font(s)
  for n in ('font_plan','font_blend','render_mirror_text_glyph_begin','render_mirror_text_glyph_end','render_mirror_text_end'):self.assertEqual(body(s,n),body(old,n))
 def test_original_warning_call_bars_and_gameplay_unchanged(self):
  s=self.src('tyrian2.c');s=one(s,'\t\t\trender_mirror_text_warning_begin(VGAScreen, (warningCol % 16) / 2);\n','');anchor='\t\t\tJE_outText(VGAScreen, 140, 178, "WARNING", 7, (warningCol % 16) / 2);';s=one(s,anchor+'\n\t\t\trender_mirror_text_end();',anchor);s=muzzle_bridge.restore('src/tyrian2.c',s);self.assertEqual(digest(s),BASE_PINS['src/tyrian2.c'])
 def test_renderer_only_scene_loop_and_all_scene_mask(self):
  s=self.src('render_mirror.c');s=one(s,'if(font_history)for(unsigned i=0;i<FONT_SCENE_COUNT;i++)','if(font_history)for(unsigned i=0;i<2;i++)');self.assertEqual(s.count('font_clear_cached(31)'),3);s=s.replace('font_clear_cached(31)','font_clear_cached(15)');s=muzzle_bridge.restore('src/render_mirror.c',s);from tank_shell_native_validation import reverse_tank_render;s=reverse_tank_render(s);self.assertEqual(digest(s),BASE_PINS['src/render_mirror.c'])
 def test_header_feature_off_and_only_new_declaration(self):
  s=self.src('render_mirror.h');s=one(s,'#define render_mirror_text_warning_begin(...) ((void)0)\n','');s=one(s,'void render_mirror_text_warning_begin(SDL_Surface *,int value);\n','');s=muzzle_bridge.restore('src/render_mirror.h',s);self.assertEqual(digest(s),BASE_PINS['src/render_mirror.h'])
 def test_font_payload_loader_original_draw_and_projectiles_unchanged(self):
  for n in ('src/gameplay_hud_font.c','src/gameplay_hud_font.h','src/fonthand.c','src/mainint.c','src/global_projectile91_mirror.inc'):
   raw=(ROOT/n).read_bytes()
   if n=='src/global_projectile91_mirror.inc':
    text=muzzle_bridge.restore(n,raw.decode('utf-8'))
    for current,prior in TANK_PROJECTILE_INVERSE:text=one(text,current,prior)
    raw=text.encode('utf-8')
   self.assertEqual(digest(raw),BASE_PINS[n],n)
  self.assertEqual(digest((ROOT/'assets/hd/shared-ui-v1/gameplay-hud-font-v1.hda').read_bytes()),'3c328c1537cf1e09529ae8805e98a8deb57a859ea80ba269cfea0b55cfae539e')
if __name__=='__main__':unittest.main()
