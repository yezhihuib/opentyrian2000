#!/usr/bin/env python3
"""Actual lower/cap loader and selected-base atomic fallback tests; no game."""
from pathlib import Path
import argparse,hashlib,json,os,shlex,struct,subprocess
p=argparse.ArgumentParser();p.add_argument('--src',type=Path,required=True);p.add_argument('--lower-pack',type=Path,required=True);p.add_argument('--cap-bundle',type=Path,required=True);p.add_argument('--selected-pack',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--sanitize',action='store_true');a=p.parse_args()
src=a.src.resolve();root=a.output.resolve()
if a.output.is_symlink() or root==src or src in root.parents or root in src.parents:raise SystemExit('output must be outside source')
root.mkdir(parents=True,exist_ok=False);here=Path(__file__).resolve().parent
cc=shlex.split(os.environ.get('CC','cc'));flags=['-std=c11','-O2','-Wall','-Wextra','-Werror','-DPLATEAU_CAP_MATERIAL_TEST','-I'+str(src),'-Wl,--wrap=malloc']
flags+=shlex.split(subprocess.check_output(['pkg-config','--cflags','sdl2'],text=True))
if a.sanitize:flags+=['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer']
exe=root/'validate-cap';subprocess.run(cc+flags+[str(src/x) for x in ['world_material.c','world_material_fast.c','ground101_material.c','plateau_cap_material.c']]+[str(here.parent/'world-material/fnv_reference.c'),str(here/'validate_loader.c'),'-o',str(exe)],check=True)
blob=a.cap_bundle.read_bytes();assert len(blob)==3397820
shared=root/'input';shared.mkdir();empty=root/'empty';empty.mkdir();receipt={}
def run(name,data,load=False,sources=False,alloc=0,mismatch=0,lower=True,directory=None):
    path=shared/'plateau-cap-world-material.pcap'
    if path.exists():path.unlink()
    if data is not None:path.write_bytes(data)
    result=subprocess.run([str(exe),str(a.lower_pack.resolve() if lower else empty),str(shared if directory is None else directory),str(a.selected_pack.resolve()),str(int(load)),str(int(sources)),str(alloc),str(mismatch),str(int(lower))],capture_output=True,text=True)
    if result.returncode:raise AssertionError((name,result.stdout,result.stderr))
    receipt[name]={'exit':0,'cap_enabled':sources,'payload_allocations':alloc,'stdout':result.stdout,'stderr':result.stderr}
def word(offset,n):return blob[:offset]+struct.pack('<I',n)+blob[offset+4:]
def flip(offset):return blob[:offset]+bytes([blob[offset]^1])+blob[offset+1:]
run('missing',None);run('empty-path',None,directory='');run('overlong-path',None,directory='a'*1100)
run('truncated-header',blob[:31]);run('truncated-payload',blob[:-1]);run('extra-byte',blob+b'\0');run('bad-magic',b'X'+blob[1:])
for name,off,n in [('version',8,2),('count',12,12),('huge-count',12,0xffffffff),('width',16,769),('height',20,895),('density',24,4),('size',28,3397631),('huge-size',28,0xffffffff),('role',32,101),('id',36,109),('enabled',40,0),('guard-enabled',40+2*12,1)]:run('bad-'+name,word(off,n))
run('duplicate-id',word(36+12,96));run('reordered-records',blob[:32]+blob[44:56]+blob[32:44]+blob[56:])
for name,offset in [('atlas',188),('alpha',191),('mask',188+2752512),('base109',188+3225600)]:run('corrupt-'+name,flip(offset),alloc=1)
run('valid',blob,True,True,1)
for identity in [96,97,98,99,100,106,107,108,109,110,118,119,120]:run('selected-mismatch-'+str(identity),blob,True,False,1,identity)
run('missing-lower-dependency',blob,lower=False)
(shared/'plateau-cap-world-material.pcap').unlink()
(root/'loader-checks.json').write_text(json.dumps({'status':'passed','cases':receipt,'bundle_sha256':hashlib.sha256(blob).hexdigest()},indent=2)+'\n')
print('PASS',len(receipt),'cap-loader/source-mismatch cases; exact lower fallback, single bounded allocation, no frame allocations')
