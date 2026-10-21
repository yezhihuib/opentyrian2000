# Shared coin and gem resource reuse

Gem100 (record 394, global bank 11 tiles 32–36, fixed popup 169) and Gem250
(record 395, tiles 14–18, fixed popup 188) add twelve byte-identical approved
8× resources. Native fixed popup types are 39 and 40. No native movement,
collision, reward, animation, RNG, input or audio logic changes.

## Five identities, one renderer

The shared cash renderer now has five explicit profiles. Gem animation is a
16-step sequence over five distinct tiles, not a five- or six-step cycle:
`a,a,b,b,c,c,d,d,e,e,d,d,c,c,b,b`. Each actual pre-visibility animation step
must match its independent slot witness, even when two successive steps draw
the same tile. Negative-y movement advances the real phase before visibility.
Full canonical 77-byte source records, native allocation generations, initialized
value, exact source banks, draw geometry and normal-body style remain bound.

Popup identity is independently derived from a genuine native fixed allocation,
its original type, position and eight-draw lifetime. Record 509's native type39
popup can share the canonical 100 glyph; record 509's body is not admitted.
Its original reward is 250 despite its 100 popup; this existing game behavior
is intentionally untouched, not inferred from the displayed number.

All five profiles share strict loading/composition and the conservative
all-five-or-classic policy: 33 resource files and all five record/source/palette
proofs must be valid. This is not per-profile failure isolation. Native role,
slot generation, animation and popup lifetime cannot be borrowed across profiles.
Legacy fallback cannot revive a rejected migrated body or popup through an old
warm cache. Missing/corrupt resources, source changes, transfer revocation,
final indexed mapping, fade and cache leases retain strict classic fallback.
Authored popup hue/value-average blending is preserved.

## Verification boundaries

The retained `global_cash25_*` test names are compatibility names for the shared
five-profile implementation. Focused structural tests cover repeated/reverse
16-step sequences, all 33 resources, native fixed allocation and eight draws,
invalid roles/records/sources, borrowed phases, cache and transfer invalidation.
A separate native matrix uses controlled original births followed by unchanged
movement/collision/rewards and per-scene trace-derived body/popup capture timing.
Linux software/dummy results do not establish Windows/GPU, whole-campaign or
human acoustic coverage. HUD coexistence is not an unmeasured ownership transfer.
