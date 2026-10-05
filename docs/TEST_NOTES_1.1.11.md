# 1.1.11 test build

Work started from the supplied complete 1.1.10 archive. The 1.0.11 input, HUD, inventory and Ocarina implementation files are unchanged.

## What changed

A bounded Azahar trace showed the Mode Select background producer at 0x44015C running AFTER both lower-screen draws and resolves. The old tail flag suppressed the producer, rather than the background during the promoted draw. The two exact Mode Select producers now always execute and identify their just-created textured queue allocation. The queued callback at 0x2FEAA4 skips only that allocation in PASS_PROMOTED_LOWER. Native callbacks remain intact. Allocation identities expire after the two lower passes, and no object/shape heuristics are used.

File Select retains its alpha-098 promoted-first/native-second target and resolve ordering. Its four previously globally widened fade lanes return to native lane 6. The four fade producer calls now identify their own primitive allocations. The general lower fade uses Nintendo's original state machine and is advanced once per frame across replay. At the promoted fade callback only, the viewport becomes (0,0,stereo,400), then returns to (0,40,stereo,320). Secondary geometry is untouched.

## Visual acceptance required

1. Cold boot to PRESS START: main shows live sky/environment and PRESS START, without the brown canvas; secondary retains its native background.
2. Open Mode Select: cards, header and selector remain intact on main; secondary keeps its brown canvas.
3. Open File Select, return to Mode Select, then open File Select again: no one-frame brown flash; save cards and selector remain intact.
4. Watch black fades in both directions and when opening/canceling a save: black reaches both horizontal edges of main; the secondary fade keeps its native size. UI after each fade stays centered and unstretched.
5. Check the existing Items/Gear/Start/Select/Ocarina/View shortcuts, LB/RB assignment and independent Ocarina controls.

Do not install over stale mod contents. Back up the existing title mod, then install the complete `load/mods/0004000000033500` folder in your Azahar user directory. No emulator-wide controller remapping is needed.

## Evidence and limits

Build and verified retail/resource identities passed. Host verify, inventory contracts, frontend artwork checks, native secondary contracts, shortcut contracts, current frontend contracts, ARM input/render regression, ARM Ocarina composition and new ARM frontend pass tests passed.

The new ARM test executes the real payload and covers native/promoted background isolation, unrelated callbacks, allocation expiry, full-width fade viewport/restoration, single fade advancement, Mode -> File handoff, and alpha-098 replay. It does not prove pixel output.

A fresh natural Azahar boot (no movie) observed 25 background DRAW callbacks on native, 25 SUPPRESS callbacks on promoted, and one full-width fade callback. See RUNTIME_SMOKE.json and FRONTEND_TRACE_1.1.11.txt. An earlier old prerecorded movie desynchronized and was excluded from this evidence. The runtime evidence is trace-only; final pixel appearance, natural controller transitions and gameplay acceptance remain pending.

An Ocarina fixture inherited from an older build expected a stray RB glyph that the unchanged 1.0.11 code deliberately hides. The same test failed on 1.1.10. Its expectation was corrected to verify that the glyph stays hidden; the Ocarina implementation was not changed.

## Bounded diagnostics

`TOS_PASS` logs twelve frames per owner/state change. Eleven hex fields: site, target command, live owner, gameMode, foregroundFrame, frameOwner, lowerPass, projecting, activePass (0 native top / 1 promoted / 2 native lower), FileSelect pass (0 idle / 1 top / 2 lower), decision (0 draw / 1 suppress / 2 full-width fade). Mode producer records say DRAW because the queue entry is deliberately preserved.

## New Xbox artwork pack

The supplied pack was inspected. It contains 50 high-resolution replacement PNGs, including native menu artwork and controller glyphs. Its README requires Henriko textures plus a different single-screen mod and global A/B and X/Y remaps. Those instructions were treated as reference material, not changes authorized for this project's controls. No texture overlay from that pack is installed in this test build: its runtime texture hashes and semantic labels need adaptation to this project's modified CTXB resources. The original supplied ZIP is preserved in Project Materials.
