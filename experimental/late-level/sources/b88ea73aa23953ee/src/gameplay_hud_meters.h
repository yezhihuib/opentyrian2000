/* Finite, optional HUM2 material sampler. No SDL or original-data dependency. */
#ifndef GAMEPLAY_HUD_METERS_H
#define GAMEPLAY_HUD_METERS_H
#include <stdbool.h>
#include <stdint.h>
enum { HUD_METER_FRONT=4, HUD_METER_REAR=8, HUD_METER_GENERATOR=16,
       HUD_METER_ARMOR=32, HUD_METERS_ALL=60 };
enum { HUD_WRITE_FRONT, HUD_WRITE_REAR, HUD_WRITE_GENERATOR,
       HUD_WRITE_ARMOR_WIPE, HUD_WRITE_ARMOR_DRAW };
/* One attempt per shutdown, one fixed621808-byte allocation; independent HUC1.
 * Capture requires200 readable320-byte rows and pristine PIC3. Blank armor is
 * distinct from A0. No allocation/I/O after load. */
bool hud_meters_load(const char *directory);
bool hud_meters_capture(const uint8_t *indices,int pitch);
void hud_meters_forget_source(void);
void hud_meters_shutdown(void);
bool hud_meters_ready(void);
bool hud_meters_palette_matches(const uint32_t palette[256]);
unsigned hud_meters_event_bits(unsigned kind);
void hud_meters_revoke(unsigned bits);
/* Observe original writes: a=P for front/rear; a=old_q,b=new_q for generator;
 * a=pre-clamp A for wipe, post-clamp A for draw. Caller removes affected cached
 * RGB before writing and verifies source/mode/generation at both notifications.
 * End compares all current indices against accepted history plus the exact
 * original write. Invalid partial history renews only with a full real write. */
void hud_meters_write_begin(unsigned kind,unsigned a,unsigned b);
bool hud_meters_write_end(unsigned kind,const uint8_t *indices,int pitch);
/* Atomic per-field preparation immediately before ordinary compose. Mismatch
 * revokes only that field, never creates history from a plausible pattern. */
unsigned hud_meters_prepare(const uint8_t *indices,int pitch);
const uint8_t *hud_meters_sample(int x,int y,int sx,int sy,int density,
                                 uint8_t current_index);
#endif
