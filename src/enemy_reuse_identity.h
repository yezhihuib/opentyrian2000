/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef ENEMY_REUSE_IDENTITY_H
#define ENEMY_REUSE_IDENTITY_H
#include <stdbool.h>
#include <stdint.h>
#if defined(ENEMY_REUSE_HD_PROTOTYPE) && ENEMY_REUSE_HD_PROTOTYPE && !defined(RENDER_MIRROR_DISABLED)
void enemy_reuse_reset(void);
void enemy_reuse_bank_changed(const void *);
uint64_t enemy_reuse_identity_generation(unsigned);
void enemy_reuse_actor_allocated(void *,unsigned,int);
void enemy_reuse_actor_initialized(void *,unsigned,unsigned);
void enemy_reuse_shot_spawn(unsigned,unsigned,unsigned,unsigned,unsigned);
void enemy_reuse_shot_retire(unsigned);
void enemy_reuse_shot_begin_draw(unsigned);
void enemy_reuse_shot_before_animation(unsigned);
void enemy_reuse_shot_after_animation(unsigned);
bool enemy_reuse_identity_matches(unsigned,unsigned,int,int);
bool enemy_reuse_identity_live(unsigned,unsigned,int,int);
void enemy_reuse_draw_end(void);
#else
static inline void enemy_reuse_reset(void) {}
static inline void enemy_reuse_bank_changed(const void *p) {(void)p;}
static inline uint64_t enemy_reuse_identity_generation(unsigned s) {(void)s;return 0;}
static inline void enemy_reuse_actor_allocated(void *p,unsigned r,int u) {(void)p;(void)r;(void)u;}
static inline void enemy_reuse_actor_initialized(void *p,unsigned r,unsigned a) {(void)p;(void)r;(void)a;}
static inline void enemy_reuse_shot_spawn(unsigned s,unsigned a,unsigned w,unsigned t,unsigned p) {(void)s;(void)a;(void)w;(void)t;(void)p;}
static inline void enemy_reuse_shot_retire(unsigned s) {(void)s;}
static inline void enemy_reuse_shot_begin_draw(unsigned s) {(void)s;}
static inline void enemy_reuse_shot_before_animation(unsigned s) {(void)s;}
static inline void enemy_reuse_shot_after_animation(unsigned s) {(void)s;}
static inline void enemy_reuse_draw_end(void) {}
static inline bool enemy_reuse_identity_live(unsigned s,unsigned i,int x,int y) {(void)s;(void)i;(void)x;(void)y;return false;}
static inline bool enemy_reuse_identity_matches(unsigned s,unsigned i,int x,int y) {(void)s;(void)i;(void)x;(void)y;return false;}
#endif
#endif
