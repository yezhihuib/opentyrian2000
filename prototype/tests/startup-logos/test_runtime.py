#!/usr/bin/env python3
"""Synthetic production MFG1 loader/presenter tests; never launches the game."""
from pathlib import Path
import argparse, os, shlex, subprocess, tempfile
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]
def fnv(b):
 h=14695981039346656037
 for v in b:h=((h^v)*1099511628211)&((1<<64)-1)
 return h

def main():
 p=argparse.ArgumentParser();p.add_argument('--sanitize',action='store_true');p.add_argument('--leak-check',action='store_true');a=p.parse_args()
 text=(ROOT/'src/startup_logos.c').read_text()
 names=['PIC10_INDEX','PIC10_PALETTE','PIC12_INDEX','PIC12_PALETTE']
 guards=['720d8ce9dda3f5f4','b50ac0b9e5f1a73d','98d7341da720b7ab','20261a06b61711d5']
 for name,guard in zip(names,guards):assert '#define MFG_'+name+'_FNV UINT64_C(0x'+guard+')' in text
 flags=[]
 for card in range(2):
  source=bytes((i*7+card*19)%253 for i in range(64000))
  palette=bytes(v for i in range(256) for v in ((i*3+card*5)%256,(i*7+card*11)%256,(i*13+card*17)%256))
  for name,b in [('INDEX',source),('PALETTE',palette)]:flags+=['-DMFG_PIC%d_%s_FNV=UINT64_C(0x%016x)'%(10+card*2,name,fnv(b))]
 cflags=shlex.split(subprocess.check_output(['pkg-config','--cflags','sdl2'],text=True))
 libs=shlex.split(subprocess.check_output(['pkg-config','--libs','sdl2'],text=True))
 with tempfile.TemporaryDirectory(prefix='mfg-unit-') as tmp:
  cmd=[os.environ.get('CC','cc'),'-std=c99','-O1' if a.sanitize else '-O2','-g','-Wall','-Wextra','-Werror','-I'+str(ROOT/'src')]+cflags+flags+[str(HERE/'test_runtime.c'),'-o',tmp+'/test']+libs
  if a.sanitize:cmd+=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie']
  subprocess.run(cmd,check=True)
  subprocess.run([tmp+'/test',tmp],check=True,timeout=180,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=%d:halt_on_error=1'%a.leak_check,UBSAN_OPTIONS='halt_on_error=1'))
if __name__=='__main__':main()
