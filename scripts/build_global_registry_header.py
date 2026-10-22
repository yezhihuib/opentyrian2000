#!/usr/bin/env python3
"""Generate C resource, source and palette pins from the reviewed global registry."""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--registry', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    raw = a.registry.read_bytes()
    registry = json.loads(raw)
    names = ['talon', 'shield', 'pulse', 'hitflare', 'vulcan', 'smoke', 'small_explosion', 'cash25', 'cash50', 'cash75', 'gem100', 'gem250', 'rotor', 'green']
    if len(registry['resources']) != 120 or len(registry['families']) != len(names):
        raise ValueError('Expected reviewed 120-resource, fourteen-family registry')
    expected_names = ['normal-talon', 'player-shield-hit', 'player-front-pulse', 'moving-hitflare', 'player-front-vulcan', 'moving-white-smoke', 'moving-small-explosion', 'cash25-body-and-value', 'cash50-body-and-value', 'cash75-body-and-value', 'gem100-body-and-value', 'gem250-body-and-value', 'rotor-enemy-5-and-11', 'green-energy-head-and-trail']
    if [f['name'] for f in registry['families']] != expected_names:
        raise ValueError('Unexpected family order or identity')
    out = ['/* SPDX-License-Identifier: GPL-2.0-or-later',
           ' * Generated from reviewed global-assets-v1/registry.json.',
           ' * Regenerate with scripts/build_global_registry_header.py; do not edit pins.',
           ' * Registry SHA256: ' + hashlib.sha256(raw).hexdigest() + ' */',
           '#ifndef GLOBAL_ASSET_REGISTRY_H', '#define GLOBAL_ASSET_REGISTRY_H',
           '#include <stdint.h>',
           'typedef struct { unsigned identity,bytes,density,width,height; int anchor_x,anchor_y; const char *path; uint64_t payload_fnv; } GlobalAssetResource;',
           'typedef struct { unsigned index; uint64_t fnv; } GlobalAssetSourceTile;',
           'typedef struct { unsigned index; uint32_t rgb; } GlobalAssetPaletteColor;',
           'static const GlobalAssetResource global_asset_resources[] = {']
    for r in registry['resources']:
        i, d, w, h, x, y = r['header_u32']
        x = x if x < 2**31 else x - 2**32
        y = y if y < 2**31 else y - 2**32
        out.append(' {%du,%du,%du,%du,%du,%d,%d,%s,UINT64_C(0x%s)},' %
                   (i, r['bytes'], d, w, h, x, y, json.dumps(r['path']), r['payload_fnv64']))
    out += ['};', 'enum { GLOBAL_ASSET_RESOURCE_COUNT = 120, GLOBAL_ASSET_FAMILY_COUNT = 14 };']
    for name, family in zip(names, registry['families']):
        source = family['source_identity']
        out.append('enum { GLOBAL_%s_BANK_BYTES = %d };' % (name.upper(), source['bank_bytes']))
        out.append('static const GlobalAssetSourceTile global_%s_source[] = {' % name)
        out += [' {%du,UINT64_C(0x%s)},' % (t['index'], t['source_fnv64']) for t in source['tiles']]
        out.append('};')
        pal = source['palette']
        ids = pal.get('indices', list(range(pal.get('first_index', 0), pal.get('first_index', 0) + pal.get('count', 0))))
        out.append('static const GlobalAssetPaletteColor global_%s_palette[] = {' % name)
        out += [' {%du,UINT32_C(0x%s)},' % (i, c) for i, c in zip(ids, pal['rgb_hex'])]
        out.append('};')
        if 'visuals' in family:
            ids = [v['resource_identity'] for v in family['visuals']]
        elif 'phases' in family:
            ids = [v['resource_identity'] or 0 for v in family['phases']]
        else:
            ids = family['resources']
        out.append('static const unsigned global_%s_resource_ids[] = {%s};' % (name, ','.join(str(v) + 'u' for v in ids)))
        if 'phases' in family:
            out.append('static const unsigned global_%s_phase_indices[] = {%s};' % (name, ','.join(str(v['index']) + 'u' for v in family['phases'])))
            out.append('static const unsigned global_%s_phase_ttl[] = {%s};' % (name, ','.join(str(v['ttl']) + 'u' for v in family['phases'])))
        value_source = source.get('value_source')
        if value_source:
            out.append('enum { GLOBAL_%s_VALUE_BANK_BYTES = %d };' % (name.upper(), value_source['bank_bytes']))
            out.append('static const GlobalAssetSourceTile global_%s_value_source[] = {' % name)
            out += [' {%du,UINT64_C(0x%s)},' % (t['index'], t['source_fnv64']) for t in value_source['tiles']]
            out.append('};')
        enemy_identity = source.get('enemy_identity')
        if enemy_identity:
            out.append('enum { GLOBAL_%s_RECORD_INDEX = %d, GLOBAL_%s_RECORD_BYTES = %d };' %
                       (name.upper(), enemy_identity['record_index'], name.upper(), enemy_identity['record_bytes']))
            out.append('static const uint64_t global_%s_record_fnv[] = {%s};' %
                       (name, ','.join('UINT64_C(0x' + v + ')' for v in enemy_identity['record_fnv64_variants'])))
        for record in source.get('enemy_records', []):
            out.append('static const uint64_t global_%s_record%d_fnv[] = {%s};' % (name, record['record_index'], ','.join('UINT64_C(0x' + v + ')' for v in record['record_fnv64_variants'])))
        for part in ('head', 'smoke'):
            part_source = source.get(part + '_source')
            if not part_source:
                continue
            out.append('enum { GLOBAL_%s_%s_BANK_BYTES = %d };' % (name.upper(), part.upper(), part_source['bank_bytes']))
            out.append('static const GlobalAssetSourceTile global_%s_source_%s[] = {' % (name, part))
            out += [' {%du,UINT64_C(0x%s)},' % (t['index'], t['source_fnv64']) for t in part_source['tiles']]
            out.append('};')
        weapon_records = source.get('weapon_records')
        if weapon_records:
            out.append('static const unsigned global_%s_weapon_ids[] = {%s};' % (name, ','.join(str(r['record_index']) + 'u' for r in weapon_records)))
            out.append('static const uint64_t global_%s_weapon_fnv[%d][3] = {' % (name, len(weapon_records)))
            out += [' {' + ','.join('UINT64_C(0x' + v + ')' for v in r['record_fnv64_variants']) + '},' for r in weapon_records]
            out.append('};')
        weapon = source.get('weapon_identity')
        if weapon:
            out.append('enum { GLOBAL_%s_PORT = %d, GLOBAL_%s_FIRST_RECORD = %d };' % (name.upper(), weapon['port_index'], name.upper(), weapon['record_indices'][0]))
            out.append('#define GLOBAL_%s_PORT_FNV UINT64_C(0x%s)' % (name.upper(), weapon['port_fnv64']))
            out.append('static const uint64_t global_%s_record_fnv[11][3] = {' % name)
            out += [' {' + ','.join('UINT64_C(0x' + v + ')' for v in row) + '},' for row in weapon['record_fnv64_variants']]
            out.append('};')
    out += ['#endif', '']
    a.output.write_bytes('\n'.join(out).encode('utf-8'))
    print('Generated reconstructed header:', a.output, hashlib.sha256(a.output.read_bytes()).hexdigest())


if __name__ == '__main__':
    main()
