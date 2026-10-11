"""Prove that bounded binder oracles reject narrowly introduced test-only faults.

Mutations affect temporary extracted snippets only, never production source.
Run the binder oracle first and provide its JSON report to reuse synthetic input.
"""
from pathlib import Path
import argparse
import json
import os
import resource
import subprocess
import tempfile

HERE=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--binder-report',required=True,type=Path)
p.add_argument('--report',type=Path)
a=p.parse_args()
base=json.loads(a.binder_report.read_text());assert base['status']=='passed'
work=Path(base['work']);original=(work/'production-helpers.inc').read_text();loader=(work/'production-loader.inc').read_text()
mutations={
 'wrong-layer':('helpers','layer==3&&layer3_gray_slot(id)>=0','layer==4&&layer3_gray_slot(id)>=0'),
 'wrong-bank':('helpers',"terrain_file=='z'&&",'true&&'),
 'wrong-slot':('helpers','return 272+i;','return 271+i;'),
 'whitelist-widened':('helpers','141,142,143,144,151,152,153,154','141,142,143,144,151,152,153,126'),
 'shadow-not-guarded':('helpers','gray_slot>=0&&style!=MIRROR_NORMAL','gray_slot>=0&&style==MIRROR_BLEND'),
 'missing-art-traced':('helpers','||gray_slot>=0)&&!a',' )&&!a'),
 'map-reset-removed':('helpers','terrain_source_count=0;','terrain_source_count=terrain_source_count;'),
 'overflow-guard-one-too-late':('helpers','terrain_source_count<140','terrain_source_count<141'),
 'loader-hook-removed':('loader','render_mirror_bind_terrain(3,z+1,megaData3.shapes[x].sh);','(void)0;'),
}
results=[];root=Path(tempfile.mkdtemp(prefix='layer3-gray-mutations-'))
for name,(kind,old,new) in mutations.items():
 d=root/name;d.mkdir()
 for filename in ['production-types.inc','original-map.inc']:(d/filename).write_bytes((work/filename).read_bytes())
 text=original if kind=='helpers' else loader
 assert text.count(old)==1,(name,text.count(old))
 (d/'production-helpers.inc').write_text(original.replace(old,new) if kind=='helpers' else original)
 (d/'production-loader.inc').write_text(loader.replace(old,new) if kind=='loader' else loader)
 cmd=[os.environ.get('CC','cc'),'-std=c99','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-I'+str(d),str(HERE/'test-layer3-gray-binder.c'),'-o',str(d/'test')]
 build=subprocess.run(cmd,text=True,capture_output=True);assert build.returncode==0,(name,build.stderr)
 run=subprocess.run([str(d/'test'),str(work)],text=True,capture_output=True,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1'),preexec_fn=lambda:resource.setrlimit(resource.RLIMIT_CORE,(0,0)))
 assert run.returncode!=0, name+' escaped independent oracle'
 (d/'result.log').write_text(run.stdout+run.stderr)
 results.append({'mutation':name,'exit_code':run.returncode,'rejected':True,'first_diagnostic':run.stderr.splitlines()[0] if run.stderr else ''})
 print('REJECTED:',name)
report={'status':'passed','mutants_rejected':len(results),'work':str(root),'results':results,'scope':'Only temporary extracted snippets mutated; candidate source and test inputs unchanged.'}
out=a.report or root/'result.json';out.write_text(json.dumps(report,indent=2)+'\n');print('Report:',out)
