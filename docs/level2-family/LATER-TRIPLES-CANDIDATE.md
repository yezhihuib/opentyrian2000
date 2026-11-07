# Optional later 132 triple origins

This default-off candidate ports the finite triple275 origin table from public
`experimental/late-level/sources/03c5968bda89ae17/triple275_family_mirror.inc`.
It reuses six existing public newshs images (153/155/157/159/161/163). It adds no
art or manifest entries and enables no other late family. It is not an accepted
whole-level visual release.

## Explicit selection

```sh
python3 scripts/launch_level2_family.py --data /path/to/game-data \
  --hd --later-triples --check-only
```

`--later-triples` requires `--hd` and adds only `TRIPLE275_LATER_132_ENABLE=1`.
Without it, inherited requests are stripped. The original event 150 retains its
existing `TRIPLE275_FAMILY_CANVAS_ENABLE` switch. Later lamps, embers and private
red vents remain independent options. Only the separately built level2-family
candidate changes; the canonical build and late-level archive are untouched.

## Exact scope and consumption

Scope remains episode 1, physical level 2 ASTEROID2, main script section 6,
map D/shapes Z, ordinary non-demo/non-probe play, with existing mode exclusions.
This is a branch after TYRIAN, not every campaign's mandatory second stage.

The original zero-based origin is `(150,1224,114)` (event index, time, X).
The 132 additions start at `(293,2540,258)` and end at `(478,4640,258)`;
the full sorted table is in `triple275_family_mirror.inc`. Every selected row
is case 6, record 275, with remaining event fields zero. The complete native
731-event stream is sealed at actual level load against FNV64
`0xa6df39659b2d348d`, before legitimate native event mutations. Selected rows
are checked again at runtime admission.

A **133-byte** consumption array uses bounded ordinals 0–132, never raw event
indexes or shifts past the width of a machine word. Allocation failure still
consumes an origin; renderer or bank changes cannot re-arm it. Only a true
level load clears consumption. Original-only mode 2, later-only mode 4 and
combined mode 6 are pinned at load. Changes of mode, root, scene or lifetime
cannot expand an existing lease. Exact source, palette, actor, geometry and
ordered native writer guards are retained. No gameplay fields are modified.

## Evidence and limits

Private offline audit confirmed all 133 full rows and that they are the complete
case-6 record-275 set in the matching 731-event stream. All six reused image
SHA256/size manifest entries and runtime payload hashes match. No original
event table is published in this source batch.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_triple275_later132.py -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_level2_family_release.py -v
```

Tests compile actual origin/mode/row predicates and event-begin admission
(scope/log/fault use stubs). They cover every origin's consumption after failed
allocation, disabled origins, mode pinning, ordinal boundaries and all eight
lamp/ember/triple launcher combinations. The optional raw-event-file argument
to the generated `harness()` program checks the real stream, all 133 rows,
last ordinal 132's admission/rejection on reuse, unrelated-row corruption,
wrong count and wrong-pointer rejection. That private real-stream check passed.

No game was run for this extension. Later scene positioning, clipping, occlusion,
blend behavior, normal play, sound, save/load and performance remain unverified.
