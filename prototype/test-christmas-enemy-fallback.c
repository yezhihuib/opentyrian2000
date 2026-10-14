/* Focused admission/cache and indexed-write units. Production functions are
 * extracted unchanged; the HD compositor is an observing stub, not a render test. */
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
typedef uint8_t Uint8; typedef uint16_t Uint16; typedef uint32_t Uint32;
typedef struct {int x,y,w,h;} SDL_Rect;
typedef struct {int BitsPerPixel,BytesPerPixel;} SDL_PixelFormat;
typedef struct {int w,h,pitch;void *pixels;SDL_PixelFormat *format;} SDL_Surface;
typedef struct {Uint8 *data;size_t size;} Sprite2_array;
typedef enum {ENTITY_NORMAL,ENTITY_BLEND,ENTITY_SHADOW} EntityDrawStyle;
typedef enum {ENTITY_TILE,ENTITY_QUAD} EntityDrawLayout;
enum {MIRROR_NORMAL,MIRROR_BLEND,MIRROR_SHADOW};
#define MIN(a,b) ((a)<(b)?(a):(b))
#include "types.inc"
#ifndef BASELINE
#define BASELINE 0
#endif
static bool xmas,active=true,game_probe_missing,game_probe_invalid,game_probe_original_reference;
static bool manual_hd_enabled=true,isNetworkGame,twoPlayerMode,galagaMode,play_demo,record_demo;
enum {DIFFICULTY_NORMAL=2,SA_NONE=0};
static bool onePlayerAction,superTyrian,timedBattleMode,bonusLevel,normalBonusLevelCurrent,bonusLevelCurrent;
static int initialDifficulty=3,superArcadeMode=SA_NONE;
static int episodeNum=1,lvlFileNum=9,game_probe_density=8;
static const char *game_probe_assets,*reject_reason,*full_pack;
static SDL_PixelFormat format={8,1};
static SDL_Surface screen={320,200,320,NULL,&format},*game_screen=&screen,*VGAScreen=&screen;
static Sprite2_array spriteSheet8,spriteSheet9,spriteSheet12,explosionSpriteSheet;
static Uint32 rgb_palette[256];
static bool cash25_fixed_value,cash75_fixed_value,cash50_fixed_value,gem100_fixed_value,gem250_fixed_value;
static TalonBank talon_banks[2];static unsigned banking_draw_player;static uint64_t mirror_logic_tick;
static const int original_visual_indices[5]={0,2,6,10,12};
static unsigned asset_opens,draws,original_calls,end_calls,logs,writes,cases,accepted_cases,fallback_cases,guard_cases;
static unsigned real_xmas_admitted[2];
static unsigned log_id;static int log_role;static bool log_mirrored;
static int write_offsets[168];static Uint8 write_values[168];
static void render_mirror_shadow_end(void) {}
static void render_mirror_shadow_begin(SDL_Surface*s,int x,int y,Sprite2_array b,unsigned id)
{(void)s;(void)x;(void)y;(void)b;(void)id;}
static void render_mirror_entity_end(void) {end_calls++;}
static bool draw_asset(int x,int y,Asset*a,int style,const SDL_Rect*r)
{(void)x;(void)y;assert(a&&a->valid&&a->rgba&&a->w==12&&a->h==14);assert(style==MIRROR_NORMAL||style==MIRROR_SHADOW);assert(!r);draws++;return true;}
static bool draw_vulcan_shadow(SDL_Surface*s,int x,int y,Sprite2_array b,unsigned id)
{(void)s;(void)x;(void)y;(void)b;(void)id;assert(0);return false;}
#define cash25_surface_ready(...) (assert(0),false)
#define cash25_family_ready() (assert(0),false)
#define cash75_family_ready() (assert(0),false)
#define cash50_family_ready() (assert(0),false)
#define gem100_family_ready() (assert(0),false)
#define gem250_family_ready() (assert(0),false)
static void game_probe_scene_draw(int role,unsigned id,int x,int y,int part,int style,bool mirrored)
{(void)x;(void)y;assert(!part&&style==ENTITY_NORMAL);logs++;log_role=role;log_id=id;log_mirrored=mirrored;}
static void game_probe_draw(int role,unsigned id,int x,int y,int style,int layout,bool mirrored)
{(void)x;(void)y;assert(role==8&&layout==ENTITY_TILE&&(style==ENTITY_NORMAL||style==ENTITY_SHADOW));logs++;log_role=role;log_id=id;log_mirrored=mirrored;}
static FILE *counted_fopen(const char *path,const char *mode) {asset_opens++;return fopen(path,mode);}
#define fopen counted_fopen
#include "functions.inc"
#undef fopen
static Uint16 SDL_SwapLE16(Uint16 v) {Uint8 b[2];memcpy(b,&v,2);return (Uint16)(b[0]|(unsigned)b[1]<<8);}
static void asset_debug_effect(SDL_Surface*s,Sprite2_array b,unsigned id,int x,int y)
{assert(s&&b.data&&id);(void)x;(void)y;original_calls++;}
static void render_mirror_pixel(SDL_Surface*s,Uint8*p,Uint8 v,int style)
{assert(s==&screen&&writes<168);write_offsets[writes]=(int)(p-(Uint8*)s->pixels);write_values[writes++]=*p;assert(style==MIRROR_SHADOW||v==*p);}
#define load_font_arrow_sprite_begin(...) ((void)0)
#define load_font_arrow_sprite_end(...) ((void)0)
#define pregame_font_sprite2_begin(...) ((void)0)
#define pregame_font_sprite2_end(...) ((void)0)
#include "blitters.inc"
#define blit_sprite2_blend(...) assert(0)
#define blit_sprite2x2(...) assert(0)
#define blit_sprite2x2_blend(...) assert(0)
#define blit_sprite2x2_darken(...) assert(0)
#include "wrappers.inc"
#include "ids.inc"
enum {SCREEN=64000,PAD=16384};
static Uint8 storage[SCREEN+2*PAD],expected[SCREEN+2*PAD];
static Uint8 reference[2][NID][336];static Sprite2_array banks[2];static int selected_bank;
static void *read_file(const char *name,size_t *size)
{FILE*f=fopen(name,"rb");assert(f&&!fseek(f,0,SEEK_END));long n=ftell(f);assert(n>0&&!fseek(f,0,SEEK_SET));void*p=malloc((size_t)n);assert(p&&fread(p,1,(size_t)n,f)==(size_t)n&&!fclose(f));*size=(size_t)n;return p;}
static void clear_assets(void)
{for(unsigned i=0;i<sizeof(assets)/sizeof(*assets);i++){free(assets[i].rgba);memset(assets+i,0,sizeof(*assets));}for(unsigned i=0;i<13;i++){free(talon_frames[i].rgba);memset(talon_frames+i,0,sizeof(*talon_frames));}enemy_energy_checked=enemy_energy_valid=enemy_tank_shell_checked=enemy_tank_shell_valid=false;}
static void select_mode(bool flag,int bank) {xmas=flag;selected_bank=bank;spriteSheet8=banks[bank];}
static bool expected_enemy(unsigned k) {return !(xmas&&k<9&&!BASELINE);}
static bool expected_player(unsigned k) {return ids[k]==58||ids[k]==59||(!xmas&&(k>=11||ids[k]==163||ids[k]==164));}
static void transaction(unsigned k,bool player,bool shadow,bool admitted,int x,int y)
{
 for(unsigned i=0;i<sizeof(storage);i++)storage[i]=expected[i]=(Uint8)(i*29+17);
 writes=0;unsigned old_draws=draws,old_original=original_calls,old_ends=end_calls,old_logs=logs;
 Uint8 *source=malloc(spriteSheet8.size);assert(source);memcpy(source,spriteSheet8.data,spriteSheet8.size);
 if(player)draw_entity_sprite2(&screen,x,y,spriteSheet8,ids[k],shadow?ENTITY_SHADOW:ENTITY_NORMAL,ENTITY_TILE);
 else draw_enemy_shot_sprite2(&screen,x,y,spriteSheet8,ids[k]);
 assert(draws==old_draws+(unsigned)admitted&&original_calls==old_original+1&&end_calls==old_ends+1);
 assert(logs==old_logs+1&&log_id==ids[k]&&log_mirrored==admitted&&log_role==(player?8:k<7?111:k<9?108:122));
 unsigned count=0;const Uint8*r=reference[selected_bank][k];
 for(int n=0;n<168;n++)if(r[168+n]) {
  int offset=(y+n/12)*320+x+n%12;if(offset<0||offset>=SCREEN)continue;
  Uint8 before=expected[PAD+offset],value=shadow?(Uint8)((before&240)|((before&15)/2)):r[n];
  expected[PAD+offset]=value;assert(count<writes&&write_offsets[count]==offset&&write_values[count]==value);count++;
 }
 assert(count==writes&&!memcmp(storage,expected,sizeof(storage))&&!memcmp(source,spriteSheet8.data,spriteSheet8.size));
 free(source);cases++;accepted_cases+=admitted;fallback_cases+=!admitted;
}
static void enemies(void) {for(unsigned k=0;k<11;k++)transaction(k,false,false,expected_enemy(k),94,73);}
static void players(void)
{for(unsigned k=0;k<NID;k++)transaction(k,true,false,expected_player(k),94,73);transaction(1,true,true,true,94,73);}
static void check_cache_matrix(void)
{
 /* Real pairings: normal/normal and Xmas/Christmas bank. Mismatched pairings
  * are deliberate controls proving this is a mode guard, not a bank hash. */
 for(int flag=0;flag<2;flag++)for(int bank=0;bank<2;bank++)for(int warm=0;warm<2;warm++) {
  clear_assets();select_mode(false,0);if(warm){enemies();players();}
  select_mode(flag!=0,bank);unsigned before=asset_opens;
  Asset snapshot[sizeof(assets)/sizeof(*assets)];memcpy(snapshot,assets,sizeof(assets));
  for(unsigned k=0;k<9;k++){transaction(k,false,false,expected_enemy(k),94,73);if(flag&&bank==1)real_xmas_admitted[warm]+=log_mirrored;}
  if(flag&&!BASELINE){assert(asset_opens==before&&!memcmp(snapshot,assets,sizeof(assets)));assert(enemy_energy_checked==(warm!=0));}
  for(unsigned k=9;k<11;k++)transaction(k,false,false,true,94,73);
  players();before=asset_opens;enemies();players();assert(asset_opens==before);
  select_mode(false,0);enemies();players(); /* no sticky Xmas rejection */
 }
}
static void guard_at(SDL_Surface*s,int x,int y,Sprite2_array bank,unsigned id)
{unsigned before=draws,opens=asset_opens;assert(!render_mirror_enemy_shot(s,x,y,bank,id));assert(draws==before&&asset_opens==opens);guard_cases++;}
static void guard(SDL_Surface*s,Sprite2_array bank,unsigned id) {guard_at(s,94,73,bank,id);}
static void check_guards(void)
{
 for(int flag=0;flag<2;flag++)for(int warm=0;warm<2;warm++) {
  clear_assets();select_mode(false,0);if(warm)enemies();select_mode(flag!=0,flag);
  SDL_Surface other=screen;Sprite2_array wrong=banks[1-flag],null={NULL,0};
  for(unsigned k=0;k<11;k++){guard(&screen,wrong,ids[k]);guard(&other,spriteSheet8,ids[k]);guard(&screen,null,ids[k]);}
  for(unsigned id=0;id<=303;id++)if(enemy_energy_slot(id)<0&&id!=112&&id!=113&&id!=146&&id!=147)guard(&screen,spriteSheet8,id);
  active=false;for(unsigned k=0;k<11;k++)guard(&screen,spriteSheet8,ids[k]);active=true;
  reject_reason="fixture";for(unsigned k=0;k<11;k++)guard(&screen,spriteSheet8,ids[k]);reject_reason=NULL;
  game_probe_missing=true;for(unsigned k=0;k<11;k++)guard(&screen,spriteSheet8,ids[k]);game_probe_missing=false;
  game_probe_invalid=true;for(unsigned k=0;k<11;k++)guard(&screen,spriteSheet8,ids[k]);game_probe_invalid=false;
  game_probe_assets=NULL;for(unsigned k=0;k<11;k++)guard(&screen,spriteSheet8,ids[k]);game_probe_assets=full_pack;
  game_probe_density=1;for(unsigned k=0;k<11;k++)guard(&screen,spriteSheet8,ids[k]);game_probe_density=8;
 }
}
static void check_geometry_guards(void)
{
 /* Existing energy/shell physical-surface restrictions; the older orb path
  * has different guards and is deliberately not assigned new restrictions. */
 static const int xy[][2]={{-1,73},{309,73},{94,-14},{94,200},{INT_MIN,0},{INT_MAX,0},{0,INT_MIN},{0,INT_MAX}};
 for(int flag=0;flag<2;flag++)for(int warm=0;warm<2;warm++) {
  clear_assets();select_mode(false,0);if(warm)enemies();select_mode(flag!=0,flag);
  for(unsigned k=0;k<11;k++)if(k<7||k>=9) {
   for(unsigned j=0;j<sizeof(xy)/sizeof(*xy);j++)guard_at(&screen,xy[j][0],xy[j][1],spriteSheet8,ids[k]);
   guard(NULL,spriteSheet8,ids[k]);
   screen.format=NULL;guard(&screen,spriteSheet8,ids[k]);screen.format=&format;
   format.BitsPerPixel=32;guard(&screen,spriteSheet8,ids[k]);format.BitsPerPixel=8;
   format.BytesPerPixel=4;guard(&screen,spriteSheet8,ids[k]);format.BytesPerPixel=1;
   screen.pitch=321;guard(&screen,spriteSheet8,ids[k]);screen.pitch=320;
   screen.w=319;guard(&screen,spriteSheet8,ids[k]);screen.w=320;
   screen.h=199;guard(&screen,spriteSheet8,ids[k]);screen.h=200;
   SDL_Surface other=screen;VGAScreen=&other;guard(&screen,spriteSheet8,ids[k]);VGAScreen=&screen;
   game_probe_original_reference=true;guard(&screen,spriteSheet8,ids[k]);game_probe_original_reference=false;
   game_probe_density=4;guard(&screen,spriteSheet8,ids[k]);game_probe_density=8;
  }
 }
}
static void check_geometry(void)
{
 static const int xy[][2]={{0,-13},{308,-13},{0,0},{308,0},{0,199},{308,199}};
 for(int flag=0;flag<2;flag++){clear_assets();select_mode(flag!=0,flag);for(unsigned k=0;k<11;k++)for(unsigned j=0;j<sizeof(xy)/sizeof(*xy);j++)transaction(k,false,false,expected_enemy(k),xy[j][0],xy[j][1]);}
}
static void check_manual_scope(void)
{
 for(int flag=0;flag<2;flag++) {
  xmas=flag!=0;assert(manual_hd_scope());lvlFileNum=15;
  assert(manual_hd_scope()==(!BASELINE&&!xmas));
  initialDifficulty=DIFFICULTY_NORMAL;assert(!manual_hd_scope());initialDifficulty=3;
  initialDifficulty=4;assert(manual_hd_scope()==(!BASELINE&&!xmas));initialDifficulty=3;
  bool *night_blocked[]={&isNetworkGame,&twoPlayerMode,&galagaMode,&play_demo,&record_demo,
   &onePlayerAction,&superTyrian,&timedBattleMode,&bonusLevel,&normalBonusLevelCurrent,&bonusLevelCurrent};
  for(unsigned i=0;i<sizeof(night_blocked)/sizeof(*night_blocked);i++){*night_blocked[i]=true;assert(!manual_hd_scope());*night_blocked[i]=false;}
  superArcadeMode=1;assert(!manual_hd_scope());superArcadeMode=SA_NONE;
  manual_hd_enabled=false;assert(!manual_hd_scope());manual_hd_enabled=true;
  episodeNum=2;assert(!manual_hd_scope());episodeNum=1;
  lvlFileNum=16;assert(!manual_hd_scope());lvlFileNum=9;
  episodeNum=2;assert(!manual_hd_scope());episodeNum=1;
  bool *blocked[]={&isNetworkGame,&twoPlayerMode,&galagaMode,&play_demo,&record_demo};
  for(unsigned i=0;i<sizeof(blocked)/sizeof(*blocked);i++){*blocked[i]=true;assert(!manual_hd_scope());*blocked[i]=false;}
  manual_hd_enabled=false;assert(!manual_hd_scope());manual_hd_enabled=true;
 }
}
int main(int argc,char**argv)
{
 assert(argc==3);full_pack=game_probe_assets=argv[1];char path[2048];size_t n;
 for(int i=0;i<2;i++){snprintf(path,sizeof(path),"%s/bank-%d.bin",argv[2],i);banks[i].data=read_file(path,&n);banks[i].size=n;}
 snprintf(path,sizeof(path),"%s/reference.bin",argv[2]);void*p=read_file(path,&n);assert(n==sizeof(reference));memcpy(reference,p,n);free(p);
 Uint8 tokens[3]={0};spriteSheet9=(Sprite2_array){tokens,1};spriteSheet12=(Sprite2_array){tokens+1,1};explosionSpriteSheet=(Sprite2_array){tokens+2,1};screen.pixels=storage+PAD;
 check_manual_scope();check_cache_matrix();assert(real_xmas_admitted[0]==(BASELINE?9u:0u)&&real_xmas_admitted[1]==(BASELINE?9u:0u));check_guards();check_geometry_guards();check_geometry();clear_assets();free(banks[0].data);free(banks[1].data);
 printf("{\"status\":\"PASS\",\"baseline\":%d,\"transactions\":%u,\"accepted\":%u,\"fallback\":%u,\"guard_checks\":%u,\"asset_open_attempts\":%u,\"real_xmas_cold_changed_ids_admitted\":%u,\"real_xmas_warm_changed_ids_admitted\":%u}\n",BASELINE,cases,accepted_cases,fallback_cases,guard_cases,asset_opens,real_xmas_admitted[0],real_xmas_admitted[1]);return 0;
}
