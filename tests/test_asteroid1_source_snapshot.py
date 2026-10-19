#!/usr/bin/env python3
"""Bounded current-byte source guard and renderer-epoch regression tests.

Reads only the fifteen named production family includes, their shared snapshot
include, render_mirror.c, and the explicitly selected external newshd.shp.
Record stamps are stubbed here to count every dependency query; the fifteen full
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

ROOT = Path(__file__).resolve().parents[1]
FAMILIES = [('ten', 'asteroid1'), ('four', 'asteroid4'),
            ('common4', 'asteroid_common4'), ('random5', 'asteroid_random5'),
            ('goldwing', 'goldwing'), ('random43', 'asteroid_random43'), ('random85', 'asteroid_random85'), ('random123', 'asteroid_random123'), ('random95', 'asteroid_random95'), ('random114', 'asteroid_random114'),
            ('random133', 'asteroid_random133'), ('random152', 'asteroid_random152'),
            ('random286', 'asteroid_random286'), ('fork284', 'fork284'), ('capsule545', 'capsule545')]


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
static unsigned pins_checked,record_queries,checks;
static bool corrupt_record;
static unsigned corrupt_type;
enum { FAMILY_COUNT=15, RECORD_COUNT=42 };
static struct {struct {Uint8 *rgba;} member[10];} asteroid1_resources;
'''
MAIN = r'''
static void all(Sprite2_array bank,bool expected)
{
 unsigned before=record_queries;
 for(unsigned i=0;i<FAMILY_COUNT;i++){assert(guards[i](bank)==expected);checks++;}
 if(expected)assert(record_queries-before==RECORD_COUNT);
}
static void unchanged_reference(const Uint8 *original)
{assert(asteroid1_source_snapshot.valid&&!memcmp(asteroid1_source_snapshot.bytes,original,42012));}
int main(int argc,char **argv)
{
 assert(argc==2&&sizeof(asteroid1_source_snapshot.bytes)==42012);
 FILE *f=fopen(argv[1],"rb");assert(f);
 Uint8 *bank=malloc(42012),*second=malloc(42012),*original=malloc(42012);assert(bank&&second&&original);
 assert(fread(bank,1,42012,f)==42012&&fgetc(f)==EOF);fclose(f);
 memcpy(second,bank,42012);memcpy(original,bank,42012);
 Sprite2_array source={42012,bank};enemySpriteSheets[0]=source;enemySpriteSheetIds[0]=8;
 /* Cold exclusions must not read arbitrary pointers or initialize trust. */
 Sprite2_array foreign={42012,(Uint8 *)(uintptr_t)1};
 all((Sprite2_array){42012,NULL},false);all(foreign,false);
 enemySpriteSheets[0]=foreign;enemySpriteSheetIds[0]=1;all(foreign,false);
 enemySpriteSheets[0]=source;enemySpriteSheetIds[0]=8;
 spriteSheet8=source;all(source,false);memset(&spriteSheet8,0,sizeof(spriteSheet8));
 source.size=0;all(source,false);source.size=42011;all(source,false);source.size=42013;all(source,false);source.size=42012;
 assert(!asteroid1_source_snapshot.valid&&!pins_checked&&!record_queries);
 /* Cold invalid bytes never become a reference. Each family retries its pin. */
 bank[200]^=1;all(source,false);assert(!asteroid1_source_snapshot.valid&&pins_checked==FAMILY_COUNT&&!record_queries);
 bank[200]^=1;all(source,true);assert(pins_checked==FAMILY_COUNT+1);unchanged_reference(original);
 all(source,true);assert(pins_checked==FAMILY_COUNT+1);
 /* Full current bytes are compared, including equal-pointer changes in one tick. */
 const unsigned positions[]={0,1,200,21006,42010,42011};
 for(unsigned i=0;i<sizeof(positions)/sizeof(*positions);i++) {
  unsigned before=record_queries;bank[positions[i]]^=1;all(source,false);
  assert(record_queries==before&&pins_checked==FAMILY_COUNT+1);unchanged_reference(original);
  bank[positions[i]]^=1;all(source,true);
 }
 /* No accepted call skips its family record dependencies. */
 corrupt_record=true;unsigned before=record_queries;all(source,false);assert(record_queries-before==FAMILY_COUNT);
 corrupt_record=false;all(source,true);
 for(unsigned family=0;family<FAMILY_COUNT;family++) {
  for(unsigned k=0;k<counts[family];k++) {
   corrupt_type=types[family][k];before=record_queries;
   assert(!guards[family](source));assert(record_queries-before==k+1);checks++;
  }
 }
 corrupt_type=0;all(source,true);
 /* Warm metadata exclusions remain ahead of the byte comparison. */
 before=record_queries;enemySpriteSheetIds[0]=1;all(source,false);enemySpriteSheetIds[0]=8;
 spriteSheet8=source;all(source,false);memset(&spriteSheet8,0,sizeof(spriteSheet8));
 source.size--;all(source,false);source.size++;
 assert(record_queries==before&&pins_checked==FAMILY_COUNT+1);unchanged_reference(original);
 /* Any of the four loaded bank slots is valid; unloaded pointers are not. */
 for(unsigned slot=0;slot<4;slot++) {
  memset(enemySpriteSheets,0,sizeof(enemySpriteSheets));memset(enemySpriteSheetIds,0,sizeof(enemySpriteSheetIds));
  enemySpriteSheets[slot]=source;enemySpriteSheetIds[slot]=8;all(source,true);
 }
 memset(enemySpriteSheets,0,sizeof(enemySpriteSheets));memset(enemySpriteSheetIds,0,sizeof(enemySpriteSheetIds));
 Sprite2_array reloaded={42012,second};enemySpriteSheets[0]=reloaded;enemySpriteSheetIds[0]=8;
 all(source,false);all(reloaded,true);assert(pins_checked==FAMILY_COUNT+1);
 second[200]^=1;all(reloaded,false);unchanged_reference(original);second[200]^=1;all(reloaded,true);
 /* Same-address reuse never bypasses live bytes or re-pins changed bytes. */
 enemySpriteSheets[0]=source;bank[42011]^=1;all(source,false);memcpy(bank,second,42012);all(source,true);
 assert(pins_checked==FAMILY_COUNT+1);unchanged_reference(original);
 /* Actual production shutdown frees owned art and revokes shared trust. */
 for(unsigned i=0;i<10;i++){asteroid1_resources.member[i].rgba=malloc(16);assert(asteroid1_resources.member[i].rgba);}
 asteroid1_shutdown();assert(!asteroid1_source_snapshot.valid);
 for(unsigned i=0;i<10;i++)assert(!asteroid1_resources.member[i].rgba);
 bank[42011]^=1;all(source,false);assert(!asteroid1_source_snapshot.valid&&pins_checked==2*FAMILY_COUNT+1);
 bank[42011]^=1;all(source,true);assert(pins_checked==2*FAMILY_COUNT+2);unchanged_reference(original);
 asteroid1_shutdown();asteroid1_shutdown();assert(!asteroid1_source_snapshot.valid);
 /* Live bank release does not leave an aliased private reference. */
 all(source,true);assert(pins_checked==2*FAMILY_COUNT+3);unchanged_reference(original);
 memset(enemySpriteSheets,0,sizeof(enemySpriteSheets));free(bank);source.data=NULL;all(source,false);
 unchanged_reference(original);
 enemySpriteSheets[0]=reloaded;all(reloaded,true);assert(pins_checked==2*FAMILY_COUNT+3);unchanged_reference(original);
 second[0]^=1;all(reloaded,false);second[0]^=1;all(reloaded,true);assert(pins_checked==2*FAMILY_COUNT+3);
 free(second);free(original);asteroid1_shutdown();
 printf("source snapshot guards passed: %u checks across 15 families, 42 record dependencies, cold/warm corruption, role/size/pointer/reload/address reuse and renderer epochs\n",checks);
 return 0;
}
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--sanitize', action='store_true')
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    ten = (ROOT / 'src/asteroid1_ten_mirror.inc').read_text()
    renderer = (ROOT / 'src/render_mirror.c').read_text()
    assert 'asteroid1_shutdown();' in extract(renderer, 'render_mirror_hud_shutdown')
    helper = (ROOT / 'src/asteroid1_source_snapshot.inc').read_text()
    stamp = extract(ten, 'asteroid1_stamp').replace(' uint64_t h=', ' if(n==42012)pins_checked++;\n uint64_t h=', 1)
    code = PRELUDE + stamp + helper + extract(ten, 'asteroid1_shutdown')
    sources = []
    for name, prefix in FAMILIES:
        source = (ROOT / 'src' / f'asteroid1_{name}_mirror.inc').read_text()
        pins = re.search(r'static const struct \{[^\n]+\} ' + prefix + r'_pins\[\d+\]=\{.*?\n\};', source, re.S)
        assert pins, prefix
        code += pins.group() + '\n'
        sources.append((prefix, source))
    code += 'static uint64_t asteroid1_record_stamp(unsigned type){record_queries++;if(corrupt_record||type==corrupt_type)return 0;\n'
    for prefix, _ in sources:
        code += f' for(unsigned i=0;i<sizeof({prefix}_pins)/sizeof({prefix}_pins[0]);i++)if({prefix}_pins[i].type==type)return {prefix}_pins[i].record;\n'
    code += 'return 0;}\n'
    for prefix, source in sources:
        code += extract(source, prefix + '_source')
    code += 'static bool (*guards[])(Sprite2_array)={' + ','.join(prefix + '_source' for prefix, _ in sources) + '};\n'
    code += 'static const unsigned types[15][10]={' + ','.join('{' + ','.join(re.findall(r'\{(\d+),', re.search(r'static const struct \{[^\n]+\} ' + prefix + r'_pins\[\d+\]=\{.*?\n\};', source, re.S).group())) + '}' for prefix, source in sources) + '};\n'
    code += 'static const unsigned counts[15]={10,4,4,3,1,3,3,3,2,2,2,2,1,1,1};\n' + MAIN
    harness = args.out / 'harness.c'
    harness.write_text(code)
    runs = []
    for mode in ['optimized'] + (['asan-ubsan'] if args.sanitize else []):
        exe = args.out / mode
        flags = ['cc', '-std=c99', '-Wall', '-Wextra', '-Werror', '-O2']
        if mode == 'asan-ubsan':
            flags += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer', '-g']
        def compile_limits():
            resource.setrlimit(resource.RLIMIT_AS, (1024 * 1024**2,) * 2)
        subprocess.run([*flags, str(harness), '-o', str(exe)], check=True, preexec_fn=compile_limits)
        def runtime_limits():
            if mode == 'optimized':
                resource.setrlimit(resource.RLIMIT_AS, (512 * 1024**2,) * 2)
            resource.setrlimit(resource.RLIMIT_CPU, (10,) * 2)
        result = subprocess.run([str(exe), str(args.data / 'newshd.shp')], check=True, timeout=15,
                                capture_output=True, text=True, preexec_fn=runtime_limits,
                                env={**os.environ, 'ASAN_OPTIONS': 'detect_leaks=0'})
        (args.out / (mode + '.log')).write_text(result.stdout)
        runs.append(dict(mode=mode, result=result.stdout.strip(), binary_sha256=hashlib.sha256(exe.read_bytes()).hexdigest()))
    result = dict(runs=runs, helper_sha256=hashlib.sha256(helper.encode()).hexdigest(),
                  peak_child_rss_bytes=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss * 1024,
                  leak_sanitizer=False, scope='Extracted current production helper, source predicates and shutdown. Record-stamp stub checks dependency queries; complete family suites validate real records and drawing separately.')
    (args.out / 'receipt.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
