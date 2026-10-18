/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef SECRET_EXIT_ORB_H
#define SECRET_EXIT_ORB_H
#include <stdint.h>
/* Three fixed 24x28 composites. The original engine owns the held-twice pulse. */
int secret_exit_orb_phase(unsigned base);
/* Palette-aware 8x analytic art; invalid bases return NULL. */
uint8_t *secret_exit_orb_rgba(unsigned base,const uint32_t palette[256]);
#endif
