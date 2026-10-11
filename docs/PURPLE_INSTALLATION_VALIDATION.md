# Purple installation and persistent Layer3 foundation

Accepted bounded batch on top of `0044d19ca92f54f2160a3f773da22b6fcb64188c`.

## Identity and rendering contract

- Terrain: shapesZ Layer3 IDs150/156/157/158/159/160/166/168/169/170/176/177/178, slots290–302; normal blits only, 24×28, anchor0,0, density8, opaque.
- Entities: newsh2 bases169/207/245/273/275/277/279/281/283, slots303–311, types32–39/41; static 24×28 quads, anchor6,7. Original sparse alpha samples remain exact.
- Components remain independent link0 entities. One struck component disappears without collapsing the others. The center has armor20; the other eight have armor6. Center explosion value11 produces the original big repeater and its follow-up effects.
- Foundation rows156/157/158,166/150/168,176/177/178 retain actor row offsets0/−1/+1. No enlarged opaque footprint, replacement remnant, global blend/shadow change or gameplay mutation.
- Terrain169 and entity169 have separate bank/slot caches. Existing298 debug-pack files are unchanged. Missing/invalid new resources retain original rendering.

## Selected art and reproducibility

Terrain source is `assets/hd/artwork/layer3-purple13-v4`; entity source is `assets/hd/artwork/purple-installation32-41-v2`. Source packages contain authored/generated pixels and deterministic exporters, no original game RGB, maps or captures. Image generation itself is not claimed reproducible.

The final correction changes only the last two logical rows of terrain176/177/178 and entity273/275/277. Maximum RGB change28; all alpha, dimensions, anchors and rows0–207 remain exact. The other314 combined debug-pack files are byte-identical to the preceding candidate. This reduces the thin light backing fringe; minor cobble texture-phase differences remain.

Seven opaque authored terrain PNGs use RGB encoding. Canonical runtime-source copies are normalized to RGBA with alpha255; decoded pixels and HDR1 bytes are unchanged. Source-package originals retain their own hashes.

Run from the repository root, with Python/Pillow and a C++17 compiler:

    python prototype/build-hd-assets.py
    python prototype/build-purple-foundation-art.py --output /absolute/new-foundation-directory
    python prototype/build-purple-installation-art.py --output /absolute/new-entity-directory

The accepted manifest has18 packs,2872 HDA entries,328 canonical PNGs; current preview/debug packs contain316/320 resources.

## Actual engine verification

Cloud SDL software renderer, density8 composition and explicit nearest presentation at actual640×400 (2×) and1280×800 (4×). Legal original data stays outside Git. These are private-survival diagnostics, with no weapon71 injection; ordinary gameplay naturally ends earlier. No Windows, full-level or GPU2K acceptance is implied.

- Natural no-control baseline/candidate state0–2679 is exact. Native4× state0–2609 matches the2× prefix; common120 render ticks2490–2609 match logical RGB audits.
- Missing all22 additions: all280 rendered RGB audit rows and eight original logs match the prior accepted gray/turret build. ProcessorType4: all eight original logs match over2610 ticks; Layer3 stays on its original normal route.
- Controlled sequence2540–2659 uses18 original Pulse155 calls. Each nonlethal/lethal victim is resolved from the original entity table and independently verified. Center-column components are removed first, then the other six. All original state/material/collision/projectile/effect logs match baseline.
- Last intact component draw2603; full-art versus same-foundation/no-new-entity RGB audit hashes match from2604. Effects finish at2616; first clear frame2617. Turret40 remains independent and naturally leaves at2639.
- Final fringe revision repeats the same controls:13 complete original logs byte-identical. All120 final direct SDL readbacks round-trip exactly through lossless video, match the noncapture run, and are independently visually reviewed. All visual differences versus the preceding candidate stay inside the six approved fringe bands; HUD is unchanged.
- Native intact2540, column omission2579 and all-clear2625 show original registration and persistent broken foundation. Final2× intact/all-clear acceptance includes the quieter fringe. No stale art, component seam, flash, new dark stripe or explosion residue was observed.

These entities have enemyground=false, so they do not naturally receive the ground-only palette hit filter. Generic filters are exercised by the extracted renderer oracle, not claimed as natural gameplay.

The observed window contains nine purple terrain IDs. Extra159/160/169/170 have complete source/modular coverage only. All64 static cells in nine modular placements were reviewed; this is not a full later-level runtime claim.

## Automated checks

ASan/UBSan extracted C tests cover312 asset slots,153 terrain registrations, finite banks/layers/styles,91 actual level9 registrations, missing/invalid resources, clipping, sparse alpha, normal/indexed ownership and independent caches.

- Combined foundation:433,512,512 binder assertions and932,258,673 pixel assertions;23 deliberate mutations rejected.
- Nine entities:8,923,875,840 pixel comparisons,241,696 successful quadrants,2,814 rejected guards; all9×24 quadrant orders×256 filters. Original wrapper:380,928 cases across59 bindings.
-17 entity/wrapper faults rejected, including cache poisoning, wrong slots/banks, double blits, missing/double end and gameplay-state mutation.
- Final selected art rerun:133,816,320 pixel comparisons and1,188 quadrant calls, all nine, three filters, all15 nonempty subsets and clipping. Unchanged generic Cartesian tests are explicitly reused after the RGB-only fringe correction.
- Fifteen prior fixture suites and nine gray negative mutations pass. No CI result is claimed.

One recording attempt omitted the private-survival flag and ended before its target without producing frames. It is retained as a setup failure; the correctly labeled run passes. This was not a production defect.
