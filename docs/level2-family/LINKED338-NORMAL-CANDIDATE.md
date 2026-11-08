# Optional normal Linked338–342 group

This default-off candidate reuses seven public NEWSHP images, bases 115, 117,
119, 229, 231, 267 and 269, for the two original linked structures in ordinary
E1 physical level 2 ASTEROID2. Enable only explicitly:

```sh
python3 scripts/launch_level2_family.py --data /your/game-data --check-only --hd --linked338
```

This prints a plan; it does not start a game. Actual execution additionally
needs `--launch`. The launcher clears inherited `LINKED338_*` settings, requires
`--hd`, and checks all seven additional files' lengths and SHA-256 hashes.
The original 52-file/24-terrain manifest remains unchanged. Fork, turret and
other family options are independent.

## Native group behavior remains authoritative

The four original one-based events are 288/289 and 351/354. Each pair creates
one cap338 through case6, then four independent components339–342 through
case12. Links28/29 and original positions are preserved, including cap y=-56
and the native case12 +24/-28 component adjustments. Each native allocation is
witnessed separately; a failed allocation consumes only that attempt and cannot
be replayed to acquire HD ownership. No group is synthesized or repositioned.

A full 731-event stream hash is checked at level load. The read-only script
observer wraps each actual event, before `eventLoc` advances. It admits the known
native case12 current-row clearing and event33 random-choice mutation only from
actual before/after observations. It neither generates RNG nor writes event
rows. Unsupported script changes fail closed.

Cap338 follows its original 12-cycle, three-image animation; the four component
records remain at cycle1. Native animation observation, constructor statistics,
link identity, bank/record stamps, allocation generations, palette and normal
state must remain valid. Damage graphic121 is **not loaded**; damage-state or
unsupported contracts fall back to native rendering. The original linked
combat, scoring and destruction behavior is untouched.

## Sparse rendering and boundaries

Only observed native-written cells receive HD ownership. The seven pins have
zero authored native-hole extras, so there is no rectangular hole restoration
or extra-support allocation. Art alpha blends over the current HD underlay.
Native holes are untouched. Linked, turret and Fork ownership all retire before
any family's early-return pixel writer; normal/blended overwrite and valid
shadows follow the existing shared-canvas rules.

Per-write checks remain cheap configuration/identity checks. Full image/bank
validation occurs at tile and final-output boundaries, not once per native
pixel. Incomplete callbacks or changed contributing identities invalidate the
shared HD frame.

## Verification limits

Focused tests exercise all ten independent attempts and failure consumption,
component offsets, allowed and rejected script mutations, cap/static animation,
seven native callback streams, alpha-zero underlay and native holes, retirement,
launcher combinations, damaged asset rejection, and hook placement. The C tests
execute extracted production functions with explicit stubs, not the complete
game. They do not prove real scene appearance or gameplay behavior.

Actual scene composition, performance, sound and save/load remain unverified.
This option stays default-off and makes no new terrain-coverage claim.
