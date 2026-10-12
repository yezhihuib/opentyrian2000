"""Reproduce the finite ground101 sidecar from generated-only source contracts."""
from pathlib import Path
import hashlib
import json
import struct
from PIL import Image

INVENTORY_SHA256 = "e16e4956538b942e3264c860726bdd06392a19e2287048887b4cdb59229affe6"
ATLAS_RGBA_SHA256 = "c5d990f8ca33212c30def6b5777e627132a8ae9a515142987af1d2cfc7d4be45"
FILENAME = "ground101-world-material.g101"
PIXELS = 192 * 224
PAYLOAD_BYTES = 16386048

def sha(data):
    return hashlib.sha256(data).hexdigest()

def fnv64(data):
    """Existing project convention; accidental-corruption checksum, not authentication."""
    value = 14695981039346656037
    for byte in data:
        value = ((value ^ byte) * 1099511628211) & 0xffffffffffffffff
    return value

def checked_path(root, name):
    relative = Path(name)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError("Source path must stay inside the frozen package")
    path = root / relative
    if any(p.is_symlink() for p in [path, *path.parents] if p != root.parent):
        raise ValueError("Source symlinks are not supported")
    path.resolve().relative_to(root.resolve())
    if not path.is_file():
        raise ValueError("Missing source file: " + name)
    return path

def finite_slots():
    terrain = {101: 10, 37: 11, 57: 12, 49: 13, 50: 14,
               321: 19, 322: 20, 331: 21, 332: 22}
    for ids, first in [([99,100,106,107,109,110,118,119,120],201),
                       ([96,97,98,108],227), ([323,324,333,334],237),
                       ([341,342,343,351,352,353],247)]:
        terrain.update({identity: first + i for i, identity in enumerate(ids)})
    terrain.update(dict(zip([36,39,40,46,48,56,58,38,47],
                            [220,221,222,223,224,225,226,235,236])))
    terrain.update({111: 241, 114: 242, 113: 246})
    h2 = {77:6,79:7,115:8,117:9,81:231,83:232,119:233,121:234}
    he = {identity:253+i for i,identity in enumerate([1,3,5,39,41,43,7,9,11,45,47,49])}
    return {201: terrain, 101: h2, 110: he}

def render_header(records, receipt):
    lines = ["/* Generated finite world-material contract; FNV64 detects accidental corruption only. */",
             "#define G101_BUNDLE_RECORD_COUNT 61u",
             "#define G101_BUNDLE_HEADER_BYTES 764u",
             "#define G101_BUNDLE_PAYLOAD_BYTES 16386048u",
             "#define G101_BUNDLE_FILE_BYTES 16386812u",
             "#define G101_BUNDLE_FNV64 UINT64_C(0x"+receipt["fnv64"]+")",
             "static const G101Record g101_records[61]={"]
    fields = ["role","index","slot","base_offset","mask_offset","generated_offset",
              "generated_weight_offset","ground_weight_offset"]
    for record in records:
        lines.append(" {"+",".join(str(record[k]) for k in fields)+"}, /* "+record["name"]+" */")
    lines.append("};")
    return "\n".join(lines)+"\n"

def build_bundle(repo):
    repo = Path(repo).resolve()
    package = repo / "assets/hd/artwork/ground101-world-atlas-v1"
    inventory_path = package / "package-files.json"
    if sha(inventory_path.read_bytes()) != INVENTORY_SHA256:
        raise ValueError("Frozen source inventory mismatch")
    inventory = json.loads(inventory_path.read_text())
    for name, record in inventory["files"].items():
        if sha(checked_path(package, name).read_bytes()) != record["sha256"]:
            raise ValueError("Frozen input hash mismatch: " + name)
    bindings = json.loads((package / "contracts/material-bindings.json").read_text())
    if len(bindings) != 62 or sum(bool(e["changed"]) for e in bindings.values()) != 61:
        raise ValueError("Unexpected finite binding count")

    def decode(record):
        if "constant" in record:
            if record != {"constant": 255} and record != {"constant": 0}:
                raise ValueError("Unexpected constant mask")
            return bytes([record["constant"]]) * PIXELS
        path = checked_path(package, record["path"])
        if sha(path.read_bytes()) != record["file_sha256"]:
            raise ValueError("Input file hash mismatch")
        with Image.open(path) as image:
            if list(image.size) != record["size"] or image.size != (192,224):
                raise ValueError("Unexpected source dimensions")
            if record["decoded_mode"] not in ("L", "RGBA"):
                raise ValueError("Unexpected source mode")
            data = image.convert(record["decoded_mode"]).tobytes()
        if sha(data) != record["decoded_sha256"]:
            raise ValueError("Decoded source hash mismatch")
        return data

    with Image.open(package / "selected/atlas.png") as image:
        if image.size != (768,896):
            raise ValueError("Unexpected atlas dimensions")
        atlas = image.convert("RGBA").tobytes()
    if sha(atlas) != ATLAS_RGBA_SHA256 or any(a != 255 for a in atlas[3::4]):
        raise ValueError("Atlas contract mismatch")
    manifest = json.loads((repo / "assets/hd/manifest.json").read_text())
    selected_pack = repo / "assets/hd/packs" / manifest["default_preview_pack"]
    slots = finite_slots()
    parts = [atlas]
    offset = len(atlas)
    records = []
    for name, entry in sorted(bindings.items()):
        base = decode(entry["base"])
        mask = decode(entry["material_weight"])
        header = entry["header"]
        role, identity = divmod(header[0], 10000)
        if role not in slots or identity not in slots[role]:
            raise ValueError("Unknown material identity")
        expected_header = [role*10000+identity,8,24,28,0 if role==201 else 6,0 if role==201 else 7]
        if header != expected_header or len(base) != PIXELS*4 or len(mask) != PIXELS:
            raise ValueError("Base header or pixel length mismatch")
        hda = b"HDR1" + struct.pack("<6I", *header) + base
        if sha(hda) != entry["source_hda_sha256"] or (selected_pack / (name+".hda")).read_bytes() != hda:
            raise ValueError("Compatible selected-pack source mismatch: " + name)
        if not entry["changed"]:
            if name != "terrain-shapesz-111-8" or any(mask):
                raise ValueError("Unexpected unchanged guard")
            continue
        record = {"name":name,"role":role,"index":identity,"slot":slots[role][identity],
                  "base_offset":offset}
        parts.append(base); offset += len(base)
        record["mask_offset"] = offset
        parts.append(mask); offset += len(mask)
        footer = entry.get("footer")
        if bool(footer) != (role == 201 and identity in (119,120)):
            raise ValueError("Unexpected footer identity")
        for field, key in [("generated_offset","generated_input"),
                           ("generated_weight_offset","generated_weight_input"),
                           ("ground_weight_offset","ground_weight_input")]:
            data = decode(footer[key]) if footer else b""
            record[field] = offset if data else 0
            if data:
                if field != "generated_offset" and any(data[:184*192]):
                    raise ValueError("Footer modifies protected upper rows")
                parts.append(data); offset += len(data)
        records.append(record)
    keys = {(r["role"],r["index"]) for r in records}
    if len(records) != 61 or len(keys) != 61 or offset != PAYLOAD_BYTES:
        raise ValueError("Finite bundle size or identity mismatch")
    header = b"G101AT1\0" + struct.pack("<6I",1,61,768,896,8,offset)
    header += b"".join(struct.pack("<3I",r["role"],r["index"],bool(r["generated_offset"])) for r in records)
    blob = header + b"".join(parts)
    if len(blob) != 16386812:
        raise ValueError("Unexpected bundle size")
    return blob, records, {"file":FILENAME,"sha256":sha(blob),"fnv64":f"{fnv64(blob):016x}",
                           "bytes":len(blob),"payload_bytes":offset,"material_records":61,
                           "parts":[{"file":FILENAME+"."+str(i),"offset":start,"bytes":len(blob[start:start+8388608]),"sha256":sha(blob[start:start+8388608])} for i,start in enumerate(range(0,len(blob),8388608))],
                           "source_inventory_sha256":INVENTORY_SHA256,"atlas_rgba_sha256":ATLAS_RGBA_SHA256,
                           "checksum_purpose":"accidental corruption only; not authentication"}
