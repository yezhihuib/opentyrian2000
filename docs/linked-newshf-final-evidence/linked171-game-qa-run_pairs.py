"""Natural original E1 physical12 linked family; no injected state or edited banks."""
from pathlib import Path
import subprocess,os,json,hashlib,csv
q=Path(__file__).resolve().parent;b=q.parent;r=b/'linked171-native-final/hd-on-build'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
results=[]
for scale in (4,8):
 for variant in ('present','missing','reference'):
  out=q/'runs'/f'{scale}x-{variant}';out.mkdir(parents=True,exist_ok=False)
  pack=q/('pack-missing' if variant=='missing' else 'pack')
  exe=r/'opentyrian2000'
  env=os.environ.copy();env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',SDL_RENDER_DRIVER='software',LD_LIBRARY_PATH=str(b/'dependencies/sysroot/usr/lib/x86_64-linux-gnu'),HOME=str(out),XDG_CONFIG_HOME=str(out/'config'))
  argv=[str(exe),f'--data={b}/dependencies/data','--no-sound','--no-joystick','--no-xmas','--asset-debug=custom','--asset-debug-episode=1','--asset-debug-level=12','--asset-debug-tick=106','--asset-debug-running',f'--render-test={scale}','--render-ticks=181',f'--render-assets={pack}',f'--global-assets={pack}','--asset-debug-capture','--asset-debug-capture-start=106','--asset-debug-capture-count=75','--asset-debug-window-only']
  if variant=='reference':argv.append('--render-original-reference')
  with (out/'stdout.log').open('w') as f,(out/'stderr.log').open('w') as e:z=subprocess.run(argv,cwd=out,env=env,stdout=f,stderr=e,timeout=240)
  item=dict(scale=scale,variant=variant,argv=argv,exit=z.returncode,binary_sha256=sha(exe),captures={p.name:sha(p) for p in out.glob('*.bmp')});results.append(item)
  (q/'runs.json').write_text(json.dumps(results,indent=2)+'\n');print(scale,variant,z.returncode,len(item['captures']),flush=True)
  assert z.returncode==0 and len(item['captures'])==75
for scale in (4,8):
 base=q/'runs'/f'{scale}x-missing'
 for variant in ('present','reference'):
  p=q/'runs'/f'{scale}x-{variant}'
  a=list(csv.DictReader((base/'state.tsv').open(),delimiter='\t'));c=list(csv.DictReader((p/'state.tsv').open(),delimiter='\t'))
  assert len(a)==len(c)
  assert all(all(x[k]==y[k] for k in x if k!='output_pixels') for x,y in zip(a,c))
  for name in ('enemy-projectiles.tsv','collisions.tsv','player-projectiles.tsv','player-shot-emissions.tsv'):
   assert (p/name).read_bytes()==(base/name).read_bytes(),(scale,variant,name)
print('natural state/RNG/projectile/collision equivalence PASS')
