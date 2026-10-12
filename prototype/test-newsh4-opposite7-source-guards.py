#!/usr/bin/env python3
"""Exercise opposite7 source/build rejection using independent fixture copies.

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

SOURCE = 'assets/hd/artwork/newsh4-opposite7-v1'
SCRIPT = 'prototype/build-newsh4-opposite7-art.py'
IDS = [231, 233, 235, 267, 269, 271, 273]


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
        result = run(wrapper, target)
        require(result.returncode != 0 and 'ERROR:' in result.stderr and reason in result.stderr,
                f'{label}: expected controlled rejection {reason!r}; got {result.returncode}\n{result.stdout}\n{result.stderr}')
        checks.append({'case': label, 'reason': reason, 'returncode': result.returncode})
        return result

    for label, target, reason in [
        ('existing', out, 'output must be fresh'),
        ('repository', repo, 'output must be fresh'),
        ('repository-parent', repo.parent, 'output must be fresh'),
        ('repository-child', repo / 'newsh4-opposite7-forbidden-output', 'output must be outside repository'),
        ('relative', Path('newsh4-opposite7-forbidden-output'), 'output must be absolute'),
        ('missing-parent', out / 'missing' / 'output', 'output parent must exist'),
    ]:
        rejected(label, target, reason)
    require(not (repo / 'newsh4-opposite7-forbidden-output').exists(), 'forbidden output created')
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
        name = f'enemy-newsh4-{base}-8.hda'
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

    for label, relative, reason in [
        ('master', SOURCE + '/sources/generated-whole.png', 'source file mismatch'),
        ('prompt', SOURCE + '/sources/prompt.txt', 'source file mismatch'),
        ('mask', SOURCE + '/masks/alpha-assembly-logical.png', 'source file mismatch'),
        ('contract', SOURCE + '/contract.json', 'source file mismatch'),
        ('expected-hashes', SOURCE + '/expected-hashes.json', 'source file mismatch'),
        ('recipe', SOURCE + '/rebuild.py', 'source file mismatch'),
        ('source-manifest', SOURCE + '/manifest.json', 'source manifest freeze mismatch'),
        ('source-checksums', SOURCE + '/FILES.sha256', 'source FILES.sha256 freeze mismatch'),
        ('source-proof', SOURCE + '/proof/source-composites.json', 'source file mismatch'),
        ('source-audit', SOURCE + '/proof/source-audit.json', 'source file mismatch'),
        ('frozen-png', SOURCE + '/output/enemy-newsh4-231-8.png', 'source file mismatch'),
        ('frozen-hda', SOURCE + '/output/enemy-newsh4-233-8.hda', 'source file mismatch'),
        ('canonical-png', manifest['packs'][manifest['default_preview_pack']]['files']
         ['enemy-newsh4-231-8.hda']['source_png'], 'canonical PNG mismatch'),
        ('packed-hda', f"assets/hd/packs/{manifest['default_preview_pack']}/enemy-newsh4-233-8.hda",
         'packed HDR1 mismatch'),
    ]:
        corrupted(label, relative, reason)
    for label, is_dir in [('unlisted-source', False), ('unlisted-empty-directory', True)]:
        path = fixture / SOURCE / label
        try:
            path.mkdir() if is_dir else path.write_bytes(b'unapproved raster input')
            rejected(label, out / ('bad-' + label), 'source inventory differs', wrapper)
        finally:
            path.rmdir() if is_dir else path.unlink()
    for label, relative in [('source-symlink', SOURCE + '/sources/generated-whole.png'),
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
                  'family-anchor', 'family-FNV', 'source-index', 'pack-count']:
        changed = json.loads(raw_manifest)
        pack_name = changed['default_debug_pack']
        pack = changed['packs'][pack_name]
        entry = dict(pack['files']['enemy-newsh4-231-8.hda'])
        if label == 'widened4x':
            pack['files']['enemy-newsh4-231-4.hda'] = entry
            pack['count'] += 1
        elif label == 'widened-other-pack':
            other = next(name for name in changed['packs'] if name not in
                         [changed['default_preview_pack'], changed['default_debug_pack']])
            changed['packs'][other]['files']['enemy-newsh4-231-8.hda'] = entry
            changed['packs'][other]['count'] += 1
        elif label == 'widened-quadrant':
            pack['files']['enemy-newsh4-232-8.hda'] = entry
            pack['count'] += 1
        elif label == 'alias-header':
            pack['files']['opposite-unapproved-alias.hda'] = entry
            pack['count'] += 1
        elif label == 'family-anchor':
            changed['newsh4_opposite7_v1']['entries'][0]['anchor'] = [0, 0]
        elif label == 'family-FNV':
            changed['newsh4_opposite7_v1']['entries'][0]['rgba_fnv1a64'] = '0000000000000000'
        elif label == 'source-index':
            changed['source_pngs'][entry['sha256']]['RGBA_sha256'] = '0' * 64
        else:
            pack['count'] += 1
        reason = ('entry/FNV binding mismatch' if label.startswith('family-') else
                  'source PNG index mismatch' if label == 'source-index' else
                  'pack count mismatch' if label == 'pack-count' else 'widened pack')
        try:
            manifest_path.write_text(json.dumps(changed))
            rejected(label, out / ('bad-' + label), reason, wrapper)
        finally:
            manifest_path.write_bytes(raw_manifest)
    extra = fixture / f"assets/hd/packs/{manifest['default_debug_pack']}/enemy-newsh4-231-4.hda"
    try:
        shutil.copy2(extra.with_name('enemy-newsh4-231-8.hda'), extra)
        rejected('unindexed-disk4x', out / 'bad-unindexed-disk4x', 'widened on-disk pack inventory', wrapper)
    finally:
        extra.unlink()
    # Prove the immutable recipe needs neither canonical outputs nor original data.
    generated_only = out / 'generated-only-source'
    for relative in ['rebuild.py', 'expected-hashes.json', 'sources/generated-whole.png',
                     'masks/alpha-assembly-logical.png']:
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
