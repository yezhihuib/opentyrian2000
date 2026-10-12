# Coordinated linked31 installation

Exactly eight new8x resources form one selected-pack family:

- shapesZ Layer3 IDs161,162,171,172: slots374–377,24×28 logical, anchor0,0.
- newsh2 bases15,17,53,55 for types42–45: slots378–381, complete24×28 composites, anchor6,7; existing quadrant offsets0,1,19,20 remain unchanged.
- The original actor assembly is one logical pixel below terrain. No offset is added by this binding.

Both routes use the same cached preflight before the first member can draw. It validates all eight selected-pack8x HDR1 headers, exact size, geometry, anchors and opaque alpha. Missing, truncated, trailing, bad-header, allocation-failed or nonopaque members disable the entire family. Other accepted assets remain independent. Both scene-family bits must be enabled. There is no4x fallback for this family and no new filter/compositor/sampler.

The selected pack is assigned only during startup argument parsing. Asset-debug reload exits with75 and requests a fresh process, so the family cache follows the existing Asset lifetime. A failed family remains failed until that restart; there is no per-frame I/O/retry. This does not implement live pack swapping.

## Source lifecycle clarification

The frozen artwork package is retained byte-for-byte. Its generic ground-filter wording is qualified by the independently decoded records: all four have explosiontype9. The sole production initialization sets enemyground=(explosiontype&1)==0, hence false, and explonum=4. See LINKED31_SOURCE_BEHAVIOR.json. These flags are not changed by the binding.

All four records are static, armor12, dgr/dani/dlevel0, with no independent damaged sprite. Ordinary nonlethal damage changes only the struck member's armor and keeps its pose. Original damage99 sets that target's iced counter to40 and damage0; the ground-only filter and linked-ice propagation conditions are false for this family. This source fact must not be presented as a blue-tinted or group-iced actual state. Generic renderer filter tests remain useful coverage of the unchanged filter path, separately from reachable lifecycle behavior.

A lethal hit enters the original same-link31 removal loop, marks all four unavailable, awards their existing value and invokes the original large-air explosion/repeater routines. The four static terrain pieces then become exposed. No enemy state, collision, RNG, event, movement, draw order, death timing or effects routine is edited.

## Source verification

- build-linked31-art.py: generated-only canonical PNG/RGBA/HDR1 rebuild; optional original terrain/RLE support audit and all1701 bank-qualified enemy records; unchanged neighboring artwork guards.
- test-linked31-binding.py: extracted production loader, both routes and filter helper under ASan/UBSan; both first-route orders;89 full/missing/corrupt cases; all8 allocation-failure positions; cached retry behavior and fresh-cache recovery; scene bits0/1/2; all192 prior successful bindings unchanged. LSan cannot run under executor ptrace and is not claimed.
- test-linked31-source-guards.py:17 generated-source/import/output-path negative guards with one minimal tree, no repeated pack copies.
- test-linked31-preservation.py: exact finite renderer restoration to baseline;5557 prior tracked files audited;533,996,009 prior asset payload bytes identical; prior manifest restored exactly; unchanged Windows XML with all existing compile references present.
- Central verification:3012 HDA entries,402 canonical PNGs, both default pack counts386/390, all HUD/startup/material sidecars retained. Linux compilation and nine startup package tests pass.

These source/loader checks are complemented by the bounded actual results below. No Windows compilation/runtime or full-level acceptance is claimed.

## Bounded private runtime verification

The existing private survival/readback harness queued three diagnostic projectiles for slot50 through asset_debug_projectile's existing player_shot_create(Pulse155) path: damage1 at4901, damage99 at4903, and current armor11 at4905. The original player_shot_move_and_draw and collision/removal/explosion branches were untouched; only read-only enemyground/iced/explonum observations were added. No fixture hooks enter production.

The paired original/candidate replay covered all4936 ticks through4935. Complete state, indexed game/output pixels and RNG matched, as did17 original source streams. All36 native2x frames had zero differences outside the eight-member family support. Intact4900 exposes10,752 exact authored actor pixels. Ordinary hit changed only the target armor12→11; ice changed only its counter to40 with filter0. All four original link31 members were removed together at4905. The final explosion renders at4930;4931 is the first fully clear reveal, matching10,752 authored underlay pixels exactly. Original later spawns reuse freed slots, so continued absence is tracked by source-qualified family identity.

One genuine1280×800 native4x still at4931 matches43,008 authored underlay pixels, with all4932 preceding state/indexed/RNG ticks and internal RGB/frame audits equal to2x. One36-frame640×400 clip is available at12fps for review; that rate is explicitly a review speed.

Three additional hashes-only trials prove atomic fallback when terrain161 is missing, actor15 is missing, or actor53 has corrupt alpha: all eight retain original rendering and all36 complete internal RGB hashes equal baseline. No extra videos were made. Initial symlink-mirrored fixture trials were excluded because preexisting forest/material sidecar guards reject symlinks; corrected zero-copy hardlink fixtures pass. These excluded trials do not count as acceptance.

See LINKED31_RUNTIME_VALIDATION.json for the measured results, media hashes, explicit exclusions and limits. LINKED31_AUTHOR_SOURCE_CLARIFICATION.json independently confirms the immutable-art lifecycle correction. This is private diagnostic combat evidence; natural manual combat, full-level playthrough, GPU/fullscreen and Windows remain unverified.

Artist review passed all36 chronological native2x frames and the native4x reveal with independent PNG/RGBA/BGRA hash checks; no artwork changes were needed. See LINKED31_AUTHOR_REVIEW.json.
