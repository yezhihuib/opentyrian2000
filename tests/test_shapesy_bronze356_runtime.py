#!/usr/bin/env python3
"""Focused opaque356 matrix using the unchanged old28 extraction/build driver.

Actual finite runtime include, actual indexed blitter and generated tile payload.
Only standalone fixtures are mutated; no production game, original or old28 art writes.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,struct,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
OLD_DRIVER_SHA256='e03aaeb9c5fdc7593be8ca0ff05533468de2869e87b26566ca645fbf17641252'
SHA=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--pack',type=Path,required=True);p.add_argument('--sanitize',action='store_true');p.add_argument('--sdl-include',action='append',default=[]);a=p.parse_args()
    assert not a.out.exists(),'fresh external proof directory required'
    assert ROOT not in a.out.resolve().parents
    path=ROOT/'tests/test_shapesy_platform_runtime.py';assert SHA(path)==OLD_DRIVER_SHA256,'historical old28 driver drift'
    spec=importlib.util.spec_from_file_location('bronze356_old_runtime',path);base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
    # Reuse only the immutable original source registry, clear and frame helpers.
    helpers=base.CHECKS[:base.CHECKS.index('static void verify_row(')]
    base.CHECKS=helpers+(ROOT/'tests/shapesy_bronze356_runtime.c.inc').read_text()
    source_before={q.relative_to(ROOT).as_posix():SHA(q) for q in (ROOT/'src').rglob('*') if q.is_file()}
    inputs={str(q.resolve()):SHA(q) for q in a.pack.glob('*.hda')}
    assert a.pack.joinpath('terrain-shapesy-356-8.hda').is_file()
    sys.argv=[str(path),'--data',str(a.data),'--out',str(a.out),'--pack',str(a.pack),'--positive-only']
    if a.sanitize:sys.argv.append('--sanitize')
    for include in a.sdl_include:sys.argv+=['--sdl-include',include]
    base.main()
    exe=a.out/'runtime';data=a.out/'original-sources.bin';rows=[]
    kinds=('missing','payload','magic','role','density','width','height','anchor','short','trailing','alpha')
    for kind in kinds+('bronze-only',):
        target=a.out/'negative'/kind;target.mkdir(parents=True)
        for source in a.pack.glob('*.hda'):
            if source.name=='terrain-shapesy-356-8.hda':continue
            if kind!='bronze-only':(target/source.name).symlink_to(source.resolve())
        raw=bytearray((a.pack/'terrain-shapesy-356-8.hda').read_bytes())
        if kind!='missing':
            if kind=='payload':raw[40]^=1
            elif kind=='magic':raw[:4]=b'NOPE'
            elif kind=='short':raw=raw[:-1]
            elif kind=='trailing':raw+=b'x'
            elif kind=='alpha':raw[31]=0
            elif kind!='bronze-only':struct.pack_into('<I',raw,dict(role=4,density=8,width=12,height=16,anchor=20)[kind],1)
            (target/'terrain-shapesy-356-8.hda').write_bytes(raw)
        result=subprocess.run([str(exe),str(data),str(target),'bronze-only' if kind=='bronze-only' else 'reject'],capture_output=True,text=True)
        (target/'result.log').write_text(result.stdout+result.stderr);assert result.returncode==0,(kind,result.stdout,result.stderr)
        rows.append(dict(case=kind,status='PASS'))
    assert source_before=={q.relative_to(ROOT).as_posix():SHA(q) for q in (ROOT/'src').rglob('*') if q.is_file()}
    assert all(SHA(Path(q))==h for q,h in inputs.items()) and SHA(path)==OLD_DRIVER_SHA256
    report=dict(status='PASS',source_sha256=source_before,pack_sha256=inputs,old_driver_sha256=OLD_DRIVER_SHA256,harness_sha256=SHA(a.out/'harness.c'),cases=rows,source_and_art_unchanged=True,natural_gameplay=False)
    (a.out/'bronze356-receipt.json').write_text(json.dumps(report,indent=2)+'\n');print('OPAQUE356 FOCUSED RUNTIME PASS')
if __name__=='__main__':main()
