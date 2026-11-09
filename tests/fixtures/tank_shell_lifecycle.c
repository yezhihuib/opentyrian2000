/* Included by test_tank_shell_lifecycle.py after verbatim source extraction.
 * Synthetic world/admission inputs are explicit; no gameplay writes are added. */
#define _POSIX_C_SOURCE 200809L
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "enemy_shot_family.h"
#include "tank194_family.h"
typedef int16_t JE_integer;
typedef int8_t JE_shortint;
typedef uint16_t JE_word;
typedef uint8_t JE_byte, Uint8;
typedef uint32_t Uint32;
typedef bool JE_boolean;
typedef unsigned int uint;
typedef struct {uint8_t *data;size_t size;} Sprite2_array;
typedef struct {uint8_t *rgba;} Asset;
typedef struct {int x,y,x_velocity,y_velocity;unsigned shot_hit_area_x,shot_hit_area_y,invulnerable_ticks;bool is_alive;} Player;
#define COUNTOF(x) (sizeof(x)/sizeof((x)[0]))
#define MAX(a,b) ((a)>(b)?(a):(b))
#define ENEMY_SHOT_MAX 60
#define DIFFICULTY_NORMAL 2
#define B313_FAMILY_CANVAS_DIAGNOSTIC 1
#define FC_SOURCE 1
RECORDS
#include "enemy_shot_native.inc"
#include "tank194_native.inc"
DECLARATIONS
TANK_DECLARATIONS
static EnemyShotType enemyShot[60];
static JE_byte enemyShotAvail[60],enemyAvail[100];
static struct JE_SingleEnemyType enemy[100];
static JE_WeaponType weapons[8];
static Player player[2];
static uint64_t fc_frame;
static unsigned faults,draw_calls,damage_calls,random_calls,soundQueue[8];
static unsigned eventLoc,curLoc,maxEvent=731;
static bool level_ok=true,shape_ok=true,bank_ok=true,weapon_ok=true,twoPlayerMode;
static bool damage_kills;
static bool play_demo,demo_file,game_probe_enabled,asset_debug_enabled,stopped_demo,constantPlay,constantDie,richMode;
static int mainLevel=6,terrain_file='z',difficultyLevel=DIFFICULTY_NORMAL,global_tank194_frame;
static char levelName[16]="ASTEROID2",global_asset_directory[1];
static Sprite2_array spriteSheet8,spriteSheet12;
static struct JE_EventRecType rows[258];
static uint8_t bank_data[1];
static Sprite2_array body_bank={bank_data,1};
static bool family_scope(void){return level_ok;}
static bool t194_level_scope(void){return level_ok;}
static const char *t194_root(void){return "fixture";}
static bool t194_shape(unsigned slot,unsigned stage){(void)slot;(void)stage;return shape_ok;}
static bool t194_targets(unsigned type,const int *d,unsigned s){(void)type;(void)d;(void)s;return false;}
static bool t194_resources_current(void){return true;}
static void t194_fail(unsigned reason){(void)reason;++faults;}
static void family_fault(int reason){(void)reason;++faults;}
static bool es_bank(Sprite2_array bank){(void)bank;return bank_ok;}
static uint64_t es_weapon(unsigned weapon){
 for(unsigned i=0;weapon_ok&&i<COUNTOF(es_weapons);i++)
  if(es_weapons[i].weapon==weapon)return es_weapons[i].stamp;
 return 0;
}
TANK_FUNCTIONS
FUNCTIONS

/* External presentation/audio/damage effects are not part of this harness.
 * Consume the actual before_draw lease with a synthetic renderer completion. */
static void draw_enemy_shot_sprite2(void *screen,int x,int y,Sprite2_array bank,unsigned sprite){
 (void)screen;(void)bank;++draw_calls;
 if(!es.pending)return;
 unsigned slot=es.slot;
 EnemyShotBirth *b=&es_life[slot].birth;
 EnemyShotDraw d={.slot=slot,.epoch=b->epoch,.serial=b->serial,.generation=b->generation,
  .index=sprite,.x=x,.y=y,.state=es_state(slot)};
 assert(es_draw_current(&d));
 assert(es.lease_generation==b->generation&&es.lease_frame==fc_frame);
 es_life[slot].draw_frame=fc_frame;++b->draws;es.pending=false;
}
static unsigned mt_rand(void){++random_calls;return 0;}
static int JE_playerDamage(int damage,Player *p){++damage_calls;if(damage_kills)p->is_alive=false;return damage;}
#define tank_muzzle_allocate(...) ((void)0)
#define tank_muzzle_birth(...) ((void)0)
#define tank_muzzle_retire(...) ((void)0)
#define tank_muzzle_draw(...) 0
#define render_mirror_tank147_muzzle_lane() false
#define render_mirror_gray325_shot_fired(...) ((void)0)
#define render_mirror_normal270_shot_fired(...) ((void)0)
#define render_mirror_late_actor_shot_fired(...) ((void)0)
#define game_probe_collision(...) ((void)0)
#define JE_setupHitflareExplosion(...) ((void)0)
#define blit_sprite2(...) ((void)0)
#define draw_tank147_muzzle_sprite2(...) ((void)0)
#define render_mirror_shadow_end() ((void)0)
#define render_mirror_entity_end() ((void)0)
#define widget_sonic_member_index(x) 0
#define orb_protron_protron_index(x) 0
#define VGAScreen NULL
static unsigned native_allocate(unsigned i,unsigned temp3,unsigned j,int tempX,int tempY,int tempMapXOfs){
 unsigned b=60,temp=0,temp2=0;
ALLOCATION
draw_enemy_end:
 (void)temp2;
 return b;
}
static void native_step(void){
 int temp=0;
MOTION
}

static void reset(void){
 memset(es_life,0,sizeof es_life);memset(es_actor_generation,0,sizeof es_actor_generation);
 memset(enemy,0,sizeof enemy);memset(enemyShot,0,sizeof enemyShot);
 memset(enemyShotAvail,1,sizeof enemyShotAvail);memset(enemyAvail,1,sizeof enemyAvail);
 memset(player,0,sizeof player);memset(weapons,0,sizeof weapons);
 memset(&t194_life,0,sizeof t194_life);memset(t194_slots,0,sizeof t194_slots);
 memset(&t194_frame,0,sizeof t194_frame);memset(es_retirements,0,sizeof es_retirements);
 es_epoch=es_serial=es_allocations=es_motions=es_animations=es_lifetime_losses=0;
 faults=draw_calls=damage_calls=random_calls=0;fc_frame=10;
 level_ok=shape_ok=bank_ok=weapon_ok=true;twoPlayerMode=damage_kills=false;
 setenv("ENEMY_SHOT_FAMILY_ENABLE","1",1);setenv("BUILDING313_FAMILY_CANVAS_ENABLE","1",1);
 es_tick();render_mirror_enemy_shot_pool_begin();
 for(unsigned n=0;n<258;n++){
  const int *d=t194_events[n].d;
  rows[n]=(struct JE_EventRecType){.eventtime=t194_events[n].time,.eventtype=t194_events[n].type,
   .eventdat=d[0],.eventdat2=d[1],.eventdat3=d[2],.eventdat4=d[3],.eventdat5=d[4],.eventdat6=d[5]};
 }
 t194_life.epoch=7;t194_life.loaded=true;t194_life.events=rows;strcpy(t194_life.root,"fixture");
 enemyAvail[75]=0;enemy[75].enemytype=194;enemy[75].sprite2s=&body_bank;
 enemy[75].tur[0]=2;enemy[75].tur[1]=3;enemy[75].tur[2]=4;
 t194_slots[75].live=true;t194_slots[75].generation=t194_slots[75].witness=1;
 t194_slots[75].birth=(Tank194Birth){.epoch=7,.token=11,.event=6,.live=true};
 t194_slots[75].bank=&body_bank;t194_slots[75].data=body_bank.data;t194_slots[75].bytes=body_bank.size;
 render_mirror_enemy_shot_actor_allocated(enemy+75);
 /* Synthetic bounded records use the published native velocity/orientation.
  * Duration and damage can vary below to reach otherwise distant exits. */
 for(unsigned w=2;w<=3;w++){
  weapons[w].multi=weapons[w].max=1;weapons[w].del[0]=255;
  weapons[w].sg[0]=144+w;weapons[w].attack[0]=5;
 }
 weapons[2].sy[0]=4;weapons[3].sx[0]=-3;weapons[3].sy[0]=3;
}
static unsigned birth(unsigned w,int x,int y){
 unsigned slot=native_allocate(75,w,w-1,x,y,0);
 assert(slot<60&&es_live(slot));return slot;
}
static void next_frame(void){++fc_frame;es_tick();}
static void assert_retired(unsigned slot,unsigned reason){
 assert(enemyShotAvail[slot]&&!es_life[slot].birth.live);
 assert(es_life[slot].birth.retirement_reason==reason);
 assert(es_life[slot].birth.retired_frame==fc_frame);
 EnemyShotState state=es_state(slot);
 assert(es_equal(&es_life[slot].birth.current,&state)&&es_equal(&es_life[slot].birth.retired,&state));
 assert(es_retirements[reason-1]==1&&!es_lifetime_losses&&!faults);
}
static void test_parent_independence(void){
 for(unsigned weapon=2;weapon<=3;weapon++)for(unsigned mode=0;mode<3;mode++){
  reset();unsigned slot=birth(weapon,40,30);uint64_t serial=es_life[slot].birth.serial;
  native_step();assert(es_live(slot)&&es_life[slot].birth.observations==1);
  if(mode==0){enemyAvail[75]=1;render_mirror_tank194_family_retired(75);}
  if(mode==1){
   render_mirror_tank194_family_retired(75);render_mirror_enemy_shot_actor_allocated(enemy+75);
   enemy[75].enemytype=999;enemy[75].tur[0]=7;enemy[75].sprite2s=NULL;
  }
  if(mode==2){
   eventLoc=t194_life.next_event=259;curLoc=0;
   render_mirror_tank194_family_event_before(259);
   assert(t194_life.stream_broken&&!t194_slots[75].live&&!t194_scope());
  }
  for(unsigned frame=0;frame<3;frame++){
   next_frame();native_step();assert(es_live(slot)&&es_life[slot].birth.serial==serial);
   assert(es_life[slot].birth.observations==frame+2);
  }
  assert(enemyShot[slot].sx==40+(weapon==2?0:12));
  assert(enemyShot[slot].sy==30+(weapon==2?16:12));
  unsigned rejected=native_allocate(75,weapon,weapon-1,60,30,0);
  assert(rejected==1&&!es_life[rejected].birth.live&&es_live(slot));
  assert(!es_lifetime_losses&&!faults&&!random_calls);
 }
}
static void test_retirement(void){
 for(unsigned weapon=2;weapon<=3;weapon++){
  for(unsigned duration=0;duration<=1;duration++){
   reset();weapons[weapon].del[0]=duration;unsigned slot=birth(weapon,40,30);
   native_step();
   if(duration){assert(es_live(slot)&&enemyShot[slot].duration==0);next_frame();native_step();}
   assert_retired(slot,ENEMY_SHOT_RETIRE_DURATION);assert(enemyShot[slot].duration==255);
  }
  for(unsigned side=0;side<4;side++){
   reset();int vx=weapon==2?0:3,vy=weapon==2?4:3;
   int x=side==0?-vx:side==1?276-vx:40;
   int y=side==2?-14-vy:side==3?191-vy:30;
   unsigned slot=birth(weapon,x,y);native_step();assert_retired(slot,ENEMY_SHOT_RETIRE_BOUNDARY);
  }
  for(unsigned side=0;side<4;side++){
   reset();int vx=weapon==2?0:3,vy=weapon==2?4:3;
   int x=side==0?1-vx:side==1?275-vx:40;
   int y=side==2?-13-vy:side==3?190-vy:30;
   unsigned slot=birth(weapon,x,y);native_step();assert(es_live(slot)&&draw_calls==1);
  }
  for(unsigned invulnerable=0;invulnerable<2;invulnerable++){
   reset();unsigned slot=birth(weapon,40,30);
   player[0]=(Player){.x=40+(weapon==2?0:3),.y=30+(weapon==2?4:3),
    .shot_hit_area_x=3,.shot_hit_area_y=3,.is_alive=true,.invulnerable_ticks=invulnerable};
   native_step();assert_retired(slot,ENEMY_SHOT_RETIRE_COLLISION);
   assert(damage_calls==!invulnerable&&draw_calls==0);
  }
  reset();unsigned lethal=birth(weapon,40,30);damage_kills=true;
  player[0]=(Player){.x=40,.y=34,.shot_hit_area_x=10,.shot_hit_area_y=10,.is_alive=true};
  native_step();assert_retired(lethal,ENEMY_SHOT_RETIRE_COLLISION);
  assert(!player[0].is_alive&&damage_calls==1); /* receipt precedes damage */
  /* Exact hitbox edges and dead players do not collide. */
  for(unsigned side=0;side<5;side++){
   reset();unsigned slot=birth(weapon,40,30);int x=40+(weapon==2?0:3),y=30+(weapon==2?4:3);
   player[0]=(Player){.x=x+(side==0?3:side==1?-3:0),.y=y+(side==2?3:side==3?-3:0),
    .shot_hit_area_x=3,.shot_hit_area_y=3,.is_alive=side!=4};
   native_step();assert(es_live(slot)&&!damage_calls&&draw_calls==1);
  }
  reset();weapons[weapon].del[0]=0;unsigned slot=birth(weapon,276,190);
  native_step();assert_retired(slot,ENEMY_SHOT_RETIRE_DURATION); /* expiry has priority */
 }
}
static void test_slot_reuse(void){
 reset();weapons[2].del[0]=0;unsigned slot=birth(2,40,30);
 uint64_t generation=es_life[slot].generation,serial=es_life[slot].birth.serial;
 native_step();assert_retired(slot,ENEMY_SHOT_RETIRE_DURATION);
 next_frame();assert(birth(3,50,40)==slot);
 assert(es_life[slot].generation==generation+1&&es_life[slot].birth.serial==serial+1);
 native_step();assert(es_live(slot)&&enemyShot[slot].sgr==147&&es_life[slot].birth.observations==1);
 /* Reusing the same native pool slot for an unrelated weapon cannot inherit HD. */
 enemyShotAvail[slot]=1;weapons[4]=weapons[2];enemy[75].tur[2]=4;
 assert(native_allocate(75,4,3,50,40,0)==slot);
 assert(!es_live(slot)&&es_life[slot].generation==generation+2);
 reset();for(unsigned n=0;n<60;n++)assert(birth(n%2+2,40,30)==n);
 assert(native_allocate(75,2,1,40,30,0)==60&&es_allocations==60&&es_serial==60);
 native_step();for(unsigned n=0;n<60;n++)assert(es_live(n)&&es_life[n].birth.observations==1);
 assert(draw_calls==60&&!faults);
 render_mirror_enemy_shot_pool_begin();assert(es_retirements[3]==60);
 for(unsigned n=0;n<60;n++)assert(!es_live(n));
}
static void test_fail_closed(void){
 for(unsigned mode=0;mode<8;mode++){
  reset();
  if(mode==0)unsetenv("ENEMY_SHOT_FAMILY_ENABLE");
  if(mode==1)setenv("ENEMY_SHOT_FAMILY_ENABLE","0",1);
  if(mode==2)unsetenv("BUILDING313_FAMILY_CANVAS_ENABLE");
  if(mode==3)level_ok=false;
  if(mode==4)bank_ok=false;
  if(mode==5)weapon_ok=false;
  if(mode==6)shape_ok=false;
  if(mode==7)t194_slots[75].birth.event=259;
  unsigned slot=native_allocate(75,2,1,40,30,0);assert(slot==0&&!es_live(slot));
  native_step();assert(!enemyShotAvail[slot]&&enemyShot[slot].sy==34&&enemyShot[slot].duration==254);
  assert(!es_serial&&!random_calls);
 }
 for(unsigned mode=0;mode<5;mode++){
  reset();unsigned slot=birth(2,40,30);native_step();
  if(mode==0)native_step(); /* duplicate step */
  if(mode==1){fc_frame+=2;es_tick();native_step();} /* missed frame */
  if(mode==2){next_frame();++enemyShot[slot].sxm;native_step();} /* native mutation */
  if(mode==3){next_frame();weapon_ok=false;native_step();}
  if(mode==4){next_frame();level_ok=false;native_step();}
  assert(!es_live(slot)&&es_lifetime_losses==1);
 }
 /* An old draw identity cannot alias a replacement in the same pool slot. */
 reset();unsigned slot=birth(2,40,30);native_step();
 EnemyShotBirth old=es_life[slot].birth;enemyShotAvail[slot]=1;
 assert(birth(3,50,40)==slot);
 EnemyShotDraw d={.slot=slot,.epoch=old.epoch,.serial=old.serial,.generation=old.generation,
  .index=old.current.sprite,.x=old.current.x,.y=old.current.y,.state=old.current};
 assert(!es_draw_current(&d));
}
static void test_timing_and_draw_leases(void){
 /* Both actual scheduling possibilities: fire before or after the shot loop. */
 for(unsigned delay=0;delay<3;delay++){
  reset();unsigned slot=birth(2,40,30);
  for(unsigned n=0;n<delay;n++)next_frame();
  native_step();assert(es_live(slot)==(delay<2));
  assert(es_life[slot].birth.observations==(delay<2));
 }
 reset();unsigned slot=birth(2,40,30);native_step();
 render_mirror_enemy_shot_before_draw(slot); /* duplicate draw in one frame */
 assert(!es.pending&&!es_live(slot)&&es_lifetime_losses==1);
 reset();slot=birth(2,40,30);native_step();
 /* Supply no previous draw completion, as at the renderer entry point. */
 es_life[slot].draw_frame=UINT64_MAX;
 render_mirror_enemy_shot_before_draw(slot);assert(es.pending);
 enemyShotAvail[slot]=1;assert(birth(3,50,40)==slot);assert(!es.pending);
 reset();slot=birth(2,40,30);native_step();es_life[slot].draw_frame=UINT64_MAX;
 render_mirror_enemy_shot_before_draw(slot);assert(es.pending);
 render_mirror_enemy_shot_after_draw();assert(es.failed&&!es.pending);
 reset();slot=birth(2,40,30);native_step();
 EnemyShotBirth b=es_life[slot].birth;
 EnemyShotDraw d={.slot=slot,.epoch=b.epoch,.serial=b.serial,.generation=b.generation,
  .index=b.current.sprite,.x=b.current.x,.y=b.current.y,.state=b.current};
 assert(es_draw_current(&d));++enemyShot[slot].sx;assert(!es_draw_current(&d));
 --enemyShot[slot].sx;next_frame();assert(!es_draw_current(&d));
 /* A previously contributed draw cannot survive slot reuse in the same frame. */
 reset();slot=birth(2,40,30);native_step();es.contributed=true;
 es.count=1;es.draws[0].slot=slot;enemyShotAvail[slot]=1;
 assert(birth(3,50,40)==slot);assert(es.failed&&faults==1);
}
static void test_native_equivalence(void){
 EnemyShotType shots[60];JE_byte avail[60];Player players[2];
 unsigned draws=0,damage=0,random=0;
 for(unsigned weapon=2;weapon<=3;weapon++)for(unsigned scenario=0;scenario<5;scenario++){
  for(unsigned enabled=0;enabled<2;enabled++){
   reset();setenv("ENEMY_SHOT_FAMILY_ENABLE",enabled?"1":"0",1);
   if(scenario==1)weapons[weapon].del[0]=1;
   if(scenario==2)player[0]=(Player){.x=40,.y=34,.shot_hit_area_x=10,.shot_hit_area_y=10,.is_alive=true};
   assert(native_allocate(75,weapon,weapon-1,40,30,0)==0);
   if(scenario==3){enemyAvail[75]=1;render_mirror_tank194_family_retired(75);}
   if(scenario==4){eventLoc=t194_life.next_event=259;render_mirror_tank194_family_event_before(259);}
   for(unsigned frame=0;frame<3;frame++){native_step();next_frame();}
   if(!enabled){
    memcpy(shots,enemyShot,sizeof shots);memcpy(avail,enemyShotAvail,sizeof avail);
    memcpy(players,player,sizeof players);draws=draw_calls;damage=damage_calls;random=random_calls;
   }else{
    assert(!memcmp(shots,enemyShot,sizeof shots)&&!memcmp(avail,enemyShotAvail,sizeof avail));
    assert(!memcmp(players,player,sizeof players));
    assert(draws==draw_calls&&damage==damage_calls&&random==random_calls);
   }
  }
 }
}
int main(void){
 test_parent_independence();test_retirement();test_slot_reuse();test_fail_closed();
 test_timing_and_draw_leases();test_native_equivalence();
 puts("PASS: native shell allocation/update; parent death/reuse/event259; expiry/boundary/collision; 60-slot reuse; timing/leases/default-off; 10 enabled/disabled native-state pairs");
 return 0;
}
