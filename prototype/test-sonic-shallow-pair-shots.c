/* Exact unchanged original create/move coverage for all22 Sonic rows, including
 * finite shallow pair63/82 reuse. Extracted functions only; never runs the game. */
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef uint8_t Uint8;typedef uint8_t JE_byte;typedef uint16_t JE_word;typedef int16_t JE_integer;typedef int8_t JE_shortint;typedef bool JE_boolean;typedef unsigned int uint;
#define WEAP_NUM 2000
#define PORT_NUM 60
#define MAX_PWEAPON 81
#include "shot-types.inc"
#include "weapon-records.inc"
static PlayerShotDataType playerShotData[MAX_PWEAPON+1];static JE_byte shotAvail[MAX_PWEAPON],shotMultiPos[11],shotRepeat[11],soundQueue[8];
static struct {JE_word poweruse;} weaponPort[PORT_NUM+1];static JE_word power;
static struct {int delta_x_shot_move,delta_y_shot_move;} player[2];
static struct {int scoreitem,ex,ey;} enemy[100];static JE_byte enemyAvail[100];static JE_word x,y;
static bool background2;static int shadowYDist=9;
typedef struct {int unused;} SDL_Surface;static SDL_Surface screen,*VGAScreen=&screen;
typedef struct {int tag;} Sprite2_array;static Sprite2_array spriteSheet8={8},spriteSheet12={12};
enum {ENTITY_NORMAL,ENTITY_BLEND,ENTITY_SHADOW,ENTITY_TILE};
#define OPTION_SHAPES 0
static struct {unsigned width,height;} unused_sprite;
static const void* unused_sprite_ptr(void){assert(!"unexpected special sprite");return &unused_sprite;}
#define sprite(...) ((void)unused_sprite_ptr(),&unused_sprite)
static unsigned creates,emits,draws,shadows,moves,capacity_cases,requests,phase_cases,rng_calls;
static unsigned shallow_emits[2],shallow_moves[2],shallow_shadow_orders[2];
static int shallow_member(unsigned id){return id==63?0:id==82?1:-1;}
static struct {int x,y,style,bank;unsigned id;} events[2];static unsigned event_count;static int draw_x,draw_y;static unsigned draw_id;static int last_bank;
static unsigned game_probe_shot_begin(JE_word port,uint bay,JE_word wp,JE_byte p,JE_word px,JE_word py){assert(port==11&&bay==1&&wp>=276&&wp<=297&&p==1&&px==130&&py==100);requests++;return requests;}
static void game_probe_shot_result(unsigned call,const char*r,int n,int id){assert(call==requests);(void)r;(void)n;(void)id;}
static void game_probe_shot_emit(unsigned call,int multi,int phase,int id){assert(call==requests&&multi>=1&&phase>=1&&id>=0&&id<MAX_PWEAPON);emits++;}
static void game_probe_shot_draw(int shot,JE_word raw,int bank,int frame,int px,int py,int style,int w,int h){(void)shot;(void)raw;assert(bank==8&&frame>0&&px>-100&&py>-100&&w==12&&h==14&&(style==ENTITY_NORMAL||style==ENTITY_SHADOW));}
static void draw_entity_sprite2(SDL_Surface*s,int px,int py,Sprite2_array b,unsigned id,int style,int layout){assert(s==VGAScreen&&layout==ENTITY_TILE&&event_count<2);events[event_count].x=px;events[event_count].y=py;events[event_count].id=id;events[event_count].style=style;events[event_count++].bank=b.tag;draws++;if(style==ENTITY_SHADOW)shadows++;else{assert(style==ENTITY_NORMAL);draw_x=px;draw_y=py;draw_id=id;last_bank=b.tag;}}
#define JE_setupExplosion(...) assert(!"unexpected trail")
#define JE_doSP(...) assert(!"unexpected special source")
#define blit_sprite_blend(...) assert(!"unexpected special blend")
/* A future RNG dependency in either extracted production function must fail. */
#define rand(...) (++rng_calls,assert(!"unexpected gameplay RNG"),0)
#define random(...) (++rng_calls,assert(!"unexpected gameplay RNG"),0)
#define mt_rand(...) (++rng_calls,assert(!"unexpected gameplay RNG"),0U)
#define mt_rand_1(...) (++rng_calls,assert(!"unexpected gameplay RNG"),0.0)
#define srand(...) (++rng_calls,assert(!"unexpected gameplay RNG seed"))
#include "shot-functions.inc"
static int clamp(int n,int lo,int hi){return n<lo?lo:n>hi?hi:n;}
static void reset(void){memset(playerShotData,0,sizeof(playerShotData));memset(shotAvail,0,sizeof(shotAvail));memset(shotMultiPos,0,sizeof(shotMultiPos));memset(shotRepeat,0,sizeof(shotRepeat));memset(soundQueue,0,sizeof(soundQueue));power=500;}
static void original_row_membership(void){
 unsigned masks[2]={0,0};
 for(unsigned rid=276;rid<=297;rid++){
  const JE_WeaponType*w=weapons+rid;
  assert(w->multi>0&&w->multi<=w->max&&w->max<=8&&w->weapani==0&&w->shotrepeat==6);
  for(unsigned n=0;n<w->max;n++){int member=shallow_member(w->sg[n]);if(member>=0)masks[member]|=1U<<(rid-276);}
 }
 /* ID63: mode1P2/P4 and mode2P2/P3/P4/P5/P6/P8/P9. ID82: mode1P8. */
 assert(masks[0]==((1U<<1)|(1U<<3)|(1U<<12)|(1U<<13)|(1U<<14)|(1U<<15)|(1U<<16)|(1U<<18)|(1U<<19)));
 assert(masks[1]==(1U<<7));
}
static void normal_rows(void){
 const int drift[]={-20,-6,-5,-4,-3,-1,0,1,3,4,5,6,20};
 for(unsigned rid=276;rid<=297;rid++)for(unsigned dx=0;dx<sizeof(drift)/sizeof(*drift);dx++)for(unsigned dy=0;dy<sizeof(drift)/sizeof(*drift);dy++){
  const JE_WeaponType*w=weapons+rid;reset();unsigned before=emits;JE_word mx=(JE_word)(130-drift[dx]),my=(JE_word)(100-drift[dy]);
  assert(player_shot_create(11,1,130,100,mx,my,(JE_word)rid,1)==w->multi-1);assert(emits==before+w->multi&&power==450&&soundQueue[2]==w->sound&&shotRepeat[1]==6&&shotMultiPos[1]==w->multi);creates++;
  for(unsigned n=0;n<w->multi;n++){
   PlayerShotDataType*s=playerShotData+n;int member=shallow_member(s->shotGr);if(member>=0)shallow_emits[member]++;int vx=w->sx[n]+(w->del[n]==98?clamp(drift[dx],-5,5):0);int vy=w->del[n]==100?clamp(drift[dy]-w->sy[n],-4,4):-w->sy[n];
   assert(s->shotX==130+w->bx[n]&&s->shotY==100+w->by[n]&&s->shotXM==vx&&s->shotYM==vy&&s->shotXC==w->accelerationx&&s->shotYC==-w->acceleration);
   assert(s->shotGr==w->sg[n]&&s->shotAni==0&&s->shotAniMax==1&&shotAvail[n]==w->del[n]&&s->shotTrail==255&&!s->shotComplicated&&!s->aimAtEnemy&&!s->chainReaction);
   int ex=s->shotX,ey=s->shotY;unsigned lifespan=shotAvail[n];
   for(int tick=1;tick<=4;tick++){
    vx+=w->accelerationx;ex+=vx;vy-=w->acceleration;ey+=vy;bool special=true;int ox=-999,oy=-999;JE_integer dmg=-999;JE_byte blast=0,chain=99,p=99;JE_word rw=0,rh=0;background2=(tick%2)==1;unsigned olddraws=draws,oldshadows=shadows;
    event_count=0;bool inside=ex>=-34&&ex<=290&&ey>=-15&&ey<=190;bool got=player_shot_move_and_draw((int)n,&special,&ox,&oy,&dmg,&blast,&chain,&p,&rw,&rh);assert(got==inside&&ox==ex&&oy==ey&&s->shotX==ex&&s->shotY==ey&&s->shotXM==vx&&s->shotYM==vy);
    assert(shotAvail[n]==(inside?lifespan-(unsigned)tick:0));
    if(!inside){assert(draws==olddraws&&shadows==oldshadows&&!event_count);break;}
    unsigned sh=background2&&ey+shadowYDist<190&&vx<100;assert(draws==olddraws+1+sh&&shadows==oldshadows+sh&&draw_x==ex+1&&draw_y==ey&&draw_id==w->sg[n]&&last_bank==8&&!special&&dmg==w->attack[n]&&blast==w->shipblastfilter&&!chain&&p==1&&s->shotAni==0);assert(event_count==1+sh&&events[sh].x==ex+1&&events[sh].y==ey&&events[sh].id==w->sg[n]&&events[sh].style==ENTITY_NORMAL&&events[sh].bank==8);if(sh)assert(events[0].x==ex+1&&events[0].y==ey+shadowYDist&&events[0].id==w->sg[n]&&events[0].style==ENTITY_SHADOW&&events[0].bank==8);if(member>=0){shallow_moves[member]++;if(sh)shallow_shadow_orders[member]++;}moves++;
   }
  }
  // Phase cycling is independent of the current mouse position.
  memset(shotAvail,0,sizeof(shotAvail));assert(player_shot_create(11,1,130,100,130,100,(JE_word)rid,1)==w->multi-1);assert(shotMultiPos[1]==w->multi&&power==400);creates++;
 }
}
static void shifted_phases(void){
 for(unsigned rid=276;rid<=297;rid++){
  const JE_WeaponType*w=weapons+rid;
  for(unsigned phase=0;phase<=w->max;phase++){
   reset();shotMultiPos[1]=(JE_byte)phase;
   assert(player_shot_create(11,1,130,100,129,99,(JE_word)rid,1)==w->multi-1);
   for(unsigned n=0;n<w->multi;n++){unsigned p=(phase+n)%w->max;PlayerShotDataType*s=playerShotData+n;assert(s->shotGr==w->sg[p]&&s->shotX==130+w->bx[p]&&s->shotY==100+w->by[p]);}
   assert(shotMultiPos[1]==(phase+w->multi-1)%w->max+1&&power==450);phase_cases++;
  }
 }
}
static void capacity(void){
 for(unsigned rid=276;rid<=297;rid++){const JE_WeaponType*w=weapons+rid;
  for(unsigned available=0;available<=w->multi;available++){
   reset();memset(shotAvail,1,sizeof(shotAvail));for(unsigned i=0;i<available;i++)shotAvail[i]=0;unsigned before=emits;int got=player_shot_create(11,1,130,100,130,100,(JE_word)rid,1);assert(got==(available<w->multi?MAX_PWEAPON:(int)w->multi-1)&&power==450&&emits==before+available&&soundQueue[2]==w->sound&&shotMultiPos[1]==available);capacity_cases++;
  }
  const unsigned energies[]={0,1,49,50,51,99,100,500};
  for(unsigned e=0;e<sizeof(energies)/sizeof(*energies);e++){unsigned energy=energies[e];reset();power=(JE_word)energy;unsigned before=emits;int got=player_shot_create(11,1,130,100,130,100,(JE_word)rid,1);assert(got==(energy<50?MAX_PWEAPON:(int)w->multi-1)&&power==(energy<50?energy:energy-50)&&emits==before+(energy<50?0:w->multi));assert(soundQueue[2]==(energy<50?0:w->sound)&&shotRepeat[1]==(energy<50?0:6)&&shotMultiPos[1]==(energy<50?0:w->multi));capacity_cases++;}
  /* Sparse free slots preserve lowest-slot emission order and partial-volley cost. */
  for(unsigned available=0;available<=w->multi;available++){
   reset();memset(shotAvail,1,sizeof(shotAvail));for(unsigned i=0;i<MAX_PWEAPON;i++)playerShotData[i].shotGr=777;
   for(unsigned i=0;i<available;i++)shotAvail[2*i+1]=0;
   unsigned before=emits;int got=player_shot_create(11,1,130,100,130,100,(JE_word)rid,1);
   assert(got==(available<w->multi?MAX_PWEAPON:(int)(2*w->multi-1))&&power==450&&emits==before+available&&shotMultiPos[1]==available);
   for(unsigned i=0;i<MAX_PWEAPON;i++){if(i%2&&i/2<available){unsigned phase=i/2;assert(playerShotData[i].shotGr==w->sg[phase]&&playerShotData[i].shotX==130+w->bx[phase]&&playerShotData[i].shotY==100+w->by[phase]&&shotAvail[i]==w->del[phase]);}else assert(playerShotData[i].shotGr==777&&shotAvail[i]==1);}
   capacity_cases++;
  }
 }
}
int main(void){weaponPort[11].poweruse=50;original_row_membership();normal_rows();shifted_phases();capacity();assert(!rng_calls);for(unsigned i=0;i<2;i++)assert(shallow_emits[i]&&shallow_moves[i]&&shallow_shadow_orders[i]);printf("{\"status\":\"PASS\",\"ordinary_first_level_rows\":22,\"rng_calls\":%u,\"shallow_pair_ids\":[63,82],\"shallow_pair_emissions\":[%u,%u],\"shallow_pair_movement_ticks\":[%u,%u],\"shallow_pair_shadow_before_head_cases\":[%u,%u],\"original_shadow_then_head_order_verified\":true,\"create_cases\":%u,\"movement_ticks\":%u,\"capacity_and_power_cases\":%u,\"volley_phase_cases\":%u,\"emits\":%u,\"draws\":%u,\"shadow_draws\":%u,\"game_runs\":0}\n",rng_calls,shallow_emits[0],shallow_emits[1],shallow_moves[0],shallow_moves[1],shallow_shadow_orders[0],shallow_shadow_orders[1],creates,moves,capacity_cases,phase_cases,emits,draws,shadows);return 0;}
