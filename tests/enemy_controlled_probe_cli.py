#!/usr/bin/env python3
"""Bounded real-binary CLI rejection and pause/step/revocation checks.
Hit/destroy cases are explicitly negative synthetic controls, never positives.
"""
import argparse,csv,hashlib,json,os,subprocess
from pathlib import Path
p=argparse.ArgumentParser();
for key in ('binary','data','assets','out'):p.add_argument('--'+key,type=Path,required=True)
a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
flag='--render-enemy-reuse-session=original-events-v1'
base=[str(a.binary),'--data='+str(a.data),'--asset-debug=custom','--asset-debug-episode=3','--asset-debug-level=1','--asset-debug-tick=239','--render-test=8','--render-assets='+str(a.assets),'--render-ticks=280','--render-no-capture','--render-scene=v1','--render-front-port=36','--render-front-power=11','--render-rear-port=37','--render-rear-power=11','--render-rear-mode=1',flag]
checks=[]
def run(name,args,control=None,want=2):
 d=a.out/name;d.mkdir(exist_ok=True);cmd=list(args)
 if control is not None:(d/'control.txt').write_text(control);cmd+=['--asset-debug-control='+str(d/'control.txt')]
 env={**os.environ,'SDL_VIDEODRIVER':'dummy','SDL_AUDIODRIVER':'dummy','SDL_RENDER_DRIVER':'software','XDG_CONFIG_HOME':str(d/'config')}
 with (d/'run.log').open('w') as f:r=subprocess.run(cmd,cwd=d,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=30)
 ok=r.returncode==want
 log=(d/'run.log').read_text()
 if control is None:ok=ok and 'Enemy reuse controlled probe: generation=' not in log
 if name.startswith('record-conflict-'):ok=ok and 'rejects pre-existing demo/record mode' in log
 record={'name':name,'command':cmd,'returncode':r.returncode,'expected':want,'pass':ok,'synthetic_negative_control':bool(control and ('hit ' in control or 'destroy ' in control))}
 if control is not None and want in (0,75):
  rows=lambda n:list(csv.DictReader((d/n).open(),delimiter='\t')) if (d/n).exists() else []
  draws=rows('scene-draw-commands.tsv');present=rows('presentation.tsv');log=(d/'run.log').read_text()
  record['accepted_ticks']=sorted({int(x['tick']) for x in draws if x['role']=='146' and x['mirrored']=='1'})
  record['present_ticks']=[int(x['tick']) for x in present];record['revocation_logged']='revoke generation=' in log
  ok=ok and record['revocation_logged'] and 239 in record['accepted_ticks'] and 239 in record['present_ticks']
  if name in ('hit-revokes','destroy-revokes'):
   ok=ok and all(t==239 for t in record['accepted_ticks']) and all(t==239 for t in record['present_ticks'])
  record['pass']=ok
 checks.append(record);(a.out/'receipt.json').write_text(json.dumps({'binary_sha256':hashlib.sha256(a.binary.read_bytes()).hexdigest(),'checks':checks},indent=2));print(name,ok,flush=True)
 assert ok,(name,record,(d/'run.log').read_text()[-3000:])
def replace(prefix,new):return [new if x.startswith(prefix) else x for x in base]
for record_flag in ('--record','-r','RECORD'):
 run('record-conflict-'+record_flag.lstrip('-'),base+[record_flag])
run('unknown-contract',replace('--render-enemy-reuse-session=','--render-enemy-reuse-session=unknown'))
run('duplicate-contract',base+[flag])
run('no-probe',[str(a.binary),flag])
run('no-asset-debug',[x for x in base if not x.startswith('--asset-debug')])
run('missing-original-data',replace('--data=','--data=/does-not-exist'),want=1)
run('missing-assets',replace('--render-assets=','--render-assets=/does-not-exist'))
run('unknown-profile',replace('--render-scene=','--render-scene=unknown'))
run('banking-profile',replace('--render-scene=','--render-scene=banking'))
run('unapproved-loadout',replace('--render-front-port=','--render-front-port=1'))
run('density4',replace('--render-test=','--render-test=4'))
run('repeat-mode',replace('--render-test=','--render-test=repeat'))
run('normal-observer-conflict',base+['--enemy-reuse-observe-assets='+str(a.assets)])
run('unapproved-level',replace('--asset-debug-level=','--asset-debug-level=2'))
run('pause-step-resume',base,'pause\nstep\nstep\nresume\nquit\n',0)
run('quit-revokes',base,'quit\n',0)
run('reload-revokes',base,'reload\n',75)
run('hit-revokes',base,'hit 0\nresume\nquit\n',0)
run('destroy-revokes',base,'destroy 0\nresume\nquit\n',0)
