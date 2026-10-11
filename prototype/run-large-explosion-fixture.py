"""Two existing original-event fixtures, finite through an observed stable tail.

No artificial explosion spawns, pointer jumps, gameplay edits, downloads or cleanup.
The documented artificial Pulse155 shot passes through the original collision path.
"""
from pathlib import Path
import argparse,csv,hashlib,json,os,subprocess,time

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p):return list(csv.DictReader(p.open(encoding='utf-8'),delimiter='\t'))

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--repo',type=Path,default=Path(__file__).resolve().parent.parent)
p.add_argument('--output',type=Path,required=True,help='New output directory; never overwrites or removes an old run')
p.add_argument('--case',choices=['ground','air','both'],default='both',help='Enemy scene labels: ground=turret type124 uses large-air; air=type10 uses large-ground. Original enemyGround flag is authoritative.')
p.add_argument('--exe',type=Path,help='Explicit previous checkpoint executable for unchanged before baseline')
p.add_argument('--before',action='store_true',help='Previous executable: do not send newly added capture/log flags')
p.add_argument('--capture',choices=['none','tail','full'],default='tail',help='Default 4 native windows per fixture; full is bounded to 83/45 windows')
a=p.parse_args();repo=a.repo.resolve();root=repo.parent
out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
exe=(a.exe or repo/'opentyrian-x64-Release.exe').resolve()
pack=root/'runtime-hd-assets/packed-blue-four-foundation-type10-explosion-v2-test'
data=root/'runtime-data/tyrian2000'
for x in [exe,pack,data]:assert x.exists(),x
if a.before:assert a.capture=='none','Before baseline must use --capture none'
fixtures=[('ground','turret',232,315,28,124),('air','type10',150,195,1,10)]
if a.case!='both':fixtures=[f for f in fixtures if f[0]==a.case]
pack_sha={f.name:sha(f) for f in pack.glob('*.hda')}
records=[]
for name,preset,target,until,slot,enemy_type in fixtures:
 run=out/name;run.mkdir();control=run/'control.txt';control.write_text('',encoding='utf-8')
 cfg="section 'video'\n    item 'fullscreen' '-1'\n    item 'scaler' '4x'\n    item 'scaling_mode' 'Integer'\n"
 (run/'opentyrian.cfg').write_text(cfg,encoding='utf-8')
 argv=[str(exe),'--data='+str(data),'--no-sound','--no-joystick','--no-xmas','--asset-debug='+preset,'--asset-debug-tick='+str(target),'--render-ticks='+str(until),'--render-assets='+str(pack),'--asset-debug-control='+str(control),'--render-test=local']
 capture_start=None;capture_count=0
 if not a.before:
  argv.append('--asset-debug-explosion-log')
  if a.capture!='none':
   capture_start=until-4 if a.capture=='tail' else target;capture_count=4 if a.capture=='tail' else until-target
   argv+=['--asset-debug-capture','--asset-debug-window-only','--asset-debug-capture-start='+str(capture_start),'--asset-debug-capture-count='+str(capture_count)]
 env=dict(os.environ)
 for k in ['SDL_VIDEODRIVER','SDL_AUDIODRIVER','SDL_RENDER_DRIVER']:env.pop(k,None)
 with (run/'stdout.log').open('w',encoding='utf-8') as stdout,(run/'stderr.log').open('w',encoding='utf-8') as stderr:
  process=subprocess.Popen(argv,cwd=run,env=env,stdout=stdout,stderr=stderr)
  def wait_for(text):
   start=time.monotonic()
   while not ((run/'asset-debug-control.tsv').exists() and text in (run/'asset-debug-control.tsv').read_text(encoding='utf-8')):
    assert process.poll() is None,(name,'early exit',(run/'stderr.log').read_text(encoding='utf-8'))
    assert time.monotonic()-start<20,(name,'pause timeout');time.sleep(.02)
  try:
   wait_for('target-frame-complete')
   with control.open('a',encoding='utf-8') as f:f.write(f'destroy {slot}\n')
   wait_for('step-complete');commands=(run/'asset-debug-control.tsv').read_text(encoding='utf-8')
   assert 'rejected-' not in commands,commands
   assert f'enemy{slot} type{enemy_type} ' in commands,commands
   with control.open('a',encoding='utf-8') as f:f.write('resume\n')
   assert process.wait(timeout=40)==0,(run/'stderr.log').read_text(encoding='utf-8')
  finally:
   if process.poll() is None:process.kill();process.wait()
 assert len(rows(run/'state.tsv'))==until
 assert (run/'opentyrian.cfg').read_text(encoding='utf-8')==cfg and not (run/'tyrian.sav').exists()
 captures=list(run.glob('asset-debug-window-*.bmp'))
 assert len(captures)==capture_count,(name,len(captures),capture_count)
 assert not list(run.glob('display-*.bmp')) and not list(run.glob('classic-*.bmp'))
 if not a.before:
  pools=rows(run/'asset-debug-explosion-pools.tsv');assert len(pools)==until
  assert all(x['active_explosions']=='0' and x['active_repeaters']=='0' for x in pools[-4:]),(name,'not clear at tail',pools[-4:])
 record={'case':name,'actual_large_assembly':'large-air' if name=='ground' else 'large-ground','run':str(run),'argv':argv,'exe_sha256':sha(exe),'target':target,'destroy_tick':target+1,'enemy_slot':slot,'enemy_type':enemy_type,'until_exclusive':until,'capture_start':capture_start,'capture_count':capture_count,'capture_native_window_only':not a.before,'explicit_artificial_original_collision_shot':True,'renderer_sha256':sha(repo/'src/render_mirror.c'),'unchanged_pack_sha256':pack_sha,'existing_fixture':True}
 (run/'case.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8');records.append(record)
 (out/'cases.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')
 print(f'DONE {name}: tick0..{until-1}, original destroy{slot}@{target+1}, {len(captures)} native captures',flush=True)
assert pack_sha=={f.name:sha(f) for f in pack.glob('*.hda')},'Original runtime pack changed'
