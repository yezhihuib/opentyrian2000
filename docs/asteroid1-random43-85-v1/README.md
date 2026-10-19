# ASTEROID1: two more static random rocks

This adds two separate one-image families to the existing asteroid-only opt-in,
for 24 images and 28 original records across seven independently preflighted
families. The two default packs still contain 629 HDR1 entries each.

## Original identity and scope

- Base43: records260/261/262, original tiles43/44/62/63, armor3.
- Base85: records263/264/265, original tiles85/86/104/105, armor2.
- Both are static24x28 bankD/newshd.shp designs (ani1, animate0, size1, bank8).
  Within each family the three records differ in downward speed4/5/6.
- Each family occupies three of the original21 random-table entries. These are
  two different designs, not rotation frames. No new animation was invented.
- The unchanged original random spawner, events, motion, collision and INDEX8
  rendering remain authoritative. Only normal-data Episode1 physical level1
  is eligible under the existing --asteroid-hd-assets flag. The flag does not
  select a level. No ordinary spriteSheet8 registration or default-pack entry
  was added.

Each family has its own exact source-bank/three-record/payload pins and isolated
one-image preflight. Missing, corrupt, wrong-role or non-regular resources fall
back coherently for that family. The shared immutable source reference is still
compared with current bank bytes on every attempted draw. Warm sibling-record
or source changes cannot retain a partial HD frame. The previous22 HDA files,
five family includes and shared source helper are byte-identical.

## Artwork and rebuild

Two built-in image-generation calls produced separate transparent continuous
neutral-grey rock masters after inspecting both original static designs.
The masters and exact prompts are in assets/hd/artwork/asteroid1-random43-v1
and asteroid1-random85-v1. The recipe aligns each generated rock to its own
original support and applies inward-only smooth alpha. No nontransparent HD
pixel lies outside its original coverage. HD images are192x224 at density8.
No original game data or runtime screenshots are included here.

With original data supplied externally, run the recipe separately for each base:

    python3 prototype/build-asteroid1-random-static-art.py --base 43 --data /path/to/original-data --out /new/output43
    python3 prototype/build-asteroid1-random-static-art.py --base 85 --data /path/to/original-data --out /new/output85

Independent rebuilds of both PNG/HDR1 pairs are byte-identical. The top-level
optional_packs catalog lists all24 exact PNG/header/payload fingerprints and
all28 records. Its frozen inventory is separate from the default-pack inverse
checks. Catalog-only verification accepted both629-entry defaults using an
existing historical asset root, plus all24 optional entries. Missing/corrupt
source, runtime and catalog cases are rejected.

## Bounded validation

- Strict production compile/link passed with warnings treated as errors.
- Both new extracted-production suites passed optimized and ASan/UBSan:
  72 process cases total, including eight positives and64 malformed/missing
  cases. Each family checks all231 serialized record-byte mutations, six warm
  sibling mutations, 12 ordered quadrants, clipping, modes, formats, filters,
  current source bytes, rebinding and sticky family-local failure.
- The shared-source regression passed343 checks across seven families and28
  source dependencies. This uses record stubs to count dependencies; the new
  family suites independently exercise the actual serialized records.
- External diagnostic seeds1 and2 used the unmodified original random spawner,
  with no actor/table/event injection. Each selected seed ran120 ticks at native
  2x and4x. Actual engine witnesses are record265/base85 (132 new quadrant
  commands) and record261/base43 (156). The other four motion records are unit
  covered; they are not claimed as gameplay witnesses.
- All14 gameplay/state traces, including RNG and INDEX8 game/output buffer hashes,
  match the baseline exactly. Prior-family draw commands also match exactly.
  Coverage mismatch and rejected-frame totals are zero. At2x the target pixels
  change to HD; base43's original HUD occlusion is preserved. Native4x runs have
  command/trace checks and no screenshot capture.
- Removing the matching image produces no new-family HD commands, exact
  baseline/candidate PNGs and unchanged prior-family commands. A60-tick flag-off
  physical9 regression also matches exactly.

Runtime processes stayed under512MiB and compilers under1GiB. All new output,
including both generated originals, copied masters, fixtures, captures and
modified build outputs, stayed under75MB total and16MiB PNG, with more than5GB
free. LeakSanitizer was disabled; ASan and UBSan were enabled in both family
suites. This is finite diagnostic acceptance, not a natural campaign playthrough,
full-level completion, Windows verification or performance acceptance.
