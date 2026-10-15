# Plasma Storm body: finite five-frame renderer batch

Baseline b1a8927fb9e892f87452813010cd206e069cc413, tree
 a31d6b78214e592e4d4a8615762854ff692d19a0.

## Production boundary

Only option9/style0/charge0 bank9 TILE body frames224/243/262/281/300 enter
role129, slots541 through545. The original12x14 canvas, anchor0,0 and
sidekick.x,y origin are retained. Every wrapper always performs exactly one
original indexed blit_sprite2 and ends the ordered mirror entity. There is no
new shadow. Existing weapon88's three simultaneous variable-size raw blend
pieces, shots, collision, ammo, timing, RNG, placement and unrelated weapons
remain byte-identical to the published baseline.

The original initialization already enables this animation at phase0. Its
increment-before-draw first phase1 and twenty-phase loop, four phases per
source frame, remain unchanged. Firing does not introduce a new animation or
reset. Every cold or warm lookup rechecks current bank pointer/size and
boundedly decodes all168 indices plus168 coverage bytes into zeroed buffers
before matching exact current semantic identity. Identical normal and Christmas
sources are eligible subject to the unchanged scene rules. Wrong/malformed
source or resources fall back to original indexed rendering. Each frame has
independent8-to4-to-indexed fallback. Horizontal row-wrap is conservatively
excluded from HD while original indexed edge writes remain exact.

## Frozen resources

Five independently generated and reviewed masters use one identical fixed
crop(84,74,1124,1226), LANCZOS resize88x104 and paste0,0 into96x112. There is
no per-frame alignment, recolor, threshold, original-source mask, shell
compositing or pixel repair. The silver T/pedestal has subtle generated
micro-luminance drift; it is not pixel-static. Later top caps are darker and
frame262 lacks the original mild neck pre-brightening. The fixed crop clips a
very small edge area in281/300, below0.04 logical-pixel equivalent each.
These disclosed tradeoffs were retained through actual native2x visual review.

Each default pack grows549 to554 listed resources and560 to565 physical
files, including560 HDA and five auxiliaries. Every previous physical byte,
including six unlisted HDA, remains present. All3378 old files across18packs
are preserved; other16packs are unchanged. The verifier compares exact baseline
blob identities and the finite addition allowlist, independent of git staging.
Run python3 prototype/build-plasma-body-art.py for exact art reconstruction and
pack verification. Generated masters are included; original game data, extracted
source pixels, runtime fixtures, logs, screens and binaries are not.

## Qualification

Exactly four original-engine processes completed320 ticks each: published
baseline and final candidate in Normal physical9 and Hard physical15. Ordinary
first-shop input actually buys the right Plasma Storm for9500 from10000,
leaving500 and leftNone/right9. No equipment, cash, position, invulnerability,
animation, refill, time or RNG override is used. All four processes naturally
retain the same untouched time(NULL) seed and exit0 without rerunning.
Every paired tick's indexed surfaces, palettes, explicit player/enemy/shot/
particle/global state, RNG and original input/draw/fire/blend events match.
The sole allowed added observer event records candidate HD body admission.

Every process keeps320 original body calls,97 original writes each, and all
five phase IDs. Space main fire alone never requests weapon88. Ordinary LeftAlt
presses at100/108/116/124/132/140 consume the six limited shots. Each requests
three simultaneous pieces:18 emissions, six each of raw60023/60024/60025.
Their312 raw blend draws retain separate slots/order, actual sizes62x24,
65x28 and62x23, and original blend destination/source-cell traces. An empty
seventh press at148 emits nothing. End ammo is0 with95 refill ticks remaining;
a later actual refill event is not qualified by this window.

All92 untouched640x400 native2x PNGs pass chunk CRCs, including IEND. All40
gameplay pairs differ only inside the original12x14 logical body canvas; six
shop pairs match. Normal/Hard body contacts and actual full screens were
visually accepted with no conspicuous geometric frame jump. Normal's97 original
body support cells are lit throughout. Hard has one ordinary all-lit tick and
319 NIGHT ticks with transition/dark support cells only, including23/74,
31/66,17/80 and12/85 transition/dark splits. This is source-cell evidence,
not a claim about all authored alpha subpixels or fully lit NIGHT body coverage.
Natural noninvulnerable occupied body/Talon overlap occurs on28ticks per case,
up to26cells, but no fixed screenshot coincides, so no overlap screenshot is
claimed. Actual right purchase only, not left/dual purchase, is qualified.

Focused optimized and ASan/UBSan tests pass with synthetic fixtures and the
accepted production art. They cover current source identity/coverage changes,
normal/Christmas cold/warm reloads, malformed resources, per-frame8-to4 fallback,
original dispatch/animation, clipping/row-wrap, overlap and duplicate calls.
All153 production sources inverse byte-exactly after removing the finite
five-file additions; seven forbidden scope changes are rejected. All72
translation units link; the classic-disabled renderer boundary compiles.
See verification.json. No actual Christmas gameplay, whole-level/campaign,
Windows, physical GPU or performance claim is made.
