/* Real diagnostic adapter; no game loop or SDL window is started. */
#include "game_probe.c"
#include <assert.h>
int manual_probe_test(void)
{
 assert(!game_probe_enabled&&!asset_debug_enabled&&game_probe_tick==0);
 manual_hd_enabled=true;
 presentations=tmpfile();assert(presentations);
 /* A nonnull sentinel detects any unguarded window access before early return. */
 main_window=(SDL_Window *)(uintptr_t)1;
 game_probe_present(1,23,23);assert(ftell(presentations)==0&&!sdl_runtime_recorded);
 assert(!game_probe_capture_tick());
 main_window=NULL;game_probe_enabled=true;
 game_probe_present(1,23,23);assert(ftell(presentations)>0);
 assert(game_probe_capture_tick());no_capture=true;assert(!game_probe_capture_tick());
 fclose(presentations);presentations=NULL;
 puts("disabled diagnostics and enabled probe regression units passed");return 0;
}
