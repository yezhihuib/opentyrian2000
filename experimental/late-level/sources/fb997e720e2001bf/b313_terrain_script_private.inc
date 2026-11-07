/* One synchronous ordinary case19 or case31 close, never an actor/cache lease. The
 * original frame origin is only copied, never replaced or reissued. */
#include "palette.h"
#include "b313_terrain_script_pins.inc"
static struct {
 bool enabled,enabled31,loaded,broken,inflight,policy_failed;
 unsigned next,event,time;
 struct JE_EventRecType rows[258];
} script19_stream;
static struct {
 bool enabled,enabled31,started,dispatch,attempted,close_seen,close_success;
 unsigned stage,count,event,time,kind,close_cause,close_calls,successful_closes;
 uint64_t close_order,close_lifetime;
 B313TerrainContext origin;
 B313FamilyCacheWindow old_window;
 B313FamilyCacheStatus cache;
 B313FamilyObserverStatus observer;
 B313FamilyWriterStatus writer;
 JE_MultiEnemyType slots;
 JE_byte avail[100];
 JE_EnemyDatType records;
 Source sources[4];Sprite2_array banks[4];unsigned bank_ids[4];
 unsigned char bank_digest[4][SHA256_DIGEST_LENGTH];
 SDL_Surface surface,output;SDL_Surface *vga,*out;
 SDL_PixelFormat format;SDL_Palette palette;SDL_Color colors[256];
 Uint32 rgb[256];
 intptr_t context[32];
} script19;
static bool script19_blocks(void){return script19.attempted;}
static bool script19_requested(void)
{
 const char *e=getenv("BUILDING313_TERRAIN_SCRIPT19_ENABLE");
 const char *o=getenv("BUILDING313_FAMILY_OBSERVER_ENABLE");
 return e&&!strcmp(e,"1")&&o&&!strcmp(o,"1");
}
static bool script31_requested(void)
{
 const char *e=getenv("BUILDING313_TERRAIN_SCRIPT31_ENABLE");
 const char *o=getenv("BUILDING313_FAMILY_OBSERVER_ENABLE");
 return e&&!strcmp(e,"1")&&o&&!strcmp(o,"1");
}
/* Separate level/frame opt-ins share only the authenticated stream and the
 * one terrain credential. Either observed policy change fails this level. */
static bool script19_policy(void)
{
 return (script19.enabled||script19.enabled31)&&!script19_stream.policy_failed&&
  script19.enabled==script19_stream.enabled&&script19.enabled==script19_requested()&&
  script19.enabled31==script19_stream.enabled31&&script19.enabled31==script31_requested();
}
static bool script19_row_pin(unsigned i,const struct JE_EventRecType *r)
{
 if(i>=258)return false;
 const int d[6]={r->eventdat,r->eventdat2,r->eventdat3,r->eventdat4,r->eventdat5,r->eventdat6};
 return r->eventtime==script19_events[i].time&&r->eventtype==script19_events[i].type&&
  !memcmp(d,script19_events[i].d,sizeof d);
}
static bool script19_stream_current(void)
{
 return script19_stream.loaded&&!script19_stream.broken&&maxEvent==731&&
  !memcmp(script19_stream.rows,eventRec,sizeof script19_stream.rows);
}
static bool script19_motion_row(unsigned e)
{
 if(e<1||e>=258||!script19_row_pin(e-1,eventRec+e-1))return false;
 const struct JE_EventRecType *r=eventRec+e-1;
 return r->eventtype==19&&!r->eventdat3&&!r->eventdat6&&
  r->eventdat>=-2&&r->eventdat<=2&&r->eventdat2>=-2&&r->eventdat2<=2&&
  (r->eventdat4==1||r->eventdat4==3||r->eventdat4==4||r->eventdat4==5||r->eventdat4==6||r->eventdat4==7)&&
  r->eventdat5>=1&&r->eventdat5<=8;
}
static bool script31_fire_row(unsigned e)
{
 if(e<1||e>=258||!script19_row_pin(e-1,eventRec+e-1))return false;
 const struct JE_EventRecType *r=eventRec+e-1;
 return r->eventtype==31&&r->eventdat4>=1&&r->eventdat4<=7&&
  (r->eventdat==0||r->eventdat==30)&&(r->eventdat2==0||r->eventdat2==30)&&
  (r->eventdat3==0||r->eventdat3==30)&&!r->eventdat5&&!r->eventdat6;
}
static bool script19_row_enabled(unsigned e)
{
 return (script19.enabled&&script19_motion_row(e))||
  (script19.enabled31&&script31_fire_row(e));
}
static bool script19_cache_equal(const B313FamilyCacheStatus *a,const B313FamilyCacheStatus *b)
{
 return a->diagnostic_enabled==b->diagnostic_enabled&&a->ready==b->ready&&a->frame_open==b->frame_open&&
  a->write_allowed==b->write_allowed&&a->runtime_eligible==b->runtime_eligible&&a->production_enabled==b->production_enabled&&
  a->phase_mask==b->phase_mask&&a->reasons==b->reasons&&a->read_calls==b->read_calls&&a->hash_calls==b->hash_calls&&
  a->generation_serial==b->generation_serial&&a->pack_generation==b->pack_generation&&
  a->frame_generation==b->frame_generation&&a->bytes==b->bytes;
}
static bool script19_resources(void)
{
 if(memcmp(script19.sources,source,sizeof source)||memcmp(script19.records,enemyDat,sizeof enemyDat))return false;
 for(unsigned i=0;i<4;i++)if(enemySpriteSheetIds[i]!=script19.bank_ids[i]||
  enemySpriteSheets[i].data!=script19.banks[i].data||enemySpriteSheets[i].size!=script19.banks[i].size)return false;
 return true;
}
/* Content hashes occur only inside the synchronous event witness, never in
 * currentness/receipt queries or during finish/Present. Existing source guards
 * remain responsible for all later drawing. The original event2 bank roles
 * and complete byte lengths/digests are pinned before any content read. */
static bool script19_bank_content(bool capture)
{
 static const unsigned role[4]={8,23,20,17};
 static const size_t bytes[4]={42012,46566,46204,42126};
 static const unsigned char pinned[4][SHA256_DIGEST_LENGTH]={
 {0x08,0xc7,0xc8,0x1b,0x4e,0xd5,0x90,0x60,0x9f,0x97,0x34,0x7b,0x1a,0x4e,0xc6,0x0a,0xba,0x56,0x92,0x5e,0xcc,0x71,0x93,0xa6,0x71,0x8c,0x34,0xcb,0x8d,0x69,0x8a,0xdf},
 {0xf0,0xbc,0xcf,0x15,0x4a,0x43,0x6b,0xa4,0x68,0x34,0xa0,0x0b,0x93,0x4e,0x7c,0xb8,0xa7,0x7d,0x85,0x85,0xb1,0x75,0xa3,0x9c,0x12,0x70,0xad,0x78,0x88,0x41,0x1c,0x88},
 {0x4b,0xd9,0xa7,0x23,0x39,0xe3,0x04,0x40,0xc1,0x72,0xe3,0x85,0xf2,0x58,0xc8,0x89,0x5b,0x51,0x6f,0xf8,0x40,0x26,0xa9,0xa6,0xb5,0xa6,0x5a,0xda,0x4c,0xf0,0xab,0x90},
 {0xa0,0x02,0x2a,0x44,0x25,0xfe,0xda,0x04,0x00,0x4e,0x8c,0x27,0xb4,0x0c,0xd2,0x37,0x79,0xa2,0xfe,0x95,0x7d,0xe7,0x0e,0xbb,0x7f,0xb8,0x14,0xf7,0x60,0x1c,0xc4,0xe1}};
 for(unsigned i=0;i<4;i++){
  if(source[i].loading||!source[i].loaded)return false;
  const Sprite2_array *b=enemySpriteSheets+i;
  if(enemySpriteSheetIds[i]!=role[i]||!b->data||b->size!=bytes[i])return false;
  unsigned char digest[SHA256_DIGEST_LENGTH];
  if(!SHA256(b->data,b->size,digest)||memcmp(digest,pinned[i],sizeof digest))return false;
  if(capture)memcpy(script19.bank_digest[i],digest,sizeof digest);
  else if(memcmp(script19.bank_digest[i],digest,sizeof digest))return false;
 }
 return true;
}
static void script19_context(intptr_t out[32])
{
 const intptr_t now[32]={curLoc,maxEvent,mapX,mapY,mapX2,mapY2,mapX3,mapY3,
  (intptr_t)mapYPos,(intptr_t)mapY2Pos,(intptr_t)mapY3Pos,mapXPos,oldMapXOfs,mapXOfs,mapX2Ofs,mapX2Pos,
  mapX3Pos,oldMapX3Ofs,mapX3Ofs,tempMapXOfs,mapXbpPos,mapX2bpPos,mapX3bpPos,
  backMove,backMove2,backMove3,map1YDelay,map1YDelayMax,map2YDelay,map2YDelayMax,episodeNum,lvlFileNum};
 memcpy(out,now,sizeof now);
}
static bool script19_writer_equal(void)
{
 B313FamilyWriterStatus a=b313_family_writer_status(),*b=&script19.writer;
 return b313_family_writer_peek_draw(s.frame)&&a.diagnostic_enabled==b->diagnostic_enabled&&
  a.active==b->active&&a.valid==b->valid&&a.sealed==b->sealed&&a.fill_pending==b->fill_pending&&
  a.rect_pending==b->rect_pending&&a.rect_active==b->rect_active&&a.crop_started==b->crop_started&&
  a.reasons==b->reasons&&a.first_reason==b->first_reason&&a.copy_rows==b->copy_rows&&a.pending_pixels==b->pending_pixels&&
  a.frame==b->frame&&a.stores==b->stores&&a.store_bytes==b->store_bytes&&a.pixels==b->pixels&&
  a.fills==b->fills&&a.fill_rows_suppressed==b->fill_rows_suppressed;
}
static bool script19_target(void)
{
 Target t={script19.origin.surface,script19.origin.pixels,script19.origin.format};
 if(!target_matches(game_screen,&t)||game_screen->format->palette!=script19.format.palette)return false;
 SDL_Palette *p=game_screen->format->palette;
 return p&&p->ncolors==256&&p->colors==script19.palette.colors&&
  !memcmp(game_screen->format,&script19.format,sizeof script19.format)&&
  !memcmp(p,&script19.palette,sizeof script19.palette)&&
  !memcmp(p->colors,script19.colors,sizeof script19.colors)&&!memcmp(rgb_palette,script19.rgb,sizeof script19.rgb);
}
/* Equality is across the actual synchronous operation only. Later ordinary
 * motion/drawing is checked by the unchanged canvas, family and writer gates. */
static bool script19_native_equal(bool moved)
{
 if(memcmp(enemyAvail,script19.avail,sizeof script19.avail))return false;
 const struct JE_EventRecType *r=script19_stream.rows+script19.event-1;
 for(unsigned i=0;i<100;i++){
  struct JE_SingleEnemyType expected;memcpy(&expected,script19.slots+i,sizeof expected);
  /* Both native branches operate on all 100 slots, including free slots.
   * Only this local expected copy is changed; native state is read-only. */
  if(moved&&expected.linknum==r->eventdat4){
   if(script19.kind==19){expected.exc=r->eventdat;expected.eyc=r->eventdat2;expected.enemycycle=r->eventdat5;}
   else if(script19.kind==31){
    expected.freq[0]=r->eventdat;expected.freq[1]=r->eventdat2;expected.freq[2]=r->eventdat3;
    for(unsigned j=0;j<3;j++)expected.eshotwait[j]=1;
    if(expected.launchtype>0){expected.launchfreq=r->eventdat5;expected.launchwait=1;}
   }else return false;
  }
  if(memcmp(enemy+i,&expected,sizeof expected))return false;
 }
 return true;
}
static bool script19_synchronous(bool moved,bool closed)
{
 intptr_t now[32];script19_context(now);
 B313FamilyObserverStatus expected;memcpy(&expected,&script19.observer,sizeof expected);
 if(closed)++expected.event_frames;
 B313FamilyCacheStatus cache=b313_family_cache_status(),want=script19.cache;
 if(closed){want.frame_open=false;want.frame_generation=0;}
 return script19_policy()&&terrain_spawn_scope()&&terrain_spawn_quiet()&&!terrain_spawn.active&&
  terrain.valid&&terrain.requested&&terrain_requested()&&same_frame(&terrain.origin.frame,&script19.origin.frame)&&
  terrain.continuity_lifetime==script19.origin.frame.lifetime_serial&&
  lifetime_serial==script19.origin.frame.lifetime_serial+(closed?1:0)&&
  frame_event==closed&&!memcmp(&s,&expected,sizeof s)&&script19_cache_equal(&cache,&want)&&
  (closed?(!window.pack_generation&&!window.frame_generation):
   (window.pack_generation==script19.old_window.pack_generation&&window.frame_generation==script19.old_window.frame_generation))&&
  script19_resources()&&script19_writer_equal()&&script19_target()&&
  VGAScreen==script19.vga&&VGAScreenSeg==script19.out&&
  !memcmp(game_screen,&script19.surface,sizeof script19.surface)&&
  !memcmp(VGAScreenSeg,&script19.output,sizeof script19.output)&&
  !memcmp(now,script19.context,sizeof now)&&script19_native_equal(moved)&&script19_bank_content(false);
}
static bool script19_current(const B313FamilyFrameIdentity *frame)
{
 if(!frame||script19.stage!=4||script19.dispatch||script19_stream.inflight||
  !script19.close_seen||!script19.close_success||script19.close_cause!=script19.kind||!script19_row_enabled(script19.event)||script19.count!=1||
  script19.close_calls!=1||script19.successful_closes!=1||
  !script19_policy()||!script19_stream_current()||script19_stream.next!=script19.event+1||
  eventLoc!=script19.event+1||!same_frame(frame,&script19.origin.frame)||
  !same_frame(frame,&terrain.origin.frame)||!terrain_spawn_scope()||!terrain_spawn_quiet()||terrain_spawn.active||
  !entry_policy_current()||tail.policy_failed||tail.session_enabled!=tail_requested()||tail.frame_enabled!=tail.session_enabled||
  !terrain.valid||!terrain.requested||!terrain_requested()||bridge_exhausted||!configured||!valid_config||
  !s.requested||!s.active||s.failed||!s.frame_open||!frame_event||
  s.session!=frame->session||s.frame!=frame->frame||s.pack_generation!=frame->pack_generation||
  lifetime_serial!=script19.close_lifetime||script19.close_lifetime!=frame->lifetime_serial+1||
  s.allocation_serial!=script19.observer.allocation_serial||
  memcmp(s.generation,script19.observer.generation,sizeof s.generation)||
  memcmp(s.resource_epoch,script19.observer.resource_epoch,sizeof s.resource_epoch)||
  s.event_frames!=script19.observer.event_frames+1||s.reasons!=script19.observer.reasons||
  s.target_calls!=script19.observer.target_calls||window.pack_generation||window.frame_generation||
  memcmp(enemyAvail,script19.avail,sizeof script19.avail)||!script19_resources()||!script19_target())return false;
 B313FamilyCacheStatus cache=b313_family_cache_status(),want=script19.cache;
 want.frame_open=false;want.frame_generation=0;
 return script19_cache_equal(&cache,&want)&&
  (b313_family_writer_peek_draw(s.frame)||b313_family_writer_peek_current(s.frame));
}
void b313_family_observer_script_level_begin(char map,char shape)
{
 memset(&script19_stream,0,sizeof script19_stream);memset(&script19,0,sizeof script19);
 script19_stream.enabled=script19_requested();script19_stream.enabled31=script31_requested();
 if(!script19_stream.enabled&&!script19_stream.enabled31)return;
 script19_stream.next=1;
 if(!scope()||mainLevel!=6||strncmp(levelName,"ASTEROID2",9)||
  (levelName[9]&&levelName[9]!=' ')||map!='D'||shape!='Z'||mapX!=1||mapX2!=1||mapX3!=1||maxEvent!=731)return;
 for(unsigned i=0;i<258;i++)if(!script19_row_pin(i,eventRec+i))return;
 memcpy(script19_stream.rows,eventRec,sizeof script19_stream.rows);script19_stream.loaded=true;
}
void b313_family_observer_script_dispatch_begin(void)
{
 if(!script19.enabled&&!script19.enabled31)return;
 if(script19.started){script19.stage=5;return;}
 script19.started=script19.dispatch=true;
 if(!script19_policy()||!script19_stream_current()||script19_stream.inflight||
  script19_stream.next!=eventLoc||!script19_row_enabled(eventLoc)||eventRec[eventLoc-1].eventtime!=curLoc||
  eventRec[eventLoc].eventtime<=curLoc||!terrain_spawn_scope()||!terrain_spawn_quiet()||terrain_spawn.active||
  terrain.continuity_lifetime!=terrain.origin.frame.lifetime_serial||
  !b313_family_observer_terrain_context_current(game_screen,&terrain.origin)||!b313_family_writer_peek_draw(s.frame)||
  VGAScreen!=game_screen||!VGAScreenSeg||!game_screen->format->palette||game_screen->format->palette->ncolors!=256||
  !game_screen->format->palette->colors||lifetime_serial==UINT64_MAX||s.event_frames==UINT64_MAX||
  (s.reasons&(B313FO_CONFIG|B313FO_ORDER|B313FO_RESOURCE|B313FO_SOURCE|B313FO_CONTEXT|B313FO_CACHE|B313FO_IO)))return;
 script19.attempted=true;script19.stage=1;script19.event=eventLoc;script19.time=curLoc;
 script19.kind=eventRec[eventLoc-1].eventtype;
 script19.origin=terrain.origin;script19.old_window=window;script19.cache=b313_family_cache_status();
 if(script19.cache.reasons){script19.stage=5;return;}
 memcpy(&script19.observer,&s,sizeof s);script19.writer=b313_family_writer_status();
 memcpy(script19.slots,enemy,sizeof enemy);memcpy(script19.avail,enemyAvail,sizeof script19.avail);
 memcpy(script19.records,enemyDat,sizeof enemyDat);memcpy(script19.sources,source,sizeof source);
 for(unsigned i=0;i<4;i++){script19.banks[i]=enemySpriteSheets[i];script19.bank_ids[i]=enemySpriteSheetIds[i];}
 script19.vga=VGAScreen;script19.out=VGAScreenSeg;
 memcpy(&script19.surface,game_screen,sizeof script19.surface);memcpy(&script19.output,VGAScreenSeg,sizeof script19.output);
 memcpy(&script19.format,game_screen->format,sizeof script19.format);
 memcpy(&script19.palette,game_screen->format->palette,sizeof script19.palette);
 memcpy(script19.colors,script19.palette.colors,sizeof script19.colors);memcpy(script19.rgb,rgb_palette,sizeof script19.rgb);
 script19_context(script19.context);
 if(!script19_bank_content(true))script19.stage=5;
}
void b313_family_observer_script_event_before(unsigned event)
{
 if(!script19_stream.enabled&&!script19_stream.enabled31)return;
 if(script19_stream.enabled!=script19_requested()||script19_stream.enabled31!=script31_requested())
  script19_stream.policy_failed=true;
 if(script19.dispatch){if(script19.count==UINT_MAX)script19.stage=5;else ++script19.count;}
 if(script19.stage&&(!script19.dispatch||script19.count!=1||event!=script19.event))script19.stage=5;
 if(!script19_stream_current()||script19_stream.inflight||event!=eventLoc||event!=script19_stream.next||
  event<1||event>258||!script19_row_pin(event-1,eventRec+event-1)||eventRec[event-1].eventtime>curLoc){script19_stream.broken=true;script19.stage=5;return;}
 script19_stream.inflight=true;script19_stream.event=event;script19_stream.time=curLoc;
}
/* Called only from observer_event, directly around its original revoke/close.
 * Success is the real cache_frame_end return, not an inference from ready. */
static bool script19_close_before(void)
{
 return script19.stage==1&&script19.dispatch&&script19.count==1&&!script19.close_calls&&script19_stream.inflight&&
  script19_stream.event==script19.event&&eventLoc==script19.event&&curLoc==script19.time&&
  script19_stream_current()&&script19_row_enabled(eventLoc)&&script19_synchronous(false,false);
}
static void script19_close_after(bool expected,bool success)
{
 if(!script19.attempted)return;
 if(script19.close_calls==UINT_MAX||script19.successful_closes==UINT_MAX){script19.stage=5;return;}
 ++script19.close_calls;if(success)++script19.successful_closes;
 script19.close_seen=true;script19.close_success=success;
 script19.close_cause=script19_stream.inflight&&eventLoc>=1&&eventLoc<=258?eventRec[eventLoc-1].eventtype:0;
 script19.close_order=script19.count;script19.close_lifetime=lifetime_serial;
 script19.stage=expected&&success&&script19.close_cause==script19.kind&&script19_synchronous(false,true)?2:5;
}
void b313_family_observer_script_event_after(unsigned event)
{
 if(!script19_stream.enabled&&!script19_stream.enabled31)return;
 if(!script19_stream.inflight||script19_stream.broken||event!=script19_stream.event||
  event<1||event>258||eventLoc!=event+1||curLoc!=script19_stream.time){script19_stream.broken=true;script19.stage=5;return;}
 struct JE_EventRecType expected;memcpy(&expected,script19_stream.rows+event-1,sizeof expected);
 /* These already-existing native mutations only update stream identity.
  * They cannot arm/commit a terrain credential and are neither case19 nor case31. */
 if(event==31){int r=eventRec[event-1].eventdat;if(r!=533&&(r<829||r>834)){script19_stream.broken=true;}else expected.eventdat=r;}
 if(event==106||event==230||event==240)expected.eventdat6=0;
 if(memcmp(&expected,eventRec+event-1,sizeof expected))script19_stream.broken=true;
 memcpy(script19_stream.rows+event-1,&expected,sizeof expected);
 if(!script19_stream_current())script19_stream.broken=true;
 if(script19.stage==2)script19.stage=!script19_stream.broken&&script19_synchronous(true,true)?3:5;
 else if(script19.attempted)script19.stage=5;
 script19_stream.inflight=false;script19_stream.next=event+1;
}
void b313_family_observer_script_dispatch_end(void)
{
 if(!script19.enabled&&!script19.enabled31)return;
 if(!script19.dispatch){script19.stage=5;return;}
 if(script19.stage==3&&script19.count==1&&!script19_stream.inflight&&script19_stream_current()&&
  eventLoc==script19.event+1&&eventRec[eventLoc-1].eventtime>curLoc&&script19_synchronous(true,true))script19.stage=4;
 else if(script19.attempted)script19.stage=5;
 script19.dispatch=false;
}
B313TerrainScriptReceipt b313_family_observer_script_receipt(void)
{
 B313TerrainScriptReceipt r={0};r.requested=script19_requested();r.session_enabled=script19_stream.enabled;
 r.frame_enabled=script19.enabled;r.policy_failed=script19_stream.policy_failed;r.loaded=script19_stream.loaded;
 r.stream_broken=script19_stream.broken;r.next_event=script19_stream.next;r.dispatch_open=script19.dispatch;
 r.event_inflight=script19_stream.inflight;r.event_count=script19.count;r.stage=script19.stage;r.attempted=script19.attempted;
 r.close_seen=script19.close_seen;r.close_success=script19.close_success;r.close_cause=script19.close_cause;
 r.close_calls=script19.close_calls;r.successful_closes=script19.successful_closes;
 r.close_order=script19.close_order;r.close_lifetime=script19.close_lifetime;r.origin=script19.origin.frame;
 r.origin_surface=script19.origin.surface;r.origin_pixels=script19.origin.pixels;r.origin_format=script19.origin.format;
 r.origin_target_calls=script19.origin.target_calls;r.frame_origin=terrain.origin.frame;
 r.frame_origin_surface=terrain.origin.surface;r.frame_origin_pixels=terrain.origin.pixels;r.frame_origin_format=terrain.origin.format;
 r.frame_origin_target_calls=terrain.origin.target_calls;
 r.event=script19.event;r.time=script19.time;r.allocation_serial=s.allocation_serial;
 r.old_window=script19.old_window;r.pending=pending.ready;r.used_groups=used_groups;
 r.current_window=window;r.birth_active=birth.active;r.tail_call_active=tail_call.active;
 r.terrain_valid=terrain.valid;r.spawn_active=terrain_spawn.active;r.pending_nonce=pending.ready?pending.borrow.nonce:0;
 r.spawn_continuity_lifetime=terrain.continuity_lifetime;
 r.target_seen=terrain.target_seen;r.consume_seen=terrain.consume_seen;r.target_calls=s.target_calls;
 for(unsigned i=0;i<25;i++)r.live_groups+=groups[i].live;
 for(unsigned i=0;i<100;i++)r.memberships+=membership[i]!=0;
 if(script19.event&&script19.event<=258)memcpy(r.data,script19_events[script19.event-1].d,sizeof r.data);
 r.committed=script19.stage==4;r.current=script19_current(&terrain.origin.frame);return r;
}
/* Separate pure policy receipt keeps the pre-existing script receipt ABI. */
B313TerrainScript31PolicyReceipt b313_family_observer_script31_policy_receipt(void)
{
 return (B313TerrainScript31PolicyReceipt){script31_requested(),script19_stream.enabled31,
  script19.enabled31,script19_stream.policy_failed};
}
