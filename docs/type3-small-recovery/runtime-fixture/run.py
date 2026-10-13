#!/usr/bin/env python3
"""Newly regenerated finite recovery runner. Default validates only; explicit launch flag required."""
from pathlib import Path
import argparse,hashlib,json,subprocess,os,selectors,time,struct,gzip,re,shutil,traceback
from PIL import Image
ROOT=Path(__file__).resolve().parent;F=ROOT/'fixture-v2';REPO=ROOT.parent/'type3-small-recovery-20261013'
P=json.loads((F/'provenance.json').read_text());HEAD=P['source_head'];BASE=P['baseline'];DATA=Path(P['data_root'])
TICKS=list(range(6181,6193))+list(range(6512,6532))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def integrity():
 assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()==HEAD
 assert not subprocess.check_output(['git','status','--porcelain'],cwd=REPO)
 for n,h in P['files'].items():assert sha(F/n)==h,n
 for n,h in P['production_source'].items():assert sha(REPO/n)==h,n
 for n,h in P['data_files'].items():assert sha(DATA/n)==h,n
 for n,h in P['scripts'].items():assert sha(F/n)==h,n
 return True
ap=argparse.ArgumentParser();ap.add_argument('--case',choices=['baseline','candidate','native4-baseline','native4-candidate','missing266','corrupt209','density4-baseline','density4-candidate'],required=True);ap.add_argument('--execute-approved-census',action='store_true');args=ap.parse_args()
case=args.case;main=case in ('baseline','candidate');native4=case.startswith('native4-');density4=case.startswith('density4-');scale=4 if native4 else 2;limit=6532 if main else 6184;captures=TICKS if main else [6181] if density4 else [6181,6182,6183];mode='main'if main else'density4'if density4 else'cycle';binary='baseline'if case.endswith('baseline')else'candidate';pack=case if case in ('missing266','corrupt209')else binary
out=ROOT/(case+'-census'+('-4x'if native4 else''))
assert integrity()
# Compatibility metadata is descriptive and hash-derived, not substituted evidence.
def build_meta(label):
 b='baseline'if label.endswith('baseline')else'candidate';pk=label if label in ('missing266','corrupt209')else b;p=F/'packs'/pk
 return {'commit':BASE if b=='baseline'else HEAD,'executable':str(F/'bin'/b),'executable_sha256':sha(F/'bin'/b),'pack':str(p),'pack_hashes':{x.name:sha(x)for x in sorted(p.iterdir())}}
meta={'baseline':BASE,'candidate':HEAD,'source_root':str(REPO),'data':str(DATA),'data_sha256':P['data_files'],'production_src_hashes':{Path(n).name:h for n,h in P['production_source'].items()},'census_ticks':TICKS,'builds':{label:build_meta(label)for label in ('baseline','candidate','native4-baseline','native4-candidate','missing266','corrupt209','density4-baseline','density4-candidate')},'fixture_provenance_sha256':sha(F/'provenance.json'),'recovery_status':'Newly regenerated fixture and runner; exact production renderer and frozen art restored. All evidence must be fresh.','private_survival':True,'artificial_original_projectiles':True,'no_ram_type16_boss_coverage':True}
for name in ('provenance.json','gates-provenance.json'):
 path=ROOT/name;raw=json.dumps(meta,indent=2)+'\n'
 if path.exists():assert path.read_text()==raw
 else:path.write_text(raw)
if not args.execute_approved_census:
 print(json.dumps({'status':'VALIDATED_NO_LAUNCH','case':case,'capture_ticks':captures,'logic_ticks':[0,limit-1],'fixture_provenance_sha256':sha(F/'provenance.json')},indent=2));raise SystemExit
assert not out.exists(),out
assert shutil.disk_usage(ROOT).free>4*1024**3
out.mkdir();configdir=out/'home/.config/opentyrian2000';configdir.mkdir(parents=True);config=configdir/'opentyrian.cfg';config.write_text('section video\n\titem fullscreen -1\n\titem scaler '+str(scale)+'x\n\titem scaling_mode integer\n');config_pin=sha(config)
# Every possible telemetry writer is drained, including logs not retained.
texts='\n'.join((F/'build/src'/n).read_text()for n in ('game_probe.c','asset_debug.c','tyrian2.c'))
names=sorted(set(re.findall(r'fopen\("([a-zA-Z0-9_-]+)\.tsv"',texts)))
all_names={'state','collisions','presentation','asset-debug-clock','asset-debug-explosion-pools','late-census','type3-explosion-census','type3-original-effects','type3-pulse-guards','type3-pulse-shots','blend-palette','fire-events','player-shot-emissions','player-shot-requests','player-shot-results','weapon-loadout','sidekick-loadout','sdl-runtime','asset-debug-control','fade-steps'}
audit_names={'frames','effects','rgb-audit'}
sel=selectors.DefaultSelector();streams={};fds=[]
for n in names:
 fifo=out/(n+'.tsv');os.mkfifo(fifo);fd=os.open(fifo,os.O_RDWR|os.O_NONBLOCK);fds.append(fd);sel.register(fd,selectors.EVENT_READ,n)
 streams[n]={'fd':fd,'hash':hashlib.sha256(),'bytes':0,'lines':0,'kept_lines':0,'buf':b'','gz':gzip.open(out/(n+'.tsv.gz'),'wb',compresslevel=6),'retention':'all'if n in all_names else'audit-6181-through-stop'if n in audit_names else'exact-retained-ticks'}
nativefifo=out/'native-rgba.fifo';os.mkfifo(nativefifo);fd=os.open(nativefifo,os.O_RDWR|os.O_NONBLOCK);fds.append(fd);sel.register(fd,selectors.EVENT_READ,'NATIVE');nativebuf=b'';frames=[]
env=os.environ.copy();env.update({'SDL_VIDEODRIVER':'dummy','SDL_AUDIODRIVER':'dummy','SDL_RENDER_DRIVER':'software','HOME':str(out/'home'),'XDG_CONFIG_HOME':str(out/'home/.config'),'OT_LATE_TERRAIN_INVULNERABLE':'1','OT_LATE_CENSUS':'1','OT_TYPE3_LIFECYCLE':'1','OT_TYPE3_CAPTURE_MODE':mode,'OT_CAPTURE_RGBA_STREAM':str(nativefifo)})
cmd=[str(F/'bin'/binary),'--data='+str(DATA),'--asset-debug=custom','--asset-debug-episode=1','--asset-debug-level=9','--asset-debug-tick=6181','--asset-debug-running','--asset-debug-explosion-log','--render-test='+('4'if density4 else'local'),'--render-assets='+str(F/'packs'/pack),'--render-scene-assets=all','--render-scene=enemy-hit','--render-ticks='+str(limit),'--render-no-capture','--no-sound','--no-joystick','--no-xmas']
(out/'invocation.json').write_text(json.dumps({'command':cmd,'private_environment':{k:env[k]for k in env if k.startswith('OT_')or k.startswith('SDL_')or k in ('HOME','XDG_CONFIG_HOME')},'runner_sha256':sha(Path(__file__)),'fixture_provenance_sha256':sha(F/'provenance.json'),'config_sha256':config_pin,'scope':'Private survival; artificial original Pulse155 only; native SDL software output; no ram/type16/boss actual claim'},indent=2)+'\n')
started=time.monotonic();last_budget=started;proc=None;error=None
try:
 stdout=(out/'stdout.log').open('wb');stderr=(out/'stderr.log').open('wb');proc=subprocess.Popen(cmd,cwd=out,env=env,stdout=stdout,stderr=stderr)
 while True:
  events=sel.select(.2);read_any=False
  for key,_ in events:
   try:data=os.read(key.fd,1024*1024)
   except BlockingIOError:continue
   if not data:continue
   read_any=True;n=key.data
   if n=='NATIVE':
    nativebuf+=data
    while len(nativebuf)>=20:
     assert nativebuf[:4]==b'ORF1';tick,w,h,size=struct.unpack_from('<4I',nativebuf,4);assert (w,h,size)==(320*scale,200*scale,320*200*4*scale*scale)
     if len(nativebuf)<20+size:break
     assert tick==captures[len(frames)],(tick,captures,len(frames));raw=nativebuf[20:20+size];nativebuf=nativebuf[20+size:];im=Image.frombytes('RGBA',(w,h),raw,'raw','BGRA');p=out/f'actual-{tick}-native{scale}x.png';im.save(p);rgba=im.tobytes();check=Image.open(p).convert('RGBA');assert check.size==(w,h)and check.tobytes()==rgba
     frames.append({'tick':tick,'width':w,'height':h,'path':str(p),'PNG_sha256':sha(p),'RGBA_sha256':hashlib.sha256(rgba).hexdigest()});(out/'frame-hashes.json').write_text(json.dumps(frames,indent=2)+'\n')
    continue
   s=streams[n];s['hash'].update(data);s['bytes']+=len(data);buf=s['buf']+data;lines=buf.split(b'\n');s['buf']=lines.pop();retained=[]
   for line in lines:
    first=s['lines']==0;s['lines']+=1;keep=first or n in all_names
    if not keep:
     field=line.split(b'\t',1)[0]
     if field.isdigit():tick=int(field);keep=(6181<=tick<limit)if n in audit_names else tick in captures
    if keep:retained.append(line+b'\n');s['kept_lines']+=1
   if retained:s['gz'].write(b''.join(retained))
  now=time.monotonic()
  if now-started>900:raise RuntimeError('900-second approved execution ceiling reached')
  if now-last_budget>=2:
   last_budget=now;size=sum(p.stat().st_size for p in out.rglob('*')if p.is_file());assert size<96*1024**2,('96 MiB evidence ceiling',size);assert shutil.disk_usage(ROOT).free>4*1024**3
  if proc.poll()is not None and not events and not read_any:break
 assert proc.returncode==0,proc.returncode
 assert not nativebuf and [f['tick']for f in frames]==captures
 for n,s in streams.items():assert not s['buf'],n
 assert sha(config)==config_pin,'Configuration changed'
 assert integrity()
except BaseException as e:
 error=repr(e)
 if proc and proc.poll()is None:proc.terminate();proc.wait(timeout=10)
finally:
 receipts={}
 for n,s in streams.items():
  s['gz'].close();p=out/(n+'.tsv.gz');receipts[n]={'gzip_sha256':sha(p),'retention':s['retention'],'raw_sha256':s['hash'].hexdigest(),'raw_bytes':s['bytes'],'lines':s['lines'],'retained_lines':s['kept_lines']}
 for fd in fds:os.close(fd)
 sel.close()
 (out/'stream-receipts.json').write_text(json.dumps(receipts,indent=2)+'\n')
 summary={'status':'PASS'if error is None else'FAILED','error':error,'integrity_passed':error is None,'case':case,'commit':BASE if binary=='baseline'else HEAD,'logic_ticks':[0,limit-1],'native_captures':len(frames),'capture_ticks':[f['tick']for f in frames],'native_dimensions':[320*scale,200*scale],'wall_seconds':time.monotonic()-started,'runner_sha256':sha(Path(__file__)),'fixture_provenance_sha256':sha(F/'provenance.json'),'private_survival':True,'artificial_original_projectiles':main,'no_ram_type16_boss_coverage':True}
 (out/'run-summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2),flush=True)
if error:raise RuntimeError(error)
