#!/usr/bin/env python3
"""Fresh HUM2 source rebuild, exact payload and narrow path/manifest guards."""
from pathlib import Path
import os,sys,tempfile,subprocess,hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'prototype'))
from gameplay_hud_meter_bundle import build_bundle,FILENAME,SOURCE,SOURCE_FILES
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def call(script,out,cwd,ok=True):
 r=subprocess.run([sys.executable,str(script),'--output',str(out)],cwd=cwd,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),capture_output=True,text=True)
 assert(r.returncode==0)==ok,(script,out,r.stdout,r.stderr)
source=ROOT/SOURCE;before={n:sha(source/n)for n in SOURCE_FILES};raw,receipt=build_bundle(ROOT)
with tempfile.TemporaryDirectory(prefix='hum-package-')as tmp:
 d=Path(tmp);cwd=d/'foreign working directory';cwd.mkdir();out=d/'fresh output with spaces'
 wrapper=ROOT/'prototype/build-gameplay-hud-meters.py';call(wrapper,out,cwd)
 assert(out/FILENAME).read_bytes()==raw
 assert(out/'meter-scope-1390.mask').read_bytes()==(source/'canonical/meter-scope-1390.mask').read_bytes()
 for bad in [out,ROOT,ROOT/'must-not-create-hum-output',ROOT.parent]:call(wrapper,bad,cwd,False)
 assert not(ROOT/'must-not-create-hum-output').exists()
 dest=d/'real destination';dest.mkdir();link=d/'linked destination';link.symlink_to(dest,target_is_directory=True);call(wrapper,link/'new',cwd,False)
 # Rebuild using source-only input. Canonical payload and previous output are absent.
 relocated=d/'relocated sources';relocated.mkdir()
 for n in ['build_resource.py','materials.py','selected-rgb.json','requirements.txt','contract.json']:
  shutil.copyfile(source/n,relocated/n)
 newout=d/'relocated output';call(relocated/'build_resource.py',newout,cwd)
 assert(newout/FILENAME).read_bytes()==raw
 assert(newout/'meter-scope-1390.mask').read_bytes()==(source/'canonical/meter-scope-1390.mask').read_bytes()
 for bad in [newout,relocated,relocated/'nested',link/'other']:
  call(relocated/'build_resource.py',bad,cwd,False)
 # Independent temporary manifest/source directory; never mutate published inputs.
 fake=d/'test repo';target=fake/SOURCE;shutil.copytree(source,target)
 m=json.loads((ROOT/'assets/hd/manifest.json').read_text());(fake/'assets/hd/manifest.json').write_text(json.dumps(m))
 assert build_bundle(fake)[0]==raw
 hp=target/'canonical'/FILENAME;original=hp.read_bytes();mut=bytearray(original);mut[-1]^=1;hp.write_bytes(mut)
 try:build_bundle(fake);raise RuntimeError('corrupt accepted')
 except AssertionError:pass
 hp.write_bytes(original)
 (target/'unexpected.txt').write_text('extra')
 try:build_bundle(fake);raise RuntimeError('extra accepted')
 except AssertionError:pass
assert before=={n:sha(source/n)for n in SOURCE_FILES}
print(json.dumps({'status':'PASS','resource':receipt,'fresh_and_relocated_exact':True,'wrapper_path_rejections':5,'standalone_path_rejections':4,'corrupt_extra_rejections':2,'formal_source_files':13}))
