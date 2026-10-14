# Red250 and portable font coexistence

## Scope

This local candidate composes the already accepted red250 production/artwork
from `5e40f2bec8e8ec56f6f3f368ecc41ae547924ccf` with the portable Title,
Settings and Load font fix from `8d991306b3dcc18b92047ab08fa0f8a063d7d220`.
Both descend from `4597e39c75b949d8f4e1f22bbc6117b432294132`. The original
red branch, runtime fixture, screenshots, receipts and bundles remain intact.
Neither top-level README is changed from the font commit.

The three red production files and manifest are byte-identical to the accepted
red commit. The nine font production files are byte-identical to the font
commit. The other production files and all existing artwork remain unchanged.
There are no gameplay, art, runtime-fixture, renderer-behavior or input edits
in this coexistence step.

## Finite proof composition

`tests/red250_font_projection.py` reverses only four enumerated red files and
seven small proof-adapter edits. Every inverse uses exact line hunks, whole-file
before/after hashes and exact immutable-parent restoration. The 50 added red
asset paths are enumerated individually and their actual bytes must equal the
accepted red commit. There is no directory exemption or refreshed historical
hash set.

The original red commit is provenance only, not a required local Git object.
The finite forward hunks reconstruct its production snapshot from published
4597e39; accepted added-file SHA256/blob/mode pins protect all 72 additions.
Only published ancestors4597e39 and8d99130 are required for these new guards.

The existing portable-font projection and its historical JSON are unchanged.
The outer inverse runs before it. An already-normalized guard may be reused
only when it is byte-identical to its immutable portable parent; this does not
qualify a reverted current file. Current-file validation requires the exact new
bytes. The shared pregame/selector/type15 paths use this same composition.
Modified proof guards are themselves protected by finite inverses; the two new
proof files are individually hashed.

The renderer test normalizes only the exact font delta when checking that the
red source delta consists of three files. It still extracts, compiles and tests
the actual red renderer and original indexed blitter bytes. It does not test a
projected substitute renderer.

## Qualifications and retained failures

The coexistence suite tests both inverse directions across all 148 production
files, the exact source/asset path sets, every admitted red file and guard,
mutated inverse hunks, all 50 added assets, and preservation of all 72 red
additions. The portable, pregame, coexistence and selector integrations retain
their historical controls. The selector regression projection must recover the
same 140,247-byte renderer as the qualified font parent.

Relevant extracted renderer/mutation/original-semantic/Data266 checks, font
units and sanitizers, and Release plus `RENDER_MIRROR_DISABLED` builds use
`WITH_NETWORK=false`. The Windows project check covers source/header inventory
only; no Windows compilation or runtime result is claimed here.

The older Settings integration still has its pre-existing stale
`src/opentyr.c` pin. The older Load integration still has its pre-existing stale
`README.md` pin. The historical title source guard inherits the Settings
failure. These failures remain reported rather than hidden by updated pins.

## Runtime evidence is reused, not expanded

No game or engine-main process is launched for this integration. The accepted
red evidence remains three successful simulation runs and four engine process
starts total, including the preserved parser-only failure. It contains exactly
25 actual native2x frames and one actual native4x popup-only frame. It does not
establish a native4x body cycle, natural/manual gameplay, a full-level or mode
matrix, Windows behavior, or additional backgrounds. The bounded actual-image
author and technical acceptance receipts remain unchanged.
