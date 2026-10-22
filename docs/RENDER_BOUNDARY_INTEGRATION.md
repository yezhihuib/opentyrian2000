# Reviewed render-boundary integration

The render-only predecessor (`ab16f187d27ca53812d1e897afa209d35d44c9e4`)
starts from public commit
`6ada526fa11c633e3ae02facb5f498bbfdacd1d9`, tree
`ca0b415afd576e29fcb8ac5dcbe3ed9025f30fb2`. It retains the six-body authoring
foundation, its selected artwork and existing runtime qualifications.

The supplied eight-file patch has SHA256
`fc9f2dfa859fb59a29c95b0bab323164850308cda25621d8ad90c6b7f9cdf55a`.
The qualified-source Talon follow-up was reviewed at
`5cc0bccc6a1500a153b6b1e06cf717a747a56a92`. This integration applies their
production changes without altering the original blitters, game logic,
resource identities, raw-bank pins, HDA art or generated payload pins.

## Current source versus historical evidence

Exactly two production files differ from the integration base:
`src/render_mirror.c` and `src/global_talon_mirror.inc`. The current
`packaging/current-production-validation.json` binds all 252 actual source
files, the fixed build inputs and both unchanged historical validation
receipts. `packaging/runtime-assets-v1.json` is regenerated from the existing
pinned base and current selections. It retains all 1006 destinations; only the
current-production binding row and its source-manifest digest change.

Historical `current-source-inventory.json`, the older feature ledgers and
frontend/global receipts remain immutable. The new
`tests/fixtures/accepted-later-changes-v1/render-boundaries-source.json` records
the exact two-file correction: whole current SHA256, every finite inverse hunk
and whole previous SHA256, with the public integration base and input patch
identity. Its bytes are pinned in `accepted_later_changes.py`.

Older feature source oracles undo this correction first, then apply their
original named inverse. This proves the historical bytes separately; it does
not claim that current production bytes are unchanged from 775. Current source
validation checks the real files and exact inverse, while the generated
sidekick source/asset proof requires the real current source binding. Added,
deleted, reverted or arbitrarily modified source remains rejected, including
mutations inside the accepted hunks. There is no prefix or suffix exemption.

Future authoring regeneration retains the current rendering bytes in the
source inventory and runtime binding. The six-sidekick payload header remains
a Python build/package consistency input, with no new production C include or
runtime payload enforcement.

## Bounded regression contract

- The generic fixture uses production admission/cache/compositor/pixel and
  original indexed blitter/wrapper extraction, synthetic RLE, selected
  tile/quad edges and pointer/size cache sequences. Existing MSVC `/O2` and
  AddressSanitizer modes are supported; the original cc path remains available.
- The Talon fixture qualifies the externally supplied original bank before
  frame_begin and before invalidation, loads 13 pinned HDA resources through
  production code and creates contributions through the real Talon draw.
  RGB/owner/contributed state is not seeded. Its four failure cases and three
  positive controls run at 4x/8x for one pose and selected pixels.
- Stable Talon contributions are checked both while owned and after all owner
  bits transfer. The pointer control replaces a qualified original with an
  intentionally unqualified zero-filled new bank; it does not demand rejection
  of an identical qualified clone. Palette pins are from the registry; the
  remaining palette is a synthetic grayscale underlay.
- Wrong expectations and missing resources must produce nonzero controls.
  The HDA fixture covers ordinary synthetic header/payload/allocation controls.
- Current source/asset projection and package-binding negative controls are
  retained, together with the four existing Data frame/portrait, rear P1 and
  Storm historical source oracles. Native link creation previously denied by
  Windows is not retried; portable alias-guard controls retain their scope.

These are finite extraction/SDL-structure-shim tests, with MSVC ASan and no
UBSan or LeakSanitizer in the native Windows runs. Their finish/ready/retained
states and selected output pixels do not establish actual SDL Present, the
native game caller, GPU/compositor, natural gameplay or whole-level acceptance.
The four retained historical oracles also keep their existing scope; no full
long suite or additional visual acceptance is implied by this integration.

Original `tyrian.shp` bytes are read-only and pass through memory/stdin only;
they are not included in source, receipts, commits or delivery archives. The
six new artwork samples and enemy267 are outside that render-only predecessor.

The authoring builder's whole-source authority digest is refreshed to this
exact current source inventory. The old digest is provenance, not an alternate
accepted value: reverting either corrected file or mutating an accepted hunk
remains rejected even with a freshly rebound source manifest. Registry
role/source and build-input authority checks stay unchanged.

The retained portrait regeneration oracle exposed native Windows newline
translation in its JSON/pin text exporter. Those two writes now emit explicit
UTF-8 LF bytes, matching the frozen Linux-generated artifacts exactly; no
portrait pixels, HDA payloads or production pins change.

## Prepared combination with the approved six-body selection

The isolated combined candidate is based on exact
`e556698ace6c52b4b94c079cb24c22d29807127a` (tree
`f85e7a03f57ba7bd0ac2e9401ec5f039409860a4`), whose parent is the approved
six-body artwork commit `7e0fb3685293b1ce54fb117a4ca527b934e79773`.
It retains all six approved PNG/HDA bytes and the e556 test semantics split:
current selection is checked independently against decoded PNG RGBA, while
old bootstrap bytes are rebuilt in a fixed historical fixture.

The retained original positive test additionally validates the true current
source binding and applies only the already pinned two-file rendering inverse
before comparing all 251 historical source bytes. Every other old source is
still compared directly. This closes the stale blanket 775 assertion without
removing it, adding path skips or claiming that current rendering code equals
775. The bootstrap fixture and all older ledgers retain their exact bytes.

The current 252-source binding and 1006-destination manifest are regenerated
for the combined inputs. The new PNGs live under `authoring-inputs/`, so the
historical `assets/` inventory needs no new exception. Existing source/asset
projection rules, resource authority, runtime roles, geometry and phase remain
unchanged. No production implementation is added beyond the reviewed original
two-file rendering correction.

This is local preparation pending independent review and confirmation that
e556 is actually available from the intended remote with the exact same tree.
It is not publication authorization, a remote push, or a formal game update.
