"""Preparation only: finite fixtures and exact-source diagnostics, no compiler/process/writes."""
from pathlib import Path
import hashlib,struct,types,re
ROOT=Path(__file__).resolve().parents[1]
WIDGET_HELPER_SHA='d87929e9dda9d11d8832884fc5d9bcb69dd506b88534ed29c6100f31e773d595'
NEW_IDS=(112,113,226,227)
MATERIAL={112:1420112,113:1420113,226:80226,227:1470227}
NEW_PINS={112:'84546804885d7c602449fe0c4783d1873e60f30a8abde3e3095356fc3d8bd720',113:'20a9b6480d91a324a4ca375e79f596504103a80f165512fa33d8c5ffeeac7fba',226:'231a78b2ebc6a2410da297d05703b4c548f38926e7bd6e6b28c4fe6c4fa7071c',227:'9de332ec5d8d7f5c0e7eb56445aabebe22897b27a6fde1ee7f36da822076aac7'}
WRONG_MATERIALS={112:('assets/hd/current-compat/enemy-orb/bullet-112-8.hda','22e2be2903bc897f2f2d674dc6f95e740f57a510110d8bbcd8df8e969ab5c6fd',80112),227:('assets/hd/current-compat/protron/bullet-244-8.hda','901b61b1da6f538d6aac9bbd06a2f7d34e5e9d1e4d9df50c3f3eb01b1cd7b452',80244)}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def old_helper(root):
 p=Path(root)/'tests/widget_sonic_native_validation.py';raw=p.read_bytes()
 if sha(raw)!=WIDGET_HELPER_SHA:raise ValueError('Changed widget helper')
 m=types.ModuleType('approved_widget_native');m.__file__=str(p);exec(compile(raw,str(p),'exec'),m.__dict__);return m
_old=old_helper(ROOT)
OLD_IDS=_old.IDS
IDS=OLD_IDS+NEW_IDS
CANONICAL=dict(_old.CANONICAL,**{})
CANONICAL.update(NEW_PINS)
PACKS=('valid',)+tuple(k+str(i)for i in NEW_IDS for k in ('missing','bad','header'))
TAIL=b'\n#include "orb_protron_native_additions.c.inc"\nint main(int argc,char **argv)\n{\n if(argc>=2&&!strcmp(argv[1],"--orb-protron"))return op_main(argc,argv);\n return inherited_widget_sonic_dispatch(argc,argv);\n}\n'
def source_bundle(root):
 sources,old=old_helper(root).source_bundle(root);return sources,outer_shim(old,root)
def outer_shim(raw,root):
 if raw!=old_helper(root).source_bundle(root)[1]or raw.count(b'int main(')!=1:raise ValueError('Changed ten historical dispatches')
 return raw.replace(b'int main(',b'int inherited_widget_sonic_dispatch(',1)+TAIL
def reverse_shim(raw,root):
 if not raw.endswith(TAIL):raise ValueError('Changed new tail')
 body=raw[:-len(TAIL)]
 if body.count(b'int inherited_widget_sonic_dispatch(')!=1 or b'int main('in body:raise ValueError('Changed dispatcher')
 old=body.replace(b'int inherited_widget_sonic_dispatch(',b'int main(',1)
 if old!=old_helper(root).source_bundle(root)[1]:raise ValueError('Changed old bytes')
 return old
def wrong_materials(root=ROOT):
 out={}
 for i,(name,pin,identity)in WRONG_MATERIALS.items():
  raw=(Path(root)/name).read_bytes()
  if sha(raw)!=pin or len(raw)!=43036 or struct.unpack('<4s6I',raw[:28])!=(b'HDR1',identity,8,12,14,0,0):raise ValueError('Changed real wrong-material fixture input')
  out[i]=raw
 return out
def fixture_bytes(raw,index,leaf,wrong=None):
 if type(raw)is not bytes or len(raw)!=43036 or type(index)is not int or index not in IDS or leaf not in PACKS:raise ValueError('Invalid finite fixture')
 if leaf=='valid':return raw
 m=re.fullmatch(r'(missing|bad|header)([0-9]+)',leaf);kind,target=m.group(1),int(m.group(2))
 if index!=target:return raw
 if kind=='missing':return None
 b=bytearray(raw)
 if kind=='header':struct.pack_into('<I',b,4,{112:80112,113:80113,226:1470226,227:80227}[index])
 elif index in WRONG_MATERIALS:
  if wrong is None or sha(wrong[index])!=WRONG_MATERIALS[index][1]:raise ValueError('Actual alternate material required')
  b=bytearray(wrong[index]);struct.pack_into('<I',b,4,MATERIAL[index])
 else:b[128]^=1
 return bytes(b)
def fixture_payloads(hdas,pins,names):
 if any(set(d)!=set(IDS)for d in (hdas,pins,names)):raise ValueError('Exact29 assets required')
 for i in IDS:
  if type(i)is not int or type(hdas[i])is not bytes or sha(hdas[i])!=pins[i]:raise ValueError('Changed fixture bytes')
  p=Path(names[i])
  if p.is_absolute()or '..'in p.parts or not str(p).endswith('.hda'):raise ValueError('Bad fixture path')
  if i in CANONICAL:
   if sha(hdas[i])!=CANONICAL[i]or str(p)!='content/'+CANONICAL[i]+'.hda':raise ValueError('Changed canonical identity/path')
  elif p.name!=str(p):raise ValueError('Old flat path changed')
 if len(set(names.values()))!=29:raise ValueError('Duplicate paths')
 wrong=wrong_materials();out={}
 for leaf in PACKS:
  for i in IDS:
   raw=fixture_bytes(hdas[i],i,leaf,wrong)
   if raw is not None:out['orb-protron-packs/'+leaf+'/'+names[i]]=raw
 for missing in (None,112,113):
  leaf='legacy-valid'if missing is None else'legacy-missing'+str(missing)
  for i in (112,113):
   if i!=missing:out['orb-protron-packs/'+leaf+'/enemy-orb112113-'+str(i)+'-8.hda']=hdas[i]
 if len(out)!=377:raise ValueError('Finite377 fixture closure changed')
 return out
def native_input(base_stdin,hdt):return _old.native_input(base_stdin,hdt)
CASE_INVENTORY={'current28_complete_oracles':28,'four_missing_coldwrong_identity_retired':16,'two_phase_transitions_and_four_missing_phase_isolation':6,'four_phase_used_and_other_phase_unused_palette':8,'background_four_stages':4,'227_two_halos_ordinary_and_real_fade':4,'independent_roots_player_lease':3,'bit27_all28':1,'clip_xmas_density_asteroid_intent':4,'four_used_cache_and_two_source_mutations':6,'old_orb_atomic_missing_both_directions':2,'real227_to_player70_retired_cell_bit27_guard':1}
assert sum(CASE_INVENTORY.values())==83
SYNTAX_TUS=('src/render_mirror.c','src/tyrian2.c','src/entity_draw.c')
MACRO_ON_PIXEL_SCOPE='DEFERRED; tiny uses actual policy/render route/used-source proof with explicit state/resource stubs, not complete ON sessions/pixels'
def function(raw,name):
 matches=list(re.finditer(r'^(?:static )?(?:bool|void) '+re.escape(name)+r'\(',raw,re.M))
 if len(matches)!=1:raise ValueError('Nonunique function '+name)
 start=matches[0].start();op=raw.index('{',start);depth=0
 for end in range(op,len(raw)):
  depth+=(raw[end]=='{')-(raw[end]=='}')
  if not depth:return raw[start:end+1]
 raise ValueError('Unclosed function')
def tiny_sources(root):
 root=Path(root);game=(root/'src/tyrian2.c').read_text();render=(root/'src/render_mirror.c').read_text();shared=(root/'src/global_projectile91_mirror.inc').read_text()
 begin='\n#if defined(ENEMY_REUSE_HD_PROTOTYPE) && ENEMY_REUSE_HD_PROTOTYPE && !defined(RENDER_MIRROR_DISABLED)\n\t\t\t\t\t\t\tif ((widget_sonic_member_index(sprite)'
 if game.count(begin)!=1:raise ValueError('Changed unique route context')
 start=game.index(begin);endmark='blit_sprite2(VGAScreen, enemyShot[z].sx, enemyShot[z].sy, spriteSheet8, sprite);';route=game[start:game.index(endmark,start)+len(endmark)]
 admission=function(render,'render_mirror_enemy_shot');source=function(shared,'global_projectile91_source_matches');decline=function(shared,'global_projectile91_cache_decline');cache=function(shared,'global_projectile91_check_cache')
 members=re.findall(r'^static const unsigned global_projectile91_widget_sonic_members=.*?;',shared,re.M)
 if len(members)!=1:raise ValueError('Changed finite mask')
 resources=sorted(set(re.findall(r'\b([a-zA-Z0-9_]+_resource)\(',source)));macros='\n'.join('#define '+n+'(...) ((void *)1)'for n in resources)
 text=r'''#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "enemy_orb_protron_policy.h"
bool game_probe_enabled,asteroid_hd_enabled;int game_probe_density=8;bool game_probe_missing,game_probe_invalid;const char *game_probe_assets="legacy";
static bool observe_requested,probe_requested;
#if defined(ENEMY_REUSE_HD_PROTOTYPE) && ENEMY_REUSE_HD_PROTOTYPE
bool enemy_reuse_observe_requested(void){return observe_requested;}
bool enemy_reuse_probe_requested(void){return probe_requested;}
#endif
/* Explicit stand-ins for unrelated resources/backend, not a private session. */
typedef struct {void *data;} Sprite2_array;
typedef struct {bool initialized,valid;int bank,index,w,h,anchor_x,anchor_y;} Asset;
static Asset assets[600];static int native_data;static Sprite2_array spriteSheet8={&native_data};
static SDL_PixelFormat fmt;static SDL_Surface screen;static SDL_Surface *game_screen=&screen,*VGAScreen=&screen;
static bool active=true,xmas=false;static const char *reject_reason=NULL;static char global_asset_directory[2]="x";
static unsigned shared_calls,atomic_calls,generic_reads,generic_draws;static bool accept;
#define MIRROR_NORMAL 0
#define render_mirror_shadow_end() ((void)0)
#define global_projectile91_observed_preflight() ((void)0)
static int global_projectile91_draw(SDL_Surface *s,int x,int y,Sprite2_array b,unsigned i){(void)s;(void)x;(void)y;(void)b;(void)i;++shared_calls;return accept;}
#define projectile91_draw(...) false
#define projectile304_draw(...) false
static bool enemy_orb112113_draw(SDL_Surface *s,int x,int y,Sprite2_array b,unsigned i){(void)s;(void)x;(void)y;(void)b;(void)i;++atomic_calls;return accept;}
#define enemy_energy_slot(...) (-1)
#define enemy_tank_shell_family_ready() false
#define enemy_energy_family_ready() false
static bool read_asset(Asset *a,int density){assert(a->bank==8&&(a->index==112||a->index==113));assert(density==8||density==4);++generic_reads;return accept;}
static bool draw_asset(int x,int y,Asset *a,int style,void *extra){(void)x;(void)y;(void)style;(void)extra;assert(a->bank==8&&(a->index==112||a->index==113));++generic_draws;return true;}
'''+admission+r'''
static unsigned ordinary,legacy,classic,begins,blits;static bool mirrored;
static struct {int sx,sy;unsigned sgr;} enemyShot[1];
#define enemy_reuse_shot_begin_draw(...) (++begins)
#define draw_enemy_reuse_shot_sprite2(...) (++legacy,++blits)
#define draw_enemy_shot_sprite2(s,x,y,b,i) (++ordinary,mirrored=render_mirror_enemy_shot(s,x,y,b,i),++blits)
#define blit_sprite2(...) (++classic,++blits)
static void route(unsigned sprite){unsigned z=0;(void)z;
'''+route+r'''
}
static unsigned global_projectile91_used_members;static bool ready,last_output_valid,have_fade_saved,global_projectile91_cached,global_projectile91_fault;static int fade_mode;static unsigned global_projectile91_output_palette[256],rgb_palette[256];
#define projectile91_source(...) true
'''+macros+'\n'+members[0]+'\n'+source+'\n'+decline+r'''
static bool global_projectile91_cache_source_matches(void){return global_projectile91_source_matches(spriteSheet8);}
'''+cache+r'''
static void clear_counts(void){ordinary=legacy=classic=begins=blits=shared_calls=atomic_calls=generic_reads=generic_draws=0;mirrored=false;memset(assets,0,sizeof(assets));}
int main(void){unsigned cases=0;unsigned ids[4]={112,113,226,227};fmt.BitsPerPixel=8;fmt.BytesPerPixel=1;screen.format=&fmt;screen.w=320;screen.h=200;screen.pitch=320;screen.pixels=&native_data;
#if defined(ENEMY_REUSE_HD_PROTOTYPE) && ENEMY_REUSE_HD_PROTOTYPE
 const bool enabled=true;
#else
 const bool enabled=false;
#endif
 for(unsigned state=0;state<8;state++)for(unsigned asteroid=0;asteroid<2;asteroid++)for(unsigned root=0;root<2;root++)for(unsigned valid=0;valid<2;valid++)for(unsigned k=0;k<4;k++) {
  game_probe_enabled=state&1;observe_requested=state&2;probe_requested=state&4;asteroid_hd_enabled=asteroid;global_asset_directory[0]=root?'x':0;accept=valid;
  bool orb=k<2,legacy_route=!orb&&enabled&&state!=0,observe=enabled&&(state&2);bool allowed=orb?(!asteroid&&!observe):(!enabled||state==0);
  clear_counts();route(ids[k]);assert(blits==1&&legacy==legacy_route&&ordinary==!legacy_route&&begins==legacy_route&&!classic);
  if(legacy_route)assert(!shared_calls&&!atomic_calls&&!generic_reads&&!generic_draws);
  /* Direct API is checked separately too: legacy intent cannot be bypassed. */
  clear_counts();bool result=render_mirror_enemy_shot(game_screen,0,0,spriteSheet8,ids[k]);
  if(observe)assert(!result&&!shared_calls&&!atomic_calls&&!generic_reads&&!generic_draws);
  else if(orb&&asteroid)assert(result==accept&&atomic_calls==1&&!shared_calls&&!generic_reads&&!generic_draws);
  else if(root)assert(result==(allowed&&accept)&&shared_calls==allowed&&!atomic_calls&&!generic_reads&&!generic_draws);
  else if(orb)assert(result==accept&&!shared_calls&&!atomic_calls&&generic_reads==(accept?1u:2u)&&generic_draws==accept);
  else assert(!result&&!shared_calls&&!atomic_calls&&!generic_reads&&!generic_draws);
  global_projectile91_used_members=16777216u<<k;assert(global_projectile91_source_matches(spriteSheet8)==allowed);ready=last_output_valid=have_fade_saved=global_projectile91_cached=true;fade_mode=1;global_projectile91_check_cache();assert(ready==allowed&&last_output_valid==allowed&&global_projectile91_cached==allowed);if(!allowed)assert(!have_fade_saved&&!fade_mode);
  global_projectile91_used_members=131072u;assert(global_projectile91_source_matches(spriteSheet8));++cases;
 }
 unsigned prior[]={91,70,20,214,215,216,244,42};
 for(unsigned state=0;state<8;state++)for(unsigned j=0;j<8;j++) {game_probe_enabled=state&1;observe_requested=state&2;probe_requested=state&4;asteroid_hd_enabled=false;global_asset_directory[0]='x';clear_counts();route(prior[j]);bool old=enabled&&(j>=3&&j<=6||(j==2&&state));assert(blits==1&&legacy==old&&begins==old);if(j==7)assert(classic==1);else if(!old)assert(ordinary==1||(j>=3&&j<=6&&classic==1));++cases;}
 assert(cases==320);printf("PASS Orb Protron exact-source routing proof: 320 cases; NOT full ON session/pixels\n");return 0;}
'''
 files=('src/tyrian2.c','src/render_mirror.c','src/global_projectile91_mirror.inc','src/enemy_widget_sonic_policy.h','src/enemy_orb_protron_policy.h','src/asteroid1_enemy_orb112113_mirror.inc','src/enemy_reuse_mirror.inc')
 return text.encode(),{p:sha((root/p).read_bytes())for p in files}
