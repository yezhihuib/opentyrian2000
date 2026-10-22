#!/usr/bin/env python3
"""Ordinary-file HDA rejection/allocation controls, using production read_asset.

No original assets, game process, profiles, FIFO, devices or GUI are needed.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import tempfile
from run_render_boundary_tests import ROOT, extract


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt', required=True, type=Path)
    args = parser.parse_args()
    text = (ROOT / 'src/render_mirror.c').read_text(encoding='utf-8')
    body = extract(text, 'read_asset')
    enums = re.search(r'enum \{ ASSET_NEWSH2=.*?\};', text).group()
    source = '''#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef uint8_t Uint8;
typedef struct {bool initialized,valid;int bank,index,w,h,anchor_x,anchor_y,density;Uint8 *rgba;} Asset;
static bool asteroid_hd_enabled,fail_allocation;
static const char *game_probe_assets;
static size_t maximum_allocation,allocations;
static void *bounded_malloc(size_t n){assert(n<=43008);maximum_allocation=n;allocations++;return fail_allocation?NULL:malloc(n);}
#define malloc bounded_malloc
static struct {const Uint8 *rgba;char path[1024];} vulcan_shadow_resource[13],vulcan_shadow_coverage_resource[3];
static int vulcan_shadow_member(unsigned i){(void)i;return -1;}
''' + enums + '\n' + body + '''
int main(int argc,char **argv){
 assert(argc==4);game_probe_assets=argv[1];int d=atoi(argv[2]);fail_allocation=atoi(argv[3])!=0;
 Asset a={0};a.bank=8;a.index=1;a.w=12;a.h=14;
 bool accepted=read_asset(&a,d);assert(accepted==(a.rgba!=NULL));
 if(accepted)assert(a.density==d);else assert(a.density==0);
 printf("accepted=%d allocations=%zu max_allocation=%zu pixels=%d\\n",accepted,allocations,maximum_allocation,a.rgba!=NULL);
 free(a.rgba);return accepted?0:1;
}
'''
    report = {'status': 'PASS', 'function_sha256_lf_utf8': hashlib.sha256(body.encode()).hexdigest(),
              'scope': 'Production generic HDA reader, finite internal geometry, ordinary synthetic files and allocation failure; ASan+UBSan. No native Windows IO or complete-family acceptance claim.', 'cases': []}
    with tempfile.TemporaryDirectory(prefix='hda-boundary-') as temporary:
        root = Path(temporary)
        c, exe = root / 'test.c', root / 'test'
        c.write_text(source, encoding='utf-8')
        command = ['cc', '-std=c99', '-O1', '-g', '-Wall', '-Wextra', '-Werror', '-fsanitize=address,undefined',
                   '-fno-sanitize-recover=all', '-fno-omit-frame-pointer', '-no-pie', str(c), '-o', str(exe)]
        subprocess.run(command, check=True, timeout=60)
        for density in (4, 8):
            header = struct.pack('<4s6I', b'HDR1', 80001, density, 12, 14, 0, 0)
            payload = bytes(12 * 14 * density * density * 4)
            cases = [('valid', header + payload, 0), ('empty', b'', 1), ('short-header', header[:27], 1),
                     ('short-payload', header + payload[:-1], 1), ('extra-byte', header + payload + b'X', 1),
                     ('bad-magic', b'BAD!' + header[4:] + payload, 1), ('missing', None, 1)]
            for name, offset, value in [('wrong-id', 4, 80002), ('wrong-density', 8, 0xffffffff),
                                         ('max-width', 12, 0xffffffff), ('max-height', 16, 0xffffffff),
                                         ('wrong-anchor-x', 20, 0x80000000), ('wrong-anchor-y', 24, 1)]:
                changed = bytearray(header + payload)
                struct.pack_into('<I', changed, offset, value)
                cases.append((name, changed, 1))
            for name, data, expected in cases + [('allocation-failure', header + payload, 1)]:
                folder = root / (str(density) + '-' + name)
                folder.mkdir()
                if data is not None:
                    (folder / ('bullet-1-%d.hda' % density)).write_bytes(data)
                result = subprocess.run([str(exe), str(folder), str(density), str(int(name == 'allocation-failure'))],
                                        capture_output=True, text=True, timeout=5,
                                        env=dict(os.environ, ASAN_OPTIONS='detect_leaks=1:halt_on_error=1', UBSAN_OPTIONS='halt_on_error=1'))
                assert result.returncode == expected, (name, result.stdout, result.stderr)
                assert not result.stderr, result.stderr
                report['cases'].append({'density': density, 'name': name, 'exit': result.returncode, 'stdout': result.stdout.strip()})
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
