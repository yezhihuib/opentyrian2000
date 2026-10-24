#!/usr/bin/env python3
"""Real aggregate authoring check in an independent disposable checkout copy.

Run from repository root. Copies only materialized inputs (no Git/object store);
never writes the source checkout. Emits a receipt and log outside the checkout.
Not native renderer/platform acceptance. Approximately 170 MiB temporary space.
"""
from pathlib import Path
import shutil,tempfile,sys,json,io,hashlib
sys.path.insert(0,str(Path('scripts').resolve()))
import build_current_protron as b
import current_protron_compatibility as c
from PIL import Image
base=Path(tempfile.mkdtemp(prefix='protron-current-integration-',dir='../')).resolve();r=base/'repo';r.mkdir()
try:
 for n in ('assets','authoring-inputs','scripts','src','packaging','visualc'):
  shutil.copytree(Path(n),r/n,ignore=shutil.ignore_patterns('__pycache__'))
 for p in Path('.').iterdir():
  if p.is_file() and p.name!='.git': shutil.copyfile(p,r/p.name)
 original=json.loads((r/b.RUNTIME).read_bytes()); original_dest={x['destination'] for x in original['files']}
 request=json.loads((r/c.SELECTION).read_bytes());request.pop('resources');request['schema']=c.CANDIDATE_SCHEMA;request['version']='integration-cell244-only'
 master=r/request['master']['source_png'];im=Image.open(master).copy();crop=im.crop((651,38,1373,762));channels=crop.split();crop=Image.merge('RGBA',(channels[0].point(lambda x:(x+43)%256),*channels[1:]));im.paste(crop,(651,38));im.save(master)
 request['master']['source_sha256']=c.sha(master.read_bytes());draft=base/'candidate.json';draft.write_bytes(b.encoded(request))
 before={p:c.sha((r/c.ROOT/c.name(*p)).read_bytes()) for p in c.PAIRS}
 print('STAGE actual edited candidate',flush=True);b.stage(r,draft,base/'stage')
 print('APPLY actual edited candidate',flush=True);b.apply(r,base/'stage')
 print('CHECK',b.check(r),flush=True)
 after={p:c.sha((r/c.ROOT/c.name(*p)).read_bytes()) for p in c.PAIRS};assert {p for p in before if before[p]!=after[p]}=={(80244,8),(1470227,8)}
 runtime=json.loads((r/b.RUNTIME).read_bytes());assert len(runtime['files'])==1029;assert {x['destination'] for x in runtime['files']}==original_dest
 assert len(json.loads((r/b.REGISTRY).read_bytes())['resources'])==120
 for module in ('build_current_plasma_projectile','build_current_enemy_orb','build_current_front_multi'):
  m=__import__(module);print('CROSS',module,m.check(r),flush=True)
 import build_current_sidekick_body as body
 print('CROSS charge-body',body.charge_check(r),flush=True)
 print('CROSS mint-front-body',body.mf_check(r),flush=True)
 import build_current_art as art
 print('CROSS green',art.check(r,'green'),flush=True)
 import build_current_craft267 as craft
 overlays=craft.current_overlays(r);assert len(overlays)==178
 print('CROSS preview178; destinations1029; global120; changed244+227 only PASS',flush=True)
 (Path('../protron-current-integration-receipt.json')).write_text(json.dumps(dict(status='PASS',real_candidate_stage_apply_check=True,cell244_propagation=[80244,1470227],runtime_destinations=1029,global_registry=120,current_overlays=178,cross_workflows=['plasma-projectile','enemy-orb','front-multi','charge-body','mint-front-body','green']),indent=2)+'\n')
finally:
 shutil.rmtree(base)
