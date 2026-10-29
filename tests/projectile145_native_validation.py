#!/usr/bin/env python3
"""Local full-renderer-TU145 probe plus unchanged91 harness methods.

Recompiles renderer/harness, sprite, entity_draw and tyrian2 with ASan+UBSan.
Other unchanged production objects are read-only reused from the qualified170
fresh build, hash-bound to its retained proof. Not a fresh game build/playthrough.
"""
from pathlib import Path
import argparse, ast, hashlib, json, os, resource, shutil, signal, struct, subprocess, time
SHA=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def inventory(p):return {q.relative_to(p).as_posix():SHA(q) for q in sorted(p.rglob('*')) if q.is_file() and '__pycache__' not in q.parts}
def allocated(p):return sum(q.lstat().st_blocks*512 for q in p.rglob('*'))
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ('source-root','baseline','fresh-proof','object-proof','data','sysroot','out'):p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a=argparse.Namespace(**{k:v.resolve() for k,v in vars(a).items()})
 r=a.source_root;q=a.out;reserve=250*1024**2;peak=60*1024**2;cap=48*1024**2
 assert not q.exists() and shutil.disk_usage(q.parent).free>=reserve+peak
 proof=json.loads((a.fresh_proof/'native-receipt.json').read_text());assert proof['status']=='PASS'
 sources=inventory(r/'src');old={n.removeprefix('src/'):h for n,h in proof['source_sha256'].items()}
 changed={n for n in old if sources.get(n)!=old[n]};added=set(sources)-set(old)
 assert changed=={'render_mirror.c','global_projectile91_mirror.inc','tyrian2.c','entity_draw.c'},changed
 assert added=={'enemy_projectile145_mirror.inc','current_projectile145_payload_pins.h'},added
 assert inventory(a.fresh_proof/'hd-on-build/src')==old
 object_proof=json.loads(a.object_proof.read_text())
 bound={Path(n):h for n,h in object_proof['objects_sha256'].items()}
 assert all(SHA(n)==h for n,h in bound.items())
 objects=[n for n in bound if n.name not in ('sprite-sanitized.o','tyrian2-sanitized.o','entity_draw.o')]
 assert len(objects)==82 and all(n.is_file() for n in objects)
 # Every borrowed TU's source/headers remain exactly the fresh-build closure.
 # Changed .inc/new pin are private render_mirror includes; changed C TUs are excluded.
 external_dependencies={}
 for n in objects:
  if n.name!='opentyr-test.o':
   dep=n.with_suffix('.d');assert dep.is_file()
   tokens=dep.read_text().replace('\\\n',' ').split()
   for token in tokens[1:]:
    if token.endswith(':') or not token.startswith('src/'):continue
    name=token[4:];assert name not in changed|added,(n,name)
    if name.startswith('../assets/'):
     rel=name[3:]
     assert rel in {'assets/hd/shared-menu-runs-v1/'+h for h in ('reconstructed_run_specs.h','reconstructed_numeric_specs.h','reconstructed_name_source_specs.h')},(n,name)
     original=a.fresh_proof/'hd-on-build'/rel;current=a.baseline/rel
     assert SHA(original)==SHA(current),(n,name)
     external_dependencies[str(original)]=SHA(original);external_dependencies[str(current)]=SHA(current)
    else:assert name in old and sources[name]==old[name],(n,name)
 driver=Path(__file__).resolve();companion=driver.with_name('projectile145_native_additions.c.inc');oldtest=r/'tests/test_projectile91_global_runtime.py'
 tree=ast.parse(oldtest.read_text());node=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='HARNESS' for t in n.targets))
 oldh=ast.literal_eval(node.value);assert hashlib.sha256(oldh.encode()).hexdigest()=='4edcb186f10a47b8d331b6ecaefe15f12c620d7967145f5f9cdbf93c0e76ce89'
 marker='int main(int argc,char **argv)\n{';assert oldh.count(marker)==1
 harness=oldh.split(marker)[0]+companion.read_text()
 producers={str(f):SHA(f) for f in (driver,companion,oldtest)}
 scripts=inventory(r/'scripts');assets=dict(external_dependencies)
 for base in (a.baseline/'assets/hd/global-assets-v1/content',):
  assets.update({str(f):SHA(f) for f in base.rglob('*') if f.is_file()})
 hdas={91:r/'assets/hd/current-compat/projectile91/enemy-projectile91-91-8.hda',145:r/'assets/hd/current-compat/projectile145/enemy-projectile145-145-8.hda'}
 assets.update({str(f):SHA(f) for f in hdas.values()})
 data={str(a.data/n):SHA(a.data/n) for n in ('tyrian.shp','palette.dat')}
 index=Path(subprocess.check_output(['git','--no-optional-locks','-C',str(r),'rev-parse','--path-format=absolute','--git-path','index'],text=True).strip());indexhash=SHA(index)
 q.mkdir();(q/'src').mkdir()
 for n,h in sources.items():(q/'src'/n).parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(r/'src'/n,q/'src'/n)
 for name in ('reconstructed_run_specs.h','reconstructed_numeric_specs.h','reconstructed_name_source_specs.h'):
  src=a.baseline/'assets/hd/shared-menu-runs-v1'/name;dest=q/src.relative_to(a.baseline);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest);assets[str(src)]=SHA(src)
 (q/'harness.c').write_text(harness)
 packs=[]
 for name,missing,bad in [('valid',None,None),('missing91',91,None),('missing145',145,None),('bad145',None,145),('bad91',None,91)]:
  dest=q/name;dest.mkdir();(dest/'content').symlink_to(a.baseline/'assets/hd/global-assets-v1/content',target_is_directory=True)
  for sel,f in hdas.items():
   if sel!=missing:
    b=bytearray(f.read_bytes())
    if sel==bad:b[128]^=1
    (dest/f.name).write_bytes(b)
  packs.append(dest)
 env={**os.environ,'PKG_CONFIG_SYSROOT_DIR':str(a.sysroot),'PKG_CONFIG_LIBDIR':str(a.sysroot/'usr/lib/x86_64-linux-gnu/pkgconfig'),'LD_LIBRARY_PATH':str(a.sysroot/'usr/lib/x86_64-linux-gnu'),'SDL_VIDEODRIVER':'dummy','SDL_AUDIODRIVER':'dummy','SDL_RENDER_DRIVER':'software','ASAN_OPTIONS':'detect_leaks=0:halt_on_error=1','UBSAN_OPTIONS':'halt_on_error=1:print_stacktrace=1','TMPDIR':str(q/'tmp')}
 for k in tuple(env):
  if k.startswith(('AIRCRAFT170_','SHARED170_','TYRIAN_GAME_PROBE','OT_')):env.pop(k)
 (q/'tmp').mkdir()
 flags=subprocess.check_output(['pkg-config','--cflags','sdl2','SDL2_net'],env=env,text=True).split();libs=subprocess.check_output(['pkg-config','--libs','sdl2','SDL2_net'],env=env,text=True).split()
 flags=['-std=c99','-O0','-g','-DWITH_NETWORK','-DTARGET_UNIX','-DNEWSHF_HD_COMPOSITOR=1','-I'+str(a.sysroot/'usr/include/x86_64-linux-gnu'),*flags,'-I'+str(q/'src'),'-fsanitize=address,undefined','-fno-omit-frame-pointer','-no-pie']
 report=dict(status='RUNNING',scope=__doc__,source_sha256=sources,changed_source=sorted(changed),added_source=sorted(added),producer_sha256=producers,script_sha256=scripts,borrowed_objects_sha256={str(n):bound[n] for n in objects},all_original_object_pins={str(n):h for n,h in bound.items()},original_data_sha256=data,assets_sha256=assets,index_sha256=indexhash,fresh_receipt_sha256=SHA(a.fresh_proof/'native-receipt.json'),object_proof_sha256=SHA(a.object_proof),old91_harness_sha256=hashlib.sha256(oldh.encode()).hexdigest(),old91_method_prefix_byte_exact=True,generated_harness_sha256=SHA(q/'harness.c'),reserve_bytes=reserve,peak_budget_bytes=peak,final_output_cap_bytes=cap,free_before=shutil.disk_usage(q).free,peak_allocated_bytes=allocated(q),minimum_free_bytes=shutil.disk_usage(q).free,commands=[],sanitizers='ASan+UBSan new full renderer/harness, sprite.c, entity_draw.c, tyrian2.c.82 borrowed objects including renamed main are non-sanitized; SDL/system libraries not instrumented; LSan disabled.')
 def save():(q/'receipt.json').write_text(json.dumps(report,indent=2)+'\n')
 def no_core():resource.setrlimit(resource.RLIMIT_CORE,(0,0))
 def run(cmd,label,payload=None):
  row={'argv':list(map(str,cmd)),'label':label};report['commands'].append(row);save()
  with (q/(label+'.stdout')).open('wb') as out,(q/(label+'.stderr')).open('wb') as err:
   z=subprocess.Popen(row['argv'],env=env,cwd=q,stdin=subprocess.PIPE if payload is not None else subprocess.DEVNULL,stdout=out,stderr=err,start_new_session=True,preexec_fn=no_core)
   row['pid']=z.pid;save()
   if payload is not None:z.stdin.write(payload);z.stdin.close()
   start=time.monotonic()
   while z.poll() is None:
    free=shutil.disk_usage(q).free;used=allocated(q);report['minimum_free_bytes']=min(free,report['minimum_free_bytes']);report['peak_allocated_bytes']=max(used,report['peak_allocated_bytes'])
    if free<reserve or used>peak or time.monotonic()-start>300:
     os.killpg(z.pid,signal.SIGTERM);z.wait();row['killed_for_budget_or_timeout']=True;break
    time.sleep(.25)
   row['returncode']=z.wait();row['seconds']=time.monotonic()-start;save()
   if row['returncode'] or row.get('killed_for_budget_or_timeout'):raise RuntimeError(label+' failed; retained logs')
 start=time.monotonic();save()
 try:
  newobjects=[]
  for name in ('sprite','entity_draw','tyrian2'):
   obj=q/(name+'-sanitized.o');run(['cc',*flags,'-c',q/'src'/f'{name}.c','-o',obj],name+'-compile');newobjects.append(obj)
  exe=q/'projectile145-test';run(['cc',*flags,q/'harness.c',*objects,*newobjects,*libs,'-lm','-o',exe],'renderer-link')
  raw=(a.data/'tyrian.shp').read_bytes();offsets=struct.unpack_from('<13I',raw,2);bank=raw[offsets[7]:offsets[8]];assert hashlib.sha256(bank).hexdigest()=='9bba1e94d38df61f152412c226bfd6df235e42027c9143c5961d4a5add853a68'
  pal=(a.data/'palette.dat').read_bytes()[:768];rgb=bytes((v<<2)|(v>>4) for v in pal);talon=raw[offsets[8]:offsets[9]]
  payload=bank+b''.join(struct.pack('<I',int.from_bytes(rgb[i:i+3],'big')) for i in range(0,768,3))+struct.pack('<I',len(talon))+talon
  report['stdin_sha256']=hashlib.sha256(payload).hexdigest();report['original_stdin_persisted']=False
  run([exe,*packs],'native-run',payload)
  stdout=(q/'native-run.stdout').read_text();assert 'PASS inherited91 native lifecycle:' in stdout and 'PASS shared145 native lifecycle:' in stdout
  report.update(status='PASS',stdout=stdout,binary_sha256=SHA(exe))
 except Exception as e:
  report.update(status='FAIL',error=repr(e));raise
 finally:
  checks=dict(source_unchanged=sources==inventory(r/'src'),scripts_unchanged=scripts==inventory(r/'scripts'),objects_unchanged=all(SHA(n)==h for n,h in bound.items()),inputs_unchanged=all(SHA(Path(n))==h for n,h in {**producers,**data,**assets}.items()),index_unchanged=SHA(index)==indexhash)
  report.update(checks=checks,seconds=time.monotonic()-start,final_allocated_bytes=allocated(q),free_after=shutil.disk_usage(q).free)
  report['peak_allocated_bytes']=max(report['peak_allocated_bytes'],report['final_allocated_bytes'])
  if not all(checks.values()) or report['final_allocated_bytes']>cap or report['free_after']<reserve:report['status']='FAIL'
  save();print(json.dumps({k:report.get(k) for k in ('status','stdout','error','checks','peak_allocated_bytes','minimum_free_bytes','final_allocated_bytes','free_after','seconds')},indent=2))
 assert report['status']=='PASS'
if __name__=='__main__':main()
