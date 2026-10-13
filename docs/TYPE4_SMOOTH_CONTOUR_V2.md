# Type4 smooth-contour v2 candidate

Five approved generated poses159/161/163/165/167 replace only their density8 assets in the two current default packs. Production source is unchanged from317bf551db59df9c4e3754d2072446c7313ab1f4. Namespace101, slots369–373, full24×28 registration, anchor6,7, original20-step animation and gameplay behavior are unchanged.

Unlike v1, v2 reconstructs fractional contour/support inside the original rectangle. The alpha≥128 support bounding box remains exactly the original per-pose bounding box, with no global shrink or opaque backing. Full frozen generated masters, deterministic rebuild contract, exact support-addition/removal masks and native-scale references are retained under `assets/hd/artwork/type4-fivepose-smooth-contour-v2`. Old art, canonical PNGs and historical proof remain available.

`prototype/build-type4-art.py` verifies the exact frozen import and fresh PNG/RGBA/HDR1 reproduction, registration, source masks as evidence (not imposed alpha), both selected packs and absence from other packs. Optional original data verifies all20 RLE cells and all1701 enemy records; only record4 uses the five bank1 bases. `prototype/test-type4-source-guards.py` rejects17 invalid paths/provenance/pack-scope mutations.

`prototype/test-type4-binding.py` extracts23 current production helpers and requires all146 src files byte-identical to317bf551. ASan/UBSan cover both packs, all5 IDs, original20-step × four-quadrant order/origin,256 filters preserving alpha,55 per-member malformed/missing cases, missing-all-five, namespace/neighbor preservation. Type4 keeps its historical independent member/header/size fallback and4× retry; no4× B resources are supplied. It does not have payload-checksum or atomic-family runtime enforcement; exact art bytes are pinned by the source/package verifier. Type15/C remains independent and unchanged.

Validation commands:

    python3 prototype/build-type4-art.py --output /absolute/fresh/output
    python3 prototype/test-type4-source-guards.py --out /absolute/fresh/guards
    python3 prototype/test-type4-binding.py --out /absolute/fresh/binding
    python3 prototype/build-hd-assets.py
    python3 prototype/test-windows-project.py

## Bounded runtime result

Exactly four fresh protected/no-fire runs passed: current-v1 and candidate-v2 native640×400 at3340–3359, candidate native1280×800 at3348, and missing-all-five native640×400 at3348. One identical private binary served finite read-only asset overlays. No game was rerun. Full paired state/indexed/RNG and original source streams match through3359; the4× prefix matches through3348. All4,953,248 final native pixels outside actual type4 full rectangles are exact across the20-frame pair.

Actual source actor56 is fully exposed in all20 original phases. All candidate foreground, including fractional alpha, matches exact after-four-quadrant compositing in the final native2× output and true4× spot. The fixed2× window has280 source-qualified calls,2,668,032 exact canvas samples and932,354 fractional samples, with zero mismatches. Missing-all-five returnsfalse for every type4 call; original RLE/palette pixels and the final selected actor are exact. Full RGB equality to the v1 HD baseline is not claimed for missing art.

The first offline verifier assertion required allfour calls for every actor. Original caller clipping legitimately emitted only bottom parts19/20 for actor61 at3347–3352. Both lanes were identical. A reviewed proof-only correction derives allowed parts from original enemy.y conditions; the fully visible selected actor still requires allfour. The original failed log and prior verifier are retained. No runtime or capture extension followed.

This is seeded stationary/no-fire Linux software/dummy SDL display evidence with a matched private alive-only invulnerability floor2 immediately after original events. No natural hit/ice/death, natural survival, full-level, manual-input, GPU/fullscreen or Windows result is implied. The independent author reviewed all20 actual candidate2× frames, all20 current/candidate actor pairs and true4×3348 and approved without art changes. The sealed visual receipt is `type4-smooth-contour-v2/AUTHOR_REVIEW.json`; the numeric/fixture review is `type4-smooth-contour-v2/INDEPENDENT_REVIEW.json`. Historical v1 acceptance is retained independently.

## Known historical test limitation

The broad startup-manufacturer package suite passes14/15 tests. Its settings whole-manifest pin assertion fails in both this candidate and untouched main317bf551. This unrelated preexisting assertion was not relaxed. The five updated B compatibility pins are checked separately and exactly. Aggregate HD-resource validation,17 source-negative cases,67 ASan/UBSan binding cases and Windows source-inventory checks pass.
