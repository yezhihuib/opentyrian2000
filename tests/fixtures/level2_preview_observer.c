/* Read-only actual-Present observer. Never linked by a normal game build. */
#include "SDL.h"
#include "game_probe.h"
#include "b313_family_canvas.h"
#ifdef TERRAIN_FALLBACK_OBSERVER
#include "b313_terrain_fallback.h"
#endif
#include <stdio.h>
#include <stdlib.h>
#include <inttypes.h>
static FILE *stream;
void __real_SDL_RenderPresent(SDL_Renderer *renderer);
void __wrap_SDL_RenderPresent(SDL_Renderer *renderer)
{
 B313FamilyCanvasStatus status=render_mirror_family_status();
 if (!status.frames) { __real_SDL_RenderPresent(renderer); return; }
 if (!stream) {
  stream=fopen("continuity-present.csv","w");
  if (!stream) abort();
  fputs("tick,failed,accepted,fallback,presents,terrain_presenting,terrain_prepared,terrain_presents,terrain_cells,blend_fallbacks\n",stream);
 }
 unsigned terrain_presenting=0,terrain_cells=0;
 uint64_t terrain_prepared=0,terrain_presents=0;
#ifdef TERRAIN_FALLBACK_OBSERVER
 B313TerrainFallbackStatus terrain=render_mirror_terrain_fallback_status();
 terrain_presenting=terrain.presenting;terrain_cells=terrain.surviving_cells;
 terrain_prepared=terrain.prepared;terrain_presents=terrain.presents;
#endif
 fprintf(stream,"%u,%u,%"PRIu64",%"PRIu64",%"PRIu64",%u,%"PRIu64",%"PRIu64",%u,%"PRIu64"\n",game_probe_tick,
         status.frame_failed,status.accepted_frames,status.fallback_frames,status.presents,
         terrain_presenting,terrain_prepared,terrain_presents,terrain_cells,status.blend_fallbacks);
 if (fflush(stream)) abort();
 __real_SDL_RenderPresent(renderer);
}
