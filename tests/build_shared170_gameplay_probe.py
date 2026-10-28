#!/usr/bin/env python3
"""Build only identical test-only audit TUs over source-bound already-fresh objects.

No production checkout/build is modified; no fresh production-config claim.
The controlled170 environment flag is absent during natural bronze356 runs.
"""
from pathlib import Path
import argparse,hashlib,json,os,shutil,subprocess,time
from aircraft170_controlled_gameplay import inventory,instrument_texts,INSTRUMENTED_PATHS,verify_instrumented_build
SHA=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def tree(root):return {p.relative_to(root).as_posix():SHA(p) for p in sorted(root.rglob('*')) if p.is_file()}
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('root','fresh-proof','out','sysroot'):p.add_argument('--'+name,type=Path,required=True)
 a=p.parse_args();a=argparse.Namespace(**{k:v.resolve() for k,v in vars(a).items()});assert not a.out.exists()
 free=shutil.disk_usage(a.out.parent).free;assert free>25*1024**2+250*1024**2
 root=a.root;fresh=a.fresh_proof;baseline=fresh/'hd-on-build';proof=json.loads((fresh/'native-receipt.json').read_bytes())
 source=inventory(root);assert proof['status']=='PASS' and proof['source_sha256']==source
 assert inventory(baseline)==source and SHA(baseline/'opentyrian2000')==proof['modes']['hd-on']['binary_sha256']
 objects=tree(baseline/'obj');assert len(list((baseline/'obj').glob('*.o')))>80
 driver=SHA(Path(__file__));helper=Path(__file__).with_name('aircraft170_controlled_gameplay.py');helper_sha=SHA(helper)
 a.out.mkdir();files={**source,'Makefile':SHA(root/'Makefile')}
 files.update({p.relative_to(root).as_posix():SHA(p) for p in (root/'assets/hd/shared-menu-runs-v1').glob('reconstructed*specs.h')})
 for n,h in files.items():
  d=a.out/n;d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/n,d);assert SHA(d)==h
 changed=instrument_texts({n:(root/n).read_text() for n in INSTRUMENTED_PATHS})
 for n,text in changed.items():(a.out/n).write_text(text)
 instrumented={n:SHA(a.out/n) for n in files};(a.out/'obj').mkdir()
 # Never compile into a linked object: replaced TUs are excluded from linking.
 units=('render_mirror','tyrian2','sprite')
 for q in (baseline/'obj').glob('*.o'):
  if q.stem not in units:os.link(q,a.out/'obj'/q.name)
 env={**os.environ,'PKG_CONFIG_SYSROOT_DIR':str(a.sysroot),'PKG_CONFIG_LIBDIR':str(a.sysroot/'usr/lib/x86_64-linux-gnu/pkgconfig'),'LD_LIBRARY_PATH':str(a.sysroot/'usr/lib/x86_64-linux-gnu')}
 cflags=subprocess.check_output(['pkg-config','--cflags','sdl2','SDL2_net'],env=env,text=True).split();libs=subprocess.check_output(['pkg-config','--libs','sdl2','SDL2_net'],env=env,text=True).split()
 commands=[];started=time.monotonic()
 for unit in units:
  target=a.out/'obj'/(unit+'.o');assert not target.exists()
  cmd=['cc','-std=c99','-O2','-g','-DWITH_NETWORK','-DTARGET_UNIX','-DNEWSHF_HD_COMPOSITOR=1','-I'+str(a.sysroot/'usr/include/x86_64-linux-gnu'),*cflags,'-I'+str(a.out/'src'),'-c',str(a.out/'src'/(unit+'.c')),'-o',str(target)]
  result=subprocess.run(cmd,env=env,capture_output=True);(a.out/(unit+'-compile.log')).write_bytes(result.stdout+result.stderr);commands.append(cmd);assert result.returncode==0,result.stderr.decode()
 cmd=['cc',*[str(q) for q in sorted((a.out/'obj').glob('*.o'))],*libs,'-lm','-o',str(a.out/'opentyrian2000')]
 result=subprocess.run(cmd,env=env,capture_output=True);(a.out/'link.log').write_bytes(result.stdout+result.stderr);commands.append(cmd);assert result.returncode==0,result.stderr.decode()
 checks={'production_source_unchanged':source==inventory(root),'already_fresh_objects_unchanged':objects==tree(baseline/'obj'),'instrumented_inputs_unchanged':all(SHA(a.out/n)==h for n,h in instrumented.items()),'driver_unchanged':driver==SHA(Path(__file__)),'helper_unchanged':helper_sha==SHA(helper),'already_fresh_binary_unchanged':SHA(baseline/'opentyrian2000')==proof['modes']['hd-on']['binary_sha256']};assert all(checks.values())
 report={'status':'PASS','scope':__doc__,'production_source':source,'source_before':instrumented,'source_after':inventory(root),'source_unchanged':True,'commands':commands,'seconds':time.monotonic()-started,'binary_sha256':SHA(a.out/'opentyrian2000'),'driver_sha256':driver,'helper_sha256':helper_sha,'fresh_proof_sha256':SHA(fresh/'native-receipt.json'),'fresh_objects_before':objects,'fresh_objects_after':tree(baseline/'obj'),'checks':checks}
 (a.out/'build-receipt.json').write_text(json.dumps(report,indent=2)+'\n');verify_instrumented_build(root,a.out,report);print('SOURCE-BOUND GAMEPLAY PROBE BUILD PASS')
if __name__=='__main__':main()
