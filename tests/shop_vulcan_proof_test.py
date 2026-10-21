#!/usr/bin/env python3
"""Compile production shop provenance against actual types; pipe private tables in memory.
This is a focused proof/module harness, not native allocator or display evidence.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data', type=Path, required=True)
    p.add_argument('--sdl-root', type=Path, help='Optional extracted dependency sysroot')
    p.add_argument('--receipt', type=Path, required=True)
    p.add_argument('--sanitize', action='store_true')
    a = p.parse_args()
    registry = json.loads((ROOT/'assets/hd/global-assets-v1/registry.json').read_text())
    identity = registry['families'][4]['source_identity']['weapon_identity']
    payload = b''
    for provenance in identity['variant_source_provenance']:
        data = (a.data/provenance['file']).read_bytes()
        assert hashlib.sha256(data).hexdigest() == provenance['sha256']
        start = provenance['table_offset'] + 14
        payload += b''.join(data[start+i*80:start+(i+1)*80] for i in identity['record_indices'])
        start += (819+819)*80 + identity['port_index']*82
        payload += data[start:start+82]
    sources = [ROOT/'src/shop_vulcan.h', ROOT/'src/shop_vulcan_proof.inc', ROOT/'src/global_asset_registry.h',
               ROOT/'src/shots.h', ROOT/'src/episodes.h', ROOT/'src/player.h', Path(__file__),
               ROOT/'tests/shop_vulcan_proof_test.c']
    before = {str(x.relative_to(ROOT)): hashlib.sha256(x.read_bytes()).hexdigest() for x in sources}
    if a.sdl_root:
        inc = a.sdl_root/'usr/include'
        cflags = ['-I'+str(inc/'SDL2'), '-I'+str(inc/'x86_64-linux-gnu')]
    else:
        cflags = shlex.split(os.environ.get('SDL_CFLAGS') or subprocess.check_output(['sdl2-config', '--cflags'], text=True))
    with tempfile.TemporaryDirectory(prefix='shop-vulcan-proof-') as tmp:
        binary = Path(tmp)/'proof'
        cmd = shlex.split(os.environ.get('CC', 'cc')) + ['-std=c99','-O1','-g','-Wall','-Wextra',
              '-Werror=implicit-function-declaration','-I'+str(ROOT/'src')] + cflags
        if a.sanitize:
            cmd += ['-fsanitize=address,undefined','-fno-omit-frame-pointer','-no-pie']
        cmd += [str(ROOT/'tests/shop_vulcan_proof_test.c'), '-o', str(binary)]
        subprocess.run(cmd, check=True, timeout=120)
        result = subprocess.run([str(binary)], input=payload, capture_output=True, timeout=60,
                 env={**os.environ,'ASAN_OPTIONS':'detect_leaks=0:halt_on_error=1','UBSAN_OPTIONS':'halt_on_error=1:print_stacktrace=1'})
    stdout, stderr = result.stdout.decode(), result.stderr.decode()
    print(stdout+stderr, end='')
    unchanged = all(hashlib.sha256(x.read_bytes()).hexdigest()==before[str(x.relative_to(ROOT))] for x in sources)
    report = {'status':'PASS' if result.returncode==0 and unchanged else 'FAIL',
              'scope':'Isolated production shop provenance with actual header types and original raw table variants; manually initialized shots and read-only simple simulation oracle, not actual allocator or native display evidence',
              'returncode':result.returncode,'stdout':stdout,'stderr':stderr,
              'sanitizers':'ASan+UBSan (LSan disabled: ptrace environment)' if a.sanitize else 'none',
              'original_bytes_persisted':False,'sources_unchanged':unchanged,'source_sha256':before}
    a.receipt.parent.mkdir(parents=True, exist_ok=True)
    a.receipt.write_text(json.dumps(report, indent=2)+'\n')
    raise SystemExit(0 if report['status']=='PASS' else 1)

if __name__ == '__main__':
    main()
