/* Private default-OFF native-origin shells145/146/147, orb112/113, late91
* and the independently gated exact turret273 weapon144/projectile304.
* Own allocation generations and lifecycle receipts, independent of emitter
* death/reuse and all legacy global projectile routes. No native state writes.
*/
#include <math.h>
#include "enemy_shot_native.inc"
static struct {unsigned checked,valid;
 char root[4][1024];
 Uint8 *rgba[COUNTOF(es_specs)];
} es_art;
static struct {EnemyShotBirth birth;
 EnemyShotState before;
 uint64_t generation,allocated_frame,step_frame,draw_frame;
 uint64_t emitter_token;unsigned emitter_event;bool late,turret273;
 int emitter_x,emitter_y,emitter_map;
 bool pending,stepping,moved;
} es_life[60];
static uint64_t es_actor_generation[100],es_epoch,es_serial,es_allocations,es_motions,es_animations,es_retirements[4];
static uint64_t es_normal_retirements,es_blend_retirements,es_shadow_cells,es_extra_retirements,es_clipped,es_unwitnessed,es_lifetime_losses;
static struct {bool active,pending,contributed,failed,accepted;
 unsigned reason,count,spec,pixels,used,slot;
 uint64_t lease_generation,lease_frame;
 EnemyShotDraw draws[60];
 EnemyShotWrite writes[62];
} es;
static uint8_t es_native_owner[64000],es_extra_cell[64000],es_extra_owner[4096000];
static const char *es_root(unsigned root){const char *e=getenv(root==3?"TURRET273_PROJECTILE_ASSET_DIR":root==2?"ENEMY_ORDNANCE_LATE_ASSET_DIR":root?"ENEMY_ORDNANCE_NEXT_ASSET_DIR":"ENEMY_SHOT_FAMILY_ASSET_DIR");
 return e?e:"";
}
/* This switch does not imply any legacy enemy-shot or body switch. */
static bool es_turret273_requested(void)
{
#if B313_FAMILY_CANVAS_DIAGNOSTIC
 const char *e=getenv("TURRET273_COMBAT_ENABLE"),*f=getenv("BUILDING313_FAMILY_CANVAS_ENABLE");
 return e&&!strcmp(e,"1")&&f&&!strcmp(f,"1");
#else
 return false;
#endif
}
static bool es_requested(void)
{
#if B313_FAMILY_CANVAS_DIAGNOSTIC
 const char *e=getenv("ENEMY_SHOT_FAMILY_ENABLE"),*f=getenv("BUILDING313_FAMILY_CANVAS_ENABLE");
 return e&&!strcmp(e,"1")&&f&&!strcmp(f,"1");
#else
 return false;
#endif
}
static bool es_any_requested(void)
{return es_requested()||es_turret273_requested();
}
static bool es_next_requested(void)
{const char *e=getenv("ENEMY_ORDNANCE_NEXT_ENABLE");
 return es_requested()&&e&&!strcmp(e,"1");
}
static bool es_late_requested(void)
{const char *e=getenv("ENEMY_ORDNANCE_LATE_ENABLE");
 return es_requested()&&e&&!strcmp(e,"1");
}
static bool es_next_scope(void)
{return es_next_requested()&&curLoc<1960&&eventLoc<=259;
}
static bool es_scope(void)
{return es_any_requested()&&family_scope()&&mainLevel==6&&terrain_file=='z'&&
 !strncmp(levelName,"ASTEROID2",9)&&(levelName[9]==0||levelName[9]==' ')&&
 !play_demo&&!demo_file&&!game_probe_enabled&&!asset_debug_enabled&&!stopped_demo&&
 !constantPlay&&!constantDie&&!richMode;
}
static EnemyShotState es_state(unsigned slot)
{
 const EnemyShotType *s=enemyShot+slot;
 return (EnemyShotState){.x=s->sx,.y=s->sy,.xm=s->sxm,.ym=s->sym,.xc=s->sxc,.yc=s->syc,
  .tx=s->tx,.ty=s->ty,.sprite=s->sgr,.damage=s->sdmg,.duration=s->duration,.animate=s->animate,.animax=s->animax};
}
static bool es_equal(const EnemyShotState *a,const EnemyShotState *b)
{
 return a->x==b->x&&a->y==b->y&&a->xm==b->xm&&a->ym==b->ym&&a->xc==b->xc&&a->yc==b->yc&&
 a->tx==b->tx&&a->ty==b->ty&&a->sprite==b->sprite&&a->damage==b->damage&&
 a->duration==b->duration&&a->animate==b->animate&&a->animax==b->animax;
}
static uint64_t es_weapon(unsigned weapon)
{if(!es_requested())return 0;
 for(unsigned i=0;i<COUNTOF(es_weapons);i++)if((i<3||es_next_scope())&&es_weapons[i].weapon==weapon&&global_front_record_stamp(weapons+weapon)==es_weapons[i].stamp)return es_weapons[i].stamp;
 return 0;
}
static int es_spec(unsigned index)
{for(unsigned i=0;i<COUNTOF(es_specs);i++)if(((i<4&&es_requested())||(i==4&&es_next_requested())||(i==5&&es_late_requested())||(i==6&&es_turret273_requested()))&&es_specs[i].index==index)return (int)i;
 return -1;
}
static bool es_next_emitter(unsigned actor,unsigned weapon,unsigned turret)
{
 const struct JE_SingleEnemyType *e=enemy+actor;
 for(unsigned i=0;i<COUNTOF(es_next_emitters);i++){
  const unsigned r=es_next_emitters[i].record;
  if(weapon==es_next_emitters[i].weapon&&turret==es_next_emitters[i].turret&&e->enemytype==r&&
   e->enemydatofs==enemyDat+r&&asteroid1_record_stamp(r)==es_next_emitters[i].stamp&&
   enemyDat[r].tur[turret-1]==weapon)return true;
 }
 return false;
}
/* The body worker supplies actual event/allocation identity at completed native
 * shot initialization. No screen-coordinate or shared-sprite inference. The
 * token is retained privately; shot survival never depends on its parent. */
static uint64_t es_late_weapon(unsigned weapon,unsigned record,unsigned turret)
{
 if(!es_late_requested())return 0;
 for(unsigned i=0;i<COUNTOF(es_late_emitters);i++)
  if(weapon==es_late_emitters[i].weapon&&record==es_late_emitters[i].record&&turret==es_late_emitters[i].turret&&
   global_front_record_stamp(weapons+weapon)==es_late_emitters[i].weapon_stamp)return es_late_emitters[i].weapon_stamp;
 return 0;
}
static bool es_late_event(unsigned record,unsigned event)
{
 for(unsigned i=0;i<COUNTOF(es_late_emitters);i++)if(record==es_late_emitters[i].record)
  for(unsigned j=0;j<COUNTOF(es_late_emitters[i].event);j++)if(event==es_late_emitters[i].event[j])return true;
 return false;
}
static bool es_late_emitter(unsigned actor,unsigned weapon,unsigned turret,uint64_t *token,unsigned *event)
{
 if(actor>=100||!token||!event||!es_late_requested())return false;
 const struct JE_SingleEnemyType *e=enemy+actor;
 for(unsigned i=0;i<COUNTOF(es_late_emitters);i++){
  const unsigned r=es_late_emitters[i].record;
  if(weapon==es_late_emitters[i].weapon&&turret==es_late_emitters[i].turret&&e->enemytype==r&&
   e->enemydatofs==enemyDat+r&&asteroid1_record_stamp(r)==es_late_emitters[i].record_stamp&&
   enemyDat[r].tur[turret-1]==weapon&&late_actor_emitter(actor,weapon,token,event)&&*token&&es_late_event(r,*event))return true;
 }
 return false;
}
static bool es_late_colors(void)
{for(unsigned i=0;i<COUNTOF(es_late_palette);i++)if((rgb_palette[es_late_palette[i].index]&0xffffffu)!=es_late_palette[i].rgb)return false;
 return true;
}
static bool es_turret273_colors(void)
{for(unsigned i=0;i<COUNTOF(es_turret273_palette);i++)if((rgb_palette[es_turret273_palette[i].index]&0xffffffu)!=es_turret273_palette[i].rgb)return false;
 return true;
}
static bool es_bank(Sprite2_array bank)
{return bank.data&&bank.data==spriteSheet8.data&&bank.size==spriteSheet8.size&&bank.size==32060&&asteroid1_stamp(bank.data,bank.size)==UINT64_C(0x2b63027f74aaa21e);
}
static bool es_colors(void)
{/* Retain the old palette contract whenever an old route is requested or used.
  * A304-only frame has only304's own palette dependencies. */
 if(es_requested()||(es.used&63u))for(unsigned i=0;i<COUNTOF(es_palette);i++)if((rgb_palette[es_palette[i].index]&0xffffffu)!=es_palette[i].rgb)return false;
 return (!(es.used&32u)||es_late_colors())&&(!(es.used&64u)||es_turret273_colors());
}
static void es_fail(unsigned reason)
{if(!es.reason)es.reason=reason;
 es.failed=true;
 es.accepted=es.active=es.pending=false;
 if(es.contributed)family_fault(FC_SOURCE);
}
static void es_lose(unsigned slot)
{
 if(slot>=60)return;
 if(es_life[slot].birth.live)++es_lifetime_losses;
 es_life[slot].birth.live=false;
 es_life[slot].pending=es_life[slot].stepping=es_life[slot].moved=false;
 if(es.pending&&es.slot==slot)es.pending=false;
 for(unsigned j=0;j<es.count;j++)if(es.draws[j].slot==slot){es_fail(3);
  break;
 }
}
static void es_tick(void)
{memset(&es,0,sizeof es);
 memset(es_native_owner,0,sizeof es_native_owner);
 memset(es_extra_cell,0,sizeof es_extra_cell);
 memset(es_extra_owner,0,sizeof es_extra_owner);
}
static void es_reset(void)
{
 if(es.contributed||es.active||es.pending)es_fail(1);
 for(unsigned i=0;i<60;i++){
  if(es_life[i].birth.live){es_life[i].birth.live=false;
   es_life[i].birth.retirement_reason=ENEMY_SHOT_RETIRE_RESET;
   es_life[i].birth.retired_frame=fc_frame;
   ++es_retirements[3];
  }
  es_life[i].pending=es_life[i].stepping=es_life[i].moved=false;
 }
 if(es_epoch<UINT64_MAX)++es_epoch;
 es_tick();
}
static void es_shutdown(void)
{es_reset();
 for(unsigned i=0;i<COUNTOF(es_specs);i++)free(es_art.rgba[i]);
 memset(&es_art,0,sizeof es_art);
}
void render_mirror_enemy_shot_pool_begin(void){es_reset();
}
void render_mirror_enemy_shot_actor_allocated(void *p)
{
 uintptr_t a=(uintptr_t)p,b=(uintptr_t)enemy;
 if(a<b||a-b>=sizeof enemy||(a-b)%sizeof enemy[0])return;
 unsigned slot=(unsigned)((a-b)/sizeof enemy[0]);
 if(es_actor_generation[slot]<UINT64_MAX)++es_actor_generation[slot];
}
void render_mirror_enemy_shot_allocated(unsigned slot)
{
 if(slot>=60)return;
 es_lose(slot);
 es_life[slot].emitter_token=0;es_life[slot].emitter_event=0;es_life[slot].late=es_life[slot].turret273=false;
 es_life[slot].emitter_x=es_life[slot].emitter_y=es_life[slot].emitter_map=0;
 if(es_life[slot].generation<UINT64_MAX)++es_life[slot].generation;
 es_life[slot].pending=es_scope()&&enemyShotAvail[slot]==1&&es_epoch&&es_epoch<UINT64_MAX&&es_life[slot].generation<UINT64_MAX;
 es_life[slot].allocated_frame=fc_frame;
 ++es_allocations;
}
static uint64_t es_turret273_weapon(unsigned weapon)
{return es_turret273_requested()&&weapon==144&&global_front_record_stamp(weapons+144)==es_turret273_weapon_stamp?es_turret273_weapon_stamp:0;
}
static bool es_turret273_event(unsigned event)
{return event==476||event==477;
}
/* Read only after the real native allocation and complete initialization.
 * Multiposition advances only when the native pool allocation succeeds; this
 * observer neither requires a full five-shot volley nor manufactures phases. */
static void es_turret273_initialized(unsigned slot,unsigned actor,unsigned weapon,unsigned turret,unsigned phase,int x,int y,int map)
{
 uint64_t token=0,stamp=es_turret273_weapon(weapon);unsigned event=0;
 if(!stamp||turret!=1||phase>=5||enemy[actor].eshotmultipos[0]!=phase+1||
  enemy[actor].enemytype!=273||enemy[actor].enemydatofs!=enemyDat+273||
  !es_bank(spriteSheet8)||!turret273_emitter(actor,weapon,&token,&event)||!token||!es_turret273_event(event))return;
 const JE_WeaponType *w=weapons+weapon;
 EnemyShotState s=es_state(slot);
 if(w->multi!=5||w->max!=5||w->weapani||w->aim||w->tx||w->ty||
  s.x!=(JE_integer)(x+w->bx[phase]+map)||s.y!=(JE_integer)(y+w->by[phase])||
  s.xm!=w->sx[phase]||s.ym!=w->sy[phase]||s.xc!=w->accelerationx||s.yc!=w->acceleration||s.tx||s.ty||
  s.sprite!=304||s.sprite!=w->sg[phase]||s.damage!=w->attack[phase]||s.duration!=w->del[phase]||s.animate||s.animax)return;
 es_life[slot].birth=(EnemyShotBirth){.epoch=es_epoch,.serial=++es_serial,.generation=es_life[slot].generation,.emitter_generation=es_actor_generation[actor],
  .weapon_stamp=stamp,.birth_frame=fc_frame,.last_frame=fc_frame,.slot=slot,.weapon=weapon,.turret=turret,.phase=phase,
  .emitter_slot=actor,.emitter_record=273,.witnessed=true,.live=true,.born=s,.current=s};
 es_life[slot].turret273=true;es_life[slot].emitter_token=token;es_life[slot].emitter_event=event;
 es_life[slot].emitter_x=x;es_life[slot].emitter_y=y;es_life[slot].emitter_map=map;
 es_life[slot].step_frame=es_life[slot].draw_frame=UINT64_MAX;
}
/* The original initializer has finished, including optional aiming. */
void render_mirror_enemy_shot_initialized(unsigned slot,unsigned actor,unsigned weapon,unsigned turret,unsigned phase,int x,int y,int map)
{
 if(slot>=60)return;
 bool pending=es_life[slot].pending;
 es_life[slot].pending=false;
 if(!pending||!es_scope()||es_life[slot].allocated_frame!=fc_frame||actor>=100||turret<1||turret>3||enemyShotAvail[slot]||
 !es_actor_generation[actor]||es_actor_generation[actor]==UINT64_MAX||enemyAvail[actor]==1||enemy[actor].tur[turret-1]!=weapon||
 es_serial==UINT64_MAX)return;
 if(weapon==144){es_turret273_initialized(slot,actor,weapon,turret,phase,x,y,map);return;}
 if(phase||enemy[actor].eshotmultipos[turret-1]!=1)return;
 bool late=weapon==59||weapon==24;
 uint64_t token=0;unsigned event=0;
 uint64_t stamp=late?es_late_weapon(weapon,enemy[actor].enemytype,turret):es_weapon(weapon);
 if(!stamp||!es_bank(spriteSheet8))return;
 if(late){if(!es_late_emitter(actor,weapon,turret,&token,&event))return;}
 else if(weapon!=2&&weapon!=3&&weapon!=116&&!es_next_emitter(actor,weapon,turret))return;
 const JE_WeaponType *w=weapons+weapon;
 EnemyShotState s=es_state(slot);
 int xm=turret==1?w->sx[0]:turret==2?w->sy[0]:-w->sy[0];
 int ym=turret==1?w->sy[0]:-w->sx[0];
 if(w->aim){
  unsigned aim=w->aim;
  if(difficultyLevel>DIFFICULTY_NORMAL)aim+=difficultyLevel-2;
  JE_integer ax=(player[0].x+25)-x-map-4,ay=player[0].y-y;
  if(!ax)ax=1;
  if(!ay)ay=1;
  int mag=MAX(abs(ax),abs(ay));
  xm=roundf((float)ax/mag*aim);
  ym=roundf((float)ay/mag*aim);
 }
 if(w->multi!=1||w->max!=1||w->tx||w->ty||w->acceleration||w->accelerationx||
 s.x!=(JE_integer)(x+w->bx[0]+map)||s.y!=(JE_integer)(y+w->by[0])||s.xm!=xm||s.ym!=ym||s.xc||s.yc||s.tx||s.ty||
 s.sprite!=w->sg[0]||s.damage!=w->attack[0]||s.duration!=w->del[0]||s.animate||s.animax!=w->weapani||
 !((weapon==2&&s.sprite==146&&!s.animax)||(weapon==3&&s.sprite==147&&!s.animax)||(weapon==116&&s.sprite==112&&s.animax==2)||
  (weapon==4&&s.sprite==145&&!s.animax)||((weapon==145||weapon==146)&&s.sprite==112&&s.animax==2)||
  (late&&weapon==59&&s.sprite==112&&s.animax==2)||(late&&weapon==24&&s.sprite==91&&!s.animax)))return;
 es_life[slot].birth=(EnemyShotBirth){.epoch=es_epoch,.serial=++es_serial,.generation=es_life[slot].generation,.emitter_generation=es_actor_generation[actor],
  .weapon_stamp=stamp,.birth_frame=fc_frame,.last_frame=fc_frame,.slot=slot,.weapon=weapon,.turret=turret,.phase=phase,
  .emitter_slot=actor,.emitter_record=enemy[actor].enemytype,.witnessed=true,.live=true,.born=s,.current=s};
 es_life[slot].late=late;es_life[slot].emitter_token=token;es_life[slot].emitter_event=event;
 es_life[slot].step_frame=es_life[slot].draw_frame=UINT64_MAX;
}
static bool es_live(unsigned slot)
{
 if(slot>=60)return false;
 const EnemyShotBirth *b=&es_life[slot].birth;
 return b->witnessed&&b->live&&b->epoch==es_epoch&&b->generation==es_life[slot].generation&&
 !enemyShotAvail[slot]&&(es_life[slot].turret273?
  (es_life[slot].emitter_token&&es_turret273_event(es_life[slot].emitter_event)&&b->emitter_record==273&&b->turret==1&&b->phase<5&&
   b->weapon_stamp==es_turret273_weapon(b->weapon)):
  es_life[slot].late?
  (es_life[slot].emitter_token&&es_late_event(b->emitter_record,es_life[slot].emitter_event)&&b->weapon_stamp==es_late_weapon(b->weapon,b->emitter_record,b->turret)):
  b->weapon_stamp==es_weapon(b->weapon));
}
/* No emitter reads after birth: original acceleration precedes movement.
 * Other admitted records retain their existing zero-acceleration path. */
static EnemyShotState es_motion(unsigned slot)
{
 EnemyShotState want=es_life[slot].before;
 if(es_life[slot].turret273)want.xm=(JE_integer)(want.xm+want.xc);
 want.x=(JE_integer)(want.x+want.xm);
 if(es_life[slot].turret273)want.ym=(JE_integer)(want.ym+want.yc);
 want.y=(JE_integer)(want.y+want.ym);
 return want;
}
void render_mirror_enemy_shot_before_motion(unsigned slot)
{
 if(slot>=60||!es_life[slot].birth.live)return;
 EnemyShotState s=es_state(slot);
 if(!es_scope()||!es_live(slot)||es_life[slot].stepping||es_life[slot].step_frame==fc_frame||
 (fc_frame!=es_life[slot].birth.last_frame+1&&!(es_life[slot].birth.observations==0&&fc_frame==es_life[slot].birth.birth_frame))||!es_equal(&s,&es_life[slot].birth.current)){es_lose(slot);
  return;
 }
 es_life[slot].before=s;
 es_life[slot].stepping=true;
 es_life[slot].moved=false;
 es_life[slot].step_frame=fc_frame;
}
void render_mirror_enemy_shot_after_motion(unsigned slot)
{
 if(slot>=60||!es_life[slot].birth.live)return;
 EnemyShotState want=es_motion(slot),s=es_state(slot);
 if(!es_live(slot)||!es_life[slot].stepping||es_life[slot].moved||es_life[slot].step_frame!=fc_frame||!es_equal(&s,&want)){es_lose(slot);
  return;
 }
 es_life[slot].moved=true;
 ++es_motions;
}
void render_mirror_enemy_shot_retired(unsigned slot,unsigned kind,unsigned player_number)
{
 if(slot>=60||!es_life[slot].birth.live)return;
 EnemyShotState want=es_motion(slot),s=es_state(slot);
 want.duration=(JE_byte)(want.duration-1);
 bool expired=es_life[slot].before.duration==0;
 bool boundary=s.y>190||s.y<=-14||s.x>275||s.x<=0;
 bool reason=kind==ENEMY_SHOT_RETIRE_BOUNDARY?(expired||boundary):kind==ENEMY_SHOT_RETIRE_COLLISION&&!expired&&!boundary&&player_number<2;
 if(kind==ENEMY_SHOT_RETIRE_COLLISION&&reason){const Player *p=player+player_number;
  reason=p->is_alive&&s.x>p->x-(signed)p->shot_hit_area_x&&s.x<p->x+(signed)p->shot_hit_area_x&&s.y>p->y-(signed)p->shot_hit_area_y&&s.y<p->y+(signed)p->shot_hit_area_y;
 }
 if(!es_live(slot)||!es_life[slot].stepping||!es_life[slot].moved||es_life[slot].step_frame!=fc_frame||!reason||!es_equal(&s,&want)){es_lose(slot);
  return;
 }
 if(expired)kind=ENEMY_SHOT_RETIRE_DURATION;
 EnemyShotBirth *b=&es_life[slot].birth;
 b->live=false;
 b->current=b->retired=s;
 b->last_frame=b->retired_frame=fc_frame;
 b->retirement_reason=kind;
 b->player=player_number;
 es_life[slot].stepping=es_life[slot].moved=false;
 ++es_retirements[kind-1];
}
void render_mirror_enemy_shot_after_animation(unsigned slot)
{
 if(slot>=60||!es_life[slot].birth.live)return;
 EnemyShotState want=es_motion(slot),s=es_state(slot);
 want.duration=(JE_byte)(want.duration-1);
 if(want.animax)want.animate=(want.animate+1)%want.animax;
 if(!es_live(slot)||!es_life[slot].stepping||!es_life[slot].moved||es_life[slot].step_frame!=fc_frame||!es_life[slot].before.duration||
 s.y>190||s.y<=-14||s.x>275||s.x<=0||!es_equal(&s,&want)){es_lose(slot);
  return;
 }
 es_life[slot].birth.current=s;
 es_life[slot].birth.last_frame=fc_frame;
 ++es_life[slot].birth.observations;
 es_life[slot].stepping=es_life[slot].moved=false;
 ++es_animations;
}
void render_mirror_enemy_shot_before_draw(unsigned slot)
{
 if(es.pending||es.active){es_fail(5);
  return;
 }
 if(slot>=60||!es_live(slot))return;
 EnemyShotState s=es_state(slot);
 if(!es_scope()||es_life[slot].stepping||es_life[slot].step_frame!=fc_frame||es_life[slot].draw_frame==fc_frame||!es_equal(&s,&es_life[slot].birth.current)){es_lose(slot);
  return;
 }
 es.pending=true;
 es.slot=slot;
 es.lease_generation=es_life[slot].generation;
 es.lease_frame=fc_frame;
}
void render_mirror_enemy_shot_after_draw(void)
{if(es.pending||es.active)es_fail(5);
 es.pending=false;
}
static bool es_art_current(void)
{
 if(!es_art.checked||((es_requested()||(es.used&63u))&&(es_art.checked&3u)&&strcmp(es_art.root[0],es_root(0))))return false;
 if((es.used&16u)&&(!es_next_requested()||strcmp(es_art.root[1],es_root(1))))return false;
 if((es.used&32u)&&(!es_late_requested()||strcmp(es_art.root[2],es_root(2))))return false;
 if((es.used&64u)&&(!es_turret273_requested()||strcmp(es_art.root[3],es_root(3))))return false;
 for(unsigned i=0;i<COUNTOF(es_specs);i++)if((es.used&(1u<<i))&&(!(es_art.valid&(1u<<es_spec_group[i]))||!es_art.rgba[i]||asteroid1_stamp(es_art.rgba[i],43008)!=es_specs[i].payload))return false;
 return true;
}
static bool es_load(unsigned selected_spec)
{
 if(selected_spec>=COUNTOF(es_specs)||(selected_spec<4&&!es_requested())||(selected_spec==4&&!es_next_requested())||
  (selected_spec==5&&!es_late_requested())||(selected_spec==6&&!es_turret273_requested()))return false;
 unsigned group=es_spec_group[selected_spec];
 if(group>=COUNTOF(es_groups))return false;
 unsigned bit=1u<<group,root=es_groups[group].root;
 unsigned first=es_groups[group].first,end=first+es_groups[group].count;
 if(root>=COUNTOF(es_art.root)||end>COUNTOF(es_specs))return false;
 if(es_art.checked&bit)return (es_art.valid&bit)&&es_art_current();
 unsigned root_groups=0;
 for(unsigned i=0;i<COUNTOF(es_groups);i++)if(es_groups[i].root==root)root_groups|=1u<<i;
 const char *path_root=es_root(root);
 if(!path_root[0]||strlen(path_root)>=sizeof es_art.root[root]||((es_art.checked&root_groups)&&strcmp(es_art.root[root],path_root)))return false;
 if(!(es_art.checked&root_groups))strcpy(es_art.root[root],path_root);
 es_art.checked|=bit;
 bool all=true;
 for(unsigned i=first;i<end&&all;i++){
  char path[1200];
  Uint8 header[28],extra;
  REAR_STAT st;
  int n=snprintf(path,sizeof path,"%s/%s",es_art.root[root],es_specs[i].file);
  if(n<0||(size_t)n>=sizeof path){all=false;
   break;
  }int fd=REAR_OPEN(path);
  if(fd<0){all=false;
   break;
  }
  bool good=!REAR_FSTAT(fd,&st)&&REAR_REGULAR(st.st_mode)&&st.st_size==43036&&REAR_READ(fd,header,28)==28&&!memcmp(header,"HDR1",4);
  uint32_t values[6]={0},want[6]={es_specs[i].identity,8,12,14,0,0};
  if(good){for(unsigned k=0;k<6;k++)for(unsigned j=0;j<4;j++)values[k]|=(uint32_t)header[4+k*4+j]<<(8*j);
   for(unsigned k=0;k<6;k++)if(values[k]!=want[k])good=false;
  }
  if(good){es_art.rgba[i]=malloc(43008);
   good=es_art.rgba[i]!=NULL;
  }
  if(good)good=REAR_READ(fd,es_art.rgba[i],43008)==43008&&REAR_READ(fd,&extra,1)==0&&asteroid1_stamp(es_art.rgba[i],43008)==es_specs[i].payload;
  if(REAR_CLOSE(fd))good=false;
  all=good;
 }
 if(!all)for(unsigned i=first;i<end;i++){free(es_art.rgba[i]);
  es_art.rgba[i]=NULL;
 }
 if(all)es_art.valid|=bit;
 return all;
}
static bool es_draw_current(const EnemyShotDraw *d)
{
 if(d->slot>=60||!es_live(d->slot))return false;
 const EnemyShotBirth *b=&es_life[d->slot].birth;
 EnemyShotState s=es_state(d->slot);
 return d->epoch==b->epoch&&d->serial==b->serial&&d->generation==b->generation&&b->last_frame==fc_frame&&
 d->index==s.sprite+s.animate&&d->x==s.x&&d->y==s.y&&es_equal(&s,&d->state)&&es_equal(&s,&b->current);
}
static bool es_finish(void)
{
 if(!es.contributed)return !es.failed&&!es.active&&!es.pending;
 if(es.failed||es.active||es.pending||!es_scope()||!es_art_current()||!es_colors()||!family_geometry(true)||memcmp(fc_palette,rgb_palette,sizeof fc_palette))return false;
 for(unsigned j=0;j<es.count;j++){
  const EnemyShotDraw *d=es.draws+j;
  int i=es_spec(d->index);
  if(i<0||d->frame!=fc_frame||!d->complete||d->callbacks!=es_specs[i].count||d->core_stores!=es_specs[i].count*64||d->extra_stores!=es_specs[i].extra||
  !es_draw_current(d)||(uintptr_t)spriteSheet8.data!=d->bank_data||spriteSheet8.size!=d->bank_bytes||!es_bank(spriteSheet8))return false;
 }
 return true;
}
static bool es_guard(void){bool good=es_finish();
 if(!good&&es.contributed)es_fail(2);
 return good;
}
static bool es_draw(SDL_Surface *surface,int x,int y,Sprite2_array bank,unsigned index)
{
 bool pending=es.pending;
 unsigned slot=es.slot;
 uint64_t generation=es.lease_generation,frame=es.lease_frame;
 es.pending=false;
 if(!es_any_requested())return false;
 if(!pending||slot>=60||!es_live(slot)){if(es_spec(index)>=0)++es_unwitnessed;
  return false;
 }
 EnemyShotBirth *b=&es_life[slot].birth;
 int i=es_spec(index);
 EnemyShotDraw d={.frame=fc_frame,.epoch=b->epoch,.serial=b->serial,.generation=b->generation,.bank_stamp=UINT64_C(0x2b63027f74aaa21e),
  .bank_data=(uintptr_t)bank.data,.slot=slot,.index=index,.bank_bytes=(unsigned)bank.size,.x=x,.y=y,.state=es_state(slot)};
 bool witness=i>=0&&frame==fc_frame&&generation==b->generation&&es_draw_current(&d)&&es_life[slot].draw_frame!=fc_frame;
 es_life[slot].draw_frame=fc_frame;
 ++b->draws;
 if(es.contributed&&!es_guard())return false;
 if(!witness){es_lose(slot);
  return false;
 }
 if(!fc.frame_active||fc.frame_failed||!es_scope()||surface!=fc_source||surface!=VGAScreen||!family_geometry(false)||!es_bank(bank)||!es_colors()||
  (i==5&&!es_late_colors())||(i==6&&!es_turret273_colors())){if(es.contributed)es_fail(4);
  return false;
 }
 if(x<24||x>276||y<0||y>170){++es_clipped;
  return false;
 }
 if(es.active||es.count>=60||fc_native_call||suppress){es_fail(5);
  family_fault(FC_ORDER);
  return false;
 }
 if(!b313_family_writer_draw_ready(fc_frame)||memcmp(fc_palette,rgb_palette,sizeof fc_palette)){es_fail(5);
  return false;
 }
 /* Each old pair and each independent singleton are atomic. An unused group may remain native.
  * A failed optional load never enters the final contributor dependency set. */
 if(!es_load((unsigned)i))return false;
 es.used|=1u<<(unsigned)i;
 if(!family_prepare_canvas()){es_fail(4);
  return false;
 }
 es.spec=(unsigned)i;
 es.pixels=0;
 es.draws[es.count]=d;
 es.active=true;
 return true;
}
static bool es_retire(unsigned off,int style)
{
 if(off>=64000)return false;
 bool native=es_native_owner[off]!=0;
 if(style!=MIRROR_SHADOW){
  if(native){if(style==MIRROR_BLEND)++es_blend_retirements;
   else ++es_normal_retirements;
   es_native_owner[off]=0;
  }
  if(es_extra_cell[off]){unsigned x=off%320,y=off/320;
   for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++){size_t n=(y*8+sy)*2560+x*8+sx;
    es_extra_retirements+=es_extra_owner[n]!=0;
    es_extra_owner[n]=0;
   }es_extra_cell[off]=0;
  }
 }else if(native||es_extra_cell[off])++es_shadow_cells;
 return native;
}
static bool es_extra(size_t n){return n<4096000&&es_extra_owner[n]!=0;
}
static void es_store(EnemyShotDraw *d,unsigned ax,unsigned ay,bool extra)
{
 size_t n=((unsigned)d->y*8+ay)*2560+(unsigned)d->x*8+ax;
 Uint32 *dst=(Uint32 *)canvas->pixels+n;
 const Uint8 *a=es_art.rgba[es.spec]+(ay*96+ax)*4;
 *dst=blend_rgba(*dst,a,a[3]);
 if(extra){es_extra_owner[n]=(uint8_t)(d->slot+1);
  es_extra_cell[(d->y+(int)(ay/8))*320+d->x+ax/8]=1;
  ++d->extra_stores;
 }
 else{hd_owner[n]=1;
  cloud_owner[n]=green_first[n]=green_under_owner[n]=0;
  ++d->core_stores;
 }
 OHS_SURVIVAL_WRITE(canvas,dst,extra?ENEMY_SHOT_EXTRA_STORE_TAG:ENEMY_SHOT_NATIVE_STORE_TAG);
}
static bool es_pixel(unsigned x,unsigned y,int style)
{
 if(!es.active)return false;
 EnemyShotDraw *d=es.draws+es.count;
 const EnemyShotSpec *s=es_specs+es.spec;
 if(es.pixels>=s->count){es_fail(6);
  family_fault(FC_ORDER);
  return true;
 }const EnemyShotWrite *w=s->writes+es.pixels;
 if(style!=MIRROR_NORMAL||x!=(unsigned)d->x+w->x||y!=(unsigned)d->y+w->y||expected[y*320+x]!=w->index||((Uint8 *)fc_source_pixels)[y*320+x]!=w->index){es_fail(6);
  family_fault(FC_ORDER);
  return true;
 }
 for(unsigned sy=0;sy<8;sy++)for(unsigned sx=0;sx<8;sx++)es_store(d,w->x*8+sx,w->y*8+sy,false);
 unsigned off=y*320+x;
 lamp272_clear(off);
 triple275_clear(off);
 private_ember269_clear(off);
 gray325_clear(off);
 longface573_clear(off);
 es_native_owner[off]=(uint8_t)(d->slot+1);
 selected[off]=1;
 es.writes[es.pixels]=*w;
 ++es.pixels;
 d->callbacks=es.pixels;
 es.contributed=true;
 return true;
}
static void es_end(void)
{
 if(!es.active)return;
 EnemyShotDraw *d=es.draws+es.count;
 const EnemyShotSpec *s=es_specs+es.spec;
 if(fc.frame_failed||es.pixels!=s->count||!es_draw_current(d)||!es_scope()||!es_art_current()||!es_bank(spriteSheet8)||!es_colors()||
 !b313_family_writer_draw_ready(fc_frame)||!family_geometry(true)||memcmp(fc_palette,rgb_palette,sizeof fc_palette)){es_fail(7);
  family_fault(FC_ORDER);
  return;
 }
 for(unsigned ay=0;ay<112;ay++)for(unsigned ax=0;ax<96;ax++)if(!s->mask[(ay/8)*12+ax/8]&&es_art.rgba[es.spec][(ay*96+ax)*4+3])es_store(d,ax,ay,true);
 if(d->extra_stores!=s->extra){es_fail(7);
  family_fault(FC_ORDER);
  return;
 }
 d->complete=true;
 ++es.count;
 es.active=false;
}
static void es_accept(void){es.accepted=es.contributed&&fc.ready&&!fc.frame_failed&&es_finish();
}
EnemyShotFamilyStatus render_mirror_enemy_shot_family_status(void)
{
 EnemyShotFamilyStatus s={.requested=es_any_requested(),.loaded=es_art.valid!=0,.active=es.active,.pending=es.pending,.contributed=es.contributed,.failed=es.failed||fc.frame_failed,
  .accepted=es.accepted,.first_reason=es.reason,.draw_count=es.count,.material_mask=es.used,.frame=fc_frame,.births=es_serial,.allocations=es_allocations,.motions=es_motions,.animations=es_animations,
  .normal_retirements=es_normal_retirements,.blend_retirements=es_blend_retirements,.shadow_cells=es_shadow_cells,.extra_retirements=es_extra_retirements,.clipped=es_clipped,.unwitnessed=es_unwitnessed,.lifetime_losses=es_lifetime_losses};
 memcpy(s.retirements,es_retirements,sizeof s.retirements);
 memcpy(s.draw,es.draws,sizeof s.draw);
 for(unsigned i=0;i<60;i++)s.birth[i]=es_life[i].birth;
 for(unsigned i=0;i<64000;i++)s.native_cells+=es_native_owner[i]!=0;
 for(unsigned i=0;i<4096000;i++)s.extra_pixels+=es_extra_owner[i]!=0;
 return s;
}
/* Separate read-only provenance receipt keeps EnemyShotBirth/FamilyStatus ABI
 * unchanged. It remains queryable after the emitter or shot retires, until
 * this native shot slot is allocated again. It grants no drawing authority. */
bool render_mirror_turret273_projectile_birth(unsigned slot,EnemyShotBirth *birth,uint64_t *token,unsigned *event,int *x,int *y,int *map)
{
 if(slot>=60||!birth||!token||!event||!x||!y||!map||!es_life[slot].turret273||
  !es_life[slot].birth.witnessed||es_life[slot].birth.generation!=es_life[slot].generation)return false;
 *birth=es_life[slot].birth;*token=es_life[slot].emitter_token;*event=es_life[slot].emitter_event;
 *x=es_life[slot].emitter_x;*y=es_life[slot].emitter_y;*map=es_life[slot].emitter_map;
 return true;
}
bool render_mirror_enemy_shot_family_pre_draw(EnemyShotDraw *d,uint32_t *argb,size_t count,uint8_t *native,size_t bytes)
{
 if(!d||!argb||count!=10752||!native||bytes!=168||!es.active||es.pixels||fc.frame_failed||!family_geometry(true))return false;
 *d=es.draws[es.count];
 for(unsigned y=0;y<112;y++)memcpy(argb+y*96,(const Uint32 *)canvas->pixels+(d->y*8+y)*2560+d->x*8,96*sizeof *argb);
 for(unsigned y=0;y<14;y++)memcpy(native+y*12,(const Uint8 *)fc_source_pixels+(d->y+y)*320+d->x,12);
 return true;
}
unsigned render_mirror_enemy_shot_family_callbacks(EnemyShotWrite *out,size_t count)
{if(!out||count<es.pixels)return 0;
 memcpy(out,es.writes,es.pixels*sizeof *out);
 return es.pixels;
}
bool render_mirror_enemy_shot_family_support(uint8_t *native,size_t bytes,uint8_t *extra,size_t pixels)
{
 if(!native||bytes!=64000||!extra||pixels!=4096000||!es.accepted||fc.frame_active||fc.frame_failed||!es_finish()||!b313_family_writer_peek_current(fc_frame))return false;
 memcpy(native,es_native_owner,64000);
 memcpy(extra,es_extra_owner,4096000);
 return true;
}
