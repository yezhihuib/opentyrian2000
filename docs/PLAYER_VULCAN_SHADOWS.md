# Normal Vulcan67/70: finite smooth shadow display

This local correction starts from the accepted two-head Vulcan baseline
4e75dbda875922303fda92d514fe6d9755e40696. It adds no assets and changes no
projectile, weapon, position, eligibility, collision, timing, or random state.
The original shadow condition and shadow-before-own-head call order are intact.
Protron, green, Charge and Missile shadows retain their previous behavior.

## Coverage and intensity

Only normal player bank8/TILE67 and70 shadow calls are admitted. The same
frozen density8 RGBA head resources supply alpha only; their RGB is unused.
The original shadow origin stays (headX, headY + 10). Complete accepted alpha
includes respectively78 and110 density8 samples outside original RLE support,
always within the original12x14 rectangle. These are display-only samples:
no indexed writes, source geometry, head position, or extra shadow is added.

Each subpixel starts from the already-composed underlay at this actual command:

- Indexed background: coverage blend toward the current palette color of
  D(i) = (i & 240) | floor((i & 15) / 2).
- Authored cloud background: coverage blend toward the existing before-to-after
  palette channel-ratio transfer. Zero denominator channels retain their
  authored value; unchanged indices at the ramp floor are exact no-ops.
- Other HD background: coverage blend toward the existing full-strength
  darken_rgba(color,255) result. The full operator is rounded first, followed
  by the existing integer alpha blend. This preserves the current HD analogue
  and explicitly differs from applying darken_rgba(color,alpha) directly.

Existing cloud provenance is retained rather than painting a gray head or
assigning cloud ownership to the whole footprint. An original covered write
that changes an indexed byte claims display-divergence ownership even where
alpha is zero, keeping the actual preserved underlay through later fades.

## One-command lifetime

The entity hook prepares only validated metadata. The original darken blitter
provides its exact surface, bank, source ID and origin at entry. Only a matching
entry can sample the underlay and compose the smooth shadow. It then executes
every original indexed operation, once and in its unchanged order. Visible
original support writes consume their matching one-call coverage exactly once.
Both normal and vertically clipped exits clear the association.

An intervening or mismatched call cancels a still-pending preparation without
visual residue. Once composition starts, incomplete, duplicate or unexpected
writes reject the HD frame rather than replaying an earlier layer. Frame begin
resets the display. Ordinary later draws overwrite the shadow at their original
positions. The finite rectangle is registered for existing local restoration.
There are no persistent projectile fields, global shadow pass, delayed replay,
or association with a most-recent or neighboring head.

## Validation and fallback

Normal mode, active surface and density8 guards precede warm cache acceptance.
The semantic original source (indices plus support) and full frozen RGBA payload
are fingerprinted at preparation and again at the matching actual blitter entry.
This catches source reload/address reuse and mutated in-memory resources.
The two loaded resource identities retain their exact load path and allocation;
a changed resource root cannot reuse an old shadow entry. Other asset-loader
and head-cache semantics are unchanged.

The resource epoch is the existing immutable loaded asset epoch. Changing or
removing an on-disk file after a successful load does not invalidate frozen
bytes already held by the head loader. A changed root, invalid/missing runtime
flag, non-frozen cached bytes, absent cold file, invalid resource, Christmas
source, or density4 fallback disables this finite shadow treatment. No live
filesystem polling or new reload facility is introduced.

Horizontal physical-address wrapping is declined. A target equal to both the
game surface and VGAScreen with matching padded indexed pitch is supported;
Cartesian top/bottom clipping retains the original indexed physical writes.
Unsupported paths keep their existing classic shadow behavior.

Production changes are limited to render_mirror.c, two declarations/disabled
stubs in render_mirror.h, and finite entry/end calls in blit_sprite2_darken.
Removing those sprite hooks restores the original source byte-for-byte.
Focused extracted-source tests and bounded native2x P1/P7 runtime verification
are recorded separately; this document alone is not a runtime PASS receipt.

## Bounded actual acceptance

Two new P1/P7 native 2x runs passed against unchanged retained old-shadow
captures, with independent numeric and author review. See the
[portable runtime summary](player-vulcan-shadow-v1/README.md) for exact scope,
negative-x fallbacks and limitations. No publication is implied by local checks.
