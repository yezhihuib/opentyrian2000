/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef SHOP_VULCAN_H
#define SHOP_VULCAN_H
#include <stdbool.h>
#include <stddef.h>
void shop_vulcan_port_name(unsigned port,unsigned length,const char *name);
void shop_vulcan_port_loaded(unsigned port);
void shop_vulcan_reset(void);
size_t shop_vulcan_proof_bytes(void);
void shop_vulcan_preview_begin(bool authorized);
void shop_vulcan_preview_end(void);
void shop_vulcan_front_begin(unsigned port,unsigned bay,unsigned level,unsigned mode,unsigned pnum,unsigned record);
void shop_vulcan_front_end(void);
void shop_vulcan_allocated(unsigned slot,int px,int py,int mx,int my);
void shop_vulcan_initialized(unsigned slot,unsigned port,unsigned bay,unsigned record,unsigned pnum,unsigned phase);
bool shop_vulcan_head(unsigned slot,unsigned index,int x,int y);
bool shop_vulcan_records_valid(void);
void pregame_shop_vulcan_set_directory(const char *);
void pregame_shop_vulcan_preview_begin(void);
void pregame_shop_vulcan_preview_end(void);
void pregame_shop_vulcan_head_begin(unsigned slot,unsigned index,int x,int y);
void pregame_shop_vulcan_head_end(void);
#endif
