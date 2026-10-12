#!/usr/bin/env python3
"""Finite HUF source packaging, standalone rebuild, relocation and path guards."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'prototype'))
from gameplay_hud_font_bundle import build_bundle, FILENAME, SOURCE, SOURCE_FILES

sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def invoke(script, out, cwd, success=True):
    result = subprocess.run([sys.executable, str(script), '--output', str(out)], cwd=cwd,
        env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    assert (result.returncode == 0) == success, (script, out, result.stdout, result.stderr)
    return result

source = ROOT / SOURCE
before = {n: sha(source / n) for n in SOURCE_FILES}
raw, receipt = build_bundle(ROOT)
wrapper = ROOT / 'prototype/build-gameplay-hud-font.py'
with tempfile.TemporaryDirectory(prefix='huf-package-') as temp:
    d = Path(temp)
    cwd = d / 'foreign working directory'; cwd.mkdir()
    output = d / 'fresh output with spaces'
    invoke(wrapper, output, cwd)
    assert (output / FILENAME).read_bytes() == raw
    # Existing output, repository destination/descendant/ancestor, and symlink paths.
    for out in (output, ROOT, ROOT / 'must-not-create-huf-output', ROOT.parent):
        invoke(wrapper, out, cwd, False)
    assert not (ROOT / 'must-not-create-huf-output').exists()
    real = d / 'real destination'; real.mkdir()
    link = d / 'linked destination'; link.symlink_to(real, target_is_directory=True)
    invoke(wrapper, link / 'fresh', cwd, False)
    assert not (real / 'fresh').exists()
    # Relocated repository wrapper: only this finite family and three Python modules.
    relocated = d / 'relocated repo with spaces'; (relocated / 'prototype').mkdir(parents=True)
    for name in ('build-gameplay-hud-font.py', 'gameplay_hud_font_bundle.py', 'gameplay_hud_extension_bundles.py'):
        shutil.copy2(ROOT / 'prototype' / name, relocated / 'prototype' / name)
    shutil.copytree(source, relocated / SOURCE)
    manifest = json.loads((ROOT / 'assets/hd/manifest.json').read_text())
    (relocated / 'assets/hd/manifest.json').write_text(json.dumps({'gameplay_hud_font_v1': manifest['gameplay_hud_font_v1']}))
    invoke(relocated / 'prototype/build-gameplay-hud-font.py', d / 'relocated output', cwd)
    assert (d / 'relocated output' / FILENAME).read_bytes() == raw
    # Seven independent authored inputs; no canonical resource/image/alpha is present.
    standalone = d / 'standalone sources'; standalone.mkdir()
    inputs = ['build_resource.py', 'reproduce.py', 'requirements.txt'] + sorted(n for n in SOURCE_FILES if n.startswith('sources/'))
    assert len(inputs) == 7
    for name in inputs:
        path = standalone / name; path.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(source / name, path)
    generated = d / 'standalone output'
    subprocess.run([sys.executable, str(standalone / 'build_resource.py'), '--output', str(generated / FILENAME),
        '--proof-output', str(generated / 'proof')], cwd=cwd, check=True, stdout=subprocess.PIPE,
        env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
    assert (generated / FILENAME).read_bytes() == raw
    for name in ('tiny-coverage-atlas-4x.png', 'tiny-coverage-atlas-4x.alpha.bin', 'tiny-vector-atlas.svg'):
        assert (generated / 'proof' / name).read_bytes() == (source / 'canonical' / name).read_bytes()
    # Finite inventory, corrupt canonical payload, and symlink input reject locally.
    local_source = relocated / SOURCE
    extra = local_source / 'extra.txt'; extra.write_text('unlisted')
    try: build_bundle(relocated)
    except AssertionError: pass
    else: raise AssertionError('extra source accepted')
    extra.unlink()
    target = local_source / 'canonical' / FILENAME; saved = target.read_bytes(); target.write_bytes(saved[:-1] + bytes([saved[-1] ^ 1]))
    try: build_bundle(relocated)
    except AssertionError: pass
    else: raise AssertionError('corrupt payload accepted')
    target.unlink(); target.symlink_to(source / 'canonical' / FILENAME)
    try: build_bundle(relocated)
    except AssertionError: pass
    else: raise AssertionError('symlink source accepted')
assert {n: sha(source / n) for n in SOURCE_FILES} == before
print(json.dumps({'status': 'PASS', 'source_files_exact_and_unchanged': 19, 'standalone_inputs': 7,
    'fresh_relocated_standalone_rebuilds': 3, 'output_guard_rejections': 5,
    'inventory_payload_symlink_rejections': 3, 'resource': receipt}, indent=2))
