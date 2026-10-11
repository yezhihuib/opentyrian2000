#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef uint8_t Uint8;
typedef uint16_t Uint16;
typedef uint32_t Uint32;
typedef struct {int x,y,w,h;} SDL_Rect;
typedef struct {int BitsPerPixel;} SDL_PixelFormat;
typedef struct {int w,h,pitch;void *pixels;SDL_PixelFormat *format;} SDL_Surface;
enum {MIRROR_NORMAL,MIRROR_BLEND,MIRROR_SHADOW};
enum {ASSET_NEWSH2=101,ASSET_NEWSHE=110,ASSET_TALON_BANK=109,ASSET_EXPLOSION=106,ASSET_SHAPESZ=201};
#include "production-types.inc"
#define CHECK(x) do {if(!(x)){fprintf(stderr,"FAIL %s:%d: %s\n",__FILE__,__LINE__,#x);abort();}++checks;}while(0)
static unsigned long checks;
static SDL_Surface storage,screen,*canvas=&storage,*game_screen=&screen;
static int game_probe_density;
static bool game_probe_original_reference,game_probe_local_blend,game_probe_missing,game_probe_invalid;
static const char *game_probe_assets="/nonexistent-layer3-purple-fixture",*reject_reason;
static bool suppress,suppress_green_smoke,suppress_cloud,active=true;
static unsigned draws,local_entities,region_count,green_head_count,traces,occlusions,terrain_source_count,game_probe_scene_assets=2;
static char terrain_file;
typedef struct {SDL_Rect rect;int bank,index,style;bool live;} HdRegion;
static HdRegion regions[256];
typedef struct {Asset *asset;int x,y;} GreenHead;
static GreenHead green_heads[256];
typedef struct {Uint16 peak[16][14];} GreenBackground;
static Uint8 *cloud_owner,*hd_owner,*green_under_owner;
static Uint16 *green_first;
static Uint32 *green_under;
static Uint8 selected[320*200],expected[320*200];
static const unsigned ids[]={150,156,157,158,159,160,166,168,169,170,176,177,178,121,122,123,124,125,131,132,133,134,135,141,142,143,144,151,152,153,154,66,67,69,76,78,79,80,89,90};
static Uint8 rgba[40][192*224*4],original[40][672],indexed_backing[320*(36+56)];
static Uint8 *indexed=indexed_backing+320*28;
static bool valid[40];
static void unreachable(void){CHECK(!"unrelated effect or restore path executed");}
static int explosion_asset_slot(unsigned i){(void)i;unreachable();return -1;}
static void restore_classic_rect(SDL_Rect r){(void)r;unreachable();}
static void render_mirror_unsupported(const char *why){fprintf(stderr,"unexpected: %s\n",why);unreachable();}
static void green_background_snapshot(GreenBackground *b,int x,int y){(void)b;(void)x;(void)y;unreachable();}
static void enemy_filter_rgba(const Uint8 *s,Uint8 f,Uint8 *d){(void)s;(void)f;(void)d;unreachable();}
static Uint32 palette_rgb(Uint8 i){return 0xff000000u|((unsigned)i*71%256)<<16|((unsigned)i*37%256)<<8|((unsigned)i*19%256);}
static unsigned green_background_peak(const GreenBackground *b,int x,int y,Uint32 p){(void)b;(void)x;(void)y;(void)p;unreachable();return 0;}
static void explosion_asset_blend_rgba(Uint32 p,const Uint8 *s,Uint8 *d){(void)p;(void)s;(void)d;unreachable();}
static Uint32 green_head_composite(int x,int y,unsigned f,Uint32 p){(void)x;(void)y;(void)f;(void)p;unreachable();return 0;}
static Uint32 cloud_shadow_rgba(Uint32 p,Uint8 a,Uint8 b){(void)p;(void)a;(void)b;unreachable();return 0;}
static void render_mirror_reset_banking(void){}
static void asset_debug_terrain_row(int x,int y,Uint8 **map){(void)x;(void)y;CHECK(map);}
static void game_probe_scene_draw(int role,unsigned id,int x,int y,int part,int style,bool mirrored)
{(void)x;(void)y;bool found=false;for(unsigned j=0;j<40;j++)found|=ids[j]==id;CHECK(role==201&&found&&part==0&&style==MIRROR_NORMAL&&mirrored);traces++;}
#include "production-helpers.inc"
static Uint32 background(unsigned n){return 0xff203040u+(n%71)*0x00010101u;}
static Uint8 initial_owner(unsigned n){return (Uint8)(n%3);}
static Uint32 normal_color(Uint32 old,const Uint8 *p)
{
 Uint32 out=0xff000000u;for(int c=0;c<3;c++){unsigned shift=(unsigned)(2-c)*8;out|=((((old>>shift)&255)*(255-p[3])+p[c]*p[3]+127)/255)<<shift;}return out;
}
/* These controls deliberately include artificial alpha holes. The verified
 * original purple family is fully opaque; no fixture here is authored art. */
static int slot(unsigned j){return j>=31?312+(int)j-31:j<13?290+(int)j:272+(int)j-13;}
static void fill_tile(unsigned j,int mode)
{
 for(unsigned k=0;k<672;k++){
  bool occupied=(mode!=1&&mode!=2)||(k%24+k/24+ids[j])%4;
  original[j][k]=occupied?((Uint8)(ids[j]+k)%254+1):0;
 }
 const unsigned fractional[]={1,127,128,254,255};
 const unsigned fractional_with_zero[]={0,1,127,128,254,255};
 for(unsigned ay=0;ay<224;ay++)for(unsigned ax=0;ax<192;ax++){
  unsigned k=ay*192+ax;bool occupied=original[j][(ay/8)*24+ax/8]!=0;
  rgba[j][4*k]=(Uint8)(ids[j]+ax*3+ay);rgba[j][4*k+1]=(Uint8)(ids[j]*3+ax+ay*5);rgba[j][4*k+2]=(Uint8)(ids[j]*7+ax*11+ay);
  rgba[j][4*k+3]=mode==4?0:mode==3?fractional_with_zero[(ax+2*ay)%6]:occupied?(mode==2?fractional[(ax+2*ay)%5]:255):0;
 }
}
static void reset_scene(void)
{
 memset(assets,0,sizeof(assets));memset(valid,0,sizeof(valid));render_mirror_map_begin('Z');
 size_t n=(size_t)canvas->w*canvas->h;
 for(size_t k=0;k<n;k++){((Uint32*)canvas->pixels)[k]=background((unsigned)k);cloud_owner[k]=1;hd_owner[k]=initial_owner((unsigned)k);green_first[k]=7;green_under[k]=0xabcdef01;green_under_owner[k]=2;}
 memset(indexed_backing,0xa5,sizeof(indexed_backing));memset(indexed,17,320*36);memset(expected,17,sizeof(expected));memset(selected,0,sizeof(selected));region_count=green_head_count=draws=local_entities=traces=occlusions=0;
 suppress=suppress_cloud=suppress_green_smoke=false;
}
static void prepare(unsigned j,int mode,int missing,bool bind)
{
 fill_tile(j,mode);if(bind)render_mirror_bind_terrain(j>=31?1:3,ids[j],original[j]);valid[j]=bind&&missing==0;
 if(missing!=1)assets[slot(j)]=(Asset){true,missing==0,201,(int)ids[j],24,28,0,0,8,rgba[j]};
}
/* model[tile] is -1 for NULL; bind=false is represented by valid[j]==false.
 * The reference below does not consult production slots, state, or compositor. */
static void assert_row(const int *model,int x,int y,bool indexed_draw,bool replacement_allowed)
{
 int d=game_probe_density;
 for(int cy=0;cy<canvas->h;cy++)for(int cx=0;cx<canvas->w;cx++){
  unsigned k=(unsigned)(cy*canvas->w+cx);int rx=cx-x*d,ay=cy-y*d;
  bool inrow=rx>=0&&rx<12*24*d&&ay>=0&&ay<28*d;
  int tile=inrow?rx/(24*d):-1,j=tile>=0?model[tile]:-1,ax=inrow?rx%(24*d):0;
  const Uint8 *p=j>=0?rgba[j]+4*((ay*8/d)*192+ax*8/d):NULL;
  Uint8 classic=j>=0?original[j][(ay/d)*24+ax/d]:0;
  bool replaced=j>=0&&valid[j]&&replacement_allowed,covered=p&&p[3]&&replaced;
  bool classic_write=classic&&indexed_draw,classic_rgb=classic_write&&!replaced;
  Uint32 wanted=covered?normal_color(background(k),p):classic_rgb?palette_rgb(classic):background(k);
  CHECK(((Uint32*)canvas->pixels)[k]==wanted);
  CHECK(cloud_owner[k]==(covered||classic_rgb?0:1));CHECK(green_first[k]==(covered||classic_rgb?0:7));
  Uint8 owner=covered||(replaced&&classic_write)?1:classic_rgb?0:initial_owner(k);
  CHECK(hd_owner[k]==owner);CHECK(green_under[k]==0xabcdef01);CHECK(green_under_owner[k]==2);
 }
 for(int cy=0;cy<36;cy++)for(int cx=0;cx<320;cx++){
  int rx=cx-x,ay=cy-y;bool inrow=rx>=0&&rx<12*24&&ay>=0&&ay<28;
  int tile=inrow?rx/24:-1,j=tile>=0?model[tile]:-1,ax=inrow?rx%24:0;
  Uint8 value=j>=0?original[j][ay*24+ax]:0;
  CHECK(indexed[cy*320+cx]==(indexed_draw&&value?value:17));CHECK(expected[cy*320+cx]==(indexed_draw&&value?value:17));
  bool want_selected=false;
  if(j>=0&&valid[j]&&replacement_allowed){
   want_selected=indexed_draw&&value;
   for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++)if(cx*d+sx<canvas->w&&cy*d+sy<canvas->h)
    want_selected|=rgba[j][4*(((ay*d+sy)*8/d)*192+(ax*d+sx)*8/d)+3]!=0;
  }
  CHECK(selected[cy*320+cx]==want_selected);
 }
 for(unsigned k=0;k<320*28;k++){CHECK(indexed_backing[k]==0xa5);CHECK(indexed_backing[320*(28+36)+k]==0xa5);}
 CHECK(!local_entities&&!green_head_count&&!occlusions);
}
static void allocate(int d,int width)
{
 game_probe_density=d;canvas->w=width*d;canvas->h=36*d;canvas->pitch=canvas->w*4;
 size_t n=(size_t)canvas->w*canvas->h;canvas->pixels=malloc(n*4);cloud_owner=malloc(n);hd_owner=malloc(n);green_under_owner=malloc(n);green_first=malloc(n*2);green_under=malloc(n*4);
 CHECK(canvas->pixels&&cloud_owner&&hd_owner&&green_under_owner&&green_first&&green_under);
}
static void release(void){free(canvas->pixels);free(cloud_owner);free(hd_owner);free(green_under_owner);free(green_first);free(green_under);}
static void one_tile_cases(void)
{
 for(int d=2;d<=8;d*=2){
  allocate(d,64);
  for(unsigned j=0;j<40;j++)for(int mode=0;mode<5;mode++)for(int placement=0;placement<4;placement++){
   int x=placement>=2?32:0,y=placement==0?1:placement==1?-3:placement==2?30:1;
   int column=placement==3?1:0;int model[12];for(unsigned k=0;k<12;k++)model[k]=-1;model[column]=(int)j;
   Uint8 *row[12]={0};row[column]=original[j];
   reset_scene();prepare(j,mode,0,true);CHECK(render_mirror_terrain_row(game_screen,x,y,row,MIRROR_NORMAL)==(1u<<column));CHECK(draws==1&&traces==1&&!suppress&&!suppress_cloud&&!suppress_green_smoke);assert_row(model,x,y,false,true);
   /* A64-pixel canvas can independently test right clipping, but the original
    * indexed callback requires full canvas coverage for every written column. */
   if(placement<3){reset_scene();prepare(j,mode,0,true);blit_background_row(game_screen,x,y,row);CHECK(draws==1&&traces==1&&!suppress);assert_row(model,x,y,true,true);}
  }
  for(unsigned j=0;j<40;j++)for(int missing=1;missing<=2;missing++)for(int placement=0;placement<3;placement++){
   int model[12];for(unsigned k=0;k<12;k++)model[k]=-1;model[0]=(int)j;
   int y=placement==0?1:placement==1?-3:30;
   reset_scene();prepare(j,0,missing,true);Uint8 *row[12]={original[j]};blit_background_row(game_screen,0,y,row);CHECK(!draws&&!traces&&!region_count);assert_row(model,0,y,true,true);
  }
  const int styles[]={INT_MIN,-1,MIRROR_BLEND,MIRROR_SHADOW,3,INT_MAX};
  for(unsigned j=0;j<31;j++)for(unsigned s=0;s<sizeof(styles)/sizeof(*styles);s++){
   int model[12];for(unsigned k=0;k<12;k++)model[k]=-1;model[0]=(int)j;
   reset_scene();prepare(j,3,0,true);Uint8 *row[12]={original[j]};CHECK(!render_mirror_terrain_row(game_screen,0,1,row,styles[s]));CHECK(!draws&&!traces&&!region_count&&!suppress);assert_row(model,0,1,false,false);
  }
  int empty_model[12];for(unsigned k=0;k<12;k++)empty_model[k]=-1;
  reset_scene();Uint8 *empty[12]={0};blit_background_row(game_screen,0,1,empty);CHECK(!draws&&!traces);assert_row(empty_model,0,1,true,true);
  release();
 }
}
static void mixed_cases(void)
{
 const unsigned masks[]={0,1,2048,0x555,0xaaa,0xfff,0xa91};
 for(int d=2;d<=8;d*=2){
  allocate(d,320);
  for(unsigned mix=0;mix<2;mix++)for(unsigned profile=0;profile<3;profile++)for(unsigned m=0;m<7;m++){
   reset_scene();int model[12];Uint8 *row[12];unsigned wanted=0;
   for(unsigned k=0;k<12;k++){
    unsigned j=mix==0?(k%2?13+(k+profile*5)%18:(k+profile*5)%13):k%3==0?31+(k/3+profile)%9:k%3==1?13+(k/3+profile*5)%18:(k/3+profile*5)%13;
    model[k]=(masks[m]&(1u<<k))?(int)j:-1;row[k]=model[k]<0?NULL:original[j];
    int missing=profile==1&&k%3==0?2:0;bool bind=!(profile==2&&k%3==0);
    prepare(j,(int)(k%5),missing,bind);if(model[k]>=0&&valid[j])wanted++;
   }
   blit_background_row(game_screen,16,profile==2?-3:1,row);CHECK(draws==wanted&&traces==wanted&&region_count==wanted&&!suppress);
   assert_row(model,16,profile==2?-3:1,true,true);
  }
  release();
 }
}
/* Optional frozen art: independently decoded PNG bytes are the oracle;
 * the original production HDA loader supplies the actual compositor input. */
static void actual_cases(const char *pack,const char *oracle)
{
 const char *saved=game_probe_assets;game_probe_assets=pack;
 for(int d=2;d<=8;d*=2){
  allocate(d,64);
  for(unsigned k=0;k<9;k++)for(unsigned placement=0;placement<3;placement++){
   unsigned j=31+k;int y=placement==0?1:placement==1?-3:30;
   reset_scene();fill_tile(j,0);char path[4096];
   CHECK(snprintf(path,sizeof(path),"%s/actual-%u.rgba",oracle,ids[j])<(int)sizeof(path));
   FILE *f=fopen(path,"rb");CHECK(f);CHECK(fread(rgba[j],1,sizeof(rgba[j]),f)==sizeof(rgba[j]));CHECK(fgetc(f)==EOF);CHECK(!fclose(f));
   render_mirror_bind_terrain(1,ids[j],original[j]);valid[j]=true;
   /* Load the native8 asset, then exercise unchanged downsampling at2/4/8. */
   game_probe_density=8;Asset *loaded=scene_asset(slot(j),ASSET_SHAPESZ,(int)ids[j],0,0);game_probe_density=d;
   CHECK(loaded&&loaded->valid&&loaded->density==8);CHECK(!memcmp(loaded->rgba,rgba[j],sizeof(rgba[j])));
   int model[12];for(unsigned c=0;c<12;c++)model[c]=-1;model[0]=(int)j;Uint8 *row[12]={original[j]};
   blit_background_row(game_screen,0,y,row);CHECK(draws==1&&traces==1&&!suppress);assert_row(model,0,y,true,true);
   free(loaded->rgba);loaded->rgba=NULL;
  }
  release();
 }
 game_probe_assets=saved;puts("PASS: actual frozen grass9 PNG oracle vs production HDA loader and NORMAL compositor,81 placements/scales; exact RGB/indexed/ownership/clip output.");
}
int main(int argc,char **argv)
{
 SDL_PixelFormat format={8};screen=(SDL_Surface){320,36,320,indexed,&format};
 CHECK(argc==1||argc==3);one_tile_cases();mixed_cases();if(argc==3)actual_cases(argv[1],argv[2]);
 printf("PASS: %lu assertions; actual NORMAL row/compositor/original indexed blitter and pixel callback, all40 grass/sand9 plus prior purple13/gray18 IDs,2x/4x/8x; opaque, binary holes, fractional alpha, synthetic holes over opaque source and allzero controls; top/bottom/horizontal clipping, missing/invalid/null/unbound fallback,126 original gray/purple plus mixed grass/sand/gray/purple rows; exact RGBA/owner metadata/indexed writes/guard bytes; all prior Layer3 non-NORMAL style classes do not draw or restore.\n",checks);return 0;
}
