LOAD TYPOGRAPHY SOURCE CANDIDATE, 2026-10-13

Current accepted runtime and packaging status is in ../load-font-v1/ACCEPTANCE.txt.
The source-only and unrun-gate paragraphs below preserve the original c0f1f446
checkpoint record; they are historical, not the final acceptance status.
Baseline a4974da93ee75fb18c7ad5827ea42a6b02d1b74d.

Source-only result
- Fresh original plan proof reproduced byte-identically: ef63aed3094e155c6e9df1caa84b5ebbc39d09f69596be5db15425a9f6b66d29.
- Independent protocol PASS: c4867acb8ffe51b48fd497bc05212723a27b040abb763cbab329067379078714.
- Independent unchanged-art Load role review PASS: f6caebaf268a6547597e4a31d73ef49e1c2df4357714fac1cd9951f6e4ffc5d5. Receipt included; original-containing visual references intentionally omitted.
- Correct existing resource option is --startup-assets <startup-title-settings-v1 directory>; protocol's '--hd-assets' wording was a naming error only. No new resource flags, art bytes, or medium dependency.
- Source harness: 192 paired source layouts, 144 enhanced/48 full-classic, byte-exact indexed surfaces and complete ordered-write hashes versus original draw calls. Maximum 37 runs /2618 glyph commands plus204 exact arrow writes =2822 of4096 fixed slots. All16 samples at each of4 footer-overlap pixels independently checked, plus per-state sample oracle, reduction oracle, outside-support exactness,7 cursor positions and absent cursor, same-index cursor write, whole-byte eligibility in both dynamic fields, guarded unterminated fields, default-help-state fallback, resource corruption/truncation/FIFO/missing/allocation failures, renderer/source identity invalidation and real sibling-owner exclusivity.
- Original settings harness still passes:359 frame calls,339687940 checks, max468 commands. Actual settings source remains the original C token stream after removal of narrow owner-exclusion and budget plumbing.
- ASan+UBSan source suites pass. LeakSanitizer itself cannot run under the executor's ptrace, so sanitizer reruns use ASAN_OPTIONS=detect_leaks=0. Both independent suite allocation ledgers verify tracked owned allocations return to zero. This is not an LSan pass.
- New production load_font.c is clean under -std=c99 -pedantic -Wall -Wextra -Werror. Full build succeeds; full clean baseline has existing unrelated misleading-indentation warnings in asset_debug.c, game_probe_fields.inc and render_mirror.c. No additional warnings remain in this candidate.
- Integration guard checks6271 unchanged prior files,631706987 unchanged asset bytes,10 exact original-C token projections,17 pinned changed/source/test files,36 mutation rejections, both release-after-fade paths and complete Windows C/header inventory. No Windows compilation/runtime claim.

Measured memory (64-bit Linux compiler)
Load static state542104 bytes; settings static state508376 bytes. Command sizeof14,4096cap =57344 bytes included in Load state. Both owner states retain storage but begin calls release the other owner's dynamic allocation before allocating. Load peak owned allocations1097728+4096000 =5193728bytes; settings peak1785856+4096000 =5881856bytes.
Measured state+worst active allocation+2432 parser/alignment allowance =6934768bytes, below7340032(7MiB). Conservatively including both compiled object .bss/.data/.rodata sections and8192 stack/allocator bookkeeping reserve is under6,945,000bytes, still below7MiB. This ceiling covers font-owner CPU working storage, not original engine assets or code. One nominal4096000byte presentation texture is separate; actual driver overhead unmeasured. Build-time checks additionally reserve600000bytes for the inactive sibling, and acquisition checks sibling's sizeof before allocation.

Reproduce (source/core only)
Source ../recovery-dependencies-20261013/env.sh in bash, then make -j4.
tests/run_load_font_tests.sh "$TYRIAN_DATA" "$PWD/assets/hd/packs/startup-title-settings-v1"
ASAN_OPTIONS=detect_leaks=0 tests/run_load_font_tests.sh --sanitize "$TYRIAN_DATA" "$PWD/assets/hd/packs/startup-title-settings-v1"
tests/run_settings_font_tests.sh "$TYRIAN_DATA" "$PWD/assets/hd/packs/startup-title-settings-v1"
ASAN_OPTIONS=detect_leaks=0 tests/run_settings_font_tests.sh --sanitize "$TYRIAN_DATA" "$PWD/assets/hd/packs/startup-title-settings-v1"
python3 tests/test_load_font_integration.py --out /tmp/load-font-integration.json
The fixture strings/fields in the harness are synthetic metadata from the approved proof. These tests read original data assets supplied separately and do not read/write tyrian.sav or config files.

Unrun gates
No actual game launch, actual input/state/save/fade timing matrix, successful load through JE_operation, actual window/scaler transitions, screenshots or gameplay regression execution has occurred for this candidate. Independent finished-source review and durable checkpoint are required before that separate explicit runtime gate. Runtime must use new disposable HOME/XDG_CONFIG_HOME profiles and only safe fixture slots1/11/12/22 for actual loads. The10-character levels/episode255 maxima are display-only. User saves must never be read, copied, backed up, restored or modified. No publication is authorized.
