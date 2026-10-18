# Rear Multi-Cannon P11 mode 2: exact eight-shot route

Baseline commit `4a0ae32c57b816d2ec885621bea530ef2ad7d1c8`, tree
`30ee5be9b6ed79e3aa6a3792c0e2f67f6e34fac2`.

## Exact scope

Adds ordinary player 1, rear port 10 / bay 1, power index 10, mode index 1,
physical normal record 275. The complete original 80-byte record has FNV-1a64
`719bf3ad022a1918` and SHA256
`b562575491ba4f8f290ff8698540dd0d0f7e3a1aa2fefaf6d1aa41d9b020b790`.
Original multi/max are 8 and repeat is 6. All eight entries are active.

Ordered raws: 277, 278, 295, 294, 298, 299, 40, 2. Original movement:
(-9, -2), (9, -2), (6, 6), (-6, 6), (-2, 9), (2, 9), (-10, 0), (10, 0).
Birth dx is -2, 2, 4, -4, -4, 4, 0, 0; dy is zero. Damage is 2 and
lifetime 255 for all eight. Placement stays (current shotX+1, current shotY),
with HDA anchor (0, 0). Admission requires exact `op[1][10] == 275`,
complete record pin, and all existing ordinary scope/source/shot checks.
Identical physical alias 1275 is excluded. P11 first-mode physical 264 remains
excluded. The normal physical level 9 / Hard physical level 15 scope and all
other mode, linked, generic, shadow, and two-player exclusions are unchanged.

Only three production files change: the ownership core, dedicated adapter,
and full-record pin header. A strict inverse of the 275-specific additions
reproduces all three baseline files exactly. The other 157 current source
files, including the header, allocator, renderer, and wrappers, are byte-exact.
The inherited original-source inverse also passes all 156 applicable files.
Existing renderer cap 8 is sufficient and unchanged. Original gameplay still
allocates 81 slots (0..80); renderer ownership remains 0..79. Slot 80 remains
native fallback. No gameplay arrays, allocation, phase advancement, energy,
damage, cooldown, movement, RNG, or collision logic changes. All twenty older
routes, particularly six-head 263 and eight-head 274, remain intact. There
are now 21 exact routes / 99 canonical phases, still 23 drawable and 25 observed
source identities. Observed-only 163/164 remain pass-through.

All eight heads reuse their individually pinned accepted d4/d8 HDA files.
Their 16 selected files have exact role 131, 12x14, anchor (0, 0), density,
length, and existing RGBA payload pins. The 40/2 files are independently
accepted payloads, not asserted to be exact byte-mirrors. Source/RGBA index
orders, pins, and caches are unchanged. No art, asset file, transform, catalog,
or density substitution is added. Candidate assets are unmaterialized;
asset preservation is a tracked-diff and unchanged-pin statement rather than
a full candidate disk-tree comparison. Tests use the existing verified local
selected pack and official original data; no remote asset retrieval.

## Tests and build

- Twenty core executables pass plain and ASan/UBSan: all forty runs. The new
  exact 275 suite executes 4,356,469 checks per run, all 648 prior/new 0..8
  cyclic capacity designs, all 80x80 renderer slot pairs, lease/seal/reuse
  checks, 1275 and opposite 264 exclusions, and 21 routes / 99 phases in
  bounded retained/newborn cohorts.
- The exact-source adapter passes plain and ASan/UBSan, each 15,400,528 checks
  and 736 malformed-resource variants. Pending-art lanes each pass 981 checks;
  a further private local 161-check lane per configuration proves 275 remains usable at both
  densities when unrelated 203/222 payload pins are deliberately zero.
- Full production strict C99/pedantic/Wall/Wextra/Werror build passes using the
  existing warning exclusions, with no new suppression. No Windows build.
- Authentic local input tests validate all 21 full80 record pins and all 25
  decoded source pins; exact 263, 274, 275 fields and byte-identical excluded
  aliases are independently checked. No original payload is bundled.
- Existing public synthetic record bytes, source fixtures, and RGBA fixture
  arrays remain unchanged; one distinct synthetic record is appended at index
  20 / byte offset 1600, for a total 1680-byte generated fixture. The synthetic
  pin is intentionally different from the authentic original pin.

The first adapter attempt exposed a copied negative-test setup error: case 16
had no invalidating active=false mutation because its selector had been
mistakenly changed to 17. The unchanged rejection assertion correctly failed.
An external diagnostic reproduces start1/bad1/kind16, remaining7/lease1/owned
birth; restoring only the two active selectors to 16 passes the focused
1,048,613-check test. The second compile overlapped this edit and is preserved
as timing-uncertain. A later complete authoritative run uses a frozen
244-file source/test snapshot and passes all lanes. The sole post-freeze edit
corrects a coexistence comment; comment-stripped and fully preprocessed tokens
are proven identical. Both failures, diagnostic, and all retry receipts remain
preserved. No production change or rejection assertion was weakened.

## Offline actual compositor and fallback

Actual copied candidate ownership core and adapter, extracted original
compositor, decoder, normal-tile dispatch, classic blit, and pixel path run
against authentic private original records/bank and accepted selected art.
Backgrounds, calls, positions, and age progression are finite synthetic scenes,
not ordinary gameplay timing or acquisition evidence.

- 69,344,649 main checks; 743 scenes; 2,228 admitted draws; 267 native 640x400
  SDL software-renderer readbacks.
- All 28 new phase pairs, both draw orders, ages 0/1/2/4/8/16 and both densities:
  672 pair cases and 112 ordered density/pair tuples. All 56 density/pair tuples
  have disjoint original rectangles at age16. Off-screen admissions are
  checked with exact view bounds; this does not claim every head is visible.
- Full eight-head ages 0..16, clipping, independent ordered integer alpha,
  full canvas/owner-mask/native nearest-neighbor equality, and 32 mixed
  263-to-275 retained-identity/restoration cases.
- Fifty-six separate cold-cache missing/corrupt processes cover every 275
  phase and every protected 263 phase at d4/d8. Optional failure preserves
  qualified birth and unaffected siblings. Actual wrapper/classic indexed
  output equals a direct original blit, and native output equals an independent
  decoded classic oracle. Generic entity admission and unrelated font/shadow
  paths are intentionally stubbed in this finite fallback fixture.
- Intentional alpha-rounding, ownership-write, and restoration-pixel mutations
  each fail the corresponding independent oracle check. Expected failures
  remain preserved; no passing assertion was weakened.

Every offline compilation and runtime has a 512MiB address-space cap; main
and fallback receipts have live kernel observations. Aggregate evidence has a
512MiB cap and a 4GiB free-disk guard. Main peak virtual size is 116,412,416
bytes. The native bright-background, mixed-separation, and overlap frames were
visually inspected at 640x400; eight distinct reused heads remain readable,
with no black backing rectangle or obvious square highlight. This is reuse
validation rather than a new art approval.

## One bounded ordinary runtime pair

One 180-tick baseline/candidate pair was launched only after independent
prelaunch approval and all frozen unit lanes passed. Both binaries preserve
the ordinary title / Full Game / Episode 1 / Normal / shop acquisition of
Rear Multi-Cannon at P4. They retain the original time(NULL) RNG seed and
synchronize by read-only seed, complete RNG, player/shop, and level-entry
snapshots. This is not render-test/demo startup.

The diagnostic explicitly performs two rear-power-byte writes: P4 to P10 at
tick0, then P10 to P11 while still in mode2 at tick110. Each write changes
only that byte, with exact original player-byte and RNG snapshots checked.
The mode1-to-mode2 change at tick50 uses the actual SDL key handler and is
observed at tick51. The resulting sequence is protected263, protected274,
then new275. The test does not claim ordinary P10/P11 purchases, a full
campaign, or first-mode264 support.

Both processes exit0 at exactly180ticks. The pair runs 46.68 seconds and
captures16 groups per process:284,240,370 baseline bytes and284,282,250
candidate bytes. Each process has512MiB address-space and512MiB capture caps;
the pair cap is1GiB and the free-disk guard4GiB. Live limits and peak usage
are in the launcher receipt. The one attempt is preserved with no rerun.

The sealed analyzer passes131/131 checks with no gaps. All20 named
telemetry streams are byte-identical. Four additional mixed streams compare
only explicitly enumerated original/nonchanging fields; all four projections
match. Renderer-only fields are excluded explicitly rather than described as
original state. All180 frames are hd-ordered with zero coverage mismatch and
exactly empty rejection strings; nonempty/unknown rejection text fails.

- Across all observed player-shot requests, outcomes are69 complete and12
  original power failures. The three complete sampled rear cohorts start at
  ticks4,54,114 and are separately checked for exact6/8/8 ordered births.
- Exact eligible/admitted draw counts are263:602/602,274:608/608,275:654/654,
  with no missing or unexpected normal-head draws. Protected263/274 draw rows
  are byte-identical across the pair. Old263 births retain113 admitted draws
  after tick50; old274 births retain73 after tick110.
- Candidate275 has all eight exact phases and retained record/mode/phase/raw/
  generation/slot seals. Baseline275 remains native fallback.264 is absent.
- Every actual optional draw checks ordered alpha and ownership. Sampled
  upload pixels match the actual SDL path and native readback. Full observed
  differences stay inside actual275 viewport rectangles. This is not an ideal
  whole-game-frame reconstruction.
- Original fade protection uses unconditional baseline/candidate whole native
  and upload equality in sampled pre110 frames. It does not compare protected
  faded heads to raw unfaded authored RGB. Every263/274 phase has a final
  visible witness in a fullframe-equal protected capture.
- All eight275 phases have sampled final authored support at tick115, with
  counts83,88,42,11,8,48,130,180. Phase5 has only8 support pixels and phase4
  only11 in that witness. This proves finite visibility, not full bounds or
  broad separation in ordinary gameplay. Mixed old/new visibility is sampled
  after both transitions. Wider all-pair separation is offline evidence only.

The frozen launch manifest covers top-level build inputs; the independent
prelaunch review additionally seals all three unchanged nested dr_mp3 files
for each private copy, including the compiled header. Both private patches
are independently inverted against the exact production roots. No omitted
recursive-manifest coverage is implied.

The coordinator personally inspected actual640x400 native frames at ticks
8,55,115,179 and accepted those four frames: protected original fade remains,
274/new275 shapes and colors are consistent, and clouds/rock show no black
rectangles or obvious square highlight. This visual judgment is limited to
those four frames. Other sampled frames have numeric witness checks only.

## Review and limitations

Independent read-only checks approve the exact three-file production inverse,
original/full80/source/asset pins, the offline compositor receipts and oracle
mutations, and the public-test diff/correction/fixture preservation. Frozen
before/after test manifests match all244 files; corrected-comment compiled
tokens match exactly. All three older checkouts retain their original HEAD,
index, refs, status, and every materialized file byte. Source and tests remain
local pending exact-batch publication approval.

This is finite Linux/SDL optional-rendering validation. No Windows build,
full campaign, exhaustive gameplay scene coverage, ordinary P11 purchase,
ideal full-game composite oracle, fresh artwork approval, GitHub CI pass,
remote upload, merge, or deployment is claimed.
