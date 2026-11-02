"""Finite render-only muzzle qualification preparation; no subprocess or writes.
Current renderer runs in the native TU. Sidecar/dispatch are exact source
extracts; the reviewed new wrapper is linked from fresh entity_draw.o; real JE_drawEnemy allocation and JE_main retirement callsites
are static contracts + later scene evidence, NOT full native gameplay coverage.
"""
from pathlib import Path
import hashlib,json,re,struct,types
ROOT=Path(__file__).resolve().parents[1]
OLD_HELPER_SHA='c407cbbc5111d949d06882c3d6fa57c3f502dc2a38fe18a2024e024075ef2219'
RAW_PINS={'bank20':'4bd9a72339e30440c172e385f258c8895b516ff84026a9a6b5a65ada4cf0ab90','pic':'76fa51ba6878c886f67daa65cf6d19968615e4423822c9fe1dde797fc2f8d802','shp':'80cae98e073be6d7f710495920b71497bb23f108ea6631d6faf352c4729474f0'}
CASE_INVENTORY={'shifted147_and_unregistered_actor15_actor195_weapon7_and146_oracles':5,'isolated_actual_sidecar_lifecycle_and_poison':6,'viewport_two_inside_four_outside_density4':7,'missing_corrupt_used_asset_palette_background_pre_cache':6,'actual_Green_outside_oldtile_retirement_pixel_rect_normal_fade':4,'actual_font_context_overlap_retirement':2,'partial_halo_final_pixel_rect':2}
assert sum(CASE_INVENTORY.values())==32
SCOPE='32 finite OFF renderer setups; exact extracted sidecar/route state, not full JE_drawEnemy/JE_main execution. ON diagnostic only lane/dispatch, not legacy pixels. No old46 matrix rerun.'
def sha(b):return hashlib.sha256(b).hexdigest()
def old_helper(root):
 p=Path(root)/'tests/tank_shell_native_validation.py';raw=p.read_bytes()
 if sha(raw)!=OLD_HELPER_SHA:raise ValueError('Changed approved predecessor helper')
 m=types.ModuleType('muzzle_predecessor');m.__file__=str(p);exec(compile(raw,str(p),'exec'),m.__dict__);return m

def extracts(root):
 root=Path(root);ty=(root/'src/tyrian2.c').read_text();en=(root/'src/entity_draw.c').read_text()
 start=ty.index('/* Render-only birth registration.');end=ty.index('\nboss_bar_t boss_bar[2];',start);side=ty[start:end]
 if side.count('tank_muzzle_shots[ENEMY_SHOT_MAX]')!=1 or any(side.count(n+'(')!=1 for n in ('tank_muzzle_allocate','tank_muzzle_retire','tank_muzzle_birth','tank_muzzle_draw')):raise ValueError('Changed finite sidecar block')
 for text,count in [('tank_muzzle_allocate(b);',1),('tank_muzzle_birth(b,i,temp3,j,tempPos);',1),('tank_muzzle_retire(z);',2),('memset(tank_muzzle_shots, 0, sizeof(tank_muzzle_shots));',1)]:
  if ty.count(text)!=count:raise ValueError('Missing/duplicate lifecycle callsite '+text)
 if not ty.index('tank_muzzle_allocate(b);')<ty.index('enemyShotAvail[b] = !enemyShotAvail[b];')<ty.index('tank_muzzle_birth(b,i,temp3,j,tempPos);'):raise ValueError('Allocation provenance ordering')
 anchor='int muzzle_registration = tank_muzzle_draw(z, enemyShot[z].sgr + enemyShot[z].animate);'
 if ty.count(anchor)!=1:raise ValueError('Dispatch provenance')
 p=ty.index(anchor);q=ty.index('\n\t\t\t\t\t\t}',p)+len('\n\t\t\t\t\t\t}')
 route=ty[p:q]
 if route.count('spriteSheet12')!=1 or route.index('tank_muzzle_draw(')>route.index('sgr >= 500')or route.count('draw_tank147_muzzle_sprite2(')!=1:raise ValueError('Bank-crossing route order')
 p=en.index('void draw_tank147_muzzle_sprite2(');q=en.index('\n}',p)+2;wrapper=en[p:q]
 if en.count('void draw_tank147_muzzle_sprite2(')!=1 or wrapper.count('blit_sprite2(')!=1:raise ValueError('Single classic wrapper')
 result={'sidecar':side,'route':route,'wrapper':wrapper}
 if any(sha(v.encode())!=EXTRACT_PINS[k]for k,v in result.items()):raise ValueError('Changed reviewed extract bytes')
 return result

def source_bundle(root):
 root=Path(root);old=old_helper(root);sources,raw=old.source_bundle(root);sources=dict(sources);ex=extracts(root)
 generated=(ex['sidecar']+'\nstatic void mu_level_reset(void){memset(tank_muzzle_shots, 0, sizeof(tank_muzzle_shots));}\nstatic void mu_actual_route(unsigned z){\n'+ex['route']+'\n}\n').encode()
 sources['tank_muzzle_extracted.c.inc']=generated;sources['tank_muzzle_native_additions.c.inc']=(root/'tests/tank_muzzle_native_additions.c.inc').read_bytes()
 if raw.count(b'int main(')!=1:raise ValueError('Changed inherited entry')
 body=raw.replace(b'int main(',b'int inherited_tank_dispatch(',1)
 return sources,body+b'\n#include "tank_muzzle_extracted.c.inc"\n#include "tank_muzzle_native_additions.c.inc"\nint main(int argc,char **argv){if(argc>=2&&!strcmp(argv[1],"--tank-muzzle"))return mu_main(argc,argv);return inherited_tank_dispatch(argc,argv);}\n'

def fixture_payloads(hdas,pins,names,huf,root=ROOT):
 result=old_helper(root).fixture_payloads(hdas,pins,names)
 approved=(Path(root)/'assets/hd/shared-ui-v1/gameplay-hud-font-v1.hda').read_bytes()
 if type(huf)is not bytes or huf!=approved:raise ValueError('Exact existing HUF required')
 result['muzzle-font/gameplay-hud-font-v1.hda']=huf
 return result

def native_input(base_stdin,hdt,smoke,bank20,pic,shp,root=ROOT):
 for name,raw in [('bank20',bank20),('pic',pic),('shp',shp)]:
  if type(raw)is not bytes or sha(raw)!=RAW_PINS[name]:raise ValueError('Changed original '+name)
 old=old_helper(root).native_input(base_stdin,hdt,smoke,root)
 if len(old)!=117112 or len(bank20)!=46204:raise ValueError('Changed predecessor stream')
 # Original packed weapon3 (not logical extended-table arithmetic).
 weapon=hdt[21188+3*80:21188+4*80]
 if len(weapon)!=80:raise ValueError('Missing weapon3')
 offsets=struct.unpack_from('<14I',pic,2);p,end=offsets[2:4];pixels=bytearray()
 while len(pixels)<64000:
  if p>=end:raise ValueError('PIC3 truncated')
  v=pic[p];p+=1;n=1
  if v&192==192:n=v&63;v=pic[p];p+=1
  pixels.extend(bytes([v])*n)
 if len(pixels)!=64000 or sha(pixels)!='83c5979f54de07f79e0c13970f242ae6f7435d4d396a168b340458c955c0e0f4':raise ValueError('Changed original PIC3')
 tables=struct.unpack_from('<H',shp)[0];offsets=struct.unpack_from('<%dI'%tables,shp,2);p=offsets[2];count=struct.unpack_from('<H',shp,p)[0];p+=2
 if count!=127:raise ValueError('TINY glyph count')
 glyphs=bytearray(struct.pack('<H',count))
 for _ in range(count):
  present=shp[p];p+=1
  if not present:glyphs.extend(bytes(6));continue
  w,h,n=struct.unpack_from('<3H',shp,p);p+=6;glyphs.extend(struct.pack('<3H',w,h,n)+shp[p:p+n]);p+=n
 return old+weapon+bank20+bytes(pixels)+bytes(glyphs)

EXTRACT_PINS={'sidecar':'21f74515a9304cb6ef7f2d2a1a867017ef758b7754b0c2c1ee1698c3cb644617','route':'d638dd4304837526be61e43afd7c7ade1c3388d02d93f63615f7dd42c965a71a','wrapper':'65c1310262618c4d6ae6c72307eba1c51319cdb84050d0c16c37897a36e9ad96'}
PROVENANCE={'current_renderer':'whole current render_mirror.c included; real font and owner implementation', 'extracted_units':'exact reviewed sidecar and bank-crossing dispatch; controlled shot/actor fixtures; wrapper byte-checked and linked from fresh entity_draw.o', 'not_executed':'new JE_drawEnemy/JE_main allocation/retirement integration; static callsite contracts plus separate actual scene', 'support_object_exceptions':'Fresh tyrian2.o/entity_draw.o plus new harness; 83 unchanged support objects. Actual new entity wrapper linked, hash-reviewed but not redefined in harness. No claim of JE_drawEnemy/JE_main execution', 'font':'real existing HUF and original caller PIC3/TINY, not inactive stub; conservative footprint retirement is distinct from actual alpha overlap', 'macro_on':'actual lane/header/dispatch with explicit backend counters only; no legacy ON pixels'}
TINY_CASES=153
TINY_STDOUT='PASS Tank muzzle exact-source lane/dispatch: 153 cases; NOT legacy ON pixels or full gameplay\n'
def tiny_sources(root):
 root=Path(root);ex=extracts(root);renderer=(root/'src/render_mirror.c').read_text()
 lane='bool render_mirror_tank147_muzzle_lane(void)\n{return global_asset_directory[0]&&tank_shared_ordinary_allowed(147);}'
 if renderer.count(lane)!=1:raise ValueError('Changed exact lane')
 prefix=r'''#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <assert.h>
/* Explicit diagnostic backend declarations, not replacement policy logic. */
#define GAME_PROBE_H
static bool game_probe_enabled,asteroid_hd_enabled,observe,probe;
static const char *game_probe_assets;
#include "enemy_tank_shared_policy.h"
#include "enemy_orb_protron_policy.h"
#if defined(ENEMY_REUSE_HD_PROTOTYPE) && ENEMY_REUSE_HD_PROTOTYPE && !defined(RENDER_MIRROR_DISABLED)
bool enemy_reuse_observe_requested(void){return observe;}
bool enemy_reuse_probe_requested(void){return probe;}
#endif
static char global_asset_directory[2];
static struct {unsigned sgr,animate;int sx,sy;} enemyShot[1];
static int VGAScreen,spriteSheet8=8,spriteSheet12=12,registration;
static unsigned ordinary,registered,classic,legacy,begins,shadows,ends,blits,queries,lastbank,lastindex;
static bool resource_ok,mirrored;
static int tank_muzzle_draw(unsigned z,unsigned index){assert(!z&&index==enemyShot[0].sgr);++queries;return registration;}
static void blit_sprite2(int s,int x,int y,int bank,unsigned index){(void)s;(void)x;(void)y;++blits;lastbank=bank;lastindex=index;}
static void render_mirror_shadow_end(void){++shadows;}
static void render_mirror_entity_end(void){++ends;}
static void draw_tank147_muzzle_sprite2(int s,int x,int y,int bank){++registered;mirrored=resource_ok;blit_sprite2(s,x,y,bank,147);}
static void draw_enemy_shot_sprite2(int s,int x,int y,int bank,unsigned index){++ordinary;blit_sprite2(s,x,y,bank,index);}
static void enemy_reuse_shot_begin_draw(unsigned z){assert(!z);++begins;}
static void draw_enemy_reuse_shot_sprite2(int s,int x,int y,int bank,unsigned index,unsigned z,unsigned base){assert(!z&&base==index);++legacy;blit_sprite2(s,x,y,bank,index);}
static void clear(void){ordinary=registered=classic=legacy=begins=shadows=ends=blits=queries=lastbank=lastindex=0;mirrored=false;}
'''
 driver=r'''
int main(void){unsigned cases=0;
#if defined(ENEMY_REUSE_HD_PROTOTYPE) && ENEMY_REUSE_HD_PROTOTYPE && !defined(RENDER_MIRROR_DISABLED)
 const bool on=true;
#else
 const bool on=false;
#endif
 for(int reg=-1;reg<=1;reg++)for(unsigned root=0;root<2;root++)for(unsigned assets=0;assets<3;assets++)for(unsigned flags=0;flags<4;flags++)for(unsigned resource=0;resource<2;resource++){
  registration=reg;global_asset_directory[0]=root?'x':0;game_probe_assets=assets==0?NULL:assets==1?"":"missing";game_probe_enabled=flags==1;observe=flags==2;probe=flags==3;resource_ok=resource;enemyShot[0].sgr=147;enemyShot[0].animate=0;clear();
  bool allowed=root&&!assets&&(!on||flags==0);
#ifdef RENDER_MIRROR_DISABLED
  allowed=false;
#endif
assert(render_mirror_tank147_muzzle_lane()==allowed);route(0);
  assert(queries==1&&blits==1&&lastindex==147&&lastbank==8&&!legacy&&!begins);
  assert(registered==(allowed&&reg>0)&&ordinary==(!allowed||reg==0));assert(shadows==(allowed&&reg<0)&&ends==shadows);assert(mirrored==(allowed&&reg>0&&resource_ok));assert(registration==reg);++cases;
 }
 game_probe_assets=NULL;game_probe_enabled=observe=probe=false;global_asset_directory[0]='x';
 for(int reg=-1;reg<=1;reg++){registration=reg;enemyShot[0].sgr=647;clear();route(0);assert(queries==1&&blits==1&&lastindex==147&&lastbank==12&&!ordinary&&!registered&&!legacy&&!shadows&&!ends);++cases;}
 unsigned old[]={7,146,214,215,216,42};registration=0;
 for(unsigned i=0;i<6;i++){enemyShot[0].sgr=old[i];clear();route(0);assert(queries==1&&blits==1&&lastindex==old[i]&&lastbank==8&&!registered&&!shadows);assert(ordinary==(i<2)&&legacy==(on&&i>=2&&i<=4)&&begins==legacy);++cases;}
 assert(cases==153);puts("PASS Tank muzzle exact-source lane/dispatch: 153 cases; NOT legacy ON pixels or full gameplay");return 0;}
'''
 disabled='#define render_mirror_tank147_muzzle_lane() false'
 if (root/'src/render_mirror.h').read_text().count(disabled)!=1:raise ValueError('Changed disabled lane')
 lane='#ifdef RENDER_MIRROR_DISABLED\n'+disabled+'\n#else\n'+lane+'\n#endif\n'
 raw=(prefix+lane+'\nstatic void route(unsigned z){\n'+ex['route']+'\n}\n'+driver).encode()
 names=('src/tyrian2.c','src/entity_draw.c','src/render_mirror.c','src/render_mirror.h','src/enemy_tank_shared_policy.h','src/enemy_widget_sonic_policy.h','src/enemy_orb_protron_policy.h','src/enemy_reuse_observe.h','src/enemy_reuse_probe.h')
 return raw,{n:sha((root/n).read_bytes())for n in names}
