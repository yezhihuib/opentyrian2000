# Shared Cash25 / Cash50 / Cash75 resource reuse

Cash50 (record 392, bank 11 tiles 26–31, fixed value tile 204) and Cash75
(record 393, tiles 20–25, fixed value tile 223) reuse fourteen approved, unchanged
8× resources. Native popup types are 37 and 38; Cash25 is type 36. No reward,
movement, animation, collision, random, or input logic is changed.

## Shared mechanics, separate identity

The existing cash renderer now selects one of three explicit profiles instead
of duplicating its compositor. Every native enemy allocation binds its complete
77-byte canonical record, pool generation, source bank, initialized value and
animation sequence to that profile. The actual pre-visibility animation witness
remains mandatory, including coins entering from negative y. Popup allocation
has its own slot generation, fixed-only native type, geometry and eight-draw
lifetime. Neither body nor popup identity can borrow another profile's phase or
source. Legacy generic-cache fallback is denied for all migrated body ranges
and fixed value source tiles, including rejected roles.

Storage, strict loading, pixel composition and frame-invalidity bookkeeping are
shared. The conservative all-three-or-classic policy intentionally requires all
21 cash resources and all three source/record profiles to be valid. One missing
or corrupt cash asset declines all three cash profiles; other global resource
families retain their own decisions. This is not a promise of per-coin resource
failure isolation. Native roles, allocation generations and draw lifetimes are
never shared across profiles.

The renderer retains the authored value-average HSV blend for fixed popup text,
normal body rendering, ordered ownership transfer, sticky revocation after
another family has copied RGB, source/palette leases, final indexed output,
cache and fade handling. It adds no scene/level allowlist admission.

## Verification boundaries

`tests/global_cash25_identity.py` exercises all three identities; the retained
filename is a compatibility name, not a Cash25-only scope. The structural
renderer harness covers all 21 assets, all profile phases and fixed lifetimes,
independent RGBA/HSV arithmetic, resource faults and cross-profile negatives.
These are bounded SDL shims, not claims of native collisions or GPU operation.
The separate native matrix verifies controlled original enemy allocation,
original movement and pickup, exact rewards and eight popup draws in both old
and previously unleased scenes. Per-scene trace timestamps determine capture
frames; a popup may correctly have expired at another scene's capture time.
Linux software/dummy tests do not establish Windows/GPU or whole-campaign
coverage, and audio-call parity does not establish human acoustic quality.
