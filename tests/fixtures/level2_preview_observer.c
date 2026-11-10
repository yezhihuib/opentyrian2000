/* Read-only actual-Present observer. Never linked by a normal game build. */
#include "SDL.h"
#include "game_probe.h"
#include "b313_family_canvas.h"
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
  fputs("tick,failed,accepted,fallback,presents\n",stream);
 }
 fprintf(stream,"%u,%u,%"PRIu64",%"PRIu64",%"PRIu64"\n",game_probe_tick,
         status.frame_failed,status.accepted_frames,status.fallback_frames,status.presents);
 if (fflush(stream)) abort();
 __real_SDL_RenderPresent(renderer);
}
