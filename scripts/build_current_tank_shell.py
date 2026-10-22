#!/usr/bin/env python3
"""Edit the selected enemy shell pair once; update its two legacy consumers.

No global registration, rotation, scaling, historical output edits or deletions.
Apply preflights every source/old/staged hash and replaces files atomically, not
as a crash-safe multi-file transaction. Restage after interruption.
"""
import argparse,io,json,os,re,struct,subprocess,sys,tempfile
from pathlib import Path
from PIL import Image
from build_current_art import (sha,read,encoded,fingerprint,validate_stage_location,
                              verify_authority,REGISTRY,BINDING,RUNTIME,REBUILD)
from current_art_policy import PROFILES,profile,LEGACY_HEADER,legacy_header
from current_tank_shell_compatibility import IDS,SELECTION,MAPPING,HEADER,ROOT as COMPAT,name,fnv,payload_header
from package_runtime import contained_file,checked_source
from verify_current_production import source_inventory,source_manifest_digest,BUILD_INPUTS

def selection(root,raw):
    j=json.loads(raw)
    if set(j)!={'schema','version','resources'} or j['schema']!='opentyrian-current-tank-shell-authoring-v1':raise ValueError('Invalid tank-shell selection schema')
    if not isinstance(j['version'],str) or not j['version'] or len(j['version'])>128:raise ValueError('Invalid tank-shell version')
    if not isinstance(j['resources'],list) or len(j['resources'])!=2:raise ValueError('Expected two selected shell resources')
    for identity,row in zip(IDS,j['resources']):
        if not isinstance(row,dict) or set(row)!={'identity','source_png','source_sha256'} or type(row['identity']) is not int or row['identity']!=identity:raise ValueError('Invalid tank-shell identity/fields/order')
        if not isinstance(row['source_png'],str) or not isinstance(row['source_sha256'],str) or not re.fullmatch('[0-9a-f]{64}',row['source_sha256']):raise ValueError('Invalid selected source')
        if sha(read(root,row['source_png']))!=row['source_sha256']:raise ValueError('Selected shell source changed')
    return j

def source_blob(root,row):
    if type(row['identity']) is not int or row['identity'] not in IDS:raise ValueError('Unknown shell identity')
    raw=read(root,row['source_png'])
    if len(raw)>16*1024*1024:raise ValueError('Oversize PNG')
    with Image.open(io.BytesIO(raw)) as im:
        if im.format!='PNG' or im.mode!='RGBA' or im.size!=(96,112) or getattr(im,'n_frames',1)!=1:raise ValueError('Expected single 96x112 straight RGBA PNG')
        payload=im.tobytes()
    return b'HDR1'+struct.pack('<6I',row['identity'],8,12,14,0,0)+payload,payload

def derive(root,raw):
    selected=selection(root,raw);registry=json.loads(read(root,REGISTRY))
    verify_authority(root,registry)
    if read(root,LEGACY_HEADER)!=legacy_header(registry['resources']):raise ValueError('Unrelated legacy art pins changed')
    outputs={SELECTION:raw};rows=[];pins={}
    for row in selected['resources']:
        identity=row['identity'];data,payload=source_blob(root,row);path=f'{COMPAT}/{name(identity)}'
        outputs[path]=data;pins[identity]=fnv(payload)
        rows.append(dict(identity=identity,source_path=path,destination=f'assets/gameplay/{name(identity)}',sha256=sha(data)))
    outputs[HEADER]=payload_header(pins)
    outputs[MAPPING]=encoded(dict(schema='opentyrian-current-tank-shell-compatibility-v1',selection=SELECTION,version=selected['version'],files=rows))
    old=json.loads(read(root,RUNTIME));base=json.loads(read(root,'packaging/runtime-assets-public63a89b3.json'))
    generated=set(outputs)|{BINDING,RUNTIME}
    for row in old['files']:
        if row['source_path'] not in generated:checked_source(contained_file(root,row['source_path']),row)
    names={r['source_path'] for r in old['files']+base['files']}
    names|={REGISTRY,BINDING,'packaging/runtime-assets-public63a89b3.json','packaging/shop-static-approved-v1.json',MAPPING,'packaging/current-hud-compatibility.json'}|set(BUILD_INPUTS)
    names|={profile(f)['mapping'] for f in PROFILES}
    names.add('packaging/current-enemy-energy-compatibility.json')
    names.add('packaging/current-sidekick-body-compatibility.json')
    names|={p.relative_to(root).as_posix() for p in (root/'src').rglob('*') if p.is_file() or p.is_symlink()}
    names|={p.relative_to(root).as_posix() for p in (root/'scripts').glob('*.py')}
    with tempfile.TemporaryDirectory(prefix='tank-shell-authoring-build-') as tmp:
        work=Path(tmp)
        for key in sorted(names|set(outputs)):
            data=outputs[key] if key in outputs else read(root,key)
            p=work/key;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        header='src/global_asset_registry.h'
        subprocess.run([sys.executable,str(work/'scripts/build_global_registry_header.py'),'--registry',str(work/REGISTRY),'--output',str(work/header)],check=True,stdout=subprocess.DEVNULL)
        if (work/header).read_bytes()!=read(root,header):raise ValueError('Unrelated global pins changed')
        binding=json.loads(read(root,BINDING));binding['production_commit']=None
        binding['source_sha256']=source_inventory(work);binding['production_source_manifest_sha256']=source_manifest_digest(binding['source_sha256'])
        binding['scope']='Exact current single-source generated art pins; gameplay/role/source identity unchanged. Source binding only, not runtime acceptance.'
        outputs[BINDING]=(json.dumps(binding,indent=2,sort_keys=True)+'\n').encode();(work/BINDING).write_bytes(outputs[BINDING])
        subprocess.run([sys.executable,str(work/REBUILD),'--root',str(work),'--output',str(work/RUNTIME)],check=True,stdout=subprocess.DEVNULL)
        outputs[RUNTIME]=(work/RUNTIME).read_bytes()
    return outputs

def make_plan(root,outputs,raw):
    return dict(schema='opentyrian-current-tank-shell-stage-v1',selection_sha256=sha(raw),files=[dict(path=p,before_sha256=fingerprint(root,p),after_sha256=sha(data),bytes=len(data)) for p,data in sorted(outputs.items())])

def stage(root,selected,destination):
    validate_stage_location(root,destination)
    if destination.exists():raise ValueError('Stage destination must be new')
    raw=selected.read_bytes();outputs=derive(root,raw);plan=make_plan(root,outputs,raw)
    destination.mkdir(parents=True)
    for name,data in outputs.items():
        p=destination/'files'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    (destination/'plan.json').write_bytes(encoded(plan));return plan

def apply(root,destination):
    validate_stage_location(root,destination)
    plan=json.loads(read(destination,'plan.json'));raw=read(destination,'files/'+SELECTION)
    outputs=derive(root,raw);expected=make_plan(root,outputs,raw)
    if plan!=expected:raise ValueError('Stale or modified plan/current source; restage explicitly')
    for name,data in outputs.items():
        if read(destination,'files/'+name)!=data:raise ValueError('Modified staged bytes: '+name)
        temp=contained_file(root,name).with_name(Path(name).name+'.tank-shell-tmp')
        if temp.exists() or temp.is_symlink():raise ValueError('Unexpected temporary output')
    for name,data in outputs.items():
        p=contained_file(root,name);p.parent.mkdir(parents=True,exist_ok=True)
        if p.exists() and p.read_bytes()==data:continue
        temp=p.with_name(p.name+'.tank-shell-tmp')
        with temp.open('xb') as f:f.write(data)
        os.replace(temp,p)
    return expected

def check(root):
    outputs=derive(root,read(root,SELECTION))
    bad=[p for p,data in outputs.items() if fingerprint(root,p)!=sha(data)]
    if bad:raise ValueError('Stale/missing current tank-shell outputs: '+', '.join(bad))
    return dict(status='PASS',resources=2,logical_consumers=2,global_registry_additions=0,historical_outputs='untouched')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('mode',choices=('stage','apply','check'));p.add_argument('--selection',type=Path);p.add_argument('--stage',type=Path)
    a=p.parse_args();root=a.root.resolve()
    if a.mode=='check':result=check(root)
    else:
        if not a.stage:p.error('--stage required')
        result=stage(root,a.selection or root/SELECTION,a.stage) if a.mode=='stage' else apply(root,a.stage)
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
