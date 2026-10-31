#!/usr/bin/env python3
"""Four empty independent builds and five actual native processes: 107+157+365+251+449.
Current ROOT inputs only; no historical receipt/object/.d/ELF/source fallback.
All86 project TUs/config fresh; 84 fresh SAN objects+fresh renamed main+real
renderer/harness. System SDL remains native, LSan off. Not gameplay/fullgate.
Qualified gold root is protected with its actual f64 HEAD and frozen staged index;
its public-tree equivalence never substitutes a different HEAD. No source/index writes, refresh, staging, retry or auto-cleanup.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,re,resource,shlex,shutil,signal,stat,subprocess,sys,threading,time
sys.dont_write_bytecode=True
SHA=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(data):return hashlib.sha256(data).hexdigest()
PEAK=384*1024**2;FINAL_CAP=288*1024**2;LOG_CAP=48*1024**2;RESERVE=250*1024**2;START_REQUIRED=PEAK+RESERVE
MODES={'default-off':'','hd-on':'-DNEWSHF_HD_COMPOSITOR=1','mirror-disabled':'-DNEWSHF_HD_COMPOSITOR=1 -DRENDER_MIRROR_DISABLED','hd-on-asan-ubsan':'-DNEWSHF_HD_COMPOSITOR=1'}
SAN=('-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie')
DEFAULT_CFLAGS='-pedantic -Wall -Wextra -Wno-format-truncation -Wno-missing-field-initializers -O2'
SUCCESS='PASS_FOUR_FRESH_CONFIGS_AND_FULL_PROJECT_SANITIZED1329'
NATIVE_HELPER_SHA='88f2d4ccb4fbca8be4d00b11d501cf8cfb076a70cc9355bf887d045ffa4fa90a'
STATICS_COMPANION_SHA='6886018f5bc62216ae48797ae888fbd169fcdbee3d42107856872b536d4e866e'
GOLD_WRAPPER_SHA='cf43c879e05018407aafb293116c0731ba9f87ea03f9097fca79a91016096792'
GOLD_COMPANION_SHA='b00796c4d72265022da0e9e4e1c46acbbbff00ee754b5a51a61701aa778e6f46'
OLD_BLUE_HELPER_SHA='38d904bf84c17ae9179c6c4bc4ca895f31393efcc774ac851d7db1bc6a23ef6d'
PROTECTED_PROFILE_SHA='bf9f8209cc4db5c5dc0b6d06e3713f4357fd26fd6619e21a6995ff0183694843'
PROTECTED_IDENTITY={'head':'f64a7ddc6bbf11a0667665f4faf5b6db6c9ea6bc','raw_sha256':'e579802d832d2be0ba6628927c175377e1d71ec2eb04cf93a6ad0758e6606d56','semantic_sha256':'8c775eaa2e44eb4ec489eeb9a102130f9d3fe5629fe73f522028c6bdb34b9d2e'}
PROTECTED_TREE='945bb6e98d98056c094120617fe538199de5ddbd'
PRODUCTION6={
 'current_projectile_statics_payload_pins.h':'2b859dba5213af576fc2aadf76ddacabc59df3fc5e1ca1a8da863ddf2d93f90b',
 'enemy_statics_mirror.inc':'2aca7e11a03882eea6543640b735a0919fec82462165c24476c2dd231a027c18',
 'entity_draw.c':'177c22892477630908be83ef011013b0490dcd5d343f4c0d68846e70acd51182',
 'global_projectile91_mirror.inc':'0e0088a93502ff55fb086c9a52c841bb3593cb61fd7a44b567ce57771dd5762a',
 'render_mirror.c':'387710a63568932245a7f9f1e87fea004bb28c60fabb487d3dd63ecdcc4a4f19',
 'tyrian2.c':'240a6d6c05d114d34d41d20235ebc1f730ac96f34863a1b4ce01fbbb86a63e19'}
SOURCE_PINS={'inherited145_harness.c':'8925fb11215446339f067124fa7223ec48dc7c86459e303d3803477773b2d9ac','accepted_projectile61_native_additions.c.inc':'5f80d681e84a6dff20873f7f05bb3a02e3fd0f22013edf2b5fbf133d36c51cfe','accepted61_wrapper.c':'59bfbe4d8e3bb8db4403eaabb199d8ff2f09b2eb2047769f39069c93dff7f4eb','projectile61_native_additions.c.inc':'d894e392ce315b855d5a764fbb526b6d6568a14f223e7e577a4ebf303ecbf67a','projectile_blue_triplet_native_additions.c.inc':'cf38a2c8582bf9c3299a84721d37dae83402b938c859a2489ad382844a9a6084','harness.c':'d39e3b9633eff3abfc70604f96895f21184fa87ad7f344ffa64f2b7705b353e1'}
STDIN_PINS=('7dedf7066696fc278f5fbb8dfb1462e7b6ac290cb5d08ae5260a6cdabc1ecca7','a9739298f031cafbfefb3befd359750872f6caafe69ebf5c7cf948544713830b')
STDOUT_PINS={'inherited107_stdout':('56b267d7cf607164010655de7fbd79fa42d3dc4518865434c2c4b705280856b2',236),'inherited61_stdout':('bbc4b539205c19faa66ec7ada0c755d80907950e9ab91b554633c77fe261bcf4',165),'new_blue_stdout':('833b3944bde9933444f4102716403b9868e1cefec4a077daeecd8535bef5208e',631)}
GOLD_STDOUT_SHA='a1f762926d2fb3bbc2499c5d7dc87f94cd20e239189f69af3646dcc58c4459d5'
STDOUT_PINS['gold251_stdout']=(GOLD_STDOUT_SHA,973)
HDA_STATICS={162:'2d045f7fc472ed6e2f33f9d742072f3b7ea1c3a606d8f1909bbcd33b57ae0119',260:'5545ee065fcf879eb306a6c25dc0b9be8ecf8dcaa5154cdbb69ae907e75adf8e'}
HDA_GOLD={168:'a453142d1d1d5e662a5c36053f5af42b719fa2a2d993e7b2384c5d4231cfdb14',169:'1dc205caccc8320968389868f844cacd50046a285b2d1e90f5b9073fcfddc831'}


def allocated(root,races=None):
 root=Path(root)
 total=0
 def visit(path):
  nonlocal total
  try:
   st=path.lstat();total+=st.st_blocks*512
   if stat.S_ISDIR(st.st_mode):
    with os.scandir(path) as entries:
     for entry in entries:visit(Path(entry.path))
  except FileNotFoundError:
   if races is None or not path.is_relative_to(root/'tmp'):raise
   races.append({'path':str(path),'utc_ns':time.time_ns()})
 visit(root);return total

def budget_ok(used,free,final=False,logs=0):return used<=(FINAL_CAP if final else PEAK) and free>=RESERVE and 0<=logs<=LOG_CAP

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
 assert len(profile)==9800,'Exact qualified-gold9800 profile required'
 actual=inventory(root);expected={path:{'sha256':row['sha256'],'bytes':row['bytes'],'mode':row['mode'],'nlink':1} for path,row in profile.items()}
 assert actual==expected and identity(root)[0]==PROTECTED_IDENTITY
 return actual

def check_source_epoch(source,protected_source):
 assert len(protected_source)==314 and len(source)==316
 expected={**protected_source,**PRODUCTION6};assert source==expected,'Production source differs from selected six-file statics overlay'
 assert len([p for p in source if p.endswith('.c')])==86
 return True

def validate_stdout_bytes(actual):
 assert set(actual)==set(STDOUT_PINS)
 for name,data in actual.items():
  assert isinstance(data,bytes);pin,size=STDOUT_PINS[name];assert len(data)==size and digest(data)==pin,('Original880 stdout bytes changed',name)
 return True

def load_native(root):
 assert re.fullmatch('[0-9a-f]{64}',NATIVE_HELPER_SHA),'DRAFT helper pin: execution forbidden'
 path=root/'tests/projectile_statics_native_validation.py';assert SHA(path)==NATIVE_HELPER_SHA,'Installed-only helper mismatch; no external fallback'
 spec=importlib.util.spec_from_file_location('statics_current_helpers',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def make_command(mode,sysroot,cc,pkg):
 assert mode in MODES
 cpp='-MD -DNDEBUG '+MODES[mode]+' -I'+str(sysroot/'usr/include/x86_64-linux-gnu');ld='-Wl,-rpath,'+str(sysroot/'usr/lib/x86_64-linux-gnu');flags=DEFAULT_CFLAGS
 if mode=='hd-on-asan-ubsan':ld+=' -fsanitize=address,undefined -no-pie';flags='-O1 -g '+' '.join(SAN)
 return ['make','-j2','CC='+str(cc),'PKG_CONFIG='+str(pkg),'VCS_IDREV=printf enemy-statics-fresh-native','CPPFLAGS='+cpp,'CFLAGS='+flags,'LDFLAGS='+ld]

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
 link=[str(cc),*flags,'-MD','-MF',str(out/'renderer-harness.d'),str(out/'statics-wrapper.c'),str(renamed),*map(str,objects),*libs,'-lm','-o',str(out/'enemy-statics-fresh-test')]
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

COMPILER_LINK_NAMES=('crt1.o','Scrt1.o','crti.o','crtbegin.o','crtbeginS.o','crtend.o','crtendS.o','crtn.o','libasan_preinit.o','libgcc.a','libgcc_s.so','libgcc_s.so.1','libc.so','libm.so','libc.so.6','libc_nonshared.a','ld-linux-x86-64.so.2','libm.so.6','libmvec.so.1','libasan.so','libubsan.so')
SCRIPT_TEXT={
 'libgcc_s.so':'GROUP ( libgcc_s.so.1 -lgcc )',
 'libc.so':'OUTPUT_FORMAT(elf64-x86-64) GROUP ( /lib/x86_64-linux-gnu/libc.so.6 /usr/lib/x86_64-linux-gnu/libc_nonshared.a AS_NEEDED ( /lib64/ld-linux-x86-64.so.2 ) )',
 'libm.so':'OUTPUT_FORMAT(elf64-x86-64) GROUP ( /lib/x86_64-linux-gnu/libm.so.6 AS_NEEDED ( /lib/x86_64-linux-gnu/libmvec.so.1 ) )'}
SCRIPT_TARGETS={
 'libgcc_s.so':(('libgcc_s.so.1','libgcc_s.so.1'),('libgcc.a','-lgcc')),
 'libc.so':(('libc.so.6','/lib/x86_64-linux-gnu/libc.so.6'),('libc_nonshared.a','/usr/lib/x86_64-linux-gnu/libc_nonshared.a'),('ld-linux-x86-64.so.2','/lib64/ld-linux-x86-64.so.2')),
 'libm.so':(('libm.so.6','/lib/x86_64-linux-gnu/libm.so.6'),('libmvec.so.1','/lib/x86_64-linux-gnu/libmvec.so.1'))}

def compiler_link_inputs(cc,env,links):
 # Finite current startup objects, archives, all three GNU scripts AND targets.
 # Current compiler inputs are not historical project objects or qualification receipts.
 pins={};records={}
 for name in COMPILER_LINK_NAMES:
  token=subprocess.check_output([str(cc),'-print-file-name='+name],env=env).decode('utf-8').strip()
  path=Path(token);assert path.is_absolute(),('Unresolved compiler link input',name,token)
  actual=resolve_traced(path,links);assert actual.is_file();pin=SHA(actual)
  assert pins.setdefault(str(actual),pin)==pin
  records[name]={'reported_path':token,'resolved_path':str(actual),'sha256':pin}
 for name,expected in SCRIPT_TEXT.items():
  payload=Path(records[name]['resolved_path']).read_bytes();text=re.sub(r'/\*.*?\*/','',payload.decode('ascii'),flags=re.S)
  assert re.sub(r'\s+','',text)==re.sub(r'\s+','',expected),('Unrecognized '+name.split('.')[0]+' linker-script syntax/target; fail closed')
  targets=[]
  for target,token in SCRIPT_TARGETS[name]:
   actual=resolve_traced(Path(token) if Path(token).is_absolute() else Path(records[target]['reported_path']),links)
   assert str(actual)==records[target]['resolved_path'],('Script target differs from compiler query',name,target)
   targets.append({'name':target,'script_path':token,'resolved_path':str(actual),'sha256':pins[str(actual)]})
  records[name]['script_targets']=[n for n,_ in SCRIPT_TARGETS[name]];records[name]['resolved_script_targets']=targets
 for name,row in records.items():
  if name not in SCRIPT_TEXT:
   payload=Path(row['resolved_path']).read_bytes();assert payload.startswith(b'!<arch>\n' if name.endswith('.a') else b'\x7fELF'),('Unexpected compiler target format',name)
 return pins,records

def sdl_link_inputs(pkg,sysroot,env,links):
 libdir=sysroot/'usr/lib/x86_64-linux-gnu';pins={};aliases={}
 argv=shlex.split(subprocess.check_output([str(pkg),'--libs','sdl2','SDL2_net'],env=env).decode('utf-8'))
 assert argv==['-L'+str(libdir),'-lSDL2_net','-lSDL2'],'Unexpected current SDL link flags/order'
 for name in ('libSDL2.so','libSDL2_net.so','pkgconfig/sdl2.pc','pkgconfig/SDL2_net.pc'):
  alias=libdir/name;actual=resolve_traced(alias,links)
  if name.endswith('.so'):assert actual.read_bytes().startswith(b'\x7fELF')
  pins[str(actual)]=SHA(actual);aliases[str(alias)]=str(actual)
 absent=[str(libdir/('lib'+name+suffix)) for name in ('c','m','asan','ubsan','gcc_s','gcc') for suffix in ('.so','.a')]
 assert all(not os.path.lexists(p) for p in absent),'Sysroot shadows compiler-resolved library'
 return pins,{'argv':argv,'aliases':aliases,'shadow_paths_absent':absent}

def loaded_runtime_inputs(links):
 # Actual Linux interpreter/Pillow mapped ELF closure, not guessed install-prefix.
 pins={}
 for line in Path('/proc/self/maps').read_text().splitlines():
  fields=line.split(None,5)
  if len(fields)==6 and fields[5].startswith('/'):
   token=fields[5];assert not token.endswith(' (deleted)'),'Deleted mapped runtime input'
   actual=resolve_traced(Path(token),links);assert actual.is_file();pins[str(actual)]=SHA(actual)
 assert pins,'No current interpreter mappings'
 return pins

def environment(sysroot,tmp,home):
 # No caller test flags, compiler paths, library/preload overrides or Make overrides.
 return {'PATH':'/usr/local/bin:/usr/bin:/bin','LANG':'C.UTF-8','LC_ALL':'C.UTF-8','PYTHONDONTWRITEBYTECODE':'1','GIT_OPTIONAL_LOCKS':'0',
 'PKG_CONFIG_SYSROOT_DIR':str(sysroot),'PKG_CONFIG_LIBDIR':str(sysroot/'usr/lib/x86_64-linux-gnu/pkgconfig'),
 'LD_LIBRARY_PATH':str(sysroot/'usr/lib/x86_64-linux-gnu'),'TMPDIR':str(tmp),'HOME':str(home),'XDG_CONFIG_HOME':str(home/'config'),
 'SDL_VIDEODRIVER':'dummy','SDL_AUDIODRIVER':'dummy','SDL_RENDER_DRIVER':'software','ASAN_OPTIONS':'detect_leaks=0:halt_on_error=1','UBSAN_OPTIONS':'halt_on_error=1:print_stacktrace=1'}

def stop_process(proc,row):
 errors=row.setdefault('cleanup_errors',[]);reaped=False
 for sig in (signal.SIGTERM,signal.SIGKILL):
  # Also signal the process group after parent exit: inherited pipe owners matter.
  try:os.killpg(proc.pid,sig)
  except ProcessLookupError:pass
  except Exception as exc:errors.append(repr(exc))
  try:proc.wait(timeout=5);reaped=True
  except subprocess.TimeoutExpired:pass
  except Exception as exc:errors.append(repr(exc))
 if not reaped:errors.append('Process not reaped after bounded TERM/KILL');row['cleanup_incomplete']=True
 return reaped

def run_process(argv,label,cwd,out,report,save,measure,env,payload=None,empty_stderr=False):
 row={'label':label,'argv':list(map(str,argv)),'cwd':str(cwd)};report['commands'].append(row)
 proc=None;feeder=None;feed_errors=[];failure=None;result=None;started=time.monotonic()
 def retain(exc,key):
  nonlocal failure
  row.setdefault('secondary_errors',[]).append({key:repr(exc)})
  if failure is None:failure=exc
 try:
  save();measure()
  def no_core():resource.setrlimit(resource.RLIMIT_CORE,(0,0))
  with (out/(label+'.stdout')).open('xb') as so,(out/(label+'.stderr')).open('xb') as se:
   proc=subprocess.Popen(row['argv'],cwd=cwd,env=env,stdin=subprocess.PIPE if payload is not None else subprocess.DEVNULL,stdout=so,stderr=se,start_new_session=True,preexec_fn=no_core);row['pid']=proc.pid
   if payload is not None:
    assert isinstance(payload,bytes);row['stdin_sha256']=digest(payload);row['stdin_bytes']=len(payload)
    def feed():
     try:
      assert proc.stdin.write(payload)==len(payload),'Short RAM stdin write';proc.stdin.close()
     except BaseException as exc:feed_errors.append(repr(exc))
    feeder=threading.Thread(target=feed,daemon=True)
   save()
   if feeder is not None:feeder.start()
   while proc.poll() is None:measure();assert time.monotonic()-started<1200,'Process timeout';time.sleep(.25)
   proc.wait(timeout=5)
 except BaseException as exc:
  failure=exc
  if proc is not None:
   try:stop_process(proc,row)
   except BaseException as more:retain(more,'cleanup');row['cleanup_incomplete']=True
 finally:
  if feeder is not None and feeder.ident is not None:
   try:
    feeder.join(timeout=2)
    if feeder.is_alive():row['cleanup_incomplete']=True;raise RuntimeError('RAM feeder did not terminate')
   except BaseException as exc:retain(exc,'feeder_join')
  row.update(returncode=proc.returncode if proc else None,seconds=time.monotonic()-started,stdin_writer_errors=feed_errors)
  if failure is not None:row['original_error']=repr(failure)
  try:
   assert failure is None or proc is None or not row.get('cleanup_incomplete'),'Cleanup uncertain; stage must not be resumed'
   if failure is None:assert row['returncode']==0 and not feed_errors,('Command failed',label,row)
   for kind in ('stdout','stderr'):
    p=out/(label+'.'+kind)
    if p.exists():row[kind+'_sha256']=SHA(p);row[kind+'_bytes']=p.stat().st_size
   if failure is None:
    result=(out/(label+'.stdout')).read_bytes()
    if empty_stderr:assert (out/(label+'.stderr')).read_bytes()==b'',('Sanitizer/native diagnostic retained',label)
   measure()
  except BaseException as exc:retain(exc,'result_read_or_budget')
  try:save()
  except BaseException as exc:retain(exc,'result_save_error')
  if failure is not None:row.setdefault('original_error',repr(failure))
 if failure is not None:raise failure
 return result

def last_actual_budget(out,report,errors,save):
 used=free=None;ok=False
 try:
  used=allocated(out);free=shutil.disk_usage(out.parent).free;assert budget_ok(used,free,True);ok=True
 except Exception as exc:
  errors['last_actual_budget']=repr(exc)
  if report['status']!='UNKNOWN_PROCESS_CLEANUP_RETAINED':report['status']='FAIL_LAST_ACTUAL_BUDGET_RETAINED'
  try:save()
  except Exception as more:errors['last_save']=repr(more)
 return {'actual_allocated':used,'actual_free':free,'last_budget_ok':ok}


def main():
 parser=argparse.ArgumentParser(description=__doc__)
 for key in ('root','stage','data','sysroot','protected-qualifiedgold','protected-profile','root-snapshot'):parser.add_argument('--'+key,type=Path,required=True)
 parser.add_argument('--root-snapshot-sha256',required=True)
 a=parser.parse_args();out=a.stage.absolute();created=False;ready=False;failure=None;started=time.monotonic();finalizers=[]
 report={'status':'PRELAUNCH_INITIALIZATION','scope':__doc__,'commands':[],'builds_started':[],'modes':{},'historical_consumers':{},'historical_objects_consumed':0,'historical_executables_consumed':0,'historical_depfiles_consumed':0,'historical_sourcecopies_consumed':0,'all_builds_fresh':True,'reused_project_objects':0,'new_artifacts_sha256':{},'generated_input_sha256':{},'fresh_dependency_file_sha256':{},'fresh_dependency_sha256':{},'native_linked_objects_sha256':{},'fixture_sha256':{},'fixture_links':{},'tmp_enoent_races':[],'peak_allocated':0,'minimum_free':None,'peak_cap':PEAK,'final_cap':FINAL_CAP,'log_cap':LOG_CAP,'reserve':RESERVE,'start_required':START_REQUIRED,'sample_interval_seconds':.25,'sanitizer_scope':'All86projectTUs in fourthbuild, native84newSANobjects+newrenamedmain+newactualrenderer/harness. External SDL/system libraries native; LSanoff.','outer_wrapper_scope':'Preserve original six sources + gold wrapper + gold companion; distinct new statics wrapper reverses to gold wrapper then262B old harness.','preflight_complete':False}
 def measure(extra=0,final=False):
  used=allocated(out,report['tmp_enoent_races']);free=shutil.disk_usage(out.parent).free
  logs=sum(p.lstat().st_blocks*512 for p in out.iterdir() if p.name.endswith(('.stdout','.stderr'))) if created else 0
  report['peak_allocated']=max(report['peak_allocated'],used);report['minimum_free']=free if report['minimum_free'] is None else min(report['minimum_free'],free);report['logs_allocated']=logs
  assert extra>=0 and budget_ok(used+extra,free-extra,final,logs),(used,free,extra,final,logs)
 def save():
  assert created,'Stage initialization failed; never overwrite an existing stage'
  payload=(json.dumps(report,indent=2)+'\n').encode();p=out/'receipt.json';old=p.stat().st_blocks*512 if p.exists() else 0;measure(max(0,snapshot_allocation(payload)-old))
  with p.open('wb') as f:assert f.write(payload)==len(payload);f.flush();os.fsync(f.fileno())
 def write(p,b):
  assert created and p.is_relative_to(out) and not os.path.lexists(p)
  missing=sum(not parent.exists() for parent in (p.parent,*p.parent.parents) if parent.is_relative_to(out))
  measure(snapshot_allocation(b)+4096*(missing+1));p.parent.mkdir(parents=True,exist_ok=True)
  with p.open('xb') as f:assert f.write(b)==len(b)
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
  assert ready,'No compile/process before complete preflight'
  result=run_process(argv,label,cwd,out,report,save,measure,env,payload,empty_stderr)
  for suffix in ('.stdout','.stderr'):p=out/(label+suffix);report['new_artifacts_sha256'][str(p)]=SHA(p)
  return result
 try:
  r=a.root.resolve(strict=True);data=a.data.resolve(strict=True);sysroot=a.sysroot.resolve(strict=True);protected=a.protected_qualifiedgold.resolve(strict=True)
  assert all(p.absolute()==p.resolve(strict=True) for p in (a.root,a.data,a.sysroot,a.protected_qualifiedgold)),'Root aliases forbidden'
  assert out.parent.resolve(strict=True)==out.parent and not os.path.lexists(out) and r!=protected
  assert all(not out.is_relative_to(p) and not p.is_relative_to(out) for p in (r,protected,data,sysroot))
  assert shutil.disk_usage(out.parent).free>=START_REQUIRED
  out.mkdir();created=True;(out/'tmp').mkdir();(out/'home').mkdir();measure();save()
  assert all(p.absolute()==p.resolve(strict=True) for p in (a.root_snapshot,a.protected_profile)),'Snapshot/profile aliases forbidden'
  assert re.fullmatch('[0-9a-f]{64}',a.root_snapshot_sha256) and SHA(a.root_snapshot)==a.root_snapshot_sha256
  snapshot=json.loads(a.root_snapshot.read_bytes());assert snapshot['status']=='FROZEN_STATICS_SOURCE_BEFORE_FRESH' and snapshot['root']==str(r)
  before,raw,sem=identity(r);files=hydrated_manifest(r);assert before==snapshot['identity'] and files==snapshot['files'] and len(files)==9826
  finalizers.append(('complete_current_root_unchanged',lambda:hydrated_manifest(r)==files and identity(r)[0]==before))
  assert SHA(a.protected_profile)==PROTECTED_PROFILE_SHA;profile=json.loads(a.protected_profile.read_bytes());public_files=protected_manifest(protected,profile);pi,pr,ps=identity(protected)
  finalizers.append(('protected_qualifiedgold_root_unchanged',lambda:protected_manifest(protected,profile)==public_files))
  def final_indices():
   after,ra,se=identity(r);pa,pra,pse=identity(protected);report['root_identity_after']=after;report['protected_qualifiedgold_identity_after']=pa
   measure(snapshot_allocation(ra,se,pra,pse)+262144,final=True)
   for name,b in [('root-index-after.bin',ra),('root-index-semantic-after.bin',se),('protected-index-after.bin',pra),('protected-index-semantic-after.bin',pse)]:write(out/name,b)
   measure(262144,final=True);return after==before and pa==pi
  finalizers.append(('actual_indices_unchanged_and_saved',final_indices))
  source={p[4:]:row['sha256'] for p,row in files.items() if p.startswith('src/')};old_source={p[4:]:row['sha256'] for p,row in public_files.items() if p.startswith('src/')};check_source_epoch(source,old_source)
  units=sorted(Path(p).stem for p in source if p.endswith('.c'));assert len(units)==86
  driver=Path(__file__).resolve();assert driver==r/'tests/projectile_statics_fresh_native_validation.py','Run only installed ROOT driver, never an external fallback'
  native=load_native(r);gold=native.gold_helper(r);blue=gold.blue_helper(r);assert SHA(r/'tests/projectile_blue_triplet_native_validation.py')==OLD_BLUE_HELPER_SHA
  bundle,wrapper=native.source_bundle(r);gold_wrapper=native.reverse_shim(wrapper)
  assert {k:digest(v) for k,v in bundle.items()}==SOURCE_PINS and len(bundle['harness.c'])==262 and digest(gold_wrapper)==GOLD_WRAPPER_SHA and gold.reverse_shim(gold_wrapper)==bundle['harness.c']
  gold_c=(r/'tests/projectile_gold_pulse_native_additions.c.inc').read_bytes();statics_c=(r/'tests/projectile_statics_native_additions.c.inc').read_bytes()
  assert digest(gold_c)==GOLD_COMPANION_SHA and digest(statics_c)==STATICS_COMPANION_SHA
  registration=native.registration(r);assert {m['selector']:m['hda_sha256'] for m in registration['members']}==HDA_STATICS
  old_stdin,new_stdin=native.native_inputs(r,data);assert (digest(old_stdin),digest(new_stdin))==STDIN_PINS
  bound={str(a.root_snapshot.resolve()):a.root_snapshot_sha256,str(a.protected_profile.resolve()):PROTECTED_PROFILE_SHA};producers={};assets={};data_pins={};links={}
  for rel,row in files.items():
   if rel.startswith(('scripts/','tests/','authoring-inputs/projectile')) or rel=='Makefile':producers[str(r/rel)]=row['sha256']
   if rel.startswith(('assets/hd/current-compat/','assets/hd/global-assets-v1/content/','assets/hd/shared-menu-runs-v1/','authoring-inputs/projectile')):assets[str(r/rel)]=row['sha256']
  data_inventory=inventory(data);assert len(data_inventory)==99,'Expected complete recovered99 original game-data files'
  finalizers.append(('original_data99_unchanged',lambda:inventory(data)==data_inventory))
  for rel,row in data_inventory.items():data_pins[str(data/rel)]=row['sha256']
  for name,pin in blue.DATA_SHA.items():assert data_pins[str(data/name)]==pin
  hdas={}
  for i in native.IDS:
   directory='projectile-statics' if i in native.STATICS else 'projectile-gold-pulse' if i in native.GOLD else 'projectile-blue-triplet' if i in blue.BLUE else 'projectile'+str(i)
   p=r/'assets/hd/current-compat'/directory/native.HDA_NAMES[i];pin=HDA_STATICS[i] if i in native.STATICS else HDA_GOLD[i] if i in native.GOLD else blue.HDA_SHA[i]
   payload=p.read_bytes();assert digest(payload)==pin and len(payload)==43036;hdas[i]=payload;assets[str(p)]=pin
  assert native.registered_hdas(r)=={i:hdas[i] for i in native.STATICS}
  content=r/'assets/hd/global-assets-v1/content';assert content.is_dir()
  fixtures=native.fixture_payloads(r,hdas,registration);old_fixtures=gold.fixture_payloads(r,{i:hdas[i] for i in gold.IDS},gold.registration(r))
  assert len(old_fixtures)==335 and len(fixtures)==725 and all(fixtures[k]==v for k,v in old_fixtures.items())
  assert sum(name.startswith('statics-packs/') for name in fixtures)==390
  leaves=['legacy264/'+name for name,_,_ in blue.PACKS]+['blue-packs/'+name for name in blue.PACK_NAMES]+['gold-packs/'+name for name in gold.PACK_NAMES]+['statics-packs/'+name for name in native.PACK_NAMES]
  assert len(leaves)==len(set(leaves))==102 and len(native.PACK_NAMES)==42
  for rel,b in fixtures.items():assert type(b) is bytes and not Path(rel).is_absolute() and '..' not in Path(rel).parts and Path(rel).parent.as_posix() in leaves
  headers=[r/'assets/hd/shared-menu-runs-v1'/n for n in ('reconstructed_run_specs.h','reconstructed_numeric_specs.h','reconstructed_name_source_specs.h')];assert all(str(p) in assets for p in headers)
  env=environment(sysroot,out/'tmp',out/'home');cc=resolve_traced(Path(shutil.which('cc',path=env['PATH'])),links);pkg=resolve_traced(Path(shutil.which('pkg-config',path=env['PATH'])),links);make=resolve_traced(Path(shutil.which('make',path=env['PATH'])),links)
  builtin=Path(subprocess.check_output([cc,'-print-file-name=include'],env=env).decode().strip());assert builtin.is_dir()
  system={};tools={}
  for base in (sysroot/'usr/include',Path('/usr/include'),builtin):
   for p in base.rglob('*'):
    if p.is_file():actual=resolve_traced(p.absolute(),links);pin=SHA(actual);assert system.setdefault(str(actual),pin)==pin
  tool_paths={cc,pkg,make,resolve_traced(Path(sys.executable).absolute(),links),resolve_traced(Path(shutil.which('git',path=env['PATH'])),links)}
  for name in ('sh','uname','touch','mkdir'):
   tool_paths.add(resolve_traced(Path(shutil.which(name,path=env['PATH'])),links))
  for name in ('as','ld','cc1','collect2'):
   token=subprocess.check_output([cc,'-print-prog-name='+name],env=env).decode().strip();p=Path(token) if token.startswith('/') else Path(shutil.which(token,path=env['PATH']));tool_paths.add(resolve_traced(p,links))
  for base,patterns in ((sysroot/'usr/lib/x86_64-linux-gnu',('libSDL2-2.0.so.*','libSDL2_net-2.0.so.*')),(Path('/usr/lib/x86_64-linux-gnu'),('libc.so.6','libm.so.6','libasan.so.8*','libubsan.so.1*','libgcc_s.so.1','libstdc++.so.6*','ld-linux-x86-64.so.2'))):
   for pattern in patterns:
    found=list(base.glob(pattern));assert found,(base,pattern);tool_paths.update(resolve_traced(p,links) for p in found)
  for module in tuple(sys.modules.values()):
   path=getattr(module,'__file__',None)
   if path and Path(path).is_absolute() and Path(path).is_file():tool_paths.add(resolve_traced(Path(path),links))
  for p in tool_paths:tools[str(p)]=SHA(p)
  runtime_pins=loaded_runtime_inputs(links);tools.update(runtime_pins)
  compiler_link_pins,compiler_link_records=compiler_link_inputs(cc,env,links);tools.update(compiler_link_pins)
  sdl_pins,sdl_records=sdl_link_inputs(pkg,sysroot,env,links);tools.update(sdl_pins)
  cflags=shlex.split(subprocess.check_output([pkg,'--cflags','sdl2','SDL2_net'],env=env).decode());libs=sdl_records['argv'];cflags=['-I'+str(sysroot/'usr/include/x86_64-linux-gnu'),*cflags]
  assert all(flag.startswith('-I') or flag=='-D_REENTRANT' for flag in cflags),'Unexpected SDL compiler flags'
  bound.update(producers);bound.update(assets);bound.update(data_pins);bound.update(system);bound.update(tools)
  finalizers.extend([('all_actual_inputs_unchanged',lambda:all(SHA(p)==v for p,v in bound.items())),('dependency_link_texts_unchanged',lambda:all(Path(p).is_symlink() and os.readlink(p)==v for p,v in links.items())),('loaded_interpreter_runtime_unchanged',lambda:loaded_runtime_inputs({})==runtime_pins),('compiler_link_selection_unchanged',lambda:compiler_link_inputs(cc,env,{})==(compiler_link_pins,compiler_link_records) and sdl_link_inputs(pkg,sysroot,env,{})==(sdl_pins,sdl_records))])
  assert identity(r)[0]==before and hydrated_manifest(r)==files and protected_manifest(protected,profile)==public_files
  assert all(SHA(p)==v for p,v in bound.items()) and all(Path(p).is_symlink() and os.readlink(p)==v for p,v in links.items())
  report.update(root_identity_before=before,root_file_count=len(files),source_sha256=source,protected_qualifiedgold_identity_before=pi,protected_qualifiedgold_profile_sha256=PROTECTED_PROFILE_SHA,producer_sha256=producers,asset_sha256=assets,original_data_sha256=data_pins,original_data_inventory99=data_inventory,current_system_header_sha256=system,toolchain_sha256=tools,compiler_link_inputs=compiler_link_records,sdl_link_inputs=sdl_records,all_bound_inputs_sha256=bound,actual_dependency_symlinks=links,old107_stdin_sha256=digest(old_stdin),old61_stdin_sha256=digest(new_stdin),fixture_old335_sha256={k:digest(v) for k,v in old_fixtures.items()},python_version=sys.version,pillow_version=__import__('PIL').__version__)
  ready=True;report['preflight_complete']=True;report['status']='RUNNING';save()
  for name,b in [('root-index-before.bin',raw),('root-index-semantic-before.bin',sem),('protected-index-before.bin',pr),('protected-index-semantic-before.bin',ps)]:write(out/name,b)
  write(out/'root-files-before.json',(json.dumps(files,indent=2)+'\n').encode());report['root_manifest_sha256']=SHA(out/'root-files-before.json')
  generated={**bundle,'gold-wrapper.c':gold_wrapper,'projectile_gold_pulse_native_additions.c.inc':gold_c,'statics-wrapper.c':wrapper,'projectile_statics_native_additions.c.inc':statics_c};assert len(generated)==10
  for name,b in generated.items():write(out/name,b);report['generated_input_sha256'][str(out/name)]=digest(b)
  for mode in MODES:
   build=out/(mode+'-build');assert not build.exists();measure(4096);build.mkdir();report['builds_started'].append(mode)
   for rel,pin in source.items():write(build/'src'/rel,(r/'src'/rel).read_bytes());assert SHA(build/'src'/rel)==pin
   write(build/'Makefile',(r/'Makefile').read_bytes())
   for p in headers:write(build/p.relative_to(r),p.read_bytes())
   assert not (build/'obj').exists() and not (build/'opentyrian2000').exists()
   argv=make_command(mode,sysroot,cc,pkg);argv[0]=str(make);output=run(argv,mode+'-build',build,empty_stderr=mode=='hd-on-asan-ubsan')
   objects={p.name:SHA(p) for p in (build/'obj').glob('*.o')};assert set(objects)=={u+'.o' for u in units}
   assert {p.relative_to(build/'src').as_posix():SHA(p) for p in (build/'src').rglob('*') if p.is_file()}==source
   commands,link=compile_contract(output.decode('utf-8'),units,mode);assert [arg for arg in link if arg.startswith('-l')]==['-lm','-lSDL2_net','-lSDL2']
   assert [arg for arg in link if arg.startswith('-L')]==[libs[0]]
   deps=list((build/'obj').glob('*.d'));assert len(deps)==86 and {p.stem for p in deps}==set(units)
   for p in deps:bind_dep(p,build)
   for p in (build/'obj').glob('*.o'):report['new_artifacts_sha256'][str(p)]=SHA(p)
   binary=build/'opentyrian2000';report['new_artifacts_sha256'][str(binary)]=SHA(binary)
   report['modes'][mode]={'objects_sha256':objects,'binary_sha256':SHA(binary),'source_sha256':source.copy(),'compile_commands':commands,'link_command':link,'fresh_object_count':86,'sanitized':mode=='hd-on-asan-ubsan'};measure();save()
  build=out/'hd-on-asan-ubsan-build';compile_main,link,objects=native_compile_commands(cc,build,out,cflags,libs)
  assert [arg for arg in link if arg.startswith('-l')]==['-lSDL2_net','-lSDL2','-lm']
  assert all(SHA(p)==report['new_artifacts_sha256'][str(p)] for p in objects[1:])
  run(compile_main,'renamed-main',out,empty_stderr=True);bind_dep(out/'renamed-main.d',out);report['new_artifacts_sha256'][str(build/'opentyr-test.o')]=SHA(build/'opentyr-test.o')
  run(link,'full-sanitized-harness',out,empty_stderr=True);bind_dep(out/'renderer-harness.d',out);exe=out/'enemy-statics-fresh-test';report['native_binary_sha256']=SHA(exe);report['new_artifacts_sha256'][str(exe)]=SHA(exe)
  report['native_linked_objects_sha256']={str(p):SHA(p) for p in objects};assert len(objects)==85 and all(p.is_relative_to(build) for p in objects)
  assert len(report['fresh_dependency_file_sha256'])==346
  actual={resolve_traced(Path(t) if Path(t).is_absolute() else out/t,links) for t in dependency_tokens((out/'renderer-harness.d').read_bytes().decode())}
  required={build/'src'/n for n in ('render_mirror.c','global_projectile91_mirror.inc','enemy_blue_triplet_mirror.inc','current_projectile_blue_triplet_payload_pins.h','enemy_gold_pulse_mirror.inc','current_projectile_gold_pulse_payload_pins.h','enemy_statics_mirror.inc','current_projectile_statics_payload_pins.h')}
  required.update(out/n for n in generated if n not in ('harness.c','gold-wrapper.c'))
  assert required<=actual,('Required actual native includes missing',sorted(map(str,required-actual)))
  for leaf in leaves:
   dest=out/leaf;measure(12288);dest.mkdir(parents=True);(dest/'content').symlink_to(content,target_is_directory=True);report['fixture_links'][str(dest/'content')]=str(content);measure()
  for rel,b in fixtures.items():write(out/rel,b);report['fixture_sha256'][str(out/rel)]=digest(b)
  assert len(report['fixture_sha256'])==725 and len(report['fixture_links'])==102
  legacy=[out/'legacy264'/name for name,_,_ in blue.PACKS];outputs={}
  for label,key,argv,payload in [('inherited107','inherited107_stdout',[exe,'--inherited107',*legacy[:5]],old_stdin),('inherited61','inherited61_stdout',[exe,'--projectile61',*legacy],new_stdin),('new-blue-triplet','new_blue_stdout',[exe,'--blue-triplet',out/'blue-packs'],new_stdin),('gold251','gold251_stdout',[exe,'--gold-pulse',out/'gold-packs'],new_stdin)]:
   assert SHA(exe)==report['native_binary_sha256'];outputs[key]=run(argv,label,out,payload,True)
   pin,size=STDOUT_PINS[key];assert digest(outputs[key])==pin and len(outputs[key])==size
  validate_stdout_bytes(outputs);legacy_counts=native.verify_legacy_stdout(outputs);assert legacy_counts['cases']==880 and legacy_counts['assertions']==50255790
  assert SHA(exe)==report['native_binary_sha256'];statics=run([exe,'--enemy-statics',out/'statics-packs'],'statics449',out,new_stdin,True)
  counts=native.parse_statics_stdout(statics);assert counts['cases']==449 and counts['assertions']==91342858
  report.update(status=SUCCESS,**{k:v.decode('ascii') for k,v in outputs.items()},statics449_stdout=statics.decode('ascii'),old880=legacy_counts,statics449=counts,total_cases=1329,total_assertions=141598648);measure(final=True)
 except BaseException as exc:failure=exc;report.update(status='FAIL_RETAINED',error=repr(exc))
 finally:
  report['status_before_final_checks']=report['status'];checks={};errors={}
  if created:
   try:save()
   except BaseException as exc:errors['save_original_result']=repr(exc)
   for name,fn in finalizers:guarded_check(checks,errors,name,fn)
   guarded_check(checks,errors,'all_new_artifacts_unchanged',lambda:all(SHA(p)==v for p,v in report['new_artifacts_sha256'].items()))
   guarded_check(checks,errors,'all_new_dependencies_unchanged',lambda:all(SHA(p)==v for p,v in report['fresh_dependency_sha256'].items()))
   guarded_check(checks,errors,'all_native_linked_objects_unchanged',lambda:all(SHA(p)==v for p,v in report['native_linked_objects_sha256'].items()))
   guarded_check(checks,errors,'fixture_links_unchanged',lambda:all(Path(p).is_symlink() and os.readlink(p)==v for p,v in report['fixture_links'].items()))
   guarded_check(checks,errors,'no_game_captures',lambda:not list(out.rglob('*.bmp')) and not list(out.rglob('*.png')))
   if ready:
    guarded_check(checks,errors,'original_eight_and_double_inverse',lambda:all(SHA(out/k)==v for k,v in SOURCE_PINS.items()) and SHA(out/'gold-wrapper.c')==GOLD_WRAPPER_SHA and SHA(out/'projectile_gold_pulse_native_additions.c.inc')==GOLD_COMPANION_SHA and native.reverse_shim((out/'statics-wrapper.c').read_bytes())==(out/'gold-wrapper.c').read_bytes() and gold.reverse_shim((out/'gold-wrapper.c').read_bytes())==bundle['harness.c'])
   report.update(checks=checks,final_check_errors=errors,seconds=time.monotonic()-started)
   if errors or not all(checks.values()):report['status']='FAIL_FINAL_BINDING_OR_BUDGET_RETAINED'
   if any(row.get('cleanup_incomplete') for row in report['commands']):report['status']='UNKNOWN_PROCESS_CLEANUP_RETAINED'
   try:measure(262144,final=True);report['final_allocated_before_receipt']=allocated(out);report['free_before_receipt']=shutil.disk_usage(out.parent).free;save();measure(final=True)
   except BaseException as exc:
    errors['postwrite_budget_or_save']=repr(exc)
    if report['status']!='UNKNOWN_PROCESS_CLEANUP_RETAINED':report['status']='FAIL_RECEIPT_OR_FINAL_BUDGET_RETAINED'
    try:save()
    except BaseException as more:errors['final_save']=repr(more)
   actual=last_actual_budget(out,report,errors,save)
  else:actual={'last_budget_ok':False,'stage_created':False}
  print(json.dumps({'status':report['status'],'total_cases':report.get('total_cases'),'total_assertions':report.get('total_assertions'),'peak_allocated':report['peak_allocated'],**actual,'error':report.get('error'),'final_errors':errors}))
 if failure is not None:raise failure
 assert report['status']==SUCCESS and actual['last_budget_ok'],report['status']
if __name__=='__main__':main()
