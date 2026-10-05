# 1.1.11 current update

Current host and ARM checks pass. Natural Azahar boot trace confirms pass-scoped background/fade decisions. Final visual acceptance remains pending. See TEST_NOTES_1.1.11.md and RUNTIME_SMOKE.json.

The material below is historical.

# Validation — 1.0.5 experimental update

The 1.0.5 static pass adds retail verification of **44** patch sites including
`0x41EE74` and runs `native_secondary_contracts.py` against the original UV
origin/size table and independent large glyph cells. The new red Quit-card
letter patch preserves alpha. Archive CRC/CHECKSUMS and available host tests
must pass before distribution. The build was compiled with clang for ARM via
a Zig-command shim in this workspace; exact Zig output and in-game timing are
not verified. Unicorn-based ARM emulation and Azahar runtime tests **have
not been run** for this build. The following log is preserved as historical
1.0.4 validation; do not attribute its Unicorn results to 1.0.5.

---

# Validation — 1.0.4

Passed for this build:
- Cross-compilation/link, full executable hash and original bytes at 43 patches.
- IPS round-trip equality, patch extent/overlap checks and payload allocation.
- Rejection of incorrect retail inputs; independent dotted version counters.
- 65,536 host input-mask cases: gameplay identity, contextual Ocarina A/B swap,
  unchanged X/Y, and held/pressed/released translation.
- Ordered HID history tests: sub-frame taps, release/repeated notes, holds,
  ring wrap, reset and bounded-overflow behavior.
- Executed built ARM payload in Unicorn 2.1.4 with isolated native-call stubs:
  bounded two-pass restart; stack and callee-saved registers; correct native
  and main transfers; precise background-node filtering; fade only once;
  touch pulse/release, owner handoff and held I; minimap quads 2/3 move with
  the body delta, other quads unchanged, no accumulation and context restoration.
- Four file/name textures unchanged outside declared lettering, alpha identical.
- Ocarina native art unchanged outside explicit ETC1 blocks; container alpha
  unchanged. Native X/Y and shared A0 staff-note regions remain untouched.
- Root-level ZIP layout, required docs and integrity checks.

Existing source identity evidence (not repeated this iteration):
- CCI BLZ decompression matches supplied 4,567,040-byte code.bin.
- All 1,944 CCI RomFS files match the supplied resource ZIP.

Not completed for 1.0.4:
- Azahar boot, visual transitions, real audio timing, performance and gameplay.
- Normal/MQ marker orientation and room transitions in the running game.
- Hardware memory permissions and execution.

The ARM harness executes production machine code but replaces native calls with
controlled stubs; it does not emulate the game's graphics/audio subsystems.
The old RUNTIME_SMOKE.json records an older binary and is not current acceptance.
BUILD_MANIFEST.json retains NOT_RUN for emulator validation of this binary.

The prior automatic approval review denied computer-use access to Azahar.
No new emulator interaction or installation was performed in this iteration.

Additional 1.0.4 checks:
- Built ARM Ocarina geometry: independent X/Y press movement, associated rim/
  sparkle relocation, whole-button RB center, HUD bubble and A/Quit placement.
- Song cursor includes native selection offsets. Live title is transformed for
  projection, drawn, and restored before the lower screen uses it.
- Dynamic song-page tail quads do not receive the playable-control swap.
- Inventory letter mapping and pixel preservation outside letter/chrome regions.
- Native Ocarina red Quit texture restored outside other established staff/trigger
  lettering changes.

The user supplied positive runtime feedback and defect screenshots for 1.0.3.
Those do not establish visual or audio acceptance of 1.0.4.
