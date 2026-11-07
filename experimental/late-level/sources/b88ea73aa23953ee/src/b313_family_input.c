#include "b313_family_input.h"

#if (defined(B313_FAMILY_OBSERVER_DIAGNOSTIC) && B313_FAMILY_OBSERVER_DIAGNOSTIC) || \
    (defined(B313_FAMILY_CANVAS_DIAGNOSTIC) && B313_FAMILY_CANVAS_DIAGNOSTIC)
#include "b313_family_observer.h"
#include "b313_family_cache.h"
#include "b313_family_writer.h"
#include "b313_family_canvas.h"
#include "render_mirror.h"
#include <stdio.h>

static bool canvas_requested(void)
{
#if defined(B313_FAMILY_CANVAS_DIAGNOSTIC) && B313_FAMILY_CANVAS_DIAGNOSTIC
 return render_mirror_family_requested();
#else
 return false;
#endif
}

static void canvas_release(void)
{
#if defined(B313_FAMILY_CANVAS_DIAGNOSTIC) && B313_FAMILY_CANVAS_DIAGNOSTIC
 render_mirror_release_texture();
#endif
}

static void canvas_report(void)
{
#if defined(B313_FAMILY_CANVAS_DIAGNOSTIC) && B313_FAMILY_CANVAS_DIAGNOSTIC
 render_mirror_family_report();
#endif
}

static B313FamilyCanvasStatus canvas_status(void)
{
#if defined(B313_FAMILY_CANVAS_DIAGNOSTIC) && B313_FAMILY_CANVAS_DIAGNOSTIC
 return render_mirror_family_status();
#else
 return(B313FamilyCanvasStatus){0};
#endif
}

static bool requested(void)
{
 /* Invalid nonzero configuration is still a request to fail closed. */
 return b313_family_observer_enabled()||canvas_requested();
}

void b313_family_input_consumed(Uint32 type)
{
 if(!requested())return;
 /* Never use observer_event here: it intentionally requires a script frame.
  * These two revocations also cover already sealed but unpresented frames. */
 b313_family_observer_external_event();
 b313_family_writer_gap(B313FW_GAP);
 if((type==SDL_RENDER_DEVICE_RESET||type==SDL_RENDER_TARGETS_RESET)&&canvas_requested()){
  /* This existing operation revokes the family canvas generation and its
   * writer, destroys/nulls the texture, and forces fresh texture ownership
   * on the next legitimate present. It cannot grant any new qualification.
   * Never touch the legacy renderer when the new canvas is not requested. */
  canvas_release();
 }
}

void b313_family_input_quit(void)
{
 if(!requested())return;
 const bool canvas=canvas_requested();
 b313_family_observer_external_event();
 b313_family_writer_gap(B313FW_GAP);
 /* Existing reasons 1..4 denote other session exits; 5 is SDL_QUIT. */
 b313_family_observer_finish(5);
 /* Also close explicitly when no observer session/report was pending. */
 b313_family_cache_close();
 b313_family_writer_reset();
 if(canvas){canvas_release();canvas_report();}

 /* A final, non-authorizing receipt even for a QUIT before session begin.
  * Existing observer/canvas report schemas and status layouts stay intact. */
 B313FamilyObserverStatus observer=b313_family_observer_status();
 B313FamilyCacheStatus cache=b313_family_cache_status();
 B313FamilyWriterStatus writer=b313_family_writer_status();
 B313FamilyCanvasStatus display=canvas_status();
 fprintf(stderr,"B313_FAMILY_INPUT_QUIT observer_active=%u observer_frame_open=%u observer_failed=%u cache_ready=%u cache_frame_open=%u writer_active=%u writer_valid=%u canvas_requested=%u canvas_frame_active=%u canvas_ready=%u write_allowed=0 runtime_eligible=0 production_enabled=0\n",
  (unsigned)observer.active,(unsigned)observer.frame_open,(unsigned)observer.failed,
  (unsigned)cache.ready,(unsigned)cache.frame_open,(unsigned)writer.active,
  (unsigned)writer.valid,(unsigned)canvas,(unsigned)display.frame_active,
  (unsigned)display.ready);
}
#else
typedef int b313_family_input_disabled_translation_unit;
#endif
