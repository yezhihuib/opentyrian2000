/* SPDX-License-Identifier: GPL-2.0-or-later
 * Isolated production proof module test. Not a native allocator/display test.
 * Original table bytes arrive only on stdin and are never persisted. */
#include "pregame_font.h"
#include "episodes.h"
#include "player.h"
#include "tyrian2.h"
#include "shots.h"
#include "shop_vulcan.h"
#include "global_asset_registry.h"
#include <string.h>
static uint64_t hash(const void *p,size_t n){const Uint8 *b=p;uint64_t h=UINT64_C(14695981039346656037);while(n--)h=(h^*b++)*UINT64_C(1099511628211);return h;}
#include "shop_vulcan_proof.inc"

#include <stdio.h>
#include <stdlib.h>
Player player[2];
JE_WeaponType weapons[WEAP_NUM+1];
JE_WeaponPortType weaponPort;
PlayerShotDataType playerShotData[MAX_PWEAPON+1];
JE_byte shotAvail[MAX_PWEAPON];
static unsigned checks;
#define CHECK(x) do {++checks;if(!(x)){fprintf(stderr,"FAIL line %u: %s\n",__LINE__,#x);exit(1);}}while(0)
static Uint8 raw_records[3][11][80],raw_ports[3][82];
static unsigned variant;
static int mouse_dx,mouse_dy;
static void read_exact(void *p,size_t n){CHECK(fread(p,1,n,stdin)==n);}
static unsigned get16(const Uint8 **p){unsigned n=(*p)[0]+256u*(*p)[1];*p+=2;return n;}
static void load_tables(unsigned v)
{
 variant=v;
 for(unsigned k=0;k<11;k++) {
  const Uint8 *p=raw_records[v][k];JE_WeaponType *w=&weapons[221+k];memset(w,0,sizeof(*w));
  w->drain=get16(&p);w->shotrepeat=*p++;w->multi=*p++;w->weapani=get16(&p);w->max=*p++;w->tx=*p++;w->ty=*p++;w->aim=*p++;
  memcpy(w->attack,p,8);p+=8;memcpy(w->del,p,8);p+=8;memcpy(w->sx,p,8);p+=8;memcpy(w->sy,p,8);p+=8;memcpy(w->bx,p,8);p+=8;memcpy(w->by,p,8);p+=8;
  for(unsigned j=0;j<8;j++)w->sg[j]=get16(&p);
  w->acceleration=(int8_t)*p++;w->accelerationx=(int8_t)*p++;w->circlesize=*p++;w->sound=*p++;w->trail=*p++;w->shipblastfilter=*p++;CHECK(p==raw_records[v][k]+80);
 }
 const Uint8 *p=raw_ports[v];unsigned length=*p++;memcpy(weaponPort[7].name,p,30);shop_vulcan_port_name(7,length,weaponPort[7].name);weaponPort[7].name[MIN(length,30)]=0;p+=30;weaponPort[7].opnum=*p++;
 for(unsigned j=0;j<2;j++)for(unsigned i=0;i<11;i++)weaponPort[7].op[j][i]=get16(&p);
 weaponPort[7].cost=get16(&p);weaponPort[7].itemgraphic=get16(&p);weaponPort[7].poweruse=get16(&p);CHECK(p==raw_ports[v]+82);shop_vulcan_port_loaded(7);
}

static void birth(unsigned rec,unsigned phase){
 unsigned k=phase-1;const JE_WeaponType*w=weapons+rec;
 shotAvail[0]=0;shop_vulcan_allocated(0,player[0].x,player[0].y,player[0].x-mouse_dx,player[0].y-mouse_dy);PlayerShotDataType*s=playerShotData;memset(s,0,sizeof(*s));
 s->shotX=player[0].x+w->bx[k];s->shotY=player[0].y+w->by[k];s->shotXC=w->accelerationx;s->shotYC=-w->acceleration;
 s->shotXM=w->sx[k];s->shotYM=-w->sy[k];
 if(w->del[k]==98||w->del[k]==99){JE_integer d=mouse_dx;s->shotXM+=d < -5 ? -5 : d > 5 ? 5 : d;}
 if(w->del[k]==99||w->del[k]==100){JE_integer d=mouse_dy-w->sy[k];s->shotYM=d < -4 ? -4 : d > 4 ? 4 : d;}s->shotGr=w->sg[k];s->shotAniMax=w->weapani+1;s->shotDmg=w->attack[k];s->shotBlastFilter=w->shipblastfilter;s->shotTrail=w->trail;s->playerNumber=1;
 shotAvail[0]=w->del[k];shop_vulcan_initialized(0,7,FRONT_WEAPON,rec,1,phase);
}
static unsigned step(void){PlayerShotDataType*s=playerShotData;--shotAvail[0];s->shotXM+=s->shotXC;if(s->shotXM<=100)s->shotX+=s->shotXM;s->shotYM+=s->shotYC;s->shotY+=s->shotYM;unsigned raw=s->shotGr+s->shotAni;if(++s->shotAni==s->shotAniMax)s->shotAni=0;return raw;}
static void begin(unsigned rec){shop_vulcan_reset();memset(shotAvail,0,sizeof(shotAvail));player[0].items.weapon[0].id=7;player[0].items.weapon[0].power=rec-220;player[0].x=70;player[0].y=130;shop_vulcan_preview_begin(true);shop_vulcan_front_begin(7,0,rec-221,0,1,rec);}
static bool head(unsigned raw){return shop_vulcan_head(0,raw,playerShotData[0].shotX+1,playerShotData[0].shotY);}
int main(void){
 for(unsigned v=0;v<3;v++){read_exact(raw_records[v],sizeof(raw_records[v]));read_exact(raw_ports[v],82);}CHECK(fgetc(stdin)==EOF);
 for(unsigned v=0;v<3;v++){load_tables(v);for(unsigned rec=221;rec<=231;rec++)for(unsigned phase=1;phase<=weapons[rec].max;phase++){
 begin(rec);birth(rec,phase);CHECK(shop_vulcan.slots[0].role);shop_vulcan_front_end();
 for(unsigned n=0;n<10;n++){unsigned raw=step();bool visible=playerShotData[0].shotX>=0&&playerShotData[0].shotX<=140&&playerShotData[0].shotY>=0&&playerShotData[0].shotY<=170;CHECK(head(raw)==visible);if(!visible)break;CHECK(shop_vulcan_records_valid());shop_vulcan_preview_end();shop_vulcan_preview_begin(true);}
 begin(rec);birth(rec,phase);unsigned raw=step();CHECK(head(raw));CHECK(!head(raw));
 begin(rec);birth(rec,phase);raw=step();playerShotData[0].shotX++;CHECK(!head(raw));
 begin(rec);birth(rec,phase);raw=step();shotAvail[0]++;CHECK(!head(raw));
 begin(rec);birth(rec,phase);raw=step();shop_vulcan_allocated(0,player[0].x,player[0].y,player[0].x,player[0].y);CHECK(!head(raw));
 begin(rec);birth(rec,phase);raw=step();shop_vulcan_preview_end();CHECK(!head(raw));
 begin(rec);birth(rec,phase);raw=step();player[0].items.weapon[0].power=12;CHECK(!head(raw));
 begin(rec);birth(rec,phase);raw=step();CHECK(head(raw));weapons[rec].sound^=1;CHECK(!shop_vulcan_records_valid());weapons[rec].sound^=1;
 begin(rec);birth(rec,phase);raw=step();CHECK(head(raw));load_tables(v);CHECK(!shop_vulcan_records_valid());CHECK(!head(raw));
 begin(rec);shop_vulcan_front_begin(7,1,rec-221,0,1,rec);birth(rec,phase);CHECK(!shop_vulcan.slots[0].role);
 }}
 for(unsigned v=0;v<3;v++){
  for(unsigned rec=221;rec<=231;rec++)for(unsigned b=0;b<80;b++){
   raw_records[v][rec-221][b]^=1;load_tables(v);CHECK(!shop_vulcan_table(rec));raw_records[v][rec-221][b]^=1;
  }
  for(unsigned b=0;b<82;b++){
   raw_ports[v][b]^=1;load_tables(v);CHECK(!shop_vulcan_table(221));raw_ports[v][b]^=1;
  }
 }
 load_tables(0);begin(221);birth(221,1);shop_vulcan_front_end();shop_vulcan_preview_end();shop_vulcan_preview_begin(true);CHECK(!head(step()));
 begin(221);birth(221,1);shop_vulcan_preview_end();shop_vulcan_reset();shop_vulcan_preview_begin(true);CHECK(!head(step()));
 begin(221);birth(221,1);shop_vulcan_preview_end();shop_vulcan_preview_begin(false);CHECK(!head(step()));
 begin(221);shotAvail[0]=0;shop_vulcan_allocated(0,player[0].x,player[0].y,player[0].x,player[0].y);shop_vulcan_front_end();shop_vulcan_front_begin(7,0,0,0,1,221);shop_vulcan_initialized(0,7,0,221,1,1);CHECK(!shop_vulcan.slots[0].role);
 for(unsigned v=0;v<3;v++){load_tables(v);for(unsigned rec=221;rec<=231;rec++)for(unsigned phase=1;phase<=weapons[rec].max;phase++){
 const int deltas[]={-65536,-32769,-32768,-100,-6,-5,-4,-1,0,1,4,5,6,100,32767,32768,65536};
 for(unsigned d=0;d<sizeof(deltas)/sizeof(deltas[0]);d++){
  mouse_dx=deltas[d];begin(rec);birth(rec,phase);CHECK(shop_vulcan.slots[0].role);CHECK(head(step()));
  begin(rec);birth(rec,phase);playerShotData[0].shotXM++;CHECK(!head(step()));
  begin(rec);birth(rec,phase);PlayerShotDataType saved=playerShotData[0];unsigned ttl=shotAvail[0];
  /* A speed merely inside [-5,+5], but not the exact clamp, cannot claim. */
  shotAvail[0]=0;shop_vulcan_allocated(0,player[0].x,player[0].y,player[0].x-mouse_dx,player[0].y);
  shop_vulcan.emitted=0;shotAvail[0]=ttl;playerShotData[0]=saved;playerShotData[0].shotXM++;
  shop_vulcan_initialized(0,7,0,rec,1,phase);CHECK(!shop_vulcan.slots[0].role);
 }
 mouse_dx=mouse_dy=0;
 for(unsigned bay=1;bay<5;bay++){begin(rec);shop_vulcan_front_begin(7,bay,rec-221,0,1,rec);birth(rec,phase);CHECK(!shop_vulcan.slots[0].role);}
 begin(rec);shop_vulcan_front_begin(1,0,rec-221,0,1,rec);birth(rec,phase);CHECK(!shop_vulcan.slots[0].role);
 begin(rec);shop_vulcan_front_begin(7,0,rec-221,1,1,rec);birth(rec,phase);CHECK(!shop_vulcan.slots[0].role);
 begin(rec);shop_vulcan_front_begin(7,0,rec-221,0,2,rec);birth(rec,phase);CHECK(!shop_vulcan.slots[0].role);
 begin(rec);birth(rec,phase);CHECK(!head(step()+1));
#define BAD_BIRTH(field) do {begin(rec);birth(rec,phase);unsigned ttl_=shotAvail[0];shotAvail[0]=0;shop_vulcan_allocated(0,player[0].x,player[0].y,player[0].x,player[0].y);shotAvail[0]=ttl_;shop_vulcan.emitted=0;playerShotData[0].field=playerShotData[0].field+1;shop_vulcan_initialized(0,7,0,rec,1,phase);CHECK(!shop_vulcan.slots[0].role);}while(0)
 BAD_BIRTH(shotX);BAD_BIRTH(shotY);BAD_BIRTH(shotXC);BAD_BIRTH(shotYC);BAD_BIRTH(shotXM);BAD_BIRTH(shotYM);
 BAD_BIRTH(shotComplicated);BAD_BIRTH(shotDevX);BAD_BIRTH(shotDevY);BAD_BIRTH(shotDirX);BAD_BIRTH(shotDirY);BAD_BIRTH(shotCirSizeX);BAD_BIRTH(shotCirSizeY);
 BAD_BIRTH(shotGr);BAD_BIRTH(shotAni);BAD_BIRTH(shotAniMax);BAD_BIRTH(shotTrail);BAD_BIRTH(shotDmg);BAD_BIRTH(shotBlastFilter);BAD_BIRTH(chainReaction);BAD_BIRTH(playerNumber);BAD_BIRTH(aimAtEnemy);
#undef BAD_BIRTH
 begin(rec);birth(rec,phase);unsigned geometry_ttl=shotAvail[0];shotAvail[0]=0;shop_vulcan_allocated(0,player[0].x+1,player[0].y,player[0].x+1,player[0].y);shotAvail[0]=geometry_ttl;shop_vulcan.emitted=0;playerShotData[0].shotX++;shop_vulcan_initialized(0,7,0,rec,1,phase);CHECK(!shop_vulcan.slots[0].role);
 /* Non-guided allocator preserves aim delays: they are not invented zeros. */
 begin(rec);birth(rec,phase);unsigned ttl=shotAvail[0];shotAvail[0]=0;shop_vulcan_allocated(0,player[0].x,player[0].y,player[0].x,player[0].y);shotAvail[0]=ttl;shop_vulcan.emitted=0;playerShotData[0].aimDelay=3;playerShotData[0].aimDelayMax=9;shop_vulcan_initialized(0,7,0,rec,1,phase);CHECK(shop_vulcan.slots[0].role);CHECK(head(step()));
 }}
 printf("PASS %u proof checks; 3 raw table variants, all 11 powers/phases, consecutive simulation ticks until bounds exit; exact allocator clamp and signed narrowing; duplicate, wrong geometry/TTL, reuse, exit, selection, warm record mutation/reload, rear negatives.\n",checks);return 0;
}
