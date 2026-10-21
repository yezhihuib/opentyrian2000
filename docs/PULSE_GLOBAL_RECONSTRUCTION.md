# Global Pulse5 reconstruction

This batch migrates only the five accepted front Pulse-Cannon assets to the independent `--global-assets` route. Authored resources, indexed sprites, weapon tables and simulation are unchanged. No episode, level, scene selector or current equipment at draw time grants eligibility. The existing default launcher and packaged manifest remain unchanged; this is an explicit global-resource development route.

## Identity and call lifetime

The real normal front-fire call captures selected port, power, mode, player and record. The actual allocator consumes a scoped call token and advances each selected slot's generation before initialization, including zero-graphic or reused slots. All exits close the allocator envelope. Only fully initialized matching Pulse slots receive a birth witness, including whether the optional global route was on at birth. A later equipment change cannot grant identity. Unrelated, rear, linked or shop calls cannot borrow matching sprite numbers.

The loader observes the original port name before its existing null termination and the completed fields afterward. It validates the exact 82-byte original port fingerprint, then retains a fingerprint of the normalized runtime fields. Weapon matching serializes all 80 original loader bytes, including inactive lanes and signed bytes, and accepts the pinned three historical data variants without selecting by episode. Draws revalidate their exact birth record; contributed frames and cached frames continue validating every used record and the port.

The five source tiles and their used palette colors are independently pinned. Each resource is authenticated before use; missing or corrupt resources fail closed. An eligible but rejected call still executes the original indexed draw exactly once, without entering an old warm generic cache.

## Pixels and composition

Head and shadow retain the original native draw coordinates. Asset 59's `anchor_x = -1` is authenticated metadata, not an extra runtime translation: the previously accepted RGBA is already aligned to the native origin, as in the old `draw_asset_filtered` route. The shadow uses the same authored alpha as its head, original palette-darkening on classic underlay and continuous darkening on HD underlay.

The support is the union of authored alpha and native covered cells. Every native indexed write is observed in order, including equal-index writes. Independent ownership, source/output leases, palette dependencies and final ordinary/low-detail/night mapping are retained. Copied contributions to later owners (including antialiased HUD text) keep their proof until the frame retires. A failed dependency conservatively declines the current Present, rather than leaving stale copied pixels. Cache/fade/root resets do not authorize old births or revive old RGB.

## Validation boundary

Focused tests execute the production Pulse observer and actual `player_shot_create` through a bounded harness. Native tests exercise real SDL fire input through the ordinary front call and compare original indexed surfaces, palette, RNG, players, entities, Present, sound queue and fire traces. Deliberate exceptional injections are labelled diagnostic seams, not spontaneous gameplay. Final run counts and acceptance receipts are recorded with the batch; no Windows, GPU, full campaign or later Hitflare/Vulcan claim is implied.

## Frozen candidate results (2026-10-21)

The final production build passed. ASan/UBSan focused tests passed 551 cases / 9,575,682 assertions, independently reproduced from the frozen source. Existing isolated regressions passed: Shield 354 cases / 15,046,787 assertions; Talon 365 / 421,050,144; HUD 166,155,902 checks. The focused Pulse harness covers all three pinned data-table variants; these results are not native engine proof.

Native integration passed 18 scenarios / 54 runs / 8,640 total frames (5,760 variant frames compared against their baselines), using the Tyrian2000 data variant. All 11 records and five heads were exercised through actual normal front births, with 24,396 accepted head/shadow calls. Indexed surfaces, palette, RNG, simulation, audio queue and front-fire traces matched exactly; sampled RGB changes stayed within independently decoded native/alpha support. Scenarios cover all powers, two-player, Hard15 night, ordinary/night HUD overlap, legacy scene coexistence, root transition and controlled nonfront allocation. All 159 old off-birth draws remained rejected; 384 post-enable draws were admitted; 16 controlled nonfront draws were rejected.

The actual glyph copied-contribution test observes 202 Pulse subpixels copied into font underlay and 136 glyph intersections at frame 96. Source corruption after indexed HUD drawing gives exactly the classic Present; restoration at frame 97 gives exactly the nonmutated output. State and audio queue remain identical. This controlled in-memory source mutation is an explicitly labelled diagnostic seam. An early frame-100 mutation proved ordinary fallback only; it is not the copied-contribution evidence. A historical frame-100 label in the v4 source-mutation metadata is superseded by the actual frame-96 hook, observer and result receipt.

Evidence is retained outside the repository under `recovery-validation-20261021/pulse`, `pulse-native` and `pulse-independent-v2`. The frozen source/test receipt, focused suite summary, native `summary-v2.json`, `mutation-v4-result.json` and independent sanitizer/review receipts identify the exact candidate. Visual inspection of ordinary power-5 and night/overlap power-11 frames confirmed retained native placement and intact Talon/HUD composition. The native platform is Linux SDL dummy/software, with bounded sequences and sampled RGB: no Windows/GPU, full-campaign or listening-test claim is made.
