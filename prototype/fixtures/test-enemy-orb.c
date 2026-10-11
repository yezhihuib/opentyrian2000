#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef uint8_t Uint8;typedef uint16_t Uint16;typedef uint32_t Uint32;
typedef struct {int x,y,w,h;} SDL_Rect;
typedef struct {int BitsPerPixel;} SDL_PixelFormat;
typedef struct {int w,h,pitch;void *pixels;SDL_PixelFormat *format;} SDL_Surface;
typedef struct {size_t size;Uint8 *data;} Sprite2_array;
#define MAX(a,b) ((a)>(b)?(a):(b))
#define MIN(a,b) ((a)<(b)?(a):(b))
#define SDL_SwapLE16(x) (x)
enum {MIRROR_NORMAL,MIRROR_BLEND,MIRROR_SHADOW};
enum {ENTITY_NORMAL,ENTITY_BLEND,ENTITY_SHADOW};
enum {ENTITY_TILE,ENTITY_QUAD};
enum {ASSET_NEWSH2=101,ASSET_EXPLOSION=106,ASSET_TALON_BANK=109,ASSET_NEWSHE=110,ASSET_SHAPESZ=201};
#include "types.inc"
static SDL_Surface *canvas,*game_screen,*VGAScreen;
static int game_probe_density;
static bool game_probe_original_reference,game_probe_local_blend=true,game_probe_known_blend;
static bool game_probe_missing,game_probe_invalid,active=true,suppress,suppress_green_smoke,suppress_cloud;
static const char *game_probe_assets,*reject_reason;
static Uint32 rgb_palette[256];
static Uint8 expected[320*200],selected[320*200],restored_mask[320*200];
static Uint8 *hd_owner,*cloud_owner,*green_under_owner;
static Uint16 *green_first;
static Uint32 *green_under;
static GreenHead green_heads[256];
static HdRegion regions[256];
static unsigned int green_head_count,region_count,local_entities,draws,occlusions;
static unsigned int local_regions,local_blocks,expanded_regions,boundary_crossings,blend_source_index;
static Sprite2_array spriteSheet8,spriteSheet9,explosionSpriteSheet;
static unsigned int scene_calls,original_calls,end_calls;static int logged_role,logged_index,logged_x,logged_y,logged_part,logged_style;static bool logged_mirrored;
static bool allow_reject;
static void render_mirror_unsupported(const char *reason){if(allow_reject){reject_reason=reason;return;}fprintf(stderr,"Unexpected rejection: %s\n",reason);abort();}
static void game_probe_restore_region(unsigned int s,SDL_Rect a,SDL_Rect b,unsigned int g,unsigned int c){(void)s;(void)a;(void)b;(void)g;(void)c;}
static void game_probe_scene_draw(int role,unsigned int index,int x,int y,int part,int style,bool mirrored){scene_calls++;logged_role=role;logged_index=(int)index;logged_x=x;logged_y=y;logged_part=part;logged_style=style;logged_mirrored=mirrored;}
#define render_mirror_entity_end production_render_mirror_entity_end
#include "functions.inc"
#undef render_mirror_entity_end
static void render_mirror_entity_end(void){end_calls++;production_render_mirror_entity_end();}
static void asset_debug_effect(SDL_Surface *surface,Sprite2_array bank,unsigned int index,int x,int y){(void)surface;(void)bank;(void)index;(void)x;(void)y;original_calls++;}
#include "blitter.inc"
#include "wrapper.inc"
#define LW 32
#define LH 32
static Uint32 *oracle,*base;
static Uint8 *oracle_cloud,*oracle_owner;
static Uint16 *oracle_first;
static Uint8 oracle_index[LW*LH];
static unsigned long long checks,wrapper_checks,helper_checks,guards;
static char pack_path[2048];static const char *pack_root;
static void select_pack(const char *name){snprintf(pack_path,sizeof(pack_path),"%s/%s",pack_root,name);game_probe_assets=pack_path;}
static void clear_assets(void){for(size_t i=0;i<sizeof(assets)/sizeof(*assets);i++){free(assets[i].rgba);memset(&assets[i],0,sizeof(assets[i]));}}
static void synthetic(int index,int x,int y,Uint8 p[4]){static const Uint8 alpha[]={0,1,127,128,254,255};p[0]=(Uint8)(index*7+x*3+y);p[1]=(Uint8)(index*11+x+y*5);p[2]=(Uint8)(index*13+x*7+y*2);p[3]=alpha[(x+2*y+index)%6];}
static Uint32 alpha_oracle(Uint32 dst,const Uint8 p[4]){Uint32 out=0xff000000u;for(int c=0;c<3;c++){unsigned shift=(2-c)*8,n=((dst>>shift)&255)*(255-p[3])+p[c]*p[3];out|=(n/255+(n%255>=128))<<shift;}return out;}
static bool original_mask(int id,int x,int y){return (x+y+id)%5!=0;}
static Uint8 original_index(int id,int x,int y){return (Uint8)((id+3*x+7*y)%240+1);}
static void alloc_canvas(int d){game_probe_density=d;canvas->w=LW*d;canvas->h=LH*d;canvas->pitch=canvas->w*4+16;size_t n=(size_t)canvas->w*canvas->h;canvas->pixels=malloc((size_t)canvas->pitch*canvas->h);oracle=malloc(n*4);base=malloc(n*4);oracle_cloud=malloc(n);oracle_owner=malloc(n);oracle_first=malloc(n*2);hd_owner=malloc(n);cloud_owner=malloc(n);green_first=malloc(n*2);green_under=malloc(n*4);green_under_owner=malloc(n);assert(canvas->pixels&&oracle&&base&&oracle_cloud&&oracle_owner&&oracle_first&&hd_owner&&cloud_owner&&green_first&&green_under&&green_under_owner);}
static void free_canvas(void){free(canvas->pixels);free(oracle);free(base);free(oracle_cloud);free(oracle_owner);free(oracle_first);free(hd_owner);free(cloud_owner);free(green_first);free(green_under);free(green_under_owner);}
static void reset_canvas(void){size_t n=(size_t)canvas->w*canvas->h;memset(canvas->pixels,0xcd,(size_t)canvas->pitch*canvas->h);memset(hd_owner,1,n);memset(oracle_owner,1,n);memset(cloud_owner,1,n);memset(oracle_cloud,1,n);memset(green_first,0,n*2);memset(oracle_first,0,n*2);memset(selected,0,sizeof(selected));memset(expected,17,sizeof(expected));memset(game_screen->pixels,17,LW*LH);memset(oracle_index,17,sizeof(oracle_index));region_count=green_head_count=draws=scene_calls=original_calls=end_calls=0;suppress=suppress_green_smoke=suppress_cloud=false;active=true;reject_reason=NULL;game_probe_original_reference=false;
 for(int y=0;y<canvas->h;y++)for(int x=0;x<canvas->w;x++){Uint32 c=0xff000000u|((x*7u+y*3u)%256)<<16|((x+y*11u)%256)<<8|((x*17u+y*5u)%256);oracle[y*canvas->w+x]=base[y*canvas->w+x]=c;*(Uint32 *)((Uint8 *)canvas->pixels+y*canvas->pitch+x*4)=c;}}
static void check_pixels(const char *label){for(int y=0;y<canvas->h;y++){for(int x=0;x<canvas->w;x++){int n=y*canvas->w+x;Uint32 got=*(Uint32 *)((Uint8 *)canvas->pixels+y*canvas->pitch+x*4);if(got!=oracle[n]||cloud_owner[n]!=oracle_cloud[n]||hd_owner[n]!=oracle_owner[n]||green_first[n]!=oracle_first[n]){fprintf(stderr,"%s mismatch d%d x%d y%d color %08x/%08x cloud%u/%u owner%u/%u first%u/%u\n",label,game_probe_density,x,y,got,oracle[n],cloud_owner[n],oracle_cloud[n],hd_owner[n],oracle_owner[n],green_first[n],oracle_first[n]);abort();}checks++;}for(int p=canvas->w*4;p<canvas->pitch;p++)assert(((Uint8 *)canvas->pixels)[y*canvas->pitch+p]==0xcd);}assert(!memcmp(game_screen->pixels,oracle_index,sizeof(oracle_index)));for(int y=0;y<LH;y++)for(int x=0;x<LW;x++)if(active&&!reject_reason)assert(expected[y*320+x]==oracle_index[y*LW+x]);}
static void oracle_asset(int id,int x,int y,int ad){int d=game_probe_density;for(int py=0;py<canvas->h;py++)for(int px=0;px<canvas->w;px++){int ax=px-x*d,ay=py-y*d;if(ax<0||ay<0||ax>=12*d||ay>=14*d)continue;Uint8 src[4];synthetic(id,ax*ad/d,ay*ad/d,src);if(!src[3])continue;int n=py*canvas->w+px;oracle[n]=alpha_oracle(oracle[n],src);oracle_cloud[n]=0;oracle_first[n]=0;oracle_owner[n]=game_probe_original_reference?2:1;}}
static void oracle_original(int id,int x,int y,bool mirrored){int d=game_probe_density;for(int ay=0;ay<14;ay++)for(int ax=0;ax<12;ax++){int px=x+ax,py=y+ay;if(px<0||px>=LW||py<0||py>=LH||!original_mask(id,ax,ay))continue;Uint8 value=original_index(id,ax,ay);oracle_index[py*LW+px]=value;if(!active||reject_reason)continue;for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++){int n=(py*d+sy)*canvas->w+px*d+sx;oracle_cloud[n]=0;if(mirrored)oracle_owner[n]=game_probe_original_reference?2:1;else{oracle[n]=0xff000000u|rgb_palette[value];oracle_owner[n]=0;oracle_first[n]=0;}}}}
static void call_wrapper(int id,int x,int y,int ad,bool mirrored){unsigned before=original_calls,ends=end_calls,logs=scene_calls;draw_enemy_shot_sprite2(game_screen,x,y,spriteSheet8,(unsigned)id);wrapper_checks++;assert(original_calls==before+1&&end_calls==ends+1);assert(!suppress&&!suppress_cloud&&!suppress_green_smoke);assert(scene_calls==logs+1&&logged_role==108&&logged_index==id&&logged_x==x&&logged_y==y&&logged_part==0&&logged_style==ENTITY_NORMAL&&logged_mirrored==mirrored);if(mirrored)oracle_asset(id,x,y,ad);oracle_original(id,x,y,mirrored);check_pixels("wrapper");}
static void exercise_frame(int id,int ad,int x,int y){reset_canvas();call_wrapper(id,x,y,ad,true);Asset *a=&assets[218+id-112];assert(a->valid&&a->bank==8&&a->index==id&&a->w==12&&a->h==14&&a->anchor_x==0&&a->anchor_y==0&&a->density==ad);assert(green_head_count==0&&region_count==1);}
static void helper_clip(int id,int ad,int x,int y){reset_canvas();assert(render_mirror_enemy_shot(game_screen,x,y,spriteSheet8,id));helper_checks++;oracle_asset(id,x,y,ad);check_pixels("helper clipping");assert(!original_calls&&!scene_calls);render_mirror_entity_end();assert(!suppress&&!suppress_green_smoke&&!suppress_cloud);}
static void guard_case(SDL_Surface *surface,Sprite2_array bank,unsigned id){assert(!render_mirror_enemy_shot(surface,4,5,bank,id));assert(!suppress&&!scene_calls&&!original_calls);check_pixels("guard");guards++;}
static void guard_tests(void){SDL_Surface other=*game_screen;Sprite2_array wrong=spriteSheet9;reset_canvas();guard_case(&other,spriteSheet8,112);guard_case(game_screen,wrong,112);for(unsigned id=0;id<256;id++)if(id!=112&&id!=113)guard_case(game_screen,spriteSheet8,id);guard_case(game_screen,spriteSheet8,500);guard_case(game_screen,spriteSheet8,1000);guard_case(game_screen,spriteSheet8,UINT32_MAX);active=false;guard_case(game_screen,spriteSheet8,112);active=true;reject_reason="test";guard_case(game_screen,spriteSheet8,113);reject_reason=NULL;for(int id=112;id<=113;id++)for(int layout=0;layout<=1;layout++)assert(get_asset(spriteSheet8,id,layout)==NULL);for(int i=0;i<218;i++)assert(!assets[i].initialized);}
static void loader_tests(void){const char *bad[]={"missing112","bad-anchor","bad-role","bad-size","bad-density","truncated","extra"};for(size_t i=0;i<sizeof(bad)/sizeof(*bad);i++){clear_assets();select_pack(bad[i]);reset_canvas();call_wrapper(112,5,6,8,false);call_wrapper(113,15,16,8,true);}clear_assets();select_pack("missing113");reset_canvas();call_wrapper(113,5,6,8,false);call_wrapper(112,15,16,8,true);
 clear_assets();select_pack("empty");for(int id=112;id<=113;id++){reset_canvas();call_wrapper(id,5,6,8,false);}clear_assets();select_pack("full8");game_probe_assets=NULL;reset_canvas();call_wrapper(112,5,6,8,false);select_pack("full8");reset_canvas();call_wrapper(112,5,6,8,true);game_probe_missing=true;reset_canvas();call_wrapper(112,5,6,8,false);game_probe_missing=false;game_probe_invalid=true;reset_canvas();call_wrapper(112,5,6,8,false);game_probe_invalid=false;reset_canvas();active=false;call_wrapper(112,5,6,8,false);reset_canvas();reject_reason="test";call_wrapper(113,5,6,8,false);reject_reason=NULL;active=true;
 clear_assets();select_pack("full8");reset_canvas();memset(regions,0,sizeof(regions));region_count=256;allow_reject=true;call_wrapper(112,5,6,8,false);assert(reject_reason&&!strcmp(reject_reason,"hd-region-capacity"));allow_reject=false;reject_reason=NULL;
}
static Asset constant_asset(int bank,int id,int d,const Uint8 color[4]){Asset a={0};a.bank=bank;a.index=id;a.w=12;a.h=14;a.density=d;a.valid=true;a.rgba=malloc(12*14*d*d*4);assert(a.rgba);for(int i=0;i<12*14*d*d;i++)memcpy(a.rgba+i*4,color,4);return a;}
static void green_foreground_tests(int ad){int d=game_probe_density;Uint8 head_color[4]={60,180,90,128},smoke_color[4]={40,130,70,100};Asset h=constant_asset(8,214,ad,head_color),smoke=constant_asset(106,78,ad,smoke_color);
 for(int id=112;id<=113;id++){
  reset_canvas();assert(draw_asset(5,6,&h,MIRROR_NORMAL,NULL));production_render_mirror_entity_end();for(int y=6*d;y<20*d;y++)for(int x=5*d;x<17*d;x++){int n=y*canvas->w+x;oracle[n]=alpha_oracle(oracle[n],head_color);oracle_cloud[n]=0;oracle_first[n]=1;}check_pixels("head setup");
  call_wrapper(id,5,6,ad,true);assert(green_head_count==1);
  /* Orange coverage bakes the old head; later green smoke must cover that orange. */
  assert(draw_asset(5,6,&smoke,MIRROR_NORMAL,NULL));production_render_mirror_entity_end();for(int y=6*d;y<20*d;y++)for(int x=5*d;x<17*d;x++){int n=y*canvas->w+x;if(oracle_first[n])oracle[n]=alpha_oracle(alpha_oracle(base[n],smoke_color),head_color);else oracle[n]=alpha_oracle(oracle[n],smoke_color);oracle_cloud[n]=0;oracle_owner[n]=1;}check_pixels("smoke after orb");
  /* Later unrelated indexed foreground covers the current RGB and ends protection. */
  int px=9,py=10;Uint8 *address=(Uint8 *)game_screen->pixels+py*LW+px;*address=99;oracle_index[py*LW+px]=99;render_mirror_pixel(game_screen,address,99,MIRROR_NORMAL);for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++){int n=(py*d+sy)*canvas->w+px*d+sx;oracle[n]=0xff000000u|rgb_palette[99];oracle_owner[n]=0;oracle_cloud[n]=0;oracle_first[n]=0;}check_pixels("later foreground");
 }
 free(h.rgba);free(smoke.rgba);
}
static Uint32 shadow_oracle(Uint32 color,Uint8 before,Uint8 after,bool cloud){Uint32 out=0xff000000u;for(int c=0;c<3;c++){unsigned shift=(2-c)*8,old=(color>>shift)&255,value;if(cloud){unsigned den=(rgb_palette[before]>>shift)&255,num=(rgb_palette[after]>>shift)&255;if(before==after||!den)value=old;else{unsigned n=old*num;value=n/den+(n%den>=(den+1)/2);if(value>255)value=255;}}else value=(old+1)/2;out|=value<<shift;}return out;}
static void cloud_after_orb(int ad){reset_canvas();call_wrapper(112,5,6,ad,true);int d=game_probe_density;unsigned ratio=0,ordinary=0;for(int py=6;py<20;py++)for(int px=5;px<17;px++){Uint8 *address=(Uint8 *)game_screen->pixels+py*LW+px;Uint8 before=*address,after=(before&0xf0)|((before&15)/2);*address=after;oracle_index[py*LW+px]=after;render_mirror_pixel(game_screen,address,0,MIRROR_SHADOW);for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++){int n=(py*d+sy)*canvas->w+px*d+sx;bool cloud=oracle_cloud[n]!=0;ratio+=cloud;ordinary+=!cloud;oracle[n]=shadow_oracle(oracle[n],before,after,cloud);oracle_first[n]=0;}}assert(ratio&&ordinary);check_pixels("shadow on surviving cloud and orb");}
int main(int argc,char **argv){assert(argc==2);pack_root=argv[1];char name[2048];snprintf(name,sizeof(name),"%s/original-bank.bin",pack_root);FILE*f=fopen(name,"rb");assert(f);fseek(f,0,SEEK_END);long size=ftell(f);rewind(f);spriteSheet8=(Sprite2_array){(size_t)size,malloc((size_t)size)};assert(spriteSheet8.data&&fread(spriteSheet8.data,1,(size_t)size,f)==(size_t)size);fclose(f);Uint8 wrong=0;spriteSheet9=(Sprite2_array){1,&wrong};explosionSpriteSheet=(Sprite2_array){0,NULL};SDL_PixelFormat format={8};SDL_Surface c={0},g={LW,LH,LW,calloc(LW*LH,1),&format};canvas=&c;game_screen=VGAScreen=&g;for(int i=0;i<256;i++)rgb_palette[i]=((i*71u)%256)<<16|((i*31u)%256)<<8|((i*13u)%256);assert(sizeof(assets)/sizeof(*assets)>=220);
 for(int mode=0;mode<3;mode++){int d=mode==0?4:8,ad=mode==1?8:4;alloc_canvas(d);clear_assets();select_pack(ad==8?"full8":"full4");for(int k=0;k<8;k++){int id=k%2?112:113;exercise_frame(id,ad,5,6);exercise_frame(id,ad,2,-13);exercise_frame(id,ad,3,LH-2);}for(int id=112;id<=113;id++){helper_clip(id,ad,-11,-13);helper_clip(id,ad,LW-2,LH-2);helper_clip(id,ad,1000,-1000);}guard_tests();green_foreground_tests(ad);cloud_after_orb(ad);if(mode==1)loader_tests();printf("PASS density%d source%d: both phases, original indexed blit once, reset once, alpha, clips, cloud/green/foreground ordering\n",d,ad);clear_assets();free_canvas();}
 alloc_canvas(1);select_pack("full8");reset_canvas();call_wrapper(112,5,6,8,false);call_wrapper(113,15,16,8,false);for(int i=0;i<220;i++)assert(!assets[i].initialized);free_canvas();clear_assets();free(g.pixels);free(spriteSheet8.data);printf("PASS %llu pixel comparisons, %llu wrappers, %llu clipped helpers, %llu scope guards; missing/header/classic/player-isolation tests\n",checks,wrapper_checks,helper_checks,guards);return 0;
}
