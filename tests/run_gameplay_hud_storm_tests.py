#!/usr/bin/env python3
"""Entirely synthetic standalone C/UBSan/ASan suite; no SDL/game data needed."""
from pathlib import Path
import os,struct,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[1]
fnv=lambda b:__import__('functools').reduce(lambda h,v:((h^v)*1099511628211)&((1<<64)-1),b,14695981039346656037)
with tempfile.TemporaryDirectory(prefix='storm-tests-') as directory:
    p=Path(directory)
    raw=b''.join(bytes([255,3]+[192+(x+y)%16 for x in range(3,25)]) for y in range(13))
    indices=b''.join(bytes([0]*3+[192+(x+y)%16 for x in range(3,25)]) for y in range(13))
    coverage=bytes([0]*3+[255]*22)*13
    pal=bytes(c for i in range(256) for c in [i,255-i,i^0x55])
    payload=b''
    for n in [2000,8000]:
        a=bytes([0,128,255][i%3] for i in range(n));v=bytes(197+i%5 if a[i] else 0 for i in range(n));payload+=v+a
    pins={'SOURCE_BYTES':len(raw),'RAW_FNV':fnv(raw),'INDICES_FNV':fnv(indices),'COVERAGE_FNV':fnv(coverage),'PIC3_FNV':fnv(bytes([17])*64000),'PALETTE_FNV':fnv(pal),'ART_FNV':fnv(payload)}
    (p/'storm_test_pins.h').write_text('\n'.join(f'#define HUD_STORM_{k} UINT64_C(0x{v:x})' for k,v in pins.items())+'\n')
    h=struct.pack('<4s9I7Q',b'HSI1',1,25,5,2,20000,25,13,len(raw),0,*[pins[k] for k in ['RAW_FNV','INDICES_FNV','COVERAGE_FNV','PIC3_FNV','ART_FNV','PALETTE_FNV']],0)
    resource=h+payload;(p/'gameplay-hud-storm-label-v1.hda').write_bytes(resource)
    (p/'alternate').mkdir();(p/'alternate/gameplay-hud-storm-label-v1.hda').write_bytes(resource)
    bad=[resource[:-1],resource+b'x',b'']
    for off in [0,4,8,12,16,20,24,28,32,36,40,48,56,64,72,80,88,96,2095]:
        b=bytearray(resource);b[off]^=1;bad.append(bytes(b))
    assert len(bad)==22
    for i,b in enumerate(bad):
        q=p/f'bad{i}';q.mkdir();(q/'gameplay-hud-storm-label-v1.hda').write_bytes(b)
    (p/'bad22').mkdir() # missing
    (p/'bad23').mkdir();os.mkfifo(p/'bad23/gameplay-hud-storm-label-v1.hda')
    for test in ['gameplay_hud_storm_test.c','gameplay_hud_storm_adapter_test.c']:
        for sanitizer in ['', 'undefined,address']:
            exe=p/(test+('-san' if sanitizer else '-plain'))
            cmd=['cc','-std=c99','-Wall','-Wextra','-Werror','-pedantic','-O1','-g','-I',str(p),str(ROOT/'tests'/test),'-o',str(exe)]
            if sanitizer:cmd+=['-fsanitize='+sanitizer,'-fno-omit-frame-pointer']
            subprocess.run(cmd,check=True);subprocess.run([str(exe),str(p)],check=True,env={**os.environ,'ASAN_OPTIONS':os.environ.get('ASAN_OPTIONS','detect_leaks=0')})
