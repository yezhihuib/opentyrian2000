#!/usr/bin/env python3
"""Private exact-pin Load coexistence adapter for historical source-only guards.
Production/historical files are never edited. Actual module runtime tests compile
current source separately. Type3 helpers compile current render_mirror.c; only
the original indexed sprite recorder drops proven-dormant Load observer calls.
"""
from pathlib import Path
import base64,difflib,hashlib,json,runpy,subprocess,sys
root=Path(__file__).resolve().parent.parent/'load-font-implementation-20261013';sys.path.insert(0,str(root/'prototype'))
import settings_font_coexistence as legacy
sha=lambda b:hashlib.sha256(b).hexdigest()
base='a4974da93ee75fb18c7ad5827ea42a6b02d1b74d';pins=json.loads((root/'docs/load-font-source-pins.json').read_text());records={}
for name,pin in pins.items():
 raw=(root/name).read_bytes();assert sha(raw)==pin
 try:old=subprocess.check_output(['git','-C',str(root),'show',base+':'+name],stderr=subprocess.DEVNULL)
 except subprocess.CalledProcessError:continue
 if raw==old:continue
 edits=[];before=raw.splitlines(keepends=True);after=old.splitlines(keepends=True)
 for op,a,b,c,d in difflib.SequenceMatcher(a=before,b=after,autojunk=False).get_opcodes():
  if op!='equal':edits.append((a,b,base64.b64encode(b''.join(after[c:d])).decode()))
 records[name]={'current':pin,'previous':sha(old),'reverse_line_edits':edits}
def project_load(name,raw):
 pin=records.get(name)
 if pin is None:return raw
 if sha(raw)==pin['previous']:return raw
 assert sha(raw)==pin['current'],('unreviewed whole file',name)
 lines=raw.splitlines(keepends=True)
 for a,b,data in reversed(pin['reverse_line_edits']):lines[a:b]=base64.b64decode(data).splitlines(keepends=True)
 result=b''.join(lines);assert sha(result)==pin['previous'];return result
negatives=0
for name,pin in records.items():
 raw=(root/name).read_bytes();project_load(name,raw)
 for i in {0,len(raw)//2,len(raw)-1}:
  try:project_load(name,raw[:i]+bytes([raw[i]^1])+raw[i+1:])
  except AssertionError:negatives+=1
  else:raise AssertionError('accepted mutation')
original_project=legacy.project_settings_source
legacy.project_settings_source=lambda name,raw:original_project(name,project_load(name,raw))
def verify(root):
 for name,pin in legacy.PINS.items():
  raw=project_load(name,(root/name).read_bytes());assert sha(raw)==pin['current'],name;original_project(name,raw)
 for name,pin in legacy.ADDITIONS.items():assert sha(project_load(name,(root/name).read_bytes()))==pin,name
 return len(legacy.PINS),len(legacy.ADDITIONS)
legacy.verify_settings_sources=verify
verify(root)
path=root/sys.argv[1];sys.argv=sys.argv[1:];sys.argv[0]=str(path)
source=path.read_text()
if path.name=='test-type3-small-binding.py':
 old="original = (repo / 'src/sprite.c').read_text()";new="original = project_settings_source('src/sprite.c', (repo / 'src/sprite.c').read_bytes()).decode()";assert source.count(old)==1;source=source.replace(old,new)
report={'result':'PASS','source':str(root),'projection_base':base,'exact_changed_files':records,'mutation_rejections':negatives,'historical_files_modified':False,'runtime_test_target':'Current production type3 render helpers; original indexed recorder projection separately pinned and proven token-equal by tests/test_load_font_integration.py','test':str(path),'test_sha256':sha(path.read_bytes())}
(Path(__file__).parent/(path.stem+'-projection.json')).write_text(json.dumps(report,indent=2)+'\n')
exec(compile(source,str(path),'exec'),{'__file__':str(path),'__name__':'__main__'})
