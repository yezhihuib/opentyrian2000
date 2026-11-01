/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef ENEMY_ORB_PROTRON_POLICY_H
#define ENEMY_ORB_PROTRON_POLICY_H
#include "enemy_widget_sonic_policy.h"
static inline bool orb_protron_orb_index(unsigned index)
{return index==112||index==113;}
static inline bool orb_protron_protron_index(unsigned index)
{return index==226||index==227;}
static inline bool orb_protron_member_index(unsigned index)
{return orb_protron_orb_index(index)||orb_protron_protron_index(index);}
static inline bool orb_protron_ordinary_allowed(unsigned index)
{
#if defined(ENEMY_REUSE_HD_PROTOTYPE) && ENEMY_REUSE_HD_PROTOTYPE && !defined(RENDER_MIRROR_DISABLED)
 if(enemy_reuse_observe_requested())return false;
#endif
 if(orb_protron_orb_index(index))return !asteroid_hd_enabled;
 if(orb_protron_protron_index(index))return !widget_sonic_legacy_intent();
 return false;
}
#endif
