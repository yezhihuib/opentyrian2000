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
