# ASTEROID1 NEWSHS272 continuous reactor pulse

This checkpoint adds the complete four-image record 272 family to the existing
normal-data Episode 1 physical-level 1 ASTEROID1 opt-in:
`--asteroid-hd-assets=assets/hd/packs/asteroid1-ten-v1`. The option only enables
the renderer; it does not select or play a level. The optional catalog now has
57 images, 20 independent families and 52 source-record dependencies. All previous
53 PNG/HDR1 pairs, 19 family metadata entries and both 629-entry default catalogs
remain unchanged.

## Source, actor identity and original lifecycle

Logical bank 23 is NEWSHS, exactly 46,566 bytes with FNV1a64
`f22ec1295ced5d11`. The family reuses only the renderer-owned immutable NEWSHS
byte-equality helper already used by record 325. It independently pins all 77
serialized source-record 272 bytes to `2f2c9491d2030153` on every callback.
Changing 325 alone disables 325 alone; changing 272 disables 272 alone; changing
the current NEWSHS bytes disables both. The separate NEWSHD 42,012-byte and
NEWSHP 46,204-byte snapshots are unchanged. Loaded-bank selection accepts any of
the four correct logical-23 slots. The live actor must bind the actual slot's
Sprite2_array object; unloaded clones, copied objects, ordinary spriteSheet8,
foreign bank IDs, cold/warm corruption and stale/reused bindings are excluded.

Seven independent original event 6 actors spawn in pool 25..49 at curLoc 3940
(x66/90),6040 (x162/210),6208 (x90),6768 (x114/90). The unrelated original 276 event
between the6040 actors retains its allocation and order. No partner, adjacent
slot, complete group or fixed position is required. The original first-free
allocator, failures and holes remain authoritative. Constructors consume no
positioning RNG. Each composite uses the four original 12x14 calls in order
0/1/19/20, preserving independent row/side clipping and actor-relative scrolling.

The complete eighteen-entry source sequence is:
229,229,229,233,233,233,235,235,235,233,233,233,231,231,231,229,229,229.
Stored entries19/20 remain zero and are pinned too. Horizontal eligibility
controls the original pre-increment from constructor cycle 0 to 1 and wrap 18 to 1.
Vertical invisibility and ice do not pause animation. The hidden first update
has no quadrant call; at ordinary backMove 2 the first lower callbacks occur at
cycle 3, and the first HD-bounds-eligible lower call occurs at cycle 5. There is
no added cadence, interpolation, flash, firing state or actor simulation.

Original source explosiontype 5 yields ground=false and explonum 2. Legitimate
positive difficulty-scaled/hit-reduced armor, ice, inactive shot/launch timers,
backscroll and bounce metadata remain simulation-owned. Nonlethal player shots
reduce only the struck armor; there is no alternate damage image. Lethal shots
run the unchanged original link0/sentinel255 destruction search, freeing only
the struck actor and retaining normal effects, counters, sounds and RNG. Value 0
and death-child 0 produce no cash, cube, child, drop or persistent wreck. The
normal shared explosion route remains classic. Odd source 5 excludes the
ordinary ship-ram damage branch. There are no firing or launch dependencies.

## Authored artwork and material isolation

Built-in imagegen authored a smooth grey/charcoal 2D metal housing with a deep-red
oval lens and warm orange rim, then three lens-illumination edits. Four generated
masters, exact prompts/provenance, final PNGs and a deterministic converter are
retained. The common 229 master is identical in every state outside the exact
original 288-index-cell difference union, bbox[4,4,15,20]. All 672 source cells are
opaque, including dark machinery/floor-looking borders. Generated states are
registered by full-canvas 192x224 normalization; the converter only resizes and
composites authored samples inside the source union. It does not draw geometry,
recolor artwork, change original data or create extra animation entries.

New material 136 is deliberately distinct from source-bank 23. Existing NEWSHD286
already owns all four material 108/base tuples, and NEWSHP341/342 own material 135
bases 229/231. Existing NEWSHS325 remains material 108. The new roles are
1360229/1360231/1360233/1360235. Each HDR1 has density 8, logical 24x28, anchor 0/0 and
exact 172060-byte length. Internal density 8 is separate from native display 2x/4x.
Typed 272 dispatch, header identity, accepted commands, regions and finite catalog
family/base allowlists retain 136. Generic read_asset rejects 136, and the draw
path admits 136 only under a short private pointer lease from the guarded family.

All four images preflight before the first replacement. Missing, corrupt,
foreign-role, malformed-header, wrong-density/anchor/length and payload failures
fall back for the whole 272 family, sticky until root/cache reset. The private
family payloads are revalidated once per display frame; current source bytes
are compared on every callback. Losing a dependency after an accepted quadrant
rejects the whole HD frame. Peer families remain independent.

## Validation and evidence boundary

See validation.json for exact final receipts and native-window coverage.
Optimized and ASan/UBSan new-family tests each exercise 77 cold plus 77 warm record
byte mutations across every member, 20788 positive HD admissions, all 18 cycles and
four images, 4080 production animation comparisons, 96 allocator cases, 35 original
shot-damage cases and 68 bad-resource fixtures. The extracted original ram
predicate/body excludes all 255 positive armor values times 256 ice values, with
a positive control proving the branch is executable. Original constructor,
event 6, ordered draw, collision, explosion allocation, repeating effects and MT
RNG are used. Extracted tests cover side boundaries and malformed actors without
changing the real-game evidence.

The shared source suite passes 6812 checks in each mode across 20 families and 52
dependencies: 17 NEWSHD/45, 2 NEWSHS/2, 1 NEWSHP/5. The finite catalog-only verifier
checks all 57 optional pairs and both 629-entry defaults through the explicitly
required historical validation input, without rebuilding artwork. That input
is external validation data, never a public runtime path.

The prior 269, 325, 287/288 and 338–342 runtime suites pass optimized and
ASan/UBSan, and all 18 associated authored images rebuild exactly. A clean strict
production build compiles all 81 C sources and links with zero warnings.

Actual-engine validation completes 84 paired cases/168 runs and 13,200 logic ticks:
8 intact site/scale pairs, 2 genuine partial/lethal pairs, 2 early-entry pose pairs,
and 72 negative pairs. Every site at both scales exercises each of four missing
members, each of four corrupt members, and flag-off. All 2,184 trace comparisons
are exact, 7,392 new material 136 commands preserve 31,228 previous-family commands,
and no frame has a coverage mismatch or integrity rejection.

Actual-engine evidence uses explicitly ASSISTED original-event windows at all
four sites with raw events, original setup/spawn order, real allocation and
selector RNG preserved; omitted prefix actors are disclosed. No actor/projectile
injection, healing, resurrection or forced graphics is used. Ordinary movement
and fire supply genuine player-shot partial/lethal witnesses. At this family checkpoint, the damage contact exposed a shared-
effects rendering issue: an original palette-blend pixel restores the complete
24x28 body region to classic, despite all four material 136 calls being accepted.
At tick 28 this restores (95,21,24,28), replacing 590 HD blocks; 672 classic blocks
are checked with no mismatch. The then-existing ASTEROID blend path bypassed per-effect
index attribution, so its source_index 0 trace cannot identify one exact explosion
sprite. This family checkpoint did not fix that shared-effects path or claim visually fixed
damage overlap. A later [scoped warm/contact fix](../asteroid1-warm-contact-blend-v1/README.md)
authenticates original effects, identifies the trigger as index151 and preserves
the HD body through the witnessed overlap; its other-effect limits are explicit. The damage captures prove original processing and gameplay
preservation, not an alternate authored damage pose. These finite
windows do not claim a natural campaign playthrough. Original gameplay, INDEX8,
RNG, event/actor/call traces and the exact prior 53 accepted-command subsequence
are compared against baseline 8ef127de at native 2x/4x.

The selected source placements do not cross side viewport edges; no actual-engine
side-clipping witness is claimed. Extracted production tests cover those
boundaries. Runs use headless SDL dummy video/software rendering, with unresized
640x400 and 1280x800 captures, rather than a desktop-window check. No Windows
build, remote push or publication is included. Original inputs, native captures,
test harnesses and binaries remain external. LeakSanitizer is disabled;
AddressSanitizer and UndefinedBehaviorSanitizer run. Runtime RSS is bounded to
512 MiB, compiler address space to 1 GiB, and free disk reserve to at least 5 GB.
