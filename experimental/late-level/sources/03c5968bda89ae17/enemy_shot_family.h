#ifndef ENEMY_SHOT_FAMILY_H
#define ENEMY_SHOT_FAMILY_H
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
enum { ENEMY_SHOT_NATIVE_STORE_TAG=13,ENEMY_SHOT_EXTRA_STORE_TAG=19,
 ENEMY_SHOT_RETIRE_DURATION=1,ENEMY_SHOT_RETIRE_BOUNDARY=2,ENEMY_SHOT_RETIRE_COLLISION=3,ENEMY_SHOT_RETIRE_RESET=4 };
typedef struct {uint8_t x,y,index;} EnemyShotWrite;
typedef struct {
 int x,y,xm,ym,xc,yc;unsigned tx,ty,sprite,damage,duration,animate,animax;
} EnemyShotState;
typedef struct {
 uint64_t epoch,serial,generation,emitter_generation,weapon_stamp,birth_frame,last_frame,retired_frame;
 unsigned slot,weapon,turret,phase,emitter_slot,emitter_record,retirement_reason,player;
 unsigned observations,draws;bool witnessed,live;
 EnemyShotState born,current,retired;
} EnemyShotBirth;
typedef struct {
 uint64_t frame,epoch,serial,generation,bank_stamp;uintptr_t bank_data;
 unsigned slot,index,bank_bytes,callbacks,core_stores,extra_stores;int x,y;
 EnemyShotState state;bool complete;
} EnemyShotDraw;
typedef struct {
 bool requested,loaded,active,pending,contributed,failed,accepted;
 unsigned first_reason,draw_count,material_mask,native_cells,extra_pixels;
 uint64_t frame,births,allocations,motions,animations,retirements[4],normal_retirements,blend_retirements,shadow_cells,extra_retirements,clipped,unwitnessed,lifetime_losses;
 EnemyShotBirth birth[60];EnemyShotDraw draw[60];
} EnemyShotFamilyStatus;
/* Read-only diagnostic receipts. They cannot authorize native or RGB writes. */
EnemyShotFamilyStatus render_mirror_enemy_shot_family_status(void);
bool render_mirror_enemy_shot_family_pre_draw(EnemyShotDraw *,uint32_t *,size_t,uint8_t *,size_t);
unsigned render_mirror_enemy_shot_family_callbacks(EnemyShotWrite *,size_t);
bool render_mirror_enemy_shot_family_support(uint8_t *,size_t,uint8_t *,size_t);
#endif
