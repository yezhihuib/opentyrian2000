"""Shared bounded runner for independent, one-static-image random families.

Only the named ten-family test helper, production renderer/family sources, the
selected family's single HDA, newshd.shp, and its exact tyrian.hdt records are
inputs. Generated fixtures and receipts stay in the explicitly selected output
directory. This does not launch the game or read other tests or projections.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os
import resource
import shutil
import struct
import subprocess
import time


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / 'assets/hd/packs/asteroid1-ten-v1'
MIB = 1024 ** 2
FAMILY_OUTPUT_LIMIT = 8 * MIB
MIN_FREE = 5_000_000_000


BODY = r'''
/* The values under test are extracted production functions, not test copies. */
static unsigned record_byte_mutations, warm_sibling_checks;
static G101EnemyContext context(unsigned type)
{
 return (G101EnemyContext){type,0,0,TEST_SIZE,false,false,false,true};
}
static void geometry(Sprite2_array source)
{
 const int parts[]={0,1,19,20};
 unsigned before=accepted,log_before=logged;
 assert(sizeof(FAMILY_PINS)/sizeof(*FAMILY_PINS)==TEST_RECORD_COUNT);
 for(unsigned type=TEST_FIRST;type<=TEST_LAST;type++) {
  G101EnemyContext c=context(type);
  assert(FAMILY_PINS[type-TEST_FIRST].type==type);
  assert(FAMILY_PINS[type-TEST_FIRST].base==TEST_BASE&&FAMILY_PINS[type-TEST_FIRST].size==TEST_SIZE);
  for(unsigned p=0;p<TEST_PART_COUNT;p++) {
   int part=parts[p],px=part==1||part==20?12:0,py=part==19||part==20?14:0;
   assert(FAMILY_DRAW(&surface,100,80,source,TEST_BASE,part,17,&c));
   assert(last_x==100-px&&last_y==80-py&&last_part_x==px&&last_part_y==py&&last_filter==17);
   assert(last_asset==&FAMILY_RESOURCES.member[0]);
  }
 }
 assert(accepted-before==TEST_RECORD_COUNT*TEST_PART_COUNT&&logged-log_before==TEST_RECORD_COUNT*TEST_PART_COUNT);
}
static void exact_record_guards(Sprite2_array source)
{
 /* Toggle each serialized byte independently, including both bytes of words.
  * The visible actor stays TEST_FIRST when its sibling's motion/graphic moves. */
 for(unsigned t=TEST_FIRST;t<=TEST_LAST;t++) {
#define MUTATE(v) do { \
  for(unsigned bit_=1;bit_<=(sizeof(enemyDat[t].v)==2?256U:1U);bit_*=256U) { \
   enemyDat[t].v^=bit_;assert(!FAMILY_SOURCE(source)); \
   enemyDat[t].v^=bit_;assert(FAMILY_SOURCE(source));record_byte_mutations++; \
  } \
 } while(0)
  MUTATE(ani);for(unsigned i=0;i<3;i++)MUTATE(tur[i]);for(unsigned i=0;i<3;i++)MUTATE(freq[i]);
  MUTATE(xmove);MUTATE(ymove);MUTATE(xaccel);MUTATE(yaccel);MUTATE(xcaccel);MUTATE(ycaccel);
  MUTATE(startx);MUTATE(starty);MUTATE(startxc);MUTATE(startyc);MUTATE(armor);MUTATE(esize);
  for(unsigned i=0;i<20;i++)MUTATE(egraphic[i]);
  MUTATE(explosiontype);MUTATE(animate);MUTATE(shapebank);MUTATE(xrev);MUTATE(yrev);MUTATE(dgr);
  MUTATE(dlevel);MUTATE(dani);MUTATE(elaunchfreq);MUTATE(elaunchtype);MUTATE(value);MUTATE(eenemydie);
#undef MUTATE
 }
 assert(record_byte_mutations==TEST_RECORD_COUNT*77);
 G101EnemyContext c=context(TEST_FIRST);
 for(unsigned t=TEST_FIRST;t<=TEST_LAST;t++) {
#define WARM_MUTATE(v) do { \
  assert(FAMILY_DRAW(&surface,100,80,source,TEST_BASE,0,0,&c)); \
  unsigned rejected_before_=rejected,accepted_before_=accepted; \
  enemyDat[t].v^=1;assert(!FAMILY_DRAW(&surface,100,80,source,TEST_BASE,TEST_SIZE?1:0,0,&c)); \
  assert(rejected==rejected_before_+1&&accepted==accepted_before_); \
  assert(reject_reason&&!strcmp(reject_reason,TEST_REASON)); \
  enemyDat[t].v^=1;reject_reason=NULL;assert(FAMILY_SOURCE(source));warm_sibling_checks++; \
 } while(0)
  WARM_MUTATE(ymove);WARM_MUTATE(egraphic[19]);
#undef WARM_MUTATE
 }
 assert(warm_sibling_checks==TEST_RECORD_COUNT*2);
}
static void source_guards(Sprite2_array source)
{
 Uint8 *bank=source.data,*rebound=malloc(source.size);assert(rebound);
 memcpy(rebound,bank,source.size);
 Sprite2_array alternate={source.size,rebound};
 assert(source.data!=asteroid1_source_snapshot.bytes);
 assert(!FAMILY_SOURCE((Sprite2_array){source.size,NULL}));
 assert(!FAMILY_SOURCE((Sprite2_array){source.size-1,bank}));
 assert(!FAMILY_SOURCE(alternate)); /* A byte-identical ordinary/unbound bank. */
 spriteSheet8=alternate;assert(!FAMILY_SOURCE(alternate));
 enemySpriteSheets[0]=alternate;assert(!FAMILY_SOURCE(alternate));
 memset(&spriteSheet8,0,sizeof(spriteSheet8));assert(FAMILY_SOURCE(alternate));
 assert(!FAMILY_SOURCE(source)); /* Stale binding after the bank was rebound. */
 const unsigned offsets[]={0,200,42011};
 G101EnemyContext c=context(TEST_FIRST);
 for(unsigned j=0;j<3;j++) {
  assert(FAMILY_DRAW(&surface,100,80,alternate,TEST_BASE,0,0,&c));
  unsigned before=rejected;
  rebound[offsets[j]]^=1;assert(!FAMILY_SOURCE(alternate));
  assert(!FAMILY_DRAW(&surface,100,80,alternate,TEST_BASE,TEST_SIZE?1:0,0,&c));
  assert(rejected==before+1&&reject_reason&&!strcmp(reject_reason,TEST_REASON));
  rebound[offsets[j]]^=1;reject_reason=NULL;assert(FAMILY_SOURCE(alternate));
 }
 enemySpriteSheets[0]=source;free(rebound);assert(FAMILY_SOURCE(source));
 for(unsigned slot=0;slot<4;slot++) {
  memset(enemySpriteSheets,0,sizeof(enemySpriteSheets));memset(enemySpriteSheetIds,0,sizeof(enemySpriteSheetIds));
  enemySpriteSheets[slot]=source;enemySpriteSheetIds[slot]=8;assert(FAMILY_SOURCE(source));
  enemySpriteSheetIds[slot]=1;assert(!FAMILY_SOURCE(source));enemySpriteSheetIds[slot]=8;
  enemySpriteSheets[slot].size--;assert(!FAMILY_SOURCE(source));enemySpriteSheets[slot].size++;
 }
 memset(enemySpriteSheets,0,sizeof(enemySpriteSheets));memset(enemySpriteSheetIds,0,sizeof(enemySpriteSheetIds));
 enemySpriteSheets[0]=source;enemySpriteSheetIds[0]=8;
 spriteSheet8=source;assert(!FAMILY_SOURCE(source));memset(&spriteSheet8,0,sizeof(spriteSheet8));
 for(unsigned j=0;j<3;j++) {
  assert(FAMILY_DRAW(&surface,100,80,source,TEST_BASE,0,0,&c));
  unsigned before=rejected;
  bank[offsets[j]]^=1;assert(!FAMILY_SOURCE(source));
  assert(!FAMILY_DRAW(&surface,100,80,source,TEST_BASE,TEST_SIZE?1:0,0,&c));assert(rejected==before+1);
  bank[offsets[j]]^=1;reject_reason=NULL;assert(FAMILY_SOURCE(source));
 }
 /* With no accepted call this tick, a corrupt source is plain classic fallback. */
 mirror_logic_tick++;unsigned before=rejected;
 bank[200]^=1;assert(!FAMILY_DRAW(&surface,100,80,source,TEST_BASE,0,0,&c));assert(rejected==before&&!reject_reason);
 bank[200]^=1;assert(FAMILY_SOURCE(source));
}
static void scope_guards(void)
{
 assert(asteroid1_scope());
 bool *excluded[]={&xmas,&isNetworkGame,&twoPlayerMode,&galagaMode,&twoPlayerLinked,&record_demo,
  &onePlayerAction,&superTyrian,&timedBattleMode,&bonusLevel,&normalBonusLevelCurrent,&bonusLevelCurrent,&play_demo,&game_probe_enabled};
 for(unsigned i=0;i<sizeof(excluded)/sizeof(*excluded);i++){*excluded[i]=true;assert(!asteroid1_scope());*excluded[i]=false;}
 lvlFileNum=2;assert(!asteroid1_scope());lvlFileNum=9;assert(!asteroid1_scope());lvlFileNum=15;assert(!asteroid1_scope());lvlFileNum=1;
 episodeNum=2;assert(!asteroid1_scope());episodeNum=1;
}
static void drawing_guards(Sprite2_array source)
{
 G101EnemyContext c=context(TEST_FIRST);
 const int badx[]={INT_MIN,-1,309,INT_MAX},bady[]={INT_MIN,-14,200,INT_MAX},badpart[]={INT_MIN,-1,2,18,21,INT_MAX};
 unsigned before=accepted,log_before=logged;
 for(unsigned i=0;i<4;i++){assert(!FAMILY_DRAW(&surface,badx[i],80,source,TEST_BASE,0,0,&c));assert(!FAMILY_DRAW(&surface,100,bady[i],source,TEST_BASE,0,0,&c));}
 for(unsigned i=0;i<sizeof(badpart)/sizeof(*badpart);i++)assert(!FAMILY_DRAW(&surface,100,80,source,TEST_BASE,badpart[i],0,&c));
 if(!TEST_SIZE) {
  const int quadrants[]={1,19,20};
  for(unsigned i=0;i<3;i++)assert(!FAMILY_DRAW(&surface,100,80,source,TEST_BASE,quadrants[i],0,&c));
 }
 assert(!FAMILY_DRAW(&surface,100,80,source,TEST_BASE,0,-1,&c));assert(!FAMILY_DRAW(&surface,100,80,source,TEST_BASE,0,256,&c));
 assert(!FAMILY_DRAW(&surface,100,80,source,TEST_BASE+1,0,0,&c));
 c.type=TEST_FIRST-1;assert(!FAMILY_DRAW(&surface,100,80,source,TEST_BASE,0,0,&c));c.type=TEST_LAST+1;assert(!FAMILY_DRAW(&surface,100,80,source,TEST_BASE,0,0,&c));c.type=TEST_FIRST;
#define DENY_CONTEXT(v,bad,good) do {c.v=bad;assert(!FAMILY_DRAW(&surface,100,80,source,TEST_BASE,0,0,&c));c.v=good;} while(0)
 DENY_CONTEXT(size,TEST_SIZE?0:1,TEST_SIZE);DENY_CONTEXT(size,2,TEST_SIZE);DENY_CONTEXT(availability,1,0);DENY_CONTEXT(availability,3,0);DENY_CONTEXT(availability,UINT_MAX,0);
 DENY_CONTEXT(static_animation,false,true);DENY_CONTEXT(score_item,true,false);DENY_CONTEXT(damaged,true,false);
#undef DENY_CONTEXT
#define DENY_STATE(v,bad,good) do {v=bad;assert(!FAMILY_DRAW(&surface,100,80,source,TEST_BASE,0,0,&c));v=good;} while(0)
 DENY_STATE(lvlFileNum,2,1);DENY_STATE(episodeNum,2,1);DENY_STATE(asteroid_hd_enabled,false,true);DENY_STATE(asteroid_hd_lease,false,true);
 DENY_STATE(active,false,true);DENY_STATE(game_probe_scene_assets,0,1);DENY_STATE(reject_reason,"preexisting rejection",NULL);
 DENY_STATE(surface.pixels,NULL,pixels);DENY_STATE(surface.w,319,320);DENY_STATE(surface.h,199,200);DENY_STATE(surface.pitch,321,320);DENY_STATE(surface.format,NULL,&format);
 DENY_STATE(format.format,SDL_PIXELFORMAT_ARGB8888,SDL_PIXELFORMAT_INDEX8);DENY_STATE(format.BitsPerPixel,32,8);DENY_STATE(format.BytesPerPixel,4,1);
 DENY_STATE(game_screen,NULL,&surface);DENY_STATE(VGAScreen,NULL,&surface);
#undef DENY_STATE
 SDL_Surface other=surface;assert(!FAMILY_DRAW(&other,100,80,source,TEST_BASE,0,0,&c));
 assert(!FAMILY_DRAW(NULL,100,80,source,TEST_BASE,0,0,&c));assert(!FAMILY_DRAW(&surface,100,80,source,TEST_BASE,0,0,NULL));
 assert(accepted==before&&logged==log_before);
 const int parts[]={0,1,19,20};
 for(unsigned type=TEST_FIRST;type<=TEST_LAST;type++) {
  c=context(type);
  for(unsigned p=0;p<TEST_PART_COUNT;p++) {
   int px=parts[p]==1||parts[p]==20?12:0,py=parts[p]==19||parts[p]==20?14:0;
   assert(FAMILY_DRAW(&surface,0,-13,source,TEST_BASE,parts[p],255,&c));
   assert(last_x==-px&&last_y==-13-py&&last_part_x==px&&last_part_y==py&&last_filter==255);
   assert(FAMILY_DRAW(&surface,308,199,source,TEST_BASE,parts[p],0,&c));
   assert(last_x==308-px&&last_y==199-py&&last_filter==0);
  }
  c.availability=2;assert(FAMILY_DRAW(&surface,100,80,source,TEST_BASE,0,0,&c));
 }
}
static void cache_guards(void)
{
 const char *root=game_probe_assets;
 const char *bad_roots[]={NULL,"","/foreign-asteroid-root"};
 for(unsigned i=0;i<3;i++){game_probe_assets=bad_roots[i];assert(!FAMILY_READY());}game_probe_assets=root;
 char too_long[1025];memset(too_long,'a',sizeof(too_long));too_long[sizeof(too_long)-1]=0;
 game_probe_assets=too_long;assert(!FAMILY_READY());game_probe_assets=root;assert(FAMILY_READY());
 game_probe_density=4;assert(!FAMILY_READY());game_probe_density=8;
 bool *bad_modes[]={&game_probe_missing,&game_probe_invalid,&game_probe_original_reference};
 for(unsigned i=0;i<3;i++){*bad_modes[i]=true;assert(!FAMILY_READY());*bad_modes[i]=false;assert(FAMILY_READY());}
#define BAD_MEMBER(v,bad) do { \
 FAMILY_SHUTDOWN();assert(FAMILY_READY());Asset saved_=FAMILY_RESOURCES.member[0]; \
 mirror_logic_tick++;FAMILY_RESOURCES.member[0].v=bad;assert(!FAMILY_READY()); \
 FAMILY_RESOURCES.member[0]=saved_;assert(!FAMILY_READY()); \
 } while(0)
 BAD_MEMBER(initialized,false);BAD_MEMBER(valid,false);BAD_MEMBER(bank,1);BAD_MEMBER(index,TEST_BASE+1);
 BAD_MEMBER(w,TEST_WIDTH+1);BAD_MEMBER(h,TEST_HEIGHT+1);BAD_MEMBER(anchor_x,1);BAD_MEMBER(anchor_y,1);BAD_MEMBER(density,4);BAD_MEMBER(rgba,NULL);
#undef BAD_MEMBER
 FAMILY_SHUTDOWN();assert(FAMILY_READY());mirror_logic_tick++;
 FAMILY_RESOURCES.member[0].rgba[10]^=1;assert(!FAMILY_READY());FAMILY_RESOURCES.member[0].rgba[10]^=1;assert(!FAMILY_READY());
 FAMILY_SHUTDOWN();assert(FAMILY_READY());
}
int main(int argc,char **argv)
{
 assert(argc==6);game_probe_assets=argv[3];records(argv[2]);
 FILE *f=fopen(argv[1],"rb");assert(f);Uint8 *bank=malloc(42012);assert(bank&&fread(bank,1,42012,f)==42012&&fgetc(f)==EOF);fclose(f);
 enemySpriteSheets[0]=(Sprite2_array){42012,bank};enemySpriteSheetIds[0]=8;Sprite2_array source=enemySpriteSheets[0];
 /* A cold corrupt source must not seed a trusted private reference. */
 bank[200]^=1;assert(!FAMILY_SOURCE(source)&&!asteroid1_source_snapshot.valid);bank[200]^=1;
 assert(FAMILY_SOURCE(source));scope_guards();
 if(!strcmp(argv[4],"reject")) {
  assert(!FAMILY_READY());
  const int parts[]={0,1,19,20};
  for(unsigned type=TEST_FIRST;type<=TEST_LAST;type++) {
   G101EnemyContext c=context(type);
   for(unsigned p=0;p<TEST_PART_COUNT;p++)assert(!FAMILY_DRAW(&surface,100,80,source,TEST_BASE,parts[p],0,&c));
  }
  assert(!accepted&&!logged&&!rejected&&!reject_reason);
  /* Failure remains local/sticky even if the selected root later becomes good. */
  game_probe_assets=argv[5];assert(!FAMILY_READY());FAMILY_SHUTDOWN();assert(FAMILY_READY());geometry(source);
 } else {
  assert(!strcmp(argv[4],"accept")&&FAMILY_READY());
  geometry(source);exact_record_guards(source);source_guards(source);drawing_guards(source);cache_guards();
  printf("%s: %u ordered %s; %u record-byte guards; %u warm sibling guards; source/loader/clipping/cache checks passed\n",
   TEST_NAME,TEST_RECORD_COUNT*TEST_PART_COUNT,TEST_SIZE?"quadrants":"unquadranted draws",record_byte_mutations,warm_sibling_checks);
 }
 FAMILY_SHUTDOWN();free(bank);return 0;
}
'''


def _limits(memory, *, address_space=True):
    def apply():
        if address_space:
            resource.setrlimit(resource.RLIMIT_AS, (memory, memory))
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    return apply


def _run_bounded(command, *, compiler=False, sanitize=False):
    """Bound normal address space and sampled sanitizer resident memory.

    ASan's reserved virtual shadow cannot fit an RLIMIT_AS. Its child instead
    receives the same 512 MiB RSS ceiling, monitored through its exact /proc PID.
    wait4 supplies the exact exit high-water mark, including compiler children.
    """
    ceiling = (1024 if compiler else 512) * MIB
    proc = subprocess.Popen(command, env={**os.environ, 'ASAN_OPTIONS': 'detect_leaks=0'},
                            preexec_fn=_limits(ceiling, address_space=not sanitize or compiler))
    peak = 0
    deadline = time.monotonic() + (90 if compiler else 15)
    try:
        while True:
            pid, status, usage = os.wait4(proc.pid, os.WNOHANG)
            if pid:
                proc.returncode = os.waitstatus_to_exitcode(status)
                peak = max(peak, usage.ru_maxrss * 1024)
                if peak > ceiling:
                    raise RuntimeError('subprocess resident-memory ceiling exceeded')
                break
            if time.monotonic() > deadline:
                raise RuntimeError('bounded subprocess timed out: ' + str(command[0]))
            try:
                # This dynamically named file belongs only to our direct child.
                status = Path('/proc') / str(proc.pid) / 'status'
                for line in status.read_text().splitlines():
                    if line.startswith('VmRSS:'):
                        rss = int(line.split()[1]) * 1024
                        peak = max(peak, rss)
                        if rss > ceiling:
                            raise RuntimeError('subprocess resident-memory ceiling exceeded')
                        break
            except FileNotFoundError:
                pass
            time.sleep(0.01)
        if proc.returncode:
            raise subprocess.CalledProcessError(proc.returncode, command)
    finally:
        if proc.returncode is None:
            proc.kill()
            _, status, _ = os.wait4(proc.pid, 0)
            proc.returncode = os.waitstatus_to_exitcode(status)
    return peak


def main(base, first, last):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--sdl-include', action='append', default=[])
    parser.add_argument('--sanitize', action='store_true')
    args = parser.parse_args()
    assert (base, first, last) in [(43, 260, 262), (85, 263, 265),
                                  (123, 266, 268), (95, 317, 318), (114, 319, 320),
                                  (133, 321, 322), (152, 323, 324)]
    record_count = last - first + 1
    args.out.mkdir(parents=True, exist_ok=True)
    if shutil.disk_usage(args.out).free < MIN_FREE:
        raise RuntimeError('less than 5 GB free before the bounded test run')
    family_name = f'random{base}'
    helper = ROOT / 'tests/test_asteroid1_ten_assets.py'
    render = ROOT / 'src/render_mirror.c'
    ten_source = ROOT / 'src/asteroid1_ten_mirror.inc'
    family_source = ROOT / f'src/asteroid1_{family_name}_mirror.inc'
    art = PACK / f'enemy-newshd-{base}-8.hda'
    original_hdt = args.data / 'tyrian.hdt'
    original_shp = args.data / 'newshd.shp'
    read_allowlist = {helper, render, ten_source, family_source,
                      ROOT / 'src/asteroid1_source_snapshot.inc', art, original_hdt, original_shp}

    def read(path, *, binary=False):
        if path not in read_allowlist:
            raise RuntimeError('input is outside the explicit read allowlist')
        return path.read_bytes() if binary else path.read_text()

    payload = read(art, binary=True)
    if len(payload) < 28:
        raise RuntimeError('short one-static-image HDA header')
    magic, role, density, width, height, anchor_x, anchor_y = struct.unpack_from('<4s6I', payload)
    if (magic != b'HDR1' or role != 1080000 + base or density != 8 or
            anchor_x or anchor_y or (width, height) not in [(12, 14), (24, 28)]):
        raise RuntimeError('unexpected one-static-image HDA geometry or identity')
    size = int(width == 24)
    part_count = 4 if size else 1
    ordered_draws = record_count * part_count
    if len(payload) != 28 + width * height * 8 * 8 * 4:
        raise RuntimeError('unexpected one-static-image HDA size')

    # Import exactly the permitted helper, with no test discovery or globbing.
    spec = importlib.util.spec_from_file_location('asteroid_ten_harness', helper)
    ten = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ten)
    source, original, family = read(render), read(ten_source), read(family_source)
    scopes = ten.extract(source, 'asteroid1_level_scope') + ten.extract(source, 'asteroid1_scope')
    shared = ten.extract(original, 'asteroid1_stamp') + '#include "asteroid1_source_snapshot.inc"\n' + ten.extract(original, 'asteroid1_record_stamp')
    prefix = ten.HARNESS.split('@SCOPE@', 1)[0]
    prefix = prefix.replace('static Uint8 last_filter;', 'static Uint8 last_filter;static Asset *last_asset;')
    prefix = prefix.replace('accepted++;last_x=x;', 'last_asset=a;accepted++;last_x=x;')
    part_contract = 'part&&part->w==12&&part->h==14' if size else '!part'
    prefix = prefix.replace('assert(a&&a->bank==108', f'assert(a&&a->index=={base}&&a->w=={width}&&a->h=={height}&&{part_contract}&&a->bank==108')
    record_parser = ten.extract(ten.HARNESS, 'word') + ten.extract(ten.HARNESS, 'records').replace('t=444;t<=453', f't={first};t<={last}')
    namespace = f'asteroid_{family_name}_'
    defines = f'#define TEST_FIRST {first}\n#define TEST_LAST {last}\n#define TEST_BASE {base}\n#define TEST_SIZE {size}\n#define TEST_WIDTH {width}\n#define TEST_HEIGHT {height}\n#define TEST_RECORD_COUNT {record_count}U\n#define TEST_PART_COUNT {part_count}U\n#define TEST_NAME "{family_name}"\n#define TEST_REASON "asteroid-{family_name}-family-integrity"\n'
    for macro, suffix in [('SOURCE', 'source'), ('DRAW', 'draw'), ('READY', 'family_ready'), ('SHUTDOWN', 'shutdown'), ('PINS', 'pins'), ('RESOURCES', 'resources')]:
        defines += f'#define FAMILY_{macro} {namespace}{suffix}\n'
    code = prefix + scopes + shared + family + record_parser + defines + BODY
    harness = args.out / 'harness.c'
    harness.write_text(code)
    generated = [harness]

    # Read the HDT offset header and exactly this family's original records.
    with original_hdt.open('rb') as stream:
        offset = stream.read(4)
        if len(offset) != 4:
            raise RuntimeError('short tyrian.hdt offset header')
        start = struct.unpack('<i', offset)[0] + 14 + 1638 * 80 + 61 * 82 + 55 * 37 + 7 * 37 + 19 * 41 + 38 * 86 + 12 * 37
        stream.seek(start + first * 77)
        records = stream.read(record_count * 77)
        if len(records) != record_count * 77:
            raise RuntimeError('short original record range')
    recordfile = args.out / f'original-{family_name}-records.bin'
    recordfile.write_bytes(records)
    generated.append(recordfile)
    if original_shp.stat().st_size != 42012:
        raise RuntimeError('unexpected original newshd.shp size')
    fixtures = args.out / 'fixtures'
    fixtures.mkdir()
    isolated = fixtures / 'isolated-own-family'
    isolated.mkdir()
    isolated_art = isolated / art.name
    isolated_art.write_bytes(payload)
    generated.append(isolated_art)
    variants = []
    kinds = ['missing', 'payload', 'magic', 'role', 'foreign-base', 'density', 'width', 'height', 'anchor-x', 'anchor-y', 'header-short', 'short', 'extra', 'fifo', 'directory', 'broken-symlink']
    for kind in kinds:
        directory = fixtures / kind
        directory.mkdir()
        dest = directory / art.name
        if kind == 'missing':
            pass
        elif kind == 'fifo':
            os.mkfifo(dest)
        elif kind == 'directory':
            dest.mkdir()
        elif kind == 'broken-symlink':
            dest.symlink_to(directory / 'absent-own-resource.hda')
        else:
            data = bytearray(payload)
            if kind == 'payload':
                data[40] ^= 1
            elif kind == 'magic':
                data[:4] = b'NOPE'
            elif kind == 'foreign-base':
                struct.pack_into('<I', data, 4, 1080000 + base + 1)
            elif kind in ['role', 'density', 'width', 'height', 'anchor-x', 'anchor-y']:
                struct.pack_into('<I', data, dict(role=4, density=8, width=12, height=16, **{'anchor-x': 20, 'anchor-y': 24})[kind], 1)
            elif kind == 'header-short':
                data = data[:12]
            elif kind == 'short':
                data = data[:-1]
            elif kind == 'extra':
                data += b'X'
            dest.write_bytes(data)
            generated.append(dest)
        variants.append((directory, kind))
    flags = ['-std=c99', '-Wall', '-Wextra', '-Werror', '-Wno-misleading-indentation', '-I' + str(ROOT / 'src')]
    flags += ['-I' + path for path in args.sdl_include]
    if not args.sdl_include:
        flags += subprocess.check_output(['pkg-config', '--cflags', 'sdl2'], text=True).split()
    runs = []
    runtime_peak = compiler_peak = 0
    for mode in ['optimized'] + (['asan-ubsan'] if args.sanitize else []):
        exe = args.out / mode
        compiler = ['cc', *flags, '-O2']
        if mode == 'asan-ubsan':
            compiler += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-g']
        compiler_peak = max(compiler_peak, _run_bounded([*compiler, str(harness), '-o', str(exe)], compiler=True))
        generated.append(exe)
        for directory, expected in [(PACK, 'accept'), (isolated, 'accept')] + [(directory, 'reject') for directory, _ in variants]:
            runtime_peak = max(runtime_peak, _run_bounded([str(exe), str(original_shp), str(recordfile), str(directory), expected, str(PACK)], sanitize=mode == 'asan-ubsan'))
        runs.append(dict(mode=mode, positive=2, negative=len(variants), binary_sha256=hashlib.sha256(exe.read_bytes()).hexdigest()))
    output_bytes = sum(path.stat().st_size for path in generated)
    if output_bytes > FAMILY_OUTPUT_LIMIT:
        raise RuntimeError('family outputs exceeded 8 MiB; batch budget is externally capped')
    if shutil.disk_usage(args.out).free < MIN_FREE:
        raise RuntimeError('less than 5 GB free after the bounded test run')
    result = dict(family=family_name, original_records=list(range(first, last + 1)), base=base, runs=runs,
                  source_sha256=hashlib.sha256(family.encode()).hexdigest(), original_records_sha256=hashlib.sha256(records).hexdigest(),
                  record_count=record_count, context_size=size, width=width, height=height,
                  record_byte_mutations=record_count * 77, warm_sibling_mutations=record_count * 2,
                  ordered_draws=ordered_draws, ordered_quadrants=ordered_draws if size else 0,
                  unquadranted_draws=ordered_draws if not size else 0, fixture_kinds=kinds,
                  runtime_peak_rss_bytes=runtime_peak, compiler_peak_rss_bytes=compiler_peak,
                  peak_child_rss_bytes=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss * 1024,
                  runtime_memory_limit_bytes=512 * MIB, compiler_address_space_limit_bytes=1024 * MIB,
                  output_bytes_before_receipt=output_bytes, png_bytes=0, leak_sanitizer=False,
                  read_allowlist=[str(path) for path in sorted(read_allowlist)],
                  scope=f'Independent extracted-production family. Exact 77-byte records, all sibling source guards, ordinary/rebound/same-address sources, one isolated resource, loader negatives, {ordered_draws} ordered {"quadrants" if size else "unquadranted draws"}, clipping/filter/format/mode checks, sticky local fallback. Actual-engine random-spawn acceptance is separate.')
    (args.out / 'receipt.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
