#!/usr/bin/env python3
"""Build the engineer-defined HUF1 resource from frozen authored vector inputs.

No game assets or reference PNG are input to this build. PIC3, palette and
original encoded-font signatures are supplied compatibility metadata.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import struct
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("frozen_vector_reproducer", ROOT / "reproduce.py")
reproduce = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(reproduce)
EXPECTED_RESOURCE_SHA256 = "3c328c1537cf1e09529ae8805e98a8deb57a859ea80ba269cfea0b55cfae539e"


def fnv1a64(data):
    value = 14695981039346656037
    for byte in data:
        value = ((value ^ byte) * 1099511628211) & 0xffffffffffffffff
    return value


def require(condition, message):
    if not condition:
        raise ValueError(message)


def build(output, proof):
    contract = json.loads((ROOT / "sources/resource-contract.json").read_text())
    metrics = json.loads((ROOT / "sources/source-font-metrics.json").read_text())
    vectors = json.loads((ROOT / "sources/glyph-vectors.json").read_text())
    # Alpha is rendered from vectors by the standalone reproducer, never decoded
    # from the packaged canonical PNG or copied from an existing resource.
    reproduce.reproduce(proof)
    alpha = (proof / "tiny-coverage-atlas-4x.alpha.bin").read_bytes()
    require(contract["struct_format"] == "<4s11I8Q", "Unexpected header format")
    require(contract["u32_values"] == [1, 4, 512, 320, 127, 86, 32, 40, 4, 163840, 7],
            "Unexpected HUF1 geometry or eligibility fields")
    stamps = [int(value, 16) for value in contract["u64_values_hex"]]
    require(len(stamps) == 8 and stamps[7] == 0, "Unexpected compatibility stamps")
    font_ascii = struct.pack("<256i", *metrics["font_ascii"])
    require(fnv1a64(font_ascii) == stamps[2], "font_ascii FNV-1a64 mismatch")
    glyphs = sorted(metrics["tiny_font"]["glyphs"], key=lambda g: g["sprite_id"])
    require([g["sprite_id"] for g in glyphs] == list(range(127)),
            "Unexpected source glyph IDs")
    require(all(g["advance"] == g["width"] + 1 for g in glyphs),
            "Original source advance is not width plus one")
    serialized_metrics = b"".join(struct.pack("<3H", g["width"], g["height"], g["width"] + 1)
                                  for g in glyphs)
    require(len(serialized_metrics) == 762 and fnv1a64(serialized_metrics) == stamps[3],
            "Glyph metrics FNV-1a64 mismatch")
    eligible_ids = {sid for sid in metrics["font_ascii"][:128] if sid >= 0}
    require(eligible_ids == set(range(86)), "Unexpected eligible ASCII glyph IDs")
    eligible_mask = bytes(255 if sid in eligible_ids else 0 for sid in range(127))
    require(fnv1a64(eligible_mask) == stamps[6], "Eligible-mask FNV-1a64 mismatch")
    require(fnv1a64(alpha) == stamps[5], "Alpha payload FNV-1a64 mismatch")
    require(hashlib.sha256(alpha).hexdigest() == reproduce.EXPECTED_ALPHA_SHA256,
            "Canonical raw alpha SHA-256 mismatch")
    require(len(alpha) == 163840, "Unexpected alpha length")

    allowed = bytearray(512 * 320)
    bounds_checks = []
    for glyph in vectors["glyphs"]:
        sid = glyph["sprite_id"]
        x, y = (sid % 16) * 32 + 4, (sid // 16) * 40 + 4
        width, height = glyph["width"] * 4, glyph["height"] * 4
        require(glyph["atlas_box_px_half_open"] == [x, y, x + width, y + height],
                f"Glyph {sid}: original canvas at inset 4 mismatch")
        for row in range(y, y + height):
            allowed[row * 512 + x:row * 512 + x + width] = b"\x01" * width
        bounds_checks.append({"sprite_id": sid, "canvas_at_inset_4": True})
    nonzero_outside = sum(bool(value) and not allowed[index]
                          for index, value in enumerate(alpha))
    slot127 = bytes(alpha[y * 512 + x] for y in range(280, 320) for x in range(480, 512))
    require(nonzero_outside == 0, "Nonzero alpha outside original glyph canvases")
    require(not any(slot127), "Unused slot 127 is not empty")
    header = struct.pack("<4s11I8Q", b"HUF1", *contract["u32_values"], *stamps)
    require(len(header) == contract["header_bytes"] == 112, "Header size mismatch")
    resource = header + alpha
    require(len(resource) == contract["total_bytes"] == 163952, "Resource size mismatch")
    resource_hash = hashlib.sha256(resource).hexdigest()
    require(resource_hash == EXPECTED_RESOURCE_SHA256, "HUF1 SHA-256 mismatch")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(resource)
    # Reopen and independently unpack the completed file, then compare every
    # field in order and the payload bytes. This also proves exact EOF.
    saved = output.read_bytes()
    fields = struct.unpack("<4s11I8Q", saved[:112])
    require(fields == (b"HUF1", *contract["u32_values"], *stamps), "Packed header mismatch")
    require(saved[112:] == alpha, "Saved payload mismatch")
    report = {
        "status": "PASS", "resource_filename": output.name,
        "resource_bytes": len(saved), "resource_sha256": resource_hash,
        "header_struct": "<4s11I8Q", "header_bytes": 112,
        "header_fields_verified_by_unpack": True,
        "payload_bytes": len(alpha), "exact_eof_verified": True,
        "payload_equals_vector_reproduced_canonical_alpha": True,
        "payload_sha256": hashlib.sha256(alpha).hexdigest(),
        "payload_fnv1a64": f"{fnv1a64(alpha):016x}",
        "font_ascii_fnv1a64_independently_recomputed": f"{fnv1a64(font_ascii):016x}",
        "font_ascii_encoding": "256 signed 32-bit integers, little-endian",
        "metrics_fnv1a64_independently_recomputed": f"{fnv1a64(serialized_metrics):016x}",
        "metrics_encoding": "Glyph IDs 0 through 126, each u16le(width,height,width+1); 762 bytes",
        "eligible_mask_fnv1a64_independently_recomputed": f"{fnv1a64(eligible_mask):016x}",
        "eligible_mask_encoding": "127 bytes in glyph-ID order; 255 for mapped ASCII IDs 0 through 85, otherwise 0",
        "nonzero_alpha_outside_original_w_by_h_at_inset_4": nonzero_outside,
        "unused_slot_127_entirely_zero": not any(slot127),
        "glyph_canvas_checks": bounds_checks,
        "geometry_records": 127, "eligible_ascii_glyphs": 86,
        "extended_or_accented_runs": "Wholly classic",
        "authored_stroke_role": 7,
        "source_asset_compatibility_stamps": {
            "status": "Supplied by hook engineer; not recomputed from game assets by this package",
            "pic3_fnv1a64": f"{stamps[0]:016x}",
            "palette_fnv1a64": f"{stamps[1]:016x}",
            "tiny_encoded_fnv1a64": f"{stamps[4]:016x}",
        },
        "runtime_installed_or_executed_by_this_build": False,
    }
    (proof / "huf1-resource-proof.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "gameplay-hud-font-v1.hda")
    parser.add_argument("--proof-output", type=Path, default=ROOT / "proof/resource-build")
    args = parser.parse_args()
    result = build(args.output.resolve(), args.proof_output.resolve())
    print(json.dumps({k: result[k] for k in ("status", "resource_bytes", "resource_sha256",
                                           "payload_fnv1a64", "eligible_ascii_glyphs")}, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as error:
        print(f"Resource build failed: {error}", file=sys.stderr)
        sys.exit(1)
