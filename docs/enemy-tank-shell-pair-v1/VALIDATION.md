# Bounded enemy tank-shell 146/147 validation

## Status and identity

Numeric source/unit/runtime checks pass for candidate 3f793793b70fbddb1011a6fa65f52bd55c784cca
on 916b7aa8a4a837c695d6cef4b1e9da133db27ef1. Actual-image author review also
passes at this bounded scope. Publication-content checks are a separate gate;
this report does not claim that any commit has been published.

Only enemy spriteSheet8 IDs 146/147 gain role 122, slots 505/506, capacity 507.
The frozen generated 96×112 RGBA resources retain logical 12×14, anchor (0,0),
density 8, fixed down/down-right headings and their approved fractional alpha.
No rotation follows velocity or actor facing. All-two-or-classic validation is
independent of energy/orb/player/gem families and independent newsh6 explosion IDs.
Enemy records 15/194/195 share weapons 2/3/6/7; only tank 15 weapons 2/3 are covered
by this actual replay. Records 194/195 and 6/7 remain source-level evidence.

## Source and finite units

The exact inverse restores all three changed production files to 916b7aa;
original shot/motion/collision/RNG tables and prior compositor paths are preserved.
Both selected packs add only the two shell bindings; every predecessor entry and
payload is unchanged. Canonical PNG/RGBA and HDR1 hashes are pinned by the art
inventory. The public proof metadata is a declared derivative of the private audit;
original reference pixels and machine paths are excluded.

Extracted-production ASan/UBSan units pass preview/debug × normal/Xmas. Per lane:
807 transactions, 423 accepted/384 fallback, 240 player cases, 46 guard checks,
11,383,232 pixel comparisons, 60 full-frame checks and 393,216 exact-alpha cases.
Twenty-nine negative packs include either member missing/malformed and density 4-only.
Fresh/sticky caches, clipping/extreme coordinates, exact original blit/reset,
ordered alpha writes and unrelated-family isolation are checked. The disabled
build performs 12 original blits. LeakSanitizer is disabled; ASan/UBSan are enabled.
Release and RENDER_MIRROR_DISABLED Linux builds pass, with a pre-existing warning
in unchanged output-fade code. These units are not game runs. Two corrected test-
adapter assumptions remain recorded privately; neither changed production code.

## Accepted numeric runtime matrix

Five engine processes started and 18 native PNGs are retained. Four cases form the
accepted numeric matrix (16 PNGs): baseline 2× six, candidate 2× six, candidate 4× two,
and corrected missing-147 at 2× two. The first missing-147 process and its two failed
whole-frame images remain separate failed evidence; they are not counted as a pass.

Baseline/candidate 2× capture 4214, 4215, 4614–4617 at 640×400. Candidate 4× captures 4214
and 4615 at 1280×800; corrected fallback uses the same two ticks at 640×400.
The baseline alone selected V = 4614. Source 146 is slot 4/generation 8, allocated 4206;
source 147 is slot 0/generation 51, allocated 4614. Identity includes emitter, link,
turret and weapon, not pool slot alone. Original terminal tick 4663 yields 4664
executed logic ticks in every accepted process, within the fixed 4715 ceiling.

Fourteen complete original semantic streams and control excluding wall time match
baseline. Indexed pixels, shot state, collision, presentation RNG, clocks, original
fire/allocation/removal and loadout observations remain equal. Exact alpha and SDL
nearest-sampling checks verify each selected 12×14 rectangle; changed authored pixels
survive ordinary later composition. Candidate 2× whole-frame differences lie only
inside actual shell draw rectangles. The 4× internal 8× planes equal candidate 2×.
Missing-147 declines both shells; both corrected full native frames exactly equal
baseline, with no cropped or excluded terrain pixels.

## Failed fixture and controlled replacement

The fourth process used a private fallback pack whose forest13.policy was a
symlink. The unchanged lstat regular-file guard rejected it, triggering unrelated
terrain fallback although the 29 resolved bytes matched. Shell fallback itself did
not explain the whole-frame differences. The failed run and images are preserved.
One independently reviewed and explicitly authorized fifth process used the same
policy bytes as a regular file. No production source, art, binary, observation
window, selected identity or numeric acceptance rule changed. The corrected
full-frame check passes; no automatic retry or guard relaxation occurred.

## Exact private controls and remaining limits

Linux software-renderer replay uses original stationary/no-fire input, seed 0x5eed,
Normal/story Episode 1 physical level 9, no-xmas and original tank events. A private,
symmetric alive-only invulnerability floor 2 after original events keeps the player
alive. This is controlled survival, not natural manual play. No shot/enemy injection,
position override, background suppression or later search is used. Private controls
and observers are not included in production.

Actual selected backgrounds cover cliff/stone and dark metal/stone boundaries.
Dark-forest readability belongs to the earlier art-only composite. Nearby bright
cloud does not prove selected-shell/cloud overlap or foreground-cloud occlusion.
No Windows/manual-input/GPU/fullscreen, all-level/all-mode/all-emitter, general
background/overlap, real-time or performance acceptance is claimed. Source-normal/
Xmas units do not imply a Xmas runtime replay.

The final author review checked all 18 retained PNG/RGBA hashes and inspected
the 16 accepted images, while preserving the 2 failed images as failed evidence.
Physical-shell identity, fixed headings, clean fractional-alpha contours and
registration pass. The selected 147 initially overlaps its original turret barrel
and separates without a visible jump; this is not a general overlap guarantee.

See source-unit-summary.json, runtime-summary.json, author-review-summary.json
and pixel-review.json for portable receipts. The art README documents exact wrapper reproduction from shipped canonical
PNGs; historical generated masters and original game data remain external.
