/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef ENEMY_WIDGET_SONIC_POLICY_H
#define ENEMY_WIDGET_SONIC_POLICY_H
#include <stdbool.h>
#include "game_probe.h"
#include "enemy_reuse_observe.h"
#include "enemy_reuse_probe.h"
static inline bool widget_sonic_member_index(unsigned index)
{return index==20||index==21||index==105||index==106||index==124||index==125;}
/* Requested/revoked legacy sessions cannot lend ordinary enemy authority. */
static inline bool widget_sonic_legacy_intent(void)
{
#if defined(ENEMY_REUSE_HD_PROTOTYPE) && ENEMY_REUSE_HD_PROTOTYPE && !defined(RENDER_MIRROR_DISABLED)
 return game_probe_enabled||enemy_reuse_observe_requested()||enemy_reuse_probe_requested();
#else
 return false;
#endif
}
#endif
