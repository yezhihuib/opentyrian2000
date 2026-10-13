#!/usr/bin/env python3
"""Mutation sensitivity for the compact extracted coin25 unit oracle. No game."""
import argparse,json,os,subprocess,tempfile
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--units',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();units=a.units.resolve();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);root=Path(__file__).resolve().parents[1];m=json.loads((root/'assets/hd/manifest.json').read_text());pack=root/'assets/hd/packs'/m['default_preview_pack'];functions=(units/'functions.inc').read_text();wrapper=(units/'wrapper.inc').read_text()
mutations=[
 ('body-wrong-bank','functions.inc','bank.data!=spriteSheet11.data','bank.data!=spriteSheet8.data'),
 ('body-wrong-slot','functions.inc','&assets[472+(int)base-7]','&assets[473+(int)base-7]'),
 ('body-no-record-gate','functions.inc','||context->type!=391',''),
 ('value-nonfixed-admitted','functions.inc','if(fixed_value&&bank.data&&','if(bank.data&&'),
 ('value-context-leaks','functions.inc','bool fixed_value=cash25_fixed_value;cash25_fixed_value=false;','bool fixed_value=cash25_fixed_value;'),
 ('alpha-forced-opaque','functions.inc','talon_blend?(src[3]+1)/2:src[3]','talon_blend?(src[3]+1)/2:255'),
 ('blend-no-value-average','functions.inc','unsigned int next=(source_peak+destination_peak+1)/2;','unsigned int next=source_peak;'),
 ('family-allows-missing','functions.inc','if(!a->valid)cash25_valid=false;','if(!a->valid)cash25_valid=true;'),
 ('skip-original-after-hd','wrapper.inc','if (layout == ENTITY_QUAD)','if (mirrored) {render_mirror_entity_end();return;}\n\tif (layout == ENTITY_QUAD)'),
]
results=[]
with tempfile.TemporaryDirectory(prefix='coin25-mutation-pack-') as tmp:
 missing=Path(tmp)
 for f in pack.glob('coin25-*.hda'):
  if 'value-' not in f.name:(missing/f.name).write_bytes(f.read_bytes())
 for label,target,old,new in mutations:
  d=out/label;d.mkdir()
  for n in ['types.inc','functions.inc','blitters.inc','wrapper.inc']:
   text=(units/n).read_text()
   if n==target:assert text.count(old)==1,(label,old);text=text.replace(old,new)
   (d/n).write_text(text)
  cmd=[os.environ.get('CC','cc'),'-std=c99','-O1','-g','-Wall','-Wextra','-Wno-unused-function','-Wno-unused-variable','-Wno-misleading-indentation','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','-I'+str(d),str(root/'prototype/test-cash25-seven.c'),'-o',str(d/'test')]
  r=subprocess.run(cmd,capture_output=True,text=True);(d/'compile.log').write_text(r.stdout+r.stderr);r.check_returncode()
  mode='loader' if label=='family-allows-missing' else 'render';chosen=missing if mode=='loader' else pack
  r=subprocess.run([str(d/'test'),mode,str(chosen),'0' if mode=='loader' else '1',str(units)],capture_output=True,text=True,timeout=120,env=dict(os.environ,ASAN_OPTIONS='detect_leaks=0:halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1'))
  assert r.returncode!=0 and ('FAIL line' in r.stderr or 'Sanitizer' in r.stderr),(label,r.returncode,r.stdout,r.stderr)
  (d/'result.log').write_text(r.stdout+r.stderr);results.append({'mutation':label,'status':'KILLED','returncode':r.returncode,'diagnostic':r.stderr[:1000]});print('KILLED',label,flush=True)
(out/'result.json').write_text(json.dumps({'status':'PASS','game_runs':0,'mutations':results},indent=2)+'\n')
