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

#define MIN(a,b) ((a)<(b)?(a):(b))
#define MAX(a,b) ((a)>(b)?(a):(b))
#include "types.inc"
static bool xmas;
static bool active=true,suppress,suppress_green_smoke,suppress_cloud,game_probe_missing,game_probe_invalid,game_probe_original_reference,game_probe_local_blend;
static const char *game_probe_assets,*reject_reason,*full_pack,*work;
static int game_probe_density=8;
static SDL_PixelFormat format={8,1};
static SDL_Surface screen={320,200,320,NULL,&format},display,*game_screen=&screen,*VGAScreen=&screen,*canvas=&display;
static Sprite2_array spriteSheet8,spriteSheet9,spriteSheet12,explosionSpriteSheet;
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
static void font_before_effect(SDL_Rect r){assert(r.w>0&&r.h>0);font_calls++;}
static bool font_pixel(int x,int y,Uint8 p,int style){(void)x;(void)y;(void)p;(void)style;return false;}
static bool game_probe_known_blend;
static Uint8 restored_mask[64000];
static unsigned local_blocks,local_regions,expanded_regions,boundary_crossings,blend_source_index;
static void game_probe_restore_region(unsigned source,SDL_Rect requested,SDL_Rect restored,unsigned groups,unsigned blocks)
{(void)source;(void)requested;(void)restored;(void)groups;(void)blocks;}
static Uint32 palette_rgb(Uint8 index);
static char all_rejections[512];
void render_mirror_unsupported(const char *s);
static Uint16 SDL_SwapLE16(Uint16 value){Uint8 b[2];memcpy(b,&value,2);return (Uint16)(b[0]|(unsigned)b[1]<<8);}

static void game_probe_scene_draw(int,unsigned,int,int,int,int,bool);
static bool cash25_fixed_value,cash75_fixed_value,cash50_fixed_value,gem100_fixed_value,gem250_fixed_value;
#define cash25_surface_ready(...) (assert(0),false)
#define cash25_family_ready() (assert(0),false)
#define cash75_family_ready() (assert(0),false)
#define cash50_family_ready() (assert(0),false)
#define gem100_family_ready() (assert(0),false)
#define gem250_family_ready() (assert(0),false)
#define enemy_tank_shell_family_ready() (assert(0),false)
#define pregame_font_sprite2_begin(...) ((void)0)
#define pregame_font_sprite2_end(...) ((void)0)
#define selector_font_pixel(...) ((void)0)
#define pregame_font_pixel(...) ((void)0)

#define render_mirror_entity_end production_end
#include "functions.inc"
#undef render_mirror_entity_end
static void render_mirror_entity_end(void){end_calls++;production_end();}
static void asset_debug_effect(SDL_Surface*s,Sprite2_array b,unsigned id,int x,int y){assert(s&&b.data&&id);(void)x;(void)y;original_calls++;}
static void observed_pixel(SDL_Surface*,Uint8*,Uint8,int);
#define render_mirror_pixel observed_pixel
#include "blitters.inc"
#undef render_mirror_pixel
#define blit_sprite2_blend(...) assert(0)
#define blit_sprite2x2(...) assert(0)
#define blit_sprite2x2_blend(...) assert(0)
#define blit_sprite2x2_darken(...) assert(0)
static void game_probe_scene_draw(int role,unsigned id,int x,int y,int part,int style,bool mirrored){assert(part==0&&style==ENTITY_NORMAL);scene_calls++;log_role=role;log_id=id;log_x=x;log_y=y;log_mirrored=mirrored;}
static void game_probe_draw(int role,unsigned id,int x,int y,int style,int layout,bool mirrored){assert(role==8&&layout==ENTITY_TILE);(void)style;player_calls++;log_role=role;log_id=id;log_x=x;log_y=y;log_mirrored=mirrored;}
#include "wrappers.inc"
#include "variants.inc"
#ifndef BASELINE
#define BASELINE 0
#endif
/* Bounded adaptation of the existing missile and enemy-energy unit tests. */
enum {W=320,H=200,SCREEN=W*H,PAD=16384,REF=336+43008,NREF=28};
static const unsigned ids[NREF]={121,122,163,164,201,202,279,280,58,59,67,70,121,122,163,164,201,202,279,280,58,59,67,70,163,164,163,164};
static Uint8 references[NREF][REF],index_ref[328*H],selection_ref[SCREEN],*index_storage,*owner_ref,*cloud_ref;
static Uint16 *first_ref;static Uint32 *color_ref;
static unsigned area[4096],area_count;static bool seen[SCREEN];
static unsigned cases,accepted_cases,fallback_cases,binding_cases,cache_cases,guard_cases,full_comparisons,blend_cases;
static unsigned observed_count,write_count,write_offsets[168],isolation_cases,lease_cases,identity_cases,overlap_cases;
static Uint8 write_values[168];static bool observing;
static uint64_t shadow_fingerprint=UINT64_C(0xcbf29ce484222325);
static uint64_t comparisons,alpha_cases;static char pack_path[2048];
static void *read_file(const char *name,size_t *len)
{FILE*f=fopen(name,"rb");assert(f&&!fseek(f,0,SEEK_END));long n=ftell(f);assert(n>0&&!fseek(f,0,SEEK_SET));Uint8*p=malloc((size_t)n);assert(p&&fread(p,1,(size_t)n,f)==(size_t)n&&!fclose(f));*len=(size_t)n;return p;}
static void clear_assets(void)
{for(unsigned i=0;i<sizeof(assets)/sizeof(*assets);i++){free(assets[i].rgba);memset(assets+i,0,sizeof(*assets));}for(unsigned i=0;i<13;i++){free(talon_frames[i].rgba);memset(talon_frames+i,0,sizeof(*talon_frames));}enemy_energy_checked=enemy_energy_valid=false;vulcan_shadow_clear();memset(vulcan_shadow_resource,0,sizeof(vulcan_shadow_resource));}
static void select_pack(const char *name)
{snprintf(pack_path,sizeof(pack_path),"%s/%s",work,name);game_probe_assets=pack_path;}
static Uint32 initial_color(unsigned n){return 0xff000000u|((n*2654435761u+0x594123u)&0xffffffu);}
static Uint32 *pixel(unsigned n){return (Uint32*)((Uint8*)canvas->pixels+(n/(unsigned)canvas->w)*canvas->pitch)+n%(unsigned)canvas->w;}
static void init_cell(int a)
{
 int d=game_probe_density,x=a%W,y=a/W,pa=y*screen.pitch+x;
 index_ref[pa]=expected[a]=((Uint8*)screen.pixels)[pa]=(Uint8)(a*29+23);selection_ref[a]=selected[a]=0;
 for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++){
  int n=(y*d+sy)*canvas->w+x*d+sx;color_ref[n]=*pixel(n)=initial_color((unsigned)n);
  owner_ref[n]=hd_owner[n]=(Uint8)(n%3);cloud_ref[n]=cloud_owner[n]=(Uint8)(n&1);
  first_ref[n]=green_first[n]=(Uint16)(n%4);green_under[n]=initial_color((unsigned)n+19);green_under_owner[n]=(Uint8)(n%3);
 }
}
static void allocate(int d,int indexed_pitch,int rgba_padding)
{
 game_probe_density=d;screen.pitch=indexed_pitch;canvas->w=W*d;canvas->h=H*d;canvas->pitch=canvas->w*4+rgba_padding;
 size_t n=(size_t)canvas->w*canvas->h;canvas->pixels=malloc((size_t)canvas->pitch*canvas->h);memset(canvas->pixels,0xa9,(size_t)canvas->pitch*canvas->h);
 color_ref=malloc(n*4);hd_owner=malloc(n);owner_ref=malloc(n);cloud_owner=malloc(n);cloud_ref=malloc(n);green_first=malloc(n*2);first_ref=malloc(n*2);green_under=malloc(n*4);green_under_owner=malloc(n);
 assert(canvas->pixels&&color_ref&&hd_owner&&owner_ref&&cloud_owner&&cloud_ref&&green_first&&first_ref&&green_under&&green_under_owner);
 memset(index_storage,0xa9,328*H+2*PAD);memset(index_ref,0xa9,sizeof(index_ref));for(int a=0;a<SCREEN;a++)init_cell(a);
}
static void release(void)
{free(canvas->pixels);free(color_ref);free(hd_owner);free(owner_ref);free(cloud_owner);free(cloud_ref);free(green_first);free(first_ref);free(green_under);free(green_under_owner);}
static void begin_area(int x,int y,bool reset)
{
 if(reset){memset(seen,0,sizeof(seen));area_count=region_count=green_head_count=0;}
 for(int py=-1;py<15;py++)for(int px=-1;px<13;px++){
  int pa=(y+py)*screen.pitch+x+px;if(pa<0||pa>=screen.pitch*H||pa%screen.pitch>=W)continue;
  int a=(pa/screen.pitch)*W+pa%screen.pitch;if(!seen[a]){assert(area_count<4096);seen[a]=true;area[area_count++]=(unsigned)a;init_cell(a);}
 }
 production_end();
}
static void check_area(void)
{
 int d=game_probe_density;
 for(unsigned k=0;k<area_count;k++){
  int a=(int)area[k],x=a%W,y=a/W,pa=y*screen.pitch+x;assert(index_ref[pa]==((Uint8*)screen.pixels)[pa]);assert(expected[a]==index_ref[pa]);assert(selected[a]==selection_ref[a]);
  for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++){
   int n=(y*d+sy)*canvas->w+x*d+sx;assert(color_ref[n]==*pixel(n));assert(owner_ref[n]==hd_owner[n]&&cloud_ref[n]==cloud_owner[n]&&first_ref[n]==green_first[n]);
   assert(green_under[n]==initial_color((unsigned)n+19)&&green_under_owner[n]==n%3);comparisons++;
  }
 }
 for(int i=0;i<PAD;i++)assert(index_storage[i]==0xa9&&index_storage[PAD+328*H+i]==0xa9);
}
static void check_all(void)
{
 assert(!memcmp(index_ref,screen.pixels,(size_t)screen.pitch*H));assert(!memcmp(selected,selection_ref,SCREEN));
 for(int y=0;y<H;y++)for(int x=0;x<W;x++)assert(expected[y*W+x]==index_ref[y*screen.pitch+x]);
 size_t n=(size_t)canvas->w*canvas->h;for(size_t p=0;p<n;p++)assert(color_ref[p]==*pixel((unsigned)p));
 assert(!memcmp(owner_ref,hd_owner,n)&&!memcmp(cloud_ref,cloud_owner,n)&&!memcmp(first_ref,green_first,n*2));
 for(int y=0;y<canvas->h;y++)for(int b=canvas->w*4;b<canvas->pitch;b++)assert(((Uint8*)canvas->pixels)[y*canvas->pitch+b]==0xa9);
 full_comparisons++;
}
static Uint32 blend_oracle(Uint32 dst,const Uint8 *src)
{Uint32 out=0xff000000u;for(int c=0;c<3;c++){unsigned shift=16-c*8,n=((dst>>shift)&255)*(255-src[3])+src[c]*src[3];out|=(n/255+(n%255>=128))<<shift;}return out;}
static Uint32 dark_oracle(Uint32 dst,unsigned alpha)
{Uint32 out=0xff000000u;for(unsigned shift=0;shift<24;shift+=8){unsigned n=((dst>>shift)&255)*(510-alpha);out|=(n/510+(n%510>=255))<<shift;}return out;}
static Uint32 cloud_shadow_oracle(Uint32 dst,Uint8 before,Uint8 after)
{if(before==after)return dst;Uint32 out=0xff000000u;for(unsigned shift=0;shift<24;shift+=8){unsigned den=(rgb_palette[before]>>shift)&255,num=((dst>>shift)&255)*((rgb_palette[after]>>shift)&255),v=den?num/den+(num%den>=(den+1)/2):((dst>>shift)&255);out|=MIN(v,255u)<<shift;}return out;}
static void oracle_asset(const Uint8 *rgba,int x,int y,bool shadow,int ad)
{
 int d=game_probe_density;
 for(int ay=0;ay<14*d;ay++)for(int ax=0;ax<12*d;ax++){
  int dx=x*d+ax,dy=y*d+ay;if(dx<0||dy<0||dx>=canvas->w||dy>=canvas->h)continue;
  const Uint8*s=rgba+4*(((ay*ad/d)*8/ad)*96+(ax*ad/d)*8/ad);if(!s[3])continue;int n=dy*canvas->w+dx;
  if(shadow&&owner_ref[n]!=1){Uint8 ci=index_ref[(dy/d)*screen.pitch+dx/d];Uint32 dark=rgb_palette[(ci&0xf0)|((ci&15)/2)];Uint8 q[4]={(dark>>16)&255,(dark>>8)&255,dark&255,s[3]};color_ref[n]=blend_oracle(color_ref[n],q);}
  else color_ref[n]=shadow?dark_oracle(color_ref[n],s[3]):blend_oracle(color_ref[n],s);
  owner_ref[n]=game_probe_original_reference?2:1;cloud_ref[n]=0;first_ref[n]=0;selection_ref[(dy/d)*W+dx/d]=1;
 }
}
static void oracle_original(unsigned k,int x,int y,bool accepted,bool shadow)
{
 int d=game_probe_density;
 for(int py=0;py<14;py++)for(int px=0;px<12;px++){
  int cell=py*12+px;if(!references[k][168+cell])continue;int pa=(y+py)*screen.pitch+x+px;if(pa<0||pa>=screen.pitch*H)continue;
  Uint8 before=index_ref[pa],v=shadow?(Uint8)((before&0xf0)|((before&15)/2)):references[k][cell];index_ref[pa]=v;
  if(!active||pa%screen.pitch>=W)continue;int a=(pa/screen.pitch)*W+pa%screen.pitch;assert(seen[a]);
  if(reject_reason)continue;selection_ref[a]=(Uint8)accepted;
  for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++){
   int n=((a/W)*d+sy)*canvas->w+(a%W)*d+sx;
   if(accepted){owner_ref[n]=game_probe_original_reference?2:1;cloud_ref[n]=0;}
   else{bool cloud=shadow&&cloud_ref[n]&&owner_ref[n]==1;first_ref[n]=0;if(!cloud)cloud_ref[n]=0;color_ref[n]=cloud?cloud_shadow_oracle(color_ref[n],before,v):shadow&&owner_ref[n]==1?dark_oracle(color_ref[n],255):0xff000000u|rgb_palette[v];if(!shadow)owner_ref[n]=0;}
  }
 }
}
static void oracle_smooth(unsigned k,int x,int y)
{
 for(int ay=0;ay<112;ay++)for(int ax=0;ax<96;ax++) {
  int dx=x*8+ax,dy=y*8+ay;if(dy<0||dy>=canvas->h)continue;
  unsigned alpha=references[k][336+4*(ay*96+ax)+3];if(!alpha)continue;
  int n=dy*canvas->w+dx,a=(dy/8)*W+dx/8;
  Uint8 before=index_ref[(dy/8)*screen.pitch+dx/8],after=(before&0xf0)|((before&15)/2);
  Uint32 target=owner_ref[n]==1?(cloud_ref[n]?cloud_shadow_oracle(color_ref[n],before,after):dark_oracle(color_ref[n],255)):0xff000000u|rgb_palette[after];
  Uint8 q[4]={(target>>16)&255,(target>>8)&255,target&255,(Uint8)alpha};
  Uint32 next=blend_oracle(color_ref[n],q);if(next!=color_ref[n]){owner_ref[n]=1;selection_ref[a]=1;}
  color_ref[n]=next;first_ref[n]=0;
 }
}
static void oracle_smooth_original(unsigned k,int x,int y)
{
 for(int py=0;py<14;py++)for(int px=0;px<12;px++) {
  if(!references[k][168+py*12+px])continue;
  int pa=(y+py)*screen.pitch+x+px;if(pa<0||pa>=screen.pitch*H)continue;
  Uint8 before=index_ref[pa],after=(before&0xf0)|((before&15)/2);index_ref[pa]=after;
  int a=(pa/screen.pitch)*W+pa%screen.pitch;
  if(before!=after)selection_ref[a]=1;
  for(int sy=0;sy<8;sy++)for(int sx=0;sx<8;sx++) {
   int n=((a/W)*8+sy)*canvas->w+(a%W)*8+sx;
   if(before!=after)owner_ref[n]=1;first_ref[n]=0;
  }
 }
}
static void observed_pixel(SDL_Surface *s,Uint8 *p,Uint8 source,int style)
{
 if(observing){assert(s==&screen&&observed_count<write_count);assert(p==(Uint8*)screen.pixels+write_offsets[observed_count]);assert(*p==write_values[observed_count]);observed_count++;}
 render_mirror_pixel(s,p,source,style);
}
static void prepare_writes(unsigned k,int x,int y,bool shadow)
{
 observed_count=write_count=0;
 for(int cy=0;cy<14;cy++)for(int cx=0;cx<12;cx++){
  int cell=cy*12+cx;if(!references[k][168+cell])continue;
  int pa=(y+cy)*screen.pitch+x+cx;if(pa<0||pa>=screen.pitch*H)continue;
  write_offsets[write_count]=(unsigned)pa;Uint8 before=index_ref[pa];
  write_values[write_count++]=shadow?(before&0xf0)|((before&15)/2):references[k][cell];
 }
 observing=true;
}
static bool smooth(unsigned k){return ids[k]==67||ids[k]==70;}
static void execute(unsigned k,int x,int y,bool accepted,bool shadow,int mode)
{
 unsigned before=original_calls,ends=end_calls,logs=player_calls,scenes=scene_calls,old_draws=draws;
 Uint8 *allocation=spriteSheet8.data;size_t allocation_size=spriteSheet8.size;
 prepare_writes(k,x,y,shadow);
 if(mode==1){if(shadow)blit_sprite2_darken(&screen,x,y,spriteSheet8,ids[k]);else blit_sprite2(&screen,x,y,spriteSheet8,ids[k]);}
 else if(mode==2)draw_enemy_shot_sprite2(&screen,x,y,spriteSheet8,ids[k]);
 else draw_entity_sprite2(&screen,x,y,spriteSheet8,ids[k],shadow?ENTITY_SHADOW:ENTITY_NORMAL,ENTITY_TILE);
 observing=false;assert(observed_count==write_count);
 assert(original_calls==before+1&&end_calls==ends+(unsigned)(mode!=1)&&draws==old_draws+(unsigned)accepted);
 assert(!suppress&&!suppress_cloud&&!suppress_green_smoke&&!vulcan_shadow.live);
 assert(spriteSheet8.data==allocation&&spriteSheet8.size==allocation_size);
 if(mode==0)assert(player_calls==logs+1&&log_id==ids[k]&&log_x==x&&log_y==y&&log_mirrored==accepted&&log_role==8);
 if(mode==2){bool energy=enemy_energy_slot(ids[k])>=0;assert(scene_calls==scenes+(unsigned)energy&&player_calls==logs);if(energy)assert(log_role==111&&log_id==ids[k]&&log_mirrored==accepted);}
 if(accepted&&shadow&&smooth(k)){oracle_smooth(k,x,y);oracle_smooth_original(k,x,y);}
 else {
  if(accepted){Asset*a=mode==2?&assets[enemy_energy_slot(ids[k])]:get_asset(spriteSheet8,ids[k],ENTITY_TILE);assert(a&&a->valid);oracle_asset(references[k]+336,x,y,shadow,a->density);}
  oracle_original(k,x,y,accepted,shadow);
 }
 check_area();cases++;accepted_cases+=accepted;fallback_cases+=!accepted;
}
static void transaction(unsigned k,int x,int y,bool accepted,bool shadow,int mode,bool reset)
{begin_area(x,y,reset);execute(k,x,y,accepted,shadow,mode);}
/* Independent finite enumeration inherited from the regular-missile proof. */
static int expected_slot(int bank,unsigned id,int layout)
{
 if(bank==0&&layout==ENTITY_TILE){
  if(!xmas){if(id==67)return 522;if(id==70)return 523;}
  if(!BASELINE&&!xmas)for(int k=0;k<8;k++)if(id==ids[k])return 524+k;
  if(!xmas){if(id==225)return 469;if(id==244)return 470;if(id==226)return 471;}
  if(id>=31&&id<=33)return 333+(int)id-31;
  if(id>=252&&id<=254)return 330+(int)id-252;
  if(id==59)return 5;if(id==103)return 325;
  const unsigned pulse[]={58,60,62,165},guided[]={19,171,20,21};
  for(int i=0;i<4;i++){if(id==pulse[i])return 321+i;if(id==guided[i])return 326+i;}
  if(id>=214&&id<=217)return 182+(int)id-214;
 }
 if(bank==1&&layout==ENTITY_QUAD&&id>=229&&id<=237&&id%2==1)return ((int)id-229)/2;
 if(bank==3&&layout==ENTITY_TILE){
  const int ranges[][3]={{122,133,31},{3,14,43},{41,52,55},{22,33,67},{60,71,79},{146,152,91},{192,203,98},{154,165,110},{211,222,122},{173,184,134},{135,141,146},{78,84,175}};
  for(unsigned i=0;i<sizeof(ranges)/sizeof(*ranges);i++)if(id>=(unsigned)ranges[i][0]&&id<=(unsigned)ranges[i][1])return ranges[i][2]+(int)id-ranges[i][0];
  const unsigned shield[]={229,230,231,232,233,234,235,236,237,248,249,250,252,253,254,255,256,267,268,269,272,275};
  for(int i=0;i<22;i++)if(id==shield[i])return 153+i;
 }
 return -1;
}
static void finite_bindings(void)
{
 assert(sizeof(assets)/sizeof(*assets)==(BASELINE?524:532));Uint8 token;
 Sprite2_array banks[]={spriteSheet8,spriteSheet9,spriteSheet12,explosionSpriteSheet,{&token,1},{NULL,0}};const int layouts[]={ENTITY_TILE,ENTITY_QUAD,-1,2};
 for(int christmas=0;christmas<2;christmas++)for(int b=0;b<6;b++)for(int l=0;l<4;l++)for(unsigned n=0;n<601;n++){
  clear_assets();xmas=christmas;game_probe_invalid=true;unsigned id=n==600?UINT_MAX:n;int layout=layouts[l],slot=expected_slot(b,id,layout);
  assert(!get_asset(banks[b],id,layout));unsigned initialized=0;
  for(unsigned s=0;s<sizeof(assets)/sizeof(*assets);s++)if(assets[s].initialized){Asset*a=assets+s;initialized++;assert((int)s==slot&&!a->valid&&a->index==(int)id);assert(a->bank==(b==0?8:b==1?9:ASSET_EXPLOSION));assert(a->w==(layout==ENTITY_QUAD?24:12)&&a->h==(layout==ENTITY_QUAD?28:14));assert(a->anchor_x==(b==1?5:b==0&&id==59?-1:0)&&a->anchor_y==(b==1?7:0));}
  assert(initialized==(unsigned)(slot>=0));binding_cases++;
 }
 clear_assets();xmas=game_probe_invalid=false;
}
static void metadata_cache(void)
{
 const unsigned prior[]={252,253,254,19,171,20,21,58,60,62,165,103,59,214,215,216,217,31,32,33,225,244,226,67,70};
 for(unsigned i=0;i<sizeof(prior)/sizeof(*prior);i++){
  unsigned id=prior[i];Asset*a=get_asset(spriteSheet8,id,ENTITY_TILE);assert(a==assets+expected_slot(0,id,ENTITY_TILE)&&a->valid&&a->bank==8&&a->index==(int)id&&a->density==8&&a->w==12&&a->h==14&&a->anchor_x==(id==59?-1:0)&&!a->anchor_y);cache_cases++;
 }
 for(unsigned k=8;k<12;k++){Asset*a=get_asset(spriteSheet8,ids[k],ENTITY_TILE);assert(!memcmp(a->rgba,references[k]+336,43008));cache_cases++;}
 if(BASELINE){for(unsigned k=0;k<8;k++)assert(!get_asset(spriteSheet8,ids[k],ENTITY_TILE));clear_assets();return;}
 for(unsigned k=0;k<8;k++){
  Asset*a=get_asset(spriteSheet8,ids[k],ENTITY_TILE);assert(a==assets+524+k&&a->initialized&&a->valid&&a->bank==8&&a->index==(int)ids[k]&&a->w==12&&a->h==14&&!a->anchor_x&&!a->anchor_y&&a->density==8);assert(!memcmp(a->rgba,references[k]+336,43008));
  Uint8*rgba=a->rgba;xmas=true;assert(!get_asset(spriteSheet8,ids[k],ENTITY_TILE));assert(a->rgba==rgba&&a->valid);xmas=false;assert(get_asset(spriteSheet8,ids[k],ENTITY_TILE)==a&&a->rgba==rgba);cache_cases++;
 }
 clear_assets();for(int k=7;k>=0;k--){Asset*a=get_asset(spriteSheet8,ids[k],ENTITY_TILE);assert(a==assets+524+k&&!memcmp(a->rgba,references[k]+336,43008));cache_cases++;}
 clear_assets();xmas=true;for(unsigned k=0;k<8;k++){assert(!get_asset(spriteSheet8,ids[k],ENTITY_TILE));assert(!assets[524+k].initialized);cache_cases++;}xmas=false;
 clear_assets();
}
static void fallback_variants(void)
{
 for(unsigned v=0;v<sizeof(variants)/sizeof(*variants);v++){
  clear_assets();select_pack(variants[v]);
  for(unsigned k=0;k<8;k++){
   bool ok=!BASELINE&&variant_valid[v][k];transaction(k,94,73,ok,false,0,true);
   if(!BASELINE){assert(assets[524+k].initialized);if(ok)assert(assets[524+k].density==variant_density[v][k]);}
  }
  for(unsigned k=8;k<12;k++){transaction(k,94,73,true,false,0,true);transaction(k,94,73,true,true,0,true);}
  /* Positive/negative ordinary caches retain their startup-root lifetime. */
  game_probe_assets=full_pack;
  for(unsigned k=0;k<8;k++)transaction(k,94,73,!BASELINE&&variant_valid[v][k],false,0,true);
 }
 clear_assets();game_probe_assets=full_pack;
}
static void test_guards(void)
{
 SDL_Surface other=screen;Uint8 token;Sprite2_array wrong={&token,1},null={NULL,0};
 for(unsigned k=0;k<8;k++)for(int gate=0;gate<8;gate++){
  clear_assets();unsigned before=draws;active=gate!=0;reject_reason=gate==1?"fixture":NULL;xmas=gate==2;game_probe_density=gate==3?1:8;game_probe_missing=gate==4;
  Sprite2_array b=gate==5?wrong:gate==6?null:spriteSheet8;
  assert(!render_mirror_entity(gate==7?&other:&screen,7,11,b,ids[k],MIRROR_NORMAL,ENTITY_TILE));assert(draws==before&&!suppress&&!suppress_green_smoke&&!suppress_cloud);guard_cases++;
  if(!BASELINE)assert(!assets[524+k].initialized);
 }
 active=true;reject_reason=NULL;xmas=game_probe_missing=false;game_probe_density=8;clear_assets();
}
static void exact_shadow_guard(void)
{
 for(unsigned k=0;k<8;k++)for(int warm=0;warm<2;warm++){
  clear_assets();if(warm)(void)get_asset(spriteSheet8,ids[k],ENTITY_TILE);
  Asset before[532];memset(before,0,sizeof(before));memcpy(before,assets,sizeof(assets));
  transaction(k,94,73,false,true,0,true);
  assert(!memcmp(before,assets,sizeof(assets)));
  for(unsigned a=0;a<area_count;a++){
   int logical=(int)area[a],x=logical%W,y=logical/W;shadow_fingerprint^=index_ref[y*screen.pitch+x];shadow_fingerprint*=UINT64_C(0x100000001b3);
   for(int sy=0;sy<8;sy++)for(int sx=0;sx<8;sx++){
    unsigned n=(y*8+sy)*(unsigned)canvas->w+x*8+sx;shadow_fingerprint^=color_ref[n];shadow_fingerprint*=UINT64_C(0x100000001b3);
    shadow_fingerprint^=owner_ref[n]|(unsigned)cloud_ref[n]<<8;shadow_fingerprint*=UINT64_C(0x100000001b3);
   }
  }
  guard_cases++;
 }
 clear_assets();
}
static void test_identity(Sprite2_array normal,Sprite2_array christmas)
{
 Sprite2_array copy=normal;copy.data=malloc(copy.size);assert(copy.data);memcpy(copy.data,normal.data,copy.size);
 for(int warm=0;warm<2;warm++)for(unsigned k=0;k<8;k++){
  clear_assets();spriteSheet8=normal;xmas=false;
  if(warm)(void)get_asset(normal,ids[k],ENTITY_TILE);
  Asset before[532];memset(before,0,sizeof(before));memcpy(before,assets,sizeof(assets));
  assert(!get_asset(copy,ids[k],ENTITY_TILE));assert(!memcmp(before,assets,sizeof(assets)));
  spriteSheet8=copy;assert(!get_asset(normal,ids[k],ENTITY_TILE));
  transaction(k,94,73,!BASELINE,false,0,true);transaction(k,94,73,false,true,0,true);
  xmas=true;spriteSheet8=christmas;transaction(k+12,94,73,false,false,0,true);transaction(k+12,94,73,false,true,0,true);
  transaction(k+12,94,73,false,false,1,true);transaction(k+12,94,73,false,true,1,true);
  xmas=false;spriteSheet8=normal;transaction(k,94,73,!BASELINE,false,0,true);identity_cases++;
 }
 clear_assets();free(copy.data);spriteSheet8=normal;xmas=false;
}
static void test_isolation(Sprite2_array normal,Sprite2_array christmas)
{
 for(int christmas_mode=0;christmas_mode<2;christmas_mode++)for(int warm=0;warm<2;warm++)for(int reverse=0;reverse<2;reverse++)for(int member=0;member<2;member++){
  clear_assets();xmas=christmas_mode;spriteSheet8=xmas?christmas:normal;
  unsigned player=(unsigned)(2+member)+(xmas?12u:0u),enemy=24u+(unsigned)member+(xmas?2u:0u);
  bool player_ok=!BASELINE&&!xmas,enemy_ok=screen.pitch==320;
  if(warm){transaction(player,94,73,player_ok,false,0,true);transaction(enemy,94,73,enemy_ok,false,2,true);}
  for(int i=0;i<2;i++)if((i==0)!=reverse)transaction(player,94,73,player_ok,false,0,true);else transaction(enemy,94,73,enemy_ok,false,2,true);
  if(enemy_ok){Asset*a=&assets[member?468:465];assert(a->valid&&a->bank==111&&a->index==(int)ids[player]&&a->w==12&&a->h==14&&a->density==8&&!a->anchor_x&&!a->anchor_y&&!memcmp(a->rgba,references[enemy]+336,43008));
   if(player_ok){Asset*p=&assets[526+member];assert(p!=a&&p->rgba!=a->rgba&&p->bank==8&&!memcmp(p->rgba,references[player]+336,43008));}}
  if(!BASELINE&&xmas)assert(!assets[526+member].initialized);
  for(unsigned k=0;k<8;k++)if(k!=2&&k!=3)transaction(k+(xmas?12u:0u),94,73,false,false,2,true);
  for(unsigned slot=507;slot<522;slot++)assert(!assets[slot].initialized);isolation_cases++;
 }
 spriteSheet8=normal;xmas=false;clear_assets();
}
static void test_cross_mode_caches(Sprite2_array normal,Sprite2_array christmas)
{
 for(int reverse=0;reverse<2;reverse++)for(int member=0;member<2;member++){
  clear_assets();spriteSheet8=normal;xmas=false;bool enemy_ok=screen.pitch==320;
  for(int call=0;call<2;call++)if((call==0)!=reverse)transaction(2+member,94,73,!BASELINE,false,0,true);else transaction(24+member,94,73,enemy_ok,false,2,true);
  Uint8*player=BASELINE?NULL:assets[526+member].rgba,*enemy=assets[member?468:465].rgba;
  spriteSheet8=christmas;xmas=true;
  for(int call=0;call<2;call++)if((call==0)!=reverse)transaction(14+member,94,73,false,false,0,true);else transaction(26+member,94,73,enemy_ok,false,2,true);
  if(!BASELINE)assert(assets[526+member].rgba==player);
  if(enemy_ok)assert(assets[member?468:465].rgba==enemy);
  for(unsigned old=20;old<22;old++){transaction(old,94,73,true,false,0,true);transaction(old,94,73,true,true,0,true);}
  spriteSheet8=normal;xmas=false;
  transaction(2+member,94,73,!BASELINE,false,0,true);transaction(24+member,94,73,enemy_ok,false,2,true);isolation_cases++;
 }
 clear_assets();
}
static void test_vulcan_resources(void)
{
 for(unsigned v=0;v<sizeof(vulcan_variants)/sizeof(*vulcan_variants);v++){
  clear_assets();select_pack(vulcan_variants[v]);
  for(unsigned k=0;k<8;k++){transaction(k,94,73,!BASELINE,false,0,true);transaction(k,94,73,false,true,0,true);}
  for(unsigned old=10;old<12;old++){
   bool head=vulcan_head_valid[v][old-10],shadow=vulcan_shadow_valid[v][old-10];
   transaction(old,94,73,shadow,true,0,true);
   bool payload=strstr(vulcan_variants[v],"payload")&&!shadow;
   if(payload)references[old][336+3]^=1;
   transaction(old,94,73,head,false,0,true);
   if(payload)references[old][336+3]^=1;
   transaction(old,94,73,shadow,true,0,true);lease_cases++;
  }
  game_probe_assets=full_pack;
  for(unsigned old=10;old<12;old++)transaction(old,94,73,false,true,0,true);
 }
 clear_assets();game_probe_assets=full_pack;
}
static void test_overlap(void)
{
 for(unsigned a=0;a<8;a++)for(unsigned b=0;b<8;b++)for(int reverse=0;reverse<2;reverse++){
  begin_area(94,73,true);begin_area(96,75,false);
  if(!reverse){execute(a,94,73,!BASELINE,false,0);execute(b,96,75,!BASELINE,false,0);}
  else {execute(b,96,75,!BASELINE,false,0);execute(a,94,73,!BASELINE,false,0);}
  execute(a,94,73,false,true,0);execute(b,96,75,false,false,1);overlap_cases++;
 }
 for(unsigned k=0;k<8;k++)for(unsigned old=8;old<12;old++)for(int reverse=0;reverse<2;reverse++){
  begin_area(94,73,true);begin_area(96,75,false);
  if(reverse){execute(k,94,73,!BASELINE,false,0);execute(old,96,75,true,false,0);}
  else {execute(old,96,75,true,false,0);execute(k,94,73,!BASELINE,false,0);}
  execute(k,94,73,false,true,0);execute(old,96,75,true,true,0);overlap_cases++;
 }
 check_all();
}
static void prime_vulcan(unsigned k)
{
 assert(k==10||k==11);unsigned before=draws;
 assert(render_mirror_entity(&screen,94,73,spriteSheet8,ids[k],MIRROR_SHADOW,ENTITY_TILE));
 assert(vulcan_shadow.live&&!vulcan_shadow.entered&&draws==before);
}
static void reset_after_abort(void)
{reject_reason=NULL;production_end();for(int a=0;a<SCREEN;a++)init_cell(a);region_count=0;}
static void test_vulcan_interleaving(Sprite2_array normal,Sprite2_array christmas)
{
 for(unsigned old=10;old<12;old++)for(unsigned k=0;k<8;k++)for(int shadow=0;shadow<2;shadow++){
  begin_area(94,73,true);prime_vulcan(old);execute(k,94,73,!BASELINE&&!shadow,shadow,0);assert(!vulcan_shadow.live&&!reject_reason);lease_cases++;
  execute(old,94,73,true,true,0);execute(k,94,73,!BASELINE,false,0);execute(old,94,73,true,true,0);lease_cases++;
  /* Entered but incomplete shadow must reject at the next target boundary. */
  begin_area(94,73,true);prime_vulcan(old);render_mirror_shadow_begin(&screen,94,73,spriteSheet8,ids[old]);assert(vulcan_shadow.entered);
  assert(!render_mirror_entity(&screen,94,73,spriteSheet8,ids[k],shadow?MIRROR_SHADOW:MIRROR_NORMAL,ENTITY_TILE));
  assert(!vulcan_shadow.live&&reject_reason&&!strcmp(reject_reason,"incomplete-vulcan-shadow-command"));reset_after_abort();lease_cases++;
 }
 for(unsigned old=10;old<12;old++){
  transaction(old,94,73,true,true,0,true);Asset*a=get_asset(spriteSheet8,ids[old],ENTITY_TILE);assert(a);
  Uint8 saved=a->rgba[3];a->rgba[3]^=1;transaction(old,94,73,false,true,0,true);a->rgba[3]=saved;
  const char*root=game_probe_assets;select_pack("missing-all");transaction(old,94,73,false,true,0,true);game_probe_assets=root;
  size_t off=normal.data[2*(ids[old]-1)]|((size_t)normal.data[2*(ids[old]-1)+1]<<8);while(!(normal.data[off]>>4))off++;
  saved=normal.data[off+1];normal.data[off+1]^=1;assert(!render_mirror_entity(&screen,94,73,spriteSheet8,ids[old],MIRROR_SHADOW,ENTITY_TILE));normal.data[off+1]=saved;
  transaction(old,94,73,true,true,0,true);
  xmas=true;transaction(old,94,73,false,true,0,true);spriteSheet8=christmas;transaction(old+12,94,73,false,true,0,true);
  xmas=false;spriteSheet8=normal;transaction(old,94,73,true,true,0,true);lease_cases+=6;
  /* A pending lease must not accept a coincident source allocation. */
  Sprite2_array copy=normal;copy.data=malloc(copy.size);assert(copy.data);memcpy(copy.data,normal.data,copy.size);
  begin_area(94,73,true);prime_vulcan(old);render_mirror_shadow_begin(&screen,94,73,copy,ids[old]);assert(!vulcan_shadow.live&&!reject_reason);check_area();free(copy.data);lease_cases++;
 }
 clear_assets();
}
static void blend_fallback(void)
{
 if(BASELINE)return;
 for(unsigned k=0;k<8;k++)for(int local=0;local<2;local++){
  clear_assets();game_probe_assets=full_pack;transaction(k,94,73,true,false,false,true);unsigned before=draws;game_probe_local_blend=local;
  assert(!render_mirror_entity(&screen,94,73,spriteSheet8,ids[k],MIRROR_BLEND,ENTITY_TILE));assert(draws==before&&!suppress);
  if(local){
   assert(!reject_reason);
   for(int y=73;y<87;y++)for(int x=94;x<106;x++){
    int a=y*W+x;selection_ref[a]=0;
    for(int sy=0;sy<game_probe_density;sy++)for(int sx=0;sx<game_probe_density;sx++){
     int n=(y*game_probe_density+sy)*canvas->w+x*game_probe_density+sx;color_ref[n]=0xff000000u|rgb_palette[index_ref[y*screen.pitch+x]];owner_ref[n]=cloud_ref[n]=0;first_ref[n]=0;
    }
   }
  }else{assert(reject_reason&&!strcmp(reject_reason,"hd-invulnerability-palette-blend"));reject_reason=NULL;}
  check_area();check_all();production_end();game_probe_local_blend=false;blend_cases++;
 }
}
static void exact_alpha(void)
{
 const Uint8 alphas[]={0,1,17,63,127,128,191,254,255};for(unsigned a=0;a<sizeof(alphas);a++)for(unsigned s=0;s<256;s++)for(unsigned d=0;d<256;d++){
  Uint8 rgba[4]={(Uint8)s,(Uint8)(255-s),(Uint8)(s^0x69),alphas[a]};Uint32 dst=0xff000000u|d<<16|(255-d)<<8|(d^0x96);assert(blend_rgba(dst,rgba,rgba[3])==blend_oracle(dst,rgba));alpha_cases++;
 }
}
int main(int argc,char **argv)
{
 assert(argc==3);full_pack=game_probe_assets=argv[1];work=argv[2];char path[2048];size_t bytes;
 snprintf(path,sizeof(path),"%s/bank.bin",work);spriteSheet8.data=read_file(path,&bytes);spriteSheet8.size=bytes;Sprite2_array normal=spriteSheet8;
 snprintf(path,sizeof(path),"%s/xmas-bank.bin",work);Sprite2_array christmas={0};christmas.data=read_file(path,&bytes);christmas.size=bytes;
 snprintf(path,sizeof(path),"%s/reference.bin",work);void*ref=read_file(path,&bytes);assert(bytes==sizeof(references));memcpy(references,ref,bytes);free(ref);
 Uint8 tokens[3]={0};spriteSheet9=(Sprite2_array){tokens,1};spriteSheet12=(Sprite2_array){tokens+1,1};explosionSpriteSheet=(Sprite2_array){tokens+2,1};
 index_storage=malloc(328*H+2*PAD);assert(index_storage);screen.pixels=index_storage+PAD;
 for(unsigned i=0;i<256;i++)rgb_palette[i]=((i*71)%256)<<16|((i*31)%256)<<8|((i*13)%256);
 finite_bindings();metadata_cache();exact_alpha();
 for(int layout=0;layout<2;layout++){
  allocate(8,layout?328:320,layout?28:0);game_probe_assets=full_pack;test_guards();exact_shadow_guard();
  const int xy[][2]={{94,73},{0,0},{308,0},{0,-13},{308,-1},{94,187},{0,199},{308,199},{-3,73},{315,73},{94,-14},{94,200}};
  for(unsigned k=0;k<8;k++)for(unsigned p=0;p<sizeof(xy)/sizeof(*xy);p++){
   transaction(k,xy[p][0],xy[p][1],!BASELINE,false,0,true);transaction(k,xy[p][0],xy[p][1],false,true,0,true);
  }
  for(unsigned k=0;k<8;k++){
   transaction(k,94,73,false,false,1,true);transaction(k,94,73,false,true,1,true);
   game_probe_original_reference=true;transaction(k,94,73,!BASELINE,false,0,true);transaction(k,94,73,false,true,0,true);game_probe_original_reference=false;
  }
  test_identity(normal,christmas);test_isolation(normal,christmas);test_cross_mode_caches(normal,christmas);test_overlap();test_vulcan_interleaving(normal,christmas);test_vulcan_resources();
  fallback_variants();blend_fallback();check_all();clear_assets();release();
 }
 for(int d=1;d<=4;d+=3){
  allocate(d,328,28);game_probe_assets=full_pack;
  for(unsigned k=0;k<8;k++)transaction(k,94,73,false,false,0,true);
  clear_assets();select_pack("only4");
  for(unsigned k=0;k<8;k++){transaction(k,94,73,!BASELINE&&d==4,false,0,true);transaction(k,94,73,false,true,0,true);}
  check_all();clear_assets();release();
 }
 assert(spriteSheet8.data==normal.data&&spriteSheet8.size==normal.size);
 free(index_storage);free(normal.data);free(christmas.data);
 printf("{\"status\":\"PASS\",\"baseline\":%s,\"binding_cases\":%u,\"cache_cases\":%u,\"transactions\":%u,\"accepted\":%u,\"fallback\":%u,\"guard_cases\":%u,\"blend_cases\":%u,\"isolation_cases\":%u,\"lease_cases\":%u,\"identity_cases\":%u,\"overlap_cases\":%u,\"pixel_comparisons\":%llu,\"full_frame_checks\":%u,\"exact_alpha_cases\":%llu,\"shadow_fingerprint\":\"%016llx\"}\n",BASELINE?"true":"false",binding_cases,cache_cases,cases,accepted_cases,fallback_cases,guard_cases,blend_cases,isolation_cases,lease_cases,identity_cases,overlap_cases,(unsigned long long)comparisons,full_comparisons,(unsigned long long)alpha_cases,(unsigned long long)shadow_fingerprint);
 return 0;
}
