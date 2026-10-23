#!/usr/bin/env python3
"""Full native SDL/production-object NEWSHF compositor test, not a game playthrough.
Original game bytes are verified and passed over stdin, never saved by this test.
"""
import argparse, hashlib, json, os, resource, shutil, struct, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from check_newshf_phase_a import check, IDENTITY
SHA=lambda b:hashlib.sha256(b).hexdigest()
def no_core():
 resource.setrlimit(resource.RLIMIT_CORE,(0,0))
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--original-data',type=Path,required=True);p.add_argument('--sysroot',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
 p.add_argument('--negative-control',action='store_true');p.add_argument('--compose-negative-control',action='store_true');p.add_argument('--build-only',action='store_true');p.add_argument('--skip-build',action='store_true')
 a=p.parse_args();a.sysroot=a.sysroot.resolve();a.out=a.out.resolve();a.original_data=a.original_data.resolve();a.out.mkdir(parents=True,exist_ok=True)
 assert shutil.disk_usage(a.out).free>5*1024**3
 check(ROOT/'authoring-inputs/enemies/newshf-phase-a',a.original_data)
 env={**os.environ,'PKG_CONFIG_SYSROOT_DIR':str(a.sysroot),'PKG_CONFIG_LIBDIR':str(a.sysroot/'usr/lib/x86_64-linux-gnu/pkgconfig'),'LD_LIBRARY_PATH':str(a.sysroot/'usr/lib/x86_64-linux-gnu'),'ASAN_OPTIONS':'detect_leaks=0:halt_on_error=1','UBSAN_OPTIONS':'halt_on_error=1:print_stacktrace=1'}
 subprocess.run(['pkg-config','--exists','sdl2','SDL2_net'],env=env,check=True)
 snap={str(x.relative_to(ROOT)):SHA(x.read_bytes()) for x in (ROOT/'src').iterdir() if x.is_file()}
 modes={'default-off':'','hd-on':'-DNEWSHF_HD_COMPOSITOR=1','mirror-disabled':'-DNEWSHF_HD_COMPOSITOR=1 -DRENDER_MIRROR_DISABLED'}
 report={'scope':'Full native SDL production objects and actual sprite blits/JE_makeEnemy; no game loop or E1 acceptance','status':'RUNNING','modes':{},'source_sha256':snap,'private_original_bytes_persisted':False}
 for mode,flags in modes.items():
  build=a.out/(mode+'-build');build.mkdir(exist_ok=True)
  if not a.skip_build:
   (build/'src').mkdir(exist_ok=True)
   for source in (ROOT/'src').iterdir():
    if source.is_file():
     dst=build/'src'/source.name
     if not dst.exists() or dst.read_bytes()!=source.read_bytes():shutil.copyfile(source,dst)
   if not (build/'Makefile').exists() or (build/'Makefile').read_bytes()!=(ROOT/'Makefile').read_bytes():shutil.copyfile(ROOT/'Makefile',build/'Makefile')
   for h in ['reconstructed_run_specs.h','reconstructed_numeric_specs.h','reconstructed_name_source_specs.h']:
    src=ROOT/'assets/hd/shared-menu-runs-v1'/h;dst=build/src.relative_to(ROOT);dst.parent.mkdir(parents=True,exist_ok=True);
    if not dst.exists() or dst.read_bytes()!=src.read_bytes():shutil.copyfile(src,dst)
   cmd=['make','-j3','VCS_IDREV=printf newshf-identity-native','CPPFLAGS=-MMD -DNDEBUG '+flags+' -I'+str(a.sysroot/'usr/include/x86_64-linux-gnu'),'LDFLAGS=-Wl,-rpath,'+str(a.sysroot/'usr/lib/x86_64-linux-gnu')]
   with (a.out/(mode+'.log')).open('wb') as log:r=subprocess.run(cmd,cwd=build,env=env,stdout=log,stderr=subprocess.STDOUT)
   report['modes'][mode]={'exit_code':r.returncode,'binary_sha256':SHA((build/'opentyrian2000').read_bytes()) if (build/'opentyrian2000').exists() else None}
   (a.out/'native-receipt.json').write_text(json.dumps(report,indent=2)+'\n')
   if r.returncode:raise SystemExit(f'{mode} build failed; see log')
 if not a.skip_build:
  report['status']='PASS';report['source_unchanged']=all(SHA((ROOT/n).read_bytes())==h for n,h in snap.items())
  (a.out/'native-build-receipt.json').write_text(json.dumps(report,indent=2)+'\n')
 if a.build_only:return
 build=a.out/'hd-on-build'
 cflags=subprocess.check_output(['pkg-config','--cflags','sdl2','SDL2_net'],env=env,text=True).split()
 libs=subprocess.check_output(['pkg-config','--libs','sdl2','SDL2_net'],env=env,text=True).split()
 flags=['-std=c99','-O0','-g','-DWITH_NETWORK','-DTARGET_UNIX','-DNEWSHF_HD_COMPOSITOR=1','-I'+str(a.sysroot/'usr/include/x86_64-linux-gnu'),*cflags,'-I'+str(ROOT/'src')]
 # Main is renamed in only the ordinary game TU; the test includes the actual
 # renderer TU to inspect its private proof state without production test APIs.
 cmd=['cc',*flags,'-Dmain=newshf_unused_game_main','-c',str(ROOT/'src/opentyr.c'),'-o',str(build/'opentyr-test.o')]
 subprocess.run(cmd,env=env,check=True,capture_output=True)
 objects=[str(x) for x in sorted((build/'obj').glob('*.o')) if x.stem not in ['render_mirror','opentyr','sprite','tyrian2']]
 for unit in ['sprite','tyrian2']:
  target=build/(unit+'-sanitized.o')
  subprocess.run(['cc',*flags,'-fsanitize=address,undefined','-fno-omit-frame-pointer','-c',str(ROOT/'src'/(unit+'.c')),'-o',str(target)],env=env,check=True,capture_output=True)
  objects.append(str(target))
 if a.negative_control or a.compose_negative_control:
  mutant=a.out/'mutant-src';mutant.mkdir(exist_ok=True)
  shutil.copyfile(ROOT/'src/render_mirror.c',mutant/'render_mirror.c')
  if a.negative_control:
   code=(ROOT/'src/newshf_identity_validation.inc').read_text();guard='&&global_bytes_hash(b->data,b->size)==NEWSHF_PROTOTYPE_BANK_FNV';assert code.count(guard)==1
   (mutant/'newshf_identity_validation.inc').write_text(code.replace(guard,''))
  if a.compose_negative_control:
   code=(ROOT/'src/global_newshf_mirror.inc').read_text();store='*p=night?normal15_rgba(color,before,after,normal15_branch(x-24,y,lightx,lighty)<0):color;';assert code.count(store)==1
   (mutant/'global_newshf_mirror.inc').write_text(code.replace(store,''))
  flags.insert(0,'-I'+str(mutant))
 cmd=['cc',*flags,'-fsanitize=address,undefined','-fno-omit-frame-pointer','-no-pie',str(ROOT/'tests/newshf_compositor_validation.c'),str(build/'opentyr-test.o'),*objects,*libs,'-lm','-o',str(build/'compositor-test')]
 r=subprocess.run(cmd,env=env,capture_output=True,text=True);(a.out/'harness-compile.log').write_text(r.stdout+r.stderr)
 if r.returncode:print(r.stderr);raise SystemExit(r.returncode)
 bank=(a.original_data/'newshf.shp').read_bytes();raw=(a.original_data/'tyrian.hdt').read_bytes();pal=(a.original_data/'palette.dat').read_bytes()
 assert SHA(pal)=='f628396306805387f07f72c4ccf0fdee9ca84b8e70ae23ba4ec58ec5fb362da0'
 shape=(a.original_data/'tyrian.shp').read_bytes();offsets=struct.unpack_from('<13I',shape,2);talon_bank=shape[offsets[8]:offsets[9]]
 rgb=bytes((v<<2)|(v>>4) for v in pal[5*768:6*768]);payload=bank+b''.join(raw[r['offset']:r['offset']+77] for r in IDENTITY['records'])+b''.join(struct.pack('<I',int.from_bytes(rgb[n:n+3],'big')) for n in range(0,768,3))+struct.pack('<I',len(talon_bank))+talon_bank
 resource_root=a.out/'asset-fixture';(resource_root/'newshf').mkdir(parents=True,exist_ok=True)
 for source in (ROOT/'assets/hd/newshf-v1').glob('*.hda'):shutil.copyfile(source,resource_root/'newshf'/source.name)
 content=resource_root/'content'
 if not content.exists():content.symlink_to(ROOT/'assets/hd/global-assets-v1/content',target_is_directory=True)
 for index,source in enumerate(sorted((ROOT/'assets/hd/newshf-v1').glob('*.hda'))):
  for mode in ['missing','corrupt','header','trailing']:
   root=resource_root/(mode+str(index));(root/'newshf').mkdir(parents=True,exist_ok=True)
   for other in (ROOT/'assets/hd/newshf-v1').glob('*.hda'):
    dst=root/'newshf'/other.name
    if dst.exists() or dst.is_symlink():dst.unlink()
    if other!=source:dst.symlink_to(other)
    elif mode!='missing':
     b=bytearray(other.read_bytes())
     if mode=='corrupt':b[31]^=1
     if mode=='header':b[4]^=1
     if mode=='trailing':b+=b'!'
     dst.write_bytes(b)
 r=subprocess.run([str(build/'compositor-test'),str(resource_root)],input=payload,env=env,capture_output=True,timeout=240,preexec_fn=no_core)
 (a.out/'harness.log').write_bytes(r.stdout+r.stderr);print((r.stdout+r.stderr).decode())
 transfer_line=next(i for i,line in enumerate((ROOT/'tests/newshf_compositor_validation.c').read_text().splitlines(),1) if 'quartet();talon();Uint8 bank_saved' in line)
 expected_bank_failure=f'newshf_compositor_validation.c:{transfer_line}: !ready&&!last_output_valid'.encode()
 accepted=(r.returncode!=0 and expected_bank_failure in r.stderr and b'AddressSanitizer' not in r.stderr and b'runtime error:' not in r.stderr) if a.negative_control else r.returncode==0
 if a.compose_negative_control:accepted=r.returncode!=0 and b'*pixel(output,x-24*d,y)==want' in r.stderr and b'AddressSanitizer' not in r.stderr and b'runtime error:' not in r.stderr
 unchanged=all(SHA((ROOT/n).read_bytes())==h for n,h in snap.items());accepted=accepted and unchanged
 report.update(status='PASS' if accepted else 'FAIL',negative_control='compose-store' if a.compose_negative_control else a.negative_control,returncode=r.returncode,stdout=r.stdout.decode(),stderr=r.stderr.decode(),sanitizers='ASan+UBSan renderer, sprite, tyrian2 and harness; remaining production objects optimized native',source_unchanged=unchanged,free_disk_bytes=shutil.disk_usage(a.out).free)
 (a.out/'native-receipt.json').write_text(json.dumps(report,indent=2)+'\n');raise SystemExit(not accepted)
if __name__=='__main__':main()
