"""Finite preparation helpers only: no compiler, child process, or writes."""
from pathlib import Path
import hashlib,re,struct,types
OLD_IDS=(91,145,61,101,120,139,168,169,162,260,166,94,7,45,153,154,155)
NEW_IDS=(20,21,105,106,124,125)
IDS=OLD_IDS+(70,67)+NEW_IDS
ENEMY70_HELPER_SHA='8321138603c3bd07f798df1883b0b2037793495eb151037b1de030ddf6675986'
CANONICAL=dict(zip((70,67)+NEW_IDS,('eebd525dab58f0fc6708f4f3c7b15a88e67270be877ff250e93c4bb2a2aeb8de','96b975abbccf393464cf2444f72d63c8ad3f996d8cc5c153593ad16f476e30e0','328f9831389399fa7c8d623889732bbc1574dac458a30b97511e2d031dd7aed8','a8fbcb2952ec4a4b3f84388f1b410ec70648052cbaff35487d2ed930c9b5dc55','d12fde24b67f6b57ede3483e07a155b95cd5f538cf9f96c64e0d80fc2e0eba78','1a47b5701ecbdef673251cd1de7b975e42291cef29ab9a0bfd10f1c48facb2ba','b37e9664609365b53a250c0a711b6ae863ab55299904794051091b206aeef158','11ffdf82296ed985ec9534ba19a555eb22594c14e5fc92414531a47e36383752')))
PACKS=('valid',)+tuple(k+str(i)for i in NEW_IDS for k in ('missing','bad','header'))+('width20','density105')
TAIL=b'\n#include "widget_sonic_native_additions.c.inc"\nint main(int argc,char **argv)\n{\n if(argc>=2&&!strcmp(argv[1],"--widget-sonic"))return ws_main(argc,argv);\n return inherited_enemy70_dispatch(argc,argv);\n}\n'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def old_helper(root):
 p=Path(root)/'tests/enemy_vulcan70_native_validation.py';raw=p.read_bytes()
 if sha(raw)!=ENEMY70_HELPER_SHA:raise ValueError('Changed enemy70 helper')
 m=types.ModuleType('approved_enemy70');m.__file__=str(p);exec(compile(raw,str(p),'exec'),m.__dict__);return m
def source_bundle(root):
 sources,old=old_helper(root).source_bundle(root)
 return sources,outer_shim(old,root)
def outer_shim(raw,root):
 _,expected=old_helper(root).source_bundle(root)
 if raw!=expected or raw.count(b'int main(')!=1:raise ValueError('Changed old nine dispatches')
 return raw.replace(b'int main(',b'int inherited_enemy70_dispatch(',1)+TAIL
def reverse_shim(raw,root):
 if not raw.endswith(TAIL):raise ValueError('Changed tenth tail')
 body=raw[:-len(TAIL)]
 if body.count(b'int inherited_enemy70_dispatch(')!=1 or b'int main('in body:raise ValueError('Changed old dispatcher')
 old=body.replace(b'int inherited_enemy70_dispatch(',b'int main(',1)
 if old!=old_helper(root).source_bundle(root)[1]:raise ValueError('Changed inherited bytes')
 return old
def fixture_bytes(raw,index,leaf):
 if type(raw)is not bytes or len(raw)!=43036 or type(index)is not int or index not in IDS or leaf not in PACKS:raise ValueError('Invalid finite fixture')
 if leaf=='valid':return raw
 m=re.fullmatch(r'(missing|bad|header|width|density)([0-9]+)',leaf);kind,target=m.group(1),int(m.group(2))
 if index!=target:return raw
 if kind=='missing':return None
 b=bytearray(raw)
 if kind=='bad':b[128]^=1
 elif kind=='header':b[4]^=1
 else:struct.pack_into('<I',b,12 if kind=='width'else 8,11 if kind=='width'else 4)
 return bytes(b)
def fixture_payloads(hdas,pins,names):
 if any(set(d)!=set(IDS)for d in (hdas,pins,names)):raise ValueError('Exact old19 plus six required')
 for i in IDS:
  if type(i)is not int or type(hdas[i])is not bytes or sha(hdas[i])!=pins[i]:raise ValueError('Changed fixture bytes')
  p=Path(names[i])
  if p.is_absolute()or '..'in p.parts or not str(p).endswith('.hda'):raise ValueError('Invalid fixture path')
  if i in CANONICAL:
   if sha(hdas[i])!=CANONICAL[i]or str(p)!='content/'+CANONICAL[i]+'.hda':raise ValueError('Changed canonical bytes/path')
  elif p.name!=str(p):raise ValueError('Old flat path changed')
 if len(set(names.values()))!=25:raise ValueError('Duplicate paths')
 out={}
 for leaf in PACKS:
  for i in IDS:
   raw=fixture_bytes(hdas[i],i,leaf)
   if raw is not None:out['widget-sonic-packs/'+leaf+'/'+names[i]]=raw
 if len(out)!=519:raise ValueError('Fixture closure changed')
 return out
def native_input(base_stdin,hdt):
 if type(base_stdin)is bytes and len(base_stdin)==99142 and sha(base_stdin)=='e3925cbf2d0f005ddfaf9ad3329ad99ee8826b11cea97b191e0b6b3a69d56684':return base_stdin
 # No new source tables: the exact inherited player70 birth input is enough.
 if type(base_stdin)is not bytes or len(base_stdin)!=98980 or sha(base_stdin)!='723d7a7a431b202419c12cce25e7298c2db9e9c5d88ac42cb7dc95fe51fcb463' or type(hdt)is not bytes or sha(hdt)!='fde8506326e7bb0916b38c362e33bf8a8a5affa561206c021af7f65b4a17745b':raise ValueError('Unbound original input')
 start=21174+14;port=start+1638*80+7*82;out=base_stdin+hdt[start+227*80:start+228*80]+hdt[port:port+82]
 if sha(out)!='e3925cbf2d0f005ddfaf9ad3329ad99ee8826b11cea97b191e0b6b3a69d56684':raise ValueError('Changed old record/port')
 return out
CASE_INVENTORY={'current24_complete_oracles':24,'six_missing_other23_retained':6,'six_cold_corrupt':6,'six_used_cache_corrupt':6,'six_used_retired_corrupt':6,'six_identity_headers':6,'shared_geometry_headers':2,'family_used_unused_palette_precompose':4,'source_before_and_cache':2,'background_fourstages_recovery':4,'dense_adjacent_overlap':3,'sparse_final_fade_foreign_partial_fullcell':4,'root_epochs_player_lease':3,'clipping_xmas_density_unsupported_output':4,'all24_repeated_warm_identity_unused_old18_OFFintent':6}
assert sum(CASE_INVENTORY.values())==86
MACRO_ON_PIXEL_SCOPE='DEFERRED: ordinary objects are macro OFF; tiny proves routing/intent/proof transitions only'
SYNTAX_TUS=('src/render_mirror.c','src/tyrian2.c','src/entity_draw.c')
MACRO_SENSITIVE_OLD_OBJECTS=('asset_debug','backgrnd','config','destruct','enemy_reuse_identity','entity_draw','episodes','fonthand','game_menu','game_probe','mainint','menus','mouse','nortsong','nortvars','palette','picload','shots','sprite','tyrian2','varz','vga256d','video','xmas','opentyr-renamed','renderer-harness')
def function(raw,name):
 matches=list(re.finditer(r'^static (?:bool|void) '+re.escape(name)+r'\(',raw,re.M))
 if len(matches)!=1:raise ValueError('Function definition not unique '+name)
 start=matches[0].start();op=raw.index('{',start);depth=0
 for end in range(op,len(raw)):
  depth+=(raw[end]=='{')-(raw[end]=='}')
  if not depth:return raw[start:end+1]
 raise ValueError('Unclosed function')
def tiny_sources(root):
 """Exact production branch/functions + actual policy header. State-provider
 stubs are deliberate: NOT full private observation/probe session execution."""
 root=Path(root);game=(root/'src/tyrian2.c').read_text();shared=(root/'src/global_projectile91_mirror.inc').read_text();render=(root/'src/render_mirror.c').read_text()
 begin='\n#if defined(ENEMY_REUSE_HD_PROTOTYPE) && ENEMY_REUSE_HD_PROTOTYPE && !defined(RENDER_MIRROR_DISABLED)\n\t\t\t\t\t\t\tif ((widget_sonic_member_index(sprite)'
 if game.count(begin)!=1:raise ValueError('Production route context changed')
 start=game.index(begin);endmark='blit_sprite2(VGAScreen, enemyShot[z].sx, enemyShot[z].sy, spriteSheet8, sprite);';end=game.index(endmark,start)+len(endmark);route=game[start:end]
 guard=' if(widget_sonic_member_index(index)&&widget_sonic_legacy_intent())return false;'
 if render.count(guard)!=1:raise ValueError('Ordinary admission not unique')
 a=render.index(guard);b=render.index(' if(index==304)',a);admission=render[a:b]
 source=function(shared,'global_projectile91_source_matches');decline=function(shared,'global_projectile91_cache_decline');cache=function(shared,'global_projectile91_check_cache')
 memberline=re.findall(r'^static const unsigned global_projectile91_widget_sonic_members=.*?;',shared,re.M)
 if len(memberline)!=1:raise ValueError('Finite mask changed')
 resources=sorted(set(re.findall(r'\b([a-zA-Z0-9_]+_resource)\(',source)))
 macros='\n'.join('#define '+n+'(...) ((void *)1)'for n in resources)
 text=r'''#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "enemy_widget_sonic_policy.h"
bool game_probe_enabled;
static bool observe_requested,probe_requested;
#if defined(ENEMY_REUSE_HD_PROTOTYPE) && ENEMY_REUSE_HD_PROTOTYPE
bool enemy_reuse_observe_requested(void){return observe_requested;}
bool enemy_reuse_probe_requested(void){return probe_requested;}
#endif
static unsigned ordinary,legacy,classic,begins,blits;
static int VGAScreen,spriteSheet8;static struct {int sx,sy;unsigned sgr;} enemyShot[1];
#define enemy_reuse_shot_begin_draw(...) (++begins)
#define draw_enemy_reuse_shot_sprite2(...) (++legacy,++blits)
#define draw_enemy_shot_sprite2(...) (++ordinary,++blits)
#define blit_sprite2(...) (++classic,++blits)
static void route(unsigned sprite){unsigned z=0;(void)z;
'''+route+r'''
}
typedef int Sprite2_array;
static unsigned global_projectile91_used_members;
static bool ready,last_output_valid,have_fade_saved,global_projectile91_cached,global_projectile91_fault;
static int fade_mode;static unsigned global_projectile91_output_palette[256],rgb_palette[256];
static char global_asset_directory[2]="x";
#define projectile91_source(...) true
'''+macros+'\n'+memberline[0]+'\n'+source+'\n'+decline+r'''
static bool global_projectile91_cache_source_matches(void){return global_projectile91_source_matches(0);}
'''+cache+r'''
#define global_projectile91_observed_preflight() ((void)0)
#define global_projectile91_draw(...) 1
static bool ordinary_admission(unsigned index){
'''+admission+r'''
 return false;
}
int main(void){unsigned checks=0;unsigned ids[]={20,21,105,106,124,125};
 for(unsigned state=0;state<8;state++) {
  game_probe_enabled=state&1;observe_requested=state&2;probe_requested=state&4;
#if defined(ENEMY_REUSE_HD_PROTOTYPE) && ENEMY_REUSE_HD_PROTOTYPE
  bool old=state!=0;
#else
  bool old=false;
#endif
  assert(widget_sonic_legacy_intent()==old);checks++;
  for(unsigned i=0;i<6;i++){ordinary=legacy=classic=begins=blits=0;route(ids[i]);assert(blits==1&&ordinary==!old&&legacy==old&&begins==old&&!classic);assert(ordinary_admission(ids[i])==!old);checks+=2;}
  ordinary=legacy=classic=begins=blits=0;route(70);assert(blits==1&&ordinary==1&&!legacy&&!classic&&!begins);checks++;
  ordinary=legacy=classic=begins=blits=0;route(214);
#if defined(ENEMY_REUSE_HD_PROTOTYPE) && ENEMY_REUSE_HD_PROTOTYPE
  assert(legacy==1&&begins==1&&!ordinary&&!classic&&blits==1);
#else
  assert(classic==1&&!begins&&!ordinary&&!legacy&&blits==1);
#endif
  checks++;ordinary=legacy=classic=begins=blits=0;route(42);assert(classic==1&&blits==1&&!ordinary&&!legacy&&!begins);checks++;
  for(unsigned used=0;used<2;used++){global_projectile91_used_members=used?262144u:131072u;assert(global_projectile91_source_matches(0)==(!used||!old));ready=last_output_valid=have_fade_saved=global_projectile91_cached=true;fade_mode=1;global_projectile91_check_cache();assert(ready==(!used||!old)&&last_output_valid==ready&&global_projectile91_cached==ready);if(!ready)assert(!have_fade_saved&&!fade_mode);checks+=2;}
 }
 assert(checks==160);printf("PASS Widget Sonic exact-source routing intent: 160 checks; NOT full ON session/pixels\n");return 0;}
'''
 provenance={p:sha((root/p).read_bytes())for p in ('src/tyrian2.c','src/render_mirror.c','src/global_projectile91_mirror.inc','src/enemy_widget_sonic_policy.h')}
 return text.encode(),provenance
