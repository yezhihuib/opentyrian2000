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
enum {ASSET_NEWSH2=101,ASSET_NEWSH4=102,ASSET_NEWSHE=110,ASSET_ENEMY_ENERGY=111,ASSET_TALON_BANK=109,ASSET_SHAPESZ=201,ASSET_EXPLOSION=106};
#define MIN(a,b) ((a)<(b)?(a):(b))
#define MAX(a,b) ((a)>(b)?(a):(b))
#include "types.inc"
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
static void font_before_effect(SDL_Rect r){assert(r.w==12&&r.h==14);font_calls++;}
static bool font_pixel(int x,int y,Uint8 p,int style){(void)x;(void)y;(void)p;(void)style;return false;}
static void restore_classic_rect(SDL_Rect r){(void)r;assert(0);}
static void render_mirror_unsupported(const char *s){fprintf(stderr,"Unexpected rejection: %s\n",s);abort();}
static Uint16 SDL_SwapLE16(Uint16 value){Uint8 b[2];memcpy(b,&value,2);return (Uint16)(b[0]|(unsigned)b[1]<<8);}
#define render_mirror_entity_end production_end
#include "functions.inc"
#undef render_mirror_entity_end
static void render_mirror_entity_end(void){end_calls++;production_end();}
static void asset_debug_effect(SDL_Surface*s,Sprite2_array b,unsigned id,int x,int y){assert(s&&b.data&&id);(void)x;(void)y;original_calls++;}
#include "blitters.inc"
#define blit_sprite2_blend(...) assert(0)
#define blit_sprite2x2(...) assert(0)
#define blit_sprite2x2_blend(...) assert(0)
#define blit_sprite2x2_darken(...) assert(0)
static void game_probe_scene_draw(int role,unsigned id,int x,int y,int part,int style,bool mirrored){assert(part==0&&style==ENTITY_NORMAL);scene_calls++;log_role=role;log_id=id;log_x=x;log_y=y;log_mirrored=mirrored;}
static void game_probe_draw(int role,unsigned id,int x,int y,int style,int layout,bool mirrored){assert(role==8&&layout==ENTITY_TILE);(void)style;player_calls++;log_role=role;log_id=id;log_x=x;log_y=y;log_mirrored=mirrored;}
#include "wrappers.inc"
#include "variants.inc"
enum {W=320,H=200,SCREEN=W*H,PAD=16384,REF=336+43008};
static const unsigned ids[10]={77,58,182,163,1,183,164,112,113,58};
static Uint8 references[10][REF],index_ref[SCREEN],selection_ref[SCREEN],*index_storage,*owner_ref,*cloud_ref;
static Uint16 *first_ref;static Uint32 *color_ref;
static unsigned area[512],area_count;static bool seen[SCREEN];
static unsigned cases,accepted_cases,fallback_cases,guard_cases,full_comparisons,player_cases;
static uint64_t comparisons,alpha_cases;static char pack_path[2048];
static void *read_file(const char *name,size_t *len){FILE*f=fopen(name,"rb");assert(f&&!fseek(f,0,SEEK_END));long n=ftell(f);assert(n>0&&!fseek(f,0,SEEK_SET));Uint8*p=malloc((size_t)n);assert(p&&fread(p,1,(size_t)n,f)==(size_t)n&&!fclose(f));*len=(size_t)n;return p;}
static void clear_assets(void){for(unsigned i=0;i<sizeof(assets)/sizeof(*assets);i++){free(assets[i].rgba);memset(assets+i,0,sizeof(*assets));}for(unsigned i=0;i<13;i++){free(talon_frames[i].rgba);memset(talon_frames+i,0,sizeof(*talon_frames));}enemy_energy_checked=enemy_energy_valid=false;}
static void select_pack(const char *name){snprintf(pack_path,sizeof(pack_path),"%s/%s",work,name);game_probe_assets=pack_path;}
static Uint32 initial_color(unsigned n){return 0xff000000u|((n*2654435761u+0x594123u)&0xffffffu);}
static void init_cell(int a){int d=game_probe_density,x=a%W,y=a/W;index_ref[a]=expected[a]=((Uint8*)screen.pixels)[a]=(Uint8)(a*29+23);selection_ref[a]=selected[a]=0;for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++){int n=(y*d+sy)*canvas->w+x*d+sx;color_ref[n]=((Uint32*)canvas->pixels)[n]=initial_color((unsigned)n);owner_ref[n]=hd_owner[n]=1;cloud_ref[n]=cloud_owner[n]=(Uint8)(n&1);first_ref[n]=green_first[n]=(Uint16)(n%4);green_under[n]=initial_color((unsigned)n+19);green_under_owner[n]=(Uint8)(n%3);}}
static void allocate(int d){game_probe_density=d;canvas->w=W*d;canvas->h=H*d;canvas->pitch=canvas->w*4;size_t n=(size_t)canvas->w*canvas->h;canvas->pixels=malloc(n*4);color_ref=malloc(n*4);hd_owner=malloc(n);owner_ref=malloc(n);cloud_owner=malloc(n);cloud_ref=malloc(n);green_first=malloc(n*2);first_ref=malloc(n*2);green_under=malloc(n*4);green_under_owner=malloc(n);assert(canvas->pixels&&color_ref&&hd_owner&&owner_ref&&cloud_owner&&cloud_ref&&green_first&&first_ref&&green_under&&green_under_owner);for(int a=0;a<SCREEN;a++)init_cell(a);}
static void release(void){free(canvas->pixels);free(color_ref);free(hd_owner);free(owner_ref);free(cloud_owner);free(cloud_ref);free(green_first);free(first_ref);free(green_under);free(green_under_owner);}
static void begin_area(int x,int y,bool reset){if(reset){memset(seen,0,sizeof(seen));area_count=region_count=green_head_count=0;}for(int py=-1;py<15;py++)for(int px=-1;px<13;px++){int a=(y+py)*W+x+px;if(a>=0&&a<SCREEN&&!seen[a]){assert(area_count<512);seen[a]=true;area[area_count++]=(unsigned)a;init_cell(a);}}production_end();}
static void check_area(void){int d=game_probe_density;for(unsigned k=0;k<area_count;k++){int a=(int)area[k];assert(index_ref[a]==((Uint8*)screen.pixels)[a]);assert(expected[a]==index_ref[a]);assert(selected[a]==selection_ref[a]);int x=a%W,y=a/W;for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++){int n=(y*d+sy)*canvas->w+x*d+sx;assert(color_ref[n]==((Uint32*)canvas->pixels)[n]);assert(owner_ref[n]==hd_owner[n]&&cloud_ref[n]==cloud_owner[n]&&first_ref[n]==green_first[n]);assert(green_under[n]==initial_color((unsigned)n+19)&&green_under_owner[n]==n%3);comparisons++;}}for(int i=0;i<PAD;i++)assert(index_storage[i]==0xa9&&index_storage[PAD+SCREEN+i]==0xa9);}
static void check_all(void){size_t n=(size_t)canvas->w*canvas->h;assert(!memcmp(index_ref,screen.pixels,SCREEN)&&!memcmp(index_ref,expected,SCREEN)&&!memcmp(selected,selection_ref,SCREEN));assert(!memcmp(color_ref,canvas->pixels,n*4)&&!memcmp(owner_ref,hd_owner,n)&&!memcmp(cloud_ref,cloud_owner,n)&&!memcmp(first_ref,green_first,n*2));full_comparisons++;}
static Uint32 blend_oracle(Uint32 dst,const Uint8 *src){Uint32 out=0xff000000u;for(int c=0;c<3;c++){unsigned shift=16-c*8,n=((dst>>shift)&255)*(255-src[3])+src[c]*src[3];out|=(n/255+(n%255>=128))<<shift;}return out;}
static Uint32 dark_oracle(Uint32 dst,unsigned alpha){Uint32 out=0xff000000u;for(unsigned shift=0;shift<24;shift+=8){unsigned n=((dst>>shift)&255)*(510-alpha);out|=(n/510+(n%510>=255))<<shift;}return out;}
static Uint32 cloud_shadow_oracle(Uint32 dst,Uint8 before,Uint8 after){if(before==after)return dst;Uint32 out=0xff000000u;for(unsigned shift=0;shift<24;shift+=8){unsigned den=(rgb_palette[before]>>shift)&255,num=((dst>>shift)&255)*((rgb_palette[after]>>shift)&255),v=den?num/den+(num%den>=(den+1)/2):((dst>>shift)&255);out|=MIN(v,255u)<<shift;}return out;}
static void oracle_asset(const Uint8 *rgba,int x,int y,bool shadow,int ad){int d=game_probe_density;for(int ay=0;ay<14*d;ay++)for(int ax=0;ax<12*d;ax++){int dx=x*d+ax,dy=y*d+ay;if(dx<0||dy<0||dx>=canvas->w||dy>=canvas->h)continue;const Uint8*s=rgba+4*(((ay*ad/d)*8/ad)*96+(ax*ad/d)*8/ad);if(!s[3])continue;int n=dy*canvas->w+dx;if(shadow&&owner_ref[n]!=1){Uint8 ci=index_ref[(dy/d)*W+dx/d];Uint32 dark=rgb_palette[(ci&0xf0)|((ci&15)/2)];Uint8 rgba[4]={(dark>>16)&255,(dark>>8)&255,dark&255,s[3]};color_ref[n]=blend_oracle(color_ref[n],rgba);}else color_ref[n]=shadow?dark_oracle(color_ref[n],s[3]):blend_oracle(color_ref[n],s);owner_ref[n]=game_probe_original_reference?2:1;cloud_ref[n]=0;first_ref[n]=0;selection_ref[(dy/d)*W+dx/d]=1;}}
static void oracle_original(unsigned k,int x,int y,bool accepted,bool shadow){int d=game_probe_density;for(int py=0;py<14;py++)for(int px=0;px<12;px++){int cell=py*12+px;if(!references[k][168+cell])continue;int a=(y+py)*W+x+px;if(a<0||a>=SCREEN)continue;assert(seen[a]);Uint8 before=index_ref[a],v=shadow?(Uint8)((before&0xf0)|((before&15)/2)):references[k][cell];index_ref[a]=v;if(!active||reject_reason)continue;selection_ref[a]=(Uint8)accepted;for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++){int n=((a/W)*d+sy)*canvas->w+(a%W)*d+sx;if(accepted){owner_ref[n]=game_probe_original_reference?2:1;cloud_ref[n]=0;}else{bool cloud=shadow&&cloud_ref[n]&&owner_ref[n]==1;first_ref[n]=0;if(!cloud)cloud_ref[n]=0;color_ref[n]=cloud?cloud_shadow_oracle(color_ref[n],before,v):shadow&&owner_ref[n]==1?dark_oracle(color_ref[n],255):0xff000000u|rgb_palette[v];if(!shadow)owner_ref[n]=0;}}}}
static void transaction(unsigned k,int x,int y,bool accepted,bool player,bool shadow,bool reset){begin_area(x,y,reset);unsigned before=original_calls,ends=end_calls,logs=player?player_calls:scene_calls,old_draws=draws;Uint8 *bank=spriteSheet8.data;size_t bank_size=spriteSheet8.size;if(player)draw_entity_sprite2(&screen,x,y,spriteSheet8,ids[k],shadow?ENTITY_SHADOW:ENTITY_NORMAL,ENTITY_TILE);else draw_enemy_shot_sprite2(&screen,x,y,spriteSheet8,ids[k]);assert(original_calls==before+1&&end_calls==ends+1&&draws==old_draws+(unsigned)accepted);assert(!suppress&&!suppress_cloud&&!suppress_green_smoke);assert((player?player_calls:scene_calls)==logs+1&&log_id==ids[k]&&log_x==x&&log_y==y&&log_mirrored==accepted&&log_role==(player?8:k<7?111:108));assert(bank==spriteSheet8.data&&bank_size==spriteSheet8.size);if(accepted)oracle_asset(references[k]+336,x,y,shadow,assets[player?321:k<7?462+k:218+k-7].density);oracle_original(k,x,y,accepted,shadow);check_area();cases++;accepted_cases+=accepted;fallback_cases+=!accepted;player_cases+=player;if(!(cases%32))check_all();}
static void all_seven(bool accepted){for(unsigned k=0;k<7;k++)transaction(k,94,73,accepted,false,false,true);}
static void isolation(void){for(unsigned i=0;i<3;i++){transaction(1,94,73,enemy_energy_valid,false,false,true);transaction(9,94,73,true,true,false,false);transaction(1,94,73,enemy_energy_valid,false,false,false);transaction(9,94,73,true,true,true,false);}assert(assets[321].valid&&assets[321].bank==8&&assets[321].index==58);assert(assets[463].bank==111&&assets[463].index==58);for(unsigned k=0;k<7;k++)if(k!=1){assert(!get_asset(spriteSheet8,ids[k],ENTITY_TILE));assert(!render_mirror_entity(&screen,94,73,spriteSheet8,ids[k],MIRROR_SHADOW,ENTITY_TILE));}for(unsigned k=7;k<9;k++)transaction(k,94,73,true,false,false,true);check_all();}
static void test_variants(void){for(unsigned i=0;i<sizeof(variants)/sizeof(*variants);i++){clear_assets();select_pack(variants[i]);all_seven(false);assert(enemy_energy_checked&&!enemy_energy_valid);isolation();/* Cached failure remains coherent if the pack pointer is later changed. */game_probe_assets=full_pack;all_seven(false);}clear_assets();game_probe_assets=full_pack;all_seven(true);/* Cached success retains its selected immutable payload. */select_pack("missing-77");all_seven(true);game_probe_assets=full_pack;}
static void guard(SDL_Surface *s,int x,int y,Sprite2_array b,unsigned id){unsigned old_draws=draws,old_font=font_calls;assert(!render_mirror_enemy_shot(s,x,y,b,id));assert(draws==old_draws&&font_calls==old_font&&!suppress&&!suppress_cloud&&!suppress_green_smoke);guard_cases++;}
static void test_guards(void){production_end();SDL_Surface other=screen;Sprite2_array wrong={(Uint8*)&other,1},null={NULL,0};for(unsigned k=0;k<7;k++){guard(NULL,3,4,spriteSheet8,ids[k]);guard(&other,3,4,spriteSheet8,ids[k]);guard(&screen,3,4,wrong,ids[k]);guard(&screen,3,4,null,ids[k]);}for(unsigned id=0;id<=303;id++)if(enemy_energy_slot(id)<0&&id!=112&&id!=113)guard(&screen,3,4,spriteSheet8,id);guard(&screen,3,4,spriteSheet8,UINT_MAX);Sprite2_array saved_bank=spriteSheet8;spriteSheet8=null;guard(&screen,3,4,null,77);spriteSheet8=saved_bank;VGAScreen=&other;guard(&screen,3,4,spriteSheet8,77);VGAScreen=&screen;SDL_PixelFormat *saved=screen.format;screen.format=NULL;guard(&screen,3,4,spriteSheet8,77);screen.format=saved;format.BitsPerPixel=32;guard(&screen,3,4,spriteSheet8,77);format.BitsPerPixel=8;format.BytesPerPixel=4;guard(&screen,3,4,spriteSheet8,77);format.BytesPerPixel=1;screen.pitch=321;guard(&screen,3,4,spriteSheet8,77);screen.pitch=320;screen.w=319;guard(&screen,3,4,spriteSheet8,77);screen.w=320;screen.h=199;guard(&screen,3,4,spriteSheet8,77);screen.h=200;active=false;guard(&screen,3,4,spriteSheet8,77);active=true;reject_reason="fixture";guard(&screen,3,4,spriteSheet8,77);reject_reason=NULL;const int xy[][2]={{INT_MIN,0},{INT_MAX,0},{0,INT_MIN},{0,INT_MAX},{-1,0},{309,0},{0,-14},{0,200}};for(unsigned j=0;j<sizeof(xy)/sizeof(*xy);j++)guard(&screen,xy[j][0],xy[j][1],spriteSheet8,77);check_all();}
static void diagnostics(void){for(unsigned mode=0;mode<4;mode++){clear_assets();game_probe_assets=mode==3?NULL:full_pack;game_probe_missing=mode==0;game_probe_invalid=mode==1;game_probe_original_reference=mode==2;all_seven(false);assert(!enemy_energy_checked);game_probe_missing=game_probe_invalid=game_probe_original_reference=false;}game_probe_assets=full_pack;all_seven(true);game_probe_missing=true;all_seven(false);game_probe_missing=false;game_probe_invalid=true;all_seven(false);game_probe_invalid=false;game_probe_original_reference=true;all_seven(false);game_probe_original_reference=false;all_seven(true);}
static void geometry(void){const int xy[][2]={{0,-13},{308,-13},{94,-1},{0,0},{308,0},{94,187},{0,199},{308,199},{-1,73},{309,73},{319,73},{320,73},{94,-14},{94,200}};for(unsigned k=0;k<7;k++)for(unsigned p=0;p<sizeof(xy)/sizeof(*xy);p++)transaction(k,xy[p][0],xy[p][1],p<8,false,false,true);check_all();}
static void foreground_shadow(void){transaction(0,94,73,true,false,false,true);int d=game_probe_density;for(int y=73;y<87;y++)for(int x=94;x<106;x++){int a=y*W+x;Uint8 before=index_ref[a],after=(Uint8)((before&0xf0)|((before&15)/2));((Uint8*)screen.pixels)[a]=after;render_mirror_pixel(&screen,(Uint8*)screen.pixels+a,0,MIRROR_SHADOW);index_ref[a]=after;selection_ref[a]=0;for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++){int n=(y*d+sy)*canvas->w+x*d+sx;bool cloud=cloud_ref[n]!=0;color_ref[n]=cloud?cloud_shadow_oracle(color_ref[n],before,after):dark_oracle(color_ref[n],255);if(!cloud)cloud_ref[n]=0;first_ref[n]=0;}}check_area();int a=78*W+99;((Uint8*)screen.pixels)[a]=99;render_mirror_pixel(&screen,(Uint8*)screen.pixels+a,99,MIRROR_NORMAL);index_ref[a]=99;selection_ref[a]=0;for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++){int n=(78*d+sy)*canvas->w+99*d+sx;color_ref[n]=0xff000000u|rgb_palette[99];owner_ref[n]=cloud_ref[n]=0;first_ref[n]=0;}check_area();check_all();}
static void exact_alpha(void){const Uint8 alphas[]={0,1,127,128,254,255};for(unsigned a=0;a<6;a++)for(unsigned s=0;s<256;s++)for(unsigned d=0;d<256;d++){Uint8 rgba[4]={(Uint8)s,(Uint8)(255-s),(Uint8)(s^0x69),alphas[a]};Uint32 dst=0xff000000u|d<<16|(255-d)<<8|(d^0x96);assert(blend_rgba(dst,rgba,rgba[3])==blend_oracle(dst,rgba));alpha_cases++;}}
int main(int argc,char **argv){assert(argc==3);full_pack=game_probe_assets=argv[1];work=argv[2];char path[2048];size_t bytes;snprintf(path,sizeof(path),"%s/bank.bin",work);spriteSheet8.data=read_file(path,&bytes);spriteSheet8.size=bytes;snprintf(path,sizeof(path),"%s/reference.bin",work);void *ref=read_file(path,&bytes);assert(bytes==sizeof(references));memcpy(references,ref,bytes);free(ref);Uint8 tokens[3]={0};spriteSheet9=(Sprite2_array){tokens,1};spriteSheet12=(Sprite2_array){tokens+1,1};explosionSpriteSheet=(Sprite2_array){tokens+2,1};index_storage=malloc(SCREEN+2*PAD);assert(index_storage);memset(index_storage,0xa9,SCREEN+2*PAD);screen.pixels=index_storage+PAD;for(unsigned i=0;i<256;i++)rgb_palette[i]=((i*71)%256)<<16|((i*31)%256)<<8|((i*13)%256);assert(sizeof(assets)/sizeof(*assets)==469);allocate(8);all_seven(true);for(unsigned k=0;k<7;k++){Asset*a=assets+462+k;assert(a->valid&&a->bank==111&&a->index==(int)ids[k]&&a->w==12&&a->h==14&&!a->anchor_x&&!a->anchor_y&&a->density==8);assert(!memcmp(a->rgba,references[k]+336,43008));}isolation();for(unsigned k=0;k<7;k++)if(k!=1){transaction(k,94,73,false,true,false,true);transaction(k,94,73,false,true,true,true);}fprintf(stderr,"PASS seven frozen assets, original indexed exact, player58 shadow and enemy112/113 isolation\n");test_variants();fprintf(stderr,"PASS coherent family fallback, all missing/changed members and malformed payloads\n");test_guards();diagnostics();geometry();foreground_shadow();exact_alpha();clear_assets();select_pack("only4");for(unsigned k=7;k<9;k++)transaction(k,94,73,true,false,false,true);transaction(9,94,73,true,true,false,true);assert(assets[218].density==4&&assets[219].density==4&&assets[321].density==4);clear_assets();release();for(int d=1;d<=4;d+=3){allocate(d);game_probe_assets=full_pack;all_seven(false);assert(!enemy_energy_checked);if(d==4){select_pack("only4");all_seven(false);for(unsigned k=7;k<9;k++)transaction(k,94,73,true,false,false,true);transaction(9,94,73,true,true,false,true);assert(assets[218].density==4&&assets[219].density==4&&assets[321].density==4);}check_all();clear_assets();release();}free(index_storage);free(spriteSheet8.data);printf("{\"status\":\"PASS\",\"transactions\":%u,\"accepted\":%u,\"fallback\":%u,\"player_cases\":%u,\"guard_cases\":%u,\"pixel_comparisons\":%llu,\"full_frame_checks\":%u,\"exact_alpha_cases\":%llu}\n",cases,accepted_cases,fallback_cases,player_cases,guard_cases,(unsigned long long)comparisons,full_comparisons,(unsigned long long)alpha_cases);return 0;}
