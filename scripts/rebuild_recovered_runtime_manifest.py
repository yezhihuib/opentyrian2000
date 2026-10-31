#!/usr/bin/env python3
"""Extend the pinned public runtime allowlist with explicitly reconstructed work.

No network, downloads, deletions, or inferred assets. Output is mandatory and
must not replace the input manifest. Every original non-launcher row is verified
before it can enter the new manifest. Reconstructed resources retain new hashes.
"""
import argparse, hashlib, json
from verify_current_production import verify
from current_art_compatibility import load as current_art_compatibility
from current_art_policy import PROFILES
from current_hud_compatibility import load as current_hud_compatibility
from current_tank_shell_compatibility import load as current_tank_shell_compatibility
from current_enemy_energy_compatibility import load as current_enemy_energy_compatibility
from current_sidekick_body_compatibility import load as current_sidekick_body_compatibility
from current_craft267_compatibility import load as current_craft267_compatibility
GLOBAL_REGISTRY_SHA256 = 'b224adfc0b12aee5a4753e32aa12e30c8594eb4237727a983148776239162860'
from pathlib import Path

def pins(path):
    if path.is_symlink() or not path.is_file():
        raise ValueError('Expected regular selected file: '+str(path))
    data=path.read_bytes()
    if len(data)>64*1024*1024: raise ValueError('Oversized selected file')
    return len(data),hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest(),hashlib.sha256(data).hexdigest()

def approved_static(root):
    """Use reviewed input pins, never metadata from the output being rebuilt."""
    approval=json.loads((root/'packaging/shop-static-approved-v1.json').read_text())
    if approval['schema']!='opentyrian-approved-shop-static-v1':
        raise ValueError('Unexpected static approval schema')
    expected={f'assets/shop-static-v1/shop-static-newsh1-quad{q}-v1.hda' for q in (169,235,199)}
    if len(approval['files'])!=3 or {r['source_path'] for r in approval['files']}!=expected:
        raise ValueError('Expected exact three approved static resources')
    for row in approval['files']:
        if (row['destination']!='assets/startup/'+Path(row['source_path']).name or
                row['group']!='shop' or row['revision']!='local-user-accepted-static-source-quad'):
            raise ValueError('Unexpected static approval metadata')
        if pins(root/row['source_path'])!=(row['bytes'],row['git_blob'],row['sha256']):
            raise ValueError('Approved static content mismatch: '+row['source_path'])
    if set(approval['source_revision'])!={'shop_static_art'}:
        raise ValueError('Unexpected static source revision keys')
    return approval

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    ap.add_argument('--base-manifest',type=Path)
    ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();root=a.root.resolve();base=(a.base_manifest or root/'packaging/runtime-assets-public63a89b3.json').resolve()
    if a.output.resolve()==base:raise ValueError('Output must not overwrite pinned base manifest')
    current=json.loads((root/'packaging/current-production-validation.json').read_text())
    verify(root,current)
    j=json.loads(base.read_text());rows={}
    art_compat={}
    for family in PROFILES:
        for destination,row in current_art_compatibility(root,family).items():
            if destination in art_compat:raise ValueError('Current art compatibility collision')
            art_compat[destination]=dict(row,authoring_family=family)
    for destination,row in current_tank_shell_compatibility(root).items():
        if destination in art_compat:raise ValueError('Legacy/global compatibility collision')
        art_compat[destination]=dict(row,authoring_family='tank-shell')
    for destination,row in current_enemy_energy_compatibility(root).items():
        if destination in art_compat:raise ValueError('Legacy/global compatibility collision')
        art_compat[destination]=dict(row,authoring_family='enemy-energy')
    for destination,row in current_sidekick_body_compatibility(root).items():
        if destination in art_compat:raise ValueError('Legacy/global compatibility collision')
        art_compat[destination]=dict(row,authoring_family='sidekick-body')
    for destination,row in current_craft267_compatibility(root).items():
        if destination in art_compat:raise ValueError('Legacy/global compatibility collision')
        art_compat[destination]=dict(row,authoring_family='craft267')
    from current_sidekick_body_compatibility import mf_load
    for destination,row in mf_load(root).items():
        if destination in art_compat:raise ValueError('Mint/Front compatibility collision')
        art_compat[destination]=dict(row,authoring_family='mint-front-body')
    from current_plasma_projectile_compatibility import load as plasma_projectile_load
    for destination,row in plasma_projectile_load(root).items():
        if destination in art_compat:raise ValueError('Plasma projectile compatibility collision')
        art_compat[destination]=dict(row,authoring_family='plasma-projectile')
    from current_front_multi_compatibility import load as front_multi_load
    for destination,row in front_multi_load(root).items():
        if destination in art_compat:raise ValueError('Front Multi compatibility collision')
        art_compat[destination]=dict(row,authoring_family='front-multi')
    from current_enemy_orb_compatibility import load as enemy_orb_load, ORDINARY_IDS
    for destination,row in enemy_orb_load(root).items():
        # Role142 remains opt-in; it must never enter the default runtime.
        if row['identity'] not in ORDINARY_IDS:continue
        if destination in art_compat:raise ValueError('Enemy orb compatibility collision')
        art_compat[destination]=dict(row,authoring_family='enemy-orb')
    from current_guided_compatibility import load as guided_load
    for destination,row in guided_load(root).items():
        if destination in art_compat:raise ValueError('Guided compatibility collision')
        art_compat[destination]=dict(row,authoring_family='guided')
    from current_mint27_compatibility import load as mint27_load
    for destination,row in mint27_load(root).items():
        if destination in art_compat:raise ValueError('Mint27 compatibility collision')
        art_compat[destination]=dict(row,authoring_family='mint27')
    from current_missile_compatibility import load as missile_load
    for destination,row in missile_load(root).items():
        if destination in art_compat:raise ValueError('Missile compatibility collision')
        art_compat[destination]=dict(row,authoring_family='missile')
    from current_rear_p7_compatibility import load as rear_p7_load
    for destination,row in rear_p7_load(root).items():
        if destination in art_compat:raise ValueError('Rear P7 compatibility collision')
        art_compat[destination]=dict(row,authoring_family='rear-p7')
    from current_rear39_compatibility import load as rear39_load
    for destination,row in rear39_load(root).items():
        if destination in art_compat:raise ValueError('Rear39 compatibility collision')
        art_compat[destination]=dict(row,authoring_family='rear39')
    from current_rear1_compatibility import load as rear1_load
    for destination,row in rear1_load(root).items():
        if destination in art_compat:raise ValueError('Rear1 compatibility collision')
        art_compat[destination]=dict(row,authoring_family='rear1')
    from current_rear281_compatibility import load as rear281_load
    for destination,row in rear281_load(root).items():
        if destination in art_compat:raise ValueError('Rear281 compatibility collision')
        art_compat[destination]=dict(row,authoring_family='rear281')
    from current_rear_lobes_compatibility import load as rear_lobes_load
    for destination,row in rear_lobes_load(root).items():
        if destination in art_compat:raise ValueError('Rear lobes compatibility collision')
        art_compat[destination]=dict(row,authoring_family='rear-lobes')
    # Sonic is a separately bounded additive transport family, not a relaxed
    # historical art consumer. Its loader also rederives pixels and header pins.
    from current_sonic_compatibility import load as sonic_load
    sonic = sonic_load(root)
    from current_protron_compatibility import load as protron_load
    protron_current = protron_load(root)
    private_destination = 'assets/gameplay/enemy-protron-p09-227-8.hda'
    private_protron = protron_current.pop(private_destination)
    for destination,row in protron_current.items():
        if destination in art_compat:raise ValueError('Protron compatibility collision')
        art_compat[destination]=dict(row,authoring_family='protron')
    hud_compat=current_hud_compatibility(root)
    def add(source,destination,group,exact=None):
        size,blob,sha=pins(root/source)
        if exact and (size!=exact['bytes'] or blob!=exact['git_blob'] or (exact.get('sha256') and sha!=exact['sha256'])):
            raise ValueError('Pinned baseline mismatch: '+source)
        row=dict(source_path=source,destination=destination,group=group,bytes=size,git_blob=blob,sha256=sha,revision='reconstructed-local-unpublished')
        if destination in rows:raise ValueError('Destination collision: '+destination)
        rows[destination]=row
    for old in j['files']:
        changed=old['group']=='launcher-and-config'
        if old['source_path']=='assets/data-portrait-v1/DATA-PORTRAIT-PROVENANCE.txt':
            # Public63a89b3 updated this notice but left the older packaging row.
            # This is the only preexisting mismatch, pinned to the verified tree.
            if old['git_blob']!='44b4a4d7e976d2f407f7a50a0e87c0fdba9d1497':raise ValueError('Unexpected old notice pin')
            old=dict(old,bytes=(root/old['source_path']).stat().st_size,git_blob='ab6842928c05f8598e0c03f5f82cffc9bbc48735')
            old.pop('sha256',None)
        add(old['source_path'],old['destination'],old['group'],None if changed else old)
        if old['destination'] in art_compat:
            replacement=art_compat.pop(old['destination'])
            del rows[old['destination']]
            add(replacement['source_path'],old['destination'],old['group'])
            rows[old['destination']]['revision']='current-single-source-'+replacement['authoring_family']
        if old['destination'] in hud_compat:
            replacement=hud_compat.pop(old['destination'])
            del rows[old['destination']]
            add(replacement['source_path'],old['destination'],old['group'])
            rows[old['destination']]['revision']='current-single-source-hud'
    if art_compat: raise ValueError('Current art consumer absent from historical runtime selection')
    # These exact four approved resources complete the existing P02/P04 atomic
    # family together with historical 20/21. Shipping bytes does not enable its
    # default-off renderer. Unrelated new historical consumers still fail above.
    expected_sonic = {f'assets/gameplay/bullet-{i}-8.hda' for i in (105,106,124,125)}
    if len(sonic)!=4 or set(sonic)!=expected_sonic or set(sonic)&set(rows):
        raise ValueError('Unexpected/colliding Sonic runtime extension')
    for destination,row in sorted(sonic.items()):
        add(row['source_path'],destination,'gameplay')
        rows[destination]['revision']='current-single-source-sonic'

    # Charge is a new, separately bounded family. Keep the historical residual
    # rejection above intact; it must never admit an unrelated new consumer.
    from current_sidekick_body_compatibility import charge_load, CHARGE_IDS, charge_name
    charge = charge_load(root)
    expected_charge = {'assets/gameplay/'+charge_name(i) for i in CHARGE_IDS}
    if len(charge)!=9 or set(charge)!=expected_charge or set(charge)&set(rows):
        raise ValueError('Unexpected/colliding Charge runtime extension')
    for destination,row in sorted(charge.items()):
        add(row['source_path'],destination,'gameplay')
        rows[destination]['revision']='current-single-source-charge-body'

    # NEWSHF is a separate exact-nine additive opt-in extension. In particular,
    # do not fold it into art_compat: unknown historical consumers still fail.
    from current_newshf_compatibility import load as newshf_load, IDS as NEWSHF_IDS, name as newshf_name
    newshf = newshf_load(root)
    expected_newshf = {'assets/global/newshf/'+newshf_name(i) for i in NEWSHF_IDS}
    if len(newshf)!=9 or set(newshf)!=expected_newshf or set(newshf)&set(rows):
        raise ValueError('Unexpected/colliding NEWSHF runtime extension')
    for destination,row in sorted(newshf.items()):
        add(row['source_path'],destination,'newshf-optin')
        rows[destination]['revision']='current-single-source-newshf-nine'

    from current_linked_newshf_compatibility import load as linked_load
    linked=linked_load(root)
    if len(linked)!=6 or set(linked)&set(rows):raise ValueError('Unexpected/colliding linked NEWSHF extension')
    for destination,row in sorted(linked.items()):
        add(row['source_path'],destination,'newshf-optin')
        rows[destination]['revision']='current-single-source-linked-newshf-six'

    from current_dualmissile_newshf_compatibility import load as dualmissile_load, REVISION as dualmissile_revision
    dualmissile=dualmissile_load(root)
    if len(dualmissile)!=1 or set(dualmissile)&set(rows):raise ValueError('Unexpected/colliding dualmissile NEWSHF extension')
    for destination,row in sorted(dualmissile.items()):
        add(row['source_path'],destination,'newshf-optin')
        rows[destination]['revision']=dualmissile_revision

    from current_turret_newshf_compatibility import load as turret_load, REVISION as turret_revision
    turret=turret_load(root)
    if len(turret)!=2 or set(turret)&set(rows):raise ValueError('Unexpected/colliding turret NEWSHF extension')
    for destination,row in sorted(turret.items()):
        add(row['source_path'],destination,'newshf-optin')
        rows[destination]['revision']=turret_revision

    from current_large_newshi_compatibility import load as large_load, REVISION as large_revision
    large=large_load(root)
    if len(large)!=10 or set(large)&set(rows):raise ValueError('Unexpected/colliding large NEWSHI extension')
    for destination,row in sorted(large.items()):
        add(row['source_path'],destination,'newshf-optin')
        rows[destination]['revision']=large_revision

    from current_scout164_newshf_compatibility import load as scout164_load, REVISION as scout164_revision
    scout164=scout164_load(root)
    if len(scout164)!=3 or set(scout164)&set(rows):raise ValueError('Unexpected/colliding scout164 NEWSHF extension')
    for destination,row in sorted(scout164.items()):
        add(row['source_path'],destination,'newshf-optin')
        rows[destination]['revision']=scout164_revision

    from current_fighter165_newshf_compatibility import load as fighter165_load, REVISION as fighter165_revision
    fighter165=fighter165_load(root)
    if len(fighter165)!=3 or set(fighter165)&set(rows):raise ValueError('Unexpected/colliding fighter165 NEWSHF extension')
    for destination,row in sorted(fighter165.items()):
        add(row['source_path'],destination,'newshf-optin')
        rows[destination]['revision']=fighter165_revision

    from current_interceptor166_newshf_compatibility import load as interceptor166_load, REVISION as interceptor166_revision
    interceptor166=interceptor166_load(root)
    if len(interceptor166)!=3 or set(interceptor166)&set(rows):raise ValueError('Unexpected/colliding interceptor166 NEWSHF extension')
    for destination,row in sorted(interceptor166.items()):
        add(row['source_path'],destination,'newshf-optin')
        rows[destination]['revision']=interceptor166_revision

    from current_aircraft169_newshf_compatibility import load as aircraft169_load, REVISION as aircraft169_revision
    aircraft169=aircraft169_load(root)
    if len(aircraft169)!=3 or set(aircraft169)&set(rows):raise ValueError('Unexpected/colliding aircraft169 NEWSHF extension')
    for destination,row in sorted(aircraft169.items()):
        add(row['source_path'],destination,'newshf-optin')
        rows[destination]['revision']=aircraft169_revision

    from current_aircraft170_newshf_compatibility import load as aircraft170_load, REVISION as aircraft170_revision
    aircraft170=aircraft170_load(root)
    if len(aircraft170)!=3 or set(aircraft170)&set(rows):raise ValueError('Unexpected/colliding aircraft170 NEWSHF extension')
    for destination,row in sorted(aircraft170.items()):
        add(row['source_path'],destination,'newshf-optin')
        rows[destination]['revision']=aircraft170_revision

    from current_shapesy_cyan_compatibility import load as cyan_load, REVISION as cyan_revision
    cyan=cyan_load(root)
    if len(cyan)!=4 or set(cyan)&set(rows):raise ValueError('Unexpected/colliding cyan layer2 extension')
    for destination,row in sorted(cyan.items()):
        add(row['source_path'],destination,'gameplay')
        rows[destination]['revision']=cyan_revision

    from current_shapesy_cyan_secondary_compatibility import load as cyan_secondary_load, REVISION as cyan_secondary_revision
    cyan_secondary=cyan_secondary_load(root)
    if len(cyan_secondary)!=5 or set(cyan_secondary)&set(rows):raise ValueError('Unexpected/colliding cyan_secondary layer2 extension')
    for destination,row in sorted(cyan_secondary.items()):
        add(row['source_path'],destination,'gameplay')
        rows[destination]['revision']=cyan_secondary_revision

    from current_shapesy_bronze356_compatibility import load as bronze356_load, REVISION as bronze356_revision
    bronze356=bronze356_load(root)
    if len(bronze356)!=1 or set(bronze356)&set(rows):raise ValueError('Unexpected/colliding bronze356 extension')
    for destination,row in sorted(bronze356.items()):
        add(row['source_path'],destination,'gameplay')
        rows[destination]['revision']=bronze356_revision

    # Independent finite Y terrain family; never aliases Z/coast/water assets.
    from current_shapesy_platform_compatibility import load as shapesy_load, IDS as SHAPESY_IDS, name as shapesy_name, REVISION as SHAPESY_REVISION
    shapesy=shapesy_load(root)
    if set(shapesy)!={'assets/gameplay/'+shapesy_name(i) for i in SHAPESY_IDS} or set(shapesy)&set(rows):
        raise ValueError('Unexpected/colliding shapesY platform extension')
    for destination,row in sorted(shapesy.items()):
        add(row['source_path'],destination,'gameplay')
        rows[destination]['revision']=SHAPESY_REVISION

    # Exact additive shared91 enemy-shot role, never another bank/body selector.
    from current_projectile91_compatibility import load as projectile91_load
    projectile91 = projectile91_load(root)
    if set(projectile91) != {'assets/gameplay/enemy-projectile91-91-8.hda'} or set(projectile91)&set(rows):
        raise ValueError('Unexpected/colliding projectile91 runtime extension')
    for destination,row in projectile91.items():
        add(row['source_path'],destination,'gameplay')
        rows[destination]['revision']='current-single-source-projectile91'

    # Independent optional shared145 enemy-shot role; no player145 alias.
    from current_projectile145_compatibility import load as projectile145_load, REVISION as projectile145_revision
    projectile145=projectile145_load(root)
    if set(projectile145)!={'assets/gameplay/enemy-projectile145-145-8.hda'} or set(projectile145)&set(rows):
        raise ValueError('Unexpected/colliding projectile145 runtime extension')
    for destination,row in projectile145.items():
        add(row['source_path'],destination,'gameplay')
        rows[destination]['revision']=projectile145_revision
    from current_projectile61_compatibility import load as projectile61_load, REVISION as projectile61_revision
    projectile61=projectile61_load(root)
    if set(projectile61)!={'assets/gameplay/enemy-projectile61-61-8.hda'} or set(projectile61)&set(rows):
        raise ValueError('Unexpected/colliding projectile61 runtime extension')
    for destination,row in projectile61.items():
        add(row['source_path'],destination,'gameplay')
        rows[destination]['revision']=projectile61_revision

    # Exact three current blue enemy-shot resources; not generic role aliases.
    from current_projectile_blue_triplet_compatibility import load as blue_triplet_load, REVISION as blue_triplet_revision
    blue_triplet=blue_triplet_load(root)
    expected_blue={'assets/gameplay/enemy-projectile-blue-triplet-'+str(i)+'-8.hda' for i in (101,120,139)}
    if set(blue_triplet)!=expected_blue or set(blue_triplet)&set(rows):
        raise ValueError('Unexpected/colliding blue-triplet runtime extension')
    for destination,row in sorted(blue_triplet.items()):
        add(row['source_path'],destination,'gameplay')
        rows[destination]['revision']=blue_triplet_revision

    # Exact two animation frames of weapon63; preserve original shot behavior.
    from current_projectile_gold_pulse_compatibility import load as gold_pulse_load, REVISION as gold_pulse_revision
    gold_pulse=gold_pulse_load(root)
    expected_gold={'assets/gameplay/enemy-projectile-gold-pulse-'+str(i)+'-8.hda' for i in (168,169)}
    if set(gold_pulse)!=expected_gold or set(gold_pulse)&set(rows):
        raise ValueError('Unexpected/colliding gold-pulse runtime extension')
    for destination,row in sorted(gold_pulse.items()):
        add(row['source_path'],destination,'gameplay')
        rows[destination]['revision']=gold_pulse_revision

    # Exact two static enemy resources; preserve single-shot lobes and multi2.
    from current_projectile_statics_compatibility import load as statics_load, REVISION as statics_revision
    statics=statics_load(root)
    expected_statics={'assets/gameplay/enemy-projectile-statics-'+str(i)+'-8.hda' for i in (162,260)}
    if set(statics)!=expected_statics or set(statics)&set(rows):
        raise ValueError('Unexpected/colliding static-projectile runtime extension')
    for destination,row in sorted(statics.items()):
        add(row['source_path'],destination,'gameplay')
        rows[destination]['revision']=statics_revision

    # Exactly one private P09 transport; no player227 or duplicate226/244.
    from build_enemy_protron_p09 import derive as protron_derive, read as protron_read, DIRECTORY as PROTRON_DIRECTORY
    for name,raw in protron_derive(root).items():
        if protron_read(root,name)!=raw:raise ValueError('Stale P09 selected-B output: '+name)
    protron_source=private_protron['source_path']
    add(protron_source,'assets/gameplay/enemy-protron-p09-227-8.hda','enemy-protron-p09-optin')
    rows['assets/gameplay/enemy-protron-p09-227-8.hda']['revision']='current-single-source-protron-private-enemy-p09'

    if len(hud_compat)!=6 or any(not d.startswith('assets/shared-ui/') for d in hud_compat):
        raise ValueError('Current HUD fallback missing from historical selection')
    for destination,row in sorted(hud_compat.items()):
        add(row['source_path'],destination,'shared-hud-exact-recovery')
        rows[destination]['revision']='current-single-source-hud'
    m=root/'assets/hd/shared-menu-runs-v1'
    runs=sorted(m.glob('*.rfr'))
    if len(runs)!=171:raise ValueError('Expected171 explicitly rebuilt complete runs')
    for p in runs+[m/'numeric-runs-v1.nfr']:
        add(p.relative_to(root).as_posix(),'assets/startup/'+p.name,'reconstructed-menu-runs' if p.suffix=='.rfr' else 'numeric-exact-recovery')
    for name in ['FONT-LICENSE.txt','OSIFONT-LICENSE.txt','OSIFONT-GPL-2.txt','RFR3-RECONSTRUCTION.md']:
        add((m/name).relative_to(root).as_posix(),'licenses/shared-menu/'+name,'font-notice')
    for p in sorted((m/'osifont-source').glob('*')):
        if p.is_file():add(p.relative_to(root).as_posix(),'licenses/shared-menu/osifont-source/'+p.name,'font-corresponding-source')
    add('packaging/frontend-validation.json','FRONTEND-VALIDATION.json','frontend-validation')
    # The final independent registry is an exact accepted 120-resource allowlist,
    # not a filesystem glob that could silently package unrelated artwork.
    global_root=root/'assets/hd/global-assets-v1'
    registry=global_root/'registry.json'
    if hashlib.sha256(registry.read_bytes()).hexdigest() != GLOBAL_REGISTRY_SHA256:
        raise ValueError('Accepted global registry fingerprint mismatch')
    gj=json.loads(registry.read_text())
    if gj['schema']!='opentyrian-global-asset-registry-v1' or len(gj['resources'])!=120:
        raise ValueError('Expected exact 120-resource global registry')
    seen=set()
    for resource in gj['resources']:
        sha=resource['sha256']
        if len(sha)!=64 or any(c not in '0123456789abcdef' for c in sha):
            raise ValueError('Invalid resource hash')
        relative='content/'+sha+'.hda'
        if resource['path']!=relative or relative in seen:
            raise ValueError('Unexpected or duplicate global resource path')
        seen.add(relative)
        source='assets/hd/global-assets-v1/'+relative
        size,blob,actual=pins(root/source)
        if size!=resource['bytes'] or actual!=sha:
            raise ValueError('Global resource content mismatch: '+relative)
        add(source,'assets/global/'+relative,'global-source-identity')
    add('assets/hd/global-assets-v1/registry.json','assets/global/registry.json','global-registry')
    add('packaging/global-validation.json','GLOBAL-VALIDATION.json','global-validation')
    add('packaging/current-production-validation.json','CURRENT-PRODUCTION-VALIDATION.json','current-production-validation')
    approval=approved_static(root)
    for approved in approval['files']:
        add(approved['source_path'],approved['destination'],'shop',approved)
        rows[approved['destination']]['revision']=approved['revision']
    j['source_revision'].update(approval['source_revision'])
    j['source_revision']['current_production_commit']=current['production_commit']
    if 'production_source_manifest_sha256' in current:
        j['source_revision']['current_production_source_manifest_sha256']=current['production_source_manifest_sha256']
    j['closure']['shop_files']=15
    j['closure']['shop_static_canonical_quads']=[169,235,199]
    # Count the actual verified unique destination rows, not the637 public base.
    j['closure']['gameplay_files']=sum(row['group']=='gameplay' for row in rows.values())
    j['files']=sorted(rows.values(),key=lambda x:x['destination'])
    j['source_revision']['reconstruction']='Public63a89b33e4ee3f287b422df0ea986b907941cedd plus independently verified shared UI/frontend and fourteen globally source-authenticated player/effect/weapon families; see separate validation records'
    j['closure']['reconstructed_complete_menu_runs']=171
    j['closure']['byte_exact_numeric_pack']=True
    j['closure']['independent_shared_roots']=True
    j['source_revision']['global_runtime_commit']=json.loads((root/'packaging/global-validation.json').read_text())['production_commit']
    j['source_revision']['global_registry_sha256']=GLOBAL_REGISTRY_SHA256
    j['closure']['global_hda_files']=120
    j['closure']['global_registry_files']=1
    j['closure']['global_families']=['Talon13','Shield22','Pulse5','Hitflare7','FrontVulcan2','WhiteSmoke7','SmallExplosion12','Cash25BodyAndValue7','Cash50BodyAndValue7','Cash75BodyAndValue7','Gem100BodyAndValue6','Gem250BodyAndValue6','Rotor5And11Eight','GreenHeadAndTrail11']
    a.output.write_bytes((json.dumps(j,indent=2,sort_keys=True)+'\n').encode('utf-8'))
    print(json.dumps({'files':len(rows),'bytes':sum(x['bytes'] for x in rows.values()),'output':str(a.output)}))
if __name__=='__main__':main()
