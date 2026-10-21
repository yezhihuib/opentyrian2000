/* SPDX-License-Identifier: GPL-2.0-or-later
 * Reconstructed shared natural-run resource interface. Runtime uses immutable
 * packaged masks, never a host font or a font rasterizer. */
#ifndef COMMON_MENU_RUNS_H
#define COMMON_MENU_RUNS_H
#include "SDL.h"
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
enum CommonMenuFamily {
 COMMON_MENU_ESC, COMMON_MENU_MAIN, COMMON_MENU_SHOP,
 COMMON_MENU_CATEGORY, COMMON_MENU_PRODUCT, COMMON_MENU_NAMES,
 COMMON_MENU_FAMILY_COUNT
};
typedef struct CommonMenuRun {
 /* All raster positions are canonical4 pixels. advance256 is canonical4
  * pixels multiplied by256, not logical game pixels. */
 int dx,dy;
 unsigned width,height,pitch,advance256;
 const Uint8 *alpha,*roles,*stroke;
 const char *text;
 unsigned role_min,role_max;
} CommonMenuRun;
/* NULL disables. Every root change retires all borrowed views. Callers must
 * validate readiness/generation immediately before replay; cached resource
 * bytes are private and load-once, not a filesystem hot-reload promise. */
bool common_menu_runs_set_directory(const char *);
bool common_menu_runs_load(enum CommonMenuFamily);
bool common_menu_runs_ready(enum CommonMenuFamily);
void common_menu_runs_shutdown(enum CommonMenuFamily);
void common_menu_runs_shutdown_all(void);
unsigned common_menu_runs_count(enum CommonMenuFamily);
uint64_t common_menu_runs_generation(enum CommonMenuFamily);
bool common_menu_runs_get(enum CommonMenuFamily,unsigned id,CommonMenuRun *);
int common_menu_runs_find(enum CommonMenuFamily,const char *exact_display_text);
size_t common_menu_runs_retained_bytes(void);
/* Numeric packed family is independent from the six complete-run families.
 * Numeric admission/economy authority belongs to the original draw observer,
 * not this raster layout API. */
enum { COMMON_MENU_NUMERIC_MAX_TOKENS=20 };
typedef struct CommonMenuNumericPlacement {unsigned mask;int x,y;} CommonMenuNumericPlacement;
typedef struct CommonMenuNumericRun {
 unsigned count,width,height,advance256;
 int dx,dy;
 CommonMenuNumericPlacement token[COMMON_MENU_NUMERIC_MAX_TOKENS];
} CommonMenuNumericRun;
bool common_menu_numeric_runs_load(void);
bool common_menu_numeric_runs_ready(void);
void common_menu_numeric_runs_shutdown(void);
uint64_t common_menu_numeric_runs_generation(void);
bool common_menu_numeric_runs_layout(const char *,CommonMenuNumericRun *);
bool common_menu_numeric_runs_sample(const CommonMenuNumericRun *,int x,int y,Uint8 *alpha,Uint8 *role);
size_t common_menu_numeric_runs_retained_bytes(void);
#endif
