#!/usr/bin/env python3
"""Synthetic-only strict C99 core verification, both plain and ASan/UBSan."""
from pathlib import Path
import os,subprocess,tempfile,sys
from contextlib import nullcontext
root=Path(__file__).resolve().parents[1]
with (nullcontext(sys.argv[1]) if len(sys.argv)>1 else tempfile.TemporaryDirectory(prefix='rear-p1-core-')) as directory:
    Path(directory).mkdir(parents=True,exist_ok=True)
    for test in ['rear_multi_p1_test.c','rear_multi_p1_provenance_test.c','rear_multi_p2_ownership_test.c','rear_multi_p3_mode2_ownership_test.c','rear_multi_p3_mode1_ownership_test.c','rear_multi_p4_mode1_ownership_test.c','rear_multi_p4_mode2_ownership_test.c','rear_multi_p5_mode2_ownership_test.c','rear_multi_p5_mode1_ownership_test.c','rear_multi_p6_mode1_ownership_test.c','rear_multi_p6_mode2_ownership_test.c','rear_multi_p7_mode1_ownership_test.c','rear_multi_p7_mode2_ownership_test.c','rear_multi_p8_mode1_ownership_test.c','rear_multi_p8_mode2_ownership_test.c','rear_multi_p9_mode1_ownership_test.c']:
        for sanitizer in ['', 'address,undefined']:
            exe=Path(directory)/(Path(test).stem+('-san' if sanitizer else '-plain'))
            cmd=['cc','-std=c99','-pedantic','-Wall','-Wextra','-Werror','-O1','-g','-I'+str(root/'src'),str(root/'tests'/test),str(root/'src/rear_multi_p1.c'),'-o',str(exe)]
            if sanitizer:cmd+=['-fsanitize='+sanitizer,'-fno-omit-frame-pointer']
            subprocess.run(cmd,check=True)
            subprocess.run([str(exe)],check=True,env={**os.environ,'ASAN_OPTIONS':os.environ.get('ASAN_OPTIONS','detect_leaks=0:halt_on_error=1'),'UBSAN_OPTIONS':os.environ.get('UBSAN_OPTIONS','halt_on_error=1')})
