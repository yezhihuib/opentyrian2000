#!/usr/bin/env python3
"""Bounded real356 provider→real170 borrower; internal8, physical output2/4.

One new sanitized harness/fullrenderer TU links exact already-fresh production
objects and existing sanitized sprite/tyrian2. No game capture or new production
build. Test-only map pointer/actor placement is controlled, never natural proof.
"""
from pathlib import Path
import argparse,hashlib,json,os,resource,shutil,struct,subprocess,sys,time
SHA=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def inventory(p):return {q.relative_to(p).as_posix():SHA(q) for q in sorted(p.rglob('*')) if q.is_file() and '__pycache__' not in q.parts}
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('source-root','fresh-proof','data','sysroot','out'):p.add_argument('--'+name,type=Path,required=True)
 a=p.parse_args();a=argparse.Namespace(**{k:v.resolve() for k,v in vars(a).items()});r=a.source_root;q=a.out;fresh=a.fresh_proof
 assert not q.exists() and shutil.disk_usage(q.parent).free>=300*1024**2
 proof=json.loads((fresh/'native-receipt.json').read_text());assert proof['status']=='PASS'
 source=inventory(r/'src');assert {'src/'+n:h for n,h in source.items()}==proof['source_sha256']
 assert inventory(fresh/'hd-on-build/src')==source
 test=r/'tests/aircraft170_newshf_native_validation.c';base=r/'tests/newshf_compositor_validation.c'
 assert SHA(test)=='94fad02379d66f2bde79985e2e8b7effd85e00a21503d4829aaff9a006770fd4'
 assert SHA(base)=='c7243a9208e1f1f1bee7c26d3d3af66caf7028f69429478011b10da4b9ba306e'
 scripts_before={str(f):SHA(f) for f in sorted((r/'scripts').glob('*.py'))}
 assert {str(r/n):h for n,h in proof['test_sha256'].items() if n.startswith('scripts/')}==scripts_before
 data_before={str(a.data/n):SHA(a.data/n) for n in ('newshf.shp','newshi.shp','tyrian.hdt','palette.dat','tyrian.shp','shapesy.dat','tyrian1.lvl')}
 sys.path.insert(0,str(r/'scripts'))
 from check_aircraft170_newshf_pins import verify as aircraft_verify
 from check_shapesy_bronze356_pins import verify as bronze_verify
 from build_newshf_prototype_pins import IDENTITY
 aircraft_verify(r,a.data);bronze_verify(r,a.data)
 companion=Path(__file__).with_name('shared170_bronze356_borrow_native.c.inc');driver=Path(__file__).resolve()
 consume={str(driver):SHA(driver),str(companion):SHA(companion),str(test):SHA(test),str(base):SHA(base)}
 build=fresh/'hd-on-build';objects=[x for x in sorted((build/'obj').glob('*.o')) if x.stem not in ('render_mirror','opentyr','sprite','tyrian2')]
 objects += [build/'opentyr-test.o',build/'sprite-sanitized.o',build/'tyrian2-sanitized.o']
 obj_before={str(x):SHA(x) for x in objects}
 index=Path(subprocess.check_output(['git','-C',str(r),'rev-parse','--git-path','index'],text=True).strip());index_hash=SHA(index)
 q.mkdir();harness=q/'harness.c';original=test.read_text();marker='int main(int argc,char **argv)\n{';assert original.count(marker)==1
 harness.write_text(original.split(marker)[0]+'\n'+companion.read_text())
 pack=q/'pack';pack.mkdir();assets={}
 for family in ('newshf','newshf-aircraft170'):
  dest=pack/family;dest.mkdir()
  family_root=r/'assets/hd/newshf-v1' if family=='newshf' else r/'assets/hd/current-compat'/family
  files=sorted(family_root.glob('*.hda'));assert len(files)==(9 if family=='newshf' else 3)
  for f in files:(dest/f.name).symlink_to(f);assets[str(f)]=SHA(f)
 bronze=sorted((r/'assets/hd/current-compat/shapesy-bronze356').glob('*.hda'));assert len(bronze)==1
 (pack/bronze[0].name).symlink_to(bronze[0]);assets[str(bronze[0])]=SHA(bronze[0])
 env={**os.environ,'PKG_CONFIG_SYSROOT_DIR':str(a.sysroot),'PKG_CONFIG_LIBDIR':str(a.sysroot/'usr/lib/x86_64-linux-gnu/pkgconfig'),'LD_LIBRARY_PATH':str(a.sysroot/'usr/lib/x86_64-linux-gnu'),'SDL_VIDEODRIVER':'dummy','SDL_AUDIODRIVER':'dummy','SDL_RENDER_DRIVER':'software','ASAN_OPTIONS':'detect_leaks=0:halt_on_error=1','UBSAN_OPTIONS':'halt_on_error=1:print_stacktrace=1'}
 cflags=subprocess.check_output(['pkg-config','--cflags','sdl2','SDL2_net'],env=env,text=True).split();libs=subprocess.check_output(['pkg-config','--libs','sdl2','SDL2_net'],env=env,text=True).split()
 exe=q/'borrow-test';cmd=['cc','-std=c99','-O0','-g','-DWITH_NETWORK','-DTARGET_UNIX','-DNEWSHF_HD_COMPOSITOR=1','-I'+str(a.sysroot/'usr/include/x86_64-linux-gnu'),*cflags,'-I'+str(r/'src'),'-I'+str(r/'tests'),'-fsanitize=address,undefined','-fno-omit-frame-pointer','-no-pie',str(harness),*[str(o) for o in objects],*libs,'-lm','-o',str(exe)]
 report=dict(status='RUNNING',scope=__doc__,source_sha256=source,producer_input_sha256=consume,script_snapshot_sha256=scripts_before,objects_sha256=obj_before,original_data_sha256=data_before,assets_sha256=assets,index_before_sha256=index_hash,generated_harness_sha256=SHA(harness),compile_argv=cmd,fresh_native_receipt_sha256=SHA(fresh/'native-receipt.json'),sanitizer_scope='New fullrenderer/harness TU plus existing ASan+UBSan sprite.c andtyrian2.c. opentyr-test.o andremainingproductionobjects native(non-sanitized); SDL/systemlibraries notinstrumented. LSanoff for established environment limitation.',final_output_cap_bytes=16000000,compile_transient_peak_forecast=50*1024**2,reserve=250*1024**2,free_before=shutil.disk_usage(q).free)
 (q/'receipt.json').write_text(json.dumps(report,indent=2)+'\n');start=time.time();z=subprocess.run(cmd,env=env,capture_output=True);(q/'compile.log').write_bytes(z.stdout+z.stderr);report['compile_returncode']=z.returncode
 if z.returncode:
  report['status']='COMPILE_FAIL';(q/'receipt.json').write_text(json.dumps(report,indent=2)+'\n');raise SystemExit(z.returncode)
 raw=(a.data/'tyrian.hdt').read_bytes();pal=(a.data/'palette.dat').read_bytes();rgb=bytes((v<<2)|(v>>4) for v in pal[5*768:6*768]);shape=(a.data/'tyrian.shp').read_bytes();offsets=struct.unpack_from('<13I',shape,2);talon=shape[offsets[8]:offsets[9]]
 payload=(a.data/'newshf.shp').read_bytes()+b''.join(raw[row['offset']:row['offset']+77] for row in IDENTITY['records'])+raw[177105:177182]+raw[176720:176797]+raw[176797:176874]+raw[177028:177105]+(a.data/'newshi.shp').read_bytes()+raw[187269:187346]+b''.join(struct.pack('<I',int.from_bytes(rgb[n:n+3],'big')) for n in range(0,768,3))+struct.pack('<I',len(talon))+talon
 raw=(a.data/'shapesy.dat').read_bytes();tiles={};pos=0
 for i in range(1,601):
  blank=raw[pos];pos+=1;tiles[i]=bytes(672) if blank else raw[pos:pos+672];pos+=0 if blank else 672
 raw=(a.data/'tyrian1.lvl').read_bytes();pos=316541;mc,sc,x1,x2,x3,ne=struct.unpack_from('<ccHHHH',raw,pos);assert (mc,sc)==(b'3',b'Y');pos+=10+2*ne
 n=struct.unpack_from('<H',raw,pos)[0];pos+=2+11*n;lookup=struct.unpack_from('>128H',raw,pos)[:72];pos+=768;grid=raw[pos:pos+4200]
 payload+=struct.pack('<72H',*lookup)+b''.join(tiles[i] for i in lookup)+grid
 def no_core():resource.setrlimit(resource.RLIMIT_CORE,(0,0))
 run=subprocess.run([str(exe),str(pack)],input=payload,env=env,cwd=q,capture_output=True,timeout=180,preexec_fn=no_core)
 (q/'stdout.log').write_bytes(run.stdout);(q/'stderr.log').write_bytes(run.stderr)
 checks=dict(source_unchanged=source==inventory(r/'src'),scripts_unchanged=scripts_before=={str(f):SHA(f) for f in sorted((r/'scripts').glob('*.py'))},objects_unchanged=all(SHA(Path(n))==h for n,h in obj_before.items()),inputs_unchanged=all(SHA(Path(n))==h for n,h in {**consume,**data_before,**assets}.items()),raw_index_unchanged=SHA(index)==index_hash)
 output_bytes=sum(x.lstat().st_blocks*512 for x in q.rglob('*'))
 passed=run.returncode==0 and b'BRONZE356_AIRCRAFT170_BORROW PASS positives=6 negatives=6' in run.stdout and all(checks.values()) and output_bytes<16000000
 report.update(status='PASS' if passed else 'FAIL',returncode=run.returncode,checks=checks,stdout=run.stdout.decode(),stderr=run.stderr.decode(),binary_sha256=SHA(exe),seconds=time.time()-start,output_allocated_bytes=output_bytes,free_after=shutil.disk_usage(q).free,stdin_sha256=hashlib.sha256(payload).hexdigest(),private_original_stdin_persisted=False)
 (q/'receipt.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ('status','returncode','checks','stdout','stderr','seconds','output_allocated_bytes','free_after')},indent=2));raise SystemExit(not passed)
if __name__=='__main__':main()
