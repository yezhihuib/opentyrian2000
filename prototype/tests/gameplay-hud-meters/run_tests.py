#!/usr/bin/env python3
"""Pure synthetic HUM2 parser/event/raster/material tests; no original assets."""
import argparse,os,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def main():
 p=argparse.ArgumentParser();p.add_argument('--sanitize',action='store_true');p.add_argument('--leak-check',action='store_true');a=p.parse_args()
 text=(ROOT/'src/gameplay_hud_meters.c').read_text()
 for value in ('14c1441f3d5dc0e2','5e80e83992be2927','92ce2a65c65f67db','33f13810daec0125','c4231771a5413868','1d129d23c2edc134','fcc77c108870c9db'):assert f'UINT64_C(0x{value})' in text
 with tempfile.TemporaryDirectory(prefix='hum2-') as temp:
  cmd=[os.environ.get('CC','cc'),'-std=c99','-O1' if a.sanitize else '-O2','-g','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-I'+str(ROOT/'src'),str(HERE/'test_meters.c'),'-o',temp+'/test']
  if a.sanitize:cmd+=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie']
  subprocess.run(cmd,check=True);subprocess.run([temp+'/test',temp],check=True,timeout=240,env=dict(os.environ,ASAN_OPTIONS=f'detect_leaks={int(a.leak_check)}:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1'))
if __name__=='__main__':main()
