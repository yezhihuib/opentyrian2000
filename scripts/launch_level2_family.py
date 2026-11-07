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
    "TRIPLE275_", "EMBER269_", "NATIVE_WRITER_", "OLD_HD_SAMPLE_",
    "ASSET_DEBUG_", "GAME_PROBE_",
)
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
