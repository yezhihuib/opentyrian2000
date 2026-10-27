# Shared NEWSHF interceptor 166: three-pose finite extension

This local prototype adds the original record 166 only, with unchanged gameplay coordinates, events, movement, collision, health and pose timing. It is a single shared family rather than per-level copies.

- Logical source bank: 10 (`newshf.shp`). Original bases: 87 straight, 85 and 89 opposite banks; 24×28 actor quartets, anchor (6,7), offsets 0/1/19/20.
- Resource IDs: 2100034–2100036; exact runtime phases 34–36; profile 19. The existing 64-bit dependency mask retains these bits with group mask `UINT64_C(0x1c00000000)`. Finite resource count is 37; unknown phases must reject before any array access or shift.
- Source-zero cells remain RGBA zero. Partial-alpha or cleared originally occupied cells require the original typed underlay proof and suppression of the native mirror overwrite.
- Independent loading, record/tile identity, palette, frame/root reset, cached contribution and copied/occluded dependencies preserve previous safety contracts. The pre-contribution whole-actor classic fallback for native row wrapping is unchanged.
- Original 165, 164, NEWSHI, terrain and cyan assets are unchanged. Historical proof ledgers and native harness bytes remain immutable; exact hash-locked compatibility adapters expose only the declared new finite boundary.

## Original natural evidence

E5 physical level 4 naturally shows all three poses across a 350-tick no-fire run, not simultaneously in one frame. Base87 appears at ticks154–199, base89 at180–219, base85 at200–277. Used source palette values were independently matched to verified palette5 in actual captures180 and205; this is not a claim of capturing all256 palette entries. Original reuse totals50 direct spawns across E1L8/L12, E3L10 and E5L4. Rendering eligibility is source/identity-based, never a level whitelist.

## Bounded identity and episode scope

This candidate admits only the original77-byte record166 from `tyrian.hdt` (episodes1–3). Episodes4/5 embed a different record: byte2 (`tur[1]`) is0 rather than146, although the graphics and movement fields match. The original complete-record pin is intentionally retained; these embedded identities remain classic and gain no166 HD contribution. Existing legacy bank10 guards are unchanged.

An exploratory exact-two-identity implementation was rejected during preflight: unsupported legacy E5 records163/167/168 then caused whole-frame fallback. Shipping that partial support would regress the scene. The exploration and failed receipts remain private evidence; the candidate restores the original single-identity runtime instead of adding a new legacy birth-token mechanism. E5 acceptance must prove present-new-pack equals missing-new-pack and the qualified prior scene, not claim visible166 HD. Natural E1–3 observations and controlled E1L12 pose fixtures are reported separately.

## Acceptance scope

Authoring, source/pack inverses, finite phase and dependency tests, naturally visible frame pairs, controlled borrow/ownership tests and complete historical gates must all pass on frozen input bytes before this candidate is qualified. Natural source appearance alone is not proof of HD admission. Controlled fixture evidence must remain labeled separately from normal gameplay. Linux cloud checks do not establish Windows or full-campaign acceptance. All failed/interrupted attempts are retained outside the source tree; final receipts are separate immutable artifacts.
