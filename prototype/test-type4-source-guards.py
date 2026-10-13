#!/usr/bin/env python3
"""Finite negative tests for the type4 public artwork wrapper; never runs a game."""
from pathlib import Path
import argparse
import json
import shutil
import subprocess
import sys

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--out', type=Path, required=True)
a = p.parse_args()
repo = Path(__file__).resolve().parents[1]
given, out = a.out.absolute(), a.out.resolve()
if (out.exists() or any(q.is_symlink() for q in [given, *given.parents])
        or repo == out or repo in out.parents or out in repo.parents):
    p.error('Choose a fresh directory outside the repository, without symlink components')
out.mkdir(parents=True)
script = repo / 'prototype/build-type4-art.py'
checks = []


def rejected(label, output, wrapper=script):
    run = subprocess.run([sys.executable, str(wrapper), '--output', str(output)],
                         capture_output=True, text=True, timeout=90)
    (out / (label + '.log')).write_text(run.stdout + run.stderr)
    assert run.returncode != 0, label
    checks.append(label)


for label, target in [('existing', out), ('repository', repo), ('repository-child', repo / 'type4-forbidden-output'),
                      ('repository-parent', repo.parent)]:
    rejected(label, target)
assert not (repo / 'type4-forbidden-output').exists()
link = out / 'link'
link.symlink_to(out, target_is_directory=True)
rejected('symlink-parent', link / 'not-created')
assert not (out / 'not-created').exists()
direct = out / 'direct'
direct.symlink_to(out / 'absent', target_is_directory=True)
rejected('symlink-output', direct)
assert not (out / 'absent').exists()

manifest = json.loads((repo / 'assets/hd/manifest.json').read_text())
minimal = out / 'pristine'
source_path = 'assets/hd/artwork/type4-fivepose-smooth-contour-v2'
(minimal / 'prototype').mkdir(parents=True)
shutil.copy2(script, minimal / 'prototype/build-type4-art.py')
shutil.copytree(repo / source_path, minimal / source_path)
historical = 'assets/hd/artwork/type4-fivepose-v1/proof/type4-source-proof.json'
(minimal / historical).parent.mkdir(parents=True)
shutil.copy2(repo / historical, minimal / historical)
shutil.copy2(repo / 'assets/hd/manifest.json', minimal / 'assets/hd/manifest.json')
for key in ('default_preview_pack', 'default_debug_pack'):
    name = manifest[key]
    (minimal / 'assets/hd/packs' / name).mkdir(parents=True)
    for sprite_id in (159, 161, 163, 165, 167):
        filename = f'enemy-newsh2-{sprite_id}-8.hda'
        entry = manifest['packs'][name]['files'][filename]
        for relative in [entry['source_png'], str(Path('assets/hd/packs') / name / filename)]:
            (minimal / relative).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(repo / relative, minimal / relative)
valid = subprocess.run([sys.executable, str(minimal / 'prototype/build-type4-art.py'),
                        '--output', str(out / 'valid')], capture_output=True, text=True, timeout=90)
(out / 'valid.log').write_text(valid.stdout + valid.stderr)
valid.check_returncode()
mutations = {
    'master': source_path + '/sources/generated-159.png',
    'mask': source_path + '/masks/authored-alpha-159-8.png',
    'contract': source_path + '/contract.json',
    'recipe': source_path + '/rebuild.py',
    'inventory': source_path + '/SHA256SUMS.json',
    'proof': source_path + '/proof/source-only-rebuild-audit.json',
    'canonical-png': manifest['packs'][manifest['default_preview_pack']]['files']['enemy-newsh2-159-8.hda']['source_png'],
    'packed-hda': str(Path('assets/hd/packs') / manifest['default_preview_pack'] / 'enemy-newsh2-159-8.hda'),
}
for label, relative in mutations.items():
    copy = out / ('bad-' + label)
    shutil.copytree(minimal, copy)
    target = copy / relative
    target.write_bytes(target.read_bytes() + b'\0')
    rejected(label, out / ('rebuilt-' + label), copy / 'prototype/build-type4-art.py')
for label in ('unlisted-source', 'source-symlink', 'widened4x'):
    copy = out / ('bad-' + label)
    shutil.copytree(minimal, copy)
    if label == 'unlisted-source':
        (copy / source_path / 'reference.png').write_bytes(b'not-an-approved-input')
    elif label == 'source-symlink':
        target = copy / source_path / 'sources/generated-159.png'
        target.rename(target.with_suffix('.retained'))
        target.symlink_to(minimal / source_path / 'sources/generated-159.png')
    else:
        path = copy / 'assets/hd/manifest.json'
        modified = json.loads(path.read_text())
        pack = modified['packs'][modified['default_debug_pack']]
        pack['files']['enemy-newsh2-159-4.hda'] = pack['files']['enemy-newsh2-159-8.hda']
        pack['count'] += 1
        path.write_text(json.dumps(modified))
    rejected(label, out / ('rebuilt-' + label), copy / 'prototype/build-type4-art.py')
report = {'status': 'passed', 'valid_generated_only_reproduction': True, 'rejected_cases': checks,
          'original_RGB_inputs': False, 'game_runs': 0}
(out / 'receipt.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
