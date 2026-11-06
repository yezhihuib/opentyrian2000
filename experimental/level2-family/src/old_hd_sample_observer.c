#include "b313_v6_recovery.h"
#include "b313_v6_sequence.h"
#include "b313_v6_slice.h"
/* SPDX-License-Identifier: GPL-2.0-or-later
 * Private first slice: samples, not pixels/RGB equality/owner bits.
 * The unadapted writer set is deliberately NOT closed. All final queries remain
 * UNKNOWN regardless of partial tags or subsequent opaque writes.
 */
#include "old_hd_sample_observer.h"
#include "building313_final_proof.h"
#include "building313_precommit.h"
#if defined(OLD_HD_SAMPLE_OBSERVER_DIAGNOSTIC) && OLD_HD_SAMPLE_OBSERVER_DIAGNOSTIC
#include <limits.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define OHS_MAX_SAMPLES ((size_t)320*200*8*8)
typedef struct { SDL_Surface *s; void *pixels; SDL_PixelFormat *format; int w,h,pitch; Uint32 code; } Lease;
static OhsStatus st;
static OhsCanvasStatus cp;
static OhsIoStatus io;
static OhsSurvivalStatus sv;
bool ohs_survival_active;
static uint64_t *survival_tokens[3];
static size_t survival_capacity,survival_samples;
static void survival_fail(unsigned reason);
static void survival_arm(size_t index,uint64_t event);
static void survival_row(unsigned domain,int row,unsigned writer);
static void survival_crop(int row);
static void survival_texture(int row);
static uint64_t survival_count(unsigned domain);
#define OHS_CP_CALLS 128u
#define OHS_CP_ROI_SAMPLES (2688u*64u)
struct CpCall {NwlIdentity id;uint64_t first,last;unsigned events;bool closed;};
static struct CpCall cp_calls[OHS_CP_CALLS];
static unsigned cp_current,cp_sample_count;
static uint64_t cp_event,cp_seen;
static size_t cp_offset;
static bool cp_event_live;
static unsigned char cp_roi_seen[OHS_CP_ROI_SAMPLES];
static void canvas_finish(void);

static Lease lease[4];
static Uint8 *tags[3];
static size_t capacity,samples;
static Uint32 palette_pin[256];
static uint64_t serial;
static unsigned previous_tick;
static bool previous_selected;
/* Fixed one-shot 0415 artifact: independent from the revocable live lease. */
static bool presentation_reported;
static int width,height;
static void *texture_pixels;
static int texture_pitch;
static bool canvas_barrier,output_barrier;
#if defined(B313_V6_SEQUENCE_DIAGNOSTIC) && B313_V6_SEQUENCE_DIAGNOSTIC
bool ohs_sequence_frame_retire(void)
{
 if(io.failed||(st.selected&&(!st.valid_subset||!st.committed||st.present_count!=1)))return false;
 presentation_reported=false;memset(&io,0,sizeof(io));return true;
}
#endif
#if defined(B313_V6_RECOVERY_DIAGNOSTIC) && B313_V6_RECOVERY_DIAGNOSTIC
bool ohs_recovery_rearm(void)
{
 if(!b313_recovery_permit_ready()||!b313_recovery_continuity()||io.failed||!st.selected||st.tick!=410||st.valid_subset||st.committed||st.staged||st.reasons!=OHS_REASON_SCOPE||st.present_count||io.successful_writes!=1)return false;
 presentation_reported=false;memset(&io,0,sizeof(io));return true;
}
#endif
static bool io_fail(unsigned reason)
{
 io.failed=true;io.error|=reason;return false;
}
static bool report(void)
{
 if(!st.selected||presentation_reported||io.failed)return false;
 ++io.attempts;
 const char *tmp=b313_slice_path(B313_REPORT_SAMPLES,true);
 FILE *f=fopen(tmp,"w");if(!f)return io_fail(1);
 fprintf(f,"{\n\"schema\":\"partial-sample-tags-v1\",\"tick\":%u,\"epoch\":%" PRIu64 ",\"density\":%u,\n",st.tick,st.epoch,st.density);
 fprintf(f,"\"valid_subset\":%s,\"staged\":%s,\"committed\":%s,\"present_count\":%u,\"reasons\":%" PRIu64 ",\"coverage_gaps\":%" PRIu64 ",\n",st.valid_subset?"true":"false",st.staged?"true":"false",st.committed?"true":"false",st.present_count,st.reasons,st.coverage_gaps);
 fprintf(f,"\"coverage_complete\":false,\"eligible\":false,\"final_roi_query\":\"UNKNOWN\",\"roi_native_cells\":2688,\"roi_samples\":%u,\"bottom_samples\":%u,\n",2688*st.density*st.density,48*st.density*st.density);
 fprintf(f,"\"upscale_canvas\":%" PRIu64 ",\"upscale_output\":%" PRIu64 ",\"crop_samples\":%" PRIu64 ",\"crop_rows\":%u,\"texture_samples\":%" PRIu64 ",\"texture_rows\":%u,\"talon_calls\":%u,\n",st.upscale_samples[0],st.upscale_samples[1],st.crop_samples,st.crop_rows,st.texture_samples,st.texture_rows,st.talon_calls);
 fprintf(f,"\"operations\":[");for(unsigned i=0;i<OHS_OPERATION_COUNT;i++)fprintf(f,"%s%" PRIu64,i?",":"",st.operations[i]);
 fprintf(f,"],\"talon_copy_by_source\":[%" PRIu64 ",%" PRIu64 ",%" PRIu64 "],\"unknown_barriers\":[%" PRIu64 ",%" PRIu64 ",%" PRIu64 "],\n\"transitions\":[",st.talon_copy[0],st.talon_copy[1],st.talon_copy[2],st.barriers[0],st.barriers[1],st.barriers[2]);
 for(unsigned i=0;i<3;i++)for(unsigned j=0;j<3;j++)fprintf(f,"%s%" PRIu64,(i||j)?",":"",st.transitions[i][j]);
 fprintf(f,"],\"canvas_palette_at_write\":{\"enabled\":%s,\"valid\":%s,\"finished\":%s,\"reasons\":%" PRIu64 ",\"lease\":%" PRIu64 ",\"scene\":%" PRIu64 ",\"frame\":%" PRIu64 ",\"group\":%" PRIu64 ",\"calls\":%u,\"closed_calls\":%u,\"native_events\":%" PRIu64 ",\"complete_events\":%" PRIu64 ",\"classic_assignment_samples\":%" PRIu64 ",\"distinct_roi_samples\":%" PRIu64 ",\"bottom_samples\":%" PRIu64 ",\"missing_samples\":%" PRIu64 ",\"font_stages\":%u,\"font_rect_checks\":%u,\"current_canvas_proven\":false,\"calls_detail\":[",cp.enabled?"true":"false",cp.valid_at_write?"true":"false",cp.finished?"true":"false",cp.reasons,cp.lease,cp.scene,cp.frame,cp.group,cp.calls,cp.closed_calls,cp.events,cp.complete_events,cp.samples,cp.unique_samples,cp.bottom_samples,cp.missing_samples,cp.font_stages,cp.font_rects);
 for(unsigned i=0;i<cp.calls;i++){struct CpCall *c=cp_calls+i;fprintf(f,"%s{\"call\":%" PRIu64 ",\"generation\":%" PRIu64 ",\"slot\":%u,\"type\":%u,\"part\":%u,\"x\":%d,\"y\":%d,\"first_event\":%" PRIu64 ",\"last_event\":%" PRIu64 ",\"events\":%u,\"closed\":%s}",i?",":"",c->id.call,c->id.generation,c->id.slot,c->id.type,c->id.part,c->id.x,c->id.y,c->first,c->last,c->events,c->closed?"true":"false");}
 fprintf(f,"],\"timing\":\"at-write events only; not current canvas or final native validity\"},\n");
 fprintf(f,"\"candidate_survival\":{\"enabled\":%s,\"valid_subset\":%s,\"staged\":%s,\"committed\":%s,\"reasons\":%" PRIu64 ",\"armed\":%" PRIu64 ",\"retired\":[%" PRIu64 ",%" PRIu64 ",%" PRIu64 "],\"copies\":[%" PRIu64 ",%" PRIu64 ",%" PRIu64 "],\"canvas_before_crop\":%" PRIu64 ",\"output_after_crop\":%" PRIu64 ",\"output_before_texture\":%" PRIu64 ",\"texture_at_stage\":%" PRIu64 ",\"first_retiring_writer\":%u,\"storm_checks\":%u,\"writer_events\":[",sv.enabled?"true":"false",sv.valid_subset?"true":"false",sv.staged?"true":"false",sv.committed?"true":"false",sv.reasons,sv.armed,sv.retired[0],sv.retired[1],sv.retired[2],sv.copies[0],sv.copies[1],sv.copies[2],sv.canvas_before_crop,sv.output_after_crop,sv.output_before_texture,sv.texture_at_stage,sv.first_retiring_writer,sv.storm_checks);
 for(unsigned i=0;i<OHS_SURVIVAL_WRITER_LIMIT;i++)fprintf(f,"%s%" PRIu64,i?",":"",sv.writer_events[i]);
 fprintf(f,"],\"roi_events\":[");
 for(unsigned i=0;i<OHS_SURVIVAL_WRITER_LIMIT;i++)fprintf(f,"%s%" PRIu64,i?",":"",sv.roi_events[i]);
 fprintf(f,"],\"scope\":\"Frozen finite renderer writes and ordinary transport only. Tokens are instantaneous candidate event provenance, not semantic CLASSIC/OLD_HD or native completeness.\"},\"io_failed\":false,\"limits\":\"Semantic labels remain partial and final query UNKNOWN with gaps31. Unwitnessed raw writes require the pinned source gate, not color comparison. No new HD admission.\"\n}\n");
 bool write_failed=ferror(f)!=0;
 int closed=fclose(f);
 if(write_failed||closed){remove(tmp);return io_fail((write_failed?2u:0u)|(closed?4u:0u));}
 if(rename(tmp,b313_slice_path(B313_REPORT_SAMPLES,false))){remove(tmp);return io_fail(8);}
 ++io.successful_writes;return true;
}
void ohs_revoke(unsigned reason)
{
 if(!st.selected)return;
 survival_fail(OHS_SURVIVAL_REVOKED);
 st.reasons|=reason;st.valid_subset=false;st.staged=st.committed=false;
 /* Multiple reset/present attempts cannot erase the historical artifact. */
 report();
}
static bool alive(void){return st.selected&&st.valid_subset;}
static bool add(uint64_t *v,uint64_t n)
{if(UINT64_MAX-*v<n){ohs_revoke(OHS_REASON_OVERFLOW);return false;}*v+=n;return true;}
static bool capture_lease(Lease *l,SDL_Surface *s,int w,int h,int bpp)
{
 if(!s||!s->pixels||!s->format||s->w!=w||s->h!=h||s->pitch<w*bpp||s->pitch<=0||
 s->format->BytesPerPixel!=bpp||s->format->BitsPerPixel!=8*bpp||
 s->format->format!=(bpp==4?SDL_PIXELFORMAT_ARGB8888:SDL_PIXELFORMAT_INDEX8)||
 (bpp==4&&(s->pitch%4||(uintptr_t)s->pixels%4))||
 (uintptr_t)s->pixels>UINTPTR_MAX-(size_t)s->pitch*h)return false;
 *l=(Lease){s,s->pixels,s->format,w,h,s->pitch,s->format->format};return true;
}
static bool matches(const Lease *l)
{
 SDL_Surface *s=l->s;
 return s&&s->pixels==l->pixels&&s->format==l->format&&s->w==l->w&&s->h==l->h&&s->pitch==l->pitch&&
 s->format&&s->format->format==l->code&&s->format->BytesPerPixel==(l->code==SDL_PIXELFORMAT_INDEX8?1:4)&&
 s->format->BitsPerPixel==(l->code==SDL_PIXELFORMAT_INDEX8?8:32);
}
static bool context(void)
{
 if(!alive())return false;
 if(!st.bound){ohs_revoke(OHS_REASON_ORDER);return false;}
 for(unsigned i=0;i<4;i++)if(!matches(lease+i)){ohs_revoke(OHS_REASON_GEOMETRY);return false;}
 return true;
}
static bool point(SDL_Surface *s,const void *p,unsigned *domain,size_t *index)
{
 if(!alive())return false;
 if(!st.bound){ohs_revoke(OHS_REASON_ORDER);return false;}
 unsigned i=s==lease[0].s?0:s==lease[1].s?1:2;
 if(i==2||!matches(lease+i)){ohs_revoke(OHS_REASON_GEOMETRY);return false;}
 uintptr_t a=(uintptr_t)p,b=(uintptr_t)lease[i].pixels;
 if(a<b||a-b>=(size_t)lease[i].pitch*height){ohs_revoke(OHS_REASON_GEOMETRY);return false;}
 size_t off=a-b,row=off/(unsigned)lease[i].pitch,col=off%(unsigned)lease[i].pitch;
 if(col%4||col>=(size_t)width*4){ohs_revoke(OHS_REASON_GEOMETRY);return false;}
 *domain=i;*index=row*width+col/4;return true;
}
static void set_tag(unsigned domain,size_t index,unsigned value)
{
 unsigned before=tags[domain][index];
 if(!add(&st.transitions[before][value],1))return;
 tags[domain][index]=(Uint8)value;
}
void ohs_begin(unsigned tick,bool scope,int density)
{
 if(st.selected&&!st.committed&&st.valid_subset)ohs_revoke(OHS_REASON_ORDER);
 bool repeat=previous_selected&&previous_tick==tick;
 /* Reset live state, not the historical fixed-capture file lock. */
 memset(&sv,0,sizeof(sv));ohs_survival_active=false;survival_samples=0;
 memset(&st,0,sizeof(st));memset(&cp,0,sizeof(cp));memset(cp_calls,0,sizeof(cp_calls));memset(cp_roi_seen,0,sizeof(cp_roi_seen));cp_event_live=false;cp_sample_count=0;cp_seen=0;
 memset(lease,0,sizeof(lease));samples=0;texture_pixels=NULL;texture_pitch=0;
 canvas_barrier=output_barrier=false;
 const char *enabled=getenv("OLD_HD_SAMPLE_OBSERVER_ENABLE");
 if(!enabled||strcmp(enabled,"1")||!scope||tick!=b313_slice_tick())return;
 st.selected=true;st.tick=tick;st.density=(unsigned)density;
 st.coverage_gaps=OHS_GAP_CANVAS|OHS_GAP_GLOBALS|OHS_GAP_UI_CACHE|OHS_GAP_TEXTURE|OHS_GAP_SOURCE_AUDIT;
 previous_selected=true;previous_tick=tick;
 if(serial==UINT64_MAX){ohs_revoke(OHS_REASON_OVERFLOW);return;}
 st.epoch=++serial;st.valid_subset=true;st.phase=1;
 const char *capture=getenv("BUILDING313_CANVAS_PALETTE_ENABLE");cp.enabled=capture&&strcmp(capture,"1")==0;cp.valid_at_write=cp.enabled;
 const char *survive=getenv("BUILDING313_SAMPLE_SURVIVAL_ENABLE");
 sv.enabled=survive&&strcmp(survive,"1")==0;sv.valid_subset=sv.enabled&&cp.enabled;
 if(sv.enabled&&!cp.enabled)survival_fail(OHS_SURVIVAL_CONTEXT);
 if(repeat||density<1||density>8){ohs_revoke(repeat?OHS_REASON_ORDER:OHS_REASON_SCOPE);return;}
 width=320*density;height=200*density;
}
void ohs_bind(SDL_Surface *c,SDL_Surface *o,SDL_Surface *nc,SDL_Surface *no,const Uint32 *palette)
{
 if(!alive())return;
 if(st.bound||st.phase!=1){ohs_revoke(OHS_REASON_ORDER);return;}
 if(!palette||!capture_lease(lease,c,width,height,4)||!capture_lease(lease+1,o,width,height,4)||
 !capture_lease(lease+2,nc,320,200,1)||!capture_lease(lease+3,no,320,200,1)){ohs_revoke(OHS_REASON_GEOMETRY);return;}
 for(unsigned i=0;i<4;i++)for(unsigned j=i+1;j<4;j++){
  uintptr_t a=(uintptr_t)lease[i].pixels,b=(uintptr_t)lease[j].pixels;
  if(a<b+(size_t)lease[j].pitch*lease[j].h&&b<a+(size_t)lease[i].pitch*lease[i].h){ohs_revoke(OHS_REASON_GEOMETRY);return;}
 }
 samples=(size_t)width*height;
 if(samples>OHS_MAX_SAMPLES){ohs_revoke(OHS_REASON_OVERFLOW);return;}
 if(capacity<samples){
  for(unsigned i=0;i<3;i++){free(tags[i]);tags[i]=NULL;}
  capacity=0;
  for(unsigned i=0;i<3;i++)if(!(tags[i]=calloc(samples,1))){ohs_revoke(OHS_REASON_ALLOCATION);return;}
  capacity=samples;
 }
 for(unsigned i=0;i<3;i++)memset(tags[i],OHS_UNKNOWN,samples);
 memcpy(palette_pin,palette,sizeof(palette_pin));st.bound=true;
 if(sv.enabled&&sv.valid_subset){
  survival_samples=(size_t)2688*st.density*st.density;
  if(survival_capacity<survival_samples){
   for(unsigned i=0;i<3;i++){free(survival_tokens[i]);survival_tokens[i]=NULL;}
   survival_capacity=0;
   for(unsigned i=0;i<3;i++)if(!(survival_tokens[i]=calloc(survival_samples,sizeof(uint64_t)))){survival_fail(OHS_SURVIVAL_ALLOCATION);return;}
   survival_capacity=survival_samples;
  }
  for(unsigned i=0;i<3;i++)memset(survival_tokens[i],0,survival_samples*sizeof(uint64_t));
  ohs_survival_active=true;
 }
}
void ohs_upscale_row(SDL_Surface *dst,SDL_Surface *src,int row)
{
 if(!context())return;
 unsigned domain=dst==lease[0].s?0:dst==lease[1].s?1:2;
 unsigned *next=domain?&st.output_rows:&st.canvas_rows;
 if(domain>1||src!=lease[domain+2].s||row<0||(unsigned)row!=*next||row>=height||st.phase!=domain+1){ohs_revoke(OHS_REASON_ORDER);return;}
 survival_row(domain,row,5);
 for(int x=0;x<width;x++)set_tag(domain,(size_t)row*width+x,OHS_CLASSIC);
 if(add(&st.upscale_samples[domain],width))++*next;
}
void ohs_talon_begin(void)
{
 if(!context())return;
 if(st.phase!=1||st.canvas_rows!=(unsigned)height||st.talon_calls==UINT_MAX){ohs_revoke(OHS_REASON_ORDER);return;}
 /* Other canvas writers and font_before_effect are not adapted. Reset their
  * underlay before interpreting this admitted Talon call's actual writes. */
 memset(tags[0],OHS_UNKNOWN,samples);add(&st.barriers[0],1);++st.talon_calls;
}
void ohs_write(SDL_Surface *s,void *p,unsigned op,unsigned alpha)
{
 if(!alive())return;
 unsigned domain;size_t n;
 if(op>=OHS_OPERATION_COUNT||alpha>255){ohs_revoke(OHS_REASON_SCOPE);return;}
 if(!point(s,p,&domain,&n))return;
 if(st.phase>4||st.phase<1){ohs_revoke(OHS_REASON_ORDER);return;}
 unsigned value=OHS_CLASSIC;
 if(op==OHS_BLEND||op==OHS_SHADOW){
  if(!alpha){ohs_revoke(OHS_REASON_ORDER);return;}
  value=(op==OHS_BLEND&&alpha==255)||tags[domain][n]!=OHS_UNKNOWN?OHS_OLD_HD:OHS_UNKNOWN;
 }
 if(add(&st.operations[op],1))set_tag(domain,n,value);
}
void ohs_copy_sample(SDL_Surface *dst,void *p,SDL_Surface *src,const void *q)
{
 if(!alive())return;
 unsigned a,b;size_t n,m;
 if(!point(dst,p,&a,&n)||!point(src,q,&b,&m))return;
 if(st.phase!=2||a!=1||b!=0||st.output_rows!=(unsigned)height){ohs_revoke(OHS_REASON_ORDER);return;}
 unsigned value=tags[b][m];if(add(&st.talon_copy[value],1))set_tag(a,n,value);
}
void ohs_finish_begin(bool ordinary)
{
 if(!context())return;
 canvas_finish();
 if(sv.enabled&&(!cp.valid_at_write||!cp.finished))survival_fail(OHS_SURVIVAL_INCOMPLETE);
 if(!ordinary||st.phase!=1||st.canvas_rows!=(unsigned)height){ohs_revoke(OHS_REASON_ORDER);return;}
 st.phase=2;
}
void ohs_canvas_unknown(void)
{
 if(!context())return;
 if(st.phase!=2||canvas_barrier||st.output_rows!=(unsigned)height){ohs_revoke(OHS_REASON_ORDER);return;}
 memset(tags[0],OHS_UNKNOWN,samples);canvas_barrier=true;add(&st.barriers[0],1);
}
void ohs_crop_row(SDL_Surface *dst,SDL_Surface *src,int row,int density)
{
 if(!context())return;
 if(st.phase!=2||!canvas_barrier||src!=lease[0].s||dst!=lease[1].s||density!=(int)st.density||row<0||(unsigned)row!=st.crop_rows||row>=184*density){ohs_revoke(OHS_REASON_ORDER);return;}
 survival_crop(row);
 for(int x=0;x<264*density;x++)set_tag(1,(size_t)row*width+x,tags[0][(size_t)row*width+x+24*density]);
 if(add(&st.crop_samples,264*density))++st.crop_rows;
}
void ohs_output_unknown(void)
{
 if(!context())return;
 if(st.phase!=2||output_barrier||!canvas_barrier||st.crop_rows!=184*st.density){ohs_revoke(OHS_REASON_ORDER);return;}
 memset(tags[1],OHS_UNKNOWN,samples);output_barrier=true;add(&st.barriers[1],1);
}
void ohs_finish_end(void)
{
 if(!context())return;
 if(st.phase!=2||!output_barrier||st.output_rows!=(unsigned)height){ohs_revoke(OHS_REASON_ORDER);return;}
 st.phase=3;
}
void ohs_present_begin(SDL_Surface *src,const Uint32 *palette)
{
 if(!context())return;
 if(st.phase!=3||src!=lease[3].s){ohs_revoke(OHS_REASON_ORDER);return;}
 if(!palette||memcmp(palette_pin,palette,sizeof(palette_pin))){ohs_revoke(OHS_REASON_PALETTE);return;}
 /* Late cache/HUD/font adapters absent: never reuse partial earlier labels. */
 memset(tags[1],OHS_UNKNOWN,samples);add(&st.barriers[1],1);st.phase=4;
}
void ohs_texture_begin(void *pixels,int pitch)
{
 if(!context())return;
 if(st.phase!=4||!pixels||pitch<width*4||pitch%4||(uintptr_t)pixels%4||
 (uintptr_t)pixels>UINTPTR_MAX-(size_t)pitch*height){ohs_revoke(OHS_REASON_GEOMETRY);return;}
 uintptr_t p=(uintptr_t)pixels;
 for(unsigned i=0;i<4;i++)if(p<(uintptr_t)lease[i].pixels+(size_t)lease[i].pitch*lease[i].h&&(uintptr_t)lease[i].pixels<p+(size_t)pitch*height){ohs_revoke(OHS_REASON_GEOMETRY);return;}
 texture_pixels=pixels;texture_pitch=pitch;st.phase=5;
}
void ohs_texture_row(int row)
{
 if(!alive())return;
 if(st.phase!=5||!texture_pixels||texture_pitch<width*4||row<0||(unsigned)row!=st.texture_rows||row>=height){ohs_revoke(OHS_REASON_ORDER);return;}
 survival_texture(row);
 for(int x=0;x<width;x++)set_tag(2,(size_t)row*width+x,tags[1][(size_t)row*width+x]);
 if(add(&st.texture_samples,width))++st.texture_rows;
}
void ohs_stage(void)
{
 if(!context())return;
 if(st.phase!=5||st.texture_rows!=(unsigned)height){ohs_revoke(OHS_REASON_ORDER);return;}
 /* Actual storm/texture writes not adapted in this first slice. */
 memset(tags[2],OHS_UNKNOWN,samples);add(&st.barriers[2],1);st.staged=true;st.phase=6;
 if(cp.enabled&&cp.font_stages!=3){cp.valid_at_write=false;cp.reasons|=OHS_CP_FONT;}
 if(sv.enabled){
  if(!cp.valid_at_write||!cp.finished||sv.storm_checks!=1||sv.armed!=survival_samples)survival_fail(OHS_SURVIVAL_INCOMPLETE);
  if(sv.valid_subset){sv.texture_at_stage=survival_count(2);sv.staged=true;}
 }
 report();
}
void ohs_commit(unsigned presents)
{
 if(!alive())return;
 if(st.phase!=6||!st.staged||(presents!=1&&presents!=2)){ohs_revoke(OHS_REASON_ORDER);return;}
 st.committed=true;st.present_count=presents;st.phase=7;
 if(sv.enabled&&sv.valid_subset&&sv.staged)sv.committed=true;
 if(report())presentation_reported=true;
}
bool ohs_present_fail(void){ohs_revoke(OHS_REASON_PRESENT);return false;}
const OhsStatus *ohs_status(void){return &st;}
unsigned ohs_partial_tag(unsigned domain,int x,int y)
{
 if(!alive()||!st.bound||domain>2||x<0||y<0||x>=width||y>=height)return OHS_UNKNOWN;
 return tags[domain][(size_t)y*width+x];
}

static bool cp_alive(void){return alive()&&cp.enabled&&cp.valid_at_write;}
static void cp_fail(unsigned reason)
{
 if(!cp.enabled)return;
 cp.valid_at_write=false;cp.reasons|=reason;survival_fail(OHS_SURVIVAL_INCOMPLETE);
 uint64_t expected=UINT64_C(2688)*st.density*st.density;
 cp.missing_samples=cp.samples<expected?expected-cp.samples:0;
}
static bool cp_id_equal(const NwlIdentity *a,const NwlIdentity *b)
{
 return a->scene==b->scene&&a->frame==b->frame&&a->group==b->group&&a->call==b->call&&a->generation==b->generation&&a->tick==b->tick&&a->slot==b->slot&&a->type==b->type&&a->part==b->part&&a->base==b->base&&a->x==b->x&&a->y==b->y;
}
bool ohs_canvas_observing(void){return cp_alive();}
void ohs_native_call_begin(uint64_t native_lease,const NwlIdentity *id,SDL_Surface *surface)
{
 if(!cp_alive())return;
 if(!context()||st.phase!=1||st.canvas_rows!=(unsigned)height||cp.pending||!native_lease||!id||surface!=lease[2].s){cp_fail(OHS_CP_CONTEXT);return;}
 if(cp.calls>=OHS_CP_CALLS){cp_fail(OHS_CP_OVERFLOW);return;}
 if(!id->scene||!id->frame||!id->group||!id->call||!id->generation||id->tick!=st.tick||id->slot>=100||id->type<313||id->type>316||(id->part!=0&&id->part!=1&&id->part!=19&&id->part!=20)){cp_fail(OHS_CP_IDENTITY);return;}
 unsigned part=id->part==0?0:id->part==1?1:id->part==19?2:3;
 int x=(id->type==314||id->type==316?164:140)+(int)(part%2)*12;
 int y=(id->type<=314?(b313_slice_top()+28):b313_slice_top())+(int)(part/2)*14;
 if(id->x!=x||id->y!=y){cp_fail(OHS_CP_IDENTITY);return;}
 if(!cp.calls){cp.lease=native_lease;cp.scene=id->scene;cp.frame=id->frame;cp.group=id->group;}
 if(cp.lease!=native_lease||cp.scene!=id->scene||cp.frame!=id->frame||cp.group!=id->group){cp_fail(OHS_CP_IDENTITY);return;}
 for(unsigned i=0;i<cp.calls;i++)if(cp_calls[i].id.call==id->call||!cp_calls[i].closed){cp_fail(OHS_CP_IDENTITY);return;}
 cp_current=cp.calls++;cp_calls[cp_current].id=*id;cp.pending=true;cp_event_live=false;cp_sample_count=0;cp_seen=0;
}
static bool cp_flush_event(void)
{
 if(!cp_event_live)return true;
 unsigned count=st.density*st.density;
 uint64_t mask=count==64?UINT64_MAX:(UINT64_C(1)<<count)-1;
 if(cp_sample_count!=count||cp_seen!=mask){cp_fail(OHS_CP_MISSING);return false;}
 ++cp.complete_events;cp_event_live=false;return true;
}
void ohs_native_event(uint64_t native_lease,const NwlIdentity *id,uint64_t event,size_t offset)
{
 if(!cp_alive())return;
 if(!context()||st.phase!=1||!cp.pending||native_lease!=cp.lease||!id||!event||!cp_id_equal(id,&cp_calls[cp_current].id)){cp_fail(OHS_CP_CONTEXT);return;}
 if(!cp_flush_event())return;
 struct CpCall *c=cp_calls+cp_current;
 size_t row=offset/(unsigned)lease[2].pitch,col=offset%(unsigned)lease[2].pitch;
 if(c->events>=168||row!=(unsigned)c->id.y+c->events/12||col!=(unsigned)c->id.x+c->events%12||(c->events&&event!=c->last+1)){cp_fail(OHS_CP_EVENT);return;}
 if(!c->events)c->first=event;
 c->last=event;++c->events;++cp.events;cp_event=event;cp_offset=offset;cp_sample_count=0;cp_seen=0;cp_event_live=true;
}
void ohs_native_palette(SDL_Surface *native,const void *address,SDL_Surface *canvas,void *sample,int normal)
{
 if(!cp_alive()||!cp.pending)return;
 if(!context()||st.phase!=1||!cp_event_live||!normal||native!=lease[2].s||canvas!=lease[0].s||
 (uintptr_t)address!=(uintptr_t)lease[2].pixels+cp_offset||cp_event!=cp_calls[cp_current].last){cp_fail(OHS_CP_SAMPLE);return;}
 unsigned domain;size_t n;
 if(!point(canvas,sample,&domain,&n)||domain!=0){cp_fail(OHS_CP_SAMPLE);return;}
 unsigned x=(unsigned)(cp_offset%(unsigned)lease[2].pitch),y=(unsigned)(cp_offset/(unsigned)lease[2].pitch),d=st.density;
 size_t px=n%(unsigned)width,py=n/(unsigned)width;
 if(px<x*d||px>=(x+1)*d||py<y*d||py>=(y+1)*d){cp_fail(OHS_CP_SAMPLE);return;}
 unsigned ordinal=(unsigned)(py-y*d)*d+(unsigned)(px-x*d);
 uint64_t bit=UINT64_C(1)<<ordinal;
 if((cp_seen&bit)||ordinal!=cp_sample_count){cp_fail(OHS_CP_SAMPLE);return;}
 size_t roi=(py-b313_slice_top()*d)*(48*d)+(px-140*d);
 if(roi>=(size_t)2688*d*d||roi>=OHS_CP_ROI_SAMPLES||cp_roi_seen[roi]){cp_fail(OHS_CP_SAMPLE);return;}
 cp_seen|=bit;++cp_sample_count;++cp.samples;++cp.unique_samples;cp_roi_seen[roi]=1;
 if(y==(b313_slice_top()+55))++cp.bottom_samples;
 set_tag(0,n,OHS_CLASSIC);
 survival_arm(n,cp_event);
}
void ohs_native_call_end(NwlToken token,uint64_t first,uint64_t last)
{
 if(!cp_alive())return;
 if(!cp.pending||token.lease!=cp.lease||token.call!=cp_calls[cp_current].id.call){cp_fail(OHS_CP_CONTEXT);return;}
 if(!cp_flush_event())return;
 struct CpCall *c=cp_calls+cp_current;
 if(c->events!=168||first!=c->first||last!=c->last||last<first||last-first+1!=168){cp_fail(OHS_CP_EVENT);return;}
 c->closed=true;cp.pending=false;++cp.closed_calls;
}
static void canvas_finish(void)
{
 if(!cp.enabled)return;
 cp.finished=true;
 if(!cp_alive())return;
 NwlStatus ls=nwl_status();
 if(!ls.enabled||!ls.valid||ls.sealed||ls.pending||!ls.calls||ls.lease!=cp.lease||ls.scene!=cp.scene||ls.frame!=cp.frame||ls.tick!=st.tick||ls.calls!=cp.calls||cp.pending||cp_event_live||cp.calls!=16||cp.closed_calls!=cp.calls||cp.events!=2688||cp.complete_events!=cp.events||cp.unique_samples!=UINT64_C(2688)*st.density*st.density||cp.font_stages!=1){cp_fail(OHS_CP_MISSING|OHS_CP_CONTEXT);return;}
 cp.missing_samples=0;
}
void ohs_font_scope(unsigned stage,const SDL_Rect rects[5],unsigned mask)
{
 if(!cp_alive())return;
 if(!rects||stage>1||mask>31||(mask&24)!=24||cp.font_stages!=(stage?1u:0u)){cp_fail(OHS_CP_FONT);return;}
 for(unsigned i=0;i<5;i++)if(mask&(1u<<i)){
  SDL_Rect r=rects[i];int64_t right=(int64_t)r.x+r.w,bottom=(int64_t)r.y+r.h;
  bool valid=r.w>0&&r.h>0;
  if(i<3)valid=valid&&r.x>=24&&right<=288&&r.y>=0&&bottom<=184;
  if(i==0)valid=valid&&r.y==174&&r.w<=101&&r.h<=8;
  if(i==1)valid=valid&&(r.y==7||r.y==27)&&r.w<=141&&r.h<=10;
  if(i==2)valid=valid&&r.x==140&&r.y==178&&r.w==34&&r.h==6;
  if(i==3)valid=valid&&r.x==268&&r.y==118&&r.w==52&&r.h==8;
  if(i==4)valid=valid&&r.x==20&&r.y==190&&r.w==224&&r.h==8;
  int64_t left=(int64_t)r.x-(i<3?24:0),out_right=right-(i<3?24:0);
  if(!valid||(left<164&&out_right>116&&r.y<(b313_slice_top()+56)&&bottom>b313_slice_top())){cp_fail(OHS_CP_FONT);return;}
  ++cp.font_rects;
 }
 cp.font_stages|=1u<<stage;
}
const OhsCanvasStatus *ohs_canvas_status(void){return &cp;}
OhsIoStatus ohs_io_status(void){return io;}

/* Source-gated finite writer collection. This is candidate provenance, not a
 * replacement for semantic tags or the still-incomplete native ledger. */
static const unsigned char survival_writer_kind[OHS_SURVIVAL_WRITER_LIMIT]={
0,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,3,3,2,2,3,2,2,3,2,2,3,2,2,3,2,2,3,2,2,3,2,2,3,2,2,3,2,3,2,2,3,2,2,3,2,2,3,2,2,0,0
};
static void survival_fail(unsigned reason)
{
 if(!sv.enabled)return;
 sv.valid_subset=false;sv.staged=sv.committed=false;sv.reasons|=reason;
 ohs_survival_active=false;
 for(unsigned i=0;i<3;i++)if(survival_tokens[i])memset(survival_tokens[i],0,survival_capacity*sizeof(uint64_t));
}
void ohs_survival_unknown(unsigned reason){survival_fail(reason?reason:OHS_SURVIVAL_UNKNOWN);}
static bool survival_ready(void)
{
 if(!ohs_survival_active)return false;
 if(!sv.valid_subset||!alive()||!st.bound||!survival_samples){survival_fail(OHS_SURVIVAL_CONTEXT);return false;}
 return true;
}
static bool survival_index(unsigned domain,size_t index,size_t *roi)
{
 size_t x=index%(unsigned)width,y=index/(unsigned)width;
 unsigned d=st.density,left=(domain?116u:140u)*d;
 if(x<left||x>=left+48*d||y<b313_slice_top()*d||y>=(unsigned)(b313_slice_top()+56)*d)return false;
 *roi=(y-b313_slice_top()*d)*(48*d)+(x-left);return *roi<survival_samples;
}
static uint64_t survival_count(unsigned domain)
{
 uint64_t n=0;
 if(domain<3&&sv.valid_subset&&survival_tokens[domain])for(size_t i=0;i<survival_samples;i++)n+=survival_tokens[domain][i]!=0;
 return n;
}
static void survival_replace(unsigned domain,size_t roi,uint64_t event,unsigned writer)
{
 uint64_t old=survival_tokens[domain][roi];
 if(old&&old!=event){if(!add(&sv.retired[domain],1))return;if(!sv.first_retiring_writer)sv.first_retiring_writer=writer;}
 survival_tokens[domain][roi]=event;
}
static void survival_arm(size_t index,uint64_t event)
{
 if(!survival_ready())return;
 size_t roi;
 if(st.phase!=1||!cp.valid_at_write||!cp.pending||!event||!survival_index(0,index,&roi)){survival_fail(OHS_SURVIVAL_CONTEXT);return;}
 survival_tokens[0][roi]=event;add(&sv.armed,1);
}
void ohs_survival_write(SDL_Surface *surface,void *address,unsigned writer)
{
 if(!survival_ready())return;
 if(!writer||writer>=OHS_SURVIVAL_WRITER_LIMIT||survival_writer_kind[writer]<1||survival_writer_kind[writer]>2){survival_fail(OHS_SURVIVAL_ID);return;}
 if(st.phase<1||st.phase>4){survival_fail(OHS_SURVIVAL_ORDER);return;}
 unsigned domain;size_t index,roi;
 if(!point(surface,address,&domain,&index))return;
 if(domain+1!=survival_writer_kind[writer]){survival_fail(OHS_SURVIVAL_ID);return;}
 if(!add(&sv.writer_events[writer],1))return;
 if(survival_index(domain,index,&roi)){
  if(!add(&sv.roi_events[writer],1))return;
  survival_replace(domain,roi,0,writer);
 }
}
void ohs_survival_copy(SDL_Surface *dst,void *address,SDL_Surface *src,const void *source,unsigned writer,bool ordinary)
{
 if(!survival_ready())return;
 if(!writer||writer>=OHS_SURVIVAL_WRITER_LIMIT||survival_writer_kind[writer]!=3){survival_fail(OHS_SURVIVAL_ID);return;}
 if(!ordinary||st.phase<2||st.phase>4){survival_fail(OHS_SURVIVAL_ORDER);return;}
 unsigned a,b;size_t n,m,r,q;
 if(!point(dst,address,&a,&n)||!point(src,source,&b,&m))return;
 if(a!=1||b!=0||n/(unsigned)width!=m/(unsigned)width||n%(unsigned)width+24*st.density!=m%(unsigned)width){survival_fail(OHS_SURVIVAL_CONTEXT);return;}
 if(!add(&sv.writer_events[writer],1))return;
 bool target=survival_index(a,n,&r),origin=survival_index(b,m,&q);
 if(target!=origin){survival_fail(OHS_SURVIVAL_CONTEXT);return;}
 if(target){
  if(!add(&sv.roi_events[writer],1)||!add(&sv.copies[a],1))return;
  survival_replace(a,r,survival_tokens[b][q],writer);
 }
}
static void survival_row(unsigned domain,int row,unsigned writer)
{
 if(!survival_ready())return;
 if(writer!=5||domain>1){survival_fail(OHS_SURVIVAL_ID);return;}
 if(!add(&sv.writer_events[writer],(unsigned)width))return;
 unsigned d=st.density;
 if(row<(int)(b313_slice_top()*d)||row>=(int)((b313_slice_top()+56)*d))return;
 if(!add(&sv.roi_events[writer],48*d))return;
 size_t base=(row-b313_slice_top()*d)*(48*d);
 for(unsigned x=0;x<48*d&&ohs_survival_active;x++)survival_replace(domain,base+x,0,writer);
}
static void survival_crop(int row)
{
 if(!survival_ready())return;
 unsigned d=st.density;
 if(row==0)sv.canvas_before_crop=survival_count(0);
 if(!add(&sv.writer_events[139],264*d))return;
 if(row>=(int)(b313_slice_top()*d)&&row<(int)((b313_slice_top()+56)*d)){
  size_t base=(row-b313_slice_top()*d)*(48*d);
  if(!add(&sv.roi_events[139],48*d)||!add(&sv.copies[1],48*d))return;
  for(unsigned x=0;x<48*d&&ohs_survival_active;x++)survival_replace(1,base+x,survival_tokens[0][base+x],139);
 }
 if(row==(int)(184*d)-1)sv.output_after_crop=survival_count(1);
}
static void survival_texture(int row)
{
 if(!survival_ready())return;
 unsigned d=st.density;
 if(row==0)sv.output_before_texture=survival_count(1);
 if(!add(&sv.writer_events[140],(unsigned)width))return;
 if(row>=(int)(b313_slice_top()*d)&&row<(int)((b313_slice_top()+56)*d)){
  size_t base=(row-b313_slice_top()*d)*(48*d);
  if(!add(&sv.roi_events[140],48*d)||!add(&sv.copies[2],48*d))return;
  for(unsigned x=0;x<48*d&&ohs_survival_active;x++)survival_replace(2,base+x,survival_tokens[1][base+x],140);
 }
}
void ohs_survival_storm_scope(bool scope)
{
 if(!survival_ready())return;
 if(st.phase!=5||sv.storm_checks){survival_fail(OHS_SURVIVAL_ORDER);return;}
 ++sv.storm_checks;
 if(scope)survival_fail(OHS_SURVIVAL_STORM);
}
const OhsSurvivalStatus *ohs_survival_status(void){return &sv;}
uint64_t ohs_survival_token(unsigned domain,int x,int y)
{
 if(!survival_ready()||domain>2||x<0||y<0||x>=width||y>=height)return 0;
 size_t r;if(!survival_index(domain,(size_t)y*width+x,&r))return 0;
 return survival_tokens[domain][r];
}
#if defined(BUILDING313_FINAL_PROOF_DIAGNOSTIC) && BUILDING313_FINAL_PROOF_DIAGNOSTIC
/* This final view never dereferences an SDL surface or the unlocked texture.
 * It is a current owned-token view, separate from the sticky earlier artifact. */
static bool final_token_context(uint64_t sample_epoch,uint64_t native_lease)
{
 return sample_epoch&&native_lease&&alive()&&st.bound&&st.epoch==sample_epoch&&st.tick==b313_slice_tick()&&
  st.density==8&&st.phase==7&&st.staged&&st.committed&&st.present_count==1&&
  presentation_reported&&!io.failed&&cp.enabled&&cp.valid_at_write&&cp.finished&&!cp.pending&&
  !cp_event_live&&cp.lease==native_lease&&cp.calls==16&&cp.closed_calls==16&&
  cp.events==2688&&cp.complete_events==2688&&cp.samples==172032&&cp.unique_samples==172032&&
  cp.bottom_samples==3072&&!cp.missing_samples&&cp.font_stages==3&&
  sv.enabled&&sv.valid_subset&&sv.staged&&sv.committed&&!sv.reasons&&ohs_survival_active&&
  sv.storm_checks==1&&sv.armed==172032&&survival_samples==172032&&survival_tokens[2];
}
bool ohs_final_call_matches(uint64_t sample_epoch,uint64_t native_lease,const NwlIdentity *id,uint64_t first,uint64_t last)
{
 if(!final_token_context(sample_epoch,native_lease)||!id||!first||last<first||last-first!=167||
  id->scene!=cp.scene||id->frame!=cp.frame||id->group!=cp.group||id->tick!=b313_slice_tick())return false;
 unsigned found=0;
 for(unsigned i=0;i<cp.calls;i++){
  const struct CpCall *c=cp_calls+i;
  if(cp_id_equal(&c->id,id)){
   if(!c->closed||c->events!=168||c->first!=first||c->last!=last)return false;
   ++found;
  }
 }
 return found==1;
}
bool ohs_final_texture_token(uint64_t sample_epoch,uint64_t native_lease,int x,int y,uint64_t *event)
{
 if(!event)return false;
 *event=0;
 if(!final_token_context(sample_epoch,native_lease)||x<116*8||x>=164*8||y<b313_slice_top()*8||y>=(b313_slice_top()+56)*8)return false;
 /* Use the actual owned token lookup, not aggregate counters or partial tags. */
 *event=ohs_survival_token(2,x,y);
 return true;
}
#endif

#if defined(BUILDING313_PRECOMMIT_DIAGNOSTIC) && BUILDING313_PRECOMMIT_DIAGNOSTIC
bool ohs_precommit_matches(const B313PreLease *p)
{
 return p&&p->native_epoch&&p->sample_epoch&&p->tick==b313_slice_tick()&&alive()&&st.bound&&st.tick==b313_slice_tick()&&st.epoch==p->sample_epoch&&
  st.density==8&&st.phase==6&&st.staged&&!st.committed&&!st.present_count&&!presentation_reported&&!io.failed&&
  cp.enabled&&cp.valid_at_write&&cp.finished&&!cp.pending&&!cp_event_live&&cp.lease==p->native_epoch&&cp.scene==p->scene&&cp.frame==p->frame&&
  cp.calls==16&&cp.closed_calls==16&&cp.events==2688&&cp.complete_events==2688&&cp.samples==172032&&cp.unique_samples==172032&&
  cp.bottom_samples==3072&&!cp.missing_samples&&cp.font_stages==3&&
  sv.enabled&&sv.valid_subset&&sv.staged&&!sv.committed&&!sv.reasons&&sv.storm_checks==1&&sv.armed==172032&&
  ohs_survival_active&&survival_samples==172032&&survival_tokens[2];
}
bool ohs_precommit_call(const B313PreLease *p,const NwlIdentity *id,uint64_t first,uint64_t last,B313PreSamples *out)
{
 if(!out||!ohs_precommit_matches(p)||!id||!first||last<first||last-first!=167||
  id->scene!=cp.scene||id->frame!=cp.frame||id->group!=cp.group||id->tick!=b313_slice_tick()||
  id->x<140||id->x>176||id->y<b313_slice_top()||id->y>(b313_slice_top()+42))return false;
 unsigned found=0;
 for(unsigned i=0;i<cp.calls;i++)if(cp_id_equal(&cp_calls[i].id,id)){
  if(!cp_calls[i].closed||cp_calls[i].events!=168||cp_calls[i].first!=first||cp_calls[i].last!=last)return false;
  ++found;
 }
 if(found!=1)return false;
 memset(out,0,sizeof(*out));out->first_bad_x=out->first_bad_y=-1;
 /* One context check per call; no raw surface or unlocked texture reads. */
 for(unsigned y=0;y<14;y++)for(unsigned x=0;x<12;x++){
  uint64_t expected=first+y*12+x;
  for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){
   unsigned px=(unsigned)(id->x-140+(int)x)*8+sx,py=(unsigned)(id->y-b313_slice_top()+(int)y)*8+sy;
   size_t index=(size_t)py*(48*8)+px;uint64_t actual=survival_tokens[2][index];++out->samples;
   if(actual!=expected){++out->unknown;if(out->first_bad_x<0){out->first_bad_x=(int)px+116*8;out->first_bad_y=(int)py+b313_slice_top()*8;}}
   else{++out->matched;if(id->y+(int)y==(b313_slice_top()+55))++out->bottom;}
  }
 }
 return true;
}
#endif
#endif
