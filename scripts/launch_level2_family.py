#!/usr/bin/env python3
"""Verify and optionally launch the opt-in level-2 family build.

Importing this module and check-only mode never execute a game or write files.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent.parent
MANIFEST = Path("assets/hd/level2-family-v1/MANIFEST.json")
FAMILY_ROOT = Path("assets/hd/level2-family-v1")
REUSED_ROOT = Path("assets/hd/packs/asteroid1-ten-v1")
CONTROL_PREFIXES = (
    "BUILDING313_", "B313_", "LAMP272_", "GRAY325_", "LONGFACE573_",
    "TRIPLE275_", "EMBER269_", "FORK284_", "TURRET273_", "LINKED338_", "LINKED_PROP287288_", "LATE_ACTORS_", "NORMAL270_", "NATIVE_WRITER_", "OLD_HD_SAMPLE_",
    "ASSET_DEBUG_", "GAME_PROBE_",
)
TURRET273_SHA256 = {169: '0650b5ef93849d23b757eb76c9ccbcc222dbdfbed7e23f872cf0990873543639', 193: 'b09b304729ccb04ba569ddc0383d9934ac7de562c5402494b9c3c8db451d3b4c', 195: 'ba9005d5a19616a1425b04164c3b3e59193f1db8e01bca0805ac3382dfef1652', 197: 'aa3f8b90ab19c1160647be14264df73678b763064cdc8d8abc22aba2ecfe347a', 199: '1812680982e5b22242cedfb1c7d378a4c53073d548e27dbbd7f0c63250c1ada2', 201: 'bae10e8a4dce967a6d19868dbb527fc6ff2d0a4be5a7a6e3256ae0a56b6f9c31', 203: 'dae8ebc5b00ae7815432827ba352998fa4d387a77e327dea790bdf02523bb5fc', 205: 'dc8ceeba073abd35e508b1004b77c022d298027fd01f99accc563640b20ebac4', 207: '48da35b8f1240d938296c9fdfeb3118335f8dc8faa246f731a722bf445874071'}
LINKED338_SHA256 = {115: 'f3990602fa3c9199cf15c85e62d96954d414d08cea7171c1ba07172c9f44322c', 117: '951364ebd06145962cde9e6d0f676e547bffc36777297d98a4f9a3ce349d2519', 119: '09b0bd98f62a7c5ee16114cbd71c2a09e34a03a17aca23387ce5033fe0930c0e', 229: '74efdec8ff95e20ab7c47f2aa8ec4e40a963551da6396392d04d4c6e0be7b89c', 231: 'c97be4c67e41aa129be53aec9cdbe31b23f9b93b5cc657be69f80556d4c26c1a', 267: '1eb0fe96fd5c86a967fa4bc73ab97bac2d9cc360cf8db570b294d12951984678', 269: '7ef0d2edc92cec157b49d7346dada16e430dc9942276b4bfaa0968c82aa9aaaf'}
LINKED_PROPS_SHA256 = {245: '71f5abb6edef89f4f151eca6aec54d5d6e517e17db48875d1bfcc2672b283f5e', 281: '0669e8e3ea3a50752f2e645dd72c6ae5ad1bc5af8931cc3b039fd12a43a07b23', 283: '9e8d91e67d142ec4351001aebe9dc33fb70dcc91123dbe353ce84f6bf5b8a658'}
LATE282285_SHA256 = {'enemy-newshd-79-8.hda': '58ec2fbe2fb605cef591dda33e373283dd35974e9e160cff0c4f3509c1dba298', 'enemy-newshd-81-8.hda': 'a657626679cbe322680394f4489443efed4532548ead118f4794699b9ec1cb56', 'enemy-newshd-83-8.hda': '3f103041cc41eaa52d53b8f06d53056204a7f76ed38d56eca63064b4d354c901', 'enemy-newshd-157-8.hda': '4cbf65176d6536c148a4f7a1b8f5a54e565bca47fae24a82a9c0e8345c1c0ebd', 'enemy-newshd-159-8.hda': 'f19c34174c2a17a0c2386de06c4ba497996122122dc67c50bd9fd8677cb7c07e', 'enemy-newshd-161-8.hda': 'ad178825c48d9a2e0946c848e2c38c747a391b876ef8b4e8944295654b01e5b5'}
NORMAL270_SHA256 = {'enemy-newshd-127-8.hda': '0fe44c1bc3a533f0f771a45705df0c07f66d662f51c0beb67fcae8ec7c30ffb5', 'enemy-newshd-129-8.hda': 'fbdca2d2609801fa3dd89c0f3458c981f3c515f9de2f25f07111f8111a3d3b0b', 'enemy-newshd-131-8.hda': 'd6629214cb77a7bebf3b4753caa473d6653048bfa548147e61fb1c0e0b5bfb8f'}
PUBLIC_CANDIDATE_FLAGS = ("later_lamps", "later_embers", "later_triples", "fork284", "turret273", "linked338", "linked_props", "late282285", "normal270")
CONTROL_NAMES = {"TYRIAN_CYAN_BORROW_TRACE"}
HD_ENABLE_KEYS = (
    "BUILDING313_FAMILY_OBSERVER_ENABLE",
    "BUILDING313_FAMILY_CANVAS_ENABLE",
    "BUILDING313_FAMILY_GROUND_ENABLE",
    "BUILDING313_FAMILY_CLIFF_ENABLE",
    "BUILDING313_FAMILY_CORNER_ENABLE",
    "BUILDING313_TERRAIN_CONTINUITY_ENABLE",
    "BUILDING313_FAMILY_STATIC340_ENABLE",
    "LAMP272_FAMILY_CANVAS_ENABLE",
    "GRAY325_FAMILY_CANVAS_ENABLE",
    "LONGFACE573_FAMILY_CANVAS_ENABLE",
    "TRIPLE275_FAMILY_CANVAS_ENABLE",
    "BUILDING313_TERRAIN_BLEND_RETIRE_ENABLE",
    "LAMP272_LATER_THREE_ENABLE",
    "LAMP272_MIDDLE_PAIR_ENABLE",
    "EMBER269_FAMILY_CANVAS_ENABLE",
)


def controlled_name(name):
    return name.startswith(CONTROL_PREFIXES) or name in CONTROL_NAMES


def expected_asset_paths():
    paths = {str(FAMILY_ROOT / "building" / f"phase{n}.argb32le") for n in range(3)}
    for bank, bases in (("newshd", (155, 163, 165, 167)),
                        ("newshp", (123, 125, 127, 129))):
        paths.update(str(FAMILY_ROOT / "longface" / f"enemy-{bank}-{n}-8.hda") for n in bases)
    for bank, bases in (("newshs", (11, 125, 277, 153, 155, 157, 159, 161, 163, 229, 231, 233, 235)),
                        ("newshd", (267, 269, 271, 273))):
        paths.update(str(REUSED_ROOT / f"enemy-{bank}-{n}-8.hda") for n in bases)
    ground = (372, 380, 390, 367, 368, 376, 378, 386, 387, 388)
    cliff = (361, 362, 363, 364, 365, 371, 373, 374, 375, 381, 382, 383)
    paths.update(f"assets/hd/current-terrain23/terrain-shapesz-{n}-8.hda"
                 for n in ground + cliff + (366,))
    paths.add("assets/hd/current-terrain24/terrain-shapesz-340-8.hda")
    return paths


def verify_assets(root=ROOT):
    """Read only the exact committed family inputs, including dormant damaged art."""
    manifest_path = root / MANIFEST
    document = json.loads(manifest_path.read_text(encoding="utf-8"))
    if document.get("schema") != "opentyrian-level2-family-assets-v1":
        raise ValueError("Unsupported family asset manifest")
    entries = document.get("files", [])
    paths = [entry["path"] for entry in entries]
    if len(paths) != len(set(paths)) or set(paths) != expected_asset_paths():
        raise ValueError("Family asset manifest does not contain the exact 52 required files")
    for entry in entries:
        relative = entry["path"]
        path = root / relative
        if not path.is_file():
            raise ValueError("Missing family asset: " + relative)
        digest = hashlib.sha256()
        with path.open("rb") as source:
            for block in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(block)
        if digest.hexdigest() != entry["sha256"]:
            raise ValueError("Family asset SHA-256 mismatch: " + relative)
    return len(entries)


def hd_environment(root):
    values = dict.fromkeys(HD_ENABLE_KEYS, "1")
    values.update({f"BUILDING313_V6_PHASE{n}": str(root / FAMILY_ROOT / "building" / f"phase{n}.argb32le")
                   for n in range(3)})
    for family in ("LAMP272", "GRAY325", "TRIPLE275", "EMBER269"):
        values[family + "_FAMILY_ASSET_DIR"] = str(root / REUSED_ROOT)
    values["LONGFACE573_FAMILY_ASSET_DIR"] = str(root / FAMILY_ROOT / "longface")
    return values


REDVENT_PINS = {339: "5eb2706b6dac539478274343c83739071839a8d30cd87bbd8b21046abc39cf29",
                348: "0cc51907884a740a339ceffa10a6c421d648eb6f4cf11982d5e3ae06ac0d5bff"}


def verify_redvent_pair(directory):
    directory = Path(directory).expanduser().resolve()
    if not directory.is_dir():
        raise ValueError("--redvent-pair must name the private candidate directory")
    for tile, expected in REDVENT_PINS.items():
        path = directory / f"terrain-shapesz-{tile}-8.hda"
        if not path.is_file() or path.stat().st_size != 172060:
            raise ValueError("Missing or wrong-size red-vent asset: " + path.name)
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError("Changed red-vent asset: " + path.name)
    return directory


def build_plan(args, inherited=None, root=ROOT):
    """Return a public plan and the process environment without changing either CWD or files."""
    # Copy the namespace: public preset expansion must not mutate caller input.
    args = argparse.Namespace(**vars(args))
    public_candidates = getattr(args, "public_candidates", False)
    if public_candidates:
        if not args.hd:
            raise ValueError("--public-candidates requires explicit --hd")
        if getattr(args, "redvent_pair", None):
            raise ValueError("--public-candidates excludes private --redvent-pair")
        for flag in PUBLIC_CANDIDATE_FLAGS:
            setattr(args, flag, True)
    root = root.resolve()
    data = Path(args.data).expanduser().resolve()
    binary = (Path(args.binary).expanduser() if args.binary else root / "opentyrian2000-family").resolve()
    profile = (Path(args.profile).expanduser() if args.profile else root / ".level2-family-profile").resolve()
    if not data.is_dir():
        raise ValueError("--data must name an existing game-data directory")
    if not binary.is_file() or not os.access(binary, os.X_OK):
        raise ValueError("Game binary is missing or not executable; build it first or use --binary: " + str(binary))
    if profile == root or profile == data:
        raise ValueError("--profile must be a separate directory, not the repository or game-data directory")
    # The game stores its user-directory path in a 500-byte buffer.
    config = profile / "config"
    if len(os.fsencode(config / "opentyrian2000")) >= 500:
        raise ValueError("Profile path is too long for the game's configuration-directory buffer")
    checked = verify_assets(root)
    inherited = os.environ if inherited is None else inherited
    environment = {key: value for key, value in inherited.items() if not controlled_name(key)}
    overrides = {
        "HOME": str(profile), "XDG_CONFIG_HOME": str(config),
        "XDG_DATA_HOME": str(profile / "data"), "XDG_CACHE_HOME": str(profile / "cache"),
        "XDG_STATE_HOME": str(profile / "state"),
    }
    family = hd_environment(root) if args.hd else {}
    later_lamps = getattr(args, "later_lamps", False)
    if later_lamps:
        if not args.hd:
            raise ValueError("--later-lamps requires --hd; it cannot enable the parent itself")
        family["LAMP272_LATER_SIXTEEN_ENABLE"] = "1"
    later_embers = getattr(args, "later_embers", False)
    if later_embers:
        if not args.hd:
            raise ValueError("--later-embers requires --hd; it cannot enable the parent itself")
        family["EMBER269_LATER_FIVE_ENABLE"] = "1"
    later_triples = getattr(args, "later_triples", False)
    if later_triples:
        if not args.hd:
            raise ValueError("--later-triples requires --hd; it cannot enable the parent itself")
        family["TRIPLE275_LATER_132_ENABLE"] = "1"
    fork284 = getattr(args, "fork284", False)
    if fork284:
        if not args.hd:
            raise ValueError("--fork284 requires --hd; it cannot enable the parent itself")
        asset = root / REUSED_ROOT / "enemy-newshd-121-8.hda"
        if asset.stat().st_size != 172060 or hashlib.sha256(asset.read_bytes()).hexdigest() != "65609c1c9d7cc981faecc914ada8e1100c550047733967ba7ae4b3635fdd1dad":
            raise ValueError("Changed Fork284 asset")
        family.update({"FORK284_ENABLE": "1", "FORK284_ASSET_DIR": str(root / REUSED_ROOT)})
    turret273 = getattr(args, "turret273", False)
    if turret273:
        if not args.hd:
            raise ValueError("--turret273 requires --hd; it cannot enable the parent itself")
        for base, digest in TURRET273_SHA256.items():
            asset = root / REUSED_ROOT / f"enemy-newshd-{base}-8.hda"
            if asset.stat().st_size != 172060 or hashlib.sha256(asset.read_bytes()).hexdigest() != digest:
                raise ValueError("Changed Turret273 asset: " + asset.name)
        family.update({"TURRET273_COMBAT_ENABLE": "1", "TURRET273_BODY_ASSET_DIR": str(root / REUSED_ROOT)})
    linked338 = getattr(args, "linked338", False)
    if linked338:
        if not args.hd:
            raise ValueError("--linked338 requires --hd; it cannot enable the parent itself")
        for base, digest in LINKED338_SHA256.items():
            asset = root / REUSED_ROOT / f"enemy-newshp-{base}-8.hda"
            if asset.stat().st_size != 172060 or hashlib.sha256(asset.read_bytes()).hexdigest() != digest:
                raise ValueError("Changed Linked338 asset: " + asset.name)
        family.update({"LINKED338_NORMAL_ENABLE": "1", "LINKED338_NORMAL_ASSET_DIR": str(root / REUSED_ROOT)})
    linked_props = getattr(args, "linked_props", False)
    if linked_props:
        if not args.hd:
            raise ValueError("--linked-props requires --hd; it cannot enable the parent itself")
        for base, digest in LINKED_PROPS_SHA256.items():
            asset = root / REUSED_ROOT / f"enemy-newshd-{base}-8.hda"
            if asset.stat().st_size != 172060 or hashlib.sha256(asset.read_bytes()).hexdigest() != digest:
                raise ValueError("Changed linked-props asset: " + asset.name)
        family.update({"LINKED_PROP287288_ENABLE": "1", "LINKED_PROP287288_ASSET_DIR": str(root / REUSED_ROOT)})
    late282285 = getattr(args, "late282285", False)
    if late282285:
        if not args.hd:
            raise ValueError("--late282285 requires --hd")
        for name, digest in LATE282285_SHA256.items():
            asset = root / REUSED_ROOT / name
            if asset.stat().st_size != 172060 or hashlib.sha256(asset.read_bytes()).hexdigest() != digest:
                raise ValueError("Changed late282285 asset: " + name)
        family.update({"LATE_ACTORS_ENABLE": "1", "LATE_ACTORS_ASSET_DIR": str(root / REUSED_ROOT)})
    normal270 = bool(public_candidates)
    if normal270:
        if not args.hd:
            raise ValueError("normal270 public candidate requires --hd")
        for name, digest in NORMAL270_SHA256.items():
            asset = root / REUSED_ROOT / name
            if asset.stat().st_size != 172060 or hashlib.sha256(asset.read_bytes()).hexdigest() != digest:
                raise ValueError("Changed normal270 asset: " + name)
        family.update({"NORMAL270_ENABLE": "1", "NORMAL270_ASSET_DIR": str(root / REUSED_ROOT)})
    redvent = getattr(args, "redvent_pair", None)
    if redvent:
        if not args.hd:
            raise ValueError("--redvent-pair requires --hd; it cannot enable the parent itself")
        directory = verify_redvent_pair(redvent)
        family.update({"BUILDING313_REDVENT_PAIR_ENABLE": "1",
                       "BUILDING313_REDVENT_PAIR_ASSET_DIR": str(directory)})
    overrides.update(family)
    environment.update(overrides)
    plan = {
        "status": "CHECK_ONLY" if not args.launch else "LAUNCH_PLAN",
        "hd_enabled": bool(args.hd), "family_environment_count": len(family),
        "argv": [str(binary), "--data=" + str(data)], "cwd": str(root),
        "profile": str(profile), "save_directory": str(config / "opentyrian2000"),
        "environment_overrides": overrides,
        "inherited_controls_removed": sorted(key for key in inherited if controlled_name(key)),
        "assets_sha256_verified": checked,
        "public_candidates_enabled": bool(public_candidates),
        "public_candidate_flags": list(PUBLIC_CANDIDATE_FLAGS) if public_candidates else [],
        "qualification": "Experimental offline candidate; actual combined scene/gameplay is unverified.",
        "normal270_enabled": bool(normal270),
        "normal270_assets_sha256_verified": 3 if normal270 else 0,
        "normal270_scope": "events244/245 only; curLoc<1960 and eventLoc<=259; body only" if normal270 else None,
        "late282285_enabled": bool(late282285),
        "late282285_assets_sha256_verified": 6 if late282285 else 0,
        "linked_props_enabled": bool(linked_props),
        "linked_props_assets_sha256_verified": 3 if linked_props else 0,
        "linked338_enabled": bool(linked338),
        "linked338_assets_sha256_verified": 7 if linked338 else 0,
        "turret273_enabled": bool(turret273),
        "turret273_assets_sha256_verified": 9 if turret273 else 0,
        "fork284_enabled": bool(fork284),
        "fork284_assets_sha256_verified": 1 if fork284 else 0,
        "later_triples_enabled": bool(later_triples),
        "later_embers_enabled": bool(later_embers),
        "later_lamps_enabled": bool(later_lamps),
        "redvent_pair_enabled": bool(redvent), "redvent_assets_sha256_verified": 2 if redvent else 0,
        "game_data_check": "Directory exists; original game-file validity is not verified.",
        "binary_check": "Executable file exists; build options and gameplay are not verified.",
        "profile_created": False, "game_started": False,
        "stdin": "inherited; no synthetic input", "game_timeout": None,
        "diagnostic_output_directory": str(root),
    }
    return plan, environment


def parser():
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--data", required=True, help="Your existing original game-data directory; no data is bundled")
    result.add_argument("--binary", help="Executable to use (default: repository/opentyrian2000-family)")
    result.add_argument("--profile", help="Separate profile directory (default: repository/.level2-family-profile)")
    result.add_argument("--hd", action="store_true", help="Enable the 23 fixed family environment settings")
    result.add_argument("--redvent-pair", help="Opt-in private 339/348 candidate directory; requires --hd and matching assets; not gameplay-validated")
    result.add_argument("--later-lamps", action="store_true", help="Opt in to 16 exact later lamp origins using existing public art; requires --hd, not scene-qualified")
    result.add_argument("--later-embers", action="store_true", help="Opt in to 5 exact later ember origins using existing public art; requires --hd, not scene-qualified")
    result.add_argument("--later-triples", action="store_true", help="Opt in to 132 exact later triple origins using existing public art; requires --hd, not scene-qualified")
    result.add_argument("--fork284", action="store_true", help="Opt in to four exact sparse Fork284 origins; requires --hd, not scene-qualified")
    result.add_argument("--turret273", action="store_true", help="Opt in to normal nine-image turret273 body at two exact origins; requires --hd, not scene-qualified")
    result.add_argument("--linked338", action="store_true", help="Opt in to normal linked338-342 group; seven public images, four exact events; requires --hd, not scene-qualified")
    result.add_argument("--linked-props", action="store_true", help="Opt in to six exact independent linked props287/288 origins; requires --hd, not scene-qualified")
    result.add_argument("--late282285", action="store_true", help="Opt in to eight original282/285 bodies; excludes283 and projectiles; requires --hd")
    result.add_argument("--public-candidates", action="store_true", help="Experimental combination of all supported public extensions; requires explicit --hd; excludes private redvent")
    mode = result.add_mutually_exclusive_group()
    mode.add_argument("--launch", action="store_true", help="Actually start the game with normal input and no timeout")
    mode.add_argument("--check-only", "--dry-run", action="store_true", help="Only check and print the plan (the default)")
    return result


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        plan, environment = build_plan(args)
        if not args.launch:
            print(json.dumps(plan, indent=2, sort_keys=True))
            return 0
        if os.name != "posix":
            raise ValueError("This launcher currently supports POSIX launches only; Windows profile isolation is not implemented")
        profile = Path(plan["profile"])
        profile.mkdir(mode=0o700, parents=True, exist_ok=True)
        for name in ("config", "data", "cache", "state"):
            (profile / name).mkdir(mode=0o700, exist_ok=True)
        os.chdir(plan["cwd"])
        # Keep the real terminal/display and ordinary game lifecycle. Never replay input.
        os.execvpe(plan["argv"][0], plan["argv"], environment)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print("level2-family: " + str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
