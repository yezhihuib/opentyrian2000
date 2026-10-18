#!/usr/bin/env python3
"""Run finite actual-shadow preparation guards, strict C99 and ASan/UBSan.
Usage: SCRIPT synthetic-adapter-fixture NEW-output-directory
Prepare synthetic inputs with run_rear_multi_p1_adapter_tests.py first.
No SDL installation, authentic game data, or original artwork is required.
"""
from pathlib import Path
import hashlib,json,os,re,subprocess,sys
root=Path(__file__).resolve().parents[1]
if len(sys.argv)!=3:raise SystemExit(__doc__)
fixture,out=map(lambda s:Path(s).resolve(),sys.argv[1:]);out.mkdir(parents=True,exist_ok=False)
receipt=json.loads((fixture/'fixture_receipt.json').read_text());assert receipt['generated_only'] and not receipt['original_inputs']
source=(root/'src/render_mirror.c').read_text();match=re.search(r'typedef struct \{\n bool live,entered,rear;.*?\} VulcanShadowCall;',source,re.S);assert match
(out/'shadow_types.inc').write_text(match[0]+'\n')
results=[]
for mode in ('plain','sanitize'):
 exe=out/('shadow-'+mode);cmd=['cc','-std=c99','-pedantic','-Wall','-Wextra','-Werror','-O1','-g','-I'+str(root/'src'),'-I'+str(fixture),'-I'+str(out),str(root/'tests/rear_multi_p11_shadow_test.c'),str(root/'src/rear_multi_p1.c'),'-lm','-o',str(exe)]
 if mode=='sanitize':cmd+=['-fsanitize=address,undefined','-fno-omit-frame-pointer']
 subprocess.run(cmd,check=True)
 r=subprocess.run([str(exe),str(fixture)],capture_output=True,text=True,timeout=120,env={**os.environ,'ASAN_OPTIONS':'detect_leaks=0:halt_on_error=1','UBSAN_OPTIONS':'halt_on_error=1'});(out/(mode+'.log')).write_text(r.stdout+r.stderr);print(mode,r.stdout,end='');print(r.stderr,end='',file=sys.stderr);r.check_returncode();results.append(mode)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(out/'receipt.json').write_text(json.dumps({'status':'PASS','synthetic_inputs_only':True,'scope':'Actual preparation and epoch guards; no compositor/gameplay-runtime claim','modes':results,'source_sha256':{n:sha(root/n) for n in ['src/rear_multi_p11_shadow.inc','src/render_mirror.c','src/rear_multi_p1.c','src/rear_multi_p1_mirror.inc','tests/rear_multi_p11_shadow_test.c']}},indent=2)+'\n')
