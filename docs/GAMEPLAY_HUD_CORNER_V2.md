# Gameplay HUD bottom-right corner V2

This finite revision refines the narrow brace and grille termination at logical
[248,184,269,200). The user rejected V1's discontinuous rail and subsequently
accepted this continuity-preserving V2. No other frame or meter art is revised.

## Ownership and fallback

The rectangle has 336 cells: 150 previously owned cells remain byte-exact and
186 are newly eligible, including 46 pinned source-zero cells. The static union
is 6,853 cells. All 6,667 previous frame cells retain their exact RGBA. Ten black
seam cells preserve the rail profile; 176 interior cells receive new metal.

The existing single-player PIC3, surface, palette and lifecycle guards remain.
Every indexed cell of the 336-cell rectangle must match the captured original
PIC3 region (FNV64 ca5548b4cdd8767a). Any mismatch suppresses the whole corner,
including its 150 old cells, so long message tails remain original. The bounded
source-zero exception applies only to the exact union mask and pinned PIC3/region source identities.
Missing or invalid HUD resources use the existing classic HUD fallback without
turning off unrelated scene HD. No message erase, gameplay or palette logic changes.

## Source reconstruction

The historical V5 source package and its 4ff6cd95… HUD1 remain immutable. The V2
package imports the authored source and audit files from the frozen trial package;
IMPORT.json records omission of two redundant rebuilt-output directories. Its
freeze-time README predates user and actual acceptance and remains unmodified.

Run `python prototype/build-gameplay-hud-art.py --output /absolute/fresh/path`.
This rebuilds V5 from its original generated components, then derives V2 from the
pinned V5 bytes and generated junction master. `build-hd-assets.py` independently
reconstructs and checks both selected default pack resources. The resulting HUD1
SHA256 is 98cd6cfefa02a9ae79b75a65e02dd2566d3dec1492552f20b042b3c61c19cd17.
No original game image, private fixture or capture is included.

## Bounded validation

Independent source review and ASan/UBSan verify all 336 single-cell mismatches,
source-zero restrictions, long-to-short message/expiry tails, fades and modal
restoration. Legacy V5 output/cache/fade digests match the published parent.
Those lifecycle cases are source-level tests, not a claim of natural death or
end-level runtime coverage.

Actual native 2× tick250 and true 4× tick250 use the same normal-input debug
fixture as the accepted HUD checkpoint. All 33 retained original ledgers match
through 251 ticks. At 2×, 662 changed pixels are confined to the corner; all old
frame pixels and HUC1/HUL1/playfield pixels are unchanged. A fresh paired 60-tick
run supplies ten hash-only presentations per side with the same scope/state
proof. Canonical 4× art and 4×→2× nearest samples match exactly within the corner;
whole-frame cross-scale equality is not claimed. Author and root visual review
pass both native scales. No new Windows compilation/runtime or CI claim is made.

Fixed typography, dynamic fonts and meter revisions remain separate candidates.
