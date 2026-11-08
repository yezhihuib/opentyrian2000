#define _POSIX_C_SOURCE 200809L
#include "b313_continuity_report.h"
#include "b313_continuity_link.h"
#include "b313_continuity.h"
#include <stdio.h>
#include <stdlib.h>
#include <inttypes.h>
#include <errno.h>
#include <time.h>
#include <fcntl.h>
#include "b313_platform.h"
static BcoReportStatus r;
static bool busy,identified,finish_mark_seen,halt_seen;
static unsigned halt_code;
static unsigned attempted_mask;
static const char *names[]={"begin","birth-pending","birth-closed","first-failure","final-receipt","anchor409"};
static const char *boolean(bool b){return b?"true":"false";}
static bool io_fail(unsigned stage,int error)
{
 if(!r.io_failed){r.io_failed=true;r.io_stage=stage;r.io_error_known=error!=0;r.io_error=error>0?(unsigned)error:0;}
 bco_report_io_failure(); /* Deliberately cannot call this reporter again. */
 BcoStatus s=bco_status();
 fprintf(stderr,"BCO_REPORT_FAILED stage=%u errno_known=%u errno=%u first_reason=%u first_tick_known=%u first_tick=%u reasons=%u\n",r.io_stage,r.io_error_known,r.io_error,s.first_reason,s.first_tick_known,s.first_tick,s.reasons);
 return false;
}
static bool identify(void)
{
 if(identified)return true;
 uint64_t sec,nsec;if(!b313_monotonic_time(&sec,&nsec))return io_fail(BCO_IO_CLOCK,errno);
 r.process_id=b313_process_id();r.monotonic_sec=sec;r.monotonic_nsec=nsec;identified=true;return true;
}
static bool serialize(FILE *f,unsigned stage,unsigned tick,bool tick_known,const BcoStatus *s)
{
 const CoObserver *c=&s->consumption;BcoLinkStatus link=bco_link_status();
 /* Even the terminal receipt conveys state, never lifecycle success. */
 fprintf(f,"{\n\"schema\":1,\"observational_only\":true,\"run_status\":\"INCOMPLETE\",\"external_end_receipt_required\":true,\"write_allowed\":false,\"runtime_eligible\":false,\"production_enabled\":false,\n");
 fprintf(f,"\"run\":{\"process_id\":%"PRIu64",\"monotonic_sec\":%"PRIu64",\"monotonic_nsec\":%"PRIu64"},\"stage\":\"%s\",\"report_seq\":%u,\"previous_published_seq\":%u,\"previous_published_mask\":%u,\"tick\":%u,\"tick_known\":%s,\n",r.process_id,r.monotonic_sec,r.monotonic_nsec,names[stage],r.attempted_seq,r.published_seq,r.published_mask,tick_known?tick:0,boolean(tick_known));
 fprintf(f,"\"session\":%"PRIu64",\"failed\":%s,\"reasons\":%u,\"first_reason\":%u,\"first_tick\":%u,\"first_tick_known\":%s,\"birth_pending\":%s,\"birth_closed_observed\":%s,\"attempt\":%"PRIu64",\"group\":%"PRIu64",\"scene\":%"PRIu64",\"allocation_serial\":%"PRIu64",\"entry_serial\":%"PRIu64",\"birth_allocations\":%u,\n",s->session,boolean(s->failed),s->reasons,s->first_reason,s->first_tick,boolean(s->first_tick_known),boolean(s->birth_pending),boolean(s->birth_closed),s->attempt,s->group,s->scene,s->serial,s->entry_serial,s->birth_allocations);
 fprintf(f,"\"raw_args_recorded\":%s,\"full_tuple_validated\":false,\"raw_args\":",boolean(s->raw_args_recorded));
 if(s->raw_args_recorded){fputc('[',f);for(unsigned i=0;i<6;i++)fprintf(f,"%s%d",i?",":"",s->raw_args[i]);fputc(']',f);}else fputs("null",f);
 fputs(",\"generation\":[",f);for(unsigned i=0;i<100;i++)fprintf(f,"%s%"PRIu64,i?",":"",s->generation[i]);
 fputs("],\"resource_epochs\":[",f);for(unsigned i=0;i<4;i++)fprintf(f,"%s%"PRIu64,i?",":"",s->resources[i]);
 fprintf(f,"],\"consumption_state\":{\"failed\":%s,\"first_reason\":%u,\"reasons\":%u,\"received\":%"PRIu64",\"handled\":%"PRIu64",\"discarded\":%"PRIu64",\"commands\":%"PRIu64",\"command_parent\":%"PRIu64",\"pending\":%s,\"pending_seq\":%"PRIu64",\"pending_domain\":%u,\"pending_tick\":%u,\"pending_type\":%u,\"interrupted\":%s,\"interrupt_kind\":%u,\"boundary_observed\":%s},\n",boolean(c->failed),c->first_reason,c->reasons,c->received,c->handled,c->discarded,c->commands,c->command_parent,boolean(c->pending),c->pending_seq,c->pending_domain,c->pending_tick,c->pending_type,boolean(c->interrupted),c->interrupt_kind,boolean(c->boundary_observed));
 fprintf(f,"\"finish_mark_seen\":%s,\"halt_seen\":%s,\"halt_code\":%u,\n",boolean(finish_mark_seen),boolean(halt_seen),halt_code);
 fprintf(f,"\"independent_link\":{\"requested\":%s,\"configuration_valid\":%s,\"configuration_conflict\":%s,\"birth_source_observed\":%s,\"birth_scene\":%"PRIu64",\"birth_group\":%"PRIu64",\"birth_serial\":%"PRIu64",\"anchor_observed\":%s,\"anchor_tick\":%u,\"anchor_serial\":%"PRIu64",\"anchor_preparation\":%"PRIu64",\"original_snapshot_saved\":%s,\"original_report_published\":%s},\n",boolean(link.independent_requested),boolean(link.configuration_valid),boolean(link.configuration_conflict),boolean(link.birth_source_observed),link.birth_scene,link.birth_group,link.birth_serial,boolean(link.anchor_observed),link.anchor_tick,link.anchor_serial,link.anchor_preparation,boolean(link.anchor_snapshot_saved),boolean(link.anchor_report_published));
 fputs("\"scope\":\"Historical observer metadata only; not full birth, resource, renderer or lifecycle proof. Consumption state is not the rejected event identity.\"\n}\n",f);
 return !ferror(f);
}
bool bco_report_emit(unsigned stage,unsigned tick,bool tick_known)
{
 if(!bco_enabled()||r.io_failed)return false;
 if(busy)return io_fail(BCO_IO_REENTRY,0);
 busy=true;
 if(stage>BCO_REPORT_ANCHOR409||(attempted_mask&(1u<<stage))){io_fail(BCO_IO_ORDER,0);busy=false;return false;}
 attempted_mask|=1u<<stage;++r.attempted_seq;
 BcoStatus s=bco_status();
 bool ordered=stage==BCO_REPORT_FINAL_RECEIPT?(finish_mark_seen&&halt_seen&&(s.session||s.failed)):
  stage==BCO_REPORT_ANCHOR409?((r.published_mask&4u)&&bco_link_status().anchor_observed&&!s.failed):
  stage==BCO_REPORT_FIRST_FAILURE?s.failed:
  stage==BCO_REPORT_BEGIN?(s.session||s.failed):
  stage==BCO_REPORT_BIRTH_PENDING?((r.published_mask&1u)&&s.attempt&&s.birth_pending):
  ((r.published_mask&2u)&&s.birth_closed&&!s.birth_pending&&!s.failed);
 if(!ordered||!identify()){if(!r.io_failed)io_fail(BCO_IO_ORDER,0);busy=false;return false;}
 char path[100],tmp[104];snprintf(path,sizeof(path),"building313-continuity-%s.json",names[stage]);snprintf(tmp,sizeof(tmp),"%s.tmp",path);
 errno=0;int fd=b313_open_exclusive(tmp);
 if(fd<0){io_fail(BCO_IO_OPEN,errno);busy=false;return false;}
 FILE *f=b313_fdopen_write(fd);if(!f){int e=errno;b313_close(fd);b313_unlink(tmp);io_fail(BCO_IO_STREAM,e);busy=false;return false;}
 unsigned error_stage=0;int error=0;
 errno=0;if(!serialize(f,stage,tick,tick_known,&s)){error_stage=BCO_IO_WRITE;error=errno;}
 if(!error_stage&&fflush(f)){error_stage=BCO_IO_FLUSH;error=errno;}
 if(!error_stage&&b313_sync_file(f)){error_stage=BCO_IO_SYNC;error=errno;}
 if(fclose(f)&&!error_stage){error_stage=BCO_IO_CLOSE;error=errno;}
 if(!error_stage&&r.io_failed){error_stage=r.io_stage;error=(int)r.io_error;}
 if(!error_stage&&b313_publish_no_replace(tmp,path)){error_stage=BCO_IO_PUBLISH;error=errno;}
 if(b313_unlink(tmp)&&!error_stage){error_stage=BCO_IO_CLEANUP;error=errno;}
 if(!error_stage&&r.io_failed){error_stage=r.io_stage;error=(int)r.io_error;}
 if(error_stage){io_fail(error_stage,error);busy=false;return false;}
 r.published_seq=r.attempted_seq;r.published_mask|=1u<<stage;busy=false;return true;
}
void bco_report_first_failure(void)
{
 BcoStatus s=bco_status();(void)bco_report_emit(BCO_REPORT_FIRST_FAILURE,s.first_tick,s.first_tick_known);
}
BcoReportStatus bco_report_status(void){return r;}

void bco_report_finish_mark(void)
{
 if(!bco_enabled())return;
 if(finish_mark_seen||halt_seen){(void)io_fail(BCO_IO_ORDER,0);return;}
 finish_mark_seen=true;
}
void bco_report_at_halt(unsigned tick,unsigned code)
{
 if(!bco_enabled())return;
 if(halt_seen){(void)io_fail(BCO_IO_ORDER,0);return;}
 halt_seen=true;halt_code=code;
 if(!finish_mark_seen)(void)io_fail(BCO_IO_ORDER,0);
 bool written=bco_report_emit(BCO_REPORT_FINAL_RECEIPT,tick,true);
 BcoStatus s=bco_status();
 int result=fprintf(stderr,"BCO_FINAL_RECEIPT {\"schema\":1,\"process_id\":%"PRIu64",\"monotonic_sec\":%"PRIu64",\"monotonic_nsec\":%"PRIu64",\"run_identified\":%s,\"finish_mark_seen\":%s,\"next_tick\":%u,\"halt_code\":%u,\"file_published\":%s,\"observer_failed\":%s,\"reasons\":%u,\"first_reason\":%u,\"first_tick_known\":%s,\"first_tick\":%u,\"birth_pending\":%s,\"birth_closed_observed\":%s,\"io_failed\":%s,\"io_stage\":%u,\"attempted_seq\":%u,\"published_seq\":%u,\"published_mask\":%u,\"write_allowed\":false,\"runtime_eligible\":false,\"production_enabled\":false}\n",r.process_id,r.monotonic_sec,r.monotonic_nsec,boolean(identified),boolean(finish_mark_seen),tick,code,boolean(written),boolean(s.failed),s.reasons,s.first_reason,boolean(s.first_tick_known),s.first_tick,boolean(s.birth_pending),boolean(s.birth_closed),boolean(r.io_failed),r.io_stage,r.attempted_seq,r.published_seq,r.published_mask);
 if(result<0||fflush(stderr))(void)io_fail(BCO_IO_WRITE,errno);
}
