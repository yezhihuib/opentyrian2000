#!/usr/bin/env python3
"""Bounded shared turret qualification against frozen inputs; never refreshes pins.

Run after focused edge/runtime tests and source freeze. This gate performs each
historical compatibility positive once, not the full historical test sweep.
Only the current Git index is read for asset modes; no historical objects,
index writes, game data, native gameplay, or Windows acceptance are required.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from unittest.mock import patch


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    root, out = args.root.resolve(), args.out.resolve()
    if out == root or root in out.parents:
        parser.error('--out must be outside the source checkout')
    # A fresh receipt directory prevents silently overwriting old evidence.
    out.mkdir(parents=True, exist_ok=False)
    os.environ['GIT_OPTIONAL_LOCKS'] = '0'
    sys.path[:0] = [str(root / 'tests'), str(root / 'scripts')]
    import shapesy_platform_projection as y
    import turret_newshf_projection as d
    import accepted_later_changes as a
    import shop_current_acceptance as shop
    from verify_current_production import verify

    assert y.ROOT.resolve() == root and a.ROOT.resolve() == root and shop.ROOT.resolve() == root
    sha = lambda raw: hashlib.sha256(raw).hexdigest()

    def git_index():
        return subprocess.check_output(['git', 'ls-files', '--stage', '-z'], cwd=root)

    def snapshot():
        names = set(subprocess.check_output(['git', 'ls-files', '-z'], cwd=root).decode().rstrip('\0').split('\0'))
        names |= d.qualified_paths(root) | y.qualified_paths(root) | {y.LEDGER,
            'tests/shapesy_platform_projection.py',
            'tests/run_turret_qualification.py',
            'tests/test_shapesy_platform_projection.py',
            'tests/test_shapesy_platform_runtime.py',
            'tests/test_shapesy_platform_edge_aa.py',
            'tests/test_turret_newshf_projection.py', 'tests/test_current_turret_newshf_authoring.py'}
        # Re-enumerate at both boundaries: additions and removals are mutations.
        for top in ('src', 'assets', 'authoring-inputs/shapesy-platform-current', 'authoring-inputs/newshf-turret'):
            names |= {p.relative_to(root).as_posix() for p in (root / top).rglob('*')
                      if p.is_file() or p.is_symlink()}
        names |= {p.relative_to(root).as_posix() for p in (root / 'tests').glob('*shapesy*.py')}
        result = {}
        for name in sorted(names):
            path = root / name
            assert path.is_file() and not path.is_symlink(), ('nonregular gate input', name)
            result[name] = sha(path.read_bytes())
        return result

    start, index_before = snapshot(), sha(git_index())
    report = dict(scope='bounded turret PRIVATEd293 + prior immutable inverse/current-source/P9/SHOP acceptance; '
                       'edge tests are separately executed; no game or Windows claim',
                  base=d.PRIVATE_BASE, before=start, current_index_sha256=index_before, phases={})

    def save():
        (out / 'receipt.json').write_text(json.dumps(report, indent=2) + '\n')

    def phase(name, call):
        print('START', name, flush=True)
        started = time.monotonic()
        try:
            result = call()
            report['phases'][name] = dict(status='PASS', seconds=round(time.monotonic()-started, 3), result=result)
            save()
            print('PASS', name, flush=True)
        except Exception as error:
            report['phases'][name] = dict(status='FAIL', seconds=round(time.monotonic()-started, 3), error=repr(error))
            report['status'] = 'FAIL'
            save()
            raise

    def tests():
        env = dict(os.environ, PYTHONPATH=os.pathsep.join((str(root/'tests'), str(root/'scripts'))))
        subprocess.run([sys.executable, '-m', 'unittest', 'test_turret_newshf_projection', 'test_dualmissile_newshf_projection', 'test_shapesy_platform_projection.ShapesYProjection.test_exact_inventory_and_runtime_projection', 'test_shapesy_platform_projection.ShapesYProjection.test_catalog_and_non_y_assets_keep_public_identity', '-v'],
                       cwd=root, env=env, check=True)
        return 'turret and prior dual inverse/mutation tests plus old Y inventory/runtime/catalog positives'

    def binding():
        receipt = json.loads((root/'packaging/current-production-validation.json').read_bytes())
        return dict(source_files=verify(root, receipt))

    def p9():
        a.validate_current_catalog(json.loads((root/y.CATALOG).read_bytes()))
        result = a.project_p9_inventory(a.current_asset_inventory())
        digest = sha(a.canonical(result))
        assert digest == '45ad4ff592f22934c23a4014708ad90fbc01518471144ea47aaef5f820dd583f' and len(result) == 7225
        return dict(sha256=digest, files=len(result))

    def shopgate():
        shop.check_current_inventory()
        original = Path.read_bytes
        targets = sorted(d.FILES | d.ADDED | {d.LEDGER,
            'authoring-inputs/newshf-turret/cold-master.png',
            'authoring-inputs/newshf-turret/hot-overlay.png',
            'authoring-inputs/newshf-turret/native-hot-mask.png',
            'assets/hd/authoring/newshf-turret.json',
            'assets/hd/current-compat/newshf-turret/newshf-role2100016-8.hda'})
        rejected = []
        for name in targets:
            def changed(path):
                raw = original(path)
                return raw+b'\n' if path == root/name else raw
            try:
                with patch.object(Path, 'read_bytes', changed):
                    shop.check_current_inventory()
            except (AssertionError, ValueError, OSError):
                rejected.append(name)
            else:
                raise AssertionError('SHOP accepted mutated turret dependency: '+name)
        return dict(positive=True, mutation_rejections=rejected)

    save()
    phase('current-production-binding', binding)
    phase('SHOP-positive-and-turret-mutations', shopgate)
    phase('current-source', a.validate_current_sources)
    phase('turret-and-nested-projection', tests)
    phase('P9-inventory-and-catalog', p9)
    report['after'] = snapshot()
    report['current_index_after_sha256'] = sha(git_index())
    assert start == report['after'], 'Inputs changed during bounded gate'
    assert index_before == report['current_index_after_sha256'], 'Current index changed during bounded gate'
    report['status'] = 'PASS'
    save()
    print('BOUNDED GATE PASS', flush=True)


if __name__ == '__main__':
    main()
