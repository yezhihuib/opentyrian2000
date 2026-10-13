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

struct JE_EventRecType eventRec[1];
int eventLoc=1,newPL[10];
int mapX=1,mapX3=1,backMove=1,backMove2=2,backMove3=3;
bool background3x1,background3x1b,smallEnemyAdjust;
#include "spawn_enemy.inc"
static void apply_event(const struct JE_EventRecType *record)
{
 int temp;eventRec[0]=*record;
 switch(eventRec[0].eventtype) {
#include "event7.inc"
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
static int allocation_calls,factory_calls,release_calls,carrier_count;
static bool observe_pair,mode_control;
static Uint8 default_lives=3;
Sint16 __real_JE_newEnemy(int,Uint16,Sint16);
uint __real_JE_makeEnemy(struct JE_SingleEnemyType *,Uint16,Sint16);
uint __wrap_JE_makeEnemy(struct JE_SingleEnemyType *e,Uint16 type,Sint16 shape)
{factory_calls++;return __real_JE_makeEnemy(e,type,shape);}
Sint16 __wrap_JE_newEnemy(int offset,Uint16 type,Sint16 shape)
{
 if(!observe_pair)return __real_JE_newEnemy(offset,type,shape);
 CHECK(allocation_calls<carrier_count);int n=allocation_calls++;
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
 CHECK(release_calls<carrier_count);int n=release_calls++;
 struct Carrier *c=&carriers[n];struct Allocation *a=&allocations[n];
 CHECK(ground==enemy[c->slot].enemyground && count==enemy[c->slot].explonum);
 CHECK(x==c->x+enemy[c->slot].mapoffset && y==c->y);
 CHECK(enemy[c->slot].enemytype==c->type && enemyAvail[c->slot]==1 && !c->released);
 CHECK(allocation_calls==n+1 && enemyKilled==n+1);
 c->released=true;c->cash_at_release=player[galagaMode?0:playerNum-1].cash;
 if(a->result){int slot=a->result-1;CHECK(slot!=c->slot && enemy[slot].enemytype==394 && enemyAvail[slot]==2);CHECK(enemy[slot].ex==c->x && enemy[slot].ey==c->y);}
}
static bool globalFlags[256];
static void linked_death(int hit)
{
 int temp,temp2,temp3;b=hit;
#include "link_normalization.inc"
#include "linked_death.inc"
}
struct BodyDraw {int slot,id,x,y,cycle,filter;};
static struct BodyDraw body_draws[256];static int body_count,tempMapXOfs=11,tempBackMove=1;
static void blit_enemy(SDL_Surface *surface,int i,int dx,int dy,int part)
{
 CHECK(surface==VGAScreen && body_count<(int)COUNTOF(body_draws));
 body_draws[body_count++]=(struct BodyDraw){i,enemy[i].egr[enemy[i].enemycycle-1]+part,enemy[i].ex+tempMapXOfs+dx,enemy[i].ey+dy,enemy[i].enemycycle,enemy[i].filter};
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
static bool gates25[256],gates75[256],gates50[256],gates100[256];
static int draw_count,gate_count25,gate_count75,gate_count50,gate_count100;
void render_mirror_coin25_value_begin(bool e){CHECK(gate_count25<(int)COUNTOF(gates25));gates25[gate_count25++]=e;}
void render_mirror_coin75_value_begin(bool e){CHECK(gate_count75<(int)COUNTOF(gates75));gates75[gate_count75++]=e;}
void render_mirror_coin50_value_begin(bool e){CHECK(gate_count50<(int)COUNTOF(gates50));gates50[gate_count50++]=e;}
void render_mirror_gem100_value_begin(bool e){CHECK(gate_count100<(int)COUNTOF(gates100));gates100[gate_count100++]=e;}
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
 memset(draws,0,sizeof(draws));memset(gates25,0,sizeof(gates25));memset(gates75,0,sizeof(gates75));memset(gates50,0,sizeof(gates50));memset(gates100,0,sizeof(gates100));
 memset(carriers,0,sizeof(carriers));memset(allocations,0,sizeof(allocations));memset(body_draws,0,sizeof(body_draws));
 b=cubeMax=superArcadeMode=superArcadePowerUp=enemyKilled=totalEnemy=0;
 galagaMode=twoPlayerLinked=isNetworkGame=twoPlayerMode=onePlayerAction=superTyrian=observe_pair=mode_control=false;
 allocation_calls=factory_calls=release_calls=body_count=draw_count=gate_count25=gate_count75=gate_count50=gate_count100=carrier_count=0;rng_calls=0;
 playerNum=1;explodeMove=3;explosionFollowAmountX=5;explosionFollowAmountY=-2;tempMapXOfs=11;tempBackMove=3;
 explosionTransparent=false;player[0].lives=player[1].lives=&default_lives;player[0].cash=1000;player[1].cash=2000;difficultyLevel=DIFFICULTY_NORMAL;
#include "record_fixture.inc"
}
static void seed_coin(int rid,int y)
{
 enemyAvail[20]=(JE_byte)JE_makeEnemy(&enemy[20],(Uint16)rid,0);
 enemy[20].ex=78;enemy[20].mapoffset=20;enemy[20].ey=(JE_integer)y;
}
static int sprite_for(int rid){return rid==391?184:rid==392?203:rid==393?222:168;}
static void set509(int episode)
{
 if(episode==0){
#include "record509_shared.inc"
 }else if(episode==4){
#include "record509_ep4.inc"
 }else{
#include "record509_ep5.inc"
 }
}
static void expect_popup(int rid,int y)
{
 CHECK(explosions[0].ttl==8 && explosions[0].sprite==sprite_for(rid));
 CHECK(explosions[0].x==98 && explosions[0].y==y && explosions[0].fixedPosition && !explosions[0].followPlayer && explosions[0].deltaY==0);
 for(int i=1;i<MAX_EXPLOSIONS;i++)CHECK(explosions[i].ttl==0);
}
static void check_gates(int count)
{
 CHECK(gate_count25==count && gate_count75==count && gate_count50==count && gate_count100==count);
 for(int i=0;i<count;i++){
  bool fixed=draws[i].fixed && !draws[i].follow && draws[i].deltaY==0 && draws[i].ttl<=8;
  CHECK(gates25[i]==(fixed && draws[i].id==185));CHECK(gates50[i]==(fixed && draws[i].id==204));
  CHECK(gates75[i]==(fixed && draws[i].id==223));CHECK(gates100[i]==(fixed && draws[i].id==169));
 }
}
static void test_collection(void)
{
 const int ids[]={391,392,393,394,509},episodes[]={0,4,5};
 for(size_t r=0;r<COUNTOF(ids);r++)for(size_t ep=0;ep<COUNTOF(episodes);ep++)for(int linked=0;linked<2;linked++)for(int who=1;who<=2;who++)
 {
  reset();set509(episodes[ep]);int rid=ids[r],value=enemyDat[rid].value;twoPlayerLinked=linked;seed_coin(rid,150);collect_scoreitem(20,(JE_byte)who);
  CHECK(player[0].cash==1000UL+(linked?value/2:(who==1?value:0)));CHECK(player[1].cash==2000UL+(linked?value/2:(who==2?value:0)));
  CHECK(enemyAvail[20]==1 && soundQueue[7]==S_ITEM);expect_popup(rid,150);
  draw_candidate();check_gates(1);CHECK(draws[0].id==sprite_for(rid)+1);
  if(rid==509){CHECK(value==(episodes[ep]==0?250:100));}
  scenarios++;
 }
 const int dxs[]={-13,-12,-11,0,11,12,13},dys[]={-15,-14,-13,0,13,14,15};
 for(size_t x=0;x<COUNTOF(dxs);x++)for(size_t y=0;y<COUNTOF(dys);y++)
 {
  reset();seed_coin(394,150);player[0].x=98+dxs[x];player[0].y=150+dys[y];bool hit=abs(dxs[x])<12 && abs(dys[y])<14;collect_near(1);
  CHECK(enemyAvail[20]==(hit?1:2) && player[0].cash==1000UL+(hit?100:0));CHECK(soundQueue[7]==(hit?S_ITEM:0) && explosions[0].ttl==(hit?8:0));scenarios++;
 }
 puts("PASS collection394 and509 all source variants; original509 nominal250/display100 mismatch; strict dx12/dy14 boundaries and separate linked halves");
}
static void test_effect_bounds_pool(void)
{
 const int ys[]={-17,-16,-15,0,186,187,188,189,190,191};
 for(size_t k=0;k<COUNTOF(ys);k++)for(int style=0;style<2;style++)
 {
  int y=ys[k];bool admitted=y>-16 && y<190;reset();explosionTransparent=style;seed_coin(394,y);collect_scoreitem(20,1);
  CHECK(enemyAvail[20]==1 && player[0].cash==1100);CHECK((explosions[0].ttl!=0)==admitted);
  if(admitted)expect_popup(394,y);
  Explosion initial[MAX_EXPLOSIONS],reference[MAX_EXPLOSIONS];struct Draw expected[256];memcpy(initial,explosions,sizeof(initial));
  draw_original();memcpy(reference,explosions,sizeof(reference));memcpy(expected,draws,sizeof(expected));int count=draw_count;
  CHECK(count==(admitted && y<=186));memcpy(explosions,initial,sizeof(initial));memset(draws,0,sizeof(draws));draw_count=0;draw_candidate();
  CHECK(memcmp(reference,explosions,sizeof(reference))==0 && memcmp(expected,draws,sizeof(expected))==0 && draw_count==count);check_gates(count);scenarios++;
 }
 for(int linked=0;linked<2;linked++)
 {
  reset();twoPlayerLinked=linked;for(int i=0;i<MAX_EXPLOSIONS;i++)explosions[i]=(Explosion){.ttl=(JE_byte)(1+i%8),.x=(JE_integer)i,.y=33,.sprite=168,.fixedPosition=true};
  Explosion before[MAX_EXPLOSIONS];memcpy(before,explosions,sizeof(before));JE_setupExplosion(98,150,0,39,true,false);CHECK(memcmp(before,explosions,sizeof(before))==0);
  seed_coin(394,150);collect_scoreitem(20,1);CHECK(memcmp(before,explosions,sizeof(before))==0 && enemyAvail[20]==1 && soundQueue[7]==S_ITEM);
  CHECK(player[0].cash==1000UL+(linked?50:100) && player[1].cash==2000UL+(linked?50:0));scenarios++;
 }
 for(int kind=0;kind<3;kind++)
 {
  reset();JE_setupExplosion(98,40,0,39,true,false);if(kind==0)explosions[0].followPlayer=true;if(kind==1)explosions[0].deltaY=1;if(kind==2)explosions[0].ttl=9;
  draw_candidate();CHECK(draw_count==1 && !gates100[0]);check_gates(1);scenarios++;
 }
 puts("PASS setup y bounds, y187..189 pre-draw cancellation, full200 effect pool preserves collection, follow/deltaY/TTL gate exclusions");
}
static void compare_effects(const int *types,int n,int style,bool fixed)
{
 Explosion history[12][MAX_EXPLOSIONS];struct Draw expected[256];int count=0;
 for(int candidate=0;candidate<2;candidate++)
 {
  reset();explosionTransparent=style;for(int k=0;k<n;k++)JE_setupExplosion((JE_integer)(80+k*20),(JE_integer)(40+k*20),0,(JE_integer)types[k],fixed,false);
  for(int f=0;f<12;f++){
   if(candidate){draw_candidate();CHECK(memcmp(history[f],explosions,sizeof(explosions))==0);}
   else {draw_original();memcpy(history[f],explosions,sizeof(explosions));}
  }
  CHECK(draw_count==n*8);
  if(candidate){CHECK(draw_count==count && memcmp(expected,draws,sizeof(expected))==0);check_gates(count);}
  else {count=draw_count;memcpy(expected,draws,sizeof(expected));CHECK(gate_count25==0 && gate_count50==0 && gate_count75==0 && gate_count100==0);}
 }
 if(fixed){for(int i=0;i<count;i++)CHECK(draws[i].ttl==8-i/n && draws[i].fixed);}
 else {int hit=0;for(int i=0;i<count;i++){CHECK(!gates100[i] && !gates25[i] && !gates50[i] && !gates75[i]);CHECK(draws[i].id==167+i && !draws[i].fixed);if(draws[i].id==169){hit++;CHECK(i==2 && draws[i].ttl==6);}}CHECK(hit==1);}
 scenarios++;
}
static void test_lifecycle_mixed(void)
{
 for(int style=0;style<2;style++)
 {
  const int fixed[]={39},moving[]={35};compare_effects(fixed,1,style,true);compare_effects(moving,1,style,false);
  /* All24 ordered placements exercise original ascending effect-pool draw order. */
  for(int a=36;a<=39;a++)for(int b_=36;b_<=39;b_++)for(int c_=36;c_<=39;c_++)for(int d=36;d<=39;d++)
   if(a!=b_ && a!=c_ && a!=d && b_!=c_ && b_!=d && c_!=d){const int order[]={a,b_,c_,d};compare_effects(order,4,style,true);}
 }
 puts("PASS eight fixed169 draws and four clear steps; moving35 draws167..174 including169 remains classic; all24 mixed25/50/75/100 orders in NORMAL/BLEND; all200 Explosion bytes and draw arguments identical");
}
static void test_difficulty(void)
{
 const int values[]={-32768,-4,-1,0,1,2,25,50,75,100,1250,1251,2499,2500,2501,4000,4001,5000,5001,6666,6667,8888,8889,9999,10000,10001,30000,32767};
 const int numer[]={6,6,8,8,9,12,16,20,32,32,64,64};
 const int expected100[]={75,75,100,100,112,150,200,250,400,400,800,800};
 for(int difficulty=-2;difficulty<=11;difficulty++)for(size_t k=0;k<COUNTOF(values);k++)
 {
  reset();difficultyLevel=difficulty;int v=values[k],expected=v;enemyDat[394].value=(JE_integer)v;
  if(v>1 && v<10000){expected=difficulty>=-1 && difficulty<=10?v*numer[difficulty+1]/8:0;if(expected>10000)expected=10000;}
  assign_reward(&enemy[0],394);CHECK(enemy[0].evalue==expected);scenarios++;
 }
 for(int difficulty=-1;difficulty<=10;difficulty++)for(int linked=0;linked<2;linked++)for(int who=1;who<=2;who++)
 {
  reset();difficultyLevel=difficulty;twoPlayerLinked=linked;seed_coin(394,150);int v=expected100[difficulty+1];CHECK(enemy[20].evalue==v);collect_scoreitem(20,(JE_byte)who);
  CHECK(player[0].cash==1000UL+(linked?v/2:(who==1?v:0)) && player[1].cash==2000UL+(linked?v/2:(who==2?v:0)));expect_popup(394,150);
  if(difficulty==-1 && linked)CHECK(v==75 && player[0].cash==1037 && player[1].cash==2037);
  JE_makeEnemy(&enemy[30],30,0);CHECK(enemy[30].evalue==15*numer[difficulty+1]/8);scenarios++;
 }
 puts("PASS difficulty thresholds/cap and100=75/100/112/150/200/250/400/800; linked75 pays37+37; carrier15 scales independently");
}
static void seed_carrier(int slot,int link,int n,bool drops)
{
 enemyAvail[slot]=(JE_byte)JE_makeEnemy(&enemy[slot],30,0);enemy[slot].ex=(JE_integer)(26+n*24);enemy[slot].ey=-7;
 enemy[slot].mapoffset=64;enemy[slot].linknum=(JE_byte)link;enemy[slot].enemydie=drops?394:0;
}
static void test_top_pool(void)
{
 const int pairs[][2]={{50,51},{50,74},{61,62},{73,74}};
 for(size_t p=0;p<COUNTOF(pairs);p++)for(int free_case=0;free_case<3;free_case++)for(int count=1;count<=2;count++)
 {
  reset();for(int i=50;i<75;i++){enemyAvail[i]=(i%3==0)?2:0;enemy[i].enemytype=10;enemy[i].linknum=99;}
  int available=free_case==2?3:free_case;for(int i=50,n=0;i<75 && n<available;i++)if(i!=pairs[p][0] && (count==1 || i!=pairs[p][1])){enemyAvail[i]=1;n++;}
  carrier_count=count;for(int n=0;n<count;n++){int slot=pairs[p][n];seed_carrier(slot,182,n,true);carriers[n]=(struct Carrier){slot,30,26+n*24,-7,false,0};}
  int prior_factory=factory_calls;unsigned prior_rng=rng_calls;observe_pair=true;linked_death(pairs[p][0]);observe_pair=false;
  CHECK(allocation_calls==count && release_calls==count && enemyKilled==count && b==pairs[p][0]);int successes=0;
  for(int n=0;n<count;n++)
  {
   struct Allocation *a=&allocations[n];CHECK(carriers[n].released && carriers[n].cash_at_release==1000UL+15*(n+1));
   CHECK(a->offset==50 && a->type==394 && a->rng_after-a->rng_before==(unsigned)(a->result!=0));
   if(a->result){int slot=a->result-1;uint sample=rng_stream[a->rng_before%COUNTOF(rng_stream)];successes++;
    CHECK(a->constructor_x==(int)(130+sample%250-125+1) && a->constructor_y==-12);
    CHECK(enemy[slot].enemytype==394 && enemyAvail[slot]==2 && enemy[slot].scoreitem && enemy[slot].armorleft==255 && enemy[slot].linknum==0);
    CHECK(enemy[slot].sprite2s==&spriteSheet11 && enemy[slot].enemycycle==0 && enemy[slot].egr[0]==32 && enemy[slot].egr[15]==33);
    CHECK(enemy[slot].ex==carriers[n].x && enemy[slot].ey==carriers[n].y);
   }
  }
  CHECK(successes==(available?count:count-1) && factory_calls==prior_factory+successes && rng_calls==prior_rng+(unsigned)successes);
  if(!available){CHECK(allocations[0].result==0);if(count==2)CHECK(allocations[1].result==pairs[p][0]+1 && enemy[pairs[p][0]].ex==50);}
  CHECK(player[0].cash==1000UL+15*count && player[1].cash==2000);
  if(successes){int which=allocations[0].result?0:1,slot=allocations[which].result-1;collect_scoreitem(slot,1);CHECK(player[0].cash==1100UL+15*count && enemyAvail[slot]==1);}
  scenarios++;
 }
 puts("PASS top25 allocation0/1/3 vacancies: full single carrier omits gem; second reuses released first; request before own release, original constructor/RNG before exact ex/ey copy;15 carrier reward separate from100 pickup");
}
static void test_link_sweep(void)
{
 const int links[]={0,40,41,59,60,99,100,101,143,163,182,253,254,255};
 for(size_t h=0;h<COUNTOF(links);h++)for(int other=0;other<256;other++)for(int availability=0;availability<3;availability++)
 {
  reset();int hitlink=links[h],normalized=hitlink?hitlink:255;seed_carrier(50,hitlink,0,false);seed_carrier(10,other,1,false);enemyAvail[10]=(JE_byte)availability;
  bool killed=availability!=1 && (normalized==254 || (normalized!=255 && (normalized==other || normalized-100==other || (other>40 && other/20==normalized/20 && other<=normalized))));
  mode_control=true;linked_death(50);mode_control=false;CHECK(enemyAvail[50]==1 && enemyAvail[10]==(killed?1:availability));
  CHECK(enemyKilled==1+killed && release_calls==1+killed && player[0].cash==1015UL+15*killed && player[1].cash==2000);
  CHECK(allocation_calls==0 && rng_calls==0);scenarios++;
 }
 puts("PASS exact linked sweep including actual182 matches82/180/181/182 but excludes179/183/189; avail0/2 eligible, avail1 skipped; lower/equal20 groups,254/all and normalized0/255 self-only controls; earlier actors not assumed absent");
}
/* Original ascending avail0 scan and all source predicates are included unchanged.
   This observer reports first match; it does not execute damage/piercing aftermath. */
static int first_normal_shot_collision(int tempShotX,int tempShotY)
{
 int z=0,temp=0,temp2=0,chain=0,damage=6,tempX2=0,tempY2=0,zinglonDuration=0;
 bool is_special=false;
#include "shot_collision_prefix.inc"
 if(collided)return b;
 } }
 (void)temp2;(void)chain;(void)damage;
 return -1;
}
static void test_first_shot_collision(void)
{
 const int delta[]={-30,-29,-28,-26,-25,-24,-16,-15,-14,-13,-12,0,12,13,14,15,16,24,25,26,28,29,30};
 for(int cycle=0;cycle<=1;cycle++)for(int available=0;available<3;available++)for(size_t x=0;x<COUNTOF(delta);x++)for(size_t y=0;y<COUNTOF(delta);y++)
 {
  reset();enemyAvail[50]=(JE_byte)available;enemy[50].enemycycle=(JE_byte)cycle;enemy[50].ex=(JE_integer)(26+delta[x]);enemy[50].mapoffset=64;
  enemy[50].ey=(JE_integer)(-13+(cycle?6:12)+delta[y]);
  bool hit=available==0 && abs(delta[x])<(cycle?13:25) && abs(delta[y])<(cycle?15:29);
  CHECK(first_normal_shot_collision(90,-13)==(hit?50:-1));scenarios++;
 }
 /* Source-predicted geometry only. Side actor dx12 wins at any lower slot;
    lead31 at y8 is precisely15 from shot's y+6 center and is excluded. */
 const int lower[]={0,24,25,49};
 for(size_t k=0;k<COUNTOF(lower);k++)for(int available=0;available<3;available++)
 {
  reset();seed_carrier(50,182,0,false);enemy[50].enemycycle=1;
  int side=lower[k];seed_carrier(side,181,1,false);enemy[side].ex=38;enemy[side].enemycycle=1;enemyAvail[side]=(JE_byte)available;
  enemyAvail[51]=(JE_byte)JE_makeEnemy(&enemy[51],31,0);enemy[51].ex=26;enemy[51].mapoffset=64;enemy[51].ey=8;enemy[51].enemycycle=1;
  CHECK(first_normal_shot_collision(90,-13)==(available==0?side:50));
  enemyAvail[side]=1;enemyAvail[50]=1;CHECK(first_normal_shot_collision(90,-13)==-1);
  enemy[51].ey=7;CHECK(first_normal_shot_collision(90,-13)==51);scenarios++;
 }
 for(int first=0;first<100;first+=11)
 {
  reset();for(int i=first;i<100;i++){enemyAvail[i]=0;enemy[i].enemycycle=1;enemy[i].ex=26;enemy[i].mapoffset=64;enemy[i].ey=-7;}
  CHECK(first_normal_shot_collision(90,-13)==first);scenarios++;
 }
 puts("PASS original ordinary-shot ascending avail0 first-match predicate; cycle0/1 strict boundaries, lower-slot dx12 side precedence and lead31 exactdy15 exclusion; no weapon aftermath/runtime-presence claim");
}
static void test_body_movement(void)
{
 static const int sequence[]={32,32,33,33,34,34,35,35,36,36,35,35,34,34,33,33};
 reset();seed_coin(394,-7);enemy[20].ex=26;tempMapXOfs=64;
 for(int f=0;f<32;f++){enemy[20].filter=9;move_coin(20);CHECK(body_count==f+1);CHECK(body_draws[f].id==sequence[f%16] && body_draws[f].cycle==f%16+1);
  CHECK(body_draws[f].x==90 && body_draws[f].y==-7+f*4 && body_draws[f].filter==9 && enemy[20].filter==0);CHECK(enemy[20].ey==-3+f*4 && enemyAvail[20]==2);}
 CHECK(rng_calls==1);scenarios++;
 const int xs[]={-40,-39,288,289},ys[]={-14,-13,-12,189,190};
 for(size_t x=0;x<COUNTOF(xs);x++)for(size_t y=0;y<COUNTOF(ys);y++)
 {
  reset();seed_coin(394,ys[y]);enemy[20].ex=(JE_integer)xs[x];enemy[20].filter=9;move_coin(20);bool anim=xs[x]+11>-29 && xs[x]+11<300,draw=anim && ys[y]>-13;
  CHECK(enemy[20].enemycycle==(anim?1:0) && body_count==draw && enemy[20].filter==(anim?0:9));
  CHECK(enemyAvail[20]==(ys[y]==190?1:2) && enemy[20].ey==ys[y]+(ys[y]==190?1:4));scenarios++;
 }
 const int bottom[]={-114,-113,-112,188,189,190};
 for(size_t y=0;y<COUNTOF(bottom);y++)
 {
  reset();seed_coin(394,bottom[y]);move_coin(20);bool removed=bottom[y]+1 < -112 || bottom[y]+1 >190;
  CHECK(enemyAvail[20]==(removed?1:2) && enemy[20].ey==bottom[y]+(removed?1:4));
  if(removed){int n=body_count;move_coin(20);move_coin(20);CHECK(body_count==n);}scenarios++;
 }
 reset();seed_coin(394,-7);int removed_at=-1;for(int f=0;f<53;f++){move_coin(20);if(enemyAvail[20]==1 && removed_at<0)removed_at=f;}
 CHECK(removed_at==50 && body_count==51 && body_draws[50].y==193 && enemy[20].ey==194);scenarios++;
 for(int ep=0;ep<3;ep++){reset();set509(ep==0?0:ep==1?4:5);seed_coin(509,40);move_coin(20);CHECK(body_draws[0].id==(ep==0?95:57) && enemy[20].evalue==(ep==0?250:100));scenarios++;}
 puts("PASS all16 held394 body states twice; original +1 intrinsic/+3 top-background y, advance-before-draw, filter clear and horizontal/top gates; removal before background-y; unchanged509 bodies95/57");
}
static void test_events_modes(void)
{
 for(size_t n=0;n<COUNTOF(fixture_spawns);n++)
 {
  reset();apply_event(&fixture_spawns[n]);int slot=b-1;CHECK(slot==50 && enemyAvail[slot]==0 && enemy[slot].enemytype==30);
  CHECK(enemy[slot].ex==fixture_spawns[n].eventdat2-66 && enemy[slot].ey==-28 && enemy[slot].eyc==0 && enemy[slot].exc==0);
  CHECK(enemy[slot].linknum==fixture_events[n].eventdat4 && enemy[slot].armorleft==6 && enemy[slot].evalue==15 && enemy[slot].size==1);
  CHECK(enemy[slot].egr[0]==89 && enemy[slot].sprite2s==&enemySpriteSheets[0] && rng_calls==0 && factory_calls==1);
  apply_event(&fixture_events[n]);CHECK(enemy[slot].enemydie==394);scenarios++;
 }
 for(int st=0;st<2;st++)for(int two=0;two<2;two++)for(int action=0;action<2;action++)for(int arcade=0;arcade<2;arcade++)
 {
  reset();superTyrian=st;twoPlayerMode=two;onePlayerAction=action;superArcadeMode=arcade;
  for(int i=0;i<3;i++){enemy[50+i].linknum=fixture_events[i].eventdat4;enemyAvail[50+i]=0;}
  enemy[80].linknum=182;enemyAvail[80]=1;seed_coin(394,100);struct JE_SingleEnemyType gem=enemy[20];unsigned prior=rng_calls;
  for(size_t k=0;k<COUNTOF(fixture_events);k++){apply_event(&fixture_events[k]);CHECK(enemy[50+k].enemydie==394 && memcmp(&gem,&enemy[20],sizeof(gem))==0 && rng_calls==prior);}
  CHECK(enemy[80].enemydie==394);struct JE_EventRecType e=fixture_events[0];e.eventtype=19;e.eventdat=0;e.eventdat2=7;apply_event(&e);CHECK(enemy[50].eyc==7 && memcmp(&gem,&enemy[20],sizeof(gem))==0);
  for(int dat=512;dat<=513;dat++){e=fixture_events[0];e.eventdat=(JE_integer)dat;enemy[50].enemydie=0;apply_event(&e);CHECK(enemy[50].enemydie==((st||two||action)?0:dat));}
  e=fixture_events[0];e.eventdat=534;prior=rng_calls;apply_event(&e);int remap=arcade?827:st?828+superTyrianSpecials[rng_stream[prior%COUNTOF(rng_stream)]%4]:534;CHECK(enemy[50].enemydie==remap && rng_calls-prior==(unsigned)(!arcade && st));
  e=fixture_events[0];e.eventtype=45;e.eventdat=628;enemy[50].enemydie=394;apply_event(&e);CHECK(enemy[50].enemydie==(!st&&(two||action)?628:394));scenarios++;
 }
 const int ids[]={391,392,393,394,509,628};
 for(int arcade=0;arcade<2;arcade++)for(size_t k=0;k<COUNTOF(ids);k++)
 {
  reset();superArcadeMode=arcade;seed_carrier(50,182,0,true);enemy[50].enemydie=(JE_word)ids[k];int prior=factory_calls;unsigned rng=rng_calls;mode_control=true;linked_death(50);mode_control=false;
  bool suppressed=arcade && ids[k]==628;CHECK(factory_calls-prior==(suppressed?0:1));CHECK(rng_calls-rng==(unsigned)(suppressed?0:(enemyDat[ids[k]].startxc!=0)+(enemyDat[ids[k]].startyc!=0)));
  CHECK(enemyAvail[50]==1 && enemyKilled==1 && player[0].cash==1015);CHECK(enemyAvail[51]==(suppressed?1:2));if(!suppressed)CHECK(enemy[51].enemytype==ids[k]);scenarios++;
 }
 puts("PASS source events313/320/331 top spawns and316/325/334 assignments;16 mode flag controls, stale matching links and new link0 independence;30000 arcade drop suppression preserves25/50/75/100/509");
}
int main(void)
{
 test_collection();test_effect_bounds_pool();test_lifecycle_mixed();test_difficulty();test_top_pool();test_link_sweep();test_first_shot_collision();test_body_movement();test_events_modes();
 printf("RESULT {\"status\":\"PASS\",\"scenarios\":%u,\"checks\":%u,\"evidence_kind\":\"source-unit-only\",\"gameplay_runs\":0}\n",scenarios,checks);return 0;
}
