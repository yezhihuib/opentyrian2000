#!/usr/bin/env python3
"""Build/run pure synthetic cap tests against an explicitly selected source tree."""
from pathlib import Path
import argparse
import os
import shlex
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--src", type=Path, required=True,
                        help="Directory containing world_material{,_fast}.{c,h}")
    parser.add_argument("--output", type=Path, required=True,
                        help="Fresh output directory outside --src")
    parser.add_argument("--sanitize", action="store_true",
                        help="Enable AddressSanitizer and UndefinedBehaviorSanitizer")
    args = parser.parse_args()
    src = args.src.resolve(strict=True)
    output = args.output.resolve()
    required = [src / f"world_material{suffix}.{extension}"
                for suffix in ("", "_fast") for extension in ("c", "h")]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        parser.error("missing source inputs: " + ", ".join(missing))
    if output.exists() or args.output.is_symlink():
        parser.error("--output must be a fresh directory")
    if output == src or output in src.parents or src in output.parents:
        parser.error("--output must be outside --src and must not contain --src")

    output.mkdir(parents=True)
    here = Path(__file__).resolve().parent
    compiler = shlex.split(os.environ.get("CC", "cc"))
    flags = ["-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-I" + str(src)]
    if args.sanitize:
        flags += ["-O1", "-g", "-fsanitize=address,undefined", "-fno-omit-frame-pointer"]
    wrappers = ["-Wl,--wrap=" + name
                for name in ("malloc", "calloc", "realloc", "aligned_alloc")]
    binary = output / "test-cap-material"
    command = compiler + flags + [str(src / "world_material.c"),
                                  str(src / "world_material_fast.c"),
                                  str(here / "test_cap_material.c")] + wrappers + ["-o", str(binary)]
    print("Building:", shlex.join(command), flush=True)
    subprocess.run(command, check=True)
    env = os.environ.copy()
    if args.sanitize:
        # LeakSanitizer cannot run under ptrace-based execution sandboxes.
        # The production paths have separate allocation traps in both modes.
        # An unsandboxed caller may explicitly opt in with ASAN_OPTIONS.
        env.setdefault("ASAN_OPTIONS", "detect_leaks=0:halt_on_error=1")
        env.setdefault("UBSAN_OPTIONS", "halt_on_error=1:print_stacktrace=1")
    subprocess.run([str(binary)], check=True, env=env)
    print("PASS standalone synthetic cap tests; no SDL, pack/media generation, game process, or capture")


if __name__ == "__main__":
    main()
