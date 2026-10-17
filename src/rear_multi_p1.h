/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef REAR_MULTI_P1_H
#define REAR_MULTI_P1_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
/* Renderer-owned identities only. Never embedded in a gameplay shot. */
enum { REAR_P1_SLOTS=80, REAR_P1_HEADS=19, REAR_P1_OBSERVED=21, REAR_P1_CELLS=168, REAR_P1_MAX_BUDGET=5 };
typedef struct {
 unsigned gr,ani,ani_max,player,trail,aim,chain,complicated,filter;
 int xm,ym,xc,yc;
} RearP1Shot;
typedef struct {bool qualified;unsigned record,mode,phase,raw;uint64_t generation;} RearP1Birth;
typedef struct {
 RearP1Birth birth[REAR_P1_SLOTS];
 /* Original admitted identity, separate from mutable presentation metadata. */
 uint64_t birth_identity[REAR_P1_SLOTS];
 uint64_t generation,tick,call_serial,call;
 bool pending,lease;
 unsigned record,mode,budget,remaining,next_ordinal,next_phase,used_count;
 unsigned used_slots[REAR_P1_MAX_BUDGET];
} RearP1State;
uint64_t rear_p1_stamp(const void *,size_t);
/* Drawable resources and validated observations are deliberately distinct. */
int rear_p1_member(unsigned raw);
int rear_p1_observed(unsigned raw);
void rear_p1_reset(RearP1State *);
void rear_p1_call_end(RearP1State *);
void rear_p1_call_begin(RearP1State *,uint64_t tick,unsigned port,unsigned bay,
 unsigned power_index,unsigned mode_index,unsigned player,unsigned record,bool scope,bool table);
uint64_t rear_p1_create_begin(RearP1State *,uint64_t tick,unsigned port,unsigned bay,
 unsigned record,unsigned player);
void rear_p1_create_end(RearP1State *,uint64_t call);
void rear_p1_emit(RearP1State *,uint64_t tick,uint64_t call,unsigned ordinal,unsigned slot,unsigned port,unsigned bay,
 unsigned record,unsigned player,unsigned phase,unsigned raw,const RearP1Shot *,bool scope,bool table,bool source);
bool rear_p1_current(RearP1State *,unsigned slot,unsigned index,unsigned raw,
 const RearP1Shot *,bool scope,bool table,bool source);
#endif
