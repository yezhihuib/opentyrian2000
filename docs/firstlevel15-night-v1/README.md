[English](README.md) | [简体中文](README.zh-CN.md)

# Hard first level night HD

Validated scope, 2026-10-14. Source/unit review, one bounded native Hard opening
and a separate protected mid-level/Boss diagnostic have passed. The final
combined night/Christmas source also passes both finite unit families and
Linux build checks. This is renderer support for the night version of the
first level; it does not establish natural Hard survival, a full-level clear
or Windows acceptance.

## Supported scope

The existing `--manual-hd-assets` option now also admits ordinary local
single-player Full Game, Episode 1, physical level 15, with an original Hard or
higher difficulty selection and normal game data. Physical 15 is the Hard+
first-level variant, not the fifteenth level selected in a menu. Existing
physical-level-9 eligibility and crop behavior are preserved.

The new path requires the original PIC3 scene lease, palette 5, valid source
resources and supported indexed/RGBA surface layouts. Christmas data, demos,
network/two-player/Galaga and other special modes are outside this extension.
Unknown output kinds, inconsistent indices or ownership, and unsupported
resources fail closed. Unsafe surface layouts decline HD presentation.

Use the normal menus and controls with the existing manual-HD launch option;
no new launch option or artwork pack is introduced. Original game data remains
an external requirement. Without the manual-HD option, normal startup remains
classic.

## Rendering behavior

The original indexed lighting loop remains unchanged. Before composing HD,
the renderer verifies its actual destination indices against the original
source and captured light coordinates.

- Geometrically lit authored pixels are retained exactly.
- Every nonlit branch uses the approved Option 1 transfer: authored RGB detail
  is anchored to the original destination palette color, with residual slope
  at most one quarter and reduced further when required by the available color
  range. Residuals round half up; alpha is already composited.
- Nonlit detail is compressed even when an original palette index happens to
  remain unchanged. The original sharp cone boundary is preserved. A channel
  below its destination anchor can increase; this is not uniform RGB dimming.
- Classic-owned pixels use the actual destination palette color. Original
  hue-8/brightness-8 cash remains locally classic and follows original lighting.
- Only the scene crop is affected. HUD composition, gameplay, events, RNG and
  player/light updates are unchanged. Existing fades use the composed output;
  presentation does not apply lighting a second time.

## Bounded validation

Independent optimized and ASan/UBSan units cover the complete channel domain,
original indexed geometry, ownership, fail-closed cases, HUD boundaries and
fade/presentation behavior. One unprotected normal-menu Hard opening produced
23 observed finishes and five actual 640×400 captures: the selected Hard menu
and four gameplay frames. The cone appeared and responded to original right
and left input. Four retained indexed/palette pairs independently matched the
original loop and native renderer readback.

A separate protected original-event progression reached 7,429 ticks. Independent
review accepted five selected gameplay windows: shells 146/147, a complete
20-part boss assembly, the weapon-81 energy burst and a successfully launched
child overlapping the core. All 360 sampled original-index oracles were exact;
five retained pairs independently matched 242,880 indexed cells and 1,280,000
native pixels. Cash and HUD stayed legible. The retained boss bars were entirely
lit; dark-region bar appearance is not established.

The protected diagnostic alters damage response/player drawing and downstream
trajectory. Its acceptance is limited to these selected render samples, separate
from the unprotected opening. It does not establish normal player-style coverage,
unchanged gameplay progression, all headings or all projectile directions.
All comparison reconstructions come from their respective same candidate runs;
none is a separate baseline gameplay run. Actual runtime evidence is native 2× Linux
SDL dummy/software with density-8 assets. Density-4/8 unit coverage and derived
images do not establish native 4× runtime acceptance. Unobserved actors and later
content, physical GPU/input/audio, performance and Windows remain outside these
bounded reviews. No game run was added for the final combined-source integration. See [validation inventory](VALIDATION.md).
