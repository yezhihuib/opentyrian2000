/* SPDX-License-Identifier: GPL-2.0-or-later
 * Compile-time opt-in IDENTITY VALIDATION ONLY. Never authorizes or draws HD.
 * NEWSHF logical bank10 is NOT static spriteSheet10. No animation is introduced.
 * This include observes production state; every rejection leaves classic intact.
 */
#include "newshf_prototype_pins.h"
#include "newshf_linked_pins.h"
#include "newshf_dualmissile_pins.h"
#include "newshf_turret_pins.h"
/* Native cycles select resources; these descriptors never advance animation. */
static const struct {unsigned record,cycles,bases[7],resources[7]; bool linked;} newshf_profiles[]={
 {163,3,{125,123,127,0},{0,1,2,0},false},
 {167,3,{3,1,5,0},{3,4,5,0},false},
 {168,3,{55,17,93,0},{6,7,8,0},false},
 {171,4,{43,45,45,43},{9,10,10,9},true},
 {172,4,{81,83,83,81},{11,12,12,11},true},
 {173,4,{119,121,121,119},{13,14,14,13},true},
 {2,1,{169,0,0,0},{15,0,0,0},false},
 {500,1,{169,0,0,0},{15,0,0,0},false},
 {162,7,{39,41,41,41,39,39,39},{16,17,17,17,16,16,16},true},
 {840,7,{39,41,41,41,39,39,39},{16,17,17,17,16,16,16},true}
};
static struct {
 uint64_t generation,witnessed,born_tick,draw_tick,bank_epoch;
 const Sprite2_array *bank_object;
 const Uint8 *bank_data;
 size_t bank_size;
 uint64_t bank_stamp,record_stamp;
 bool pending,role;
 unsigned remaining,pose;
 int profile,value,x,y,filter;
} newshf_validation_slots[100];
static uint64_t newshf_validation_tick,newshf_validation_bank_epoch;
/* Diagnostic counters only; not runtime acceptance or a rendering lease. */
static struct {uint64_t allocations,initialized,tiles,assemblies,rejected,resets;} newshf_validation_counts;
static int newshf_validation_profile(unsigned record)
{
 for(unsigned i=0;i<COUNTOF(newshf_profiles);i++)if(record==newshf_profiles[i].record)return (int)i;
 return -1;
}
static int newshf_validation_slot(const void *ptr)
{
 uintptr_t p=(uintptr_t)ptr,b=(uintptr_t)enemy;
 if(p<b||p-b>=sizeof(enemy)||(p-b)%sizeof(enemy[0]))return -1;
 return (int)((p-b)/sizeof(enemy[0]));
}
static const Sprite2_array *newshf_validation_bank(void)
{
 const Sprite2_array *bank=NULL;unsigned count=0;
 for(unsigned i=0;i<COUNTOF(enemySpriteSheetIds);i++)if(enemySpriteSheetIds[i]==10){bank=&enemySpriteSheets[i];count++;}
 return count==1&&bank->data&&bank->size==NEWSHF_PROTOTYPE_BANK_BYTES?bank:NULL;
}
static bool newshf_validation_bank_valid(const Sprite2_array *b)
{return b&&b->data&&b->size==NEWSHF_PROTOTYPE_BANK_BYTES&&global_bytes_hash(b->data,b->size)==NEWSHF_PROTOTYPE_BANK_FNV;}
static uint64_t newshf_validation_record_stamp(unsigned profile)
{
 if(profile>=COUNTOF(newshf_profiles))return 0;
 unsigned record=newshf_profiles[profile].record;
 Uint8 bytes[77];size_t n=0;
#define NEWSHF_BYTE(v) do {bytes[n++]=(Uint8)(v);} while(0)
#define NEWSHF_WORD(v) do {unsigned cv_=(unsigned)(v);NEWSHF_BYTE(cv_);NEWSHF_BYTE(cv_>>8);} while(0)
 NEWSHF_BYTE(enemyDat[record].ani);
 for(unsigned i=0;i<3;i++)NEWSHF_BYTE(enemyDat[record].tur[i]);
 for(unsigned i=0;i<3;i++)NEWSHF_BYTE(enemyDat[record].freq[i]);
 NEWSHF_BYTE(enemyDat[record].xmove);NEWSHF_BYTE(enemyDat[record].ymove);
 NEWSHF_BYTE(enemyDat[record].xaccel);NEWSHF_BYTE(enemyDat[record].yaccel);
 NEWSHF_BYTE(enemyDat[record].xcaccel);NEWSHF_BYTE(enemyDat[record].ycaccel);
 NEWSHF_WORD(enemyDat[record].startx);NEWSHF_WORD(enemyDat[record].starty);
 NEWSHF_BYTE(enemyDat[record].startxc);NEWSHF_BYTE(enemyDat[record].startyc);
 NEWSHF_BYTE(enemyDat[record].armor);NEWSHF_BYTE(enemyDat[record].esize);
 for(unsigned i=0;i<20;i++)NEWSHF_WORD(enemyDat[record].egraphic[i]);
 NEWSHF_BYTE(enemyDat[record].explosiontype);NEWSHF_BYTE(enemyDat[record].animate);NEWSHF_BYTE(enemyDat[record].shapebank);
 NEWSHF_BYTE(enemyDat[record].xrev);NEWSHF_BYTE(enemyDat[record].yrev);NEWSHF_WORD(enemyDat[record].dgr);
 NEWSHF_BYTE(enemyDat[record].dlevel);NEWSHF_BYTE(enemyDat[record].dani);NEWSHF_BYTE(enemyDat[record].elaunchfreq);
 NEWSHF_WORD(enemyDat[record].elaunchtype);NEWSHF_WORD(enemyDat[record].value);NEWSHF_WORD(enemyDat[record].eenemydie);
#undef NEWSHF_BYTE
#undef NEWSHF_WORD
 return n==77?global_bytes_hash(bytes,n):0;
}
static bool newshf_validation_record_valid(unsigned p)
{
 return p<COUNTOF(newshf_profiles)&&newshf_validation_record_stamp(p)==
  (p<3?newshf_prototype_record_fnv[p]:p<6?newshf_linked_record_fnv[p-3]:p<8?newshf_dualmissile_record_fnv[p-6]:newshf_turret_record_fnv[p-8]);
}
static bool newshf_validation_records(void)
{
 for(unsigned i=0;i<3;i++)if(newshf_validation_record_stamp(i)!=newshf_prototype_record_fnv[i])return false;
 return true;
}
static bool newshf_validation_palette(void)
{
 Uint8 bytes[768];
 for(unsigned i=0;i<256;i++){
  bytes[3*i]=(Uint8)(rgb_palette[i]>>16);bytes[3*i+1]=(Uint8)(rgb_palette[i]>>8);bytes[3*i+2]=(Uint8)rgb_palette[i];
 }
 return global_bytes_hash(bytes,sizeof(bytes))==NEWSHF_PROTOTYPE_PALETTE_FNV;
}
static bool newshf_validation_bind(unsigned slot)
{
 const Sprite2_array *b=newshf_validation_bank();
 return b&&b==newshf_validation_slots[slot].bank_object&&b==enemy[slot].sprite2s&&
  b->data==newshf_validation_slots[slot].bank_data&&b->size==newshf_validation_slots[slot].bank_size&&
  newshf_validation_slots[slot].bank_epoch==newshf_validation_bank_epoch&&
  newshf_validation_slots[slot].bank_stamp==NEWSHF_PROTOTYPE_BANK_FNV&&newshf_validation_bank_valid(b);
}
static bool newshf_validation_shape(unsigned slot)
{
 const struct JE_SingleEnemyType *e=enemy+slot;int p=newshf_validation_slots[slot].profile;
 if(p<0||(unsigned)p>=COUNTOF(newshf_profiles))return false;
 unsigned record=newshf_profiles[p].record;
 if(!newshf_validation_record_valid((unsigned)p))return false;
 bool animation=newshf_profiles[p].linked?
  e->ani==newshf_profiles[p].cycles&&e->animin==1&&e->animax==newshf_profiles[p].cycles&&e->aniwhenfire==2&&(e->aniactive==1||e->aniactive==2):
  e->ani==1&&e->animin==1&&!e->aniactive&&!e->animax&&!e->aniwhenfire;
 if(!newshf_validation_bind(slot)||e->enemytype!=record||e->enemydatofs!=&enemyDat[record]||
  e->size!=1||e->scoreitem||e->edamaged||!animation||
  e->edani!=enemyDat[record].dani||e->edgr!=enemyDat[record].dgr||e->edlevel!=enemyDat[record].dlevel)return false;
 for(unsigned i=0;i<20;i++)if(e->egr[i]!=enemyDat[record].egraphic[i])return false;
 return true;
}
/* Revoke all three records coherently. There is no RGB contribution to undo. */
static void newshf_validation_reject(void)
{
#if defined(NEWSHF_HD_COMPOSITOR) && NEWSHF_HD_COMPOSITOR
 global_newshf_invalidate();
#endif
 for(unsigned i=0;i<COUNTOF(newshf_validation_slots);i++){
  newshf_validation_slots[i].role=false;newshf_validation_slots[i].pending=false;newshf_validation_slots[i].remaining=0;
 }
 ++newshf_validation_counts.rejected;
}
void render_mirror_newshf_validation_reset(void)
{
#if defined(NEWSHF_HD_COMPOSITOR) && NEWSHF_HD_COMPOSITOR
 global_newshf_invalidate();
#endif
 if(++newshf_validation_bank_epoch==0)++newshf_validation_bank_epoch;
 memset(newshf_validation_slots,0,sizeof(newshf_validation_slots));
 ++newshf_validation_counts.resets;
}
void render_mirror_newshf_validation_bank_changed(const void *ptr)
{
 for(unsigned i=0;i<COUNTOF(enemySpriteSheets);i++)if(ptr==&enemySpriteSheets[i]){
  render_mirror_newshf_validation_reset();return;
 }
}
void render_mirror_newshf_validation_frame(void)
{
 bool good=true;
 for(unsigned i=0;i<COUNTOF(newshf_validation_slots);i++)if(newshf_validation_slots[i].role){
  if(newshf_validation_slots[i].remaining)good=false;
  /* Ordinary death/despawn is not corruption of another live actor's proof. */
  if(enemyAvail[i]!=0){newshf_validation_slots[i].role=false;continue;}
  if(!newshf_validation_shape(i)||enemy[i].evalue!=newshf_validation_slots[i].value)good=false;
 }
 if(!good||!newshf_validation_records())newshf_validation_reject();
 for(unsigned i=0;i<COUNTOF(newshf_validation_slots);i++)newshf_validation_slots[i].pending=false;
 if(++newshf_validation_tick==0){render_mirror_newshf_validation_reset();++newshf_validation_tick;}
}
void render_mirror_newshf_validation_allocated(void *ptr,unsigned record,int unique_shape)
{
 int s=newshf_validation_slot(ptr);if(s<0)return;
 /* Every allocation, including unrelated records, retires any old role. */
 if(++newshf_validation_slots[s].generation==0)++newshf_validation_slots[s].generation;
 newshf_validation_slots[s].role=newshf_validation_slots[s].pending=false;newshf_validation_slots[s].remaining=0;
 newshf_validation_slots[s].profile=newshf_validation_profile(record);
 if(newshf_validation_slots[s].profile<0)return;
 ++newshf_validation_counts.allocations;
 const Sprite2_array *b=newshf_validation_bank();
 if(enemyAvail[s]!=1||(unique_shape>0&&unique_shape!=10)||!newshf_validation_records()||!newshf_validation_bank_valid(b)){
  newshf_validation_reject();return;
 }
 newshf_validation_slots[s].bank_object=b;newshf_validation_slots[s].bank_data=b->data;newshf_validation_slots[s].bank_size=b->size;
 newshf_validation_slots[s].bank_stamp=global_bytes_hash(b->data,b->size);
 newshf_validation_slots[s].bank_epoch=newshf_validation_bank_epoch;
 newshf_validation_slots[s].record_stamp=newshf_validation_record_stamp((unsigned)newshf_validation_slots[s].profile);
 newshf_validation_slots[s].born_tick=newshf_validation_tick;newshf_validation_slots[s].pending=true;
}
void render_mirror_newshf_validation_initialized(void *ptr,unsigned record,unsigned avail)
{
 int s=newshf_validation_slot(ptr);if(s<0)return;
 int p=newshf_validation_profile(record);bool pending=newshf_validation_slots[s].pending;
 newshf_validation_slots[s].pending=false;
 if(p<0)return;
 if(!pending||p!=newshf_validation_slots[s].profile||newshf_validation_slots[s].born_tick!=newshf_validation_tick||
  avail!=0||enemyAvail[s]!=1||!newshf_validation_records()||!newshf_validation_shape(s)||enemy[s].enemycycle!=1||
  newshf_validation_slots[s].record_stamp!=newshf_validation_record_stamp((unsigned)p)){
  newshf_validation_reject();return;
 }
 newshf_validation_slots[s].witnessed=newshf_validation_slots[s].generation;
 newshf_validation_slots[s].value=enemy[s].evalue;newshf_validation_slots[s].draw_tick=UINT64_MAX;
 newshf_validation_slots[s].role=true;++newshf_validation_counts.initialized;
}
/* Observe pose chosen by native code; no next-phase expectation or timer. */
void render_mirror_newshf_validation_observe(unsigned s)
{
 if(s>=COUNTOF(newshf_validation_slots)||newshf_validation_profile(enemy[s].enemytype)<0)return;
 /* A revoked/unwitnessed actor remains ineligible, but must not repeatedly
  * poison fresh allocations after an earlier failure or ordinary retirement. */
 if(!newshf_validation_slots[s].role)return;
 const struct JE_SingleEnemyType *e=enemy+s;
 if(newshf_validation_slots[s].remaining||
  newshf_validation_slots[s].witnessed!=newshf_validation_slots[s].generation||
  newshf_validation_slots[s].draw_tick==newshf_validation_tick||enemyAvail[s]!=0||!newshf_validation_shape(s)||
  !newshf_validation_records()||!newshf_validation_palette()||e->evalue!=newshf_validation_slots[s].value||
  e->enemycycle<1||e->enemycycle>newshf_profiles[newshf_validation_slots[s].profile].cycles||(int)e->ex+(int)tempMapXOfs<=-29||(int)e->ex+(int)tempMapXOfs>=300){
  newshf_validation_reject();return;
 }
 newshf_validation_slots[s].draw_tick=newshf_validation_tick;newshf_validation_slots[s].pose=e->enemycycle;
 newshf_validation_slots[s].remaining=(e->ey>-13?3u:0u)|(e->ey>-26&&e->ey<182?12u:0u);
 newshf_validation_slots[s].x=(int)e->ex+(int)tempMapXOfs;newshf_validation_slots[s].y=e->ey;newshf_validation_slots[s].filter=e->filter;
}
static bool newshf_validation_tile_source(Sprite2_array bank,unsigned index)
{
 for(unsigned i=0;i<COUNTOF(newshf_prototype_tiles);i++)if(newshf_prototype_tiles[i].index==index){
  Uint8 bytes[336]={0};
  return decode_tile(bank,index,bytes,bytes+168,12,0,0)&&global_bytes_hash(bytes,sizeof(bytes))==newshf_prototype_tiles[i].fnv;
 }
 for(unsigned i=0;i<COUNTOF(newshf_linked_tiles);i++)if(newshf_linked_tiles[i].index==index){
  Uint8 bytes[336]={0};
  return decode_tile(bank,index,bytes,bytes+168,12,0,0)&&global_bytes_hash(bytes,sizeof(bytes))==newshf_linked_tiles[i].fnv;
 }
 for(unsigned i=0;i<COUNTOF(newshf_dualmissile_tiles);i++)if(newshf_dualmissile_tiles[i].index==index){
  Uint8 bytes[336]={0};
  return decode_tile(bank,index,bytes,bytes+168,12,0,0)&&global_bytes_hash(bytes,sizeof(bytes))==newshf_dualmissile_tiles[i].fnv;
 }
 for(unsigned i=0;i<COUNTOF(newshf_turret_tiles);i++)if(newshf_turret_tiles[i].index==index){
  Uint8 bytes[336]={0};
  return decode_tile(bank,index,bytes,bytes+168,12,0,0)&&global_bytes_hash(bytes,sizeof(bytes))==newshf_turret_tiles[i].fnv;
 }
 return false;
}
bool render_mirror_newshf_validation_tile(SDL_Surface *surface,int x,int y,Sprite2_array bank,unsigned base,int part,int filter,const G101EnemyContext *c)
{
 if(!c||newshf_validation_profile(c->type)<0)return false;
 unsigned s=c->pool_slot,q=part==0?0:part==1?1:part==19?2:part==20?3:4;
 if(s>=COUNTOF(newshf_validation_slots)){newshf_validation_reject();return false;}
 if(!newshf_validation_slots[s].role)return false;
 const struct JE_SingleEnemyType *e=enemy+s;unsigned bit=q<4?1u<<q:0,remaining=newshf_validation_slots[s].remaining;
 int p=newshf_validation_profile(c->type);
 bool good=surface&&surface==game_screen&&surface==VGAScreen&&surface->pixels&&surface->format&&
  surface->w==320&&surface->h==200&&surface->pitch==320&&surface->format->format==SDL_PIXELFORMAT_INDEX8&&
  surface->format->BitsPerPixel==8&&surface->format->BytesPerPixel==1&&
  newshf_validation_slots[s].role&&p==newshf_validation_slots[s].profile&&
  newshf_validation_slots[s].witnessed==newshf_validation_slots[s].generation&&
  newshf_validation_slots[s].draw_tick==newshf_validation_tick&&enemyAvail[s]==0&&newshf_validation_shape(s)&&
  newshf_validation_records()&&newshf_validation_palette()&&e->evalue==newshf_validation_slots[s].value&&
  c->availability==0&&c->size==1&&!c->score_item&&!c->damaged&&
  q<4&&bit==(remaining&(~remaining+1u))&&filter>=0&&filter<=255&&filter==e->filter&&filter==newshf_validation_slots[s].filter&&
  bank.data==newshf_validation_slots[s].bank_data&&bank.size==newshf_validation_slots[s].bank_size&&
  e->enemycycle==newshf_validation_slots[s].pose&&e->enemycycle>=1&&e->enemycycle<=newshf_profiles[p].cycles&&
  base==newshf_profiles[p].bases[e->enemycycle-1]&&base==e->egr[e->enemycycle-1]&&
  (int)e->ex+(int)tempMapXOfs==newshf_validation_slots[s].x&&(int)e->ey==newshf_validation_slots[s].y&&
  x==newshf_validation_slots[s].x+(q&1?6:-6)&&y==newshf_validation_slots[s].y+(q>=2?7:-7)&&
  newshf_validation_tile_source(bank,base+(unsigned)part);
 if(!good){newshf_validation_reject();return false;}
 newshf_validation_slots[s].remaining&=~bit;++newshf_validation_counts.tiles;
 if(!newshf_validation_slots[s].remaining)++newshf_validation_counts.assemblies;
 return true;
}
