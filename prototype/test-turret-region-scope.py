#!/usr/bin/env python3
"""Prove the live-turret sibling predicate is the only production change."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BASE = '884b9acc5e015cd964a6afe3cc7c4e95cfd2c485'
PATH = 'src/render_mirror.c'
LIVE = b'if(regions[j].live&&regions[j].bank==ASSET_NEWSH2'
LEGACY = b'if(regions[j].bank==ASSET_NEWSH2'


def git(*args, **kwargs):
    return subprocess.check_output(['git', '-C', str(ROOT), *args], **kwargs)


def source_inverse(current, baseline):
    assert set(current) == set(baseline), 'Production inventory changed'
    assert {p for p in current if current[p] != baseline[p]} == {PATH}, 'Production change escaped renderer'
    raw = current[PATH]
    assert raw.count(LIVE) == 1 and raw.count(LEGACY) == 0, 'Missing or repeated live-sibling guard'
    restored = dict(current)
    restored[PATH] = raw.replace(LIVE, LEGACY, 1)
    assert restored == baseline, 'Change beyond the exact sibling-live predicate'
    return restored


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    root, out = args.root.resolve(), args.out.resolve()
    assert not out.exists(), 'Report must be new'
    assert out != root and root not in out.parents, 'Report must stay outside checkout'
    names = git('ls-tree', '-r', '--name-only', BASE, '--', 'src').decode().splitlines()
    actual = {str(p.relative_to(root)) for p in (root / 'src').rglob('*') if p.is_file() or p.is_symlink()}
    assert actual == set(names) and not any((root / p).is_symlink() for p in names)
    baseline = {p: git('show', BASE + ':' + p) for p in names}
    current = {p: (root / p).read_bytes() for p in names}
    restored = source_inverse(current, baseline)
    negative = []
    for name, path, before, after in [
        ('removed sibling-live guard', PATH, LIVE, LEGACY),
        ('changed turret identity', PATH, b'int ids[4]={77,79,115,117}', b'int ids[4]={78,79,115,117}'),
        ('changed closure overlap', PATH, b'r.x<q.x+q.w', b'r.x<=q.x+q.w'),
        ('broadened Plasma vertical admission', PATH, b'y<=-(int)h||y>=200', b'false'),
        ('changed indexed blend arithmetic', 'src/sprite.c', b' / 2)', b' / 3)'),
        ('changed gameplay source', 'src/shots.c', b'#include', b'/* changed */\n#include'),
    ]:
        mutated = dict(current)
        assert before in mutated[path], name
        mutated[path] = mutated[path].replace(before, after, 1)
        try:
            source_inverse(mutated, baseline)
        except AssertionError:
            negative.append(name)
        else:
            raise AssertionError('Scope guard accepted: ' + name)
    pins = {}
    for line in git('ls-tree', '-r', BASE, '--', 'assets').decode().splitlines():
        metadata, path = line.split('\t')
        mode, kind, oid = metadata.split()
        assert kind == 'blob' and mode in ('100644', '100755')
        pins[path] = (mode, oid)
    actual = {str(p.relative_to(root)) for p in (root / 'assets').rglob('*') if p.is_file() or p.is_symlink()}
    assert actual == set(pins) and not any((root / p).is_symlink() for p in pins)
    paths = sorted(pins)
    hashes = subprocess.check_output(['git', '-C', str(root), 'hash-object', '--no-filters', '--stdin-paths'],
                                     input=('\n'.join(paths) + '\n').encode()).decode().splitlines()
    assert len(hashes) == len(paths)
    for path, oid in zip(paths, hashes):
        assert oid == pins[path][1] and bool((root / path).stat().st_mode & 0o100) == (pins[path][0] == '100755'), path
    report = {
        'status': 'PASS', 'baseline': BASE,
        'production_files_checked': len(names), 'production_files_changed': [PATH],
        'exact_one_predicate_inverse': restored == baseline,
        'renderer_sha256': hashlib.sha256(current[PATH]).hexdigest(),
        'all_asset_bytes_and_modes_unchanged': len(paths),
        'negative_controls_rejected': negative,
        'gameplay_indexed_blitters_Plasma_clouds_and_all_other_production_bytes_unchanged': True,
        'game_runs': 0,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + '\n')
    print(f'PASS: {len(names)} production files, exact one-predicate inverse, {len(paths)} unchanged assets, {len(negative)} rejected mutations')


if __name__ == '__main__':
    main()
