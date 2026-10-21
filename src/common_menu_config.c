/* SPDX-License-Identifier: GPL-2.0-or-later
 * Configuration/provider bridge only. No scene, gameplay or input authority. */
#include "common_menu_config.h"
#include "common_menu_runs.h"
#include "common_pause.h"
#include "game_probe.h"
#include <string.h>
static bool enabled;
static uint64_t esc_generation;
static bool acquire(void *context)
{
 (void)context;
 if(!enabled || game_probe_original_reference || !common_menu_runs_load(COMMON_MENU_ESC))return false;
 esc_generation=common_menu_runs_generation(COMMON_MENU_ESC);return true;
}
static bool valid(void *context)
{
 (void)context;
 return enabled && !game_probe_original_reference && esc_generation && common_menu_runs_ready(COMMON_MENU_ESC) && esc_generation==common_menu_runs_generation(COMMON_MENU_ESC);
}
static bool get(void *context,unsigned id,CommonPauseNaturalRun *out)
{
 CommonMenuRun run;
 if(!out || !valid(context) || id>=16 || !common_menu_runs_get(COMMON_MENU_ESC,id,&run) || strcmp(run.text,common_pause_esc_text(id)))return false;
 out->x=run.dx;out->y=run.dy;out->width=run.width;out->height=run.height;out->pitch=run.pitch;out->alpha=run.alpha;out->roles=run.roles;return true;
}
static void release(void *context){(void)context;esc_generation=0;}
bool common_menu_configure(const char *directory)
{
 static const CommonPauseEscProvider provider={NULL,acquire,valid,get,release};
 if(directory && (!*directory || strlen(directory)>=1024))return false;
 common_pause_end();
 if(!common_menu_runs_set_directory(directory))return false;
 enabled=directory!=NULL;esc_generation=0;
 common_pause_set_directory(directory);
 common_pause_set_esc_provider(enabled?&provider:NULL);
 return true;
}
bool common_menu_configured(void){return enabled && !game_probe_original_reference;}
