"""Finite combined WARNING+muzzle production projection; never a fallback.
All constants are reproducible from public source bytes, no Git/private inputs.
WARNING four exact inverses restore the muzzle epoch before its existing inverse.
"""
import hashlib,json
def sha(raw):return hashlib.sha256(raw).hexdigest()
def inventory_digest(value):return sha(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode('utf-8'))
COMBINED_PINS={'src/gameplay_hud_font_mirror.inc': '305007e37553f7501da5ef600790732867fc0d3f440dc6a6f8621f6a8fa8687a', 'src/render_mirror.c': '225d755785776469e426c5362b5c2c6d9e2156536263764794dbcfd46dc18abd', 'src/render_mirror.h': '634f252aa56d3c238e563996ec59c1e239626a27f48362e6e3a03254db197bee', 'src/tyrian2.c': 'b6548eda2c7059440cd54adf170f85d021ca2ecefc36e60183dfbe76586728ab'}
MUZZLE_PINS={'src/gameplay_hud_font_mirror.inc': 'f895ef13ae4e0bc8bb6cf1460ae93acf0c99c762560ee48dbb3d2fbf1725e044', 'src/render_mirror.c': '0959d084a18c11c92f28c316342ae9fc85bf4f805ba93f497ea14b2ae5614392', 'src/render_mirror.h': '8bc9c0c5d9af697d2453f3aae5ca2dabbbe05dca06fe136244419bb37358bca6', 'src/tyrian2.c': 'b922abdb25f1441322f614d32e1ea6c9354e93c29cec532509763f6347aff4fd'}
COMBINED_SOURCE_DIGEST='d25f72a41559656771d0ebf29439eb8e232cc799a70ecd65e44ebfb57f1e3384'
MUZZLE_SOURCE_DIGEST='6f1954d8b4fdd7fb9bd0cbb510b07a68fe2465583473543a06dd4a0849106ca7'
INVERSE={'src/gameplay_hud_font_mirror.inc': [(' int d=font_density;\n'
                                       ' for(unsigned which=0;which<FONT_SCENE_COUNT;which++) {\n'
                                       '  FontScene '
                                       '*r=font_scenes+which;if(!r->output_live)continue;\n',
                                       ' int d=font_density;\n'
                                       ' for(unsigned which=0;which<2;which++) {\n'
                                       '  FontScene '
                                       '*r=font_scenes+which;if(!r->output_live)continue;\n'),
                                      (' if(!font_history||!font_output_generation)return;\n'
                                       ' for(unsigned i=0;i<FONT_SCENE_COUNT;i++){FontScene '
                                       '*r=font_scenes+i;if(!r->output_live)continue;\n'
                                       '  '
                                       'memcpy(font_saved_under+r->offset,font_under+r->offset,r->used*4);memcpy(font_saved_lower_owner+r->offset,font_lower_owner+r->offset,r->used);memcpy(font_saved_owner+r->offset,font_owner+r->offset,r->used);}\n',
                                       ' if(!font_history||!font_output_generation)return;\n'
                                       ' for(unsigned i=0;i<2;i++){FontScene '
                                       '*r=font_scenes+i;if(!r->output_live)continue;\n'
                                       '  '
                                       'memcpy(font_saved_under+r->offset,font_under+r->offset,r->used*4);memcpy(font_saved_lower_owner+r->offset,font_lower_owner+r->offset,r->used);memcpy(font_saved_owner+r->offset,font_owner+r->offset,r->used);}\n'),
                                      (' bool retained=false;\n'
                                       ' for(unsigned i=0;i<FONT_SCENE_COUNT;i++) {\n'
                                       '  FontScene '
                                       '*r=font_scenes+i;r->output_live=accepted&&r->canvas_live&&font_scene_owned(r,font_owner);r->canvas_live=false;\n',
                                       ' bool retained=false;\n'
                                       ' for(unsigned i=0;i<2;i++) {\n'
                                       '  FontScene '
                                       '*r=font_scenes+i;r->output_live=accepted&&r->canvas_live&&font_scene_owned(r,font_owner);r->canvas_live=false;\n'),
                                      (' bool retained=false;\n'
                                       ' for(unsigned i=0;i<FONT_SCENE_COUNT;i++) {\n'
                                       '  FontScene '
                                       '*r=font_scenes+i;if(!r->canvas_live)continue;\n',
                                       ' bool retained=false;\n'
                                       ' for(unsigned i=0;i<2;i++) {\n'
                                       '  FontScene '
                                       '*r=font_scenes+i;if(!r->canvas_live)continue;\n'),
                                      (' int d=font_density;\n'
                                       ' for(unsigned '
                                       'i=0;i<FONT_SCENE_COUNT;i++)if(font_shared_rejected&(1u<<i)) '
                                       '{\n'
                                       '  FontScene *r=font_scenes+i;\n',
                                       ' int d=font_density;\n'
                                       ' for(unsigned i=0;i<2;i++)if(font_shared_rejected&(1u<<i)) '
                                       '{\n'
                                       '  FontScene *r=font_scenes+i;\n'),
                                      ('{\n'
                                       ' for(unsigned i=0;i<FONT_SCENE_COUNT;i++) {\n'
                                       '  FontScene *r=font_scenes+i;\n',
                                       '{\n'
                                       ' for(unsigned i=0;i<2;i++) {\n'
                                       '  FontScene *r=font_scenes+i;\n'),
                                      ('{\n'
                                       ' if(font_history)for(unsigned '
                                       'i=0;i<FONT_SCENE_COUNT;i++)font_strip_scene(i);\n'
                                       ' '
                                       'font_clear_cached(31);if(font_gameplay)font_suspended=true;\n'
                                       '}\n',
                                       '{\n'
                                       ' if(font_history)for(unsigned '
                                       'i=0;i<2;i++)font_strip_scene(i);\n'
                                       ' '
                                       'font_clear_cached(15);if(font_gameplay)font_suspended=true;\n'
                                       '}\n'),
                                      (' '
                                       'font_context=-1;font_glyph_active=false;font_output_generation=font_saved_generation=0;\n'
                                       ' for(unsigned i=0;i<FONT_SCENE_COUNT;i++) {\n'
                                       '  FontScene *r=font_scenes+i;\n',
                                       ' '
                                       'font_context=-1;font_glyph_active=false;font_output_generation=font_saved_generation=0;\n'
                                       ' for(unsigned i=0;i<2;i++) {\n'
                                       '  FontScene *r=font_scenes+i;\n'),
                                      ('{\n'
                                       ' if(font_history)for(unsigned '
                                       'i=0;i<FONT_SCENE_COUNT;i++)font_strip_scene(i);\n'
                                       ' '
                                       'font_clear_cached(31);font_gameplay=font_suspended=false;font_context=-1;font_glyph_active=false;\n'
                                       ' '
                                       '++font_generation;if(!font_generation)++font_generation;\n',
                                       '{\n'
                                       ' if(font_history)for(unsigned '
                                       'i=0;i<2;i++)font_strip_scene(i);\n'
                                       ' '
                                       'font_clear_cached(15);font_gameplay=font_suspended=false;font_context=-1;font_glyph_active=false;\n'
                                       ' '
                                       '++font_generation;if(!font_generation)++font_generation;\n'),
                                      (' if(x>=320||y>=200)return;\n'
                                       ' for(unsigned i=0;i<FONT_SCENE_COUNT;i++) {\n'
                                       '  FontScene *r=font_scenes+i;\n',
                                       ' if(x>=320||y>=200)return;\n'
                                       ' for(unsigned i=0;i<2;i++) {\n'
                                       '  FontScene *r=font_scenes+i;\n'),
                                      (' bool '
                                       'saved=memchr(font_psaved_owner,1,FONT_PERSIST_CELLS)!=NULL;\n'
                                       ' for(unsigned '
                                       'i=0;i<FONT_SCENE_COUNT;i++)saved=saved||font_scene_owned(font_scenes+i,font_saved_owner);\n'
                                       ' if(!saved)font_saved_generation=0;\n',
                                       ' bool '
                                       'saved=memchr(font_psaved_owner,1,FONT_PERSIST_CELLS)!=NULL;\n'
                                       ' for(unsigned '
                                       'i=0;i<2;i++)saved=saved||font_scene_owned(font_scenes+i,font_saved_owner);\n'
                                       ' if(!saved)font_saved_generation=0;\n'),
                                      (' '
                                       'if(!verified){ready=false;last_output_valid=false;have_fade_saved=false;fade_mode=0;}\n'
                                       ' for(unsigned which=0;which<FONT_SCENE_COUNT;which++) {\n'
                                       '  FontScene '
                                       '*r=font_scenes+which;if(!(bits&(4u<<which))||!r->output_live)continue;\n',
                                       ' '
                                       'if(!verified){ready=false;last_output_valid=false;have_fade_saved=false;fade_mode=0;}\n'
                                       ' for(unsigned which=0;which<2;which++) {\n'
                                       '  FontScene '
                                       '*r=font_scenes+which;if(!(bits&(4u<<which))||!r->output_live)continue;\n'),
                                      ('}\n'
                                       '/* bits1=level,2=message,4=cash,8=name,16=warning. Never '
                                       "remove another field's history. */\n"
                                       'static void font_clear_cached(unsigned bits)\n',
                                       '}\n'
                                       '/* bits1=level,2=message,4=cash,8=name. Never remove '
                                       "another field's history. */\n"
                                       'static void font_clear_cached(unsigned bits)\n'),
                                      (' '
                                       'if(have_fade_saved&&(font_saved_generation!=font_generation||memcmp(font_powner,font_psaved_owner,FONT_PERSIST_CELLS)))return '
                                       'false;\n'
                                       ' for(unsigned '
                                       'i=0;i<FONT_SCENE_COUNT;i++)if(font_scenes[i].output_live) '
                                       '{\n'
                                       '  const FontScene *r=font_scenes+i;int d=font_density;\n',
                                       ' '
                                       'if(have_fade_saved&&(font_saved_generation!=font_generation||memcmp(font_powner,font_psaved_owner,FONT_PERSIST_CELLS)))return '
                                       'false;\n'
                                       ' for(unsigned i=0;i<2;i++)if(font_scenes[i].output_live) '
                                       '{\n'
                                       '  const FontScene *r=font_scenes+i;int d=font_density;\n'),
                                      ('{\n'
                                       ' return '
                                       'font_history&&(font_output_generation||font_saved_generation||font_scenes[0].output_live||font_scenes[1].output_live||font_scenes[2].output_live||\n'
                                       '  '
                                       'memchr(font_powner,1,FONT_PERSIST_CELLS)||memchr(font_psaved_owner,1,FONT_PERSIST_CELLS));\n',
                                       '{\n'
                                       ' return '
                                       'font_history&&(font_output_generation||font_saved_generation||font_scenes[0].output_live||font_scenes[1].output_live||\n'
                                       '  '
                                       'memchr(font_powner,1,FONT_PERSIST_CELLS)||memchr(font_psaved_owner,1,FONT_PERSIST_CELLS));\n'),
                                      ('}\n'
                                       '/* Old full-shade callers retain their finite two-context '
                                       'contract. */\n'
                                       'void render_mirror_text_begin(SDL_Surface '
                                       '*surface,unsigned kind,int x,int y,const char '
                                       '*text,unsigned hue,int value)\n'
                                       '{\n'
                                       ' '
                                       'if(kind>1){if(font_context>=0)font_strip_scene((unsigned)font_context);return;}\n'
                                       ' font_scene_begin(surface,kind,x,y,text,hue,value,true);\n'
                                       '}\n'
                                       '/* Face-only observation of the original fixed WARNING '
                                       'call, never a draw. */\n'
                                       'void render_mirror_text_warning_begin(SDL_Surface '
                                       '*surface,int value)\n'
                                       '{font_scene_begin(surface,2,140,178,"WARNING",7,value,false);}\n'
                                       'void render_mirror_text_glyph_begin(SDL_Surface '
                                       '*surface,int x,int y,unsigned table,unsigned id,bool '
                                       'black,unsigned hue,int value)\n',
                                       '}\n'
                                       'void render_mirror_text_glyph_begin(SDL_Surface '
                                       '*surface,int x,int y,unsigned table,unsigned id,bool '
                                       'black,unsigned hue,int value)\n'),
                                      ('  box.w>(kind?141:101)||box.h>(kind?10:8))return;\n'
                                       ' '
                                       'if(kind==2&&(box.x!=140||box.y!=178||box.w!=34||box.h!=6||font_command_count!=7))return;\n'
                                       ' if(!font_allocate())return;\n',
                                       '  box.w>(kind?141:101)||box.h>(kind?10:8))return;\n'
                                       ' if(!font_allocate())return;\n'),
                                      (' font_shared_rejected&=~(1u<<kind);\n'
                                       ' SDL_Rect '
                                       'box;if(!font_plan(x,y,text,hue,value,kind==2?7:20,full,&box)||!box.w||box.x<24||box.y<0||box.x+box.w>288||box.y+box.h>184||\n'
                                       '  box.w>(kind?141:101)||box.h>(kind?10:8))return;\n',
                                       ' font_shared_rejected&=~(1u<<kind);\n'
                                       ' SDL_Rect '
                                       'box;if(!font_plan(x,y,text,hue,value,20,true,&box)||!box.w||box.x<24||box.y<0||box.x+box.w>288||box.y+box.h>184||\n'
                                       '  box.w>(kind?141:101)||box.h>(kind?10:8))return;\n'),
                                      (' '
                                       'if((kind==0&&(x!=30||y!=175||hue!=2||value!=4))||(kind==1&&(x!=28||(y!=8&&y!=28)||hue!=2||value!=6)))return;\n'
                                       ' '
                                       'if(kind==2&&(isNetworkGame||x!=140||y!=178||hue!=7||value<0||value>7||!text||strcmp(text,"WARNING")))return;\n'
                                       ' if(kind==0)for(unsigned '
                                       "i=0;i<=20&&text&&text[i];i++)if(text[i]<'0'||text[i]>'9')return;\n",
                                       ' '
                                       'if((kind==0&&(x!=30||y!=175||hue!=2||value!=4))||(kind==1&&(x!=28||(y!=8&&y!=28)||hue!=2||value!=6)))return;\n'
                                       ' if(kind==0)for(unsigned '
                                       "i=0;i<=20&&text&&text[i];i++)if(text[i]<'0'||text[i]>'9')return;\n"),
                                      (' '
                                       'if(!font_gameplay||font_suspended||!hud_font_ready()||(!active&&!shared_hud_frame)||reject_reason||surface!=game_screen||suppress||\n'
                                       '  '
                                       'game_probe_original_reference||!font_source_matches()||!font_runtime_source()||!hud_font_palette_matches(rgb_palette)||full!=(kind!=2))return;\n'
                                       ' '
                                       'if((kind==0&&(x!=30||y!=175||hue!=2||value!=4))||(kind==1&&(x!=28||(y!=8&&y!=28)||hue!=2||value!=6)))return;\n',
                                       ' '
                                       'if(!font_gameplay||font_suspended||!hud_font_ready()||(!active&&!shared_hud_frame)||reject_reason||surface!=game_screen||suppress||\n'
                                       '  '
                                       'game_probe_original_reference||!font_source_matches()||!font_runtime_source()||!hud_font_palette_matches(rgb_palette)||kind>1)return;\n'
                                       ' '
                                       'if((kind==0&&(x!=30||y!=175||hue!=2||value!=4))||(kind==1&&(x!=28||(y!=8&&y!=28)||hue!=2||value!=6)))return;\n'),
                                      (' '
                                       'if(font_context>=0)font_strip_scene((unsigned)font_context);\n'
                                       ' if(kind>=FONT_SCENE_COUNT)return;\n'
                                       ' /* A rejected replacement must not leave the prior '
                                       'warning run visible. */\n'
                                       ' '
                                       'if(kind==2&&font_scenes[2].canvas_live)font_strip_scene(2);\n'
                                       ' '
                                       'if(!font_gameplay||font_suspended||!hud_font_ready()||(!active&&!shared_hud_frame)||reject_reason||surface!=game_screen||suppress||\n',
                                       ' '
                                       'if(font_context>=0)font_strip_scene((unsigned)font_context);\n'
                                       ' '
                                       'if(!font_gameplay||font_suspended||!hud_font_ready()||(!active&&!shared_hud_frame)||reject_reason||surface!=game_screen||suppress||\n'),
                                      ('}\n'
                                       'static void font_scene_begin(SDL_Surface *surface,unsigned '
                                       'kind,int x,int y,const char *text,unsigned hue,int '
                                       'value,bool full)\n'
                                       '{\n',
                                       '}\n'
                                       'void render_mirror_text_begin(SDL_Surface '
                                       '*surface,unsigned kind,int x,int y,const char '
                                       '*text,unsigned hue,int value)\n'
                                       '{\n'),
                                      (' '
                                       'if(style!=MIRROR_NORMAL){font_before_effect((SDL_Rect){x,y,1,1});return '
                                       'false;}\n'
                                       ' for(unsigned i=0;i<FONT_SCENE_COUNT;i++) {\n'
                                       '  FontScene '
                                       '*r=font_scenes+i;if(!r->canvas_live||x<r->rect.x||x>=r->rect.x+r->rect.w||y<r->rect.y||y>=r->rect.y+r->rect.h)continue;\n',
                                       ' '
                                       'if(style!=MIRROR_NORMAL){font_before_effect((SDL_Rect){x,y,1,1});return '
                                       'false;}\n'
                                       ' for(unsigned i=0;i<2;i++) {\n'
                                       '  FontScene '
                                       '*r=font_scenes+i;if(!r->canvas_live||x<r->rect.x||x>=r->rect.x+r->rect.w||y<r->rect.y||y>=r->rect.y+r->rect.h)continue;\n'),
                                      (' if(!font_gameplay||!font_history)return;\n'
                                       ' for(unsigned '
                                       'i=0;i<FONT_SCENE_COUNT;i++)if(font_scenes[i].canvas_live&&font_intersects(font_scenes[i].rect,footprint))font_strip_scene(i);\n'
                                       '}\n',
                                       ' if(!font_gameplay||!font_history)return;\n'
                                       ' for(unsigned '
                                       'i=0;i<2;i++)if(font_scenes[i].canvas_live&&font_intersects(font_scenes[i].rect,footprint))font_strip_scene(i);\n'
                                       '}\n'),
                                      (' '
                                       'font_scenes[1].offset=808*64;font_scenes[1].logical_offset=808;\n'
                                       ' '
                                       'font_scenes[2].offset=2218*64;font_scenes[2].logical_offset=2218;\n'
                                       ' return true;\n',
                                       ' '
                                       'font_scenes[1].offset=808*64;font_scenes[1].logical_offset=808;\n'
                                       ' return true;\n'),
                                      (' if(!font_history)return false;\n'
                                       ' for(unsigned '
                                       'i=0;i<FONT_SCENE_COUNT;i++)if(font_scene_owned(font_scenes+i,font_owner))return '
                                       'true;\n'
                                       ' return memchr(font_powner,1,FONT_PERSIST_CELLS)!=NULL;\n',
                                       ' if(!font_history)return false;\n'
                                       ' for(unsigned '
                                       'i=0;i<2;i++)if(font_scene_owned(font_scenes+i,font_owner))return '
                                       'true;\n'
                                       ' return memchr(font_powner,1,FONT_PERSIST_CELLS)!=NULL;\n'),
                                      ('typedef struct {bool '
                                       'valid,poison,seen,blank,inflight,expect_erase;char '
                                       'text[256];} FontPersistent;\n'
                                       'static FontScene font_scenes[FONT_SCENE_COUNT];\n'
                                       'static FontPersistent font_persistent[2];\n',
                                       'typedef struct {bool '
                                       'valid,poison,seen,blank,inflight,expect_erase;char '
                                       'text[256];} FontPersistent;\n'
                                       'static FontScene font_scenes[2];\n'
                                       'static FontPersistent font_persistent[2];\n'),
                                      (' * Original font routines and indexed writes remain the '
                                       'source of authority. */\n'
                                       'enum { '
                                       'FONT_SCENE_COUNT=3,FONT_SCENE_CELLS=2422,FONT_PIXELS=FONT_SCENE_CELLS*64,FONT_PERSIST_CELLS=2208,\n'
                                       ' '
                                       'FONT_HISTORY_BYTES=FONT_PIXELS*20+FONT_SCENE_CELLS+FONT_PERSIST_CELLS*4 '
                                       '};\n',
                                       ' * Original font routines and indexed writes remain the '
                                       'source of authority. */\n'
                                       'enum { '
                                       'FONT_SCENE_CELLS=2218,FONT_PIXELS=FONT_SCENE_CELLS*64,FONT_PERSIST_CELLS=2208,\n'
                                       ' '
                                       'FONT_HISTORY_BYTES=FONT_PIXELS*20+FONT_SCENE_CELLS+FONT_PERSIST_CELLS*4 '
                                       '};\n')],
 'src/render_mirror.c': [(' if(normal15) {\n'
                          '  '
                          'if(!manual_hd_enabled||!manual_hd_lease||!normal15_scope()||terrain_file!=\'z\')render_mirror_unsupported("normal15-output-scope");\n'
                          '  '
                          'if(!normal15_palette())render_mirror_unsupported("normal15-output-palette");\n'
                          '  if(font_history)for(unsigned i=0;i<FONT_SCENE_COUNT;i++)\n'
                          '   '
                          'if(font_scenes[i].canvas_live||font_scenes[i].output_live||font_scene_owned(font_scenes+i,font_owner))\n'
                          '    render_mirror_unsupported("normal15-scene-font");\n'
                          '  '
                          'if(supported&&!normal15_indices_match(kind,lightx,lighty))render_mirror_unsupported("normal15-output-indices");\n',
                          ' if(normal15) {\n'
                          '  '
                          'if(!manual_hd_enabled||!manual_hd_lease||!normal15_scope()||terrain_file!=\'z\')render_mirror_unsupported("normal15-output-scope");\n'
                          '  '
                          'if(!normal15_palette())render_mirror_unsupported("normal15-output-palette");\n'
                          '  if(font_history)for(unsigned i=0;i<2;i++)\n'
                          '   '
                          'if(font_scenes[i].canvas_live||font_scenes[i].output_live||font_scene_owned(font_scenes+i,font_owner))\n'
                          '    render_mirror_unsupported("normal15-scene-font");\n'
                          '  '
                          'if(supported&&!normal15_indices_match(kind,lightx,lighty))render_mirror_unsupported("normal15-output-indices");\n'),
                         (' if(!global_newshf_fade_decline())return;\n'
                          ' '
                          'if((manual_hd_enabled||asteroid_hd_enabled)&&!mirror_enabled()&&!shared_hud_lease&&!global_talon_requested()&&!global_newshf_requested()&&!global_projectile91_requested()) '
                          '{render_mirror_hud_reset();return;}\n'
                          ' hud_check_mode();\n'
                          ' if(font_cached()&&!font_cached_indices_match())font_clear_cached(31);\n'
                          ' '
                          'global_talon_check_cache();global_shield_check_cache();global_pulse_check_cache();global_hitflare_check_cache();global_smoke_check_cache();global_green_check_cache();global_small_explosion_check_cache();global_cash25_check_cache();global_rotor_check_cache();global_projectile91_check_cache();global_newshf_check_cache();global_vulcan_check_cache();\n'
                          ' bool '
                          'cached=last_output_valid;last_output_valid=false;fade_mode=0;ready=false;\n'
                          ' '
                          'if((!mirror_enabled()&&!(shared_hud_lease&&shared_hud_requested())&&!global_talon_requested()&&!global_newshf_requested()&&!global_projectile91_requested())||game_probe_density<2||!output||!cached||first!=0||last!=255)return;\n',
                          ' if(!global_newshf_fade_decline())return;\n'
                          ' '
                          'if((manual_hd_enabled||asteroid_hd_enabled)&&!mirror_enabled()&&!shared_hud_lease&&!global_talon_requested()&&!global_newshf_requested()&&!global_projectile91_requested()) '
                          '{render_mirror_hud_reset();return;}\n'
                          ' hud_check_mode();\n'
                          ' if(font_cached()&&!font_cached_indices_match())font_clear_cached(15);\n'
                          ' '
                          'global_talon_check_cache();global_shield_check_cache();global_pulse_check_cache();global_hitflare_check_cache();global_smoke_check_cache();global_green_check_cache();global_small_explosion_check_cache();global_cash25_check_cache();global_rotor_check_cache();global_projectile91_check_cache();global_newshf_check_cache();global_vulcan_check_cache();\n'
                          ' bool '
                          'cached=last_output_valid;last_output_valid=false;fade_mode=0;ready=false;\n'
                          ' '
                          'if((!mirror_enabled()&&!(shared_hud_lease&&shared_hud_requested())&&!global_talon_requested()&&!global_newshf_requested()&&!global_projectile91_requested())||game_probe_density<2||!output||!cached||first!=0||last!=255)return;\n'),
                         (' hud_check_mode();\n'
                          ' if(!fade_mode||steps<=0)return;\n'
                          ' '
                          'if(!global_newshf_fade_decline()||!global_talon_fade_step_valid(steps)||!global_shield_fade_step_valid(steps)||!global_pulse_fade_step_valid(steps)||!global_vulcan_fade_step_valid(steps)||!global_hitflare_fade_step_valid(steps)||!global_green_fade_step_valid(steps)||!global_smoke_fade_step_valid(steps)||!global_rotor_fade_step_valid(steps)||!global_projectile91_fade_step_valid(steps)||!global_cash25_fade_step_valid(steps)||!global_small_explosion_fade_step_valid(steps))return;\n'
                          ' '
                          'if(font_cached()&&!font_cached_indices_match()){font_clear_cached(31);return;}\n'
                          ' if(fixed_text_output_generation&&!fixed_text_cached_indices_match()) '
                          '{fixed_text_clear_cached();return;}\n'
                          ' '
                          'if(indicator_output_generation&&(!indicators_cached_indices_match()||!indicators_underlay_matches())) '
                          '{indicators_clear_cached(3);return;}\n'
                          ' if(hud_output_generation&&!hud_cached_indices_match()) '
                          '{hud_clear_cached();return;}\n',
                          ' hud_check_mode();\n'
                          ' if(!fade_mode||steps<=0)return;\n'
                          ' '
                          'if(!global_newshf_fade_decline()||!global_talon_fade_step_valid(steps)||!global_shield_fade_step_valid(steps)||!global_pulse_fade_step_valid(steps)||!global_vulcan_fade_step_valid(steps)||!global_hitflare_fade_step_valid(steps)||!global_green_fade_step_valid(steps)||!global_smoke_fade_step_valid(steps)||!global_rotor_fade_step_valid(steps)||!global_projectile91_fade_step_valid(steps)||!global_cash25_fade_step_valid(steps)||!global_small_explosion_fade_step_valid(steps))return;\n'
                          ' '
                          'if(font_cached()&&!font_cached_indices_match()){font_clear_cached(15);return;}\n'
                          ' if(fixed_text_output_generation&&!fixed_text_cached_indices_match()) '
                          '{fixed_text_clear_cached();return;}\n'
                          ' '
                          'if(indicator_output_generation&&(!indicators_cached_indices_match()||!indicators_underlay_matches())) '
                          '{indicators_clear_cached(3);return;}\n'
                          ' if(hud_output_generation&&!hud_cached_indices_match()) '
                          '{hud_clear_cached();return;}\n'),
                         (' render_mirror_shadow_end();\n'
                          ' '
                          'if((manual_hd_enabled||asteroid_hd_enabled)&&!mirror_enabled()&&!shared_hud_lease&&!global_talon_requested()&&!global_newshf_requested()&&!global_projectile91_requested()) '
                          '{render_mirror_hud_reset();return false;}\n'
                          ' hud_check_mode();\n'
                          ' '
                          'if(font_cached()&&(!font_cached_indices_match()||memcmp(font_output_palette,rgb_palette,sizeof(font_output_palette))))font_clear_cached(31);\n'
                          ' '
                          'if(fixed_text_output_generation&&(!fixed_text_cached_indices_match()||memcmp(fixed_text_output_palette,rgb_palette,sizeof(fixed_text_output_palette))!=0))fixed_text_clear_cached();\n'
                          ' '
                          'if(indicator_output_generation&&(!indicators_cached_indices_match()||!indicators_underlay_matches()||memcmp(indicator_output_palette,rgb_palette,sizeof(indicator_output_palette))!=0))indicators_clear_cached(3);\n'
                          ' '
                          'if(hud_output_generation&&(!hud_cached_indices_match()||memcmp(hud_output_palette,rgb_palette,sizeof(hud_output_palette))!=0))hud_clear_cached();\n',
                          ' render_mirror_shadow_end();\n'
                          ' '
                          'if((manual_hd_enabled||asteroid_hd_enabled)&&!mirror_enabled()&&!shared_hud_lease&&!global_talon_requested()&&!global_newshf_requested()&&!global_projectile91_requested()) '
                          '{render_mirror_hud_reset();return false;}\n'
                          ' hud_check_mode();\n'
                          ' '
                          'if(font_cached()&&(!font_cached_indices_match()||memcmp(font_output_palette,rgb_palette,sizeof(font_output_palette))))font_clear_cached(15);\n'
                          ' '
                          'if(fixed_text_output_generation&&(!fixed_text_cached_indices_match()||memcmp(fixed_text_output_palette,rgb_palette,sizeof(fixed_text_output_palette))!=0))fixed_text_clear_cached();\n'
                          ' '
                          'if(indicator_output_generation&&(!indicators_cached_indices_match()||!indicators_underlay_matches()||memcmp(indicator_output_palette,rgb_palette,sizeof(indicator_output_palette))!=0))indicators_clear_cached(3);\n'
                          ' '
                          'if(hud_output_generation&&(!hud_cached_indices_match()||memcmp(hud_output_palette,rgb_palette,sizeof(hud_output_palette))!=0))hud_clear_cached();\n')],
 'src/render_mirror.h': [('#define render_mirror_explosion_initialized(...) ((void)0)\n'
                          '#define render_mirror_owns_display() false\n'
                          '#define render_mirror_text_begin(...) ((void)0)\n'
                          '#define render_mirror_text_warning_begin(...) ((void)0)\n'
                          '#define render_mirror_text_end(...) ((void)0)\n'
                          '#define render_mirror_text_glyph_begin(...) ((void)0)\n'
                          '#define render_mirror_text_glyph_end(...) ((void)0)\n',
                          '#define render_mirror_explosion_initialized(...) ((void)0)\n'
                          '#define render_mirror_owns_display() false\n'
                          '#define render_mirror_text_begin(...) ((void)0)\n'
                          '#define render_mirror_text_end(...) ((void)0)\n'
                          '#define render_mirror_text_glyph_begin(...) ((void)0)\n'
                          '#define render_mirror_text_glyph_end(...) ((void)0)\n'),
                         ('void render_mirror_explosion_initialized(unsigned slot,unsigned type);\n'
                          'bool render_mirror_owns_display(void);\n'
                          'void render_mirror_text_begin(SDL_Surface *,unsigned kind,int x,int '
                          'y,const char *,unsigned hue,int value);\n'
                          'void render_mirror_text_warning_begin(SDL_Surface *,int value);\n'
                          'void render_mirror_text_end(void);\n'
                          'void render_mirror_text_glyph_begin(SDL_Surface *,int x,int y,unsigned '
                          'table,unsigned id,bool black,unsigned hue,int value);\n'
                          'void render_mirror_text_glyph_end(void);\n',
                          'void render_mirror_explosion_initialized(unsigned slot,unsigned type);\n'
                          'bool render_mirror_owns_display(void);\n'
                          'void render_mirror_text_begin(SDL_Surface *,unsigned kind,int x,int '
                          'y,const char *,unsigned hue,int value);\n'
                          'void render_mirror_text_end(void);\n'
                          'void render_mirror_text_glyph_begin(SDL_Surface *,int x,int y,unsigned '
                          'table,unsigned id,bool black,unsigned hue,int value);\n'
                          'void render_mirror_text_glyph_end(void);\n')],
 'src/tyrian2.c': [('\t\t\tfill_rectangle_xy(VGAScreen, 175, 181, 287, 183, warningCol);\n'
                    '\t\t\tfill_rectangle_xy(VGAScreen, 24, 0, 287, 3, warningCol);\n'
                    '\n'
                    '\t\t\trender_mirror_text_warning_begin(VGAScreen, (warningCol % 16) / 2);\n'
                    '\t\t\tJE_outText(VGAScreen, 140, 178, "WARNING", 7, (warningCol % 16) / 2);\n'
                    '\t\t\trender_mirror_text_end();\n'
                    '\n'
                    '\t\t}\n'
                    '\t}\n',
                    '\t\t\tfill_rectangle_xy(VGAScreen, 175, 181, 287, 183, warningCol);\n'
                    '\t\t\tfill_rectangle_xy(VGAScreen, 24, 0, 287, 3, warningCol);\n'
                    '\n'
                    '\t\t\tJE_outText(VGAScreen, 140, 178, "WARNING", 7, (warningCol % 16) / 2);\n'
                    '\n'
                    '\t\t}\n'
                    '\t}\n')]}

def restore(name,text):
 if name not in COMBINED_PINS or type(text)is not str or sha(text.encode('utf-8'))!=COMBINED_PINS[name]:raise ValueError('Changed WARNING source bytes: '+str(name))
 for current,prior in INVERSE[name]:
  if text.count(current)!=1:raise ValueError('Missing/duplicate exact WARNING hunk: '+name)
  text=text.replace(current,prior,1)
 if sha(text.encode('utf-8'))!=MUZZLE_PINS[name]:raise ValueError('Unrelated projected WARNING edit: '+name)
 return text

def project(sources,read_source):
 """Return strict muzzle inventory and its four restored actual byte strings."""
 if type(sources)is not dict or len(sources)!=328 or inventory_digest(sources)!=COMBINED_SOURCE_DIGEST:raise ValueError('Unreviewed combined production epoch')
 result=dict(sources);restored={}
 for name,pin in COMBINED_PINS.items():
  raw=read_source(name)
  if type(raw)is not bytes or sha(raw)!=pin or sources.get(name)!=pin:raise ValueError('Changed WARNING source bytes: '+name)
  restored[name]=restore(name,raw.decode('utf-8')).encode('utf-8');result[name]=sha(restored[name])
 if inventory_digest(result)!=MUZZLE_SOURCE_DIGEST:raise ValueError('Unreviewed WARNING projected epoch')
 return result,restored
