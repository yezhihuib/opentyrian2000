#!/usr/bin/env python3
"""Bounded extracted-production asteroid scope, loader and source tests.

Only explicit source/art files and the three named external original resources
are read. No other tests, repository payloads or private projection are imported.
The full game is not launched by this source harness.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import resource
import shutil
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / 'assets/hd/packs/asteroid1-ten-v1'


def extract(source, name):
    m = re.search(r'^[A-Za-z_][^\n;{}]*\b' + re.escape(name) + r'\([^;{}]*\)\s*\{', source, re.M)
    assert m, name
    end = source.index('{', m.start()) + 1
    depth = 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[m.start():end] + '\n'


HARNESS = r'''
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <limits.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include "sprite.h"
#include "episodes.h"
#include "ground101_material.h"
#include "plateau_cap_material.h"
#include "forest13_material.h"
#define REAR_OPEN(p) open(p,O_RDONLY|O_NONBLOCK)
#define REAR_READ read
#define REAR_CLOSE close
#define REAR_FSTAT fstat
#define REAR_STAT struct stat
#define REAR_REGULAR(m) S_ISREG(m)
#define ASSET_ASTEROID1 108
#define MIRROR_NORMAL 0
#define SA_NONE 0
JE_EnemyDatType enemyDat;
JE_byte episodeNum=1;
static int lvlFileNum=1,superArcadeMode;
static bool xmas,isNetworkGame,twoPlayerMode,galagaMode,twoPlayerLinked,record_demo;
bool bonusLevel;
static bool onePlayerAction,superTyrian,timedBattleMode,normalBonusLevelCurrent,bonusLevelCurrent;
static bool asteroid_hd_enabled=true,game_probe_enabled,play_demo,asteroid_hd_lease=true;
static bool game_probe_missing,game_probe_invalid,game_probe_original_reference,active=true;
static int game_probe_density=8;
static unsigned game_probe_scene_assets=1;
static const char *game_probe_assets,*reject_reason;
static uint64_t mirror_logic_tick=1;
Sprite2_array enemySpriteSheets[4],spriteSheet8;
Uint8 enemySpriteSheetIds[4];
typedef struct {bool initialized,valid;int bank,index,w,h,anchor_x,anchor_y,density;Uint8 *rgba;} Asset;
static SDL_PixelFormat format={.format=SDL_PIXELFORMAT_INDEX8,.BitsPerPixel=8,.BytesPerPixel=1};
static Uint8 pixels[320*200];
static SDL_Surface surface={.format=&format,.w=320,.h=200,.pitch=320,.pixels=pixels};
static SDL_Surface *game_screen=&surface,*VGAScreen=&surface;
static unsigned accepted,rejected,logged;static int last_x,last_y,last_part_x,last_part_y;static Uint8 last_filter;
static bool draw_asset_filtered(int x,int y,Asset *a,int style,const SDL_Rect *part,Uint8 filter,const G101Record *m,const PCapRecord *p,const Forest13Record *f)
{
 assert(a&&a->bank==108&&a->rgba&&a->density==8&&style==0&&!m&&!p&&!f);
 accepted++;last_x=x;last_y=y;last_part_x=part?part->x:0;last_part_y=part?part->y:0;last_filter=filter;return true;
}
static void game_probe_scene_draw(int role,unsigned base,int x,int y,int part,int style,bool mirrored)
{(void)base;(void)x;(void)y;(void)part;(void)style;assert(role==108&&mirrored);logged++;}
static void render_mirror_unsupported(const char *reason){reject_reason=reason;rejected++;}
@SCOPE@
@FAMILY@
static unsigned word(const Uint8 *b){return b[0]|((unsigned)b[1]<<8);}
static void records(const char *path)
{
 FILE *f=fopen(path,"rb");assert(f);
 for(unsigned t=444;t<=453;t++) {
  Uint8 b[77];assert(fread(b,1,77,f)==77);unsigned p=0;
#define BYTE(v) do {enemyDat[t].v=b[p++];} while(0)
#define SBYTE(v) do {enemyDat[t].v=(int8_t)b[p++];} while(0)
#define WORD(v) do {enemyDat[t].v=word(b+p);p+=2;} while(0)
#define SWORD(v) do {enemyDat[t].v=(int16_t)word(b+p);p+=2;} while(0)
  BYTE(ani);for(unsigned i=0;i<3;i++)BYTE(tur[i]);for(unsigned i=0;i<3;i++)BYTE(freq[i]);
  SBYTE(xmove);SBYTE(ymove);SBYTE(xaccel);SBYTE(yaccel);SBYTE(xcaccel);SBYTE(ycaccel);
  SWORD(startx);SWORD(starty);SBYTE(startxc);SBYTE(startyc);BYTE(armor);BYTE(esize);
  for(unsigned i=0;i<20;i++)WORD(egraphic[i]);BYTE(explosiontype);BYTE(animate);BYTE(shapebank);
  SBYTE(xrev);SBYTE(yrev);WORD(dgr);SBYTE(dlevel);SBYTE(dani);BYTE(elaunchfreq);WORD(elaunchtype);SWORD(value);WORD(eenemydie);assert(p==77);
#undef BYTE
#undef SBYTE
#undef WORD
#undef SWORD
 }
 assert(fgetc(f)==EOF);fclose(f);
}
int main(int argc,char **argv)
{
 assert(argc==5);game_probe_assets=argv[3];records(argv[2]);
 FILE *f=fopen(argv[1],"rb");assert(f);Uint8 *bank=malloc(42012);assert(bank&&fread(bank,1,42012,f)==42012&&fgetc(f)==EOF);fclose(f);
 enemySpriteSheets[0]=(Sprite2_array){42012,bank};enemySpriteSheetIds[0]=8;Sprite2_array source=enemySpriteSheets[0];
 assert(asteroid1_source(source)&&asteroid1_scope());
 bool *excluded[]={&xmas,&isNetworkGame,&twoPlayerMode,&galagaMode,&twoPlayerLinked,&record_demo,&onePlayerAction,&superTyrian,&timedBattleMode,&bonusLevel,&normalBonusLevelCurrent,&bonusLevelCurrent,&play_demo,&game_probe_enabled};
 for(unsigned i=0;i<sizeof(excluded)/sizeof(*excluded);i++){*excluded[i]=true;assert(!asteroid1_scope());*excluded[i]=false;}
 lvlFileNum=2;assert(!asteroid1_scope());lvlFileNum=9;assert(!asteroid1_scope());lvlFileNum=15;assert(!asteroid1_scope());lvlFileNum=1;episodeNum=2;assert(!asteroid1_scope());episodeNum=1;
 G101EnemyContext c={444,0,0,0,false,false,false,true};
 if(strcmp(argv[4],"reject")==0){assert(!asteroid1_draw(&surface,100,80,source,31,0,0,&c));assert(!accepted&&!rejected);asteroid1_shutdown();free(bank);return 0;}
 assert(asteroid1_family_ready());
 for(unsigned k=0;k<10;k++) {
  c.type=asteroid1_pins[k].type;c.size=asteroid1_pins[k].size;unsigned base=asteroid1_pins[k].base;
  const int parts[]={0,1,19,20};unsigned count=c.size?4:1;
  for(unsigned p=0;p<count;p++) {
   int part=parts[p],px=part==1||part==20?12:0,py=part==19||part==20?14:0;
   assert(asteroid1_draw(&surface,100,80,source,base,part,17,&c));
   assert(last_x==100-px&&last_y==80-py&&last_part_x==px&&last_part_y==py&&last_filter==17);
  }
 }
 assert(accepted==28&&logged==28);
 c=(G101EnemyContext){444,0,0,0,false,false,false,true};
 const int badx[]={INT_MIN,-1,309,INT_MAX},bady[]={INT_MIN,-14,200,INT_MAX};
 for(unsigned i=0;i<4;i++){assert(!asteroid1_draw(&surface,badx[i],80,source,31,0,0,&c));assert(!asteroid1_draw(&surface,100,bady[i],source,31,0,0,&c));}
 assert(!asteroid1_draw(&surface,100,80,source,31,1,0,&c));
 assert(!asteroid1_draw(&surface,100,80,source,32,0,0,&c));
 c.type=443;assert(!asteroid1_draw(&surface,100,80,source,31,0,0,&c));c.type=444;
 c.size=1;assert(!asteroid1_draw(&surface,100,80,source,31,0,0,&c));c.size=0;
 c.availability=1;assert(!asteroid1_draw(&surface,100,80,source,31,0,0,&c));c.availability=0;
 c.static_animation=false;assert(!asteroid1_draw(&surface,100,80,source,31,0,0,&c));c.static_animation=true;
 c.score_item=true;assert(!asteroid1_draw(&surface,100,80,source,31,0,0,&c));c.score_item=false;
 c.damaged=true;assert(!asteroid1_draw(&surface,100,80,source,31,0,0,&c));c.damaged=false;
 lvlFileNum=2;assert(!asteroid1_draw(&surface,100,80,source,31,0,0,&c));lvlFileNum=1;
 asteroid_hd_lease=false;assert(!asteroid1_draw(&surface,100,80,source,31,0,0,&c));asteroid_hd_lease=true;
 enemySpriteSheetIds[0]=1;assert(!asteroid1_source(source));enemySpriteSheetIds[0]=8;
 spriteSheet8=source;assert(!asteroid1_source(source));memset(&spriteSheet8,0,sizeof(spriteSheet8));
 enemyDat[444].egraphic[19]=99;assert(!asteroid1_source(source));enemyDat[444].egraphic[19]=0;
 bank[200]^=1;assert(!asteroid1_draw(&surface,100,80,source,31,0,0,&c));assert(rejected==1);bank[200]^=1;reject_reason=NULL;
 /* Warm foreign root and unsupported density must decline before cached art. */
 const char *root=game_probe_assets;game_probe_assets="/foreign-asteroid-root";assert(!asteroid1_family_ready());game_probe_assets=root;
 game_probe_density=4;assert(!asteroid1_family_ready());game_probe_density=8;
 /* Private immutable payload guard is refreshed before the first next-tick call. */
 mirror_logic_tick++;asteroid1_resources.member[3].rgba[10]^=1;assert(!asteroid1_family_ready());asteroid1_resources.member[3].rgba[10]^=1;assert(!asteroid1_family_ready());
 asteroid1_shutdown();assert(asteroid1_family_ready());
 asteroid1_shutdown();free(bank);puts("asteroid scope/source/loader/28-call geometry passed");return 0;
}
'''


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--sdl-include', action='append', default=[])
    p.add_argument('--sanitize', action='store_true')
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    source = (ROOT / 'src/render_mirror.c').read_text()
    family = (ROOT / 'src/asteroid1_ten_mirror.inc').read_text()
    scopes = extract(source, 'asteroid1_level_scope') + extract(source, 'asteroid1_scope')
    code = HARNESS.replace('@SCOPE@', scopes).replace('@FAMILY@', family)
    harness = args.out / 'harness.c'
    harness.write_text(code)
    raw = (args.data / 'tyrian.hdt').read_bytes()
    start = struct.unpack_from('<i', raw)[0] + 14 + 1638 * 80 + 61 * 82 + 55 * 37 + 7 * 37 + 19 * 41 + 38 * 86 + 12 * 37
    recordfile = args.out / 'original-ten-records.bin'
    recordfile.write_bytes(raw[start + 444 * 77:start + 454 * 77])
    flags = ['-std=c99', '-Wall', '-Wextra', '-Werror', '-Wno-misleading-indentation', '-I' + str(ROOT / 'src')]
    flags += ['-I' + path for path in args.sdl_include]
    if not args.sdl_include:
        flags += subprocess.check_output(['pkg-config', '--cflags', 'sdl2'], text=True).split()
    runs = []
    fixtures = args.out / 'fixtures'
    fixtures.mkdir()
    files = sorted(PACK / f'enemy-newshd-{base}-8.hda' for base in [31, 13, 15, 34, 49, 51, 53, 88, 89, 91])
    variants = []
    specs = [(file.name, 'missing') for file in files] + [(file.name, 'payload') for file in files]
    specs += [(files[0].name, kind) for kind in ['magic', 'role', 'density', 'width', 'height', 'anchor-x', 'anchor-y', 'short', 'extra', 'fifo', 'directory']]
    for number, (target, kind) in enumerate(specs):
        d = fixtures / f'{number:02d}-{kind}'
        d.mkdir()
        for file in files:
            dest = d / file.name
            if file.name != target:
                dest.symlink_to(file)
            elif kind == 'missing':
                continue
            elif kind == 'fifo':
                os.mkfifo(dest)
            elif kind == 'directory':
                dest.mkdir()
            else:
                b = bytearray(file.read_bytes())
                if kind == 'payload': b[40] ^= 1
                elif kind == 'magic': b[:4] = b'NOPE'
                elif kind in ['role', 'density', 'width', 'height', 'anchor-x', 'anchor-y']:
                    offset = dict(role=4, density=8, width=12, height=16, **{'anchor-x': 20, 'anchor-y': 24})[kind]
                    struct.pack_into('<I', b, offset, 1)
                elif kind == 'short': b = b[:-1]
                elif kind == 'extra': b += b'X'
                dest.write_bytes(b)
        variants.append((d, target, kind))
    for mode in ['optimized'] + (['asan-ubsan'] if args.sanitize else []):
        exe = args.out / mode
        compiler = ['cc', *flags, '-O2']
        if mode == 'asan-ubsan': compiler += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-g']
        def compile_limits(): resource.setrlimit(resource.RLIMIT_AS, (1024 * 1024**2,) * 2)
        subprocess.run([*compiler, str(harness), '-o', str(exe)], check=True, preexec_fn=compile_limits)
        for directory, expected in [(PACK, 'accept')] + [(d, 'reject') for d, _, _ in variants]:
            subprocess.run([str(exe), str(args.data / 'newshd.shp'), str(recordfile), str(directory), expected], check=True, timeout=10,
                           env={**os.environ, 'ASAN_OPTIONS': 'detect_leaks=0'})
        runs.append(dict(mode=mode, positive=1, negative=len(variants), binary_sha256=hashlib.sha256(exe.read_bytes()).hexdigest()))
    # Central isolation checks catch accidentally omitted bypass guards.
    assert 'asteroid_hd_enabled&&a->bank!=ASSET_ASTEROID1' in extract(source, 'read_asset')
    assert 'asteroid_hd_enabled&&a->bank!=ASSET_ASTEROID1' in extract(source, 'draw_asset_filtered')
    for name in ['draw_vulcan_shadow', 'render_mirror_cloud_blend_row', 'render_mirror_plasma_projectile_begin',
                 'render_mirror_sprite2_blend_pixel', 'render_mirror_ground101_layer1', 'render_mirror_hud_start',
                 'render_mirror_finish', 'render_mirror_present', 'render_mirror_fade_start', 'render_mirror_fade_step']:
        assert 'asteroid_hd_enabled' in extract(source, name), name
    result = dict(runs=runs, source_sha256=hashlib.sha256(family.encode()).hexdigest(),
                  peak_child_rss_bytes=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss * 1024,
                  leak_sanitizer=False, leak_sanitizer_note='Unavailable under this executor ptrace; address/undefined checks remain enabled.',
                  scope='Extracted production loader/scope/source/geometry; actual game acceptance is separate.')
    (args.out / 'receipt.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
