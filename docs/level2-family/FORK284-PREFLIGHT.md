# Fork284 offline input preflight

This tool is **only a read-only checker**, not a renderer or launch flag.
It leaves the existing 52-file family manifest and runtime unchanged. A separate
[default-off integration candidate](FORK284-CANDIDATE.md) now supplies sparse
ownership and lifetime hooks; this checker does not activate or qualify it.

```sh
python3 scripts/preflight_fork284.py --data /path/to/original/game-data
```

The script can be invoked by absolute path from any working directory. `--data`
is resolved from the caller's directory; the public asset is resolved relative
to the script's repository. It reads only `tyrian1.lvl` and the public
`assets/hd/packs/asteroid1-ten-v1/enemy-newshd-121-8.hda`. It writes JSON to stdout,
creates no files and starts no game. Successful validation exits 0. Missing,
truncated, incompatible or damaged input exits 1 with a JSON error. Command-line
usage errors use argparse's usual nonzero exit.

## What is checked

- A bounded read (16 MiB maximum) and complete, ordered, in-file signed offset
  table. Physical level 2 uses native `lvlPos[(2-1)*2]`, with the following
  offset as its event-section boundary.
- Exact map D/shapes Z and initial map X values 1/1/1; a bounded enemy-list skip,
  event count 731 and all 8041 event bytes inside the section.
- Full event-stream FNV64 `a6df39659b2d348d`, followed by all fields of the four
  selected case-7 record-284 rows. Their **one-based eventLoc numbers are
  12–15**, not zero-based indexes. No additional case-6/7 record-284 origin is
  admitted. This identifies the known E1 physical-2 ASTEROID2 input; it does
  not parse the campaign script or prove the current runtime scene.
- Exact asset length 172060, HDR1 header `(1080121,8,24,28,0,0)`, SHA256
  `65609c1c9d7cc981faecc914ada8e1100c550047733967ba7ae4b3635fdd1dad`,
  and payload FNV64 `56eb78103f545e7e`.
- Counts of transparent, partial-alpha and opaque pixels, without exporting
  image pixels or original event data. The asset is intentionally not opaque.

Output reports hashes, match status and the four origin numbers, not the raw
event table. No original game data is included. This is **not** a complete level
parser: map lookup/payload validity, later sections, enemy/sprite source-bank
pins, runtime draw order, appearance, sound, saves and gameplay are not checked.
A PASS cannot grant or claim a runtime HD lease.

## Verification

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_fork284_preflight.py -v
```

Tests use a synthetic offset/enemy/event structure, explicitly rejected by the
production stream pin. A test-only pin substitution exercises the positive
parser/report path; no CLI pin override exists. Other cases cover bad offsets,
truncation, abnormal counts, changed stream/row bytes, damaged assets, bounded
reads, caller-independent asset lookup, JSON errors and no file changes.
The real private extracted `tyrian1.lvl` also passed the unmodified checker.
No game was run.
