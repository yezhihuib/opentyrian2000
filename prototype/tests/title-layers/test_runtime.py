#!/usr/bin/env python3
"""Compile the actual title compositor against synthetic fixtures; never run the game."""
from pathlib import Path
import argparse, os, shlex, subprocess, tempfile
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MASK_ON = 255

def fnv(data):
    h = 14695981039346656037
    for value in data:
        h = ((h ^ value) * 1099511628211) & ((1 << 64) - 1)
    return h

def logo_fixture(asset, w, h):
    indices = bytearray(w*h)
    mask = bytearray(w*h)
    rle = bytearray()
    for y in range(h):
        if y < 2 or y >= h-2:
            rle.append(254)
            continue
        rle.extend((255, 2))
        for x in range(2, w-2):
            p = y*w+x
            if (x+y) % 19 == 0:
                rle.append(253)
            else:
                indices[p] = (x*7+y*11+asset) % 239
                mask[p] = MASK_ON
                rle.append(indices[p])
        rle.append(254)
    return indices, mask, rle

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sanitize', action='store_true')
    args = parser.parse_args()
    palette = bytes(v for i in range(256) for v in ((i*3)%256, (i*7)%256, (i*13)%256))
    identities = {'PIC4': fnv(bytes((i*7)%239 for i in range(64000))), 'PAL': fnv(palette)}
    for asset, w, h in ((146,304,121),(151,162,64)):
        for suffix, data in zip(('INDEX','MASK','RLE'),logo_fixture(asset,w,h)):
            identities[f'{asset}_{suffix}'] = fnv(data)
    flags = [f'-DTITLE_{name}_FNV=UINT64_C(0x{value:016x})' for name,value in identities.items()]
    cflags = shlex.split(subprocess.check_output(['pkg-config','--cflags','sdl2'],text=True))
    libs = shlex.split(subprocess.check_output(['pkg-config','--libs','sdl2'],text=True))
    with tempfile.TemporaryDirectory(prefix='title-layer-unit-') as tmp:
        exe = str(Path(tmp)/'test-title-layers')
        cmd = [os.environ.get('CC','cc'),'-std=c99','-O1' if args.sanitize else '-O2','-g','-Wall','-Wextra','-Werror','-I'+str(ROOT/'src')]
        cmd += cflags + flags + [str(HERE/'test_runtime.c'),'-o',exe] + libs
        if args.sanitize:
            cmd += ['-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie']
        subprocess.run(cmd,check=True)
        subprocess.run([exe,tmp],check=True,timeout=300,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1'))
if __name__ == '__main__':
    main()
