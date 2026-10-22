"""Build/query an observed draw-reference index; replay by segment or sheet-qualified material."""
from pathlib import Path
import argparse,csv,hashlib,json,collections,subprocess,struct,os,datetime,shutil,sys
repo=Path(__file__).resolve().parent.parent;root=repo.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def key(x):return f'{x["category"]}:{x["sheet"]}:{x["id"]}'
def hdstate(x,pack):
 name=None;id=int(x['id'])
 if x['category']=='enemy' and x['sheet']=='newsh2.shp' and id in [77,79,115,117,85,87,123,125,191,193,195,197,199,201,203,205,267]:name=f'enemy-newsh2-{id}-8.hda'
 elif x['category']=='terrain-layer1' and x['sheet']=='shapesz.dat' and id in [101,37,57,49,50,321,322,331,332]:name=f'terrain-shapesz-{id}-8.hda'
 elif x['category']=='effect' and x['sheet']=='newsh6.shp' and (122<=id<=133 or 3<=id<=14 or 22<=id<=33 or 41<=id<=52 or 60<=id<=71 or 146<=id<=152 or 192<=id<=203 or 154<=id<=165 or 211<=id<=222 or 173<=id<=184 or 135<=id<=141 or id in (229,230,231,232,233,234,235,236,237,248,249,250,252,253,254,255,256,267,268,269,272,275) or 78<=id<=84):name=f'explosion-newsh6-{id}-8.hda'
 elif x['category']=='player' and x['sheet']=='tyrian.shp#spriteSheet9' and id in [229,231,233,235,237]:name=f'ship-{id}-8.hda'
 elif x['category']=='player-projectile' and x['sheet']=='tyrian.shp#spriteSheet8' and id==59:name='bullet-59-8.hda'
 p=pack/name if name else None
 return {'status':'mapped external asset available' if p and p.exists() else 'original fallback / no external binding','file':name,'sha256':sha(p) if p and p.exists() else None,'header_values':list(struct.unpack('<6I',p.read_bytes()[4:28])) if p and p.exists() else None,'note':'Availability, not proof that every effect/occlusion draw uses HD; replay reloads pack in a fresh process.'}
p=argparse.ArgumentParser();sub=p.add_subparsers(dest='command',required=True)
b=sub.add_parser('build');b.add_argument('--run',type=Path,required=True);b.add_argument('--output',type=Path,required=True);b.add_argument('--assets',type=Path)
for name in ['list','find','play','replace']:
 q=sub.add_parser(name);q.add_argument('--index',type=Path,default=repo/'assets/hd/tyrian-e1-level9-index.json')
 if name in ['list','play']:q.add_argument('--segment',type=int)
 if name!='list':q.add_argument('--sheet');q.add_argument('--id',type=int);q.add_argument('--category')
 if name=='play':q.add_argument('--no-launch',action='store_true');q.add_argument('--headless',action='store_true');q.add_argument('--running',action='store_true');q.add_argument('--capture',action='store_true');q.add_argument('--capture-start',type=int,default=-1);q.add_argument('--capture-count',type=int,default=36);q.add_argument('--window-only',action='store_true');q.add_argument('--explosion-log',action='store_true');q.add_argument('--talon13',action='store_true');q.add_argument('--talon5',action='store_true');q.add_argument('--until',type=int,default=6000);q.add_argument('--assets',type=Path)
 if name=='replace':q.add_argument('--hda',type=Path,required=True);q.add_argument('--assets',type=Path,required=True)
 if name in ['list','find']:q.add_argument('--assets',type=Path)
a=p.parse_args()
if a.command=='build':
 if a.assets is None:
  import uuid
  sys.path.insert(0,str(repo/'scripts'))
  from build_current_craft267 import view
  a.assets=Path(view(repo,'debug',root/'current-craft267-packs'/('index-'+uuid.uuid4().hex))['path'])
 r=a.run.resolve();clock=rows(r/'asset-debug-clock.tsv');draws=rows(r/'asset-debug-materials.tsv');state=rows(r/'state.tsv');assert len(clock)==len(state) and all(int(x['tick'])==i for i,x in enumerate(clock));assert clock
 for x in draws:
  x['sheet']={'shapes9.dat':'tyrian.shp#spriteSheet9','shapes8.dat':'tyrian.shp#spriteSheet8','shapes12.dat':'tyrian.shp#spriteSheet12','OPTION_SHAPES':'tyrian.shp#OPTION_SHAPES','explosions-shapes6':'newsh6.shp'}.get(x['sheet'],x['sheet'].lower())
 ticks={int(x['tick']):x for x in clock};segments={};materials={}
 for x in clock:
  sid=int(float(x['start_ms'])//15000);seg=segments.setdefault(sid,{'number':sid,'start_tick':int(x['tick']),'end_tick':int(x['tick']),'nominal_start_ms':float(x['start_ms']),'nominal_end_ms':float(x['end_ms']),'index_window_ms':15000,'materials':{},'hard_playback_stop':False});seg['end_tick']=int(x['tick']);seg['nominal_end_ms']=float(x['end_ms'])
 for x in draws:
  t=int(x['tick']);assert t in ticks;sid=int(float(ticks[t]['start_ms'])//15000);k=key(x)
  item=segments[sid]['materials'].setdefault(k,{'category':x['category'],'sheet':x['sheet'],'id':int(x['id']),'first_tick':t,'last_tick':t,'draw_reference_count':0,'tile_IDs':set(),'first_xy':[int(x['x']),int(x['y'])]});item['last_tick']=t;item['draw_reference_count']+=1;item['tile_IDs'].add(int(x['tile_id']))
 for sid,seg in segments.items():
  for k,item in seg['materials'].items():
   item['tile_IDs']=sorted(item['tile_IDs']);item['replacement_at_index_build']=hdstate(item,a.assets)
   materials.setdefault(k,{'category':item['category'],'sheet':item['sheet'],'id':item['id'],'segments':[]})['segments'].append({'segment':sid,'first_tick':item['first_tick'],'last_tick':item['last_tick'],'draw_reference_count':item['draw_reference_count']})
 info=json.loads((r/'asset-debug-run.json').read_text())
 for prefix,expected in [('--asset-debug-episode=',1),('--asset-debug-level=',9)]:
  selected=[int(x[len(prefix):]) for x in info['argv'] if x.startswith(prefix)]
  if selected and selected[-1]!=expected:p.error('This first index builder supports the observed episode1 physical-level9 route only')
 if any(x.startswith('--render-scene=') and x!='--render-scene=enemy-hit' for x in info['argv']):p.error('This first index builder requires stationary enemy-hit input')
 data={'schema':'opentyrian-observed-segment-material-index-v1','replay':{'episode':1,'physical_level':9,'level_name':'TYRIAN','seed':'0x5eed','input':'enemy-hit: stationary, no firing; original natural enemies/projectiles','mode':'existing controlled level entry, original event engine and indexed drawing','index_window_ms':15000,'time_basis':'sum of actual configured original frameCountMax * PIT delayPeriod for each simulated logic tick; excludes debug pause and video playback FPS','source_HEAD':subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo).decode().strip(),'source_sha256':info.get('source_sha256',{}),'exe_sha256':info['exe_sha256'],'data_sha256':{n:sha(root/'runtime-data/tyrian2000'/n) for n in ['tyrian1.lvl','tyrian.shp','newsh2.shp','shapesz.dat','palette.dat']},'pack_directory':str(a.assets.resolve()),'reentry':'Fresh original initialization plus deterministic replay from tick0; no pointer jump, snapshots or artificial spawned enemy scene'},'coverage':{'first_tick':0,'last_tick':len(clock)-1,'nominal_end_ms':float(clock[-1]['end_ms']),'draw_reference_rows':len(draws),'kind':'Original ordered draw references whose rect intersects original playfield; later occlusion may cover them','limitations':['One observed level/input/seed/mode only, not static full coverage for other routes, firing, RNG or difficulty','Enemy IDs normalize original quad base; tile_IDs retain actual quadrants; sheet namespace prevents collisions','Terrain layers and player/projectile/effect sprite2 references recorded; UI fonts, procedural particles and menu assets excluded','Last index window may be partial; playback may continue beyond recorded coverage but later materials are not indexed','Replacement status is frozen at build; regenerate or inspect current pack after editing external assets']},'segments':[segments[x] for x in sorted(segments)],'materials':materials,'trace_sha256':{n:sha(r/n) for n in ['asset-debug-clock.tsv','asset-debug-materials.tsv','state.tsv']}}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8');print(json.dumps({'index':str(a.output),'segments':len(segments),'unique_materials':len(materials),'coverage':data['coverage']},indent=2));raise SystemExit()
data=json.loads(a.index.read_text(encoding='utf-8'));segments={x['number']:x for x in data['segments']}
if a.command=='list':
 if a.segment is None:
  print('Zero-based segments; times are configured engine logic seconds, not wall-clock/video seconds. Playback can continue across windows.')
  for s in segments.values():print(f'segment{s["number"]}: ticks{s["start_tick"]}..{s["end_tick"]}, {s["nominal_start_ms"]/1000:.3f}..{s["nominal_end_ms"]/1000:.3f} logic-s, {len(s["materials"])} materials (play can continue)')
 else:
  if a.segment not in segments:p.error('Segment outside collected coverage')
  for k,v in segments[a.segment]['materials'].items():
   current=hdstate(v,a.assets) if a.assets else v['replacement_at_index_build'];print(f'{k:42} ticks{v["first_tick"]}..{v["last_tick"]}  {current["status"]} [{current["file"] or "unbound"}]')
 raise SystemExit()
matches=[(k,v) for k,v in data['materials'].items() if (a.sheet is None or v['sheet']==a.sheet) and (a.id is None or v['id']==a.id) and (a.category is None or v['category']==a.category)]
if a.command=='find':
 if not a.sheet or a.id is None:p.error('Find requires --sheet and --id')
 if a.assets:
  matches=[(k,dict(v,current_replacement=hdstate(v,a.assets))) for k,v in matches]
 print(json.dumps(dict(matches),indent=2));raise SystemExit()
if a.command=='replace':
 if not a.sheet or a.id is None or len(matches)!=1:p.error('Replace requires one unambiguous sheet+ID, optionally category')
 k,material=matches[0];occurrence=material['segments'][0];entry=segments[occurrence['segment']]['materials'][k];binding=entry['replacement_at_index_build'];header=binding['header_values']
 if not binding['file'] or not header:p.error('No validated external binding for this material; code integration is required first')
 raw=a.hda.read_bytes()
 if len(raw)<28 or raw[:4]!=b'HDR1' or list(struct.unpack('<6I',raw[4:28]))!=header or len(raw)!=28+header[1]**2*header[2]*header[3]*4:p.error('HDA ID/density/size/anchor does not match the existing binding')
 pack=a.assets.resolve()
 if not pack.is_dir():p.error('Existing target pack directory required')
 target=pack/binding['file'];backup=None
 if target.exists():
  backup=pack/'.asset-debug-backups'/(datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')+'-'+target.name);backup.parent.mkdir(exist_ok=True);shutil.copyfile(target,backup)
 temporary=target.with_name(target.name+'.asset-debug-new');temporary.write_bytes(raw);os.replace(temporary,target)
 print(json.dumps({'material':k,'target':str(target),'sha256':sha(target),'backup':str(backup) if backup else None,'original_ID_size_anchor_preserved':True,'reload':'Replay same segment/material or press R in start-asset-debug.ps1; a fresh process reloads external assets'},indent=2));raise SystemExit()
if not 60<=a.until<=6000:p.error('--until must be60..6000 (finite debug safety limit, independent of15s index windows)')
if not -1<=a.capture_start<=5999 or not 1<=a.capture_count<=120:p.error('Capture bounds require start -1..5999 and count1..120')
if (a.capture_start>=0 or a.capture_count!=36 or a.window_only) and not a.capture:p.error('Capture bounds/window-only require --capture')
if a.segment is not None and a.segment not in segments:p.error('Segment outside collected coverage')
target=segments[a.segment]['start_tick'] if a.segment is not None else None
if a.sheet is not None or a.id is not None:
 if not a.sheet or a.id is None:p.error('Material play requires both --sheet and --id')
 occurrences=[x for _,v in matches for x in v['segments'] if a.segment is None or x['segment']==a.segment]
 if not occurrences:p.error('Material not observed in the selected coverage')
 target=min(x['first_tick'] for x in occurrences)
if target is None:p.error('Play requires --segment or a sheet-qualified material')
if a.until<=target:p.error('--until must exceed selected target tick')
cmd=['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(repo/'prototype/start-asset-debug.ps1'),'-Preset','custom','-Episode',str(data['replay']['episode']),'-Level',str(data['replay']['physical_level']),'-Tick',str(target),'-Until',str(a.until)]
if a.assets:cmd+=['-Assets',str(a.assets.resolve())]
else:cmd+=['-Python',sys.executable]
if a.capture:cmd+=['-CaptureCount',str(a.capture_count)]
if a.capture_start>=0:cmd+=['-CaptureStart',str(a.capture_start)]
if a.window_only:cmd.append('-WindowOnly')
if a.explosion_log:cmd.append('-ExplosionLog')
if a.talon13 and a.talon5:p.error('Choose --talon5 for compatibility or keep the default13')
for flag,enabled in [('-Headless',a.headless),('-Running',a.running),('-Capture',a.capture),('-Talon5',a.talon5)]:
 if enabled:cmd.append(flag)
print(subprocess.list2cmdline(cmd),flush=True)
if not a.no_launch:raise SystemExit(subprocess.call(cmd))
