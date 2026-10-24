#!/usr/bin/env python3
"""Four independent Guided projectile masters -> four current transports and payload pins.

Stage is read-only. Apply rederives and preflights the full finite plan, then
rolls back handled write failures; it is not crash-safe across process/power
loss. Fixed geometry/eligibility/blend and historical evidence never change.
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from build_current_art import (encoded, fingerprint, verify_authority, fnv,
                               REGISTRY, BINDING, RUNTIME, REBUILD)
from build_current_craft267 import external, replace_batch, SUFFIX
from current_art_policy import PROFILES, profile, LEGACY_HEADER, legacy_header
from current_craft267_compatibility import path
import current_guided_compatibility as compat
from current_guided_compatibility import sha, read, parse, SELECTION
from package_runtime import checked_source
from verify_current_production import source_inventory, source_manifest_digest, BUILD_INPUTS


def dependencies(root, selected):
    """Explicit data closure, plus already-required build/source/tool inventory."""
    from current_sidekick_body_compatibility import (charge_input_paths, mf_input_paths,
                                                     CHARGE_MAPPING, MF_MAPPING)
    names = charge_input_paths(root) | mf_input_paths(root) | {CHARGE_MAPPING, MF_MAPPING}
    from build_enemy_protron_p09 import input_paths as p09_input_paths
    names |= p09_input_paths(root)
    # The user edits these four masters in place; installed hashes are deliberately
    # stale until apply. Bind its fixed paths without validating old selection.
    names |= {SELECTION, compat.MAPPING} | compat.generated_paths()
    from current_newshf_compatibility import input_paths as newshf_input_paths
    names |= newshf_input_paths(root)
    from current_enemy_orb_compatibility import input_paths as orb_input_paths, MAPPING as ORB_MAPPING
    names |= orb_input_paths(root) | {ORB_MAPPING}
    from current_front_multi_compatibility import input_paths as front_multi_input_paths, MAPPING as FRONT_MULTI_MAPPING
    names |= front_multi_input_paths(root) | {FRONT_MULTI_MAPPING}
    from current_plasma_projectile_compatibility import input_paths as plasma_input_paths, MAPPING as PLASMA_MAPPING
    names |= plasma_input_paths(root) | {PLASMA_MAPPING}
    from current_protron_compatibility import input_paths as protron_input_paths, MAPPING as PROTRON_MAPPING
    names |= protron_input_paths(root) | {PROTRON_MAPPING}
    from current_sonic_compatibility import input_paths as sonic_input_paths, MAPPING as SONIC_MAPPING
    names |= sonic_input_paths(root) | {SONIC_MAPPING}
    names |= {r['source_png'] for r in selected['masters']} | {selected['recipe']['path']}
    names |= {REGISTRY, BINDING, RUNTIME, 'packaging/runtime-assets-public63a89b3.json',
              'packaging/shop-static-approved-v1.json', 'packaging/current-hud-compatibility.json',
              'packaging/current-sidekick-body-compatibility.json',
              'packaging/current-enemy-energy-compatibility.json',
              'packaging/current-tank-shell-compatibility.json',
              'packaging/current-craft267-compatibility.json'} | set(BUILD_INPUTS)
    names |= {profile(family)['mapping'] for family in PROFILES}
    names |= {p.relative_to(root).as_posix() for p in (root/'src').rglob('*') if p.is_file() or p.is_symlink()}
    names |= {p.relative_to(root).as_posix() for p in (root/'scripts').glob('*.py')}
    return names


def derive(root, raw):
    request = parse(raw)
    candidate = isinstance(request, dict) and request.get('schema') == compat.CANDIDATE_SCHEMA
    selected, pngs, blobs = compat.generate(root, raw, candidate=candidate)
    registry = parse_manifest(read(root, REGISTRY))
    verify_authority(root, registry, family='guided')
    if read(root, LEGACY_HEADER) != legacy_header(registry['resources']):
        raise ValueError('Unrelated legacy art pins changed')
    outputs = {SELECTION: encoded(selected), **pngs}
    rows, pins = [], {}
    for (identity, density), blob in blobs.items():
        source = compat.ROOT + '/' + compat.name(identity, density)
        outputs[source] = blob
        pins[(identity, density)] = fnv(blob[28:])
        rows.append(dict(identity=identity, density=density, source_path=source,
                         destination='assets/gameplay/' + compat.name(identity, density), sha256=sha(blob)))
    outputs[compat.HEADER] = compat.payload_header(pins)
    outputs[compat.MAPPING] = encoded(dict(schema='opentyrian-current-guided-compatibility-v1',
        selection=SELECTION, version=selected['version'], files=rows))
    old = parse_manifest(read(root, RUNTIME, 2 * 1024 * 1024))
    base = parse_manifest(read(root, 'packaging/runtime-assets-public63a89b3.json', 2 * 1024 * 1024))
    for row in old['files']:
        if row['source_path'] not in set(outputs) | {BINDING}:
            checked_source(path(root, row['source_path']), row)
    names = dependencies(root, selected) | {row['source_path'] for row in old['files'] + base['files']}
    with tempfile.TemporaryDirectory(prefix='guided-build-') as tmp:
        work = Path(tmp)
        for name in sorted(names | set(outputs)):
            data = outputs[name] if name in outputs else read(root, name)
            target = work/name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        # This family cannot rebind unrelated global source/geometry pins.
        # Reconstruct the complete header from the already-verified registry
        # inside the scratch root, then demand byte equality before rebinding.
        global_header = 'src/global_asset_registry.h'
        subprocess.run([sys.executable, str(work/'scripts/build_global_registry_header.py'),
                        '--registry', str(work/REGISTRY), '--output', str(work/global_header)],
                       check=True, stdout=subprocess.DEVNULL)
        if (work/global_header).read_bytes() != read(root, global_header):
            raise ValueError('Unrelated global pins changed')
        binding = json.loads(read(root, BINDING))
        binding['production_commit'] = None
        binding['source_sha256'] = source_inventory(work)
        binding['production_source_manifest_sha256'] = source_manifest_digest(binding['source_sha256'])
        binding['scope'] = 'Exact current source binding including the separately reviewed Charge body extension, Plasma projectile and Front Multi payload-pin extractions. Build/package consistency only; historical receipts retain their original scope.'
        outputs[BINDING] = (json.dumps(binding, indent=2, sort_keys=True) + '\n').encode()
        (work/BINDING).write_bytes(outputs[BINDING])
        subprocess.run([sys.executable, str(work/REBUILD), '--root', str(work), '--output', str(work/RUNTIME)],
                       check=True, stdout=subprocess.DEVNULL)
        outputs[RUNTIME] = (work/RUNTIME).read_bytes()
    return outputs


def parse_manifest(raw):
    # Runtime manifests have >1000 rows. Keep candidate/plan JSON at 128 KiB;
    # use the established duplicate-key manifest reader for these fixed inputs.
    from current_craft267_compatibility import parse as parse_large
    return parse_large(raw)


def make_plan(root, outputs, raw):
    selected = parse(raw)
    names = dependencies(root, selected) | {SELECTION, compat.MAPPING, compat.HEADER}
    return dict(schema='opentyrian-current-guided-stage-v1', request_sha256=sha(raw),
        inputs_sha256={name: fingerprint(root, name) for name in sorted(names)},
        files=[dict(path=name, before_sha256=fingerprint(root, name), after_sha256=sha(data), bytes=len(data))
               for name, data in sorted(outputs.items())])


def stage(root, selected, destination):
    external(root, destination)
    if destination.exists():
        raise ValueError('Stage destination must be new')
    raw = read(selected.absolute().parent, selected.name, 128 * 1024)
    outputs = derive(root, raw)
    plan = make_plan(root, outputs, raw)
    destination.mkdir(parents=True)
    for name, data in outputs.items():
        target = destination/'files'/name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    (destination/'request.json').write_bytes(raw)
    (destination/'plan.json').write_bytes(encoded(plan))
    return plan


def apply(root, destination):
    external(root, destination)
    plan = parse(read(destination, 'plan.json', 128 * 1024))
    raw = read(destination, 'request.json', 128 * 1024)
    outputs = derive(root, raw)
    expected = make_plan(root, outputs, raw)
    if json.dumps(plan, sort_keys=True) != json.dumps(expected, sort_keys=True):
        raise ValueError('Stale or modified Guided plan/current inputs; restage explicitly')
    for name, data in outputs.items():
        if read(destination, 'files/' + name) != data:
            raise ValueError('Modified staged Guided bytes: ' + name)
        target = path(root, name)
        temporary = path(root, name + SUFFIX)
        if temporary.exists() or temporary.is_symlink():
            raise ValueError('Unexpected Guided temporary output')
        if target.exists() and not target.is_file():
            raise ValueError('Nonregular Guided output')
    replace_batch(root, outputs)
    return expected


def check(root):
    compat.load(root)
    outputs = derive(root, read(root, SELECTION, 128 * 1024))
    bad = [name for name, data in outputs.items() if fingerprint(root, name) != sha(data)]
    if bad:
        raise ValueError('Stale/missing current Guided outputs: ' + ', '.join(bad))
    return dict(status='PASS', resources=4, editable_masters=4, logical_pieces=4,
                global_registry_additions=0, historical_outputs='untouched')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('mode', choices=('stage', 'apply', 'check'))
    parser.add_argument('--selection', type=Path)
    parser.add_argument('--stage', type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    if args.mode == 'check':
        result = check(root)
    else:
        if not args.stage:
            parser.error('--stage required')
        result = (stage(root, args.selection or root/SELECTION, args.stage) if args.mode == 'stage'
                  else apply(root, args.stage))
        result = dict(status='PASS', mode=args.mode, stage=str(args.stage), files=result['files'],
                      bound_inputs=len(result['inputs_sha256']))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
