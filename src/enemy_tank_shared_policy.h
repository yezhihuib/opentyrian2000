/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef ENEMY_TANK_SHARED_POLICY_H
#define ENEMY_TANK_SHARED_POLICY_H
#include <stddef.h>
#include "enemy_widget_sonic_policy.h"
static inline bool tank_shared_member_index(unsigned index)
{return index==146||index==147;}
/* Generic debug-enabled alone is not a legacy tank resource request.
 * Legacy tank art exists even with ENEMY_REUSE_HD_PROTOTYPE disabled.
 * A requested empty/broken legacy root still owns the lane; never lend its
 * failed authorization to the ordinary global owner. */
static inline bool tank_shared_legacy_intent(void)
{return game_probe_assets!=NULL||widget_sonic_legacy_intent();}
static inline bool tank_shared_ordinary_allowed(unsigned index)
{return tank_shared_member_index(index)&&!tank_shared_legacy_intent();}
#endif
