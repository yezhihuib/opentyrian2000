/* Private ordinary family-canvas ground10 bridge with opt-in cliff12, corner366 and static340. Source INDEX bytes and native
 * draw order are never changed. No actor cache, draw lease or admission grant.
 * Each loader slot is 672 bytes; there are at most 72 Layer1 loader slots. */
#define FG_ROOT "assets/hd/current-terrain23"
#define FG_STATIC340_PATH "assets/hd/current-terrain24/terrain-shapesz-340-8.hda"
enum { FG_SOURCE_BYTES=672,FG_RGBA_BYTES=172032,FG_SLOTS=72 };
static const unsigned fg_ids[10]={372,380,390,367,368,376,378,386,387,388};
static const uint64_t fg_source_pins[10]={UINT64_C(0xe5ab487b1d777c88),UINT64_C(0xeaf92ca7e66b6029),UINT64_C(0x18e7b1576b2c866f),UINT64_C(0xb5c43e4d37eef3c1),UINT64_C(0xfbf4027a212bc257),UINT64_C(0xf164c0ad2583443f),UINT64_C(0x526beca231fd766a),UINT64_C(0x59cae4c3dc8ff0ee),UINT64_C(0x8bdf81b6fdfa4f28),UINT64_C(0x812a9162941357b3)};
static const uint64_t fg_payload_pins[10]={UINT64_C(0x979842c7fb07f657),UINT64_C(0x1319d37af0fcbb79),UINT64_C(0x5c79d31ca0640d11),UINT64_C(0x7f6d7c512bff04e6),UINT64_C(0xcae428fe01fd2a26),UINT64_C(0xcd88af59096f5597),UINT64_C(0xae8597271faf9c31),UINT64_C(0x360f6c61766416ad),UINT64_C(0x300e49764e3a21c7),UINT64_C(0x49817f3e5b941434)};
#include "b313_family_cliff_pins.inc"
#include "b313_redvent_pair.inc"
static struct {
 bool enabled,frame_requested,cache_ready,cache_failed,source_fault,support_ready;
 unsigned setting,first_reason;
 const Uint8 *rgba[12];
 Uint8 mask[64000],support[64000];
 uint64_t frames,cache_loads,target_tiles,target_pixels,rejected_frames;
 uint64_t support_session,support_frame,support_generation,support_epoch;
 uint64_t frame_target_pixels,surviving_logical_pixels,joint_accepted_frames,joint_presents;
 uint64_t target_tiles_by_id[12],target_pixels_by_id[12],frame_target_pixels_by_id[12],surviving_by_id[12];
} fl;
/* One independent opaque member. It is neither ground11 nor cliff13. */
static const uint64_t fg_corner_source_pin=UINT64_C(0x81b68a1f0eb10a8e);
static const uint64_t fg_corner_payload_pin=UINT64_C(0xb1b927d49fd73817);
static struct {
 bool enabled,frame_requested,cache_ready,cache_failed,source_fault,support_ready;
 unsigned setting,first_reason;
 const Uint8 *rgba;
 Uint8 mask[64000],support[64000];
 uint64_t frames,cache_loads,target_tiles,target_pixels,rejected_frames;
 uint64_t support_session,support_frame,support_generation,support_epoch;
 uint64_t frame_target_pixels,surviving_logical_pixels,joint_accepted_frames,joint_presents;
} fk;
/* Independent opaque static340 family; never borrows the legacy probe cache. */
static const uint64_t fg_static340_source_pin=UINT64_C(0x5488748d1b6f0a96);
static const uint64_t fg_static340_payload_pin=UINT64_C(0x1b469b4a10a446c6);
static struct {
 bool enabled,frame_requested,cache_ready,cache_failed,source_fault,support_ready;
 unsigned setting,first_reason;
 const Uint8 *rgba;
 Uint8 mask[64000],support[64000];
 uint64_t frames,cache_loads,target_tiles,target_pixels,rejected_frames;
 uint64_t support_session,support_frame,support_generation,support_epoch;
 uint64_t frame_target_pixels,surviving_logical_pixels,joint_accepted_frames,joint_presents;
} fs340;
static struct {
 bool frame_requested,in_pixel,cache_ready,cache_failed,map_z,source_fault,enabled,pass,row,done;
 uint64_t epoch,frame_epoch,frame_generation;
 const Uint8 *rgba[10];
 struct { const Uint8 *data;unsigned id;int member,cliff_member;bool corner_member,static340_member;Uint8 bytes[FG_SOURCE_BYTES]; } sources[FG_SLOTS];
 unsigned source_count,next_row,cursor,row_counts[12],row_expected[12];
 bool used[FG_SLOTS];
 const Uint8 *map_snapshot[8][12];
 Uint8 **first,**row_map; SDL_Surface *surface; int x,y,row_y,row_slots[12];
 uint64_t frames,passes,rows,target_tiles,target_pixels,native_callbacks,rejected_frames;
 Uint8 ground_mask[64000];
 uint64_t cache_loads,frame_target_pixels,surviving_logical_pixels,joint_accepted_frames,joint_presents;
 unsigned first_reason;
} fg;
enum {FG_CONFIG=1,FG_CACHE=2,FG_SOURCE=3,FG_PASS=4,FG_ROW=5,FG_CALLBACK=6,FG_END=7,FG_LEASE=8,FG_RESET=9,FG_ORDER=10};
static int fg_member(unsigned id){for(int i=0;i<10;i++)if(id==fg_ids[i])return i;return -1;}
static uint64_t fg_hash(const Uint8 *p,size_t n)
{uint64_t h=UINT64_C(0xcbf29ce484222325);while(n--){h^=*p++;h*=UINT64_C(0x100000001b3);}return h;}
static int fg_effective_member(unsigned slot)
{int m=fg.sources[slot].member,r=rp_member(fg.sources[slot].id);return m>=0?m:rp.enabled&&r>=0?10+r:-1;}
static void fg_fault(unsigned reason)
{
 if(fg.frame_requested&&!fg.first_reason)fg.first_reason=reason;
 fl.support_ready=fk.support_ready=fs340.support_ready=false;
 if(fl.frame_requested){if(!fl.first_reason)fl.first_reason=reason;if(!fc.frame_failed)++fl.rejected_frames;}
 if(fk.frame_requested){if(!fk.first_reason)fk.first_reason=reason;if(!fc.frame_failed)++fk.rejected_frames;}
 if(fs340.frame_requested){if(!fs340.first_reason)fs340.first_reason=reason;if(!fc.frame_failed)++fs340.rejected_frames;}
 if(!fc.frame_failed&&fg.frame_requested)++fg.rejected_frames;
 family_fault(FC_GROUND);
}
/* The independent switch defaults off and cannot turn on any old path. */
static bool fg_requested(void)
{
#if B313_FAMILY_CANVAS_DIAGNOSTIC
 const char *e=getenv("BUILDING313_FAMILY_GROUND_ENABLE");
 return render_mirror_family_requested()&&e&&!strcmp(e,"1");
#else
 return false;
#endif
}
/* A change is admitted only by the next family_begin. A mid-frame change
 * revokes the complete terrain transaction; it cannot acquire a new lease. */
static unsigned fg_cliff_setting(void)
{
#if B313_FAMILY_CANVAS_DIAGNOSTIC
 const char *e=getenv("BUILDING313_FAMILY_CLIFF_ENABLE");
 return !e||!strcmp(e,"0")?0:!strcmp(e,"1")?1:2;
#else
 return 0;
#endif
}
static bool fg_cliff_requested(void){return render_mirror_family_requested()&&fg_cliff_setting()==1;}
static unsigned fg_corner_setting(void)
{
#if B313_FAMILY_CANVAS_DIAGNOSTIC
 const char *e=getenv("BUILDING313_FAMILY_CORNER_ENABLE");
 return !e||!strcmp(e,"0")?0:!strcmp(e,"1")?1:2;
#else
 return 0;
#endif
}
static bool fg_corner_requested(void){return render_mirror_family_requested()&&fg_corner_setting()==1;}
static unsigned fg_static340_setting(void)
{
#if B313_FAMILY_CANVAS_DIAGNOSTIC
 const char *e=getenv("BUILDING313_FAMILY_STATIC340_ENABLE");
 return !e||!strcmp(e,"0")?0:!strcmp(e,"1")?1:2;
#else
 return 0;
#endif
}
static bool fg_static340_requested(void){return render_mirror_family_requested()&&fg_static340_setting()==1;}
static int fg_cliff_member(unsigned id){for(int i=0;i<12;i++)if(id==fg_cliff_ids[i])return i;return -1;}
static bool fg_cliff_solid(unsigned member,unsigned off)
{return (fg_cliff_masks[member][off/8]>>(off%8))&1;}
static void fg_revoke(void){rp.enabled=false;fs340.enabled=fs340.support_ready=false;fk.enabled=fk.support_ready=false;fl.enabled=fl.support_ready=false;fg.in_pixel=fg.pass=fg.row=fg.done=fg.enabled=false;fg.first=NULL;fg.row_map=NULL;fg.surface=NULL;}
static void fg_free_ground_cache(void)
{
 fg_revoke(); /* Revoke the shared transaction before freeing this family. */
 for(unsigned i=0;i<10;i++){free((void *)fg.rgba[i]);fg.rgba[i]=NULL;}
 fg.cache_ready=false;
}
static void fg_free_cliff_cache(void)
{
 fg_revoke();
 for(unsigned i=0;i<12;i++){free((void *)fl.rgba[i]);fl.rgba[i]=NULL;}
 fl.cache_ready=false;
}
static void fg_free_corner_cache(void)
{
 fg_revoke();
 free((void *)fk.rgba);fk.rgba=NULL;fk.cache_ready=false;
}
static void fg_free_static340_cache(void)
{
 fg_revoke();
 free((void *)fs340.rgba);fs340.rgba=NULL;fs340.cache_ready=false;
}
static void fg_free_cache(void){rp_free();fg_free_ground_cache();fg_free_cliff_cache();fg_free_corner_cache();fg_free_static340_cache();}
static Uint32 fg_le32(const Uint8 *p){return (Uint32)p[0]|(Uint32)p[1]<<8|(Uint32)p[2]<<16|(Uint32)p[3]<<24;}
static bool fg_cache_load(void)
{
 if(fg.cache_ready)return true;
 if(fg.cache_failed)return false;
 for(unsigned i=0;i<10;i++) {
  char path[512];snprintf(path,sizeof path,FG_ROOT "/terrain-shapesz-%u-8.hda",fg_ids[i]);
  FILE *f=fopen(path,"rb");Uint8 header[28],*p=NULL;bool ok=f!=NULL;
  if(ok)ok=fread(header,1,sizeof header,f)==sizeof header;
  if(ok)ok=!memcmp(header,"HDR1",4)&&fg_le32(header+4)==2010000+fg_ids[i]&&fg_le32(header+8)==8&&fg_le32(header+12)==24&&fg_le32(header+16)==28&&!fg_le32(header+20)&&!fg_le32(header+24);
  if(ok){p=malloc(FG_RGBA_BYTES);ok=p!=NULL;}
  if(ok)ok=fread(p,1,FG_RGBA_BYTES,f)==FG_RGBA_BYTES&&fgetc(f)==EOF&&!ferror(f);
  if(f&&fclose(f))ok=false;
  if(ok)ok=fg_hash(p,FG_RGBA_BYTES)==fg_payload_pins[i];
  if(ok)for(unsigned n=3;n<FG_RGBA_BYTES;n+=4)if(p[n]!=255){ok=false;break;}
  if(!ok){free(p);fg.cache_failed=true;fg_free_ground_cache();return false;}
  fg.rgba[i]=p;
 }
 fg.cache_ready=true;fg.cache_loads+=10;return true;
}
static bool fg_cliff_cache_load(void)
{
 if(fl.cache_ready)return true;
 if(fl.cache_failed)return false;
 for(unsigned i=0;i<12;i++) {
  char path[512];snprintf(path,sizeof path,FG_ROOT "/terrain-shapesz-%u-8.hda",fg_cliff_ids[i]);
  FILE *f=fopen(path,"rb");Uint8 header[28],*p=NULL;bool ok=f!=NULL;
  if(ok)ok=fread(header,1,sizeof header,f)==sizeof header;
  if(ok)ok=!memcmp(header,"HDR1",4)&&fg_le32(header+4)==2010000+fg_cliff_ids[i]&&fg_le32(header+8)==8&&fg_le32(header+12)==24&&fg_le32(header+16)==28&&!fg_le32(header+20)&&!fg_le32(header+24);
  if(ok){p=malloc(FG_RGBA_BYTES);ok=p!=NULL;}
  if(ok)ok=fread(p,1,FG_RGBA_BYTES,f)==FG_RGBA_BYTES&&fgetc(f)==EOF&&!ferror(f);
  if(f&&fclose(f))ok=false;
  if(ok)ok=fg_hash(p,FG_RGBA_BYTES)==fg_cliff_payload_pins[i];
  if(ok)for(unsigned y=0;y<224&&ok;y++)for(unsigned x=0;x<192;x++) {
   bool solid=fg_cliff_solid(i,(y/8)*24+x/8);const Uint8 *q=p+4*(y*192+x);
   if(q[3]!=(solid?255:0)||(!solid&&(q[0]||q[1]||q[2]))){ok=false;break;}
  }
  if(!ok){free(p);fl.cache_failed=true;fg_free_cliff_cache();return false;}
  fl.rgba[i]=p;
 }
 fl.cache_ready=true;fl.cache_loads+=12;return true;
}
static bool fg_corner_cache_load(void)
{
 if(fk.cache_ready)return true;
 if(fk.cache_failed)return false;
 FILE *f=fopen(FG_ROOT "/terrain-shapesz-366-8.hda","rb");Uint8 header[28],*p=NULL;bool ok=f!=NULL;
 if(ok)ok=fread(header,1,sizeof header,f)==sizeof header;
 if(ok)ok=!memcmp(header,"HDR1",4)&&fg_le32(header+4)==2010366&&fg_le32(header+8)==8&&fg_le32(header+12)==24&&fg_le32(header+16)==28&&!fg_le32(header+20)&&!fg_le32(header+24);
 if(ok){p=malloc(FG_RGBA_BYTES);ok=p!=NULL;}
 if(ok)ok=fread(p,1,FG_RGBA_BYTES,f)==FG_RGBA_BYTES&&fgetc(f)==EOF&&!ferror(f);
 if(f&&fclose(f))ok=false;
 if(ok)ok=fg_hash(p,FG_RGBA_BYTES)==fg_corner_payload_pin;
 if(ok)for(unsigned n=3;n<FG_RGBA_BYTES;n+=4)if(p[n]!=255){ok=false;break;}
 if(!ok){free(p);fk.cache_failed=true;fg_free_corner_cache();return false;}
 fk.rgba=p;fk.cache_ready=true;++fk.cache_loads;return true;
}
static bool fg_static340_cache_load(void)
{
 if(fs340.cache_ready)return true;
 if(fs340.cache_failed)return false;
 FILE *f=fopen(FG_STATIC340_PATH,"rb");Uint8 header[28],*p=NULL;bool ok=f!=NULL;
 if(ok)ok=fread(header,1,sizeof header,f)==sizeof header;
 if(ok)ok=!memcmp(header,"HDR1",4)&&fg_le32(header+4)==2010340&&fg_le32(header+8)==8&&fg_le32(header+12)==24&&fg_le32(header+16)==28&&!fg_le32(header+20)&&!fg_le32(header+24);
 if(ok){p=malloc(FG_RGBA_BYTES);ok=p!=NULL;}
 if(ok)ok=fread(p,1,FG_RGBA_BYTES,f)==FG_RGBA_BYTES&&fgetc(f)==EOF&&!ferror(f);
 if(f&&fclose(f))ok=false;
 if(ok)ok=fg_hash(p,FG_RGBA_BYTES)==fg_static340_payload_pin;
 if(ok)for(unsigned n=3;n<FG_RGBA_BYTES;n+=4)if(p[n]!=255){ok=false;break;}
 if(!ok){free(p);fs340.cache_failed=true;fg_free_static340_cache();return false;}
 fs340.rgba=p;fs340.cache_ready=true;++fs340.cache_loads;return true;
}
static bool fg_cliff_config_current(void)
{
 if(!render_mirror_family_requested()||fl.setting==fg_cliff_setting())return true;
 fg_fault(FG_CONFIG);fg_free_cliff_cache();return false;
}
static bool fg_corner_config_current(void)
{
 if(!render_mirror_family_requested()||fk.setting==fg_corner_setting())return true;
 fg_fault(FG_CONFIG);fg_free_corner_cache();return false;
}
static bool fg_static340_config_current(void)
{
 if(!render_mirror_family_requested()||fs340.setting==fg_static340_setting())return true;
 fg_fault(FG_CONFIG);fg_free_static340_cache();return false;
}
static bool fg_config_current(void)
{if(render_mirror_family_requested()&&!rp_current()){fg_fault(FG_CONFIG);return false;}return fg_cliff_config_current()&&fg_corner_config_current()&&fg_static340_config_current();}
static void fg_reset(void)
{
 if(fg.enabled&&(fg.pass||fg.row||fc.ready))fg_fault(FG_RESET);
 fg_revoke();
 if(!fg_requested())fg_free_ground_cache();
 if(!fg_cliff_requested())fg_free_cliff_cache();
 if(!fg_corner_requested())fg_free_corner_cache();
 if(!fg_static340_requested())fg_free_static340_cache();
}
static void fg_map_begin(char shape)
{
 rp_map_begin();
 fg_reset();
 if(fg.epoch==UINT64_MAX){fg.source_fault=true;return;}
 ++fg.epoch;fg.source_count=0;fg.source_fault=false;fl.source_fault=false;fk.source_fault=false;fs340.source_fault=false;fg.map_z=shape=='Z'||shape=='z';
 memset(fg.sources,0,sizeof fg.sources);
}
static void fg_bind(unsigned layer,unsigned id,const Uint8 *data)
{
 if(!render_mirror_family_requested()||!fg.map_z||layer!=1)return;
 if(fg.enabled||fg.pass||fg.row){fg_fault(FG_SOURCE);fg.source_fault=true;return;}
 uintptr_t p=(uintptr_t)data,b=(uintptr_t)&megaData1.shapes[0];
 if(!data||id<1||id>600||p<b||p-b>=sizeof megaData1.shapes||(p-b)%FG_SOURCE_BYTES||fg.source_count>=FG_SLOTS){fg.source_fault=true;return;}
 for(unsigned i=0;i<fg.source_count;i++)if(fg.sources[i].data==data){fg.source_fault=true;return;}
 unsigned n=fg.source_count++;int member=fg_member(id);
 fg.sources[n].data=data;fg.sources[n].id=id;fg.sources[n].member=member;fg.sources[n].cliff_member=fg_cliff_member(id);fg.sources[n].corner_member=id==366;fg.sources[n].static340_member=id==340;
 memcpy(fg.sources[n].bytes,data,FG_SOURCE_BYTES);
 rp_bind(id,data);
 if(member>=0) {
  if(fg_hash(data,FG_SOURCE_BYTES)!=fg_source_pins[member])fg.source_fault=true;
  for(unsigned k=0;k<FG_SOURCE_BYTES;k++)if(!data[k])fg.source_fault=true;
 }
 if(fg.sources[n].corner_member) {
  if(fg_hash(data,FG_SOURCE_BYTES)!=fg_corner_source_pin)fk.source_fault=true;
  for(unsigned k=0;k<FG_SOURCE_BYTES;k++)if(!data[k])fk.source_fault=true;
 }
 if(fg.sources[n].static340_member) {
  if(fg_hash(data,FG_SOURCE_BYTES)!=fg_static340_source_pin)fs340.source_fault=true;
  for(unsigned k=0;k<FG_SOURCE_BYTES;k++)if(!data[k])fs340.source_fault=true;
 }
 int cliff=fg.sources[n].cliff_member;
 if(cliff>=0) {
  if(fg_hash(data,FG_SOURCE_BYTES)!=fg_cliff_source_pins[cliff])fl.source_fault=true;
  for(unsigned k=0;k<FG_SOURCE_BYTES;k++)if((data[k]!=0)!=fg_cliff_solid((unsigned)cliff,k))fl.source_fault=true;
 }
}
static void fg_frame_begin(void)
{
 /* family_begin already rejects abandoned active frames; never carry a pass.
  * All loader slots are registered at map load even while optional families are OFF. A new
  * ON frame uses only that same pinned epoch plus exact live row snapshots. */
 fg_revoke();memset(fg.used,0,sizeof fg.used);fg.next_row=0;
 memset(fg.ground_mask,0,sizeof fg.ground_mask);fg.frame_target_pixels=fg.surviving_logical_pixels=0;
 memset(fl.mask,0,sizeof fl.mask);memset(fl.support,0,sizeof fl.support);
 memset(fl.frame_target_pixels_by_id,0,sizeof fl.frame_target_pixels_by_id);memset(fl.surviving_by_id,0,sizeof fl.surviving_by_id);
 fl.frame_target_pixels=fl.surviving_logical_pixels=0;fl.setting=fg_cliff_setting();
 memset(fk.mask,0,sizeof fk.mask);memset(fk.support,0,sizeof fk.support);
 fk.frame_target_pixels=fk.surviving_logical_pixels=0;fk.setting=fg_corner_setting();
 memset(fs340.mask,0,sizeof fs340.mask);memset(fs340.support,0,sizeof fs340.support);
 fs340.frame_target_pixels=fs340.surviving_logical_pixels=0;fs340.setting=fg_static340_setting();
 const char *setting=getenv("BUILDING313_FAMILY_GROUND_ENABLE");
 bool ground=fg_requested(),cliff=fg_cliff_requested(),corner=fg_corner_requested(),static340=fg_static340_requested();
 fg.frame_requested=ground;fl.frame_requested=cliff;fk.frame_requested=corner;fs340.frame_requested=static340;
 if(setting&&strcmp(setting,"0")&&strcmp(setting,"1")&&render_mirror_family_requested()){fg.frame_requested=fg.enabled=true;++fg.frames;fg_fault(FG_CONFIG);return;}
 /* Revoke the shared transaction first, then free only disabled families.
  * T ground cache identity/load counts remain untouched by cliff toggles. */
 if(!ground&&fg.cache_ready)fg_free_ground_cache();
 if(!cliff&&fl.cache_ready)fg_free_cliff_cache();
 if(!corner&&fk.cache_ready)fg_free_corner_cache();
 if(!static340&&fs340.cache_ready)fg_free_static340_cache();
 if(fl.setting==2&&render_mirror_family_requested()){fl.frame_requested=fg.enabled=fl.enabled=true;++fl.frames;fg_fault(FG_CONFIG);fg_free_cliff_cache();return;}
 if(cliff&&!ground){fl.enabled=true;++fl.frames;fg_fault(FG_CONFIG);fg_free_cliff_cache();return;}
 if(fk.setting==2&&render_mirror_family_requested()){fk.frame_requested=fg.enabled=fk.enabled=true;++fk.frames;fg_fault(FG_CONFIG);fg_free_corner_cache();return;}
 if(corner&&!ground){fk.enabled=true;++fk.frames;fg_fault(FG_CONFIG);fg_free_corner_cache();return;}
 if(fs340.setting==2&&render_mirror_family_requested()){fs340.frame_requested=fg.enabled=fs340.enabled=true;++fs340.frames;fg_fault(FG_CONFIG);fg_free_static340_cache();return;}
 if(static340&&!ground){fs340.enabled=true;++fs340.frames;fg_fault(FG_CONFIG);fg_free_static340_cache();return;}
 if(!rp_begin(render_mirror_family_requested(),ground)){fg.frame_requested=fg.enabled=true;fg_fault(FG_CACHE);return;}
 if(!ground)return;
 fg.enabled=true;fl.enabled=cliff;fk.enabled=corner;fs340.enabled=static340;
 ++fg.frames;
 if(cliff)++fl.frames;
 if(corner)++fk.frames;
 if(static340)++fs340.frames;
 fg.frame_epoch=fg.epoch;fg.frame_generation=fc_generation;
 if(!fg.epoch||!fg.map_z||fg.source_fault||!fg.source_count||(cliff&&fl.source_fault)||(corner&&fk.source_fault)||(static340&&fs340.source_fault)){fg_fault(FG_SOURCE);return;}
 if(!fg_cache_load()||(cliff&&!fg_cliff_cache_load())||(corner&&!fg_corner_cache_load())||(static340&&!fg_static340_cache_load())){fg_fault(FG_CACHE);return;}
}
static bool fg_current(void)
{
 if(!fg_config_current())return false;
 if(fg.enabled&&!fg_requested()){fg_fault(FG_CONFIG);fg_free_ground_cache();return false;}
 return rp_current()&&fg.enabled&&fg_requested()&&fg.cache_ready&&!fg.cache_failed&&(!fl.enabled||(fg_cliff_requested()&&fl.cache_ready&&!fl.cache_failed&&!fl.source_fault))&&(!fk.enabled||(fg_corner_requested()&&fk.cache_ready&&!fk.cache_failed&&!fk.source_fault))&&(!fs340.enabled||(fg_static340_requested()&&fs340.cache_ready&&!fs340.cache_failed&&!fs340.source_fault))&&fg.map_z&&!fg.source_fault&&fg.frame_epoch==fg.epoch&&fg.frame_generation==fc_generation&&family_geometry(false)&&!memcmp(fc_palette,rgb_palette,sizeof fc_palette);
}
static int fg_slot(const Uint8 *p)
{for(unsigned i=0;i<fg.source_count;i++)if(fg.sources[i].data==p)return (int)i;return -1;}
static bool fg_sources_current(void)
{
 for(unsigned i=0;i<fg.source_count;i++)if(fg.used[i]&&memcmp(fg.sources[i].bytes,fg.sources[i].data,FG_SOURCE_BYTES))return false;
 return true;
}
static bool fg_maps_current(unsigned rows)
{
 if(!fg.first||rows>8)return false;
 for(unsigned r=0;r<rows;r++)for(unsigned t=0;t<12;t++)if(fg.first[r*14+t]!=fg.map_snapshot[r][t])return false;
 return true;
}
void render_mirror_family_ground_layer1(SDL_Surface *s,Uint8 **first,int x,int y)
{
 if(fc.frame_failed||!fg_config_current()||!fg.enabled)return;
 uintptr_t b=(uintptr_t)megaData1.mainmap,p=(uintptr_t)first;
 const size_t bytes=sizeof megaData1.mainmap,needed=(7*14+12)*sizeof(Uint8 *);
 if(!fg_current()||fg.pass||fg.row||fg.done||s!=fc_source||s!=VGAScreen||x<0||x>32||y< -28||y> -1||p<b||p-b>bytes-needed||(p-b)%sizeof(Uint8 *)||((p-b)/sizeof(Uint8 *))%14>2){fg_fault(FG_PASS);return;}
 /* Authoritative Layer1 call site supplies the real first; later rows must
  * match this first + row*14 exactly, not merely any in-range map row. */
 fg.first=first;fg.surface=s;fg.x=x;fg.y=y;fg.next_row=0;fg.pass=true;++fg.passes;
}
static void fg_row_begin(SDL_Surface *s,int x,int y,Uint8 **map,int style)
{
 if(fc.frame_failed||!fg_config_current()||!fg.enabled)return;
 if(!fg.pass){if(fg.row)fg_fault(FG_ROW);return;} /* Native later layers. */
 if(!fg_current()||fg.row||fg.next_row>=8||s!=fg.surface||map!=fg.first+fg.next_row*14||x!=fg.x||y!=fg.y+(int)fg.next_row*28||style!=MIRROR_NORMAL){fg_fault(FG_ROW);return;}
 fg.row_map=map;fg.row_y=y;fg.cursor=0;memset(fg.row_counts,0,sizeof fg.row_counts);
 int visible=MIN(200,y+28)-MAX(0,y);if(visible<0)visible=0;
 for(unsigned t=0;t<12;t++) {
  fg.map_snapshot[fg.next_row][t]=map[t];fg.row_slots[t]=-1;fg.row_expected[t]=0;
  if(!map[t])continue;
  int n=fg_slot(map[t]);
  if(n<0||memcmp(fg.sources[n].data,fg.sources[n].bytes,FG_SOURCE_BYTES)){fg_fault(FG_SOURCE);return;}
  fg.row_slots[t]=n;fg.used[n]=true;
  if(fg_effective_member((unsigned)n)>=0){fg.row_expected[t]=(unsigned)visible*24;++fg.target_tiles;}
  else if(fl.enabled&&fg.sources[n].cliff_member>=0) {
   /* Native INDEX0 never has a callback. Count only visible nonzero support. */
   for(unsigned sy=0;sy<28;sy++)if(y+(int)sy>=0&&y+(int)sy<200)
    for(unsigned sx=0;sx<24;sx++)if(fg.sources[n].bytes[sy*24+sx])++fg.row_expected[t];
   ++fl.target_tiles;++fl.target_tiles_by_id[fg.sources[n].cliff_member];
  }
  else if(fk.enabled&&fg.sources[n].corner_member){fg.row_expected[t]=(unsigned)visible*24;++fk.target_tiles;}
  else if(fs340.enabled&&fg.sources[n].static340_member){fg.row_expected[t]=(unsigned)visible*24;++fs340.target_tiles;}
 }
 fg.row=true;
}
/* Enumerate exactly the ordinary native loop's observable stores, including
 * zero holes in non-target tiles and top/bottom clipping. x is in [0,32]. */
static bool fg_next(unsigned *tile,unsigned *offset,unsigned *screen)
{
 while(fg.cursor<28*12*24) {
  unsigned c=fg.cursor,sy=c/(12*24),t=(c%(12*24))/24,sx=c%24;int n=fg.row_slots[t],y=fg.row_y+(int)sy;
  if(y>=0&&y<200&&n>=0&&fg.sources[n].bytes[sy*24+sx]){*tile=t;*offset=sy*24+sx;*screen=(unsigned)y*320+(unsigned)fg.x+t*24+sx;return true;}
  ++fg.cursor;
 }
 return false;
}
static void fg_pixel(SDL_Surface *s,Uint8 *address,Uint8 source,int style,bool replaced)
{
 unsigned t=0,off=0,screen=0;int n=-1,member=-1,cliff=-1;bool corner=false,static340=false;
 if(fg.enabled&&fg.pass&&!fc.frame_failed) {
  if(!rp_current()||!fg.row||!fg.cache_ready||(fl.enabled&&(!fl.cache_ready||fl.source_fault))||(fk.enabled&&(!fk.cache_ready||fk.source_fault))||(fs340.enabled&&(!fs340.cache_ready||fs340.cache_failed||fs340.source_fault))||fg.source_fault||fg.frame_epoch!=fg.epoch||fg.frame_generation!=fc_generation||!family_geometry(false)||s!=fg.surface||style!=MIRROR_NORMAL||replaced||!fg_next(&t,&off,&screen)||(uintptr_t)address!=(uintptr_t)fc_source_pixels+screen){fg_fault(FG_CALLBACK);return;}
  n=fg.row_slots[t];member=fg_effective_member((unsigned)n);cliff=fl.enabled?fg.sources[n].cliff_member:-1;corner=fk.enabled&&fg.sources[n].corner_member;static340=fs340.enabled&&fg.sources[n].static340_member;
  if(fg.row_map[t]!=fg.sources[n].data||source!=fg.sources[n].bytes[off]||source!=fg.sources[n].data[off]||*address!=source){fg_fault(FG_SOURCE);return;}
 }
 fg.in_pixel=n>=0;
 family_pixel(s,address,style); /* Writer consumes the real native store first. */
 fg.in_pixel=false;
 if(n<0||fc.frame_failed)return;
 ++fg.cursor;++fg.native_callbacks;
 if(member<0&&cliff<0&&!corner&&!static340)return;
 if(!family_prepare_canvas()||fc.frame_failed){fg_fault(FG_LEASE);return;}
 unsigned x=screen%320,y=screen/320,sx0=off%24,sy0=off/24;
 const Uint8 *rgba=member>=0?(member<10?fg.rgba[member]:rp.rgba[member-10]):cliff>=0?fl.rgba[cliff]:corner?fk.rgba:fs340.rgba;
 for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++) {
  const Uint8 *p=rgba+((sy0*8+sy)*192+sx0*8+sx)*4;
  size_t dst=(size_t)(y*8+sy)*2560+x*8+sx;
  ((Uint32 *)canvas->pixels)[dst]=UINT32_C(0xff000000)|(Uint32)p[0]<<16|(Uint32)p[1]<<8|p[2];
  hd_owner[dst]=1;cloud_owner[dst]=0;green_first[dst]=0;
 }
 selected[screen]=1;++fg.row_counts[t];
 if(member>=0){fg.ground_mask[screen]=1;++fg.target_pixels;++fg.frame_target_pixels;}
 else if(cliff>=0){fl.mask[screen]=(Uint8)(cliff+1);++fl.target_pixels;++fl.frame_target_pixels;++fl.target_pixels_by_id[cliff];++fl.frame_target_pixels_by_id[cliff];}
 else if(corner){fk.mask[screen]=1;++fk.target_pixels;++fk.frame_target_pixels;}
 else{fs340.mask[screen]=1;++fs340.target_pixels;++fs340.frame_target_pixels;}
}
void render_mirror_family_ground_row_end(SDL_Surface *s,int x,int y,Uint8 **map)
{
 if(fc.frame_failed||!fg_config_current()||!fg.enabled||!fg.pass)return;
 unsigned t,off,screen;
 if(!fg.row||!fg_current()||!b313_family_writer_draw_ready(fc_frame)||s!=fg.surface||x!=fg.x||y!=fg.row_y||map!=fg.row_map||fg_next(&t,&off,&screen)||!fg_sources_current()||!fg_maps_current(fg.next_row+1)){fg_fault(FG_END);return;}
 for(unsigned i=0;i<12;i++)if(fg.row_counts[i]!=fg.row_expected[i]){fg_fault(FG_END);return;}
 fg.row=false;fg.row_map=NULL;++fg.next_row;++fg.rows;
}
void render_mirror_family_ground_end(void)
{
 if(fc.frame_failed||!fg_config_current()||!fg.enabled)return;
 if(!fg_current()||!b313_family_writer_draw_ready(fc_frame)||!fg.pass||fg.row||fg.next_row!=8||!fg_sources_current()||!fg_maps_current(8)){fg_fault(FG_END);return;}
 fg.pass=false;fg.done=true;tf_capture();
}
static bool fg_final_check(void)
{
 if(!fg_config_current())return false;
 if(!fg.enabled)return true;
 if(!fg_current()||fg.pass||fg.row||!fg.done||!fg_sources_current()||!fg_maps_current(8)){fg_fault(FG_LEASE);return false;}
 return true;
}
static bool fg_writer_entry(void)
{if(!fg_config_current())return false;if(fg.enabled&&fg.pass&&!fg.in_pixel){fg_fault(FG_CALLBACK);return false;}return true;}
static void fg_before_actor(void)
{if(!fg_config_current())return;if(fg.enabled&&(fg.pass||fg.row||!fg_final_check()))fg_fault(FG_ORDER);}
static void fg_native_written(unsigned off,int style)
{if(off<64000&&style!=MIRROR_SHADOW){fg.ground_mask[off]=0;fl.mask[off]=0;fk.mask[off]=0;fs340.mask[off]=0;}}
/* Pure snapshot counterpart of fg_final_check, for the read-only support
 * receipt. No fault, cache freeing or change to historical ground statistics. */
static bool fg_terrain_snapshot_current(void)
{
 return rp_current()&&fg.enabled&&fg_requested()&&fg.cache_ready&&!fg.cache_failed&&fg.map_z&&!fg.source_fault&&
  fl.setting==fg_cliff_setting()&&fk.setting==fg_corner_setting()&&fs340.setting==fg_static340_setting()&&
  (!fl.enabled||(fg_cliff_requested()&&fl.cache_ready&&!fl.cache_failed&&!fl.source_fault))&&
  (!fk.enabled||(fg_corner_requested()&&fk.cache_ready&&!fk.cache_failed&&!fk.source_fault))&&
  (!fs340.enabled||(fg_static340_requested()&&fs340.cache_ready&&!fs340.cache_failed&&!fs340.source_fault))&&
  fg.frame_epoch==fg.epoch&&fg.frame_generation==fc_generation&&fg.done&&!fg.pass&&!fg.row&&
  family_geometry(true)&&!memcmp(fc_palette,rgb_palette,sizeof fc_palette)&&fg_sources_current()&&fg_maps_current(8);
}
/* One shared pure survival predicate for admission and support receipts.
 * Historical draw counts cannot stand in for a surviving cropped cell. */
static bool fg_terrain_cell_survives(unsigned off)
{
 if(!rp_current()||off>=64000||!fg.enabled||!fg.done||fg.pass||fg.row||!fc_canvas_ready||fc.frame_failed)return false;
 unsigned x=off%320,y=off/320;
 if(y>=184||x<24||x>=288||(!fg.ground_mask[off]&&!(fl.enabled&&fl.mask[off])&&!(fk.enabled&&fk.mask[off])&&!(fs340.enabled&&fs340.mask[off])))return false;
 for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++)
  if(hd_owner[(y*8+sy)*2560+x*8+sx]!=1)return false;
 return true;
}
static bool fg_terrain_survives(void)
{
 for(unsigned y=0;y<184;y++)for(unsigned x=24;x<288;x++)
  if(fg_terrain_cell_survives(y*320+x))return true;
 return false;
}
static void fg_on_accept(void)
{
 fg.surviving_logical_pixels=0;
 if(!fg.enabled||!fg.done||!fc.ready||fc.frame_failed)return;
 for(unsigned y=0;y<184;y++)for(unsigned x=24;x<288;x++)if(fg.ground_mask[y*320+x]) {
  bool owned=true;
  for(unsigned sy=0;sy<8&&owned;sy++)for(unsigned sx=0;sx<8;sx++)if(hd_owner[(y*8+sy)*2560+x*8+sx]!=1){owned=false;break;}
  if(owned)++fg.surviving_logical_pixels;
 }
 if(fg.surviving_logical_pixels)++fg.joint_accepted_frames;
 if(fl.enabled) {
  for(unsigned y=0;y<184;y++)for(unsigned x=24;x<288;x++)if(fl.mask[y*320+x]) {
   bool owned=true;
   for(unsigned sy=0;sy<8&&owned;sy++)for(unsigned sx=0;sx<8;sx++)if(hd_owner[(y*8+sy)*2560+x*8+sx]!=1){owned=false;break;}
   if(owned){unsigned member=fl.mask[y*320+x]-1;fl.support[y*320+x]=(Uint8)(member+1);++fl.surviving_logical_pixels;++fl.surviving_by_id[member];}
  }
  fl.support_session=fc_session;fl.support_frame=fc_frame;fl.support_generation=fc_generation;fl.support_epoch=fg.epoch;
  fl.support_ready=true;if(fl.surviving_logical_pixels)++fl.joint_accepted_frames;
 }
 if(fk.enabled) {
  for(unsigned y=0;y<184;y++)for(unsigned x=24;x<288;x++)if(fk.mask[y*320+x]) {
   bool owned=true;
   for(unsigned sy=0;sy<8&&owned;sy++)for(unsigned sx=0;sx<8;sx++)if(hd_owner[(y*8+sy)*2560+x*8+sx]!=1){owned=false;break;}
   if(owned){fk.support[y*320+x]=1;++fk.surviving_logical_pixels;}
  }
  fk.support_session=fc_session;fk.support_frame=fc_frame;fk.support_generation=fc_generation;fk.support_epoch=fg.epoch;
  fk.support_ready=true;if(fk.surviving_logical_pixels)++fk.joint_accepted_frames;
 }
 if(fs340.enabled) {
  for(unsigned y=0;y<184;y++)for(unsigned x=24;x<288;x++)if(fs340.mask[y*320+x]) {
   bool owned=true;
   for(unsigned sy=0;sy<8&&owned;sy++)for(unsigned sx=0;sx<8;sx++)if(hd_owner[(y*8+sy)*2560+x*8+sx]!=1){owned=false;break;}
   if(owned){fs340.support[y*320+x]=1;++fs340.surviving_logical_pixels;}
  }
  fs340.support_session=fc_session;fs340.support_frame=fc_frame;fs340.support_generation=fc_generation;fs340.support_epoch=fg.epoch;
  fs340.support_ready=true;if(fs340.surviving_logical_pixels)++fs340.joint_accepted_frames;
 }
}
static void fg_on_present(void)
{if(fg.enabled&&!fc.frame_failed&&fg.surviving_logical_pixels)++fg.joint_presents;if(fl.enabled&&!fc.frame_failed&&fl.surviving_logical_pixels)++fl.joint_presents;if(fk.enabled&&!fc.frame_failed&&fk.surviving_logical_pixels)++fk.joint_presents;if(fs340.enabled&&!fc.frame_failed&&fs340.surviving_logical_pixels)++fs340.joint_presents;}
B313FamilyGroundStatus render_mirror_family_ground_status(void)
{
 B313FamilyGroundStatus s={0};
 s.requested=fg_requested();s.enabled=fg.enabled;s.cache_ready=fg.cache_ready;s.frame_failed=fc.frame_failed;
 s.pass_active=fg.pass;s.row_active=fg.row;s.pass_done=fg.done;s.first_reason=fg.first_reason;
 s.session=fc_session;s.frame=fc_frame;s.map_epoch=fg.epoch;s.cache_loads=fg.cache_loads;
 s.frames=fg.frames;s.passes=fg.passes;s.rows=fg.rows;s.target_tiles=fg.target_tiles;s.target_pixels=fg.target_pixels;
 s.frame_family_draws=fc_frame_draws;
 s.native_callbacks=fg.native_callbacks;s.rejected_frames=fg.rejected_frames;s.frame_target_pixels=fg.frame_target_pixels;
 s.surviving_logical_pixels=fg.surviving_logical_pixels;s.joint_accepted_frames=fg.joint_accepted_frames;s.joint_presents=fg.joint_presents;
 return s;
}
/* Snapshot readers have no mutation or admission side effects. They are not
 * callable evidence of Present: joint_presents advances only after SDL Present. */
/* Pure sibling guard: getters must reject stale shared-frame configuration
 * immediately, without invoking the mutating frame-boundary fault handler. */
static bool fg_corner_snapshot_current(void)
{
 return fk.setting==fg_corner_setting()&&(fk.setting==0||
  (fk.setting==1&&fk.enabled&&fk.cache_ready&&!fk.cache_failed&&!fk.source_fault));
}
static bool fg_static340_snapshot_current(void)
{
 return fs340.setting==fg_static340_setting()&&(fs340.setting==0||
  (fs340.setting==1&&fs340.enabled&&fs340.cache_ready&&!fs340.cache_failed&&!fs340.source_fault));
}
static bool fg_cliff_support_current(void)
{
 return rp_current()&&fl.support_ready&&fg_corner_snapshot_current()&&fg_static340_snapshot_current()&&render_mirror_family_requested()&&fg_requested()&&fg.enabled&&fg.cache_ready&&!fg.cache_failed&&!fg.source_fault&&
  fl.enabled&&fl.cache_ready&&!fl.cache_failed&&!fl.source_fault&&!fc.frame_failed&&fl.setting==1&&fg_cliff_setting()==1&&
  fg.done&&!fg.pass&&!fg.row&&fl.support_session==fc_session&&fl.support_frame==fc_frame&&
  fl.support_generation==fc_generation&&fl.support_epoch==fg.epoch&&fg.frame_epoch==fg.epoch&&
  family_geometry(true)&&!memcmp(fc_palette,rgb_palette,sizeof fc_palette)&&fg_sources_current()&&fg_maps_current(8);
}
B313FamilyCliffStatus render_mirror_family_cliff_status(void)
{
 B313FamilyCliffStatus s={0};
 s.requested=fg_cliff_requested();s.enabled=fl.enabled;s.cache_ready=fl.cache_ready;s.frame_failed=fc.frame_failed;
 s.pass_active=fl.enabled&&fg.pass;s.row_active=fl.enabled&&fg.row;s.pass_done=fl.enabled&&fg.done;
 s.support_ready=fg_cliff_support_current();s.first_reason=fl.first_reason;
 s.session=fc_session;s.frame=fc_frame;s.map_epoch=fg.epoch;s.cache_loads=fl.cache_loads;
 s.frames=fl.frames;s.target_tiles=fl.target_tiles;s.target_pixels=fl.target_pixels;s.rejected_frames=fl.rejected_frames;
 s.frame_family_draws=fc_frame_draws;s.frame_target_pixels=fl.frame_target_pixels;s.surviving_logical_pixels=fl.surviving_logical_pixels;
 s.joint_accepted_frames=fl.joint_accepted_frames;s.joint_presents=fl.joint_presents;
 for(unsigned i=0;i<12;i++) {
  s.ids[i]=fg_cliff_ids[i];s.target_tiles_by_id[i]=fl.target_tiles_by_id[i];s.target_pixels_by_id[i]=fl.target_pixels_by_id[i];
  s.frame_target_pixels_by_id[i]=fl.frame_target_pixels_by_id[i];s.surviving_by_id[i]=fl.surviving_by_id[i];
 }
 return s;
}
bool render_mirror_family_cliff_support(uint8_t *out,size_t bytes)
{
 if(!out||bytes!=sizeof fl.support||!fg_cliff_support_current())return false;
 memcpy(out,fl.support,sizeof fl.support);return true;
}
static bool fg_corner_support_current(void)
{
 return rp_current()&&fk.support_ready&&fg_static340_snapshot_current()&&render_mirror_family_requested()&&fg_requested()&&fg.enabled&&fg.cache_ready&&!fg.cache_failed&&!fg.source_fault&&
  fk.enabled&&fk.setting==1&&fg_corner_snapshot_current()&&!fc.frame_failed&&
  fl.setting==fg_cliff_setting()&&(fl.setting==0||(fl.setting==1&&fl.enabled&&fl.cache_ready&&!fl.cache_failed&&!fl.source_fault))&&
  fg.done&&!fg.pass&&!fg.row&&fk.support_session==fc_session&&fk.support_frame==fc_frame&&
  fk.support_generation==fc_generation&&fk.support_epoch==fg.epoch&&fg.frame_epoch==fg.epoch&&
  family_geometry(true)&&!memcmp(fc_palette,rgb_palette,sizeof fc_palette)&&fg_sources_current()&&fg_maps_current(8);
}
B313FamilyCornerStatus render_mirror_family_corner_status(void)
{
 B313FamilyCornerStatus s={0};
 s.id=366;s.requested=fg_corner_requested();s.enabled=fk.enabled;s.cache_ready=fk.cache_ready;s.frame_failed=fc.frame_failed;
 s.pass_active=fk.enabled&&fg.pass;s.row_active=fk.enabled&&fg.row;s.pass_done=fk.enabled&&fg.done;
 s.support_ready=fg_corner_support_current();s.first_reason=fk.first_reason;
 s.session=fc_session;s.frame=fc_frame;s.map_epoch=fg.epoch;s.cache_loads=fk.cache_loads;
 s.frames=fk.frames;s.target_tiles=fk.target_tiles;s.target_pixels=fk.target_pixels;s.rejected_frames=fk.rejected_frames;
 s.frame_family_draws=fc_frame_draws;s.frame_target_pixels=fk.frame_target_pixels;s.surviving_logical_pixels=fk.surviving_logical_pixels;
 s.joint_accepted_frames=fk.joint_accepted_frames;s.joint_presents=fk.joint_presents;
 return s;
}
bool render_mirror_family_corner_support(uint8_t *out,size_t bytes)
{
 if(!out||bytes!=sizeof fk.support||!fg_corner_support_current())return false;
 memcpy(out,fk.support,sizeof fk.support);return true;
}
static void fg_corner_report(void)
{
 if(!fk.frames&&!fk.first_reason)return;
 FILE *f=fopen("building313-family-corner.json.tmp","w");if(!f){fprintf(stderr,"B313_FAMILY_CORNER_REPORT_FAILED\n");return;}
 B313FamilyCornerStatus s=render_mirror_family_corner_status();
 fprintf(f,"{\"schema\":1,\"id\":366");
#define CORNER_BOOL(field) fprintf(f,",\"" #field "\":%s",s.field?"true":"false")
#define CORNER_COUNT(field) fprintf(f,",\"" #field "\":%llu",(unsigned long long)s.field)
 CORNER_BOOL(requested);CORNER_BOOL(enabled);CORNER_BOOL(cache_ready);CORNER_BOOL(frame_failed);CORNER_BOOL(pass_active);CORNER_BOOL(row_active);CORNER_BOOL(pass_done);CORNER_BOOL(support_ready);
 CORNER_COUNT(first_reason);CORNER_COUNT(session);CORNER_COUNT(frame);CORNER_COUNT(map_epoch);CORNER_COUNT(cache_loads);
 CORNER_COUNT(frames);CORNER_COUNT(target_tiles);CORNER_COUNT(target_pixels);CORNER_COUNT(rejected_frames);
 CORNER_COUNT(frame_family_draws);CORNER_COUNT(frame_target_pixels);CORNER_COUNT(surviving_logical_pixels);CORNER_COUNT(joint_accepted_frames);CORNER_COUNT(joint_presents);
#undef CORNER_BOOL
#undef CORNER_COUNT
 fprintf(f,",\"production_enabled\":false,\"length_damage_tests\":\"SKIPPED_UNVERIFIED\"}\n");
 bool bad=ferror(f);int c=fclose(f);if(bad||c||rename("building313-family-corner.json.tmp","building313-family-corner.json"))fprintf(stderr,"B313_FAMILY_CORNER_REPORT_FAILED\n");
}
static bool fg_static340_support_current(void)
{
 return rp_current()&&fs340.support_ready&&fg_corner_snapshot_current()&&render_mirror_family_requested()&&fg_requested()&&fg.enabled&&fg.cache_ready&&!fg.cache_failed&&!fg.source_fault&&
  fs340.enabled&&fs340.setting==1&&fg_static340_snapshot_current()&&!fc.frame_failed&&
  fl.setting==fg_cliff_setting()&&(fl.setting==0||(fl.setting==1&&fl.enabled&&fl.cache_ready&&!fl.cache_failed&&!fl.source_fault))&&
  fg.done&&!fg.pass&&!fg.row&&fs340.support_session==fc_session&&fs340.support_frame==fc_frame&&
  fs340.support_generation==fc_generation&&fs340.support_epoch==fg.epoch&&fg.frame_epoch==fg.epoch&&
  family_geometry(true)&&!memcmp(fc_palette,rgb_palette,sizeof fc_palette)&&fg_sources_current()&&fg_maps_current(8);
}
B313FamilyStatic340Status render_mirror_family_static340_status(void)
{
 B313FamilyStatic340Status s={0};
 s.id=340;s.requested=fg_static340_requested();s.enabled=fs340.enabled;s.cache_ready=fs340.cache_ready;s.frame_failed=fc.frame_failed;
 s.pass_active=fs340.enabled&&fg.pass;s.row_active=fs340.enabled&&fg.row;s.pass_done=fs340.enabled&&fg.done;
 s.support_ready=fg_static340_support_current();s.first_reason=fs340.first_reason;
 s.session=fc_session;s.frame=fc_frame;s.map_epoch=fg.epoch;s.cache_loads=fs340.cache_loads;
 s.frames=fs340.frames;s.target_tiles=fs340.target_tiles;s.target_pixels=fs340.target_pixels;s.rejected_frames=fs340.rejected_frames;
 s.frame_family_draws=fc_frame_draws;s.frame_target_pixels=fs340.frame_target_pixels;s.surviving_logical_pixels=fs340.surviving_logical_pixels;
 s.joint_accepted_frames=fs340.joint_accepted_frames;s.joint_presents=fs340.joint_presents;
 return s;
}
bool render_mirror_family_static340_support(uint8_t *out,size_t bytes)
{
 if(!out||bytes!=sizeof fs340.support||!fg_static340_support_current())return false;
 memcpy(out,fs340.support,sizeof fs340.support);return true;
}
static void fg_static340_report(void)
{
 if(!fs340.frames&&!fs340.first_reason)return;
 FILE *f=fopen("building313-family-static340.json.tmp","w");if(!f){fprintf(stderr,"B313_FAMILY_STATIC340_REPORT_FAILED\n");return;}
 B313FamilyStatic340Status s=render_mirror_family_static340_status();
 fprintf(f,"{\"schema\":1,\"id\":340");
#define STATIC340_BOOL(field) fprintf(f,",\"" #field "\":%s",s.field?"true":"false")
#define STATIC340_COUNT(field) fprintf(f,",\"" #field "\":%llu",(unsigned long long)s.field)
 STATIC340_BOOL(requested);STATIC340_BOOL(enabled);STATIC340_BOOL(cache_ready);STATIC340_BOOL(frame_failed);STATIC340_BOOL(pass_active);STATIC340_BOOL(row_active);STATIC340_BOOL(pass_done);STATIC340_BOOL(support_ready);
 STATIC340_COUNT(first_reason);STATIC340_COUNT(session);STATIC340_COUNT(frame);STATIC340_COUNT(map_epoch);STATIC340_COUNT(cache_loads);
 STATIC340_COUNT(frames);STATIC340_COUNT(target_tiles);STATIC340_COUNT(target_pixels);STATIC340_COUNT(rejected_frames);
 STATIC340_COUNT(frame_family_draws);STATIC340_COUNT(frame_target_pixels);STATIC340_COUNT(surviving_logical_pixels);STATIC340_COUNT(joint_accepted_frames);STATIC340_COUNT(joint_presents);
#undef STATIC340_BOOL
#undef STATIC340_COUNT
 fprintf(f,",\"production_enabled\":false,\"length_damage_tests\":\"SKIPPED_UNVERIFIED\"}\n");
 bool bad=ferror(f);int c=fclose(f);if(bad||c||rename("building313-family-static340.json.tmp","building313-family-static340.json"))fprintf(stderr,"B313_FAMILY_STATIC340_REPORT_FAILED\n");
}
static void fg_cliff_report(void)
{
 if(!fl.frames&&!fl.first_reason)return;
 FILE *f=fopen("building313-family-cliff.json.tmp","w");if(!f){fprintf(stderr,"B313_FAMILY_CLIFF_REPORT_FAILED\n");return;}
 fprintf(f,"{\"schema\":1,\"frames\":%llu,\"target_tiles\":%llu,\"target_pixels\":%llu,\"rejected_frames\":%llu,\"first_reason\":%u,\"cache_ready\":%s,\"cache_loads\":%llu,\"joint_accepted_frames\":%llu,\"joint_presents\":%llu,\"by_id\":[",(unsigned long long)fl.frames,(unsigned long long)fl.target_tiles,(unsigned long long)fl.target_pixels,(unsigned long long)fl.rejected_frames,fl.first_reason,fl.cache_ready?"true":"false",(unsigned long long)fl.cache_loads,(unsigned long long)fl.joint_accepted_frames,(unsigned long long)fl.joint_presents);
 for(unsigned i=0;i<12;i++)fprintf(f,"%s{\"id\":%u,\"target_tiles\":%llu,\"target_pixels\":%llu,\"frame_target_pixels\":%llu,\"surviving_logical_pixels\":%llu}",i?",":"",fg_cliff_ids[i],(unsigned long long)fl.target_tiles_by_id[i],(unsigned long long)fl.target_pixels_by_id[i],(unsigned long long)fl.frame_target_pixels_by_id[i],(unsigned long long)fl.surviving_by_id[i]);
 fprintf(f,"],\"production_enabled\":false,\"length_damage_tests\":\"SKIPPED_UNVERIFIED\"}\n");
 bool bad=ferror(f);int c=fclose(f);if(bad||c||rename("building313-family-cliff.json.tmp","building313-family-cliff.json"))fprintf(stderr,"B313_FAMILY_CLIFF_REPORT_FAILED\n");
}
static void fg_report(void)
{
 fg_cliff_report();fg_corner_report();fg_static340_report();
 if(!fg.frames&&!fg.first_reason)return;
 FILE *f=fopen("building313-family-ground.json.tmp","w");if(!f){fprintf(stderr,"B313_FAMILY_GROUND_REPORT_FAILED\n");return;}
 fprintf(f,"{\"schema\":1,\"frames\":%llu,\"passes\":%llu,\"rows\":%llu,\"target_tiles\":%llu,\"target_pixels\":%llu,\"native_callbacks\":%llu,\"rejected_frames\":%llu,\"first_reason\":%u,\"cache_ready\":%s,\"cache_loads\":%llu,\"joint_accepted_frames\":%llu,\"joint_presents\":%llu,\"production_enabled\":false,\"length_damage_tests\":\"SKIPPED_UNVERIFIED\"}\n",(unsigned long long)fg.frames,(unsigned long long)fg.passes,(unsigned long long)fg.rows,(unsigned long long)fg.target_tiles,(unsigned long long)fg.target_pixels,(unsigned long long)fg.native_callbacks,(unsigned long long)fg.rejected_frames,fg.first_reason,fg.cache_ready?"true":"false",(unsigned long long)fg.cache_loads,(unsigned long long)fg.joint_accepted_frames,(unsigned long long)fg.joint_presents);
 bool bad=ferror(f);int c=fclose(f);if(bad||c||rename("building313-family-ground.json.tmp","building313-family-ground.json"))fprintf(stderr,"B313_FAMILY_GROUND_REPORT_FAILED\n");
}
