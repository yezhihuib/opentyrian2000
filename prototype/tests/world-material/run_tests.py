#!/usr/bin/env python3
"""Build/run standalone synthetic tests against an explicitly supplied src directory."""
from pathlib import Path
import argparse, os, shlex, subprocess
p=argparse.ArgumentParser()
p.add_argument('--src',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
approved=p.add_mutually_exclusive_group()
approved.add_argument('--approved-bundle',type=Path)
approved.add_argument('--approved-pack',type=Path)
p.add_argument('--rejected-bundle',type=Path)
p.add_argument('--sanitize',action='store_true')
a=p.parse_args();src=a.src.resolve();out=a.output.resolve();
if out.exists() or a.output.is_symlink():raise SystemExit('output must be a fresh directory')
if out==src or out in src.parents or src in out.parents:raise SystemExit('output must be outside source')
out.mkdir(parents=True);here=Path(__file__).resolve().parent
cc=shlex.split(os.environ.get('CC','cc'));cflags=['-std=c11','-O2','-Wall','-Wextra','-Werror','-I'+str(src)]
if a.sanitize:cflags+=['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer']
# game_probe.h uses SDL declarations, but these standalone tests do not link SDL.
sdl=shlex.split(subprocess.check_output(['pkg-config','--cflags','sdl2'],text=True))
base=[str(src/'world_material.c')];fast=base+[str(src/'world_material_fast.c')]
for name,inputs,flags in [
 ('test-world',base+[str(here/'test_world_material.c')],[]),
 ('test-fast',fast+[str(here/'test_fast.c')],[]),
 ('validate-portable',fast+[str(src/'ground101_material.c'),str(here/'fnv_reference.c'),str(here/'validate_portable.c')],sdl+['-DGROUND101_MATERIAL_TEST','-Wl,--wrap=malloc'])]:
 subprocess.run(cc+cflags+flags+inputs+['-o',str(out/name)],check=True)
 if name!='validate-portable':subprocess.run([str(out/name)],check=True)
cmd=['python3',str(here/'check_loader.py'),'--validator',str(out/'validate-portable'),'--output',str(out/'loader')]
if a.approved_bundle:cmd+=['--approved-bundle',str(a.approved_bundle.resolve())]
if a.approved_pack:cmd+=['--approved-pack',str(a.approved_pack.resolve())]
if a.rejected_bundle:cmd+=['--rejected-bundle',str(a.rejected_bundle.resolve())]
subprocess.run(cmd,check=True)
# Verify the opt-in trace build compiles without turning default traces on.
subprocess.run(cc+cflags+sdl+['-DGROUND101_MATERIAL_TRACE','-c',str(src/'ground101_material.c'),'-o',str(out/'trace-opt-in.o')],check=True)
print('PASS standalone tests and optional-trace compile; no game process or capture')
