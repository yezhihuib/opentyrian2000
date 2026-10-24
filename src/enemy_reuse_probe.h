/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef ENEMY_REUSE_PROBE_H
#define ENEMY_REUSE_PROBE_H
#include <stdbool.h>
#include <stdint.h>
#if defined(ENEMY_REUSE_HD_PROTOTYPE) && ENEMY_REUSE_HD_PROTOTYPE && !defined(RENDER_MIRROR_DISABLED)
bool enemy_reuse_probe_requested(void);
uint64_t enemy_reuse_probe_generation(void);
void enemy_reuse_probe_revoke(void);
#else
static inline bool enemy_reuse_probe_requested(void) {return false;}
static inline uint64_t enemy_reuse_probe_generation(void) {return 0;}
static inline void enemy_reuse_probe_revoke(void) {}
#endif
#endif
