#!/usr/bin/env python3
"""Exercise late-spike source/build rejection using independent fixture copies.

Never mutates the real artwork, canonical files, packs, original data or Git.
No hardlinks are used. No game is run. All receipts and fixtures stay external.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys

from nondefault_pack_fixture import NONDEFAULT_PACK, add_nondefault_pack_fixture

SOURCE = 'assets/hd/artwork/late-spike-v1'
SCRIPT = 'prototype/build-late-spike-art.py'
IDS = [1, 3, 5, 7, 9, 11]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    given = args.out.expanduser()
    require(given.is_absolute(), 'absolute external output required')
    require(not any(path.is_symlink() for path in [given, *given.parents]), 'output symlinks forbidden')
    out = given.resolve()
    require(not out.exists() and out.parent.is_dir(), 'fresh output with existing parent required')
    require(out != repo and out not in repo.parents and repo not in out.parents, 'external output required')
    out.mkdir()
    checks = []
    script = repo / SCRIPT

    def run(wrapper, target):
        return subprocess.run([sys.executable, str(wrapper), '--output', str(target)],
                              capture_output=True, text=True, timeout=90)

    def rejected(label, target, reason, wrapper=script):
        existed = target.exists() or target.is_symlink()
        result = run(wrapper, target)
        require(result.returncode != 0 and 'ERROR:' in result.stderr and reason in result.stderr,
                f'{label}: expected controlled rejection {reason!r}; got {result.returncode}\n{result.stdout}\n{result.stderr}')
        if not existed:
            require(not target.exists() and not target.is_symlink(), 'rejection created output: ' + label)
        checks.append({'case': label, 'reason': reason, 'returncode': result.returncode})
        return result

    for label, target, reason in [
        ('existing', out, 'output must be fresh'),
        ('repository', repo, 'output must be fresh'),
        ('repository-parent', repo.parent, 'output must be fresh'),
        ('repository-child', repo / 'late-spike-forbidden-output', 'output must be outside repository'),
        ('relative', Path('late-spike-forbidden-output'), 'output must be absolute'),
        ('missing-parent', out / 'missing' / 'output', 'output parent must exist'),
    ]:
        rejected(label, target, reason)
    require(not (repo / 'late-spike-forbidden-output').exists(), 'forbidden output created')
    link = out / 'link'
    link.symlink_to(out, target_is_directory=True)
    rejected('symlink-parent', link / 'absent', 'symlink path forbidden')
    direct = out / 'direct'
    direct.symlink_to(out / 'absent', target_is_directory=True)
    rejected('symlink-output', direct, 'symlink path forbidden')
    require(not (out / 'absent').exists(), 'symlink output created')
    manifest = json.loads((repo / 'assets/hd/manifest.json').read_text())
    fixture = out / 'fixture'
    files = {SCRIPT, 'assets/hd/manifest.json'}
    files.update(path.relative_to(repo).as_posix() for path in (repo / SOURCE).rglob('*') if path.is_file())
    for base in IDS:
        name = f'enemy-newsh2-{base}-8.hda'
        for key in ['default_preview_pack', 'default_debug_pack']:
            pack = manifest[key]
            row = manifest['packs'][pack]['files'][name]
            files.add(row['source_png'])
            files.add(f'assets/hd/packs/{pack}/{name}')
    before = {name: digest(repo / name) for name in files}
    for name in sorted(files):
        target = fixture / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(repo / name, target)
        require(not target.samefile(repo / name), 'fixture must not share inode: ' + name)
    wrapper = fixture / SCRIPT
    valid = run(wrapper, out / 'valid')
    require(valid.returncode == 0, 'valid fixture failed:\n' + valid.stdout + valid.stderr)
    (out / 'valid.stdout.txt').write_text(valid.stdout)

    def corrupted(label, relative, reason):
        path = fixture / relative
        original = path.read_bytes()
        try:
            path.write_bytes(original + b'\0')
            rejected(label, out / ('bad-' + label), reason, wrapper)
            require(not (out / ('bad-' + label)).exists(), 'failed validation wrote output: ' + label)
        finally:
            path.write_bytes(original)

    # Tamper every frozen file, not only a sample of the art/proof inputs.
    for path in sorted((repo / SOURCE).rglob('*')):
        if not path.is_file():
            continue
        relative = path.relative_to(repo).as_posix()
        label = 'frozen-' + path.relative_to(repo / SOURCE).as_posix().replace('/', '-')
        reason = ('source manifest freeze mismatch' if path.name == 'manifest.json' else
                  'source FILES.sha256 freeze mismatch' if path.name == 'FILES.sha256' else
                  'source file mismatch')
        corrupted(label, relative, reason)
    for base in IDS:
        name = f'enemy-newsh2-{base}-8.hda'
        entry = manifest['packs'][manifest['default_preview_pack']]['files'][name]
        corrupted(f'canonical-png-{base}', entry['source_png'], 'canonical PNG mismatch')
        for key in ['default_preview_pack', 'default_debug_pack']:
            corrupted(f'{key}-hda-{base}', f"assets/hd/packs/{manifest[key]}/{name}",
                      'packed HDR1 mismatch')
    for label, is_dir in [('unlisted-source', False), ('unlisted-empty-directory', True)]:
        path = fixture / SOURCE / label
        try:
            path.mkdir() if is_dir else path.write_bytes(b'unapproved raster input')
            rejected(label, out / ('bad-' + label), 'source inventory differs', wrapper)
        finally:
            path.rmdir() if is_dir else path.unlink()
    for label, relative in [('source-symlink', SOURCE + '/sources/generated-two-triplets.png'),
                            ('source-directory-symlink', SOURCE + '/sources')]:
        path = fixture / relative
        saved = path.with_name(path.name + '.saved')
        path.rename(saved)
        try:
            path.symlink_to(repo / relative, target_is_directory=saved.is_dir())
            rejected(label, out / ('bad-' + label), 'source symlink', wrapper)
        finally:
            path.unlink()
            saved.rename(path)
    # Restore every independent mutation before proceeding; no real file is written.
    manifest_path = fixture / 'assets/hd/manifest.json'
    raw_manifest = manifest_path.read_bytes()
    for label in ['widened4x', 'widened-other-pack', 'widened-quadrant', 'alias-header',
                  'family-anchor', 'family-FNV', 'source-index', 'source-index-alias', 'pack-count',
                  'scope-density', 'scope-quadrants', 'scope-bank', 'scope-links',
                  'pack-anchor', 'pack-density', 'pack-source']:
        changed = json.loads(raw_manifest)
        pack_name = changed['default_debug_pack']
        pack = changed['packs'][pack_name]
        entry = dict(pack['files']['enemy-newsh2-1-8.hda'])
        if label == 'widened4x':
            pack['files']['enemy-newsh2-1-4.hda'] = entry
            pack['count'] += 1
        elif label == 'widened-other-pack':
            other = add_nondefault_pack_fixture(changed)
            changed['packs'][other]['files']['enemy-newsh2-1-8.hda'] = entry
            changed['packs'][other]['count'] += 1
        elif label == 'widened-quadrant':
            pack['files']['enemy-newsh2-2-8.hda'] = entry
            pack['count'] += 1
        elif label == 'alias-header':
            pack['files']['late-spike-unapproved-alias.hda'] = entry
            pack['count'] += 1
        elif label == 'family-anchor':
            changed['late_spike_v1']['entries'][0]['anchor'] = [0, 0]
        elif label == 'family-FNV':
            changed['late_spike_v1']['entries'][0]['rgba_fnv1a64'] = '0000000000000000'
        elif label == 'source-index':
            changed['source_pngs'][entry['sha256']]['RGBA_sha256'] = '0' * 64
        elif label == 'source-index-alias':
            changed['source_pngs']['0' * 64] = dict(changed['source_pngs'][entry['sha256']])
        elif label.startswith('scope-'):
            field, value = {'scope-density': ('density', 4),
                            'scope-quadrants': ('runtime_components', [0]),
                            'scope-bank': ('bank_role', 102),
                            'scope-links': ('links', [7, 8, 9, 10, 11])}[label]
            changed['late_spike_v1'][field] = value
        elif label.startswith('pack-') and label != 'pack-count':
            row = pack['files']['enemy-newsh2-1-8.hda']
            if label == 'pack-anchor':
                row['header_u32'][4:6] = [0, 0]
            elif label == 'pack-density':
                row['header_u32'][1] = 4
            else:
                row['source_png'] = 'assets/hd/source/unapproved.png'
        else:
            pack['count'] += 1
        reason = ('entry/FNV binding mismatch' if label.startswith('family-') else
                  'source PNG index mismatch' if label == 'source-index' else
                  'widened source PNG index' if label == 'source-index-alias' else
                  'family metadata mismatch' if label.startswith('scope-') else
                  'packed metadata mismatch' if label in ['pack-anchor', 'pack-density', 'pack-source'] else
                  'pack count mismatch' if label == 'pack-count' else 'widened pack')
        try:
            manifest_path.write_text(json.dumps(changed))
            rejected(label, out / ('bad-' + label), reason, wrapper)
        finally:
            manifest_path.write_bytes(raw_manifest)
    defaults = [manifest['default_preview_pack'], manifest['default_debug_pack']]
    other = NONDEFAULT_PACK
    canonical = manifest['packs'][defaults[0]]['files']['enemy-newsh2-1-8.hda']['source_png']
    extras = [
        ('unindexed-disk4x', f'assets/hd/packs/{defaults[1]}/enemy-newsh2-1-4.hda', 'widened on-disk pack inventory'),
        ('unindexed-other-pack', f'assets/hd/packs/{other}/enemy-newsh2-1-8.hda', 'widened on-disk pack inventory'),
        ('unindexed-quadrant', f'assets/hd/packs/{defaults[1]}/enemy-newsh2-2-8.hda', 'widened on-disk pack inventory'),
        ('unindexed-alias', f'assets/hd/packs/{defaults[1]}/late-spike-unapproved-alias.hda', 'widened on-disk pack inventory'),
        ('unindexed-source-png', 'assets/hd/source/enemy-newsh2-1-4-unapproved.png', 'widened canonical PNG inventory'),
    ]
    for label, relative, reason in extras:
        extra = fixture / relative
        extra.parent.mkdir(parents=True, exist_ok=True)
        source = fixture / (canonical if relative.endswith('.png') else
                            f'assets/hd/packs/{defaults[1]}/enemy-newsh2-1-8.hda')
        try:
            shutil.copy2(source, extra)
            rejected(label, out / ('bad-' + label), reason, wrapper)
            require(not (out / ('bad-' + label)).exists(), 'failed widening validation wrote output')
        finally:
            extra.unlink()
    # Even a fresh external destination cannot be placed inside optional original inputs.
    original_dir = out / 'original-inputs'
    original_dir.mkdir()
    overlap = subprocess.run([sys.executable, str(wrapper), '--output', str(original_dir / 'new-output'),
                              '--original-data', str(original_dir)], capture_output=True, text=True, timeout=90)
    require(overlap.returncode != 0 and 'output must not overlap original data' in overlap.stderr,
            'original input/output overlap was not rejected')
    require(not (original_dir / 'new-output').exists(), 'original input directory was written')
    checks.append({'case': 'original-output-overlap', 'reason': 'output must not overlap original data',
                   'returncode': overlap.returncode})
    # Prove the immutable recipe needs neither canonical outputs nor original data.
    generated_only = out / 'generated-only-source'
    for relative in ['rebuild.py', 'expected-hashes.json', 'sources/generated-two-triplets.png',
                     'masks/alpha-triplet-a-logical.png', 'masks/alpha-triplet-b-logical.png',
                     'sources/prompt.txt']:
        path = generated_only / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(repo / SOURCE / relative, path)
    result = run(generated_only / 'rebuild.py', out / 'generated-only-result')
    require(result.returncode == 0, 'generated-only recipe failed: ' + result.stdout + result.stderr)
    for path in (out / 'valid').iterdir():
        require(path.read_bytes() == (out / 'generated-only-result' / path.name).read_bytes(),
                'generated-only reproduction differs: ' + path.name)
    require(before == {name: digest(repo / name) for name in files}, 'original repository input changed')
    require(before == {name: digest(fixture / name) for name in files}, 'fixture restoration failed')
    receipt = {'status': 'PASS', 'valid_source_validation': True,
               'generated_only_reproduction_without_canonical_outputs': True,
               'rejected_cases': checks, 'rejected_count': len(checks),
               'independent_copies_only': True, 'real_inputs_unchanged': True,
               'original_RGB_inputs': False, 'game_runs': 0}
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError, subprocess.SubprocessError) as exc:
        print('ERROR: ' + str(exc), file=sys.stderr)
        sys.exit(1)
