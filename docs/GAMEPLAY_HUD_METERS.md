# Gameplay firepower, generator and coarse armor (HUM2)

This finite candidate refines the original front/rear firepower bars, generator
raster and armor bar. It uses the accepted coarse-group armor V2 artwork; the
rejected fine two-row separator design is not selected. Original values, colors,
occupied heights, update timing, clamps and black/blank cells stay authoritative.
The bounded actual Linux trial and source/resource gates pass. See the exact
coverage and limitations below.

## Scope and original history

Half-open logical HUD rectangles are front `(289,17)–(311,20)`, rear
`(289,38)–(311,41)`, generator `(269,12)–(277,104)` and armor
`(307,137)–(316,195)`: 1,390 disjoint cells. These use output coordinates, without
the scene's x−24 transfer. No shield, labels, digits, lamps or frame cells are
newly owned by this feature.

The sampler does not infer a displayed gauge from current player values. Four
pairs of passive notifications observe the unchanged original write routines:

- Firepower supports P0–11 and retains each two-by-three segment and palette
  role. The original item power is displayed even when a port is absent. An
  unsupported P12+ revokes ownership before the original write, rather than
  confusing its in-box pixels with P11.
- Generator keeps the 92-row painted index history. Increase/decrease/no-write
  events retain their original behavior. Only actual contiguous equal-color
  runs receive edge shading; no synthetic fixed bands are introduced. An arcade
  branch with power900 can legitimately leave a fresh meter blank or retain an
  earlier raster because it performs no meter write.
- Armor retains A+1 original two-row units for A0–28, including A0's baseline.
  Shading follows contiguous original coarse palette groups rather than adding
  a separator at every unit. There is no capacity marker or normalized fill.
  Original two-player clamps remain unchanged. Wipe-only blank and redraw A0
  are distinct events; the renderer does not invent a frame between them.

Every field is compared atomically against its accepted original-index history.
Mismatches revoke that field; plausible pixels alone cannot restore authority.
Only an eligible full original write or a fresh compatible PIC3 can renew it.
A value change without a draw does not change the displayed raster.

## Resource and fallback

HUM2 is 621,920 bytes, SHA256
`3f8d9c35a3a9791d554a3c46f3431289c8ecd68b57419747ce3a40c225dafa4c`.
A 112-byte fixed header precedes 621,808 payload bytes: 11 firepower tiles, 29
coarse armor group tiles, 944 unique generator rows and 222,456 uint16 row IDs.
All material samples are opaque canonical 4×; internal density8 repeats them.
Native2× visual sampling is checked separately against actual readback.

The loader verifies regular-file identity, exact size/header, every row ID,
alpha, section and payload signatures, EOF, source and palette compatibility.
Bounds are independently checked before reads/allocation. Checksums detect
accidental corruption and do not authenticate files. It makes one bounded
621,808-byte allocation; history is152 bytes and prepared row offsets600 bytes.
No I/O or allocation occurs during capture, write, sample or composition.

Missing/corrupt HUM2 leaves the selected scene, HUF1 typography and other HUD
families active while those meters use original graphics. Each affected meter
also has independent field-history revocation. HUC1 shield/labels and HUM2 share
disjoint owner bits; HUF1 retains its separate generation and region ownership.
Saved/current cache trust is checked before fades and presentation.

## Reproduction and source validation

Formal source is `assets/hd/artwork/gameplay-hud-meters-v2`: exactly13 files.
The deterministic authored recipe and selected role colors reproduce all four
sections, all1,196 generator materials, the ownership mask and final HUM2 bytes.
No original game image is a build input. The portable package records fresh
recovery/rebuild evidence, not unavailable earlier runtime files.

Run `python prototype/build-gameplay-hud-meters.py --output /absolute/fresh/path`.
Existing, in-repository, ancestor and symlink output paths are rejected. Both
default packs are checked by the central asset builder.

The independently reviewed combined source preserves HUF code/writers and all
original meter logic. The only HUF/HUM merge decisions are additive shutdown and
cache-retention calls. Source tests compare whole output/saved frames with
counterfactual family removal, both last-owner orders and isolated generation or
owner loss at fade start, step and presentation. Active HUF with HUM absent
matches the exact pre-meter implementation. Parser, legal values, original
writers, geometry and material reconstruction have bounded sanitizer/scalar
coverage. None of these source tests is presented as a natural game capture.

## Bounded actual acceptance

The ordinary 265-tick A/B replay preserves original state, indexed output, RNG,
writer histories and shared simulation ledgers. Nine selected internal8× and
native2× samples match the frozen canonical resource inside exact active meter
ownership, with zero change outside the 1,390-cell scope. The true4× tick250
pair is checked independently. Presentation evidence includes natural ticks5,
100 and250 plus all seven consecutive frames248–254.

At tick250, firing changes live power to850 while the displayed generator still
holds its previous q90 raster. The original writer clears90→86 at251, then
refills87→89→90 at252–254. This history is checked from actual original writes,
not inferred from end-of-tick values. Ordinary armor remains10; its broad color
groups are visually checked without claiming an ordinary armor transition.

A separate existing `--death` 60-tick debug fixture checks original armor writes,
A4 at5, and A0 at9. Wipe-only blank is an event observation followed by the
original18-cell, two-row A0 redraw; no intermediate blank armor presentation is
invented. Shield remains separately blank after its diagnostic wipe. Native
frame0 is the identical opaque-black startup presentation, so visible death
samples are5/9/10/11. This fixture is not a natural-play survival claim.

Two120-tick absent/corrupt-resource checks preserve complete accepted-baseline
HD RGB, original state/indexed output and writer prefix. Declared run duration
in loadout metadata differs120 versus265; that metadata is not gameplay state.
No additional fallback media is captured.

Private trial capture, passive readback and fixture-only code remains outside
production; the existing public debug capture remains available.
Arcade900 blank/stale history, unsupported values, modal/fade lifecycle and
other modes are covered only by their stated source tests. Current Windows
runtime and whole-game visual/performance acceptance remain outstanding.
Validation hashes and exact counts are in `GAMEPLAY_HUD_METERS_VALIDATION.json`.

The final production-only merge with the independently accepted left mechanical
four-tile binder matches all 27 standard raw log streams and all 265 internal
RGB/state/indexed rows exactly. It uses the same documented default debug pack
and creates no new captures. This is output equivalence for the reviewed early
window, not new visual coverage of later map placements.
