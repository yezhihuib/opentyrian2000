#!/usr/bin/env python3
"""Synthetic production-module tests. No game entrypoint or original font pixels."""
from pathlib import Path
import argparse, importlib.util, os, re, shlex, struct, subprocess, tempfile
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
spec=importlib.util.spec_from_file_location('title_fixture',HERE.parent/'title-layers/test_runtime.py')
classic=importlib.util.module_from_spec(spec);spec.loader.exec_module(classic)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--sanitize',action='store_true');args=parser.parse_args()
    text=(ROOT/'src/fonthand.c').read_text().split('const int font_ascii[256] =',1)[1].split('};',1)[0]
    mapping=list(map(int,re.findall(r'-?\d+',re.sub(r'//[^\n]*','',text))))
    assert len(mapping)==256
    metrics=bytearray();encoded=bytearray();mask=bytearray()
    for gid in range(85):
        w,h=2+gid%3,3+gid%2
        blank=gid in [60,63,64,65,66,67,68,69,84]
        rle=bytes(254 for _ in range(h)) if blank else bytes(253 if (gid+x+y)%5==0 else 3+(gid+x+3*y)%13 for y in range(h) for x in range(w))
        metrics+=struct.pack('<3H',w,h,w+1);encoded+=struct.pack('<3H',w,h,len(rle))+rle;mask.append(0 if blank else 255)
    pins={'MAP':classic.fnv(struct.pack('<256i',*mapping)),'METRICS':classic.fnv(metrics),'ENCODED':classic.fnv(encoded),'INK':classic.fnv(mask)}
    palette=bytes(v for i in range(256) for v in ((i*3)%256,(i*7)%256,(i*13)%256))
    ids={'PIC4':classic.fnv(bytes((i*7)%239 for i in range(64000))),'PAL':classic.fnv(palette)}
    for asset,w,h in ((146,304,121),(151,162,64)):
        for suffix,data in zip(('INDEX','MASK','RLE'),classic.logo_fixture(asset,w,h)):ids[f'{asset}_{suffix}']=classic.fnv(data)
    flags=[f'-DTITLE_{k}_FNV=UINT64_C(0x{v:016x})' for k,v in ids.items()]+[f'-DTITLE_MENU_{k}_FNV=UINT64_C(0x{v:016x})' for k,v in pins.items()]
    with tempfile.TemporaryDirectory(prefix='title-menu-unit-') as tmp:
        base=Path(tmp);header=base/'map.h';header.write_text('const int font_ascii[256]={'+','.join(map(str,mapping))+'};\n')
        cmd=[os.environ.get('CC','cc'),'-std=c99','-O1' if args.sanitize else '-O2','-g','-Wall','-Wextra','-Werror','-I'+str(ROOT/'src'),'-include',str(header)]+flags
        cmd+=shlex.split(subprocess.check_output(['pkg-config','--cflags','sdl2'],text=True))+[str(HERE/'test_runtime.c'),'-lm','-o',str(base/'test')]+shlex.split(subprocess.check_output(['pkg-config','--libs','sdl2'],text=True))
        if args.sanitize:cmd+=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie']
        subprocess.run(cmd,check=True)
        subprocess.run([str(base/'test'),tmp],check=True,timeout=300,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1'))
if __name__=='__main__':main()
