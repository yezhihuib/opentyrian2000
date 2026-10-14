#!/usr/bin/env python3
"""Offline mixer contracts: real callbacks/LDS/PCM renderer, no SDL audio device.

The historical callback and play_song bodies come directly from --baseline-ref
(default the immutable pre-MP3 source tree). The production PCM render body is extracted verbatim into the
same translation unit so this suite does not need a decoder, MP3 fixture, SDL
runtime library, or actual audio device. Preparation and OPL are deterministic
fakes; decoder/file/resampling behavior belongs in the decoder test suite.

Run after sourcing a dependency environment providing SDL2 headers:
    python3 prototype/test-external-music-mixer.py
Use --sanitize to run the finite harness with ASan and UBSan as well.
LeakSanitizer is off by default because ptrace-based sandboxes cannot run it;
set ASAN_OPTIONS=detect_leaks=1:halt_on_error=1 on a supported host to enable it.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import shlex
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BASELINE_TREE = "4383e1b75248e7ed0910e89f8c0db05dec8d4281"


def function(text: str, name: str) -> str:
    """Extract one C function definition, preserving its original source."""
    pattern = re.compile(r"^[^\n;{}]*\b" + re.escape(name) + r"\s*\([^;{}]*?\)\s*(?://[^\n]*)?\s*\{", re.M)
    matches = list(pattern.finditer(text))
    if len(matches) != 1:
        raise AssertionError(f"Expected one {name} definition, found {len(matches)}")
    begin = matches[0].start()
    opening = text.index("{", matches[0].start(), matches[0].end())
    # C comments/strings cannot supply structural braces.
    tokens = re.compile(r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|[{}]', re.S)
    depth = 0
    for token in tokens.finditer(text, opening):
        if token.group() == "{":
            depth += 1
        elif token.group() == "}":
            depth -= 1
            if depth == 0:
                return text[begin:token.end()]
    raise AssertionError(f"Unclosed {name}")


def without_comments(text: str) -> str:
    return re.sub(r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"', "", text, flags=re.S)


def calls(text: str) -> set[str]:
    return set(re.findall(r"\b([A-Za-z_]\w*)\s*\(", without_comments(text)))


def verify_source(baseline: str, historical_lds: str) -> tuple[str, str, str]:
    current = (ROOT / "src/loudness.c").read_text()
    lds = (ROOT / "src/lds_play.c").read_text()
    external = (ROOT / "src/external_music.c").read_text()
    callback = function(current, "audioCallback")
    renderer = function(external, "external_music_render")
    accessor = function(lds, "lds_get_master_volume_q8")
    permitted = {
        "audioCallback", "if", "while", "for", "sizeof", "MIN", "MAX",
        "FIXED_TO_INT", "lds_update", "opl_update", "external_music_render",
        "lds_get_master_volume_q8",
    }
    assert calls(callback) <= permitted, f"Unreviewed callback calls: {calls(callback) - permitted}"
    permitted_render = {"external_music_render", "if", "for", "sizeof", "memset"}
    assert calls(renderer) <= permitted_render, f"Unreviewed renderer calls: {calls(renderer) - permitted_render}"
    assert calls(accessor) <= {"lds_get_master_volume_q8"}, "LDS accessor must be read-only arithmetic"
    assert callback.index("opl_update(") < callback.index("external_music_render("), "OPL must advance before PCM replacement"
    # The actual LDS scheduler is compiled in the harness. Also establish that
    # adding the read-only gain accessor did not alter the historical engine.
    assert lds.replace(accessor + "\n\n", "", 1) == historical_lds, "LDS engine changed beyond the gain accessor"
    for name in ("init_audio", "load_song", "stop_song", "fade_song", "set_volume", "multiSamplePlay"):
        assert function(current, name) == function(baseline, name), f"Historical {name} changed"
    old_callback = function(baseline, "audioCallback").replace("audioCallback(", "originalAudioCallback(", 1)
    old_play = function(baseline, "play_song").replace("play_song(", "originalPlaySong(", 1)
    print("PASS source: callback/renderer have no IO, allocation, free, decoder, or new synchronization calls", flush=True)
    print("PASS source: original LDS engine and unaffected mixer controls are unchanged", flush=True)
    return old_callback, old_play, renderer


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-ref", default=BASELINE_TREE, help="Git revision/tree before the external-music patch")
    parser.add_argument("--sanitize", action="store_true", help="Run ASan/UBSan in addition to the plain binary")
    args = parser.parse_args()
    baseline = subprocess.check_output(["git", "show", f"{args.baseline_ref}:src/loudness.c"], cwd=ROOT, text=True)
    historical_lds = subprocess.check_output(["git", "show", f"{args.baseline_ref}:src/lds_play.c"], cwd=ROOT, text=True)
    old_callback, old_play, renderer = verify_source(baseline, historical_lds)
    cflags = shlex.split(os.environ.get("SDL_CFLAGS", ""))
    if not cflags:
        cflags = shlex.split(subprocess.check_output(["pkg-config", "--cflags", "sdl2"], text=True))
    compiler = shlex.split(os.environ.get("CC", "cc"))
    with tempfile.TemporaryDirectory(prefix="opentyrian-mixer-test-") as directory:
        temp = Path(directory)
        (temp / "mixer-generated-bodies.h").write_text("/* Generated from actual production and historical source. */\n" + old_callback + "\n\n" + old_play + "\n\n" + renderer + "\n")
        common = compiler + ["-std=c99", "-O1", "-g", "-Wall", "-Wextra", "-Werror", "-ffunction-sections", "-fdata-sections"] + cflags + ["-I", str(temp), "-I", str(ROOT / "src"), str(ROOT / "prototype/test-external-music-mixer.c"), "-Wl,--gc-sections", "-lm"]
        configurations = [("plain", [])]
        if args.sanitize:
            configurations.append(("asan-ubsan", ["-fsanitize=address,undefined", "-fno-omit-frame-pointer", "-fno-pie", "-no-pie"]))
        for label, flags in configurations:
            binary = temp / f"mixer-{label}"
            subprocess.run(common + flags + ["-o", str(binary)], cwd=ROOT, check=True)
            env = dict(os.environ)
            env.setdefault("ASAN_OPTIONS", "detect_leaks=0:halt_on_error=1")
            env.setdefault("UBSAN_OPTIONS", "halt_on_error=1:print_stacktrace=1")
            subprocess.run([str(binary)], cwd=ROOT, env=env, check=True, timeout=60)
            print(f"PASS {label}: direct callback harness, no audio device opened", flush=True)


if __name__ == "__main__":
    main()
