/* Exact extracted loader/hook/wrapper/compositor/RLE with independent RGBA,
 * physical-address and ownership oracles. Unit only: no game or capture. */
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
typedef uint8_t Uint8;typedef uint16_t Uint16;typedef uint32_t Uint32;
typedef struct {int x,y,w,h;} SDL_Rect;
typedef struct {int BitsPerPixel,BytesPerPixel;} SDL_PixelFormat;
typedef struct {int w,h,pitch;void *pixels;SDL_PixelFormat *format;} SDL_Surface;
typedef struct {Uint8 *data;size_t size;} Sprite2_array;
typedef struct {int unused;} G101Record,PCapRecord,Forest13Record;
typedef enum {ENTITY_NORMAL,ENTITY_BLEND,ENTITY_SHADOW} EntityDrawStyle;
typedef enum {ENTITY_TILE,ENTITY_QUAD} EntityDrawLayout;
enum {MIRROR_NORMAL,MIRROR_BLEND,MIRROR_SHADOW};
enum {ASSET_NEWSH2=101,ASSET_NEWSH4=102,ASSET_NEWSHE=110,ASSET_ENEMY_ENERGY=111,ASSET_CASH25_BODY=112,ASSET_CASH25_VALUE=113,ASSET_TALON_BANK=109,ASSET_SHAPESZ=201,ASSET_EXPLOSION=106};
#define MIN(a,b) ((a)<(b)?(a):(b))
#define MAX(a,b) ((a)>(b)?(a):(b))
#include "types.inc"
static bool xmas;
static bool active=true,suppress,suppress_green_smoke,suppress_cloud,game_probe_missing,game_probe_invalid,game_probe_original_reference,game_probe_local_blend;
static const char *game_probe_assets,*reject_reason,*full_pack,*work;
static int game_probe_density=8;
static SDL_PixelFormat format={8,1};
static SDL_Surface screen={320,200,320,NULL,&format},display,*game_screen=&screen,*VGAScreen=&screen,*canvas=&display;
static Sprite2_array spriteSheet11,spriteSheet8,spriteSheet9,spriteSheet12,explosionSpriteSheet;
static Uint32 rgb_palette[256];
static Uint8 expected[64000],selected[64000],*hd_owner,*cloud_owner,*green_under_owner;
static Uint16 *green_first;static Uint32 *green_under;
typedef struct {Asset *asset;int x,y;} GreenHead;static GreenHead green_heads[256];
typedef struct {Uint16 peak[16][14];} GreenBackground;
typedef struct {SDL_Rect rect;int bank,index,style;bool live;} HdRegion;static HdRegion regions[256];
static unsigned green_head_count,region_count,draws,occlusions,local_entities;
static TalonBank talon_banks[2];static unsigned banking_draw_player;static uint64_t mirror_logic_tick;
static const int original_visual_indices[5]={0,2,6,10,12};
static unsigned original_calls,end_calls,scene_calls,player_calls,font_calls;
static unsigned log_id;static int log_role,log_x,log_y;static bool log_mirrored;
#define ground101_select(...) assert(0)
#define plateau_cap_select(...) assert(0)
#define forest13_select(...) assert(0)
#define settings_font_pixel(...) ((void)0)
#define load_font_pixel(...) ((void)0)
#define load_font_arrow_sprite_begin(...) ((void)0)
#define load_font_arrow_sprite_end(...) ((void)0)
static void font_before_effect(SDL_Rect r){(void)r;font_calls++;}
static bool font_pixel(int x,int y,Uint8 p,int style){(void)x;(void)y;(void)p;(void)style;return false;}
static void restore_classic_rect(SDL_Rect r){(void)r;assert(0);}
static void render_mirror_unsupported(const char *s){fprintf(stderr,"Unexpected rejection: %s\n",s);abort();}
static Uint16 SDL_SwapLE16(Uint16 value){Uint8 b[2];memcpy(b,&value,2);return (Uint16)(b[0]|(unsigned)b[1]<<8);}
typedef struct {unsigned type,pool_slot,availability,size;bool score_item,damaged,independent_motion,static_animation;} G101EnemyContext;
static void game_probe_scene_draw(int role,unsigned id,int x,int y,int part,int style,bool mirrored){(void)role;(void)id;(void)x;(void)y;(void)part;(void)style;(void)mirrored;scene_calls++;}
#include "functions.inc"
/* Indexed writes are tested through the unchanged real blitters/wrapper.
 * Display pixel hooks are observed separately by the RGBA oracle above. */
static void asset_debug_effect(SDL_Surface *surface,Sprite2_array bank,unsigned id,int x,int y){(void)surface;(void)bank;(void)id;(void)x;(void)y;original_calls++;}
static void render_mirror_pixel(SDL_Surface*s,Uint8*p,Uint8 v,int style){(void)s;(void)p;(void)v;(void)style;}
static void render_mirror_sprite2_blend_pixel(SDL_Surface*s,Uint8*p,Uint8 v,Sprite2_array bank,unsigned id,int x,int y){(void)s;(void)p;(void)v;(void)bank;(void)id;(void)x;(void)y;}
static void game_probe_draw(int role,unsigned id,int x,int y,int style,int layout,bool mirrored){(void)role;(void)id;(void)x;(void)y;(void)style;(void)layout;(void)mirrored;player_calls++;}
#include "blitters.inc"
#define blit_sprite2x2(...) assert(0)
#define blit_sprite2x2_blend(...) assert(0)
#define blit_sprite2x2_darken(...) assert(0)
#include "wrapper.inc"
static const unsigned ids[7]={7,8,9,10,11,12,185};
static uint64_t pixels,checks;
#define CHECK(x) do{if(!(x)){fprintf(stderr,"FAIL line%d: %s\n",__LINE__,#x);exit(3);}checks++;}while(0)
static void clear_assets(void){for(unsigned i=0;i<sizeof(assets)/sizeof(*assets);i++){free(assets[i].rgba);memset(assets+i,0,sizeof(*assets));}cash25_checked=cash25_valid=false;enemy_energy_checked=enemy_energy_valid=false;}
static Uint32 bg(int n){return 0xff000000u|((n*2654435761u+0x594123u)&0xffffffu);}
static void start(void){int d=8;canvas->w=320*d;canvas->h=200*d;canvas->pitch=canvas->w*4;size_t n=canvas->w*canvas->h;canvas->pixels=calloc(n,4);hd_owner=calloc(n,1);cloud_owner=calloc(n,1);green_first=calloc(n,2);green_under=calloc(n,4);green_under_owner=calloc(n,1);screen.pixels=calloc(64000,1);CHECK(canvas->pixels&&hd_owner&&cloud_owner&&green_first&&green_under&&green_under_owner&&screen.pixels);}
static void reset_area(int x,int y){region_count=draws=green_head_count=0;reject_reason=NULL;render_mirror_entity_end();for(int py=0;py<14*8;py++)for(int px=0;px<12*8;px++){int dx=x*8+px,dy=y*8+py;if(dx<0||dx>=canvas->w||dy<0||dy>=canvas->h)continue;int n=dy*canvas->w+dx;((Uint32*)canvas->pixels)[n]=bg(n);hd_owner[n]=1;cloud_owner[n]=1;green_first[n]=7;}}
static Uint32 alpha_oracle(Uint32 dst,const Uint8*s){Uint32 out=0xff000000u;for(int c=0;c<3;c++){int sh=16-8*c;unsigned n=((dst>>sh)&255)*(255-s[3])+s[c]*s[3];out|=(n/255+(n%255>=128))<<sh;}return out;}
static void check_pixels(const Asset *a,int x,int y,bool blend,int filter){for(int py=0;py<14*8;py++)for(int px=0;px<12*8;px++){int dx=x*8+px,dy=y*8+py;if(dx<0||dx>=canvas->w||dy<0||dy>=canvas->h)continue;int n=dy*canvas->w+dx;const Uint8*s=a->rgba+4*(py*96+px);Uint8 rgba[4];memcpy(rgba,s,4);Uint32 want=bg(n);if(s[3]){if(filter){unsigned peak=MAX(s[0],MAX(s[1],s[2])),value=(peak*15*256+127)/255,lo=value/256,hi=MIN(15,lo+1),f=value%256;for(int c=0;c<3;c++){int sh=16-8*c;rgba[c]=((((rgb_palette[filter|lo]>>sh)&255)*(256-f)+((rgb_palette[filter|hi]>>sh)&255)*f+128)/256);}}if(blend){unsigned peak=MAX(s[0],MAX(s[1],s[2])),dest=MAX((want>>16)&255,MAX((want>>8)&255,want&255)),average=(peak+dest+1)/2;for(int c=0;c<3;c++)rgba[c]=peak?(s[c]*average+peak/2)/peak:0;}want=alpha_oracle(want,rgba);}CHECK(((Uint32*)canvas->pixels)[n]==want);CHECK(hd_owner[n]==1);CHECK(cloud_owner[n]==(s[3]?0:1));CHECK(green_first[n]==(s[3]?0:7));pixels++;}}
static Uint32 composed(Uint32 dst,const Uint8 *s,bool blend){Uint8 rgba[4];memcpy(rgba,s,4);if(blend){unsigned peak=MAX(s[0],MAX(s[1],s[2])),d=MAX((dst>>16)&255,MAX((dst>>8)&255,dst&255)),v=(peak+d+1)/2;for(int c=0;c<3;c++)rgba[c]=peak?(s[c]*v+peak/2)/peak:0;}return s[3]?alpha_oracle(dst,rgba):dst;}
static void overlaps(void){for(int first=0;first<7;first++)for(int second=0;second<7;second++)for(int blend=0;blend<(second==6?2:1);blend++){int x=98,y=100;reset_area(x,y);CHECK(draw_asset(x,y,assets+472+first,MIRROR_NORMAL,NULL));CHECK(draw_asset(x,y,assets+472+second,blend?MIRROR_BLEND:MIRROR_NORMAL,NULL));for(int py=0;py<112;py++)for(int px=0;px<96;px++){int n=(y*8+py)*canvas->w+x*8+px;const Uint8 *a=assets[472+first].rgba+4*(py*96+px),*b=assets[472+second].rgba+4*(py*96+px);Uint32 want=composed(composed(bg(n),a,false),b,blend);CHECK(((Uint32*)canvas->pixels)[n]==want);CHECK(cloud_owner[n]==((a[3]||b[3])?0:1));CHECK(green_first[n]==((a[3]||b[3])?0:7));pixels++;}render_mirror_entity_end();}}
static bool popup(SDL_Surface *surface,int x,int y,Sprite2_array bank,unsigned id,int style,int layout,bool eligible){render_mirror_coin25_value_begin(eligible);bool r=render_mirror_entity(surface,x,y,bank,id,style,layout);CHECK(!cash25_fixed_value);return r;}
static void guards(void){G101EnemyContext c={391,25,2,0,true,false,true,false};Sprite2_array wrong={(Uint8*)&c,1},null={NULL,0};SDL_Surface other=screen;unsigned saved=draws;
 for(unsigned id=0;id<500;id++)if(id<7||id>12)CHECK(!cash25_pickup(&screen,98,100,spriteSheet11,id,0,0,&c));
 CHECK(!cash25_pickup(&screen,98,100,wrong,7,0,0,&c));CHECK(!cash25_pickup(&screen,98,100,null,7,0,0,&c));CHECK(!cash25_pickup(&screen,98,100,spriteSheet11,7,1,0,&c));CHECK(!cash25_pickup(&screen,98,100,spriteSheet11,7,0,0,NULL));c.type=390;CHECK(!cash25_pickup(&screen,98,100,spriteSheet11,7,0,0,&c));c.type=391;c.size=1;CHECK(!cash25_pickup(&screen,98,100,spriteSheet11,7,0,0,&c));c.size=0;
 CHECK(!popup(&screen,98,100,explosionSpriteSheet,185,MIRROR_NORMAL,ENTITY_TILE,false));CHECK(!popup(&screen,98,100,wrong,185,MIRROR_NORMAL,ENTITY_TILE,true));CHECK(!popup(&screen,98,100,null,185,MIRROR_NORMAL,ENTITY_TILE,true));CHECK(!popup(&screen,98,100,explosionSpriteSheet,186,MIRROR_NORMAL,ENTITY_TILE,true));CHECK(!popup(&screen,98,100,explosionSpriteSheet,185,MIRROR_SHADOW,ENTITY_TILE,true));CHECK(!popup(&screen,98,100,explosionSpriteSheet,185,MIRROR_NORMAL,ENTITY_QUAD,true));CHECK(!popup(NULL,98,100,explosionSpriteSheet,185,MIRROR_NORMAL,ENTITY_TILE,true));CHECK(!popup(&other,98,100,explosionSpriteSheet,185,MIRROR_NORMAL,ENTITY_TILE,true));
 active=false;CHECK(!popup(&screen,98,100,explosionSpriteSheet,185,MIRROR_NORMAL,ENTITY_TILE,true));active=true;reject_reason="guard";CHECK(!popup(&screen,98,100,explosionSpriteSheet,185,MIRROR_NORMAL,ENTITY_TILE,true));reject_reason=NULL;CHECK(!render_mirror_entity(&screen,98,100,explosionSpriteSheet,185,MIRROR_NORMAL,ENTITY_TILE));
 const int xy[][2]={{-1,0},{309,0},{0,-14},{0,200},{INT_MIN,INT_MAX}};for(unsigned i=0;i<5;i++){CHECK(!cash25_pickup(&screen,xy[i][0],xy[i][1],spriteSheet11,7,0,0,&c));CHECK(!popup(&screen,xy[i][0],xy[i][1],explosionSpriteSheet,185,MIRROR_BLEND,ENTITY_TILE,true));}
 for(int mode=0;mode<8;mode++){SDL_PixelFormat *fmt=screen.format;SDL_Surface old=screen;SDL_Surface *vg=VGAScreen;if(mode==0)screen.w=319;if(mode==1)screen.h=199;if(mode==2)screen.pitch=328;if(mode==3)screen.format=NULL;if(mode==4)format.BitsPerPixel=32;if(mode==5)format.BytesPerPixel=4;if(mode==6)VGAScreen=&other;if(mode==7)VGAScreen=NULL;CHECK(!cash25_pickup(&screen,98,100,spriteSheet11,7,0,0,&c));CHECK(!popup(&screen,98,100,explosionSpriteSheet,185,MIRROR_BLEND,ENTITY_TILE,true));screen=old;screen.format=fmt;format.BitsPerPixel=8;format.BytesPerPixel=1;VGAScreen=vg;}
 for(int mode=0;mode<6;mode++){game_probe_density=mode==0?1:mode==1?4:8;game_probe_missing=mode==2;game_probe_invalid=mode==3;game_probe_original_reference=mode==4;game_probe_assets=mode==5?NULL:full_pack;CHECK(!cash25_pickup(&screen,98,100,spriteSheet11,7,0,0,&c));CHECK(!popup(&screen,98,100,explosionSpriteSheet,185,MIRROR_NORMAL,ENTITY_TILE,true));}game_probe_density=8;game_probe_missing=game_probe_invalid=game_probe_original_reference=false;game_probe_assets=full_pack;CHECK(draws==saved);render_mirror_coin25_value_begin(true);render_mirror_entity_end();CHECK(!cash25_fixed_value);
}
static void *read_file(const char *path,size_t *size){FILE*f=fopen(path,"rb");CHECK(f&&!fseek(f,0,SEEK_END));long n=ftell(f);CHECK(n>0&&!fseek(f,0,SEEK_SET));void *p=malloc((size_t)n);CHECK(p&&fread(p,1,(size_t)n,f)==(size_t)n&&!fclose(f));*size=(size_t)n;return p;}
static void indexed_cases(const char *dir){char path[2048];size_t n;snprintf(path,sizeof(path),"%s/bank11.bin",dir);Uint8 *b11=read_file(path,&n);spriteSheet11=(Sprite2_array){b11,n};snprintf(path,sizeof(path),"%s/newsh6.bin",dir);Uint8 *b6=read_file(path,&n);explosionSpriteSheet=(Sprite2_array){b6,n};snprintf(path,sizeof(path),"%s/index-reference.bin",dir);Uint8 *ref=read_file(path,&n);CHECK(n==7*336);Uint8 *want=malloc(64000);CHECK(want);G101EnemyContext context={391,25,2,0,true,false,true,false};unsigned transactions=0;
 const int xy[][2]={{98,100},{0,-13},{308,-1},{0,199},{-1,100},{309,100}};
 for(int accepted=0;accepted<2;accepted++)for(int k=0;k<7;k++)for(int style=0;style<(k==6?2:1);style++)for(int p=0;p<6;p++){int x=xy[p][0],y=xy[p][1];for(int i=0;i<64000;i++)want[i]=((Uint8*)screen.pixels)[i]=(Uint8)(i*29+23);reset_area(x,y);game_probe_missing=!accepted;const Uint8 *r=ref+336*k;for(int py=0;py<14;py++)for(int px=0;px<12;px++){int i=py*12+px,a=(y+py)*320+x+px;if(r[168+i]&&a>=0&&a<64000)want[a]=style?(r[i]&240)|(((want[a]&15)+(r[i]&15))/2):r[i];}unsigned before=original_calls;if(k<6){bool hd=cash25_pickup(&screen,x,y,spriteSheet11,ids[k],0,0,&context);CHECK(hd==(accepted&&p<4));blit_sprite2(&screen,x,y,spriteSheet11,ids[k]);render_mirror_entity_end();}else{render_mirror_coin25_value_begin(true);draw_entity_sprite2(&screen,x,y,explosionSpriteSheet,185,style?ENTITY_BLEND:ENTITY_NORMAL,ENTITY_TILE);CHECK(!cash25_fixed_value);}CHECK(original_calls==before+1);CHECK(!memcmp(want,screen.pixels,64000));CHECK(!suppress);transactions++;}game_probe_missing=false;CHECK(transactions==96);free(want);free(b11);free(b6);free(ref);}
int main(int argc,char**argv){CHECK(argc==5);game_probe_assets=full_pack=argv[2];bool valid=atoi(argv[3])!=0;Uint8 tokens[5]={0};spriteSheet8=(Sprite2_array){tokens,1};spriteSheet9=(Sprite2_array){tokens+1,1};spriteSheet11=(Sprite2_array){tokens+2,1};spriteSheet12=(Sprite2_array){tokens+3,1};explosionSpriteSheet=(Sprite2_array){tokens+4,1};CHECK(sizeof(assets)/sizeof(*assets)==479);CHECK(cash25_family_ready()==valid);CHECK(cash25_checked&&cash25_valid==valid);CHECK(cash25_family_ready()==valid);for(int i=0;i<472;i++)CHECK(!assets[i].initialized);if(!strcmp(argv[1],"loader")){G101EnemyContext c={391,25,2,0,true,false,true,false};if(!valid){CHECK(!cash25_pickup(&screen,98,100,spriteSheet11,7,0,0,&c));CHECK(!popup(&screen,98,100,explosionSpriteSheet,185,MIRROR_NORMAL,ENTITY_TILE,true));CHECK(!cash25_fixed_value&&!draws&&!suppress);}clear_assets();printf("PASS coherent-family %d\n",valid);return 0;}CHECK(valid);start();for(int i=0;i<256;i++)rgb_palette[i]=(i*71%256)<<16|(i*31%256)<<8|(i*13%256);G101EnemyContext c={391,25,2,0,true,false,true,false};
 const int xy[][2]={{98,100},{0,-13},{308,-1},{0,199}};for(int k=0;k<7;k++)for(int b=0;b<(k==6?2:1);b++)for(int p=0;p<4;p++){int x=xy[p][0],y=xy[p][1];reset_area(x,y);CHECK(k<6?cash25_pickup(&screen,x,y,spriteSheet11,ids[k],0,0,&c):popup(&screen,x,y,explosionSpriteSheet,185,b?MIRROR_BLEND:MIRROR_NORMAL,ENTITY_TILE,true));CHECK(draws==1&&suppress);check_pixels(assets+472+k,x,y,b,0);render_mirror_entity_end();CHECK(!suppress);}
 for(int f=16;f<=240;f+=16){reset_area(98,100);CHECK(cash25_pickup(&screen,98,100,spriteSheet11,7,0,f,&c));check_pixels(assets+472,98,100,false,f);render_mirror_entity_end();}
 reset_area(98,100);guards();overlaps();
 /* Synthetic alpha values exercise unchanged underlay, all rounding and authored blend. */
 Uint8 *rgba=malloc(43008);CHECK(rgba);for(int k=0;k<7;k++){memcpy(rgba,assets[472+k].rgba,43008);Asset a=assets[472+k];a.rgba=rgba;for(int i=0;i<96*112;i++)rgba[4*i+3]=(Uint8[]){0,1,63,127,128,191,254,255}[i%8];for(int b=0;b<(k==6?2:1);b++){reset_area(98,100);CHECK(draw_asset(98,100,&a,b?MIRROR_BLEND:MIRROR_NORMAL,NULL));check_pixels(&a,98,100,b,0);}}
 /* Existing bank8 orb IDs and slots stay independent and healthy. */
 for(unsigned id=112;id<=113;id++){reset_area(98,100);CHECK(render_mirror_enemy_shot(&screen,98,100,spriteSheet8,id));CHECK(assets[218+id-112].bank==8&&assets[218+id-112].index==(int)id);render_mirror_entity_end();}
 indexed_cases(argv[4]);
 /* Alpha0 retains existing owner0 as well as owner1 and exact RGB. */
 reset_area(98,100);Asset zero=assets[478];zero.rgba=rgba;memset(rgba,0,43008);for(int py=0;py<112;py++)for(int px=0;px<96;px++)hd_owner[(100*8+py)*canvas->w+98*8+px]=0;CHECK(draw_asset(98,100,&zero,MIRROR_BLEND,NULL));for(int py=0;py<112;py++)for(int px=0;px<96;px++){int n=(100*8+py)*canvas->w+98*8+px;CHECK(((Uint32*)canvas->pixels)[n]==bg(n)&&hd_owner[n]==0&&cloud_owner[n]==1&&green_first[n]==7);}
 free(rgba);clear_assets();free(canvas->pixels);free(hd_owner);free(cloud_owner);free(green_first);free(green_under);free(green_under_owner);free(screen.pixels);printf("{\"status\":\"PASS\",\"checks\":%llu,\"pixel_checks\":%llu}\n",(unsigned long long)checks,(unsigned long long)pixels);return 0;}
