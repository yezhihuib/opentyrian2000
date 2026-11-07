/* SPDX-License-Identifier: GPL-2.0-or-later
 * Native allocator/movement proof for the canonical radial green records.
 * This observer never writes gameplay state. A matching sprite is not a role. */
#include "global_asset_registry.h"
static uint64_t global_green_create_serial;
static bool global_green_identity_fault;
static uint64_t global_green_used_records[2];
static struct {
 bool live,on;uint64_t token,tick;unsigned port,bay,record,player;int px,py,mx,my;
} global_green_create;
static struct {
 uint64_t generation,witnessed,allocated_tick,step_tick,head_tick,shadow_tick;
 bool pending,claimed,role,on,step;
 unsigned record,player,phase,ttl,raw;uint64_t stamp;
 PlayerShotDataType previous;
} global_green_shots[MAX_PWEAPON];
static struct {bool live;unsigned slot;uint64_t generation,tick;int x,y;} global_green_trail;
static uint64_t global_green_weapon_stamp(const JE_WeaponType *w)
{
 Uint8 b[80];size_t n=0;
#define GBYTE(v) do {b[n++]=(Uint8)(v);} while(0)
#define GWORD(v) do {unsigned z_=(unsigned)(v);GBYTE(z_);GBYTE(z_>>8);} while(0)
 GWORD(w->drain);GBYTE(w->shotrepeat);GBYTE(w->multi);GWORD(w->weapani);
 GBYTE(w->max);GBYTE(w->tx);GBYTE(w->ty);GBYTE(w->aim);
 for(unsigned i=0;i<8;i++)GBYTE(w->attack[i]);
 for(unsigned i=0;i<8;i++)GBYTE(w->del[i]);
 for(unsigned i=0;i<8;i++)GBYTE(w->sx[i]);
 for(unsigned i=0;i<8;i++)GBYTE(w->sy[i]);
 for(unsigned i=0;i<8;i++)GBYTE(w->bx[i]);
 for(unsigned i=0;i<8;i++)GBYTE(w->by[i]);
 for(unsigned i=0;i<8;i++)GWORD(w->sg[i]);
 GBYTE(w->acceleration);GBYTE(w->accelerationx);GBYTE(w->circlesize);GBYTE(w->sound);GBYTE(w->trail);GBYTE(w->shipblastfilter);
#undef GBYTE
#undef GWORD
 return n==80?global_bytes_hash(b,n):0;
}
static int global_green_record_profile(unsigned record)
{for(unsigned i=0;i<2;i++)if(record==global_green_weapon_ids[i])return (int)i;return -1;}
static bool global_green_record_valid(unsigned record)
{
 int p=global_green_record_profile(record);if(p<0)return false;
 uint64_t h=global_green_weapon_stamp(weapons+record);
 for(unsigned i=0;i<3;i++)if(h==global_green_weapon_fnv[p][i])return true;
 return false;
}
static bool global_green_identity_records_match(void)
{
 /* Smoke outlives its emitting head. Both canonical records stay part of
  * this shared family even during frames with no new shot observation. */
 for(unsigned i=0;i<2;i++)if(!global_green_record_valid(global_green_weapon_ids[i])||
  (global_green_used_records[i]&&global_green_weapon_stamp(weapons+global_green_weapon_ids[i])!=global_green_used_records[i]))return false;
 return true;
}
static void global_green_identity_bad(unsigned slot)
{if(slot<MAX_PWEAPON){if(global_green_shots[slot].role)global_green_identity_fault=true;global_green_shots[slot].role=false;global_green_shots[slot].step=false;}}
static void global_green_identity_reset(void)
{
 memset(global_green_shots,0,sizeof(global_green_shots));memset(&global_green_create,0,sizeof(global_green_create));
 memset(&global_green_trail,0,sizeof(global_green_trail));memset(global_green_used_records,0,sizeof(global_green_used_records));global_green_identity_fault=false;
}
static bool global_green_identity_complete(void)
{
 if(global_green_create.live||global_green_trail.live){global_green_identity_fault=true;return false;}
 return true;
}
static void global_green_identity_frame_begin(void)
{
 bool leaked=global_green_create.live||global_green_trail.live;
 global_green_identity_fault=leaked;memset(global_green_used_records,0,sizeof(global_green_used_records));
 memset(&global_green_create,0,sizeof(global_green_create));memset(&global_green_trail,0,sizeof(global_green_trail));
}
uint64_t render_mirror_green_create_begin(unsigned port,unsigned bay,unsigned record,unsigned pnum,int px,int py,int mx,int my)
{
 memset(&global_green_create,0,sizeof(global_green_create));
 if(global_green_record_profile(record)<0||port>PORT_NUM||bay>=11||pnum<1||pnum>2)return 0;
 global_green_create.live=true;global_green_create.on=global_asset_directory[0]&&!game_probe_original_reference&&!game_probe_missing&&!game_probe_invalid;
 if(++global_green_create_serial==0)++global_green_create_serial;
 global_green_create.token=global_green_create_serial;global_green_create.tick=mirror_logic_tick;
 global_green_create.port=port;global_green_create.bay=bay;global_green_create.record=record;global_green_create.player=pnum;
 global_green_create.px=px;global_green_create.py=py;global_green_create.mx=mx;global_green_create.my=my;
 return global_green_create.token;
}
void render_mirror_green_create_end(uint64_t token)
{if(token&&token==global_green_create.token)memset(&global_green_create,0,sizeof(global_green_create));}
void render_mirror_green_shot_allocated(unsigned slot)
{
 if(slot>=MAX_PWEAPON)return;
 if(++global_green_shots[slot].generation==0)++global_green_shots[slot].generation;
 global_green_shots[slot].role=global_green_shots[slot].step=false;
 global_green_shots[slot].pending=shotAvail[slot]==0;
 global_green_shots[slot].claimed=global_green_shots[slot].pending&&global_green_create.live&&global_green_create.tick==mirror_logic_tick;
 global_green_shots[slot].on=global_green_shots[slot].claimed&&global_green_create.on;
 global_green_shots[slot].allocated_tick=mirror_logic_tick;
}
void render_mirror_green_shot_initialized(uint64_t token,unsigned slot,unsigned port,unsigned bay,unsigned record,unsigned pnum,unsigned phase)
{
 if(slot>=MAX_PWEAPON)return;
 bool fresh=global_green_shots[slot].pending&&global_green_shots[slot].allocated_tick==mirror_logic_tick;
 global_green_shots[slot].pending=false;
 if(!fresh||!global_green_shots[slot].claimed||!token||token!=global_green_create.token||!global_green_create.live||global_green_create.tick!=mirror_logic_tick||
 port!=global_green_create.port||bay!=global_green_create.bay||record!=global_green_create.record||pnum!=global_green_create.player||phase<1||phase>8||!global_green_record_valid(record))return;
 const PlayerShotDataType *s=playerShotData+slot;const JE_WeaponType *w=weapons+record;unsigned k=phase-1;
 /* All accepted records have simple radial geometry and ordinary del=8.
  * The full record pin, not these convenient fields, is the authority. */
 if(shotAvail[slot]!=8||w->del[k]!=8||s->shotGr!=214||s->shotGr!=w->sg[k]||s->shotAni!=0||s->shotAniMax!=4||s->playerNumber!=pnum||
 s->shotX!=(JE_integer)(global_green_create.px+w->bx[k])||s->shotY!=(JE_integer)(global_green_create.py+w->by[k])||
 s->shotXM!=w->sx[k]||s->shotYM!=-w->sy[k]||s->shotXC!=w->accelerationx||s->shotYC!=-w->acceleration||
 s->shotComplicated||s->shotDevX||s->shotDirX||s->shotDevY||s->shotDirY||s->shotCirSizeX||s->shotCirSizeY||
 s->aimAtEnemy||s->chainReaction||s->shotTrail!=12||s->shotDmg!=w->attack[k]||s->shotBlastFilter!=w->shipblastfilter)return;
 global_green_shots[slot].role=true;global_green_shots[slot].witnessed=global_green_shots[slot].generation;
 global_green_shots[slot].record=record;global_green_shots[slot].player=pnum;global_green_shots[slot].phase=phase;
 global_green_shots[slot].stamp=global_green_weapon_stamp(w);global_green_shots[slot].previous=*s;global_green_shots[slot].ttl=shotAvail[slot];
 global_green_shots[slot].step_tick=global_green_shots[slot].head_tick=global_green_shots[slot].shadow_tick=UINT64_MAX;
 global_green_used_records[global_green_record_profile(record)]=global_green_shots[slot].stamp;
}
static bool global_green_identity_constants(unsigned slot)
{
 const PlayerShotDataType *s=playerShotData+slot,*p=&global_green_shots[slot].previous;
 return global_green_shots[slot].witnessed==global_green_shots[slot].generation&&
 global_green_record_valid(global_green_shots[slot].record)&&global_green_weapon_stamp(weapons+global_green_shots[slot].record)==global_green_shots[slot].stamp&&
 s->shotGr==p->shotGr&&s->shotAniMax==p->shotAniMax&&s->playerNumber==p->playerNumber&&
 s->shotXC==p->shotXC&&s->shotYC==p->shotYC&&!s->shotComplicated&&!s->aimAtEnemy&&!s->chainReaction&&
 !s->shotDevX&&!s->shotDirX&&!s->shotDevY&&!s->shotDirY&&!s->shotCirSizeX&&!s->shotCirSizeY&&
 s->shotTrail==p->shotTrail&&s->shotDmg==p->shotDmg&&s->shotBlastFilter==p->shotBlastFilter;
}
void render_mirror_green_trail_begin(unsigned slot)
{
 memset(&global_green_trail,0,sizeof(global_green_trail));
 if(slot>=MAX_PWEAPON||!global_green_shots[slot].claimed||!global_green_shots[slot].role)return;
 const PlayerShotDataType *s=playerShotData+slot,*p=&global_green_shots[slot].previous;
 bool good=slot<MAX_PWEAPON-1&&global_green_identity_constants(slot)&&global_green_shots[slot].ttl>0&&
 shotAvail[slot]==global_green_shots[slot].ttl-1&&global_green_shots[slot].step_tick!=mirror_logic_tick&&
 (!global_green_shots[slot].step||global_green_shots[slot].head_tick==global_green_shots[slot].step_tick)&&
 s->shotXM==(JE_integer)(p->shotXM+p->shotXC)&&s->shotYM==(JE_integer)(p->shotYM+p->shotYC)&&
 s->shotX==(JE_integer)(p->shotX+s->shotXM)&&s->shotY==(JE_integer)(p->shotY+s->shotYM)&&s->shotAni==p->shotAni&&
 s->shotX>=-34&&s->shotX<=290&&s->shotY>=-15&&s->shotY<=190;
 if(!good){global_green_identity_bad(slot);return;}
 global_green_shots[slot].step=true;global_green_shots[slot].step_tick=mirror_logic_tick;
 global_green_used_records[global_green_record_profile(global_green_shots[slot].record)]=global_green_shots[slot].stamp;
 global_green_shots[slot].raw=s->shotGr+s->shotAni;global_green_shots[slot].ttl=shotAvail[slot];
 global_green_trail.live=true;global_green_trail.slot=slot;global_green_trail.generation=global_green_shots[slot].generation;
 global_green_trail.tick=mirror_logic_tick;global_green_trail.x=s->shotX;global_green_trail.y=s->shotY;
}
void render_mirror_green_trail_end(void){global_green_trail.live=false;}
static bool global_green_trail_identity(int x,int y,int deltaY,int type,bool fixed,bool follow)
{
 if(!global_green_trail.live||global_green_trail.tick!=mirror_logic_tick)return false;
 unsigned slot=global_green_trail.slot;
 bool good=slot<MAX_PWEAPON&&global_green_shots[slot].role&&global_green_shots[slot].on&&
 global_green_shots[slot].generation==global_green_trail.generation&&global_green_identity_constants(slot)&&
 type==12&&!fixed&&!follow&&deltaY==0&&x==global_green_trail.x&&y==global_green_trail.y&&
 x==playerShotData[slot].shotX&&y==playerShotData[slot].shotY;
 if(!good)global_green_identity_bad(slot);
 return good;
}
static int global_green_head_identity(unsigned slot,unsigned raw,unsigned index,int x,int y,int style)
{
 if(slot>=MAX_PWEAPON||!global_green_shots[slot].claimed)return -1;
 if(!global_green_shots[slot].on&&!global_asset_directory[0])return -1;
 if(!global_green_shots[slot].role)return 0;
 const PlayerShotDataType *s=playerShotData+slot;
 bool shadow=style==MIRROR_SHADOW;uint64_t *seen=shadow?&global_green_shots[slot].shadow_tick:&global_green_shots[slot].head_tick;
 bool good=global_green_shots[slot].on&&global_green_identity_constants(slot)&&global_green_shots[slot].step&&global_green_shots[slot].step_tick==mirror_logic_tick&&
 (style==MIRROR_NORMAL||shadow)&&*seen!=mirror_logic_tick&&raw==global_green_shots[slot].raw&&raw==index&&index>=214&&index<=217&&
 s->shotAni==(raw-214+1)%4&&shotAvail[slot]==global_green_shots[slot].ttl&&
 s->shotXM==(JE_integer)(global_green_shots[slot].previous.shotXM+global_green_shots[slot].previous.shotXC)&&
 s->shotYM==(JE_integer)(global_green_shots[slot].previous.shotYM+global_green_shots[slot].previous.shotYC)&&
 s->shotX==(JE_integer)(global_green_shots[slot].previous.shotX+s->shotXM)&&
 s->shotY==(JE_integer)(global_green_shots[slot].previous.shotY+s->shotYM)&&x==s->shotX+1&&
 y==s->shotY+(shadow?(int)shadowYDist:0)&&(!shadow||(background2&&s->shotXM<100&&y<190&&global_green_shots[slot].head_tick!=mirror_logic_tick));
 if(!good){global_green_identity_bad(slot);return 0;}
 *seen=mirror_logic_tick;
 if(!shadow)global_green_shots[slot].previous=*s;
 return 1;
}
