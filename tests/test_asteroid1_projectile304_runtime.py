#!/usr/bin/env python3
"""Bounded extracted-production shared enemy304 source, role, loader and draw tests.

Uses named source files, one reviewed optional HDR1, and the named original
TYRIAN.SHP/TYRIANC.SHP inputs. Runs the real normal compositor, enemy dispatcher,
wrapper, indexed tile blitter and enemy-shot update loop with observational
stubs for unrelated effects. No game launch, original edits or publication.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os
import re
import shutil
import struct
import subprocess

ROOT=Path(__file__).resolve().parents[1]
MIB=1024**2
HDA='enemy-projectile304-304-8.hda'


def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod


PREFIX=r'''
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <limits.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include "sprite.h"
#include "entity_draw.h"
#include "ground101_material.h"
#include "plateau_cap_material.h"
#include "forest13_material.h"
#include "mtrand.h"
#define REAR_OPEN(p) open(p,O_RDONLY|O_NONBLOCK)
#define REAR_READ read
#define REAR_CLOSE close
#define REAR_FSTAT fstat
#define REAR_STAT struct stat
#define REAR_REGULAR(m) S_ISREG(m)
#define SA_NONE 0
#define ENEMY_SHOT_MAX 60
@ENUM@
enum { MIRROR_NORMAL, MIRROR_BLEND, MIRROR_SHADOW };
static int episodeNum=1,lvlFileNum=1,superArcadeMode;
static bool xmas,isNetworkGame,twoPlayerMode,galagaMode,twoPlayerLinked,record_demo;
static bool bonusLevel,onePlayerAction,superTyrian,timedBattleMode,normalBonusLevelCurrent,bonusLevelCurrent;
static bool asteroid_hd_enabled=true,game_probe_enabled,play_demo,asteroid_hd_lease=true;
static bool game_probe_missing,game_probe_invalid,game_probe_original_reference,active=true,game_probe_local_blend;
static int game_probe_density=8;
static unsigned game_probe_scene_assets=1;
static const char *game_probe_assets,*reject_reason;
static uint64_t mirror_logic_tick=1;
Sprite2_array spriteSheet8,spriteSheet9,spriteSheet12,explosionSpriteSheet;
typedef struct {bool initialized,valid;int bank,index,w,h,anchor_x,anchor_y,density;Uint8 *rgba;} Asset;
static const Asset *pulsing272_draw_lease,*triple275_draw_lease,*columns276_draw_lease,*turret273_draw_lease,*enemy_orb112113_draw_lease,*projectile304_draw_lease,*terrain144_draw_lease,*firing285_draw_lease,*firing270_draw_lease;
static Asset assets[567];
static SDL_PixelFormat format={.format=SDL_PIXELFORMAT_INDEX8,.BitsPerPixel=8,.BytesPerPixel=1};
static Uint8 pixel_storage[8192+320*200+8192],*pixels=pixel_storage+8192;
static SDL_Surface surface={.format=&format,.w=320,.h=200,.pitch=320,.pixels=pixel_storage+8192};
static SDL_Surface *game_screen=&surface,*VGAScreen=&surface;
static Uint32 rgb_palette[256];
static Uint32 canvas_pixels[2560*1600];
static SDL_Surface canvas_surface={.w=2560,.h=1600,.pitch=2560*4,.pixels=canvas_pixels},*canvas=&canvas_surface;
static Uint8 hd_owner[2560*1600],cloud_owner[2560*1600],selected[320*200],green_under_owner[2560*1600];
static Uint16 green_first[2560*1600];static Uint32 green_under[2560*1600];
typedef struct {Asset *asset;int x,y;} GreenHead;
static GreenHead green_heads[256];static unsigned green_head_count;
typedef struct {Uint16 peak[16][14];} GreenBackground;
typedef struct {SDL_Rect rect;int bank,index,style;bool live;} HdRegion;
static HdRegion regions[65536];static unsigned region_count,draws,local_entities;
static bool suppress,suppress_green_smoke,suppress_cloud;
static unsigned blits,ends,logged,rejected,unrelated_loads;
static void render_mirror_unsupported(const char *reason){reject_reason=reason;rejected++;}
static void render_mirror_shadow_end(void){}
static void font_before_effect(SDL_Rect r){(void)r;}
static int explosion_asset_slot(unsigned i){(void)i;return -1;}
static void restore_classic_rect(SDL_Rect r){(void)r;assert(!"unrelated restore");}
static void green_background_snapshot(GreenBackground *b,int x,int y){(void)b;(void)x;(void)y;assert(0);}
static unsigned green_background_peak(const GreenBackground *b,int x,int y,Uint32 c){(void)b;(void)x;(void)y;(void)c;assert(0);return 0;}
static Uint32 green_head_composite(int x,int y,unsigned n,Uint32 c){(void)x;(void)y;(void)n;(void)c;assert(0);return 0;}
void ground101_select(const G101Record *m,const Uint8 *s,unsigned n,int x,int y,Uint8 o[4]){(void)m;(void)s;(void)n;(void)x;(void)y;(void)o;assert(0);}
void plateau_cap_select(const PCapRecord *m,const Uint8 s[4],unsigned n,int x,int y,Uint8 o[4]){(void)m;(void)s;(void)n;(void)x;(void)y;(void)o;assert(0);}
void forest13_select(const Forest13Record *m,const Uint8 s[4],unsigned n,int x,int y,Uint8 o[4]){(void)m;(void)s;(void)n;(void)x;(void)y;(void)o;assert(0);}
static void enemy_filter_rgba(const Uint8 *s,Uint8 f,Uint8 *o){(void)s;(void)f;(void)o;assert(0);}
static void explosion_asset_blend_rgba(Uint32 d,const Uint8 *s,Uint8 *o){(void)d;(void)s;(void)o;assert(0);}
static bool enemy_orb112113_draw(SDL_Surface *s,int x,int y,Sprite2_array b,unsigned i){(void)s;(void)x;(void)y;(void)b;(void)i;assert(!"unrelated112113 route");return false;}
static bool enemy_tank_shell_family_ready(void){unrelated_loads++;return false;}
static bool enemy_energy_family_ready(void){unrelated_loads++;return false;}
static bool read_asset(Asset *a,int wanted){(void)wanted;
@READ_GATES@
 unrelated_loads++;return false;
}
static void game_probe_scene_draw(int role,unsigned base,int x,int y,int part,int style,bool mirrored)
{(void)x;(void)y;assert(role==140&&base==304&&!part&&style==ENTITY_NORMAL);logged++;(void)mirrored;}
static void render_mirror_entity_end(void){suppress=false;suppress_green_smoke=false;suppress_cloud=false;ends++;}
static void load_font_arrow_sprite_begin(SDL_Surface *s,int x,int y,const Uint8 *p,size_t n,unsigned i)
{(void)s;(void)x;(void)y;(void)p;(void)n;(void)i;blits++;}
static void pregame_font_sprite2_begin(SDL_Surface *s,int x,int y,const Uint8 *p,size_t n,unsigned i)
{(void)s;(void)x;(void)y;(void)p;(void)n;(void)i;}
static void asset_debug_effect(SDL_Surface *s,Sprite2_array b,unsigned i,int x,int y){(void)s;(void)b;(void)i;(void)x;(void)y;}
static void load_font_arrow_sprite_end(void){}
static void pregame_font_sprite2_end(void){}
static void render_mirror_pixel(SDL_Surface *s,Uint8 *p,Uint8 v,int style){assert(s==&surface&&p>=pixels&&p<pixels+64000&&*p==v&&style==MIRROR_NORMAL);}
@SHOT_STRUCT@
static EnemyShotType enemyShot[ENEMY_SHOT_MAX];static Uint8 enemyShotAvail[ENEMY_SHOT_MAX];
struct Player {int x,y,x_velocity,y_velocity,shot_hit_area_x,shot_hit_area_y,invulnerable_ticks;bool is_alive;};
static struct Player player[2];static unsigned collision_calls,explosion_calls,damage_calls;
static void game_probe_collision(const char *s,int z,int i,int d){assert(!strcmp(s,"enemy-shot")&&z<60&&i<2&&d>=0);collision_calls++;}
static void JE_setupExplosion(int x,int y,int d,int t,bool a,bool b){(void)x;(void)y;assert(!d&&!t&&!a&&!b);explosion_calls++;}
static int JE_playerDamage(int d,struct Player *p){(void)p;damage_calls++;return d;}
'''

CHECKS=r'''
static void frame(void){mirror_logic_tick++;reject_reason=NULL;region_count=0;suppress=false;}
static bool checked(int x,int y,Sprite2_array bank,unsigned index)
{
 EnemyShotType before[60];Uint8 avail[60],before_pixels[64000];Uint32 palette[256];struct Player players[2];
 memcpy(before,enemyShot,sizeof(before));memcpy(avail,enemyShotAvail,sizeof(avail));memcpy(before_pixels,pixels,64000);memcpy(palette,rgb_palette,sizeof(palette));memcpy(players,player,sizeof(players));
 uint64_t rng=mt_state_fingerprint();bool result=render_mirror_enemy_shot(&surface,x,y,bank,index);
 assert(!memcmp(before,enemyShot,sizeof(before))&&!memcmp(avail,enemyShotAvail,sizeof(avail))&&!memcmp(before_pixels,pixels,64000)&&!memcmp(palette,rgb_palette,sizeof(palette))&&!memcmp(players,player,sizeof(players))&&mt_state_fingerprint()==rng&&!projectile304_draw_lease);
 return result;
}
static void source_guards(Sprite2_array bank,Sprite2_array christmas)
{
 assert(projectile304_source(bank,304));
 for(unsigned i=0;i<bank.size;i++){
  frame();projectile304_source_snapshot.valid=false;bank.data[i]^=1;
  assert(!projectile304_source(bank,304)&&!checked(100,80,bank,304)&&!reject_reason);
  bank.data[i]^=1;assert(projectile304_source(bank,304));
 }
 frame();assert(checked(100,80,bank,304));
 for(unsigned i=0;i<bank.size;i++){
  bank.data[i]^=1;assert(!projectile304_source(bank,304)&&!checked(100,80,bank,304)&&reject_reason);bank.data[i]^=1;
  assert(projectile304_source(bank,304));reject_reason=NULL;
 }
 assert(rejected==bank.size);
 frame();Uint8 *copy=malloc(bank.size);assert(copy);memcpy(copy,bank.data,bank.size);
 Sprite2_array clone={bank.size,copy};assert(!projectile304_source(clone,304)&&!checked(100,80,clone,304));
 spriteSheet8=clone;assert(projectile304_source(clone,304)&&checked(100,80,clone,304));spriteSheet8=bank;free(copy);
 frame();Sprite2_array wrong=bank;wrong.size--;assert(!projectile304_source(wrong,304));wrong.size+=2;assert(!projectile304_source(wrong,304));wrong=(Sprite2_array){32060,NULL};assert(!projectile304_source(wrong,304));
 for(unsigned i=0;i<=305;i++)if(i!=304)assert(!projectile304_source(bank,i));assert(!projectile304_source(bank,UINT_MAX));
 spriteSheet12=bank;assert(!projectile304_source(bank,304)&&!checked(100,80,bank,304));spriteSheet12=(Sprite2_array){0,NULL};
 xmas=true;assert(!projectile304_source(bank,304)&&!checked(100,80,bank,304));spriteSheet8=christmas;assert(!projectile304_source(christmas,304)&&!checked(100,80,christmas,304));xmas=false;assert(!projectile304_source(christmas,304));spriteSheet8=bank;
 frame();assert(checked(100,80,bank,304));
}
static void scope_guards(Sprite2_array bank)
{
 bool *flags[]={&xmas,&isNetworkGame,&twoPlayerMode,&galagaMode,&twoPlayerLinked,&record_demo,&onePlayerAction,&superTyrian,&timedBattleMode,&bonusLevel,&normalBonusLevelCurrent,&bonusLevelCurrent,&play_demo};
 for(unsigned i=0;i<sizeof(flags)/sizeof(*flags);i++){*flags[i]=true;assert(!checked(100,80,bank,304));*flags[i]=false;}
 for(unsigned i=0;i<6;i++)if(i!=1){episodeNum=i;assert(!checked(100,80,bank,304));}episodeNum=1;
 for(unsigned i=0;i<99;i++)if(i!=1){lvlFileNum=i;assert(!checked(100,80,bank,304));}lvlFileNum=1;
 superArcadeMode=1;assert(!checked(100,80,bank,304));superArcadeMode=0;
 bool *off[]={&asteroid_hd_enabled,&asteroid_hd_lease,&active};for(unsigned i=0;i<3;i++){*off[i]=false;assert(!checked(100,80,bank,304));*off[i]=true;}
 game_probe_enabled=true;asteroid_hd_lease=false;assert(checked(100,80,bank,304));game_probe_enabled=false;asteroid_hd_lease=true;
 game_probe_scene_assets=0;assert(!checked(100,80,bank,304));game_probe_scene_assets=1;
 bool *bad[]={&game_probe_missing,&game_probe_invalid,&game_probe_original_reference};for(unsigned i=0;i<3;i++){frame();*bad[i]=true;assert(!checked(100,80,bank,304)&&!reject_reason);*bad[i]=false;}
 for(unsigned d=0;d<=9;d++)if(d!=8){game_probe_density=d;assert(!checked(100,80,bank,304));}game_probe_density=8;
 const char *root=game_probe_assets;game_probe_assets=NULL;assert(!checked(100,80,bank,304));game_probe_assets="";assert(!checked(100,80,bank,304));game_probe_assets="unselected-root";assert(!checked(100,80,bank,304));char longpath[1025];memset(longpath,'x',1024);longpath[1024]=0;game_probe_assets=longpath;assert(!checked(100,80,bank,304));game_probe_assets=root;
 SDL_Surface original=surface;SDL_PixelFormat original_format=format;
#define BAD_SURFACE(field,value) do{surface.field=value;assert(!checked(100,80,bank,304));surface=original;}while(0)
 BAD_SURFACE(pixels,NULL);BAD_SURFACE(w,319);BAD_SURFACE(w,321);BAD_SURFACE(h,199);BAD_SURFACE(pitch,319);BAD_SURFACE(pitch,321);BAD_SURFACE(format,NULL);
#define BAD_FORMAT(field,value) do{format.field=value;assert(!checked(100,80,bank,304));format=original_format;}while(0)
 BAD_FORMAT(format,SDL_PIXELFORMAT_ARGB8888);BAD_FORMAT(BitsPerPixel,32);BAD_FORMAT(BytesPerPixel,4);
 SDL_Surface other=surface;assert(!projectile304_draw(NULL,100,80,bank,304));assert(!projectile304_draw(&other,100,80,bank,304));game_screen=&other;assert(!checked(100,80,bank,304));game_screen=&surface;VGAScreen=&other;assert(!checked(100,80,bank,304));VGAScreen=&surface;
 const int badx[]={INT_MIN,-1,309,320,INT_MAX},bady[]={INT_MIN,-14,200,INT_MAX};for(unsigned i=0;i<5;i++)assert(!checked(badx[i],80,bank,304));for(unsigned i=0;i<4;i++)assert(!checked(100,bady[i],bank,304));
#undef BAD_FORMAT
#undef BAD_SURFACE
 frame();assert(checked(100,80,bank,304));
}
static void role_guards(Sprite2_array bank)
{
 frame();assert(checked(100,80,bank,304));Asset *a=&projectile304_resources.member;unsigned before=draws;
 assert(!read_asset(a,8)&&!draw_asset_filtered(100,80,a,MIRROR_NORMAL,NULL,0,NULL,NULL,NULL));
 const Asset **foreign[]={&pulsing272_draw_lease,&triple275_draw_lease,&columns276_draw_lease,&turret273_draw_lease};
 for(unsigned i=0;i<4;i++){*foreign[i]=a;assert(!draw_asset_filtered(100,80,a,MIRROR_NORMAL,NULL,0,NULL,NULL,NULL));*foreign[i]=NULL;}
 projectile304_draw_lease=a;Asset clone=*a;assert(!draw_asset_filtered(100,80,&clone,MIRROR_NORMAL,NULL,0,NULL,NULL,NULL));projectile304_draw_lease=NULL;
 for(unsigned enabled=0;enabled<2;enabled++)for(unsigned christmas=0;christmas<2;christmas++)for(unsigned layout=0;layout<2;layout++){
  asteroid_hd_enabled=enabled;xmas=christmas;assert(!get_asset(bank,304,layout));
 }
 asteroid_hd_enabled=true;xmas=false;assert(draws==before&&unrelated_loads==0);
 /* A direct classic player/generic call has no role lease and never draws HD. */
 unsigned b=blits;blit_sprite2(&surface,100,80,bank,304);assert(blits==b+1&&draws==before&&!projectile304_draw_lease);
 frame();assert(!render_mirror_enemy_shot(&surface,100,80,bank,303));assert(!render_mirror_enemy_shot(&surface,100,80,bank,305));
}
static void resource_guards(Sprite2_array bank)
{
 Asset *a=&projectile304_resources.member;Asset saved=*a;
#define BAD_ASSET(field,value) do{frame();a->field=value;assert(!checked(100,80,bank,304)&&!reject_reason);*a=saved;projectile304_resources.valid=true;}while(0)
 BAD_ASSET(initialized,false);BAD_ASSET(valid,false);BAD_ASSET(bank,8);BAD_ASSET(bank,108);BAD_ASSET(bank,135);BAD_ASSET(bank,136);BAD_ASSET(bank,137);BAD_ASSET(bank,138);BAD_ASSET(bank,139);BAD_ASSET(index,303);BAD_ASSET(index,305);BAD_ASSET(w,11);BAD_ASSET(h,13);BAD_ASSET(density,4);BAD_ASSET(anchor_x,1);BAD_ASSET(anchor_y,1);BAD_ASSET(rgba,NULL);
 frame();a->rgba[100]^=1;assert(!checked(100,80,bank,304));a->rgba[100]^=1;assert(!checked(100,80,bank,304));projectile304_resources.valid=true;
 /* Resource validation happens at least once in every new display frame. */
 frame();assert(checked(100,80,bank,304));a->rgba[100]^=1;frame();assert(!checked(100,80,bank,304)&&!reject_reason);a->rgba[100]^=1;projectile304_resources.valid=true;
 frame();assert(checked(100,80,bank,304));a->valid=false;projectile304_resources.frame_checked=false;assert(!checked(100,80,bank,304)&&reject_reason);*a=saved;projectile304_resources.valid=true;frame();
#undef BAD_ASSET
}
static void geometry(Sprite2_array bank)
{
 Uint8 decoded[336]={0};assert(decode_tile(bank,304,decoded,decoded+168,12,0,0));assert(asteroid1_stamp(decoded,sizeof(decoded))==UINT64_C(0x14e02b0346d1349f));
 unsigned support=0;for(unsigned i=0;i<168;i++)if(decoded[168+i]){support++;assert(i%12>=4&&i%12<=8&&i/12>=5&&i/12<=9);}assert(support==13);
 Asset *a=&projectile304_resources.member;unsigned occupied=0;
 for(unsigned cell=0;cell<168;cell++){unsigned covered=0;for(unsigned dy=0;dy<8;dy++)for(unsigned dx=0;dx<8;dx++){unsigned p=((cell/12*8+dy)*96+cell%12*8+dx)*4;covered+=a->rgba[p+3]!=0;assert((a->rgba[p+3]!=0)==(decoded[168+cell]!=0));}occupied+=covered>0;}assert(occupied==13);
 const int positions[][2]={{100,80},{0,-13},{308,-13},{0,-9},{308,-6},{0,0},{308,186},{0,190},{308,194},{0,199}};
 for(unsigned n=0;n<sizeof(positions)/sizeof(*positions);n++){
  int x=positions[n][0],y=positions[n][1];frame();memset(pixel_storage,0xa5,sizeof(pixel_storage));for(unsigned j=0;j<2560*1600;j++)canvas_pixels[j]=0xff123456;memset(hd_owner,0,sizeof(hd_owner));memset(selected,0,sizeof(selected));
  unsigned before=draws,b=blits,e=ends;Uint32 palette[256];memcpy(palette,rgb_palette,sizeof(palette));uint64_t rng=mt_state_fingerprint();
  draw_enemy_shot_sprite2(&surface,x,y,bank,304);assert(draws==before+1&&blits==b+1&&ends==e+1&&!suppress&&!projectile304_draw_lease&&mt_state_fingerprint()==rng&&!memcmp(palette,rgb_palette,sizeof(palette)));
  Uint8 reference[64000];memcpy(reference,pixels,64000);memset(pixels,0xa5,64000);blit_sprite2(&surface,x,y,bank,304);assert(!memcmp(reference,pixels,64000));
  for(unsigned j=0;j<8192;j++)assert(pixel_storage[j]==0xa5&&pixel_storage[8192+64000+j]==0xa5);
  for(int sy=0;sy<1600;sy++)for(int sx=0;sx<2560;sx++){
   int ax=sx-x*8,ay=sy-y*8;bool covered=ax>=0&&ax<96&&ay>=0&&ay<112&&a->rgba[(ay*96+ax)*4+3];unsigned k=sy*2560+sx;
   assert((hd_owner[k]!=0)==covered);if(covered)assert(canvas_pixels[k]==blend_rgba(0xff123456,a->rgba+(ay*96+ax)*4,a->rgba[(ay*96+ax)*4+3]));else assert(canvas_pixels[k]==0xff123456);
  }
 }
}
struct Trace {EnemyShotType shots[60];Uint8 avail[60],indexed[64000];struct Player players[2];uint64_t rng;unsigned blits,collision,explosion,damage;};
static void trace(struct Trace *t){memset(t,0,sizeof(*t));memcpy(t->shots,enemyShot,sizeof(enemyShot));memcpy(t->avail,enemyShotAvail,sizeof(enemyShotAvail));memcpy(t->indexed,pixels,64000);memcpy(t->players,player,sizeof(player));t->rng=mt_state_fingerprint();t->blits=blits;t->collision=collision_calls;t->explosion=explosion_calls;t->damage=damage_calls;}
static void production_shots(void)
{
 static struct Trace baseline[40];unsigned comparisons=0;
 for(unsigned scenario=0;scenario<16;scenario++)for(unsigned run=0;run<2;run++){
  memset(enemyShot,0,sizeof(enemyShot));memset(enemyShotAvail,1,sizeof(enemyShotAvail));memset(player,0,sizeof(player));memset(pixels,0xa5,64000);blits=collision_calls=explosion_calls=damage_calls=0;mt_srand(304144);active=run;
  player[0]=(struct Player){.x=106,.y=120,.shot_hit_area_x=3,.shot_hit_area_y=3,.is_alive=false};
  for(unsigned i=0;i<5;i++){enemyShotAvail[i]=0;enemyShot[i]=(EnemyShotType){.sx=106,.sy=87,.sxm=(int[]){0,-1,1,-2,2}[i],.sym=(int[]){-1,-3,-3,-4,-4}[i],.syc=1,.sgr=304,.sdmg=1,.duration=255};}
  if(scenario==1)for(unsigned i=0;i<5;i++)enemyShot[i].duration=2;
  if(scenario==2)for(unsigned i=0;i<5;i++)enemyShot[i].sx=1;
  if(scenario==3)for(unsigned i=0;i<5;i++)enemyShot[i].sx=275;
  if(scenario==4)for(unsigned i=0;i<5;i++)enemyShot[i].sy=-13;
  if(scenario==5)for(unsigned i=0;i<5;i++)enemyShot[i].sy=189;
  if(scenario==6)for(unsigned i=0;i<5;i++){enemyShot[i].tx=3;enemyShot[i].ty=3;}
  if(scenario==7)for(unsigned i=0;i<5;i++){enemyShot[i].sxc=1;enemyShot[i].syc=-1;}
  if(scenario==8){player[0].is_alive=true;player[0].y=87;}
  if(scenario==9){player[0].is_alive=true;player[0].y=87;player[0].invulnerable_ticks=2;}
  if(scenario==10)memset(enemyShotAvail,1,sizeof(enemyShotAvail));
  if(scenario==11){memset(enemyShotAvail,0,sizeof(enemyShotAvail));for(unsigned i=5;i<60;i++)enemyShot[i]=enemyShot[i%5];}
  if(scenario==12)for(unsigned i=0;i<5;i++)enemyShot[i].sgr=303;
  if(scenario==13)for(unsigned i=0;i<5;i++){enemyShot[i].sgr=303;enemyShot[i].animax=2;}
  if(scenario==14)for(unsigned i=0;i<5;i++){enemyShot[i].sgr=304;enemyShot[i].sxm=-enemyShot[i].sxm;enemyShot[i].sym=-enemyShot[i].sym;}
  if(scenario==15)for(unsigned i=0;i<5;i++)enemyShot[i].duration=0;
  for(unsigned tick=0;tick<40;tick++){frame();engine_shots();struct Trace now;trace(&now);if(!run)baseline[tick]=now;else{assert(!memcmp(&baseline[tick],&now,sizeof(now)));comparisons++;}}
 }
 active=true;assert(comparisons==640);printf("production shot comparisons=%u\n",comparisons);
}
int main(int argc,char **argv)
{
 assert(argc==5);game_probe_assets=argv[3];mt_srand(304);
 Uint8 normal[32060],christmas[32404];FILE *f=fopen(argv[1],"rb");assert(f&&fread(normal,1,sizeof(normal),f)==sizeof(normal)&&fgetc(f)==EOF);fclose(f);f=fopen(argv[2],"rb");assert(f&&fread(christmas,1,sizeof(christmas),f)==sizeof(christmas)&&fgetc(f)==EOF);fclose(f);
 Sprite2_array bank={sizeof(normal),normal},winter={sizeof(christmas),christmas};spriteSheet8=bank;
 for(unsigned i=0;i<256;i++)rgb_palette[i]=i*0x010101u;memset(pixel_storage,0xa5,sizeof(pixel_storage));
 if(!strcmp(argv[4],"reject")){
  for(unsigned i=0;i<3;i++){frame();unsigned b=blits,d=draws,e=ends;draw_enemy_shot_sprite2(&surface,100,80,bank,304);assert(blits==b+1&&draws==d&&ends==e+1&&!reject_reason&&!projectile304_draw_lease);}
  projectile304_shutdown();puts("optional304 failclosed three frames; original blit once");return 0;
 }
 assert(checked(100,80,bank,304));source_guards(bank,winter);scope_guards(bank);role_guards(bank);resource_guards(bank);geometry(bank);production_shots();
 projectile304_shutdown();assert(!projectile304_source_snapshot.valid&&!projectile304_resources.checked&&!projectile304_draw_lease);assert(checked(100,80,bank,304));projectile304_shutdown();
 printf("cold source bytes=32060 warm source bytes=32060; role140 source304; indexed equality; actual compositor clipping; blits=%u\n",blits);return 0;
}
'''


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo',type=Path,default=ROOT);p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--sdl-include',action='append',default=[]);p.add_argument('--sanitize',action='store_true');a=p.parse_args();root=a.repo.resolve();a.out=a.out.resolve()
    a.out.mkdir(parents=True,exist_ok=True)
    if any(a.out.iterdir()):raise RuntimeError('Select a new empty output directory')
    if shutil.disk_usage(a.out).free<5_000_000_000:raise RuntimeError('At least5GB free required')
    ten=module(root/'tests/test_asteroid1_ten_assets.py','projectile304_ten');linked=module(root/'tests/test_asteroid1_linked338_runtime.py','projectile304_linked');extract=ten.extract
    names=('render_mirror.c','asteroid1_projectile304_mirror.inc','asteroid1_ten_mirror.inc','entity_draw.c','tyrian2.c','sprite.c','varz.h','mtrand.c')
    source={n:(root/'src'/n).read_text() for n in names};r=source['render_mirror.c'];engine=source['tyrian2.c'];varz=source['varz.h']
    assert 'projectile304_shutdown();' in extract(r,'render_mirror_hud_shutdown')
    assert 'if(index==304)return projectile304_draw(surface,x,y,bank,index);' in extract(r,'render_mirror_enemy_shot')
    wrapper=extract(source['entity_draw.c'],'draw_enemy_shot_sprite2');assert wrapper.count('blit_sprite2(')==1 and not re.search(r'\breturn\b',wrapper)
    assert 'projectile304' not in extract(r,'get_asset') and '304' not in extract(r,'get_asset')
    enum=re.search(r'enum \{ ASSET_NEWSH2=.*?\};',r).group(0)
    reader=extract(r,'read_asset');gates=reader[reader.index(' if(a->bank==ASSET_ASTEROID1_NEWSHP'):reader.index(' char name[1024];')]
    shot_end=varz.index('} EnemyShotType;')+len('} EnemyShotType;');shot_start=varz.rindex('typedef struct {',0,shot_end)
    prefix=PREFIX.replace('@ENUM@',enum).replace('@READ_GATES@',gates).replace('@SHOT_STRUCT@',varz[shot_start:shot_end])
    helpers=''.join(extract(r,n) for n in ('asteroid1_level_scope','asteroid1_scope','palette_rgb','blend_rgba','darken_rgba','cloud_asset','decode_tile'))
    # These unmodified finite source functions are needed by the generic
    # player lookup.304 must miss every existing family before resource IO.
    sonic_names=re.findall(r'^static (?:int|bool) (sonic_\w+|mint27_source_matches)\(',r,re.M)
    helpers+=''.join(extract(r,n) for n in sonic_names)
    helpers+=extract(r,'get_asset')+extract(r,'draw_asset_filtered')+extract(r,'draw_asset')
    helpers+=extract(source['asteroid1_ten_mirror.inc'],'asteroid1_stamp')+source['asteroid1_projectile304_mirror.inc']
    helpers+=extract(r,'enemy_energy_slot')+extract(r,'render_mirror_enemy_shot')+extract(source['sprite.c'],'blit_sprite2')+wrapper
    start=engine.index('\t\tfor (int z = 0; z < ENEMY_SHOT_MAX; z++)',engine.index('/* Draw Enemy Shots */'));opening=engine.index('{',start);end=opening+1;depth=1
    while depth:depth+=(engine[end]=='{')-(engine[end]=='}');end+=1
    loop=engine[start:end];assert '|| sprite == 304)' in loop
    engine_func='static void engine_shots(void){JE_byte temp;'+loop+'}\n'
    code=prefix+helpers+source['mtrand.c']+engine_func+CHECKS
    assert not re.search(r'@[A-Z_]+@',code);harness=a.out/'harness.c';harness.write_text(code)
    files=[]
    for name,n,size,sha in [('tyrian.shp','normal-bank8.bin',32060,'9bba1e94d38df61f152412c226bfd6df235e42027c9143c5961d4a5add853a68'),('tyrianc.shp','christmas-bank8.bin',32404,None)]:
        raw=(a.data/name).read_bytes();offsets=struct.unpack_from('<13I',raw,2);bank=raw[offsets[7]:offsets[8]];assert len(bank)==size
        if sha:assert hashlib.sha256(bank).hexdigest()==sha
        path=a.out/n;path.write_bytes(bank);files.append(path)
    pack=root/'assets/hd/packs/asteroid1-ten-v1';payload=(pack/HDA).read_bytes();assert len(payload)==43036 and struct.unpack_from('<4s6I',payload)==(b'HDR1',1400304,8,12,14,0,0)
    assert hashlib.sha256(payload).hexdigest()=='0b86006d9d749f3bdceae0f7a4081250d07838eee7f1f54f284313fd14f17da8'
    kinds=['missing','payload','magic','role8','role108','role135','role136','role137','role138','role139','foreign-base','density','width','height','anchor-x','anchor-y','header-short','short','extra','fifo','directory','broken-symlink'];fixtures=a.out/'fixtures';fixtures.mkdir();variants=[]
    for kind in kinds:
        d=fixtures/kind;d.mkdir();dest=d/HDA
        if kind=='missing':pass
        elif kind=='fifo':os.mkfifo(dest)
        elif kind=='directory':dest.mkdir()
        elif kind=='broken-symlink':dest.symlink_to(d/'absent.hda')
        else:
            data=bytearray(payload)
            if kind=='payload':data[100]^=1
            elif kind=='magic':data[:4]=b'NOPE'
            elif kind.startswith('role'):struct.pack_into('<I',data,4,int(kind[4:])*10000+304)
            elif kind=='foreign-base':struct.pack_into('<I',data,4,1400303)
            elif kind=='header-short':data=data[:12]
            elif kind=='short':data=data[:-1]
            elif kind=='extra':data+=b'X'
            else:struct.pack_into('<I',data,dict(density=8,width=12,height=16,**{'anchor-x':20,'anchor-y':24})[kind],1)
            dest.write_bytes(data)
        variants.append(d)
    flags=['-std=c99','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-I'+str(root/'src')]+['-I'+x for x in a.sdl_include]
    if not a.sdl_include:flags+=subprocess.check_output(['pkg-config','--cflags','sdl2'],text=True).split()
    compiler_peak=runtime_peak=0;runs=[]
    for mode in ['optimized']+(['asan-ubsan'] if a.sanitize else []):
        exe=a.out/mode;log=a.out/(mode+'-compile.log');compiler=['cc',*flags,'-O2']+(['-fsanitize=address,undefined','-fno-omit-frame-pointer','-g'] if mode=='asan-ubsan' else [])
        compiler_peak=max(compiler_peak,linked.run_bounded([*compiler,str(harness),'-lm','-o',str(exe)],log,compiler=True))
        for i,(directory,expected) in enumerate([(pack,'accept')]+[(d,'reject') for d in variants]):
            log=a.out/f'{mode}-{i:03d}.log';runtime_peak=max(runtime_peak,linked.run_bounded([str(exe),str(files[0]),str(files[1]),str(directory),expected],log,sanitize=mode=='asan-ubsan'))
        runs.append(dict(mode=mode,positive=1,negative=len(variants),binary_sha256=hashlib.sha256(exe.read_bytes()).hexdigest()))
    output_bytes=sum(p.stat().st_size for p in a.out.rglob('*') if p.is_file() and not p.is_symlink())
    assert output_bytes<64*MIB
    receipt=dict(material=140,source_index=304,scope='Shared enemy-only original TYRIAN.SHP selector304, normal Episode1 physicallevel1; not emitter-specific.',cold_source_byte_mutations=32060,warm_source_byte_mutations=32060,full_bank_sha256='9bba1e94d38df61f152412c226bfd6df235e42027c9143c5961d4a5add853a68',private_lease_cross_checks=True,generic_player_lookup_rejection=True,source_pointer_alias_rejection=True,Christmas_rejection=True,source_geometry_cells=13,actual_normal_compositor=True,original_indexed_blit_exactly_once=True,original_enemy_shot_dispatch=True,original_enemy_update_loop=True,production_shot_trace_comparisons=640,INDEX8_equality=True,palette_unchanged=True,RNG_unchanged=True,corrupt_optional_resource_fixtures=len(variants),negative_frame_count=3,resource_failure_isolated=True,compiler_peak_rss_bytes=compiler_peak,runtime_peak_rss_bytes=runtime_peak,compiler_address_space_limit_bytes=1024*MIB,runtime_rss_limit_bytes=512*MIB,output_limit_bytes=64*MIB,output_bytes=output_bytes,runs=runs,leak_sanitizer=False,source_sha256={n:hashlib.sha256(s.encode()).hexdigest() for n,s in source.items()},harness_sha256=hashlib.sha256(harness.read_bytes()).hexdigest(),test_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (a.out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
