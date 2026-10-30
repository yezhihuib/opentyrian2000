#!/usr/bin/env python3
"""Four empty independent builds and four actual native processes: 107+157+365+251.
Current ROOT inputs only; no historical receipt/object/.d/ELF/source fallback.
All86 project TUs/config fresh; 84 fresh SAN objects+fresh renamed main+real
renderer/harness. System SDL remains native, LSan off. Not gameplay/fullgate.
New recovered public root is protected; unavailable historical live roots are
not invented. No source/index writes, refresh, staging, retry or auto-cleanup.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,re,resource,shlex,shutil,signal,stat,subprocess,sys,threading,time
sys.dont_write_bytecode=True
SHA=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(data):return hashlib.sha256(data).hexdigest()
PEAK=384*1024**2;FINAL_CAP=256*1024**2;RESERVE=250*1024**2;START_REQUIRED=PEAK+RESERVE
MODES={'default-off':'','hd-on':'-DNEWSHF_HD_COMPOSITOR=1','mirror-disabled':'-DNEWSHF_HD_COMPOSITOR=1 -DRENDER_MIRROR_DISABLED','hd-on-asan-ubsan':'-DNEWSHF_HD_COMPOSITOR=1'}
SAN=('-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie')
DEFAULT_CFLAGS='-pedantic -Wall -Wextra -Wno-format-truncation -Wno-missing-field-initializers -O2'
SUCCESS='PASS_FOUR_FRESH_CONFIGS_AND_FULL_PROJECT_SANITIZED880'
NATIVE_HELPER_SHA='39082c80c9fd37f28ca76ad34e342024a18799902dbfb44429baddb4a32170f2'
GOLD_COMPANION_SHA='b00796c4d72265022da0e9e4e1c46acbbbff00ee754b5a51a61701aa778e6f46'
OLD_BLUE_HELPER_SHA='38d904bf84c17ae9179c6c4bc4ca895f31393efcc774ac851d7db1bc6a23ef6d'
PROTECTED_PROFILE_SHA='e681bac9f6019354247d11e48ed82043a33792f0b703a7ce96d8dcba65655bdb'
PROTECTED_IDENTITY={'head':'f64a7ddc6bbf11a0667665f4faf5b6db6c9ea6bc','raw_sha256':'364b1f621703e726885b6a2369ac5d36f549f9bfa00907622098dabd1e82a4e6','semantic_sha256':'7454601fd6410880e6863ab958d5be7e0727b7523e0eedb2fc4b2abc3a66720d'}
PROTECTED_TREE='f9b6239f59af4cebaef489dca2054c75cc06f1a9'
PRODUCTION6={
 'current_projectile_gold_pulse_payload_pins.h':'2e13023af89d7c627a65d3d3fa16996edc301be643862733d8925013513bb133',
 'enemy_gold_pulse_mirror.inc':'d98a2c28be5b78997224b3b1fe86438edb6008fa01253cc2c0c99f651a89a9be',
 'entity_draw.c':'82a7a001807afe6c86b9f3cf07113b97ae6a2d1cd71e0765319e01859ababc60',
 'global_projectile91_mirror.inc':'0cec80aac0eb87f8d97754508512d1dce78852699bf51941918b91c9b9b524da',
 'render_mirror.c':'271cd3d86fcab490745bbdc9e69d06226257ac15d8093ff3bc3b935dcabdc9f3',
 'tyrian2.c':'52f749de40bd9fc3025aeec89d169c45028366ee70db8d0ced36a5e987b7e9e9'}
SOURCE_PINS={'inherited145_harness.c':'8925fb11215446339f067124fa7223ec48dc7c86459e303d3803477773b2d9ac','accepted_projectile61_native_additions.c.inc':'5f80d681e84a6dff20873f7f05bb3a02e3fd0f22013edf2b5fbf133d36c51cfe','accepted61_wrapper.c':'59bfbe4d8e3bb8db4403eaabb199d8ff2f09b2eb2047769f39069c93dff7f4eb','projectile61_native_additions.c.inc':'d894e392ce315b855d5a764fbb526b6d6568a14f223e7e577a4ebf303ecbf67a','projectile_blue_triplet_native_additions.c.inc':'cf38a2c8582bf9c3299a84721d37dae83402b938c859a2489ad382844a9a6084','harness.c':'d39e3b9633eff3abfc70604f96895f21184fa87ad7f344ffa64f2b7705b353e1'}
STDIN_PINS=('7dedf7066696fc278f5fbb8dfb1462e7b6ac290cb5d08ae5260a6cdabc1ecca7','a9739298f031cafbfefb3befd359750872f6caafe69ebf5c7cf948544713830b')
STDOUT_PINS={'inherited107_stdout':('56b267d7cf607164010655de7fbd79fa42d3dc4518865434c2c4b705280856b2',236),'inherited61_stdout':('bbc4b539205c19faa66ec7ada0c755d80907950e9ab91b554633c77fe261bcf4',165),'new_blue_stdout':('833b3944bde9933444f4102716403b9868e1cefec4a077daeecd8535bef5208e',631)}
GOLD_STDOUT_SHA='a1f762926d2fb3bbc2499c5d7dc87f94cd20e239189f69af3646dcc58c4459d5'
HDA_GOLD={168:'a453142d1d1d5e662a5c36053f5af42b719fa2a2d993e7b2384c5d4231cfdb14',169:'1dc205caccc8320968389868f844cacd50046a285b2d1e90f5b9073fcfddc831'}


def allocated(root):
 total=root.lstat().st_blocks*512 if root.exists() else 0
 for p in root.rglob('*'):
  try:total+=p.lstat().st_blocks*512
  except FileNotFoundError:pass
 return total

def budget_ok(used,free,final=False):return used<=(FINAL_CAP if final else PEAK) and free>=RESERVE

def snapshot_allocation(*blobs):return sum((len(x)+4095)//4096*4096 for x in blobs)

def guarded_check(checks,errors,name,fn):
 try:checks[name]=bool(fn())
 except Exception as exc:checks[name]=False;errors[name]=repr(exc)
 return checks[name]

def git(root,*args):return subprocess.check_output(['git','--no-optional-locks','-C',str(root),*args],env={'PATH':os.environ.get('PATH','/usr/bin:/bin'),'GIT_OPTIONAL_LOCKS':'0'})

def identity(root):
 ip=Path(git(root,'rev-parse','--path-format=absolute','--git-path','index').decode().strip());raw=ip.read_bytes();sem=git(root,'ls-files','--stage','-z');assert ip.read_bytes()==raw
 return {'head':git(root,'rev-parse','HEAD').decode().strip(),'raw_sha256':digest(raw),'semantic_sha256':digest(sem)},raw,sem

def inventory(root):
 names=set();result={}
 for base,dirs,files in os.walk(root,followlinks=False):
  dirs[:]=[d for d in dirs if d!='.git'];assert all(not(Path(base)/d).is_symlink() for d in dirs)
  for name in files:
   p=Path(base)/name
   if p==root/'.git':continue
   rel=p.relative_to(root).as_posix();assert not rel.startswith('/') and '..' not in Path(rel).parts
   st=p.lstat();assert stat.S_ISREG(st.st_mode) and st.st_nlink==1,('Nonregular/shared repository file',rel)
   result[rel]={'sha256':SHA(p),'bytes':st.st_size,'mode':stat.S_IMODE(st.st_mode),'nlink':1};names.add(rel)
 assert names and len(names)==len(result)
 return result

def hydrated_manifest(root):
 assert not any(row.startswith(b'S ') for row in git(root,'ls-files','-t','-z').split(b'\0')),'Full hydration required'
 for row in git(root,'ls-files','--stage','-z').split(b'\0'):
  if row:assert row.split(b'\t',1)[0].split()[2]==b'0','Unmerged index'
 wanted=set(git(root,'ls-files','--cached','--others','--exclude-standard','-z').decode().split('\0'))-{''};actual=inventory(root)
 assert set(actual)==wanted,'Unexpected ignored/untracked actual files or missing indexed files'
 return actual

def protected_manifest(root,profile):
 assert profile['commit']==PROTECTED_IDENTITY['head'] and profile['tree']==PROTECTED_TREE and len(profile['files'])==9773
 actual=inventory(root);expected={r['path']:{'sha256':r['sha256'],'bytes':r['bytes'],'mode':int(r['mode'],8)&0o777,'nlink':1} for r in profile['files']}
 assert actual==expected and identity(root)[0]==PROTECTED_IDENTITY
 return actual

def check_source_epoch(source,protected_source):
 assert len(protected_source)==312 and len(source)==314
 expected={**protected_source,**PRODUCTION6};assert source==expected,'Production source differs from selected six-file gold overlay'
 assert len([p for p in source if p.endswith('.c')])==86
 return True

def validate_stdout_bytes(actual):
 assert set(actual)==set(STDOUT_PINS)
 for name,data in actual.items():
  assert isinstance(data,bytes);pin,size=STDOUT_PINS[name];assert len(data)==size and digest(data)==pin,('Original629 stdout bytes changed',name)
 return True

def load_native(root):
 assert re.fullmatch('[0-9a-f]{64}',NATIVE_HELPER_SHA),'DRAFT helper pin: execution forbidden'
 path=root/'tests/projectile_gold_pulse_native_validation.py';assert SHA(path)==NATIVE_HELPER_SHA,'Installed-only helper mismatch; no external fallback'
 spec=importlib.util.spec_from_file_location('gold_current_helpers',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def make_command(mode,sysroot,cc,pkg):
 assert mode in MODES
 cpp='-MD -DNDEBUG '+MODES[mode]+' -I'+str(sysroot/'usr/include/x86_64-linux-gnu');ld='-Wl,-rpath,'+str(sysroot/'usr/lib/x86_64-linux-gnu');flags=DEFAULT_CFLAGS
 if mode=='hd-on-asan-ubsan':ld+=' -fsanitize=address,undefined -no-pie';flags='-O1 -g '+' '.join(SAN)
 return ['make','-j2','CC='+str(cc),'PKG_CONFIG='+str(pkg),'VCS_IDREV=printf gold-pulse-fresh-native','CPPFLAGS='+cpp,'CFLAGS='+flags,'LDFLAGS='+ld]

def compile_contract(log,units,mode):
 lines=[line for line in log.splitlines() if ' -c -o obj/' in line];assert len(lines)==86;observed=[]
 for line in lines:
  argv=shlex.split(line);out=argv[argv.index('-o')+1];unit=Path(out).stem
  assert out=='obj/'+unit+'.o' and argv[-1]=='src/'+unit+'.c' and '-MD' in argv and '-DNDEBUG' in argv
  assert ('-DNEWSHF_HD_COMPOSITOR=1' in argv)==(mode!='default-off') and ('-DRENDER_MIRROR_DISABLED' in argv)==(mode=='mirror-disabled')
  if mode=='hd-on-asan-ubsan':assert all(flag in argv for flag in (*SAN,'-O1','-g')) and '-O2' not in argv
  else:assert '-O2' in argv and not any(flag.startswith('-fsanitize=') for flag in argv)
  observed.append(unit)
 assert len(set(observed))==86 and set(observed)==set(units)
 links=[shlex.split(line) for line in log.splitlines() if ' -o opentyrian2000 ' in line];assert len(links)==1;link=links[0]
 objects=[x for x in link if x.endswith('.o')];assert len(objects)==86 and set(objects)=={'obj/'+u+'.o' for u in units}
 assert ('-fsanitize=address,undefined' in link)==(mode=='hd-on-asan-ubsan')
 if mode=='hd-on-asan-ubsan':assert '-no-pie' in link
 return lines,link

def native_compile_commands(cc,build,out,cflags,libs):
 flags=['-std=c99','-O1','-g','-DWITH_NETWORK','-DTARGET_UNIX','-DNEWSHF_HD_COMPOSITOR=1',*cflags,'-I'+str(build/'src'),*SAN,'-no-pie']
 renamed=build/'opentyr-test.o';objects=sorted(p for p in (build/'obj').glob('*.o') if p.stem not in ('render_mirror','opentyr'));assert len(objects)==84
 compile_main=[str(cc),*flags,'-Dmain=unused_game_main','-MD','-MF',str(out/'renamed-main.d'),'-c',str(build/'src/opentyr.c'),'-o',str(renamed)]
 link=[str(cc),*flags,'-MD','-MF',str(out/'renderer-harness.d'),str(out/'gold-wrapper.c'),str(renamed),*map(str,objects),*libs,'-lm','-o',str(out/'gold-pulse-fresh-test')]
 return compile_main,link,[renamed,*objects]

def dependency_tokens(text):
 text=text.replace('\\\n',' ');assert ':' in text
 return shlex.split(text.split(':',1)[1])

def resolve_traced(path,links):
 p=Path(path);assert p.is_absolute();parts=list(p.parts[1:]);cur=Path('/');hops=0
 while parts:
  part=parts.pop(0)
  if part in ('','.'):continue
  if part=='..':cur=cur.parent;continue
  entry=cur/part;st=entry.lstat()
  if stat.S_ISLNK(st.st_mode):
   target=os.readlink(entry);assert links.setdefault(str(entry),target)==target;hops+=1;assert hops<=128
   value=Path(target)
   if value.is_absolute():cur=Path('/');parts=list(value.parts[1:])+parts
   else:parts=list(value.parts)+parts
  else:cur=entry
 return cur

COMPILER_LINK_NAMES=('crt1.o','Scrt1.o','crti.o','crtbegin.o','crtbeginS.o','crtend.o','crtendS.o','crtn.o','libasan_preinit.o','libgcc.a','libgcc_s.so','libgcc_s.so.1')

def compiler_link_inputs(cc,env,links):
 # Finite current compiler runtime inputs for ordinary PIE and SAN/no-PIE.
 # These are current toolchain startup objects, never historical project objects.
 pins={};records={}
 for name in COMPILER_LINK_NAMES:
  token=subprocess.check_output([str(cc),'-print-file-name='+name],env=env).decode('utf-8').strip()
  path=Path(token);assert path.is_absolute(),('Unresolved compiler link input',name,token)
  actual=resolve_traced(path,links);assert actual.is_file();pin=SHA(actual)
  assert pins.setdefault(str(actual),pin)==pin
  records[name]={'reported_path':token,'resolved_path':str(actual),'sha256':pin}
 script=Path(records['libgcc_s.so']['resolved_path']).read_bytes()
 if not script.startswith(b'\x7fELF'):
  text=re.sub(r'/\*.*?\*/','',script.decode('ascii'),flags=re.S).strip()
  assert re.fullmatch(r'GROUP\s*\(\s*libgcc_s\.so\.1\s+-lgcc\s*\)',text),'Unrecognized libgcc linker-script target; fail closed'
  records['libgcc_s.so']['script_targets']=['libgcc_s.so.1','libgcc.a']
 return pins,records

def environment(sysroot,tmp,home):
 # No caller test flags, compiler paths, library/preload overrides or Make overrides.
 return {'PATH':'/usr/local/bin:/usr/bin:/bin','LANG':'C.UTF-8','LC_ALL':'C.UTF-8','PYTHONDONTWRITEBYTECODE':'1','GIT_OPTIONAL_LOCKS':'0',
 'PKG_CONFIG_SYSROOT_DIR':str(sysroot),'PKG_CONFIG_LIBDIR':str(sysroot/'usr/lib/x86_64-linux-gnu/pkgconfig'),
 'LD_LIBRARY_PATH':str(sysroot/'usr/lib/x86_64-linux-gnu'),'TMPDIR':str(tmp),'HOME':str(home),'XDG_CONFIG_HOME':str(home/'config'),
 'SDL_VIDEODRIVER':'dummy','SDL_AUDIODRIVER':'dummy','SDL_RENDER_DRIVER':'software','ASAN_OPTIONS':'detect_leaks=0:halt_on_error=1','UBSAN_OPTIONS':'halt_on_error=1:print_stacktrace=1'}

def stop_process(proc,row):
 errors=row.setdefault('cleanup_errors',[])
 for sig in (signal.SIGTERM,signal.SIGKILL):
  try:
   if proc.poll() is None:os.killpg(proc.pid,sig)
  except ProcessLookupError:pass
  except Exception as exc:errors.append(repr(exc))
  try:proc.wait(timeout=5);return
  except subprocess.TimeoutExpired:continue
  except Exception as exc:errors.append(repr(exc));return
 errors.append('Process not reaped after bounded TERM/KILL')

def run_process(argv,label,cwd,out,report,save,measure,env,payload=None,empty_stderr=False):
 row={'label':label,'argv':list(map(str,argv)),'cwd':str(cwd)};report['commands'].append(row);proc=None;feeder=None;feed_errors=[];failure=None;started=time.monotonic()
 try:
  save();measure()
  def no_core():resource.setrlimit(resource.RLIMIT_CORE,(0,0))
  with (out/(label+'.stdout')).open('xb') as so,(out/(label+'.stderr')).open('xb') as se:
   proc=subprocess.Popen(row['argv'],cwd=cwd,env=env,stdin=subprocess.PIPE if payload is not None else subprocess.DEVNULL,stdout=so,stderr=se,start_new_session=True,preexec_fn=no_core);row['pid']=proc.pid
   if payload is not None:
    row['stdin_sha256']=digest(payload)
    def feed():
     try:proc.stdin.write(payload);proc.stdin.close()
     except BaseException as exc:feed_errors.append(repr(exc))
    feeder=threading.Thread(target=feed,daemon=True)
   save()
   if feeder is not None:feeder.start()
   while proc.poll() is None:measure();assert time.monotonic()-started<1800,'Process timeout';time.sleep(.25)
   proc.wait()
 except BaseException as exc:
  failure=exc
  if proc is not None:stop_process(proc,row)
 finally:
  if feeder is not None and feeder.ident is not None:feeder.join(timeout=2)
  row.update(returncode=proc.returncode if proc else None,seconds=time.monotonic()-started,stdin_writer_errors=feed_errors)
  if failure:row['original_error']=repr(failure)
  try:save()
  except Exception as exc:
   row['result_save_error']=repr(exc)
   if failure is None:failure=exc
 if failure:raise failure
 assert row['returncode']==0 and not feed_errors and (feeder is None or not feeder.is_alive()),('Command failed',label,row)
 for kind in ('stdout','stderr'):
  p=out/(label+'.'+kind);row[kind+'_sha256']=SHA(p);row[kind+'_bytes']=p.stat().st_size
 if empty_stderr:assert (out/(label+'.stderr')).read_bytes()==b'',('Sanitizer/native diagnostic retained',label)
 measure();save();return (out/(label+'.stdout')).read_bytes()

def last_actual_budget(out,report,errors,save):
 used=free=None;ok=False
 try:
  used=allocated(out);free=shutil.disk_usage(out.parent).free;assert budget_ok(used,free,True);ok=True
 except Exception as exc:
  errors['last_actual_budget']=repr(exc);report['status']='FAIL_LAST_ACTUAL_BUDGET_RETAINED'
  try:save()
  except Exception as more:errors['last_save']=repr(more)
 return {'actual_allocated':used,'actual_free':free,'last_budget_ok':ok}


def main():
 parser=argparse.ArgumentParser(description=__doc__)
 for key in ('root','out','data','sysroot','protected-public','protected-profile','root-snapshot'):parser.add_argument('--'+key,type=Path,required=True)
 parser.add_argument('--root-snapshot-sha256',required=True)
 a=parser.parse_args();r=a.root.resolve();out=a.out.absolute();data=a.data.resolve();sysroot=a.sysroot.resolve();protected=a.protected_public.resolve()
 assert out.is_absolute() and not out.exists() and out.parent.is_dir() and not out.is_relative_to(r) and not out.is_relative_to(protected) and r!=protected
 assert shutil.disk_usage(out.parent).free>=START_REQUIRED
 assert SHA(a.root_snapshot)==a.root_snapshot_sha256 and re.fullmatch('[0-9a-f]{64}',a.root_snapshot_sha256)
 snapshot=json.loads(a.root_snapshot.read_text());assert snapshot['status']=='FROZEN_GOLD_SOURCE_BEFORE_FRESH' and snapshot['root']==str(r)
 before,raw,sem=identity(r);files=hydrated_manifest(r);assert before==snapshot['identity'] and files==snapshot['files']
 assert SHA(a.protected_profile)==PROTECTED_PROFILE_SHA;profile=json.loads(a.protected_profile.read_text());public_files=protected_manifest(protected,profile);pi,pr,ps=identity(protected);assert pi==PROTECTED_IDENTITY
 source={p[4:]:row['sha256'] for p,row in files.items() if p.startswith('src/')};old_source={p[4:]:row['sha256'] for p,row in public_files.items() if p.startswith('src/')};check_source_epoch(source,old_source)
 units=sorted(Path(p).stem for p in source if p.endswith('.c'));assert len(units)==86
 driver=Path(__file__).resolve();assert driver==r/'tests/projectile_gold_pulse_fresh_native_validation.py','Run only the installed ROOT driver, never an external fallback'
 native=load_native(r);blue=native.blue_helper(r);assert SHA(r/'tests/projectile_blue_triplet_native_validation.py')==OLD_BLUE_HELPER_SHA
 bundle,wrapper=native.source_bundle(r);assert {k:digest(v) for k,v in bundle.items()}==SOURCE_PINS and len(bundle['harness.c'])==262 and native.reverse_shim(wrapper)==bundle['harness.c']
 companion=r/'tests/projectile_gold_pulse_native_additions.c.inc';assert SHA(companion)==GOLD_COMPANION_SHA
 registration=native.registration(r);members={m['selector']:m for m in registration['members']};assert set(members)=={168,169} and {i:members[i]['hda_sha256'] for i in members}==HDA_GOLD
 old_stdin,new_stdin=native.native_inputs(r,data);assert (digest(old_stdin),digest(new_stdin))==STDIN_PINS
 expected_stdout={k:v.encode('utf-8') for k,v in native.LEGACY_STDOUT.items()};validate_stdout_bytes(expected_stdout)
 bound={str(a.root_snapshot.resolve()):SHA(a.root_snapshot),str(a.protected_profile.resolve()):PROTECTED_PROFILE_SHA};producers={};assets={};data_pins={};links={}
 for rel,row in files.items():
  if rel.startswith(('scripts/','tests/','authoring-inputs/projectile-gold-pulse-current/')) or rel=='Makefile':producers[str(r/rel)]=row['sha256']
  if rel.startswith(('assets/hd/current-compat/','assets/hd/global-assets-v1/content/','assets/hd/shared-menu-runs-v1/','authoring-inputs/projectile')):assets[str(r/rel)]=row['sha256']
 data_inventory=inventory(data);assert len(data_inventory)==99,'Expected complete recovered99 original game-data files'
 for rel,row in data_inventory.items():data_pins[str(data/rel)]=row['sha256']
 for name,pin in blue.DATA_SHA.items():assert data_pins[str(data/name)]==pin
 hdas={}
 for i in native.IDS:
  if i in native.GOLD:p=r/'assets/hd/current-compat/projectile-gold-pulse'/native.hda_name(i,blue);pin=HDA_GOLD[i]
  else:p=r/'assets/hd/current-compat'/('projectile-blue-triplet' if i in blue.BLUE else 'projectile'+str(i))/blue.HDA_NAMES[i];pin=blue.HDA_SHA[i]
  assert SHA(p)==pin and len(p.read_bytes())==43036;hdas[i]=p.read_bytes();assets[str(p)]=pin
 content=r/'assets/hd/global-assets-v1/content';assert content.is_dir();talon=content/'d1fe9bfe2dd84207fceb2f453c862eeaea802d9832fd14c1e1c3290622a53964.hda';assert SHA(talon)==talon.stem
 fixtures=native.fixture_payloads(r,hdas,registration);assert len(fixtures)==335 and sum(name.startswith('gold-packs/') for name in fixtures)==184
 leaves=['legacy264/'+name for name,_,_ in blue.PACKS]+['blue-packs/'+name for name in blue.PACK_NAMES]+['gold-packs/'+name for name in native.PACK_NAMES];assert len(leaves)==len(set(leaves))==60
 for rel,b in fixtures.items():assert not Path(rel).is_absolute() and '..' not in Path(rel).parts and Path(rel).parent.as_posix() in leaves
 headers=[r/'assets/hd/shared-menu-runs-v1'/n for n in ('reconstructed_run_specs.h','reconstructed_numeric_specs.h','reconstructed_name_source_specs.h')]
 assert all(str(p) in assets for p in headers)
 env=environment(sysroot,out/'tmp',out/'home');cc=Path(shutil.which('cc',path=env['PATH'])).resolve();pkg=Path(shutil.which('pkg-config',path=env['PATH'])).resolve();make=Path(shutil.which('make',path=env['PATH'])).resolve()
 builtin=Path(subprocess.check_output([cc,'-print-file-name=include'],env=env).decode().strip());assert builtin.is_dir()
 system={};tools={}
 for base in (sysroot/'usr/include',Path('/usr/include'),builtin):
  for p in base.rglob('*'):
   if p.is_file():actual=resolve_traced(p.absolute(),links);pin=SHA(actual);assert system.setdefault(str(actual),pin)==pin
 tool_paths={cc,pkg,make,Path(sys.executable).resolve(),Path(shutil.which('git',path=env['PATH'])).resolve()}
 for name in ('as','ld','cc1','collect2'):
  token=subprocess.check_output([cc,'-print-prog-name='+name],env=env).decode().strip();p=Path(token) if token.startswith('/') else Path(shutil.which(token,path=env['PATH']));tool_paths.add(p.resolve())
 for base,patterns in ((sysroot/'usr/lib/x86_64-linux-gnu',('libSDL2-2.0.so.*','libSDL2_net-2.0.so.*')),(Path('/usr/lib/x86_64-linux-gnu'),('libc.so.6','libm.so.6','libasan.so.8*','libubsan.so.1*','libgcc_s.so.1','libstdc++.so.6*','ld-linux-x86-64.so.2'))):
  for pattern in patterns:
   found=list(base.glob(pattern));assert found,(base,pattern)
   tool_paths.update(resolve_traced(p,links) for p in found)
 for p in tool_paths:tools[str(p)]=SHA(p)
 compiler_link_pins,compiler_link_records=compiler_link_inputs(cc,env,links);tools.update(compiler_link_pins)
 bound.update(producers);bound.update(assets);bound.update(data_pins);bound.update(system);bound.update(tools)
 assert identity(r)[0]==before and hydrated_manifest(r)==files and protected_manifest(protected,profile)==public_files
 report={'status':'PRELAUNCH_INITIALIZATION','scope':__doc__,'root_identity_before':before,'root_file_count':len(files),'source_sha256':source,'scripts_sha256':{p[8:]:v['sha256'] for p,v in files.items() if p.startswith('scripts/')},'protected_public_identity_before':pi,'protected_public_profile_sha256':PROTECTED_PROFILE_SHA,'producer_sha256':producers,'asset_sha256':assets,'original_data_sha256':data_pins,'original_data_inventory99':data_inventory,'current_system_header_sha256':system,'toolchain_sha256':tools,'compiler_link_inputs':compiler_link_records,'all_bound_inputs_sha256':bound,'actual_dependency_symlinks':links,'generated_input_sha256':{},'fresh_dependency_file_sha256':{},'fresh_dependency_sha256':{},'native_linked_objects_sha256':{},'fixture_sha256':{},'fixture_links':{},'new_artifacts_sha256':{},'commands':[],'builds_started':[],'modes':{},'historical_consumers':{},'historical_objects_consumed':0,'historical_executables_consumed':0,'historical_depfiles_consumed':0,'historical_sourcecopies_consumed':0,'all_builds_fresh':True,'reused_project_objects':0,'old107_stdin_sha256':digest(old_stdin),'old61_stdin_sha256':digest(new_stdin),'sample_interval_seconds':.25,'peak_cap':PEAK,'final_cap':FINAL_CAP,'reserve':RESERVE,'peak_allocated':0,'minimum_free':shutil.disk_usage(out.parent).free,'sanitizer_scope':'Fourthbuild all86projectTUs; native84newSANobjects+newrenamedmain+newrealrenderer/harness. External SDL/system libraries native; LSanoff.','outer_wrapper_scope':'Six original generated sources byte-exact; separate seventh main-rename+gold-dispatch wrapper is inverse-exact262B, not the original compile bytes.','retained_history':'Recovered original gold is UNKNOWN; epoch2 wrong-FNV native01 FAIL and correction/native02/gameplay proof remain separate immutable epochs. This run never edits old receipts.'}
 def measure(extra=0,final=False):
  used=allocated(out);free=shutil.disk_usage(out.parent).free;report['peak_allocated']=max(report['peak_allocated'],used);report['minimum_free']=min(report['minimum_free'],free)
  assert extra>=0 and budget_ok(used+extra,free-extra,final),(used,free,extra,final)
 def save():
  payload=(json.dumps(report,indent=2)+'\n').encode();p=out/'receipt.json';old=p.stat().st_blocks*512 if p.exists() else 0;measure(max(0,snapshot_allocation(payload)-old))
  with p.open('wb') as f:f.write(payload);f.flush();os.fsync(f.fileno())
 def write(p,b):
  measure(snapshot_allocation(b)+4096);p.parent.mkdir(parents=True,exist_ok=True)
  with p.open('xb') as f:f.write(b)
  assert p.stat().st_nlink==1 and SHA(p)==digest(b);report['new_artifacts_sha256'][str(p)]=digest(b);measure()
 def bind_dep(dep,cwd):
  report['fresh_dependency_file_sha256'][str(dep)]=SHA(dep);report['new_artifacts_sha256'][str(dep)]=SHA(dep)
  for token in dependency_tokens(dep.read_bytes().decode('utf-8')):
   path=resolve_traced(Path(token) if Path(token).is_absolute() else cwd/token,links);pin=SHA(path);expected=report['generated_input_sha256'].get(str(path),system.get(str(path)))
   for mode in MODES:
    build=out/(mode+'-build')
    if path.is_relative_to(build/'src'):expected=source.get(path.relative_to(build/'src').as_posix());break
    if path.is_relative_to(build/'assets'):expected=assets.get(str(r/path.relative_to(build)));break
   assert expected==pin,('Unbound fresh actual dependency',str(path),expected,pin)
   report['fresh_dependency_sha256'][str(path)]=pin
 def run(argv,label,cwd,payload=None,empty_stderr=False):
  result=run_process(argv,label,cwd,out,report,save,measure,env,payload,empty_stderr)
  for suffix in ('.stdout','.stderr'):p=out/(label+suffix);report['new_artifacts_sha256'][str(p)]=SHA(p)
  return result
 failure=None;started=time.monotonic()
 try:
  out.mkdir();(out/'tmp').mkdir();(out/'home').mkdir();measure();save();report['status']='RUNNING'
  write(out/'root-index-before.bin',raw);write(out/'root-index-semantic-before.bin',sem);write(out/'protected-index-before.bin',pr);write(out/'protected-index-semantic-before.bin',ps)
  write(out/'root-files-before.json',(json.dumps(files,indent=2)+'\n').encode());report['root_manifest_sha256']=SHA(out/'root-files-before.json')
  for name,b in bundle.items():write(out/name,b);report['generated_input_sha256'][str(out/name)]=digest(b)
  write(out/'gold-wrapper.c',wrapper);report['generated_input_sha256'][str(out/'gold-wrapper.c')]=digest(wrapper)
  write(out/companion.name,companion.read_bytes());report['generated_input_sha256'][str(out/companion.name)]=GOLD_COMPANION_SHA
  for mode in MODES:
   build=out/(mode+'-build');assert not build.exists();build.mkdir();report['builds_started'].append(mode)
   for rel,pin in source.items():write(build/'src'/rel,(r/'src'/rel).read_bytes());assert SHA(build/'src'/rel)==pin
   write(build/'Makefile',(r/'Makefile').read_bytes())
   for p in headers:write(build/p.relative_to(r),p.read_bytes())
   assert not (build/'obj').exists() and not (build/'opentyrian2000').exists()
   argv=make_command(mode,sysroot,cc,pkg);argv[0]=str(make);output=run(argv,mode+'-build',build,empty_stderr=mode=='hd-on-asan-ubsan')
   objects={p.name:SHA(p) for p in (build/'obj').glob('*.o')};assert set(objects)=={u+'.o' for u in units}
   assert {p.relative_to(build/'src').as_posix():SHA(p) for p in (build/'src').rglob('*') if p.is_file()}==source
   commands,link=compile_contract(output.decode('utf-8'),units,mode);deps=list((build/'obj').glob('*.d'));assert len(deps)==86 and {p.stem for p in deps}==set(units)
   for p in deps:bind_dep(p,build)
   for p in (build/'obj').glob('*.o'):report['new_artifacts_sha256'][str(p)]=SHA(p)
   binary=build/'opentyrian2000';report['new_artifacts_sha256'][str(binary)]=SHA(binary)
   report['modes'][mode]={'objects_sha256':objects,'binary_sha256':SHA(binary),'source_sha256':source.copy(),'compile_commands':commands,'link_command':link,'fresh_object_count':86,'sanitized':mode=='hd-on-asan-ubsan'};measure();save()
  build=out/'hd-on-asan-ubsan-build';cflags=shlex.split(subprocess.check_output([pkg,'--cflags','sdl2','SDL2_net'],env=env).decode());libs=shlex.split(subprocess.check_output([pkg,'--libs','sdl2','SDL2_net'],env=env).decode());cflags=['-I'+str(sysroot/'usr/include/x86_64-linux-gnu'),*cflags]
  compile_main,link,objects=native_compile_commands(cc,build,out,cflags,libs)
  run(compile_main,'renamed-main',out,empty_stderr=True);bind_dep(out/'renamed-main.d',out);report['new_artifacts_sha256'][str(build/'opentyr-test.o')]=SHA(build/'opentyr-test.o')
  run(link,'full-sanitized-harness',out,empty_stderr=True);bind_dep(out/'renderer-harness.d',out);exe=out/'gold-pulse-fresh-test';report['native_binary_sha256']=SHA(exe);report['new_artifacts_sha256'][str(exe)]=SHA(exe)
  report['native_linked_objects_sha256']={str(p):SHA(p) for p in objects};assert len(objects)==85 and all(p.is_relative_to(build) for p in objects)
  assert len(report['fresh_dependency_file_sha256'])==346
  actual={resolve_traced(Path(t) if Path(t).is_absolute() else out/t,links) for t in dependency_tokens((out/'renderer-harness.d').read_bytes().decode())}
  required={build/'src'/n for n in ('render_mirror.c','global_projectile91_mirror.inc','enemy_blue_triplet_mirror.inc','current_projectile_blue_triplet_payload_pins.h','enemy_gold_pulse_mirror.inc','current_projectile_gold_pulse_payload_pins.h')}
  required.update(out/n for n in ('gold-wrapper.c','projectile_gold_pulse_native_additions.c.inc',*bundle));required.remove(out/'harness.c') # Original preserved; derived seventh wrapper is compile consumer.
  assert required<=actual,('Required actual native includes missing',sorted(map(str,required-actual)))
  for leaf in leaves:
   dest=out/leaf;dest.mkdir(parents=True);(dest/'content').symlink_to(content,target_is_directory=True);report['fixture_links'][str(dest/'content')]=str(content);measure()
  for rel,b in fixtures.items():write(out/rel,b);report['fixture_sha256'][str(out/rel)]=digest(b)
  assert len(report['fixture_sha256'])==335
  legacy=[out/'legacy264'/name for name,_,_ in blue.PACKS];outputs={}
  for label,key,argv,payload in [('inherited107','inherited107_stdout',[exe,'--inherited107',*legacy[:5]],old_stdin),('inherited61','inherited61_stdout',[exe,'--projectile61',*legacy],new_stdin),('new-blue-triplet','new_blue_stdout',[exe,'--blue-triplet',out/'blue-packs'],new_stdin)]:
   assert SHA(exe)==report['native_binary_sha256'];outputs[key]=run(argv,label,out,payload,True);assert outputs[key]==expected_stdout[key]
  validate_stdout_bytes(outputs);legacy_counts=native.verify_legacy_stdout({k:v.decode('utf-8') for k,v in outputs.items()});assert legacy_counts['cases']==629 and legacy_counts['assertions']==12208831
  assert SHA(exe)==report['native_binary_sha256'];gold=run([exe,'--gold-pulse',out/'gold-packs'],'gold251',out,new_stdin,True);assert digest(gold)==GOLD_STDOUT_SHA
  counts=native.parse_gold_stdout(gold.decode('utf-8'));assert counts['cases']==251 and counts['assertions']==38046959
  report.update(status=SUCCESS,**{k:v.decode('utf-8') for k,v in outputs.items()},gold251_stdout=gold.decode('utf-8'),old629=legacy_counts,gold251=counts,total_cases=880,total_assertions=50255790);measure(final=True)
 except BaseException as exc:failure=exc;report.update(status='FAIL_RETAINED',error=repr(exc))
 finally:
  report['status_before_final_checks']=report['status'];checks={};errors={}
  try:save()
  except Exception as exc:errors['save_original_result']=repr(exc)
  def check(name,fn):return guarded_check(checks,errors,name,fn)
  check('complete_current_root_unchanged',lambda:hydrated_manifest(r)==files)
  check('protected_public_root_unchanged',lambda:protected_manifest(protected,profile)==public_files)
  check('original_data99_unchanged',lambda:inventory(data)==data_inventory)
  check('all_actual_inputs_unchanged',lambda:all(SHA(p)==v for p,v in bound.items()))
  check('all_new_artifacts_unchanged',lambda:all(SHA(p)==v for p,v in report['new_artifacts_sha256'].items()))
  check('all_new_dependencies_unchanged',lambda:all(SHA(p)==v for p,v in report['fresh_dependency_sha256'].items()))
  check('all_native_linked_objects_unchanged',lambda:all(SHA(p)==v for p,v in report['native_linked_objects_sha256'].items()))
  check('fixture_links_unchanged',lambda:all(Path(p).is_symlink() and os.readlink(p)==v for p,v in report['fixture_links'].items()))
  check('dependency_link_texts_unchanged',lambda:all(Path(p).is_symlink() and os.readlink(p)==v for p,v in links.items()))
  check('original_six_and_outer_inverse',lambda:all(SHA(out/k)==v for k,v in SOURCE_PINS.items()) and native.reverse_shim((out/'gold-wrapper.c').read_bytes())==bundle['harness.c'])
  check('no_game_captures',lambda:not list(out.rglob('*.bmp')) and not list(out.rglob('*.png')))
  def final_indices():
   after,ra,se=identity(r);pa,pra,pse=identity(protected);report['root_identity_after']=after;report['protected_public_identity_after']=pa
   measure(snapshot_allocation(ra,se,pra,pse)+262144,final=True)
   for name,b in [('root-index-after.bin',ra),('root-index-semantic-after.bin',se),('protected-index-after.bin',pra),('protected-index-semantic-after.bin',pse)]:write(out/name,b)
   measure(262144,final=True);return after==before and pa==pi
  check('actual_indices_unchanged_and_saved',final_indices)
  report.update(checks=checks,final_check_errors=errors,seconds=time.monotonic()-started)
  if errors or not all(checks.values()):report['status']='FAIL_FINAL_BINDING_OR_BUDGET_RETAINED'
  try:measure(262144,final=True);report['final_allocated_before_receipt']=allocated(out);report['free_before_receipt']=shutil.disk_usage(out.parent).free;save();measure(final=True)
  except Exception as exc:
   errors['postwrite_budget_or_save']=repr(exc);report['status']='FAIL_RECEIPT_OR_FINAL_BUDGET_RETAINED'
   try:save()
   except Exception as more:errors['final_save']=repr(more)
  actual=last_actual_budget(out,report,errors,save);print(json.dumps({'status':report['status'],'total_cases':report.get('total_cases'),'total_assertions':report.get('total_assertions'),'peak_allocated':report['peak_allocated'],**actual,'error':report.get('error'),'final_errors':errors}))
 if failure:raise failure
 assert report['status']==SUCCESS,report['status']
if __name__=='__main__':main()
