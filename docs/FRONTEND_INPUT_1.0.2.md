# Frontend and input contracts

The native source and resource hashes remain pinned to USA Rev 1.

## Foreground composition

`COmoteUraSelector` is allocated into 0x50BB50 by 0x454F4C, constructed at
0x468DA8 and loads localized `misc/*/ura.ctxb` resources at 0x468920. Its
0x4401A8 update handles left/right mode selection; 0x4407A4 handles the
single-mode case. Ownership requires gameMode 1, a valid object pointer,
resource-loaded +9, enabled +10, interaction +7 and state +4 in 1..8.
This predicate is derived from disassembly and still needs transition testing.

File-select remains gameMode 2; name entry uses 0x5077F0+4. These owners keep
the upper 400x240 scene on its native target. The lower 320x240 foreground is
centered horizontally, at x40, over that live scene. No framebuffer snapshot
is stored and no native update is paused. Native draw calls at 0x30005C
(canvas) and 0x41EE2C (common backdrop) are omitted only during this composed
lower pass; the surrounding projection and material setup still execute.
The main transfer is delayed from 0x41952C until after lower drawing at
0x4198B0. Right-eye transfer 0x4197DC is likewise deferred. In stereo mode
both eyes receive the same final composed frame; target acceptance is 2D.

Container colours, border details and cursor art are retained. The lettering
repair cannot reconstruct original texels hidden beneath baked letters exactly.
No brown colour-keying or speculative retained-node replay is used.

## Input

The 0x423340 hook replays `ldr r0,[r0,#4]` and captures the exact HID ring
used by native 0x4232C8. `TOS_HID native_reader=0x...` is logged when bound.
Gameplay and audio use independent history cursors; neither drains the other's
samples. Timestamps identify generations, so index equality alone does not
discard a whole fresh ring. Four attempts bound concurrent-writer retries.

At 0x41A904, r9 identifies the controller lane. Only lane zero consumes the
Ocarina queue. Interactive states 4,12,16 translate physical B to native A;
X/Y/L/R retain their semantics. Distinct held-state transitions, including
releases, are queued in order and delivered once per native audio poll.
Unchanged holds do not create extra notes. Context changes discard the queue.

The queue holds 64 transitions. Overflow recovers to the latest input and is
counted rather than leaving a stuck note. A finite HID ring cannot recover
samples already overwritten by the platform. Exported `tosInputMetrics` words
are queue depth, peak depth, ring overruns and queue overflow count. A burst
faster than the native consumer introduces queue latency; this does not increase
the native game's maximum note-processing rate.

## Required runtime acceptance

Mode selection (including MQ), save cards, Start/Copy/Erase, name entry and Back
must appear on main with original containers and no brown canvas. Confirm the
sky/Link scene updates behind save cards through repeated transitions. Test
fast B/X/Y/LT/RT taps and repeated B notes; A must close, B must never close,
and gameplay A/B/X/Y bindings must remain unchanged. Test song lists, song
learning and returning to play without stale queued notes. These checks are
pending, not assumed from successful compilation.
