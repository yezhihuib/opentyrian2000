#!/usr/bin/env python3
"""Bounded Talon lifecycle controls with a verified external original source bank.

Production source checks, pinned HDA loading, Talon draw, pixel, reset and finish
execute in an SDL structure shim. No RGB, owner or contributed state is seeded.
Original bank bytes pass through stdin in memory and are never saved. Palette
pins come from the registry; other palette entries are synthetic grayscale.
This is not native-caller, game-runtime or whole-level proof.
Existing cc is required. Generated artifacts are automatically removed.
"""
from pathlib import Path
import argparse
import atexit
import hashlib
import json
import os
import re
import shlex
import subprocess
import struct
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
default_repo = Path(__file__).resolve().parent.parent / 'opentyrian-render-audit'
if (Path(__file__).resolve().parent.parent / 'src/render_mirror.c').exists():
    default_repo = Path(__file__).resolve().parent.parent
parser.add_argument('--repo', type=Path, default=default_repo)
parser.add_argument('--source-ref', help='Git ref; baseline selects requested audit commit. Omit for saved working-tree sources.')
parser.add_argument('--expect-baseline-defects', action='store_true')
parser.add_argument('--msvc', type=Path, help='Existing cl.exe; run from an initialized MSVC x64 environment. Uses ASan without UBSan.')
parser.add_argument('--source-shp', type=Path, required=True, help='Read-only external Tyrian 2000 tyrian.shp; original data is never copied or saved.')
parser.add_argument('--talon-assets', type=Path, help='Existing public Talon HDA root; defaults to assets/hd/global-assets-v1 in --repo.')
parser.add_argument('--receipt', type=Path, required=True)
args = parser.parse_args()
ROOT = args.repo.resolve()
ref = '775b6b77163723c6cae727bafce1d53746a5bd60' if args.source_ref == 'baseline' else args.source_ref
asset_root = (args.talon_assets or ROOT / 'assets/hd/global-assets-v1').resolve()
# Same little-endian offset table used by JE_loadMainShapeTables; do not save
# the original container or bank to a fixture, receipt, or generated C source.
container = args.source_shp.read_bytes()
container_sha = hashlib.sha256(container).hexdigest()
if len(container) != 505983 or container_sha != '80cae98e073be6d7f710495920b71497bb23f108ea6631d6faf352c4729474f0':
    parser.error('Original container size/SHA256 mismatch')
count, = struct.unpack_from('<H', container)
if count < 10 or 2 + 4 * count > len(container):
    parser.error('Invalid shape offset table')
offsets = struct.unpack_from('<' + 'i' * count, container, 2)
start, stop = offsets[8:10]
if (start, stop) != (382486, 415970):
    parser.error('Unexpected spriteSheet9 interval')
source_bank = container[start:stop]
del container
bank_sha = hashlib.sha256(source_bank).hexdigest()
if len(source_bank) != 33484 or bank_sha != '6e783ccf58eb55a4fad82cd1fb600968e1397f297d30398ac935c7f81dfd9cff':
    parser.error('Original bank size/SHA256 mismatch')
temporary = tempfile.TemporaryDirectory(prefix='talon-lifecycle-')
atexit.register(temporary.cleanup)
BASE = Path(temporary.name)
files = ['src/render_mirror.c', 'src/sprite.c', 'src/global_talon_mirror.inc',
         'src/global_asset_registry.h', 'src/shared_asset_reader.h', 'tests/global_talon_reconstruction.c']
snapshot = {}
for name in files:
    snapshot[name] = (subprocess.run(['git', '-C', str(ROOT), 'show', ref + ':' + name],
                     check=True, capture_output=True, timeout=30).stdout if ref else (ROOT / name).read_bytes())
for name in ['src/global_asset_registry.h', 'src/shared_asset_reader.h']:
    (BASE / Path(name).name).write_bytes(snapshot[name])

def extract(source, name):
    match = re.search(r'^[A-Za-z_][^\n;{}]*\b' + re.escape(name) + r'\([^;{}]*\)\s*\{', source, re.M)
    assert match, name
    pos = source.index('{', match.start()) + 1
    depth = 1
    while depth:
        depth += (source[pos] == '{') - (source[pos] == '}')
        pos += 1
    return source[match.start():pos] + '\n'

mirror = snapshot['src/render_mirror.c'].decode()
native = snapshot['src/sprite.c'].decode()
test = snapshot['tests/global_talon_reconstruction.c'].decode()
talon = snapshot['src/global_talon_mirror.inc'].decode()
names = ['palette_rgb', 'blend_rgba', 'darken_rgba', 'decode_tile', 'upscale', 'cloud_shadow_rgba',
         'normal15_palette', 'normal15_branch', 'normal15_index', 'normal15_channel', 'normal15_rgba', 'normal15_indices_match']
(BASE / 'primitives.inc').write_text('\n'.join(extract(mirror, name) for name in names))
for out, name in [('pixel.inc', 'render_mirror_pixel'), ('root.inc', 'render_mirror_set_global_assets'),
                  ('blend.inc', 'render_mirror_sprite2_blend_pixel'), ('finish.inc', 'render_mirror_finish')]:
    (BASE / out).write_text(extract(mirror, name))
(BASE / 'blitter.inc').write_text(extract(native, 'blit_sprite2_blend'))
(BASE / 'global_talon_mirror.inc').write_bytes(snapshot['src/global_talon_mirror.inc'])
prefix = test[:test.index('static void finish_layout_guard(void)')]
prefix = prefix.replace('typedef struct {SDL_Rect rect;bool live;} HdRegion;',
                        'typedef struct {SDL_Rect rect;int bank,index,style;bool live;} HdRegion;')
constants = re.search(r'enum \{ ASSET_NEWSH2=.*?\};', mirror).group(0)
draw_prelude = constants + r'''
typedef int G101Record;typedef int PCapRecord;typedef int Forest13Record;typedef int GreenBackground;
static Asset *pulsing272_draw_lease,*triple275_draw_lease,*columns276_draw_lease,*turret273_draw_lease,*projectile304_draw_lease,*firing270_draw_lease,*firing285_draw_lease,*enemy_orb112113_draw_lease,*terrain144_draw_lease;
typedef struct {Asset *asset;int x,y;} GreenHead;
static GreenHead green_heads[256];static unsigned green_head_count;
#define cloud_asset(a) false
#define explosion_asset_slot(i) (-1)
#define green_background_snapshot(...) ((void)0)
#define green_background_peak(...) 0
#define ground101_select(...) CHECK(false)
#define plateau_cap_select(...) CHECK(false)
#define forest13_select(...) CHECK(false)
#define enemy_filter_rgba(...) CHECK(false)
#define explosion_asset_blend_rgba(...) CHECK(false)
#define green_head_composite(...) 0
'''
prefix += draw_prelude + extract(mirror, 'draw_asset_filtered')
prefix += '#define CHECK_CONTRIBUTED() CHECK(global_talon_contributed)\n' if 'global_talon_contributed' in talon else '#define CHECK_CONTRIBUTED() ((void)0) /* Field absent in baseline. */\n'
prefix += '#define CHECK_FINISH_PROOF() CHECK(global_talon_finish_proof())\n' if 'global_talon_finish_proof' in talon else '#define CHECK_FINISH_PROOF() ((void)0) /* Proof absent in baseline. */\n'
main = r'''
#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#endif
int main(int argc,char **argv)
{
 CHECK(argc==5);bool baseline=atoi(argv[2])!=0;int density=atoi(argv[3]);
 bool empty=!strcmp(argv[1],"reset-no-contribution");
 bool owned=!strcmp(argv[1],"talon-valid-owned"),transferred_positive=!strcmp(argv[1],"talon-valid-transferred");
 bool positive=empty||owned||transferred_positive;
#ifdef _WIN32
 CHECK(_setmode(_fileno(stdin),_O_BINARY)!=-1);
#endif
#ifdef _MSC_VER
 _set_abort_behavior(0,_WRITE_ABORT_MSG|_CALL_REPORTFAULT);
#endif
 Uint8 *prior_bank=malloc(GLOBAL_TALON_BANK_BYTES),*replacement=NULL;CHECK(prior_bank);
 read_exact(prior_bank,GLOBAL_TALON_BANK_BYTES);CHECK(fgetc(stdin)==EOF);
 spriteSheet9=(Sprite2_array){GLOBAL_TALON_BANK_BYTES,prior_bank};
 Sprite2_array admitted_bank=spriteSheet9;
 /* Only the finite required palette pins are real registry values. The rest
  * is an explicit fixture underlay, not a claimed original game palette. */
 for(unsigned i=0;i<256;i++)normal_palette[i]=i*0x010101u;
 for(unsigned i=0;i<COUNTOF(global_talon_palette);i++)
  normal_palette[global_talon_palette[i].index]=global_talon_palette[i].rgb;
 initialize_surfaces(density);
 CHECK(strlen(argv[4])<sizeof(global_asset_directory));strcpy(global_asset_directory,argv[4]);
 /* Bind and qualify the real source before frame_begin and before every
  * later invalidation. The included production validator is never stubbed. */
 CHECK(global_talon_source_matches(spriteSheet9));CHECK(global_talon_palette_matches());
 active=true;global_talon_frame_begin();CHECK(global_talon_frame);
 memcpy(initial_palette,rgb_palette,sizeof(initial_palette));
 int ox=95,oy=73,x=ox,y=oy,d=game_probe_density;
 if(!empty) {
  mirror_logic_tick=1;global_talon_pose(1,spriteSheet9,233,233,0);
  CHECK(global_talon_poses[0].valid);
  CHECK(render_mirror_global_player_ship(game_screen,ox,oy,spriteSheet9,233,MIRROR_NORMAL,1,233)==1);
  CHECK(global_talon_loaded&&global_talon_good&&asset_opens==13);
  /* Existing independent quad walker supplies original INDEX8 callbacks;
   * it is not the full engine's native caller. */
  finish_draw(ox,oy,233,MIRROR_NORMAL);CHECK_CONTRIBUTED();
  bool found=false;
  for(int yy=0;yy<28&&!found;yy++)for(int xx=0;xx<24&&!found;xx++) {
   size_t n=(size_t)((oy+yy)*d)*canvas->w+(ox+xx)*d;
   if(global_talon_owner[n]&&*rgba_at((ox+xx)*d,(oy+yy)*d)!=palette_rgb(*index_at(ox+xx,oy+yy)))
    {x=ox+xx;y=oy+yy;found=true;}
  }
  CHECK(found);
 }
 Uint8 *at=index_at(x,y);Uint8 before=*at;Uint32 talon_rgb=*rgba_at(x*d,y*d);
 /* A later generic HD entity composites semi-transparent pixels and its
  * INDEX8 callbacks transfer ALL Talon ownership through production pixel(). */
 if(!owned) {
  Uint8 semi[24*28*4];for(unsigned i=0;i<24*28;i++)memcpy(semi+4*i,(Uint8[]){0,255,0,128},4);
  Asset later={true,true,8,1,24,28,0,0,1,semi};
  CHECK(draw_asset_filtered(ox,oy,&later,MIRROR_NORMAL,NULL,0,NULL,NULL,NULL));CHECK(suppress);
  for(int yy=0;yy<28;yy++)for(int xx=0;xx<24;xx++) {
   Uint8 *pixel=index_at(ox+xx,oy+yy);*pixel=0x73;render_mirror_pixel(game_screen,pixel,*pixel,MIRROR_NORMAL);
  }
  suppress=false;CHECK(!memchr(global_talon_owner,1,global_talon_capacity));
  CHECK(*rgba_at(x*d,y*d)==reference_blend(talon_rgb,(Uint8[]){0,255,0,128},128));
  if(!empty)CHECK(*rgba_at(x*d,y*d)!=reference_blend(palette_rgb(before),(Uint8[]){0,255,0,128},128));
 }
 CHECK(hd_owner[(size_t)(y*d)*canvas->w+x*d]);
 Uint32 transferred=*rgba_at(x*d,y*d);
 map_final_indices();
 CHECK(global_talon_source_matches(admitted_bank));CHECK(global_talon_source_matches(spriteSheet9));
 CHECK(global_talon_palette_matches()&&global_talon_underlay_matches());
 CHECK(global_talon_surface_matches()&&global_talon_final_surface_matches());CHECK_FINISH_PROOF();
 bool do_reset=!strcmp(argv[1],"reset")||empty;
 if(do_reset)global_talon_reset();
 else if(!strcmp(argv[1],"source-absent"))spriteSheet9=(Sprite2_array){0,NULL};
 /* Replacement deliberately has invalid contents as in the original control.
  * This does not assert that an identical qualified clone must be rejected. */
 else if(!strcmp(argv[1],"source-pointer-replaced")) {replacement=calloc(GLOBAL_TALON_BANK_BYTES,1);CHECK(replacement);spriteSheet9=(Sprite2_array){GLOBAL_TALON_BANK_BYTES,replacement};}
 else if(!strcmp(argv[1],"source-length-changed"))spriteSheet9.size--;
 else if(owned||transferred_positive) {CHECK(global_talon_source_matches(spriteSheet9));CHECK_FINISH_PROOF();}
 else CHECK(false);
 bool source_valid_after=global_talon_source_matches(spriteSheet9);
 if(!positive&&!do_reset){CHECK(!source_valid_after);CHECK(!global_talon_source_matches(admitted_bank));}
 bool active_after_reset=active;
 if(active){finish_allow_upscale=true;render_mirror_finish(MIRROR_OUTPUT_ORDINARY,0,0);finish_allow_upscale=false;}
 Uint32 result=((Uint32 *)((Uint8 *)output->pixels+(y*d)*output->pitch))[(x-24)*d];
 printf("mode=%s density=%d source_valid_before=1 palette_valid_before=1 source_valid_after=%d talon_drawn=%d all_owners_transferred=%d resource_opens=%u transferred=%08x output=%08x classic=%08x active_after_reset=%d ready=%d retained=%d\n",
  argv[1],d,source_valid_after,!empty,!owned,asset_opens,transferred,result,palette_rgb(*at),active_after_reset,ready,last_output_valid);
 if(positive){CHECK(active_after_reset);CHECK(ready);CHECK(last_output_valid);CHECK(result==transferred);if(!empty)CHECK(result!=palette_rgb(*at));}
 else if(baseline){CHECK(active_after_reset);CHECK(last_output_valid);CHECK(result==transferred);CHECK(result!=palette_rgb(*at));}
 else {CHECK(!ready);CHECK(!last_output_valid);CHECK(!have_fade_saved);if(do_reset)CHECK(!active_after_reset);}
 global_talon_shutdown();free(prior_bank);free(replacement);
 return 0;
}
'''
(BASE / 'talon_transfer_probe.c').write_text(prefix + main)
executable = BASE / ('talon_transfer_probe.exe' if os.name == 'nt' else 'talon_transfer_probe')
command = ([str(args.msvc), '/nologo', '/std:c11', '/Od', '/Zi', '/W3',
            '/D_CRT_SECURE_NO_WARNINGS', '/fsanitize=address', '/I' + str(BASE),
            str(BASE / 'talon_transfer_probe.c'), '/Fe:' + str(executable)] if args.msvc else
           shlex.split(os.environ.get('CC', 'cc')) + ['-std=c99', '-O1', '-g', '-Wall', '-Wextra', '-Werror=implicit-function-declaration', '-Wno-unused-function',
           '-Wno-unused-parameter', '-Wno-unused-variable', '-Wno-misleading-indentation', '-I' + str(BASE),
           '-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-no-pie',
           str(BASE / 'talon_transfer_probe.c'), '-o', str(executable)])
build = subprocess.run(command, capture_output=True, timeout=60, cwd=BASE)
if build.returncode:
    print(build.stdout.decode(errors='replace'), end='')
    print(build.stderr.decode(), end='')
    raise SystemExit(build.returncode)
outputs = []
for density in [4,8]:
    for mode in ['reset', 'source-absent', 'source-pointer-replaced', 'source-length-changed', 'reset-no-contribution', 'talon-valid-owned', 'talon-valid-transferred']:
        result = subprocess.run([str(executable), mode, str(int(args.expect_baseline_defects)), str(density), str(asset_root)], capture_output=True, input=source_bank,
                                env={**os.environ, 'ASAN_OPTIONS':'detect_leaks=0:halt_on_error=1', 'UBSAN_OPTIONS':'halt_on_error=1:print_stacktrace=1'}, timeout=30)
        outputs.append({'case':mode, 'density':density, 'returncode':result.returncode, 'stdout':result.stdout.decode(), 'stderr':result.stderr.decode()})
        print(outputs[-1]['stdout'], end='');print(outputs[-1]['stderr'], end='')
status = 'FAIL' if any(item['returncode'] for item in outputs) else 'BASELINE_DEFECT_REPRODUCED' if args.expect_baseline_defects else 'PASS'
temporary.cleanup()
receipt = args.receipt.resolve();receipt.parent.mkdir(parents=True, exist_ok=True)
receipt.write_text(json.dumps({
    'status':status,'source_ref':ref or 'saved-working-tree',
    'scope':'Bounded original-bank qualification and pinned HDA loading with exact production Talon/generic draw, pixel, reset and finish; SDL structure shim; not native caller/game/whole-level proof',
    'seed':'No seeded RGB/owner/contributed. Registry-required palette pins plus synthetic grayscale underlay; original INDEX8 callbacks use the existing independent quad walker.',
    'source_input':{'container_bytes':505983,'container_sha256':container_sha,'bank_interval':[start,stop],'bank_bytes':len(source_bank),'bank_sha256':bank_sha,'raw_bytes_saved':False},
    'preconditions':'Every case asserts the unmodified production source validator before frame_begin and before invalidation; all 20 registry tile hashes checked. Production HDA loader checks all 13 resource headers/payload pins for each actual Talon draw.',
    'pointer_control':'Valid original source -> new pointer with intentionally unqualified zero bytes; not rejection of a byte-identical qualified clone.',
    'sanitizers':'MSVC ASan (UBSan unavailable)' if args.msvc else 'ASan+UBSan',
    'leak_detection':'unavailable in MSVC ASan' if args.msvc else 'disabled for executor ptrace compatibility',
    'original_game_data_accessed':True,'profiles_accessed':False,
    'temporary_artifacts_automatically_removed':True,
    'compile_command':command,'compile_stdout':build.stdout.decode(errors='replace'),
    'compile_stderr':build.stderr.decode(errors='replace'),'cases':outputs,
    'production_sha256':{name:hashlib.sha256(content).hexdigest() for name,content in snapshot.items()}
}, indent=2)+'\n')
raise SystemExit(0 if status != 'FAIL' else 1)
