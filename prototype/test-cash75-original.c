#include "unit.h"
/* Only record fields read by the selected exact source blocks are materialized. */
struct {JE_integer value; JE_byte explosiontype;} enemyDat[1000];
struct JE_SingleEnemyType enemy[100];
JE_byte enemyAvail[100],soundQueue[8],shotMultiPos[16],shotAvail[100];
Player player[2];
Explosion explosions[MAX_EXPLOSIONS];
JE_word tempW,enemyKilled;
int b,cubeMax,superArcadeMode,superArcadePowerUp,playerNum=1,difficultyLevel;
bool galagaMode,twoPlayerLinked,isNetworkGame,twoPlayerMode,onePlayerAction,superTyrian;
int mouseX,mouseY;
char *miscTextB[4],*miscText[46];
enum {SA_NONE=0,FRONT_WEAPON=0,REAR_WEAPON=1,SHOT_MISC=4,S_ITEM=18,S_POWERUP=29,V_DATA_CUBE=39};
typedef enum {ENTITY_NORMAL,ENTITY_BLEND,ENTITY_SHADOW} EntityDrawStyle;
typedef enum {ENTITY_TILE,ENTITY_QUAD} EntityDrawLayout;
static void unexpected(void) {fputs("Unselected branch called a stub\n",stderr);abort();}
const char *JE_getName(int i) {(void)i;unexpected();return "";}
void JE_drawTextWindow(const char *p) {(void)p;unexpected();}
bool power_up_weapon(Player *p,uint w) {(void)p;(void)w;unexpected();return false;}
uint player_shot_create(int a,int c,int d,int e,int f,int g,int h,int i)
{(void)a;(void)c;(void)d;(void)e;(void)f;(void)g;(void)h;(void)i;unexpected();return 0;}
uint mt_rand(void) {unexpected();return 0;}
#include "super_specials.inc"
#include "event_fixture.inc"
struct JE_EventRecType eventRec[1];
int eventLoc=1;
static void apply_event(const struct JE_EventRecType *record)
{
 int temp;
 eventRec[0]=*record;
 switch(eventRec[0].eventtype) {
#include "event33.inc"
#include "event45.inc"
 default:unexpected();
 }
}
#include "setup_explosion.inc"
static void assign_reward(struct JE_SingleEnemyType *enemy, Uint16 eDatI)
{
#include "reward.inc"
}
/* These wrappers supply only original caller locals around byte-exact blocks. */
static void collect_scoreitem(int z,JE_byte playerNum_)
{
 Player *this_player=&player[playerNum_-1];
 int evalue=enemy[z].evalue,enemy_screen_x=enemy[z].ex+enemy[z].mapoffset;
 char tempStr[256];
 if(false) {}
#include "scoreitem.inc"
}
static void drop_then_release(int temp2)
{
 int temp=enemy[temp2].linknum,temp3=temp;
 b=temp2;
#include "drop_release.inc"
}
static int allocation_calls,factory_calls,last_offset,last_free,last_carrier_avail,last_return,carrier,last_type;
Sint16 __real_JE_newEnemy(int,Uint16,Sint16);
Sint16 __wrap_JE_newEnemy(int offset,Uint16 type,Sint16 shape)
{
 allocation_calls++;last_offset=offset;last_free=0;last_type=type;
 last_carrier_avail=enemyAvail[carrier];
 for(int i=offset;i<offset+25;i++)last_free+=enemyAvail[i]==1;
 last_return=__real_JE_newEnemy(offset,type,shape);
 return (Sint16)last_return;
}
uint JE_makeEnemy(struct JE_SingleEnemyType *e,Uint16 type,Sint16 shape)
{
 /* Labeled constructor stub for positive controls ONLY. Reward is exact source.
    Full-pool and suppressed-drop proofs never reach this stub. */
 factory_calls++;assert(type==391 || type==393 || type==628);assert(shape==0);
 memset(e,0,sizeof(*e));e->enemytype=type;assign_reward(e,type);
 return 2;
}
SDL_Surface *VGAScreen;
static Uint8 bank_byte;
Sprite2_array explosionSpriteSheet={1,&bank_byte};
bool explosionTransparent;
JE_integer explosionFollowAmountX,explosionFollowAmountY,explodeMove;
struct Draw {int x,y,id,style,layout,ttl,sprite,deltaY,fixed,follow;};
static struct Draw draws[256];
static bool gates25[256],gates75[256];
static int draw_count,gate_count25,gate_count75;
void render_mirror_coin25_value_begin(bool eligible)
{assert(gate_count25<(int)COUNTOF(gates25));gates25[gate_count25++]=eligible;}
void render_mirror_coin75_value_begin(bool eligible)
{assert(gate_count75<(int)COUNTOF(gates75));gates75[gate_count75++]=eligible;}
void draw_entity_sprite2(SDL_Surface *s,int x,int y,Sprite2_array bank,unsigned id,EntityDrawStyle style,EntityDrawLayout layout)
{
 assert(s==VGAScreen && bank.data==explosionSpriteSheet.data && layout==ENTITY_TILE);
 assert(draw_count<(int)COUNTOF(draws));
 Explosion *e=NULL;
 for(int i=0;i<MAX_EXPLOSIONS;i++)
  if(explosions[i].ttl && explosions[i].x==x && explosions[i].y==y && (unsigned)explosions[i].sprite+1==id) {assert(e==NULL);e=&explosions[i];}
 assert(e!=NULL);
 draws[draw_count++]=(struct Draw){x,y,(int)id,style,layout,e->ttl,e->sprite,e->deltaY,e->fixedPosition,e->followPlayer};
}
static void draw_original(void)
{
#include "draw_original.inc"
}
static void draw_candidate(void)
{
#include "draw_candidate.inc"
}
static unsigned checks,scenarios;
#define CHECK(x) do {++checks;if(!(x)){fprintf(stderr,"FAIL %s:%d: %s\n",__FILE__,__LINE__,#x);exit(1);}} while(0)
static void reset(void)
{
 memset(enemy,0,sizeof(enemy));memset(enemyAvail,1,sizeof(enemyAvail));
 memset(enemyDat,0,sizeof(enemyDat));memset(player,0,sizeof(player));
 memset(explosions,0,sizeof(explosions));memset(soundQueue,0,sizeof(soundQueue));
 memset(draws,0,sizeof(draws));memset(gates25,0,sizeof(gates25));memset(gates75,0,sizeof(gates75));
 b=cubeMax=superArcadeMode=superArcadePowerUp=enemyKilled=0;
 galagaMode=twoPlayerLinked=isNetworkGame=twoPlayerMode=onePlayerAction=superTyrian=false;
 allocation_calls=factory_calls=draw_count=gate_count25=gate_count75=0;
 last_offset=last_free=last_carrier_avail=last_return=last_type=-1;
 playerNum=1;explodeMove=3;explosionFollowAmountX=5;explosionFollowAmountY=-2;
 explosionTransparent=false;player[0].cash=1000;player[1].cash=2000;difficultyLevel=DIFFICULTY_NORMAL;
#include "record_fixture.inc"
}
static void seed_coin(int rid,int y)
{
 enemyAvail[20]=2;enemy[20].enemytype=(JE_word)rid;assign_reward(&enemy[20],(Uint16)rid);
 enemy[20].scoreitem=true;enemy[20].ex=78;enemy[20].mapoffset=20;enemy[20].ey=(JE_integer)y;
}
static int sprite_for(int rid) {return rid==391?184:222;}
static void expect_coin_popup(int rid,int y)
{
 CHECK(explosions[0].ttl==8 && explosions[0].sprite==sprite_for(rid));
 CHECK(explosions[0].x==98 && explosions[0].y==y);
 CHECK(explosions[0].fixedPosition && !explosions[0].followPlayer && explosions[0].deltaY==0);
 for(int i=1;i<MAX_EXPLOSIONS;i++)CHECK(explosions[i].ttl==0);
}
static void test_collection(void)
{
 for(int family=0;family<2;family++)for(int linked=0;linked<2;linked++)for(int who=1;who<=2;who++)
 {
  int rid=family?393:391,value=family?75:25,share=value/2;
  reset();twoPlayerLinked=linked;seed_coin(rid,150);collect_scoreitem(20,(JE_byte)who);
  CHECK(player[0].cash==1000UL+(linked?share:(who==1?value:0)));
  CHECK(player[1].cash==2000UL+(linked?share:(who==2?value:0)));
  CHECK(enemyAvail[20]==1 && soundQueue[7]==S_ITEM);expect_coin_popup(rid,150);scenarios++;
 }
 puts("PASS Normal collection both collectors: 75 or linked37+37; preserved25 or linked12+12; item sound, removal, fixed type38/type36 setup");
}
static void fill_effects(void)
{
 for(int i=0;i<MAX_EXPLOSIONS;i++)
  explosions[i]=(Explosion){.ttl=(JE_byte)(1+i%8),.x=(JE_integer)i,.y=33,.sprite=222,.fixedPosition=true,.followPlayer=false,.deltaY=0};
}
static void test_full_effect_pool(void)
{
 for(int linked=0;linked<2;linked++)
 {
  reset();fill_effects();Explosion before[MAX_EXPLOSIONS];memcpy(before,explosions,sizeof(before));
  JE_setupExplosion(98,150,0,38,true,false);CHECK(memcmp(before,explosions,sizeof(before))==0);
  twoPlayerLinked=linked;seed_coin(393,150);collect_scoreitem(20,1);
  CHECK(memcmp(before,explosions,sizeof(before))==0);
  CHECK(enemyAvail[20]==1 && soundQueue[7]==S_ITEM);
  CHECK(player[0].cash==1000+(linked?37:75) && player[1].cash==2000+(linked?37:0));scenarios++;
 }
 puts("PASS all200 effect slots occupied: no allocation/overwrite; 75 normal/linked cash and removal retained");
}
static void test_setup_bounds(void)
{
 const int ys[]={-17,-16,-15,0,186,187,188,189,190,191};
 for(size_t k=0;k<COUNTOF(ys);k++)
 {
  int y=ys[k];bool admitted=y>-16 && y<190;reset();
  JE_setupExplosion(98,(JE_integer)y,0,38,true,false);
  if(admitted)expect_coin_popup(393,y);else {Explosion empty[MAX_EXPLOSIONS]={0};CHECK(memcmp(empty,explosions,sizeof(empty))==0);}
  reset();seed_coin(393,y);collect_scoreitem(20,1);
  CHECK(enemyAvail[20]==1 && player[0].cash==1075);CHECK((explosions[0].ttl!=0)==admitted);scenarios++;
 }
 puts("PASS setup y limits: -17/-16/190/191 reject; -15/0/186/187/188/189 admit; rejected setup preserves collection/removal");
}
static void test_drop_pool(void)
{
 for(carrier=0;carrier<25;carrier++)
 {
  reset();for(int i=0;i<25;i++)enemyAvail[i]=(i%3==0)?2:0;enemyAvail[carrier]=0;
  enemy[carrier].enemytype=12;enemy[carrier].enemydie=393;enemy[carrier].linknum=10;
  enemy[carrier].evalue=15;enemy[carrier].ex=120;enemy[carrier].ey=59;
  JE_byte before[100];memcpy(before,enemyAvail,sizeof(before));
  drop_then_release(carrier);
  CHECK(allocation_calls==1 && factory_calls==0 && last_offset==0 && last_type==393 && last_free==0);
  CHECK(last_carrier_avail==0 && last_return==0 && enemyAvail[carrier]==1);
  CHECK(enemyKilled==1 && player[0].cash==1015 && player[1].cash==2000 && b==carrier);
  for(int i=0;i<100;i++)if(i!=carrier)CHECK(enemyAvail[i]==before[i]);
  for(int i=0;i<100;i++)CHECK(enemy[i].enemytype!=393);
  /* Positive control: original allocator, labeled stub constructor. */
  CHECK(JE_newEnemy(0,393,0)==carrier+1);CHECK(factory_calls==1);scenarios++;
 }
 puts("PASS full sky pool0..24 at all25 carrier positions: failure before release, no constructor, separate15 reward; post-release allocation control");
}
static void test_lifecycle(void)
{
 for(int family=0;family<2;family++)for(int style=0;style<2;style++)
 {
  int rid=family?393:391;
  Explosion history[12][MAX_EXPLOSIONS];struct Draw expected[8];
  reset();explosionTransparent=style;JE_setupExplosion(98,150,0,enemyDat[rid].explosiontype,true,false);
  for(int frame=0;frame<12;frame++)
  {
   int n=draw_count;draw_original();memcpy(history[frame],explosions,sizeof(explosions));
   CHECK(draw_count==n+(frame<8));CHECK(explosions[0].ttl==(frame<8?7-frame:0));
   if(frame<8){struct Draw *d=&draws[frame];CHECK(d->id==sprite_for(rid)+1 && d->ttl==8-frame && d->sprite==sprite_for(rid));CHECK(d->x==98 && d->y==150 && d->fixed && !d->follow && d->deltaY==0 && d->style==style);}
  }
  CHECK(draw_count==8 && gate_count25==0 && gate_count75==0);memcpy(expected,draws,sizeof(expected));
  reset();explosionTransparent=style;JE_setupExplosion(98,150,0,enemyDat[rid].explosiontype,true,false);
  for(int frame=0;frame<12;frame++){draw_candidate();CHECK(memcmp(history[frame],explosions,sizeof(explosions))==0);CHECK(gate_count25==(frame<8?frame+1:8) && gate_count75==gate_count25);}
  CHECK(draw_count==8 && memcmp(expected,draws,sizeof(expected))==0);
  for(int i=0;i<8;i++){CHECK(gates25[i]==!family);CHECK(gates75[i]==!!family);}
  scenarios++;
 }
 puts("PASS fixed223 and preserved185 NORMAL/BLEND: exactly8 original indexed draws TTL8..1 then4 clear loops; all200 Explosion bytes and call parameters match");
}
static void test_draw_boundaries(void)
{
 const int ys[]={-15,186,187,188,189};
 for(size_t k=0;k<COUNTOF(ys);k++)for(int style=0;style<2;style++)
 {
  Explosion baseline[MAX_EXPLOSIONS];struct Draw expected[256];int n;
  reset();explosionTransparent=style;JE_setupExplosion(98,(JE_integer)ys[k],0,38,true,false);draw_original();
  n=draw_count;memcpy(expected,draws,sizeof(expected));memcpy(baseline,explosions,sizeof(baseline));
  CHECK(n==(ys[k]<=186));CHECK(explosions[0].ttl==(ys[k]<=186?7:0));
  reset();explosionTransparent=style;JE_setupExplosion(98,(JE_integer)ys[k],0,38,true,false);draw_candidate();
  CHECK(memcmp(baseline,explosions,sizeof(baseline))==0 && memcmp(expected,draws,sizeof(expected))==0);
  CHECK(gate_count25==n && gate_count75==n && draw_count==n);scenarios++;
 }
 puts("PASS y186 draws; y187/188/189 cancel before both hooks; original/candidate byte and draw-call projection equal");
}
static void test_moving_and_mixed(void)
{
 for(int kind=0;kind<2;kind++)for(int style=0;style<2;style++)
 {
  int type=kind?49:45,ttl=kind?14:20;
  Explosion history[24][MAX_EXPLOSIONS];struct Draw expected[256];
  reset();explosionTransparent=style;JE_setupExplosion(98,40,0,(JE_integer)type,false,false);
  for(int f=0;f<24;f++){draw_original();memcpy(history[f],explosions,sizeof(explosions));}
  CHECK(draw_count==ttl);memcpy(expected,draws,sizeof(expected));
  reset();explosionTransparent=style;JE_setupExplosion(98,40,0,(JE_integer)type,false,false);
  for(int f=0;f<24;f++){draw_candidate();CHECK(memcmp(history[f],explosions,sizeof(explosions))==0);}
  CHECK(draw_count==ttl && gate_count25==ttl && gate_count75==ttl && memcmp(expected,draws,sizeof(expected))==0);
  int hits=0;
  for(int n=0;n<ttl;n++){CHECK(!gates25[n] && !gates75[n]);if(draws[n].id==223){hits++;CHECK(!draws[n].fixed && draws[n].sprite==222 && draws[n].ttl<=8);}}
  CHECK(hits==1);scenarios++;
 }
 for(int reverse=0;reverse<2;reverse++)for(int style=0;style<2;style++)
 {
  Explosion history[10][MAX_EXPLOSIONS];struct Draw expected[256];
  for(int candidate=0;candidate<2;candidate++)
  {
   reset();explosionTransparent=style;
   JE_setupExplosion(80,70,0,reverse?38:36,true,false);JE_setupExplosion(100,90,0,reverse?36:38,true,false);
   for(int f=0;f<10;f++)
   {
    if(candidate){draw_candidate();CHECK(memcmp(history[f],explosions,sizeof(explosions))==0);}
    else {draw_original();memcpy(history[f],explosions,sizeof(explosions));}
   }
   CHECK(draw_count==16);
   if(candidate){CHECK(memcmp(expected,draws,sizeof(expected))==0);CHECK(gate_count25==16 && gate_count75==16);for(int i=0;i<16;i++){CHECK(gates25[i]==(draws[i].id==185));CHECK(gates75[i]==(draws[i].id==223));}}
   else memcpy(expected,draws,sizeof(expected));
  }
  scenarios++;
 }
 puts("PASS moving types45/49 each traverse223 exactly once with eligibility false; mixed185/223 both orders and styles keep independent call-site gates and original states");
}
static void test_difficulty(void)
{
 const int values[]={-32768,-4,-1,0,1,2,25,75,1250,1251,2499,2500,2501,4000,4001,5000,5001,6666,6667,8888,8889,9999,10000,10001,30000,32767};
 /* Independent exact rational test oracle for the source's binary-exact factors. */
 const int numer[]={6,6,8,8,9,12,16,20,32,32,64,64};
 const int expected75[]={56,56,75,75,84,112,150,187,300,300,600,600};
 const int expected25[]={18,18,25,25,28,37,50,62,100,100,200,200};
 for(int difficulty=-2;difficulty<=11;difficulty++)for(size_t k=0;k<COUNTOF(values);k++)
 {
  reset();difficultyLevel=difficulty;int v=values[k];enemyDat[393].value=(JE_integer)v;
  int expected=v;
  if(v>1 && v<10000){expected=difficulty>=-1 && difficulty<=10?v*numer[difficulty+1]/8:0;if(expected>10000)expected=10000;}
  assign_reward(&enemy[0],393);CHECK(enemy[0].evalue==expected);scenarios++;
 }
 for(int difficulty=-1;difficulty<=10;difficulty++)for(int family=0;family<2;family++)for(int linked=0;linked<2;linked++)
 {
  int rid=family?393:391;
  reset();difficultyLevel=difficulty;twoPlayerLinked=linked;seed_coin(rid,150);
  int expected=family?expected75[difficulty+1]:expected25[difficulty+1];
  CHECK(enemy[20].evalue==expected);collect_scoreitem(20,1);
  CHECK(player[0].cash==1000UL+(linked?expected/2:expected));CHECK(player[1].cash==2000UL+(linked?expected/2:0));
  CHECK(enemyDat[rid].explosiontype==(family?38:36));expect_coin_popup(rid,150);scenarios++;
 }
 puts("PASS exact JE_makeEnemy reward block: all difficulty branches -1/Wimp..10, invalid-switch defaults, 26 threshold/cap values; 75=56/75/84/112/150/187/300/600, 25 preserved; popup choice stays type38/type36");
}
static void test_modes(void)
{
 static Uint8 lives=3;
 for(int st=0;st<2;st++)for(int two=0;two<2;two++)for(int action=0;action<2;action++)for(int arcade=0;arcade<2;arcade++)
 {
  reset();superTyrian=st;twoPlayerMode=two;onePlayerAction=action;superArcadeMode=arcade;player[0].lives=&lives;
  enemyAvail[1]=enemyAvail[2]=0;enemy[1].linknum=10;enemy[2].linknum=5;
  seed_coin(393,100);CHECK(enemy[20].linknum==0);
  struct JE_SingleEnemyType coin=enemy[20];JE_byte before[100];memcpy(before,enemyAvail,sizeof(before));
  int expected=(!st && (two || action))?628:393;
  for(size_t k=0;k<COUNTOF(fixture_events);k++)
  {
   const struct JE_EventRecType *ev=&fixture_events[k];apply_event(ev);
   int slot=ev->eventdat4==10?1:2;
   CHECK(enemy[slot].enemydie==(ev->eventtype==33?393:expected));
   CHECK(memcmp(&coin,&enemy[20],sizeof(coin))==0 && memcmp(before,enemyAvail,sizeof(before))==0);
   CHECK(memcmp(&eventRec[0],ev,sizeof(*ev))==0);CHECK(player[0].cash==1000 && player[1].cash==2000);
   if(k==0)CHECK(enemy[2].enemydie==0); /*240 only targets link10*/
   if(k==2)CHECK(enemy[1].enemydie==393); /*340 targets link5*/
  }
  CHECK(enemy[1].enemydie==expected && enemy[2].enemydie==expected);scenarios++;
 }
 puts("PASS exact event33/event45: 240 index29 link10; 340 indices43/44 link5; 440 indices60/61 link10; 16 mode combinations, SuperTyrian exception, unchanged existing393/link0 coin");
 for(int arcade=0;arcade<2;arcade++)for(int family=0;family<2;family++)
 {
  reset();carrier=10;superArcadeMode=arcade;enemyAvail[carrier]=0;enemy[carrier].enemytype=12;
  int type=family?628:393;enemy[carrier].enemydie=(JE_word)type;enemy[carrier].evalue=15;enemy[carrier].ex=120;enemy[carrier].ey=59;
  drop_then_release(carrier);bool suppressed=arcade && family;
  CHECK(allocation_calls==!suppressed && factory_calls==!suppressed);
  CHECK(enemyAvail[carrier]==1 && enemyKilled==1 && player[0].cash==1015);
  if(!suppressed){CHECK(last_offset==0 && last_free==24 && last_carrier_avail==0 && last_type==type && last_return==1);CHECK(enemy[0].enemytype==type && enemy[0].scoreitem && enemy[0].ex==120 && enemy[0].ey==59);}
  else {CHECK(last_return==-1);CHECK(enemyAvail[0]==1);}
  scenarios++;
 }
 puts("PASS original death branch: super-arcade suppresses628/value30000 before allocator, keeps393/value75 drop; carrier release and15 reward retained");
}
int main(void)
{
 test_collection();test_full_effect_pool();test_setup_bounds();test_drop_pool();test_lifecycle();test_draw_boundaries();test_moving_and_mixed();test_difficulty();test_modes();
 printf("RESULT {\"status\":\"PASS\",\"scenarios\":%u,\"checks\":%u,\"evidence_kind\":\"source-unit-only\",\"gameplay_runs\":0}\n",scenarios,checks);
 return 0;
}
