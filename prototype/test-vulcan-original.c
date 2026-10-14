/* Exact-source creation/movement/cadence, bounded caller-owned unit fixtures. */
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef unsigned uint;typedef uint8_t Uint8,JE_byte;typedef uint16_t JE_word;typedef int16_t JE_integer;typedef int8_t JE_shortint;typedef bool JE_boolean;
enum {PORT_NUM=60,WEAP_NUM=1818,MAX_PWEAPON=81,REAR_WEAPON=1};
enum {ENTITY_NORMAL,ENTITY_BLEND,ENTITY_SHADOW};
enum {ENTITY_TILE,OPTION_SHAPES};
#include "weapon_type.inc"
#include "port_type.inc"
#include "shot_type.inc"
#include "records.inc"
static JE_WeaponType weapons[WEAP_NUM+1];static JE_WeaponPortType weaponPort;
static PlayerShotDataType playerShotData[MAX_PWEAPON+1];static JE_byte shotAvail[MAX_PWEAPON],shotMultiPos[11],shotRepeat[11],soundQueue[8];
typedef struct {int delta_x_shot_move,delta_y_shot_move,x,y,weapon_mode;struct {struct {uint id,power;} weapon[2];} items;} Player;
static Player player[2];static int power,background2,shadowYDist=5;static JE_word x,y;static bool twoPlayerLinked,twoPlayerMode,galagaMode,button[4];
typedef struct {int token;} Sprite2_array;static Sprite2_array spriteSheet8={8},spriteSheet12={12};static void *VGAScreen;
static unsigned emissions,requests,results,draw_count,normal_count,shadow_count,calls,drifts,moves,cadence_ticks;static int last_phase;static const char *last_result;
typedef struct {int x,y,style;unsigned id;} Draw;static Draw draws[4];
static unsigned game_probe_shot_begin(unsigned p,unsigned bay,unsigned w,unsigned pl,unsigned px,unsigned py){assert(p==7&&bay==0&&w>=221&&w<=231&&pl==1);(void)px;(void)py;requests++;return requests;}
static void game_probe_shot_result(unsigned call,const char*r,int count,int id){assert(call==requests);(void)count;(void)id;last_result=r;results++;}
static void game_probe_shot_emit(unsigned call,int multi,int phase,int id){assert(call==requests&&multi==1&&id<MAX_PWEAPON);last_phase=phase;emissions++;}
static void game_probe_fire(unsigned pl,unsigned p,int bay,int px,int py,unsigned w,int id){assert(pl==1&&p==7&&bay==0&&w>=221&&w<=231&&id<MAX_PWEAPON);(void)px;(void)py;}
static void game_probe_shot_draw(int id,unsigned raw,int bank,unsigned frame,int px,int py,int style,int w,int h){assert(id<MAX_PWEAPON&&raw==frame&&bank==8&&w==12&&h==14);(void)px;(void)py;(void)style;}
static void draw_entity_sprite2(void *s,int px,int py,Sprite2_array bank,unsigned id,int style,int layout){assert(s==VGAScreen&&bank.token==8&&layout==ENTITY_TILE&&draw_count<4);draws[draw_count++]=(Draw){px,py,style,id};if(style==ENTITY_NORMAL)normal_count++;else{assert(style==ENTITY_SHADOW);shadow_count++;}}
static int enemyAvail[100];static struct {int scoreitem,ex,ey;} enemy[100];
#define JE_setupExplosion(...) assert(0)
#define JE_doSP(...) assert(0)
#define blit_sprite_blend(...) assert(0)
static struct {int width,height;} special_shape;
#define sprite(...) (&special_shape)
#include "player_shot_create.inc"
#include "player_shot_move_and_draw.inc"
static void cadence(void){Player *this_player=player;int playerNum_=1,temp,b,mx=player[0].x,my=player[0].y;int *mouseX_=&mx,*mouseY_=&my;
#include "cadence.inc"
}
static void load(int table,int p){memset(weapons,0,sizeof(weapons));memset(shotAvail,0,sizeof(shotAvail));memset(playerShotData,0,sizeof(playerShotData));memset(shotMultiPos,0,sizeof(shotMultiPos));memset(shotRepeat,0,sizeof(shotRepeat));memset(soundQueue,0,sizeof(soundQueue));memset(player,0,sizeof(player));weaponPort[7].poweruse=20;for(int i=0;i<11;i++){weapons[221+i]=fixture[table][i];weaponPort[7].op[0][i]=221+i;}player[0].x=150;player[0].y=160;player[0].weapon_mode=1;player[0].items.weapon[0].id=7;player[0].items.weapon[0].power=p+1;power=999;background2=0;draw_count=0;}
static int create(int p,int drift){power=999;memset(shotAvail,0,sizeof(shotAvail));unsigned before=emissions;int id=player_shot_create(7,0,150,160,150-drift,160,221+p,1);assert(id==0&&emissions==before+1&&!strcmp(last_result,"complete")&&power==979);return id;}
static void inspect(int table,int p,int phase,int drift){const JE_WeaponType *w=&fixture[table][p];PlayerShotDataType *s=playerShotData;int dc=drift<-5?-5:drift>5?5:drift;assert(last_phase==phase+1&&shotMultiPos[0]==phase+1&&shotRepeat[0]==w->shotrepeat&&soundQueue[0]==w->sound);assert(s->shotX==150+w->bx[phase]&&s->shotY==160+w->by[phase]);assert(s->shotXM==w->sx[phase]+dc&&s->shotYM==-20&&s->shotYC==1&&s->shotXC==0);assert(s->shotGr==(p<6?67:70)&&s->shotAni==0&&s->shotAniMax==1&&shotAvail[0]==98);assert(s->shotDmg==(p<6?1:2)&&s->shotBlastFilter==(table?112:208)&&s->shotTrail==255&&s->chainReaction==0&&s->playerNumber==1&&!s->aimAtEnemy&&!s->shotComplicated);}
static bool step(void){bool special=true;int px=0,py=0;JE_integer dmg=0;JE_byte filter=0,chain=99,pl=0;JE_word rw=123,rh=456;draw_count=0;bool ok=player_shot_move_and_draw(0,&special,&px,&py,&dmg,&filter,&chain,&pl,&rw,&rh);if(ok){assert(!special&&px==playerShotData[0].shotX&&py==playerShotData[0].shotY&&dmg==playerShotData[0].shotDmg&&filter==playerShotData[0].shotBlastFilter&&!chain&&pl==1&&rw==123&&rh==456);assert(draw_count>=1&&draws[draw_count-1].x==px+1&&draws[draw_count-1].y==py&&draws[draw_count-1].id==playerShotData[0].shotGr&&draws[draw_count-1].style==ENTITY_NORMAL&&playerShotData[0].shotAni==0);}moves++;return ok;}
int main(void){
 const int phase_counts[]={2,4,4,6,8,8,4,6,8,8,8},repeat[]={1,1,1,1,1,1,2,2,2,1,0};
 for(int t=0;t<3;t++)for(int p=0;p<11;p++){load(t,p);assert(fixture[t][p].max==phase_counts[p]&&fixture[t][p].multi==1&&fixture[t][p].shotrepeat==repeat[p]);for(int n=0;n<2*phase_counts[p];n++){int phase=n%phase_counts[p];create(p,0);inspect(t,p,phase,0);int ox=playerShotData[0].shotX,oy=playerShotData[0].shotY,vx=playerShotData[0].shotXM;for(int tick=1;tick<=3;tick++){assert(step());assert(playerShotData[0].shotX==ox+tick*vx&&playerShotData[0].shotY==oy-20*tick+tick*(tick+1)/2&&shotAvail[0]==98-tick&&draw_count==1);}calls++;}}
 assert(calls==396);
 const int delta[]={-9,-5,-1,0,1,5,9};for(int p=0;p<=6;p+=6)for(unsigned d=0;d<sizeof(delta)/sizeof(*delta);d++){load(0,p);create(p,delta[d]);inspect(0,p,0,delta[d]);assert(step());drifts++;}
 /* Original conditional shadow order, exact strict190 cutoff and background gate. */
 for(int p=0;p<=6;p+=6)for(int gate=0;gate<3;gate++){load(0,p);create(p,0);background2=gate!=0;shadowYDist=gate==2?49:5;assert(step());assert(draw_count==(unsigned)(gate==1?2:1));if(gate==1){assert(draws[0].style==ENTITY_SHADOW&&draws[0].y==draws[1].y+5&&draws[0].x==draws[1].x&&draws[0].id==draws[1].id);}}
 /* Unmodified screen exit clears the pool entry. */
 for(int p=0;p<=6;p+=6){load(0,p);create(p,0);unsigned ticks=0;while(step()){assert(++ticks<30);}assert(shotAvail[0]==0&&draw_count==0);}
 /* Actual original cadence block with bounded held/released input and ample unit power. */
 for(int p=0;p<11;p++){load(0,p);unsigned countdown=0;for(unsigned tick=0;tick<24;tick++){button[0]=tick<8||tick>=16;memset(shotAvail,0,sizeof(shotAvail));power=999;unsigned before=emissions;bool fire=!countdown&&button[0];if(countdown)countdown--;else if(fire)countdown=repeat[p];cadence();assert(emissions==before+(unsigned)fire&&shotRepeat[0]==countdown);cadence_ticks++;}}
 /* A failed power request must not advance phase, spawn or set cadence. */
 load(0,0);power=19;unsigned before=emissions;assert(player_shot_create(7,0,150,160,150,160,221,1)==MAX_PWEAPON);assert(emissions==before&&shotMultiPos[0]==0&&shotRepeat[0]==0&&power==19&&!strcmp(last_result,"power"));assert(results==requests);
 printf("{\"status\":\"PASS\",\"tables\":3,\"powers\":11,\"two_cycle_calls\":%u,\"drift_cases\":%u,\"movement_calls\":%u,\"cadence_ticks\":%u,\"game_runs\":0}\n",calls,drifts,moves,cadence_ticks);return 0;
}
