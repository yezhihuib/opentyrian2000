"""Actual engine, original data/events; only optional91 transport differs. No injected state."""
from pathlib import Path
import subprocess,os,csv,json,hashlib,time,shutil
q=Path(__file__).resolve().parent;b=q.parent;r=b/'repository'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
name='enemy-projectile91-91-8.hda'
for variant in ('missing','corrupt'):
 pack=q/f'pack-{variant}';pack.mkdir(exist_ok=True)
 for p in (q/'pack').iterdir():
  if p.name!=name and not (pack/p.name).exists():(pack/p.name).symlink_to(p.resolve())
 if variant=='corrupt':
  raw=bytearray((q/'pack'/name).read_bytes());raw[-1]^=1;(pack/name).write_bytes(raw)
results=[]
for ep,lev,tick,consumer in [(1,12,70,173),(5,5,830,285)]:
 for variant in ('present','missing','corrupt','public-baseline','reference'):
  out=q/'final-runs'/f'{consumer}-{variant}';out.mkdir(parents=True,exist_ok=False)
  pack=q/('pack' if variant in ('present','public-baseline','reference') else f'pack-{variant}')
  exe=q/('baseline' if variant=='public-baseline' else 'candidate')/'opentyrian2000'
  env=os.environ.copy();env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',SDL_RENDER_DRIVER='software',LD_LIBRARY_PATH=str(b/'dependencies/sysroot/usr/lib/x86_64-linux-gnu'),HOME=str(out),XDG_CONFIG_HOME=str(out/'config'))
  argv=[str(exe),f'--data={b}/dependencies/data','--no-sound','--no-joystick','--no-xmas','--asset-debug=custom',f'--asset-debug-episode={ep}',f'--asset-debug-level={lev}',f'--asset-debug-tick={tick}','--asset-debug-running','--render-test=8',f'--render-ticks={tick+8}',f'--render-assets={pack}',f'--global-assets={pack}','--asset-debug-capture',f'--asset-debug-capture-start={tick}','--asset-debug-capture-count=8','--asset-debug-window-only']
  if variant=='reference':argv.append('--render-original-reference')
  start=time.time()
  with (out/'stdout.log').open('w') as f,(out/'stderr.log').open('w') as e:z=subprocess.run(argv,cwd=out,env=env,stdout=f,stderr=e,timeout=120)
  item=dict(consumer=consumer,variant=variant,argv=argv,exit=z.returncode,binary_sha256=sha(exe),duration=time.time()-start,captures={p.name:sha(p) for p in out.glob('*.bmp')});results.append(item)
  (q/'runs.json').write_text(json.dumps(results,indent=2)+'\n');print(consumer,variant,z.returncode,len(item['captures']),flush=True)
  assert z.returncode==0 and len(item['captures'])==8
