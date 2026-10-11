"""Extract the production finite binder and loader and test their actual C99 code."""
from pathlib import Path
import argparse,re,subprocess,tempfile,os,json,hashlib
TOOLS=Path(__file__).resolve().parent;ROOT=TOOLS.parents[1]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,default=ROOT);p.add_argument('--sanitize',action='store_true');p.add_argument('--report',type=Path);a=p.parse_args();source=(a.source/'src/render_mirror.c').read_text()
def extract(name):
 match=re.search(r'^.*\b'+name+r'\([^\n]*\)\s*\{',source,re.M);assert match,name
 start=source.index('{',match.start());depth=1;end=start+1
 while depth:depth+=(source[end]=='{')-(source[end]=='}');end+=1
 return source[match.start():end]+'\n'
types=re.search(r'typedef struct \{\s*bool initialized,valid;.*?\} Asset;',source,re.S).group()
arrays='\n'.join(re.search(p,source).group() for p in [r'static Asset assets\[\d+\];',r'static struct \{const Uint8 \*data;unsigned int id;\} terrain_sources\[\d+\];'])
funcs='\n'.join(extract(n) for n in ['read_asset','scene_asset','render_mirror_map_begin','cloud_terrain_slot','ground_terrain_slot','plateau_terrain_slot','underlay_terrain_slot','road_terrain_slot','terrain_holes_slot','stone_foundation_slot','render_mirror_bind_terrain','render_mirror_terrain_row'])
with tempfile.TemporaryDirectory(prefix='plateau-four-binder-') as tmp:
 d=Path(tmp);(d/'production-types.inc').write_text(types+'\n'+arrays+'\n');(d/'production-helpers.inc').write_text(funcs)
 command=['cc','-std=c99','-O1','-g','-Wall','-Wextra','-Werror','-I'+str(d),str(Path(__file__).with_suffix('.c')),'-o',str(d/'test')]
 if a.sanitize:command+=['-fsanitize=address,undefined','-fno-omit-frame-pointer']
 subprocess.run(command,check=True);env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
 result=subprocess.run([str(d/'test')],cwd=d,env=env,text=True,capture_output=True);print(result.stdout);print(result.stderr,end='');result.check_returncode()
 report={'status':'passed','sanitize':a.sanitize,'source':str(a.source.resolve()),'renderer_sha256':hashlib.sha256(source.encode()).hexdigest(),'command':command,'result':result.stdout,'stderr':result.stderr,'leak_sanitizer':'Disabled because runtime uses ptrace; ASan address checks and UBSan remain enabled.'}
 out=a.report or Path(tempfile.mkdtemp(prefix='plateau-binder-report-'))/'result.json';out.write_text(json.dumps(report,indent=2)+'\n')
