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
    """The fixed craft267 body plus the six independently selected current bodies."""
    from current_sidekick_body_compatibility import load as sidekick_load
    from build_current_sidekick_body import selection as sidekick_selection, source_blob as sidekick_blob
    load(root)
    selected = selection(root, read(root, SELECTION))
    canonical = read(root, CANONICAL)
    if source_blob(root, selected['resources'][0]) != canonical:
        raise ValueError('Stale craft267 selected pixels')
    files = {NAME: canonical}
    six = sidekick_selection(root, read(root, 'assets/hd/authoring/sidekick-body-current.json'))
    mapping = sidekick_load(root)
    for row in six['resources']:
        generated, _ = sidekick_blob(root, row)
        matched = [entry for entry in mapping.values() if entry['identity'] == row['identity']]
        if len(matched) != 1:
            raise ValueError('Missing current sidekick body consumer')
        entry = matched[0]
        data = read(root, entry['source_path'])
        if generated != data:
            raise ValueError('Stale sidekick selected pixels')
        name = entry['destination'].removeprefix('assets/gameplay/')
        if '/' in name or name in files:
            raise ValueError('Current preview overlay collision')
        files[name] = data
    if len(files) != 7:
        raise ValueError('Expected exactly seven current body overlays')
    return files


def view(root, kind, destination):
    """Materialize one frozen pack plus the seven fixed current body overlays."""
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
    if not set(overlays).issubset(files):
        raise ValueError('Missing original current body consumer')
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
    p.add_argument('--kind', choices=tuple(BASES))
    p.add_argument('--output', type=Path)
    a = p.parse_args()
    root = a.root.resolve()
    if a.mode == 'check':
        result = check(root)
    elif a.mode == 'view':
        if not a.kind or not a.output:
            p.error('view requires --kind and --output')
        result = view(root, a.kind, a.output)
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
