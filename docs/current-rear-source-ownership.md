# Rear projectile source ownership

All48 supported runtime outputs have identified source ownership: **46 current
editable outputs and2 intentionally protected historical outputs**. This is not
48 freely editable current outputs. Generated PNG/HDA files, pack copies and
preview/debug exports are not additional editing authorities.

## Current editable sources

Each listed current family has a candidate `stage` / `apply` / `check` workflow.
All listed raws have d4 and d8 outputs; edit the master, not derived copies.

| Master under `authoring-inputs/` | Raw outputs | Outputs | Builder under `scripts/` |
| --- | --- | ---: | --- |
| `rear-p7-current/master-294.svg` |294,295|4|`build_current_rear_p7.py`|
| `rear39-current/master-39.json` |39,40,41|6|`build_current_rear39.py`|
| `rear1-current/master-1.json` |1,2,3,77|8|`build_current_rear1.py`|
| `rear281-current/master-281.json` |281,282,300,301,277,278,296,297,298,299|20|`build_current_rear281.py`|
| `rear-lobes-current/master-203.json` |203,222|4|`build_current_rear_lobes.py`|
| `rear-lobes-current/master-43.json` |43,5|4|`build_current_rear_lobes.py`|

The last two are independent masters with a shared fixed compiler. Shared
payload-header composition verifies all five current families. Source pins,
record/phase eligibility, anchors and canvas constraints remain separately fixed.
See each `docs/current-*-authoring.md` guide for candidate requirements.

## Protected historical182/183

- Rear182 d8 derives directly from frozen
  `assets/hd/artwork/player-front-multi-eight-v1/output/bullet-163-8.png`.
- Rear183 d8 derives directly from frozen `bullet-164-8.png` in the same folder.
- `assets/hd/artwork/player-rear-multicannon-p4-mode2-down-diagonals-v1/inputs.json`
  pins both sources. Its existing `build.py` reads those paths directly, flips
  each complete canvas vertically and verifies encodedPNG/RGBA/HDR1 goldens.
  No extra source copies are needed.

From the repository root, rebuild into **two new external directories**:

```sh
python assets/hd/artwork/player-rear-multicannon-p4-mode2-down-diagonals-v1/build.py --output /path/to/new-art-output --hda-output /path/to/new-hda-output
```

The strict pixel-transform rebuild passed in the audited Pillow12.3.0 /
zlib1.3.1 environment. This does not claim a rerun of the older Sharp SVG renderer.
The accepted163 and164 rasters are not exact horizontal bitmap mirrors:290 RGBA
samples differ. Do not replace this pinned pair with one bitmap plus flip.

These two d8 outputs serve records268/269/270: raw182 phase4 and raw183 phase3,
six consumers. Flat payload cells19/21 are d8; unsupported d4 cells18/20 stay zero.
The current-editable Front sources under `authoring-inputs/front-multi-current/`
are **different mutable authorities**, even when bytes happen to match today.
Their edits must not change historical Rear182/183. Existing regression
`FrontMultiAuthoringTests.test_historical_rear_multi_derivatives_stay_frozen_after_163_164_edits`
protects that isolation. Making these two independently editable later would be
a separate reviewed migration, not a missing step in current source ownership.
