#!/usr/bin/env python3
"""Read-only bounded authoring check. No runtime registration or output writes."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from PIL import Image

IDENTITY = {'logical_bank': 10,
 'bank': 'newshf.shp',
 'bank_size': 33543,
 'bank_sha256': '852c2fb552c9077a198be7902d8f58699ed070dabcd36c6e3acfe80dd3804cce',
 'item_table': 'tyrian.hdt',
 'item_table_sha256': 'fde8506326e7bb0916b38c362e33bf8a8a5affa561206c021af7f65b4a17745b',
 'records': [{'record': 163,
              'offset': 176566,
              'size': 77,
              'sha256': '9e7afb0db4dc9e07278b2e2de4fe610215b2b2241f43ebcda116816e9d8c901c',
              'bases': [125, 123, 127],
              'ani': 1,
              'animate': 0,
              'esize': 1},
             {'record': 167,
              'offset': 176874,
              'size': 77,
              'sha256': '799fcf3bdf90d75e0cdf09eb63988db12a113bbd692cceaf80ed521aa29aaaa8',
              'bases': [3, 1, 5],
              'ani': 1,
              'animate': 0,
              'esize': 1},
             {'record': 168,
              'offset': 176951,
              'size': 77,
              'sha256': '574bce52037236a1bc3dd655ad7be44c933fa71a68e203f6eecdb3c08aeb2e11',
              'bases': [55, 17, 93],
              'ani': 1,
              'animate': 0,
              'esize': 1}],
 'logical_size': [24, 28],
 'density': 8,
 'logical_anchor': [6, 7],
 'pixel_size': [192, 224],
 'component_offsets': [0, 1, 19, 20],
 'alpha': 'binary-0-255',
 'selection': 'enemycycle; not automatic three-frame animation'}
# Artwork policy is versioned separately from immutable original source identity.
SOFT168_POLICY = {'alpha': 'straight-rgba8-zero-transparent-rgb', 'bases': [55, 17, 93], 'record': 168, 'revision': 'newshf168-v4-max-canvas-soft-alpha-v1', 'selected_png_sha256': {'17': 'e02d8f0b3c622aa7fd846406f5df30dc6ac0a4af1eed70a1103fec19dac1955b', '55': '9cfc7d7b8c2b20917bd58898cf21fbb76ad2841e371158f37316aab3f8818e70', '93': 'c0f68d1715b31fa314f9ba65dbb910bc7c7edc3f6ad4bb4f2958da032e6f61b5'}}

DEFAULT = Path(__file__).resolve().parents[1] / "authoring-inputs/enemies/newshf-phase-a"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError("nonfinite JSON")))


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def check(directory=DEFAULT, game_data=None):
    directory = Path(directory).resolve()
    for name in ("manifest.json", "provenance.json"):
        require(not (directory / name).is_symlink(), "metadata symlink")
    manifest = read_json(directory / "manifest.json")
    require(isinstance(manifest, dict), "manifest object")
    require(type(manifest.get("schema")) is int and manifest["schema"] in (1, 2), "schema")
    fields = {"schema", "scope", "identity", "art"}
    if manifest["schema"] == 2:
        fields.add("art_policy")
        require(canonical(manifest.get("art_policy")) == canonical(SOFT168_POLICY), "unapproved artwork alpha policy/revision")
    require(set(manifest) == fields, "manifest fields")
    require(manifest["scope"] == "source-only-selected-art-candidate", "scope")
    require(canonical(manifest["identity"]) == canonical(IDENTITY), "immutable source identity/geometry")
    art = manifest["art"]
    require(isinstance(art, list) and len(art) == 9, "exactly nine source PNGs required")
    expected = [(r["record"], b) for r in IDENTITY["records"] for b in r["bases"]]
    seen_files, seen_hashes, seen_pixels = set(), set(), set()
    outputs = []
    for entry, (record, base) in zip(art, expected):
        require(isinstance(entry, dict) and set(entry) == {"source_id", "record", "base", "file", "art_sha256"}, "art fields")
        require(type(entry["record"]) is int and type(entry["base"]) is int and
                (entry["record"], entry["base"]) == (record, base), "record/base order or duplicate/missing identity")
        require(entry["source_id"] == f"newshf.shp:base:{base}", "source alias")
        filename = f"enemy-{record}-v1-bbox-fit-base{base}.png"
        require(entry["file"] == filename and filename not in seen_files, "path escape/alias or duplicate file")
        path = directory / filename
        require(not path.is_symlink() and path.is_file() and path.resolve().parent == directory, "missing/unsafe PNG")
        data = path.read_bytes()
        actual = digest(data)
        require(isinstance(entry["art_sha256"], str) and re.fullmatch(r"[0-9a-f]{64}", entry["art_sha256"]) and actual == entry["art_sha256"], "art hash mismatch")
        require(actual not in seen_hashes, "duplicate art bytes")
        with Image.open(path) as im:
            require(im.format == "PNG" and im.mode == "RGBA" and im.size == (192, 224), "PNG RGBA geometry")
            require(getattr(im, "n_frames", 1) == 1, "animated PNG forbidden")
            im.load()
            alpha = im.getchannel("A")
            raw = im.tobytes()
            if manifest["schema"] == 2 and record == 168:
                require(actual == SOFT168_POLICY["selected_png_sha256"][str(base)], "unselected soft-alpha artwork revision")
                require({0, 255}.issubset(set(alpha.tobytes())) and any(0 < v < 255 for v in alpha.tobytes()), "selected soft-alpha foreground/background required")
            else:
                require(set(alpha.tobytes()) == {0, 255}, "binary alpha with nonempty foreground/background required")
            require(all(raw[i+3] or raw[i:i+3] == b"\0\0\0" for i in range(0, len(raw), 4)), "hidden transparent RGB")
            pixels = digest(im.tobytes())
            require(pixels not in seen_pixels, "duplicate pose pixels/source alias")
            outputs.append(dict(source_id=entry["source_id"], file=filename, art_sha256=actual,
                                rgba_sha256=pixels, alpha_bbox=list(alpha.getbbox()),
                                opaque_pixels=alpha.histogram()[255]))
        seen_files.add(filename); seen_hashes.add(actual); seen_pixels.add(pixels)
    inventory = list(directory.iterdir())
    require({p.name for p in inventory} == seen_files | {"manifest.json", "provenance.json", "report.json"}, "unexpected/missing source-bundle file")
    require(all(p.is_file() and not p.is_symlink() for p in inventory), "source-bundle directories/symlinks forbidden")
    provenance = read_json(directory / "provenance.json")
    require(set(provenance) == {"schema", "origin", "selection", "postprocess", "groups"} and type(provenance["schema"]) is int and provenance["schema"] == 1, "provenance schema")
    require(all(isinstance(provenance[k], str) and provenance[k] for k in ("origin", "selection", "postprocess")), "provenance descriptions")
    require(isinstance(provenance["groups"], list) and len(provenance["groups"]) == 3, "provenance groups")
    for group, rec in zip(provenance["groups"], IDENTITY["records"]):
        require(set(group) == {"record", "ai_raw_sha256", "normalization_script_sha256", "poses"} and type(group["record"]) is int and group["record"] == rec["record"], "provenance record")
        for key in ("ai_raw_sha256", "normalization_script_sha256"):
            require(isinstance(group[key], str) and re.fullmatch(r"[0-9a-f]{64}", group[key]), "provenance digest")
        require(isinstance(group["poses"], list) and len(group["poses"]) == 3, "provenance poses")
        for pose, base in zip(group["poses"], rec["bases"]):
            require(set(pose) == {"base", "source_bbox", "resize", "paste", "source_edge_to_canvas_matrix", "selected_png_sha256"}, "provenance pose fields")
            require(type(pose["base"]) is int and pose["base"] == base, "provenance pose identity")
            selected = next(e for e in art if e["base"] == base)
            require(pose["selected_png_sha256"] == selected["art_sha256"], "provenance/art hash drift")
            for key, length in (("source_bbox", 4), ("resize", 2), ("paste", 2)):
                require(isinstance(pose[key], list) and len(pose[key]) == length and all(type(x) is int and x >= 0 for x in pose[key]), "provenance geometry")
            box, size, paste = pose["source_bbox"], pose["resize"], pose["paste"]
            require(box[2] > box[0] and box[3] > box[1] and min(size) > 0 and paste[0]+size[0] <= 192 and paste[1]+size[1] <= 224, "provenance crop/paste bounds")
            sx, sy = size[0]/(box[2]-box[0]), size[1]/(box[3]-box[1])
            matrix = [[sx, 0, paste[0]-box[0]*sx], [0, sy, paste[1]-box[1]*sy], [0, 0, 1]]
            require(canonical(pose["source_edge_to_canvas_matrix"]) == canonical(matrix), "provenance transform")
    verified = False
    if game_data is not None:
        game_data = Path(game_data)
        bank = (game_data / IDENTITY["bank"]).read_bytes()
        require(len(bank) == IDENTITY["bank_size"] and digest(bank) == IDENTITY["bank_sha256"], "original bank pin")
        table = (game_data / IDENTITY["item_table"]).read_bytes()
        require(digest(table) == IDENTITY["item_table_sha256"], "item table pin")
        for rec in IDENTITY["records"]:
            require(digest(table[rec["offset"]:rec["offset"]+rec["size"]]) == rec["sha256"], "77-byte record pin")
        verified = True
    return dict(schema=1, status="source-only-selected-art-candidate", runtime_accepted=False,
                source_identity_sha256=digest(canonical(IDENTITY).encode()),
                manifest_sha256=digest((directory/"manifest.json").read_bytes()),
                provenance_sha256=digest((directory/"provenance.json").read_bytes()),
                original_bytes_verified=verified, sources=outputs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=DEFAULT)
    parser.add_argument("--game-data", type=Path, help="optional private original bytes; never copied")
    args = parser.parse_args()
    try:
        print(json.dumps(check(args.source_dir, args.game_data), indent=2, sort_keys=True))
    except (ValueError, OSError, TypeError, KeyError) as exc:
        print("NEWSHF source check failed: " + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
