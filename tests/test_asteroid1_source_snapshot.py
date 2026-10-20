#!/usr/bin/env python3
"""Bounded current-byte source guard and renderer-epoch regression tests.

Reads only the nineteen named production family includes, inline record269 in
render_mirror.c, their three independent snapshot implementations, and the
explicitly selected external newshd.shp/newshs.shp/newshp.shp.
Record stamps are stubbed here to count every dependency query; the twenty full
asset suites separately exercise real serialized records, scopes and drawing.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import resource
import subprocess
import signal
import time
import shutil
MIB=1024**2
OUTPUT_LIMIT=16*MIB

ROOT = Path(__file__).resolve().parents[1]
FAMILIES = [('ten', 'asteroid1'), ('four', 'asteroid4'),
            ('common4', 'asteroid_common4'), ('random5', 'asteroid_random5'),
            ('goldwing', 'goldwing'), ('random43', 'asteroid_random43'), ('random85', 'asteroid_random85'), ('random123', 'asteroid_random123'), ('random95', 'asteroid_random95'), ('random114', 'asteroid_random114'),
            ('random133', 'asteroid_random133'), ('random152', 'asteroid_random152'),
            ('random286', 'asteroid_random286'), ('fork284', 'fork284'), ('capsule545', 'capsule545'), ('paired287_288', 'paired287_288'), ('firing325', 'firing325'), ('ember269', 'ember269'), ('linked338', 'linked338'), ('pulsing272', 'pulsing272')]

BANK_NAMES = ['NEWSHD', 'NEWSHS', 'NEWSHP']
BANK_SIZES = [42012, 46566, 46204]
BANK_RECORDS = [45, 2, 5]
BANK_FAMILIES = [17, 2, 1]
LINKED338_PINS = {
    338: 'cbad2cf90f5c58cf', 339: '2ddda4009b77985a',
    340: 'cf24bb2935688c70', 341: '1dbea2914b901887',
    342: '68faea6f9286755d',
}


def extract(source, name):
    match = re.search(r'^[A-Za-z_][^\n;{}]*\b' + re.escape(name) + r'\([^;{}]*\)\s*\{', source, re.M)
    assert match, name
    end = source.index('{', match.start()) + 1
    depth = 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[match.start():end] + '\n'


PRELUDE = r'''
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
typedef uint8_t Uint8;
typedef struct {unsigned size;Uint8 *data;} Sprite2_array;
static Sprite2_array enemySpriteSheets[4],spriteSheet8;
static unsigned char enemySpriteSheetIds[4];
static unsigned pins_checked[3],record_queries,checks;
static bool corrupt_record;
static unsigned corrupt_type;
enum { FAMILY_COUNT=20, RECORD_COUNT=52, BANK_COUNT=3, MAX_BANK_SIZE=46566 };
static struct {struct {Uint8 *rgba;} member[10];} asteroid1_resources;
static struct {struct {Uint8 *rgba;} member[3];} firing325_resources;
static struct {struct {Uint8 *rgba;} member[8];} linked338_resources;
static struct {struct {Uint8 *rgba;} member[4];} pulsing272_resources;
static void *pulsing272_draw_lease;
'''
MAIN = r'''
static const unsigned sizes[BANK_COUNT]={42012,46566,46204};
static const unsigned logical[BANK_COUNT]={8,23,20};
static const unsigned bank_records[BANK_COUNT]={45,2,5};
static const unsigned bank_families[BANK_COUNT]={17,2,1};
static void all(Sprite2_array bank,int expected_bank)
{
 unsigned before=record_queries;
 for(unsigned i=0;i<FAMILY_COUNT;i++) {
  bool expected=expected_bank>=0&&family_bank[i]==(unsigned)expected_bank;
  assert(guards[i](bank)==expected);checks++;
 }
 if(expected_bank>=0)assert(record_queries-before==bank_records[expected_bank]);
 else if(!corrupt_type&&!corrupt_record)assert(record_queries==before);
}
static void bound(Sprite2_array bank,unsigned role,unsigned slot)
{
 memset(enemySpriteSheets,0,sizeof(enemySpriteSheets));
 memset(enemySpriteSheetIds,0,sizeof(enemySpriteSheetIds));
 enemySpriteSheets[slot]=bank;enemySpriteSheetIds[slot]=role;
}
static void bound_all(const Sprite2_array *banks)
{
 memset(enemySpriteSheets,0,sizeof(enemySpriteSheets));
 memset(enemySpriteSheetIds,0,sizeof(enemySpriteSheetIds));
 for(unsigned k=0;k<BANK_COUNT;k++){enemySpriteSheets[k]=banks[k];enemySpriteSheetIds[k]=logical[k];}
}
static bool snapshot_valid(unsigned k)
{return k==0?asteroid1_source_snapshot.valid:k==1?firing325_source_snapshot.valid:linked338_source_snapshot.valid;}
static void shutdown(unsigned k)
{if(k==0)asteroid1_shutdown();else if(k==1){firing325_shutdown();pulsing272_shutdown();}else linked338_shutdown();}
static void reference(Uint8 *const *original,unsigned valid_mask)
{
 const Uint8 *bytes[BANK_COUNT]={asteroid1_source_snapshot.bytes,firing325_source_snapshot.bytes,linked338_source_snapshot.bytes};
 for(unsigned k=0;k<BANK_COUNT;k++) {
  assert(snapshot_valid(k)==!!(valid_mask&(1U<<k)));
  if(snapshot_valid(k))assert(!memcmp(bytes[k],original[k],sizes[k]));
 }
}
static void assert_resources(unsigned live_mask)
{
 for(unsigned i=0;i<10;i++)assert(!!asteroid1_resources.member[i].rgba==!!(live_mask&1));
 for(unsigned i=0;i<3;i++)assert(!!firing325_resources.member[i].rgba==!!(live_mask&2));
 for(unsigned i=0;i<8;i++)assert(!!linked338_resources.member[i].rgba==!!(live_mask&4));
 for(unsigned i=0;i<4;i++)assert(!!pulsing272_resources.member[i].rgba==!!(live_mask&2));
}
static Uint8 *input(const char *path,unsigned size)
{
 FILE *f=fopen(path,"rb");assert(f);
 /* Maximum-sized backing allocations allow actual same-address cross-bank
  * reuse without making an out-of-bounds read part of the test fixture. */
 Uint8 *p=calloc(MAX_BANK_SIZE,1);
 assert(p&&fread(p,1,size,f)==size&&fgetc(f)==EOF);fclose(f);return p;
}
int main(int argc,char **argv)
{
 assert(argc==4&&sizeof(asteroid1_source_snapshot.bytes)==42012&&
  sizeof(firing325_source_snapshot.bytes)==46566&&sizeof(linked338_source_snapshot.bytes)==46204);
 assert(FAMILY_COUNT==20&&RECORD_COUNT==52);
 Uint8 *raw[BANK_COUNT],*copy[BANK_COUNT],*original[BANK_COUNT];Sprite2_array banks[BANK_COUNT];
 unsigned families[BANK_COUNT]={0},records[BANK_COUNT]={0};
 for(unsigned i=0;i<FAMILY_COUNT;i++){families[family_bank[i]]++;records[family_bank[i]]+=counts[i];}
 for(unsigned k=0;k<BANK_COUNT;k++) {
  assert(families[k]==bank_families[k]&&records[k]==bank_records[k]);
  raw[k]=input(argv[k+1],sizes[k]);copy[k]=malloc(MAX_BANK_SIZE);original[k]=malloc(sizes[k]);
  assert(copy[k]&&original[k]);memcpy(copy[k],raw[k],sizes[k]);memcpy(original[k],raw[k],sizes[k]);
  banks[k]=(Sprite2_array){sizes[k],raw[k]};
 }
 /* Every snapshot rejects every other bank's exact size, even before reading
  * an invalid pointer. The older42012/46566 boundaries remain strict. */
 bool (*match[BANK_COUNT])(const Uint8 *,size_t)={asteroid1_source_bytes_match,firing325_source_bytes_match,linked338_source_bytes_match};
 for(unsigned k=0;k<BANK_COUNT;k++)for(unsigned j=0;j<BANK_COUNT;j++)if(k!=j)
  assert(!match[k]((const Uint8 *)(uintptr_t)1,sizes[j]));
 /* Invalid pointer/role/size exclusions precede byte reads and record pins. */
 for(unsigned k=0;k<BANK_COUNT;k++) {
  Sprite2_array bank=banks[k],foreign={sizes[k],(Uint8 *)(uintptr_t)1};
  bound((Sprite2_array){0,NULL},0,0);
  all((Sprite2_array){sizes[k],NULL},-1);all(foreign,-1);
  for(unsigned j=0;j<BANK_COUNT;j++)if(j!=k){bound(foreign,logical[j],0);all(foreign,-1);}
  bound(bank,logical[k],0);spriteSheet8=bank;all(bank,-1);memset(&spriteSheet8,0,sizeof(spriteSheet8));
  for(int delta=-1;delta<=1;delta+=2)all((Sprite2_array){sizes[k]+delta,raw[k]},-1);
  for(unsigned j=0;j<BANK_COUNT;j++)if(j!=k)all((Sprite2_array){sizes[j],raw[k]},-1);
 }
 reference(original,0);assert(!record_queries);
 for(unsigned k=0;k<BANK_COUNT;k++)assert(!pins_checked[k]);
 /* Cold corruption of each bank leaves BOTH peers independently usable.
  * Reset each time to exercise every direction from a genuinely cold epoch. */
 for(unsigned bad=0;bad<BANK_COUNT;bad++) {
  for(unsigned k=0;k<BANK_COUNT;k++)shutdown(k);
  bound_all(banks);raw[bad][200]^=1;
  unsigned before=pins_checked[bad];all(banks[bad],-1);
  assert(!snapshot_valid(bad)&&pins_checked[bad]-before==bank_families[bad]);
  unsigned valid_mask=0;
  for(unsigned k=0;k<BANK_COUNT;k++)if(k!=bad) {
   before=pins_checked[k];all(banks[k],(int)k);all(banks[k],(int)k);
   assert(pins_checked[k]==before+1);valid_mask|=1U<<k;reference(original,valid_mask);
  }
  raw[bad][200]^=1;before=pins_checked[bad];all(banks[bad],(int)bad);all(banks[bad],(int)bad);
  assert(pins_checked[bad]==before+1);reference(original,7);
 }
 for(unsigned k=0;k<BANK_COUNT;k++) {
  Sprite2_array bank=banks[k];const unsigned offsets[]={0,1,200,sizes[k]/2,sizes[k]-2,sizes[k]-1};
  unsigned pins[BANK_COUNT];memcpy(pins,pins_checked,sizeof(pins));
  /* Every warm call checks all current bytes, including equal pointers/ticks;
   * a mutation in one bank does not suppress either valid peer. */
  for(unsigned j=0;j<sizeof(offsets)/sizeof(offsets[0]);j++) {
   bound_all(banks);unsigned before=record_queries;raw[k][offsets[j]]^=1;
   all(bank,-1);assert(record_queries==before);reference(original,7);
   for(unsigned peer=0;peer<BANK_COUNT;peer++)if(peer!=k)all(banks[peer],(int)peer);
   raw[k][offsets[j]]^=1;all(bank,(int)k);
  }
  /* Every loaded slot works, while every foreign bank identity is rejected. */
  for(unsigned slot=0;slot<4;slot++) {
   bound(bank,logical[k],slot);all(bank,(int)k);
   for(unsigned peer=0;peer<BANK_COUNT;peer++)if(peer!=k){enemySpriteSheetIds[slot]=logical[peer];all(bank,-1);}
   enemySpriteSheetIds[slot]=17;all(bank,-1);
   enemySpriteSheetIds[slot]=logical[k];enemySpriteSheets[slot].size--;all(bank,-1);
  }
  bound(bank,logical[k],0);spriteSheet8=bank;all(bank,-1);memset(&spriteSheet8,0,sizeof(spriteSheet8));
  /* Equal bytes in an unloaded clone are not a loaded current identity. */
  Sprite2_array reloaded={sizes[k],copy[k]};all(reloaded,-1);
  bound(reloaded,logical[k],0);all(bank,-1);all(reloaded,(int)k);
  copy[k][200]^=1;all(reloaded,-1);copy[k][200]^=1;all(reloaded,(int)k);
  bound(bank,logical[k],0);raw[k][sizes[k]-1]^=1;all(bank,-1);
  memcpy(raw[k],copy[k],sizes[k]);all(bank,(int)k);
  /* Reuse the exact same address as EACH other bank, with that bank's actual
   * bytes/size/role, then reload the original. No pointer-based trust survives. */
  for(unsigned peer=0;peer<BANK_COUNT;peer++)if(peer!=k) {
   memcpy(raw[k],original[peer],sizes[peer]);Sprite2_array reused={sizes[peer],raw[k]};
   bound(reused,logical[peer],0);all(bank,-1);all(banks[peer],-1);all(reused,(int)peer);
   raw[k][sizes[peer]/2]^=1;all(reused,-1);raw[k][sizes[peer]/2]^=1;all(reused,(int)peer);
   memcpy(raw[k],original[k],sizes[k]);bound(bank,logical[k],0);all(reused,-1);all(bank,(int)k);
  }
  assert(!memcmp(pins,pins_checked,sizeof(pins)));reference(original,7);
 }
 /* Each guard queries its complete closure, with bad records local to exactly
  * the declaring families. This includes the FIFTH linked record342 and both
  * independent foreign banks for every one of the52 dependencies, including independent325/272 records
  * sharing only NEWSHS byte trust. */
 for(unsigned family=0;family<FAMILY_COUNT;family++) {
  unsigned k=family_bank[family];bound(banks[k],logical[k],0);
  for(unsigned j=0;j<counts[family];j++) {
   corrupt_type=types[family][j];unsigned before=record_queries;
   assert(!guards[family](banks[k])&&record_queries-before==j+1);checks++;
   for(unsigned peer=0;peer<FAMILY_COUNT;peer++) {
    bool depends=false;
    for(unsigned n=0;n<counts[peer];n++)if(types[peer][n]==corrupt_type)depends=true;
    unsigned peer_bank=family_bank[peer];bound(banks[peer_bank],logical[peer_bank],0);
    assert(guards[peer](banks[peer_bank])==!depends);checks++;
   }
   bound(banks[k],logical[k],0);
  }
 }
 corrupt_type=0;corrupt_record=true;
 bound_all(banks);for(unsigned k=0;k<BANK_COUNT;k++)all(banks[k],-1);
 corrupt_record=false;
 /* The new family cache shutdown cannot revoke325/shared NEWSHS trust.
  * Renderer epoch shutdown below invokes the original owner and both caches. */
 for(unsigned i=0;i<4;i++){pulsing272_resources.member[i].rgba=malloc(16);assert(pulsing272_resources.member[i].rgba);}
 pulsing272_draw_lease=&banks[1];pulsing272_shutdown();assert(!pulsing272_draw_lease);
 for(unsigned i=0;i<4;i++)assert(!pulsing272_resources.member[i].rgba);
 reference(original,7);bound_all(banks);all(banks[1],1);
 /* Each bank epoch shutdown revokes ONLY its own snapshot and resource caches. */
 for(unsigned i=0;i<10;i++){asteroid1_resources.member[i].rgba=malloc(16);assert(asteroid1_resources.member[i].rgba);}
 for(unsigned i=0;i<3;i++){firing325_resources.member[i].rgba=malloc(16);assert(firing325_resources.member[i].rgba);}
 for(unsigned i=0;i<8;i++){linked338_resources.member[i].rgba=malloc(16);assert(linked338_resources.member[i].rgba);}
 for(unsigned i=0;i<4;i++){pulsing272_resources.member[i].rgba=malloc(16);assert(pulsing272_resources.member[i].rgba);}
 unsigned resource_mask=7;
 for(unsigned k=0;k<BANK_COUNT;k++) {
  shutdown(k);resource_mask&=~(1U<<k);assert_resources(resource_mask);reference(original,7&~(1U<<k));
  bound_all(banks);
  for(unsigned peer=0;peer<BANK_COUNT;peer++)if(peer!=k)all(banks[peer],(int)peer);
  raw[k][200]^=1;all(banks[k],-1);assert(!snapshot_valid(k));
  for(unsigned peer=0;peer<BANK_COUNT;peer++)if(peer!=k)all(banks[peer],(int)peer);
  raw[k][200]^=1;all(banks[k],(int)k);reference(original,7);
 }
 /* Epoch reset is idempotent. Each bank rejects cold corruption and re-pins
  * independently, rather than inheriting trust from either older snapshot. */
 for(unsigned twice=0;twice<2;twice++)for(unsigned k=0;k<BANK_COUNT;k++)shutdown(k);
 reference(original,0);unsigned valid_mask=0;bound_all(banks);
 for(unsigned k=0;k<BANK_COUNT;k++) {
  unsigned before=pins_checked[k];raw[k][200]^=1;all(banks[k],-1);assert(!snapshot_valid(k));
  raw[k][200]^=1;all(banks[k],(int)k);valid_mask|=1U<<k;reference(original,valid_mask);
  assert(pins_checked[k]==before+bank_families[k]+1);
 }
 /* Freed live storage cannot alias any immutable renderer-owned reference. */
 for(unsigned k=0;k<BANK_COUNT;k++) {
  bound((Sprite2_array){0,NULL},0,0);free(raw[k]);banks[k].data=NULL;all(banks[k],-1);
  Sprite2_array reload={sizes[k],copy[k]};bound(reload,logical[k],0);all(reload,(int)k);reference(original,7);
  copy[k][0]^=1;all(reload,-1);copy[k][0]^=1;all(reload,(int)k);
  bound((Sprite2_array){0,NULL},0,0);free(copy[k]);
 }
 for(unsigned k=0;k<BANK_COUNT;k++){free(original[k]);shutdown(k);}
 printf("source snapshot guards passed: %u checks across 20 families, 52 dependencies; 17 NEWSHD/45 records + 2 NEWSHS/records325,272 + 1 NEWSHP/records338-342; cold/warm, all slots, strict roles/sizes, reload/same-address cross-bank reuse, record-local and three-bank independence and epochs\n",checks);
 return 0;
}
'''



def run_bounded(command, log, *, compiler=False, sanitize=False):
    ceiling = (1024 if compiler else 512) * MIB

    def limits():
        resource.setrlimit(resource.RLIMIT_FSIZE, (OUTPUT_LIMIT, OUTPUT_LIMIT))
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        if compiler or not sanitize:
            resource.setrlimit(resource.RLIMIT_AS, (ceiling, ceiling))

    with log.open('wb') as stream:
        proc = subprocess.Popen(command, stdout=stream, stderr=subprocess.STDOUT,
                                env={**os.environ, 'ASAN_OPTIONS': 'detect_leaks=0',
                                     'UBSAN_OPTIONS': 'halt_on_error=1:print_stacktrace=1'},
                                preexec_fn=limits, start_new_session=True)
        peak = 0
        deadline = time.monotonic() + (90 if compiler else 15)
        try:
            while True:
                pid, status, usage = os.wait4(proc.pid, os.WNOHANG)
                if pid:
                    proc.returncode = os.waitstatus_to_exitcode(status)
                    peak = max(peak, usage.ru_maxrss * 1024)
                    if peak > ceiling:
                        raise RuntimeError('subprocess exceeded RSS bound')
                    break
                if time.monotonic() > deadline:
                    raise RuntimeError('bounded subprocess timed out')
                statusfile = Path('/proc') / str(proc.pid) / 'status'
                try:
                    for line in statusfile.read_text().splitlines():
                        if line.startswith('VmRSS:'):
                            peak = max(peak, int(line.split()[1]) * 1024)
                            if peak > ceiling:
                                raise RuntimeError('subprocess exceeded RSS bound')
                            break
                except FileNotFoundError:
                    pass
                if log.stat().st_size > OUTPUT_LIMIT:
                    raise RuntimeError('subprocess log exceeded output bound')
                time.sleep(0.01)
            if proc.returncode:
                raise RuntimeError(f'Command failed ({proc.returncode}); inspect {log}')
        finally:
            if proc.returncode is None:
                os.killpg(proc.pid, signal.SIGKILL)
                _, status, _ = os.wait4(proc.pid, 0)
                proc.returncode = os.waitstatus_to_exitcode(status)
    return peak


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--sanitize', action='store_true')
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    if any(args.out.iterdir()): raise RuntimeError('Select a new, empty output directory')
    if shutil.disk_usage(args.out).free < 5_000_000_000: raise RuntimeError('At least 5 GB free required')
    ten = (ROOT / 'src/asteroid1_ten_mirror.inc').read_text()
    renderer = (ROOT / 'src/render_mirror.c').read_text()
    assert 'asteroid1_shutdown();' in extract(renderer, 'render_mirror_hud_shutdown')
    helper = (ROOT / 'src/asteroid1_source_snapshot.inc').read_text()
    assert '0x913975450e0fc00d' in helper
    firing = (ROOT / 'src/asteroid1_firing325_mirror.inc').read_text()
    linked = (ROOT / 'src/render_mirror_asteroid_linked338.inc').read_text()
    pulsing = (ROOT / 'src/asteroid1_pulsing272_mirror.inc').read_text()
    assert 'firing325_shutdown();' in extract(renderer, 'render_mirror_hud_shutdown')
    assert 'ember269_shutdown();' in extract(renderer, 'render_mirror_hud_shutdown')
    assert 'linked338_shutdown();' in extract(renderer, 'render_mirror_hud_shutdown')
    assert 'pulsing272_shutdown();' in extract(renderer, 'render_mirror_hud_shutdown')
    pulsing_guard = extract(pulsing, 'pulsing272_source')
    assert 'firing325_source_bytes_match(bank.data,bank.size)' in pulsing_guard
    assert 'firing325_source(' not in pulsing_guard
    assert 'source_snapshot' not in pulsing.replace('source snapshot', '')
    assert 'firing325_source_snapshot.valid' not in extract(pulsing, 'pulsing272_shutdown')
    stamp = extract(ten, 'asteroid1_stamp').replace(
        ' uint64_t h=',
        ' if(n==42012)pins_checked[0]++;\n if(n==46566)pins_checked[1]++;\n'
        ' if(n==46204)pins_checked[2]++;\n uint64_t h=', 1)
    assert 'pins_checked[2]++' in stamp
    code = PRELUDE + stamp + helper + extract(ten, 'asteroid1_shutdown')
    for source, prefix, size, pin in [
            (firing, 'firing325', 46566, 'f22ec1295ced5d11'),
            (linked, 'linked338', 46204, 'e2413e3aeab4d908')]:
        declaration = re.search(r'static struct \{bool valid;Uint8 bytes\[' + str(size) +
                                r'\];\} ' + prefix + '_source_snapshot;', source)
        assert declaration, prefix
        matcher = extract(source, prefix + '_source_bytes_match')
        assert '0x' + pin in matcher, prefix
        code += declaration.group() + '\n' + matcher + extract(source, prefix + '_shutdown')
    code += extract(pulsing, 'pulsing272_shutdown')
    sources = []
    for name, prefix in FAMILIES:
        source = (renderer[renderer.index('/* Scheduled record269'):renderer.index('bool render_mirror_enemy_tile(')]
                  if name == 'ember269' else linked if name == 'linked338' else
                  (ROOT / 'src' / f'asteroid1_{name}_mirror.inc').read_text())
        pins = re.search(r'static const struct \{[^\n]+\} ' + prefix + r'_pins\[\d+\]=\{.*?\n\};', source, re.S)
        assert pins, prefix
        # Multiple art poses can share one source-record dependency.
        types = list(dict.fromkeys(int(t) for t in re.findall(r'\{(\d+),', pins.group())))
        if name == 'pulsing272':
            assert types == [272]
            assert '0x2f2c9491d2030153' in pins.group()
        if name == 'firing325':
            assert types == [325]
        if name == 'linked338':
            assert dict((int(t), pin.lower()) for t, pin in re.findall(
                r'\{(\d+),UINT64_C\(0x([0-9a-fA-F]+)\)\}', pins.group())) == LINKED338_PINS
        code += pins.group() + '\n'
        bank = 1 if name in ('firing325', 'pulsing272') else 2 if name == 'linked338' else 0
        sources.append((prefix, source, bank, types))
    assert len(sources) == 20 and sum(len(types) for _, _, _, types in sources) == 52
    for bank in range(3):
        assert sum(source_bank == bank for _, _, source_bank, _ in sources) == BANK_FAMILIES[bank]
        assert sum(len(types) for _, _, source_bank, types in sources if source_bank == bank) == BANK_RECORDS[bank]
    code += 'static uint64_t asteroid1_record_stamp(unsigned type){record_queries++;if(corrupt_record||type==corrupt_type)return 0;\n'
    for prefix, _, _, _ in sources:
        code += f' for(unsigned i=0;i<sizeof({prefix}_pins)/sizeof({prefix}_pins[0]);i++)if({prefix}_pins[i].type==type)return {prefix}_pins[i].record;\n'
    code += 'return 0;}\n'
    for prefix, source, _, _ in sources:
        code += extract(source, prefix + '_source')
    code += 'static bool (*guards[])(Sprite2_array)={' + ','.join(prefix + '_source' for prefix, _, _, _ in sources) + '};\n'
    code += 'static const unsigned types[FAMILY_COUNT][10]={' + ','.join(
        '{' + ','.join(map(str, types)) + '}' for _, _, _, types in sources) + '};\n'
    code += 'static const unsigned counts[FAMILY_COUNT]={' + ','.join(
        str(len(types)) for _, _, _, types in sources) + '};\n'
    code += 'static const unsigned family_bank[FAMILY_COUNT]={' + ','.join(
        str(bank) for _, _, bank, _ in sources) + '};\n' + MAIN
    harness = args.out / 'harness.c'
    harness.write_text(code)
    runs = []
    compiler_peak = runtime_peak = 0
    for mode in ['optimized'] + (['asan-ubsan'] if args.sanitize else []):
        exe = args.out / mode
        flags = ['cc', '-std=c99', '-Wall', '-Wextra', '-Werror', '-O2']
        if mode == 'asan-ubsan':
            flags += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-g']
        compiler_peak = max(compiler_peak, run_bounded([*flags, str(harness), '-o', str(exe)], args.out / (mode+'-compile.log'), compiler=True))
        log = args.out / (mode+'.log')
        runtime_peak = max(runtime_peak, run_bounded(
            [str(exe), *(str(args.data / filename) for filename in
                         ['newshd.shp', 'newshs.shp', 'newshp.shp'])],
            log, sanitize=mode=='asan-ubsan'))
        result_text=log.read_text().strip()
        runs.append(dict(mode=mode, result=result_text, binary_sha256=hashlib.sha256(exe.read_bytes()).hexdigest()))
    result = dict(runs=runs, helper_sha256=hashlib.sha256(helper.encode()).hexdigest(),
                  firing325_source_sha256=hashlib.sha256(firing.encode()).hexdigest(),
                  linked338_source_sha256=hashlib.sha256(linked.encode()).hexdigest(),
                  pulsing272_source_sha256=hashlib.sha256(pulsing.encode()).hexdigest(),
                  compiler_peak_rss_bytes=compiler_peak,runtime_peak_rss_bytes=runtime_peak,
                  compiler_address_space_limit_bytes=1024*MIB,runtime_rss_limit_bytes=512*MIB,
                  compiler_timeout_seconds=90,runtime_timeout_seconds=15,
                  output_limit_bytes=OUTPUT_LIMIT,minimum_free_disk_bytes=5_000_000_000,
                  families=20,record_dependencies=52,NEWSHD_families=17,NEWSHD_records=45,
                  NEWSHS_families=2,NEWSHS_records=[325,272],NEWSHP_families=1,NEWSHP_records=list(LINKED338_PINS),
                  source_bank_sizes=dict(zip(BANK_NAMES, BANK_SIZES)),
                  source_bank_pins={'NEWSHD': '913975450e0fc00d', 'NEWSHS': 'f22ec1295ced5d11',
                                    'NEWSHP': 'e2413e3aeab4d908'},
                  leak_sanitizer=False, scope='Extracted current production helpers, source predicates and shutdowns. Record-stamp stub checks all 52 dependency queries, including independently pinned325/272 sharing NEWSHS bytes; complete family suites validate real canonical77 records and drawing separately. Three independent strict-size source-bank snapshots verified in all directions, including same-address cross-bank reuse.')
    (args.out / 'receipt.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
