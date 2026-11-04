#!/usr/bin/env python3
"""Build a new finite terrain23 registration manifest, never a complete package.

Preserves the fixed1138 old nonbinding rows without claiming to re-read their
missing payloads. The normal full packager/rebuild and their old validators remain
required for full package acceptance. No downloads, rendering or source writes.
"""
import argparse
import copy
import json
from pathlib import Path

import current_tank194_body_registration as checked
import current_terrain23_registration as terrain
import current_terrain23_source_bridge as bridge


def output_path(path, root, inputs):
    path = Path(path).absolute()
    if path.exists() or path.is_symlink():
        raise ValueError('Output must be new: ' + str(path))
    if not path.parent.is_dir() or any(p.is_symlink() for p in (path.parent, *path.parents)):
        raise ValueError('Output parent must be an existing nonsymlink directory')
    resolved = path.resolve()
    if resolved.is_relative_to(root.resolve()) or resolved in {p.resolve() for p in inputs}:
        raise ValueError('Output must be outside source root and inputs')
    return path


def build(root, base_manifest):
    root, base_manifest = Path(root), Path(base_manifest)
    bridge.verify_source_epoch(root)
    proof = terrain.authority(root)
    base_raw = checked.regular(base_manifest.parent, base_manifest.name, 4 * 1024 * 1024)
    if checked.sha(base_raw) != proof['base_runtime_manifest_sha256']:
        raise ValueError('Expected exact public TOPCLIP1139 base manifest')
    base = checked.object_bytes(base_raw)
    binding_raw = checked.regular(root, bridge.BINDING, 2 * 1024 * 1024)
    rows = copy.deepcopy(base['files'])
    binding = [row for row in rows if row.get('source_path') == bridge.BINDING]
    if len(rows) != 1139 or len(binding) != 1:
        raise ValueError('Changed fixed base manifest structure')
    binding[0].update(bytes=len(binding_raw), sha256=checked.sha(binding_raw),
                      git_blob=checked.blob(binding_raw))
    rows.extend(terrain.load(root).values())
    result = copy.deepcopy(proof['candidate_metadata'])
    result['files'] = sorted(rows, key=lambda row: row['destination'])
    report = bridge.validate_runtime_rows(root, result, required=True)
    return result, report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--base-manifest', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args(argv)
    out = output_path(args.output, args.root, [args.base_manifest])
    report_path = output_path(args.report, args.root, [args.base_manifest, out]) if args.report else None
    if report_path == out:
        raise ValueError('Output and report must differ')
    result, report = build(args.root, args.base_manifest)
    # No files are created until all bounded inputs and generated rows pass.
    with out.open('xb') as stream:
        stream.write((json.dumps(result, indent=2, sort_keys=True) + '\n').encode())
    report = dict(report, output=str(out), full_package_status='NOT_ACCEPTED_MISSING_OLD_PAYLOADS')
    if report_path:
        with report_path.open('xb') as stream:
            stream.write((json.dumps(report, indent=2, sort_keys=True) + '\n').encode())
    print(json.dumps(report, sort_keys=True))


if __name__ == '__main__':
    main()
