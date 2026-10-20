# ASTEROID1 NEWSHS276 vertical-column animation

This checkpoint adds exactly six record276 images to the normal-data Episode1
physical-level1 ASTEROID1 opt-in. The optional pack now contains69 images,
22 independently preflighted families and54 source-record dependencies. Previous
63 payload/PNG entries,21 family entries and both629-entry default catalogs
remain unchanged. Enable with `--asteroid-hd-assets=assets/hd/packs/asteroid1-ten-v1`;
this selects a renderer, not a level.

## Original identity and timing

The complete77-byte original record276 is pinned to FNV1a64
`5ef5beadaa8fd4df`. Its loaded logical-bank23 NEWSHS is46,566 bytes, FNV1a64
`f22ec1295ced5d11`. Only its18 active image words differ from275; constructor,
animation, damage and movement fields match. The renderer shares immutable bank
byte authentication, never another family's record/payload/lease identity.

Two actual event6 actors occur at5676 (ordinal349, source x114) and6040
(ordinal369, source x186). These are independent single actors, not a pair.
At6040 an earlier272 actor takes pool slot25, leaving276 in26; no fixed pool slot
is required. The original first-free allocation, event order, map offsets,
clipping and quadrant callback order0/1/19/20 remain authoritative.

The exact18-state sequence is
191,191,193,193,191,191,195,195,197,197,195,195,199,199,201,201,199,199.
Two unused image words stay zero. There is no added interpolation, cadence,
positioning or actor simulation. The original first site reaches a scroll-stop
at5769 and remains visible when not fired upon; tests preserve that behavior,
not force a natural cull. The second site's actor naturally culls.

Default armor12, value0, no weapons, launch, link, drop or alternate damage
image. Explosiontype5 means enemyground=false and explonum2, despite event6's
pool assignment. The normal player-ram predicate must remain non-colliding for
all legitimate positive armor and ice values. Ordinary player shots still
produce original partial damage and independent link0 destruction. No cash,
child, persistent wreck or new effect is introduced.

## Authored art and material boundary

Built-in imagegen authored three vertical red-glass columns within an opaque
grey/charcoal metal housing, plus five lighting-only edits. Actual original
references were viewed and existing275 artwork supplied material style only,
not rotated geometry. Right, middle and left columns illuminate in original
sequence order. The source pulse is red; no orange/yellow pulse is invented.
Six generated masters, exact prompts and reproducible converter are retained.

Canvas normalization uses LANCZOS to192x224, logical24x28, density8, anchor0/0.
All672 original cells are opaque. Every state shares191's housing outside the
exact independently decoded387-cell source-index difference union,
bbox[0,4,24,20]. Inside it, authored state samples are registered without
procedural recoloring, code-drawn geometry or new animation. Portable tests
verify exact rebuilds, all30 directed state differences and each authentic
low/high red-energy pair. Density8 is separate from display2x/4x.

New material138 has roles1380191/193/195/197/199/201. Each HDR1 is172060 bytes
with exact identity, dimensions, density and pinned RGBA. All six resources
preflight before a quadrant is replaced; any missing/corrupt/foreign member
fails this family closed. Existing image-bank roles108/135/136/137 cannot borrow
its private Asset pointer lease. Generic loading rejects138. Current source
bytes, live actor object binding, exact cycle and original position, level,
INDEX8 surface/layout, filter, clipping and presentation guards all remain.
Resources are immutable and checked each display frame; a dependency failure
following an accepted quadrant rejects the HD frame. Shutdown frees all members.
No broad renderer or shared effect admission changes are included.

## Verification and scope

See validation.json for final receipts. Extracted production tests cover the
real constructor, event6 dispatch, animation, indexed blitter, ordinary shot,
ice/lethal processing and ram predicate. Both original events are exercised
under allocation pressure, holes and neighboring actors. Optimized and
ASan/UBSan runs cover all source bytes cold/warm, six payload identities and
cross-material/private-lease failures. LeakSanitizer is disabled in this
executor; this is not a leak-proof claim.

Native2x/4x software-renderer evidence covers both actual sites, all six states,
ordinary partial/lethal damage and per-member missing/corrupt plus flag-off
controls. Assisted prefix skips and original setup replay are disclosed;
original eventRec bytes and selector RNG remain exact. No actor injection,
resurrection, healing, forced graphics, game logic or original-data edits occur.
Headless SDL readback is not desktop-interactive, GPU, Windows, natural-campaign
or whole-level certification. Existing renderer limitations remain unchanged.

### Final observed result

All60 successful paired native cases pass:120 runs,8,000 logic ticks and416
paired native PNG captures. The eight positive pairs cover intact animation and
ordinary partial/lethal shots at both sites/scales. The52 negative pairs cover
each of six missing and six payload-corrupt members plus flag-off at each site
and scale. Every negative TSV/PNG is baseline-exact. There are2,544 new138
commands and74,132 retained prior108/136 commands; original gameplay/events,
collisions/effects/RNG/INDEX8 and callback ordering remain exact. Coverage
mismatches and rejected frames are zero, and captured changes stay within
original276 canvases. Existing903/487 known effect-blend writes over276 per
scale at the two sites preserve the visual effects without full-region rollback.

The first no-fire actor remains alive at the genuine5769 scroll-stop; the
second naturally culls at tick110. Ordinary shots produce true partial damage
and lethal processing, not a separately authored damage pose. No native side
clipping or nonzero-filter damage-pose claim is made. An initial test-launch
batch incorrectly requested40 ticks below the engine's60-tick minimum; those27
pre-gameplay exits and one145-tick discovery are retained but excluded from
all acceptance totals. Corrected controls use60 ticks. The final source comment
correction was recompiled to a byte-identical native object and the complete
extracted suite rerun; receipts match the final source.

Optimized and ASan/UBSan each pass1 positive plus114 negative276 fixtures,
11,100 admissions,4,080 animation comparisons,48 allocation cases and10 damage
cases. Prior272/275 suites pass1+68 and1+108 fixtures per mode. Warm/shield/Talon
regression again passes3,265,773 checks in each mode with actual Talon source
coverage enabled. Full catalog verification passes both629-entry defaults and
all69 optional pairs using explicitly named historical dependencies where needed.
