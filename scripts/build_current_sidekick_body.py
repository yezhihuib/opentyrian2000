#!/usr/bin/env python3
"""Current body authoring: six Marlo/Plasma sources, Charge, and Mint/Front.

The default six-body API is unchanged; independent families use --family.

No global registration, rotation, scaling, historical output edits or deletions.
The generated header checks build/package consistency only. Production C does
not include it; existing raw-bank qualification and fallback remain unchanged.
Apply preflights every source/old/staged hash and replaces files atomically, not
as a crash-safe multi-file transaction. Restage after interruption.
"""
import argparse,io,json,os,re,struct,subprocess,sys,tempfile
from pathlib import Path
from PIL import Image
from build_current_art import (sha,read,encoded,fingerprint,validate_stage_location,
                              verify_authority,REGISTRY,BINDING,RUNTIME,REBUILD)
from current_art_policy import PROFILES,profile,LEGACY_HEADER,legacy_header
from current_sidekick_body_compatibility import IDS,SELECTION,MAPPING,HEADER,ROOT as COMPAT,name,fnv,payload_header
from package_runtime import contained_file,checked_source
from verify_current_production import source_inventory,source_manifest_digest,BUILD_INPUTS

def selection(root,raw):
    j=json.loads(raw)
    if not isinstance(j,dict) or set(j)!={'schema','version','resources'} or j['schema']!='opentyrian-current-sidekick-body-authoring-v1':raise ValueError('Invalid sidekick-body selection schema')
    if not isinstance(j['version'],str) or not j['version'] or len(j['version'])>128:raise ValueError('Invalid sidekick-body version')
    if not isinstance(j['resources'],list) or len(j['resources'])!=6:raise ValueError('Expected six selected body resources')
    for identity,row in zip(IDS,j['resources']):
        if not isinstance(row,dict) or set(row)!={'identity','source_png','source_sha256'} or type(row['identity']) is not int or row['identity']!=identity:raise ValueError('Invalid sidekick-body identity/fields/order')
        if not isinstance(row['source_png'],str) or not isinstance(row['source_sha256'],str) or not re.fullmatch('[0-9a-f]{64}',row['source_sha256']):raise ValueError('Invalid selected source')
        if sha(read(root,row['source_png']))!=row['source_sha256']:raise ValueError('Selected body source changed')
    return j

def source_blob(root,row):
    if type(row['identity']) is not int or row['identity'] not in IDS:raise ValueError('Unknown body identity')
    raw=read(root,row['source_png'])
    if len(raw)>16*1024*1024:raise ValueError('Oversize PNG')
    try:
        with Image.open(io.BytesIO(raw)) as im:
            if im.format!='PNG' or im.mode!='RGBA' or im.size!=(96,112) or getattr(im,'n_frames',1)!=1:raise ValueError('Expected single 96x112 straight RGBA PNG')
            payload=im.tobytes()
    except OSError as exc:
        raise ValueError('Malformed selected body PNG') from exc
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
    outputs[MAPPING]=encoded(dict(schema='opentyrian-current-sidekick-body-compatibility-v1',selection=SELECTION,version=selected['version'],files=rows))
    old=json.loads(read(root,RUNTIME));base=json.loads(read(root,'packaging/runtime-assets-public63a89b3.json'))
    generated=set(outputs)|{BINDING,RUNTIME}
    for row in old['files']:
        if row['source_path'] not in generated:checked_source(contained_file(root,row['source_path']),row)
    names={r['source_path'] for r in old['files']+base['files']}
    names|={REGISTRY,BINDING,'packaging/runtime-assets-public63a89b3.json','packaging/shop-static-approved-v1.json',MAPPING,'packaging/current-hud-compatibility.json'}|set(BUILD_INPUTS)
    names|={profile(f)['mapping'] for f in PROFILES}
    names.add('packaging/current-enemy-energy-compatibility.json')
    names.add('packaging/current-tank-shell-compatibility.json')
    names.add('packaging/current-craft267-compatibility.json')
    names|={p.relative_to(root).as_posix() for p in (root/'src').rglob('*') if p.is_file() or p.is_symlink()}
    names|={p.relative_to(root).as_posix() for p in (root/'scripts').glob('*.py')}
    from current_sidekick_body_compatibility import independent_input_paths
    names|=independent_input_paths(root)
    with tempfile.TemporaryDirectory(prefix='sidekick-body-authoring-build-') as tmp:
        work=Path(tmp)
        for key in sorted(names|set(outputs)):
            data=outputs[key] if key in outputs else read(root,key)
            p=work/key;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        header='src/global_asset_registry.h'
        subprocess.run([sys.executable,str(work/'scripts/build_global_registry_header.py'),'--registry',str(work/REGISTRY),'--output',str(work/header)],check=True,stdout=subprocess.DEVNULL)
        if (work/header).read_bytes()!=read(root,header):raise ValueError('Unrelated global pins changed')
        binding=json.loads(read(root,BINDING));binding['production_commit']=None
        binding['source_sha256']=source_inventory(work);binding['production_source_manifest_sha256']=source_manifest_digest(binding['source_sha256'])
        binding['scope']='Exact current source binding including the separately reviewed Charge body extension, Plasma projectile and Front Multi payload-pin extractions. Build/package consistency only; historical receipts retain their original scope.'
        outputs[BINDING]=(json.dumps(binding,indent=2,sort_keys=True)+'\n').encode();(work/BINDING).write_bytes(outputs[BINDING])
        subprocess.run([sys.executable,str(work/REBUILD),'--root',str(work),'--output',str(work/RUNTIME)],check=True,stdout=subprocess.DEVNULL)
        outputs[RUNTIME]=(work/RUNTIME).read_bytes()
    return outputs

def make_plan(root,outputs,raw):
    from current_sidekick_body_compatibility import authoring_input_fingerprints
    return dict(inputs_sha256=authoring_input_fingerprints(root),schema='opentyrian-current-sidekick-body-stage-v1',selection_sha256=sha(raw),files=[dict(path=p,before_sha256=fingerprint(root,p),after_sha256=sha(data),bytes=len(data)) for p,data in sorted(outputs.items())])

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
        temp=contained_file(root,name+'.sidekick-body-tmp')
        if temp.exists() or temp.is_symlink():raise ValueError('Unexpected temporary output')
    for name,data in outputs.items():
        p=contained_file(root,name);p.parent.mkdir(parents=True,exist_ok=True)
        if p.exists() and p.read_bytes()==data:continue
        temp=p.with_name(p.name+'.sidekick-body-tmp')
        with temp.open('xb') as f:f.write(data)
        os.replace(temp,p)
    return expected

def check(root):
    outputs=derive(root,read(root,SELECTION))
    bad=[p for p,data in outputs.items() if fingerprint(root,p)!=sha(data)]
    if bad:raise ValueError('Stale/missing current sidekick-body outputs: '+', '.join(bad))
    return dict(status='PASS',resources=6,logical_consumers=6,global_registry_additions=0,historical_outputs='untouched')

# Charge uses the same shared transport workflow, with an explicit independent
# candidate contract. Existing six-body functions and defaults above are unchanged.
def charge_derive(root,raw):
    import current_sidekick_body_compatibility as compat
    parsed=compat._charge_parse(raw)
    candidate=isinstance(parsed,dict) and parsed.get('schema')==compat.CHARGE_CANDIDATE_SCHEMA
    selected,pngs,blobs=compat.charge_generate(root,raw,candidate=candidate)
    registry=json.loads(read(root,REGISTRY));verify_authority(root,registry)
    if read(root,LEGACY_HEADER)!=legacy_header(registry['resources']):raise ValueError('Unrelated legacy art pins changed')
    outputs={compat.CHARGE_SELECTION:encoded(selected),**pngs};rows=[]
    for identity,blob in blobs.items():
        path=compat.CHARGE_ROOT+'/'+compat.charge_name(identity);outputs[path]=blob
        rows.append(dict(identity=identity,source_path=path,destination='assets/gameplay/'+compat.charge_name(identity),sha256=sha(blob)))
    outputs[compat.CHARGE_MAPPING]=encoded(dict(schema='opentyrian-current-charge-body-compatibility-v1',selection=compat.CHARGE_SELECTION,version=selected['version'],files=rows))
    old=json.loads(read(root,RUNTIME));base=json.loads(read(root,'packaging/runtime-assets-public63a89b3.json'))
    for row in old['files']:
        if row['source_path'] not in outputs:checked_source(contained_file(root,row['source_path']),row)
    names={r['source_path'] for r in old['files']+base['files']}
    names|={REGISTRY,BINDING,'packaging/runtime-assets-public63a89b3.json','packaging/shop-static-approved-v1.json',MAPPING,'packaging/current-hud-compatibility.json','packaging/current-tank-shell-compatibility.json','packaging/current-enemy-energy-compatibility.json','packaging/current-craft267-compatibility.json'}|set(BUILD_INPUTS)
    names|={profile(f)['mapping'] for f in PROFILES}
    names|={selected['master']['source_png'],selected['recipe']['path']}
    names|=compat.mf_input_paths(root)|{compat.MF_MAPPING}
    from current_plasma_projectile_compatibility import input_paths as plasma_input_paths, MAPPING as PLASMA_MAPPING
    names|=plasma_input_paths(root)|{PLASMA_MAPPING}
    from current_front_multi_compatibility import input_paths as front_multi_input_paths, MAPPING as FRONT_MULTI_MAPPING
    names|=front_multi_input_paths(root)|{FRONT_MULTI_MAPPING}
    from current_enemy_orb_compatibility import input_paths as orb_input_paths, MAPPING as ORB_MAPPING
    names|=orb_input_paths(root)|{ORB_MAPPING}
    from build_enemy_protron_p09 import input_paths as p09_input_paths
    names |= p09_input_paths(root)
    from current_protron_compatibility import input_paths as protron_input_paths, MAPPING as PROTRON_MAPPING
    names |= protron_input_paths(root) | {PROTRON_MAPPING}
    from current_sonic_compatibility import input_paths as sonic_input_paths, MAPPING as SONIC_MAPPING
    names |= sonic_input_paths(root) | {SONIC_MAPPING}
    from current_guided_compatibility import input_paths as guided_input_paths, MAPPING as GUIDED_MAPPING
    names |= guided_input_paths(root) | {GUIDED_MAPPING}
    from current_mint27_compatibility import input_paths as mint27_input_paths, MAPPING as MINT27_MAPPING
    names |= mint27_input_paths(root) | {MINT27_MAPPING}
    from current_missile_compatibility import input_paths as missile_input_paths, MAPPING as MISSILE_MAPPING
    names |= missile_input_paths(root) | {MISSILE_MAPPING}
    from current_rear_p7_compatibility import input_paths as rear_p7_input_paths, MAPPING as REAR_P7_MAPPING
    names |= rear_p7_input_paths(root) | {REAR_P7_MAPPING}
    from current_rear39_compatibility import input_paths as rear39_input_paths, MAPPING as REAR39_MAPPING
    names |= rear39_input_paths(root) | {REAR39_MAPPING}
    from current_rear1_compatibility import input_paths as rear1_input_paths, MAPPING as REAR1_MAPPING
    names |= rear1_input_paths(root) | {REAR1_MAPPING}
    from current_rear281_compatibility import input_paths as rear281_input_paths, MAPPING as REAR281_MAPPING
    names |= rear281_input_paths(root) | {REAR281_MAPPING}
    from current_newshf_compatibility import input_paths as newshf_input_paths
    names|=newshf_input_paths(root)
    names|={p.relative_to(root).as_posix() for p in (root/'src').rglob('*') if p.is_file() or p.is_symlink()}
    names|={p.relative_to(root).as_posix() for p in (root/'scripts').glob('*.py')}
    with tempfile.TemporaryDirectory(prefix='charge-body-authoring-build-') as tmp:
        work=Path(tmp)
        for key in sorted(names|set(outputs)):
            data=outputs[key] if key in outputs else read(root,key)
            p=work/key;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        subprocess.run([sys.executable,str(work/REBUILD),'--root',str(work),'--output',str(work/RUNTIME)],check=True,stdout=subprocess.DEVNULL)
        outputs[RUNTIME]=(work/RUNTIME).read_bytes()
    return outputs


def charge_plan(root,outputs,raw):
    import current_sidekick_body_compatibility as compat
    request=compat._charge_parse(raw)
    names={request['master']['source_png'],request['recipe']['path'],compat.CHARGE_SELECTION,compat.CHARGE_MAPPING,BINDING,RUNTIME}
    names|={p.relative_to(root).as_posix() for p in (root/'scripts').glob('*.py')}
    names|=compat.mf_input_paths(root)|{compat.MF_MAPPING}
    from current_plasma_projectile_compatibility import input_paths as plasma_input_paths, MAPPING as PLASMA_MAPPING
    names|=plasma_input_paths(root)|{PLASMA_MAPPING}
    from current_front_multi_compatibility import input_paths as front_multi_input_paths, MAPPING as FRONT_MULTI_MAPPING
    names|=front_multi_input_paths(root)|{FRONT_MULTI_MAPPING}
    from current_enemy_orb_compatibility import input_paths as orb_input_paths, MAPPING as ORB_MAPPING
    names|=orb_input_paths(root)|{ORB_MAPPING}
    from build_enemy_protron_p09 import input_paths as p09_input_paths
    names |= p09_input_paths(root)
    from current_protron_compatibility import input_paths as protron_input_paths, MAPPING as PROTRON_MAPPING
    names |= protron_input_paths(root) | {PROTRON_MAPPING}
    from current_sonic_compatibility import input_paths as sonic_input_paths, MAPPING as SONIC_MAPPING
    names |= sonic_input_paths(root) | {SONIC_MAPPING}
    from current_guided_compatibility import input_paths as guided_input_paths, MAPPING as GUIDED_MAPPING
    names |= guided_input_paths(root) | {GUIDED_MAPPING}
    from current_mint27_compatibility import input_paths as mint27_input_paths, MAPPING as MINT27_MAPPING
    names |= mint27_input_paths(root) | {MINT27_MAPPING}
    from current_missile_compatibility import input_paths as missile_input_paths, MAPPING as MISSILE_MAPPING
    names |= missile_input_paths(root) | {MISSILE_MAPPING}
    from current_rear_p7_compatibility import input_paths as rear_p7_input_paths, MAPPING as REAR_P7_MAPPING
    names |= rear_p7_input_paths(root) | {REAR_P7_MAPPING}
    from current_rear39_compatibility import input_paths as rear39_input_paths, MAPPING as REAR39_MAPPING
    names |= rear39_input_paths(root) | {REAR39_MAPPING}
    from current_rear1_compatibility import input_paths as rear1_input_paths, MAPPING as REAR1_MAPPING
    names |= rear1_input_paths(root) | {REAR1_MAPPING}
    from current_rear281_compatibility import input_paths as rear281_input_paths, MAPPING as REAR281_MAPPING
    names |= rear281_input_paths(root) | {REAR281_MAPPING}
    from current_newshf_compatibility import input_paths as newshf_input_paths
    names|=newshf_input_paths(root)
    # Bind every installed destination and all request/tool inputs. Source and
    # gameplay authority are reverified on every derive, never cached by mtime.
    return dict(schema='opentyrian-current-charge-body-stage-v1',request_sha256=sha(raw),inputs_sha256={p:fingerprint(root,p) for p in sorted(names)},files=[dict(path=p,before_sha256=fingerprint(root,p),after_sha256=sha(data),bytes=len(data)) for p,data in sorted(outputs.items())])


def charge_stage(root,selected,destination):
    validate_stage_location(root,destination)
    if destination.exists():raise ValueError('Stage destination must be new')
    raw=selected.read_bytes();outputs=charge_derive(root,raw);plan=charge_plan(root,outputs,raw)
    destination.mkdir(parents=True)
    for name,data in outputs.items():
        p=destination/'files'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    (destination/'request.json').write_bytes(raw)
    (destination/'plan.json').write_bytes(encoded(plan));return plan


def charge_apply(root,destination):
    validate_stage_location(root,destination)
    import current_sidekick_body_compatibility as compat
    plan=compat._charge_parse(compat._charge_read(destination,'plan.json',128*1024));raw=compat._charge_read(destination,'request.json',128*1024)
    outputs=charge_derive(root,raw);expected=charge_plan(root,outputs,raw)
    if json.dumps(plan,sort_keys=True)!=json.dumps(expected,sort_keys=True):raise ValueError('Stale or modified Charge plan/current inputs; restage explicitly')
    for name,data in outputs.items():
        if read(destination,'files/'+name)!=data:raise ValueError('Modified staged Charge bytes: '+name)
        temp=contained_file(root,name+'.craft267-tmp')
        if temp.exists() or temp.is_symlink():raise ValueError('Unexpected Charge temporary output')
    # Existing preflighted batch helper provides handled-failure rollback.
    from build_current_craft267 import replace_batch
    replace_batch(root,outputs)
    return expected


def charge_check(root):
    import current_sidekick_body_compatibility as compat
    compat.charge_load(root)
    outputs=charge_derive(root,read(root,compat.CHARGE_SELECTION))
    bad=[p for p,data in outputs.items() if fingerprint(root,p)!=sha(data)]
    if bad:raise ValueError('Stale/missing current Charge outputs: '+', '.join(bad))
    return dict(status='PASS',resources=9,editable_masters=1,logical_consumers=9,global_registry_additions=0,historical_outputs='untouched')


# Four independent approved sources, deliberately separate from the old six.
def mf_derive(root,raw):
    import current_sidekick_body_compatibility as compat
    selected,blobs=compat.mf_generate(root,raw)
    registry=json.loads(read(root,REGISTRY));verify_authority(root,registry)
    if read(root,LEGACY_HEADER)!=legacy_header(registry['resources']):
        raise ValueError('Unrelated legacy art pins changed')
    outputs={compat.MF_SELECTION:encoded(selected)};rows=[]
    for identity,blob in blobs.items():
        path=compat.MF_ROOT+'/'+compat.mf_name(identity);outputs[path]=blob
        rows.append(dict(identity=identity,source_path=path,destination='assets/gameplay/'+compat.mf_name(identity),sha256=sha(blob)))
    outputs[compat.MF_MAPPING]=encoded(dict(schema='opentyrian-current-mint-front-body-compatibility-v1',selection=compat.MF_SELECTION,version=selected['version'],files=rows))
    old=json.loads(read(root,RUNTIME));base=json.loads(read(root,'packaging/runtime-assets-public63a89b3.json'))
    for row in old['files']:
        if row['source_path'] not in outputs:checked_source(contained_file(root,row['source_path']),row)
    names={row['source_path'] for row in old['files']+base['files']}
    names|={REGISTRY,BINDING,'packaging/runtime-assets-public63a89b3.json','packaging/shop-static-approved-v1.json',MAPPING,'packaging/current-hud-compatibility.json','packaging/current-tank-shell-compatibility.json','packaging/current-enemy-energy-compatibility.json','packaging/current-craft267-compatibility.json'}|set(BUILD_INPUTS)
    names|={profile(f)['mapping'] for f in PROFILES}
    names|=compat.charge_input_paths(root)|{compat.CHARGE_MAPPING}
    from current_plasma_projectile_compatibility import input_paths as plasma_input_paths, MAPPING as PLASMA_MAPPING
    names|=plasma_input_paths(root)|{PLASMA_MAPPING}
    from current_front_multi_compatibility import input_paths as front_multi_input_paths, MAPPING as FRONT_MULTI_MAPPING
    names|=front_multi_input_paths(root)|{FRONT_MULTI_MAPPING}
    from current_enemy_orb_compatibility import input_paths as orb_input_paths, MAPPING as ORB_MAPPING
    names|=orb_input_paths(root)|{ORB_MAPPING}
    from build_enemy_protron_p09 import input_paths as p09_input_paths
    names |= p09_input_paths(root)
    from current_protron_compatibility import input_paths as protron_input_paths, MAPPING as PROTRON_MAPPING
    names |= protron_input_paths(root) | {PROTRON_MAPPING}
    from current_sonic_compatibility import input_paths as sonic_input_paths, MAPPING as SONIC_MAPPING
    names |= sonic_input_paths(root) | {SONIC_MAPPING}
    from current_guided_compatibility import input_paths as guided_input_paths, MAPPING as GUIDED_MAPPING
    names |= guided_input_paths(root) | {GUIDED_MAPPING}
    from current_mint27_compatibility import input_paths as mint27_input_paths, MAPPING as MINT27_MAPPING
    names |= mint27_input_paths(root) | {MINT27_MAPPING}
    from current_missile_compatibility import input_paths as missile_input_paths, MAPPING as MISSILE_MAPPING
    names |= missile_input_paths(root) | {MISSILE_MAPPING}
    from current_rear_p7_compatibility import input_paths as rear_p7_input_paths, MAPPING as REAR_P7_MAPPING
    names |= rear_p7_input_paths(root) | {REAR_P7_MAPPING}
    from current_rear39_compatibility import input_paths as rear39_input_paths, MAPPING as REAR39_MAPPING
    names |= rear39_input_paths(root) | {REAR39_MAPPING}
    from current_rear1_compatibility import input_paths as rear1_input_paths, MAPPING as REAR1_MAPPING
    names |= rear1_input_paths(root) | {REAR1_MAPPING}
    from current_rear281_compatibility import input_paths as rear281_input_paths, MAPPING as REAR281_MAPPING
    names |= rear281_input_paths(root) | {REAR281_MAPPING}
    from current_newshf_compatibility import input_paths as newshf_input_paths
    names|=newshf_input_paths(root)
    names|={row['source_png'] for row in selected['resources']}
    names|={p.relative_to(root).as_posix() for p in (root/'src').rglob('*') if p.is_file() or p.is_symlink()}
    names|={p.relative_to(root).as_posix() for p in (root/'scripts').glob('*.py')}
    # No production source/header/binding generation: the exact current src inventory stays unchanged.
    with tempfile.TemporaryDirectory(prefix='mint-front-body-build-') as tmp:
        work=Path(tmp)
        for key in sorted(names|set(outputs)):
            data=outputs[key] if key in outputs else read(root,key)
            p=work/key;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        subprocess.run([sys.executable,str(work/REBUILD),'--root',str(work),'--output',str(work/RUNTIME)],check=True,stdout=subprocess.DEVNULL)
        outputs[RUNTIME]=(work/RUNTIME).read_bytes()
    return outputs


def mf_plan(root,outputs,raw):
    import current_sidekick_body_compatibility as compat
    selected=compat.mf_selection(root,raw)
    names={row['source_png'] for row in selected['resources']}
    names|={compat.MF_SELECTION,compat.MF_MAPPING,BINDING,RUNTIME}
    names|=compat.charge_input_paths(root)|{compat.CHARGE_MAPPING}
    from current_plasma_projectile_compatibility import input_paths as plasma_input_paths, MAPPING as PLASMA_MAPPING
    names|=plasma_input_paths(root)|{PLASMA_MAPPING}
    from current_front_multi_compatibility import input_paths as front_multi_input_paths, MAPPING as FRONT_MULTI_MAPPING
    names|=front_multi_input_paths(root)|{FRONT_MULTI_MAPPING}
    from current_enemy_orb_compatibility import input_paths as orb_input_paths, MAPPING as ORB_MAPPING
    names|=orb_input_paths(root)|{ORB_MAPPING}
    from build_enemy_protron_p09 import input_paths as p09_input_paths
    names |= p09_input_paths(root)
    from current_protron_compatibility import input_paths as protron_input_paths, MAPPING as PROTRON_MAPPING
    names |= protron_input_paths(root) | {PROTRON_MAPPING}
    from current_sonic_compatibility import input_paths as sonic_input_paths, MAPPING as SONIC_MAPPING
    names |= sonic_input_paths(root) | {SONIC_MAPPING}
    from current_guided_compatibility import input_paths as guided_input_paths, MAPPING as GUIDED_MAPPING
    names |= guided_input_paths(root) | {GUIDED_MAPPING}
    from current_mint27_compatibility import input_paths as mint27_input_paths, MAPPING as MINT27_MAPPING
    names |= mint27_input_paths(root) | {MINT27_MAPPING}
    from current_missile_compatibility import input_paths as missile_input_paths, MAPPING as MISSILE_MAPPING
    names |= missile_input_paths(root) | {MISSILE_MAPPING}
    from current_rear_p7_compatibility import input_paths as rear_p7_input_paths, MAPPING as REAR_P7_MAPPING
    names |= rear_p7_input_paths(root) | {REAR_P7_MAPPING}
    from current_rear39_compatibility import input_paths as rear39_input_paths, MAPPING as REAR39_MAPPING
    names |= rear39_input_paths(root) | {REAR39_MAPPING}
    from current_rear1_compatibility import input_paths as rear1_input_paths, MAPPING as REAR1_MAPPING
    names |= rear1_input_paths(root) | {REAR1_MAPPING}
    from current_rear281_compatibility import input_paths as rear281_input_paths, MAPPING as REAR281_MAPPING
    names |= rear281_input_paths(root) | {REAR281_MAPPING}
    from current_newshf_compatibility import input_paths as newshf_input_paths
    names|=newshf_input_paths(root)
    names|={p.relative_to(root).as_posix() for p in (root/'scripts').glob('*.py')}
    return dict(schema='opentyrian-current-mint-front-body-stage-v1',request_sha256=sha(raw),inputs_sha256={p:fingerprint(root,p) for p in sorted(names)},files=[dict(path=p,before_sha256=fingerprint(root,p),after_sha256=sha(data),bytes=len(data)) for p,data in sorted(outputs.items())])


def mf_stage(root,selected,destination):
    from build_current_craft267 import external
    import current_sidekick_body_compatibility as compat
    external(root,destination)
    if destination.exists():raise ValueError('Stage destination must be new')
    raw=compat.mf_read(selected.absolute().parent,selected.name,128*1024)
    outputs=mf_derive(root,raw);plan=mf_plan(root,outputs,raw)
    destination.mkdir(parents=True)
    for name,data in outputs.items():
        p=destination/'files'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    (destination/'request.json').write_bytes(raw)
    (destination/'plan.json').write_bytes(encoded(plan));return plan


def mf_apply(root,destination):
    from build_current_craft267 import external,replace_batch,SUFFIX
    from current_craft267_compatibility import path
    import current_sidekick_body_compatibility as compat
    external(root,destination)
    plan=compat.mf_parse(compat.mf_read(destination,'plan.json',128*1024))
    raw=compat.mf_read(destination,'request.json',128*1024)
    outputs=mf_derive(root,raw);expected=mf_plan(root,outputs,raw)
    # Canonical JSON keeps booleans/floats distinct from integer plan fields.
    if json.dumps(plan,sort_keys=True)!=json.dumps(expected,sort_keys=True):
        raise ValueError('Stale or modified Mint/Front plan/current inputs; restage explicitly')
    for name,data in outputs.items():
        if compat.mf_read(destination,'files/'+name)!=data:raise ValueError('Modified staged Mint/Front bytes: '+name)
        p=path(root,name);temp=path(root,name+SUFFIX)
        if temp.exists() or temp.is_symlink():raise ValueError('Unexpected Mint/Front temporary output')
        if p.exists() and not p.is_file():raise ValueError('Nonregular Mint/Front output')
    replace_batch(root,outputs)
    return expected


def mf_check(root):
    import current_sidekick_body_compatibility as compat
    compat.mf_load(root)
    outputs=mf_derive(root,compat.mf_read(root,compat.MF_SELECTION,128*1024))
    bad=[p for p,data in outputs.items() if fingerprint(root,p)!=sha(data)]
    if bad:raise ValueError('Stale/missing current Mint/Front outputs: '+', '.join(bad))
    return dict(status='PASS',resources=4,editable_sources=4,mint_independent_phases=3,front_complete_quad_sources=1,logical_consumers=4,global_registry_additions=0,historical_outputs='untouched')


def main():
    from current_sidekick_body_compatibility import CHARGE_SELECTION,MF_SELECTION
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    p.add_argument('--family',choices=('sidekick-body','charge-body','mint-front-body'),default='sidekick-body')
    p.add_argument('mode',choices=('stage','apply','check'));p.add_argument('--selection',type=Path);p.add_argument('--stage',type=Path)
    a=p.parse_args();root=a.root.resolve()
    default,stage_fn,apply_fn,check_fn={
        'sidekick-body':(SELECTION,stage,apply,check),
        'charge-body':(CHARGE_SELECTION,charge_stage,charge_apply,charge_check),
        'mint-front-body':(MF_SELECTION,mf_stage,mf_apply,mf_check),
    }[a.family]
    if a.mode=='check':result=check_fn(root)
    else:
        if not a.stage:p.error('--stage required')
        result=stage_fn(root,a.selection or root/default,a.stage) if a.mode=='stage' else apply_fn(root,a.stage)
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
