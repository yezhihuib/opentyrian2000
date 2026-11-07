#include "b313_frame_facts.h"
/* Full facts require both diagnostic status providers. */
#if B313_V6_TRANSACTION_DIAGNOSTIC && OLD_HD_SAMPLE_OBSERVER_DIAGNOSTIC
#include "varz.h"
#include "game_probe.h"
#include "b313_v6_prefix_preparation.h"
#include "b313_v6_transaction.h"
#include "native_writer_lineage.h"
#include "old_hd_sample_observer.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <inttypes.h>
extern struct JE_EventRecType eventRec[EVENT_MAXIMUM];
static uint64_t serial,generation[100],resource_epoch[4],log_serial;
static FILE *f;
static int enabled=-1;
static int is_enabled(void){if(enabled<0){const char *p=getenv("B313_FACTS_ENABLE");enabled=p&&!strcmp(p,"1");}return enabled;}
static int selected(void){return is_enabled()&&game_probe_enabled&&episodeNum==1&&lvlFileNum==2&&game_probe_tick>=408&&game_probe_tick<=415;}
static void begin(const char *kind){if(!f){f=fopen("frame-facts.jsonl","w");if(!f)exit(2);}fprintf(f,"{\"kind\":\"%s\",\"seq\":%"PRIu64",\"tick\":%u,\"counter\":%"PRIu64",\"frequency\":%"PRIu64,kind,++log_serial,game_probe_tick,(uint64_t)SDL_GetPerformanceCounter(),(uint64_t)SDL_GetPerformanceFrequency());}
static void finish(void){fputs("}\n",f);if(fflush(f)||ferror(f))exit(2);}
void b313_facts_allocate(const void *object){if(!is_enabled())return;unsigned slot=100;for(unsigned i=0;i<100;i++)if(object==&enemy[i]){slot=i;break;}if(serial==UINT64_MAX||(slot<100&&generation[slot]==UINT64_MAX))exit(2);++serial;if(slot<100)++generation[slot];if(selected()){begin("allocate");fprintf(f,",\"slot\":%u,\"serial\":%"PRIu64",\"generation\":%"PRIu64,slot,serial,slot<100?generation[slot]:0);finish();}}
void b313_facts_resource(unsigned pool,unsigned operation){if(!is_enabled())return;if(pool>=4||resource_epoch[pool]==UINT64_MAX)exit(2);++resource_epoch[pool];if(selected()){begin("resource");fprintf(f,",\"pool\":%u,\"operation\":%u,\"epoch\":%"PRIu64,pool,operation,resource_epoch[pool]);finish();}}
static void slot_record(unsigned slot){const struct JE_SingleEnemyType *e=&enemy[slot];int record=-1,pool=-1;for(unsigned j=0;j<=ENEMY_NUM;j++)if(e->enemydatofs==&enemyDat[j]){record=(int)j;break;}for(unsigned j=0;j<4;j++)if(e->sprite2s==&enemySpriteSheets[j]){pool=(int)j;break;}
 fprintf(f,"{\"slot\":%u,\"avail\":%u,\"generation\":%"PRIu64",\"record\":%d,\"pool\":%d,\"base\":%d",slot,enemyAvail[slot],generation[slot],record,pool,e->enemycycle>=1&&e->enemycycle<=20?(int)e->egr[e->enemycycle-1]:-1);
 fprintf(f,",\"fillbyte\":%d",(int)e->fillbyte);
 fprintf(f,",\"ex\":%d",(int)e->ex);
 fprintf(f,",\"ey\":%d",(int)e->ey);
 fprintf(f,",\"exc\":%d",(int)e->exc);
 fprintf(f,",\"eyc\":%d",(int)e->eyc);
 fprintf(f,",\"exca\":%d",(int)e->exca);
 fprintf(f,",\"eyca\":%d",(int)e->eyca);
 fprintf(f,",\"excc\":%d",(int)e->excc);
 fprintf(f,",\"eycc\":%d",(int)e->eycc);
 fprintf(f,",\"exccw\":%d",(int)e->exccw);
 fprintf(f,",\"eyccw\":%d",(int)e->eyccw);
 fprintf(f,",\"armorleft\":%d",(int)e->armorleft);
 fputs(",\"eshotwait\":[",f); for(unsigned j=0;j<3;j++)fprintf(f,"%s%d",j?",":"",(int)e->eshotwait[j]);fputc(']',f);
 fputs(",\"eshotmultipos\":[",f); for(unsigned j=0;j<3;j++)fprintf(f,"%s%d",j?",":"",(int)e->eshotmultipos[j]);fputc(']',f);
 fprintf(f,",\"enemycycle\":%d",(int)e->enemycycle);
 fprintf(f,",\"ani\":%d",(int)e->ani);
 fputs(",\"egr\":[",f); for(unsigned j=0;j<20;j++)fprintf(f,"%s%d",j?",":"",(int)e->egr[j]);fputc(']',f);
 fprintf(f,",\"size\":%d",(int)e->size);
 fprintf(f,",\"linknum\":%d",(int)e->linknum);
 fprintf(f,",\"aniactive\":%d",(int)e->aniactive);
 fprintf(f,",\"animax\":%d",(int)e->animax);
 fprintf(f,",\"aniwhenfire\":%d",(int)e->aniwhenfire);
 fprintf(f,",\"sprite2s\":%"PRIuPTR,(uintptr_t)e->sprite2s);
 fprintf(f,",\"exrev\":%d",(int)e->exrev);
 fprintf(f,",\"eyrev\":%d",(int)e->eyrev);
 fprintf(f,",\"exccadd\":%d",(int)e->exccadd);
 fprintf(f,",\"eyccadd\":%d",(int)e->eyccadd);
 fprintf(f,",\"exccwmax\":%d",(int)e->exccwmax);
 fprintf(f,",\"eyccwmax\":%d",(int)e->eyccwmax);
 fprintf(f,",\"enemydatofs\":%"PRIuPTR,(uintptr_t)e->enemydatofs);
 fprintf(f,",\"edamaged\":%d",(int)e->edamaged);
 fprintf(f,",\"enemytype\":%d",(int)e->enemytype);
 fprintf(f,",\"animin\":%d",(int)e->animin);
 fprintf(f,",\"edgr\":%d",(int)e->edgr);
 fprintf(f,",\"edlevel\":%d",(int)e->edlevel);
 fprintf(f,",\"edani\":%d",(int)e->edani);
 fprintf(f,",\"fill1\":%d",(int)e->fill1);
 fprintf(f,",\"filter\":%d",(int)e->filter);
 fprintf(f,",\"evalue\":%d",(int)e->evalue);
 fprintf(f,",\"fixedmovey\":%d",(int)e->fixedmovey);
 fputs(",\"freq\":[",f); for(unsigned j=0;j<3;j++)fprintf(f,"%s%d",j?",":"",(int)e->freq[j]);fputc(']',f);
 fprintf(f,",\"launchwait\":%d",(int)e->launchwait);
 fprintf(f,",\"launchtype\":%d",(int)e->launchtype);
 fprintf(f,",\"launchfreq\":%d",(int)e->launchfreq);
 fprintf(f,",\"xaccel\":%d",(int)e->xaccel);
 fprintf(f,",\"yaccel\":%d",(int)e->yaccel);
 fputs(",\"tur\":[",f); for(unsigned j=0;j<3;j++)fprintf(f,"%s%d",j?",":"",(int)e->tur[j]);fputc(']',f);
 fprintf(f,",\"enemydie\":%d",(int)e->enemydie);
 fprintf(f,",\"enemyground\":%d",(int)e->enemyground);
 fprintf(f,",\"explonum\":%d",(int)e->explonum);
 fprintf(f,",\"mapoffset\":%d",(int)e->mapoffset);
 fprintf(f,",\"scoreitem\":%d",(int)e->scoreitem);
 fprintf(f,",\"special\":%d",(int)e->special);
 fprintf(f,",\"flagnum\":%d",(int)e->flagnum);
 fprintf(f,",\"setto\":%d",(int)e->setto);
 fprintf(f,",\"iced\":%d",(int)e->iced);
 fprintf(f,",\"launchspecial\":%d",(int)e->launchspecial);
 fprintf(f,",\"xminbounce\":%d",(int)e->xminbounce);
 fprintf(f,",\"xmaxbounce\":%d",(int)e->xmaxbounce);
 fprintf(f,",\"yminbounce\":%d",(int)e->yminbounce);
 fprintf(f,",\"ymaxbounce\":%d",(int)e->ymaxbounce);
 fputs(",\"fill\":[",f); for(unsigned j=0;j<3;j++)fprintf(f,"%s%d",j?",":"",(int)e->fill[j]);fputc(']',f);
 fputc('}',f);}
void b313_facts_snapshot(const char *stage,unsigned event_entry){if(!selected())return;begin("snapshot");fprintf(f,",\"stage\":\"%s\",\"event_entry\":%u,\"event_loc_current\":%u,\"curLoc\":%u,\"allocation_serial\":%"PRIu64,stage,event_entry,eventLoc,curLoc,serial);
 if(event_entry>=1&&event_entry<=maxEvent){fprintf(f,",\"event\":{\"time\":%u,\"type\":%u,\"data\":[%d,%d,%d,%d,%d,%d]}",eventRec[event_entry-1].eventtime,eventRec[event_entry-1].eventtype,eventRec[event_entry-1].eventdat,eventRec[event_entry-1].eventdat2,eventRec[event_entry-1].eventdat3,eventRec[event_entry-1].eventdat4,eventRec[event_entry-1].eventdat5,eventRec[event_entry-1].eventdat6);}
 fputs(",\"resources\":[",f);for(unsigned i=0;i<4;i++){fprintf(f,"%s{\"pool\":%u,\"epoch\":%"PRIu64",\"bank\":%u,\"size\":%zu,\"sheet\":%"PRIuPTR",\"data\":%"PRIuPTR"}",i?",":"",i,resource_epoch[i],enemySpriteSheetIds[i],enemySpriteSheets[i].size,(uintptr_t)&enemySpriteSheets[i],(uintptr_t)enemySpriteSheets[i].data);}fputc(']',f);
 const B313V6PreparationStatus *p=b313_v6_preparation_peek();const B313V6TransactionStatus *t=b313_v6_transaction_status();const OhsStatus *o=ohs_status();NwlStatus n=nwl_status();
 fprintf(f,",\"cache\":{\"requested\":%d,\"ready\":%d,\"pack_generation\":%"PRIu64",\"preparation_id\":%"PRIu64",\"native_epoch\":%"PRIu64",\"sample_epoch\":%"PRIu64",\"file_reads\":%"PRIu64",\"hash_calls\":%"PRIu64",\"runtime_eligible\":%d,\"v6_runtime_validated\":%d,\"transaction_attempted\":%d,\"transaction_applied\":%d},\"observed_native_lease\":%"PRIu64",\"observed_sample_epoch\":%"PRIu64,p->requested,p->cache_ready,p->pack_generation,p->preparation_id,p->native_epoch,p->sample_epoch,p->file_read_calls,p->sha256_calls,p->runtime_eligible,p->v6_runtime_validated,t->attempted,t->applied,n.lease,o->epoch);
 fputs(",\"slots\":[",f);for(unsigned i=0;i<100;i++){if(i)fputc(',',f);slot_record(i);}fputc(']',f);finish();}
void b313_facts_draw(const char *stage,unsigned slot,unsigned part,int x,int y,const void *surface){if(!selected())return;begin("draw");fprintf(f,",\"stage\":\"%s\",\"surface\":%"PRIuPTR,stage,(uintptr_t)surface);fprintf(f,",\"part\":%u,\"x\":%d,\"y\":%d,\"actor\":",part,x,y);if(slot<100)slot_record(slot);else fputs("null",f);finish();}

void b313_facts_attempt(const char *stage,unsigned family,unsigned offset,unsigned type,int result){if(!selected())return;begin("allocation_attempt");fprintf(f,",\"stage\":\"%s\",\"family\":%u,\"offset\":%u,\"type\":%u,\"result_slot1\":%d",stage,family,offset,type,result);finish();}

#else
/* Disabled recording performs no state reads, mutation or file IO. */
void b313_facts_snapshot(const char *stage,unsigned event_entry)
{(void)stage;(void)event_entry;}
void b313_facts_allocate(const void *object){(void)object;}
void b313_facts_resource(unsigned pool,unsigned operation){(void)pool;(void)operation;}
void b313_facts_draw(const char *stage,unsigned slot,unsigned part,int x,int y,const void *surface)
{(void)stage;(void)slot;(void)part;(void)x;(void)y;(void)surface;}
void b313_facts_attempt(const char *stage,unsigned family,unsigned offset,unsigned type,int result)
{(void)stage;(void)family;(void)offset;(void)type;(void)result;}
#endif
