#!/usr/bin/env python3
"""Read-only authoring entry points, derived from validated current contracts.

No level-coverage inference, image generation, index file or tracked-tree writes.
Numeric IDs are material identities (not sprite numbers); HUD uses hud:<key>.
"""
import sys
sys.dont_write_bytecode = True
import argparse
import hashlib
import importlib
import json
from pathlib import Path

from current_craft267_compatibility import read, parse


def validate_records(records):
    keys = set()
    outputs = {p for r in records for p in r['derived_outputs']}
    for row in records:
        key = (row['identity'], row['density'], row['role'])
        if key in keys:
            raise ValueError('Duplicate authoring contract: ' + str(key))
        keys.add(key)
        if outputs.intersection(row['editable_inputs']):
            raise ValueError('Derived output mislabeled as editable input')
        if row['status'] == 'frozen-reproducer' and row['editable_inputs']:
            raise ValueError('Frozen reproducer has editable inputs')
    return records


def current_records(root):
    # This existing strict aggregate reconstructs selected sources in memory and
    # compares installed consumers. Orb's additional masked contracts are loaded
    # separately below, not mistaken for the ordinary-only preview overlay.
    from build_current_craft267 import current_overlays
    current_overlays(root)
    from current_art_policy import PROFILES, profile
    import build_current_art as art
    import current_sidekick_body_compatibility as sidekick
    configs = []
    for family in PROFILES:
        policy = profile(family)
        selected = art.selection(root, read(root, policy['selection']), family)
        configs.append((family, policy['selection'], policy['mapping'], selected,
                        'scripts/build_current_art.py --family ' + family))
    for family in ('craft267', 'tank-shell', 'enemy-energy', 'sidekick-body',
                   'plasma-projectile', 'front-multi', 'enemy-orb', 'protron', 'sonic'):
        module = importlib.import_module('current_' + family.replace('-', '_') + '_compatibility')
        builder = module if hasattr(module, 'selection') else importlib.import_module('build_current_' + family.replace('-', '_'))
        selected = builder.selection(root, read(root, module.SELECTION))
        module.load(root)  # Includes all four orb contracts, not just preview's two.
        configs.append((family, module.SELECTION, module.MAPPING, selected,
                        'scripts/build_current_' + family.replace('-', '_') + '.py'))
    for family, prefix in (('charge-body', 'charge'), ('mint-front-body', 'mf')):
        selection_path = getattr(sidekick, prefix.upper() + '_SELECTION')
        selected = getattr(sidekick, prefix + '_selection')(root, read(root, selection_path))
        getattr(sidekick, prefix + '_load')(root)
        configs.append((family, selection_path, getattr(sidekick, prefix.upper() + '_MAPPING'), selected,
                        'scripts/build_current_sidekick_body.py --family ' + family))
    result = []
    registry_path = 'assets/hd/global-assets-v1/registry.json'
    registry = {r['identity']: r for r in parse(read(root, registry_path))['resources']}
    from package_runtime import load_manifest, contained_file
    runtime_path = 'packaging/runtime-assets-v1.json'
    runtime = load_manifest(contained_file(root, runtime_path))['files']
    for family, selection_path, mapping_path, selected, command in configs:
        mapping = parse(read(root, mapping_path))
        by_pair = {(r['identity'], r.get('density', 8)): r for r in selected.get('resources', [])}
        for transport in mapping['files']:
            identity, density = transport['identity'], transport.get('density', 8)
            row = by_pair.get((identity, density))
            if 'master' in selected:
                sources = [selected['master']['source_png']]
            elif 'masters' in selected:
                selector = {106:105,125:124}.get(identity % 10000,identity % 10000) if family == 'sonic' else identity % 10000
                sources = [r['source_png'] for r in selected['masters'] if r['selector'] == selector]
            else:
                sources = [row['source_png']]
            outputs = [transport['source_path']]
            if row and row['source_png'] not in sources:
                outputs.append(row['source_png'])
            consumers = [dict(path=transport['destination'], role=identity // 10000,
                              evidence=mapping_path)]
            # Identity joins only: never infer semantic consumers from equal pixels.
            global_row = registry.get(identity)
            if global_row and global_row['header_u32'][1] == density:
                global_path = 'assets/hd/global-assets-v1/' + global_row['path']
                raw = read(root, global_path)
                if hashlib.sha256(raw).hexdigest() != global_row['sha256'] or raw != read(root, transport['source_path']):
                    raise ValueError('Stale identity-bound global consumer')
                outputs.append(global_path)
            for member in runtime:
                if member['source_path'] not in outputs:
                    continue
                if hashlib.sha256(read(root, member['source_path'])).hexdigest() != member['sha256']:
                    raise ValueError('Stale runtime consumer binding')
                if member['destination'] not in {c['path'] for c in consumers}:
                    consumers.append(dict(path=member['destination'], role=identity // 10000,
                                          evidence=runtime_path))
            notes = ['Only declared consumers; not an exhaustive level-usage map.',
                     'Edit a candidate source, update its selection hash, then stage/review/apply with the existing family workflow; check alone does not rebuild.']
            if family == 'green' and identity in (80214, 80215, 80216):
                evidence = 'src/enemy_reuse_mirror.inc'
                if ('CURRENT_GREEN_' + str(identity) + '_RGBA').encode() not in read(root, evidence):
                    raise ValueError('Missing declared P05 current-source consumer')
                consumers.append(dict(path=evidence, role=146, material_identity=identity,
                                      scope='finite default-off P05 lane only', evidence=evidence))
            if family == 'protron':
                notes.append('One editable master, three independent cells; 244 and private 227 share the raw middle cell, not masked output. Original source coverage stays frozen.')
                if identity in (80226, 80244, 1470227):
                    evidence = 'src/enemy_reuse_mirror.inc'
                    if ('CURRENT_PROTRON_' + str(identity) + '_D8_PAYLOAD_FNV').encode() not in read(root, evidence):
                        raise ValueError('Missing declared P09 current-source consumer')
                    consumers.append(dict(path=evidence, role=146, material_identity=identity, scope='finite default-off P09 lane only', evidence=evidence))
            if family == 'sonic':
                evidence = 'src/enemy_reuse_mirror.inc'
                if ('CURRENT_SONIC_' + str(identity) + '_D8_PAYLOAD_FNV').encode() not in read(root, evidence):
                    raise ValueError('Missing declared P02 current-source consumer')
                consumers.append(dict(path=evidence, role=146, material_identity=identity,
                                      scope='finite default-off P02 lane only', evidence=evidence))
                notes.append('Two independent masters; each produces a horizontal mirror pair. Current preview/debug only; formal runtime package does not include this quartet. The atomic P02/P04 family needs these four plus 20/21.')
            if family == 'front-multi':
                notes.append('Eight independent inputs. Historical rear 1310182/1310183 do NOT follow current Front 163/164 edits.')
            if family == 'enemy-orb':
                notes.append('Two independent masters; ordinary role8 and masked role142 remain separate. Preview overlays only ordinary two; explicit contract view exports all four.')
            result.append(dict(family=family, identity=identity, density=density, role=identity // 10000,
                status='current-editable', editable_inputs=sources, source_inputs=sources,
                selection=selection_path, recipe=[command.split()[0]] + ([selected['recipe']['path']] if 'recipe' in selected else []) + (['scripts/current_enemy_orb_compatibility.py'] if family == 'enemy-orb' else []),
                derived_outputs=outputs, declared_consumers=consumers,
                rebuild_commands=['python3 ' + command + ' stage --selection <candidate.json> --stage <new-external-stage-dir>',
                                  'python3 ' + command + ' apply --stage <new-external-stage-dir>',
                                  'python3 ' + command + ' check'], notes=notes))
    # HUD contracts have names rather than numeric material identities. Preserve
    # their selected per-contract inputs rather than inventing a single UI master.
    import build_current_hud as hud
    import current_hud_recipe as recipe
    import current_hud_compatibility as compat
    selected = hud.selection(root, read(root, hud.SELECTION))
    mapping = compat.load(root)
    for key, sources in selected['resources'].items():
        name = recipe.CONTRACTS[key]['filename']
        paths = [r['path'] for r in sources]
        result.append(dict(family='hud', identity='hud:' + key, density=4, role='hud:' + key,
            status='current-editable', editable_inputs=paths, source_inputs=paths,
            selection=hud.SELECTION, recipe=['scripts/current_hud_recipe.py'] + [r['path'] for r in recipe.FIXED_INPUTS.values()],
            derived_outputs=['assets/hd/shared-ui-v1/' + name],
            declared_consumers=[dict(path=p, role='hud:' + key, evidence=compat.MAPPING) for p, r in mapping.items() if r['source_path'].endswith('/' + name)],
            rebuild_commands=['python3 scripts/build_current_hud.py stage --selection <candidate.json> --stage <new-external-stage-dir>',
                              'python3 scripts/build_current_hud.py apply --stage <new-external-stage-dir>',
                              'python3 scripts/build_current_hud.py check'],
            notes=['Multiple selected PNG inputs and fixed recipe inputs; not one automatic master.']))
    return result


def build_map(root):
    from shared_asset_special_sources import records
    resources = validate_records(current_records(root) + records(root))
    resources.sort(key=lambda r: (r['family'], str(r['identity']), r['density'], str(r['role'])))
    inputs = {}
    for row in resources:
        for source in row['source_inputs']:
            inputs.setdefault(source, []).append(dict(identity=row['identity'], density=row['density'],
                role=row['role'], status=row['status'], recipe=row['recipe']))
    return dict(schema='opentyrian-shared-asset-authoring-map-v1',
        scope='Validated declared current families including four Protron contracts and NEWSHF; not all levels or all historical artwork. Shared input contracts are bounded to records in this map.',
        resources=resources, inputs=[dict(path=p, contracts=inputs[p]) for p in sorted(inputs)])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--id', help='Exact material identity, e.g. 80112, 1420112, or hud:font')
    parser.add_argument('--format', choices=('text', 'json'), default='text')
    args = parser.parse_args()
    try:
        report = build_map(args.root.resolve())
        if args.id:
            report['resources'] = [r for r in report['resources'] if str(r['identity']) == args.id]
            if not report['resources']:
                raise ValueError('No declared contract for identity ' + args.id)
            paths = {p for r in report['resources'] for p in r['source_inputs']}
            report['inputs'] = [r for r in report['inputs'] if r['path'] in paths]
        if args.format == 'json':
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print(report['scope'])
            for row in report['resources']:
                print('\n{identity} / role {role} / density {density}: {family} [{status}]'.format(**row))
                for key in ('editable_inputs', 'source_inputs', 'recipe', 'derived_outputs', 'declared_consumers', 'rebuild_commands', 'notes'):
                    print('  ' + key + ': ' + json.dumps(row[key], ensure_ascii=False))
                for source in row['source_inputs']:
                    shared = next(r['contracts'] for r in report['inputs'] if r['path'] == source)
                    print('  shared source contracts: ' + json.dumps(shared, ensure_ascii=False))
    except (ValueError, OSError, KeyError) as exc:
        parser.exit(1, 'authoring map: ' + str(exc) + '\n')


if __name__ == '__main__':
    main()
