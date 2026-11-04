#!/usr/bin/env python3
"""Reproduce the frozen private terrain23 HDA set from caller-owned game data.

This producer's authoring input bundle contains no original game data, source
images, palette values or copied native masks. The candidate runtime loader
separately retains its existing 1,008-byte original-derived cliff mask table
unchanged; see docs/terrain23/AUTHORING.md for the explicit scope disclosure.
This tool has no network/download fallback and never runs the game or compiler.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import struct
import stat
import sys

SOURCE_ROOT = Path(__file__).resolve().parents[1]
ART_ROOT = SOURCE_ROOT / "assets/hd/artwork/shapesz-terrain23-v1"
VERSIONS = {"Python": "3.12.14", "Pillow": "13.0.0", "numpy": "2.3.5", "scipy": "1.17.0"}
SHAPES_SHA = "3ecc9b59c82e8e7d9c91889aac7d337ca28a59519c4970e256250e4603a9b248"
PALETTE_SHA = "f628396306805387f07f72c4ccf0fdee9ca84b8e70ae23ba4ec58ec5fb362da0"
LIVE_PALETTE_SHA = "d4c24a49efb588abd6dc1ffd0f0d1279a498c422cdd26fba4fc921b07f8c159f"
GROUPS = (
    ("ground10", (372, 380, 390, 367, 368, 376, 378, 386, 387, 388), 5, 2,
     "raw-family-v2.png", "14c51a8b55e21846de4afabcb06c8ea61559b7148cddca1ce1d7f7b38bd389fe"),
    ("cliff12", (361, 362, 363, 364, 365, 371, 373, 374, 375, 381, 382, 383), 6, 2,
     "raw-cliff-v1.png", "b39c7f2883eb50b137a82325f0c3aed2362c1986af1e8c09a9c41da49d9b9c6b"),
    ("corner366", (366,), 1, 1,
     "raw-v1.png", "a7246580459c9fc6d0e06ba65b33e67da4a8ff554fb53b30a756bfc9f7fa4680"),
)
IDS = tuple(sorted(i for _, ids, *_ in GROUPS for i in ids))
RAW_BYTES = {"ground10": 1454285, "cliff12": 1874115, "corner366": 1436523}
MAX_INPUT_BYTES = 4 * 1024 * 1024
MAX_METADATA_BYTES = 64 * 1024


class AuthoringError(Exception):
    """Expected, non-destructive authoring validation failure."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_regular(path: Path, *, size: int | None = None,
                 max_size: int = MAX_INPUT_BYTES) -> bytes:
    """Bound reads before opening; reject symlinks, FIFO, devices and directories.

    A nonblocking/no-follow open plus fstat prevents a regular-file-to-FIFO
    substitution from hanging between lstat and open on platforms supporting
    those flags. All content reads remain bounded even if the file grows.
    """
    absolute = path if path.is_absolute() else Path.cwd() / path
    current = Path(absolute.anchor)
    fd = None
    try:
        # Check each original path component without resolve() hiding symlinks.
        for part in absolute.parts[1:]:
            current = current / part
            info = current.lstat()
            if stat.S_ISLNK(info.st_mode):
                raise AuthoringError(f"Input symlink is not permitted: {current}")
        info = absolute.lstat()
        if not stat.S_ISREG(info.st_mode):
            raise AuthoringError(f"Regular file required for input: {path}")
        limit = size if size is not None else max_size
        if limit < 0 or limit > MAX_INPUT_BYTES:
            raise AuthoringError("Invalid bounded input size")
        if size is not None and info.st_size != size:
            raise AuthoringError(f"Input size mismatch for {path.name}: expected {size}, got {info.st_size}")
        if info.st_size > limit:
            raise AuthoringError(f"Input exceeds maximum read size for {path.name}: {limit}")
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
        fd = os.open(absolute, flags)
        opened = os.fstat(fd)
        if (not stat.S_ISREG(opened.st_mode)
                or (opened.st_dev, opened.st_ino) != (info.st_dev, info.st_ino)):
            raise AuthoringError(f"Input changed or is not a regular file: {path}")
        if opened.st_size > limit or (size is not None and opened.st_size != size):
            raise AuthoringError(f"Input size changed while opening: {path}")
        with os.fdopen(fd, "rb") as stream:
            fd = None
            data = stream.read(limit + 1)
    except OSError as exc:
        raise AuthoringError(f"Cannot read required input {path}: {exc.strerror or exc}") from exc
    finally:
        if fd is not None:
            os.close(fd)
    if len(data) > limit or (size is not None and len(data) != size):
        raise AuthoringError(f"Input changed size during bounded read: {path}")
    return data


def read_checked(path: Path, expected: str, *, size: int | None = None) -> bytes:
    data = read_regular(path, size=size)
    if sha256(data) != expected:
        raise AuthoringError(f"SHA256 mismatch for {path.name}; supply the matching legal original data/frozen raw")
    return data


def require_dependencies():
    try:
        import PIL
        from PIL import Image
        import numpy as np
        import scipy
        from scipy.ndimage import distance_transform_edt
    except ImportError as exc:
        raise AuthoringError("Missing authoring dependency; see requirements-terrain23-authoring.txt. No install attempted.") from exc
    actual = {"Python": platform.python_version(), "Pillow": PIL.__version__,
              "numpy": np.__version__, "scipy": scipy.__version__}
    if actual != VERSIONS:
        raise AuthoringError(f"Replay environment mismatch: required {VERSIONS}; found {actual}")
    return Image, np, distance_transform_edt


def validate_paths(shapesz: Path, palette: Path, output: Path) -> Path:
    # lexists-like rejection also catches a dangling symlink. resolve() handles
    # existing symlink ancestors before testing overlap with the source tree.
    if output.exists() or output.is_symlink():
        raise AuthoringError(f"Output already exists; refusing to overwrite: {output}")
    resolved = output.resolve()
    if resolved == SOURCE_ROOT or SOURCE_ROOT in resolved.parents:
        raise AuthoringError("Output must be outside the source/artwork tree")
    if not resolved.parent.is_dir():
        raise AuthoringError("Output parent must already exist; choose a new independent child directory")
    for path in (shapesz, palette):
        input_path = path.resolve()
        if input_path == resolved or resolved in input_path.parents:
            raise AuthoringError("Output overlaps a required input path")
    return resolved


def decode_shapes(data: bytes) -> dict[int, bytes]:
    tiles = {}
    pos = 0
    for tile_id in range(1, 601):
        if pos >= len(data):
            raise AuthoringError("Truncated shapesz record flag")
        blank = data[pos]
        pos += 1
        if blank:
            tile = bytes(672)
        else:
            if pos + 672 > len(data):
                raise AuthoringError("Truncated shapesz tile payload")
            tile = data[pos:pos + 672]
            pos += 672
        if tile_id in IDS:
            tiles[tile_id] = tile
    # The exact supported original file has 520 trailing bytes after600 records.
    if pos != 318456 or len(data) - pos != 520:
        raise AuthoringError("Unexpected shapesz record layout")
    return tiles


def load_pins() -> dict[int, dict]:
    try:
        manifest = json.loads(read_regular(ART_ROOT / "OUTPUT-PINS.json", max_size=MAX_METADATA_BYTES).decode("utf-8"))
        rows = manifest["assets"]
        pins = {row["id"]: row for row in rows}
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise AuthoringError("Missing or malformed OUTPUT-PINS.json") from exc
    if len(rows) != 23 or tuple(sorted(pins)) != IDS:
        raise AuthoringError("Output pins must describe exactly the stable23 IDs")
    if manifest.get("versions") != VERSIONS:
        raise AuthoringError("Output pins dependency versions differ from the frozen contract")
    return pins


def compute_assets(shapes_data: bytes, palette_data: bytes) -> tuple[dict[str, bytes], dict]:
    Image, np, distance_transform_edt = require_dependencies()
    tiles = decode_shapes(shapes_data)
    pins = load_pins()
    bank = np.frombuffer(palette_data, np.uint8).reshape(24, 256, 3)[5].astype(np.uint16)
    if np.any(bank > 63):
        raise AuthoringError("Original palette bank5 has a channel outside VGA6-bit range")
    pal = ((bank << 2) | (bank >> 4)).astype(np.uint8)
    if sha256(pal.tobytes()) != LIVE_PALETTE_SHA:
        raise AuthoringError("Locally derived palette bank5 does not match the frozen palette hash")
    yy, xx = np.indices((224, 192))
    edge = np.minimum.reduce([xx, 191 - xx, yy, 223 - yy])
    rectedge = edge + 1
    outputs = {}
    report_rows = []
    lock_total = 0
    for family, ids, nx, ny, raw_name, raw_sha in GROUPS:
        raw_bytes = read_checked(ART_ROOT / family / raw_name, raw_sha, size=RAW_BYTES[family])
        mode = "RGB" if family == "ground10" else "RGBA"
        with Image.open(io.BytesIO(raw_bytes)) as source_image:
            raw = source_image.convert(mode)
        for j, tile_id in enumerate(ids):
            pin = pins[tile_id]
            native_bytes = tiles[tile_id]
            if sha256(native_bytes) != pin["source_native_sha256"]:
                raise AuthoringError(f"Native source hash mismatch for tile{tile_id}")
            box = (round(j % nx * raw.width / nx), round(j // nx * raw.height / ny),
                   round((j % nx + 1) * raw.width / nx), round((j // nx + 1) * raw.height / ny))
            if list(box) != pin["raw_panel_box"]:
                raise AuthoringError(f"Frozen panel box mismatch for tile{tile_id}")
            a = np.array(raw.crop(box).resize((192, 224), Image.Resampling.LANCZOS))
            n = np.frombuffer(native_bytes, np.uint8).reshape(28, 24)
            mask = np.repeat(np.repeat(n != 0, 8, 0), 8, 1)
            original = np.repeat(np.repeat(pal[n], 8, 0), 8, 1)
            art = a[:, :, :3].astype(float)
            mean = art.reshape(28, 8, 24, 8, 3).mean((1, 3))
            correction = pal[n].astype(float) - mean
            if family != "ground10":
                correction[n == 0] = 0
            field = np.stack([
                np.array(Image.fromarray(correction[:, :, k].astype(np.float32)).resize(
                    (192, 224), Image.Resampling.BILINEAR)) for k in range(3)
            ], axis=2)
            art = np.clip(art + field, 0, 255)
            if family == "ground10":
                weight = np.clip((edge - 1) / 7, 0, 1)[:, :, None]
                allowed = np.unique(n)
                lock = edge <= 1
                if not np.all(mask):
                    raise AuthoringError(f"Ground tile{tile_id} unexpectedly contains source0")
            else:
                dist = np.minimum(distance_transform_edt(np.pad(mask, 1))[1:-1, 1:-1], rectedge)
                lock = mask & (dist <= 2)
                weight = np.clip((dist - 2) / 6, 0, 1)[:, :, None] * (a[:, :, 3:4].astype(float) / 255)
                allowed = np.unique(n[n != 0])
            blend = np.rint(art * weight + original * (1 - weight)).astype(int)
            colors = pal[allowed].astype(int)
            q = ((blend[:, :, None, :] - colors[None, None, :, :]) ** 2).sum(3).argmin(2)
            rgb = pal[allowed[q]]
            rgba = np.zeros((224, 192, 4), np.uint8)
            rgba[:, :, :3] = rgb
            rgba[:, :, 3] = mask * 255
            rgba[~mask] = 0
            if not np.array_equal(rgba[:, :, :3][lock], original[lock]):
                raise AuthoringError(f"Original-color boundary lock failed for tile{tile_id}")
            if int(lock.sum()) != pin["source_color_lock_pixels"]:
                raise AuthoringError(f"Boundary lock count differs for tile{tile_id}")
            lock_total += int(lock.sum())
            # Verify the historical PNG encoding in memory; only HDA is written.
            encoded = io.BytesIO()
            Image.fromarray(rgb if family == "ground10" else rgba).save(encoded, format="PNG")
            if sha256(encoded.getvalue()) != pin["png_sha256"]:
                raise AuthoringError(f"Registered PNG byte hash differs for tile{tile_id}")
            payload = rgba.tobytes()
            hda = struct.pack("<4s6I", b"HDR1", 2010000 + tile_id, 8, 24, 28, 0, 0) + payload
            if (len(hda) != 172060 or sha256(hda) != pin["hda_sha256"]
                    or sha256(payload) != pin["rgba_payload_sha256"]):
                raise AuthoringError(f"Frozen HDA byte hash differs for tile{tile_id}; nothing written")
            filename = f"terrain-shapesz-{tile_id}-8.hda"
            outputs[filename] = hda
            report_rows.append({"id": tile_id, "file": filename, "bytes": len(hda), "sha256": sha256(hda)})
    if len(outputs) != 23 or lock_total != 36781:
        raise AuthoringError("Frozen family count or original RGB lock total changed")
    report = {"schema": 1, "status": "23_BYTE_EXACT_HDA_REPRODUCED", "versions": VERSIONS,
              "source_sha256": {"shapesz.dat": SHAPES_SHA, "palette.dat": PALETTE_SHA},
              "palette_bank_zero_based": 5, "expanded_palette_sha256": LIVE_PALETTE_SHA,
              "mandatory_original_rgb_lock_hd_pixels": lock_total,
              "c2pa_cryptographic_verification": False,
              "runtime_mask_bytes_retained_unchanged": 1008,
              "assets": sorted(report_rows, key=lambda row: row["id"])}
    return outputs, report


def publish_new_directory(output: Path, outputs: dict[str, bytes], report: dict) -> None:
    # All computations and pins have already passed. Never replace an existing
    # directory, including one created by another process during computation.
    try:
        output.mkdir()
    except OSError as exc:
        raise AuthoringError(f"Cannot create new output directory without overwrite: {exc}") from exc
    created = []
    try:
        files = dict(outputs)
        files["authoring-report.json"] = (json.dumps(report, indent=2, sort_keys=True) + "\n").encode("utf-8")
        for name, data in sorted(files.items()):
            path = output / name
            with path.open("xb") as stream:
                created.append(path)
                stream.write(data)
    except OSError as exc:
        for path in created:
            path.unlink(missing_ok=True)
        try:
            output.rmdir()
        except OSError:
            pass  # Do not remove files created by somebody else.
        raise AuthoringError(f"Output write failed; this invocation's partial files removed: {exc}") from exc


def build(shapesz: Path, palette: Path, output: Path) -> dict:
    resolved_output = validate_paths(shapesz, palette, output)
    shapes_data = read_checked(shapesz, SHAPES_SHA, size=318976)
    palette_data = read_checked(palette, PALETTE_SHA, size=18432)
    outputs, report = compute_assets(shapes_data, palette_data)
    publish_new_directory(resolved_output, outputs, report)
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shapesz", type=Path, required=True,
                        help="caller-supplied legal original shapesz.dat; exact supported SHA256 required")
    parser.add_argument("--palette", type=Path, required=True,
                        help="caller-supplied legal original palette.dat; bank5 is derived locally")
    parser.add_argument("--output", type=Path, required=True,
                        help="new independent output directory outside this source tree; must not already exist")
    args = parser.parse_args(argv)
    try:
        report = build(args.shapesz, args.palette, args.output)
    except (AuthoringError, OSError, ValueError) as exc:
        print(f"terrain23 authoring refused: {exc}", file=sys.stderr)
        return 2
    print(f"Reproduced {len(report['assets'])} byte-exact terrain HDA files in {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
