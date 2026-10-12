#!/usr/bin/env python3
"""Reproduce the frozen top lens and paired MODE assembly without game payload.

Usage: python reproduce_generated_only.py --output-dir /tmp/mode-assembly-build
The destination must be empty and separate from this frozen package.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import struct
import zlib

import PIL
from PIL import Image, ImageChops, ImageDraw

PACKAGE = Path(__file__).resolve().parent


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def fnv1a64(data: bytes) -> str:
    """Standard FNV-1a 64-bit, 16 lowercase hexadecimal digits, no prefix."""
    value = 0xCBF29CE484222325
    for byte in data:
        value ^= byte
        value = (value * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
    return f"{value:016x}"


def hashes(data: bytes) -> dict:
    return {"sha256": hashlib.sha256(data).hexdigest(), "fnv1a64": fnv1a64(data)}


def file_record(path: Path) -> dict:
    data = path.read_bytes()
    record = {"bytes": len(data), **hashes(data)}
    if path.suffix == ".png":
        with Image.open(path) as image:
            image.load()
            decoded = image.tobytes()
            record["decoded"] = {
                "mode": image.mode,
                "width": image.width,
                "height": image.height,
                "layout": "Row-major, top-to-bottom, left-to-right; interleaved mode channels; no padding.",
                "bytes": len(decoded),
                **hashes(decoded),
            }
    return record


def paint_box(mask: Image.Image, box: list[int]) -> None:
    x0, y0, x1, y1 = box
    ImageDraw.Draw(mask).rectangle((x0, y0, x1 - 1, y1 - 1), fill=255)


def sample_checks(tile: Image.Image) -> dict:
    width, height = tile.size
    preview2 = tile.resize((width // 2, height // 2), Image.Resampling.NEAREST)
    density8 = tile.resize((width * 2, height * 2), Image.Resampling.NEAREST)
    expected2 = b"".join(
        bytes(tile.getpixel((2 * x + 1, 2 * y + 1)))
        for y in range(height // 2) for x in range(width // 2)
    )
    expected8 = b"".join(
        b"".join(bytes(tile.getpixel((x, y))) * 2 for x in range(width)) * 2
        for y in range(height)
    )
    require(preview2.tobytes() == expected2, "2x preview differs from canonical 4x nearest sampling.")
    require(density8.tobytes() == expected8, "Density 8 must repeat each 4x pixel in a 2 by 2 block.")
    return {
        "native2_preview_raw_rgba": {"size": list(preview2.size), **hashes(preview2.tobytes())},
        "density8_repeat2x2_raw_rgba": {"size": list(density8.size), **hashes(density8.tobytes())},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    destination = args.output_dir.resolve()
    require(destination != PACKAGE and PACKAGE not in destination.parents,
            "Use a separate output directory outside the frozen package.")
    destination.mkdir(parents=True, exist_ok=True)
    require(not any(destination.iterdir()), "The output directory must be empty.")
    require(fnv1a64(b"") == "cbf29ce484222325", "FNV-1a empty test failed.")
    require(fnv1a64(b"a") == "af63dc4c8601ec8c", "FNV-1a a test failed.")
    require(fnv1a64(b"hello") == "a430d84680aabd0b", "FNV-1a hello test failed.")
    manifest = json.loads((PACKAGE / "manifest.json").read_text(encoding="utf-8"))
    recipe = manifest["build_recipe"]
    inputs = manifest["inputs"]
    for name, expected in inputs.items():
        require(file_record(PACKAGE / name) == expected, f"Input differs from frozen source: {name}")

    with Image.open(PACKAGE / "generated-lenses-master.png") as image:
        lens_master = image.convert("RGB")
    lenses = {}
    for name, spec in recipe["lens_crops"].items():
        # Exact prior-pilot operation order: RGB crop -> Lanczos -> RGBA.
        lenses[name] = lens_master.crop(spec["crop_half_open"]).resize(
            spec["output_size"], Image.Resampling.LANCZOS
        ).convert("RGBA")
        require(lenses[name].getchannel("A").getextrema() == (255, 255), "Lens alpha is not opaque.")
        require(hashes(lenses[name].tobytes()) == spec["expected_decoded_rgba"],
                f"Regenerated {name} lens differs from the selected prior-pilot lens.")

    with Image.open(PACKAGE / "generated-assembly-master.png") as image:
        assembly_master = image.convert("RGBA")
    # Exact accepted-pilot operation order: convert full master to RGBA first.
    metal = assembly_master.crop(recipe["assembly_crop_half_open"]).resize(
        recipe["assembly_output_size"], Image.Resampling.LANCZOS
    )
    tiles = {"lens-top-4x.png": lenses["top"]}
    for mode in (1, 2):
        tile = metal.copy()
        left = "lit" if mode == 1 else "unlit"
        right = "unlit" if mode == 1 else "lit"
        for position, lens_name in ((recipe["lens_offsets"]["left"], left),
                                    (recipe["lens_offsets"]["right"], right)):
            tile.paste(lenses[lens_name], tuple(position))
        require(tile.getchannel("A").getextrema() == (255, 255), "Assembly alpha is not opaque.")
        tiles[f"assembly-mode{mode}-4x.png"] = tile
    for name, tile in tiles.items():
        tile.save(destination / name)

    binding = manifest["resource_binding"]
    payload = b"".join(tiles[name].tobytes() for name in binding["payload_order"])
    require(len(payload) == 28992, "HUL1 payload must be 28992 bytes.")
    guards = binding["source_guard_fnv1a64"]
    header = struct.pack(
        "<4s7I6Q", b"HUL1", 1, 4, 28, 12, 108, 32, len(payload),
        int(guards["pic3_indices"], 16), int(guards["normal_palette_rgb"], 16),
        int(guards["top21_indices"], 16), int(guards["mode1_full216_indices"], 16),
        int(guards["mode2_full216_indices"], 16), int(fnv1a64(payload), 16),
    )
    require(len(header) == 80, "HUL1 header must be 80 bytes.")
    resource = header + payload
    require(len(resource) == 29072, "HUL1 whole file must be 29072 bytes.")
    (destination / binding["filename"]).write_bytes(resource)

    assembly = Image.new("L", (320, 200), 0)
    paint_box(assembly, recipe["assembly_logical_box_half_open"])
    overlap = Image.new("L", assembly.size, 0)
    draw = ImageDraw.Draw(overlap)
    for y, spans in recipe["frame_overlap_row_spans_half_open"]:
        for x0, x1 in spans:
            draw.line((x0, y, x1 - 1, y), fill=255)
    require(ImageChops.subtract(overlap, assembly).getbbox() is None,
            "Frame-overlap mask extends outside the assembly.")
    live = ImageChops.subtract(assembly, overlap)
    combined = assembly.copy()
    paint_box(combined, recipe["top_logical_box_half_open"])
    masks = {
        "assembly-mask": (assembly, 216),
        "assembly-frame-overlap": (overlap, 82),
        "assembly-live-area": (live, 134),
        "top-plus-assembly-mask": (combined, 237),
    }
    for name, (mask, count) in masks.items():
        raw = mask.tobytes()
        require(set(raw) == {0, 255}, f"{name} is not a binary 0/255 mask.")
        require(raw.count(255) == count, f"{name} has the wrong population.")
        mask.save(destination / f"{name}-1x.png")
        (destination / f"{name}.mask").write_bytes(raw)
    require(ImageChops.multiply(overlap, live).getbbox() is None, "Overlap and live masks intersect.")
    require(ImageChops.add(overlap, live).tobytes() == assembly.tobytes(),
            "Overlap plus live masks do not partition the assembly.")

    exports = {name: file_record(destination / name) for name in sorted(manifest["exports"])}
    for name, expected in manifest["exports"].items():
        require(exports[name] == expected,
                f"{name} differs from frozen expected bytes. Use the pinned encoder environment.")
    report = {
        "status": "PASS",
        "source": "Two packaged generated masters and numeric geometry only; no original game payload.",
        "python": platform.python_version(),
        "pillow": PIL.__version__,
        "zlib_compile": zlib.ZLIB_VERSION,
        "zlib_runtime": zlib.ZLIB_RUNTIME_VERSION,
        "fnv1a64_known_vectors": "PASS: empty, a, hello",
        "mask_populations": {name: count for name, (_, count) in masks.items()},
        "masks_binary_0_255": True,
        "assembly_partition_82_plus_134": True,
        "runtime_tiles_opaque_alpha_255": True,
        "unchanged_lenses_match_prior_pilot_decoded_rgba": True,
        "all_exports_match_frozen_expected_bytes": True,
        "all_three_runtime_pngs_match_accepted_pilot_bytes": True,
        "hul1_header_bytes": len(header),
        "hul1_payload_bytes": len(payload),
        "hul1_whole_file_bytes": len(resource),
        "hul1_payload_hashes": hashes(payload),
        "exports": exports,
        "sampling": {name: sample_checks(tile) for name, tile in tiles.items()},
    }
    (destination / "build-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "exports": len(exports), "combined_logical_pixels": 237}))


if __name__ == "__main__":
    main()
