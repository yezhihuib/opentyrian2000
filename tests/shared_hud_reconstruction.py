#!/usr/bin/env python3
"""Fresh extracted-production shared-HUD oracle. Original game bytes stay in memory.

Compiles current render_mirror helper bodies, the unmodified font adapter and all
six production loaders. SDL presentation and unrelated families are narrow stubs.
No historical test result is used. Original source enters the child only on stdin.
"""
import argparse, hashlib, json, os, re, struct, subprocess, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).parent
FAMILIES = ['gameplay_hud','gameplay_hud_components','gameplay_hud_meters','gameplay_hud_indicators','gameplay_hud_fixed_text','gameplay_hud_font']
RESOURCES = ['gameplay-hud-v1.hda','gameplay-hud-components-v1.hda','gameplay-hud-meters-v2.hda','gameplay-hud-indicators-v1.hda','gameplay-hud-fixed-text-v1.hda','gameplay-hud-font-v1.hda']
def extract(src,name):
    m=re.search(r'^(?:static )?(?:const char \*|Uint8|Uint32|unsigned(?: int)?|int|void|bool)\s*'+name+r'\([^\n]*\)\s*\{',src,re.M)
    assert m, 'Missing production function '+name
    pos=src.index('{',m.start()); n=1; end=pos+1
    while n:
        n+=(src[end]=='{')-(src[end]=='}'); end+=1
    return src[m.start():end]+'\n'
def original_payload(data):
    pic=(data/'tyrian.pic').read_bytes(); offsets=struct.unpack_from('<14I',pic,2)
    p,end=offsets[2:4]; pixels=bytearray()
    while len(pixels)<64000:
        assert p<end; v=pic[p]; p+=1; n=1
        if v&192==192: n=v&63; v=pic[p];p+=1
        pixels.extend(bytes([v])*n)
    assert len(pixels)==64000 and hashlib.sha256(pixels).hexdigest()=='83c5979f54de07f79e0c13970f242ae6f7435d4d396a168b340458c955c0e0f4'
    bank=(data/'palette.dat').read_bytes()[5*768:6*768]; assert len(bank)==768 and max(bank)<64
    rgb=bytes((v<<2)|(v>>4) for v in bank)
    out=bytes(pixels)+b''.join(struct.pack('<I',int.from_bytes(rgb[i:i+3],'big')) for i in range(0,768,3))
    src=(ROOT/'src/fonthand.c').read_text();body=re.search(r'const int font_ascii\[256\]\s*=\s*\{(.*?)\};',src,re.S).group(1)
    mapping=[int(x) for x in re.findall(r'-?\d+',re.sub(r'//[^\n]*','',body))];assert len(mapping)==256
    out+=struct.pack('<256i',*mapping)
    shp=(data/'tyrian.shp').read_bytes(); tables=struct.unpack_from('<H',shp)[0]; offsets=struct.unpack_from('<%dI'%tables,shp,2)
    for table in (2,5):
        p=offsets[table]; count=struct.unpack_from('<H',shp,p)[0];p+=2
        assert count<=152;out+=struct.pack('<H',count)
        for i in range(count):
            present=shp[p];p+=1
            if not present: out+=bytes(6);continue
            w,h,n=struct.unpack_from('<3H',shp,p);p+=6
            out+=struct.pack('<3H',w,h,n)+shp[p:p+n];p+=n
    return out

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--data',type=Path,required=True);ap.add_argument('--assets',type=Path,default=ROOT/'assets/hd/shared-ui-v1');ap.add_argument('--receipt',type=Path);ap.add_argument('--sanitize',action='store_true');ap.add_argument('--case',default='all');a=ap.parse_args()
    inputs=[ROOT/'src/render_mirror.c',ROOT/'src/gameplay_hud_font_mirror.inc',HERE/'shared_hud_reconstruction.c',HERE/'shared_hud_reconstruction.py']+[ROOT/'src'/(n+ext) for n in FAMILIES for ext in ('.c','.h')]
    snapshots={p:p.read_bytes() for p in inputs}
    src=snapshots[ROOT/'src/render_mirror.c'].decode()
    names=['asteroid1_level_scope','asteroid1_scope','normal15_scope','manual_hd_scope','mirror_enabled','render_mirror_owns_display','palette_rgb','upscale','render_mirror_unsupported','cloud_shadow_rgba','darken_rgba','indicator_cell','indicator_position','indicator_overlap']
    start=src.index('static bool fixed_text_owned(void)\n');end=src.index('void render_mirror_begin(void)',start)
    names+=re.findall(r'^(?:static )?(?:Uint32|unsigned(?: int)?|int|void|bool) (\w+)\([^\n]*\)\s*\{',src[start:end],re.M)
    names+=['render_mirror_begin','render_mirror_pixel','render_mirror_rect','normal15_disjoint','normal15_layout','normal15_palette','normal15_branch','normal15_index','normal15_channel','normal15_rgba','normal15_indices_match','normal15_compose','shared_hud_finish','render_mirror_finish','render_mirror_fade_start','render_mirror_fade_step','render_mirror_present','render_mirror_release_texture']
    names=list(dict.fromkeys(names))
    with tempfile.TemporaryDirectory(prefix='shared-hud-reconstruction-') as temp:
        temp=Path(temp)
        for p,content in snapshots.items():
            if p.suffix in ('.c','.h','.inc'):(temp/p.name).write_bytes(content)
        (temp/'production.inc').write_text('\n'.join(extract(src,n) for n in names))
        (temp/'shared_root.inc').write_text(extract(src,'hud_asset_directory')+extract(src,'shared_hud_requested'))
        for i,resource in enumerate(RESOURCES):
            for mode in ('missing','corrupt'):
                d=temp/f'{mode}{i}'; d.mkdir()
                for j,r in enumerate(RESOURCES):
                    if mode=='missing' and i==j:continue
                    if mode=='corrupt' and i==j:(d/r).write_bytes(b'corrupt, not original game data')
                    else:(d/r).symlink_to((a.assets/r).resolve())
        (temp/'empty').mkdir()
        cmd=[os.environ.get('CC','cc'),'-std=c99','-O1','-g','-Wall','-Wextra','-Wno-unused-parameter','-Wno-unused-variable','-Wno-unused-function','-Wno-misleading-indentation','-Werror=implicit-function-declaration','-I'+str(temp),'-I'+str(ROOT/'src')]
        if a.sanitize:cmd+=['-fsanitize=address,undefined','-fno-omit-frame-pointer','-no-pie']
        cmd+=[str(temp/'shared_hud_reconstruction.c')]+[str(temp/(n+'.c')) for n in FAMILIES]+['-o',str(temp/'oracle')]
        subprocess.run(cmd,check=True)
        result=subprocess.run([str(temp/'oracle'),str(a.assets),str(temp),a.case],input=original_payload(a.data),stdout=subprocess.PIPE,stderr=subprocess.PIPE,env={**os.environ,'ASAN_OPTIONS':'detect_leaks=0:halt_on_error=1','UBSAN_OPTIONS':'halt_on_error=1:print_stacktrace=1'})
        print(result.stdout.decode(),end='');print(result.stderr.decode(),end='')
        receipt={'status':'PASS' if result.returncode==0 else 'FAIL','sanitizers':'ASan+UBSan' if a.sanitize else 'none','leak_detection':'disabled: executor ptrace is incompatible with LeakSanitizer','case':a.case,'returncode':result.returncode,'stdout':result.stdout.decode(),'stderr':result.stderr.decode(),'original_bytes_persisted':False,'production_helpers':names,'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(content).hexdigest() for p,content in snapshots.items()},'source_unchanged_at_completion':all(p.read_bytes()==content for p,content in snapshots.items()),'resources':{r:hashlib.sha256((a.assets/r).read_bytes()).hexdigest() for r in RESOURCES}}
        if a.receipt:
            target=a.receipt.resolve();assert ROOT not in target.parents and a.data.resolve() not in target.parents;target.write_text(json.dumps(receipt,indent=2)+'\n')
        raise SystemExit(0 if result.returncode==0 else 1)
if __name__=='__main__':main()
