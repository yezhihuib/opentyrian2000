/* SPDX-License-Identifier: GPL-2.0-or-later
 * Independent shop-only provenance. This never grants a battle owner.
 * Included by pregame_font.c after hash(), shots.h and global registry pins. */
static Uint8 shop_pulse_port_name_bytes[30],shop_pulse_port_length;
static bool shop_pulse_port_pending,shop_pulse_port_valid;
static uint64_t shop_pulse_port_runtime,shop_pulse_port_epoch;
static uint64_t shop_pulse_record_stamp(const JE_WeaponType *w)
{
 Uint8 b[80];size_t n=0;
#define FRONT_BYTE(v) do {b[n++]=(Uint8)(v);} while(0)
#define FRONT_WORD(v) do {unsigned value_=(unsigned)(v);FRONT_BYTE(value_);FRONT_BYTE(value_>>8);} while(0)
 FRONT_WORD(w->drain);FRONT_BYTE(w->shotrepeat);FRONT_BYTE(w->multi);FRONT_WORD(w->weapani);
 FRONT_BYTE(w->max);FRONT_BYTE(w->tx);FRONT_BYTE(w->ty);FRONT_BYTE(w->aim);
 for(unsigned i=0;i<8;i++)FRONT_BYTE(w->attack[i]);
 for(unsigned i=0;i<8;i++)FRONT_BYTE(w->del[i]);
 for(unsigned i=0;i<8;i++)FRONT_BYTE(w->sx[i]);
 for(unsigned i=0;i<8;i++)FRONT_BYTE(w->sy[i]);
 for(unsigned i=0;i<8;i++)FRONT_BYTE(w->bx[i]);
 for(unsigned i=0;i<8;i++)FRONT_BYTE(w->by[i]);
 for(unsigned i=0;i<8;i++)FRONT_WORD(w->sg[i]);
 FRONT_BYTE(w->acceleration);FRONT_BYTE(w->accelerationx);FRONT_BYTE(w->circlesize);
 FRONT_BYTE(w->sound);FRONT_BYTE(w->trail);FRONT_BYTE(w->shipblastfilter);
#undef FRONT_BYTE
#undef FRONT_WORD
 return n==80?hash(b,n):0;
}
static uint64_t shop_pulse_port_stamp(bool disk)
{
 Uint8 b[82];size_t n=0;b[n++]=shop_pulse_port_length;
 memcpy(b+n,disk?shop_pulse_port_name_bytes:(const Uint8 *)weaponPort[1].name,30);n+=30;
 b[n++]=weaponPort[1].opnum;
 for(unsigned j=0;j<2;j++)for(unsigned i=0;i<11;i++){unsigned v=weaponPort[1].op[j][i];b[n++]=v;b[n++]=v>>8;}
 unsigned tail[3]={weaponPort[1].cost,weaponPort[1].itemgraphic,weaponPort[1].poweruse};
 for(unsigned i=0;i<3;i++){b[n++]=tail[i];b[n++]=tail[i]>>8;}
 return n==82?hash(b,n):0;
}
void shop_pulse_port_name(unsigned port,unsigned length,const char *name)
{
 if(port!=1)return;
 shop_pulse_port_valid=false;shop_pulse_port_pending=true;
 if(++shop_pulse_port_epoch==0)++shop_pulse_port_epoch;
 shop_pulse_port_length=(Uint8)length;memcpy(shop_pulse_port_name_bytes,name,30);
}
void shop_pulse_port_loaded(unsigned port)
{
 if(port!=1)return;
 shop_pulse_port_valid=shop_pulse_port_pending&&shop_pulse_port_stamp(true)==GLOBAL_PULSE_PORT_FNV;
 shop_pulse_port_pending=false;shop_pulse_port_runtime=shop_pulse_port_stamp(false);
}
static bool shop_pulse_table(unsigned record)
{
 if(record<155||record>165||!shop_pulse_port_valid||weaponPort[1].name[30]!=0||shop_pulse_port_stamp(false)!=shop_pulse_port_runtime)return false;
 uint64_t h=shop_pulse_record_stamp(weapons+record);
 for(unsigned i=0;i<3;i++)if(h==global_pulse_record_fnv[record-155][i])return true;
 return false;
}

struct ShopPulseSlot {
 uint64_t generation,witnessed,context,tick,record_stamp,port_epoch,call;
 unsigned record,ttl;
 bool pending,role;
 PlayerShotDataType previous;
};
static struct {
 bool live,front;
 uint64_t context,tick,call;
 unsigned item,level,record,emitted;
 int x,y;
 uint64_t used_records[11],used_port_epoch;
 struct ShopPulseSlot slots[MAX_PWEAPON];
} shop_pulse;
size_t shop_pulse_proof_bytes(void){return sizeof(shop_pulse)+sizeof(shop_pulse_port_name_bytes)+sizeof(shop_pulse_port_length)+sizeof(shop_pulse_port_pending)+sizeof(shop_pulse_port_valid)+sizeof(shop_pulse_port_runtime)+sizeof(shop_pulse_port_epoch);}
void shop_pulse_reset(void)
{
 shop_pulse.live=shop_pulse.front=false;
 if(++shop_pulse.context==0)++shop_pulse.context;
 shop_pulse.item=shop_pulse.level=0;
 memset(shop_pulse.used_records,0,sizeof(shop_pulse.used_records));
 for(unsigned i=0;i<MAX_PWEAPON;i++)shop_pulse.slots[i].role=shop_pulse.slots[i].pending=false;
}
void shop_pulse_preview_begin(bool authorized)
{
 unsigned item=player[0].items.weapon[FRONT_WEAPON].id;
 unsigned level=player[0].items.weapon[FRONT_WEAPON].power;
 if(!authorized||shop_pulse.live||item!=1||level<1||level>11){shop_pulse_reset();return;}
 if(item!=shop_pulse.item||level!=shop_pulse.level)shop_pulse_reset();
 shop_pulse.item=item;shop_pulse.level=level;shop_pulse.live=true;shop_pulse.front=false;
 if(++shop_pulse.tick==0){shop_pulse_reset();return;}
 memset(shop_pulse.used_records,0,sizeof(shop_pulse.used_records));
}
void shop_pulse_preview_end(void){shop_pulse.live=shop_pulse.front=false;}
void shop_pulse_front_begin(unsigned port,unsigned bay,unsigned level,unsigned mode,unsigned pnum,unsigned record)
{
 shop_pulse.front=false;
 if(!shop_pulse.live||port!=1||bay!=FRONT_WEAPON||pnum!=1||mode||level>=11||
    level+1!=shop_pulse.level||player[0].items.weapon[FRONT_WEAPON].id!=1||
    player[0].items.weapon[FRONT_WEAPON].power!=shop_pulse.level||
    record!=weaponPort[1].op[0][level]||!shop_pulse_table(record))return;
 if(++shop_pulse.call==0)++shop_pulse.call;
 shop_pulse.record=record;shop_pulse.emitted=0;
 shop_pulse.x=player[0].x;shop_pulse.y=player[0].y;shop_pulse.front=true;
}
void shop_pulse_front_end(void){shop_pulse.front=false;}
void shop_pulse_allocated(unsigned slot)
{
 if(slot>=MAX_PWEAPON)return;
 struct ShopPulseSlot *p=&shop_pulse.slots[slot];
 if(++p->generation==0)++p->generation;
 p->role=false;p->pending=shop_pulse.live&&shop_pulse.front&&shotAvail[slot]==0;
 p->context=shop_pulse.context;p->tick=shop_pulse.tick;p->call=shop_pulse.call;
}
static bool shop_pulse_index(unsigned index)
{for(unsigned i=0;i<5;i++)if(global_pulse_source[i].index==index)return true;return false;}
void shop_pulse_initialized(unsigned slot,unsigned port,unsigned bay,unsigned record,unsigned pnum,unsigned phase)
{
 if(slot>=MAX_PWEAPON)return;
 struct ShopPulseSlot *p=&shop_pulse.slots[slot];bool pending=p->pending;p->pending=false;
 if(!pending||!shop_pulse.live||!shop_pulse.front||p->call!=shop_pulse.call||p->context!=shop_pulse.context||p->tick!=shop_pulse.tick||
    port!=1||bay!=FRONT_WEAPON||pnum!=1||record!=shop_pulse.record||phase<1||phase>8||!shop_pulse_table(record))return;
 const JE_WeaponType *w=weapons+record;const PlayerShotDataType *s=playerShotData+slot;unsigned k=phase-1;
 if(++shop_pulse.emitted>w->multi||phase>w->max||!shotAvail[slot]||shotAvail[slot]!=w->del[k]||
    (w->del[k]>=98&&w->del[k]<=121)||w->sx[k]>100||w->sy[k]>=98||!shop_pulse_index(s->shotGr)||s->shotGr!=w->sg[k]||
    s->shotX!=shop_pulse.x+w->bx[k]||s->shotY!=shop_pulse.y+w->by[k]||s->playerNumber!=1||s->shotAni||
    s->shotAniMax!=w->weapani+1||s->shotComplicated||s->aimAtEnemy||s->chainReaction||s->shotTrail!=w->trail||
    s->shotXC!=w->accelerationx||s->shotYC!=-w->acceleration||s->shotXM!=w->sx[k]||s->shotYM!=-w->sy[k]||
    s->shotDmg!=w->attack[k]||s->shotBlastFilter!=w->shipblastfilter)return;
 p->role=true;p->witnessed=p->generation;p->record=record;p->record_stamp=shop_pulse_record_stamp(w);p->port_epoch=shop_pulse_port_epoch;
 p->ttl=shotAvail[slot];p->previous=*s;
 /* Newly born shots are simulated in this same preview tick. */
 p->tick=shop_pulse.tick-1;
}
/* Compare named fields, never C structure padding. No simulation writes occur. */
static bool shop_pulse_same(const PlayerShotDataType *a,const PlayerShotDataType *b)
{
#define SP_EQ(f) if(a->f!=b->f)return false
 SP_EQ(shotX);SP_EQ(shotY);SP_EQ(shotXM);SP_EQ(shotYM);SP_EQ(shotXC);SP_EQ(shotYC);
 SP_EQ(shotComplicated);SP_EQ(shotDevX);SP_EQ(shotDirX);SP_EQ(shotDevY);SP_EQ(shotDirY);SP_EQ(shotCirSizeX);SP_EQ(shotCirSizeY);
 SP_EQ(shotTrail);SP_EQ(shotGr);SP_EQ(shotAni);SP_EQ(shotAniMax);SP_EQ(shotDmg);SP_EQ(shotBlastFilter);
 SP_EQ(chainReaction);SP_EQ(playerNumber);SP_EQ(aimAtEnemy);SP_EQ(aimDelay);SP_EQ(aimDelayMax);
#undef SP_EQ
 return true;
}
bool shop_pulse_head(unsigned slot,unsigned index,int x,int y)
{
 if(slot>=MAX_PWEAPON-1)return false;
 struct ShopPulseSlot *p=&shop_pulse.slots[slot];
 if(!shop_pulse.live||!p->role)return false;
 bool valid=p->witnessed==p->generation&&p->port_epoch==shop_pulse_port_epoch&&p->context==shop_pulse.context&&p->tick+1==shop_pulse.tick&&p->ttl&&
    shotAvail[slot]==p->ttl-1&&shop_pulse_table(p->record)&&shop_pulse_record_stamp(weapons+p->record)==p->record_stamp&&
    player[0].items.weapon[FRONT_WEAPON].id==shop_pulse.item&&player[0].items.weapon[FRONT_WEAPON].power==shop_pulse.level;
 PlayerShotDataType want=p->previous;
 want.shotXM+=want.shotXC;if(want.shotXM<=100)want.shotX+=want.shotXM;
 want.shotYM+=want.shotYC;want.shotY+=want.shotYM;
 if(want.shotYM>100){want.shotY-=120;want.shotY+=player[0].delta_y_shot_move;}
 unsigned raw=want.shotGr+want.shotAni;if(++want.shotAni==want.shotAniMax)want.shotAni=0;
 valid=valid&&raw==index&&shop_pulse_index(index)&&want.shotX>=0&&want.shotX<=140&&want.shotY>=0&&want.shotY<=170&&
    x==want.shotX+1&&y==want.shotY&&shop_pulse_same(&want,playerShotData+slot);
 /* A failed or duplicate draw cannot revive this birth later. */
 if(!valid){p->role=false;return false;}
 p->previous=want;p->ttl=shotAvail[slot];p->tick=shop_pulse.tick;
 shop_pulse.used_records[p->record-155]=p->record_stamp;shop_pulse.used_port_epoch=shop_pulse_port_epoch;
 return true;
}
bool shop_pulse_records_valid(void)
{
 for(unsigned i=0;i<11;i++)if(shop_pulse.used_records[i]&&
    (shop_pulse.used_port_epoch!=shop_pulse_port_epoch||!shop_pulse_table(155+i)||shop_pulse_record_stamp(weapons+155+i)!=shop_pulse.used_records[i]))return false;
 return true;
}
