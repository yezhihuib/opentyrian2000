# Pulse-Cannon simpler art revision v2

## Scope and authorization

The user requested a less extravagant Pulse-Cannon appearance after comparing
its ornate red heads with the simpler Vulcan bullet. The selected imagegen
masters retain five silhouettes: single (58), twin (59), three (60), five (62),
and four (165) lobes. The user approved this direction and explicitly permitted
whole-image cropping, equal-axis resizing and transparent padding. No recolor,
alpha cleaning, repainting or independent lobe movement is performed.

The masters and exact prompts are retained under
`assets/hd/artwork/pulse-family-v2-simple/`. The reproducible exporter uses
visually selected rectangular crops, uniform 1/10 Lanczos resizing and placement
on a 96×112 transparent canvas. Low-alpha stray master pixels are not masked or
retouched; pixels outside the approved whole crop are simply excluded. The five
outputs have zero alpha on all outer canvas edges. The manifest records every
crop, size, placement and source/output hash. Generated art has no runtime
animation; original shot emissions and motion remain authoritative.

## Registration and common use

All five HDR1 payloads retain their original identity, density8, logical12×14
size and anchor metadata. Resource80059 retains anchor(-1,0), with its canvas
registration already baked in. Neither battle nor SHOP applies another offset.
The new family has narrower simple luminous cores and red tapered ends; it is
not a geometry-preserving recolor of the ornate art.

Only the five resource payload/provenance records are revised. The fourteen
family source/record/palette/role definitions are byte-exact. The common global
registry supplies both the separate battle Pulse owner and the independent SHOP
Pulse preview owner. No weapon tables, coordinate system, damage, power levels,
RNG, input, audio or economy code is changed. The new registry header is the
only changed production source file.

Original content-addressed HDA, original PNG, legacy packs, accepted v1 artwork,
`assets/hd/manifest.json` and historical validation receipts are retained
unchanged. Legacy non-global debug packs still represent their old artwork;
this revision selects the new art only for the current global battle and SHOP
resource root, not for unrelated same-numbered sprites.

## Exact revision validation

`packaging/pulse-art-approved-v2.json` identifies exactly the five old/new rows.
`tests/approved_pulse_art_revision.py` pins that approval and projects only an
exact matching new row to its previous row when evaluating historical
unchanged-resource assertions. It never projects family metadata, source
identity, dimensions or anchors. A new negative test rejects altered art rows;
all other rows remain subject to exact historical comparison.

`tests/test_pulse_art_revision.py` independently reproduces each permitted crop,
scale and padding operation, compares RGBA and HDR1 bytes, checks old art and
historical receipts, and verifies generated C pins. The exporter is not an
acceptance receipt. Final battle/SHOP native, regression and packaging evidence
is recorded separately after those gates complete.

## Required actual-runtime checks

- All eleven ordinary Pulse power levels, covering all five heads, battle and
  independent SHOP previews; integer2×/4× output.
- Original reference, missing and corrupt resource modes preserve classic
  fallback. No role/lifetime or cache permission is widened by new art.
- Original indexed output, state, RNG, input and audio-call parity; HD pixels
  match the new RGBA oracle and remain within actual source/new-art support.
- Visual review of bright cores, paired spacing, high-power silhouettes, tail,
  shadow, clipping and overlay ordering. No claim of Windows/GPU, listening or
  complete-campaign validation is made by this Linux software test work.

## Accepted validation (2026-10-21)

Fresh frozen-source Linux SDL software/dummy native checks passed. Battle ran
96 cases / 10,560 frames: all eleven powers at 2× and 4× in full, reference,
missing and corrupt modes, plus MINES powers 1/11 at 4×. All five heads and
body/shadow styles were observed in 19,692 accepted draw calls. Independent
bounded draw witnesses compared 624 samples / 6,709,248 pixels with zero
mismatches; 72 final-surface support checks found zero outside-support pixels.
Original INDEX8, simulation state, RNG, audio queue/calls and front-fire traces
matched. Battle input evidence is an identical deterministic SDL key-event
schedule plus exact resulting player/front-fire state, not a separately logged
raw SDL queue.

Independent SHOP ran 10 cases / 2,990 frames covering all eleven powers and both
scales, including reference/missing/corrupt fallback. Ten independent draw
oracles compared 10,240,000 canvas pixels with zero mismatches; all 72 support
checks passed. INDEX8/state/RNG/input/audio-call traces matched. Reviewed
unmodified actual battle and SHOP captures show compact readable cores, distinct
high-power lobes, retained native shadows and no clipping or opaque rectangle.
Unregistered later animation indices remain classic, deliberately unchanged.

Independent art/source review, 150 adversarial exact-allowlist probes, 27 registry
and five revision tests, eleven battle/HUD sanitizer suites, six SHOP suites,
126 typography states / 16,252 checks, shared-reader differential testing
(120 assets / 10,880 fault cases / 1,237,919 checks), and 40 packaging tests passed.
The deterministic runtime package has 1,007 payloads / 1,010 ZIP entries; its
relocated 16-second startup exited cleanly after 143 Presents. The first
incorrect typography harness invocation is retained as evidence; its corrected
rerun passed without production edits. A historical prototype head-layer
harness compile failure is not counted as a passed current gate.

Receipts are sealed separately in the local checkpoint under
`pulse-art-v2-native/summary.json`, `pulse-art-v2-regressions/final-regression-status.json`
and the independent/package directories. All 247 current production source
hashes and registry/art/package bindings were verified. Only the generated
registry header differs among production sources. Native checks use disclosed
assisted new-game loadout/SHOP cash fixtures and bounded independent draw
samples; they do not establish Windows/GPU/full-campaign or audible verification.
No GitHub publication is included in this acceptance.
