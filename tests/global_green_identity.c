/* SPDX-License-Identifier: GPL-2.0-or-later
 * Isolated observer tests; not an integrated gameplay or rendering proof. */
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <stddef.h>
typedef uint8_t Uint8;typedef uint8_t JE_byte;typedef int8_t JE_shortint;
typedef int16_t JE_integer;typedef uint16_t JE_word;typedef bool JE_boolean;
#define COUNTOF(x) (sizeof(x)/sizeof(*(x)))
#define MAX_PWEAPON 81
#define PORT_NUM 42
#define WEAP_NUM 1818
enum {MIRROR_NORMAL,MIRROR_BLEND,MIRROR_SHADOW};
#include "green_identity_types.h"
static JE_WeaponType weapons[WEAP_NUM+1];
static PlayerShotDataType playerShotData[MAX_PWEAPON+1];
static Uint8 shotAvail[MAX_PWEAPON];
static char global_asset_directory[20]="global";
static bool game_probe_original_reference,game_probe_missing,game_probe_invalid;
static bool background2;static int shadowYDist=10;
static uint64_t mirror_logic_tick;
static uint64_t global_bytes_hash(const void *v,size_t n)
{const Uint8 *b=v;uint64_t h=UINT64_C(0xcbf29ce484222325);for(size_t i=0;i<n;i++){h^=b[i];h*=UINT64_C(0x100000001b3);}return h;}
#include "../src/global_green_identity.inc"
static unsigned checks,cases;
#define CHECK(x) do {++checks;if(!(x)){fprintf(stderr,"FAIL line%d: %s\n",__LINE__,#x);assert(x);}} while(0)
static Uint8 originals[2][80];
static unsigned record=71,phase=1,pnum=1;
static void load_record(unsigned id,const Uint8 *b)
{
 JE_WeaponType *w=weapons+id;size_t n=0;
#define RB(v) do {(v)=b[n++];} while(0)
#define RW(v) do {(v)=b[n]|((unsigned)b[n+1]<<8);n+=2;} while(0)
 RW(w->drain);RB(w->shotrepeat);RB(w->multi);RW(w->weapani);RB(w->max);RB(w->tx);RB(w->ty);RB(w->aim);
 for(unsigned i=0;i<8;i++)RB(w->attack[i]);for(unsigned i=0;i<8;i++)RB(w->del[i]);
 for(unsigned i=0;i<8;i++)RB(w->sx[i]);for(unsigned i=0;i<8;i++)RB(w->sy[i]);
 for(unsigned i=0;i<8;i++)RB(w->bx[i]);for(unsigned i=0;i<8;i++)RB(w->by[i]);for(unsigned i=0;i<8;i++)RW(w->sg[i]);
 RB(w->acceleration);RB(w->accelerationx);RB(w->circlesize);RB(w->sound);RB(w->trail);RB(w->shipblastfilter);
#undef RB
#undef RW
 CHECK(n==80);
}
static void native_init(unsigned slot)
{
 PlayerShotDataType *s=playerShotData+slot;JE_WeaponType *w=weapons+record;unsigned k=phase-1;memset(s,0,sizeof(*s));
 s->shotX=100+w->bx[k];s->shotY=100+w->by[k];s->shotXM=w->sx[k];s->shotYM=-w->sy[k];s->shotXC=w->accelerationx;s->shotYC=-w->acceleration;
 s->playerNumber=pnum;s->shotGr=w->sg[k];s->shotAniMax=w->weapani+1;s->shotTrail=w->trail;s->shotDmg=w->attack[k];s->shotBlastFilter=w->shipblastfilter;
 shotAvail[slot]=w->del[k];
}
static void birth(unsigned slot)
{
 ++cases;shotAvail[slot]=0;uint64_t token=render_mirror_green_create_begin(0,0,record,pnum,100,100,90,90);
 CHECK(token);render_mirror_green_shot_allocated(slot);native_init(slot);
 render_mirror_green_shot_initialized(token,slot,0,0,record,pnum,phase);render_mirror_green_create_end(token);CHECK(global_green_shots[slot].role);
}
static unsigned move(unsigned slot)
{
 ++mirror_logic_tick;global_green_identity_frame_begin();PlayerShotDataType *s=playerShotData+slot;
 --shotAvail[slot];s->shotXM+=s->shotXC;s->shotX+=s->shotXM;s->shotYM+=s->shotYC;s->shotY+=s->shotYM;
 render_mirror_green_trail_begin(slot);CHECK(global_green_shots[slot].step);CHECK(global_green_trail.live);
 CHECK(global_green_trail_identity(s->shotX,s->shotY,0,12,false,false)==global_green_shots[slot].on);render_mirror_green_trail_end();
 unsigned raw=s->shotGr+s->shotAni;if(++s->shotAni==s->shotAniMax)s->shotAni=0;return raw;
}
static int head(unsigned slot,unsigned raw,int style)
{PlayerShotDataType *s=playerShotData+slot;return global_green_head_identity(slot,raw,raw,s->shotX+1,s->shotY+(style==MIRROR_SHADOW?shadowYDist:0),style);}
static void full_lifetimes(void)
{
 for(unsigned r=0;r<2;r++){record=global_green_weapon_ids[r];for(pnum=1;pnum<=2;pnum++)for(phase=1;phase<=8;phase++)for(int shadows=0;shadows<2;shadows++){
  global_green_identity_reset();background2=shadows;birth(0);
  for(unsigned tick=0;tick<8;tick++){unsigned raw=move(0);CHECK(raw==214+tick%4);if(shadows)CHECK(head(0,raw,MIRROR_SHADOW)==1);CHECK(head(0,raw,MIRROR_NORMAL)==1);CHECK(global_green_identity_records_match());CHECK(!global_green_identity_fault);}
  CHECK(shotAvail[0]==0);CHECK(global_green_shots[0].ttl==0);
 }}
}
static void negative_cases(void)
{
 record=71;phase=1;pnum=1;background2=true;
 /* Every serialized record byte matters before and after a genuine birth. */
 for(unsigned i=0;i<80;i++){
  Uint8 b[80];memcpy(b,originals[0],80);b[i]^=1;
  birth(0);load_record(record,b);CHECK(!global_green_record_valid(record));CHECK(!global_green_identity_records_match());
  ++mirror_logic_tick;--shotAvail[0];playerShotData[0].shotX+=playerShotData[0].shotXM;playerShotData[0].shotY+=playerShotData[0].shotYM;
  render_mirror_green_trail_begin(0);CHECK(!global_green_shots[0].role);CHECK(!global_green_trail.live);load_record(record,originals[0]);CHECK(head(0,214,MIRROR_NORMAL)==0);
 }
 /* Smoke-only frames still bind both canonical records. */
 global_green_identity_frame_begin();weapons[1071].sound++;CHECK(!global_green_identity_records_match());load_record(1071,originals[1]);CHECK(global_green_identity_records_match());
 /* Fake slot, unsupported creator, stale token or repeated initializer. */
 global_green_identity_reset();CHECK(global_green_head_identity(0,214,214,0,0,MIRROR_NORMAL)==-1);CHECK(global_green_head_identity(999,214,214,0,0,MIRROR_NORMAL)==-1);
 CHECK(!render_mirror_green_create_begin(0,0,72,1,0,0,0,0));CHECK(!render_mirror_green_create_begin(43,0,71,1,0,0,0,0));CHECK(!render_mirror_green_create_begin(0,11,71,1,0,0,0,0));CHECK(!render_mirror_green_create_begin(0,0,71,0,0,0,0,0));
 birth(0);CHECK(head(0,214,MIRROR_NORMAL)==0);CHECK(!global_green_shots[0].role);
 /* Observe malformed state, restore it: no resurrection. */
 for(unsigned field=0;field<17;field++){
  birth(0);++mirror_logic_tick;--shotAvail[0];PlayerShotDataType *s=playerShotData; s->shotX+=s->shotXM;s->shotY+=s->shotYM;PlayerShotDataType save=*s;
  switch(field){case 0:s->shotX++;break;case 1:s->shotY++;break;case 2:s->shotXM++;break;case 3:s->shotYM++;break;case 4:s->shotXC++;break;case 5:s->shotYC++;break;case 6:s->shotGr++;break;case 7:s->shotAni++;break;case 8:s->shotAniMax++;break;case 9:s->shotTrail++;break;case 10:s->shotDmg++;break;case 11:s->shotBlastFilter++;break;case 12:s->playerNumber++;break;case 13:s->shotComplicated=true;break;case 14:s->aimAtEnemy=1;break;case 15:s->chainReaction=1;break;case 16:s->shotDevX=1;break;}
  render_mirror_green_trail_begin(0);CHECK(!global_green_shots[0].role);*s=save;CHECK(head(0,214,MIRROR_NORMAL)==0);
 }
 /* Trail lease is exact, bounded and cannot outlive its native call. */
 birth(0);++mirror_logic_tick;--shotAvail[0];playerShotData[0].shotX+=playerShotData[0].shotXM;playerShotData[0].shotY+=playerShotData[0].shotYM;render_mirror_green_trail_begin(0);
 CHECK(global_green_trail_identity(playerShotData[0].shotX,playerShotData[0].shotY,0,12,false,false));
 CHECK(!global_green_trail_identity(playerShotData[0].shotX+1,playerShotData[0].shotY,0,12,false,false));CHECK(!global_green_shots[0].role);render_mirror_green_trail_end();
 birth(0);unsigned raw=move(0);CHECK(!global_green_trail_identity(playerShotData[0].shotX,playerShotData[0].shotY,0,12,false,false));
 CHECK(head(0,raw,MIRROR_SHADOW)==1);CHECK(head(0,raw,MIRROR_SHADOW)==0);CHECK(head(0,raw,MIRROR_NORMAL)==0);
 birth(0);raw=move(0);CHECK(head(0,raw,MIRROR_NORMAL)==1);CHECK(head(0,raw,MIRROR_NORMAL)==0);
 birth(0);raw=move(0);CHECK(head(0,raw,MIRROR_NORMAL)==1);CHECK(head(0,raw,MIRROR_SHADOW)==0);
 birth(0);raw=move(0);CHECK(head(0,raw,MIRROR_BLEND)==0);
 birth(0);raw=move(0);playerShotData[0].shotX++;CHECK(head(0,raw,MIRROR_NORMAL)==0);
 birth(0);raw=move(0);playerShotData[0].shotAni++;CHECK(head(0,raw,MIRROR_NORMAL)==0);
 birth(0);raw=move(0);CHECK(head(0,raw+1,MIRROR_NORMAL)==0);
 birth(0);raw=move(0);++mirror_logic_tick;CHECK(head(0,raw,MIRROR_NORMAL)==0);
 birth(0);raw=move(0);render_mirror_green_trail_begin(0);CHECK(!global_green_shots[0].role);
 /* Reallocation invalidates old role even for non-green allocator. */
 birth(0);raw=move(0);shotAvail[0]=0;render_mirror_green_shot_allocated(0);CHECK(head(0,raw,MIRROR_NORMAL)==-1);
 /* The reserved last slot has no ordinary native draw/movement. */
 birth(MAX_PWEAPON-1);--shotAvail[MAX_PWEAPON-1];++mirror_logic_tick;render_mirror_green_trail_begin(MAX_PWEAPON-1);CHECK(!global_green_shots[MAX_PWEAPON-1].role);
 /* Leaked creator/trail calls cannot survive Finish or frame restart. */
 CHECK(render_mirror_green_create_begin(0,0,71,1,100,100,90,90));CHECK(!global_green_identity_complete());global_green_identity_frame_begin();CHECK(global_green_identity_fault);CHECK(global_green_identity_complete());global_green_identity_frame_begin();CHECK(!global_green_identity_fault);
 birth(0);++mirror_logic_tick;--shotAvail[0];playerShotData[0].shotX+=playerShotData[0].shotXM;playerShotData[0].shotY+=playerShotData[0].shotYM;render_mirror_green_trail_begin(0);CHECK(!global_green_identity_complete());global_green_identity_frame_begin();CHECK(global_green_identity_fault);CHECK(!global_green_trail.live);
 /* Root-off birth cannot be promoted by enabling HD later. */
 global_asset_directory[0]=0;birth(0);raw=move(0);CHECK(head(0,raw,MIRROR_NORMAL)==-1);strcpy(global_asset_directory,"global");CHECK(head(0,raw,MIRROR_NORMAL)==0);
}
int main(void)
{
 CHECK(fread(originals,1,sizeof(originals),stdin)==sizeof(originals));load_record(71,originals[0]);load_record(1071,originals[1]);
 CHECK(global_green_record_valid(71));CHECK(global_green_record_valid(1071));full_lifetimes();negative_cases();
 printf("green identity PASS: %u cases, %u checks\n",cases,checks);return 0;
}
