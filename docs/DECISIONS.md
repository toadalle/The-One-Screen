# Decisions

## Version and packaging
The user requested `tos-alpha-X.Y.Z.zip`. X is major, Y milestone, Z iteration.
Each is an independent nonnegative integer. Iteration 9→10 never increments
milestone; changing milestone never resets iteration. First release is 1.0.0.
Project content goes at ZIP root; important records go under docs.

## Input and visual semantics
Xbox A is bottom, B right, X left, Y top. L/R presentation becomes LT/RT.
Emulator bindings remain identity. Layout changes must not swap gameplay item
semantics. Ocarina alone exchanges A/B: B plays the native A note, A exits.
X/Y notes and native stored song sequences remain canonical.

## Architecture
Physical sampling, context ownership, input translation, native ABI, layout,
scene creation, HUD, frontend and camera have separate modules. Layout groups
are configured with anchors and scales; a whole-screen swap is a presentation
policy rather than an implied repositioning of every child element.
No old feature C backend is included. Retained ABI declarations, platform IPC
and texture codecs are identified in PROVENANCE.md.

## Native ownership
Borrowed frontend registration nodes are observed for diagnostics only;
they are never cached for replay. Materialized Ocarina positions use the
recovered direct stream, which differs from the ordinary HUD accessor.
Scene renderer/texture changes fail closed pending a proven destruction and
recreation contract. This prevents stale reuse but is still an incomplete
transition behavior, not a lifecycle solution.

## Memory and patch identity
Every patch declares all original bytes. SHA-256 gates the full executable.
Native BSS allocation reaches 0x608000. Payload begins at 0x610000 and extends
the exheader BSS reservation. Historical payload address 0x5C7000 falls inside
declared native BSS; that overlap is a risk, not proof of a past crash cause.
This allocation change requires runtime validation. Hardware support is not
established.

## 1.0.3 foreground and container policy

Refresh the native lower framebuffer before projecting the same frame's foreground
onto main. Filter known background producers instead of sampling or cutting an
entire framebuffer. A mode-background node identity is recorded anew by its
producer and compared at draw time; it is never dereferenced or replayed later.
Advance stateful fades once. Preserve native container art; change only lettering.
Use a native red A-over-Quit card and center glyphs on actual native glyph geometry.

## 1.0.4 artwork boundary

Reuse supplied/native container artwork and the existing HUD A bubble. Do not
create new illustrative replacements. Text-only repairs may remove unwanted
baked lettering and reconstruct its covered background, then apply the requested
font. Asset origin evidence is recorded in ASSET_AUDIT_1.0.4.md.
