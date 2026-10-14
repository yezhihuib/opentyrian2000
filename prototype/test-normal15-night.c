/* Bounded offline source unit: actual renderer and HUD modules, no game loop. */
#include <assert.h>
#include <limits.h>
#include "render-under-test.inc"
#include "tyrian2.h"
#include "nortvars.h"
#include "nortsong.h"
#include "keyboard.h"
#include "test-fixtures.inc"

bool game_probe_enabled, manual_hd_enabled;
int game_probe_density;
bool game_probe_missing,game_probe_repeat,game_probe_invalid,game_probe_coverage_fault,game_probe_skip,game_probe_local_blend,game_probe_original_reference;
bool game_probe_known_blend,game_probe_blend_capture;
unsigned game_probe_scene_assets,game_probe_tick;
const char *game_probe_assets;
Uint32 rgb_palette[256];
SDL_Surface *game_screen,*VGAScreenSeg;
Player player[2];

JE_byte episodeNum,lvlFileNum,superArcadeMode,starShowVGASpecialCode,processorType;
JE_shortint initialDifficulty;
JE_boolean twoPlayerMode,galagaMode,onePlayerAction,timedBattleMode,superTyrian,bonusLevel,normalBonusLevelCurrent,bonusLevelCurrent;
JE_boolean playerEndLevel,skipStarShowVGA,smoothScroll,quitRequested;
bool xmas,isNetworkGame,play_demo,record_demo;
uint power,lastPower;
char levelName[11];
JE_OptionType options[OPTION_NUM+1];
JE_ShieldType shields;
Sprite_array sprite_table[SPRITE_TABLES_MAX];
JE_word frameCountMax;

static unsigned recorded_present;
static char recorded_reason[128];
void game_probe_frame(unsigned a,unsigned b,unsigned c,const char *r,const char *all,unsigned d,unsigned e,unsigned f){(void)a;(void)b;(void)c;(void)all;(void)d;(void)e;(void)f;snprintf(recorded_reason,sizeof(recorded_reason),"%s",r?r:"");}
void game_probe_effects(unsigned a,unsigned b,unsigned c,unsigned d,unsigned e){(void)a;(void)b;(void)c;(void)d;(void)e;}
void game_probe_rgb_audit(SDL_Surface *s,unsigned n){(void)s;(void)n;}
bool game_probe_capture_tick(void){return false;}
void game_probe_export(SDL_Surface *s,const char *n){(void)s;(void)n;assert(!"unexpected export");}
void game_probe_fade_sample(SDL_Surface *s,int a,unsigned b,int c){(void)s;(void)a;(void)b;(void)c;}
void game_probe_present(unsigned n,uint64_t a,uint64_t b){assert(a==b);recorded_present=n;}
void ground101_frame_reset(void){}
bool asset_debug_fast_forward(void){return false;}
void asset_debug_readback(SDL_Renderer *r){(void)r;}
#include "title_layers.h"
SDL_Surface *VGAScreen;
Sprite2_array spriteSheet8;
static unsigned frame_count,negative_count,hud_cells,persistent_cells,cash_cells;
static const char *resource_override;
static uint64_t index_cases,channel_cases,rgba_cases,composed_pixels,original_loop_pixels,floor_owner0,floor_owner1,floor_owner2,nonlit_equal_owner1,nonlit_equal_changed,lit_owner1;
static MirrorOutputKind observed_kind;
static int observed_lightx,observed_lighty;
static void capture_finish(MirrorOutputKind k,int x,int y){observed_kind=k;observed_lightx=x;observed_lighty=y;render_mirror_finish(k,x,y);}
void wait_delay(void){assert(!"unexpected delay");}
void setDelay(int n){(void)n;assert(!"unexpected delay");}
void JE_showVGA(void){} /* Isolated presentation boundary; Present is tested separately. */
#define render_mirror_finish capture_finish
#include "starshow-under-test.inc"
#undef render_mirror_finish
/* These unrelated menu layers are dormant. Actual gameplay HUD/HUF checks and
 * render_mirror_pixel ledger are linked without stubs or altered constants. */
#define MENU_HOOKS(prefix,Type) \
void prefix##_pixel(SDL_Surface *s,Uint8 *p,int k){(void)s;(void)p;(void)k;} \
void prefix##_glyph_begin(SDL_Surface*s,int x,int y,unsigned t,unsigned i,enum Type k,unsigned h,int v){(void)s;(void)x;(void)y;(void)t;(void)i;(void)k;(void)h;(void)v;} \
void prefix##_glyph_end(void){}
MENU_HOOKS(settings_font,SettingsGlyph)
MENU_HOOKS(load_font,LoadGlyph)
MENU_HOOKS(selector_font,SelectorGlyph)
MENU_HOOKS(pregame_font,PregameGlyph)
void title_layers_pixel(SDL_Surface *s,Uint8 *p,enum TitleWriter w){(void)s;(void)p;(void)w;}
void game_probe_restore_region(unsigned n,SDL_Rect a,SDL_Rect b,unsigned c,unsigned d){(void)n;(void)a;(void)b;(void)c;(void)d;}
void JE_outTextAndDarken(SDL_Surface*s,int x,int y,const char*t,unsigned h,unsigned v,unsigned f){(void)s;(void)x;(void)y;(void)t;(void)h;(void)v;(void)f;assert(!"unused text path");}
void JE_outTextModify(SDL_Surface*s,int x,int y,const char*t,unsigned h,unsigned v,unsigned f){(void)s;(void)x;(void)y;(void)t;(void)h;(void)v;(void)f;assert(!"unused text path");}
#include "text-under-test.inc"

static uint64_t stamp(const void *p,size_t n){uint64_t h=14695981039346656037ULL;const Uint8*b=p;while(n--)h=(h^*b++)*1099511628211ULL;return h;}
static uint64_t canvas_stamp(void){return stamp(canvas->pixels,(size_t)canvas->pitch*canvas->h);}
static uint64_t owner_stamp(void){return stamp(hd_owner,(size_t)canvas->w*canvas->h);}
static Uint32 at(SDL_Surface*s,int x,int y){return ((Uint32*)((Uint8*)s->pixels+y*s->pitch))[x];}
static void put(SDL_Surface*s,int x,int y,Uint32 c){((Uint32*)((Uint8*)s->pixels+y*s->pitch))[x]=c;}
static void read_fixture(const char*name,void*buf,size_t n){char p[2048];snprintf(p,sizeof(p),"%s/%s",fixture_dir,name);FILE*f=fopen(p,"rb");assert(f&&fread(buf,1,n,f)==n&&fgetc(f)==EOF);fclose(f);}
static Uint16 u16(FILE*f){unsigned a=fgetc(f),b=fgetc(f);assert(a<256&&b<256);return (Uint16)(a|b<<8);}
static void load_sprites_fixture(unsigned t){char p[2048];snprintf(p,sizeof(p),"%s/sprites-%u.bin",fixture_dir,t);FILE*f=fopen(p,"rb");assert(f);sprite_table[t].count=u16(f);for(unsigned i=0;i<sprite_table[t].count;i++){int live=fgetc(f);assert(live==0||live==1);if(!live)continue;Sprite*r=&sprite_table[t].sprite[i];r->width=u16(f);r->height=u16(f);r->size=u16(f);r->data=malloc(r->size);assert(fread(r->data,1,r->size,f)==r->size);}assert(fgetc(f)==EOF);fclose(f);}
static void palette(void){Uint8 p[768];read_fixture("palette5.bin",p,sizeof(p));for(int i=0;i<256;i++)rgb_palette[i]=0xff000000u|(Uint32)p[i*3]<<16|(Uint32)p[i*3+1]<<8|p[i*3+2];}
/* Independent source-style descending-counter oracle. No production helper. */
static Uint8 index_oracle(Uint8 src,int u,int v,int lx,int ly){int64_t y=184-(int64_t)v,x=264-(int64_t)u,dist=llabs((int64_t)lx-x)+(int64_t)ly;if((int64_t)ly>y)return (src&0xf0)|((src>>2)&3);if(dist<y)return src;if(dist-y<=5)return (src&0xf0)|(((src&15)+3*(5-(dist-y)))/4);return(src&0xf0)|((src&15)>>2);}
/* Exact nonnegative rational, independently round by quotient/remainder. */
static unsigned round_ratio(unsigned n,unsigned den){unsigned q=n/den,r=n%den;return q+(r*2>=den);}
static unsigned channel_oracle(unsigned h,unsigned b,unsigned a){
 if(h==b)return a;
 unsigned distance=h<b?b-h:h-b,range=h<b?b:255-b,room=h<b?a:255-a;
 /* The minimum of the two exact nonnegative rational residuals is rounded.
  * Monotone rounding lets us compare rounded rationals independently. */
 unsigned quarter=round_ratio(distance,4),bounded=round_ratio(distance*room,range);
 unsigned residual=quarter<bounded?quarter:bounded;
 return h<b?a-residual:a+residual;
}
static int branch_oracle(int u,int v,int lx,int ly){int64_t y=184-(int64_t)v,x=264-(int64_t)u,dist=llabs((int64_t)lx-x)+(int64_t)ly;if((int64_t)ly>y)return 6;if(dist<y)return -1;return dist-y<=5?(int)(dist-y):6;}
static Uint32 rgba_oracle(Uint32 c,Uint8 b,Uint8 a,bool lit){if(lit)return c;Uint32 r=0xff000000u;for(int k=0;k<24;k+=8)r|=channel_oracle((c>>k)&255,(rgb_palette[b]>>k)&255,(rgb_palette[a]>>k)&255)<<k;return r;}
static void math_tests(void){
 for(unsigned b=0;b<256;b++)for(unsigned a=0;a<256;a++){unsigned last=0;for(unsigned h=0;h<256;h++){unsigned q=normal15_channel(h,b,a);assert(q==channel_oracle(h,b,a)&&q<=255&&q>=last);if(h==b)assert(q==a);if(h<b)assert(q<=a&&a-q<=round_ratio(b-h,4));if(h>b)assert(q>=a&&q-a<=round_ratio(h-b,4));last=q;++channel_cases;}}
 int positions[][2]={{121,72},{281,172},{1,1},{264,184},{0,0},{-1000,-1000},{1000,1000},{INT_MIN,INT_MAX},{INT_MAX,INT_MIN}};
 for(unsigned p=0;p<sizeof(positions)/sizeof(*positions);p++)for(int y=0;y<184;y++)for(int x=0;x<264;x++){Uint8 s=(Uint8)(x+17*y);assert(normal15_branch(x,y,positions[p][0],positions[p][1])==branch_oracle(x,y,positions[p][0],positions[p][1]));assert(normal15_index(s,x,y,positions[p][0],positions[p][1])==index_oracle(s,x,y,positions[p][0],positions[p][1]));++index_cases;}
 static const Uint32 swatches[]={0xff000000,0xffffffff,0xffff0000,0xff00ff00,0xff0000ff,0xff010203,0xffe92d91,0xff719cc3,0xffa58325};
 for(unsigned s=0;s<256;s++)for(int branch=-2;branch<8;branch++){int lx=264+branch,ly=184;if(branch==-2)ly=185;if(branch==-1){lx=264;ly=183;}Uint8 a=index_oracle(s,0,0,lx,ly);assert(normal15_index(s,0,0,lx,ly)==a);++index_cases;assert(normal15_rgba(palette_rgb(s),s,a,branch==-1)==palette_rgb(a));for(unsigned k=0;k<sizeof(swatches)/sizeof(*swatches);k++){assert(normal15_rgba(swatches[k],s,a,branch==-1)==rgba_oracle(swatches[k],s,a,branch==-1));++rgba_cases;}}
 assert(normal15_rgba(0xfff12347,0,0,false)!=0xfff12347);
 assert(normal15_index(0x15,0,0,264,184)==0x15&&normal15_branch(0,0,264,184)==0);
 assert(normal15_rgba(0xfff12347,0x15,0x15,false)==rgba_oracle(0xfff12347,0x15,0x15,false));
 assert(normal15_rgba(0xfff12347,0x15,0x15,false)!=0xfff12347);
 /* Nonlit transfer may raise an H below its destination anchor; this is
  * intentional residual contraction, not an invalid direction assumption. */
 assert(normal15_channel(0,200,100)==50);
 assert(palette_rgb(0)==0xff000000&&palette_rgb(3)==0xff282828);assert(normal15_rgba(0xff713254,0,3,false)==rgba_oracle(0xff713254,0,3,false));assert(normal15_rgba(0xfff12347,0,0,true)==0xfff12347);
}
static void release_surfaces(void){render_mirror_hud_shutdown();if(texture){SDL_DestroyTexture(texture);texture=NULL;}SDL_FreeSurface(canvas);SDL_FreeSurface(output);SDL_FreeSurface(fade_saved);SDL_FreeSurface(game_screen);SDL_FreeSurface(VGAScreenSeg);canvas=output=fade_saved=game_screen=VGAScreenSeg=NULL;free(hd_owner);free(cloud_owner);free(green_first);free(green_under);free(green_under_owner);hd_owner=cloud_owner=green_under_owner=NULL;green_first=NULL;green_under=NULL;}
static void setup(int d,bool hud){
 if(canvas)release_surfaces();game_probe_enabled=false;manual_hd_enabled=true;game_probe_density=d;game_probe_original_reference=game_probe_missing=game_probe_invalid=game_probe_coverage_fault=game_probe_repeat=game_probe_skip=false;
 episodeNum=1;lvlFileNum=15;initialDifficulty=DIFFICULTY_HARD;xmas=isNetworkGame=play_demo=record_demo=false;twoPlayerMode=galagaMode=onePlayerAction=timedBattleMode=superTyrian=bonusLevel=normalBonusLevelCurrent=bonusLevelCurrent=false;superArcadeMode=SA_NONE;terrain_file='z';playerEndLevel=skipStarShowVGA=smoothScroll=false;processorType=3;starShowVGASpecialCode=2;player[0].x=160;player[0].y=100;
 palette();game_probe_assets=resource_override?resource_override:hud?fixture_dir:"/nonexistent-normal15-test-resources";game_screen=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);VGAScreenSeg=SDL_CreateRGBSurfaceWithFormat(0,320,200,8,SDL_PIXELFORMAT_INDEX8);assert(game_screen&&VGAScreenSeg);VGAScreen=game_screen;read_fixture("pic3.bin",VGAScreenSeg->pixels,64000);render_mirror_hud_start(VGAScreenSeg);assert(manual_hd_lease&&!game_probe_enabled);if(hud){assert(hud_gameplay&&component_gameplay&&indicator_gameplay&&fixed_text_gameplay&&font_gameplay);}
 for(int y=0;y<200;y++)for(int x=0;x<320;x++)((Uint8*)game_screen->pixels)[y*320+x]=(Uint8)(x+17*y);
 render_mirror_begin();assert(active&&normal15_layout());
 /* Synthetic composed swatches test output ownership only, not asset loading. */
 for(int y=0;y<200*d;y++)for(int x=0;x<320*d;x++){int cell=(y/d)*320+x/d;Uint8 owner=(Uint8)((x+y)%3);hd_owner[y*canvas->w+x]=owner;Uint8 ix=((Uint8*)game_screen->pixels)[cell];Uint32 color=(x%4==0)?palette_rgb(ix):0xff000000u|((unsigned)(x*71+y*13)&255)<<16|((unsigned)(x*3+y*59)&255)<<8|((unsigned)(x*31+y*7)&255);put(canvas,x,y,owner==1?color:palette_rgb(ix));}
}
static void verify_output(MirrorOutputKind kind,bool classic){int d=game_probe_density;for(int y=0;y<200*d;y++)for(int x=0;x<320*d;x++){Uint8 a=((Uint8*)VGAScreenSeg->pixels)[(y/d)*320+x/d];Uint32 want=palette_rgb(a);if(!classic&&x<264*d&&y<184*d){int n=y*canvas->w+x+24*d;Uint8 b=((Uint8*)game_screen->pixels)[(y/d)*320+x/d+24];if(hd_owner[n]==1){want=at(canvas,x+24*d,y);if(kind==MIRROR_OUTPUT_NORMAL15_NIGHT)want=rgba_oracle(want,b,a,branch_oracle(x/d,y/d,281-player[0].x,172-player[0].y)<0);}}assert(at(output,x,y)==want);if(!classic&&kind==MIRROR_OUTPUT_NORMAL15_NIGHT&&x<264*d&&y<184*d){Uint8 b=((Uint8*)game_screen->pixels)[(y/d)*320+x/d+24];if(a==b){Uint8 owner=hd_owner[y*canvas->w+x+24*d];if(owner==0)floor_owner0++;if(owner==1){floor_owner1++;if(branch_oracle(x/d,y/d,281-player[0].x,172-player[0].y)<0)lit_owner1++;else{nonlit_equal_owner1++;nonlit_equal_changed+=want!=at(canvas,x+24*d,y);}}if(owner==2)floor_owner2++;}}++composed_pixels;}}
static void finish_case(int code,int processor,MirrorOutputKind kind){starShowVGASpecialCode=(Uint8)code;processorType=(Uint8)processor;uint64_t c=canvas_stamp(),o=owner_stamp(),s=stamp(game_screen->pixels,64000),e=stamp(expected,sizeof(expected));JE_starShowVGA();assert(observed_kind==kind);assert(canvas_stamp()==c&&owner_stamp()==o&&stamp(game_screen->pixels,64000)==s&&stamp(expected,sizeof(expected))==e);assert(!reject_reason&&last_output_valid&&last_output_scene_hd&&!active&&ready);assert(!memcmp(last_output_palette,rgb_palette,sizeof(rgb_palette)));assert(!memcmp(last_output_indices,VGAScreenSeg->pixels,64000));verify_output(kind,false);++frame_count;}
static void compose_tests(void){for(int d=4;d<=8;d+=4){setup(d,false);finish_case(2,3,MIRROR_OUTPUT_NORMAL15_NIGHT);assert(observed_lightx==121&&observed_lighty==72);setup(d,false);finish_case(2,1,MIRROR_OUTPUT_NORMAL15_LOW_DETAIL);setup(d,false);finish_case(0,3,MIRROR_OUTPUT_ORDINARY);setup(d,false);lvlFileNum=9;starShowVGASpecialCode=0;uint64_t c=canvas_stamp();JE_starShowVGA();assert(!reject_reason&&canvas_stamp()==c);for(int y=0;y<184*d;y++)for(int x=0;x<264*d;x++)assert(at(output,x,y)==at(canvas,x+24*d,y));++frame_count;}}
static void classic_owner_authority_tests(void){
 for(int d=4;d<=8;d+=4)for(int low=0;low<2;low++){
  setup(d,false);
  /* Deliberately non-palette RGB in classic/copy-owned cells must never be
   * interpreted as authored art by either supported new15 compositor. */
  for(int y=0;y<184*d;y++)for(int x=24*d;x<288*d;x++)if(hd_owner[y*canvas->w+x]!=1)put(canvas,x,y,0xffe427bd);
  finish_case(2,low?1:3,low?MIRROR_OUTPUT_NORMAL15_LOW_DETAIL:MIRROR_OUTPUT_NORMAL15_NIGHT);
 }
}
static void actual_loop_tests(void){
 int positions[][2]={{160,100},{0,0},{280,170},{17,100},{264,100},{160,0},{160,170},{-1000,-1000},{1000,1000}};
 setup(4,false);active=false;Uint8 old[64000];uint64_t src=stamp(game_screen->pixels,64000),rng=mt_state_fingerprint();
 for(unsigned p=0;p<sizeof(positions)/sizeof(*positions);p++)for(int processor=1;processor<=3;processor+=2){
  memcpy(old,VGAScreenSeg->pixels,64000);player[0].x=positions[p][0];player[0].y=positions[p][1];Player old_player[2];memcpy(old_player,player,sizeof(player));processorType=processor;starShowVGASpecialCode=2;JE_starShowVGA();
  assert(observed_kind==(processor<2?MIRROR_OUTPUT_NORMAL15_LOW_DETAIL:MIRROR_OUTPUT_NORMAL15_NIGHT));
  for(int y=0;y<200;y++)for(int x=0;x<320;x++){Uint8 want=old[y*320+x];if(y<184&&x<264){Uint8 b=((Uint8*)game_screen->pixels)[y*320+x+24];want=processor<2?b:index_oracle(b,x,y,281-player[0].x,172-player[0].y);}assert(((Uint8*)VGAScreenSeg->pixels)[y*320+x]==want);++original_loop_pixels;}
  assert(stamp(game_screen->pixels,64000)==src&&mt_state_fingerprint()==rng&&!memcmp(player,old_player,sizeof(player)));
 }
}
static void original_index_copy(MirrorOutputKind kind){for(int y=0;y<184;y++)for(int x=0;x<264;x++){Uint8 b=((Uint8*)game_screen->pixels)[y*320+x+24];((Uint8*)VGAScreenSeg->pixels)[y*320+x]=kind==MIRROR_OUTPUT_NORMAL15_NIGHT?index_oracle(b,x,y,121,72):b;}}
static void expect_rejection(const char*why,bool malformed){uint64_t c=canvas_stamp(),s=stamp(game_screen->pixels,64000);render_mirror_finish(MIRROR_OUTPUT_NORMAL15_NIGHT,121,72);assert(reject_reason&&strstr(all_rejections,why));assert(!last_output_valid&&!last_output_scene_hd&&!active);if(malformed){assert(!ready&&!have_fade_saved);}else verify_output(MIRROR_OUTPUT_NORMAL15_NIGHT,true);assert(canvas_stamp()==c&&stamp(game_screen->pixels,64000)==s);++negative_count;}
static void rejection_tests(void){
 setup(4,false);original_index_copy(MIRROR_OUTPUT_NORMAL15_NIGHT);((Uint8*)VGAScreenSeg->pixels)[183*320+263]^=1;expect_rejection("normal15-output-indices",false);
 setup(4,false);original_index_copy(MIRROR_OUTPUT_NORMAL15_NIGHT);expected[63999]^=1;expect_rejection("uncovered-pixel-writes",false);
 setup(4,false);original_index_copy(MIRROR_OUTPUT_NORMAL15_NIGHT);rgb_palette[200]^=1;expect_rejection("normal15-output-palette",false);
 setup(4,false);original_index_copy(MIRROR_OUTPUT_NORMAL15_NIGHT);initial_palette[1]^=1;expect_rejection("hd-palette-change",false);
 setup(4,false);original_index_copy(MIRROR_OUTPUT_NORMAL15_NIGHT);boundary_crossings=1;expect_rejection("local-region-boundary-crossing",false);
 setup(4,false);original_index_copy(MIRROR_OUTPUT_NORMAL15_NIGHT);restored_mask[30]=1;for(int y=0;y<4;y++)for(int x=120;x<124;x++)hd_owner[y*canvas->w+x]=0;put(canvas,120,0,0xff00ff00);expect_rejection("local-region-residue",false);
 for(int k=0;k<19;k++){setup(4,false);original_index_copy(MIRROR_OUTPUT_NORMAL15_NIGHT);switch(k){case 0:manual_hd_enabled=false;break;case 1:manual_hd_lease=false;break;case 2:episodeNum=2;break;case 3:lvlFileNum=9;break;case 4:initialDifficulty=DIFFICULTY_NORMAL;break;case 5:xmas=true;break;case 6:isNetworkGame=true;break;case 7:twoPlayerMode=true;break;case 8:galagaMode=true;break;case 9:play_demo=true;break;case 10:record_demo=true;break;case 11:onePlayerAction=true;break;case 12:superTyrian=true;break;case 13:superArcadeMode=1;break;case 14:timedBattleMode=true;break;case 15:bonusLevel=true;break;case 16:normalBonusLevelCurrent=true;break;case 17:bonusLevelCurrent=true;break;case 18:terrain_file='x';break;}expect_rejection("normal15-output-scope",false);}
 for(int k=0;k<10;k++){setup(4,false);original_index_copy(MIRROR_OUTPUT_NORMAL15_NIGHT);void*saved=NULL;SDL_PixelFormat *fmt=NULL;switch(k){case 0:game_screen->pitch=324;break;case 1:VGAScreenSeg->w=319;break;case 2:canvas->w--;break;case 3:output->pitch--;break;case 4:game_probe_density=2;break;case 5:saved=game_screen->pixels;game_screen->pixels=VGAScreenSeg->pixels;break;case 6:saved=output->pixels;output->pixels=(Uint8*)canvas->pixels+4;break;case 7:fmt=game_screen->format;game_screen->format=NULL;break;case 8:canvas->format->format=SDL_PIXELFORMAT_RGBA8888;break;case 9:saved=output->pixels;output->pixels=(Uint8*)saved+1;break;}uint64_t c=canvas_stamp();render_mirror_finish(MIRROR_OUTPUT_NORMAL15_NIGHT,121,72);assert(reject_reason&&strstr(all_rejections,"normal15-output-layout")&&!ready&&!active&&!last_output_valid&&!have_fade_saved&&canvas_stamp()==c);if(k==5)game_screen->pixels=saved;if(k==6||k==9)output->pixels=saved;if(k==7)game_screen->format=fmt;++negative_count;}
 for(int code=0;code<5;code++){setup(4,false);starShowVGASpecialCode=(Uint8)(code==0?1:code==1?3:code==2?255:2);if(code==3)playerEndLevel=true;if(code==4)skipStarShowVGA=true;JE_starShowVGA();assert(observed_kind==MIRROR_OUTPUT_UNSUPPORTED&&reject_reason&&!last_output_valid);verify_output(MIRROR_OUTPUT_ORDINARY,true);++negative_count;}
 for(int k=0;k<3;k++){setup(4,false);original_index_copy(MIRROR_OUTPUT_NORMAL15_NIGHT);assert(font_allocate());font_scenes[0].used=16;if(k==0)font_scenes[0].canvas_live=true;if(k==1)font_scenes[0].output_live=true;if(k==2)font_owner[0]=1;expect_rejection("normal15-scene-font",false);}
}
static void hud_and_cash_tests(void){for(int d=4;d<=8;d+=4){
 setup(d,true);assert(font_context==-1);render_mirror_text_level_begin(VGAScreenSeg,"TYRIAN");JE_outText(VGAScreenSeg,268,118,"TYRIAN",12,4);render_mirror_text_level_end();render_mirror_text_message_begin("Good luck...",false);render_mirror_text_message_backdrop();JE_outText(VGAScreenSeg,20,190,"Good luck...",0,4);render_mirror_text_message_end();assert(font_persistent[0].valid&&font_persistent[1].valid);
 /* Exact existing unhooked cash context: no render_mirror_text_begin. */
 Uint8 before[64000];memcpy(before,game_screen->pixels,64000);JE_textShade(game_screen,30,175,"1250",8,8,FULL_SHADE);assert(font_context==-1&&!font_scenes[0].canvas_live&&!font_scene_owned(font_scenes,font_owner));for(int y=0;y<200;y++)for(int x=0;x<320;x++)if(before[y*320+x]!=((Uint8*)game_screen->pixels)[y*320+x]){++cash_cells;assert(expected[y*320+x]==((Uint8*)game_screen->pixels)[y*320+x]);for(int sy=0;sy<d;sy++)for(int sx=0;sx<d;sx++)assert(hd_owner[(y*d+sy)*canvas->w+x*d+sx]==0);}
 uint64_t c=canvas_stamp();starShowVGASpecialCode=0;JE_starShowVGA();assert(!reject_reason&&canvas_stamp()==c&&last_output_valid);Uint32*ordinary=malloc((size_t)output->pitch*output->h);memcpy(ordinary,output->pixels,(size_t)output->pitch*output->h);for(unsigned i=0;i<64000;i++)hud_cells+=hud_output_owner[i]!=0;for(unsigned i=0;i<FONT_PERSIST_CELLS;i++)persistent_cells+=font_powner[i]!=0;assert(hud_cells>0&&persistent_cells>0&&component_output_generation&&fixed_text_output_generation&&indicator_output_generation&&font_output_generation);
 active=true;ready=false;starShowVGASpecialCode=2;JE_starShowVGA();assert(!reject_reason&&canvas_stamp()==c&&last_output_valid);for(int y=0;y<200*d;y++)for(int x=0;x<320*d;x++){if(x>=264*d||y>=184*d)assert(at(output,x,y)==ordinary[y*output->w+x]);else{Uint8 b=((Uint8*)game_screen->pixels)[(y/d)*320+x/d+24],a=((Uint8*)VGAScreenSeg->pixels)[(y/d)*320+x/d];Uint32 want=hd_owner[y*canvas->w+x+24*d]==1?rgba_oracle(at(canvas,x+24*d,y),b,a,branch_oracle(x/d,y/d,281-player[0].x,172-player[0].y)<0):palette_rgb(a);assert(at(output,x,y)==want);}}
 free(ordinary);++frame_count;
 size_t bytes=(size_t)output->pitch*output->h;Uint8*night=malloc(bytes);memcpy(night,output->pixels,bytes);Uint32 saved_palette[256];memcpy(saved_palette,rgb_palette,sizeof(saved_palette));SDL_Color black={0,0,0,255},white={255,255,255,255},target[256];for(int i=0;i<256;i++)target[i]=(SDL_Color){(rgb_palette[i]>>16)&255,(rgb_palette[i]>>8)&255,rgb_palette[i]&255,255};
 render_mirror_fade_start(NULL,&black,0,255);assert(fade_mode==1&&font_saved_generation==font_generation&&hud_saved_generation==hud_generation);assert(!memcmp(fade_saved->pixels,night,bytes));for(int i=0;i<256;i++)rgb_palette[i]=0xff000000;render_mirror_fade_step(1);for(int y=0;y<output->h;y++)for(int x=0;x<output->w;x++)assert(at(output,x,y)==0xff000000);
 render_mirror_fade_start(target,NULL,0,255);assert(fade_mode==3);memcpy(rgb_palette,saved_palette,sizeof(rgb_palette));render_mirror_fade_step(1);assert(!memcmp(output->pixels,night,bytes));
 render_mirror_fade_start(NULL,&white,0,255);assert(fade_mode==2);for(int i=0;i<256;i++)rgb_palette[i]=0xffffffff;render_mirror_fade_step(1);for(int y=0;y<output->h;y++)for(int x=0;x<output->w;x++)assert(at(output,x,y)==0xffffffff);assert(canvas_stamp()==c);free(night);
 /* Actual prepare_finish strips an in-flight scene lease and restores saved
  * lower pixels before the new guard; malformed leases fail closed. */
 setup(d,true);render_mirror_text_begin(game_screen,0,30,175,"1250",2,4);assert(font_context==0);JE_textShade(game_screen,30,175,"1250",2,4,FULL_SHADE);assert(font_scenes[0].canvas_live);original_index_copy(MIRROR_OUTPUT_NORMAL15_NIGHT);render_mirror_finish(MIRROR_OUTPUT_NORMAL15_NIGHT,121,72);assert(font_context==-1&&!font_scenes[0].canvas_live&&!font_scene_owned(font_scenes,font_owner));assert(!strstr(all_rejections,"normal15-scene-font"));++frame_count;
}}
static void lifecycle_resource_tests(void){
 /* An unexpected completed HUF scene context must reject, whereas an in-flight
  * context was restored by actual font_prepare_finish in the previous test. */
 setup(4,true);render_mirror_text_begin(game_screen,0,30,175,"1250",2,4);JE_textShade(game_screen,30,175,"1250",2,4,FULL_SHADE);render_mirror_text_end();assert(font_context==-1&&font_scenes[0].canvas_live&&font_scene_owned(font_scenes,font_owner));original_index_copy(MIRROR_OUTPUT_NORMAL15_NIGHT);expect_rejection("normal15-scene-font",false);
 setup(4,true);original_index_copy(MIRROR_OUTPUT_NORMAL15_NIGHT);render_mirror_finish(MIRROR_OUTPUT_NORMAL15_NIGHT,121,72);assert(!reject_reason&&last_output_valid);render_mirror_hud_suspend();assert(hud_suspended&&font_suspended);render_mirror_begin();assert(active&&!hud_suspended&&!font_suspended);original_index_copy(MIRROR_OUTPUT_NORMAL15_NIGHT);render_mirror_finish(MIRROR_OUTPUT_NORMAL15_NIGHT,121,72);assert(!reject_reason);render_mirror_hud_reset();assert(!manual_hd_lease&&!last_output_valid&&!have_initial_palette&&!ready&&!active&&!font_gameplay);
 /* Ordinary lease transitions, no forced replay or level-event execution. */
 for(int level=9;level<=16;level++){if(level!=9&&level!=15&&level!=16)continue;lvlFileNum=level;read_fixture("pic3.bin",VGAScreenSeg->pixels,64000);render_mirror_hud_start(VGAScreenSeg);assert(manual_hd_lease==(level!=16));}lvlFileNum=15;read_fixture("pic3.bin",VGAScreenSeg->pixels,64000);render_mirror_hud_start(VGAScreenSeg);assert(manual_hd_lease&&font_gameplay);render_mirror_begin();assert(active);original_index_copy(MIRROR_OUTPUT_NORMAL15_NIGHT);render_mirror_finish(MIRROR_OUTPUT_NORMAL15_NIGHT,121,72);assert(!reject_reason);++frame_count;
 setup(4,false);assert(!hud_gameplay&&!font_gameplay&&!component_gameplay&&!indicator_gameplay&&!fixed_text_gameplay);finish_case(2,3,MIRROR_OUTPUT_NORMAL15_NIGHT);
 for(int k=0;k<6;k++){char path[2048];snprintf(path,sizeof(path),"%s/invalid-%d",fixture_dir,k);resource_override=path;setup(4,false);bool readiness[6]={gameplay_hud_ready(),hud_components_ready(),hud_meters_ready(),hud_indicators_ready(),hud_fixed_text_ready(),hud_font_ready()};for(int j=0;j<6;j++)assert(readiness[j]==(j!=k));starShowVGASpecialCode=2;JE_starShowVGA();assert(!reject_reason&&last_output_valid);resource_override=NULL;++frame_count;}
 /* Stale original destination snapshots revoke actual HUD/HUF cached output. */
 setup(4,true);starShowVGASpecialCode=2;JE_starShowVGA();assert(last_output_valid&&hud_output_generation);((Uint8*)VGAScreenSeg->pixels)[300]^=1;SDL_Color black={0,0,0,255};render_mirror_fade_start(NULL,&black,0,255);assert(!last_output_valid&&!fade_mode&&!ready);++negative_count;
 setup(4,true);starShowVGASpecialCode=2;JE_starShowVGA();assert(last_output_valid);rgb_palette[100]^=1;ready=true;game_probe_skip=true;assert(!render_mirror_present(NULL,VGAScreenSeg,NULL));assert(!ready&&!last_output_valid);++negative_count;
}
static Uint32 fade_oracle(Uint32 old,Uint32 target,int steps){Uint32 c=0xff000000;for(int k=0;k<24;k+=8){int a=(old>>k)&255,b=(target>>k)&255;c|=(Uint32)(a+(b-a)/steps)<<k;}return c;}
static void fade_present_tests(void){for(int d=4;d<=8;d+=4){
 setup(d,false);finish_case(2,3,MIRROR_OUTPUT_NORMAL15_NIGHT);size_t bytes=(size_t)output->pitch*output->h;Uint32*night=malloc(bytes);memcpy(night,output->pixels,bytes);Uint32 saved_palette[256];memcpy(saved_palette,rgb_palette,sizeof(saved_palette));uint64_t c=canvas_stamp(),o=owner_stamp(),s=stamp(game_screen->pixels,64000),e=stamp(expected,sizeof(expected)),rng=mt_state_fingerprint();SDL_Color black={0,0,0,255},white={255,255,255,255},target[256];for(int i=0;i<256;i++)target[i]=(SDL_Color){(saved_palette[i]>>16)&255,(saved_palette[i]>>8)&255,saved_palette[i]&255,255};
 render_mirror_fade_start(NULL,&black,0,255);assert(fade_mode==1&&have_fade_saved&&last_output_valid&&!memcmp(fade_saved->pixels,night,bytes));assert(!memcmp(fade_saved_palette,saved_palette,sizeof(saved_palette)));
 for(int step=3;step>=1;step--){for(int i=0;i<256;i++)rgb_palette[i]=fade_oracle(rgb_palette[i],0,step);Uint32*prior=malloc(bytes);memcpy(prior,output->pixels,bytes);render_mirror_fade_step(step);for(int y=0;y<200*d;y++)for(int x=0;x<320*d;x++){bool hd=x<264*d&&y<184*d&&hd_owner[y*canvas->w+x+24*d];Uint32 want=hd?fade_oracle(prior[y*output->w+x],0,step):palette_rgb(((Uint8*)VGAScreenSeg->pixels)[(y/d)*320+x/d]);assert(at(output,x,y)==want);}free(prior);}
 render_mirror_fade_start(target,NULL,0,255);assert(fade_mode==3);memcpy(rgb_palette,saved_palette,sizeof(saved_palette));render_mirror_fade_step(1);assert(!memcmp(output->pixels,night,bytes));
 /* Owner2 intentionally uses legacy HD fade interpolation, despite exact
  * current-palette classic treatment at finish. Both are verified above. */
 memcpy(last_output_palette,rgb_palette,sizeof(rgb_palette));render_mirror_fade_start(NULL,&white,0,255);assert(fade_mode==2);for(int i=0;i<256;i++)rgb_palette[i]=0xffffffff;render_mirror_fade_step(1);for(int y=0;y<output->h;y++)for(int x=0;x<output->w;x++)assert(at(output,x,y)==0xffffffff);
 assert(canvas_stamp()==c&&owner_stamp()==o&&stamp(game_screen->pixels,64000)==s&&stamp(expected,sizeof(expected))==e&&mt_state_fingerprint()==rng);
 free(night);
 setup(d,false);finish_case(2,3,MIRROR_OUTPUT_NORMAL15_NIGHT);((Uint8*)VGAScreenSeg->pixels)[500]^=1;render_mirror_fade_start(NULL,&black,0,255);assert(!fade_mode&&!last_output_valid&&!ready);++negative_count;
 setup(d,false);finish_case(2,3,MIRROR_OUTPUT_NORMAL15_NIGHT);rgb_palette[5]^=1;render_mirror_fade_start(NULL,&black,0,255);assert(!fade_mode&&!last_output_valid&&!ready);++negative_count;
 setup(d,false);finish_case(2,3,MIRROR_OUTPUT_NORMAL15_NIGHT);SDL_Surface*screen=SDL_CreateRGBSurfaceWithFormat(0,320*d,200*d,32,SDL_PIXELFORMAT_ARGB8888);SDL_Renderer*r=SDL_CreateSoftwareRenderer(screen);assert(r);uint64_t output_hash=stamp(output->pixels,(size_t)output->pitch*output->h);c=canvas_stamp();o=owner_stamp();s=stamp(game_screen->pixels,64000);e=stamp(expected,sizeof(expected));rng=mt_state_fingerprint();
 for(int n=0;n<=2;n++){ready=true;game_probe_skip=n==0;game_probe_repeat=n==2;recorded_present=99;assert(render_mirror_present(r,VGAScreenSeg,NULL)&&recorded_present==(unsigned)n);assert(!render_mirror_present(r,VGAScreenSeg,NULL));assert(stamp(output->pixels,(size_t)output->pitch*output->h)==output_hash&&canvas_stamp()==c&&owner_stamp()==o&&stamp(game_screen->pixels,64000)==s&&stamp(expected,sizeof(expected))==e&&mt_state_fingerprint()==rng);}
 SDL_DestroyTexture(texture);texture=NULL;SDL_DestroyRenderer(r);SDL_FreeSurface(screen);
}}
int main(void){assert(SDL_Init(0)==0);load_sprites_fixture(TINY_FONT);load_sprites_fixture(OPTION_SHAPES);palette();math_tests();compose_tests();classic_owner_authority_tests();actual_loop_tests();rejection_tests();hud_and_cash_tests();lifecycle_resource_tests();fade_present_tests();release_surfaces();assert(floor_owner0&&floor_owner1&&floor_owner2&&nonlit_equal_owner1&&nonlit_equal_changed&&lit_owner1);printf("{\"status\":\"PASS\",\"channel_triples\":%llu,\"index_cases\":%llu,\"rgba_cases\":%llu,\"composed_subpixels\":%llu,\"accepted_frames\":%u,\"rejections\":%u,\"hud_owned_cells\":%u,\"persistent_text_cells\":%u,\"cash_local_cells\":%u,\"actual_original_loop_pixels\":%llu,\"unchanged_index_owner0_subpixels\":%llu,\"unchanged_index_owner1_subpixels\":%llu,\"unchanged_index_owner2_subpixels\":%llu,\"nonlit_equal_index_owner1\":%llu,\"nonlit_equal_index_rgb_changed\":%llu,\"geometric_lit_owner1\":%llu,\"densities\":[4,8],\"game_runs\":0}\n",(unsigned long long)channel_cases,(unsigned long long)index_cases,(unsigned long long)rgba_cases,(unsigned long long)composed_pixels,frame_count,negative_count,hud_cells,persistent_cells,cash_cells,(unsigned long long)original_loop_pixels,(unsigned long long)floor_owner0,(unsigned long long)floor_owner1,(unsigned long long)floor_owner2,(unsigned long long)nonlit_equal_owner1,(unsigned long long)nonlit_equal_changed,(unsigned long long)lit_owner1);SDL_Quit();return 0;}
