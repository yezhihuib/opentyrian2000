/* Private, diagnostic-only last-write tags. No rendering/admission API. */
#ifndef OLD_HD_SAMPLE_OBSERVER_H
#define OLD_HD_SAMPLE_OBSERVER_H
#include "SDL.h"
#include <stdbool.h>
#include <stdint.h>
#include "native_writer_lineage.h"
enum { OHS_UNKNOWN=0, OHS_CLASSIC=1, OHS_OLD_HD=2 };
enum { OHS_PALETTE=0, OHS_BLEND=1, OHS_SHADOW=2, OHS_FAIL_PALETTE=3,
 OHS_FINAL_PALETTE=4, OHS_OUTPUT_FALLBACK=5, OHS_OPERATION_COUNT=6 };
enum { OHS_GAP_CANVAS=1, OHS_GAP_GLOBALS=2, OHS_GAP_UI_CACHE=4,
 OHS_GAP_TEXTURE=8, OHS_GAP_SOURCE_AUDIT=16 };
enum { OHS_REASON_ORDER=1, OHS_REASON_GEOMETRY=2, OHS_REASON_PALETTE=4,
 OHS_REASON_SCOPE=8, OHS_REASON_RESET=16, OHS_REASON_PRESENT=32,
 OHS_REASON_OVERFLOW=64, OHS_REASON_ALLOCATION=128 };
typedef struct {
 uint64_t epoch, reasons, coverage_gaps, operations[OHS_OPERATION_COUNT], transitions[3][3];
 uint64_t upscale_samples[2], crop_samples, talon_copy[3], barriers[3], texture_samples;
 unsigned tick, density, phase, canvas_rows, output_rows, crop_rows, texture_rows;
 unsigned talon_calls, present_count;
 bool selected, valid_subset, bound, staged, committed;
 /* Always false: no source/callgraph or final OLD_HD coverage claim. */
 bool coverage_complete, eligible;
} OhsStatus;
enum { OHS_CP_CONTEXT=1, OHS_CP_EVENT=2, OHS_CP_SAMPLE=4, OHS_CP_MISSING=8,
 OHS_CP_IDENTITY=16, OHS_CP_FONT=32, OHS_CP_OVERFLOW=64 };
typedef struct {
 bool enabled,valid_at_write,finished,pending;
 uint64_t reasons,lease,scene,frame,group,events,complete_events,samples,unique_samples,bottom_samples,missing_samples;
 unsigned calls,closed_calls,font_stages,font_rects;
} OhsCanvasStatus;
typedef struct { bool failed; unsigned attempts,successful_writes,error; } OhsIoStatus;
enum { OHS_SURVIVAL_ID=1, OHS_SURVIVAL_CONTEXT=2, OHS_SURVIVAL_ORDER=4,
 OHS_SURVIVAL_ALLOCATION=8, OHS_SURVIVAL_INCOMPLETE=16, OHS_SURVIVAL_STORM=32,
 OHS_SURVIVAL_UNKNOWN=64, OHS_SURVIVAL_REVOKED=128 };
#define OHS_SURVIVAL_WRITER_LIMIT 141u
typedef struct {
 bool enabled,valid_subset,staged,committed;
 uint64_t reasons,writer_events[OHS_SURVIVAL_WRITER_LIMIT],roi_events[OHS_SURVIVAL_WRITER_LIMIT];
 uint64_t armed,retired[3],copies[3],canvas_before_crop,output_after_crop,output_before_texture,texture_at_stage;
 unsigned first_retiring_writer,storm_checks;
} OhsSurvivalStatus;
#if defined(OLD_HD_SAMPLE_OBSERVER_DIAGNOSTIC) && OLD_HD_SAMPLE_OBSERVER_DIAGNOSTIC
extern bool ohs_survival_active;
void ohs_survival_write(SDL_Surface *surface,void *address,unsigned writer);
void ohs_survival_copy(SDL_Surface *dst,void *address,SDL_Surface *src,const void *source,unsigned writer,bool ordinary);
void ohs_survival_unknown(unsigned reason);
void ohs_survival_storm_scope(bool scope);
const OhsSurvivalStatus *ohs_survival_status(void);
uint64_t ohs_survival_token(unsigned domain,int x,int y);
#define OHS_SURVIVAL_WRITE(s,p,w) do { if(ohs_survival_active)ohs_survival_write((s),(p),(w)); } while(0)
#define OHS_SURVIVAL_COPY(d,p,s,q,w,o) do { if(ohs_survival_active)ohs_survival_copy((d),(p),(s),(q),(w),(o)); } while(0)
#define OHS_SURVIVAL_STORM(s) do { if(ohs_survival_active)ohs_survival_storm_scope(s); } while(0)
#define OHS_SURVIVAL_UNKNOWN(r) do { if(ohs_survival_active)ohs_survival_unknown(r); } while(0)
void ohs_begin(unsigned tick,bool scope,int density);
void ohs_native_call_begin(uint64_t lease,const NwlIdentity *id,SDL_Surface *surface);
void ohs_native_event(uint64_t lease,const NwlIdentity *id,uint64_t event,size_t offset);
void ohs_native_call_end(NwlToken token,uint64_t first,uint64_t last);
void ohs_native_palette(SDL_Surface *native,const void *address,SDL_Surface *canvas,void *sample,int normal);
void ohs_font_scope(unsigned stage,const SDL_Rect rects[5],unsigned mask);
bool ohs_canvas_observing(void);
const OhsCanvasStatus *ohs_canvas_status(void);
OhsIoStatus ohs_io_status(void);
void ohs_bind(SDL_Surface *canvas,SDL_Surface *output,SDL_Surface *native_canvas,SDL_Surface *native_output,const Uint32 *palette);
void ohs_upscale_row(SDL_Surface *dst,SDL_Surface *src,int row);
void ohs_talon_begin(void);
void ohs_write(SDL_Surface *surface,void *address,unsigned operation,unsigned alpha);
void ohs_copy_sample(SDL_Surface *dst,void *address,SDL_Surface *src,const void *source);
void ohs_finish_begin(bool ordinary);
void ohs_canvas_unknown(void);
void ohs_crop_row(SDL_Surface *dst,SDL_Surface *src,int row,int density);
void ohs_output_unknown(void);
void ohs_finish_end(void);
void ohs_present_begin(SDL_Surface *src,const Uint32 *palette);
void ohs_texture_begin(void *pixels,int pitch);
void ohs_texture_row(int row);
void ohs_stage(void);
void ohs_commit(unsigned presents);
void ohs_revoke(unsigned reason);
bool ohs_present_fail(void);
const OhsStatus *ohs_status(void);
/* Partial internal test view, never an eligibility/final-source query. */
unsigned ohs_partial_tag(unsigned domain,int x,int y);
#else
#define OHS_SURVIVAL_WRITE(...) ((void)0)
#define OHS_SURVIVAL_COPY(...) ((void)0)
#define OHS_SURVIVAL_STORM(...) ((void)0)
#define OHS_SURVIVAL_UNKNOWN(...) ((void)0)
#define ohs_begin(...) ((void)0)
#define ohs_native_call_begin(...) ((void)0)
#define ohs_native_event(...) ((void)0)
#define ohs_native_call_end(...) ((void)0)
#define ohs_native_palette(...) ((void)0)
#define ohs_font_scope(...) ((void)0)
#define ohs_canvas_observing() false
#define ohs_bind(...) ((void)0)
#define ohs_upscale_row(...) ((void)0)
#define ohs_talon_begin(...) ((void)0)
#define ohs_write(...) ((void)0)
#define ohs_copy_sample(...) ((void)0)
#define ohs_finish_begin(...) ((void)0)
#define ohs_canvas_unknown(...) ((void)0)
#define ohs_crop_row(...) ((void)0)
#define ohs_output_unknown(...) ((void)0)
#define ohs_finish_end(...) ((void)0)
#define ohs_present_begin(...) ((void)0)
#define ohs_texture_begin(...) ((void)0)
#define ohs_texture_row(...) ((void)0)
#define ohs_stage(...) ((void)0)
#define ohs_commit(...) ((void)0)
#define ohs_revoke(...) ((void)0)
#define ohs_present_fail() false
#endif
#endif
