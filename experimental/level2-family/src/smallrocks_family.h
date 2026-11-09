#ifndef SMALLROCKS_FAMILY_H
#define SMALLROCKS_FAMILY_H
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
typedef struct {uint8_t x,y,index;} SmallRocksWrite;
typedef struct {
 uint64_t frame,epoch,token,generation;
 unsigned slot,record,base,cur_loc,bank_role,bank_bytes,callback_count;
 uintptr_t bank_object,bank_data;
 int x,y;
 bool complete;
} SmallRocksDraw;
typedef struct {
 bool requested,loaded,contributed,failed,accepted;
 uint64_t frame,blend_retirements,normal_retirements,shadow_writes;
 uint64_t clipped,unwitnessed,lifetime_losses,bank_losses,contract_faults;
 unsigned first_reason;
 unsigned material_mask,surviving_cells,shadowed_cells;
 SmallRocksDraw draw[25];
} SmallRocksFamilyStatus;
/* Read-only diagnostics. No getter grants admission or enables gameplay.
 * Pre-draw is available after accepted tile entry, before its first native
 * store. It copies only the actual 96x112 canvas crop and 12x14 source bytes.
 * Callback receipts persist until next frame; x/y are local native positions.
 * Support is valid inside the accepted frame's Present wrappers. Owner byte
 * is slot+1, joined to the draw's generation/token. Shadow byte counts verified
 * native shadows, saturating at255, independently of selected[]. */
SmallRocksFamilyStatus render_mirror_smallrocks_family_status(void);
bool render_mirror_smallrocks_pre_draw(SmallRocksDraw *,uint32_t *,size_t,uint8_t *,size_t);
unsigned render_mirror_smallrocks_callbacks(unsigned,SmallRocksWrite *,size_t);
bool render_mirror_smallrocks_family_support(uint8_t *,size_t,uint8_t *,size_t);
#endif
