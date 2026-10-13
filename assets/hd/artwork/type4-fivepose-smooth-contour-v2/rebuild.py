#!/usr/bin/env python3
"""Rebuild frozen type4 art from generated masters only, into a fresh output."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
from PIL import Image, __version__ as pillow_version


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    contract = json.loads((root / "contract.json").read_text())
    assert pillow_version == contract["reconstruction"]["version"], "Use pinned Pillow version"
    output = args.output.absolute()
    assert not output.exists(), "Output must be a fresh path"
    assert not any(path.is_symlink() for path in [output, *output.parents]), "No symlink paths"
    assert root not in output.parents and output not in root.parents, "Output must be outside source package"
    products = []
    for entry in contract["entries"]:
        source = root / entry["source"]
        assert root in source.resolve().parents
        assert sha(source.read_bytes()) == entry["source_sha256"]
        master = Image.open(source).convert("RGBA")
        actual_box = master.getchannel("A").point(lambda value: 255 if value >= 128 else 0).getbbox()
        assert list(actual_box) == entry["generated_crop_alpha_ge128_xyxy"]
        piece = master.crop(actual_box).resize(entry["registered_piece_size"], Image.Resampling.LANCZOS)
        image = Image.new("RGBA", (192, 224))
        image.alpha_composite(piece, entry["registered_paste_xy"])
        rgba = image.tobytes()
        assert sha(rgba) == entry["RGBA_sha256"]
        hda = b"HDR1" + struct.pack("<6I", *entry["header_u32"]) + rgba
        assert sha(hda) == entry["HDA_sha256"]
        products.append((entry, image, hda))
    output.mkdir(parents=True)
    receipt = []
    for entry, image, hda in products:
        name = "enemy-newsh2-{}-8".format(entry["id"])
        png_path = output / (name + ".png")
        image.save(png_path)
        assert sha(png_path.read_bytes()) == entry["PNG_sha256"]
        (output / (name + ".hda")).write_bytes(hda)
        receipt.append({"id": entry["id"], "PNG_sha256": sha(png_path.read_bytes()), "HDA_sha256": sha(hda), "RGBA_sha256": entry["RGBA_sha256"]})
    (output / "rebuild-receipt.json").write_text(json.dumps({"pass": True, "generated_masters_only": True, "read_canonical_outputs": False, "Pillow": pillow_version, "outputs": receipt}, indent=2) + "\n")
    print("PASS: five exact PNG/RGBA/HDR1 outputs, generated-master inputs only")


if __name__ == "__main__":
    main()
