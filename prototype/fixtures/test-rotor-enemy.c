#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef uint8_t Uint8; typedef uint16_t Uint16; typedef uint32_t Uint32;
typedef struct {int x,y,w,h;} SDL_Rect;
typedef struct {int w,h,pitch;void *pixels;} SDL_Surface;
typedef struct {size_t size;Uint8 *data;} Sprite2_array;
#define MAX(a,b) ((a)>(b)?(a):(b))
#define MIN(a,b) ((a)<(b)?(a):(b))
enum {MIRROR_NORMAL,MIRROR_BLEND,MIRROR_SHADOW};
enum {ASSET_NEWSH2=101,ASSET_EXPLOSION=106,ASSET_TALON_BANK=109,ASSET_NEWSHE=110,ASSET_SHAPESZ=201};
#include "types.inc"
static SDL_Surface *canvas,*game_screen;
static int game_probe_density,game_probe_scene_assets=1;
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
static unsigned int green_head_count,region_count,local_entities,draws,occlusions,brightness_blocks;
static unsigned int local_regions,local_blocks,expanded_regions,boundary_crossings,blend_source_index;
static Sprite2_array enemySpriteSheets[4];static unsigned int enemySpriteSheetIds[4];
static unsigned int scene_calls; static int logged_role,logged_index,logged_x,logged_y,logged_part,logged_style;static bool logged_mirrored;
static void render_mirror_unsupported(const char *reason){fprintf(stderr,"Unexpected rejection: %s\n",reason);abort();}
static void game_probe_restore_region(unsigned int s,SDL_Rect a,SDL_Rect b,unsigned int g,unsigned int c){(void)s;(void)a;(void)b;(void)g;(void)c;}
static void game_probe_scene_draw(int role,unsigned int index,int x,int y,int part,int style,bool mirrored){scene_calls++;logged_role=role;logged_index=(int)index;logged_x=x;logged_y=y;logged_part=part;logged_style=style;logged_mirrored=mirrored;}
#include "functions.inc"
#define LW 40
#define LH 44
static Uint32 *oracle;static Uint8 *oracle_cloud;
static unsigned long long checks,quad_calls,guard_checks;
static char pack_path[2048];
static const char *pack_root;
static void select_pack(const char *name){snprintf(pack_path,sizeof(pack_path),"%s/%s",pack_root,name);game_probe_assets=pack_path;}
static void clear_assets(void){for(size_t i=0;i<sizeof(assets)/sizeof(*assets);i++){free(assets[i].rgba);memset(&assets[i],0,sizeof(assets[i]));}}
static void synthetic(int base,int x,int y,Uint8 p[4]){static const Uint8 alpha[]={0,1,127,128,254,255};p[0]=(Uint8)(base*7+x*3+y);p[1]=(Uint8)(base*11+x+y*5);p[2]=(Uint8)(base*13+x*7+y*2);p[3]=alpha[(x+2*y+base)%6];}
static Uint32 palette_channel(unsigned i,int channel){return (rgb_palette[i]/(1u<<((2-channel)*8)))%256;}
static void filter_oracle(const Uint8 source[4],int filter,Uint8 out[4]){
 memcpy(out,source,4);if(!filter)return;
 unsigned peak=source[0];if(source[1]>peak)peak=source[1];if(source[2]>peak)peak=source[2];
 unsigned n=peak*3840u,value=n/255+(n%255>=128),lo=value/256,hi=lo<15?lo+1:15,f=value%256;
 for(int c=0;c<3;c++){unsigned sum=palette_channel(filter|lo,c)*(256-f)+palette_channel(filter|hi,c)*f;out[c]=(Uint8)(sum/256+(sum%256>=128));}
}
static Uint32 blend_oracle(Uint32 color,const Uint8 p[4]){Uint32 result=0xff000000u;for(int c=0;c<3;c++){unsigned shift=(2-c)*8,old=(color>>shift)&255,n=old*(255-p[3])+p[c]*p[3];result|=(n/255+(n%255>=128))<<shift;}return result;}
static void alloc_canvas(int d){game_probe_density=d;canvas->w=LW*d;canvas->h=LH*d;canvas->pitch=canvas->w*4+16;size_t count=(size_t)canvas->w*canvas->h;canvas->pixels=malloc((size_t)canvas->pitch*canvas->h);oracle=malloc(count*4);oracle_cloud=malloc(count);hd_owner=malloc(count);cloud_owner=malloc(count);green_first=malloc(count*2);green_under=malloc(count*4);green_under_owner=malloc(count);assert(canvas->pixels&&oracle&&hd_owner&&cloud_owner&&green_first&&green_under&&green_under_owner);}
static void free_canvas(void){free(canvas->pixels);free(oracle);free(oracle_cloud);free(hd_owner);free(cloud_owner);free(green_first);free(green_under);free(green_under_owner);}
static void reset_canvas(void){size_t n=(size_t)canvas->w*canvas->h;memset(canvas->pixels,0xcd,(size_t)canvas->pitch*canvas->h);memset(hd_owner,1,n);memset(cloud_owner,1,n);memset(oracle_cloud,1,n);memset(green_first,0,n*2);memset(selected,0,sizeof(selected));memset(expected,0,sizeof(expected));memset(game_screen->pixels,0,(size_t)game_screen->pitch*game_screen->h);region_count=green_head_count=draws=scene_calls=0;suppress=suppress_green_smoke=suppress_cloud=false;for(int y=0;y<canvas->h;y++)for(int x=0;x<canvas->w;x++){Uint32 c=0xff000000u|((x*7u+y*3u)%256)<<16|((x+y*11u)%256)<<8|((x*17u+y*5u)%256);oracle[y*canvas->w+x]=c;*(Uint32 *)((Uint8 *)canvas->pixels+y*canvas->pitch+x*4)=c;}}
static void check_pixels(void){for(int y=0;y<canvas->h;y++){for(int x=0;x<canvas->w;x++){Uint32 got=*(Uint32 *)((Uint8 *)canvas->pixels+y*canvas->pitch+x*4);if(got!=oracle[y*canvas->w+x]){fprintf(stderr,"pixel mismatch d=%d x=%d y=%d got%08x want%08x\n",game_probe_density,x,y,got,oracle[y*canvas->w+x]);abort();}assert(cloud_owner[y*canvas->w+x]==oracle_cloud[y*canvas->w+x]);assert(hd_owner[y*canvas->w+x]==1);assert(!green_first[y*canvas->w+x]);checks++;}for(int p=canvas->w*4;p<canvas->pitch;p++)assert(((Uint8 *)canvas->pixels)[y*canvas->pitch+p]==0xcd);}for(int i=0;i<game_screen->pitch*game_screen->h;i++)assert(!((Uint8 *)game_screen->pixels)[i]);}
static void expected_part(int base,int part,int origin_x,int origin_y,int ad,int filter){int d=game_probe_density,px=part==1||part==20?12:0,py=part==19||part==20?14:0;for(int y=py*d;y<(py+14)*d;y++)for(int x=px*d;x<(px+12)*d;x++){int dx=origin_x*d+x,dy=origin_y*d+y;if(dx<0||dy<0||dx>=canvas->w||dy>=canvas->h)continue;Uint8 src[4],color[4];synthetic(base,x*ad/d,y*ad/d,src);filter_oracle(src,filter,color);if(src[3])oracle_cloud[dy*canvas->w+dx]=0;oracle[dy*canvas->w+dx]=blend_oracle(oracle[dy*canvas->w+dx],color);}}
static void exercise_frame(int base,int ad,int filter,int x,int y,bool reverse_parts){static const int order[2][4]={{0,1,19,20},{20,0,19,1}};reset_canvas();for(int k=0;k<4;k++){int part=order[reverse_parts][k],px=part==1||part==20?12:0,py=part==19||part==20?14:0;assert(render_mirror_enemy_tile(game_screen,x+px,y+py,enemySpriteSheets[0],base,part,filter));quad_calls++;assert(scene_calls==(unsigned)k+1&&logged_role==101&&logged_index==base&&logged_part==part&&logged_x==x+px&&logged_y==y+py&&logged_style==(filter?3:0)&&logged_mirrored);Asset *a=&assets[210+(base-229)/2];assert(a->valid&&a->bank==101&&a->index==base&&a->w==24&&a->h==28&&a->anchor_x==6&&a->anchor_y==7&&a->density==ad);expected_part(base,part,x,y,ad,filter);check_pixels();assert(region_count==1&&regions[0].rect.x==x&&regions[0].rect.y==y&&regions[0].rect.w==24&&regions[0].rect.h==28);render_mirror_entity_end();}}
static void guard_case(SDL_Surface *surface,Sprite2_array bank,int base,int part){reset_canvas();unsigned before=scene_calls;assert(!render_mirror_enemy_tile(surface,4,5,bank,base,part,0));assert(scene_calls==before);check_pixels();guard_checks++;}
static void guard_tests(void){Uint8 bad_data=9;Sprite2_array wrong={1,&bad_data};SDL_Surface other=*game_screen;for(int b=228;b<=244;b+=2)guard_case(game_screen,enemySpriteSheets[0],b,0);guard_case(game_screen,enemySpriteSheets[0],227,0);guard_case(game_screen,enemySpriteSheets[0],245,0);for(int p=2;p<=21;p++)if(p!=19&&p!=20)guard_case(game_screen,enemySpriteSheets[0],229,p);guard_case(game_screen,wrong,229,0);guard_case(&other,enemySpriteSheets[0],229,0);enemySpriteSheetIds[0]=2;guard_case(game_screen,enemySpriteSheets[0],229,0);enemySpriteSheetIds[0]=1;game_probe_scene_assets=0;guard_case(game_screen,enemySpriteSheets[0],229,0);game_probe_scene_assets=1;active=false;guard_case(game_screen,enemySpriteSheets[0],229,0);active=true;reject_reason="test";guard_case(game_screen,enemySpriteSheets[0],229,0);reject_reason=NULL;}
static void absent_frame(int base){reset_canvas();for(int p=0;p<4;p++){int part=(int[]){0,1,19,20}[p];assert(!render_mirror_enemy_tile(game_screen,5,7,enemySpriteSheets[0],base,part,0));assert(!logged_mirrored);}check_pixels();}
static void loader_tests(void){const char *invalid[]={"missing235","bad-anchor","bad-role","bad-size","bad-density","truncated","extra"};for(size_t j=0;j<sizeof(invalid)/sizeof(*invalid);j++){clear_assets();select_pack(invalid[j]);absent_frame(235);exercise_frame(233,8,0,5,7,false);exercise_frame(237,8,0,5,7,false);}clear_assets();select_pack("empty");for(int b=229;b<=243;b+=2)absent_frame(b);clear_assets();game_probe_assets=NULL;for(int b=229;b<=243;b+=2)absent_frame(b);clear_assets();select_pack("full8");game_probe_missing=true;for(int b=229;b<=243;b+=2)absent_frame(b);game_probe_missing=false;clear_assets();game_probe_invalid=true;for(int b=229;b<=243;b+=2)absent_frame(b);game_probe_invalid=false;clear_assets();int d=game_probe_density;game_probe_density=1;for(int b=229;b<=243;b+=2)absent_frame(b);game_probe_density=d;}
int main(int argc,char **argv){assert(argc==2);pack_root=argv[1];SDL_Surface c={0},g={LW,LH,LW,NULL};canvas=&c;game_screen=&g;g.pixels=calloc(LW*LH,1);Uint8 bank_bytes[4]={1,2,3,4};for(int k=0;k<4;k++){enemySpriteSheets[k]=(Sprite2_array){1,&bank_bytes[k]};enemySpriteSheetIds[k]=k?2:1;}for(int i=0;i<256;i++)rgb_palette[i]=((i*71u)%256)<<16|((i*31u)%256)<<8|((i*13u)%256);assert(sizeof(assets)/sizeof(*assets)>=218);
 const int filters[]={0,0x70,0x80,0x09};for(int mode=0;mode<3;mode++){int d=mode==0?4:8,ad=mode==1?8:4;alloc_canvas(d);clear_assets();select_pack(ad==8?"full8":"full4");for(int rev=0;rev<2;rev++)for(int i=0;i<8;i++){int base=rev?243-i*2:229+i*2;for(int f=0;f<4;f++)exercise_frame(base,ad,filters[f],5,7,rev);}for(int base=229;base<=243;base+=2){exercise_frame(base,ad,0,-11,-13,false);exercise_frame(base,ad,0x09,LW-4,LH-3,true);}guard_tests();for(int i=0;i<210;i++)assert(!assets[i].initialized);printf("PASS: density%d source%d all32 quadrants, forward/reverse, four filters, seams, clipping, source guards\n",d,ad);if(mode==1){loader_tests();puts("PASS: one-frame fallback/header validation/absent assets/classic/missing/invalid flags");}clear_assets();free_canvas();}
 free(g.pixels);printf("PASS: %llu pixel comparisons; %llu successful quadrant calls; %llu rejected-source/part guards\n",checks,quad_calls,guard_checks);return 0;}
