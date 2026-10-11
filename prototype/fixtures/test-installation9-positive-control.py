"""Run the unmutated native8 pass used by the faster entity mutation negatives."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,tempfile
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--work',required=True,type=Path);p.add_argument('--report',type=Path,default=None);a=p.parse_args()
w=a.work;d=Path(tempfile.mkdtemp(prefix='installation9-negative-control-'))
for name in ['types.inc','functions.inc','wrapper.inc','blitters.inc']:(d/name).write_bytes((w/name).read_bytes())
s=(w/'test-installation9.c').read_text();old='for(int mode=0;mode<3;mode++)';assert s.count(old)==1;s=s.replace(old,'for(int mode=1;mode<2;mode++)');(d/'control.c').write_text(s)
cmd=['cc','-std=c99','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer',str(d/'control.c'),'-o',str(d/'control')]
b=subprocess.run(cmd,capture_output=True,text=True);assert b.returncode==0,b.stderr
q=subprocess.run([str(d/'control'),str(w/'packs')],capture_output=True,text=True,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1'))
print(q.stdout+q.stderr);result={'status':'passed'if q.returncode==0 else'failed','work':str(d),'command':cmd,'exit_code':q.returncode,'stdout':q.stdout,'stderr':q.stderr,'scope':'Unmutated native8 subset independently passes before accepting mutant failures.'};out=a.report or d/'control.json';out.write_text(json.dumps(result,indent=2)+'\n');assert q.returncode==0
