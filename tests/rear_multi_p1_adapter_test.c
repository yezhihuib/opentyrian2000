/* Independent review of actual adapter+loader+decoder+wrapper. Synthetic fixtures only.
 * draw_asset is an observer: unchanged compositor pixels are covered separately. */
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include "rear_multi_p1.h"
#include "fixture_pins.h"
typedef uint8_t Uint8;typedef uint16_t Uint16;typedef uint32_t Uint32;
typedef int16_t JE_integer;typedef int8_t JE_shortint;typedef uint16_t JE_word;typedef uint8_t JE_byte;typedef bool JE_boolean;
#define PORT_NUM 60
typedef struct {int x,y,w,h;} SDL_Rect;
typedef struct {int format,BitsPerPixel,BytesPerPixel;} SDL_PixelFormat;
typedef struct {void*pixels;SDL_PixelFormat*format;int w,h,pitch;} SDL_Surface;
typedef struct {size_t size;Uint8*data;} Sprite2_array;
enum {SDL_PIXELFORMAT_INDEX8=1,SDL_PIXELFORMAT_ARGB8888=2,DIFFICULTY_NORMAL=2,DIFFICULTY_HARD=3,SA_NONE=0,MIRROR_NORMAL=0,ENTITY_NORMAL=0,ENTITY_TILE=0};
#include "types.inc"
static JE_WeaponType weapons[800];static JE_WeaponPortType weaponPort;
static PlayerShotDataType playerShotData[82];
static int episodeNum=1,lvlFileNum=9,initialDifficulty=DIFFICULTY_NORMAL;
static int xmas,isNetworkGame,twoPlayerMode,twoPlayerLinked,galagaMode,play_demo,record_demo,onePlayerAction,superTyrian,superArcadeMode,timedBattleMode,bonusLevel,normalBonusLevelCurrent,bonusLevelCurrent;
static int game_probe_density=4;static bool active=true,suppress,game_probe_missing,game_probe_invalid,game_probe_original_reference;static unsigned game_probe_scene_assets=1;
static const char *game_probe_assets,*reject_reason;static uint64_t mirror_logic_tick=5;
static SDL_Surface *game_screen,*VGAScreen,*canvas;static Sprite2_array spriteSheet8;
static Uint8 *hd_owner,*cloud_owner,*green_under_owner;static Uint16 *green_first;static Uint32 *green_under;
#include "functions.inc"
static unsigned drawn,blits,ends,generics,probes,checks;static bool last_mirrored;
#define CHECK(x) do { ++checks; if(!(x)){fprintf(stderr,"FAIL line%d: %s\n",__LINE__,#x);exit(1);} } while(0)
static bool draw_asset(int x,int y,Asset*a,int style,const SDL_Rect*part){CHECK(x>=0&&x<=308&&y>=-13&&y<200&&a&&a->valid&&style==0&&!part);drawn++;suppress=true;return true;}
#include "rear_multi_p1_mirror.inc"
static void game_probe_draw(int bank,unsigned index,int x,int y,int style,int layout,bool mirrored){CHECK(bank==8&&rear_p1_member(index)>=0&&x>=0&&y>=-13&&style==0&&layout==0);probes++;last_mirrored=mirrored;}
static void blit_sprite2(SDL_Surface*s,int x,int y,Sprite2_array b,unsigned i){CHECK(s&&b.data&&rear_p1_member(i)>=0&&x>=0&&y>=-13);blits++;}
static void render_mirror_entity_end(void){ends++;suppress=false;}
static void draw_entity_sprite2(SDL_Surface*s,int x,int y,Sprite2_array b,unsigned i,int style,int layout){CHECK(style==0&&layout==0);generics++;game_probe_draw(8,i,x,y,style,layout,false);blit_sprite2(s,x,y,b,i);render_mirror_entity_end();}
#include "wrapper.inc"
#include "variants.inc"
static const unsigned ids[]={39,1,281,282,301,300};static const int dx[]={-10,10,-9,9,9,-9},dy[]={0,0,-2,-2,2,2};
static Uint8 bankdata[4096],originalbank[4096],recordbytes[320],pixels[64000],ownerbyte;static size_t banksize;
static Uint32 canvasstorage[320*200*8*8];
#define canvaspixel canvasstorage[0]
static Uint16 ownerword;static Uint32 ownerlong;static SDL_PixelFormat fmt={1,8,1},cfmt={2,32,4};static SDL_Surface surface={pixels,&fmt,320,200,320},csurface={&canvaspixel,&cfmt,1280,800,5120};
static char full[4096],work[2048],path[4096];
static unsigned byte(const Uint8**p){return *(*p)++;}static unsigned word(const Uint8**p){unsigned a=byte(p);return a|(byte(p)<<8);}
static void parse_record(JE_WeaponType*w,const Uint8*b){const Uint8*p=b;w->drain=word(&p);w->shotrepeat=byte(&p);w->multi=byte(&p);w->weapani=word(&p);w->max=byte(&p);w->tx=byte(&p);w->ty=byte(&p);w->aim=byte(&p);for(unsigned i=0;i<8;i++)w->attack[i]=byte(&p);for(unsigned i=0;i<8;i++)w->del[i]=byte(&p);for(unsigned i=0;i<8;i++)w->sx[i]=(int8_t)byte(&p);for(unsigned i=0;i<8;i++)w->sy[i]=(int8_t)byte(&p);for(unsigned i=0;i<8;i++)w->bx[i]=(int8_t)byte(&p);for(unsigned i=0;i<8;i++)w->by[i]=(int8_t)byte(&p);for(unsigned i=0;i<8;i++)w->sg[i]=word(&p);w->acceleration=(int8_t)byte(&p);w->accelerationx=(int8_t)byte(&p);w->circlesize=byte(&p);w->sound=byte(&p);w->trail=byte(&p);w->shipblastfilter=byte(&p);CHECK(p==b+80);}
static void defaults(int d,const char*root){
 rear_p1_shutdown();memcpy(bankdata,originalbank,banksize);spriteSheet8=(Sprite2_array){banksize,bankdata};parse_record(&weapons[254],recordbytes);parse_record(&weapons[265],recordbytes+80);parse_record(&weapons[255],recordbytes+160);parse_record(&weapons[266],recordbytes+240);
 memset(weaponPort,0,sizeof weaponPort);weaponPort[10].opnum=2;weaponPort[10].op[0][0]=254;weaponPort[10].op[1][0]=265;weaponPort[10].op[0][1]=255;weaponPort[10].op[1][1]=266;weaponPort[10].poweruse=40;
 memset(playerShotData,0,sizeof playerShotData);episodeNum=1;lvlFileNum=9;initialDifficulty=DIFFICULTY_NORMAL;xmas=isNetworkGame=twoPlayerMode=twoPlayerLinked=galagaMode=play_demo=record_demo=onePlayerAction=superTyrian=superArcadeMode=timedBattleMode=bonusLevel=normalBonusLevelCurrent=bonusLevelCurrent=0;
 active=true;suppress=false;reject_reason=NULL;game_probe_missing=game_probe_invalid=game_probe_original_reference=false;game_probe_scene_assets=1;game_probe_density=d;game_probe_assets=root;
 fmt=(SDL_PixelFormat){1,8,1};cfmt=(SDL_PixelFormat){2,32,4};surface=(SDL_Surface){pixels,&fmt,320,200,320};csurface=(SDL_Surface){&canvaspixel,&cfmt,320*d,200*d,320*d*4};game_screen=VGAScreen=&surface;canvas=&csurface;
 hd_owner=cloud_owner=green_under_owner=&ownerbyte;green_first=&ownerword;green_under=&ownerlong;mirror_logic_tick++;rear_p1_frame();
}
static void make_shot(unsigned k,unsigned slot){PlayerShotDataType*q=playerShotData+slot;memset(q,0,sizeof *q);q->shotX=100;q->shotY=100;q->shotGr=ids[k];q->shotAniMax=1;q->playerNumber=1;q->shotTrail=255;q->shotBlastFilter=208;q->shotXM=dx[k];q->shotYM=dy[k];}
/* Compile the actual allocation function and its observer-stripped baseline.
 * Only unrelated game services are inert stubs; state writes stay authentic. */
typedef unsigned uint;
#define WEAP_NUM 780
#define MAX_PWEAPON 81
static JE_byte shotAvail[MAX_PWEAPON],shotMultiPos[11],shotRepeat[11],soundQueue[8];
static unsigned power;static JE_word x,y;
static struct {int delta_x_shot_move,delta_y_shot_move;} player[2];
static struct {int ex,ey,scoreitem;} enemy[100];static JE_byte enemyAvail[100];
static unsigned game_probe_shot_begin(unsigned p,unsigned b,unsigned r,unsigned n,unsigned px,unsigned py)
{(void)p;(void)b;(void)r;(void)n;(void)px;(void)py;return 1;}
static void game_probe_shot_result(unsigned c,const char *why,unsigned n,unsigned slot)
{(void)c;(void)why;(void)n;(void)slot;}
static void game_probe_shot_emit(unsigned c,unsigned n,unsigned phase,unsigned slot)
{(void)c;(void)n;(void)phase;(void)slot;}
static void render_mirror_plasma_art_emit(unsigned slot,unsigned record,unsigned bay,unsigned playernum,unsigned raw)
{(void)slot;(void)record;(void)bay;(void)playernum;(void)raw;}
#include "create.inc"
#include "create_baseline.inc"
static unsigned test_power;
static uint64_t test_call;
static void adapter_begin(unsigned port,unsigned bay,unsigned power,unsigned mode,unsigned player,unsigned record)
{render_mirror_rear_p1_call_begin(port,bay,power,mode,player,record);test_call=render_mirror_rear_p1_create_begin(port,bay,record,player);}
#define render_mirror_rear_p1_call_begin(...) adapter_begin(__VA_ARGS__)
#define render_mirror_rear_p1_emit(...) render_mirror_rear_p1_emit(test_call,1,__VA_ARGS__)
static void emit(unsigned k,unsigned slot){unsigned r=(k<2?254:265)+test_power;make_shot(k,slot);render_mirror_rear_p1_call_begin(10,1,test_power,k<2?0:1,1,r);render_mirror_rear_p1_emit(slot,10,1,r,1,k<2?k+1:k-1,ids[k]);render_mirror_rear_p1_create_end(test_call);render_mirror_rear_p1_call_end();}
static bool head(unsigned k,unsigned slot){return render_mirror_rear_p1_head(&surface,playerShotData[slot].shotX+1,playerShotData[slot].shotY,spriteSheet8,ids[k],slot,ids[k]);}
static bool checked_head(unsigned k,unsigned slot){unsigned n=drawn;PlayerShotDataType q=playerShotData[slot];Uint8 before[64000];memcpy(before,pixels,sizeof before);bool got=head(k,slot);CHECK(drawn==n+(unsigned)got);CHECK(!memcmp(&q,&playerShotData[slot],sizeof q));CHECK(!memcmp(before,pixels,sizeof before));render_mirror_entity_end();return got;}
static void bad_restore(unsigned k,unsigned slot){CHECK(!checked_head(k,slot));CHECK(!rear_p1_state.birth[slot].qualified);}
typedef struct {
 PlayerShotDataType shots[82];JE_byte avail[81],phase[11],repeat[11],sound[8];unsigned energy;int gx,gy;
} GameState;
static void save_game(GameState *g){memcpy(g->shots,playerShotData,sizeof g->shots);memcpy(g->avail,shotAvail,sizeof g->avail);memcpy(g->phase,shotMultiPos,sizeof g->phase);memcpy(g->repeat,shotRepeat,sizeof g->repeat);memcpy(g->sound,soundQueue,sizeof g->sound);g->energy=power;g->gx=x;g->gy=y;}
static void load_game(const GameState *g){memcpy(playerShotData,g->shots,sizeof g->shots);memcpy(shotAvail,g->avail,sizeof g->avail);memcpy(shotMultiPos,g->phase,sizeof g->phase);memcpy(shotRepeat,g->repeat,sizeof g->repeat);memcpy(soundQueue,g->sound,sizeof g->sound);power=g->energy;x=g->gx;y=g->gy;}
static void same_game(const GameState *a,const GameState *b){CHECK(!memcmp(a->shots,b->shots,sizeof a->shots));CHECK(!memcmp(a->avail,b->avail,sizeof a->avail));CHECK(!memcmp(a->phase,b->phase,sizeof a->phase));CHECK(!memcmp(a->repeat,b->repeat,sizeof a->repeat));CHECK(!memcmp(a->sound,b->sound,sizeof a->sound));CHECK(a->energy==b->energy&&a->gx==b->gx&&a->gy==b->gy);}
static void allocation_defaults(unsigned free_slots,unsigned phase){memset(shotAvail,1,sizeof shotAvail);for(unsigned i=0;i<free_slots;i++)shotAvail[i]=0;memset(shotMultiPos,0,sizeof shotMultiPos);shotMultiPos[1]=phase;memset(shotRepeat,0,sizeof shotRepeat);memset(soundQueue,0,sizeof soundQueue);power=1000;x=y=0;}
static void compare_create(unsigned port,unsigned record,unsigned power_index,unsigned mode,bool grant){
 GameState initial,observed,baseline;save_game(&initial);
 if(grant)(render_mirror_rear_p1_call_begin)(port,1,power_index,mode,1,record);
 CHECK(!grant||port!=10||record==0||record>WEAP_NUM||power_index>1||rear_p1_state.pending);JE_integer a=player_shot_create(port,1,100,100,100,100,record,1);save_game(&observed);
 CHECK(!rear_p1_state.pending&&!rear_p1_state.lease&&!rear_p1_state.remaining&&!rear_p1_state.call);
 load_game(&initial);JE_integer b=baseline_shot_create(port,1,100,100,100,100,record,1);save_game(&baseline);CHECK(a==b);same_game(&observed,&baseline);load_game(&observed);
}
static void test_actual_allocations(void){
 for(unsigned power_index=0;power_index<2;power_index++)for(unsigned mode=0;mode<2;mode++)for(unsigned start=0;start<=(mode?4u:2u);start++)for(unsigned free_slots=0;free_slots<4;free_slots++){
  defaults(4,full);allocation_defaults(free_slots,start);unsigned record=(mode?265:254)+power_index,period=mode?4:2;
  compare_create(10,record,power_index,mode,true);unsigned n=free_slots<power_index+1?free_slots:power_index+1,phase=start;
  for(unsigned i=0;i<n;i++){phase=phase==period?1:phase+1;unsigned k=mode?phase+1:phase-1;CHECK(rear_p1_state.birth[i].qualified);CHECK(rear_p1_state.birth[i].phase==phase);CHECK(checked_head(k,i));}
  CHECK(shotMultiPos[1]==phase);
  /* Full/partial allocation ends clear the lease. Freeing slots continues
   * the same original cyclic phase; no forced (1,2)/(3,4) grouping. */
  memset(shotAvail,1,sizeof shotAvail);shotAvail[10]=shotAvail[11]=0;
  compare_create(10,record,power_index,mode,true);
  for(unsigned i=0;i<power_index+1;i++){phase=phase==period?1:phase+1;unsigned k=mode?phase+1:phase-1;CHECK(rear_p1_state.birth[10+i].phase==phase);CHECK(checked_head(k,10+i));}
  CHECK(shotMultiPos[1]==phase);
  /* Exact tuple through a shop/unwrapped call stays unqualified and clears
   * any previous identity on recycled slots. */
  memset(shotAvail,1,sizeof shotAvail);shotAvail[10]=shotAvail[11]=0;compare_create(10,record,power_index,mode,false);CHECK(!rear_p1_state.birth[10].qualified&&!rear_p1_state.birth[11].qualified);
 }
 for(unsigned mode=0;mode<2;mode++){
  unsigned record=mode?266:255;
  defaults(4,full);allocation_defaults(2,0);power=0;compare_create(10,record,1,mode,true);CHECK(!rear_p1_state.birth[0].qualified);
  defaults(4,full);allocation_defaults(2,0);compare_create(PORT_NUM+1,record,1,mode,true);CHECK(!rear_p1_state.birth[0].qualified);
  defaults(4,full);allocation_defaults(2,0);compare_create(10,0,1,mode,true);CHECK(!rear_p1_state.birth[0].qualified);
  defaults(4,full);allocation_defaults(2,0);compare_create(10,WEAP_NUM+1,1,mode,true);CHECK(!rear_p1_state.birth[0].qualified);
  defaults(4,full);allocation_defaults(3,0);weapons[record+1]=weapons[record];weapons[record+1].multi=3;compare_create(10,record+1,2,mode,true);for(unsigned i=0;i<3;i++)CHECK(!rear_p1_state.birth[i].qualified);
  defaults(4,full);allocation_defaults(2,0);compare_create(37,record,1,mode,true);CHECK(!rear_p1_state.birth[0].qualified&&!rear_p1_state.birth[1].qualified);
  /* Slot 80 is a real gameplay allocation but outside renderer ownership. */
  defaults(4,full);allocation_defaults(0,0);shotAvail[79]=shotAvail[80]=0;compare_create(10,record,1,mode,true);CHECK(rear_p1_state.birth[79].qualified);CHECK(!rear_p1_state.remaining);CHECK(shotAvail[80]==255&&shotMultiPos[1]==2);
  defaults(4,full);allocation_defaults(0,0);shotAvail[80]=0;compare_create(10,record,1,mode,true);for(unsigned i=0;i<80;i++)CHECK(!rear_p1_state.birth[i].qualified);CHECK(shotMultiPos[1]==1);
 }
}
static void test_rejected_allocations(void){
 for(unsigned mode=0;mode<2;mode++)for(unsigned kind=0;kind<6;kind++){
  defaults(4,full);unsigned record=mode?266:255,first=mode?2:0,second=first+1;
  (render_mirror_rear_p1_call_begin)(10,1,1,mode,1,record);uint64_t c=render_mirror_rear_p1_create_begin(10,1,record,1);
  make_shot(first,0);unsigned off=bankdata[2*(ids[first]-1)]|((unsigned)bankdata[2*(ids[first]-1)+1]<<8);
  if(kind==0)bankdata[off+1]^=1;
  if(kind==1)playerShotData[0].shotXM++;
  (render_mirror_rear_p1_emit)(c,1,kind==2?80:kind==3?UINT_MAX:0,10,1,record,1,1,kind==4?0:ids[first]);
  if(kind==0)bankdata[off+1]^=1;
  if(kind<5){CHECK(!rear_p1_state.remaining&&!rear_p1_state.lease);CHECK(!checked_head(first,0));}
  else CHECK(checked_head(first,0));
  make_shot(second,kind==5?0:1);
  (render_mirror_rear_p1_emit)(c,2,kind==5?0:1,10,1,record,1,2,ids[second]);
  CHECK(!checked_head(second,kind==5?0:1));CHECK(!rear_p1_state.remaining&&!rear_p1_state.lease);render_mirror_rear_p1_create_end(c);
 }
}
static void test_disjoint_view(void){
 void *sp=surface.pixels,*cp=csurface.pixels;int a=surface.pitch,b=csurface.pitch;
 uintptr_t base=UINT32_C(0x10000000);size_t sn=(size_t)surface.pitch*surface.h,cn=(size_t)csurface.pitch*csurface.h;
 /* Synthetic addresses are tested only by preflight, never dereferenced. */
 surface.pixels=(void *)base;csurface.pixels=(void *)base;CHECK(!rear_p1_view(&surface,101,100));
 csurface.pixels=(void *)(base+sn-4);CHECK(!rear_p1_view(&surface,101,100));
 csurface.pixels=(void *)(base-cn+4);CHECK(!rear_p1_view(&surface,101,100));
 csurface.pixels=(void *)(base+sn);CHECK(rear_p1_view(&surface,101,100));
 csurface.pixels=(void *)(base-cn);CHECK(rear_p1_view(&surface,101,100));
 surface.pixels=(void *)(UINTPTR_MAX-sn+1);csurface.pixels=(void *)base;CHECK(!rear_p1_view(&surface,101,100));
 surface.pixels=(void *)base;csurface.pixels=(void *)((UINTPTR_MAX&~(uintptr_t)3)-cn+4);CHECK(!rear_p1_view(&surface,101,100));
 surface.pitch+=4;csurface.pitch+=4;sn=(size_t)surface.pitch*surface.h;
 csurface.pixels=(void *)(base+sn);CHECK(rear_p1_view(&surface,101,100));
 csurface.pixels=(void *)(base+sn-4);CHECK(!rear_p1_view(&surface,101,100));
 surface.pixels=sp;csurface.pixels=cp;surface.pitch=a;csurface.pitch=b;CHECK(rear_p1_view(&surface,101,100));
}
static void test_views(unsigned k){
 test_disjoint_view();
#define VCHANGE(change,restore) do{emit(k,0);change;CHECK(!checked_head(k,0));restore;CHECK(checked_head(k,0));}while(0)
 VCHANGE(active=false,active=true);VCHANGE(reject_reason="test",reject_reason=NULL);VCHANGE(suppress=true,suppress=false);
 VCHANGE(surface.w=319,surface.w=320);VCHANGE(surface.h=199,surface.h=200);VCHANGE(surface.pitch=319,surface.pitch=320);VCHANGE(surface.pitch=INT_MAX,surface.pitch=320);
 VCHANGE(surface.pixels=NULL,surface.pixels=pixels);VCHANGE(surface.format=NULL,surface.format=&fmt);VCHANGE(fmt.format=2,fmt.format=1);VCHANGE(fmt.BitsPerPixel=16,fmt.BitsPerPixel=8);VCHANGE(fmt.BytesPerPixel=2,fmt.BytesPerPixel=1);
 VCHANGE(game_screen=NULL,game_screen=&surface);VCHANGE(VGAScreen=NULL,VGAScreen=&surface);VCHANGE(canvas=NULL,canvas=&csurface);VCHANGE(csurface.pixels=NULL,csurface.pixels=&canvaspixel);VCHANGE(csurface.format=NULL,csurface.format=&cfmt);
 VCHANGE(cfmt.format=1,cfmt.format=2);VCHANGE(cfmt.BitsPerPixel=24,cfmt.BitsPerPixel=32);VCHANGE(cfmt.BytesPerPixel=3,cfmt.BytesPerPixel=4);VCHANGE(csurface.w--,csurface.w++);VCHANGE(csurface.h--,csurface.h++);VCHANGE(csurface.pitch--,csurface.pitch++);VCHANGE(csurface.pitch=INT_MAX,csurface.pitch=320*game_probe_density*4);
 VCHANGE(hd_owner=NULL,hd_owner=&ownerbyte);VCHANGE(cloud_owner=NULL,cloud_owner=&ownerbyte);VCHANGE(green_under_owner=NULL,green_under_owner=&ownerbyte);VCHANGE(green_first=NULL,green_first=&ownerword);VCHANGE(green_under=NULL,green_under=&ownerlong);
 VCHANGE(csurface.pixels=(void *)((uintptr_t)&canvaspixel+1),csurface.pixels=&canvaspixel);
 VCHANGE(green_first=(Uint16 *)((uintptr_t)&ownerword+1),green_first=&ownerword);
 VCHANGE(green_under=(Uint32 *)((uintptr_t)&ownerlong+1),green_under=&ownerlong);
 VCHANGE(game_probe_density=2,game_probe_density=rear_p1_resources.density);
#undef VCHANGE
 int xs[]={0,308,-1,309,INT_MIN,INT_MAX};for(unsigned i=0;i<6;i++){emit(k,0);playerShotData[0].shotX=xs[i]>-32768&&xs[i]<32767?xs[i]-1:100;CHECK(render_mirror_rear_p1_head(&surface,xs[i],100,spriteSheet8,ids[k],0,ids[k])==(i<2));render_mirror_entity_end();}
 int ys[]={-13,0,199,-14,200,INT_MIN,INT_MAX};for(unsigned i=0;i<7;i++){emit(k,0);playerShotData[0].shotY=ys[i]>-32768&&ys[i]<32767?ys[i]:100;CHECK(render_mirror_rear_p1_head(&surface,101,ys[i],spriteSheet8,ids[k],0,ids[k])==(i<3));render_mirror_entity_end();}
 emit(k,0);CHECK(!render_mirror_rear_p1_head(NULL,101,100,spriteSheet8,ids[k],0,ids[k]));CHECK(!render_mirror_rear_p1_head(&surface,102,100,spriteSheet8,ids[k],0,ids[k]));CHECK(!render_mirror_rear_p1_head(&surface,101,101,spriteSheet8,ids[k],0,ids[k]));CHECK(checked_head(k,0));
}
int main(int argc,char**argv){
 CHECK(argc==2);snprintf(work,sizeof work,"%s",argv[1]);snprintf(full,sizeof full,"%s/full",work);snprintf(path,sizeof path,"%s/bank.bin",work);FILE*f=fopen(path,"rb");CHECK(f);banksize=fread(originalbank,1,sizeof originalbank,f);CHECK(banksize>602&&banksize<sizeof originalbank);fclose(f);snprintf(path,sizeof path,"%s/records.bin",work);f=fopen(path,"rb");CHECK(f);CHECK(fread(recordbytes,1,320,f)==320);fclose(f);
 test_actual_allocations();test_rejected_allocations();
 for(test_power=0;test_power<2;test_power++)for(int d=4;d<=8;d+=4)for(unsigned k=0;k<6;k++){
  defaults(d,full);CHECK(rear_p1_table(254)&&rear_p1_table(265)&&rear_p1_table(255)&&rear_p1_table(266));CHECK(rear_p1_source(spriteSheet8,ids[k]));emit(k,0);CHECK(checked_head(k,0));CHECK(checked_head(k,0));
  /* Exact current immutable shot; mode/power selection belongs to birth. */
  unsigned record=(k<2?254:265)+test_power;render_mirror_rear_p1_call_begin(10,1,1-test_power,k<2?0:1,1,record);make_shot(k,1);render_mirror_rear_p1_emit(1,10,1,record,1,k<2?k+1:k-1,ids[k]);render_mirror_rear_p1_call_end();CHECK(!checked_head(k,1));CHECK(checked_head(k,0));
  emit(k,2);CHECK(!checked_head(k,1));CHECK(checked_head(k,0)&&checked_head(k,2)); /* P2->P1 never promotes old P2 */
  for(unsigned repeat=0;repeat<5;repeat++){rear_p1_call_end(&rear_p1_state);CHECK(checked_head(k,0));}mirror_logic_tick++;rear_p1_frame();CHECK(checked_head(k,0)); /* skipped/repeated presentation adds no births */
  test_views(k);
  /* Every canonical record byte mutation, including invisible unused tail. */
  for(unsigned bytei=0;bytei<80;bytei++){emit(k,0);Uint8 modified[80];memcpy(modified,recordbytes+((k<2?0:80)+test_power*160),80);modified[bytei]^=1;parse_record(&weapons[record],modified);bad_restore(k,0);parse_record(&weapons[record],recordbytes+((k<2?0:80)+test_power*160));CHECK(!checked_head(k,0));}
  for(unsigned which=0;which<6;which++){emit(k,0);if(which==0)weaponPort[10].opnum++;if(which==1)weaponPort[10].op[0][0]++;if(which==2)weaponPort[10].op[1][0]++;if(which==3)weaponPort[10].poweruse++;if(which==4)weaponPort[10].op[0][1]++;if(which==5)weaponPort[10].op[1][1]++;bad_restore(k,0);weaponPort[10].opnum=2;weaponPort[10].op[0][0]=254;weaponPort[10].op[1][0]=265;weaponPort[10].op[0][1]=255;weaponPort[10].op[1][1]=266;weaponPort[10].poweruse=40;CHECK(!checked_head(k,0));}
  unsigned off=bankdata[2*(ids[k]-1)]|((unsigned)bankdata[2*(ids[k]-1)+1]<<8);
  emit(k,0);bankdata[off+1]^=1;bad_restore(k,0);bankdata[off+1]^=1;CHECK(!checked_head(k,0));emit(k,0);CHECK(checked_head(k,0));
  emit(k,0);spriteSheet8.size--;CHECK(!rear_p1_source((Sprite2_array){banksize,bankdata},ids[k]));spriteSheet8.size++;CHECK(checked_head(k,0));
  emit(k,0);spriteSheet8.size++;bad_restore(k,0);spriteSheet8.size--;CHECK(!checked_head(k,0));
  emit(k,0);Sprite2_array copy={banksize,originalbank};CHECK(!render_mirror_rear_p1_head(&surface,101,100,copy,ids[k],0,ids[k]));CHECK(!checked_head(k,0));
  emit(k,0);bankdata[2*(ids[k]-1)]=0xff;bankdata[2*(ids[k]-1)+1]=0xff;bad_restore(k,0);memcpy(bankdata,originalbank,banksize);CHECK(!checked_head(k,0));
  emit(k,0);spriteSheet8.data=NULL;bad_restore(k,0);spriteSheet8.data=bankdata;CHECK(!checked_head(k,0));
  /* Failed source before birth stays unqualified after restoring source. */
  bankdata[off+1]^=1;emit(k,0);bankdata[off+1]^=1;CHECK(!checked_head(k,0));
  /* Invalid source revokes even while an optional view condition also fails. */
  emit(k,0);active=false;bankdata[off+1]^=1;bad_restore(k,0);bankdata[off+1]^=1;active=true;CHECK(!checked_head(k,0));
  /* Warm payload/identity/pointer checks before any replacement. */
  emit(k,0);CHECK(checked_head(k,0));Asset*a=&rear_p1_resources.cache[k][d==8].asset;Asset saved=*a;
  a->rgba[0]^=1;CHECK(!checked_head(k,0));a->rgba[0]^=1;CHECK(checked_head(k,0));
  rear_p1_resources.cache[k][d==8].attempted=false;CHECK(!checked_head(k,0));rear_p1_resources.cache[k][d==8].attempted=true;CHECK(checked_head(k,0));
#define ACHECK(change) do{*a=saved;change;CHECK(!checked_head(k,0));*a=saved;CHECK(checked_head(k,0));}while(0)
  ACHECK(a->initialized=false);ACHECK(a->valid=false);ACHECK(a->bank=8);ACHECK(a->index++);ACHECK(a->w++);ACHECK(a->h++);ACHECK(a->anchor_x++);ACHECK(a->anchor_y--);ACHECK(a->density=d==8?4:8);ACHECK(a->rgba=NULL);ACHECK(a->rgba=(Uint8*)&ownerword);
#undef ACHECK
  game_probe_missing=true;CHECK(!checked_head(k,0));game_probe_missing=false;game_probe_invalid=true;CHECK(!checked_head(k,0));game_probe_invalid=false;game_probe_original_reference=true;CHECK(!checked_head(k,0));game_probe_original_reference=false;game_probe_scene_assets=2;CHECK(!checked_head(k,0));game_probe_scene_assets=1;game_probe_assets="different-root";CHECK(!checked_head(k,0));game_probe_assets=full;CHECK(checked_head(k,0));
  unsigned oldblits=blits,oldends=ends,oldprobe=probes,oldgeneric=generics;draw_player_shot_sprite2(&surface,101,100,spriteSheet8,ids[k],0,ids[k]);CHECK(blits==oldblits+1&&ends==oldends+1&&probes==oldprobe+1&&generics==oldgeneric&&last_mirrored&&!suppress);
  render_mirror_rear_p1_reset();draw_player_shot_sprite2(&surface,101,100,spriteSheet8,ids[k],0,ids[k]);CHECK(blits==oldblits+2&&ends==oldends+2&&probes==oldprobe+2&&generics==oldgeneric+1&&!last_mirrored&&!suppress);
 }
 test_power=1;
 /* Every excluded gameplay mode, cold admission and live irrevocable revoke. */
 int*flags[]={&xmas,&isNetworkGame,&twoPlayerMode,&twoPlayerLinked,&galagaMode,&play_demo,&record_demo,&onePlayerAction,&superTyrian,&superArcadeMode,&timedBattleMode,&bonusLevel,&normalBonusLevelCurrent,&bonusLevelCurrent};
 for(unsigned i=0;i<sizeof flags/sizeof *flags;i++){defaults(4,full);emit(0,0);*flags[i]=1;bad_restore(0,0);*flags[i]=0;CHECK(!checked_head(0,0));*flags[i]=1;emit(0,0);CHECK(!rear_p1_state.birth[0].qualified);*flags[i]=0;CHECK(!checked_head(0,0));emit(0,0);CHECK(checked_head(0,0));*flags[i]=1;rear_p1_frame();*flags[i]=0;CHECK(!checked_head(0,0));}
 defaults(4,full);lvlFileNum=15;initialDifficulty=DIFFICULTY_HARD;emit(0,0);CHECK(checked_head(0,0));initialDifficulty=DIFFICULTY_NORMAL;bad_restore(0,0);initialDifficulty=DIFFICULTY_HARD;CHECK(!checked_head(0,0));
 defaults(4,full);episodeNum=4;emit(0,0);CHECK(!checked_head(0,0));episodeNum=1;CHECK(!checked_head(0,0));
 for(unsigned i=0;i<sizeof variants/sizeof *variants;i++){snprintf(path,sizeof path,"%s/%s",work,variants[i].name);defaults(variants[i].density,path);emit(variants[i].member,0);CHECK(!checked_head(variants[i].member,0));CHECK(!checked_head(variants[i].member,0));}
 /* Coverage-only mutation: source index0 was covered, then becomes transparent.
  * Every decoded palette index stays identical, but coverage pin must reject. */
 defaults(4,full);emit(0,0);unsigned coff=bankdata[76]|((unsigned)bankdata[77]<<8);Uint8 original_decoded[336]={0},changed_decoded[336]={0};CHECK(decode_tile(spriteSheet8,39,original_decoded,original_decoded+168,12,0,0));
 CHECK(bankdata[coff]==0xc0&&bankdata[coff+1]==0);bankdata[coff]=0xb1;memmove(bankdata+coff+1,bankdata+coff+2,194);CHECK(decode_tile(spriteSheet8,39,changed_decoded,changed_decoded+168,12,0,0));CHECK(!memcmp(original_decoded,changed_decoded,168));CHECK(memcmp(original_decoded+168,changed_decoded+168,168));bad_restore(0,0);memcpy(bankdata,originalbank,banksize);CHECK(!checked_head(0,0));
 /* Mixed uses retain the same source IDs but never gain qualifying birth. */
 unsigned mixed[][6]={{37,1,2,0,1,254},{10,1,1,0,1,254},{10,1,0,0,2,254},{10,0,0,0,1,254},{27,1,0,0,1,445},{32,1,0,0,1,445},{19,0,0,0,1,49},{19,0,0,0,1,50},{19,0,0,0,1,51},{22,1,0,0,1,49},{22,1,0,0,1,50},{22,1,0,0,1,51},{22,1,0,0,1,500},{22,1,0,0,1,501}};
 for(unsigned m=0;m<sizeof mixed/sizeof *mixed;m++)for(unsigned k=0;k<6;k++){defaults(4,full);emit(k,0);make_shot(k,0);unsigned *v=mixed[m];render_mirror_rear_p1_call_begin(v[0],v[1],v[2],v[3],v[4],v[5]);render_mirror_rear_p1_emit(0,v[0],v[1],v[5],v[4],k<2?k+1:k-1,ids[k]);render_mirror_rear_p1_call_end();CHECK(!checked_head(k,0));}
 /* Disk changes cannot alter warm bytes; failed cold cache retries only at restart. */
 char reloadroot[4096],reloadfile[8192];snprintf(reloadroot,sizeof reloadroot,"%s/reload",work);snprintf(reloadfile,sizeof reloadfile,"%s/rear-multicannon-p1-bank8-39-4.hda",reloadroot);
 defaults(4,reloadroot);emit(0,0);CHECK(checked_head(0,0));FILE*rf=fopen(reloadfile,"r+b");CHECK(rf);CHECK(fseek(rf,28,SEEK_SET)==0);int diskbyte=fgetc(rf);CHECK(diskbyte>=0);CHECK(fseek(rf,28,SEEK_SET)==0);CHECK(fputc(diskbyte^1,rf)!=EOF);CHECK(!fclose(rf));CHECK(checked_head(0,0));
 defaults(4,reloadroot);emit(0,0);CHECK(!checked_head(0,0));rf=fopen(reloadfile,"r+b");CHECK(rf);CHECK(fseek(rf,28,SEEK_SET)==0);CHECK(fputc(diskbyte,rf)!=EOF);CHECK(!fclose(rf));CHECK(!checked_head(0,0));defaults(4,reloadroot);emit(0,0);CHECK(checked_head(0,0));
 /* Selected root/density is startup-frozen; no exact-density fallback. */
 defaults(4,NULL);game_probe_assets=full;emit(0,0);CHECK(!checked_head(0,0));rear_p1_shutdown();rear_p1_frame();emit(0,0);CHECK(checked_head(0,0));
 defaults(4,full);game_probe_density=8;csurface.w=2560;csurface.h=1600;csurface.pitch=10240;emit(0,0);CHECK(!checked_head(0,0));
 defaults(4,full);emit(0,0);make_shot(0,1);render_mirror_rear_p1_emit(1,10,1,254,1,1,39);CHECK(!checked_head(0,1));CHECK(checked_head(0,0)); /* shop tuple has no lease */
 for(unsigned slot=80;slot<84;slot++){CHECK(!render_mirror_rear_p1_head(&surface,101,100,spriteSheet8,39,slot,39));render_mirror_rear_p1_emit(slot,10,1,254,1,1,39);}CHECK(!render_mirror_rear_p1_head(&surface,101,100,spriteSheet8,39,UINT_MAX,39));
 rear_p1_shutdown();printf("Independent actual adapter/loader/wrapper PASS: %u checks, %zu malformed resource variants\n",checks,sizeof variants/sizeof *variants);return 0;
}
