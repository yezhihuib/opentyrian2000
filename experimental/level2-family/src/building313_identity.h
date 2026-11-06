#ifndef BUILDING313_IDENTITY_H
#define BUILDING313_IDENTITY_H
#include <stdbool.h>
#include <stdint.h>
/* Private sidecar only: no native pixels, palette, or renderer admission API. */
#define B313_GROUP_CAPACITY 64u
#define B313_CALL_CAPACITY 128u
#define B313_SLOT_COUNT 100u
enum B313Reason {
 B313_SCOPE=1u,B313_OVERFLOW=2u,B313_PARTIAL=4u,B313_IDENTITY=8u,
 B313_REUSED=16u,B313_DUPLICATE=32u,B313_PHASE=64u,B313_GEOMETRY=128u,
 B313_FILTER=256u,B313_CALL_TOKEN=512u,B313_UNBOUND=1024u,B313_IO=2048u
};
typedef struct {
 unsigned slot,type,record,pool,bank,avail,size,cycle,filter;
 bool record_verified,graphics_verified,damaged,scoreitem;
 uintptr_t sheet_identity,data_identity;
 int ex,ey;
 unsigned base;
} B313Snapshot;
typedef struct {
 unsigned slot,parts,base,phase;
 uint64_t generation;
 B313Snapshot birth;
 int draw_x,draw_y;
 bool drawn;
} B313Member;
typedef struct {
 uint64_t nonce,scene;
 unsigned event_loc,cur_loc,birth_tick,pool,link,members,reasons;
 bool complete,identity_observed;
 B313Member member[4];
} B313Group;
typedef struct {
 uint64_t nonce,group,generation;
 unsigned slot,type,record,pool,bank,base,phase,part,filter,cycle;
 int x,y;
 bool ended;
} B313Call;
typedef struct {
 bool tracking,sampling,scene_valid,eligible,ledger_complete,old_hd_coverage_complete;
 uint64_t scene,frame,enemy_blit_ordinal;
 unsigned tick,groups,calls,reasons,identity_groups;
} B313Status;
void b313_scene_end(void);
void b313_scene_begin(bool target_scope);
bool b313_tracking(void);
bool b313_sampling(void);
void b313_frame_begin(unsigned tick,bool target_scope);
void b313_slot_allocated(unsigned slot);
uint64_t b313_group_begin(unsigned event_loc,unsigned cur_loc,unsigned tick,int type,unsigned pool,unsigned link);
void b313_group_member(uint64_t group,unsigned component,unsigned returned_slot1,const B313Snapshot *snapshot);
void b313_group_end(uint64_t group);
uint64_t b313_draw_begin(const B313Snapshot *snapshot,unsigned part,int x,int y,bool full_native_quad);
void b313_draw_end(uint64_t nonce);
bool b313_wants_slot(unsigned slot);
void b313_live_slot(unsigned slot,const B313Snapshot *snapshot);
void b313_frame_end(unsigned tick);
B313Status b313_status(void);
bool b313_get_group(unsigned index,B313Group *out);
bool b313_get_call(unsigned index,B313Call *out);
#ifdef B313_TESTING
void b313_test_reset(void);
void b313_test_nonces(uint64_t scene,uint64_t group,uint64_t call);
#endif
#endif
