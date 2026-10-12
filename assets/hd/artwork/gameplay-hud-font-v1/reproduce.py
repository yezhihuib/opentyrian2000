#!/usr/bin/env python3
"""Reproduce frozen authored coverage from vector JSON and metadata only.

Never imports the historical authoring script, opens original game assets, or
reads the canonical PNG/SVG. Expected hashes are non-pixel verification metadata.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
from pathlib import Path
import sys
import zlib

import PIL
from PIL import Image, ImageChops, ImageDraw

ROOT = Path(__file__).resolve().parent
SOURCES = ROOT / "sources"
EXPECTED_PNG_SHA256 = "f81c31f85ec8646e5fd5e29e9cb9e6f03b8f51988e3dfc945bc2fa6821dfed92"
EXPECTED_ALPHA_SHA256 = "e4f245519b2922b3f3575ae499f0419bfc85742d059a07680f3693e68ddbaeb7"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(name: str) -> dict:
    return json.loads((SOURCES / name).read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def coverage(record: dict, stroke_width: float) -> Image.Image:
    # Preserve the original authoring rasterizer exactly: 32 samples per
    # logical pixel, Pillow lines/dots, logical opaque-box clip, BOX to 4x.
    high_density = 32
    mask = Image.new("L", (record["width"] * high_density,
                           record["height"] * high_density))
    draw = ImageDraw.Draw(mask)
    for line in record["paths"]:
        points = [(round(x * high_density), round(y * high_density))
                  for x, y in line]
        if len(points) == 1:
            x, y = points[0]
            radius = stroke_width / 2 * high_density
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=255)
        else:
            draw.line(points, fill=255, width=round(stroke_width * high_density),
                      joint="curve")
    box = record["opaque_bbox_half_open"]
    clip = Image.new("L", mask.size)
    ImageDraw.Draw(clip).rectangle(
        (box[0] * high_density, box[1] * high_density,
         box[2] * high_density - 1, box[3] * high_density - 1), fill=255)
    mask = ImageChops.multiply(mask, clip)
    return mask.resize((record["width"] * 4, record["height"] * 4),
                       Image.Resampling.BOX)


def reproduce(output: Path) -> dict:
    vectors = load_json("glyph-vectors.json")
    metrics = load_json("source-font-metrics.json")
    original = load_json("original-atlas-manifest.json")
    require(vectors["stroke_width_logical"] == 0.72, "Unexpected stroke width")
    require(original["density"] == 4 and original["atlas_size"] == [512, 320],
            "Unexpected canonical layout")
    require(original["font_ascii"] == metrics["font_ascii"], "Mapping mismatch")
    require(sha256((SOURCES / "source-font-metrics.json").read_bytes()) ==
            original["metrics_source_sha256"], "Original metadata hash mismatch")
    require(len(vectors["glyphs"]) == 127, "Expected 127 geometric glyphs")
    ascii_bytes = [byte for byte, sprite in enumerate(metrics["font_ascii"][:128])
                   if sprite >= 0]
    require(len(ascii_bytes) == 86, "Expected 86 mapped ASCII glyphs")
    source_glyphs = {g["sprite_id"]: g for g in metrics["tiny_font"]["glyphs"]}
    original_glyphs = {g["sprite_id"]: g for g in original["glyphs"]}
    require(len(source_glyphs) == len(original_glyphs) == 127, "Glyph metadata mismatch")
    require({g["sprite_id"] for g in vectors["glyphs"]} == set(range(127)),
            "Unexpected vector glyph IDs")

    # (0,0,0,0) padding is intentionally retained. All glyph tile RGB is white,
    # including transparent tile pixels, as in the byte-frozen reviewed atlas.
    atlas = Image.new("RGBA", (512, 320))
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="512" height="320" viewBox="0 0 128 80">']
    glyph_checks = []
    for record in vectors["glyphs"]:
        sid = record["sprite_id"]
        source = source_glyphs[sid]
        reference = original_glyphs[sid]
        for key in ("width", "height", "advance", "opaque_bbox_half_open"):
            require(record[key] == source[key] == reference[key],
                    f"Glyph {sid}: {key} mismatch")
        require(record["codepoints_cp437"] == source["character_codes"] ==
                reference["codepoints_cp437"], f"Glyph {sid}: byte mapping mismatch")
        require(record["character"] == source["characters_cp437"][0] ==
                reference["character"], f"Glyph {sid}: character mismatch")
        x = (sid % 16) * 32 + 4
        y = (sid // 16) * 40 + 4
        box_px = [x, y, x + record["width"] * 4, y + record["height"] * 4]
        require(record["atlas_box_px_half_open"] == box_px ==
                reference["atlas_box_px_half_open"], f"Glyph {sid}: atlas box mismatch")
        mask = coverage(record, vectors["stroke_width_logical"])
        digest = sha256(mask.tobytes())
        require(digest == record["coverage_sha256"] == reference["coverage_sha256"],
                f"Glyph {sid}: raw coverage mismatch")
        tile = Image.new("RGBA", mask.size, "white")
        tile.putalpha(mask)
        atlas.paste(tile, (x, y))
        bx0, by0, bx1, by1 = record["opaque_bbox_half_open"]
        svg.append(f'<defs><clipPath id="glyph{sid}"><rect x="{x/4+bx0}" y="{y/4+by0}" width="{bx1-bx0}" height="{by1-by0}"/></clipPath></defs><g clip-path="url(#glyph{sid})">')
        for line in record["paths"]:
            if len(line) == 1:
                px, py = line[0]
                svg.append(f'<circle cx="{x/4+px:.5f}" cy="{y/4+py:.5f}" r=".36" fill="white"/>')
            else:
                path = "M " + " L ".join(f"{px:.5f} {py:.5f}" for px, py in line)
                svg.append(f'<path transform="translate({x/4} {y/4})" d="{path}" fill="none" stroke="white" stroke-width=".72" stroke-linejoin="round"/>')
        svg.append("</g>")
        glyph_checks.append({"sprite_id": sid, "coverage_sha256": digest,
                             "matches_frozen_vector_and_original_manifest": True})
    svg.append("</svg>")
    output.mkdir(parents=True, exist_ok=True)
    png_path = output / "tiny-coverage-atlas-4x.png"
    svg_path = output / "tiny-vector-atlas.svg"
    alpha_path = output / "tiny-coverage-atlas-4x.alpha.bin"
    # Same default PNG encoding as reviewed authoring output. No time or metadata.
    atlas.save(png_path)
    svg_path.write_text("\n".join(svg) + "\n", encoding="utf-8")
    alpha = atlas.getchannel("A").tobytes()
    alpha_path.write_bytes(alpha)
    png_hash = sha256(png_path.read_bytes())
    alpha_hash = sha256(alpha)
    colors = atlas.getcolors(atlas.width * atlas.height)
    covered_white = all(r == g == b == 255 for count, (r, g, b, a) in colors if a)
    report = {
        "status": "PASS" if png_hash == EXPECTED_PNG_SHA256 and
                  alpha_hash == EXPECTED_ALPHA_SHA256 and covered_white else "FAIL",
        "input_scope": "Frozen vector JSON and original metadata only; no image input",
        "runtime_resource_header_or_layout": "PENDING_HOOK_ENGINEER_NOT_DEFINED_HERE",
        "versions": {"python": platform.python_version(), "Pillow": PIL.__version__,
                     "zlib_build": zlib.ZLIB_VERSION, "zlib_runtime": zlib.ZLIB_RUNTIME_VERSION},
        "geometric_glyph_count": 127,
        "first_candidate_eligible_mapped_ascii_glyph_count": 86,
        "extended_geometric_glyph_count_excluded_from_first_candidate": 41,
        "png_sha256": png_hash,
        "expected_png_sha256": EXPECTED_PNG_SHA256,
        "png_bytes_match_frozen_canonical": png_hash == EXPECTED_PNG_SHA256,
        "raw_alpha_sha256": alpha_hash,
        "expected_raw_alpha_sha256": EXPECTED_ALPHA_SHA256,
        "raw_alpha_match_frozen_canonical": alpha_hash == EXPECTED_ALPHA_SHA256,
        "raw_rgba_sha256": sha256(atlas.tobytes()),
        "svg_sha256": sha256(svg_path.read_bytes()),
        "atlas_size": list(atlas.size), "mode": atlas.mode,
        "raw_alpha_size_bytes": len(alpha),
        "all_nontransparent_pixels_have_white_rgb": covered_white,
        "opaque_black_pixel_count": sum(n for n, (r, g, b, a) in colors
                                        if a and r == g == b == 0),
        "fully_transparent_pixel_count": sum(n for n, (_, _, _, a) in colors if not a),
        "transparent_black_padding_pixel_count": sum(n for n, rgba in colors
                                                      if rgba == (0, 0, 0, 0)),
        "transparent_white_tile_pixel_count": sum(n for n, rgba in colors
                                                   if rgba == (255, 255, 255, 0)),
        "intermediate_alpha_pixel_count": sum(n for n, (_, _, _, a) in colors if 0 < a < 255),
        "glyph_checks": glyph_checks,
    }
    (output / "reproduction-report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8")
    require(report["status"] == "PASS", "Canonical reproduction failed; see preserved report")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "proof" / "reproduced",
                        help="Output directory. The frozen atlas is never an input.")
    args = parser.parse_args()
    output = args.output.resolve()
    require(output != (ROOT / "atlas").resolve(), "Refusing to overwrite frozen atlas directory")
    result = reproduce(output)
    print(json.dumps({k: result[k] for k in (
        "status", "png_sha256", "raw_alpha_sha256", "svg_sha256",
        "geometric_glyph_count", "first_candidate_eligible_mapped_ascii_glyph_count")}, indent=2))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError) as error:
        print(f"Reproduction failed: {error}", file=sys.stderr)
        sys.exit(1)
