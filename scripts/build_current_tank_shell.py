#!/usr/bin/env python3
"""Edit the selected enemy shell pair once; preserve its roles and geometry.

Historical mode and current-tank-energy-v3 keep their original authority.
Explicit current-tank-energy-body194-v1 adds one strict source/runtime projection.
Both energy modes also update two exact global aliases and removes only the superseded private
aliases. No global registry additions, rotation, scaling or historical edits.
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


def rebuild_input_paths(root,selected):
    """Declared current producer inputs; no generation or historical-tree glob.

    The older shared authoring closure predates the indexed 7/45 and banana
    families. Keep their independently pinned inputs explicit in this builder.
    """
    from current_sidekick_body_compatibility import independent_input_paths
    from current_projectile_bolts745_compatibility import input_paths as bolts_inputs
    from current_projectile_animated153_compatibility import input_paths as banana_inputs
    return independent_input_paths(root)|bolts_inputs(root)|banana_inputs(root)|{row['source_png'] for row in selected['resources']}

def validate_input_closure(root,names):
    """Report the entire missing/nonregular finite set before child rebuild."""
    failures=[]
    for name in sorted(names):
        try:
            p=contained_file(root,name)
            if not p.is_file():failures.append(name)
        except (OSError,ValueError):failures.append(name)
    if failures:raise ValueError('Incomplete Tank rebuild inputs: '+', '.join(failures))

def derive(root,raw,authority="historical"):
    selected=selection(root,raw);registry=json.loads(read(root,REGISTRY))
    if authority=='historical':verify_authority(root,registry)
    elif authority=='current-tank-energy-v3':
        from current_tank_energy_authority import verify as verify_current
        verify_current(root,selected)
    elif authority=='current-tank-energy-body194-v1':
        from current_tank194_energy_authority import verify as verify_body_current
        verify_body_current(root,selected)
    elif authority=='current-tank-energy-body194-extra-poses-v1':
        from current_tank194_energy_authority import verify_extra
        verify_extra(root,selected)
    else:raise ValueError('Unknown Tank authority')
    if read(root,LEGACY_HEADER)!=legacy_header(registry['resources']):raise ValueError('Unrelated legacy art pins changed')
    outputs={SELECTION:raw};rows=[];pins={};hashes={}
    for row in selected['resources']:
        identity=row['identity'];data,payload=source_blob(root,row);path=f'{COMPAT}/{name(identity)}'
        outputs[path]=data;pins[identity]=fnv(payload);hashes[identity]=sha(data)
        if authority in ('current-tank-energy-v3','current-tank-energy-body194-v1','current-tank-energy-body194-extra-poses-v1'):
            from current_tank_energy_authority import APPROVED_HDA
            if sha(data)!=APPROVED_HDA[identity-1220000]:raise ValueError('Unreviewed Tank energy pixels')
            outputs['assets/hd/global-assets-v1/content/'+sha(data)+'.hda']=data
        rows.append(dict(identity=identity,source_path=path,destination=f'assets/gameplay/{name(identity)}',sha256=sha(data)))
    outputs[HEADER]=payload_header(pins,hashes) if authority!='historical' else payload_header(pins)
    outputs[MAPPING]=encoded(dict(schema='opentyrian-current-tank-shell-compatibility-v1',selection=SELECTION,version=selected['version'],files=rows))
    old=json.loads(read(root,RUNTIME));base=json.loads(read(root,'packaging/runtime-assets-public63a89b3.json'))
    removed=set()
    if authority!='historical':
        from current_tank_energy_authority import OLD_ALIASES
        removed=set(OLD_ALIASES)
    generated=set(outputs)|{BINDING,RUNTIME}|removed
    # Current authority already checked every unchanged runtime row and byte.
    if authority=='historical':
        for row in old['files']:
            if row['source_path'] not in generated:checked_source(contained_file(root,row['source_path']),row)
    names={r['source_path'] for r in old['files']+base['files']}
    names|={REGISTRY,BINDING,'packaging/runtime-assets-public63a89b3.json','packaging/shop-static-approved-v1.json',MAPPING,'packaging/current-hud-compatibility.json'}|set(BUILD_INPUTS)
    names|={profile(f)['mapping'] for f in PROFILES}
    names.add('packaging/current-enemy-energy-compatibility.json')
    names.add('packaging/current-sidekick-body-compatibility.json')
    names.add('packaging/current-craft267-compatibility.json')
    names|={p.relative_to(root).as_posix() for p in (root/'src').rglob('*') if p.is_file() or p.is_symlink()}
    names|={p.relative_to(root).as_posix() for p in (root/'scripts').glob('*.py')}
    names|=rebuild_input_paths(root,selected)
    if authority=='current-tank-energy-body194-v1':
        from current_tank194_source_bridge import input_paths as body_epoch_inputs
        names|=body_epoch_inputs(root)
    elif authority=='current-tank-energy-body194-extra-poses-v1':
        from current_tank194_source_bridge import extra_input_paths
        names|=extra_input_paths(root)
    names-=removed
    validate_input_closure(root,names-set(outputs))
    with tempfile.TemporaryDirectory(prefix='tank-shell-authoring-build-') as tmp:
        work=Path(tmp)
        for key in sorted(names|set(outputs)):
            data=outputs[key] if key in outputs else read(root,key)
            p=work/key;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        validate_input_closure(work,names|set(outputs))
        header='src/global_asset_registry.h'
        subprocess.run([sys.executable,str(work/'scripts/build_global_registry_header.py'),'--registry',str(work/REGISTRY),'--output',str(work/header)],check=True,stdout=subprocess.DEVNULL)
        if (work/header).read_bytes()!=read(root,header):raise ValueError('Unrelated global pins changed')
        binding=json.loads(read(root,BINDING));binding['production_commit']=None
        binding['source_sha256']=source_inventory(work);binding['production_source_manifest_sha256']=source_manifest_digest(binding['source_sha256'])
        binding['scope']='Exact current source binding including the separately reviewed Charge body extension, Plasma projectile and Front Multi payload-pin extractions. Build/package consistency only; historical receipts retain their original scope.'
        if authority=='current-tank-energy-body194-v1':
            binding['scope']+=' Includes the exact body194 source epoch and two unchanged canonical aliases; no additional native or artwork qualification.'
        if authority=='current-tank-energy-body194-extra-poses-v1':
            binding['scope']+=' Includes the exact332 extra51/55 epoch and four unchanged canonical body aliases; no additional native or artwork qualification.'
        outputs[BINDING]=(json.dumps(binding,indent=2,sort_keys=True)+'\n').encode();(work/BINDING).write_bytes(outputs[BINDING])
        subprocess.run([sys.executable,str(work/REBUILD),'--root',str(work),'--output',str(work/RUNTIME)],check=True,stdout=subprocess.DEVNULL)
        outputs[RUNTIME]=(work/RUNTIME).read_bytes()
    return outputs

def make_plan(root,outputs,raw,authority="historical"):
    from current_sidekick_body_compatibility import authoring_input_fingerprints
    plan=dict(inputs_sha256=authoring_input_fingerprints(root),schema='opentyrian-current-tank-shell-stage-v1',selection_sha256=sha(raw),files=[dict(path=p,before_sha256=fingerprint(root,p),after_sha256=sha(data),bytes=len(data)) for p,data in sorted(outputs.items())])
    if authority!='historical':
        from current_tank_energy_authority import obsolete
        selected=selection(root,raw)
        extra={row['source_png'] for row in selected['resources']}|{'scripts/build_current_tank_shell.py','scripts/current_tank_shell_compatibility.py','scripts/current_tank_energy_authority.py','scripts/current_enemy_tank_shared_aliases.py','scripts/current_tank_muzzle_source_bridge.py','scripts/current_warning_source_bridge.py'}
        if authority=='current-tank-energy-body194-v1':
            from current_tank194_source_bridge import input_paths as body_epoch_inputs
            extra|=body_epoch_inputs(root)|{'scripts/current_tank194_source_bridge.py','scripts/current_tank194_energy_authority.py','scripts/current_tank194_body_registration.py'}
        elif authority=='current-tank-energy-body194-extra-poses-v1':
            from current_tank194_source_bridge import extra_input_paths
            extra|=extra_input_paths(root)|{'scripts/current_tank194_source_bridge.py','scripts/current_tank194_energy_authority.py','scripts/current_tank194_body_registration.py','scripts/current_tank194_extra_registration.py'}
        plan['inputs_sha256'].update({name:sha(read(root,name)) for name in sorted(extra)})
        plan['authority']=authority
        plan['remove']=[dict(path=p,before_sha256=fingerprint(root,p)) for p in obsolete(root)]
    return plan

def stage(root,selected,destination,authority="historical"):
    validate_stage_location(root,destination)
    if destination.exists():raise ValueError('Stage destination must be new')
    raw=selected.read_bytes();outputs=derive(root,raw,authority);plan=make_plan(root,outputs,raw,authority)
    destination.mkdir(parents=True)
    for name,data in outputs.items():
        p=destination/'files'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    (destination/'plan.json').write_bytes(encoded(plan));return plan

def apply(root,destination,authority="historical"):
    validate_stage_location(root,destination)
    plan=json.loads(read(destination,'plan.json'));raw=read(destination,'files/'+SELECTION)
    outputs=derive(root,raw,authority);expected=make_plan(root,outputs,raw,authority)
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
    for row in expected.get("remove",[]):contained_file(root,row["path"]).unlink()
    return expected

def check(root,authority="historical"):
    outputs=derive(root,read(root,SELECTION),authority)
    bad=[p for p,data in outputs.items() if fingerprint(root,p)!=sha(data)]
    if authority!='historical':
        from current_tank_energy_authority import obsolete
        bad+=obsolete(root)
    if bad:raise ValueError('Stale/missing current tank-shell outputs: '+', '.join(bad))
    return dict(status='PASS',resources=2,logical_consumers=2,global_registry_additions=0,historical_outputs='untouched')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('mode',choices=('stage','apply','check'));p.add_argument('--selection',type=Path);p.add_argument('--stage',type=Path)
    p.add_argument('--authority',choices=('historical','current-tank-energy-v3','current-tank-energy-body194-v1','current-tank-energy-body194-extra-poses-v1'),default='historical')
    a=p.parse_args();root=a.root.resolve()
    if a.mode=='check':result=check(root,a.authority)
    else:
        if not a.stage:p.error('--stage required')
        result=stage(root,a.selection or root/SELECTION,a.stage,a.authority) if a.mode=='stage' else apply(root,a.stage,a.authority)
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
