# Live shop Vulcan preview: independent observer

## Scope and provenance

The ordinary category-3 P1 front-weapon preview reuses accepted global resources
80067 and 80070 without changing their bytes. Only port 7, complete records
221–231, and bank-8 head indices 67/70 are eligible. The 8x 12×14 resources have
zero anchors. No battle, rear, sidekick, other weapon, or generic matching-index
permission is granted.

`shop_vulcan_proof.inc` independently authenticates the complete 82-byte raw port
record and 80-byte weapon records against the three registry variants. Separate
preview context/tick, front-call, and allocation-slot generations prevent stale
or recycled slots from borrowing authority. Actual allocator PX/PY/mouseX/mouseY
arguments are captured, and the signed 16-bit narrowing and exact del98 motion
clamp are reproduced. This is not a range test or an ambient mouse-state guess.
The real SHOP sets mouse position to player position before creation, so its
usual extra horizontal motion is zero. Each subsequent accepted head must be
the exact next simulator step. Duplicate, skipped, changed-table, changed-power,
and out-of-context witnesses retire the birth.

## Ordered rendering and failure

The original allocator, simulation, INDEX8 blit, audio, random state, inventory,
and economy are unchanged. `render_mirror.c` only forwards the accepted global
root; it does not provide battle authority. Independent `C_VULCAN` commands in
the pregame compositor witness the real blitter and every original indexed
write. They preserve order with Pulse, neutral Talon, static icons, typography,
and classic interface drawing. The accepted 8x RGBA is alpha-weighted downsampled
to the owner's 4x canvas.

Bank pointer/32060-byte size, both decoded source/mask hashes, palette entries
113–124, used records, root, reference/failure flags, and immutable payload hashes
are revalidated. Failure falls back to original indexed samples. Once contributed
art loses proof, the frame fault is latched: restoring a source, flag or root
cannot resurrect that frame. New authorized preview updates establish fresh
proof. Root changes reject an in-flight primitive; disposal releases payloads.
Runtime accounting includes proof/cache state and both payloads; the existing
16 MiB owner limit and bounded event/command pool remain in force.

## Verification

Focused proof and composer suites distinguish synthetic command tests from real
allocator/native evidence. Native checks use actual menu input at 2x and 4x,
all eleven powers, switching and reentry, with matching full, missing, corrupt,
and reference modes. Receipts record exact source hashes and separate native
indexed/state/audio/economy parity from presentation differences. No original
game-data bytes or compiled binaries belong in the source checkpoint.

Focused checks on the final source:

- `tests/shop_vulcan_proof_test.py`: 66,125 checks across three raw variants,
  all eleven powers/phases, exact allocator clamp/narrowing, motion and lifetime
  negatives; ordinary and ASan/UBSan runs.
- `tests/shop_vulcan_composer_test.py`: 25,202 ASan/UBSan checks, including
  cold/warm failures, both heads, ordered Pulse/Talon/static coexistence,
  post-typography lifetime loss, early-return failure observation, exact indexed
  replay and capacity overflow. Synthetic command arms are not native evidence.
- `tests/shop_vulcan_integration.py`: removes only sixteen allowlisted observer
  lines from whole files and recovers base `e9aaf5f3` byte-for-byte, including
  original CRLF. Existing owner modules, simulation and all art are protected.
- Independent review adds an early-return regression and exact full RGB equality
  to classic replay. Removing the new preflight guard makes that regression fail.

Historical earlier-batch integration scripts intentionally retain their old base
expectations; the new whole-base integration proof supersedes those comparisons
without weakening or rewriting their history. Original `shots.c` CRLF is retained;
use `git -c core.whitespace=cr-at-eol diff --check` for whitespace validation.

The final revised-freeze native matrix passed **12 runs × 363 frames** at 2x/4x.
Each full run contains 195 real Vulcan-positive frames covering powers 1–11 and
both heads; all 195 coexist with neutral Talon. The real navigation route also
covers 30 Pulse-positive and 64 static-icon frames. Same-frame Vulcan/static
coexistence is covered by the ordered composer rather than falsely claimed from
the native route, whose Vulcan selection has no approved static icon.
All original indexed/state/shot/RNG/cash/items/audio/input/timer traces match their
baselines. Missing, corrupt and reference presentation is pixel-identical to
matched baselines. Independent saved-readback checks restrict every HD difference
to actual head support and verify blend samples and zero-alpha preservation.

Native evidence uses the Linux SDL dummy video/audio drivers with deterministic
clock and cash fixtures; it is not a physical-display, audible-output, Windows,
or real-time latency certification. Input drives real menu navigation and all
simulation data stays original. Independent review accepted the final frozen
production sources with no open defects before the local checkpoint commit.
