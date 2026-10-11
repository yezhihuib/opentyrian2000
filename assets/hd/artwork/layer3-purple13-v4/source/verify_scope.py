#!/usr/bin/env python3
"""Read-only exact v3-to-v4 pixel, source boundary, and HDR1 scope audit."""
from pathlib import Path
import argparse
import json
import runpy
import tempfile

common = runpy.run_path(str(Path(__file__).resolve().with_name('reconstruct_v3.py')))
IDS, FRINGE_IDS = common['IDS'], common['FRINGE_IDS']
require, sha, rgba, hda = [common[k] for k in ('require', 'sha', 'rgba', 'hda')]


def verify(package, target, baseline=None):
    if baseline is None:
        with tempfile.TemporaryDirectory(prefix='purple13-v3-scope-') as temporary:
            baseline, _ = common['reconstruct'](package, Path(temporary))
    contract = json.loads((package / 'source/rebuild-contract.json').read_text())
    manifest_path = package / 'runtime-overlay/manifest.json'
    require(sha(manifest_path.read_bytes()) == common['V4_MANIFEST_SHA'] ==
            contract['selected_manifest_sha256'], 'Frozen v4 manifest differs')
    manifest = json.loads(manifest_path.read_text())
    require(contract['ids'] == manifest['source_ids'] == IDS and
            contract['slots'] == manifest['slots'] == list(range(290, 303)), 'Family scope differs')
    require(contract['fringe_override_ids'] == FRINGE_IDS and
            contract['unchanged_v3_ids'] == [i for i in IDS if i not in FRINGE_IDS], 'Fringe scope differs')
    require([r['id'] for r in contract['items']] == IDS, 'Contract item order differs')
    require(contract['fringe_scope']['decoded_rows_inclusive'] == [208, 223] and
            contract['fringe_scope']['rgb_delta_cap'] == 28, 'Finite fringe bounds differ')
    require({p.name for p in (target / 'output').iterdir()} ==
            {f'terrain-shapesz-{i}-8.png' for i in IDS}, 'Unexpected output PNG scope')
    require({p.name for p in (target / 'runtime-overlay').iterdir()} ==
            {f'terrain-shapesz-{i}-8.hda' for i in IDS} | {'manifest.json'}, 'Unexpected HDA scope')
    require((target / 'runtime-overlay/manifest.json').read_bytes() == manifest_path.read_bytes(),
            'Target manifest differs')
    baseline_rows = {r['id']: r for r in json.loads(
        (package / 'source/upstream-v3/rebuild-contract.json').read_text())['items']}
    results = []
    changed_ids = []
    for index, row in enumerate(contract['items']):
        tile = row['id']
        stem = f'terrain-shapesz-{tile}-8'
        before, after = baseline[tile], rgba(target / 'output' / (stem + '.png'))
        require(sha(before) == baseline_rows[tile]['selected_rgba_sha256'] == row['v3_rgba_sha256'],
                f'Baseline v3 RGBA differs: {tile}')
        require(sha(hda(tile, before)) == baseline_rows[tile]['selected_hda_sha256'] == row['v3_hda_sha256'],
                f'Baseline v3 HDA differs: {tile}')
        require(set(before[3::4]) == {255} and before[3::4] == after[3::4], f'Alpha differs: {tile}')
        require(sha(after) == row['selected_rgba_sha256'], f'Selected RGBA differs: {tile}')
        changes = []
        changed_rows = set()
        max_delta = 0
        for pixel in range(192 * 224):
            offset = pixel * 4
            a, b = before[offset:offset + 4], after[offset:offset + 4]
            if a != b:
                x, y = pixel % 192, pixel // 192
                require(tile in FRINGE_IDS and 208 <= y <= 223,
                        f'Pixel changed outside finite fringe ROI: {tile}, {x}, {y}')
                require(all(b[c] <= a[c] for c in range(3)), f'Fringe unexpectedly brightened: {tile}')
                changes.append((x, y)); changed_rows.add(y)
                max_delta = max(max_delta, *(abs(a[c] - b[c]) for c in range(3)))
        bounds = ([min(x for x, y in changes), min(y for x, y in changes),
                   max(x for x, y in changes), max(y for x, y in changes)] if changes else None)
        require(max_delta <= 28 and max_delta == row['max_rgb_delta_from_v3'], f'RGB delta differs: {tile}')
        require(len(changes) == row['fringe_changed_hd_pixels'], f'Change count differs: {tile}')
        require(bounds == row['changed_bbox_inclusive'], f'Change bounds differ: {tile}')
        require(row['slot'] == 290 + index, f'Slot differs: {tile}')
        payload = (target / 'runtime-overlay' / (stem + '.hda')).read_bytes()
        require(len(payload) == 172060 and payload == hda(tile, after), f'HDR1 layout differs: {tile}')
        require(sha(payload) == row['selected_hda_sha256'] == manifest['files'][stem + '.hda'],
                f'Frozen HDA differs: {tile}')
        if changes:
            changed_ids.append(tile)
            require(changed_rows == set(range(208, 224)), f'Changed-row set differs: {tile}')
        else:
            require(before == after and sha(payload) == row['v3_hda_sha256'], f'Unchanged tile differs: {tile}')
        results.append({'id': tile, 'slot': row['slot'], 'changed_hd_pixels': len(changes),
                        'changed_bbox_inclusive': bounds, 'changed_rows': sorted(changed_rows),
                        'max_rgb_channel_delta': max_delta, 'alpha_exact_all255': True,
                        'dimensions_anchor_header_exact': True, 'outside_roi_rgba_exact': True,
                        'selected_rgba_and_hda_exact': True})
    require(changed_ids == FRINGE_IDS, 'Exactly three changed tiles required')
    return {'status': 'PASS', 'comparison': 'v4 against freshly reconstructed exact v3',
            'tiles': 13, 'slots': list(range(290, 303)), 'override_ids': FRINGE_IDS,
            'unchanged_v3_tiles': 10, 'total_changed_hd_pixels': sum(r['changed_hd_pixels'] for r in results),
            'maximum_rgb_channel_delta': max(r['max_rgb_channel_delta'] for r in results),
            'all_alpha_exact_255': True, 'finite_three_roi_only': True,
            'allowed_and_actual_changed_rows': list(range(208, 224)), 'items': results}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rebuild-root', type=Path,
                        help='Defaults to checking selected outputs shipped in the package')
    args = parser.parse_args()
    package = Path(__file__).resolve().parent.parent
    print(json.dumps(verify(package, args.rebuild_root.resolve() if args.rebuild_root else package), indent=2))
