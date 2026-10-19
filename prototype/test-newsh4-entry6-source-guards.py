#!/usr/bin/env python3
"""Exercise entry-craft source/build rejection using independent fixture copies.

Every mutation is confined to fresh external copies, with no hardlinks. Real
artwork, canonical files, packs and optional originals are fingerprinted and never
written. Frozen manifest/checksum closure is the import proof; no extra stamp is
added to that immutable package. No game or capture is run.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import struct
import subprocess
import sys

from nondefault_pack_fixture import NONDEFAULT_PACK, add_nondefault_pack_fixture

SOURCE = 'assets/hd/artwork/newsh4-entry6-v1'
SCRIPT = 'prototype/build-newsh4-entry6-art.py'
IDS = [81, 83, 85, 119, 121, 123]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--original-data', type=Path)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    given = args.out.expanduser()
    require(given.is_absolute(), 'absolute external output required')
    require('..' not in given.parts, 'output traversal forbidden')
    require(not any(path.is_symlink() for path in [given, *given.parents]), 'output symlinks forbidden')
    out = given.resolve()
    require(not out.exists() and out.parent.is_dir(), 'fresh output with existing parent required')
    require(out != repo and out not in repo.parents and repo not in out.parents, 'external output required')
    if args.original_data:
        original_root = args.original_data.expanduser().resolve()
        require(out != original_root and original_root not in out.parents and out not in original_root.parents,
                'output must not overlap original data')
    out.mkdir()
    checks = []
    script = repo / SCRIPT

    def run(wrapper, target, original=None):
        cmd = [sys.executable, str(wrapper), '--output', str(target)]
        if original is not None:
            cmd += ['--original-data', str(original)]
        return subprocess.run(cmd, capture_output=True, text=True, timeout=90)

    def rejected(label, target, reason, wrapper=script, original=None):
        existed = target.exists() or target.is_symlink()
        result = run(wrapper, target, original)
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
        ('repository-child', repo / 'entry6-forbidden-output', 'output must be outside repository'),
        ('relative', Path('entry6-forbidden-output'), 'output must be absolute'),
        ('traversal', out / '..' / 'entry6-forbidden-output', 'output traversal forbidden'),
        ('missing-parent', out / 'missing' / 'output', 'output parent must exist'),
    ]:
        rejected(label, target, reason)
    require(not (repo / 'entry6-forbidden-output').exists(), 'forbidden output created')
    link = out / 'link'
    link.symlink_to(out, target_is_directory=True)
    rejected('symlink-parent', link / 'absent', 'symlink path forbidden')
    direct = out / 'direct'
    direct.symlink_to(out / 'absent', target_is_directory=True)
    rejected('symlink-output', direct, 'symlink path forbidden')
    require(not (out / 'absent').exists(), 'symlink output created')
    manifest = json.loads((repo / 'assets/hd/manifest.json').read_text())
    fixture = out / 'fixture'
    files = {SCRIPT, 'assets/hd/manifest.json', 'src/episodes.c'}
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

    def corrupted(label, relative, reason, mutate=lambda original: original + b'\0'):
        path = fixture / relative
        original = path.read_bytes()
        try:
            path.write_bytes(mutate(original))
            rejected(label, out / ('bad-' + label), reason, wrapper)
        finally:
            path.write_bytes(original)

    def missing(label, relative, reason):
        path = fixture / relative
        original = path.read_bytes()
        try:
            path.unlink()
            rejected(label, out / ('bad-' + label), reason, wrapper)
        finally:
            path.write_bytes(original)

    # Both altered and absent forms of every frozen member, including manifest,
    # checksum closure, both prompts, provenance, recipe, masks and proof records.
    for path in sorted((repo / SOURCE).rglob('*')):
        if not path.is_file():
            continue
        relative = path.relative_to(repo).as_posix()
        label = path.relative_to(repo / SOURCE).as_posix().replace('/', '-')
        reason = ('source manifest freeze mismatch' if path.name == 'manifest.json' else
                  'source FILES.sha256 freeze mismatch' if path.name == 'FILES.sha256' else
                  'source file mismatch')
        corrupted('frozen-' + label, relative, reason)
        missing('missing-frozen-' + label, relative,
                'manifest.json' if path.name == 'manifest.json' else 'source inventory differs')
    for base in IDS:
        name = f'enemy-newsh4-{base}-8.hda'
        entry = manifest['packs'][manifest['default_preview_pack']]['files'][name]
        corrupted(f'canonical-png-{base}', entry['source_png'], 'canonical PNG mismatch')
        missing(f'missing-canonical-png-{base}', entry['source_png'], Path(entry['source_png']).name)
        for key in ['default_preview_pack', 'default_debug_pack']:
            relative = f"assets/hd/packs/{manifest[key]}/{name}"
            corrupted(f'{key}-hda-{base}', relative, 'packed HDR1 mismatch')
            missing(f'missing-{key}-hda-{base}', relative, name)
        relative = SOURCE + '/output/' + name
        raw = (fixture / relative).read_bytes()
        opaque = next(i for i in range(28, len(raw), 4) if raw[i + 3] == 255)
        transparent = next(i for i in range(28, len(raw), 4) if raw[i + 3] == 0)
        mutations = {
            'magic': lambda b: b'BAD!' + b[4:],
            'truncated': lambda b: b[:-1],
            'opaque-RGB': lambda b, i=opaque: b[:i] + bytes([b[i] ^ 1]) + b[i + 1:],
            'transparent-RGB': lambda b, i=transparent: b[:i] + b'\x01' + b[i + 1:],
            'partial-alpha': lambda b, i=opaque + 3: b[:i] + b'\x80' + b[i + 1:],
            'grown-alpha': lambda b, i=transparent + 3: b[:i] + b'\xff' + b[i + 1:],
        }
        for field in range(6):
            mutations[f'header-{field}'] = (lambda b, i=4 + 4 * field:
                b[:i] + struct.pack('<I', struct.unpack_from('<I', b, i)[0] + 1) + b[i + 4:])
        for name, mutate in mutations.items():
            corrupted(f'frozen-hda-{base}-{name}', relative, 'source file mismatch', mutate)
    for label, is_dir in [('unlisted-source', False), ('unlisted-empty-directory', True)]:
        path = fixture / SOURCE / label
        try:
            path.mkdir() if is_dir else path.write_bytes(b'unapproved raster input')
            rejected(label, out / ('bad-' + label), 'source inventory differs', wrapper)
        finally:
            path.rmdir() if is_dir else path.unlink()
    defaults = [manifest['default_preview_pack'], manifest['default_debug_pack']]
    canonical = manifest['packs'][defaults[0]]['files']['enemy-newsh4-81-8.hda']['source_png']
    for label, relative, reason in [
        ('source-symlink', SOURCE + '/sources/generated-whole-selected-v2.png', 'source symlink'),
        ('source-directory-symlink', SOURCE + '/sources', 'source symlink'),
        ('source-root-symlink', SOURCE, 'symlink path forbidden'),
        ('canonical-symlink', canonical, 'symlink path forbidden'),
        ('canonical-parent-symlink', 'assets/hd/source', 'symlink path forbidden'),
        ('pack-symlink', f'assets/hd/packs/{defaults[0]}/enemy-newsh4-81-8.hda', 'symlink path forbidden'),
        ('pack-parent-symlink', f'assets/hd/packs/{defaults[0]}', 'symlink path forbidden'),
        ('manifest-symlink', 'assets/hd/manifest.json', 'symlink path forbidden'),
    ]:
        path = fixture / relative
        saved = out / (label + '-saved')
        path.rename(saved)
        try:
            path.symlink_to(saved, target_is_directory=saved.is_dir())
            rejected(label, out / ('bad-' + label), reason, wrapper)
        finally:
            path.unlink()
            saved.rename(path)
    # The fixture contains the complete manifest but only this family's resources.
    # Unrelated entries are intentionally read only as finite namespace declarations.
    manifest_path = fixture / 'assets/hd/manifest.json'
    raw_manifest = manifest_path.read_bytes()
    cases = ['widened4x', 'widened-other-pack', 'widened-quadrant', 'widened-boss86',
             'widened-boss124', 'alias-header', 'family-anchor', 'family-FNV', 'family-slot',
             'family-missing-entry', 'family-extra-entry', 'source-index', 'source-index-alias',
             'source-index-renamed-alias', 'pack-count', 'scope-density', 'scope-quadrants',
             'scope-bank', 'scope-order', 'scope-stride', 'scope-scoreitem', 'scope-armor',
             'scope-extra-field', 'scope-boss', 'pack-anchor', 'pack-density', 'pack-source',
             'unsafe-pack-name', 'unsafe-pack-file', 'unsafe-source-path', 'unsafe-source-index']
    for label in cases:
        changed = json.loads(raw_manifest)
        pack_name = changed['default_debug_pack']
        pack = changed['packs'][pack_name]
        entry = dict(pack['files']['enemy-newsh4-81-8.hda'])
        family = changed['newsh4_entry6_v1']
        if label.startswith('widened') or label == 'alias-header':
            if label == 'widened-other-pack':
                other = add_nondefault_pack_fixture(changed)
                pack = changed['packs'][other]
            filename = {'widened4x': 'enemy-newsh4-81-4.hda',
                        'widened-quadrant': 'enemy-newsh4-82-8.hda',
                        'widened-boss86': 'enemy-newsh4-86-8.hda',
                        'widened-boss124': 'enemy-newsh4-124-8.hda',
                        'alias-header': 'entry6-unapproved-alias.hda'}.get(label, 'enemy-newsh4-81-8.hda')
            pack['files'][filename] = entry
            pack['count'] += 1
        elif label.startswith('family-'):
            if label == 'family-anchor':
                family['entries'][0]['anchor'] = [0, 0]
            elif label == 'family-FNV':
                family['entries'][0]['rgba_fnv1a64'] = '0' * 16
            elif label == 'family-slot':
                family['entries'][0]['slot'] = 404
            elif label == 'family-missing-entry':
                family['entries'].pop()
            else:
                family['entries'].append(dict(family['entries'][0]))
        elif label == 'source-index':
            changed['source_pngs'][entry['sha256']]['RGBA_sha256'] = '0' * 64
        elif label in ['source-index-alias', 'source-index-renamed-alias']:
            alias = dict(changed['source_pngs'][entry['sha256']])
            if label == 'source-index-renamed-alias':
                alias['path'] = 'assets/hd/source/unapproved-alias.png'
            changed['source_pngs']['0' * 64] = alias
        elif label.startswith('scope-'):
            field, value = {
                'scope-density': ('density', 4), 'scope-quadrants': ('runtime_components', [0]),
                'scope-bank': ('bank_role', 101), 'scope-order': ('source_order_placements', list(reversed(family['source_order_placements']))),
                'scope-stride': ('vertical_stride', 28), 'scope-scoreitem': ('preserve_recycled_scoreitem', False),
                'scope-armor': ('source_armor', 50), 'scope-extra-field': ('terrain_route', True),
                'scope-boss': ('excluded_boss_bases', []),
            }[label]
            family[field] = value
        elif label in ['pack-anchor', 'pack-density', 'pack-source']:
            row = pack['files']['enemy-newsh4-81-8.hda']
            if label == 'pack-anchor':
                row['header_u32'][4:6] = [0, 0]
            elif label == 'pack-density':
                row['header_u32'][1] = 4
            else:
                row['source_png'] = 'assets/hd/source/unapproved.png'
        elif label.startswith('unsafe-'):
            if label == 'unsafe-pack-name':
                changed['packs']['../outside'] = {'files': {}, 'count': 0}
            elif label == 'unsafe-pack-file':
                pack['files']['../outside.hda'] = entry
                pack['count'] += 1
            elif label == 'unsafe-source-path':
                pack['files']['enemy-newsh4-81-8.hda']['source_png'] = '../outside.png'
            else:
                changed['source_pngs']['0' * 64] = {'path': '/tmp/outside.png', 'sha256': '0' * 64,
                                                  'RGBA_sha256': '0' * 64}
        else:
            pack['count'] += 1
        reason = ('exact six entries required' if label in ['family-missing-entry', 'family-extra-entry'] else
                  'entry/FNV binding mismatch' if label.startswith('family-') else
                  'source PNG index mismatch' if label == 'source-index' else
                  'widened source PNG index' if label.startswith('source-index-') else
                  'family metadata mismatch' if label.startswith('scope-') else
                  'packed metadata mismatch' if label in ['pack-anchor', 'pack-density', 'pack-source'] else
                  'unsafe manifest path' if label.startswith('unsafe-') else
                  'pack count mismatch' if label == 'pack-count' else 'widened pack')
        try:
            manifest_path.write_text(json.dumps(changed))
            rejected(label, out / ('bad-' + label), reason, wrapper)
        finally:
            manifest_path.write_bytes(raw_manifest)
    other = NONDEFAULT_PACK
    extras = [
        ('unindexed-disk4x', f'assets/hd/packs/{defaults[1]}/enemy-newsh4-81-4.hda', 'widened on-disk pack inventory'),
        ('unindexed-other-pack', f'assets/hd/packs/{other}/enemy-newsh4-81-8.hda', 'widened on-disk pack inventory'),
        ('unindexed-quadrant', f'assets/hd/packs/{defaults[1]}/enemy-newsh4-82-8.hda', 'widened on-disk pack inventory'),
        ('unindexed-boss86', f'assets/hd/packs/{defaults[1]}/enemy-newsh4-86-8.hda', 'widened on-disk pack inventory'),
        ('unindexed-boss124', f'assets/hd/packs/{defaults[1]}/enemy-newsh4-124-8.hda', 'widened on-disk pack inventory'),
        ('unindexed-alias', f'assets/hd/packs/{defaults[1]}/entry6-unapproved-alias.hda', 'widened on-disk pack inventory'),
        ('unindexed-alias-extension', f'assets/hd/packs/{defaults[1]}/entry6-unapproved-alias.bin', 'widened on-disk pack inventory'),
        ('unindexed-source-png', 'assets/hd/source/enemy-newsh4-81-4-unapproved.png', 'widened canonical PNG inventory'),
        ('unindexed-boss-source-png', 'assets/hd/source/enemy-newsh4-86-8-unapproved.png', 'widened canonical PNG inventory'),
    ]
    for label, relative, reason in extras:
        extra = fixture / relative
        extra.parent.mkdir(parents=True, exist_ok=True)
        source = fixture / (canonical if relative.endswith('.png') else
                            f'assets/hd/packs/{defaults[1]}/enemy-newsh4-81-8.hda')
        try:
            shutil.copy2(source, extra)
            require(not source.samefile(extra), 'extra fixture hardlink forbidden')
            rejected(label, out / ('bad-' + label), reason, wrapper)
        finally:
            extra.unlink()
    original_dir = out / 'original-inputs'
    original_dir.mkdir()
    rejected('original-output-overlap', original_dir / 'new-output',
             'output must not overlap original data', wrapper, original_dir)
    # Prove the immutable recipe needs neither outputs, proof records, nor original
    # game RGB/indices. It reads exactly the frozen generated-only input inventory.
    generated_only = out / 'generated-only-source'
    expected = json.loads((repo / SOURCE / 'expected-hashes.json').read_text())
    for relative in ['rebuild.py', 'expected-hashes.json', *expected['inputs']]:
        path = generated_only / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(repo / SOURCE / relative, path)
    result = run(generated_only / 'rebuild.py', out / 'generated-only-result')
    require(result.returncode == 0, 'generated-only recipe failed: ' + result.stdout + result.stderr)
    require({path.name for path in (out / 'valid').iterdir()}
            == {path.name for path in (out / 'generated-only-result').iterdir()}, 'generated-only output inventory')
    for path in (out / 'valid').iterdir():
        require(path.read_bytes() == (out / 'generated-only-result' / path.name).read_bytes(),
                'generated-only reproduction differs: ' + path.name)
    optional_originals = False
    if args.original_data:
        original_names = ['newsh4.shp', 'tyrian.hdt', 'tyrian1.lvl']
        original_before = {name: digest(original_root / name) for name in original_names}
        for name in original_names:
            shutil.copy2(original_root / name, original_dir / name)
            require(not (original_root / name).samefile(original_dir / name), 'original fixture hardlink forbidden')
        result = run(wrapper, out / 'valid-original', original_dir)
        require(result.returncode == 0, 'valid original fixture failed: ' + result.stdout + result.stderr)
        (out / 'valid-original.stdout.txt').write_text(result.stdout)
        for name in original_names:
            path = original_dir / name
            raw = path.read_bytes()
            try:
                path.write_bytes(raw[:-1] + bytes([raw[-1] ^ 1]))
                rejected('tampered-original-' + name, out / ('bad-original-' + name),
                         'original-data identity mismatch', wrapper, original_dir)
            finally:
                path.write_bytes(raw)
            saved = out / (name + '.saved')
            path.rename(saved)
            try:
                path.symlink_to(saved)
                rejected('symlink-original-' + name, out / ('bad-original-symlink-' + name),
                         'symlink path forbidden', wrapper, original_dir)
            finally:
                path.unlink()
                saved.rename(path)
        require(original_before == {name: digest(original_root / name) for name in original_names},
                'original game input changed')
        require(original_before == {name: digest(original_dir / name) for name in original_names},
                'original fixture restoration failed')
        optional_originals = True
    require(before == {name: digest(repo / name) for name in files}, 'original repository input changed')
    require(before == {name: digest(fixture / name) for name in files}, 'fixture restoration failed')
    receipt = {'status': 'PASS', 'valid_source_validation': True,
               'generated_only_reproduction_without_canonical_outputs': True,
               'closed_frozen_import_inventory': True, 'optional_original_validation': optional_originals,
               'rejected_cases': checks, 'rejected_count': len(checks),
               'independent_copies_only': True, 'real_inputs_unchanged': True,
               'original_RGB_art_inputs': False, 'game_runs': 0}
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError, subprocess.SubprocessError) as exc:
        print('ERROR: ' + str(exc), file=sys.stderr)
        sys.exit(1)
