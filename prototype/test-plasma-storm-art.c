/* Exact production Storm art: reuse the retained compatibility harness without
 * editing its historical evidence. The added oracle evaluates all subpixels. */
#define main compatibility_test_main
#include "test-plasma-projectile-blend.c"
#undef main
#define MAX_PWEAPON 81
#define SHOT_RIGHT_SIDEKICK 3
#define LEFT_SIDEKICK 0
#define RIGHT_SIDEKICK 1
#define DIFFICULTY_NORMAL 2
#define DIFFICULTY_HARD 3
#define SA_NONE 0
#include "asset-enum.inc"
typedef struct {bool initialized,valid;int bank,index,w,h,anchor_x,anchor_y,density;Uint8 *rgba;} Asset;
static unsigned episodeNum=1,lvlFileNum=9,initialDifficulty=DIFFICULTY_NORMAL,superArcadeMode;
static bool xmas,isNetworkGame,twoPlayerMode,twoPlayerLinked,galagaMode,play_demo,record_demo;
static bool onePlayerAction,superTyrian,timedBattleMode,bonusLevel,normalBonusLevelCurrent,bonusLevelCurrent;
static bool game_probe_missing,game_probe_invalid;
static int game_probe_scene_assets=3;
static const char *game_probe_assets;
static uint64_t mirror_logic_tick=1;
static struct {struct {unsigned sidekick[2];}items;struct {unsigned style,charge;} sidekick[2];} player[2];
static struct {unsigned playerNumber,shotGr;} playerShotData[MAX_PWEAPON+1];
static int vulcan_shadow_member(unsigned i){(void)i;return -1;}
static struct {const Uint8 *rgba;char path[1024];} vulcan_shadow_resource[13],vulcan_shadow_coverage_resource[3];
#include "art-functions.inc"
typedef enum {MIRROR_OUTPUT_UNSUPPORTED,MIRROR_OUTPUT_ORDINARY,MIRROR_OUTPUT_NORMAL15_NIGHT,MIRROR_OUTPUT_NORMAL15_LOW_DETAIL} MirrorOutputKind;
static SDL_Surface display,output_screen,*VGAScreenSeg=&display,*output=&output_screen;
#include "normal15-functions.inc"
static Uint8 *art_rgba[3][2];
static Uint16 *oracle_values[3][2];
static Uint32 oracle_palette[3][2][16];
static bool oracle_cache_valid[3][2];
static unsigned art_draws,art_admitted,art_guards,resource_guards,cache_guards,projection_checks;
static unsigned contour_added,contour_suppressed,all_heights,ordered_draws,hard_checks;
static Uint32 *art_expected;
static Uint8 *art_owner,*art_cloud,*art_selected;
static Uint16 *art_green;

/* Independent exhaustive nearest-grid oracle used to certify production's
 * segment projection on sampled colors, ties, flat segments and all palettes. */
static Uint16 slow_project(const Uint8 *p)
{
 uint64_t best=UINT64_MAX;unsigned winner=0;
 for(unsigned pos=0;pos<=3840;pos++) {
  unsigned segment=pos==3840?14:pos/256,t=pos-segment*256;uint64_t distance=0;
  for(unsigned c=0;c<3;c++) {
   int a=(rgb_palette[112+segment]>>(16-8*c))&255,b=(rgb_palette[113+segment]>>(16-8*c))&255;
   int64_t diff=(int)p[c]*256-((int)(256-t)*a+(int)t*b);distance+=(uint64_t)(diff*diff);
  }
  if(distance<best){best=distance;winner=pos;}
 }
 return (Uint16)winner;
}
/* Separate algebra for per-texel oracle: evaluate floor and ceil candidates
 * explicitly rather than using production's rounded/clamped projection. */
static Uint16 reference_project(const Uint8 *p)
{
 uint64_t best=UINT64_MAX;unsigned winner=0;
 for(int seg=0;seg<15;seg++) {
  int a[3],b[3];int64_t numerator=0,denominator=0;
  for(int c=0;c<3;c++){a[c]=(rgb_palette[112+seg]>>(16-8*c))&255;b[c]=(rgb_palette[113+seg]>>(16-8*c))&255;numerator+=(p[c]-a[c])*(b[c]-a[c])*256;denominator+=(b[c]-a[c])*(b[c]-a[c]);}
  int floor=denominator?(int)(numerator/denominator):0;
  for(int n=0;n<2;n++) {
   int t=floor+n;if(t<0)t=0;if(t>256)t=256;uint64_t distance=0;
   for(int c=0;c<3;c++){int64_t diff=(int64_t)p[c]*256-(a[c]*(256-t)+b[c]*t);distance+=(uint64_t)(diff*diff);}
   unsigned pos=(unsigned)(seg*256+t);if(distance<best||(distance==best&&pos<winner)){best=distance;winner=pos;}
  }
 }
 return (Uint16)winner;
}
static Uint32 art_reference_blend(Uint32 under,unsigned owner,unsigned before,unsigned source,unsigned alpha)
{
 unsigned peak=0;for(unsigned c=0;c<3;c++){unsigned v=(under>>(c*8))&255;if(v>peak)peak=v;}
 unsigned uv=owner==1?(peak*3840+127)/255:(before%16)*256;
 unsigned v=(uv+source)>>1,lo=v>>8,t=v&255,hi=lo==15?15:lo+1;Uint32 result=0xff000000u;
 for(unsigned c=0;c<3;c++) {
  unsigned a=(rgb_palette[112+lo]>>(8*c))&255,b=(rgb_palette[112+hi]>>(8*c))&255;
  unsigned blended=((256-t)*a+t*b+128)>>8;
  result|=((alpha*blended+(255-alpha)*((under>>(8*c))&255)+127)/255)<<(8*c);
 }
 return result;
}
static void art_context(void)
{
 episodeNum=1;lvlFileNum=9;initialDifficulty=DIFFICULTY_NORMAL;superArcadeMode=SA_NONE;
 xmas=isNetworkGame=twoPlayerMode=twoPlayerLinked=galagaMode=play_demo=record_demo=false;
 onePlayerAction=superTyrian=timedBattleMode=bonusLevel=normalBonusLevelCurrent=bonusLevelCurrent=false;
 game_probe_missing=game_probe_invalid=false;game_probe_scene_assets=3;
 player[0].items.sidekick[0]=0;player[0].items.sidekick[1]=9;
 player[0].sidekick[1].style=player[0].sidekick[1].charge=0;
 plasma_art_reset();
 for(unsigned k=0;k<3;k++) {playerShotData[k].playerNumber=1;playerShotData[k].shotGr=60023+k;render_mirror_plasma_art_emit(k,88,SHOT_RIGHT_SIDEKICK,1,60023+k);}
}
static void art_snapshot(unsigned k,int x,int y)
{
 unsigned di=game_probe_density==8,d=(unsigned)game_probe_density,w=originals[0][k].s.width,h=originals[0][k].s.height;
 Uint8 *rgba=art_rgba[k][di];Uint16 *values=oracle_values[k][di];
 if(!oracle_cache_valid[k][di]||memcmp(oracle_palette[k][di],rgb_palette+112,64)) {
  for(size_t n=0;n<(size_t)w*h*d*d;n++)values[n]=rgba[n*4+3]?reference_project(rgba+n*4):0;
  memcpy(oracle_palette[k][di],rgb_palette+112,64);oracle_cache_valid[k][di]=true;
 }
 memcpy(art_expected,wanted_rgba,hd_pixels*4);memcpy(art_owner,wanted_owner,hd_pixels);
 memcpy(art_cloud,wanted_cloud,hd_pixels);memcpy(art_green,wanted_green,hd_pixels*2);memcpy(art_selected,wanted_selected,64000);
 for(unsigned ly=0;ly<h;ly++)for(unsigned lx=0;lx<w;lx++) {
  int yy=y+(int)ly,xx=x+(int)lx;if(yy<0||yy>=200||xx<0||xx>=320)continue;
  bool covered=originals[0][k].mask[ly*w+lx]!=0,touched=covered;unsigned before=oracle_store[PAD+yy*screen.pitch+xx];
  for(unsigned sy=0;sy<d;sy++)for(unsigned sx=0;sx<d;sx++) {
   size_t n=(size_t)(yy*d+sy)*hd.w+xx*d+sx,at=(size_t)(ly*d+sy)*w*d+lx*d+sx;unsigned alpha=rgba[at*4+3];
   if(alpha)art_expected[n]=art_reference_blend(wanted_rgba[n],wanted_owner[n],before,values[at],alpha);
   if(alpha||covered){art_owner[n]=1;art_cloud[n]=0;art_green[n]=0;touched=true;}
   if(alpha&&!covered)contour_added++;if(!alpha&&covered)contour_suppressed++;
  }
  if(touched)art_selected[yy*320+xx]=0;
 }
}
static void art_draw(unsigned k,int x,int y,bool admitted_art,bool compatible)
{
 if(admitted_art)art_snapshot(k,x,y);
 unsigned calls=raw_calls,bcalls=baseline_raw_calls;candidate_count=baseline_count=0;baseline_screen.pitch=screen.pitch;
 uint64_t beforehash=hash_bytes(sprite(5,22+k)->data,sprite(5,22+k)->size);
 render_mirror_plasma_art_prepare(&screen,x,y,k,5,22+k);CHECK(plasma_art_call.live==admitted_art);
 baseline_blit_sprite_blend(&baseline_screen,x,y,5,22+k);blit_sprite_blend(&screen,x,y,5,22+k);
 CHECK(admitted==compatible&&candidate_count==baseline_count);
 for(unsigned n=0;n<candidate_count;n++) {
  Write a=candidate_writes[n],b=baseline_writes[n];CHECK(a.offset==b.offset&&a.source==b.source&&a.value==b.value);
  Uint8 old=oracle_store[PAD+a.offset],value=(a.source&240)|(((old&15)+(a.source&15))/2);CHECK(value==a.value);oracle_store[PAD+a.offset]=value;
 }
 render_mirror_plasma_art_end(&screen);CHECK(!plasma_art_call.live);
 CHECK(calls+1==raw_calls&&bcalls+1==baseline_raw_calls&&beforehash==hash_bytes(sprite(5,22+k)->data,sprite(5,22+k)->size));
 CHECK(!memcmp(screen_store,baseline_store,sizeof(screen_store))&&!memcmp(screen_store,oracle_store,sizeof(screen_store)));
 if(admitted_art) {
  CHECK(!memcmp(hd.pixels,art_expected,hd_pixels*4)&&!memcmp(hd_owner,art_owner,hd_pixels));
  CHECK(!memcmp(cloud_owner,art_cloud,hd_pixels)&&!memcmp(green_first,art_green,hd_pixels*2));
  CHECK(!memcmp(selected,art_selected,64000));
  memcpy(wanted_rgba,art_expected,hd_pixels*4);memcpy(wanted_owner,art_owner,hd_pixels);memcpy(wanted_cloud,art_cloud,hd_pixels);memcpy(wanted_green,art_green,hd_pixels*2);memcpy(wanted_selected,art_selected,64000);art_admitted++;
 } else {
  bool restored=false;for(unsigned n=0;n<candidate_count;n++) {
   Write a=candidate_writes[n];if(!compatible&&owner_pattern!=0&&!restored&&a.offset%screen.pitch<320){oracle_restore();restored=true;}
   oracle_pixel(a.offset,a.source,a.value,compatible);
  }
  CHECK(!memcmp(hd.pixels,wanted_rgba,hd_pixels*4)&&!memcmp(hd_owner,wanted_owner,hd_pixels));
  CHECK(!memcmp(cloud_owner,wanted_cloud,hd_pixels)&&!memcmp(green_first,wanted_green,hd_pixels*2));
 }
 for(int yy=0;yy<200;yy++)CHECK(!memcmp(expected+yy*320,screen_store+PAD+yy*screen.pitch,320));
 art_draws++;
}
static void projection_tests(void)
{
 for(unsigned pal=0;pal<4;pal++) {
  set_palette(pal);
  for(unsigned n=0;n<160;n++) {Uint8 p[4]={(Uint8)(n*41),(Uint8)(n*127),(Uint8)(n*79),255};Uint16 value=slow_project(p);CHECK(plasma_art_source_value(p)==value&&reference_project(p)==value);projection_checks++;}
 }
 /* Flat ramp: all positions tie, must choose zero. */
 for(unsigned i=112;i<128;i++)rgb_palette[i]=0x777777;
 for(unsigned n=0;n<8;n++){Uint8 p[4]={(Uint8)(n*31),77,190,255};CHECK(plasma_art_source_value(p)==0);projection_checks++;}
 set_palette(0);
}
static void hard_test(void)
{
 int d=game_probe_density;display=(SDL_Surface){320,200,320,calloc(64000,1),&format};output_screen=(SDL_Surface){320*d,200*d,320*d*4,malloc(hd_pixels*4),&format};CHECK(display.pixels&&output_screen.pixels);
 for(unsigned mode=0;mode<2;mode++) {
  for(int yy=0;yy<184;yy++)for(int xx=0;xx<264;xx++) {Uint8 b=((Uint8 *)screen.pixels)[yy*screen.pitch+xx+24];((Uint8 *)display.pixels)[yy*320+xx]=mode?normal15_index(b,xx,yy,100,100):b;}
  normal15_compose(mode?MIRROR_OUTPUT_NORMAL15_NIGHT:MIRROR_OUTPUT_NORMAL15_LOW_DETAIL,100,100);
  for(int yy=0;yy<184;yy++)for(int xx=0;xx<264;xx++)for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++) {
   size_t source=(size_t)(yy*d+sy)*hd.w+(xx+24)*d+sx,dest=(size_t)(yy*d+sy)*hd.w+xx*d+sx;
   Uint8 before=((Uint8 *)screen.pixels)[yy*screen.pitch+xx+24],after=((Uint8 *)display.pixels)[yy*320+xx];
   Uint32 wanted=hd_owner[source]==1?normal15_rgba(((Uint32 *)hd.pixels)[source],before,after,!mode||normal15_branch(xx,yy,100,100)<0):reference_color(after);
   CHECK(((Uint32 *)output_screen.pixels)[dest]==wanted);hard_checks++;
  }
 }
 free(display.pixels);free(output_screen.pixels);
}
static void context_tests(void)
{
 const char *root=game_probe_assets;set_density(4);screen.pitch=320;set_palette(0);select_original(0);
 for(unsigned n=0;n<34;n++) {
  reset_scene(3);art_context();
  switch(n) {
  case 0:xmas=true;break;case 1:isNetworkGame=true;break;case 2:twoPlayerMode=true;break;case 3:twoPlayerLinked=true;break;
  case 4:galagaMode=true;break;case 5:play_demo=true;break;case 6:record_demo=true;break;case 7:onePlayerAction=true;break;
  case 8:superTyrian=true;break;case 9:superArcadeMode=1;break;case 10:timedBattleMode=true;break;
  case 11:bonusLevel=true;break;case 12:normalBonusLevelCurrent=true;break;case 13:bonusLevelCurrent=true;break;
  case 14:player[0].items.sidekick[0]=9;break;case 15:player[0].items.sidekick[1]=0;break;
  case 16:player[0].sidekick[1].style=1;break;case 17:player[0].sidekick[1].charge=1;break;
  case 18:episodeNum=2;break;case 19:lvlFileNum=10;break;case 20:initialDifficulty=1;break;
  case 21:lvlFileNum=15;initialDifficulty=4;break;
  case 22:render_mirror_plasma_art_emit(0,1088,3,1,60023);break;
  case 23:render_mirror_plasma_art_emit(0,88,2,1,60023);break;
  case 24:render_mirror_plasma_art_emit(0,88,3,2,60023);break;
  case 25:render_mirror_plasma_art_emit(0,88,3,1,60024);break;
  case 26:playerShotData[0].playerNumber=2;break;case 27:playerShotData[0].shotGr=60024;break;
  case 28:plasma_art_reset();break;case 29:game_probe_missing=true;break;case 30:game_probe_invalid=true;break;
  case 31:game_probe_scene_assets=2;break;case 32:game_probe_assets=NULL;break;
  default:render_mirror_plasma_art_emit(0,1,0,1,60023);break;
  }
  art_draw(0,100,70,false,true);game_probe_assets=root;art_guards++;
 }
}
static void missing_tests(const char *path)
{
 char name[2048],backup[2100];
 for(unsigned di=0;di<2;di++)for(unsigned k=0;k<3;k++) {
  set_density(di?8:4);screen.pitch=320;set_palette(0);select_original(0);art_context();game_probe_assets=path;
  snprintf(name,sizeof(name),"%s/option-plasma-projectile-%u-%d.hda",path,22+k,game_probe_density);snprintf(backup,sizeof(backup),"%s.hold",name);
  reset_scene(3);art_draw(k,100,70,true,true);
  CHECK(!rename(name,backup));reset_scene(3);unsigned fonts=font_effects;
  render_mirror_plasma_art_prepare(&screen,100,70,k,5,22+k);CHECK(!plasma_art_call.live&&font_effects==fonts);
  art_draw(k,100,70,false,true);CHECK(!rename(backup,name));resource_guards++;
  for(unsigned corrupt=0;corrupt<3;corrupt++) {
   FILE *f=fopen(name,"r+b");CHECK(f);long pos=corrupt==0?0:corrupt==1?8:32;CHECK(!fseek(f,pos,SEEK_SET));int old=fgetc(f);CHECK(old>=0);CHECK(!fseek(f,pos,SEEK_SET)&&fputc(old^1,f)!=EOF&&!fclose(f));
   reset_scene(3);fonts=font_effects;render_mirror_plasma_art_prepare(&screen,100,70,k,5,22+k);CHECK(!plasma_art_call.live&&font_effects==fonts);art_draw(k,100,70,false,true);
   f=fopen(name,"r+b");CHECK(f&&!fseek(f,pos,SEEK_SET)&&fputc(old,f)!=EOF&&!fclose(f));resource_guards++;
  }
  reset_scene(3);plasma_art_projection[k].value[0]^=193;art_draw(k,100,70,true,true);cache_guards++;
  reset_scene(3);plasma_art_projection[k].density=123;art_draw(k,100,70,true,true);cache_guards++;
  reset_scene(3);plasma_art_projection[k].palette[4]^=7;art_draw(k,100,70,true,true);cache_guards++;
 }
}
static void mixed_resource_tests(const char *path)
{
 for(unsigned di=0;di<2;di++)for(unsigned absent=0;absent<3;absent++) {
  char name[2048],hold[2100];set_density(di?8:4);screen.pitch=328;set_palette(0);select_original(0);art_context();game_probe_assets=path;
  snprintf(name,sizeof(name),"%s/option-plasma-projectile-%u-%d.hda",path,22+absent,game_probe_density);snprintf(hold,sizeof(hold),"%s.hold",name);
  CHECK(!rename(name,hold));reset_scene(3);
  for(unsigned repeat=0;repeat<2;repeat++)for(unsigned k=0;k<3;k++)art_draw(k,100+(int)k*3,70+(int)k*4,k!=absent,true);
  CHECK(!rename(hold,name));resource_guards++;
 }
}
static void admission_tests(const char *path)
{
 game_probe_assets=path;set_density(4);screen.pitch=320;set_palette(0);select_original(0);art_context();
 for(unsigned k=0;k<3;k++)for(unsigned edge=0;edge<2;edge++)for(unsigned coverage=0;coverage<2;coverage++) {
  reset_scene(3);select_original(0);const Original *o=&originals[0][k];Sprite *s=sprite(5,22+k);unsigned cells=s->width*s->height;
  Uint8 pixels[MAX_CELLS],mask[MAX_CELLS];memcpy(pixels,o->indices,cells);memcpy(mask,o->mask,cells);
  unsigned cell=edge?cells-s->width:0;while((mask[cell]!=0)==(coverage!=0))cell++;
  if(coverage)mask[cell]=255;else pixels[cell]^=1;
  s->size=(Uint16)encode(s->data,s->width,s->height,pixels,mask);
  unsigned font=font_effects;int y=edge?199:-(int)s->height+1;
  render_mirror_plasma_art_prepare(&screen,100,y,k,5,22+k);CHECK(!plasma_art_call.live&&font_effects==font);art_guards++;
 }
 select_original(0);
 for(unsigned k=0;k<3;k++)for(unsigned n=0;n<6;n++) {
  reset_scene(3);art_context();int x=n==0?-1:n==1?321-originals[0][k].s.width:100;
  int y=n==2?-(int)originals[0][k].s.height:n==3?200:n==4?INT_MIN:n==5?INT_MAX:70;
  unsigned font=font_effects;render_mirror_plasma_art_prepare(&screen,x,y,k,5,22+k);CHECK(!plasma_art_call.live&&font_effects==font);art_guards++;
 }
 /* Incorrect expected ledger is rejected before retained-text stripping. */
 reset_scene(3);art_context();expected[70*320+100]^=1;unsigned font=font_effects;
 render_mirror_plasma_art_prepare(&screen,100,70,0,5,22);CHECK(!plasma_art_call.live&&font_effects==font);art_guards++;
 for(unsigned n=0;n<15;n++) {
  reset_scene(3);art_context();render_mirror_plasma_art_prepare(&screen,100,70,0,5,22);CHECK(plasma_art_call.live);
  SDL_Surface save_screen=screen,save_hd=hd;Uint8 *save_owners=hd_owner,*save_cloud=cloud_owner;Uint16 *save_green=green_first;
  SDL_PixelFormat alternate=format;
  switch(n){case 0:mirror_logic_tick++;break;case 1:rgb_palette[116]^=1;break;case 2:screen.pitch=328;break;case 3:active=false;break;
   case 4:screen.w=319;break;case 5:screen.h=199;break;case 6:hd.w--;break;case 7:hd.h--;break;
   case 8:screen.format=&alternate;break;case 9:hd.format=&alternate;break;case 10:hd_owner=NULL;break;
   case 11:cloud_owner=NULL;break;case 12:green_first=NULL;break;case 13:screen.pixels=(Uint8 *)screen.pixels+1;break;
   default:canvas=NULL;break;}
  uint64_t rgba=hash_bytes(hd.pixels,hd_pixels*4);render_mirror_plasma_art_end(&screen);CHECK(!plasma_art_call.live&&rgba==hash_bytes(hd.pixels,hd_pixels*4));
  screen=save_screen;hd=save_hd;canvas=&hd;hd_owner=save_owners;cloud_owner=save_cloud;green_first=save_green;set_palette(0);art_guards++;
 }
}
static void matrix_tests(void)
{
 static const unsigned orders[6][3]={{0,1,2},{0,2,1},{1,0,2},{1,2,0},{2,0,1},{2,1,0}};
 for(unsigned di=0;di<2;di++)for(unsigned pitch=0;pitch<2;pitch++)for(unsigned own=0;own<4;own++) {
  set_density(di?8:4);screen.pitch=pitch?328:320;set_palette(0);select_original(0);art_context();
  for(unsigned k=0;k<3;k++) {
   unsigned h=originals[0][k].s.height;
   for(unsigned visible=1;visible<=h;visible++)for(unsigned edge=0;edge<2;edge++) {
    reset_scene(own);art_draw(k,100,edge?200-(int)visible:(int)visible-(int)h,true,true);all_heights++;
   }
  }
  for(unsigned order=0;order<6;order++)for(unsigned edge=0;edge<3;edge++) {
   reset_scene(own);
   for(unsigned repeat=0;repeat<2;repeat++)for(unsigned i=0;i<3;i++) {unsigned k=orders[order][i];art_draw(k,95+(int)k*3,edge==0?70+(int)k*7:edge==1?-12+(int)k*3:185+(int)k*3,true,true);ordered_draws++;}
  }
  reset_scene(own);lvlFileNum=15;initialDifficulty=DIFFICULTY_HARD;
  for(unsigned k=0;k<3;k++)render_mirror_plasma_art_emit(k,88,3,1,60023+k);
  art_draw(0,100,70,true,true);hard_test();art_context();
 }
 /* All actual heights under alternate monotone ramps, and per-channel
  * nonmonotone fallbacks. Full legacy suite retains exhaustive malformed raw. */
 for(unsigned pal=1;pal<4;pal++)for(unsigned di=0;di<2;di++)for(unsigned k=0;k<3;k++) {
  set_palette(pal);set_density(di?8:4);screen.pitch=328;art_context();unsigned h=originals[0][k].s.height;
  for(unsigned v=1;v<=h;v++){reset_scene(3);art_draw(k,100,(int)v-(int)h,true,true);all_heights++;}
 }
 for(unsigned pal=4;pal<7;pal++)for(unsigned k=0;k<3;k++) {set_palette(pal);set_density(4);screen.pitch=320;reset_scene(3);art_context();art_draw(k,100,70,false,false);}
}
int main(int argc,char **argv)
{
 CHECK(argc==5);screen.pixels=screen_store+PAD;load_original(argv[1],0);load_original(argv[2],1);game_probe_assets=argv[4];
 FILE *f=fopen(argv[3],"rb");CHECK(f);for(unsigned i=0;i<256;i++){unsigned r=fgetc(f),g=fgetc(f),b=fgetc(f);CHECK(r<64&&g<64&&b<64);game_palette[i]=(((r<<2)|(r>>4))<<16)|(((g<<2)|(g>>4))<<8)|((b<<2)|(b>>4));}CHECK(!fclose(f));
 set_density(8);size_t cap=hd_pixels;
 hd.pixels=malloc(cap*4);wanted_rgba=malloc(cap*4);hd_owner=malloc(cap);wanted_owner=malloc(cap);cloud_owner=malloc(cap);wanted_cloud=malloc(cap);
 green_first=malloc(cap*2);wanted_green=malloc(cap*2);green_under_owner=malloc(cap);wanted_selected=malloc(64000);
 art_expected=malloc(cap*4);art_owner=malloc(cap);art_cloud=malloc(cap);art_green=malloc(cap*2);art_selected=malloc(64000);
 CHECK(hd.pixels&&wanted_rgba&&hd_owner&&wanted_owner&&cloud_owner&&wanted_cloud&&green_first&&wanted_green&&green_under_owner&&wanted_selected&&art_expected&&art_owner&&art_cloud&&art_green&&art_selected);
 select_original(0);
 for(unsigned k=0;k<3;k++)for(unsigned di=0;di<2;di++) {
  char name[2048];unsigned d=di?8:4;snprintf(name,sizeof(name),"%s/option-plasma-projectile-%u-%u.hda",argv[4],22+k,d);
  f=fopen(name,"rb");CHECK(f&&!fseek(f,28,SEEK_SET));size_t n=(size_t)originals[0][k].s.width*originals[0][k].s.height*d*d;
  art_rgba[k][di]=malloc(n*4);oracle_values[k][di]=malloc(n*2);CHECK(art_rgba[k][di]&&oracle_values[k][di]&&fread(art_rgba[k][di],4,n,f)==n&&fgetc(f)==EOF&&!fclose(f));
 }
 projection_tests();context_tests();game_probe_assets=argv[4];missing_tests(argv[4]);mixed_resource_tests(argv[4]);admission_tests(argv[4]);matrix_tests();
 CHECK(contour_added>0&&contour_suppressed>0&&all_heights>2000&&ordered_draws==1728);
 printf("{\"status\":\"PASS\",\"assertions\":%u,\"draws\":%u,\"authored_draws\":%u,\"all_height_draws\":%u,\"ordered_repeated_draws\":%u,\"guard_cases\":%u,\"missing_corrupt_resources\":%u,\"poisoned_projection_caches\":%u,\"exhaustive_projection_samples\":%u,\"added_contour_subpixels\":%u,\"suppressed_original_subpixels\":%u,\"hard_output_subpixels\":%u}\n",checks,art_draws,art_admitted,all_heights,ordered_draws,art_guards,resource_guards,cache_guards,projection_checks,contour_added,contour_suppressed,hard_checks);
 return 0;
}
