/* SPDX-License-Identifier: GPL-2.0-or-later */
#ifndef LAUNCHER271_LINEAGE_H
#define LAUNCHER271_LINEAGE_H
#include <stdbool.h>
#include <stdint.h>

/* Observation only: none of these receipts grants permission to render.
 * Slots are zero-based; native allocation results and events are one-based.
 * Birth fields are immutable until actual slot reallocation or level reset.
 * The live flag is separate from the immutable birth and never follows a
 * parent after a child's birth. No pointer returned here can mutate state. */
typedef struct {
 uint64_t session,token,generation,frame,resource_epoch;
 uint64_t parent_token,parent_generation,parent_frame;
 unsigned slot,record,event,parent_slot,bank,physical_bank;
 int allocation_result,x,y,parent_x,parent_y,unique_shape;
 unsigned source_cycle,source_base;
} Launcher271Birth;
typedef struct {
 bool present,current;
 Launcher271Birth birth;
 uint64_t retired_frame;
 unsigned retirement_reason;
} Launcher271Receipt;
typedef struct {
 bool enabled,loaded,exhausted;
 uint64_t session,frame,serial,resource_epoch,allocation_serial;
 uint64_t parents,children,launch_attempts,no_child_results,retirements;
 unsigned event_consumed;
 int last_allocation_result;
} Launcher271Status;
Launcher271Receipt launcher271_lineage_receipt(unsigned slot);
Launcher271Status launcher271_lineage_status(void);
#endif
