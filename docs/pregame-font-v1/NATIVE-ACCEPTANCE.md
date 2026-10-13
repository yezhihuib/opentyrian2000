# Native pre-game typography acceptance

Implementation: `bf301cb37d0fe619f1ca7bf90c23f8e3580874e7`, based on published
`317bf551db59df9c4e3754d2072446c7313ab1f4`. Production code and all assets remain
identical to that implementation throughout collection and review. This document
is a later evidence-only addition; it does not change the tested runtime pair.

## Result

Seven intended cases completed in eight process starts, with exactly forty
retained captures. Every capture matches an independent original-data replay:
2,560,000 indexed pixels and 22,711,640 RGB pixels, with no tolerance or excluded
pixels. All three baseline/candidate pairs preserve the original compressed
menu/state/palette sequence and have zero changed RGB pixels outside the exact
original/authored font support. All observed settled menu RGB hashes are stable.

| Case | Binary | Actual output | Captures | Seconds |
|---|---|---|---:|---:|
| R1 | 317bf55 | 640×400, Integer 2× | 10 | 16.180 |
| R2 | bf301cb | 640×400, Integer 2× | 10 | 16.234 |
| R3 | 317bf55 | 1280×800, Integer 4× | 4 | 16.318 |
| R4_retry | bf301cb | 1280×800, Integer 4× | 4 | 16.586 |
| R5 | 317bf55 | 1365×767, Fit 4:3, 2× texture | 4 | 17.207 |
| R6 | bf301cb | 1365×767, Fit 4:3, 2× texture | 4 | 17.832 |
| R7 | bf301cb, tiny resource absent | 640×400, Integer 2× | 4 | 16.057 |

R5/R6 used the actual destination `(171,0,1022,767)`, full output-sized viewport,
unit renderer scale and nearest reference texture filtering. The independent
nearest 16.16 sampling model matches all baseline output pixels. Candidate RGB
uses the accepted atlas with complete correlated premultiplied footprint
integration. Integer 2×, exact 4× and the odd output all match numerically.

Missing only `settings-font-tiny-v1.hda` yields whole-menu classic fallback.
R7's four PNGs, indexed frames and complete palette files are byte-identical to
R1 at matching checkpoints. Its three earlier large/medium selector RGB,
indexed and palette signatures still match the fully enhanced R2 run.

## Route and state

Each successful process starts with fresh HOME, XDG configuration and working
directories, runs ordinary Full Game / Episode 1 / Normal, then follows:

`A root:2 → B root:3 → C root:4 → D category:2 → E category:9 → F root:4 → G category:9 → H root:4`.

Only seven menu keys follow A: Down, Down, Enter, Up, Enter, Enter, Escape.
The Up wrap, Done back, retained category reentry and Escape back are actual
native source behavior. No item category or purchase is activated. C and E
include input-free one-second holds with at least eight new natural frames.
The reused five startup snapshots are suppressed, not counted separately.

Cash remains 10000. Named equipment stays ship1, generator2, shield4, front1
power1, rear0 power1, no sidekicks/special; original last-items and old-items
behavior is retained. Four original cube icons occur naturally. All active and
unused selections, menu choices, armor/shield fields and ordinary-mode flags
are checked against matching cached natural frames. Unexpected mode/context,
wandering selection, live/cache disagreement or cash/equipment mutation stops
the process. Inputs, source sound dispatch and save branches remain byte-exact
under the source projection. No native auditory or disk-save-persistence test
is claimed. The native SDL_QUIT path exits before a save file appears in these
fresh profiles; normal backup operations were not disabled.

## Retained failures and repairs

The original R4 attempt stopped after 36.491 seconds with zero captures and no
pre-game lease. The reused title gate mistook the original logo-motion interval
between partial palette fades for an input-ready menu. Its early Return was
cleared by the original input flush; the original 30-second idle demo branch
then triggered the unchanged non-native-mode guard. The failed result and logs
are retained untouched.

A separately reviewed private-controller correction requires a complete
same-frame presentation and current palette equal to target colors before
pre-A readiness. Existing true fade hints remain restrictive. It changes no
transport, original input, production source, deadline or capture limit. One
fresh same-case R4_retry was authorized and passed. There were no other retries.

A preliminary offline odd-output oracle used separable floating-point averages.
It differed at 49 pixels by at most one channel unit on exact half-integer
rounding boundaries. The rejected numerical receipt is retained. Direct
row-major footprint integration preserves the approved C accumulation and
rounding contract and resolves every pixel with zero tolerance. This was an
oracle arithmetic correction; no game output or production code changed.

## Independent proof and identity

The private oracle decodes original PIC1, font/art banks, encrypted menu/help
strings and serialized equipment from authenticated original files. It reads
accepted SFN1 alpha/role planes. It replays original per-glyph dark then unsafe
face operations, both DARKEN coordinate shifts, and ordered cubes, cash, bars,
ship/shield and footer. It does not import production font commands/events.
Five pure oracle tests include call order, offsets, same-index authored
occlusion, independent text rejection and state/raster sensitivity.

- Baseline ELF: `f2436b62f7c2d1405a4de9281dc980cca432dad8a85df89d41814676373f22d8`
- Candidate ELF: `6ec5b6eada924cf99ec2a68ed7c5a16873277ceed8545a8ad3e43fe4115be838`
- Final collection identities: `ab6270863594116f74db912d7251a0bab71f5cc8fb3374b2c2f18bb0e17e0056`
- Independent replay script: `7d7dd29b18c6e3d8fdcd77c4ee4312fc58d21fe17631514c04e31b72142ca112`
- Frozen evidence inventory: `ef49bca33bec566128db69fe63d7d1c464a141a653e222a1a4762924b54274a5`

Private inputs, executable/transport/fixture identities, all raw receipts,
indexed/palette/BMP/PNG captures, successful and failed results, numeric replay,
pure tests and the preliminary oracle failure are retained in the separate
native proof archive. The sealed [independent review](INDEPENDENT-REVIEW.md) passes source, numeric
and retained-still gates. Its SHA-256 is
`68156f31c43d611c992e5b6363084f4de16468dbf0e7e25934c87d9493329855`;
the final independent evidence receipt is
`112688571cd8317ba3cbe66f27af4459ac8078ff08be454ae204c54b416983b0`.

## Limits

This matrix qualifies natural SDL software/dummy rendering, synthetic SDL keys
and one ordinary title-window resize. Windows/MSVC compilation/runtime,
hardware acceleration/DPI, fullscreen, performance and physical inputs are not
qualified. MSVC source registration is checked exactly once by the source suite.
F1 help-return fades, other modes/contexts, corrupted resources, unsupported
operations and mouse/scaler variants remain bounded source/core coverage rather
than newly executed native cases. Natural strings did not overlap cube support;
positive same-index occlusion is explicitly synthetic source/core and oracle
coverage. No item/purchase previews or other menu contexts were added.
