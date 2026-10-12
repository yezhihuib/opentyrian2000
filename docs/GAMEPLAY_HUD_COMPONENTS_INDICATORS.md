# Gameplay labels, shield and mode indicators

This finite extension follows static HUD V5 (`d2f0a36`). It preserves original
indexed drawing and gameplay. HUC1 and HUL1 are independent optional resources
in the two default HD packs. Missing or invalid resources leave the selected
scene pack and other HUD resources working. Classic rendering, non-PIC3 and
unsupported modes retain their original presentation.

## Exact scope

- HUC1: FRONT, GUN, REAR, GUN in four existing boxes (350 logical cells), plus
  event-stamped blue shield bands in [270,137,279,195). The 522-cell channel is a
  comparison bound, not a paint mask: black track and capacity marker are still
  original indexed pixels. Absolute segment heights, colors and capacity stay
  unchanged. A completed original draw records displayed S/M; a wipe revokes it.
  Thus death's wipe-only blank is different from drawing shield zero, and a stale
  displayed end-level bar is not recomputed from live player state.
- HUL1: top lens [269,4,276,7), and complete mode assembly [285,44,312,52).
  These 237 cells include exactly82 existing static-frame cells. Both original
  mode states are verified against all216 original indexed assembly cells after
  the original paired sprite draw. Shared OPTION sprites and shops are unchanged.
- No MODE/SHIELD/ARMOR lettering, score digits, message text or other bars were
  redrawn by this checkpoint. Those remain separate work.

All source/palette/surface leases and per-pixel/region guards are required before
composition. FNV64 detects accidental corruption; it is not authentication.
Fixed header, size, bounds and alpha checks do not rely on its security strength.
Both payloads use authored density4, repeated exactly2× at internal density8.
Actual native2× samples this canonical artwork, rather than a separate offline
coverage-downsampled preview.

## Ownership and fades

HUC1 has no overlap with the published6667 static-frame cells. HUL1 uses fixed
current/saved underlay arrays for the82 overlapping cells (41,984 bytes total at
maximum density8), plus bounded metadata. Hidden frame colors follow the same
integer fade recurrence. Removing the upper layer restores that faded underlay;
removing the lower layer first revokes hidden ownership without repainting a
valid upper layer. Untrusted source/cache/generation transitions discard the
cached presentation safely. There is no per-frame allocation or file I/O.

Payload sizes are38,592 bytes for HUC1 and29,072 bytes for HUL1, with fixed loaded
payload allocations38,528 and28,992 bytes. No performance/FPS improvement is
claimed. The pre-existing classic pause/help/options route remains visible as a
presentation transition; returning to gameplay restores the eligible HUD.

## Reproduction

`python prototype/build-hd-assets.py` reconstructs both headers and payloads from
21 canonical PNGs and verifies every frozen source-file hash. The unchanged HDR1
pack counts are separate from these four new default-pack sidecar copies.

`python prototype/build-gameplay-hud-extensions.py --output /fresh/external/path`
rebuilds both formal recipes, requiring a new external directory without symlink
path components. It runs the HUC1 self-directory writer only in a fresh copy of
its two required inputs. Frozen authored packages are never rewritten. Their
freeze-time trial wording is retained; this integration report records the later
runtime acceptance. Proof-only track/marker PNGs are not runtime payload tiles.

## Bounded verification

The source was independently reviewed at HUC1 `dc1a2cf` and HUL1 `4afc816`.
Eight final ASan/UBSan suites include144 whole-image fade/underlay comparisons,
17 lease/cache/ledger faults, prior HUD regressions, finite loaders and original
writer oracles. Four120-tick no-resource cases per extension preserve original
state and RGB. Those no-resource collision streams are header-only.

HUC1 actual evidence covers257 ordinary ticks; full/half/low at100/5/250,
10 consecutive frames247–256 with natural damage/regeneration, and native4×250.
The separate60-tick built-in debug-death fixture confirms a wipe-only blank;
it is not a claim of natural death coverage. All32 fade presentations and actual
pause/help/options compare against the same baseline and original controls.

HUL1 actual evidence covers default mode1 at250 and five frames248–252 using
private scripted original button presses at249/251, producing1→2→1 with the
original release/debounce behavior. This fixture does not fire: rear shot position
stays zero, so a nonzero-to-zero shot reset is source-verified only. Native4×mode2 and both missing
and corrupt-only fallback cases pass. The private input/presentation observers
are excluded from production. Full gameplay ledgers match; changed pixels stay
in237 cells, with HUC1, playfield and static V5 outside82 exact. Missing/corrupt
cases compare253 native presentation FNV64 hashes and full internal8× audits;
five selected native frames also have matching SHA256 hashes.

Author review passed all10 shield frames, allfive mode frames and the native
2×/4× spots. Actual modals/fades are distinguished from synthetic reverse-layer
removal, restart/next-level and unsupported-mode checks. This is not full-game,
all HUD text, CI, or Windows runtime acceptance. Linux build and Windows source
list/XML checks pass; no Windows compiler/runtime was run for this checkpoint.
