#!/usr/bin/env python3
"""Rebuild one retired HDR1 checkpoint in a new external directory from pinned PNGs.

Never reads or reinstalls retired runtime directories. Current installed packs
are verified by build-hd-assets.py; original recipes stay in manifest.retired_packs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import struct

from PIL import Image


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_relative(value: str) -> str:
    path = PurePosixPath(value)
    if not value or path.is_absolute() or '\\' in value or '..' in path.parts or str(path) != value:
        raise ValueError(f'Unsafe repository path: {value!r}')
    return value


def build_pack(repo: Path, pack_name: str, output: Path) -> dict:
    """Validate all recipes before creating a new, external output directory."""
    repo = repo.resolve()
    safe_relative(pack_name)
    if len(PurePosixPath(pack_name).parts) != 1:
        raise ValueError('Choose a retired pack name, not a path')
    manifest = json.loads((repo / 'assets/hd/manifest.json').read_text(encoding='utf-8'))
    if pack_name in manifest['packs'] or pack_name not in manifest.get('retired_packs', {}):
        raise ValueError('Unknown retired pack; choose a key from manifest.retired_packs')
    pack = manifest['retired_packs'][pack_name]
    if not pack['files'] or len(pack['files']) != pack['count']:
        raise ValueError('Invalid retired pack inventory')
    output = output.absolute()
    if output.exists() or output.is_symlink():
        raise ValueError('Choose a new output directory; existing files are never overwritten')
    if not output.parent.is_dir() or output.parent.resolve() != output.parent:
        raise ValueError('Output parent must be an existing directory without symlinks')
    if output == repo or repo in output.parents:
        raise ValueError('Output must be outside the repository')
    payloads = {}
    total = 0
    for name, item in pack['files'].items():
        safe_relative(name)
        if len(PurePosixPath(name).parts) != 1 or not name.endswith('.hda'):
            raise ValueError('Invalid retired resource filename')
        rel = safe_relative(item['source_png'])
        source = repo / rel
        if source.resolve() != source or not source.is_file():
            raise ValueError(f'Pinned source must be a regular, unlinked file: {rel}')
        if source.stat().st_size > 64 * 1024 * 1024:
            raise ValueError('Pinned PNG exceeds the 64 MiB source limit')
        encoded = source.read_bytes()
        if digest(encoded) != item['source_png_sha256']:
            raise ValueError(f'Pinned source fingerprint mismatch: {rel}')
        header = item['header_u32']
        if len(header) != 6 or any(not isinstance(v, int) or not 0 <= v <= 0xffffffff for v in header):
            raise ValueError('Invalid HDR1 header recipe')
        width, height = header[1] * header[2], header[1] * header[3]
        if not 0 < width * height <= 16 * 1024 * 1024:
            raise ValueError('Invalid or oversized HDR1 dimensions')
        with Image.open(source) as image:
            if image.mode != 'RGBA' or image.size != (width, height):
                raise ValueError(f'Pinned source dimensions or mode mismatch: {rel}')
            raw = b'HDR1' + struct.pack('<6I', *header) + image.tobytes()
        if digest(raw) != item['sha256']:
            raise ValueError(f'Reconstructed resource fingerprint mismatch: {name}')
        payloads[name] = raw
        total += len(raw)
        if total > 64 * 1024 * 1024:
            raise ValueError('Retired checkpoint exceeds the 64 MiB rebuild limit')
    output.mkdir()
    for name, raw in payloads.items():
        with (output / name).open('xb') as stream:
            stream.write(raw)
    return {'pack': pack_name, 'files': len(payloads), 'bytes': total,
            'output': str(output), 'source_unchanged': True, 'all_hashes_exact': True}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pack', help='A key in assets/hd/manifest.json retired_packs')
    parser.add_argument('--output', required=True, type=Path, help='New directory outside the repository')
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    try:
        receipt = build_pack(args.repo, args.pack, args.output)
    except (OSError, ValueError, KeyError, AssertionError) as error:
        parser.exit(2, f'{error}\n')
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
