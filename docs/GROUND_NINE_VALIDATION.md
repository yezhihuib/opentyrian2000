# Bounded nine-tile brown plateau

## Scope and implementation

Shapesz layer1 IDs99,100,106,107,109,110,118,119,120, logical24×28, density8, anchor0,0. Opaque generated art extends only the two current default packs. Existing101,37,49,50,57, terrain props, fifteen cloud-v2 tiles and rotor assets remain unchanged. Shared asset capacity stays218; ground uses201–209 and rotor210–217. Terrain pointer capacity grows87→96.

The finite layer1 whitelist and slot selection are the only production changes. Missing or invalid new art exits before logging/drawing, preserving the prior original path exactly. Cloud blend guard, provenance-aware cloud shadows, green layering and generic filters/shadows are unchanged. No gameplay, palette, collision, RNG or map alteration.

## Artwork and reproduction

The real main plateau and diagonal107/120 occurrences guided source registration. All22 internal facing-edge types match exactly; frozen101-facing samples differ by at most3 RGB levels due to corner constraints and rounding. No alpha holes. `prototype/build-ground-art.py` reconstructs all nine HDA/decodedRGBA bytes exactly from saved imagegen sources and the checked existing HD101 resource. Original game data is unnecessary. PNG metadata is distinguished from decoded pixel identity.

## Finite validation

Actual first522 ticks at native4×/2× cover all nine IDs. Independent reviewed continuous evidence contains two120-frame segments37–156 and300–419, totaling240 real frames per side. Both HUD regions are exact throughout; every lossless-decoded frame matches direct SDL readback. No synthetic scrolling or tweening.

Production integration replays are checked against the reviewed candidate for exact RGB, state, draw and coverage records. Original state/collision/projectile/entity logs remain exact. The expected brightness_hd_blocks diagnostic counter changes because HD ownership is broader, not because gameplay effects changed. Missing-all-nine retains original fallback, and a focused6107-check ASan/UBSan oracle covers finite IDs/layers/banks, exact slots/capacity, all header fields, missing each/all, existing cloud/ground and the wild cloud guard. The rotor101,573,120-pixel oracle and cloud/green-layer regressions pass after integration.

## Known limits

The front rim retains bounded tile repetition. Five external pair types meet original36/56/58 or accepted321; no unrelated art is forced to match. The style transition at120→36 remains. Later original96/97/98/108 relations are untested full-level risks. Dark101 ground and sandy path are outside this batch.

An ownership-traced shadow audit found439 original-dark-floor samples on99 from INSERT COIN text shading. Ship shadow on118 differs at ticks85–89, at most66 authored8× subpixels in one frame, approximately1.03 logical pixels, all single-depth. One screen sample is RGB8,5,0 versus original16,8,0. No repeated darkening stack or independent hue-shift evidence was found. Root reviewed this bounded difference and retained the existing generic renderer; shadow color is not claimed pixel-identical. Diagnostic state/RGB matches the original candidate runs. Highest-detail processorType4 produced12,855 new-ground calls over420 ticks, all NORMAL, so no speculative new blend guard is added.

No whole-level, native Windows/GPU/fullscreen, physical2K or full-level performance acceptance is claimed. Publication remains separate from the preceding rotor change.
