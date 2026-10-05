# Foreground, input and Ocarina repair — 1.0.3

## Evidence and scope

The supplied 1.0.2 screenshots show live sky behind save cards, but also an old
mode image on lower, brown mode background on main, decorative file text behind
cards, detached map arrows, and tiny Ocarina labels. The latest local log at
`%APPDATA%/Azahar/log/azahar_log.txt` reports `TOS_BUILD 1.0.2 clean_backend`
and `TOS_HID native_reader=0x10002000`. It is not a 1.0.3 test run.

## Same-frame foreground projection

The native lower draw span is 0x4197E0 through its transfer at 0x4198B0. The first
pass now targets and transfers the lower framebuffer normally. A saved-LR seam
at 0x4198B0 returns to 0x4197E0 once, with integer/VFP registers and flags restored.
The second pass targets main and omits known backgrounds, then transfers main.
No framebuffer snapshot or retained frontend-node replay is used.

The native mode updater at 0x43FCBC falls through at 0x43FDF0 into its sprite
producer at 0x43FDF4. Searching only BL references misses this relationship.
The first sprite calls at 0x43FE30 (dual mode) and 0x44015C (single mode) use
owner+0x1C and the common background texture at owner+0x498. Card and selector
sprites use owner+0x494. The background wrapper observes the node added to the
native queue 0x5C0BA8; it does not retain geometry or dereference a saved node.
The draw seam at 0x2FEAA4 omits that exact node only on the projected mode pass.
The lower display still draws the background normally.

The canvas and common backdrop draws remain suppressed only during projection.
0x41C3C8 both advances fade alpha and queues a fade rectangle; its caller at
0x419868 now runs once per frame. The already-queued fade is drawn in both passes.
Native input and mode updates are outside the repeated span. Native queue draw
0x2FEA30 iterates the prepared nodes without consuming the queue.

File-scene callback 0x4611E8 updates/draws two 2D decorative nodes at owner+0x9E4
and +0x9E8. Their draw seams 0x4612F4/0x461304 are excluded in file mode so the
logo/caption do not conflict with cards. The sky and animated Link use other
rendering paths. Normal/MQ, fades, nested screens and performance require visual
acceptance; independent stereo eyes are not composed.

## Input transaction

The old menu shortcut waited for its menu to open before releasing its synthetic
touch. These buttons activate on release, so it reached the thirty-frame timeout.
A menu shortcut now emits one down materialization then one up materialization.
A different pending owner waits through an up sample before receiving its down.
View/I/II retain hold behavior. Physical press-edge consumption still prevents
held D-pad input from repeatedly opening menus. The existing ordered Ocarina
note queue remains separate from these menu transactions.

## Minimap marker producer

0x42AEC0 writes player quad 2; 0x42B108 writes entrance quad 3 of the eight-quad
stream at 0x4FC660. The hook at 0x42B85C calls native materialization first, then
applies the map body's dx/dy only to those two quads, before the position upload
at 0x42B880. Native materialization regenerates positions from authored values;
repeated calls do not accumulate offsets. Counter/action quads are unchanged.
Native MQ mirroring precedes marker production; its final in-game alignment,
plus room/overworld/Epona transitions, still needs testing.

## Ocarina presentation

The normal control glyph quads are 67, 72, 76, 80 and 84. Labels now use their
actual bounds, not the first piece of each multipart container. Larger complete
LT/RT and face labels are centered there. Native X/Y groups, including pressed
art, move between their centers to put X left and Y top without swapping input
semantics. A remains close; B remains native A's note.

The native red card at atlas (56,160,52,34) carries A above Quit. Only its two
lettering regions are repaired/relettered; ETC1A4 alpha is preserved. The projected
card is 64x48 before the compact group scale. The Ocarina group stays 112x84 at
main-canvas (280,8); its glyph scale is independent of the group placement.
Main HUD action words increase from 7.5 to 10 pixels high. NPC fonts are unchanged.

## Targeted in-game checks

1. Cold boot; Press Start; select Normal and MQ; go back and repeat.
2. Open save cards, Start/Copy/Erase, new-file keyboard and cancel paths. Check
   live sky, card art, selection highlight, absence of brown background on main,
   no logo/caption collision, and no old mode image on the lower display.
3. Tap and hold D-pad Right. Confirm prompt opening without a long depressed
   button; close with A; repeat. Verify LB/RB hold and release item behavior.
4. Compare player/entrance markers with the relocated minimap, then change rooms,
   open/close Ocarina/pause, and repeat in MQ and on Epona.
5. Play quick alternating and repeated notes. Confirm X/Y highlight correspondence,
   centered legible labels, A above Quit, song-page transitions and cancellation.

Automated results and their limits are recorded in VALIDATION.md.
