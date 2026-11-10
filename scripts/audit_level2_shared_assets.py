#!/usr/bin/env python3
"""Read-only shared-art inventory, NOT a level-2 completeness certificate.

Manifest membership means available artwork, not reachability or runtime proof.
No game data is read, no game is launched, and no files are written.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
SOURCE = Path("experimental/level2-family/src")
HUD_NAMES = (
    "gameplay-hud-v1.hda", "gameplay-hud-components-v1.hda",
    "gameplay-hud-fixed-text-v1.hda", "gameplay-hud-font-v1.hda",
    "gameplay-hud-indicators-v1.hda", "gameplay-hud-meters-v2.hda",
)


def category(name):
    if name.startswith(("ship-", "talon-bank-")):
        return "player"
    if name.startswith(("bullet-", "rear-multicannon-", "option-", "protron-shadow-")):
        return "projectiles-and-options"
    if name.startswith(("coin", "gem", "data513-", "rear534-")):
        return "pickups-and-values"
    if name.startswith("explosion-"):
        return "effects"
    return None


def inspect_file(path, digest=None):
    if not path.is_file():
        return "missing"
    data = path.read_bytes()
    if data.startswith(b"version https://git-lfs.github.com/spec/"):
        return "lfs-pointer"
    if digest and hashlib.sha256(data).hexdigest() != digest:
        return "hash-mismatch"
    return "hash-verified" if digest else "present-unverified"


def audit(root=ROOT):
    manifest = json.loads((root / "assets/hd/manifest.json").read_text())
    pack = manifest["default_preview_pack"]
    entries = []
    for name, metadata in sorted(manifest["packs"][pack]["files"].items()):
        group = category(name)
        if group is None:
            continue
        path = Path("assets/hd/packs") / pack / name
        pose = re.fullmatch(r"ship-(229|231|233|235|237)-8.hda", name)
        entries.append({
            "category": group, "file": str(path),
            "identity": metadata["header_u32"][0],
            "resource": inspect_file(root / path, metadata["sha256"]),
            "family_integration": "guarded-five-pose-adapter" if pose else "not-wired",
            "level2_required": "loadout-and-runtime-inventory-needed",
        })
    for name in HUD_NAMES:
        path = Path("assets/hd/shared-ui-v1") / name
        entries.append({"category": "hud", "file": str(path),
                        "resource": inspect_file(root / path),
                        "family_integration": "guarded-static-border" if name == HUD_NAMES[0] else "not-wired" if name == "gameplay-hud-font-v1.hda" else "guarded-dynamic-hud-adapter",
                        "level2_required": "gameplay-hud"})
    # These two resources are actually referenced by the family weapon adapter,
    # not inferred from similarly named legacy projectile art.
    from launch_level2_family import TANK_SHELL_ROOT, TANK_SHELL_SHA256
    for index, digest in sorted(TANK_SHELL_SHA256.items()):
        path = TANK_SHELL_ROOT / f"enemy-tank-shell-{index}-8.hda"
        entries.append({"category": "enemy-projectiles", "file": str(path),
                        "identity": 1220000 + index,
                        "resource": inspect_file(root / path, digest),
                        "family_integration": "guarded-tank194-weapons2-and3",
                        "level2_required": "witnessed-tank194-shot"})
    mirror = (root / SOURCE / "render_mirror.c").read_text()
    guards = {
        "legacy_entity_disabled_in_family": bool(re.search(
            r"bool render_mirror_entity\([^\n]+\)\s*\{\s*if\(render_mirror_family_requested\(\)\)return false;", mirror)),
        "legacy_asset_lookup_disabled_in_family": bool(re.search(
            r"static Asset \*get_asset\([^\n]+\)\s*\{\s*if\(render_mirror_family_requested\(\)\)return NULL;", mirror)),
    }
    return {"schema": "level2-shared-art-inventory-v1", "complete": False,
            "scope": "static existing-art inventory; not an exhaustive level2 draw inventory",
            "source_guards": guards,
            "classification_current": all(guards.values()),
            "entries": entries}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-complete", action="store_true",
                        help="Fail while inventory/adapter/verification gaps remain")
    args = parser.parse_args()
    report = audit()
    print(json.dumps(report, indent=2))
    return 1 if args.require_complete or not report["classification_current"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
