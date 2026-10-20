#!/usr/bin/env python3
"""Extracted production tests. Reads the user's local original source only at runtime.
No game data, decoded pixels, or private source hashes are written to deliverables.
The SDL declarations are a bounded structural shim, not an SDL runtime substitute.
"""
from pathlib import Path
import argparse, hashlib, json, os, re, resource, shlex, shutil, signal, subprocess, time
HERE=Path(__file__).resolve().parent

def extract(source,name):
    m=re.search(r'^[A-Za-z_][^\n;{}]*\b'+re.escape(name)+r'\([^;{}]*\)\s*\{',source,re.M)
    if not m: raise RuntimeError('Cannot find production function '+name)
    i=source.index('{',m.start())+1; depth=1
    while depth:
        depth+=(source[i]=='{')-(source[i]=='}');i+=1
    return source[m.start():i]+'\n'

def rss_kib(pid):
    # Include descendants and fail closed if the process group exceeds its RSS cap.
    total=0
    for p in Path('/proc').iterdir():
        if not p.name.isdigit(): continue
        try:
            stat=(p/'stat').read_text(); fields=stat[stat.rfind(')')+2:].split()
            if int(fields[2]) != pid: continue
            for line in (p/'status').read_text().splitlines():
                if line.startswith('VmRSS:'): total+=int(line.split()[1]);break
        except (FileNotFoundError,ProcessLookupError,PermissionError): pass
    return total

def bounded_run(cmd,cap_mib,timeout,log,env=None):
    def child_limits():
        os.setsid()
        resource.setrlimit(resource.RLIMIT_FSIZE,(32*1024**2,)*2)
        resource.setrlimit(resource.RLIMIT_CPU,(timeout,)*2)
        resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    start=time.monotonic(); peak=0
    with log.open('w') as out:
        p=subprocess.Popen(cmd,stdout=out,stderr=subprocess.STDOUT,env=env,preexec_fn=child_limits)
        while p.poll() is None:
            peak=max(peak,rss_kib(p.pid))
            if peak>cap_mib*1024 or time.monotonic()-start>timeout:
                os.killpg(p.pid,signal.SIGKILL);p.wait()
                raise RuntimeError('RSS/timeout bound reached: '+str(cmd))
            time.sleep(.02)
        if p.returncode: raise RuntimeError('Command failed '+str(p.returncode)+'; see '+str(log))
    return {'status':'passed','peak_rss_kib_observed':peak,'seconds':round(time.monotonic()-start,3),'log':log.name}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--source-sheet',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    repo=a.repo.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
    if shutil.disk_usage(out).free<5*1024**3: raise RuntimeError('Keep at least 5 GiB free')
    src=(repo/'src/render_mirror.c').read_text();sprite=(repo/'src/sprite.c').read_text()
    funcs=['palette_rgb','complete_turret_group','restore_classic_rect','cloud_shadow_rgba','darken_rgba','decode_tile','explosion_blend_rgba','effect_ramp_monotone_to','effect_ramp_monotone','recognized_value_effect','recognized_contact_effect','have_supported_talon']
    groups={'primitives':'\n'.join(extract(src,n) for n in funcs),'pixel':extract(src,'render_mirror_pixel'),'asteroid':(repo/'src/asteroid1_effect_blend_mirror.inc').read_text(),'callback':extract(src,'render_mirror_sprite2_blend_pixel'),'blitter':extract(sprite,'blit_sprite2_blend')}
    for name,body in groups.items():(out/('actual_'+name+'.inc')).write_text(body)
    if 'asteroid1_sprite2_blend_pixel(surface,address,source,bank,index,origin_x,origin_y)' not in groups['callback']:raise RuntimeError('Production callback does not delegate to new helper')
    # The first-level path must remain exactly its parent implementation after
    # removing only the newly scoped ASTEROID1 early delegation.
    old=subprocess.check_output(['git','show','af49180:src/render_mirror.c'],cwd=repo,text=True)
    old_cb=extract(old,'render_mirror_sprite2_blend_pixel')
    old_cb=old_cb.replace('if(asteroid_hd_enabled) {render_mirror_pixel(surface,address,source,MIRROR_BLEND);return;}','if(asteroid_hd_enabled) {asteroid1_sprite2_blend_pixel(surface,address,source,bank,index,origin_x,origin_y);return;}')
    assert old_cb==groups['callback'],'Legacy callback changed outside scoped branch'
    for n in ['render_mirror_pixel','decode_tile','explosion_blend_rgba','effect_ramp_monotone_to','effect_ramp_monotone','recognized_value_effect','recognized_contact_effect','have_supported_talon']:
        assert extract(old,n)==extract(src,n),'Existing function changed: '+n
    assert extract(subprocess.check_output(['git','show','af49180:src/sprite.c'],cwd=repo,text=True),'blit_sprite2_blend')==groups['blitter'],'Original indexed blitter changed'
    cc=shlex.split(os.environ.get('CC','cc'));common=['-std=c99','-Wall','-Wextra','-Werror','-pedantic','-Wno-misleading-indentation','-I'+str(out),str(HERE/'asteroid_effect_blend_test.c')]
    receipt={'extraction':'actual production helper, callback, indexed blitter, fallback and restore; bounded SDL structural shim','first_level_source_identity':'passed: exact baseline functions and unchanged callback tail','game_data':'read-only local newsh6.shp; never copied or emitted','runtime_gameplay':'not tested by this fixture','limits':{'compile_rss_mib':1024,'runtime_rss_mib':512,'minimum_free_gib':5,'leak_detection':'disabled: this executor uses ptrace, incompatible with LeakSanitizer; ASan and UBSan remain enabled','note':'RSS watchdog used because ASan reserves virtual address space beyond an RLIMIT_AS cap'},'extracted_code_sha256':{k:hashlib.sha256(v.encode()).hexdigest() for k,v in groups.items()},'runs':{}}
    for mode,flags in [('optimized',['-O2']),('asan-ubsan',['-O1','-g','-fsanitize=address,undefined','-fno-sanitize-recover=all','-fno-omit-frame-pointer'])]:
        exe=out/('test-'+mode)
        receipt['runs'][mode+'-compile']=bounded_run(cc+common+flags+['-o',str(exe)],1024,90,out/(mode+'-compile.log'))
        env={**os.environ,'ASAN_OPTIONS':'detect_leaks=0:halt_on_error=1:allocator_may_return_null=0','UBSAN_OPTIONS':'halt_on_error=1:print_stacktrace=1'}
        receipt['runs'][mode]=bounded_run([str(exe),str(a.source_sheet.resolve())],512,120,out/(mode+'.log'),env)
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
