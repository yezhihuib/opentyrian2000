# ASTEROID1 final three static random rocks

This checkpoint adds three imagegen-authored, source-aligned 12×14 static designs
under the existing separate normal-data Episode1 physical-level1 ASTEROID1 opt-in:

- bankD/base114: records319–320, original downward speeds3/5
- bankD/base133: records321–322, original downward speeds4/6
- bankD/base152: records323–324, original downward speeds3/5

Each pair shares one image, not two animation frames. Direct original77-byte
records and complete source sequences establish ani1, animate0, size0, bank8,
with no turret, launch or damaged-image state. These finish the eight static rock
designs spanning the20 static records in the21-entry original random table.
The separately animated12-step record286 pulse remains classic.

## Artwork and scope

The new masters retain the original muted cool slate-grey relationship, lit from
the upper-left, with continuous painted geological planes, natural contours and
restrained fissures. The distinct elongated114, rounded133 and angular152 bodies
were reviewed alongside every native source form and at native2x size. Exact
prompts and masters are under the three corresponding artwork directories.
prototype/build-asteroid1-random-static-art.py applies only global source-footprint
alignment and inward coverage. It does not enlarge a low-resolution staircase
into the painted design. No original game data or runtime captures are packaged.

Use --asteroid-hd-assets=assets/hd/packs/asteroid1-ten-v1 through ordinary campaign
progression. The flag does not select or play a level. The optional pack now has
29 images,39 source records and12 independently preflighted families. Both
installed default packs retain629 entries and every prior26 optional HDA/PNG
pair remains unchanged. Other levels and excluded modes remain classic.

Each new family pins the current loaded enemy-bank role, the entire original
42012-byte newshd bank and both exact serialized77-byte records independently.
It uses one12×14 resource and only part0, preserving source position, clipping,
filter, draw order and indexed writes. Its own missing/corrupt resource falls
back locally, with sticky cache failure. Source/record mutation after an accepted
call rejects that frame. No global manual HD or gameplay scope was broadened.

## Bounded verification

- All six records: optimized and ASan/UBSan extracted-production suites,154 raw
  record-byte mutations and4 warm-sibling mutations per pair,16 loader negatives,
  isolated-own-image positives, source role/rebind/reload and rendering guards
- Shared production snapshot:579 checks across12 families and39 record dependencies
- Prior small-rock95 regression and catalog regression passed
- Catalog-only validation checked1258 default HDR1 entries and29 optional entries,
  using an explicitly supplied historical asset root for retired default sources
- Paired baseline/candidate actual-engine runs use explicit diagnostic seeds4/6/7,
  normal physical1 and the unmodified original random table/spawner/events.
  No actor, event or random-table injection is present
- Eight150-tick pairs cover native2x/4x, independent missing114/133/152 and all-three
  fallback. A separate60-tick flag-off physical9 pair passes
- All14 gameplay/RNG/INDEX8 trace files and all prior draw-command rows match
  exactly in every pair, with zero coverage mismatches or rejected frames.
  All-three missing and flag-off frames.tsv also match baseline exactly
- Actual engine records319/320/321/322/324 have uniquely matched accepted HD draws
  from the previous end-tick actor row, accounting for pre-movement drawing and
  the observed+41 stationary sky-layer map offset. Record323 is unit-only
- Full native2x bodies114/133 use seed7/tick110;152 uses seed6/tick135. These are
  cropped640×400 SDL renderer readbacks without rescaling. Internal density8
  and classic exports are suppressed into a zero-byte regular file; no BMP
  files are created. Source art and all three actual bodies were parent-reviewed

The partial seed4 screenshot and preflight-stopped captures are excluded from
full-body acceptance. Native4x has trace coverage without an image capture.
This is not natural campaign, full-level, Windows or performance acceptance;
LeakSanitizer is disabled. Runtime512MiB/compiler1GiB limits and the5GB disk
reserve were retained. New-output/Git growth and all new PNG copies are bounded
by60MB and12MiB respectively. See validation.json for exact finite receipts.
