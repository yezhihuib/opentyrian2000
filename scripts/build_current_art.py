#!/usr/bin/env python3
"""One selected semantic art version -> all declared current consumers.

stage is non-mutating; apply re-derives the exact plan and checks every old hash
before writing. check detects stale/missing outputs. No history is overwritten,
no paths deleted, no source-bank/role identity changed and no image resampling.
"""
import argparse,copy,hashlib,io,json,os,re,shutil,struct,subprocess,sys,tempfile
from pathlib import Path
from functools import lru_cache
from PIL import Image
from package_runtime import contained_file,checked_source,reparse_point
from verify_current_production import source_inventory,source_manifest_digest,BUILD_INPUTS
from current_art_policy import compatibility_name,PROFILES,ALL_IDS,profile,geometry,LEGACY_HEADER,legacy_header,APPROVED_PROVENANCE_SHA256
from current_pulse_compatibility import IDS,MAPPING,ROOT as COMPAT
SELECT='assets/hd/authoring/pulse-current.json'
REGISTRY='assets/hd/global-assets-v1/registry.json'
HEADER='src/global_asset_registry.h'
REBUILD='scripts/rebuild_recovered_runtime_manifest.py'
BINDING='packaging/current-production-validation.json'
RUNTIME='packaging/runtime-assets-v1.json'
# Immutable bounded policy after the approved Pulse base and same-value Vulcan/cash/gem
# payload macro integration, plus same-value HUD meter pin header extraction.
# Only selected art changes, never gameplay/authority.
REGISTRY_AUTHORITY_SHA256='21d0b78355542b5315df82a515f3e341a3070508bdfc414f632b1741b7682dd6'
# Exact current authority after the reviewed Plasma payload-pin extraction and
# five-file Charge body extension
# on 11a9c7f6 and the earlier two-file render correction on 6ada526. Prior foundation digest fff3fc79dc6283ea92c9b2bc20fab63c8ed53ae57967d3726e94d1a3ba997ac9
# remains historical provenance, never an alternative accepted source state.
# Charge inverse: tests/fixtures/accepted-later-changes-v1/charge-body-source.json.
# Orb opt-in payload-only inverse: tests/fixtures/accepted-later-changes-v1/enemy-orb-source.json.
# Front Multi inverse: tests/fixtures/accepted-later-changes-v1/front-multi-source.json.
# Plasma inverse: tests/fixtures/accepted-later-changes-v1/plasma-projectile-source.json.
# The finite inverse is pinned in tests/fixtures/accepted-later-changes-v1/render-boundaries-source.json.
# Also includes the reviewed default-off NEWSHF compositor; only its generated
# nine-resource header is mutable, with strict selected-PNG derivation below.
# Enemy reuse adds exactly three default-off semantic modules plus six guarded
# hook edits (enemy-reuse-source.json exact inverse); no artwork authority change.
# Prior gameplay/build digests: 0fcf5a1e252b888b99389e27f1cd3f5b93cec2af6914ada5382370b6d3e2c7c8 /
# 537111f6f8f9a1bd6b0efce18453669d72ac3e8df9062cab010b46cc4e48e7c6.
# Prior binary-alpha gameplay authority: 9855830c5b06b02c9e4ccd0952606f98357b6e2a0d2477f09e82652d2494edd3.
# Only reviewed change is exact global_newshf_mirror.inc nonopaque-foreign guard;
# finite inverse: tests/fixtures/accepted-later-changes-v1/newshf168-soft-alpha-source.json.
# Prior V4 gameplay authority: c1bc7f29b1082c7c40f537593ab23c72fc30a087275604735980ee2a27dac001.
# Exact P05 observational extension: enemy-green-reuse-source.json; no new asset authority.
# Exact observer six-file delta and two immutable modules: enemy-reuse-observe-source.json.
# Prior authority 7bf2767a8b412779de16c250b3d6240614911ed5da8801bab84058cecc14d6ed remains historical only.
# Controlled probe exact four-file/two-module extension: enemy-controlled-probe-source.json.
# Prior observer authority e2651e92494f25a0070b9b28e46806aad542bc4d1cc59a0230f913d8658c382d remains historical only.
# Normal observer exact three-source inverse: normal-observer-surface-source.json.
# Current Sonic payload-only extraction: tests/current_sonic_source_projection.json.
# Current Guided two-pin extraction: tests/current_guided_source_projection.json.
# Current NEWSHF generated-header include only: tests/current_newshf_source_projection.json.
# Current Mint27 payload-only extraction: tests/current_mint27_source_projection.json.
# Prior source authority 8ba6fed3c0c0a74b2388d5b54d9b7d9edb051690cdcb94c30626ac5cd7b758fe remains historical only.
GAMEPLAY_SOURCE_SHA256='c7ee2f9abc585391159ac40910c3a7417ac1e08422dc6aca1f7521f2f5c59e6f'
BUILD_INPUT_SHA256='dcc93711da1cb8eb764582d33f81b80c8474a0009271b682ed235548314a3800'

def sha(data):return hashlib.sha256(data).hexdigest()
def encoded(obj):return (json.dumps(obj,indent=2)+'\n').encode()
def read(root,name):
    p=contained_file(root,name)
    if not p.is_file():raise ValueError('Missing regular input: '+name)
    return p.read_bytes()
def fingerprint(root,name):
    p=contained_file(root,name)
    if not p.exists():return None
    return sha(read(root,name))
def fnv(data):
    # Retain the existing iterable interface without caching mutable inputs.
    if type(data) is bytes:return _fnv_bytes(data)
    return _fnv_bytes.__wrapped__(data)

@lru_cache(maxsize=128)
def _fnv_bytes(data):
    # Cache immutable payload bytes, never paths, mtimes or validation results.
    # Every caller still rereads and validates its current source/consumer.
    h=14695981039346656037
    for v in data:h=((h^v)*1099511628211)&((1<<64)-1)
    return f'{h:016x}'
def selection(root,raw,family='pulse'):
    policy=profile(family);IDS=policy['ids']
    j=json.loads(raw)
    if set(j)-{'schema','version','note','resources'} or j.get('schema')!=f'opentyrian-current-{family}-authoring-v1':raise ValueError('Unknown selection schema/fields')
    if not isinstance(j.get('version'),str) or not j['version'] or len(j['version'])>128:raise ValueError('Invalid version')
    rows=j.get('resources')
    if not isinstance(rows,list) or tuple(x.get('identity') for x in rows)!=IDS:raise ValueError('Expected exact ordered family identities')
    for row in rows:
        if set(row)!={'identity','source_png','source_sha256'} or type(row['identity']) is not int:raise ValueError('Invalid selected source')
        digest=row['source_sha256']
        if not isinstance(digest,str) or not re.fullmatch('[0-9a-f]{64}',digest):raise ValueError('Invalid source SHA256')
        if sha(read(root,row['source_png']))!=digest:raise ValueError('Selected source changed: '+row['source_png'])
    return j

def verify_authority(root,registry,family='pulse'):
    fixed=copy.deepcopy(registry)
    for row in fixed['resources']:
        if row['identity'] in ALL_IDS:
            for key in ('path','sha256','payload_fnv64','provenance'):row.pop(key,None)
    if source_manifest_digest(fixed)!=REGISTRY_AUTHORITY_SHA256:
        raise ValueError('Registry role/source authority or unrelated resource changed')
    sources=source_inventory(root);sources.pop(HEADER,None);sources.pop(LEGACY_HEADER,None);sources.pop('src/current_hud_payload_pins.h',None);sources.pop('src/current_tank_shell_payload_pins.h',None);sources.pop('src/current_enemy_energy_payload_pins.h',None);sources.pop('src/current_sidekick_body_payload_pins.h',None);sources.pop('src/current_plasma_projectile_payload_pins.h',None);sources.pop('src/hd_front_multi_current.h',None);sources.pop('src/current_enemy_orb_payload_pins.h',None);sources.pop('src/newshf_hd_assets.h',None);sources.pop('src/current_enemy_protron_payload_pins.h',None);sources.pop('src/current_protron_payload_pins.h',None);sources.pop('src/current_sonic_payload_pins.h',None);sources.pop('src/current_guided_payload_pins.h',None);sources.pop('src/current_newshf_hd_assets.h',None);sources.pop('src/current_mint27_payload_pins.h',None)
    if source_manifest_digest(sources)!=GAMEPLAY_SOURCE_SHA256:
        raise ValueError('Unrelated gameplay source changed')
    inputs={p:sha(read(root,p)) for p in BUILD_INPUTS}
    if source_manifest_digest(inputs)!=BUILD_INPUT_SHA256:
        raise ValueError('Build inputs changed')

    # Prove the current Sonic header here so unrelated builders cannot bless
    # stale payload pins, including the separately bounded runtime quartet.
    # Its own finite builder rederives the edited candidate before this call.
    if family != 'sonic':
        from current_sonic_compatibility import load as sonic_load
        sonic_load(root)

    if family != 'mint27':
        from current_mint27_compatibility import load as mint27_load
        mint27_load(root)

    if family != 'guided':
        from current_guided_compatibility import load as guided_load
        guided_load(root)

    from build_newshf_hd import load as newshf_load
    newshf_load(root)  # Frozen nine-pose history is always independently validated.
    if family != 'newshf':
        from current_newshf_compatibility import load as current_newshf_load
        current_newshf_load(root)
    from current_tank_shell_compatibility import load as tank_shell_compatibility
    tank_shell_compatibility(root)
    from current_enemy_energy_compatibility import load as energy_compatibility
    energy_compatibility(root)
    from current_sidekick_body_compatibility import load as sidekick_body_compatibility
    sidekick_body_compatibility(root)
    from current_craft267_compatibility import load as craft267_compatibility
    craft267_compatibility(root)
    by_id={r['identity']:r for r in registry['resources']}
    for other in PROFILES:
        selected=selection(root,read(root,profile(other)['selection']),other)
        for row in selected['resources']:
            data,payload=source_blob(root,row)
            current=by_id[row['identity']]
            if other!=family and (current['sha256']!=sha(data) or current['path']!='content/'+sha(data)+'.hda' or
                    current['payload_fnv64']!=fnv(payload) or current['bytes']!=len(data)):
                raise ValueError('Unrelated selected family resource changed')
            provenance=current.get('provenance',{})
            approved=sha(json.dumps(provenance,sort_keys=True,separators=(',',':')).encode())==APPROVED_PROVENANCE_SHA256[row['identity']]
            generated=(set(provenance)=={'selection','revision','source_png','source_png_sha256','prior_hda_sha256'} and
                       provenance.get('selection')==profile(other)['selection'] and provenance.get('revision')==selected['version'] and
                       isinstance(provenance.get('prior_hda_sha256'),str) and re.fullmatch('[0-9a-f]{64}',provenance['prior_hda_sha256']))
            if (not (approved or generated) or provenance.get('source_png')!=row['source_png'] or
                    provenance.get('source_png_sha256')!=row['source_sha256']):
                raise ValueError('Unrelated selected family provenance changed')
            if other!=family and read(root,'assets/hd/global-assets-v1/'+current['path'])!=data:
                raise ValueError('Unrelated selected family bytes changed')

def source_blob(root,row):
    raw=read(root,row['source_png'])
    if len(raw)>16*1024*1024:raise ValueError('Oversize source PNG')
    header=geometry(row['identity'])
    size=(header[1]*header[2],header[1]*header[3])
    with Image.open(io.BytesIO(raw)) as im:
        if im.format!='PNG' or im.mode!='RGBA' or im.size!=size or getattr(im,'n_frames',1)!=1:
            raise ValueError(f'Expected single {size[0]}x{size[1]} straight RGBA PNG')
        # Phase268 has an opaque original tile but explicitly transparent art.
        # This semantic constraint cannot be overridden by a selected version.
        if row['identity']==1060268 and im.getchannel('A').getextrema()!=(0,0):
            raise ValueError('Shield phase268 must remain authored transparent')
        payload=im.tobytes()
    return b'HDR1'+struct.pack('<6I',*geometry(row['identity']))+payload,payload


def validate_stage_location(root,destination):
    absolute=destination.absolute()
    if any(p.is_symlink() for p in (absolute,*absolute.parents)):
        raise ValueError('Symlink stage or parent')
    if any(reparse_point(p) for p in (absolute,*absolute.parents)):
        raise ValueError('Reparse stage or parent')
    if absolute.resolve().is_relative_to(root.resolve()):
        raise ValueError('Stage must be outside repository and historical resources')

def derive(root,selected_raw,family='pulse'):
    policy=profile(family);IDS=policy['ids'];SELECT=policy['selection'];MAPPING=policy['mapping'];COMPAT=policy['compatibility']
    selected=selection(root,selected_raw,family);registry=json.loads(read(root,REGISTRY));before=copy.deepcopy(registry)
    verify_authority(root,registry,family)
    if len(registry['resources'])!=120:raise ValueError('Unexpected global registry scope')
    by_id={r['identity']:r for r in registry['resources']}
    outputs={SELECT:selected_raw};compat=[]
    for row in selected['resources']:
        i=row['identity'];raw=read(root,row['source_png'])
        data,payload=source_blob(root,row);header=geometry(i)
        if by_id[i]['header_u32']!=header:raise ValueError('Fixed art geometry/anchor changed')
        digest=sha(data);r=by_id[i]
        r.update(path='content/'+digest+'.hda',sha256=digest,bytes=len(data),payload_fnv64=fnv(payload))
        # Preserve historical approved provenance byte-for-byte when selecting it.
        if r.get('provenance',{}).get('source_png')!=row['source_png'] or r.get('provenance',{}).get('source_png_sha256')!=sha(raw):
            r['provenance']={'selection':SELECT,'revision':selected['version'],'source_png':row['source_png'],'source_png_sha256':sha(raw),'prior_hda_sha256':before['resources'][registry['resources'].index(r)]['sha256']}
        elif r.get('provenance',{}).get('selection')==SELECT:
            r['provenance']['revision']=selected['version']
        outputs['assets/hd/global-assets-v1/'+r['path']]=data
        path=f'{COMPAT}/{compatibility_name(i)}';outputs[path]=data
        compat.append(dict(identity=i,source_path=path,destination=f'assets/gameplay/{compatibility_name(i)}',sha256=digest))
    outputs[REGISTRY]=encoded(registry)
    outputs[LEGACY_HEADER]=legacy_header(registry['resources'])
    outputs[MAPPING]=encoded({'schema':f'opentyrian-current-{family}-compatibility-v1','selection':SELECT,'version':selected['version'],'files':compat})
    script=read(root,REBUILD).decode()
    script,n=re.subn(r"GLOBAL_REGISTRY_SHA256 = '[0-9a-f]{64}'",f"GLOBAL_REGISTRY_SHA256 = '{sha(outputs[REGISTRY])}'",script)
    if n!=1:raise ValueError('Expected one packaging registry pin')
    outputs[REBUILD]=script.encode()
    # Minimal isolated rebuild root: only declared package inputs and source pins.
    with tempfile.TemporaryDirectory(prefix='pulse-authoring-build-') as temp:
        work=Path(temp)
        old_runtime=json.loads(read(root,RUNTIME));old_base=json.loads(read(root,'packaging/runtime-assets-public63a89b3.json'))
        names={r['source_path'] for r in old_runtime['files']}|{r['source_path'] for r in old_base['files']}
        names|={REGISTRY,BINDING,'packaging/runtime-assets-public63a89b3.json','packaging/shop-static-approved-v1.json'}|set(BUILD_INPUTS)
        for supported in PROFILES:
            names.add(profile(supported)['mapping'])
        names.add('packaging/current-hud-compatibility.json')
        names.add('packaging/current-tank-shell-compatibility.json')
        names.add('packaging/current-enemy-energy-compatibility.json')
        names.add('packaging/current-sidekick-body-compatibility.json')
        names.add('packaging/current-craft267-compatibility.json')
        names|={p.relative_to(root).as_posix() for p in (root/'src').rglob('*') if p.is_file() or p.is_symlink()}
        names|={p.relative_to(root).as_posix() for p in (root/'scripts').glob('*.py')}
        from current_sidekick_body_compatibility import independent_input_paths
        names|=independent_input_paths(root)
        # Verify existing runtime except allowed stale current generated outputs.
        generated_old={SELECT,REGISTRY,HEADER,LEGACY_HEADER,REBUILD,BINDING,RUNTIME,MAPPING}|{f'{COMPAT}/{compatibility_name(i)}' for i in IDS}
        pulse_paths={'assets/hd/global-assets-v1/'+r['path'] for r in before['resources'] if r['identity'] in IDS}
        for row in old_runtime['files']:
            if row['source_path'] not in generated_old|pulse_paths:checked_source(contained_file(root,row['source_path']),row)
        for name in sorted(names):
            if name in outputs:continue
            data=read(root,name);p=work/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        for name,data in outputs.items():
            p=work/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        subprocess.run([sys.executable,str(work/'scripts/build_global_registry_header.py'),'--registry',str(work/REGISTRY),'--output',str(work/HEADER)],check=True,stdout=subprocess.DEVNULL)
        outputs[HEADER]=(work/HEADER).read_bytes()
        binding=json.loads(read(root,BINDING));binding['production_commit']=None
        binding['source_sha256']=source_inventory(work);binding['production_source_manifest_sha256']=source_manifest_digest(binding['source_sha256'])
        binding['scope']='Exact current source binding including the separately reviewed Charge body extension, Plasma projectile and Front Multi payload-pin extractions. Build/package consistency only; historical receipts retain their original scope.'
        outputs[BINDING]=(json.dumps(binding,indent=2,sort_keys=True)+'\n').encode();(work/BINDING).write_bytes(outputs[BINDING])
        subprocess.run([sys.executable,str(work/REBUILD),'--root',str(work),'--output',str(work/RUNTIME)],check=True,stdout=subprocess.DEVNULL)
        outputs[RUNTIME]=(work/RUNTIME).read_bytes()
    return outputs

def make_plan(root,outputs,selected_raw,family='pulse'):
    from current_sidekick_body_compatibility import authoring_input_fingerprints
    changes=[{'path':p,'before_sha256':fingerprint(root,p),'after_sha256':sha(data),'bytes':len(data)} for p,data in sorted(outputs.items())]
    return {'inputs_sha256':authoring_input_fingerprints(root),'schema':f'opentyrian-current-{family}-stage-v1','selection_sha256':sha(selected_raw),'files':changes,'scope':f'Exactly {len(profile(family)["ids"])} {family} art identities and declared generated consumers. No deletions/history or gameplay changes.'}

def stage(root,selection_file,destination,family='pulse'):
    validate_stage_location(root,destination)
    if destination.exists():raise ValueError('Stage destination must be new')
    raw=selection_file.read_bytes();outputs=derive(root,raw,family);plan=make_plan(root,outputs,raw,family)
    destination.mkdir(parents=True)
    for name,data in outputs.items():
        p=destination/'files'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    (destination/'plan.json').write_bytes(encoded(plan));return plan

def apply(root,destination,family='pulse'):
    SELECT=profile(family)['selection']
    validate_stage_location(root,destination)
    if destination.is_symlink():raise ValueError('Symlink stage')
    plan=json.loads(read(destination,'plan.json'));raw=read(destination,'files/'+SELECT)
    outputs=derive(root,raw,family);expected=make_plan(root,outputs,raw,family)
    if plan!=expected:raise ValueError('Stale or modified plan/current source; restage explicitly')
    for name,data in outputs.items():
        if read(destination,'files/'+name)!=data:raise ValueError('Modified staged bytes: '+name)
        temporary=contained_file(root,name).with_name(Path(name).name+'.pulse-tmp')
        if temporary.exists() or temporary.is_symlink():raise ValueError('Unexpected temporary output')
    # All source/old/stage checks pass before the first write. Do not remove files.
    for name,data in outputs.items():
        p=contained_file(root,name);p.parent.mkdir(parents=True,exist_ok=True)
        if p.exists() and p.read_bytes()==data:continue
        temporary=p.with_name(p.name+'.pulse-tmp')
        if temporary.exists() or temporary.is_symlink():raise ValueError('Unexpected temporary output')
        with temporary.open('xb') as f:f.write(data)
        os.replace(temporary,p)
    return expected

def check(root,family='pulse'):
    SELECT=profile(family)['selection']
    raw=read(root,SELECT);outputs=derive(root,raw,family)
    bad=[p for p,data in outputs.items() if fingerprint(root,p)!=sha(data)]
    if bad:raise ValueError('Stale/missing current consumers: '+', '.join(bad))
    return {'status':'PASS','resources':len(profile(family)['ids']),'current_consumers':'global battle, SHOP, selected legacy compatibility package','historical_outputs':'untouched'}

def main(family='pulse'):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--family',choices=tuple(PROFILES),default=family);p.add_argument('mode',choices=['stage','apply','check']);p.add_argument('--selection',type=Path);p.add_argument('--stage',type=Path);a=p.parse_args();root=a.root.resolve();family=a.family;SELECT=profile(family)['selection']
    if a.mode=='check':result=check(root,family)
    else:
        if not a.stage:p.error('--stage required')
        result=stage(root,a.selection or root/SELECT,a.stage,family) if a.mode=='stage' else apply(root,a.stage,family)
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
