#!/usr/bin/env python3
"""Original-input HUD1 adapter oracle with real SDL software scaling and ASan/UBSan.

Original bytes are decoded read-only and passed on stdin, never saved as fixtures.
The parent scene witness is controlled here; native integrated scenes are separate.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import tempfile
from shared_hud_reconstruction import extract, original_payload

ROOT = Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--data',type=Path,required=True)
    ap.add_argument('--receipt',type=Path)
    ap.add_argument('--sanitize',action='store_true')
    a=ap.parse_args()
    overlay=ROOT/'experimental/level2-family/src'
    paths=[overlay/'family_static_hud_mirror.inc',overlay/'render_mirror.c',overlay/'b313_family_canvas_mirror.inc',ROOT/'src/gameplay_hud.c',ROOT/'src/gameplay_hud.h',ROOT/'tests/family_static_hud_test.c']
    pins={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    src=(overlay/'render_mirror.c').read_text()
    canvas=(overlay/'b313_family_canvas_mirror.inc').read_text()
    helpers='\n'.join(extract(src,n) for n in ('hud_sprite_decode','hud_runtime_compatible','shared_hud_palette_matches'))
    helpers+='\n'.join(extract(canvas,n) for n in ('family_indexed','family_rgb'))
    pkg=shlex.split(os.environ.get('PKG_CONFIG','pkg-config'))
    flags=shlex.split(subprocess.check_output(pkg+['--cflags','sdl2'],text=True))
    libs=shlex.split(subprocess.check_output(pkg+['--libs','sdl2'],text=True))
    results=[]
    with tempfile.TemporaryDirectory(prefix='family-static-hud-') as directory:
        temp=Path(directory)
        (temp/'family_static_hud_helpers.inc').write_text(helpers)
        exe=temp/'test'
        cmd=shlex.split(os.environ.get('CC','cc'))+['-std=c99','-O1','-g','-Wall','-Wextra','-Werror','-I'+str(temp),'-I'+str(overlay),'-I'+str(ROOT/'src')]+flags
        if a.sanitize:cmd+=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-no-pie']
        cmd+=[str(ROOT/'tests/family_static_hud_test.c'),str(ROOT/'src/gameplay_hud.c'),'-o',str(exe)]+libs
        subprocess.run(cmd,check=True)
        raw=original_payload(a.data.resolve())
        for case in ('valid','missing','corrupt'):
            work=temp/case;resource=work/'assets/hd/shared-ui-v1';resource.mkdir(parents=True)
            if case=='valid':(resource/'gameplay-hud-v1.hda').symlink_to(ROOT/'assets/hd/shared-ui-v1/gameplay-hud-v1.hda')
            if case=='corrupt':(resource/'gameplay-hud-v1.hda').write_bytes(b'invalid')
            result=subprocess.run([str(exe),case],cwd=work,input=raw,capture_output=True,env={**os.environ,'SDL_VIDEODRIVER':'dummy','ASAN_OPTIONS':'detect_leaks=0:halt_on_error=1','UBSAN_OPTIONS':'halt_on_error=1'})
            print(result.stdout.decode(),end='');print(result.stderr.decode(),end='')
            results.append({'case':case,'returncode':result.returncode,'stdout':result.stdout.decode(),'stderr':result.stderr.decode()})
            if result.returncode:break
    receipt={'status':'PASS' if all(r['returncode']==0 for r in results) and len(results)==3 else 'FAIL','sanitizers':'ASan+UBSan' if a.sanitize else 'none','leak_detection':'disabled','original_bytes_persisted':False,'source_sha256':pins,'source_unchanged':all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in pins.items()),'results':results}
    if a.receipt:a.receipt.write_text(json.dumps(receipt,indent=2)+'\n')
    return 0 if receipt['status']=='PASS' else 1

if __name__=='__main__':raise SystemExit(main())
