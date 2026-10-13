#include "unit.h"
/* Full original data/type/constructor excerpts, with deterministic RNG input. */
JE_EnemyDatType enemyDat;
struct JE_SingleEnemyType enemy[100];
JE_byte enemyAvail[100],soundQueue[8],shotMultiPos[16],shotAvail[100];
Player player[2];
Explosion explosions[MAX_EXPLOSIONS];
JE_word tempW,enemyKilled;
int b,cubeMax,superArcadeMode,superArcadePowerUp,playerNum=1,difficultyLevel,totalEnemy;
bool galagaMode,twoPlayerLinked,isNetworkGame,twoPlayerMode,onePlayerAction,superTyrian;
int mouseX,mouseY;
char *miscTextB[4],*miscText[46];
enum {FRONT_WEAPON=0,REAR_WEAPON=1,SHOT_MISC=4,S_ITEM=18,S_POWERUP=29,V_DATA_CUBE=39,S_EXPLOSION_9=9,S_EXPLOSION_8=8};
typedef enum {ENTITY_NORMAL,ENTITY_BLEND,ENTITY_SHADOW} EntityDrawStyle;
typedef enum {ENTITY_TILE,ENTITY_QUAD} EntityDrawLayout;
static unsigned checks,scenarios;
#define CHECK(x) do {++checks;if(!(x)){fprintf(stderr,"FAIL %s:%d: %s\n",__FILE__,__LINE__,#x);exit(1);}} while(0)
static void unexpected(void) {fputs("Unselected branch called a stub\n",stderr);abort();}
const char *JE_getName(int i) {(void)i;unexpected();return "";}
void JE_drawTextWindow(const char *p) {(void)p;unexpected();}
bool power_up_weapon(Player *p,uint w) {(void)p;(void)w;unexpected();return false;}
uint player_shot_create(int a,int c,int d,int e,int f,int g,int h,int i)
{(void)a;(void)c;(void)d;(void)e;(void)f;(void)g;(void)h;(void)i;unexpected();return 0;}
static const uint rng_stream[]={0,249,124,125,255,0x12345678,0xabcdef01,15};
static unsigned rng_calls;
uint mt_rand(void) {uint v=rng_stream[rng_calls%COUNTOF(rng_stream)];rng_calls++;return v;}
static Uint8 bank_byte,bank11_byte,bank10_byte;
SDL_Surface *VGAScreen;
Sprite2_array explosionSpriteSheet={1,&bank_byte},spriteSheet11={1,&bank11_byte},spriteSheet10={1,&bank10_byte};
Sprite2_array enemySpriteSheets[4]={{1,&bank_byte},{0,NULL},{0,NULL},{0,NULL}};
JE_byte enemySpriteSheetIds[4]={1,0,0,0};
#include "super_specials.inc"
#include "events_fixture.inc"
#include "spawn_events_fixture.inc"
#include "movement_events_fixture.inc"
struct JE_EventRecType eventRec[1];
int eventLoc=1,newPL[10];
int mapX=1,mapX3,backMove=1,backMove2=2,backMove3=3;
bool background3x1,background3x1b,smallEnemyAdjust;
#include "spawn_enemy.inc"
static void apply_event(const struct JE_EventRecType *record)
{
 int temp;eventRec[0]=*record;
 switch(eventRec[0].eventtype) {
#include "event6.inc"
#include "event19.inc"
#include "event33.inc"
#include "event45.inc"
 default:unexpected();
 }
}
#include "setup_explosion.inc"
static void assign_reward(struct JE_SingleEnemyType *enemy,Uint16 eDatI)
{
#include "reward.inc"
}
/* Caller context only. Exact collision envelope + exact scoreitem branch. */
static void collect_near(JE_byte playerNum_)
{
 Player *this_player=&player[playerNum_-1];char tempStr[256];
#include "collision_envelope.inc"
 if(false) {}
#include "scoreitem.inc"
 } } }
}
static void collect_scoreitem(int z,JE_byte playerNum_)
{
 Player *this_player=&player[playerNum_-1];
 int evalue=enemy[z].evalue,enemy_screen_x=enemy[z].ex+enemy[z].mapoffset;
 char tempStr[256];
 if(false) {}
#include "scoreitem.inc"
}
/* Exactly two selected carrier records and two allocation-return records. */
struct Carrier {int slot,type,x,y;bool released;ulong cash_at_release;};
struct Allocation {int carrier_slot,offset,type,free_count,first_free,result,constructor_x,constructor_y;unsigned rng_before,rng_after;};
static struct Carrier carriers[2];
static struct Allocation allocations[2];
static int allocation_calls,factory_calls,release_calls;
static bool observe_pair,mode_control;
static Uint8 default_lives=3;
Sint16 __real_JE_newEnemy(int,Uint16,Sint16);
uint __real_JE_makeEnemy(struct JE_SingleEnemyType *,Uint16,Sint16);
uint __wrap_JE_makeEnemy(struct JE_SingleEnemyType *e,Uint16 type,Sint16 shape)
{factory_calls++;return __real_JE_makeEnemy(e,type,shape);}
Sint16 __wrap_JE_newEnemy(int offset,Uint16 type,Sint16 shape)
{
 if(!observe_pair)return __real_JE_newEnemy(offset,type,shape);
 CHECK(allocation_calls<2);int n=allocation_calls++;
 struct Allocation *a=&allocations[n];struct Carrier *c=&carriers[n];
 *a=(struct Allocation){.carrier_slot=c->slot,.offset=offset,.type=type,.first_free=-1,.rng_before=rng_calls};
 CHECK(release_calls==n && !c->released && enemyAvail[c->slot]==0 && enemy[c->slot].enemytype==c->type);
 for(int i=offset;i<offset+25;i++)if(enemyAvail[i]==1){a->free_count++;if(a->first_free<0)a->first_free=i;}
 a->result=__real_JE_newEnemy(offset,type,shape);a->rng_after=rng_calls;
 CHECK(a->result==(a->first_free<0?0:a->first_free+1));
 if(a->result){a->constructor_x=enemy[a->result-1].ex;a->constructor_y=enemy[a->result-1].ey;}
 CHECK(enemyAvail[c->slot]==0 && enemy[c->slot].enemytype==c->type && !c->released);
 return (Sint16)a->result;
}
void JE_setupExplosionLarge(bool ground,JE_byte count,JE_integer x,JE_integer y)
{
 /* Original caller reaches this immediately after carrier reward/release.
    No gameplay state is changed by this observation sink. */
 if(!observe_pair){CHECK(mode_control);release_calls++;return;}
 CHECK(release_calls<2);int n=release_calls++;
 struct Carrier *c=&carriers[n];struct Allocation *a=&allocations[n];
 CHECK(ground==enemy[c->slot].enemyground && count==enemy[c->slot].explonum);
 CHECK(x==c->x+enemy[c->slot].mapoffset && y==c->y);
 CHECK(enemy[c->slot].enemytype==c->type && enemyAvail[c->slot]==1 && !c->released);
 CHECK(allocation_calls==n+1 && enemyKilled==n+1);
 c->released=true;c->cash_at_release=player[galagaMode?0:playerNum-1].cash;
 if(a->result){int slot=a->result-1;CHECK(slot!=c->slot && enemy[slot].enemytype==392 && enemyAvail[slot]==2);CHECK(enemy[slot].ex==c->x && enemy[slot].ey==c->y);}
}
static bool globalFlags[256];
static void linked_death(int hit)
{
 int temp=enemy[hit].linknum,temp2,temp3;b=hit;
#include "linked_death.inc"
}
struct BodyDraw {int slot,id,x,y,cycle;};
static struct BodyDraw body_draws[256];static int body_count,tempMapXOfs=11,tempBackMove=1;
static void blit_enemy(SDL_Surface *surface,int i,int dx,int dy,int part)
{
 CHECK(surface==VGAScreen && body_count<(int)COUNTOF(body_draws));
 body_draws[body_count++]=(struct BodyDraw){i,enemy[i].egr[enemy[i].enemycycle-1]+part,enemy[i].ex+tempMapXOfs+dx,enemy[i].ey+dy,enemy[i].enemycycle};
}
static void move_coin(int i)
{
 if(enemyAvail[i]==1)return;
#include "movement.inc"
draw_enemy_end:;
}
bool explosionTransparent;
JE_integer explosionFollowAmountX,explosionFollowAmountY,explodeMove;
struct Draw {int x,y,id,style,layout,ttl,sprite,deltaY,fixed,follow;};
static struct Draw draws[256];
static bool gates25[256],gates75[256],gates50[256];
static int draw_count,gate_count25,gate_count75,gate_count50;
void render_mirror_coin25_value_begin(bool e){CHECK(gate_count25<(int)COUNTOF(gates25));gates25[gate_count25++]=e;}
void render_mirror_coin75_value_begin(bool e){CHECK(gate_count75<(int)COUNTOF(gates75));gates75[gate_count75++]=e;}
void render_mirror_coin50_value_begin(bool e){CHECK(gate_count50<(int)COUNTOF(gates50));gates50[gate_count50++]=e;}
void draw_entity_sprite2(SDL_Surface *s,int x,int y,Sprite2_array bank,unsigned id,EntityDrawStyle style,EntityDrawLayout layout)
{
 CHECK(s==VGAScreen && bank.data==explosionSpriteSheet.data && layout==ENTITY_TILE);
 CHECK(draw_count<(int)COUNTOF(draws));Explosion *e=NULL;
 for(int i=0;i<MAX_EXPLOSIONS;i++)if(explosions[i].ttl && explosions[i].x==x && explosions[i].y==y && (unsigned)explosions[i].sprite+1==id){CHECK(e==NULL);e=&explosions[i];}
 CHECK(e!=NULL);draws[draw_count++]=(struct Draw){x,y,(int)id,style,layout,e->ttl,e->sprite,e->deltaY,e->fixedPosition,e->followPlayer};
}
static void draw_original(void){
#include "draw_original.inc"
}
static void draw_candidate(void){
#include "draw_candidate.inc"
}
static void reset(void)
{
 memset(enemy,0,sizeof(enemy));memset(enemyAvail,1,sizeof(enemyAvail));
 memset(enemyDat,0,sizeof(enemyDat));memset(player,0,sizeof(player));
 memset(explosions,0,sizeof(explosions));memset(soundQueue,0,sizeof(soundQueue));
 memset(draws,0,sizeof(draws));memset(gates25,0,sizeof(gates25));memset(gates75,0,sizeof(gates75));memset(gates50,0,sizeof(gates50));
 memset(carriers,0,sizeof(carriers));memset(allocations,0,sizeof(allocations));memset(body_draws,0,sizeof(body_draws));
 b=cubeMax=superArcadeMode=superArcadePowerUp=enemyKilled=totalEnemy=0;
 galagaMode=twoPlayerLinked=isNetworkGame=twoPlayerMode=onePlayerAction=superTyrian=observe_pair=mode_control=false;
 allocation_calls=factory_calls=release_calls=body_count=draw_count=gate_count25=gate_count75=gate_count50=0;rng_calls=0;
 playerNum=1;explodeMove=3;explosionFollowAmountX=5;explosionFollowAmountY=-2;tempMapXOfs=11;tempBackMove=1;
 explosionTransparent=false;player[0].lives=player[1].lives=&default_lives;player[0].cash=1000;player[1].cash=2000;difficultyLevel=DIFFICULTY_NORMAL;
#include "record_fixture.inc"
}
static void seed_coin(int rid,int y)
{
 enemyAvail[20]=(JE_byte)JE_makeEnemy(&enemy[20],(Uint16)rid,0);
 enemy[20].ex=78;enemy[20].mapoffset=20;enemy[20].ey=(JE_integer)y;
}
static int sprite_for(int rid){return rid==391?184:rid==392?203:222;}
static void expect_coin_popup(int rid,int y)
{
 CHECK(explosions[0].ttl==8 && explosions[0].sprite==sprite_for(rid));
 CHECK(explosions[0].x==98 && explosions[0].y==y);
 CHECK(explosions[0].fixedPosition && !explosions[0].followPlayer && explosions[0].deltaY==0);
 for(int i=1;i<MAX_EXPLOSIONS;i++)CHECK(explosions[i].ttl==0);
}
static void test_collection(void)
{
 for(int rid=391;rid<=393;rid++)for(int linked=0;linked<2;linked++)for(int who=1;who<=2;who++)
 {
  int value=(rid-390)*25,share=value/2;reset();twoPlayerLinked=linked;seed_coin(rid,150);collect_scoreitem(20,(JE_byte)who);
  CHECK(player[0].cash==1000UL+(linked?share:(who==1?value:0)));CHECK(player[1].cash==2000UL+(linked?share:(who==2?value:0)));
  CHECK(enemyAvail[20]==1 && soundQueue[7]==S_ITEM);expect_coin_popup(rid,150);scenarios++;
 }
 const int dxs[]={-13,-12,-11,0,11,12,13},dys[]={-15,-14,-13,0,13,14,15};
 for(size_t x=0;x<COUNTOF(dxs);x++)for(size_t y=0;y<COUNTOF(dys);y++)
 {
  reset();seed_coin(392,150);player[0].x=98+dxs[x];player[0].y=150+dys[y];
  bool hit=abs(dxs[x])<12 && abs(dys[y])<14;collect_near(1);
  CHECK(enemyAvail[20]==(hit?1:2));CHECK(player[0].cash==1000UL+(hit?50:0));CHECK(soundQueue[7]==(hit?S_ITEM:0));CHECK(explosions[0].ttl==(hit?8:0));scenarios++;
 }
 puts("PASS Normal50/linked25+25, preserved25/75 collectors; exact original strict dx12/dy14 collision boundaries, removal and S_ITEM");
}
static void fill_effects(void){for(int i=0;i<MAX_EXPLOSIONS;i++)explosions[i]=(Explosion){.ttl=(JE_byte)(1+i%8),.x=(JE_integer)i,.y=33,.sprite=203,.fixedPosition=true};}
static void test_full_effect_pool(void)
{
 for(int linked=0;linked<2;linked++)
 {
  reset();fill_effects();Explosion before[MAX_EXPLOSIONS];memcpy(before,explosions,sizeof(before));
  JE_setupExplosion(98,150,0,37,true,false);CHECK(memcmp(before,explosions,sizeof(before))==0);
  twoPlayerLinked=linked;seed_coin(392,150);collect_scoreitem(20,1);
  CHECK(memcmp(before,explosions,sizeof(before))==0 && enemyAvail[20]==1 && soundQueue[7]==S_ITEM);
  CHECK(player[0].cash==1000UL+(linked?25:50) && player[1].cash==2000UL+(linked?25:0));scenarios++;
 }
 puts("PASS full200 effect pool leaves all slots unchanged while50 collection and reward complete");
}
static void test_setup_bounds(void)
{
 const int ys[]={-17,-16,-15,0,186,187,188,189,190,191};
 for(size_t k=0;k<COUNTOF(ys);k++)
 {
  int y=ys[k];bool admitted=y>-16 && y<190;reset();JE_setupExplosion(98,(JE_integer)y,0,37,true,false);
  if(admitted)expect_coin_popup(392,y);else {Explosion empty[MAX_EXPLOSIONS]={0};CHECK(memcmp(empty,explosions,sizeof(empty))==0);}
  reset();seed_coin(392,y);collect_scoreitem(20,1);CHECK(enemyAvail[20]==1 && player[0].cash==1050);CHECK((explosions[0].ttl!=0)==admitted);scenarios++;
 }
 puts("PASS original setup y bounds; refused setup never undoes collection");
}
/* A finite matrix across all ascending carrier-slot pairs, with 0/1/3 free
   slots selected outside both carriers. No final-vacancy assertion for slot1. */
static void test_linked_pool(void)
{
 for(int first=25;first<49;first++)for(int second=first+1;second<50;second++)for(int free_case=0;free_case<3;free_case++)
 {
  reset();for(int i=25;i<50;i++){enemyAvail[i]=(i%3==0)?2:0;enemy[i].enemytype=10;enemy[i].linknum=99;}
  int available=free_case==2?3:free_case;
  for(int i=25,n=0;i<50 && n<available;i++)if(i!=first && i!=second){enemyAvail[i]=1;n++;}
  const int slots[]={first,second};
  for(int n=0;n<2;n++)
  {
   int slot=slots[n];enemyAvail[slot]=(JE_byte)JE_makeEnemy(&enemy[slot],(Uint16)(13+n),0);
   enemy[slot].ex=(JE_integer)(168+n*24);enemy[slot].ey=-8;enemy[slot].mapoffset=11;enemy[slot].linknum=2;enemy[slot].enemydie=392;
   carriers[n]=(struct Carrier){slot,13+n,168+n*24,-8,false,0};
  }
  int prior_factory=factory_calls;unsigned prior_rng=rng_calls;observe_pair=true;linked_death(first);observe_pair=false;
  CHECK(allocation_calls==2 && release_calls==2 && enemyKilled==2 && b==first);
  CHECK(carriers[0].released && carriers[1].released && carriers[0].cash_at_release==1025 && carriers[1].cash_at_release==1050);
  CHECK(player[0].cash==1050 && player[1].cash==2000);
  int successes=0;
  for(int n=0;n<2;n++)
  {
   struct Allocation *a=&allocations[n];CHECK(a->carrier_slot==slots[n] && a->offset==25 && a->type==392);
   CHECK(a->free_count==(n==0?available:available+(available==0)));
   CHECK(a->rng_after-a->rng_before==(unsigned)(a->result!=0));
   if(a->result)
   {
    int slot=a->result-1;uint sample=rng_stream[a->rng_before%COUNTOF(rng_stream)];
    CHECK(a->constructor_x==(int)(130+sample%250-125+1) && a->constructor_y==-12);
    CHECK(enemy[slot].enemytype==392 && enemyAvail[slot]==2 && enemy[slot].scoreitem && enemy[slot].armorleft==255 && enemy[slot].linknum==0);
    CHECK(enemy[slot].sprite2s==&spriteSheet11 && enemy[slot].enemycycle==0 && enemy[slot].egr[0]==26 && enemy[slot].egr[5]==31);
    CHECK(enemy[slot].ex==carriers[n].x && enemy[slot].ey==carriers[n].y);successes++;
   }
  }
  CHECK(successes==(available?2:1) && factory_calls==prior_factory+successes && rng_calls==prior_rng+(unsigned)successes);
  if(available==0)CHECK(allocations[0].result==0 && allocations[1].result==first+1 && enemy[first].enemytype==392 && enemyAvail[first]==2);
  if(allocations[1].result==first+1)CHECK(enemy[first].ex==192 && enemy[first].ey==-8); /* real alias, not old carrier */
  CHECK(enemyAvail[second]==1 && enemy[second].enemytype==14);
  /* Collect only the first successful birth using its observed return slot. */
  int selected=allocations[0].result?0:1,slot=allocations[selected].result-1;collect_scoreitem(slot,1);CHECK(player[0].cash==1100 && enemyAvail[slot]==1);
  /* A later occupant does not change the already recorded birth/release. */
  enemyAvail[slot]=(JE_byte)JE_makeEnemy(&enemy[slot],391,0);CHECK(enemy[slot].enemytype==391 && enemyAvail[slot]==2 && carriers[0].released && carriers[1].released);
  scenarios++;
 }
 puts("PASS900 ascending linked pair/pool cases:0/1/3 free, both requests before own release, first-full failure/second reuse, coordinates, exact constructor RNG counts and25+25 separate rewards");
}
static void test_lifecycle(void)
{
 for(int rid=391;rid<=393;rid++)for(int style=0;style<2;style++)
 {
  Explosion history[12][MAX_EXPLOSIONS];struct Draw expected[8];
  reset();explosionTransparent=style;JE_setupExplosion(98,150,0,enemyDat[rid].explosiontype,true,false);
  for(int frame=0;frame<12;frame++)
  {
   int n=draw_count;draw_original();memcpy(history[frame],explosions,sizeof(explosions));
   CHECK(draw_count==n+(frame<8) && explosions[0].ttl==(frame<8?7-frame:0));
   if(frame<8){struct Draw *d=&draws[frame];CHECK(d->id==sprite_for(rid)+1 && d->ttl==8-frame && d->sprite==sprite_for(rid));CHECK(d->x==98 && d->y==150 && d->fixed && !d->follow && d->deltaY==0 && d->style==style);}
  }
  CHECK(draw_count==8 && gate_count25==0 && gate_count75==0 && gate_count50==0);memcpy(expected,draws,sizeof(expected));
  reset();explosionTransparent=style;JE_setupExplosion(98,150,0,enemyDat[rid].explosiontype,true,false);
  for(int frame=0;frame<12;frame++){draw_candidate();CHECK(memcmp(history[frame],explosions,sizeof(explosions))==0);CHECK(gate_count25==(frame<8?frame+1:8) && gate_count75==gate_count25 && gate_count50==gate_count25);}
  CHECK(draw_count==8 && memcmp(expected,draws,sizeof(expected))==0);
  for(int i=0;i<8;i++){CHECK(gates25[i]==(rid==391));CHECK(gates75[i]==(rid==393));CHECK(gates50[i]==(rid==392));}
  /* The freed popup slot is reusable, so identity is established by draw id. */
  JE_setupExplosion(120,80,0,36,true,false);CHECK(explosions[0].ttl==8 && explosions[0].sprite==184);draw_candidate();CHECK(draws[8].id==185 && !gates50[8]);scenarios++;
 }
 puts("PASS fixed204/185/223 both styles:8 draws each,4 clear steps, all200 Explosion bytes and draw arguments identical; popup reuse is a different effect");
}
static void test_draw_boundaries(void)
{
 const int ys[]={-15,186,187,188,189};
 for(size_t k=0;k<COUNTOF(ys);k++)for(int style=0;style<2;style++)
 {
  Explosion baseline[MAX_EXPLOSIONS];struct Draw expected[256];int n;
  reset();explosionTransparent=style;JE_setupExplosion(98,(JE_integer)ys[k],0,37,true,false);draw_original();
  n=draw_count;memcpy(expected,draws,sizeof(expected));memcpy(baseline,explosions,sizeof(baseline));
  CHECK(n==(ys[k]<=186) && explosions[0].ttl==(ys[k]<=186?7:0));
  reset();explosionTransparent=style;JE_setupExplosion(98,(JE_integer)ys[k],0,37,true,false);draw_candidate();
  CHECK(memcmp(baseline,explosions,sizeof(baseline))==0 && memcmp(expected,draws,sizeof(expected))==0);
  CHECK(gate_count25==n && gate_count75==n && gate_count50==n && draw_count==n);scenarios++;
 }
 /* Independent exclusions within the original draw-site eligibility. */
 for(int kind=0;kind<3;kind++)
 {
  reset();JE_setupExplosion(98,40,0,37,true,false);
  if(kind==0)explosions[0].followPlayer=true;
  if(kind==1)explosions[0].deltaY=1;
  if(kind==2)explosions[0].ttl=9;
  draw_candidate();CHECK(draw_count==1 && !gates50[0] && !gates25[0] && !gates75[0]);scenarios++;
 }
 puts("PASS y187..189 cancel before all3 hooks, y186 draws; follow/deltaY/TTL exclusions remain exact");
}
static void test_moving_and_mixed(void)
{
 const int types[]={45,48,49},ttls[]={20,14,14},target[]={223,204,223};
 for(int kind=0;kind<3;kind++)for(int style=0;style<2;style++)
 {
  int ttl=ttls[kind];Explosion history[24][MAX_EXPLOSIONS];struct Draw expected[256];
  reset();explosionTransparent=style;JE_setupExplosion(98,40,0,(JE_integer)types[kind],false,false);
  for(int f=0;f<24;f++){draw_original();memcpy(history[f],explosions,sizeof(explosions));}
  CHECK(draw_count==ttl);memcpy(expected,draws,sizeof(expected));
  reset();explosionTransparent=style;JE_setupExplosion(98,40,0,(JE_integer)types[kind],false,false);
  for(int f=0;f<24;f++){draw_candidate();CHECK(memcmp(history[f],explosions,sizeof(explosions))==0);}
  CHECK(draw_count==ttl && gate_count25==ttl && gate_count75==ttl && gate_count50==ttl && memcmp(expected,draws,sizeof(expected))==0);
  int hits=0;for(int n=0;n<ttl;n++){CHECK(!gates25[n] && !gates75[n] && !gates50[n]);if(draws[n].id==target[kind]){hits++;CHECK(!draws[n].fixed);if(kind==1)CHECK(n==13 && draws[n].ttl==1 && draws[n].sprite==203);}}
  CHECK(hits==1);scenarios++;
 }
 static const int permutations[][3]={{36,37,38},{36,38,37},{37,36,38},{37,38,36},{38,36,37},{38,37,36}};
 for(size_t p=0;p<COUNTOF(permutations);p++)for(int style=0;style<2;style++)
 {
  Explosion history[10][MAX_EXPLOSIONS];struct Draw expected[256];
  for(int candidate=0;candidate<2;candidate++)
  {
   reset();explosionTransparent=style;
   for(int n=0;n<3;n++)JE_setupExplosion((JE_integer)(80+n*20),(JE_integer)(50+n*20),0,(JE_integer)permutations[p][n],true,false);
   for(int f=0;f<10;f++)if(candidate){draw_candidate();CHECK(memcmp(history[f],explosions,sizeof(explosions))==0);}else{draw_original();memcpy(history[f],explosions,sizeof(explosions));}
   CHECK(draw_count==24);
   if(candidate){CHECK(memcmp(expected,draws,sizeof(expected))==0);CHECK(gate_count25==24 && gate_count75==24 && gate_count50==24);for(int i=0;i<24;i++){CHECK(gates25[i]==(draws[i].id==185));CHECK(gates50[i]==(draws[i].id==204));CHECK(gates75[i]==(draws[i].id==223));}}
   else memcpy(expected,draws,sizeof(expected));
  }
  scenarios++;
 }
 puts("PASS moving48 reaches204 on its14th/final draw with50 gate false; moving45/49 remain classic; all6 mixed185/204/223 permutations in both styles");
}
static void test_difficulty(void)
{
 const int values[]={-32768,-4,-1,0,1,2,25,50,75,1250,1251,2499,2500,2501,4000,4001,5000,5001,6666,6667,8888,8889,9999,10000,10001,30000,32767};
 const int numer[]={6,6,8,8,9,12,16,20,32,32,64,64};
 const int expected50[]={37,37,50,50,56,75,100,125,200,200,400,400};
 for(int difficulty=-2;difficulty<=11;difficulty++)for(size_t k=0;k<COUNTOF(values);k++)
 {
  reset();difficultyLevel=difficulty;int v=values[k];enemyDat[392].value=(JE_integer)v;int expected=v;
  if(v>1 && v<10000){expected=difficulty>=-1 && difficulty<=10?v*numer[difficulty+1]/8:0;if(expected>10000)expected=10000;}
  assign_reward(&enemy[0],392);CHECK(enemy[0].evalue==expected);scenarios++;
 }
 for(int difficulty=-1;difficulty<=10;difficulty++)for(int rid=391;rid<=393;rid++)for(int linked=0;linked<2;linked++)
 {
  reset();difficultyLevel=difficulty;twoPlayerLinked=linked;seed_coin(rid,150);
  int expected=(rid-390)*25*numer[difficulty+1]/8;if(rid==392)CHECK(expected==expected50[difficulty+1]);
  CHECK(enemy[20].evalue==expected);collect_scoreitem(20,1);
  CHECK(player[0].cash==1000UL+(linked?expected/2:expected));CHECK(player[1].cash==2000UL+(linked?expected/2:0));expect_coin_popup(rid,150);
  for(int type=13;type<=14;type++){JE_makeEnemy(&enemy[30],(Uint16)type,0);CHECK(enemy[30].evalue==25*numer[difficulty+1]/8);}
  scenarios++;
 }
 puts("PASS all difficulties and27 threshold/cap controls;50=37/50/56/75/100/125/200/400, linked integer halves, carrier25 scales separately,25/75 preserved");
}
static void test_spawn_and_movement(void)
{
 reset();for(int n=0;n<2;n++)
 {
  apply_event(&fixture_spawns[n]);int slot=b-1;
  CHECK(slot==25+n && enemyAvail[slot]==0 && enemy[slot].enemytype==13+n);
  CHECK(enemy[slot].ex==168+n*24 && enemy[slot].ey==-44 && enemy[slot].eyc==1 && enemy[slot].exc==0);
  CHECK(enemy[slot].linknum==2 && enemy[slot].armorleft==6 && enemy[slot].evalue==25 && enemy[slot].size==1);
  CHECK(enemy[slot].egr[0]==85+n*2 && enemy[slot].tur[0]==116-n && enemy[slot].sprite2s==&enemySpriteSheets[0]);
 }
 CHECK(rng_calls==0 && factory_calls==2);apply_event(&fixture_events[0]);CHECK(enemy[25].enemydie==392 && enemy[26].enemydie==392);scenarios++;
 reset();seed_coin(392,-8);enemy[20].ex=168;
 for(int f=0;f<18;f++){move_coin(20);CHECK(body_count==f+1);CHECK(body_draws[f].id==26+f%6 && body_draws[f].y==-8+f*2 && body_draws[f].x==179);CHECK(enemy[20].ey==-6+f*2);}
 CHECK(rng_calls==1);scenarios++;
 const int xs[]={-40,-39,288,289},ys[]={-14,-13,-12,189,190};
 for(size_t x=0;x<COUNTOF(xs);x++)for(size_t y=0;y<COUNTOF(ys);y++)
 {
  reset();seed_coin(392,ys[y]);enemy[20].ex=(JE_integer)xs[x];move_coin(20);
  bool anim=xs[x]+11>-29 && xs[x]+11<300,draw=anim && ys[y]>-13;
  CHECK(enemy[20].enemycycle==(anim?1:0) && body_count==draw);
  CHECK(enemyAvail[20]==(ys[y]==190?1:2));CHECK(enemy[20].ey==ys[y]+(ys[y]==190?1:2));scenarios++;
 }
 const int bottom[]={-114,-113,-112,188,189,190};
 for(size_t y=0;y<COUNTOF(bottom);y++)
 {
  reset();seed_coin(392,bottom[y]);move_coin(20);bool removed=bottom[y]+1 < -112 || bottom[y]+1 >190;
  CHECK(enemyAvail[20]==(removed?1:2) && enemy[20].ey==bottom[y]+(removed?1:2));
  if(removed){int n=body_count;move_coin(20);move_coin(20);CHECK(body_count==n);}
  scenarios++;
 }
 /* Source-derived local coin movement only: no player/input/runtime claim. */
 reset();seed_coin(392,-8);enemy[20].ex=192;int removed_at=-1;
 for(int f=0;f<102;f++){move_coin(20);if(enemyAvail[20]==1 && removed_at<0)removed_at=f;}
 CHECK(removed_at==99 && body_count==100 && body_draws[99].y==190 && enemy[20].ey==191);scenarios++;
 puts("PASS original events135/136 constructor/spawn fields; six-phase advance-before-draw, x/y gates, intrinsic-y removal before background-y and2 clear observations");
}
static void test_modes(void)
{
 static Uint8 lives=3;
 for(int st=0;st<2;st++)for(int two=0;two<2;two++)for(int action=0;action<2;action++)for(int arcade=0;arcade<2;arcade++)
 {
  reset();superTyrian=st;twoPlayerMode=two;onePlayerAction=action;superArcadeMode=arcade;player[0].lives=&lives;
  for(int i=0;i<3;i++){enemy[30+i].linknum=(JE_byte)(2+i*2);enemyAvail[30+i]=0;}
  enemy[80].linknum=2;enemyAvail[80]=1; /* original assignment scans even free slots */
  seed_coin(392,100);struct JE_SingleEnemyType coin=enemy[20];JE_byte before[100];memcpy(before,enemyAvail,sizeof(before));unsigned rng_before=rng_calls;
  for(size_t k=0;k<COUNTOF(fixture_events);k++)
  {
   apply_event(&fixture_events[k]);CHECK(enemy[30+k].enemydie==392 && memcmp(&eventRec[0],&fixture_events[k],sizeof(eventRec[0]))==0);
   CHECK(memcmp(&coin,&enemy[20],sizeof(coin))==0 && memcmp(before,enemyAvail,sizeof(before))==0 && rng_calls==rng_before);
   for(size_t j=k+1;j<COUNTOF(fixture_events);j++)CHECK(enemy[30+j].enemydie==0);
  }
  CHECK(enemy[80].enemydie==392);
  for(size_t k=0;k<COUNTOF(fixture_moves);k++){apply_event(&fixture_moves[k]);CHECK(memcmp(&coin,&enemy[20],sizeof(coin))==0);CHECK(enemy[30].eyc==fixture_moves[k].eventdat2);}
  /* Exact unchanged datacube guard: applies to512/513, never392. */
  for(int dat=512;dat<=513;dat++)
  {
   struct JE_EventRecType e=fixture_events[0];e.eventdat=(JE_integer)dat;enemy[30].enemydie=0;apply_event(&e);
   CHECK(enemy[30].enemydie==((st||two||action)?0:dat));
  }
  /* Exact 534 remap contrast and533 random-special branch. */
  struct JE_EventRecType e=fixture_events[0];e.eventdat=534;unsigned prior=rng_calls;apply_event(&e);
  int remap=arcade?827:st?828+superTyrianSpecials[rng_stream[prior%COUNTOF(rng_stream)]%4]:534;
  CHECK(enemy[30].enemydie==remap && rng_calls-prior==(unsigned)(!arcade && st));
  lives=11;e.eventdat=533;prior=rng_calls;apply_event(&e);
  CHECK(enemy[30].enemydie==(!arcade&&!st?829+rng_stream[prior%COUNTOF(rng_stream)]%6:533));CHECK(rng_calls-prior==(unsigned)(!arcade&&!st));lives=3;
  /* Original event45 mode gate positive/negative controls. */
  e=fixture_events[0];e.eventtype=45;e.eventdat=628;enemy[30].enemydie=392;apply_event(&e);
  CHECK(enemy[30].enemydie==(!st&&(two||action)?628:392));scenarios++;
 }
 puts("PASS exact139/149/150 at970/1000/1010 in16 mode combinations;392 bypasses512/513/533/534 remaps, link0 ignores later link2 moves; original event45 guards retained");
}
static void test_arcade_drop_suppression(void)
{
 const int rids[]={391,392,393,628};
 for(int arcade=0;arcade<2;arcade++)for(size_t k=0;k<COUNTOF(rids);k++)
 {
  reset();superArcadeMode=arcade;
  for(int n=0;n<2;n++)
  {
   int slot=25+n;enemyAvail[slot]=(JE_byte)JE_makeEnemy(&enemy[slot],(Uint16)(13+n),0);
   enemy[slot].ex=(JE_integer)(168+n*24);enemy[slot].ey=-8;enemy[slot].linknum=2;enemy[slot].enemydie=(JE_word)rids[k];
  }
  int before=factory_calls;unsigned prior=rng_calls;mode_control=true;linked_death(25);mode_control=false;
  bool suppressed=arcade && rids[k]==628;int count=0;
  for(int i=25;i<50;i++)if(enemyAvail[i]!=1 && enemy[i].enemytype==rids[k])count++;
  CHECK(count==(suppressed?0:2) && factory_calls-before==(suppressed?0:2));
  unsigned per_birth=(enemyDat[rids[k]].startxc!=0)+(enemyDat[rids[k]].startyc!=0);
  CHECK(rng_calls-prior==(suppressed?0:2*per_birth));
  CHECK(release_calls==2 && enemyKilled==2 && player[0].cash==1050 && player[1].cash==2000);
  CHECK(enemyAvail[26]==1);if(suppressed)CHECK(enemyAvail[25]==1);else CHECK(enemy[25].enemytype==rids[k] && enemyAvail[25]==2);
  scenarios++;
 }
 puts("PASS exact linked-death suppression: super-arcade suppresses628/value30000 before constructor/RNG, preserves25/50/75 and separate25+25 carrier rewards");
}
int main(void)
{
 test_collection();test_full_effect_pool();test_setup_bounds();test_linked_pool();test_lifecycle();test_draw_boundaries();test_moving_and_mixed();test_difficulty();test_spawn_and_movement();test_modes();test_arcade_drop_suppression();
 printf("RESULT {\"status\":\"PASS\",\"scenarios\":%u,\"checks\":%u,\"evidence_kind\":\"source-unit-only\",\"gameplay_runs\":0}\n",scenarios,checks);return 0;
}
