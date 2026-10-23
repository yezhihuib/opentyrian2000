#!/usr/bin/env python3
"""One selected HUD source set generates shared and gameplay fallback consumers.

No historical bundle edits, image conversion or changed geometry/source guards.
Apply preflights all old/staged/source hashes, then uses per-file atomic replaces;
this is not a crash-safe multi-file transaction. Restage after any interruption.
"""
import argparse,json,os,subprocess,sys,tempfile
from pathlib import Path
from build_current_art import (sha,read,encoded,fingerprint,validate_stage_location,
                              verify_authority,REGISTRY,BINDING,RUNTIME,REBUILD)
from current_art_policy import PROFILES,profile,LEGACY_HEADER,legacy_header
from current_hud_compatibility import SELECTION,MAPPING,HEADER,NAMES,payload_header
from current_hud_recipe import render_resource
from package_runtime import contained_file,checked_source
from verify_current_production import source_inventory,source_manifest_digest,BUILD_INPUTS

KEYS=('static','meters','font','components','indicators','fixed_text')

def selection(root,raw):
    j=json.loads(raw)
    if set(j)!={'schema','version','resources'} or j['schema']!='opentyrian-current-hud-authoring-v1':raise ValueError('Invalid HUD selection schema')
    if not isinstance(j['version'],str) or not j['version'] or len(j['version'])>128:raise ValueError('Invalid HUD selection version')
    if not isinstance(j['resources'],dict) or set(j['resources'])!=set(KEYS):raise ValueError('Expected six semantic HUD keys')
    return j


def derive(root,raw):
    selected=selection(root,raw)
    registry=json.loads(read(root,REGISTRY))
    verify_authority(root,registry)
    if read(root,LEGACY_HEADER)!=legacy_header(registry['resources']):
        raise ValueError('Unrelated legacy art payload pins changed')
    outputs={SELECTION:raw};rows=[]
    for key,name in zip(KEYS,NAMES):
        data,pins=render_resource(root,key,selected['resources'][key])
        path='assets/hd/shared-ui-v1/'+name
        outputs[path]=data
        rows.append(dict(source_path=path,destinations=['assets/shared-ui/'+name,'assets/gameplay/'+name],sha256=sha(data)))
        if key=='meters':outputs[HEADER]=payload_header(pins)
    outputs[MAPPING]=encoded(dict(schema='opentyrian-current-hud-compatibility-v1',selection=SELECTION,version=selected['version'],files=rows))
    # Only selected HUD outputs and derived source binding may be stale.
    old=json.loads(read(root,RUNTIME));base=json.loads(read(root,'packaging/runtime-assets-public63a89b3.json'))
    generated=set(outputs)|{BINDING,RUNTIME}
    for row in old['files']:
        if row['source_path'] not in generated:checked_source(contained_file(root,row['source_path']),row)
    names={r['source_path'] for r in old['files']+base['files']}
    names|={REGISTRY,BINDING,'packaging/runtime-assets-public63a89b3.json','packaging/shop-static-approved-v1.json',MAPPING}|set(BUILD_INPUTS)
    names|={profile(f)['mapping'] for f in PROFILES}
    names.add('packaging/current-enemy-energy-compatibility.json')
    names.add('packaging/current-sidekick-body-compatibility.json')
    names.add('packaging/current-craft267-compatibility.json')
    names.add('packaging/current-tank-shell-compatibility.json')
    names|={p.relative_to(root).as_posix() for p in (root/'src').rglob('*') if p.is_file() or p.is_symlink()}
    names|={p.relative_to(root).as_posix() for p in (root/'scripts').glob('*.py')}
    from current_sidekick_body_compatibility import charge_input_paths,CHARGE_MAPPING
    names|=charge_input_paths(root)|{CHARGE_MAPPING}
    with tempfile.TemporaryDirectory(prefix='hud-authoring-build-') as tmp:
        work=Path(tmp)
        for name in sorted(names|set(outputs)):
            data=outputs[name] if name in outputs else read(root,name)
            p=work/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        global_header='src/global_asset_registry.h'
        subprocess.run([sys.executable,str(work/'scripts/build_global_registry_header.py'),'--registry',str(work/REGISTRY),'--output',str(work/global_header)],check=True,stdout=subprocess.DEVNULL)
        if (work/global_header).read_bytes()!=read(root,global_header):
            raise ValueError('Unrelated global art payload pins changed')
        binding=json.loads(read(root,BINDING));binding['production_commit']=None
        binding['source_sha256']=source_inventory(work)
        binding['production_source_manifest_sha256']=source_manifest_digest(binding['source_sha256'])
        binding['scope']='Exact current source binding including the separately reviewed Charge body rendering extension. Build/package consistency only; historical receipts retain their original scope.'
        outputs[BINDING]=(json.dumps(binding,indent=2,sort_keys=True)+'\n').encode();(work/BINDING).write_bytes(outputs[BINDING])
        subprocess.run([sys.executable,str(work/REBUILD),'--root',str(work),'--output',str(work/RUNTIME)],check=True,stdout=subprocess.DEVNULL)
        outputs[RUNTIME]=(work/RUNTIME).read_bytes()
    return outputs

def make_plan(root,outputs,raw):
    from current_sidekick_body_compatibility import authoring_input_fingerprints
    return dict(inputs_sha256=authoring_input_fingerprints(root),schema='opentyrian-current-hud-stage-v1',selection_sha256=sha(raw),files=[dict(path=p,before_sha256=fingerprint(root,p),after_sha256=sha(data),bytes=len(data)) for p,data in sorted(outputs.items())])

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
        temp=contained_file(root,name).with_name(Path(name).name+'.hud-tmp')
        if temp.exists() or temp.is_symlink():raise ValueError('Unexpected temporary output')
    for name,data in outputs.items():
        p=contained_file(root,name);p.parent.mkdir(parents=True,exist_ok=True)
        if p.exists() and p.read_bytes()==data:continue
        temp=p.with_name(p.name+'.hud-tmp')
        with temp.open('xb') as f:f.write(data)
        os.replace(temp,p)
    return expected

def check(root):
    outputs=derive(root,read(root,SELECTION))
    bad=[p for p,data in outputs.items() if fingerprint(root,p)!=sha(data)]
    if bad:raise ValueError('Stale/missing current HUD outputs: '+', '.join(bad))
    return dict(status='PASS',resources=6,logical_consumers=12,historical_outputs='untouched')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('mode',choices=('stage','apply','check'));p.add_argument('--selection',type=Path);p.add_argument('--stage',type=Path)
    a=p.parse_args();root=a.root.resolve()
    if a.mode=='check':result=check(root)
    else:
        if not a.stage:p.error('--stage required')
        result=stage(root,a.selection or root/SELECTION,a.stage) if a.mode=='stage' else apply(root,a.stage)
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
