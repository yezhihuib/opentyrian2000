# Talon13 and Rotor8 single-source authoring

`talon` selects exactly 13 existing visual identities, in visual order:
90229, 1090001, 90231, 1090003, 1090004, 1090005, 90233,
1090007, 1090008, 1090009, 90235, 1090011, 90237.
Five original poses (229/231/233/235/237) remain native animation identities;
eight intermediate poses remain display-only, never extra simulation frames.
`rotor` selects exactly eight NEWSH2 composites, identities 1010229 through
1010243 in steps of two. Native types 5 and 11 retain forward/reverse traversal.

Both profiles require single-frame 192×224 straight RGBA PNGs, density 8 and
logical 24×28 geometry. Talon anchor is (5,7); Rotor anchor is (6,7).
These are trusted code policy, not fields a source selection can override.
The bootstrap retains all approved art byte-for-byte and does no resampling.
Together with the existing profiles, the 14 generic authoring profiles cover
exactly all 120 current global registry resources, with no identity overlap.
HUD continues using its separate format-aware authoring workflow. This closes
maintenance-source coverage for existing global families only; paused terrain
and cloud work is not enabled.

Use the common stage/apply/check workflow with `--family talon` or `--family rotor`,
or `scripts/build_current_talon.py` / `scripts/build_current_rotor.py`.
Create a new source file and external selection draft for a new version; do not
change installed selections until apply. Stage must be outside the repository.
Every identity remains independent even when its pixels equal another identity.

Generated current consumers are the content-addressed global resources, registry
and C header, selected package/source inventory and compatibility files under
`assets/hd/current-compat/{talon,rotor}`. Legacy logical names remain
`ship-{pose}-8.hda`, `talon-bank-{visual}-8.hda` and
`enemy-newsh2-{base}-8.hda`. No new legacy RGBA macros are required.
Rebuild the executable after selecting new artwork to consume generated pins.

Neutral Talon 90233 is also the existing SHOP ship-1 resource. SHOP keeps its own
full native record/source/quad proof; Fang remains excluded despite sharing
original graphic233. The existing x−5/y−7 origin must not be offset again.
Battle role qualification, native source/palette fingerprints, quartet order,
filters, clipping, shadow, indexed draws, movement and collision stay unchanged.
Selecting shared art does not authorize new consumers or broaden legacy routes.

Historical packs, original PNGs and frozen receipts remain immutable. Apply is
per-file atomic, not a multi-file crash-safe transaction; inspect and restage on
interruption. Synthetic propagation fixtures are diagnostic, not new approved art.
Current source binding is not a substitute for separate native acceptance.

## Exact coverage boundary at this batch

| Current generic profile | Independent IDs |
|---|---:|
| `talon` | 13 |
| `rotor` | 8 |
| `green` | 11 |
| `shield` | 22 |
| `hitflare` | 7 |
| `white_smoke` | 7 |
| `small_explosion` | 12 |
| `pulse` | 5 |
| `vulcan` | 2 |
| `cash25` | 7 |
| `cash50` | 7 |
| `cash75` | 7 |
| `gem100` | 6 |
| `gem250` | 6 |

Total: **120**, exactly the registry's 120 resources. HUD's six format-specific
resources have a separate source workflow and 12 shared/fallback destinations;
they are not counted as generic registry sprites.

This is **not** “all game materials globally migrated.” The current package still
contains the following HDA filename groups outside these authoring profiles and
the six current HUD resources. Counts below are packaged files, not distinct
semantic resources; density variants and scene-specific legacy rules remain.
No new source selection or runtime grant was introduced for these groups.

| Still outside these current workflows | Packaged HDA files |
|---|---:|
| `bullet` | 42 |
| `data513-bank11` | 12 |
| `enemy-energy` | 7 |
| `enemy-newsh2` | 68 |
| `enemy-newsh4` | 60 |
| `enemy-newshe` | 12 |
| `enemy-tank-shell` | 2 |
| `explosion-newsh6` | 96 |
| `gameplay-hud-storm-label-v1.hda` | 1 |
| `option-frontblaster-bank10` | 1 |
| `option-marlo-bank9` | 1 |
| `option-mint-bank9` | 3 |
| `option-plasma-bank9` | 5 |
| `option-plasma-projectile` | 6 |
| `protron-shadow` | 3 |
| `rear-multicannon-p1-bank8` | 48 |
| `rear534-bank11` | 3 |
| `terrain-shapesz` | 136 |

Total outside these workflows: **506 gameplay HDA files**. This inventory
is derived from `packaging/runtime-assets-v1.json`, excluding destinations named
by the 14 generic compatibility maps and `current-hud-compatibility.json`.
It does not assess other startup/SHOP art, fonts, audio or original indexed data.
Terrain145 and cloud identity/adjacency migration remain explicitly paused;
listing a legacy file here is neither a deletion recommendation nor approval to
migrate its runtime role. Each future family needs its own semantic-source and
consumer audit before “edit once” coverage can be claimed.
