"""Bounded actual JE_main runs using local data and isolated config directories."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from launcher_paths import dependency
import argparse,csv,hashlib,json,os,subprocess,time
p=argparse.ArgumentParser();p.add_argument('--modes',default='classic,classic-again,4,8,missing,invalid,repeat');p.add_argument('--ticks',type=int,default=600);p.add_argument('--exe');p.add_argument('--assets');p.add_argument('--data',help='Original data directory; default: ../runtime-data/tyrian2000');p.add_argument('--local-blend',action='store_true');p.add_argument('--scene',choices=['v1','enemy-hit','fade-cycle','banking'],default='v1');p.add_argument('--prefix');p.add_argument('--scene-assets',choices=['off','enemy','terrain','all'],default='off');p.add_argument('--original-reference',action='store_true');p.add_argument('--known-explosion-blend',action='store_true');p.add_argument('--capture-blend',action='store_true');p.add_argument('--native-window',action='store_true');p.add_argument('--legacy-exe',action='store_true');p.add_argument('--allow-natural-end',action='store_true');p.add_argument('--png-captures',action='store_true');p.add_argument('--talon-bank',choices=['5','13'],default='13');a=p.parse_args()
repo=Path(__file__).resolve().parent.parent; task=repo.parent
exe=dependency(p,a.exe,repo/'opentyrian-x64-Release.exe','exe')
data=dependency(p,a.data,task/'runtime-data/tyrian2000','data')
if a.assets:a.assets=dependency(p,a.assets,None,'assets')

def compress_finished_captures(out,records,finished=False):
 """Store lossless PNG proofs; permanently delete redundant BMPs after the run finishes."""
 from PIL import Image
 out=Path(os.path.abspath(out)).resolve()
 if not out.is_relative_to(Path(os.path.abspath(task/'controlled-runs')).resolve()):
  raise RuntimeError('Capture outside controlled-runs')
 completed={r['file'] for r in records}
 last=-1
 if not finished and (out/'state.tsv').exists():
  lines=(out/'state.tsv').read_bytes().splitlines(keepends=True)
  for line in reversed(lines[1:]):
   if line.endswith(b'\n'):
    try:last=int(line.split(b'\t',1)[0]);break
    except ValueError:continue
 for path in sorted(out.glob('*.bmp')):
  if path.with_suffix('.png').name in completed:continue
  if path.name.startswith(('display-','classic-','window-','backdrop-')):
   tick=int(path.stem.split('-')[1])
   if not finished and tick>=last:continue
  elif path.name.startswith('fade-'):
   if not finished:continue
  else:raise RuntimeError('Unknown capture name: '+path.name)
  with path.open('rb') as f:head=f.read(14)
  if len(head)<14 or head[:2]!=b'BM' or int.from_bytes(head[2:6],'little')!=path.stat().st_size:
   if not finished:continue
   raise RuntimeError('Incomplete screenshot: '+path.name)
  try:
   with Image.open(path) as source:source.load();im=source.copy()
  except OSError:
   if not finished:continue
   raise
  raw=im.tobytes();dest=path.with_suffix('.png');temporary=dest.with_suffix('.png.partial')
  im.save(temporary,format='PNG',compress_level=1)
  with Image.open(temporary) as restored:
   if restored.mode!=im.mode or restored.size!=im.size or restored.tobytes()!=raw:
    raise RuntimeError('PNG pixel verification failed; BMP retained: '+path.name)
  os.replace(temporary,dest)
  bmp_info=path.stat()
  records.append({'file':dest.name,'mode':im.mode,'size':im.size,'pixel_sha256':hashlib.sha256(raw).hexdigest(),'bmp_bytes':bmp_info.st_size,'bmp_mtime_ns':bmp_info.st_mtime_ns,'png_bytes':dest.stat().st_size,'lossless_roundtrip':True,'bmp_retention':'Permanently deleted after lossless PNG verification and completed run; no extra capture archive'})
 if finished and records:
  redundant=[]
  for record in records:
   path=out/Path(record['file']).with_suffix('.bmp')
   if path.parent!=out or path.is_symlink() or path.resolve(strict=True).parent!=out:
    raise RuntimeError('Redundant BMP outside this completed run')
   info=path.stat()
   if info.st_size!=record['bmp_bytes'] or info.st_mtime_ns!=record['bmp_mtime_ns']:
    raise RuntimeError('Completed BMP changed after PNG verification: '+path.name)
   redundant.append(path)
  (out/'completed-bmp-delete-list.json').write_text(json.dumps([str(p) for p in redundant])+'\n')
  for path in redundant:path.unlink()
env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',SDL_RENDER_DRIVER='software')
if a.native_window:
 env=dict(os.environ)
 for key in ['SDL_VIDEODRIVER','SDL_AUDIODRIVER','SDL_RENDER_DRIVER']:env.pop(key,None)
results=[]
for requested in a.modes.split(','):
 label=a.prefix+'-'+requested if a.prefix else requested
 mode='classic' if requested in ['classic-again','baseline','baseline-again'] else requested
 if requested.startswith('8-'):mode='8'
 if requested.endswith('-local'):mode='local'
 if requested in ['repeat-local','skip-local','coverage-fault-local']:mode=requested[:-6]
 out=task/'controlled-runs'/label;out.mkdir(parents=True,exist_ok=True)
 cmd=[str(exe),'--data='+str(data),'--no-sound','--no-joystick','--no-xmas','--render-test='+mode,'--render-ticks='+str(a.ticks)]
 if a.assets:cmd+=['--render-assets='+str(Path(a.assets).resolve())]
 cmd+=['--render-talon-bank='+a.talon_bank]
 if a.local_blend:cmd+=['--render-local-blend']
 cmd+=['--render-scene='+a.scene]
 if not a.legacy_exe:cmd+=['--render-scene-assets='+a.scene_assets]
 if a.original_reference:cmd+=['--render-original-reference']
 if a.known_explosion_blend:cmd+=['--render-known-explosion-blend']
 if a.capture_blend:cmd+=['--render-capture-blend']
 start=time.monotonic()
 capture_records=[]
 with (out/'stdout.log').open('w',encoding='utf-8') as stdout,(out/'stderr.log').open('w',encoding='utf-8') as stderr:
  if not a.png_captures:proc=subprocess.run(cmd,cwd=out,env=env,stdout=stdout,stderr=stderr,timeout=max(180,a.ticks*.3))
  else:
   proc=subprocess.Popen(cmd,cwd=out,env=env,stdout=stdout,stderr=stderr)
   try:
    while proc.poll() is None:
     if time.monotonic()-start>max(180,a.ticks*.5):raise subprocess.TimeoutExpired(cmd,max(180,a.ticks*.5))
     compress_finished_captures(out,capture_records);time.sleep(.05)
    compress_finished_captures(out,capture_records,True)
   finally:
    if proc.poll() is None:proc.kill();proc.wait()
   (out/'lossless-captures.json').write_text(json.dumps(capture_records,indent=2)+'\n')
 if proc.returncode:raise SystemExit(f'{label}: exit {proc.returncode}, see logs')
 states=list(csv.DictReader((out/'state.tsv').open(),delimiter='\t'))
 collisions=list(csv.DictReader((out/'collisions.tsv').open(),delimiter='\t'))
 frames=list(csv.DictReader((out/'frames.tsv').open(),delimiter='\t'))
 presentations=list(csv.DictReader((out/'presentation.tsv').open(),delimiter='\t')) if (out/'presentation.tsv').exists() else []
 if len(states)!=a.ticks and not (a.allow_natural_end and 0<len(states)<a.ticks):raise SystemExit(f'{label}: only {len(states)} ticks')
 result={'mode':label,'ticks':len(states),'requested_ticks':a.ticks,'normal_exit_before_requested_limit':len(states)<a.ticks,'seconds':round(time.monotonic()-start,2),'collision_events':len(collisions),'collision_kinds':sorted(set(x['kind'] for x in collisions)),
         'state_sha256':hashlib.sha256((out/'state.tsv').read_bytes()).hexdigest(),'collision_sha256':hashlib.sha256((out/'collisions.tsv').read_bytes()).hexdigest(),
         'hd_frames':sum(int(x['hd_draws'])>0 and x['reason']=='hd-ordered' for x in frames),'hd_draws':sum(int(x['hd_draws']) for x in frames),
         'occluded_blocks':sum(int(x['occluded_blocks']) for x in frames),'coverage_mismatch':sum(int(x['coverage_mismatch']) for x in frames),
         'eligible_frame_mismatch':sum(int(x['coverage_mismatch']) for x in frames if x['reason'] in ['hd-ordered','classic-assets']),
         'fallback_frames':sum(x['reason'] not in ['hd-ordered','classic-assets'] for x in frames),'frame_reasons':sorted(set(x['reason'] for x in frames)),
         'display_present_calls':sum(int(x['present_calls']) for x in presentations),'display_rng_differences':sum(x['rng_before']!=x['rng_after'] for x in presentations)}
 results.append(result);print(json.dumps(result),flush=True)
(task/'controlled-runs'/'latest-results.json').write_text(json.dumps(results,indent=2)+'\n')
(task/'controlled-runs'/((a.prefix or 'run')+'-results.json')).write_text(json.dumps(results,indent=2)+'\n')
if len(results)>1:
 for r in results[1:]:
  if r['state_sha256']!=results[0]['state_sha256'] or r['collision_sha256']!=results[0]['collision_sha256']:raise SystemExit('State/collision difference; inspect per-tick records')
 print(f'Exact per-tick state/RNG/logical pixels and collision equivalence: {len(results)} modes x {a.ticks} ticks',flush=True)
