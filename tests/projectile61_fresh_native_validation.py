#!/usr/bin/env python3
"""Four complete fresh61 builds and byte-exact accepted107+157 native oracles.

Every mode compiles all86 project TUs from current310-source snapshots. The
native executable consumes84 fresh ASan/UBSan objects, a fresh renamed main,
and the fresh combined production renderer/harness. External SDL/system
libraries remain native and LSan is disabled. No game loop or full gate claim.
Historical145 FAIL_BINDING_RETAINED stays a separate accepted stat-only record.
"""
from pathlib import Path
import argparse,ast,hashlib,json,os,re,resource,shlex,shutil,signal,stat,struct,subprocess,threading,time

SHA=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
PEAK=256*1024**2
RESERVE=250*1024**2
START_REQUIRED=PEAK+RESERVE
MODES={'default-off':'','hd-on':'-DNEWSHF_HD_COMPOSITOR=1','mirror-disabled':'-DNEWSHF_HD_COMPOSITOR=1 -DRENDER_MIRROR_DISABLED','hd-on-asan-ubsan':'-DNEWSHF_HD_COMPOSITOR=1'}
SAN=('-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie')
DEFAULT_CFLAGS='-pedantic -Wall -Wextra -Wno-format-truncation -Wno-missing-field-initializers -O2'
FRESH145_SHA='86975d21f38d876c6b7f5c610c67ef051898aefb9c6d998cf6394c89318d691a'
DISPOSITION_SHA='bd037a3f7992c1d3aec69a1ecc8844f0eb4967eb32425b60739a579c51761847'
PRIOR61_SHA='3fc0b94f0d3fbea059ecda7ec565ef573ac6d7ad88ec481c2b1ac4e1b80d94aa'
PRIOR61_DRIVER_SHA='68737e976c12cfa66eaf86c536cccd2ed2dc2a39e7a81740ecbd731d48699dc8'
COMPANION_SHA='5f80d681e84a6dff20873f7f05bb3a02e3fd0f22013edf2b5fbf133d36c51cfe'
LEGACY_SHA='8925fb11215446339f067124fa7223ec48dc7c86459e303d3803477773b2d9ac'
OLD91_HARNESS_SHA='4edcb186f10a47b8d331b6ecaefe15f12c620d7967145f5f9cdbf93c0e76ce89'
WRAPPER_SHA='59bfbe4d8e3bb8db4403eaabb199d8ff2f09b2eb2047769f39069c93dff7f4eb'
OLD_STDIN_SHA='7dedf7066696fc278f5fbb8dfb1462e7b6ac290cb5d08ae5260a6cdabc1ecca7'
NEW_STDIN_SHA='a9739298f031cafbfefb3befd359750872f6caafe69ebf5c7cf948544713830b'
DATA_SHA={'tyrian.shp':'80cae98e073be6d7f710495920b71497bb23f108ea6631d6faf352c4729474f0','tyrianc.shp':'e980f02021395d39b86491acdc2ecd6dd47ea2a9f859fe3928f81b75e244fd7d','palette.dat':'f628396306805387f07f72c4ccf0fdee9ca84b8e70ae23ba4ec58ec5fb362da0'}
PACKS=(('valid',(),None),('missing91',(91,),None),('missing145',(145,),None),('bad145',(),145),('bad91',(),91),('missing61',(61,),None),('bad61',(),61),('only61',(91,145),None))
SUCCESS='PASS_FOUR_FRESH_CONFIGS_AND_FULL_PROJECT_SANITIZED264'


def inv(root):return {p.relative_to(root).as_posix():SHA(p) for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}
def allocated(root):
    total=0
    for p in root.rglob('*'):
        try:total+=p.lstat().st_blocks*512
        except FileNotFoundError:pass  # compiler temporary disappeared between directory read/stat
    return total
def budget_ok(used,free):return used<=PEAK and free>=RESERVE
def guarded_check(checks,errors,name,check):
    try:checks[name]=bool(check())
    except Exception as error:checks[name]=False;errors[name]=repr(error)
    return checks[name]
def dependency_tokens(text):
    text=text.replace('\\\n',' ')
    if ':' not in text:raise ValueError('Dependency rule has no colon')
    return shlex.split(text.split(':',1)[1])
def git(root,*args):return subprocess.check_output(['git','--no-optional-locks','-C',str(root),*args],env={**os.environ,'GIT_OPTIONAL_LOCKS':'0'})
def identity(root):
    index=Path(git(root,'rev-parse','--path-format=absolute','--git-path','index').decode().strip())
    raw=index.read_bytes();semantic=git(root,'ls-files','--stage','-z')
    assert index.read_bytes()==raw,'Read-only index query changed raw bytes'
    return dict(head=git(root,'rev-parse','HEAD').decode().strip(),index_path=str(index),raw_sha256=hashlib.sha256(raw).hexdigest(),semantic_sha256=hashlib.sha256(semantic).hexdigest()),raw,semantic

def hydrated_manifest(root):
    tagged=git(root,'ls-files','-t','-z')
    assert not any(row.startswith(b'S ') for row in tagged.split(b'\0')),'Must use completely hydrated source; no skip-worktree entries'
    staged=git(root,'ls-files','--stage','-z')
    for row in staged.split(b'\0'):
        if row:assert row.split(b'\t',1)[0].split()[2]==b'0','No unmerged index stages'
    names=git(root,'ls-files','--cached','--others','--exclude-standard','-z').decode().split('\0')
    manifest={}
    for name in sorted(set(names)-{''}):
        path=Path(name);assert not path.is_absolute() and '..' not in path.parts
        p=root/path;s=p.lstat()
        assert stat.S_ISREG(s.st_mode) and s.st_nlink==1,'Missing/symlink/hardlinked repository input: '+name
        manifest[name]={'sha256':SHA(p),'bytes':s.st_size,'mode':stat.S_IMODE(s.st_mode),'nlink':s.st_nlink}
    assert manifest
    return manifest

def literal_assignment(path,name):
    tree=ast.parse(path.read_text())
    nodes=[node for node in tree.body if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in node.targets)]
    assert len(nodes)==1
    return ast.literal_eval(nodes[0].value)

def legacy_harness(root):
    old=literal_assignment(root/'tests/test_projectile91_global_runtime.py','HARNESS')
    assert hashlib.sha256(old.encode()).hexdigest()==OLD91_HARNESS_SHA
    marker='int main(int argc,char **argv)\n{';assert old.count(marker)==1
    result=old.split(marker)[0].encode()+(root/'tests/projectile145_native_additions.c.inc').read_bytes()
    assert hashlib.sha256(result).hexdigest()==LEGACY_SHA
    return result

def accepted_wrapper(path):
    assert SHA(path)==PRIOR61_DRIVER_SHA
    raw=literal_assignment(path,'WRAPPER').encode()
    assert hashlib.sha256(raw).hexdigest()==WRAPPER_SHA
    return raw

def verify_stdout(old,new,prior):
    assert old==prior['inherited107_stdout'] and new==prior['new61_stdout'],'Accepted native stdout changed'
    a=re.findall(r'^PASS inherited91 native lifecycle: (\d+) cases (\d+) assertions$',old,re.M)
    b=re.findall(r'^PASS shared145 native lifecycle: (\d+) new cases (\d+) new assertions; internal8 only; not gameplay/full build$',old,re.M)
    c=re.findall(r'^PASS shared61 native lifecycle: (\d+) cases (\d+) assertions; internal8 only; not gameplay/full build$',new,re.M)
    assert a==[('37','81611')] and b==[('70','141992')] and c==[('157','822291')]
    assert re.findall(r'^61_TO_TALON copied=(\d+) cached=([01])$',new,re.M)==[('267','0'),('267','1')]
    return {'inherited_cases':107,'inherited_assertions':223603,'new_cases':157,'new_assertions':822291,'total_cases':264,'total_assertions':1045894}

def sanitized_env(parent,sysroot,tmp):
    env=dict(parent)
    for key in tuple(env):
        if key.startswith(('AIRCRAFT','SHARED','PROJECTILE','TYRIAN_GAME_PROBE','TYRIAN_CYAN_BORROW','OT_')) or key in ('MAKEFLAGS','MFLAGS','MAKEOVERRIDES','CC','CFLAGS','CPPFLAGS','LDFLAGS','LDLIBS','CPATH','C_INCLUDE_PATH','CPLUS_INCLUDE_PATH','COMPILER_PATH','GCC_EXEC_PREFIX','LIBRARY_PATH','LD_PRELOAD','LD_AUDIT','PKG_CONFIG_PATH','PKG_CONFIG'):
            env.pop(key)
    env.update(PKG_CONFIG_SYSROOT_DIR=str(sysroot),PKG_CONFIG_LIBDIR=str(sysroot/'usr/lib/x86_64-linux-gnu/pkgconfig'),LD_LIBRARY_PATH=str(sysroot/'usr/lib/x86_64-linux-gnu'),SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',SDL_RENDER_DRIVER='software',ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1',TMPDIR=str(tmp))
    return env

def make_command(mode,sysroot,cc,pkg_config):
    assert mode in MODES
    cpp='-MD -DNDEBUG '+MODES[mode]+' -I'+str(sysroot/'usr/include/x86_64-linux-gnu')
    ld='-Wl,-rpath,'+str(sysroot/'usr/lib/x86_64-linux-gnu')
    flags=DEFAULT_CFLAGS
    if mode=='hd-on-asan-ubsan':ld+=' -fsanitize=address,undefined -no-pie';flags='-O1 -g '+' '.join(SAN)
    return ['make','-j2','CC='+str(cc),'PKG_CONFIG='+str(pkg_config),'VCS_IDREV=printf projectile61-fresh-native','CPPFLAGS='+cpp,'CFLAGS='+flags,'LDFLAGS='+ld]

def compile_contract(log,units,mode):
    lines=[line for line in log.splitlines() if ' -c -o obj/' in line]
    assert len(lines)==86
    observed=[]
    for line in lines:
        argv=shlex.split(line);out=argv[argv.index('-o')+1];unit=Path(out).stem
        assert out=='obj/'+unit+'.o' and argv[-1]=='src/'+unit+'.c'
        assert '-MD' in argv and '-DNDEBUG' in argv
        assert ('-DNEWSHF_HD_COMPOSITOR=1' in argv)==(mode!='default-off')
        assert ('-DRENDER_MIRROR_DISABLED' in argv)==(mode=='mirror-disabled')
        if mode=='hd-on-asan-ubsan':assert all(flag in argv for flag in SAN)
        else:assert not any(flag.startswith('-fsanitize=') for flag in argv)
        observed.append(unit)
    assert len(set(observed))==86 and set(observed)==set(units)
    return lines

def native_inputs(data):
    assert all(SHA(data/name)==pin for name,pin in DATA_SHA.items())
    raw=(data/'tyrian.shp').read_bytes();assert struct.unpack_from('<H',raw)[0]==13
    offsets=struct.unpack_from('<13I',raw,2);bank=raw[offsets[7]:offsets[8]];talon=raw[offsets[8]:offsets[9]]
    assert len(bank)==32060 and hashlib.sha256(bank).hexdigest()=='9bba1e94d38df61f152412c226bfd6df235e42027c9143c5961d4a5add853a68'
    pal=(data/'palette.dat').read_bytes()[:768];assert len(pal)==768 and max(pal)<64
    rgb=bytes((v<<2)|(v>>4) for v in pal)
    old=bank+b''.join(struct.pack('<I',int.from_bytes(rgb[i:i+3],'big')) for i in range(0,768,3))+struct.pack('<I',len(talon))+talon
    raw=(data/'tyrianc.shp').read_bytes();assert struct.unpack_from('<H',raw)[0]==13
    offsets=struct.unpack_from('<13I',raw,2);xmas=raw[offsets[7]:offsets[8]]
    assert len(xmas)==32404 and hashlib.sha256(xmas).hexdigest()=='26eb4fe91672bcef4bc88d7162d5f531144ad98eba64f5c0314e35fec85241e4'
    new=old+struct.pack('<I',len(xmas))+xmas
    assert hashlib.sha256(old).hexdigest()==OLD_STDIN_SHA and hashlib.sha256(new).hexdigest()==NEW_STDIN_SHA
    return old,new

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ('root','prior-native','legacy-fresh','legacy-disposition','data','sysroot','out'):
        parser.add_argument('--'+key,type=Path,required=True)
    a=parser.parse_args();a=argparse.Namespace(**{k:v.resolve() for k,v in vars(a).items()});r=a.root;q=a.out
    assert not q.exists() and not q.is_relative_to(r) and shutil.disk_usage(q.parent).free>=START_REQUIRED
    root_identity,raw_index,semantic_index=identity(r);root_files=hydrated_manifest(r)
    assert identity(r)[0]==root_identity
    source=inv(r/'src');scripts=inv(r/'scripts');units=sorted(p.stem for p in (r/'src').glob('*.c'))
    assert len(source)==310 and len(units)==86
    assert SHA(a.prior_native/'receipt.json')==PRIOR61_SHA and SHA(a.legacy_fresh/'receipt.json')==FRESH145_SHA and SHA(a.legacy_disposition)==DISPOSITION_SHA
    prior=json.loads((a.prior_native/'receipt.json').read_text());legacy=json.loads((a.legacy_fresh/'receipt.json').read_text());disposition=json.loads(a.legacy_disposition.read_text())
    assert prior['status']=='PASS_107_AND_REAL61_PRODUCTION_TU_PROBE' and prior['source_sha256']==source and all(prior['checks'].values())
    assert legacy['status']=='FAIL_BINDING_RETAINED' and legacy['status_before_final_checks']=='PASS_FOUR_FRESH_CONFIGS_AND_FULL_PROJECT_SANITIZED107'
    assert disposition['status']=='ACCEPTED_FUNCTIONAL_RESULTS_WITH_RAW_INDEX_STAT_CACHE_DEVIATION' and disposition['original_receipt_sha256']==FRESH145_SHA
    assert prior['inherited107_stdout']==legacy['native_stdout'] and legacy['generated_harness_sha256']==LEGACY_SHA
    assert (a.prior_native/'inherited107.stdout').read_text()==prior['inherited107_stdout'] and (a.prior_native/'native61.stdout').read_text()==prior['new61_stdout']
    verify_stdout(prior['inherited107_stdout'],prior['new61_stdout'],prior)
    inherited=legacy_harness(r);assert (a.legacy_fresh/'harness.c').read_bytes()==inherited
    companion=r/'tests/projectile61_native_additions.c.inc';assert SHA(companion)==COMPANION_SHA
    wrapper=accepted_wrapper(r/'tests/projectile61_native_validation.py')
    assert prior['generated_wrapper_sha256']==WRAPPER_SHA and prior['old107_stdin_sha256']==OLD_STDIN_SHA and prior['new61_stdin_sha256']==NEW_STDIN_SHA
    driver=Path(__file__).resolve();assert SHA(r/'tests'/driver.name)==SHA(driver),'Import the frozen QA driver before this new evidence epoch'
    producer_paths=(driver,r/'tests'/driver.name,r/'tests/test_projectile61_fresh_native_adapter.py',r/'tests/projectile61_native_validation.py',companion,r/'tests/projectile145_native_additions.c.inc',r/'tests/test_projectile91_global_runtime.py',r/'Makefile',a.prior_native/'receipt.json',a.prior_native/'inherited107.stdout',a.prior_native/'native61.stdout',a.legacy_fresh/'receipt.json',a.legacy_fresh/'harness.c',a.legacy_disposition)
    producers={str(p):SHA(p) for p in producer_paths}
    assets={}
    for selector in (91,145,61):
        for base in (r/f'authoring-inputs/projectile{selector}-current',r/f'assets/hd/current-compat/projectile{selector}'):
            for p in base.rglob('*'):
                if p.is_file():assets[str(p)]=SHA(p)
        for p in (r/f'assets/hd/authoring/projectile{selector}-current.json',r/f'packaging/current-projectile{selector}-compatibility.json'):
            assets[str(p)]=SHA(p)
    content=r/'assets/hd/global-assets-v1/content'
    for p in content.rglob('*'):
        if p.is_file():assets[str(p.resolve())]=SHA(p)
    hdas={i:r/f'assets/hd/current-compat/projectile{i}/enemy-projectile{i}-{i}-8.hda' for i in (91,145,61)}
    headers=[r/'assets/hd/shared-menu-runs-v1'/name for name in ('reconstructed_run_specs.h','reconstructed_numeric_specs.h','reconstructed_name_source_specs.h')]
    for p in headers:assets[str(p)]=SHA(p)
    data={str(a.data/name):SHA(a.data/name) for name in DATA_SHA};assert all(data[str(a.data/n)]==h for n,h in DATA_SHA.items())
    env=sanitized_env(os.environ,a.sysroot,q/'tmp')
    cc=Path(shutil.which('cc',path=env.get('PATH'))).resolve();pkg=Path(shutil.which('pkg-config',path=env.get('PATH'))).resolve();make=Path(shutil.which('make',path=env.get('PATH'))).resolve()
    builtin=Path(subprocess.check_output([cc,'-print-file-name=include'],env=env,text=True).strip()).resolve()
    # -MD records both project and system headers. Snapshot their allowed roots
    # before compiling; every actual dependency must match one pinned input.
    header_roots=(a.sysroot/'usr/include',Path('/usr/include'),builtin)
    system_headers={}
    for base in header_roots:
        for p in base.rglob('*'):
            if p.is_file():system_headers[str(p.resolve())]=SHA(p)
    toolchain={str(p):SHA(p) for p in (cc,pkg,make)}
    assert identity(r)[0]==root_identity and hydrated_manifest(r)==root_files
    q.mkdir();(q/'tmp').mkdir()
    (q/'root-index-before.bin').write_bytes(raw_index);(q/'root-index-semantic-before.bin').write_bytes(semantic_index)
    (q/'root-files-before.json').write_text(json.dumps(root_files,indent=2)+'\n')
    (q/'inherited145_harness.c').write_bytes(inherited);(q/'projectile61_native_additions.c.inc').write_bytes(companion.read_bytes());(q/'harness.c').write_bytes(wrapper)
    generated={str(q/'inherited145_harness.c'):LEGACY_SHA,str(q/'projectile61_native_additions.c.inc'):COMPANION_SHA,str(q/'harness.c'):WRAPPER_SHA}
    report=dict(status='RUNNING',scope=__doc__,source_sha256=source,scripts_sha256=scripts,producer_sha256=producers,asset_sha256=assets,original_data_sha256=data,current_system_header_sha256=system_headers,toolchain_sha256=toolchain,root_identity=root_identity,root_file_count=len(root_files),root_files_manifest_sha256=SHA(q/'root-files-before.json'),raw_index_snapshot_sha256=SHA(q/'root-index-before.bin'),semantic_index_snapshot_sha256=SHA(q/'root-index-semantic-before.bin'),original145_status_retained='FAIL_BINDING_RETAINED; accepted only by separate exact stat-only disposition',prior61_receipt_sha256=PRIOR61_SHA,generated_input_sha256=generated,commands=[],modes={},builds_started=[],fresh_dependency_file_sha256={},fresh_dependency_sha256={},peak_budget_bytes=PEAK,reserve_bytes=RESERVE,start_required_bytes=START_REQUIRED,peak_allocated_sample=allocated(q),minimum_free_sample=shutil.disk_usage(q).free,free_before=shutil.disk_usage(q).free,sample_interval_seconds=.25,all_builds_fresh=True,reused_project_objects=0,original_stdin_persisted=False,sanitizer_scope='All86 project production TUs instrumented in hd-on-asan-ubsan; native test uses84 freshly built objects plus fresh renamed main and fresh renderer/harness. External SDL/system libraries native; leak sanitizer disabled.',system_header_scope='Current precompile sysroot/usr/include, host/usr/include and compiler builtin headers; every actual -MD dependency pinned before compilation and checked after.')
    def save():(q/'receipt.json').write_text(json.dumps(report,indent=2)+'\n')
    def measure():
        used=allocated(q);free=shutil.disk_usage(q).free
        report['peak_allocated_sample']=max(used,report['peak_allocated_sample']);report['minimum_free_sample']=min(free,report['minimum_free_sample'])
        assert budget_ok(used,free),('budget',used,free)
    def no_core():resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    def run(cmd,label,cwd,payload=None,empty_stderr=False):
        row=dict(argv=list(map(str,cmd)),label=label,cwd=str(cwd));report['commands'].append(row);save();measure()
        with (q/(label+'.stdout')).open('wb') as out,(q/(label+'.stderr')).open('wb') as err:
            proc=subprocess.Popen(row['argv'],cwd=cwd,env=env,stdin=subprocess.PIPE if payload is not None else subprocess.DEVNULL,stdout=out,stderr=err,start_new_session=True,preexec_fn=no_core)
            row['pid']=proc.pid;save();start=time.monotonic();writer_errors=[]
            def feed():
                try:proc.stdin.write(payload);proc.stdin.close()
                except BaseException as error:writer_errors.append(repr(error))
            feeder=threading.Thread(target=feed,daemon=True) if payload is not None else None
            try:
                if feeder:feeder.start()
                while proc.poll() is None:measure();assert time.monotonic()-start<900,'timeout';time.sleep(.25)
            except BaseException:
                if proc.poll() is None:
                    os.killpg(proc.pid,signal.SIGTERM)
                    try:proc.wait(timeout=10)
                    except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
                row['stopped']=True;raise
            finally:
                if feeder:feeder.join(timeout=2)
                row.update(returncode=proc.poll(),seconds=time.monotonic()-start,stdin_writer_errors=writer_errors);save()
            assert not writer_errors and (feeder is None or not feeder.is_alive()),'stdin transfer'
            assert row['returncode']==0,(label,row['returncode'])
        row['stdout_sha256']=SHA(q/(label+'.stdout'));row['stderr_sha256']=SHA(q/(label+'.stderr'))
        if empty_stderr:assert not (q/(label+'.stderr')).read_bytes(),label+' stderr'
        measure();save()
    def bind_dep(dep,cwd):
        report['fresh_dependency_file_sha256'][str(dep)]=SHA(dep)
        for token in dependency_tokens(dep.read_text()):
            p=(cwd/token).resolve() if not Path(token).is_absolute() else Path(token).resolve();h=SHA(p)
            expected=generated.get(str(p),system_headers.get(str(p)))
            for mode in MODES:
                build=q/(mode+'-build')
                if p.is_relative_to(build/'src'):expected=source.get(p.relative_to(build/'src').as_posix());break
                if p.is_relative_to(build/'assets'):expected=assets.get(str(r/p.relative_to(build)));break
            assert expected==h,('Unbound or changed actual dependency',str(p),expected,h)
            report['fresh_dependency_sha256'][str(p)]=h
    start=time.monotonic();save()
    try:
        measure()
        for mode in MODES:
            build=q/(mode+'-build');assert not build.exists();build.mkdir();report['builds_started'].append(mode)
            shutil.copytree(r/'src',build/'src');shutil.copyfile(r/'Makefile',build/'Makefile')
            for p in headers:target=build/p.relative_to(r);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
            assert not (build/'obj').exists() and not (build/'opentyrian2000').exists()
            command=make_command(mode,a.sysroot,cc,pkg);command[0]=str(make);run(command,mode+'-build',build)
            objects={p.name:SHA(p) for p in (build/'obj').glob('*.o')};assert set(objects)=={unit+'.o' for unit in units}
            assert inv(build/'src')==source and SHA(build/'Makefile')==producers[str(r/'Makefile')]
            lines=compile_contract((q/(mode+'-build.stdout')).read_text(),units,mode)
            deps=sorted((build/'obj').glob('*.d'));assert {p.stem for p in deps}==set(units)
            for dep in deps:bind_dep(dep,build)
            report['modes'][mode]=dict(binary_sha256=SHA(build/'opentyrian2000'),objects_sha256=objects,source_sha256=inv(build/'src'),fresh_object_count=86,compile_commands=lines,all_project_tus_sanitized=mode=='hd-on-asan-ubsan')
            measure();save()
        build=q/'hd-on-asan-ubsan-build'
        cflags=shlex.split(subprocess.check_output([pkg,'--cflags','sdl2','SDL2_net'],env=env,text=True));libs=shlex.split(subprocess.check_output([pkg,'--libs','sdl2','SDL2_net'],env=env,text=True))
        flags=['-std=c99','-O1','-g','-DWITH_NETWORK','-DTARGET_UNIX','-DNEWSHF_HD_COMPOSITOR=1','-I'+str(a.sysroot/'usr/include/x86_64-linux-gnu'),*cflags,'-I'+str(build/'src'),*SAN,'-no-pie']
        renamed=build/'opentyr-test.o';renamed_dep=q/'renamed-main.d'
        run([cc,*flags,'-Dmain=unused_game_main','-MD','-MF',renamed_dep,'-c',build/'src/opentyr.c','-o',renamed],'renamed-main',q,empty_stderr=True);bind_dep(renamed_dep,q)
        objects=[p for p in sorted((build/'obj').glob('*.o')) if p.stem not in ('render_mirror','opentyr')];assert len(objects)==84
        exe=q/'projectile61-fresh-test';harness_dep=q/'renderer-harness.d'
        run([cc,*flags,'-MD','-MF',harness_dep,q/'harness.c',renamed,*objects,*libs,'-lm','-o',exe],'full-sanitized-harness',q,empty_stderr=True);bind_dep(harness_dep,q)
        report['native_linked_objects_sha256']={str(p):SHA(p) for p in [renamed,*objects]}
        assert all(Path(p).is_relative_to(build) for p in report['native_linked_objects_sha256'])
        assert len(report['fresh_dependency_file_sha256'])==4*86+2
        packs=[]
        for name,missing,bad in PACKS:
            pack=q/name;pack.mkdir();(pack/'content').symlink_to(content,target_is_directory=True)
            for selector,p in hdas.items():
                if selector in missing:continue
                raw=bytearray(p.read_bytes())
                if selector==bad:raw[128]^=1
                (pack/p.name).write_bytes(raw)
            packs.append(pack)
        report['fixture_sha256']={str(p):SHA(p) for pack in packs for p in pack.iterdir() if p.is_file()}
        old_stdin,new_stdin=native_inputs(a.data)
        assert legacy['stdin_sha256']==OLD_STDIN_SHA
        report['old107_stdin_sha256']=hashlib.sha256(old_stdin).hexdigest();report['new61_stdin_sha256']=hashlib.sha256(new_stdin).hexdigest()
        run([exe,'--inherited107',*packs[:5]],'inherited107',q,old_stdin,True)
        assert (q/'inherited107.stdout').read_text()==prior['inherited107_stdout']
        run([exe,'--projectile61',*packs],'native61',q,new_stdin,True)
        oldout=(q/'inherited107.stdout').read_text();newout=(q/'native61.stdout').read_text()
        counts=verify_stdout(oldout,newout,prior)
        report.update(status=SUCCESS,inherited107_stdout=oldout,new61_stdout=newout,native_counts=counts,binary_sha256=SHA(exe),generated_wrapper_sha256=SHA(q/'harness.c'))
    except BaseException as error:report.update(status='FAIL_RETAINED',error=repr(error));raise
    finally:
        binding={**producers,**assets,**data,**system_headers,**toolchain,**generated,**report['fresh_dependency_sha256'],**report['fresh_dependency_file_sha256'],**report.get('fixture_sha256',{}),**report.get('native_linked_objects_sha256',{})}
        checks={};check_errors={};after_identity=None;after_raw=None;after_semantic=None
        try:
            after_identity,after_raw,after_semantic=identity(r);(q/'root-index-after.bin').write_bytes(after_raw)
            (q/'root-index-semantic-after.bin').write_bytes(after_semantic)
        except Exception as error:check_errors['after_index_snapshot']=repr(error)
        conditions={
            'source_unchanged':lambda:inv(r/'src')==source,
            'scripts_unchanged':lambda:inv(r/'scripts')==scripts,
            'all_bound_inputs_unchanged':lambda:all(SHA(Path(p))==h for p,h in binding.items()),
            'complete_hydrated_root_unchanged':lambda:hydrated_manifest(r)==root_files,
            'head_unchanged':lambda:after_identity is not None and after_identity['head']==root_identity['head'],
            'raw_index_unchanged':lambda:after_raw==raw_index,
            'semantic_index_unchanged':lambda:after_identity is not None and after_identity['semantic_sha256']==root_identity['semantic_sha256'],
            'index_before_snapshot_intact':lambda:SHA(q/'root-index-before.bin')==root_identity['raw_sha256'],
            'semantic_before_snapshot_intact':lambda:SHA(q/'root-index-semantic-before.bin')==root_identity['semantic_sha256'],
            'semantic_after_snapshot_intact':lambda:after_identity is not None and SHA(q/'root-index-semantic-after.bin')==after_identity['semantic_sha256'],
            'root_manifest_before_snapshot_intact':lambda:SHA(q/'root-files-before.json')==report['root_files_manifest_sha256'],
            'build_sources_unchanged':lambda:all(inv(q/(mode+'-build/src'))==source for mode in report['builds_started']),
            'fresh_objects_and_binaries_unchanged':lambda:all(SHA(q/(mode+'-build/obj')/name)==pin for mode,row in report['modes'].items() for name,pin in row['objects_sha256'].items()) and all(SHA(q/(mode+'-build/opentyrian2000'))==row['binary_sha256'] for mode,row in report['modes'].items())}
        for name,check in conditions.items():guarded_check(checks,check_errors,name,check)
        used=allocated(q);free=shutil.disk_usage(q).free;checks['final_budget_with_receipt_margin']=budget_ok(used+4096,free-4096)
        report.update(status_before_final_checks=report['status'],checks=checks,final_check_errors=check_errors,root_identity_after=after_identity,raw_index_after_snapshot_sha256=hashlib.sha256(after_raw).hexdigest() if after_raw is not None else None,semantic_index_after_snapshot_sha256=hashlib.sha256(after_semantic).hexdigest() if after_semantic is not None else None,final_allocated_bytes=used,free_after=free,seconds=time.monotonic()-start)
        if not checks['final_budget_with_receipt_margin']:report['status']='FAIL_BUDGET_RETAINED'
        elif not all(checks.values()):report['status']='FAIL_BINDING_RETAINED'
        save()
        if not budget_ok(allocated(q),shutil.disk_usage(q).free):report['status']='FAIL_BUDGET_AFTER_RECEIPT';save();raise AssertionError('Final receipt exceeded budget; failure retained')
        print(json.dumps({k:report.get(k) for k in ('status','native_counts','checks','peak_allocated_sample','minimum_free_sample','final_allocated_bytes','free_after','error')},indent=2))
    assert report['status']==SUCCESS

if __name__=='__main__':main()
