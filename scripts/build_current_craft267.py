#!/usr/bin/env python3
"""One NEWSH2 base267 PNG -> canonical HDA and current package/preview consumers.

Stage is read-only. Apply preflights then rolls back handled write failures;
power loss/process termination is not a crash-safe transaction. No game C changes.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from build_current_art import (encoded, fingerprint, validate_stage_location,
                               verify_authority, REGISTRY, BINDING, RUNTIME, REBUILD)
from current_art_policy import PROFILES, profile
from current_craft267_compatibility import (IDENTITY, NAME, SELECTION, MAPPING,
    CANONICAL, DESTINATION, sha, path, read, parse, selection, source_blob, load)
from package_runtime import checked_source
from verify_current_production import BUILD_INPUTS

BASES = {
    'preview': 'packed-talon13-foundation-type10-death-effects-white-smoke-shield-green-v2-head-v1-test',
    'debug': 'packed-blue-four-foundation-type10-death-effects-white-smoke-shield-green-v2-head-v1-test',
}
BASE_TREE_SHA256 = '6e40d0b6ad5868fecc00dd3a36b8144ae2e68d7ca166209328af6e0de1e3aa93'
SUFFIX = '.craft267-tmp'


def closure(root):
    old = parse(read(root, RUNTIME))
    base = parse(read(root, 'packaging/runtime-assets-public63a89b3.json'))
    names = {r['source_path'] for r in old['files'] + base['files']}
    names |= {REGISTRY, BINDING, RUNTIME, MAPPING, CANONICAL,
              'packaging/runtime-assets-public63a89b3.json',
              'packaging/shop-static-approved-v1.json',
              'packaging/current-hud-compatibility.json',
              'packaging/current-tank-shell-compatibility.json',
              'packaging/current-enemy-energy-compatibility.json',
              'packaging/current-sidekick-body-compatibility.json'} | set(BUILD_INPUTS)
    names |= {profile(f)['mapping'] for f in PROFILES}
    names |= {p.relative_to(root).as_posix() for p in (root/'src').rglob('*') if p.is_file() or p.is_symlink()}
    names |= {p.relative_to(root).as_posix() for p in (root/'scripts').glob('*.py')}
    from current_sidekick_body_compatibility import independent_input_paths
    names |= independent_input_paths(root)
    return old, names


def derive(root, raw):
    selected = selection(root, raw)
    data = source_blob(root, selected['resources'][0])
    verify_authority(root, parse(read(root, REGISTRY)))
    outputs = {SELECTION: raw, CANONICAL: data,
        MAPPING: encoded(dict(schema='opentyrian-current-craft267-compatibility-v1',
            selection=SELECTION, version=selected['version'], files=[dict(
                identity=IDENTITY, source_path=CANONICAL,
                destination=DESTINATION, sha256=sha(data))]))}
    old, names = closure(root)
    for row in old['files']:
        if row['source_path'] not in outputs:
            checked_source(path(root, row['source_path']), row)
    # Reuse the public runtime builder. C and its binding are unchanged.
    with tempfile.TemporaryDirectory(prefix='craft267-build-') as tmp:
        work = Path(tmp)
        for name in sorted(names | set(outputs)):
            blob = outputs[name] if name in outputs else read(root, name)
            p = work/name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(blob)
        subprocess.run([sys.executable, str(work/REBUILD), '--root', str(work),
                        '--output', str(work/RUNTIME)], check=True, stdout=subprocess.DEVNULL)
        outputs[RUNTIME] = (work/RUNTIME).read_bytes()
    return outputs


def make_plan(root, outputs, raw):
    _, names = closure(root)
    # Bind the exact installed state/tool closure, including the installed selection.
    # Proposed sources are re-read and SHA checked on every derive.
    inputs = {name: fingerprint(root, name) for name in sorted(names | {SELECTION})}
    return dict(schema='opentyrian-current-craft267-stage-v1',
        selection_sha256=sha(raw), inputs_sha256=inputs,
        files=[dict(path=p, before_sha256=fingerprint(root, p),
                    after_sha256=sha(data), bytes=len(data))
               for p, data in sorted(outputs.items())])


def external(root, destination):
    validate_stage_location(root, destination)
    # Inspect components without creating links or changing permissions.
    absolute = Path(os.path.abspath(destination))
    path(absolute.anchor and Path(absolute.anchor) or root, absolute.relative_to(absolute.anchor).as_posix())


def stage(root, selected, destination):
    external(root, destination)
    if destination.exists():
        raise ValueError('Stage destination must be new')
    raw = selected.read_bytes()
    outputs = derive(root, raw)
    plan = make_plan(root, outputs, raw)
    destination.mkdir(parents=True)
    for name, data in outputs.items():
        p = destination/'files'/name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
    (destination/'plan.json').write_bytes(encoded(plan))
    return plan


def replace_batch(root, outputs):
    """All callers preflight; keep original bytes for handled-failure rollback."""
    previous = {name: read(root, name) if path(root, name).exists() else None for name in outputs}
    changed = []
    temporaries = []
    made_dirs = []
    try:
        for name, data in outputs.items():
            p = path(root, name)
            if previous[name] == data:
                continue
            missing = []
            parent = p.parent
            while not parent.exists():
                missing.append(parent)
                parent = parent.parent
            for directory in reversed(missing):
                directory.mkdir()
                made_dirs.append(directory)
            tmp = p.with_name(p.name + SUFFIX)
            with tmp.open('xb') as stream:
                temporaries.append(tmp)
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(tmp, p)
            changed.append(name)
    except BaseException as failure:
        try:
            for name in reversed(changed):
                p = path(root, name)
                if previous[name] is None:
                    p.unlink()
                else:
                    tmp = p.with_name(p.name + SUFFIX)
                    with tmp.open('xb') as stream:
                        temporaries.append(tmp)
                        stream.write(previous[name])
                    os.replace(tmp, p)
            for tmp in temporaries:
                if tmp.exists():
                    tmp.unlink()
            for directory in reversed(made_dirs):
                directory.rmdir()
        except BaseException as rollback_failure:
            raise RuntimeError('craft267 rollback incomplete; preserve stage and inspect outputs') from rollback_failure
        raise failure


def apply(root, destination):
    external(root, destination)
    plan = parse(read(destination, 'plan.json'))
    raw = read(destination, 'files/' + SELECTION)
    outputs = derive(root, raw)
    expected = make_plan(root, outputs, raw)
    if plan != expected:
        raise ValueError('Stale or modified plan/current inputs; restage explicitly')
    for name, data in outputs.items():
        if read(destination, 'files/' + name) != data:
            raise ValueError('Modified staged bytes: ' + name)
        p = path(root, name)
        tmp = p.with_name(p.name + SUFFIX)
        if tmp.exists() or tmp.is_symlink():
            raise ValueError('Unexpected temporary output: ' + str(tmp))
        if p.exists() and not p.is_file():
            raise ValueError('Nonregular output: ' + name)
    replace_batch(root, outputs)
    return expected


def check(root):
    outputs = derive(root, read(root, SELECTION))
    bad = [p for p, data in outputs.items() if fingerprint(root, p) != sha(data)]
    if bad:
        raise ValueError('Stale/missing craft267 outputs: ' + ', '.join(bad))
    return dict(status='PASS', resources=1, runtime_consumers=1,
                preview_views=['preview', 'debug'], global_registry_additions=0,
                historical_outputs='untouched', runtime_acceptance='not claimed')


def current_overlays(root):
    """Current canonical gameplay consumers, not independent per-pack artwork."""
    import build_current_art as art
    import build_current_tank_shell as tank
    import build_current_enemy_energy as energy
    import build_current_sidekick_body as sidekick
    import build_current_hud as hud
    import current_art_compatibility as art_compat
    import current_tank_shell_compatibility as tank_compat
    import current_enemy_energy_compatibility as energy_compat
    import current_sidekick_body_compatibility as sidekick_compat
    import current_hud_compatibility as hud_compat
    import current_hud_recipe as hud_recipe
    from current_art_policy import compatibility_name

    files = {}

    def add(mapping_path, selection_path, selected, mapping, expected):
        # Reuse each family's exact consumer/geometry/hash checks, then also bind
        # its installed selection. A stale source or mapping must not fall back
        # silently to the frozen pack. Reconstruct in memory only; copy canonical.
        metadata = parse(read(root, mapping_path))
        if (set(metadata) != {'schema', 'selection', 'version', 'files'} or
                metadata['selection'] != selection_path or
                metadata['version'] != selected['version']):
            raise ValueError('Stale current preview selection/mapping: ' + mapping_path)
        if set(mapping) != set(expected):
            raise ValueError('Unexpected current preview consumers: ' + mapping_path)
        for destination, entry in mapping.items():
            name = destination.removeprefix('assets/gameplay/')
            if not destination.startswith('assets/gameplay/') or not name or '/' in name or name in files:
                raise ValueError('Current preview overlay collision/invalid destination: ' + destination)
            data = read(root, entry['source_path'])
            if sha(data) != entry['sha256'] or data != expected[destination]:
                raise ValueError('Stale current preview selected source/canonical: ' + destination)
            files[name] = data

    selected = selection(root, read(root, SELECTION))
    add(MAPPING, SELECTION, selected, load(root),
        {DESTINATION: source_blob(root, selected['resources'][0])})
    for family in PROFILES:
        policy = profile(family)
        selected = art.selection(root, read(root, policy['selection']), family)
        expected = {'assets/gameplay/' + compatibility_name(row['identity']): art.source_blob(root, row)[0]
                    for row in selected['resources']}
        add(policy['mapping'], policy['selection'], selected, art_compat.load(root, family), expected)
    for builder, compat in ((tank, tank_compat), (energy, energy_compat), (sidekick, sidekick_compat)):
        selected = builder.selection(root, read(root, compat.SELECTION))
        expected = {'assets/gameplay/' + compat.name(row['identity']): builder.source_blob(root, row)[0]
                    for row in selected['resources']}
        add(compat.MAPPING, compat.SELECTION, selected, compat.load(root), expected)
    selected = hud.selection(root, read(root, hud.SELECTION))
    # Preview consumes installed HUD transports, not its expensive meter recipe.
    # Check selected/fixed inputs and mapping versions without adding NumPy to
    # launch dependencies. Full source-to-HDA equivalence remains `hud ... check`.
    for key, sources in selected['resources'].items():
        if not isinstance(sources, list) or len(sources) != len(hud_recipe.DEFAULT_SELECTION[key]):
            raise ValueError('Unexpected current HUD source count')
        for record in sources:
            hud_recipe.checked(root, record)
    for record in hud_recipe.FIXED_INPUTS.values():
        hud_recipe.checked(root, record)
    expected = {'assets/gameplay/' + name: read(root, 'assets/hd/shared-ui-v1/' + name)
                for name in hud.NAMES}
    mapping = {destination: row for destination, row in hud_compat.load(root).items()
               if destination.startswith('assets/gameplay/')}
    add(hud.MAPPING, hud.SELECTION, selected, mapping, expected)
    if len(files) != 142:
        raise ValueError('Expected exactly 142 current gameplay overlays')
    selected, _, charge_blobs = sidekick_compat.charge_generate(root, read(root, sidekick_compat.CHARGE_SELECTION))
    add(sidekick_compat.CHARGE_MAPPING, sidekick_compat.CHARGE_SELECTION, selected,
        sidekick_compat.charge_load(root), {'assets/gameplay/' + sidekick_compat.charge_name(i): blob for i, blob in charge_blobs.items()})
    if len(files) != 151:
        raise ValueError('Expected exactly 151 current gameplay overlays')
    selected, mf_blobs = sidekick_compat.mf_generate(root, read(root, sidekick_compat.MF_SELECTION))
    add(sidekick_compat.MF_MAPPING, sidekick_compat.MF_SELECTION, selected,
        sidekick_compat.mf_load(root), {'assets/gameplay/' + sidekick_compat.mf_name(i): blob for i, blob in mf_blobs.items()})
    if len(files) != 155:
        raise ValueError('Expected exactly 155 current gameplay overlays')
    import current_plasma_projectile_compatibility as plasma
    selected, _, plasma_blobs = plasma.generate(root, read(root, plasma.SELECTION))
    add(plasma.MAPPING, plasma.SELECTION, selected, plasma.load(root),
        {'assets/gameplay/' + plasma.name(i, d): blob for (i, d), blob in plasma_blobs.items()})
    if len(files) != 161:
        raise ValueError('Expected exactly 161 pre-Front-Multi gameplay overlays')
    import current_front_multi_compatibility as front_multi
    selected, front_multi_blobs = front_multi.generate(root, read(root, front_multi.SELECTION))
    add(front_multi.MAPPING, front_multi.SELECTION, selected, front_multi.load(root),
        {'assets/gameplay/' + front_multi.name(identity): blob for identity, blob in front_multi_blobs.items()})
    if len(files) != 169:
        raise ValueError('Expected exactly 169 current gameplay overlays')
    import current_enemy_orb_compatibility as orb
    selected, _, blobs = orb.generate(root, read(root, orb.SELECTION))
    mapping = {destination: row for destination, row in orb.load(root).items()
               if row['identity'] in orb.ORDINARY_IDS}
    add(orb.MAPPING, orb.SELECTION, selected, mapping,
        {'assets/gameplay/' + orb.name(identity, density): blob
         for (identity, density), blob in blobs.items() if identity in orb.ORDINARY_IDS})
    if len(files) != 171:
        raise ValueError('Expected exactly 171 pre-Protron gameplay overlays')
    import current_protron_compatibility as protron
    selected, _, blobs = protron.generate(root, read(root, protron.SELECTION))
    mapping = {destination: row for destination, row in protron.load(root).items()
               if row['identity'] in (80225, 80244, 80226)}
    add(protron.MAPPING, protron.SELECTION, selected, mapping,
        {'assets/gameplay/' + protron.name(identity, density): blob
         for (identity, density), blob in blobs.items() if identity in (80225, 80244, 80226)})
    if len(files) != 174:
        raise ValueError('Expected exactly 174 pre-Sonic gameplay overlays')
    import current_sonic_compatibility as sonic
    selected, _, blobs = sonic.generate(root, read(root, sonic.SELECTION))
    add(sonic.MAPPING, sonic.SELECTION, selected, sonic.load(root),
        {'assets/gameplay/' + sonic.name(identity, density): blob
         for (identity, density), blob in blobs.items()})
    if len(files) != 178:
        raise ValueError('Expected exactly 178 pre-Guided gameplay overlays')
    import current_guided_compatibility as guided
    selected, _, blobs = guided.generate(root, read(root, guided.SELECTION))
    add(guided.MAPPING, guided.SELECTION, selected, guided.load(root),
        {'assets/gameplay/' + guided.name(identity, density): blob
         for (identity, density), blob in blobs.items()})
    if len(files) != 182:
        raise ValueError('Expected exactly 182 pre-Mint27 gameplay overlays')
    import current_mint27_compatibility as mint27
    selected, _, blobs = mint27.generate(root, read(root, mint27.SELECTION))
    add(mint27.MAPPING, mint27.SELECTION, selected, mint27.load(root),
        {'assets/gameplay/' + mint27.name(identity, density): blob
         for (identity, density), blob in blobs.items()})
    if len(files) != 183:
        raise ValueError('Expected exactly 183 pre-Missile gameplay overlays')
    import current_missile_compatibility as missile
    selected, _, blobs = missile.generate(root, read(root, missile.SELECTION))
    add(missile.MAPPING, missile.SELECTION, selected, missile.load(root),
        {'assets/gameplay/' + missile.name(identity, density): blob
         for (identity, density), blob in blobs.items()})
    if len(files) != 186:
        raise ValueError('Expected exactly 186 pre-Rear P7 gameplay overlays')
    import current_rear_p7_compatibility as rear_p7
    selected, _, blobs = rear_p7.generate(root, read(root, rear_p7.SELECTION))
    add(rear_p7.MAPPING, rear_p7.SELECTION, selected, rear_p7.load(root),
        {'assets/gameplay/' + rear_p7.name(identity, density): blob
         for (identity, density), blob in blobs.items()})
    if len(files) != 190:
        raise ValueError('Expected exactly 190 pre-Rear39 gameplay overlays')
    import current_rear39_compatibility as rear39
    selected, _, blobs = rear39.generate(root, read(root, rear39.SELECTION))
    add(rear39.MAPPING, rear39.SELECTION, selected, rear39.load(root),
        {'assets/gameplay/' + rear39.name(identity, density): blob
         for (identity, density), blob in blobs.items()})
    if len(files) != 196:
        raise ValueError('Expected exactly 196 pre-Rear1 gameplay overlays')
    import current_rear1_compatibility as rear1
    selected, _, blobs = rear1.generate(root, read(root, rear1.SELECTION))
    add(rear1.MAPPING, rear1.SELECTION, selected, rear1.load(root),
        {'assets/gameplay/' + rear1.name(identity, density): blob
         for (identity, density), blob in blobs.items()})
    if len(files) != 204:
        raise ValueError('Expected exactly 204 pre-Rear281 gameplay overlays')
    import current_rear281_compatibility as rear281
    selected, _, blobs = rear281.generate(root, read(root, rear281.SELECTION))
    add(rear281.MAPPING, rear281.SELECTION, selected, rear281.load(root),
        {'assets/gameplay/' + rear281.name(identity, density): blob
         for (identity, density), blob in blobs.items()})
    if len(files) != 224:
        raise ValueError('Expected exactly 224 current gameplay overlays')
    return files


def enemy_orb_contract_view(root, destination):
    """Explicit four-transport export, not a pack or a renderer-mode toggle."""
    import current_enemy_orb_compatibility as orb
    external(root, destination)
    if destination.exists():
        raise ValueError('View destination must be new')
    selected = orb.load(root)  # validates both contracts and their source authority
    files = {Path(row['destination']).name: read(root, row['source_path'])
             for row in selected.values()}
    if len(files) != 4:
        raise ValueError('Expected four current enemy orb transports')
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='enemy-orb-view-', dir=destination.parent) as tmp:
        work = Path(tmp)/'transports'
        work.mkdir()
        for name, data in files.items():
            (work/name).write_bytes(data)
            if (work/name).read_bytes() != data:
                raise ValueError('Enemy orb view copy verification failed')
        os.rename(work, destination)
    return dict(status='PASS', kind='enemy-orb-contracts', files=4,
                path=os.path.abspath(destination), renderer_mode_changed=False,
                sha256={name: sha(data) for name, data in sorted(files.items())})


def view(root, kind, destination):
    """Materialize one frozen pack plus all mapped current gameplay consumers."""
    external(root, destination)
    if destination.exists():
        raise ValueError('View destination must be new')
    overlays = current_overlays(root)
    canonical = overlays[NAME]
    base = 'assets/hd/packs/' + BASES[kind]
    files = {}
    for p in sorted(path(root, base).rglob('*')):
        relative = p.relative_to(root).as_posix()
        path(root, relative)
        if p.is_dir():
            continue
        files[p.relative_to(root/base).as_posix()] = read(root, relative)
    inventory = {name: sha(data) for name, data in files.items()}
    digest = sha(json.dumps(inventory, sort_keys=True, separators=(',', ':')).encode())
    if digest != BASE_TREE_SHA256:
        raise ValueError('Frozen preview base changed')
    from current_sidekick_body_compatibility import CHARGE_IDS, charge_name
    additions = {charge_name(identity) for identity in CHARGE_IDS}
    if len(files) != 641 or len(additions) != 9 or additions & set(files):
        raise ValueError('Charge additions collide with frozen preview base')
    if set(overlays) - set(files) != additions or not (set(overlays) - additions).issubset(files):
        raise ValueError('Missing original current gameplay consumer or unapproved addition')
    files.update(overlays)
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Publish only a complete verified view. Temporary tree is exclusively ours.
    with tempfile.TemporaryDirectory(prefix='craft267-view-', dir=destination.parent) as tmp:
        work = Path(tmp)/'pack'
        work.mkdir()
        for name, data in files.items():
            p = path(work, name)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
            if p.read_bytes() != data:
                raise ValueError('View copy verification failed')
        os.rename(work, destination)
    return dict(status='PASS', kind=kind, path=os.path.abspath(destination),
                files=len(files), overlay=NAME, sha256=sha(canonical),
                frozen_base_sha256=digest, current_overlays=sorted(overlays))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument('mode', choices=('stage', 'apply', 'check', 'view'))
    p.add_argument('--selection', type=Path)
    p.add_argument('--stage', type=Path)
    p.add_argument('--kind', choices=tuple(BASES) + ('enemy-orb-contracts',))
    p.add_argument('--output', type=Path)
    a = p.parse_args()
    root = a.root.resolve()
    if a.mode == 'check':
        result = check(root)
    elif a.mode == 'view':
        if not a.kind or not a.output:
            p.error('view requires --kind and --output')
        result = (enemy_orb_contract_view(root, a.output) if a.kind == 'enemy-orb-contracts'
                  else view(root, a.kind, a.output))
    else:
        if not a.stage:
            p.error('--stage required')
        result = stage(root, a.selection or root/SELECTION, a.stage) if a.mode == 'stage' else apply(root, a.stage)
    if a.mode in ('stage', 'apply'):
        result = dict(status='PASS', mode=a.mode, stage=str(a.stage),
                      files=result['files'], bound_inputs=len(result['inputs_sha256']))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
