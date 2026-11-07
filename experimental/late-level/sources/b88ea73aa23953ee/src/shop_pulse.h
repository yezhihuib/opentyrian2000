/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef SHOP_PULSE_H
#define SHOP_PULSE_H
#include <stdbool.h>
#include <stddef.h>
void shop_pulse_port_name(unsigned port,unsigned length,const char *name);
void shop_pulse_port_loaded(unsigned port);
void shop_pulse_reset(void);
size_t shop_pulse_proof_bytes(void);
void shop_pulse_preview_begin(bool authorized);
void shop_pulse_preview_end(void);
void shop_pulse_front_begin(unsigned port,unsigned bay,unsigned level,unsigned mode,unsigned pnum,unsigned record);
void shop_pulse_front_end(void);
void shop_pulse_allocated(unsigned slot);
void shop_pulse_initialized(unsigned slot,unsigned port,unsigned bay,unsigned record,unsigned pnum,unsigned phase);
bool shop_pulse_head(unsigned slot,unsigned index,int x,int y);
bool shop_pulse_records_valid(void);
void pregame_shop_pulse_set_directory(const char *);
void pregame_shop_pulse_preview_begin(void);
void pregame_shop_pulse_preview_end(void);
void pregame_shop_pulse_head_begin(unsigned slot,unsigned index,int x,int y);
void pregame_shop_pulse_head_end(void);
#endif
