"""Finite tank preparation. No compiler/process/generator/write side effects.
Caller-supplied original bytes only; no embedded original game records or paths.
"""
from pathlib import Path
import hashlib,re,struct,types
ROOT=Path(__file__).resolve().parents[1]
GREEN_HELPER_SHA='c5b62a8699a64d79c32e0605fed46eca00e1820c80c1ac91a147a2e6523b469d'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def green_helper(root):
 p=Path(root)/'tests/player_green_cache_fix_native_validation.py';raw=p.read_bytes()
 if sha(raw)!=GREEN_HELPER_SHA:raise ValueError('Changed approved Green adapter')
 m=types.ModuleType('approved_green_cache');m.__file__=str(p);exec(compile(raw,str(p),'exec'),m.__dict__);return m
_green=green_helper(ROOT);_old=_green.p244_helper(ROOT)
GREEN_IDS=tuple(i for i in _green.ASSETS if i!=1470227)
NEW_IDS=(146,147);IDS=_old.IDS+NEW_IDS+GREEN_IDS
CANONICAL=dict(_old.CANONICAL);CANONICAL.update({146:'d7c88729cdc18e4fb90a4c46be89681e99b7cdcd43bb6421c639653355109afa',147:'fef0333704fd2afb69fc48a38555e2b892608d590054a9819064cf5cb7fecdbf'});CANONICAL.update({i:_green.ASSETS[i]for i in GREEN_IDS})
PACKS=('valid',)+tuple(k+str(i)for i in NEW_IDS for k in ('missing','bad','header'))
TAIL=b'\n#include "tank_shell_native_additions.c.inc"\nint main(int argc,char **argv)\n{\n if(argc>=2&&(!strcmp(argv[1],"--tank-shared")||!strcmp(argv[1],"--tank-energy")))return tk_main(argc,argv);\n return inherited_green_cache_dispatch(argc,argv);\n}\n'
def source_bundle(root):
 sources,raw=green_helper(root).source_bundle(root);sources=dict(sources);sources['tank_shell_native_additions.c.inc']=(Path(root)/'tests/tank_shell_native_additions.c.inc').read_bytes();return sources,outer_shim(raw,root)
def outer_shim(raw,root):
 if raw!=green_helper(root).source_bundle(root)[1]or raw.count(b'int main(')!=1:raise ValueError('Changed historical entry')
 return raw.replace(b'int main(',b'int inherited_green_cache_dispatch(',1)+TAIL
def reverse_shim(raw,root):
 if not raw.endswith(TAIL):raise ValueError('Changed tank tail')
 body=raw[:-len(TAIL)]
 if body.count(b'int inherited_green_cache_dispatch(')!=1 or b'int main('in body:raise ValueError('Changed dispatcher')
 old=body.replace(b'int inherited_green_cache_dispatch(',b'int main(',1)
 if old!=green_helper(root).source_bundle(root)[1]:raise ValueError('Changed prior bytes')
 return old
def fixture_payloads(hdas,pins,names):
 if any(type(d)is not dict or set(d)!=set(IDS)for d in (hdas,pins,names))or any(type(i)is not int for i in hdas):raise ValueError('Exact43 resources required')
 for i in IDS:
  b=hdas[i];p=Path(names[i])
  if type(b)is not bytes or len(b)!=43036 or sha(b)!=pins[i]:raise ValueError('Unpinned bytes')
  if p.is_absolute()or '..'in p.parts or not str(p).endswith('.hda'):raise ValueError('Invalid finite path')
  if i in CANONICAL:
   if sha(b)!=CANONICAL[i]or str(p)!='content/'+CANONICAL[i]+'.hda':raise ValueError('Changed canonical material/path')
  elif p.name!=str(p):raise ValueError('Changed old flat path')
 if len(set(names.values()))!=43:raise ValueError('Duplicate paths')
 _green.green_payloads({**{i:hdas[i]for i in GREEN_IDS},1470227:hdas[227]})
 for i in NEW_IDS:
  if struct.unpack('<4s6I',hdas[i][:28])!=(b'HDR1',1220000+i,8,12,14,0,0):raise ValueError('Tank identity/geometry mismatch')
 result={'tank-shared-packs/valid/'+names[i]:hdas[i]for i in IDS}
 for leaf in PACKS[1:]:
  m=re.fullmatch(r'(missing|bad|header)(146|147)',leaf);kind,target=m[1],int(m[2])
  for i in NEW_IDS:
   b=hdas[i]
   if i==target:
    if kind=='missing':continue
    b=bytearray(b)
    if kind=='bad':b[128]^=1
    else:struct.pack_into('<I',b,4,80000+i)
    b=bytes(b)
   result['tank-shared-packs/'+leaf+'/'+names[i]]=b
 if len(result)!=53:raise ValueError('Finite fixture count changed')
 return result
def native_input(base_stdin,hdt,smoke,root=ROOT):return green_helper(root).native_input(base_stdin,hdt,smoke,root)
CASE_INVENTORY={'current31_full_oracles':31,'two_cold_missing_corrupt_header_peer_retained':6,'warm_identity_geometry_before_cache':4,'two_source_mutations':2,'used_unused_palette_precompose_and_cached':4,'unused_member_failure_old29_plus_peer':2,'retired_used_resource_provenance':2,'repeat_sameposition_nextframe_and_phase_transition':3,'root_epoch_and_player_lease':2,'background_fourstages_and_recovery':4,'two_highbits_real_Green_retirement_pixel_rect_normal_fade':8,'bit29_bit30_all31':1,'clipping_density':2,'retained_original_Green_prehook_cases':4}
assert len(IDS)==43 and sum(CASE_INVENTORY.values())==75
ENERGY_CASE_INVENTORY={k:v for k,v in CASE_INVENTORY.items() if k!="current31_full_oracles"}
ENERGY_CASE_INVENTORY["current_two_energy_full_oracles"]=2
assert sum(ENERGY_CASE_INVENTORY.values())==46
ENERGY_SCOPE="2 changed direct + 44 focused; prior29 direct and tiny not dispatched; mixed dependency draws retained"
SYNTAX_TUS=('src/render_mirror.c','src/tyrian2.c','src/entity_draw.c')
MACRO_ON_PIXEL_SCOPE='DEFERRED; exact-source policy/route/cache diagnostic only, explicit backend/resource stubs, not full legacy ON session/pixels'
def tiny_sources(root):
 """Actual full renderer dispatch, actual tyrian route, actual shared proof/cache
 and actual policy headers. Only finite diagnostic driver/backend stubs change.
 The legacy family-ready stub is deliberate: no old loader or ON pixel claim.
 """
 root=Path(root);raw,pins=_old.tiny_sources(root);s=raw.decode()
 def one(old,new):
  nonlocal s
  if s.count(old)!=1:raise ValueError('Changed tiny fixture anchor '+old)
  s=s.replace(old,new,1)
 one('#include "enemy_orb_protron_policy.h"','#include "enemy_orb_protron_policy.h"\n#include "enemy_tank_shared_policy.h"')
 one('#define enemy_tank_shell_family_ready() false','static unsigned tank_load_calls,tank_draw_calls;static bool legacy_accept;\nstatic bool enemy_tank_shell_family_ready(void){++tank_load_calls;assets[505].bank=assets[506].bank=122;assets[505].index=146;assets[506].index=147;return legacy_accept;}')
 one('assert(a->bank==8&&(a->index==112||a->index==113));++generic_draws;return true;}', 'if(a->bank==122){assert(a->index==146||a->index==147);++tank_draw_calls;return true;}assert(a->bank==8&&(a->index==112||a->index==113));++generic_draws;return true;}')
 one('mirrored=false;memset(assets,0,sizeof(assets));}', 'mirrored=false;tank_load_calls=tank_draw_calls=0;memset(assets,0,sizeof(assets));}')
 marker='int main(void){unsigned cases=0;'
 if s.count(marker)!=1:raise ValueError('Changed old tiny driver')
 s=s[:s.index(marker)]+r'''int main(void){unsigned cases=0;unsigned ids[2]={146,147};fmt.BitsPerPixel=8;fmt.BytesPerPixel=1;screen.format=&fmt;screen.w=320;screen.h=200;screen.pitch=320;screen.pixels=&native_data;
#if defined(ENEMY_REUSE_HD_PROTOTYPE) && ENEMY_REUSE_HD_PROTOTYPE
 const bool enabled=true;
#else
 const bool enabled=false;
#endif
 /* Four legacy-root states are deliberately distinct: NULL/empty/bad/valid.
  * OFF generic enabled without assets remains ordinary; ON requested helper
  * blocks ordinary. Failed nonNULL legacy roots must never borrow global. */
 for(unsigned state=0;state<8;state++)for(unsigned root=0;root<2;root++)for(unsigned assets_state=0;assets_state<4;assets_state++)for(unsigned valid=0;valid<2;valid++)for(unsigned k=0;k<2;k++){
  game_probe_enabled=state&1;observe_requested=state&2;probe_requested=state&4;asteroid_hd_enabled=false;global_asset_directory[0]=root?'x':0;game_probe_assets=assets_state==0?NULL:assets_state==1?"":assets_state==2?"missing":"valid";accept=valid;legacy_accept=assets_state==3&&valid;
  bool allowed=!assets_state&&(!enabled||state==0),observe=enabled&&(state&2);clear_counts();route(ids[k]);assert(blits==1&&ordinary==1&&!legacy&&!begins&&!classic);
  if(observe)assert(!mirrored&&!shared_calls&&!tank_load_calls&&!tank_draw_calls);
  else if(root&&allowed)assert(mirrored==accept&&shared_calls==1&&!tank_load_calls&&!tank_draw_calls);
  else assert(mirrored==legacy_accept&&!shared_calls&&tank_load_calls==1&&tank_draw_calls==legacy_accept);
  assert(!generic_reads&&!generic_draws&&!atomic_calls);
  /* Start a valid used-new proof then change intent, executing actual production
   * source_matches/cache invalidation (backend resource functions are stubs). */
  bool saved_enabled=game_probe_enabled,saved_observe=observe_requested,saved_probe=probe_requested;const char *saved_assets=game_probe_assets;
  game_probe_enabled=observe_requested=probe_requested=false;game_probe_assets=NULL;global_asset_directory[0]='x';global_projectile91_used_members=536870912u<<k;assert(global_projectile91_source_matches(spriteSheet8));ready=last_output_valid=have_fade_saved=global_projectile91_cached=true;fade_mode=1;
  game_probe_enabled=saved_enabled;observe_requested=saved_observe;probe_requested=saved_probe;game_probe_assets=saved_assets;assert(global_projectile91_source_matches(spriteSheet8)==allowed);global_projectile91_check_cache();assert(ready==allowed&&last_output_valid==allowed&&global_projectile91_cached==allowed);if(!allowed)assert(!have_fade_saved&&!fade_mode);
  global_projectile91_used_members=131072u;assert(global_projectile91_source_matches(spriteSheet8));++cases;
 }
 unsigned prior[]={91,70,20,214,215,216,125,42};game_probe_assets=NULL;
 for(unsigned state=0;state<8;state++)for(unsigned j=0;j<8;j++){game_probe_enabled=state&1;observe_requested=state&2;probe_requested=state&4;global_asset_directory[0]='x';clear_counts();route(prior[j]);bool old=enabled&&(j>=3&&j<=5||((j==2||j==6)&&state));assert(blits==1&&legacy==old&&begins==old);if(j==7)assert(classic==1);else if(!old)assert(ordinary==1||(j>=3&&j<=5&&classic==1));assert(!tank_load_calls&&!tank_draw_calls);++cases;}
 assert(cases==320);printf("PASS Tank exact-source routing proof: 320 cases; NOT full ON session/pixels\n");return 0;}
'''
 pins=dict(pins)
 for name in ('src/enemy_tank_shared_policy.h','src/enemy_tank_shared_mirror.inc','src/current_tank_shell_payload_pins.h'):pins[name]=sha((root/name).read_bytes())
 return s.encode(),pins

RENDER_BASE_SHA='748929771f5626045966fb9d881c4ded3e3d94c1145ab68288ca3956a963b084'
TANK_RENDER_ADDITIONS=(
 '#include "enemy_tank_shared_policy.h"\n',
 '#include "enemy_tank_shared_mirror.inc"\n',
 'static bool enemy_tank_shared_source(Sprite2_array,unsigned);\n',
 'static bool enemy_tank_shared_palette_matches(unsigned);\n',
 'static Asset *enemy_tank_shared_resource(const char *,unsigned);\n',
 'static void enemy_tank_shared_shutdown(void);\n',
 ' /* Tank legacy intent retains the original branch below in both macro modes.\n  * An ordinary global selection is authoritative even when its alias fails. */\n if(tank_shared_member_index(index)&&global_asset_directory[0]&&tank_shared_ordinary_allowed(index)) {\n  global_projectile91_observed_preflight();return global_projectile91_draw(surface,x,y,bank,index)>0;\n }\n')
def reverse_tank_render(text):
 """Exact additive inverse; preserves old pre-final fix and every legacy byte.
 No Git/private source lookup. Reject missing/duplicated addition or other edit.
 """
 binary=type(text)is bytes
 if binary:text=text.decode('utf-8')
 if type(text)is not str:raise ValueError('Renderer text/bytes required')
 for added in TANK_RENDER_ADDITIONS:
  if text.count(added)!=1:raise ValueError('Tank additive inverse count changed')
  text=text.replace(added,'',1)
 if sha(text.encode())!=RENDER_BASE_SHA:raise ValueError('Unrelated renderer edit')
 return text.encode()if binary else text
