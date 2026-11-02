"""Finite WARNING HUF preparation. No compiler/process/filesystem writes.
Production font/renderer/draw bodies are extracted verbatim. SDL presentation and
unrelated owner families are explicitly disabled test backends, not qualified.
Original game data is supplied by the caller; none is embedded or persisted.
"""
from pathlib import Path
import hashlib,re,types
ROOT=Path(__file__).resolve().parents[1]
BASE_C_SHA='b8797db9e6b8a753f0b02e67a0afb5b3b7f33f5b90c9dff905bfe9a186f1b2b0'
BASE_PY_SHA='942e733bfc9cef426882a38e4d326cffbce37c157d71ae79945b75696baa066c'
RAW_PINS={'tyrian.pic':'76fa51ba6878c886f67daa65cf6d19968615e4423822c9fe1dde797fc2f8d802','palette.dat':'f628396306805387f07f72c4ccf0fdee9ca84b8e70ae23ba4ec58ec5fb362da0','tyrian.shp':'80cae98e073be6d7f710495920b71497bb23f108ea6631d6faf352c4729474f0'}
FAMILIES=('gameplay_hud','gameplay_hud_components','gameplay_hud_meters','gameplay_hud_indicators','gameplay_hud_fixed_text','gameplay_hud_font')
RESOURCES=('gameplay-hud-v1.hda','gameplay-hud-components-v1.hda','gameplay-hud-meters-v2.hda','gameplay-hud-indicators-v1.hda','gameplay-hud-fixed-text-v1.hda','gameplay-hud-font-v1.hda')
CASE_INVENTORY={'brightness_0_to_7_at_4x_and_8x':16,'appear_absent_reappear_repeat':2,'final_same_index_pixel_rect_ordinary_fade':8,'invalid_source_palette_lease_density_and_protocol':12,'old_two_scenes_two_persistent_clear16_isolation':2,'reset_suspend':2,'missing_corrupt_HUF_isolated':2}
assert sum(CASE_INVENTORY.values())==44
SCOPE='Extracted actual HUF + six loaders + renderer lifecycle + actual JE_outText/hv blitter; SDL RAM/presentation stub, unrelated owners disabled. NOT real SDL/window/gameplay/owner interaction qualification.'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def base_module(root):
 p=Path(root)/'tests/shared_hud_reconstruction.py';raw=p.read_bytes()
 if sha(raw)!=BASE_PY_SHA:raise ValueError('Changed base adapter')
 m=types.ModuleType('shared_hud_approved');m.__file__=str(p);exec(compile(raw,str(p),'exec'),m.__dict__);return m

def extract(src,name):
 """Exact source slice, with one explicit conditional-body format exception.
 hud_reset's mutually exclusive #if branches share a closing brace; its unique
 column-zero terminator bounds the entire untouched function. No preprocessing.
 """
 pat=r'^(?:static (?:inline )?)?(?:const char \*|Sprite \*|Uint8|Uint32|unsigned(?: int)?|int|void|bool)\s*'+re.escape(name)+r'\([^\n]*\)\s*\{'
 matches=list(re.finditer(pat,src,re.M))
 if len(matches)!=1:raise ValueError('Nonunique/missing exact function '+name)
 m=matches[0]
 if name=='render_mirror_hud_reset':
  end=src.find('\n}\n',m.end())
  if end<0:raise ValueError('Missing reset terminator')
  body=src[m.start():end+3]
  if body.count('#else\n')!=1 or body.count('#endif\n')!=2:raise ValueError('Changed reset conditional boundary')
  return body
 depth=1;pos=m.end()
 while depth and pos<len(src):
  depth+=(src[pos]=='{')-(src[pos]=='}');pos+=1
 if depth:raise ValueError('Unclosed production body '+name)
 return src[m.start():pos]+'\n'

DISABLED=r'''
/* Explicit inactive-family backend. None of these stubs qualifies projectiles. */
/* Inactive layer families have no live pass, resources or borrowed geometry.
 * Actual !frame.live predicates return true; reset retires clear proof only.
 * Full source bodies are pinned in inactive_source_contract(), not qualified. */
static bool shapesy_clear_proof;
static void shapesy_frame_reset(void){shapesy_clear_proof=false;}
static void cyan_frame_reset(void){}
static void shapesy_shutdown(void){shapesy_frame_reset();}
static void cyan_shutdown(void){}
static bool shapesy_frame_check(void){return true;}
static bool cyan_frame_check(void){return true;}
static bool shapesy_present_geometry(SDL_Renderer *r,const SDL_Rect *d){return true;}
static bool cyan_present_geometry(SDL_Renderer *r,const SDL_Rect *d){return true;}
static void projectile91_shutdown(void){}
static bool global_talon_cached;
static bool global_projectile91_frame,global_projectile91_cached;
static bool global_projectile91_requested(void){return false;}
static bool global_projectile91_surface_matches(void){return true;}
static bool global_projectile91_final_surface_matches(void){return true;}
static bool global_projectile91_finish_proof(void){return true;}
static bool global_projectile91_compose(MirrorOutputKind k,int x,int y){return false;}
static bool global_projectile91_pixel(int x,int y,Uint8 b,Uint8 a,int s){return false;}
static void global_projectile91_shutdown(void){}
static void global_projectile91_frame_begin(void){global_projectile91_frame=global_projectile91_cached=false;}
static void global_projectile91_check_cache(void){}
static void global_projectile91_final_pixel(SDL_Surface*s,Uint8*p){}
static void global_projectile91_final_rect(SDL_Surface*s,const SDL_Rect*r){}
static void global_projectile91_pre_final_pixel(SDL_Surface*s,Uint8*p){}
static void global_projectile91_pre_final_rect(SDL_Surface*s,const SDL_Rect*r){}
static bool global_projectile91_fade_buffer_safe(void){return true;}
static bool global_projectile91_fade_capture(void){return true;}
static bool global_projectile91_fade_step_valid(int steps){return true;}
static void global_projectile91_fade_palette(void){}
'''
DRAW_STUBS=r'''
/* Other menu glyph observers disabled; WARNING follows actual game text/blit. */
#define settings_font_glyph_begin(...) ((void)0)
#define load_font_glyph_begin(...) ((void)0)
#define selector_font_glyph_begin(...) ((void)0)
#define pregame_font_glyph_begin(...) ((void)0)
#define common_pause_glyph_begin(...) ((void)0)
#define settings_font_glyph_end() ((void)0)
#define load_font_glyph_end() ((void)0)
#define selector_font_glyph_end() ((void)0)
#define pregame_font_glyph_end() ((void)0)
#define common_pause_glyph_end() ((void)0)
/* Positive-brightness WARNING never enters dark path; fail if it does. */
static void blit_sprite_dark(SDL_Surface*s,int x,int y,unsigned t,unsigned i,bool b){CHECK(false);}
'''
def source_bundle(root):
 root=Path(root);base=(root/'tests/shared_hud_reconstruction.c').read_bytes()
 if sha(base)!=BASE_C_SHA:raise ValueError('Changed shared harness')
 base_module(root);src=(root/'src/render_mirror.c').read_text()
 names=['asteroid1_level_scope','asteroid1_scope','normal15_scope','manual_hd_scope','mirror_enabled','render_mirror_owns_display','palette_rgb','upscale','render_mirror_unsupported','cloud_shadow_rgba','darken_rgba','indicator_cell','indicator_position','indicator_overlap']
 start=src.index('static bool fixed_text_owned(void)\n');end=src.index('void render_mirror_begin(void)',start)
 names+=re.findall(r'^(?:static )?(?:Uint32|unsigned(?: int)?|int|void|bool) (\w+)\([^\n]*\)\s*\{',src[start:end],re.M)
 names+=['render_mirror_begin','render_mirror_pixel','render_mirror_rect','normal15_disjoint','normal15_layout','normal15_palette','normal15_branch','normal15_index','normal15_channel','normal15_rgba','normal15_indices_match','normal15_compose','shared_hud_finish','render_mirror_finish','render_mirror_fade_start','render_mirror_fade_step','render_mirror_present','render_mirror_release_texture']
 names=list(dict.fromkeys(names));bodies={n:extract(src,n)for n in names}
 # Macro OFF production NEWSHF definitions, unchanged source rather than guessed stubs.
 marker='#define global_newshf_frame false\n';a=src.index(marker);z=src.index('#endif',a);off=src[a:z];a=src.index('#define enemy_reuse_shutdown()');z=src.index('#endif',a);off+=src[a:z];header=(root/'src/render_mirror.h').read_text();a=header.index('#define render_mirror_newshf_validation_reset(');z=header.index('#endif',a);off+=header[a:z]
 text=base.decode();needle='#include "gameplay_hud_font_mirror.inc"\n'
 if text.count(needle)!=1 or text.count('int main(')!=1:raise ValueError('Base insertion boundaries changed')
 text=text.replace(needle,DISABLED+off+'\n'+needle,1).replace('int main(','static int historical_hud_main_not_run(',1)
 spr=(root/'src/sprite.c').read_text();hdr=(root/'src/sprite.h').read_text();font=(root/'src/fonthand.c').read_text()
 draw={'sprite':extract(hdr,'sprite'),'sprite_exists':extract(hdr,'sprite_exists'),'blit_sprite_hv_unsafe':extract(spr,'blit_sprite_hv_unsafe'),'JE_outText':extract(font,'JE_outText')}
 text+='\n'+DRAW_STUBS+'\n'+''.join(draw.values())+'\n#include "warning_hud_native_additions.c.inc"\n'
 files={'warning-hud-wrapper.c':text.encode(),'production.inc':'\n'.join(bodies.values()).encode(),'shared_root.inc':(extract(src,'hud_asset_directory')+extract(src,'shared_hud_requested')).encode(),'gameplay_hud_font_mirror.inc':(root/'src/gameplay_hud_font_mirror.inc').read_bytes(),'warning_hud_native_additions.c.inc':(root/'tests/warning_hud_native_additions.c.inc').read_bytes()}
 for n in FAMILIES:
  for ext in('.c','.h'):files[n+ext]=(root/'src'/(n+ext)).read_bytes()
 provenance={'scope':SCOPE,'production_functions':{n:sha(v.encode())for n,v in bodies.items()},'actual_draw_functions':{n:sha(v.encode())for n,v in draw.items()},'source_files':{rel:sha((root/rel).read_bytes())for rel in ['src/render_mirror.c','src/render_mirror.h','src/tyrian2.c','src/fonthand.c','src/sprite.c','src/sprite.h','src/gameplay_hud_font_mirror.inc']},'base_harness':BASE_C_SHA,'base_adapter':BASE_PY_SHA,'setups':44,'compiler_macros':{'ENEMY_REUSE_HD_PROTOTYPE':0,'NEWSHF_HD_COMPOSITOR':0}}
 files['current_hud_payload_pins.h']=(root/'src/current_hud_payload_pins.h').read_bytes()
 provenance['quoted_include_closure']=quoted_include_closure(files)
 provenance['payload_pin_header_sha256']=sha(files['current_hud_payload_pins.h'])
 provenance['inactive_source_contract']=inactive_source_contract(root)
 provenance['symbol_inventory']=symbol_inventory(files)
 return files,provenance

def native_input(pic,palette,shapes,root=ROOT):
 values=dict(zip(RAW_PINS,(pic,palette,shapes)))
 for name,b in values.items():
  if type(b)is not bytes or sha(b)!=RAW_PINS[name]:raise ValueError('Wrong caller raw '+name)
 class Blob:
  def __init__(self,b):self.b=b
  def read_bytes(self):return self.b
 class Input:
  def __truediv__(self,name):return Blob(values[name])
 return base_module(root).original_payload(Input())

def fixture_plan(root):
 """Two HUF-only negatives; existing five resources referenced read-only, not copied."""
 root=Path(root)
 return {'resources':{n:sha((root/'assets/hd/shared-ui-v1'/n).read_bytes())for n in RESOURCES},'negative_roots':{'missing':{'omit':RESOURCES[-1]},'corrupt':{'replace':RESOURCES[-1],'bytes_hex':b'not HUF1'.hex()}},'scope':'five unchanged regular canonical inputs via reviewed links; no bitmap editing or historical all-suite'}


def inactive_source_contract(root):
 root=Path(root);result={}
 for prefix,rel in [('shapesy','src/shapesy_platform_mirror.inc'),('cyan','src/shapesy_cyan_layer2_mirror.inc')]:
  src=(root/rel).read_text();check=extract(src,prefix+'_frame_check');present=extract(src,prefix+'_present_geometry')
  if not re.search(r'if\s*\(!'+prefix+r'_frame\.live\)\s*return true;',check)or not re.search(r'if\s*\(!'+prefix+r'_frame\.live\)\s*return true;',present):raise ValueError('Changed inactive layer branch')
  result[rel]={'sha256':sha(src.encode()),'inactive_frame_check':sha(check.encode()),'inactive_present_geometry':sha(present.encode()),'scope':'Never live in this harness; no borrowed resource or layer qualification.'}
 rel='src/enemy_projectile91_mirror.inc';src=(root/rel).read_text();result[rel]={'sha256':sha(src.encode()),'shutdown':sha(extract(src,'projectile91_shutdown').encode()),'scope':'No projectile resources admitted by disabled backend.'}
 return result

# Deliberately finite macro-OFF lexical call closure, not a general C parser or
# substitute for actual compiler/depfile validation. New unresolved call fails.
C_LIBRARY_CALLS=frozenset('abort assert calloc exit fclose fgetc fopen fprintf fread free malloc memchr memcmp memcpy memset printf puts setvbuf snprintf strcmp strcpy strlen strstr UINT64_C'.split())
def _ordinary_off(text):
 lines=[];stack=[];enabled=True
 for line in text.splitlines(True):
  if line.startswith('#if '):
   expr=line[4:].strip()
   if expr not in ('defined(ENEMY_REUSE_HD_PROTOTYPE) && ENEMY_REUSE_HD_PROTOTYPE','defined(ENEMY_REUSE_HD_PROTOTYPE) && ENEMY_REUSE_HD_PROTOTYPE && !defined(RENDER_MIRROR_DISABLED)'):raise ValueError('Unknown finite conditional '+expr)
   stack.append(enabled);enabled=False
  elif line.startswith('#else'):
   if not stack:raise ValueError('Unexpected else')
   enabled=stack[-1]
  elif line.startswith('#endif'):
   if not stack:raise ValueError('Unexpected endif')
   enabled=stack.pop()
  elif enabled:lines.append(line)
 if stack:raise ValueError('Unclosed finite conditional')
 return ''.join(lines)
def symbol_inventory(files):
 names=('warning-hud-wrapper.c','production.inc','shared_root.inc','gameplay_hud_font_mirror.inc','warning_hud_native_additions.c.inc')
 text='\n'.join(_ordinary_off(files[n].decode())for n in names)
 # Headers carry ordinary declarations only; their include guards are not code.
 headers='\n'.join(files[n].decode()for n in files if n.endswith('.h'))
 text=re.sub(r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'', ' ',text,flags=re.S)
 headers=re.sub(r'/\*.*?\*/|//[^\n]*',' ',headers,flags=re.S)
 macros=set(re.findall(r'^#define\s+(\w+)',text,re.M))
 generated=set(re.findall(r'\b(?:NOOP|PIXEL2|PIXEL3|RECT)\((\w+)\)',text))-{'name','n'}
 text=re.sub(r'^#define[^\n]*','',text,flags=re.M)
 declarations=set(re.findall(r'^(?:[A-Za-z_]\w*[ \t*]+)+([A-Za-z_]\w*)\s*\([^(){};]*\)\s*(?:\{|;)',text+'\n'+headers,re.M))
 calls=set(re.findall(r'\b([A-Za-z_]\w*)\s*\(',text))
 keywords={'if','for','while','switch','sizeof','return','Uint8'}
 missing=calls-declarations-macros-generated-keywords-C_LIBRARY_CALLS
 if missing:raise ValueError('Unbound finite C calls: '+','.join(sorted(missing)))
 if 'static bool shapesy_clear_proof;'not in text:raise ValueError('Missing finite bool storage shapesy_clear_proof')
 return {'calls':sorted(calls-keywords),'declared_functions':sorted(declarations),'macros':sorted(macros),'macro_generated_functions':sorted(generated),'c_library_allowlist':sorted(C_LIBRARY_CALLS),'unresolved':[],'finite_storage':['shapesy_clear_proof'],'scope':'Lexical completeness guard for this exact OFF harness; compiler still mandatory.'}


def quoted_include_closure(files):
 """Finite generated-file graph, independently of the main-TU call inventory.
 Checks every quote include, even unreachable input; recursively walks seven C
 roots. Angle system headers remain the actual compiler/depfile gate's scope.
 """
 if type(files)is not dict:raise ValueError('Generated map required')
 edges={};angles=set()
 for name,raw in files.items():
  if type(name)is not str or Path(name).name!=name or Path(name).suffix not in('.c','.h','.inc')or type(raw)is not bytes:raise ValueError('Invalid generated member')
  text=raw.decode();edges[name]=[]
  for line in text.splitlines():
   if not re.match(r'^\s*#\s*include\b',line):continue
   m=re.fullmatch(r'\s*#\s*include\s*(["<])([^">]+)[">]\s*(?://.*|/\*.*\*/\s*)?',line)
   if not m:raise ValueError('Unsupported include directive in '+name)
   target=m[2]
   if m[1]=='<':angles.add(target);continue
   if Path(target).name!=target or target not in files:raise ValueError('Unbound quote include '+name+' -> '+target)
   edges[name].append(target)
 roots=sorted(n for n in files if n.endswith('.c'));seen=set()
 def walk(name):
  if name in seen:return
  seen.add(name)
  for target in edges[name]:walk(target)
 for name in roots:walk(name)
 if seen!=set(files):raise ValueError('Unreachable generated members: '+','.join(sorted(set(files)-seen)))
 return {'roots':roots,'quoted_edges':{n:edges[n]for n in sorted(edges)},'all_reachable':sorted(seen),'system_angle_headers':sorted(angles),'scope':'Exact finite quote closure; real compiler headers/conditional dependencies still separately verified.'}
