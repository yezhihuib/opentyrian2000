# Mint-O-Ship: one normal player projectile head

This finite checkpoint adds normal player-role8 TILE27 for the first shop's left Mint-O-Ship sidekick (option16, weapon record452). It preserves original equipment, purchase cost, firing, motion, collision, RNG, indexed pixels and shadow. Sidekick bodies, shop preview, enemy art and Christmas use their existing paths.

## Artwork and scope

The chosen generated revision3 is retained verbatim in `assets/hd/artwork/player-mint27-one-v1`. Its fixed crop339,139..966,1041 is LANCZOS-resampled to40x72 and registered at32,32 on the96x112 transparent canvas, corresponding to logical12x14, anchor0,0 and original logical bbox4,4..9,13. There is no algorithmic repainting, recoloring or alpha adjustment. `rebuild.py` reproduces the exact PNG/RGBA/HDA using Pillow12.3.0 and the recorded generated-master hash; no original raster/mask is an artwork input.

The selected HDA is `cac289e69dcbf47aa2b121dcd4c5740ce1531a4295af9a752e51fde2bc738702`. The renderer admits only the exact decoded normal27 index/support identity before every cold or warm lookup, including same-address source reload. It uses slot535 of536. Christmas and changed sources remain classic; the27 shadow is explicitly kept on the original indexed path. Existing independent8-to4 asset-loader fallback is retained, while default packs contain only this family's8x resource. Both established default manifests543→544; all prior listed and six unlisted resources remain unchanged.

Native-size review found revision1 too small/weak; it was rejected. The selected revision3 is visibly fuller, with a continuous green/white core distinguishable on sampled snow and brown terrain. It is still smaller than the original: equivalent alpha area20.7052 logical pixels versus original37. This difference is recorded rather than hidden by gameplay or alpha compensation. The final source package contains the selected revision3 only.

## Source and unit verification

- All3 item-table groups retain record452 and identical duplicate1452, with one static bank8/27 head, no charge, trail or collision-child chain. Only option16 is an actual mapped option user; no named front/rear port or enemy turret uses these records.
- `prototype/build-mint27-art.py` validates the frozen generated master, exact registered PNG/RGBA/HDA, canonical source identity and both default bindings; independent relocated reconstruction matches.
- `prototype/test-mint27-binding.py` passesO2 andASan/UBSan. Each run has58 head calls,34 labeled source-identity scenarios,15 missing/malformed/density-fallback variants,48 original-shadow/geometry cases and6297600 original indexed bytes checked. The finite harness executes production loader/source/hook/RLE code; head RGBA drawing is a metadata-checking stub. Full rendering is checked separately in actual-engine runs below. LeakSanitizer is disabled for the ptrace environment.
- `prototype/test-mint27-scope.py` proves exact renderer inverse, byte-exact old manifest restoration and the finite new-file inventory. No other production source or accepted artwork changes.
- The default LinuxO2/NDEBUG/WITH_NETWORK build and disabled-renderer translation unit compile passed. All153 production source files in the final art revision are byte-identical to that compiled candidate. Five existing misleading-indentation warnings remain; no compile/link errors.

The finite source tests pin published MP3-baseline tree `a7157ccac97494ecbe3b1d54ba03a9ef42646ffd`, not a private local commit, and accept the same finite file inventory before or after commit. With a C compiler and separately supplied original data, use fresh external output paths:

```sh
python3 prototype/build-mint27-art.py --output /absolute/new-art-check
python3 prototype/test-mint27-binding.py --data /private/tyrian2000 --out /absolute/new-binding-check
python3 prototype/test-mint27-scope.py --out /absolute/new-scope-check.json
```

## Finite actual-engine verification

Original menus were navigated using bounded synthetic SDL keydown/up events in a removable private observer build. Both difficulty routes naturally selected and bought left Mint16 for5000, changing cash10000→5000. The original main-fire button then emitted452, without forced equipment, money, power, invulnerability, probe activation or gameplay edits. A fixed original time() input makes the original seed deterministic; no additional RNG calls are introduced.

Normal physical9 andHard physical15 each have a retained original-head baseline and a selected-revision3 candidate,90 live ticks per case. Each candidate has18 natural452 emissions,279 actual on-screen HD27 draws and279 retained original indexed shadow draws. For each pair, all90 original indexed/palette/state/RNG frame hashes,42 requests,40 total emissions,1234 draw rows and all shot positions match. Hard's existing night-cone output is active for89 of90 ticks. Retained-trace geometry finds18 head draws with original support in the cone transition, with lit support in every head draw and no fully-dark head sample. The three retained native capture ticks have only lit head support; this is not full-lighting visual coverage or an authored-alpha subpixel-shader proof. Three unretouched640x400 native2x gameplay captures and two shop captures per candidate retain the visible evidence. All20 verifier fault injections are rejected.

The selected-art retest used two new candidate process starts and reused the two exact earlier baseline traces after verifying all153 production source files, the same compiled private binary, dependencies, input and unchanged pack members. The earlier rejected art was separately tested in four completed90-tick runs plus one preserved0-live-tick shop-sort fixture failure; those are historical evidence, not additional selected-art passes, and their directories are excluded from this source checkpoint.

Both90-tick windows contain zero collision contacts. State/collision parity is established for these contact-free windows; successful collision-contact rendering or a gameplay outcome is not claimed. This is limited Linux SDLdummy/software native2x evidence, not a whole-level, all-background, full-campaign, Windows, physicalGPU, native4x or performance qualification.
