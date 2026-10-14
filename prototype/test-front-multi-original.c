/* Finite exact-source Multi creation, movement, cadence and shared-use units. */
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
typedef unsigned uint;typedef uint8_t Uint8,JE_byte;typedef uint16_t JE_word;typedef int16_t JE_integer;typedef int8_t JE_shortint;typedef bool JE_boolean;typedef float JE_real;
#define M_PI 3.14159265358979323846
#define M_PI_2 (M_PI/2)
enum {PORT_NUM=60,WEAP_NUM=1818,MAX_PWEAPON=81,REAR_WEAPON=1};
enum {ENTITY_NORMAL,ENTITY_BLEND,ENTITY_SHADOW};enum {ENTITY_TILE,OPTION_SHAPES};
#include "weapon_type.inc"
#include "port_type.inc"
#include "shot_type.inc"
#include "records.inc"
#include "linkMultiGr.inc"
#include "linkMult2Gr.inc"
#include "linkSonicGr.inc"
#include "linkGunWeapons.inc"
#include "chargeGunWeapons.inc"
static JE_WeaponType weapons[WEAP_NUM+1];static JE_WeaponPortType weaponPort;
static PlayerShotDataType playerShotData[MAX_PWEAPON+1];static JE_byte shotAvail[MAX_PWEAPON],shotMultiPos[11],shotRepeat[11],soundQueue[8];
typedef struct {int delta_x_shot_move,delta_y_shot_move,x,y,weapon_mode;struct {struct {uint id,power;} weapon[2];} items;} Player;
static Player player[2];static int power,background2,shadowYDist=5;static JE_word x,y;static bool twoPlayerLinked,twoPlayerMode,galagaMode,button[4];
typedef struct {int token;} Sprite2_array;static Sprite2_array spriteSheet8={8},spriteSheet12={12};static void *VGAScreen;
typedef struct {int kind,ordinal,phase,slot;unsigned call;PlayerShotDataType shot;} Event;
static Event events[16];static int event_count,last_count,last_slot;static const char *last_result;
static unsigned requests,results,emissions,moves,front_calls,front_members,cadence_ticks,capacity_cases,power_cases,drift_cases,shadow_cases,boundary_cases,reuse_calls,direction_cases;
static unsigned expect_port=2,expect_bay,expect_record=166,expect_player=1;
typedef struct {int x,y,style;unsigned id;} Draw;static Draw draws[4];static unsigned draw_count;
static unsigned game_probe_shot_begin(unsigned p,unsigned bay,unsigned w,unsigned pl,unsigned px,unsigned py){assert(p==expect_port&&bay==expect_bay&&w==expect_record&&pl==expect_player&&px==150&&py==160);event_count=0;events[event_count++]=(Event){.kind=0,.call=++requests};return requests;}
static void game_probe_shot_result(unsigned call,const char*r,int count,int slot){assert(call==requests&&event_count<16&&events[0].kind==0);last_result=r;last_count=count;last_slot=slot;events[event_count++]=(Event){.kind=2,.call=call,.slot=slot};results++;}
static void game_probe_shot_emit(unsigned call,int multi,int phase,int id){assert(call==requests&&event_count<15&&multi==event_count&&id>=0&&id<MAX_PWEAPON);events[event_count++]=(Event){.kind=1,.ordinal=multi,.phase=phase,.slot=id,.call=call,.shot=playerShotData[id]};emissions++;}
static void game_probe_fire(unsigned pl,unsigned p,int bay,int px,int py,unsigned w,int id){assert(pl==expect_player&&p==expect_port&&bay==(int)expect_bay&&w==expect_record&&px==150&&py==160&&id<=MAX_PWEAPON);}
static void game_probe_shot_draw(int id,unsigned raw,int bank,unsigned frame,int px,int py,int style,int w,int h){assert(id<MAX_PWEAPON&&raw==frame&&bank==8&&w==12&&h==14);(void)px;(void)py;(void)style;}
static void draw_entity_sprite2(void*s,int px,int py,Sprite2_array bank,unsigned id,int style,int layout){assert(s==VGAScreen&&bank.token==8&&layout==ENTITY_TILE&&draw_count<4);draws[draw_count++]=(Draw){px,py,style,id};}
static int enemyAvail[100];static struct {int scoreitem,ex,ey;} enemy[100];
#define JE_setupExplosion(...) assert(0)
#define JE_doSP(...) assert(0)
#define blit_sprite_blend(...) assert(0)
static struct {int width,height;} special_shape;
#define sprite(...) (&special_shape)
#include "player_shot_create.inc"
#include "player_shot_move_and_draw.inc"
#include "player_shot_set_direction.inc"
static void cadence(void){Player*this_player=player;int playerNum_=1,temp,b,mx=150,my=160;int*mouseX_=&mx,*mouseY_=&my;
#include "cadence.inc"
}
static void reset(int table,int p){memset(weapons,0,sizeof(weapons));memset(weaponPort,0,sizeof(weaponPort));memset(shotAvail,0,sizeof(shotAvail));memset(playerShotData,0,sizeof(playerShotData));memset(shotMultiPos,0,sizeof(shotMultiPos));memset(shotRepeat,0,sizeof(shotRepeat));memset(soundQueue,0,sizeof(soundQueue));memset(player,0,sizeof(player));memset(button,0,sizeof(button));for(int i=0;i<61;i++)weaponPort[i].poweruse=fixture_power[table][i];for(int i=0;i<11;i++){weapons[166+i]=fixture[table][i];weaponPort[2].op[0][i]=166+i;}for(int i=0;i<16;i++)weapons[reuse_records[i]]=reuse_fixture[table][i];player[0].x=150;player[0].y=160;player[0].weapon_mode=1;player[0].items.weapon[0].id=2;player[0].items.weapon[0].power=p+1;power=999;background2=0;shadowYDist=5;draw_count=0;expect_port=2;expect_record=166+p;expect_bay=0;expect_player=1;twoPlayerLinked=twoPlayerMode=galagaMode=false;}
static int request(int delta_x,int delta_y){return player_shot_create(expect_port,expect_bay,150,160,150-delta_x,160-delta_y,expect_record,expect_player);}
static void inspect(int slot,const JE_WeaponType*w,int phase,int ticks){PlayerShotDataType*s=&playerShotData[slot];assert(s->shotX==150+w->bx[phase]+ticks*w->sx[phase]&&s->shotY==160+w->by[phase]-ticks*w->sy[phase]);assert(s->shotXM==w->sx[phase]&&s->shotYM==-w->sy[phase]&&s->shotYC==0&&s->shotXC==0);assert(s->shotGr==w->sg[phase]&&s->shotAni==0&&s->shotAniMax==1&&shotAvail[slot]==255-ticks);assert(s->shotDmg==w->attack[phase]&&s->shotBlastFilter==w->shipblastfilter&&s->shotTrail==255&&s->chainReaction==0&&s->playerNumber==expect_player&&!s->aimAtEnemy&&!s->shotComplicated);assert(!s->shotDevX&&!s->shotDirX&&!s->shotDevY&&!s->shotDirY&&!s->shotCirSizeX&&!s->shotCirSizeY);}
static void volley_events(const JE_WeaponType*w,int count,int start_phase,const int*slots){assert(event_count==count+2&&events[0].kind==0&&events[count+1].kind==2&&last_count==count);for(int j=0;j<count;j++){int phase=(start_phase+j)%w->max;assert(events[j+1].kind==1&&events[j+1].ordinal==j+1&&events[j+1].phase==phase+1&&events[j+1].slot==slots[j]);inspect(slots[j],w,phase,0);assert(!memcmp(&events[j+1].shot,&playerShotData[slots[j]],sizeof(PlayerShotDataType)));}assert(results==requests);}
static bool step(int slot){bool special=true;int px=0,py=0;JE_integer dmg=0;JE_byte filter=0,chain=99,pl=0;JE_word rw=123,rh=456;draw_count=0;bool ok=player_shot_move_and_draw(slot,&special,&px,&py,&dmg,&filter,&chain,&pl,&rw,&rh);if(ok){PlayerShotDataType*s=&playerShotData[slot];assert(!special&&px==s->shotX&&py==s->shotY&&dmg==s->shotDmg&&filter==s->shotBlastFilter&&!chain&&pl==s->playerNumber&&rw==123&&rh==456);assert(draw_count>=1&&draws[draw_count-1].x==px+1&&draws[draw_count-1].y==py&&draws[draw_count-1].id==s->shotGr&&draws[draw_count-1].style==ENTITY_NORMAL&&s->shotAni==0);}moves++;return ok;}
static void front(void){const int counts[]={1,2,3,3,5,5,3,3,5,5,5},repeats[]={3,3,4,4,5,5,5,5,5,5,5};for(int t=0;t<3;t++)for(int p=0;p<11;p++){reset(t,p);const JE_WeaponType*w=&fixture[t][p];assert(w->multi==counts[p]&&w->max==counts[p]&&w->shotrepeat==repeats[p]);for(int v=0;v<2;v++){int slots[8];for(int j=0;j<w->multi;j++)slots[j]=v*w->multi+j;int before=power;assert(request(0,0)==slots[w->multi-1]&&power==before-40&&!strcmp(last_result,"complete")&&last_slot==slots[w->multi-1]);volley_events(w,w->multi,0,slots);assert(shotMultiPos[0]==w->max&&shotRepeat[0]==w->shotrepeat&&soundQueue[0]==w->sound);for(int j=0;j<w->multi;j++)for(int tick=1;tick<=3;tick++){assert(step(slots[j]));inspect(slots[j],w,j,tick);assert(draw_count==1);}front_calls++;front_members+=w->multi;}}assert(front_calls==66&&front_members==240);}
static void drift(void){const int rows[]={1,3,6,10},deltas[]={-9,-5,-1,0,1,5,9};for(int t=0;t<3;t++)for(unsigned p=0;p<4;p++)for(unsigned d=0;d<7;d++){reset(t,rows[p]);const JE_WeaponType*w=&fixture[t][rows[p]];assert(request(deltas[d],-deltas[d])==w->multi-1);for(int j=0;j<w->multi;j++){inspect(j,w,j,0);assert(step(j));inspect(j,w,j,1);}drift_cases++;}}
static void failures_and_cadence(void){for(int t=0;t<3;t++)for(int p=0;p<11;p++){const JE_WeaponType*w=&fixture[t][p];reset(t,p);unsigned cd=0;for(unsigned tick=0;tick<40;tick++){button[0]=tick<9||tick>=19;memset(shotAvail,0,sizeof(shotAvail));power=999;unsigned before=emissions,req=requests;bool fire=!cd&&button[0];if(cd)cd--;else if(fire)cd=w->shotrepeat;cadence();assert(emissions==before+(fire?w->multi:0)&&requests==req+(unsigned)fire&&shotRepeat[0]==cd&&power==(fire?959:999));cadence_ticks++;}
 reset(t,p);power=39;shotMultiPos[0]=w->max;shotRepeat[0]=2;memset(shotAvail,7,sizeof(shotAvail));PlayerShotDataType pool[82];memcpy(pool,playerShotData,sizeof(pool));unsigned before=emissions;JE_byte sounds[8];memcpy(sounds,soundQueue,sizeof(sounds));assert(request(0,0)==MAX_PWEAPON&&emissions==before&&power==39&&!strcmp(last_result,"power")&&last_count==0&&shotMultiPos[0]==w->max&&shotRepeat[0]==2&&!memcmp(pool,playerShotData,sizeof(pool))&&!memcmp(sounds,soundQueue,sizeof(sounds)));for(int j=0;j<MAX_PWEAPON;j++)assert(shotAvail[j]==7);power_cases++;
 for(int available=0;available<w->multi;available++){reset(t,p);shotMultiPos[0]=w->max;shotRepeat[0]=1;memset(shotAvail,7,sizeof(shotAvail));int slots[8];for(int j=0;j<available;j++){slots[j]=2+j*3;shotAvail[slots[j]]=0;}before=emissions;assert(request(0,0)==MAX_PWEAPON&&power==959&&emissions==before+(unsigned)available&&!strcmp(last_result,"capacity")&&last_slot==MAX_PWEAPON);volley_events(w,available,0,slots);assert(shotMultiPos[0]==(available?available:w->max)&&shotRepeat[0]==(available?w->shotrepeat:1)&&soundQueue[0]==w->sound);for(int j=0;j<MAX_PWEAPON;j++){bool newly=false;for(int k=0;k<available;k++)if(j==slots[k])newly=true;assert(shotAvail[j]==(newly?255:7));}capacity_cases++;}
 /* A successful request after partial failure continues the exact original phase cycle. */
 if(w->multi>1){reset(t,p);memset(shotAvail,1,sizeof(shotAvail));shotAvail[0]=0;assert(request(0,0)==MAX_PWEAPON&&shotMultiPos[0]==1);memset(shotAvail,0,sizeof(shotAvail));int slots[8];for(int j=0;j<w->multi;j++)slots[j]=j;assert(request(0,0)==w->multi-1);volley_events(w,w->multi,1,slots);assert(shotMultiPos[0]==1&&power==919);}
 }}
static void motion_edges(void){for(int t=0;t<3;t++)for(int p=0;p<11;p++){const JE_WeaponType*w=&fixture[t][p];for(int j=0;j<w->multi;j++){
 for(int gate=0;gate<4;gate++){reset(t,p);request(0,0);background2=gate!=0;shadowYDist=(gate==2?190:gate==3?189:165)-(160-w->sy[j]);assert(step(j));bool shadow=gate==1||gate==3;assert(draw_count==(unsigned)(shadow?2:1));if(shadow)assert(draws[0].style==ENTITY_SHADOW&&draws[0].x==draws[1].x&&draws[0].y==draws[1].y+shadowYDist&&draws[0].id==draws[1].id);shadow_cases++;}
 reset(t,p);request(0,0);int ticks=0;while(step(j)){assert(++ticks<90);}assert(!shotAvail[j]&&!draw_count);boundary_cases++;
 const int limits[8][2]={{-34,20},{-35,20},{290,20},{291,20},{20,-15},{20,-16},{20,190},{20,191}};
 for(int edge=0;edge<8;edge++){reset(t,p);request(0,0);playerShotData[j].shotX=limits[edge][0]-w->sx[j];playerShotData[j].shotY=limits[edge][1]+w->sy[j];bool ok=step(j);assert(ok==(edge%2==0)&&shotAvail[j]==(ok?254:0)&&draw_count==(ok?1u:0u));boundary_cases++;}
 reset(t,p);request(0,0);shotAvail[j]=1;assert(step(j)&&shotAvail[j]==0); /* caller skips this slot next tick */
 }} }
static void shared_reuse(void){const int ports[]={10,16,27,27,27,37,37,37,37,37,37,37,16,16};for(int t=0;t<3;t++)for(int r=0;r<14;r++){reset(t,0);const JE_WeaponType*w=&reuse_fixture[t][r];expect_record=reuse_records[r];expect_port=ports[r];expect_bay=r>=12?2:r==1?4:1;expect_player=2;int slots[8];for(int j=0;j<w->multi;j++)slots[j]=j;assert(request(9,-9)==w->multi-1&&power==999-fixture_power[t][expect_port]);volley_events(w,w->multi,0,slots);for(int j=0;j<w->multi;j++){assert(step(j));inspect(j,w,j,1);}reuse_calls++;}}
static void directions(void){const unsigned ports[]={10,27,32,22,38};static const unsigned expected_multi[17]={77,221,183,301,1,282,164,202,58,201,163,281,39,300,182,220,77};static const unsigned expected_mult2[17]={78,299,295,297,2,278,276,280,59,279,275,277,40,296,294,298,78};for(int t=0;t<3;t++)for(unsigned p=0;p<5;p++)for(int h=0;h<49;h++){reset(t,0);unsigned port=ports[p];expect_record=linkGunWeapons[port-1];assert(expect_record==(p<3?445u:451u));expect_port=0;expect_bay=1;expect_player=2;int id=request(0,0);assert(id==0);PlayerShotDataType before=playerShotData[0];JE_byte ttl=shotAvail[0];float scaled;int expected;if(h<17){scaled=(float)h;expected=h;}else{int k=(h-17)/2;bool upper=(h-17)%2;scaled=k+0.5f+(upper?0.001f:-0.001f);expected=k+(int)upper;}JE_real angle=(JE_real)(scaled*(2*M_PI/16));int vx=-(int)roundf(sinf(angle)*before.shotYM),vy=-(int)roundf(cosf(angle)*before.shotYM);player_shot_set_direction(id,port,angle);PlayerShotDataType check=before;check.shotXM=vx;check.shotYM=vy;check.shotGr=(p<3?expected_multi:expected_mult2)[expected];assert(!memcmp(&check,&playerShotData[0],sizeof(check))&&shotAvail[0]==ttl);direction_cases++;}
 /* Non-target sonic and generic routes remain exact without changing lifetime/damage. */
 for(unsigned p=0;p<4;p++){reset(0,0);expect_port=0;expect_record=445;expect_bay=1;request(0,0);PlayerShotDataType before=playerShotData[0];JE_real angle=(JE_real)(10*(2*M_PI/16));unsigned id=p==3?99:(unsigned[]){11,28,33}[p];player_shot_set_direction(0,id,angle);assert(playerShotData[0].shotGr==(p==3?before.shotGr:linkSonicGr[10])&&playerShotData[0].shotDmg==before.shotDmg&&shotAvail[0]==255);}
 assert(chargeGunWeapons[9]+3==461);for(int p=27;p<=38;p++)assert(chargeGunWeapons[p-1]+3==461);
}
int main(void){front();drift();failures_and_cadence();motion_edges();shared_reuse();directions();assert(results==requests);printf("{\"status\":\"PASS\",\"tables\":3,\"powers\":11,\"two_volley_calls\":%u,\"two_volley_members\":%u,\"drift_cases\":%u,\"cadence_ticks\":%u,\"insufficient_power_cases\":%u,\"capacity_cases\":%u,\"shadow_gate_cases\":%u,\"screen_boundary_cases\":%u,\"reuse_calls\":%u,\"direction_cases\":%u,\"movement_calls\":%u,\"requests\":%u,\"emissions\":%u,\"game_runs\":0}\n",front_calls,front_members,drift_cases,cadence_ticks,power_cases,capacity_cases,shadow_cases,boundary_cases,reuse_calls,direction_cases,moves,requests,emissions);return 0;}
