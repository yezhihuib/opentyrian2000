# Complete the thirteen-member road family

Nine selected new road images: **36,38,39,40,46,47,48,56,58**. The already accepted four road images37/49/50/57 are byte-frozen. Together these are the complete thirteen-member road family in the audited physical level9 layer1 map. This is a bounded family update, not a whole-level or whole-game background conversion.

## Integration

The production binder is integrated after accepted underlay1daf3f6. Slots36=220,39=221,40=222,46=223,48=224,56=225,58=226,38=235,47=236; capacity241 is retained and terrain registry104→113. Installation231–234 and underlay237–240 remain active and unchanged. The original private art-validation binder was based onb13d5c6; its separate late diagnostic is described below. Source/rendering code lives in the repository, not this artwork folder.

Each asset is opaque24×28 logical, anchor0,0,8×192×224 straightRGBA. Each172060-byte HDA contains `HDR1`, six little-endian U32 words `[2010000+ID,8,24,28,0,0]`, then pixels. The manifest records every PNG/RGBA/HDA hash. No renderer, map, event, collision, scrolling, palette, shadow, object canvas or draw order change is required. Unknown/missing/invalid assets retain original fallback.

## Authored source and deterministic rebuild

All raster content was authored with imagegen using actual continuous map references and frozen accepted material context. Source includes only the nine authored target-cell crops. Full imagegen context masters, original game references and screenshots stay private; source/crop-provenance.json records master hashes and exact literal crop rectangles. The five original selected road crops36/39/40/56/58 remain intact. New46/48 were redrawn together against the true two-tile corridor to correct a roughly2-logical-pixel center displacement; the accepted replacement visually preserves width and the known curved entrances. The faint source palette-band position metric is a proxy, not an exact semantic road mask.

The four newly generated38/46/47/48 receive documented uniform RGB color registration to match the frozen warm-brown road palette. Native GEGL tile-seamless periodizes only the interior-fill47. Native C++ harmonic registration constrains actual new/frozen adjacent edges in a32-HD-pixel inward band; the interior remains unchanged after those prerequisite operations. No alpha holes are introduced: every output alpha is255. Repeated47 was reviewed as a large map area, not only the isolated early occurrence.

Requirements: ImageMagick6 `convert`, C++17, Python3 with Pillow, and `/usr/bin/python3` with GI/GEGL. Set `TYRIAN_HD_BASE_PACK` to an accepted pack with the exact18 frozen dependency HDAs, then run:

    bash rebuild-selected.sh /absolute/new-output-directory

A fresh rebuild verifies9/9 decodedRGBA and HDA hashes exactly; in the tested environment PNG files also match exactly. Normative pixel/HDA hashes are separate from incidental PNG encoding. Original game data is not needed for reconstruction.

## Whole-map topology and edge scope

The map contains363 family cells. Every occurrence is inventoried. Canonical cardinal adjacency includes142 pair types/810 unique map edges; canonical eight-neighbor coverage includes368 types/1638 edges. Of the121 pair types touching a new tile,89 new/new or new/frozen road/ground relationships receive explicit registration, while32 external relationships are visually audited without changing the external tile. Old props and other distinct terrain materials are not silently painted over.

All new/new registered8× boundary texels match exactly. Frozen assets already contain mutually inconsistent texture phases: a single new edge cannot equal every old counterpart simultaneously. The chosen frozen-priority compromise has a maximum15RGB residual at a few old-boundary relationships; the complete residual list is included. Resampled2×/4× adjacent rows also contain genuine texture variation, so their edge-difference metric is not a binary seam test. Actual-size continuous map reviews show no visible hard grid, aligned white-grain line, widened gap, or boxed47 patch. The selected repeat has some recurring stone texture, as expected from a finite repeated tile.

## Runtime evidence and bounded diagnostic

The private37b3815 baseline/candidate normal tests run through0–1052, the fixture's natural game-over. All nine new IDs draw NORMAL/HD. Indexed gameplay, original effects/blend operations, all prior scene commands and original foreground parameters remain exact; only expected HD coverage counters differ. Internal RGB audits match across2×/4× output scales. Missing-nine fallback passed27 deterministic byte-identical TSVs. Latest b13 binder ASan/UBSan passes28,100 assertions.

A separate identical baseline/candidate **private synthetic invulnerability diagnostic** reaches0–2899 to inspect the broad47 repeat beyond the ordinary fixture lifetime. It floors an already living test pilot's invulnerability counter to2 after original event processing. It does not change original map, scroll, event, RNG or renderer code. Its original state/material/foreground/effect logs remain exact between both diagnostic sides. It is not an ordinary replay, and its private hook is not included in this production patch or generated-source package.

The latest b13 installation-aware baseline/candidate normal0–1052 and private late0–2899 pair both pass the same original-state, command, effect and zero-coverage-error assertions. The published installation is preserved on both sides. Two real2× scrolling segments contain120 actual frames each: normal500–619 and private diagnostic2757–2876. All frames are directSDL readback at one frame per original logic tick, without invented scrolling/interpolation. Every lossless decode equals its original capturedRGBA hash. HUD and bottom panel are byte-identical; every before/after display-pixel difference is inside the new9 tile rectangles, with zero differences outside. Generic-shadow coverage is included in that scoped check.

Independent map matching finds a unique exact row-sequence anchor for every one of2900 diagnostic frames. It does not assume constant speed: event slowdown starts at2401, and tick2899 has actual displacement2566 rather than2899. Across this run,72/150 unique47 cells are visible, including69/147 in the r191–211 broad field; r191–199 is not reached. The chosen video window spans66 unique47 cells. Full static map coverage is not misrepresented as full runtime placement coverage.

This package is frozen after root approval of the native2× normal and broad-repeat frames. Preview media and readback hooks remain outsideGit.

Ground shadows use the existing accepted renderer. Original indexed operations are exact; genericHD darkest-brown shadow color is not claimed to be palette-identical. No wider shadow correction is part of this batch.

## Exclusions

No original game data, original reference PNG, user attachment, runtime screenshot/video, private capture executable, invulnerability hook, unselected artwork, or previously withdrawn plateau candidate is included. Those working references and rollback copies remain preserved outsideGit.
