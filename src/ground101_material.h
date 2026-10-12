/* Finite optional world-material bundle and display-only context. */
#ifndef GROUND101_MATERIAL_H
#define GROUND101_MATERIAL_H
#include "world_material.h"
typedef struct {
 unsigned role,index,slot,base_offset,mask_offset,generated_offset,generated_weight_offset,ground_weight_offset;
} G101Record;
typedef struct {
 unsigned type,pool_slot,availability,size;
 bool score_item,damaged,independent_motion,static_animation;
} G101EnemyContext;
bool ground101_bundle_load(const char *asset_directory);
const G101Record *ground101_record(unsigned role,unsigned index);
const G101Record *ground101_record_at(unsigned index);
const uint8_t *ground101_base(const G101Record *record);
void ground101_frame_reset(void);
bool ground101_layer1_preflight(const void *map,size_t bytes,const void *first,size_t stride,int x,int y);
/* -1: inconsistent recognized Layer1 row; 0: unrelated/inactive; 1: valid. */
int ground101_layer1_row(const void *actual,int x,int y);
bool ground101_enemy_eligible(const G101EnemyContext *,unsigned role,unsigned base);
#ifdef GROUND101_MATERIAL_TRACE
void ground101_actor_trace(unsigned tick,const G101EnemyContext *,unsigned role,unsigned base,int part,int filter,int x,int y,bool eligible);
void ground101_note_draw(const G101Record *,bool actor);
#else
#define ground101_actor_trace(...) ((void)0)
#define ground101_note_draw(...) ((void)0)
#endif
void ground101_select(const G101Record *,const uint8_t *accepted,unsigned n,int dx,int dy,uint8_t out[4]);
#ifdef GROUND101_MATERIAL_TRACE
void ground101_frame_report(unsigned tick,const char *rejection);
#else
#define ground101_frame_report(...) ((void)0)
#endif
#ifdef GROUND101_MATERIAL_TEST
bool ground101_test_layout(const G101Record *,size_t count,size_t payload_bytes);
#endif
#endif
