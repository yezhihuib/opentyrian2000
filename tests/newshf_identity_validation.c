/* SPDX-License-Identifier: GPL-2.0-or-later
 * Actual identity include + production structs/decode; NOT a whole-game test.
 * Private originals arrive only on stdin and are never written to an artifact. */
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <stddef.h>
#include <stdlib.h>
typedef uint8_t Uint8;
typedef uint8_t JE_byte;
typedef int8_t JE_shortint;
typedef int16_t JE_integer;
typedef uint16_t JE_word;
typedef bool JE_boolean;
typedef struct {size_t size;Uint8 *data;} Sprite2_array;
typedef struct {unsigned format;int BitsPerPixel,BytesPerPixel;} SDL_PixelFormat;
typedef struct {int w,h,pitch;void *pixels;SDL_PixelFormat *format;} SDL_Surface;
#define SDL_PIXELFORMAT_INDEX8 1
#define ENEMY_NUM 1850
#define COUNTOF(a) (sizeof(a)/sizeof((a)[0]))
#include "newshf_identity_types.h"
static JE_EnemyDatType enemyDat;
static JE_MultiEnemyType enemy;
static Uint8 enemyAvail[100];
static Sprite2_array enemySpriteSheets[4];
static Uint8 enemySpriteSheetIds[4];
static JE_word tempMapXOfs;
static uint32_t rgb_palette[256],original_palette[256];
static Uint8 pixels[64000];
static SDL_PixelFormat format={SDL_PIXELFORMAT_INDEX8,8,1};
static SDL_Surface screen={320,200,320,pixels,&format};
static SDL_Surface *game_screen=&screen,*VGAScreen=&screen;
static uint64_t global_bytes_hash(const Uint8 *b,size_t n)
{uint64_t h=UINT64_C(0xcbf29ce484222325);for(size_t i=0;i<n;i++){h^=b[i];h*=UINT64_C(0x100000001b3);}return h;}
#include "decode.inc"
#include "newshf_identity_validation.inc"
typedef unsigned uint;
typedef uint16_t Uint16;
typedef int16_t Sint16;
#include "difficulty.inc"
enum {SA_NONE=0};
static int superArcadeMode,difficultyLevel=DIFFICULTY_NORMAL,totalEnemy;
static Sprite2_array spriteSheet10,spriteSheet11;
static uint32_t rng_state=123;static unsigned rng_calls;
static unsigned mt_rand(void){rng_calls++;rng_state=rng_state*1664525u+1013904223u;return rng_state;}
#define render_mirror_cash25_enemy_allocated(...) ((void)0)
#define render_mirror_rotor_enemy_allocated(...) ((void)0)
#define render_mirror_cash25_enemy_initialized(...) ((void)0)
#define render_mirror_rotor_enemy_initialized(...) ((void)0)
#include "make_enemy.inc"
static unsigned checks;
#define CHECK(x) do {if(!(x)){fprintf(stderr,"CHECK failed %s:%d: %s\n",__FILE__,__LINE__,#x);abort();}checks++;} while(0)
/* Every observer invocation must leave indexed pixels and all actors unchanged. */
#define OBS(call) do {JE_MultiEnemyType saved;Uint8 px[64000];memcpy(saved,enemy,sizeof(enemy));memcpy(px,pixels,sizeof(px));call;CHECK(!memcmp(saved,enemy,sizeof(enemy)));CHECK(!memcmp(px,pixels,sizeof(px)));} while(0)
static Uint8 originals[3][77];
static unsigned current_record=163;
static Uint8 *bankbytes,*bankcopy;
static void record_load(const Uint8 *b)
{
 size_t n=0;
#define RBYTE(v) do {(v)=b[n++];} while(0)
#define RWORD(v) do {(v)=(unsigned)b[n]|((unsigned)b[n+1]<<8);n+=2;} while(0)
 RBYTE(enemyDat[current_record].ani);
 for(unsigned i=0;i<3;i++)RBYTE(enemyDat[current_record].tur[i]);
 for(unsigned i=0;i<3;i++)RBYTE(enemyDat[current_record].freq[i]);
 RBYTE(enemyDat[current_record].xmove);RBYTE(enemyDat[current_record].ymove);RBYTE(enemyDat[current_record].xaccel);RBYTE(enemyDat[current_record].yaccel);
 RBYTE(enemyDat[current_record].xcaccel);RBYTE(enemyDat[current_record].ycaccel);RWORD(enemyDat[current_record].startx);RWORD(enemyDat[current_record].starty);
 RBYTE(enemyDat[current_record].startxc);RBYTE(enemyDat[current_record].startyc);RBYTE(enemyDat[current_record].armor);RBYTE(enemyDat[current_record].esize);
 for(unsigned i=0;i<20;i++)RWORD(enemyDat[current_record].egraphic[i]);
 RBYTE(enemyDat[current_record].explosiontype);RBYTE(enemyDat[current_record].animate);RBYTE(enemyDat[current_record].shapebank);
 RBYTE(enemyDat[current_record].xrev);RBYTE(enemyDat[current_record].yrev);RWORD(enemyDat[current_record].dgr);RBYTE(enemyDat[current_record].dlevel);
 RBYTE(enemyDat[current_record].dani);RBYTE(enemyDat[current_record].elaunchfreq);RWORD(enemyDat[current_record].elaunchtype);
 RWORD(enemyDat[current_record].value);RWORD(enemyDat[current_record].eenemydie);
#undef RBYTE
#undef RWORD
 CHECK(n==77);
}

static G101EnemyContext context(unsigned s)
{return (G101EnemyContext){enemy[s].enemytype,s,enemyAvail[s],enemy[s].size,enemy[s].scoreitem,enemy[s].edamaged,true,true};}
static void restore(void)
{
 OBS(render_mirror_newshf_validation_reset());
 memset(enemy,0,sizeof(enemy));memset(enemyAvail,1,sizeof(enemyAvail));
 memset(enemySpriteSheetIds,0,sizeof(enemySpriteSheetIds));memset(enemySpriteSheets,0,sizeof(enemySpriteSheets));
 enemySpriteSheetIds[0]=10;enemySpriteSheets[0]=(Sprite2_array){NEWSHF_PROTOTYPE_BANK_BYTES,bankbytes};
 memcpy(bankbytes,bankcopy,NEWSHF_PROTOTYPE_BANK_BYTES);memcpy(rgb_palette,original_palette,sizeof(rgb_palette));
 for(unsigned p=0;p<3;p++){current_record=newshf_prototype_record_ids[p];record_load(originals[p]);}
 current_record=163;tempMapXOfs=0;screen=(SDL_Surface){320,200,320,pixels,&format};format=(SDL_PixelFormat){1,8,1};game_screen=VGAScreen=&screen;
}
static void fields(unsigned s)
{
 struct JE_SingleEnemyType *e=enemy+s;memset(e,0,sizeof(*e));
 e->enemytype=current_record;e->enemydatofs=&enemyDat[current_record];e->sprite2s=&enemySpriteSheets[0];e->size=1;
 e->ani=1;e->animin=1;e->enemycycle=1;e->evalue=enemyDat[current_record].value;
 e->edani=enemyDat[current_record].dani;e->edgr=enemyDat[current_record].dgr;e->edlevel=enemyDat[current_record].dlevel;
 memcpy(e->egr,enemyDat[current_record].egraphic,sizeof(e->egr));e->ex=100;e->ey=100;
}
static void birth(unsigned s)
{
 enemyAvail[s]=1;memset(enemy+s,0,sizeof(enemy[s]));
 unsigned avail=JE_makeEnemy(enemy+s,current_record,0);enemyAvail[s]=avail;CHECK(avail==0);CHECK(newshf_validation_slots[s].role);
 enemy[s].ex=100;enemy[s].ey=100;
}
static void observe(unsigned s,unsigned pose)
{OBS(render_mirror_newshf_validation_frame());enemy[s].enemycycle=pose;OBS(render_mirror_newshf_validation_observe(s));}
static bool tile_args(unsigned s,SDL_Surface *surface,int x,int y,Sprite2_array b,unsigned base,int q,int filter,G101EnemyContext *c)
{
 (void)s;bool good;OBS(good=render_mirror_newshf_validation_tile(surface,x,y,b,base,q,filter,c));return good;
}
static bool part(unsigned s,unsigned q)
{
 static const int parts[]={0,1,19,20};G101EnemyContext c=context(s);struct JE_SingleEnemyType *e=enemy+s;
 return tile_args(s,&screen,e->ex+tempMapXOfs+(q&1?6:-6),e->ey+(q>=2?7:-7),enemySpriteSheets[0],e->egr[e->enemycycle-1],parts[q],e->filter,&c);
}
static void full(unsigned s)
{for(unsigned q=0;q<4;q++)CHECK(part(s,q));CHECK(!newshf_validation_slots[s].remaining);}
static void good_cases(void)
{
 for(unsigned p=0;p<3;p++){
  restore();current_record=newshf_prototype_record_ids[p];birth(0);
  const unsigned poses[]={1,3,2,2,1,1,3};
  for(unsigned j=0;j<COUNTOF(poses);j++){enemy[0].filter=j*37;observe(0,poses[j]);full(0);}
  for(int y=-30;y<=205;y++){
   birth(0);enemy[0].ey=y;observe(0,1);
   if(y>-13){CHECK(part(0,0));CHECK(part(0,1));}
   if(y>-26&&y<182){CHECK(part(0,2));CHECK(part(0,3));}
   CHECK(!newshf_validation_slots[0].remaining);
  }
  /* Physical horizontal row wrapping is not an HD clipping guarantee. The
   * observer only proves original coordinates and does not reinterpret them. */
  for(int x=-28;x<300;x+=17){birth(0);enemy[0].ex=x;observe(0,1);full(0);}
 }
 restore();birth(0);current_record=167;birth(1);current_record=168;birth(2);
 OBS(render_mirror_newshf_validation_frame());for(unsigned s=0;s<3;s++){OBS(render_mirror_newshf_validation_observe(s));full(s);}
}
static void make_enemy_equivalence(void)
{
 for(unsigned p=0;p<3;p++)for(int difficulty=-1;difficulty<=DIFFICULTY_10;difficulty++)for(unsigned mode=0;mode<5;mode++){
  restore();unsigned record=newshf_prototype_record_ids[p];difficultyLevel=difficulty;
  int unique=mode==0?0:mode==1?10:mode==2?26:mode==3?21:13;
  /* Both versions start with identical previous occupant bytes and RNG. */
  struct JE_SingleEnemyType before={0},expected;before.sprite2s=&enemySpriteSheets[0];before.ex=17;before.ey=-5;
  enemy[0]=before;rng_state=123;rng_calls=0;totalEnemy=0;
  unsigned want=baseline_makeEnemy(enemy,record,unique);expected=enemy[0];unsigned calls=rng_calls;uint32_t state=rng_state;int total=totalEnemy;
  enemy[0]=before;rng_state=123;rng_calls=0;totalEnemy=0;
  Uint8 px[sizeof(pixels)];memcpy(px,pixels,sizeof(px));
  unsigned got=JE_makeEnemy(enemy,record,unique);
  CHECK(got==want);CHECK(!memcmp(&expected,enemy,sizeof(expected)));CHECK(rng_calls==calls&&rng_state==state);CHECK(totalEnemy==total);CHECK(!memcmp(px,pixels,sizeof(px)));
  CHECK(newshf_validation_slots[0].role==(unique==0||unique==10));
 }
 /* Actual missing bank preserves stale native pointer, but gains no role. */
 restore();enemy[0].sprite2s=&enemySpriteSheets[0];enemySpriteSheetIds[0]=0;
 CHECK(JE_makeEnemy(enemy,163,0)==0);CHECK(enemy[0].sprite2s==&enemySpriteSheets[0]);CHECK(!newshf_validation_slots[0].role);
 difficultyLevel=DIFFICULTY_NORMAL;
}
static void failure_cases(void)
{
 restore();fields(0);enemyAvail[0]=0;OBS(render_mirror_newshf_validation_observe(0));CHECK(!part(0,0));
 restore();fields(0);OBS(render_mirror_newshf_validation_initialized(enemy,163,0));CHECK(!newshf_validation_slots[0].role);
 restore();enemyAvail[0]=1;OBS(render_mirror_newshf_validation_allocated(enemy,163,0));fields(0);OBS(render_mirror_newshf_validation_frame());OBS(render_mirror_newshf_validation_initialized(enemy,163,0));CHECK(!newshf_validation_slots[0].role);
 for(unsigned unique=1;unique<=26;unique++)if(unique!=10){restore();OBS(render_mirror_newshf_validation_allocated(enemy,163,unique));CHECK(!newshf_validation_slots[0].pending);}
 restore();birth(0);observe(0,1);CHECK(!part(0,1));CHECK(!part(0,0));
 restore();birth(0);observe(0,1);CHECK(part(0,0));CHECK(!part(0,0));
 restore();birth(0);observe(0,1);CHECK(part(0,0));OBS(render_mirror_newshf_validation_frame());CHECK(!newshf_validation_slots[0].role);CHECK(!part(0,1));
 restore();birth(0);observe(0,1);OBS(render_mirror_newshf_validation_observe(0));CHECK(!newshf_validation_slots[0].role);
 restore();birth(0);enemyAvail[0]=1;OBS(render_mirror_newshf_validation_allocated(enemy,824,0));CHECK(!newshf_validation_slots[0].role);
 restore();birth(0);OBS(render_mirror_newshf_validation_reset());CHECK(!newshf_validation_slots[0].role);observe(0,1);CHECK(!part(0,0));
 restore();birth(0);uint64_t epoch=newshf_validation_bank_epoch;OBS(render_mirror_newshf_validation_bank_changed(&enemySpriteSheets[0]));CHECK(newshf_validation_bank_epoch!=epoch);CHECK(!newshf_validation_slots[0].role);observe(0,1);CHECK(!part(0,0));
 restore();birth(0);Sprite2_array unrelated={0};epoch=newshf_validation_bank_epoch;OBS(render_mirror_newshf_validation_bank_changed(&unrelated));CHECK(newshf_validation_bank_epoch==epoch);observe(0,1);full(0);
 /* All 77 record bytes, for each family member, revoke the whole family. */
 for(unsigned p=0;p<3;p++)for(unsigned b=0;b<77;b++){
  restore();birth(0);current_record=newshf_prototype_record_ids[p];Uint8 altered[77];memcpy(altered,originals[p],77);altered[b]^=1;record_load(altered);
  CHECK(!newshf_validation_records());OBS(render_mirror_newshf_validation_frame());record_load(originals[p]);CHECK(!newshf_validation_slots[0].role);
 }
 fprintf(stderr,"NEGATIVE-CONTROL bank-byte mutation assertions begin\n");
 for(unsigned b=0;b<NEWSHF_PROTOTYPE_BANK_BYTES;b+=997){restore();birth(0);bankbytes[b]^=1;observe(0,1);CHECK(!newshf_validation_slots[0].role);bankbytes[b]^=1;CHECK(!part(0,0));}
 for(unsigned c=0;c<256;c++){restore();birth(0);rgb_palette[c]^=1;observe(0,1);CHECK(!newshf_validation_slots[0].role);rgb_palette[c]^=1;CHECK(!part(0,0));}
 /* Stale inherited binding, duplicate IDs, byte-identical wrong object/data. */
 restore();birth(0);enemySpriteSheetIds[0]=0;observe(0,1);CHECK(!newshf_validation_slots[0].role);
 restore();birth(0);enemySpriteSheetIds[1]=10;enemySpriteSheets[1]=enemySpriteSheets[0];observe(0,1);CHECK(!newshf_validation_slots[0].role);
 restore();birth(0);enemySpriteSheetIds[0]=0;enemySpriteSheetIds[1]=10;enemySpriteSheets[1]=enemySpriteSheets[0];enemy[0].sprite2s=&enemySpriteSheets[1];observe(0,1);CHECK(!newshf_validation_slots[0].role);
 restore();birth(0);Sprite2_array static10=enemySpriteSheets[0];enemy[0].sprite2s=&static10;observe(0,1);CHECK(!newshf_validation_slots[0].role);
 restore();birth(0);enemySpriteSheets[0].data=bankcopy;observe(0,1);CHECK(!newshf_validation_slots[0].role);
 restore();birth(0);enemySpriteSheets[0].size--;observe(0,1);CHECK(!newshf_validation_slots[0].role);
 restore();birth(0);enemySpriteSheetIds[0]=0;enemyAvail[0]=1;OBS(render_mirror_newshf_validation_allocated(enemy,163,0));fields(0);OBS(render_mirror_newshf_validation_initialized(enemy,163,0));CHECK(!newshf_validation_slots[0].role);
 /* Between allocation and initialization: reload even to identical address. */
 restore();OBS(render_mirror_newshf_validation_allocated(enemy,163,0));fields(0);OBS(render_mirror_newshf_validation_bank_changed(&enemySpriteSheets[0]));OBS(render_mirror_newshf_validation_initialized(enemy,163,0));CHECK(!newshf_validation_slots[0].role);
 for(unsigned mode=0;mode<16;mode++){
  restore();birth(0);observe(0,1);G101EnemyContext c=context(0);int x=94,y=93,q=0,filter=0;unsigned base=125;SDL_Surface *surface=&screen;Sprite2_array b=enemySpriteSheets[0];
  switch(mode){case 0:x++;break;case 1:y++;break;case 2:q=2;break;case 3:filter=256;break;case 4:filter=-1;break;case 5:base=123;break;case 6:c.pool_slot=100;break;case 7:c.type=167;break;case 8:c.size=0;break;case 9:c.availability=2;break;case 10:c.score_item=true;break;case 11:c.damaged=true;break;case 12:surface=NULL;break;case 13:b.data=bankcopy;break;case 14:screen.pitch=321;break;case 15:format.BitsPerPixel=32;break;}
  CHECK(!tile_args(0,surface,x,y,b,base,q,filter,&c));CHECK(!newshf_validation_slots[0].role);
 }
 for(unsigned mode=0;mode<13;mode++){
  restore();birth(0);observe(0,1);
  switch(mode){case 0:enemy[0].ex++;break;case 1:enemy[0].ey++;break;case 2:enemy[0].filter++;break;case 3:enemy[0].evalue++;break;case 4:enemy[0].edamaged=true;break;case 5:enemy[0].ani=3;break;case 6:enemy[0].aniactive=1;break;case 7:enemy[0].enemycycle=2;break;case 8:enemy[0].enemydatofs=&enemyDat[167];break;case 9:enemy[0].egr[19]++;break;case 10:enemyAvail[0]=1;break;case 11:enemy[0].edgr++;break;case 12:newshf_validation_slots[0].witnessed++;break;}
  CHECK(!part(0,0));CHECK(!newshf_validation_slots[0].role);
 }
 for(unsigned j=0;j<2;j++){restore();birth(0);enemy[0].ex=j?300:-29;observe(0,1);CHECK(!newshf_validation_slots[0].role);}
 restore();birth(0);observe(0,1);G101EnemyContext unrelated_context=context(0);unrelated_context.type=824;
 CHECK(!tile_args(0,&screen,94,93,enemySpriteSheets[0],125,0,0,&unrelated_context));CHECK(newshf_validation_slots[0].role);full(0);
 for(unsigned pose=0;pose<=4;pose+=4){restore();birth(0);observe(0,pose);CHECK(!newshf_validation_slots[0].role);}
 restore();birth(0);current_record=167;birth(1);observe(0,1);CHECK(part(0,0));enemy[0].filter=1;CHECK(!part(0,1));CHECK(!newshf_validation_slots[1].role);
 restore();birth(0);current_record=167;birth(1);enemyAvail[0]=1;observe(1,1);CHECK(newshf_validation_slots[1].role);full(1);CHECK(!newshf_validation_slots[0].role);
 restore();birth(0);fields(1);enemyAvail[1]=0;OBS(render_mirror_newshf_validation_observe(1));CHECK(!part(1,0));observe(0,1);full(0);
 restore();birth(0);OBS(render_mirror_newshf_validation_allocated((char*)enemy+1,163,0));CHECK(newshf_validation_slots[0].role);
 OBS(render_mirror_newshf_validation_observe(100));
}
int main(void)
{
 bankbytes=malloc(NEWSHF_PROTOTYPE_BANK_BYTES);bankcopy=malloc(NEWSHF_PROTOTYPE_BANK_BYTES);CHECK(bankbytes&&bankcopy);
 CHECK(fread(bankcopy,1,NEWSHF_PROTOTYPE_BANK_BYTES,stdin)==NEWSHF_PROTOTYPE_BANK_BYTES);
 CHECK(fread(originals,1,sizeof(originals),stdin)==sizeof(originals));
 uint32_t palette[256];CHECK(fread(palette,1,sizeof(palette),stdin)==sizeof(palette));memcpy(original_palette,palette,sizeof(palette));CHECK(fgetc(stdin)==EOF);
 for(unsigned i=0;i<sizeof(pixels);i++)pixels[i]=(Uint8)(i*71u+3u);
 good_cases();make_enemy_equivalence();failure_cases();
 printf("PASS NEWSHF identity-only production include: %u assertions; 9 poses; no actor/indexed-pixel mutations; not whole-game/HD acceptance\n",checks);
 free(bankbytes);free(bankcopy);return 0;
}
