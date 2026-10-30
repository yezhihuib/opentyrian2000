#!/usr/bin/env python3
"""Four complete fresh blue builds and original264 + selected-art365 oracles.

All86 project TUs are freshly compiled in each configuration. The native test
links84 new SAN objects, a fresh renamed main and the real renderer/harness.
No historical object, executable or dependency file is consumed. Original264
source/stdin/stdout remain exact; selected101V6/120V4/139 is a new629 epoch.
External SDL/system libraries remain native; LSan is disabled. This is not a
new gameplay capture, uncontrolled survival proof or full test-gate result.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,re,resource,shlex,shutil,signal,stat,subprocess,sys,threading,time

SHA=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
PEAK=256*1024**2
FINAL_CAP=192*1024**2
RESERVE=250*1024**2
START_REQUIRED=PEAK+RESERVE
MODES={'default-off':'','hd-on':'-DNEWSHF_HD_COMPOSITOR=1','mirror-disabled':'-DNEWSHF_HD_COMPOSITOR=1 -DRENDER_MIRROR_DISABLED','hd-on-asan-ubsan':'-DNEWSHF_HD_COMPOSITOR=1'}
SAN=('-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie')
DEFAULT_CFLAGS='-pedantic -Wall -Wextra -Wno-format-truncation -Wno-missing-field-initializers -O2'
FRESH61_SHA='b684d867d511c43e12e9fe5f4e0d73757403881d20cb07701661bd2341479930'
PRIOR_BLUE_SHA='be6a43f073d7425790ddcc108b1d9daa4a00dbf9153cb8b32568f9cda9a3fdda'
NATIVE_HELPER_SHA='38d904bf84c17ae9179c6c4bc4ca895f31393efcc774ac851d7db1bc6a23ef6d'
PAYLOAD_HEADER='current_projectile_blue_triplet_payload_pins.h'
PAYLOAD_HEADER_SHA='857978d85a52b73a8c0a8bd9ba318a13da715db12d3ffd168e22f35a778874c8'
BLUE=(101,120,139)
SELECTORS=(91,145,61,*BLUE)
HDA_SHA={101:'4f1cb932fa0418f3236d8240a3012ec19d65ab3d33a862190a75f53302db8ac6',120:'e8935de840d09ed83e65206664ba3a4ddf25b11764ba2b6038ac752140dcb83b',139:'47a6941988a2e2a4835859dfc1cf12f2481b2bf29bab18be94307b408cf34942'}
SUCCESS='PASS_FOUR_FRESH_CONFIGS_AND_FULL_PROJECT_SANITIZED629'
HISTORICAL61_FILES=('receipt.json','inherited107.stdout','native61.stdout')
HISTORICAL_BLUE_FILES=('receipt.json',)
PROTECTION_SHA='ecda303ffb05dd6b9a33e011233092b06141ead9c2e034f7c4fdeca7b3df3e20'
PROTECTED_NAMES=('projectile61-private-sparse','projectile145-private-sparse','newshf166-private','newshf169-private','shared170-bronze356-private')


def inv(root):return {p.relative_to(root).as_posix():SHA(p) for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in p.parts}
def allocated(root):
    total=0
    for p in (root,*root.rglob('*')):
        try:total+=p.lstat().st_blocks*512
        except FileNotFoundError:pass
    return total

def budget_ok(used,free,final=False):return used<=(FINAL_CAP if final else PEAK) and free>=RESERVE

def guarded_check(checks,errors,name,fn):
    try:checks[name]=bool(fn())
    except Exception as error:checks[name]=False;errors[name]=repr(error)
    return checks[name]

def snapshot_allocation(raw,semantic):return sum((len(x)+4095)//4096*4096 for x in (raw,semantic))
def dependency_tokens(text):
    text=text.replace('\\\n',' ')
    if ':' not in text:raise ValueError('Dependency rule has no colon')
    return shlex.split(text.split(':',1)[1])

def git(root,*args):return subprocess.check_output(['git','--no-optional-locks','-C',str(root),*args],env={**os.environ,'GIT_OPTIONAL_LOCKS':'0'})
def identity(root):
    index=Path(git(root,'rev-parse','--path-format=absolute','--git-path','index').decode().strip())
    raw=index.read_bytes();semantic=git(root,'ls-files','--stage','-z')
    assert index.read_bytes()==raw,'Read-only query changed raw index'
    return dict(head=git(root,'rev-parse','HEAD').decode().strip(),index_path=str(index),raw_sha256=hashlib.sha256(raw).hexdigest(),semantic_sha256=hashlib.sha256(semantic).hexdigest()),raw,semantic

def hydrated_manifest(root):
    tagged=git(root,'ls-files','-t','-z')
    assert not any(row.startswith(b'S ') for row in tagged.split(b'\0')),'Full hydration required; sparse is not inventory qualification'
    staged=git(root,'ls-files','--stage','-z')
    for row in staged.split(b'\0'):
        if row:assert row.split(b'\t',1)[0].split()[2]==b'0','Unmerged index'
    names=git(root,'ls-files','--cached','--others','--exclude-standard','-z').decode().split('\0');result={}
    for name in sorted(set(names)-{''}):
        relative=Path(name);assert not relative.is_absolute() and '..' not in relative.parts
        p=root/relative;s=p.lstat();assert stat.S_ISREG(s.st_mode) and s.st_nlink==1,'Missing/linked repository input:'+name
        result[name]={'sha256':SHA(p),'bytes':s.st_size,'mode':stat.S_IMODE(s.st_mode),'nlink':s.st_nlink}
    assert result
    return result

def historical_inputs(fresh61,prior_blue):
    """Exact four-file allowlist. Never recurse or dereference historical .o/ELF/.d."""
    paths=[fresh61/name for name in HISTORICAL61_FILES]+[prior_blue/name for name in HISTORICAL_BLUE_FILES]
    pins={str(p):SHA(p) for p in paths}
    assert pins[str(fresh61/'receipt.json')]==FRESH61_SHA and pins[str(prior_blue/'receipt.json')]==PRIOR_BLUE_SHA
    accepted=json.loads((fresh61/'receipt.json').read_text());prior=json.loads((prior_blue/'receipt.json').read_text())
    assert accepted['status']=='PASS_FOUR_FRESH_CONFIGS_AND_FULL_PROJECT_SANITIZED264' and all(accepted['checks'].values())
    assert prior['status']=='PASS_ORIGINAL264_AND_BLUE_TRIPLET_PRODUCTION_TU' and all(prior['checks'].values())
    assert (fresh61/'inherited107.stdout').read_text()==accepted['inherited107_stdout']
    assert (fresh61/'native61.stdout').read_text()==accepted['new61_stdout']
    return accepted,prior,pins

def load_native(root):
    path=root/'tests/projectile_blue_triplet_native_validation.py'
    assert re.fullmatch('[0-9a-f]{64}',NATIVE_HELPER_SHA),'Draft helper pin; execution is forbidden'
    assert SHA(path)==NATIVE_HELPER_SHA,'Current installed helper differs; no external fallback'
    spec=importlib.util.spec_from_file_location('blue_selected_native_helpers',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

def protected_roots(snapshot,current):
    """Exact retained five-root snapshot; retired asset roots are not included."""
    assert SHA(snapshot)==PROTECTION_SHA
    original=json.loads(snapshot.read_text());rows=original['protected_after']
    assert set(rows)==set(PROTECTED_NAMES)
    result={}
    for name,row in rows.items():
        p=current.parent/name;assert p!=current and set(row)=={'identity','source_sha256'}
        expected=row['source_sha256'];assert expected and all(k.startswith('src/') for k in expected)
        assert identity(p)[0]==row['identity'] and {'src/'+k:v for k,v in inv(p/'src').items()}==expected,name
        result[str(p)]=row
    return result

def sanitized_env(parent,sysroot,tmp):
    env=dict(parent)
    for key in tuple(env):
        if key.startswith(('AIRCRAFT','SHARED','PROJECTILE','TYRIAN_GAME_PROBE','TYRIAN_CYAN_BORROW','OT_')) or key in ('MAKEFLAGS','MFLAGS','MAKEOVERRIDES','CC','CFLAGS','CPPFLAGS','LDFLAGS','LDLIBS','CPATH','C_INCLUDE_PATH','CPLUS_INCLUDE_PATH','COMPILER_PATH','GCC_EXEC_PREFIX','LIBRARY_PATH','LD_PRELOAD','LD_AUDIT','PKG_CONFIG_PATH','PKG_CONFIG'):
            env.pop(key)
    env.update(PKG_CONFIG_SYSROOT_DIR=str(sysroot),PKG_CONFIG_LIBDIR=str(sysroot/'usr/lib/x86_64-linux-gnu/pkgconfig'),LD_LIBRARY_PATH=str(sysroot/'usr/lib/x86_64-linux-gnu'),SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',SDL_RENDER_DRIVER='software',ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1',TMPDIR=str(tmp))
    return env

def make_command(mode,sysroot,cc,pkg):
    assert mode in MODES
    cpp='-MD -DNDEBUG '+MODES[mode]+' -I'+str(sysroot/'usr/include/x86_64-linux-gnu')
    ld='-Wl,-rpath,'+str(sysroot/'usr/lib/x86_64-linux-gnu');flags=DEFAULT_CFLAGS
    if mode=='hd-on-asan-ubsan':ld+=' -fsanitize=address,undefined -no-pie';flags='-O1 -g '+' '.join(SAN)
    return ['make','-j2','CC='+str(cc),'PKG_CONFIG='+str(pkg),'VCS_IDREV=printf blue-triplet-fresh-native','CPPFLAGS='+cpp,'CFLAGS='+flags,'LDFLAGS='+ld]

def compile_contract(log,units,mode):
    lines=[line for line in log.splitlines() if ' -c -o obj/' in line];assert len(lines)==86;observed=[]
    for line in lines:
        argv=shlex.split(line);out=argv[argv.index('-o')+1];unit=Path(out).stem
        assert out=='obj/'+unit+'.o' and argv[-1]=='src/'+unit+'.c' and '-MD' in argv and '-DNDEBUG' in argv
        assert ('-DNEWSHF_HD_COMPOSITOR=1' in argv)==(mode!='default-off')
        assert ('-DRENDER_MIRROR_DISABLED' in argv)==(mode=='mirror-disabled')
        if mode=='hd-on-asan-ubsan':assert all(flag in argv for flag in (*SAN,'-O1','-g'))
        else:assert '-O2' in argv and not any(flag.startswith('-fsanitize=') for flag in argv)
        observed.append(unit)
    assert len(set(observed))==86 and set(observed)==set(units)
    links=[shlex.split(line) for line in log.splitlines() if ' -o opentyrian2000 ' in line]
    assert len(links)==1
    linked=links[0];assert {Path(x).name for x in linked if x.startswith('obj/') and x.endswith('.o')}=={u+'.o' for u in units}
    assert ('-fsanitize=address,undefined' in linked)==(mode=='hd-on-asan-ubsan')
    return lines,linked


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ('root','accepted61-fresh','prior-blue-native','protection-snapshot','data','sysroot','out'):
        parser.add_argument('--'+key,type=Path,required=True)
    a=parser.parse_args();a=argparse.Namespace(**{k:v.resolve() for k,v in vars(a).items()});r=a.root;q=a.out
    assert not q.exists() and not q.is_relative_to(r) and shutil.disk_usage(q.parent).free>=START_REQUIRED
    ri,raw,semantic=identity(r);files=hydrated_manifest(r);assert identity(r)[0]==ri
    source=inv(r/'src');scripts=inv(r/'scripts');units=sorted(p.stem for p in (r/'src').glob('*.c'));assert len(source)==312 and len(units)==86
    prior61,priorblue,historical=historical_inputs(a.accepted61_fresh,a.prior_blue_native)
    assert set(source)==set(priorblue['source_sha256']) and {p for p in source if source[p]!=priorblue['source_sha256'][p]}=={PAYLOAD_HEADER}
    assert source[PAYLOAD_HEADER]==PAYLOAD_HEADER_SHA
    protection=protected_roots(a.protection_snapshot,r)
    native=load_native(r);native.verify_legacy_stdout(prior61['inherited107_stdout'],prior61['new61_stdout'])
    companion=r/'tests/projectile_blue_triplet_native_additions.c.inc'
    generated_bytes=native.harness_sources(r,companion.read_bytes())
    assert set(generated_bytes)=={'inherited145_harness.c','accepted_projectile61_native_additions.c.inc','accepted61_wrapper.c','projectile61_native_additions.c.inc','projectile_blue_triplet_native_additions.c.inc','harness.c'}
    old_stdin,new_stdin=native.native_inputs(a.data)
    assert hashlib.sha256(old_stdin).hexdigest()==prior61['old107_stdin_sha256'] and hashlib.sha256(new_stdin).hexdigest()==prior61['new61_stdin_sha256']
    driver=Path(__file__).resolve();assert SHA(r/'tests'/driver.name)==SHA(driver),'Install frozen new QA epoch before launch'
    producers={str(p):SHA(p) for p in (driver,r/'tests'/driver.name,r/'tests/test_projectile_blue_triplet_fresh_native_adapter.py',r/'tests/projectile_blue_triplet_native_validation.py',r/'tests/test_projectile_blue_triplet_native_adapter.py',companion,r/'tests/projectile61_native_validation.py',r/'tests/projectile61_native_additions.c.inc',r/'tests/projectile145_native_additions.c.inc',r/'tests/test_projectile91_global_runtime.py',r/'Makefile',a.protection_snapshot)}
    producers.update(historical)
    sys.path.insert(0,str(r/'scripts'));import current_projectile_blue_triplet_compatibility as art
    assert len(art.load(r))==3
    assets={}
    for selector in ('91','145','61','blue-triplet'):
        for sub in (f'authoring-inputs/projectile{selector}-current',f'assets/hd/current-compat/projectile{selector}') if selector!='blue-triplet' else ('authoring-inputs/projectile-blue-triplet-current','assets/hd/current-compat/projectile-blue-triplet'):
            for p in (r/sub).rglob('*'):
                if p.is_file():assets[str(p)]=SHA(p)
    blue_inputs={str(r/p) for p in art.input_paths(r)}
    for sub in ('authoring-inputs/projectile-blue-triplet-current','assets/hd/current-compat/projectile-blue-triplet'):
        blue_inputs.update(str(p) for p in (r/sub).rglob('*') if p.is_file())
    for p in art.input_paths(r):assets[str(r/p)]=SHA(r/p)
    content=r/'assets/hd/global-assets-v1/content';assert content.is_dir()
    content_files=[p for p in content.rglob('*') if p.is_file()];assert len(content_files)==125
    for p in content_files:assets[str(p.resolve())]=SHA(p)
    hdas={i:r/f'assets/hd/current-compat/projectile{i}/enemy-projectile{i}-{i}-8.hda' for i in (91,145,61)}
    hdas.update({i:r/f'assets/hd/current-compat/projectile-blue-triplet/enemy-projectile-blue-triplet-{i}-8.hda' for i in BLUE})
    for i,p in hdas.items():
        assert len(p.read_bytes())==43036;assets[str(p)]=SHA(p)
        if i in BLUE:assert assets[str(p)]==HDA_SHA[i]
    old_roots=[Path(p).parent for p in prior61['producer_sha256'] if Path(p).name=='Makefile'];assert len(old_roots)==1
    for p,h in assets.items():
        path=Path(p)
        if path.is_relative_to(r) and p not in blue_inputs:
            oldkey=str(old_roots[0]/path.relative_to(r))
            assert prior61['asset_sha256'].get(oldkey)==h,('Changed inherited asset',p)
    headers=[r/'assets/hd/shared-menu-runs-v1'/name for name in ('reconstructed_run_specs.h','reconstructed_numeric_specs.h','reconstructed_name_source_specs.h')]
    for p in headers:
        assets[str(p)]=SHA(p);assert prior61['asset_sha256'][str(old_roots[0]/p.relative_to(r))]==assets[str(p)]
    data={str(a.data/name):SHA(a.data/name) for name in native.DATA_SHA};assert all(data[str(a.data/n)]==h for n,h in native.DATA_SHA.items())
    env=sanitized_env(os.environ,a.sysroot,q/'tmp');cc=Path(shutil.which('cc',path=env.get('PATH'))).resolve();pkg=Path(shutil.which('pkg-config',path=env.get('PATH'))).resolve();make=Path(shutil.which('make',path=env.get('PATH'))).resolve()
    builtin=Path(subprocess.check_output([cc,'-print-file-name=include'],env=env,text=True).strip()).resolve();system={}
    for base in (a.sysroot/'usr/include',Path('/usr/include'),builtin):
        for p in base.rglob('*'):
            if p.is_file():system[str(p.resolve())]=SHA(p)
    tools={str(p):SHA(p) for p in (cc,pkg,make)}
    assert identity(r)[0]==ri and hydrated_manifest(r)==files and protected_roots(a.protection_snapshot,r)==protection
    q.mkdir();(q/'tmp').mkdir();(q/'root-index-before.bin').write_bytes(raw);(q/'root-index-semantic-before.bin').write_bytes(semantic);(q/'root-files-before.json').write_text(json.dumps(files,indent=2)+'\n')
    for name,payload in generated_bytes.items():(q/name).write_bytes(payload)
    generated={str(q/name):SHA(q/name) for name in generated_bytes}
    report={'status':'RUNNING','scope':__doc__,'root_identity_before':ri,'roots_protection':protection,'root_file_count':len(files),'root_manifest_sha256':SHA(q/'root-files-before.json'),'source_sha256':source,'scripts_sha256':scripts,'producer_sha256':producers,'asset_sha256':assets,'original_data_sha256':data,'current_system_header_sha256':system,'toolchain_sha256':tools,'generated_input_sha256':generated,'historical_consumers':historical,'historical_objects_consumed':0,'historical_executables_consumed':0,'historical_depfiles_consumed':0,'all_builds_fresh':True,'reused_project_objects':0,'commands':[],'builds_started':[],'modes':{},'fresh_dependency_file_sha256':{},'fresh_dependency_sha256':{},'native_linked_objects_sha256':{},'fixture_sha256':{},'peak_cap':PEAK,'final_cap':FINAL_CAP,'reserve':RESERVE,'peak_allocated':allocated(q),'minimum_free':shutil.disk_usage(q).free,'sample_interval_seconds':.25,'old107_stdin_sha256':hashlib.sha256(old_stdin).hexdigest(),'old61_stdin_sha256':hashlib.sha256(new_stdin).hexdigest(),'original_stdin_persisted':False,'sanitizer_scope':'All86projectTUs freshly SAN in fourthbuild; native84newSANobjects+newmain+newrenderer. SystemSDLnative;LSanoff. No gamecapture/fullgate claim.','original264_byte_exact':True,'old_failures_retained':'All prior natural deaths,artcoverageFAILs and historical145raw-statFAIL remain separate immutable evidence; no qualification transfer.'}
    def save():(q/'receipt.json').write_text(json.dumps(report,indent=2)+'\n')
    def measure(extra=0,final=False):
        used=allocated(q);free=shutil.disk_usage(q).free;report['peak_allocated']=max(used,report['peak_allocated']);report['minimum_free']=min(free,report['minimum_free'])
        assert budget_ok(used+extra,free-extra,final),('budget',used,free,extra,final)
    def no_core():resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    def run(cmd,label,cwd,payload=None,empty_stderr=False):
        row={'argv':list(map(str,cmd)),'label':label,'cwd':str(cwd)};report['commands'].append(row);save();measure()
        with (q/(label+'.stdout')).open('wb') as out,(q/(label+'.stderr')).open('wb') as err:
            proc=subprocess.Popen(row['argv'],cwd=cwd,env=env,stdin=subprocess.PIPE if payload is not None else subprocess.DEVNULL,stdout=out,stderr=err,start_new_session=True,preexec_fn=no_core);row['pid']=proc.pid;started=time.monotonic();writer_errors=[]
            def feed():
                try:proc.stdin.write(payload);proc.stdin.close()
                except BaseException as error:writer_errors.append(repr(error))
            feeder=threading.Thread(target=feed,daemon=True) if payload is not None else None
            try:
                save()
                if feeder:feeder.start()
                while proc.poll() is None:measure();assert time.monotonic()-started<900,'timeout';time.sleep(.25)
            except BaseException:
                if proc.poll() is None:
                    os.killpg(proc.pid,signal.SIGTERM)
                    try:proc.wait(timeout=10)
                    except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
                row['stopped']=True;raise
            finally:
                if feeder is not None and feeder.ident is not None:feeder.join(timeout=2)
                row.update(returncode=proc.poll(),seconds=time.monotonic()-started,stdin_writer_errors=writer_errors)
                try:save()
                except Exception as write_error:row['terminal_save_error']=repr(write_error)
            assert 'terminal_save_error' not in row,'Command terminal receipt write failed'
            assert not writer_errors and (feeder is None or not feeder.is_alive()),'stdin transfer'
            assert row['returncode']==0,(label,row['returncode'])
        row.update(stdout_sha256=SHA(q/(label+'.stdout')),stderr_sha256=SHA(q/(label+'.stderr')))
        if empty_stderr:assert not (q/(label+'.stderr')).read_bytes(),label+' stderr'
        measure();save()
    def bind_dep(dep,cwd):
        report['fresh_dependency_file_sha256'][str(dep)]=SHA(dep)
        for token in dependency_tokens(dep.read_text()):
            path=(cwd/token).resolve() if not Path(token).is_absolute() else Path(token).resolve();digest=SHA(path);expected=generated.get(str(path),system.get(str(path)))
            for mode in MODES:
                build=q/(mode+'-build')
                if path.is_relative_to(build/'src'):expected=source.get(path.relative_to(build/'src').as_posix());break
                if path.is_relative_to(build/'assets'):expected=assets.get(str(r/path.relative_to(build)));break
            assert expected==digest,('Unbound actual dependency',str(path),expected,digest)
            report['fresh_dependency_sha256'][str(path)]=digest
    started=time.monotonic();save()
    try:
        measure()
        for mode in MODES:
            build=q/(mode+'-build');assert not build.exists();build.mkdir();report['builds_started'].append(mode)
            shutil.copytree(r/'src',build/'src');shutil.copyfile(r/'Makefile',build/'Makefile')
            for p in headers:dest=build/p.relative_to(r);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
            assert not (build/'obj').exists() and not (build/'opentyrian2000').exists()
            cmd=make_command(mode,a.sysroot,cc,pkg);cmd[0]=str(make);run(cmd,mode+'-build',build,empty_stderr=mode=='hd-on-asan-ubsan')
            objects={p.name:SHA(p) for p in (build/'obj').glob('*.o')};assert set(objects)=={u+'.o' for u in units}
            assert inv(build/'src')==source and SHA(build/'Makefile')==producers[str(r/'Makefile')]
            compile_lines,link=compile_contract((q/(mode+'-build.stdout')).read_text(),units,mode)
            deps=sorted((build/'obj').glob('*.d'));assert {p.stem for p in deps}==set(units)
            for dep in deps:bind_dep(dep,build)
            report['modes'][mode]={'objects_sha256':objects,'binary_sha256':SHA(build/'opentyrian2000'),'source_sha256':inv(build/'src'),'compile_commands':compile_lines,'link_command':link,'fresh_object_count':86,'sanitized':mode=='hd-on-asan-ubsan'};measure();save()
        build=q/'hd-on-asan-ubsan-build';cflags=shlex.split(subprocess.check_output([pkg,'--cflags','sdl2','SDL2_net'],env=env,text=True));libs=shlex.split(subprocess.check_output([pkg,'--libs','sdl2','SDL2_net'],env=env,text=True))
        flags=['-std=c99','-O1','-g','-DWITH_NETWORK','-DTARGET_UNIX','-DNEWSHF_HD_COMPOSITOR=1','-I'+str(a.sysroot/'usr/include/x86_64-linux-gnu'),*cflags,'-I'+str(build/'src'),*SAN,'-no-pie']
        renamed=build/'opentyr-test.o';dep=q/'renamed-main.d'
        run([cc,*flags,'-Dmain=unused_game_main','-MD','-MF',dep,'-c',build/'src/opentyr.c','-o',renamed],'renamed-main',q,empty_stderr=True);bind_dep(dep,q)
        objects=[p for p in sorted((build/'obj').glob('*.o')) if p.stem not in ('render_mirror','opentyr')];assert len(objects)==84
        exe=q/'blue-triplet-fresh-test';dep=q/'renderer-harness.d'
        run([cc,*flags,'-MD','-MF',dep,q/'harness.c',renamed,*objects,*libs,'-lm','-o',exe],'full-sanitized-harness',q,empty_stderr=True);bind_dep(dep,q)
        report['native_linked_objects_sha256']={str(p):SHA(p) for p in [renamed,*objects]};report['native_binary_sha256']=SHA(exe)
        assert len(report['native_linked_objects_sha256'])==85 and all(Path(p).is_relative_to(build) for p in report['native_linked_objects_sha256'])
        assert len(report['fresh_dependency_file_sha256'])==346
        native_dependencies={(q/Path(token)).resolve() if not Path(token).is_absolute() else Path(token).resolve() for token in dependency_tokens(dep.read_text())}
        assert {build/'src'/name for name in ('render_mirror.c','global_projectile91_mirror.inc','enemy_blue_triplet_mirror.inc',PAYLOAD_HEADER)}<=native_dependencies,'Native harness must actually consume new renderer and payload pins'
        fixtures=native.fixture_payloads({i:p.read_bytes() for i,p in hdas.items()});assert len(fixtures)==151
        leaves=[q/'legacy264'/name for name,_,_ in native.PACKS]+[q/'blue-packs'/name for name in native.PACK_NAMES]
        assert len(leaves)==34 and len(set(leaves))==34
        for pack in leaves:pack.mkdir(parents=True);(pack/'content').symlink_to(content,target_is_directory=True);measure()
        for name,blob in fixtures.items():
            rel=Path(name);assert not rel.is_absolute() and '..' not in rel.parts and (q/rel).parent in leaves
            (q/rel).write_bytes(blob);report['fixture_sha256'][str(q/rel)]=SHA(q/rel);measure()
        legacy=[q/'legacy264'/name for name,_,_ in native.PACKS]
        for argv,label,payload in (([exe,'--inherited107',*legacy[:5]],'inherited107',old_stdin),([exe,'--projectile61',*legacy],'inherited61',new_stdin),([exe,'--blue-triplet',q/'blue-packs'],'new-blue-triplet',new_stdin)):
            assert SHA(exe)==report['native_binary_sha256'];run(argv,label,q,payload,True)
        oldout=(q/'inherited107.stdout').read_text();newout=(q/'inherited61.stdout').read_text();blueout=(q/'new-blue-triplet.stdout').read_text()
        assert oldout==prior61['inherited107_stdout'] and newout==prior61['new61_stdout']
        inherited_counts=native.verify_legacy_stdout(oldout,newout);blue_counts=native.parse_blue_stdout(blueout)
        assert inherited_counts['total_cases']==264 and blue_counts['new_cases']==365
        report.update(status=SUCCESS,inherited107_stdout=oldout,inherited61_stdout=newout,new_blue_stdout=blueout,inherited_counts=inherited_counts,new_counts=blue_counts,total_cases=629,total_assertions=inherited_counts['total_assertions']+blue_counts['new_assertions']);measure(final=True)
    except BaseException as error:
        report.update(status='FAIL_RETAINED',error=repr(error))
        try:save()
        except Exception as write_error:report['outcome_save_error']=repr(write_error)
        raise
    finally:
        report['status_before_final_checks']=report['status'];checks={};errors={}
        try:save()
        except Exception as error:errors['save_original_outcome']=repr(error)
        def guard(name,fn):return guarded_check(checks,errors,name,fn)
        binding={**producers,**assets,**data,**system,**tools,**generated,**report['fresh_dependency_sha256'],**report['fresh_dependency_file_sha256'],**report['native_linked_objects_sha256'],**report['fixture_sha256']}
        conditions={'source_unchanged':lambda:inv(r/'src')==source,'scripts_unchanged':lambda:inv(r/'scripts')==scripts,'all_actual_bound_inputs_unchanged':lambda:all(SHA(Path(p))==h for p,h in binding.items()),'complete_hydrated_root_unchanged':lambda:hydrated_manifest(r)==files,'protected_roots_unchanged':lambda:protected_roots(a.protection_snapshot,r)==protection,'root_manifest_snapshot_intact':lambda:SHA(q/'root-files-before.json')==report['root_manifest_sha256'],'before_raw_snapshot_intact':lambda:SHA(q/'root-index-before.bin')==ri['raw_sha256'],'before_semantic_snapshot_intact':lambda:SHA(q/'root-index-semantic-before.bin')==ri['semantic_sha256'],'build_sources_unchanged':lambda:all(inv(q/(mode+'-build/src'))==source for mode in report['builds_started']),'fresh_objects_and_binaries_unchanged':lambda:all(SHA(q/(mode+'-build/obj')/name)==h for mode,row in report['modes'].items() for name,h in row['objects_sha256'].items()) and all(SHA(q/(mode+'-build/opentyrian2000'))==row['binary_sha256'] for mode,row in report['modes'].items()),'native_binary_unchanged':lambda:'native_binary_sha256' not in report or SHA(q/'blue-triplet-fresh-test')==report['native_binary_sha256']}
        for name,fn in conditions.items():guard(name,fn)
        captured={}
        def capture_identity():
            after,raw_after,semantic_after=identity(r);captured.update(identity=after,raw=raw_after,semantic=semantic_after);report['root_identity_after']=after
            return after==ri
        guard('final_identity_read_and_match',capture_identity)
        if captured:
            extra=snapshot_allocation(captured['raw'],captured['semantic']);report['planned_after_snapshot_allocation']=extra
            def snapshots():
                measure(extra+131072,True)
                (q/'root-index-after.bin').write_bytes(captured['raw']);(q/'root-index-semantic-after.bin').write_bytes(captured['semantic']);measure(131072,True)
                report['raw_index_after_snapshot_sha256']=SHA(q/'root-index-after.bin');report['semantic_index_after_snapshot_sha256']=SHA(q/'root-index-semantic-after.bin')
                return report['raw_index_after_snapshot_sha256']==captured['identity']['raw_sha256'] and report['semantic_index_after_snapshot_sha256']==captured['identity']['semantic_sha256']
            guard('after_snapshot_budget_write_and_hash',snapshots)
        guard('final_budget_with_receipt_margin',lambda:budget_ok(allocated(q)+131072,shutil.disk_usage(q).free-131072,True))
        def observed_budget():
            report.update(final_allocated_bytes=allocated(q),free_after=shutil.disk_usage(q).free);return True
        guard('final_observed_allocation_and_free',observed_budget)
        report.update(checks=checks,final_check_errors=errors,seconds=time.monotonic()-started)
        if errors or not all(checks.values()):report['status']='FAIL_FINAL_BINDING_OR_BUDGET_RETAINED'
        try:save()
        except Exception as error:errors['final_save']=repr(error);report['status']='FAIL_RECEIPT_WRITE_RETAINED'
        guard('postwrite_actual_budget',lambda:budget_ok(allocated(q),shutil.disk_usage(q).free,True))
        if not checks['postwrite_actual_budget']:report['status']='FAIL_BUDGET_AFTER_RECEIPT_RETAINED'
        try:save()
        except Exception as error:errors['postwrite_save']=repr(error);report['status']='FAIL_RECEIPT_WRITE_RETAINED'
        guard('last_actual_budget',lambda:budget_ok(allocated(q),shutil.disk_usage(q).free,True))
        if not checks['last_actual_budget']:
            report['status']='FAIL_BUDGET_AFTER_RECEIPT_RETAINED'
            try:save()
            except Exception as error:errors['last_save']=repr(error)
        print(json.dumps({k:report.get(k) for k in ('status','status_before_final_checks','total_cases','total_assertions','inherited_counts','new_counts','checks','final_check_errors','peak_allocated','minimum_free','final_allocated_bytes','free_after','error')},indent=2))
    assert report['status']==SUCCESS

if __name__=='__main__':main()
