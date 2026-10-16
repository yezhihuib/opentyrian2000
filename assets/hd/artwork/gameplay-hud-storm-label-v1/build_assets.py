#!/usr/bin/env python3
"""Build original, data-independent STORM heading coverage and palette roles.

Read only geometry.json beside this program. No game data, palette arrays,
decoded sprites, captures, system fonts, or source bitmap masks are inputs.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import zlib

import numpy as np
from PIL import Image
import PIL

HERE = Path(__file__).resolve().parent
VERSIONS = {"Pillow": "12.3.0", "numpy": "2.3.5", "zlib": "1.3.2"}


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def fnv1a64(data):
    value = 0xcbf29ce484222325
    for byte in data:
        value = ((value ^ byte) * 0x100000001b3) & 0xffffffffffffffff
    return f"{value:016x}"


def glyph_paths(geometry):
    """Lay out geometric stroked letters; preserve the established .72 stem."""
    for letter in geometry["layout"]:
        width = letter["width"]
        for path in geometry["glyphs"][letter["character"]]:
            yield [(letter["x"] + .38 + (x - .38) * (width - .76) / 3.24,
                    y) for x, y in path]


def supersampled_fields(geometry):
    """Analytic capsule/segment distance; no pre-rasterized glyph is scaled."""
    width, height = geometry["canvas_logical"]
    sample = geometry["coverage_sampling_density"]
    y, x = np.mgrid[:height * sample, :width * sample]
    x = (x + .5) / sample
    y = (y + .5) / sample
    distance2 = np.full(x.shape, np.inf, dtype=np.float64)
    for path in glyph_paths(geometry):
        for (ax, ay), (bx, by) in zip(path, path[1:]):
            dx, dy = bx - ax, by - ay
            projection = np.clip(((x - ax) * dx + (y - ay) * dy) /
                                 (dx * dx + dy * dy), 0, 1)
            distance2 = np.minimum(distance2,
                (x - ax - projection * dx) ** 2 +
                (y - ay - projection * dy) ** 2)
    coverage = distance2 <= (geometry["stroke_width_logical"] / 2) ** 2
    top, bottom = geometry["palette_index_top"], geometry["palette_index_bottom"]
    value = top + (bottom - top) * y / height
    return coverage, value


def planes(geometry, density):
    coverage, value = supersampled_fields(geometry)
    width, height = geometry["canvas_logical"]
    block = geometry["coverage_sampling_density"] // density
    assert block * density == geometry["coverage_sampling_density"]
    shape = (height * density, block, width * density, block)
    covered = coverage.reshape(shape).sum(axis=(1, 3))
    weighted = (coverage * value).reshape(shape).sum(axis=(1, 3))
    alpha = np.floor(covered * 255.0 / (block * block) + .5).astype(np.uint8)
    index = np.zeros(alpha.shape, dtype=np.uint8)
    present = covered > 0
    index[present] = np.floor(weighted[present] / covered[present] + .5).astype(np.uint8)
    assert np.array_equal(alpha == 0, index == 0)
    assert set(index[present]).issubset(set(range(192, 208)))
    assert not alpha[:, 4 * density:5 * density].any()
    assert not alpha[:, 9 * density:10 * density].any()
    assert not alpha[:, 14 * density:15 * density].any()
    assert not alpha[:, 19 * density:20 * density].any()
    return index, alpha


def png(image):
    buffer = io.BytesIO()
    image.save(buffer, format="PNG", optimize=False, compress_level=9)
    return buffer.getvalue()


def svg(geometry):
    # SVG is a structural vector preview. Its authored display green is not a
    # runtime palette. The palette-index/coverage planes are authoritative.
    paths = []
    for path in glyph_paths(geometry):
        command = "M " + " L ".join(f"{x:.6f},{y:.6f}" for x, y in path)
        paths.append(f'  <path d="{command}"/>')
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="100" height="20" '
            'viewBox="0 0 25 5">\n'
            '<title>STORM heading independently authored vector geometry</title>\n'
            '<g fill="none" stroke="#009a04" stroke-width="0.72" '
            'stroke-linecap="round" stroke-linejoin="round">\n' +
            "\n".join(paths) + "\n</g>\n</svg>\n").encode()


def build(output):
    actual = {"Pillow": PIL.__version__, "numpy": np.__version__,
              "zlib": zlib.ZLIB_RUNTIME_VERSION}
    if actual != VERSIONS:
        raise RuntimeError(f"Reproducible build requires {VERSIONS}, found {actual}")
    source = (HERE / "geometry.json").read_bytes()
    geometry = json.loads(source)
    assert geometry["text"] == "STORM"
    assert geometry["canvas_logical"] == [25, 5]
    outputs = {"storm-heading.svg": svg(geometry)}
    densities = []
    for density in (4, 8):
        index, alpha = planes(geometry, density)
        prefix = f"storm-heading-{density}x"
        outputs[f"{prefix}-index.bin"] = index.tobytes()
        outputs[f"{prefix}-coverage.bin"] = alpha.tobytes()
        outputs[f"{prefix}-index.png"] = png(Image.fromarray(index, "L"))
        outputs[f"{prefix}-coverage.png"] = png(Image.fromarray(alpha, "L"))
        # Neutral authored-green PNG for inspecting letter geometry only. It
        # does not embed a source palette or replace runtime palette response.
        preview = np.empty((*index.shape, 4), dtype=np.uint8)
        preview[:, :, 0] = 0
        preview[:, :, 1] = 154
        preview[:, :, 2] = 4
        preview[:, :, 3] = alpha
        outputs[f"{prefix}-geometry.png"] = png(Image.fromarray(preview, "RGBA"))
        densities.append({"density": density, "pixel_size": [25*density, 5*density],
                          "plane_bytes": index.size, "index": f"{prefix}-index.bin",
                          "coverage": f"{prefix}-coverage.bin",
                          "coverage_nonzero": int(np.count_nonzero(alpha)),
                          "coverage_fractional": int(np.count_nonzero((alpha > 0) & (alpha < 255))),
                          "covered_palette_roles": sorted(int(v) for v in set(index[alpha > 0]))})
    contract = {
        "schema": "storm-heading-palette-coverage-art-v1",
        "status": "PRIVATE_PILOT_NOT_PUBLISHED",
        "original_source_not_required": True,
        "logical_size": [25, 5], "original_icon_size": [25, 13],
        "sprite_bank": 5, "sprite_index_zero_based": 37,
        "ownership_local_half_open": [0, 0, 25, 5],
        "preserve_original_local_half_open": [0, 5, 25, 13],
        "ammo_gauge_y_start": 13,
        "binding": {
            "planes": "uint8 row-major top-to-bottom, left-to-right; no stride padding",
            "index": "Absolute game palette index. Zero exactly where coverage is zero.",
            "coverage": "0..255 authored vector ink alpha; not source-sprite alpha or ownership",
            "background": "Whole top 25x5 owned rectangle is palette[0]; never blend onto old glyph pixels.",
            "composite": "(palette[index]*coverage + palette[0]*(255-coverage) + 127) // 255 per RGB channel",
            "palette": "Use active runtime palette. This package contains no source palette arrays.",
            "density2": "Offline art-preview comparison uses 2x2 averaging of composited density4; production retains existing SDL nearest sampling of selected density4/8. Native readback is authoritative.",
            "density8": "Independently integrated analytic geometry; not replicated density4 pixels.",
            "guard": "Integrator validates original full 25x13 icon identity before suppressing only rows0..4."
        },
        "densities": densities,
        "design": {"geometry": "Procedural geometric line strokes compatible with authored HUD labels",
                   "color": "Green roles197..201; continuous vertical value field then quantized palette roles",
                   "no_added_glow_panel_or_outline": True,
                   "lower_motif_redrawn": False},
        "source_sha256": {"geometry.json": sha256(source),
                          "build_assets.py": sha256(Path(__file__).read_bytes())},
        "build_dependencies": actual,
        "artifacts": [{"path": name, "bytes": len(data), "sha256": sha256(data),
                       "fnv1a64": fnv1a64(data)} for name, data in sorted(outputs.items())]
    }
    outputs["contract.json"] = (json.dumps(contract, indent=2) + "\n").encode()
    for name, data in sorted(outputs.items()):
        path = output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and path.read_bytes() != data:
            raise FileExistsError(f"Refusing different existing output: {path}")
        path.write_bytes(data)
    return contract


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.output.resolve()), indent=2))
