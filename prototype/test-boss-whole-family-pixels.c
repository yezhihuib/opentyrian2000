/* Exact extracted production draw/ownership/RLE functions with independent
 * RGBA and physical-address oracles. Non-game source unit, never a capture. */
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define MAX(a,b) ((a)>(b)?(a):(b))
#define MIN(a,b) ((a)<(b)?(a):(b))
typedef uint8_t Uint8;typedef uint16_t Uint16;typedef uint32_t Uint32;
typedef struct {int x,y,w,h;} SDL_Rect;
typedef struct {int BitsPerPixel,BytesPerPixel;} SDL_PixelFormat;
typedef struct {int pitch,w,h;SDL_PixelFormat *format;void *pixels;} SDL_Surface;
typedef struct {Uint8 *data;size_t size;} Sprite2_array;
typedef struct {unsigned type,pool_slot,availability,size;bool score_item,damaged,independent_motion,static_animation;} G101EnemyContext;
typedef struct {int unused;} G101Record;
typedef struct {int unused;} PCapRecord;
typedef struct {int unused;} Forest13Record;
enum {ASSET_NEWSH2=101,ASSET_NEWSH4=102,ASSET_NEWSHE=110,ASSET_TALON_BANK=109,ASSET_SHAPESZ=201,ASSET_EXPLOSION=106};
enum {MIRROR_NORMAL=0,MIRROR_BLEND=1,MIRROR_SHADOW=2};
#include "production-types.inc"
static bool active=true,game_probe_missing,game_probe_invalid,suppress;
static bool game_probe_original_reference,game_probe_local_blend,suppress_green_smoke,suppress_cloud;
static int game_probe_density=8,game_probe_scene_assets=3;
static const char *game_probe_assets,*reject_reason;
static SDL_PixelFormat pixel_format={8,1};
static SDL_Surface surface_storage={320,320,200,&pixel_format,NULL},*game_screen=&surface_storage,*VGAScreen=&surface_storage;
static SDL_Surface canvas_storage={2560*4,2560,1600,NULL,NULL},*canvas=&canvas_storage;
static SDL_Surface output_storage={2560*4,2560,1600,NULL,NULL},*output=&output_storage;
static Sprite2_array enemySpriteSheets[4];static unsigned enemySpriteSheetIds[4];
static Uint32 rgb_palette[256];
static Uint8 expected[64000],selected[64000],*hd_owner,*cloud_owner,*green_under_owner;
static Uint16 *green_first;
static Uint32 *green_under;
typedef struct {Asset *asset;int x,y;} GreenHead;
static GreenHead green_heads[256];static unsigned green_head_count;
typedef struct {Uint16 peak[16][14];} GreenBackground;
typedef struct {SDL_Rect rect;int bank,index,style;bool live;} HdRegion;
static HdRegion regions[32];static unsigned region_count,draws,occlusions,local_entities;
static bool ready=true;static struct{bool valid;}world={true},fast_world={true};
static const G101Record *ground101_record(unsigned r,unsigned b){(void)r;(void)b;assert(0);return NULL;}
#define ground101_select(...) assert(0)
#define plateau_cap_select(...) assert(0)
#define forest13_select(...) assert(0)
#define ground101_actor_trace(...) ((void)0)
#define ground101_note_draw(...) ((void)0)
#define game_probe_scene_draw(...) ((void)0)
#define asset_debug_effect(...) ((void)0)
static unsigned font_before_calls,unsupported_calls;
static SDL_Rect font_before_rect;
static void font_before_effect(SDL_Rect r){font_before_calls++;font_before_rect=r;}
static bool font_pixel(int x,int y,Uint8 source,int style){(void)x;(void)y;(void)source;(void)style;return false;}
static void restore_classic_rect(SDL_Rect r){(void)r;assert(0);}
static void render_mirror_unsupported(const char*s){fprintf(stderr,"unexpected production rejection: %s\n",s);unsupported_calls++;assert(0);}
static Uint16 SDL_SwapLE16(Uint16 v){Uint8 b[2];memcpy(b,&v,2);return (Uint16)(b[0]|(unsigned)b[1]<<8);}
#include "production-functions.inc"

enum {D=8,W=320,H=200,SCREEN=W*H,CW=W*D,CH=H*D,N=CW*CH,PAD=16384,GUARD=128,REF=168*2+96*112*4};
static const unsigned ids[43]={1,3,5,7,10,12,14,16,18,39,41,43,45,48,50,54,56,86,88,90,92,94,124,126,128,130,132,162,164,168,170,200,202,206,208,240,242,244,246,280,238,278,282};
static const unsigned records[43]={53,53,53,53,46,47,48,49,50,53,53,53,53,51,52,54,55,56,57,58,59,60,61,62,63,64,65,46,47,49,50,51,52,54,55,57,58,59,60,63,56,62,64};
static const unsigned parts[4]={0,1,19,20};
static Uint8 reference[172][REF],indices[SCREEN],selection[SCREEN],*owner_ref,*cloud_ref;
static Uint16 *first_ref;
static Uint32 *color_ref;
static Uint8 *indexed_all;
static unsigned cases,accepted_cases,declined_cases,full_comparisons,crop_cases;
static uint64_t original_writes,wrapped_writes,rgba_writes,operator_cases,blend_cases,alpha_samples[3];
static int area[2048],area_count;
static unsigned char seen[SCREEN];
static struct {Uint8 *base;size_t size;} allocations[24];static unsigned allocated;
static void *guarded(size_t n){Uint8*p=malloc(n+GUARD*2);assert(p&&allocated<24);memset(p,0xa9,n+GUARD*2);allocations[allocated].base=p;allocations[allocated].size=n;allocated++;return p+GUARD;}
static void guards(void){for(unsigned a=0;a<allocated;a++)for(int j=0;j<GUARD;j++)assert(allocations[a].base[j]==0xa9&&allocations[a].base[GUARD+allocations[a].size+j]==0xa9);for(int i=0;i<PAD;i++)assert(indexed_all[i]==0xa9&&indexed_all[PAD+SCREEN+i]==0xa9);}
static Uint32 initial_color(size_t n){return 0xff000000u|((Uint32)(n*2654435761u+0x594123u)&0xffffffu);}
static Uint8 initial_index(int a){return (Uint8)(a*29+23);}
static void init_cell(int a){int x=a%W,y=a/W;indices[a]=expected[a]=((Uint8*)game_screen->pixels)[a]=initial_index(a);selection[a]=selected[a]=(Uint8)(a&1);for(int sy=0;sy<D;sy++)for(int sx=0;sx<D;sx++){int n=(y*D+sy)*CW+x*D+sx;color_ref[n]=((Uint32*)canvas->pixels)[n]=initial_color((size_t)n);owner_ref[n]=hd_owner[n]=(Uint8)(n%3);cloud_ref[n]=cloud_owner[n]=(Uint8)(n%2);first_ref[n]=green_first[n]=(Uint16)(n%4);green_under[n]=initial_color((size_t)n+19);green_under_owner[n]=(Uint8)((n+1)%3);}}
static void begin_area(int x,int y,bool clear){if(clear){memset(seen,0,sizeof(seen));area_count=0;region_count=0;green_head_count=0;draws=occlusions=font_before_calls=0;}for(int py=-2;py<16;py++)for(int px=-2;px<14;px++){int a=(y+py)*W+x+px;if(a>=0&&a<SCREEN&&!seen[a]){assert(area_count<2048);seen[a]=1;area[area_count++]=a;init_cell(a);}}render_mirror_entity_end();}
static void check_cell(int a){assert(indices[a]==((Uint8*)game_screen->pixels)[a]&&indices[a]==expected[a]&&selection[a]==selected[a]);int x=a%W,y=a/W;for(int sy=0;sy<D;sy++)for(int sx=0;sx<D;sx++){int n=(y*D+sy)*CW+x*D+sx;assert(color_ref[n]==((Uint32*)canvas->pixels)[n]);assert(owner_ref[n]==hd_owner[n]&&cloud_ref[n]==cloud_owner[n]&&first_ref[n]==green_first[n]);assert(green_under[n]==initial_color((size_t)n+19)&&green_under_owner[n]==(n+1)%3);}}
static void check_area(void){for(int j=0;j<area_count;j++)check_cell(area[j]);guards();assert(!unsupported_calls);}
static void check_all(void){for(int a=0;a<SCREEN;a++)check_cell(a);guards();full_comparisons++;}
/* Compare all observable framebuffer/ownership bytes at periodic boundaries.
 * Per-transaction bounded ROI and allocation canaries are checked separately.
 * Full-frame comparison runs every64 transactions and at phase boundaries. */
static void check_frame_bytes(void)
{
 assert(!memcmp(indices, game_screen->pixels, SCREEN));
 assert(!memcmp(indices, expected, SCREEN));
 assert(!memcmp(selection, selected, SCREEN));
 assert(!memcmp(color_ref, canvas->pixels, (size_t)N * 4));
 assert(!memcmp(owner_ref, hd_owner, N));
 assert(!memcmp(cloud_ref, cloud_owner, N));
 assert(!memcmp(first_ref, green_first, (size_t)N * 2));
 full_comparisons++;
}
static void palette(unsigned seed){for(unsigned i=0;i<256;i++){unsigned r=(i*37+seed*53)&255,g=((i^0x95)*71+seed*29)&255,b=(i*i*13+seed*97)&255;rgb_palette[i]=r<<16|g<<8|b;}}
/* Independent integer interpolation oracle: round a 0..3840 luminance
 * coordinate, OR both adjacent ramp indices, interpolate channels in 8 bits. */
static void filter_oracle(const Uint8*s,unsigned f,Uint8*out){unsigned peak=s[0];if(s[1]>peak)peak=s[1];if(s[2]>peak)peak=s[2];unsigned t=(peak*3840+127)/255,left=t>>8,right=left==15?15:left+1,weight=t&255;Uint32 a=rgb_palette[f|left],b=rgb_palette[f|right];for(int c=0;c<3;c++){unsigned shift=16-c*8;out[c]=(Uint8)((((a>>shift)&255)*(256-weight)+((b>>shift)&255)*weight+128)>>8);}out[3]=s[3];}
static void test_operator(void){const unsigned alpha[]={0,1,17,127,254,255};for(unsigned pal=0;pal<3;pal++){palette(pal);for(unsigned f=0;f<256;f++)for(unsigned peak=0;peak<256;peak++)for(unsigned a=0;a<6;a++){Uint8 in[4]={(Uint8)(peak/3),(Uint8)peak,(Uint8)(peak/2),(Uint8)alpha[a]},got[4],want[4];enemy_filter_rgba(in,(Uint8)f,got);filter_oracle(in,f,want);assert(!memcmp(got,want,4)&&!memcmp(in,(Uint8[]){peak/3,peak,peak/2,alpha[a]},4));operator_cases++;}}palette(1);}
/* Local destination is the result of every earlier ordered draw. Alpha-zero
 * preserves that RGB; the subsequent original RLE write still claims ownership
 * and must never restore indexed boss RGB through authored transparency. */
static Uint32 blend_oracle(Uint32 destination,const Uint8 *source)
{
 Uint32 result=0xff000000u;
 for(unsigned channel=0;channel<3;channel++) {
  unsigned shift=16-channel*8,d=(destination>>shift)&255;
  unsigned weighted=d*(255-source[3])+source[channel]*source[3];
  unsigned value=weighted/255+(weighted%255>=128);
  result|=value<<shift;
 }
 return result;
}
static void test_blend(void)
{
 for(unsigned alpha=0;alpha<256;alpha++)for(unsigned s=0;s<256;s++)for(unsigned d=0;d<256;d++) {
  Uint8 source[4]={(Uint8)s,(Uint8)(255-s),(Uint8)(s^0x69),(Uint8)alpha};
  Uint32 destination=0xff000000u|d<<16|(255-d)<<8|(d^0x96);
  assert(blend_rgba(destination,source,(int)alpha)==blend_oracle(destination,source));blend_cases++;
 }
}
static void oracle_draw(unsigned k,int x,int y,unsigned filter)
{
 const Uint8 *rgba=reference[k]+336,*support=reference[k]+168;
 for(int ay=0;ay<112;ay++)for(int ax=0;ax<96;ax++) {
  int dx=x*D+ax,dy=y*D+ay;
  if(dx<0||dy<0||dx>=CW||dy>=CH)continue;
  const Uint8 *s=rgba+4*(ay*96+ax);
  if(support[(ay/D)*12+ax/D])alpha_samples[!s[3]?0:s[3]==255?2:1]++;
  if(!s[3])continue;
  Uint8 filtered[4];if(filter){filter_oracle(s,filter,filtered);s=filtered;}
  int n=dy*CW+dx;
  color_ref[n]=blend_oracle(color_ref[n],s);
  owner_ref[n]=1;cloud_ref[n]=0;first_ref[n]=0;
  selection[(dy/D)*W+dx/D]=1;rgba_writes++;
 }
}
static void oracle_original(unsigned k,int x,int y,unsigned filter,bool accepted){const Uint8*mask=reference[k]+168;for(int py=0;py<14;py++)for(int px=0;px<12;px++){int c=py*12+px;if(!mask[c])continue;int a=(y+py)*W+x+px;if(a<0||a>=SCREEN)continue;assert(seen[a]);Uint8 v=reference[k][c];if(filter)v=(Uint8)(filter|(v&15));indices[a]=v;selection[a]=(Uint8)accepted;for(int sy=0;sy<D;sy++)for(int sx=0;sx<D;sx++){int n=((a/W)*D+sy)*CW+(a%W)*D+sx;owner_ref[n]=(Uint8)accepted;cloud_ref[n]=0;if(!accepted){first_ref[n]=0;color_ref[n]=0xff000000u|rgb_palette[v];}}original_writes++;if(x+px<0||x+px>=W)wrapped_writes++;}}
static void run_transaction(unsigned k,int x,int y,unsigned filter,bool clear)
{
 begin_area(x,y,clear);unsigned old_draws=draws,old_font=font_before_calls;bool safe=k<160&&x>=0&&x<=308&&y>=-13&&y<=199;
 G101EnemyContext context={.type=records[k/4],.size=1,.pool_slot=25,.static_animation=true};bool accepted=render_mirror_enemy_tile(game_screen,x,y,enemySpriteSheets[0],ids[k/4],(int)parts[k%4],(int)filter,&context);assert(accepted==safe);
 if(accepted){int px=k%4&1?12:0,py=k%4&2?14:0;accepted_cases++;assert(draws==old_draws+1&&suppress&&!suppress_cloud&&!suppress_green_smoke&&font_before_calls==old_font+1);bool found=false;for(unsigned i=0;i<region_count;i++)if(regions[i].bank==102&&regions[i].index==(int)ids[k/4]&&regions[i].style==MIRROR_NORMAL&&regions[i].rect.x==x-px&&regions[i].rect.y==y-py&&regions[i].rect.w==24&&regions[i].rect.h==28)found=true;assert(found);assert(font_before_rect.x==x-px&&font_before_rect.y==y-py&&font_before_rect.w==24&&font_before_rect.h==28);oracle_draw(k,x,y,filter);}
 else{declined_cases++;assert(draws==old_draws&&!suppress&&!suppress_cloud&&!suppress_green_smoke&&font_before_calls==old_font);}
 check_area();oracle_original(k,x,y,filter,accepted);if(filter)blit_sprite2_filter(game_screen,x,y,enemySpriteSheets[0],ids[k/4]+parts[k%4],(Uint8)filter);else blit_sprite2(game_screen,x,y,enemySpriteSheets[0],ids[k/4]+parts[k%4]);render_mirror_entity_end();assert(!suppress&&!suppress_cloud&&!suppress_green_smoke);check_area();if(!(cases%64))check_frame_bytes();cases++;
}
static void run_case(unsigned k,int x,int y,unsigned filter){run_transaction(k,x,y,filter,true);}
/* Execute the exact production ordinary crop loop on the finished canvas.
 * A pointwise independent oracle proves the surrounding HUD/overscan stays
 * unchanged and that source-space x24..287/y0..183 maps to output x0..263. */
static void check_crop(void)
{
 Uint32 *pixels=output->pixels;
 for(int n=0;n<N;n++)pixels[n]=0x81234567u;
 production_crop_excerpt();
 for(int y=0;y<CH;y++)for(int x=0;x<CW;x++) {
  Uint32 want=x<2112&&y<1472?color_ref[y*CW+x+192]:0x81234567u;
  assert(pixels[y*CW+x]==want);
 }
 crop_cases++;
 guards();
}
static Uint8 *read_file(const char*path,size_t*size){FILE*f=fopen(path,"rb");assert(f&&!fseek(f,0,SEEK_END));long n=ftell(f);assert(n>0&&!fseek(f,0,SEEK_SET));Uint8*p=malloc((size_t)n);assert(p&&fread(p,1,(size_t)n,f)==(size_t)n&&!fclose(f));*size=(size_t)n;return p;}
int main(int argc,char**argv){assert(argc==4);game_probe_assets=argv[1];size_t n;Uint8*bank=read_file(argv[2],&n);enemySpriteSheets[0]=(Sprite2_array){bank,n};enemySpriteSheetIds[0]=2;Uint8*ref=read_file(argv[3],&n);assert(n==sizeof(reference));memcpy(reference,ref,n);free(ref);indexed_all=guarded(SCREEN+2*PAD);game_screen->pixels=indexed_all+PAD;canvas->pixels=guarded((size_t)N*4);output->pixels=guarded((size_t)N*4);hd_owner=guarded(N);cloud_owner=guarded(N);green_first=guarded((size_t)N*2);green_under=guarded((size_t)N*4);green_under_owner=guarded(N);color_ref=guarded((size_t)N*4);owner_ref=guarded(N);cloud_ref=guarded(N);first_ref=guarded((size_t)N*2);for(int a=0;a<SCREEN;a++)init_cell(a);test_operator();test_blend();
 for(unsigned k=0;k<172;k++){for(unsigned f=0;f<256;f++)run_case(k,94,73,f);if(k%4==3)check_all();}
 const int clipped[][2]={{0,-13},{308,-13},{24,-1},{0,0},{308,0},{24,186},{275,187},{0,199},{308,199},{94,-14},{94,200},{94,214}};
 const unsigned filters[]={0,9,255};
 for(unsigned k=0;k<172;k++){for(unsigned c=0;c<sizeof(clipped)/sizeof(*clipped);c++)for(unsigned f=0;f<3;f++)run_case(k,clipped[c][0],clipped[c][1],filters[f]);if(k%4==3)check_all();}
 const int xs[]={-321,-13,-12,-1,309,319,320,321},ys[]={-14,-13,0,187,199,200,214};
 for(unsigned k=0;k<172;k++){for(unsigned xi=0;xi<sizeof(xs)/sizeof(*xs);xi++)for(unsigned yi=0;yi<sizeof(ys)/sizeof(*ys);yi++)for(unsigned f=0;f<3;f++)run_case(k,xs[xi],ys[yi],filters[f]);if(k%4==3)check_all();}
 /* Ordered four-quadrant draws and second-actor overlap retain all prior
  * pixels/ownership. Also exercise mixed classic/HD geometry locally. */
 const int origins[][2]={{94,73},{-1,73},{300,73},{94,-14},{94,190}};
 for(unsigned base=0;base<40;base++)for(unsigned pos=0;pos<5;pos++)for(unsigned f=0;f<3;f++){
  for(unsigned actor=0;actor<2;actor++)for(unsigned q=0;q<4;q++){unsigned k=((base+actor)%40)*4+q;int x=origins[pos][0]+(int)actor*6+(q&1?12:0),y=origins[pos][1]+(int)actor*7+(q&2?14:0);run_transaction(k,x,y,filters[f],!actor&&!q);}check_frame_bytes();
 }
 const int crop_positions[][2]={{23,40},{12,40},{276,40},{287,40},{94,183},{94,184},{23,-1},{287,183}};
 for(unsigned base=0;base<40;base++)for(unsigned c=0;c<8;c++){unsigned k=base*4+c%4;run_case(k,crop_positions[c][0],crop_positions[c][1],filters[c%3]);check_crop();}
 for(unsigned base=0;base<40;base++){Asset*a=&assets[422+base];assert(a->initialized&&a->valid&&a->w==24&&a->h==28&&a->anchor_x==6&&a->anchor_y==7&&a->density==8);for(unsigned q=0;q<4;q++)for(unsigned y=0;y<112;y++)assert(!memcmp(a->rgba+(((q&2?112:0)+y)*192+(q&1?96:0))*4,reference[base*4+q]+336+y*96*4,96*4));}check_all();
 assert(alpha_samples[0]&&alpha_samples[1]&&alpha_samples[2]);
 printf("Ordered local-underlay alpha samples zero/fractional/opaque: %llu/%llu/%llu; exhaustive blend cases: %llu\n",(unsigned long long)alpha_samples[0],(unsigned long long)alpha_samples[1],(unsigned long long)alpha_samples[2],(unsigned long long)blend_cases);
 for(unsigned k=0;k<sizeof(assets)/sizeof(*assets);k++)free(assets[k].rgba);for(unsigned k=0;k<allocated;k++)free(allocations[k].base);free(bank);
 printf("PASS production pixel unit: %u cases (%u HD, %u classic); %llu RGBA writes; %llu original writes (%llu row-wrapped); %llu filter/alpha operator cases; %u whole-frame comparisons; %u production crop cases; all64 subpixels and ownership exact within each transaction ROI,600 ordered overlap sequences\n",cases,accepted_cases,declined_cases,(unsigned long long)rgba_writes,(unsigned long long)original_writes,(unsigned long long)wrapped_writes,(unsigned long long)operator_cases,full_comparisons,crop_cases);return 0;}
