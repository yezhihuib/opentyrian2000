#!/usr/bin/env python3
"""Bounded statics qualification against frozen inputs; never refreshes pins.

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
    import projectile_statics_projection as d
    import accepted_later_changes as a
    import shop_current_acceptance as shop
    from verify_current_production import verify

    assert d.ROOT.resolve() == root and y.ROOT.resolve() == root and a.ROOT.resolve() == root and shop.ROOT.resolve() == root
    sha = lambda raw: hashlib.sha256(raw).hexdigest()

    def git_index():
        return subprocess.check_output(['git', 'ls-files', '--stage', '-z'], cwd=root)

    def snapshot():
        # Complete checkout file-membership closure, including untracked inputs.
        # Git administrative state and generated Python bytecode caches are not
        # source inputs; the Git index is separately bound before/after.
        names = {p.relative_to(root).as_posix() for p in root.rglob('*')
                 if '.git' not in p.relative_to(root).parts
                 and '__pycache__' not in p.relative_to(root).parts
                 and (p.is_file() or p.is_symlink())}
        names |= d.qualified_paths(root) | y.qualified_paths(root)
        result = {}
        for name in sorted(names):
            path = root / name
            assert path.is_file() and not path.is_symlink(), ('nonregular gate input', name)
            result[name] = sha(path.read_bytes())
        return result

    start, index_before = snapshot(), sha(git_index())
    report = dict(scope='bounded statics PUBLIC5e73a699 + prior immutable inverse/current-source/P9/SHOP acceptance; '
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
        subprocess.run([sys.executable, '-m', 'unittest', 'test_projectile_statics_projection', 'test_current_projectile_statics_authoring', 'test_projectile_statics_native_adapter', 'test_projectile_statics_runtime_contract', 'test_projectile_statics_fresh_native_adapter', 'test_projectile_gold_pulse_projection', 'test_current_projectile_gold_pulse_authoring', 'test_projectile_gold_pulse_native_adapter', 'test_projectile_gold_pulse_runtime_contract', 'test_projectile_gold_pulse_fresh_native_adapter', 'test_projectile_blue_triplet_projection', 'test_current_projectile_blue_triplet_authoring', 'test_projectile_blue_triplet_native_adapter', 'test_projectile_blue_triplet_runtime_contract', 'test_projectile_blue_triplet_fresh_native_adapter', 'test_runtime_packaging.PackagingTests.test_manifest_rebuild_is_deterministic', 'test_projectile61_projection', 'test_current_projectile61_authoring', 'test_projectile61_native_adapter', 'test_projectile61_gameplay_instrumentation', 'test_projectile61_gameplay_observer', 'test_projectile61_gameplay_differential', 'test_projectile61_fresh_native_adapter', 'test_projectile145_projection', 'test_current_projectile145_authoring', 'test_projectile145_gameplay_adapters', 'test_projectile145_fresh_native_adapter', 'test_shared170_bronze356_projection', 'test_current_aircraft170_newshf_authoring', 'test_current_shapesy_bronze356_authoring', 'test_aircraft170_native_adapter', 'test_shapesy_bronze356_runtime', 'test_shared170_inherited_native_adapter', 'test_shared170_gameplay_adapters', 'test_shared170_bronze356_borrow_adapter', 'test_shared170_bronze356_game_guards', 'test_aircraft169_newshf_projection', 'test_current_aircraft169_newshf_authoring', 'test_aircraft169_native_adapter', 'test_interceptor166_newshf_projection', 'test_current_interceptor166_newshf_authoring', 'test_interceptor166_native_adapter', 'test_fighter165_newshf_projection', 'test_current_fighter165_newshf_authoring', 'test_fighter165_native_adapter', 'test_scout164_newshf_projection', 'test_current_scout164_newshf_authoring', 'test_shapesy_cyan_secondary_projection', 'test_current_shapesy_cyan_secondary_authoring', 'test_shapesy_cyan_projection', 'test_current_shapesy_cyan_authoring', 'test_large_newshi_projection', 'test_turret_newshf_projection', 'test_dualmissile_newshf_projection', 'test_shapesy_platform_projection.ShapesYProjection.test_exact_inventory_and_runtime_projection', 'test_shapesy_platform_projection.ShapesYProjection.test_catalog_and_non_y_assets_keep_public_identity', '-v'],
                       cwd=root, env=env, check=True)
        return 'statics, gold-pulse, blue-triplet, projectile61, projectile145, combined170/356, aircraft169 and all prior inverse/mutation tests plus old Y inventory/runtime/catalog positives'

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
        import aircraft169_newshf_projection as old
        import current_aircraft169_newshf_compatibility as compat
        import shared170_bronze356_projection as shared
        import projectile145_projection as projectile145_source
        import projectile_gold_pulse_projection as gold_source
        import current_projectile_statics_compatibility as statics
        import projectile_blue_triplet_projection as blue_source
        import current_projectile_gold_pulse_compatibility as gold_pulse
        import projectile61_projection as projectile61_source
        import current_projectile_blue_triplet_compatibility as blue_triplet
        import current_projectile61_compatibility as projectile61
        import current_projectile145_compatibility as projectile145
        import current_aircraft170_newshf_compatibility as aircraft170
        import current_shapesy_bronze356_compatibility as bronze356
        import interceptor166_newshf_projection as prior
        import current_interceptor166_newshf_compatibility as prior_compat
        targets = sorted(old.FILES | old.ADDED | {old.LEDGER} | compat.input_paths(root) |
                         {compat.ROOT+'/'+compat.name(i) for i in compat.IDS} |
                         prior.FILES | prior.ADDED | {prior.LEDGER} | prior_compat.input_paths(root) |
                         {prior_compat.ROOT+'/'+prior_compat.name(i) for i in prior_compat.IDS} |
                         shared.FILES | shared.ADDED | {shared.LEDGER} | aircraft170.input_paths(root) | bronze356.input_paths(root) |
                         {aircraft170.ROOT+'/'+aircraft170.name(i) for i in aircraft170.IDS} |
                         {bronze356.ROOT+'/'+bronze356.name(i) for i in bronze356.IDS} |
                         projectile145_source.FILES | projectile145_source.ADDED | {projectile145_source.LEDGER} | projectile145.input_paths(root) |
                         projectile61_source.FILES | projectile61_source.ADDED | {projectile61_source.LEDGER} | projectile61.input_paths(root) |
                         blue_source.FILES | blue_source.ADDED | {blue_source.LEDGER} | blue_triplet.input_paths(root) |
                         gold_source.FILES | gold_source.ADDED | {gold_source.LEDGER} | gold_pulse.input_paths(root) |
                         d.FILES | d.ADDED | {d.LEDGER} | statics.input_paths(root))
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
                raise AssertionError('SHOP accepted mutated statics or prior dependency: '+name)
        return dict(positive=True, mutation_rejections=rejected)

    save()
    phase('current-production-binding', binding)
    phase('current-source', a.validate_current_sources)
    phase('P9-inventory-and-catalog', p9)
    phase('SHOP-positive-and-statics-and-prior-gold-blue61-145-combined169-166-mutations', shopgate)
    phase('statics-and-nested-projection', tests)
    try:
        report['after'] = snapshot()
        report['current_index_after_sha256'] = sha(git_index())
    except Exception as error:
        report['status']='FAIL';report['error']='Final complete-checkout snapshot failed: '+repr(error);save()
        raise
    if start != report['after'] or index_before != report['current_index_after_sha256']:
        report['status']='FAIL';report['error']='Complete checkout membership/bytes or current index changed during bounded gate';save()
        raise AssertionError(report['error'])
    report['status'] = 'PASS'
    save()
    print('BOUNDED GATE PASS', flush=True)


if __name__ == '__main__':
    main()
