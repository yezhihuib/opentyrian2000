/* Private finite Pulse5/Hitflare7/ordinary SmallExplosion12 RGB sidecars.
 * Native occupied cells are authorized only by real ordered store callbacks.
 * Exact authored alpha outside those cells is a DISTINCT RGB-only receipt,
 * confined to the same authenticated12x14 payload and committed only after
 * the complete original draw. It never creates INDEX writes or hd_owner bits.
 */
#include "combat_native.inc"
static struct {bool checked,valid;char root[1024];Uint8 *rgba[24];} cb_art;
static struct {CombatBirth birth;unsigned next_ttl;int last_y;
 uint64_t head_frame,shadow_frame;} cb_life[3][200];
static uint64_t cb_serial,cb_birth_count[3],cb_normal_retirements,cb_blend_retirements,cb_shadow_cells,cb_extra_retirements,cb_clipped,cb_unwitnessed;
static struct {bool active,contributed,failed,accepted,blend_callback;unsigned reason,count,spec,pixels,used;
 CombatDraw draws[COMBAT_MAX_DRAWS];CombatWrite writes[168];} cb;
static uint8_t cb_native_owner[64000],cb_extra_cell[64000],cb_extra_owner[4096000];
static const char *cb_root(void){const char *e=getenv("COMBAT_FAMILY_ASSET_DIR");return e?e:"";}
static bool cb_requested(void)
{
#if B313_FAMILY_CANVAS_DIAGNOSTIC
 const char *e=getenv("COMBAT_FAMILY_ENABLE"),*f=getenv("BUILDING313_FAMILY_CANVAS_ENABLE");
 return e&&!strcmp(e,"1")&&f&&!strcmp(f,"1");
#else
 return false;
#endif
}
static bool cb_scope(void)
{return cb_requested()&&family_scope()&&mainLevel==6&&terrain_file=='z'&&
 !strncmp(levelName,"ASTEROID2",9)&&(levelName[9]==0||levelName[9]==' ')&&
 !play_demo&&!demo_file&&!game_probe_enabled&&!asset_debug_enabled&&!stopped_demo&&
 !constantPlay&&!constantDie&&!richMode;}
static void cb_fail(unsigned reason)
{
 if(!cb.reason)cb.reason=reason;
 cb.failed=true;cb.accepted=false;cb.active=false;cb.blend_callback=false;
 if(cb.contributed)family_fault(FC_SOURCE);
}
static void cb_tick(void)
{
 memset(&cb,0,sizeof cb);memset(cb_native_owner,0,sizeof cb_native_owner);
 memset(cb_extra_cell,0,sizeof cb_extra_cell);memset(cb_extra_owner,0,sizeof cb_extra_owner);
}
static void cb_reset(void)
{if(cb.contributed||cb.active)cb_fail(1);cb_tick();memset(cb_life,0,sizeof cb_life);}
static void cb_shutdown(void)
{cb_reset();for(unsigned i=0;i<24;i++)free(cb_art.rgba[i]);memset(&cb_art,0,sizeof cb_art);}
static int cb_spec(unsigned kind,unsigned index)
{for(unsigned i=0;i<24;i++)if(cb_specs[i].kind==kind&&cb_specs[i].index==index)return (int)i;return -1;}
static bool cb_bank(unsigned kind,Sprite2_array bank)
{
 const Sprite2_array *b=kind==1?&spriteSheet8:&explosionSpriteSheet;
 return bank.data&&bank.data==b->data&&bank.size==b->size&&
 bank.size==(kind==1?32060:17810)&&asteroid1_stamp(bank.data,bank.size)==
 (kind==1?UINT64_C(0x2b63027f74aaa21e):UINT64_C(0x7859699ad9ca3585));
}
static bool cb_palette(unsigned kind)
{return kind==1?global_pulse_palette_matches():kind==2?global_hitflare_palette_matches():global_small_explosion_palette_matches();}
static bool cb_art_current(void)
{
 if(!cb_art.checked||!cb_art.valid||strcmp(cb_art.root,cb_root()))return false;
 for(unsigned i=0;i<24;i++)if((cb.used&(1u<<i))&&(!cb_art.rgba[i]||asteroid1_stamp(cb_art.rgba[i],43008)!=cb_specs[i].payload))return false;
 return true;
}
static bool cb_load(void)
{
 if(cb_art.checked)return cb_art_current();
 cb_art.checked=true;
 if(!cb_root()[0]||strlen(cb_root())>=sizeof cb_art.root)return false;
 strcpy(cb_art.root,cb_root());bool all=true;
 for(unsigned i=0;i<24&&all;i++){
  char path[1200];Uint8 header[28],extra;REAR_STAT st;
  int n=snprintf(path,sizeof path,"%s/%s",cb_art.root,cb_specs[i].file);
  if(n<0||(size_t)n>=sizeof path){all=false;break;}
  int fd=REAR_OPEN(path);if(fd<0){all=false;break;}
  bool good=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==43036&&REAR_READ(fd,header,28)==28&&!memcmp(header,"HDR1",4);
  uint32_t values[6]={0},want[6]={cb_specs[i].identity,8,12,14,i==1?UINT32_MAX:0,0};
  if(good){for(unsigned k=0;k<6;k++)for(unsigned j=0;j<4;j++)values[k]|=(uint32_t)header[4+k*4+j]<<(8*j);
   for(unsigned k=0;k<6;k++)if(values[k]!=want[k])good=false;}
  if(good){cb_art.rgba[i]=malloc(43008);good=cb_art.rgba[i]!=NULL;}
  if(good)good=REAR_READ(fd,cb_art.rgba[i],43008)==43008&&REAR_READ(fd,&extra,1)==0&&asteroid1_stamp(cb_art.rgba[i],43008)==cb_specs[i].payload;
  if(REAR_CLOSE(fd))good=false;
  all=good;
 }
 if(!all)for(unsigned i=0;i<24;i++){free(cb_art.rgba[i]);cb_art.rgba[i]=NULL;}
 cb_art.valid=all;return all;
}
/* Called after, and only after, the original exact semantic initializer. */
static void cb_birth(unsigned kind,unsigned slot)
{
 if(kind<1||kind>3||slot>=200||(kind==1&&slot>=MAX_PWEAPON))return;
 memset(&cb_life[kind-1][slot],0,sizeof cb_life[0][0]);
 if(!cb_scope()||cb_serial==UINT64_MAX)return;
 CombatBirth b={.kind=kind,.slot=slot,.frame=fc_frame};
 if(kind==1){
  if(!global_pulse_slots[slot].role||global_pulse_slots[slot].witnessed!=global_pulse_slots[slot].generation)return;
  b.generation=global_pulse_slots[slot].generation;b.record=global_pulse_slots[slot].record;
  b.phase=global_pulse_slots[slot].phase;b.x=playerShotData[slot].shotX;b.y=playerShotData[slot].shotY;
 }else{
  const Explosion *e=explosions+slot;
  bool role=kind==2?global_hitflare_slots[slot].role:global_small_explosion_slots[slot].role;
  if(!role)return;
  b.generation=kind==2?global_hitflare_slots[slot].generation:global_small_explosion_slots[slot].generation;
  b.role=kind==2?global_hitflare_birth.role:1;b.record=kind==2?0:1;
  b.initial_ttl=e->ttl;b.x=e->x;b.y=e->y;b.delta_y=e->deltaY;
 }
 b.serial=++cb_serial;b.witnessed=true;cb_life[kind-1][slot].birth=b;
 cb_life[kind-1][slot].next_ttl=b.initial_ttl;cb_life[kind-1][slot].last_y=b.y;
 cb_life[kind-1][slot].head_frame=cb_life[kind-1][slot].shadow_frame=UINT64_MAX;
 ++cb_birth_count[kind-1];
}
static bool cb_birth_current(const CombatDraw *d)
{
 if(d->kind<1||d->kind>3||d->slot>=200)return false;
 const CombatBirth *b=&cb_life[d->kind-1][d->slot].birth;
 if(!b->witnessed||b->serial!=d->birth_serial||b->generation!=d->generation)return false;
 if(d->kind==1)return d->slot<MAX_PWEAPON&&global_pulse_slots[d->slot].role&&
  global_pulse_slots[d->slot].generation==d->generation&&global_pulse_slots[d->slot].witnessed==d->generation&&
  global_pulse_slots[d->slot].record==d->record&&global_pulse_slots[d->slot].phase==b->phase&&
  global_pulse_table(d->record)&&global_front_record_stamp(weapons+d->record)==global_pulse_slots[d->slot].record_stamp;
 if(d->kind==2)return global_hitflare_slots[d->slot].role&&global_hitflare_slots[d->slot].generation==d->generation&&global_hitflare_slots[d->slot].witnessed_generation==d->generation;
 return global_small_explosion_slots[d->slot].role&&global_small_explosion_slots[d->slot].generation==d->generation&&global_small_explosion_slots[d->slot].witnessed_generation==d->generation;
}
static bool cb_effect_current(const CombatDraw *d,bool after_native_return)
{
 if(d->kind==1)return true;
 if(d->slot>=MAX_EXPLOSIONS)return false;
 const Explosion *e=explosions+d->slot;const CombatBirth *b=&cb_life[d->kind-1][d->slot].birth;
 return d->ttl>=1&&e->ttl==d->ttl-(after_native_return?1u:0u)&&e->sprite+1u==d->index&&
  e->x==d->x&&e->y==d->y&&!e->fixedPosition&&!e->followPlayer&&e->deltaY==b->delta_y;
}
static bool cb_finish(void)
{
 if(!cb.contributed)return !cb.failed;
 if(cb.failed||cb.active||!cb_scope()||!cb_art_current()||!family_geometry(true)||memcmp(fc_palette,rgb_palette,sizeof fc_palette))return false;
 for(unsigned j=0;j<cb.count;j++){
  const CombatDraw *d=cb.draws+j;int i=cb_spec(d->kind,d->index);
  if(i<0||d->frame!=fc_frame||!d->complete||d->callbacks!=cb_specs[i].count||
   d->core_stores!=cb_specs[i].count*64||d->extra_stores!=cb_specs[i].extra||!cb_birth_current(d)||!cb_effect_current(d,true))return false;
  Sprite2_array bank=d->kind==1?spriteSheet8:explosionSpriteSheet;
  if((uintptr_t)bank.data!=d->bank_data||bank.size!=d->bank_bytes||!cb_bank(d->kind,bank)||!cb_palette(d->kind))return false;
 }
 return true;
}
static bool cb_guard(void)
{bool good=cb_finish();if(!good&&cb.contributed)cb_fail(2);return good;}
static int cb_draw(unsigned kind,SDL_Surface *surface,int x,int y,Sprite2_array bank,unsigned index,int style,unsigned slot,unsigned raw)
{
 if(!cb_requested()||kind<1||kind>3||slot>=200||(kind==1&&slot>=MAX_PWEAPON))return -1;
 bool role=kind==1?global_pulse_slots[slot].role:kind==2?global_hitflare_slots[slot].role:global_small_explosion_slots[slot].role;
 if(!role)return -1;
 const CombatBirth *b=&cb_life[kind-1][slot].birth;
 if(!b->witnessed){++cb_unwitnessed;return -1;}
 int i=cb_spec(kind,index);bool shadow=style==MIRROR_SHADOW;
 CombatDraw d={.frame=fc_frame,.birth_serial=b->serial,.generation=b->generation,.kind=kind,.slot=slot,.index=index,
 .style=(unsigned)style,.x=x,.y=y,.record=b->record,.phase=b->phase,.role=b->role,.bank_data=(uintptr_t)bank.data,.bank_bytes=(unsigned)bank.size,
 .bank_stamp=kind==1?UINT64_C(0x2b63027f74aaa21e):UINT64_C(0x7859699ad9ca3585)};
 bool witness=i>=0&&cb_birth_current(&d);
 if(kind==1){
  const PlayerShotDataType *s=playerShotData+slot,*born=&global_pulse_slots[slot].born;
  uint64_t seen=shadow?cb_life[0][slot].shadow_frame:cb_life[0][slot].head_frame;
  witness=witness&&(style==MIRROR_NORMAL||shadow)&&raw==index&&s->shotGr==born->shotGr&&
   s->shotAniMax==born->shotAniMax&&s->shotAniMax&&raw>=s->shotGr&&raw<s->shotGr+s->shotAniMax&&
   s->shotAni==(raw-s->shotGr+1)%s->shotAniMax&&s->playerNumber==born->playerNumber&&
   !s->shotComplicated&&!s->aimAtEnemy&&!s->chainReaction&&s->shotTrail==born->shotTrail&&s->shotDmg==born->shotDmg&&
   s->shotBlastFilter==born->shotBlastFilter&&s->shotXC==born->shotXC&&s->shotYC==born->shotYC&&
   x==s->shotX+1&&y==s->shotY+(shadow?(int)shadowYDist:0)&&seen!=fc_frame&&
   (!shadow||(background2&&s->shotXM<100&&y<190));
  if(shadow)cb_life[0][slot].shadow_frame=fc_frame;else cb_life[0][slot].head_frame=fc_frame;
 }else{
  const Explosion *e=explosions+slot;unsigned ttl=e->ttl,total=kind==2?7:12;
  int moved=(JE_integer)((JE_integer)(cb_life[kind-1][slot].last_y+explodeMove)+b->delta_y);
  d.ttl=ttl;d.phase=total-ttl;
  witness=witness&&(style==MIRROR_NORMAL||style==MIRROR_BLEND)&&ttl>=1&&ttl<=total&&
   ttl==cb_life[kind-1][slot].next_ttl&&cb_life[kind-1][slot].head_frame!=fc_frame&&
   index==(kind==2?146:122)+total-ttl&&e->sprite+1u==index&&e->x==x&&e->x==b->x&&e->y==y&&e->y==moved&&
   !e->fixedPosition&&!e->followPlayer&&e->deltaY==b->delta_y;
  cb_life[kind-1][slot].head_frame=fc_frame;
  if(witness){cb_life[kind-1][slot].last_y=e->y;--cb_life[kind-1][slot].next_ttl;}
 }
 /* Observe the authentic native phase before RGB admission checks. A frame
  * already rejected by any family still executes native effect progression. */
 if(cb.contributed&&!cb_guard())return 0;
 if(!witness){
  /* An unrelated unsupported slot has no RGB dependency to revoke. Keep
   * strict failure for this frame's already-contributing slot, including a
   * completed draw whose visible ownership has since been retired. */
  for(unsigned j=0;j<cb.count;j++)if(cb.draws[j].kind==kind&&cb.draws[j].slot==slot){cb_fail(3);break;}
  return 0;
 }
 if(!fc.frame_active||fc.frame_failed||!cb_scope()||surface!=fc_source||surface!=VGAScreen||!family_geometry(false)||!cb_bank(kind,bank)||!cb_palette(kind)){if(cb.contributed)cb_fail(4);return 0;}
 /* Unknown clipping stays native: neither native nor authored rectangles expand. */
 if(x<24||x>276||y<0||y>170){++cb_clipped;return 0;}
 if(cb.active||cb.count>=COMBAT_MAX_DRAWS||fc_native_call||suppress){cb_fail(5);family_fault(FC_ORDER);return 0;}
 if(!b313_family_writer_draw_ready(fc_frame)||memcmp(fc_palette,rgb_palette,sizeof fc_palette)){cb_fail(5);return 0;}
 cb.used|=1u<<(unsigned)i;
 if(!cb_load()||!family_prepare_canvas()){cb_fail(4);return 0;}
 cb.spec=(unsigned)i;cb.pixels=0;cb.blend_callback=false;cb.draws[cb.count]=d;cb.active=true;return 1;
}
static bool cb_retire(unsigned off,int style)
{
 if(off>=64000)return false;
 bool native=cb_native_owner[off]!=0;
 if(style!=MIRROR_SHADOW){
  if(native){if(style==MIRROR_BLEND)++cb_blend_retirements;else ++cb_normal_retirements;cb_native_owner[off]=0;}
  if(cb_extra_cell[off]){unsigned x=off%320,y=off/320;
   for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){size_t n=(y*8+sy)*2560+x*8+sx;
    cb_extra_retirements+=cb_extra_owner[n]!=0;cb_extra_owner[n]=0;}
   cb_extra_cell[off]=0;
  }
 }else if(native||cb_extra_cell[off])++cb_shadow_cells;
 return native; /* Extra support NEVER exempts a foreign hd_owner blend. */
}
static bool cb_extra(size_t n){return n<4096000&&cb_extra_owner[n]!=0;}
static void cb_store(CombatDraw *d,unsigned ax,unsigned ay,bool extra)
{
 size_t n=((unsigned)d->y*8+ay)*2560+(unsigned)d->x*8+ax;
 Uint32 *dst=(Uint32 *)canvas->pixels+n;const Uint8 *a=cb_art.rgba[cb.spec]+(ay*96+ax)*4;
 if(d->style==MIRROR_SHADOW){
  unsigned off=(d->y+(int)(ay/8))*320+d->x+ax/8;
  Uint8 v=expected[off];
  /* Core callback already wrote the native shadow. Hole pixels did not. */
  Uint32 dark=hd_owner[n]||cb_extra_owner[n]||fr462_extra(n)||es_extra(n)||la_extra(n)||ts_extra(n)||ln_extra(n)||tp_extra(n)||lpf_extra(n)?darken_rgba(*dst,255):palette_rgb(extra?(Uint8)((v&240)|((v&15)/2)):v);
  Uint8 c[4]={(Uint8)(dark>>16),(Uint8)(dark>>8),(Uint8)dark,255};*dst=blend_rgba(*dst,c,a[3]);
 }
 else *dst=blend_rgba(*dst,a,d->style==MIRROR_BLEND?(a[3]+1)/2:a[3]);
 if(extra){cb_extra_owner[n]=(uint8_t)d->kind;cb_extra_cell[(d->y+(int)(ay/8))*320+d->x+ax/8]=1;++d->extra_stores;}
 else {hd_owner[n]=1;cloud_owner[n]=0;green_first[n]=0;green_under_owner[n]=0;++d->core_stores;}
 OHS_SURVIVAL_WRITE(canvas,dst,extra?COMBAT_EXTRA_STORE_TAG:COMBAT_NATIVE_STORE_TAG);
}
static bool cb_pixel(unsigned x,unsigned y,int style,Uint8 before)
{
 if(!cb.active)return false;
 CombatDraw *d=cb.draws+cb.count;const CombatSpec *s=cb_specs+cb.spec;
 if(cb.pixels>=s->count){cb_fail(6);family_fault(FC_ORDER);return true;}
 const CombatWrite *w=s->writes+cb.pixels;
 Uint8 after=style==MIRROR_NORMAL?w->index:style==MIRROR_BLEND?(Uint8)((w->index&240)|(((w->index&15)+(before&15))/2)):(Uint8)((before&240)|((before&15)/2));
 if((unsigned)style!=d->style||x!=(unsigned)d->x+w->x||y!=(unsigned)d->y+w->y||
  (style==MIRROR_BLEND&&!cb.blend_callback)||expected[y*320+x]!=after||((Uint8 *)fc_source_pixels)[y*320+x]!=after){cb_fail(6);family_fault(FC_ORDER);return true;}
 cb.blend_callback=false;
 for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++)cb_store(d,w->x*8+sx,w->y*8+sy,false);
 unsigned off=y*320+x;
 if(style!=MIRROR_SHADOW){lamp272_clear(off);triple275_clear(off);private_ember269_clear(off);gray325_clear(off);longface573_clear(off);}
 cb_native_owner[off]=(uint8_t)d->kind;selected[off]=1;cb.writes[cb.pixels]=*w;
 ++cb.pixels;d->callbacks=cb.pixels;cb.contributed=true;return true;
}
static bool cb_blend(SDL_Surface *surface,Uint8 *address,Uint8 source,Sprite2_array bank,unsigned index,int x,int y)
{
 if(!cb.active)return false;
 const CombatDraw *d=cb.draws+cb.count;const CombatSpec *s=cb_specs+cb.spec;
 if(cb.pixels>=s->count||cb.blend_callback||d->style!=MIRROR_BLEND||surface!=fc_source||
  (uintptr_t)bank.data!=d->bank_data||bank.size!=d->bank_bytes||index!=d->index||x!=d->x||y!=d->y){cb_fail(6);family_fault(FC_ORDER);}
 else{
  const CombatWrite *w=s->writes+cb.pixels;unsigned off=(d->y+w->y)*320+d->x+w->x;
  if(address!=(Uint8 *)fc_source_pixels+off||source!=w->index||*address!=(Uint8)((source&240)|(((source&15)+(expected[off]&15))/2))){cb_fail(6);family_fault(FC_ORDER);}
  else cb.blend_callback=true;
 }
 family_pixel(surface,address,MIRROR_BLEND);
 if(cb.blend_callback){cb_fail(6);family_fault(FC_ORDER);}
 return true;
}
static void cb_end(void)
{
 if(!cb.active)return;
 CombatDraw *d=cb.draws+cb.count;const CombatSpec *s=cb_specs+cb.spec;
 if(fc.frame_failed||cb.pixels!=s->count||!cb_birth_current(d)||!cb_effect_current(d,false)||!cb_scope()||!cb_art_current()||!cb_bank(d->kind,d->kind==1?spriteSheet8:explosionSpriteSheet)||
  !b313_family_writer_draw_ready(fc_frame)||!family_geometry(true)||memcmp(fc_palette,rgb_palette,sizeof fc_palette)){
  cb_fail(7);family_fault(FC_ORDER);return;
 }
 /* Sparse exact authored support only, after complete authenticated native draw.
  * Zero-alpha holes do not write and cannot acquire any ownership. */
 for(unsigned ay=0;ay<112;ay++)for(unsigned ax=0;ax<96;ax++)
  if(!s->mask[(ay/8)*12+ax/8]&&cb_art.rgba[cb.spec][(ay*96+ax)*4+3])cb_store(d,ax,ay,true);
 if(d->extra_stores!=s->extra){cb_fail(7);family_fault(FC_ORDER);return;}
 d->complete=true;++cb.count;cb.active=false;
}
static void cb_accept(void){cb.accepted=cb.contributed&&fc.ready&&!fc.frame_failed&&cb_finish();}
CombatFamilyStatus render_mirror_combat_family_status(void)
{
 CombatFamilyStatus s={.requested=cb_requested(),.loaded=cb_art.valid,.active=cb.active,.contributed=cb.contributed,.failed=cb.failed||fc.frame_failed,
 .accepted=cb.accepted,.first_reason=cb.reason,.draw_count=cb.count,.material_mask=cb.used,.frame=fc_frame,
 .normal_retirements=cb_normal_retirements,.blend_retirements=cb_blend_retirements,.shadow_cells=cb_shadow_cells,
 .extra_retirements=cb_extra_retirements,.clipped=cb_clipped,.unwitnessed=cb_unwitnessed};
 memcpy(s.births,cb_birth_count,sizeof s.births);if(cb.active)s.last=cb.draws[cb.count];else if(cb.count)s.last=cb.draws[cb.count-1];
 for(unsigned i=0;i<64000;i++)s.native_cells+=cb_native_owner[i]!=0;
 for(unsigned i=0;i<4096000;i++)s.extra_pixels+=cb_extra_owner[i]!=0;
 return s;
}
unsigned render_mirror_combat_draws(CombatDraw *out,size_t count)
{if(!out||count<cb.count)return 0;memcpy(out,cb.draws,cb.count*sizeof *out);return cb.count;}
bool render_mirror_combat_birth(unsigned kind,unsigned slot,CombatBirth *out)
{if(!out||kind<1||kind>3||slot>=200||(kind==1&&slot>=MAX_PWEAPON))return false;*out=cb_life[kind-1][slot].birth;return out->witnessed;}
bool render_mirror_combat_pre_draw(CombatDraw *d,uint32_t *argb,size_t count,uint8_t *native,size_t bytes)
{
 if(!d||!argb||count!=10752||!native||bytes!=168||!cb.active||cb.pixels||fc.frame_failed||!family_geometry(true))return false;
 *d=cb.draws[cb.count];for(unsigned y=0;y<112;y++)memcpy(argb+y*96,(const Uint32 *)canvas->pixels+(d->y*8+y)*2560+d->x*8,96*sizeof *argb);
 for(unsigned y=0;y<14;y++)memcpy(native+y*12,(const Uint8 *)fc_source_pixels+(d->y+y)*320+d->x,12);
 return true;
}
unsigned render_mirror_combat_callbacks(CombatWrite *out,size_t count)
{if(!out||count<cb.pixels)return 0;memcpy(out,cb.writes,cb.pixels*sizeof *out);return cb.pixels;}
bool render_mirror_combat_support(uint8_t *native,size_t bytes,uint8_t *extra,size_t pixels)
{
 if(!native||bytes!=64000||!extra||pixels!=4096000||!cb.accepted||fc.frame_active||fc.frame_failed||!cb_finish()||!b313_family_writer_peek_current(fc_frame))return false;
 memcpy(native,cb_native_owner,64000);memcpy(extra,cb_extra_owner,4096000);return true;
}
