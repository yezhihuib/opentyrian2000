"""Explicit body194-compatible Tank energy epoch; never an automatic fallback.

The historical builder authority remains unchanged. These finite constants bind
production code, registry, build inputs and every unrelated runtime row/byte.
Only the exact two approved PNG outputs and their two aliases may be replaced.
This is an authoring boundary, not native/game qualification.
The energy-v2 artwork directory is a retained historical path, not the version.
"""
import json, struct
from build_current_art import sha, read, REGISTRY, BINDING, RUNTIME
from verify_current_production import source_inventory, source_manifest_digest, BUILD_INPUTS
from package_runtime import contained_file, checked_source
from current_tank_shell_compatibility import HEADER
import current_tank_muzzle_source_bridge as muzzle_bridge
from current_tank194_source_bridge import project_sources, project_runtime_rows
MODE='current-tank-energy-body194-v1'
SOURCE_DIGEST='13af5afe2fb1766333932965486d27ded3919c5eddb7b1e748058da3cad2ef89'
REGISTRY_SHA='b224adfc0b12aee5a4753e32aa12e30c8594eb4237727a983148776239162860'
BUILD_DIGEST='dcc93711da1cb8eb764582d33f81b80c8474a0009271b682ed235548314a3800'
UNCHANGED_ROWS_DIGEST='b49f9908bd30134f5fe8131478a215c96dec65ae9e094d8130206d844868f8d3'
OLD_ALIASES=('assets/hd/global-assets-v1/content/2ceb0dce45028a2ade170d8790e3ec960befa060c78a86e79f4d708f3ade4b8c.hda', 'assets/hd/global-assets-v1/content/70f66d870cc531eccd1e0ee2b82a23a8efefc68ed782cada1e376a6faba768c3.hda')
NEW_ALIASES=('assets/hd/global-assets-v1/content/d7c88729cdc18e4fb90a4c46be89681e99b7cdcd43bb6421c639653355109afa.hda', 'assets/hd/global-assets-v1/content/fef0333704fd2afb69fc48a38555e2b892608d590054a9819064cf5cb7fecdbf.hda')
CANONICAL=('assets/hd/current-compat/tank-shell/enemy-tank-shell-146-8.hda', 'assets/hd/current-compat/tank-shell/enemy-tank-shell-147-8.hda')
APPROVED_HDA={146: 'd7c88729cdc18e4fb90a4c46be89681e99b7cdcd43bb6421c639653355109afa', 147: 'fef0333704fd2afb69fc48a38555e2b892608d590054a9819064cf5cb7fecdbf'}
APPROVED_SELECTION={'schema': 'opentyrian-current-tank-shell-authoring-v1', 'version': 'approved-tank-energy-pulse-v3', 'resources': [{'identity': 1220146, 'source_png': 'assets/hd/artwork/enemy-tank-shell-energy-v2/source/enemy-tank-shell-146-8x.png', 'source_sha256': '73fc3728e5c429deccac4c9ff8ca0887b7ced3eea0755d7dbb2105ccfb3a0ec7'}, {'identity': 1220147, 'source_png': 'assets/hd/artwork/enemy-tank-shell-energy-v2/source/enemy-tank-shell-147-8x.png', 'source_sha256': '5e723b3eacb1d0c43cccae9d142bad4e012046cecbf9fc009cad9c41fabfe754'}]}

def verify(root, selected):
    return _verify(root, selected, project_sources, project_runtime_rows)


def verify_extra(root, selected):
    from current_tank194_source_bridge import project_extra_sources, project_extra_runtime_rows
    return _verify(root, selected, project_extra_sources, project_extra_runtime_rows)


def verify_poses15_17(root, selected):
    from current_tank194_source_bridge import project_poses15_17_sources, project_poses15_17_runtime_rows
    return _verify(root, selected, project_poses15_17_sources, project_poses15_17_runtime_rows)


def verify_pose89(root, selected):
    from current_tank194_source_bridge import project_pose89_sources, project_pose89_runtime_rows
    return _verify(root, selected, project_pose89_sources, project_pose89_runtime_rows)


def _verify(root, selected, source_projector, runtime_projector):
    if selected!=APPROVED_SELECTION:raise ValueError('Unreviewed Tank energy selection')
    sources,body_restored=source_projector(root)
    if HEADER not in sources:raise ValueError('Missing generated Tank header')
    del sources[HEADER]
    if len(sources)!=328:raise ValueError('Unreviewed Tank production epoch')
    if source_manifest_digest(sources)!=SOURCE_DIGEST:
        sources=muzzle_bridge.project(sources,lambda name:body_restored[name] if name in body_restored else read(root,name))
    if source_manifest_digest(sources)!=SOURCE_DIGEST:raise ValueError('Unreviewed Tank production epoch')
    if sha(read(root,REGISTRY))!=REGISTRY_SHA:raise ValueError('Unrelated registry changed')
    if source_manifest_digest({p:sha(read(root,p)) for p in BUILD_INPUTS})!=BUILD_DIGEST:raise ValueError('Build inputs changed')
    rows=runtime_projector(root,json.loads(read(root,RUNTIME)))
    mutable=set(CANONICAL)|set(OLD_ALIASES)|set(NEW_ALIASES)|{BINDING}
    fixed=[row for row in rows if row['source_path'] not in mutable]
    if len(rows)!=1131 or len(fixed)!=1126 or source_manifest_digest(fixed)!=UNCHANGED_ROWS_DIGEST:raise ValueError('Unrelated runtime row changed')
    if sum(row['source_path']==BINDING for row in rows)!=1:raise ValueError('Expected one source binding')
    if {row['source_path'] for row in rows if row['source_path'] in CANONICAL}!=set(CANONICAL):raise ValueError('Missing canonical Tank rows')
    aliases=[row['source_path'] for row in rows if row['source_path'] in set(OLD_ALIASES)|set(NEW_ALIASES)]
    if len(aliases)!=2 or set(aliases) not in (set(OLD_ALIASES),set(NEW_ALIASES)):raise ValueError('Mixed or duplicate Tank aliases')
    obsolete(root)  # Reject changed old files before expensive generation.
    for row in fixed:checked_source(contained_file(root,row['source_path']),row)

def obsolete(root):
    # Exact previous-epoch aliases only. No generic deletion authority.
    result=[]
    for name,identity in zip(OLD_ALIASES,(1220146,1220147)):
        p=contained_file(root,name)
        if p.exists():
            if not p.is_file():raise ValueError('Nonregular obsolete alias')
            raw=read(root,name)
            if len(raw)!=43036 or sha(raw)!=p.stem or raw[:28]!=b'HDR1'+struct.pack('<6I',identity,8,12,14,0,0):raise ValueError('Changed obsolete Tank alias; deletion refused')
            result.append(name)
    return result
