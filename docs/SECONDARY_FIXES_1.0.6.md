# 1.0.6 experimental correction pass — secondary labels, Ocarina, fades

**Status: compiled, statically verified; not tested inside Azahar.**
This is a trial build, not an accepted final fix. Preserve the user-tested
`tos-alpha-1.0.4.zip` and the 1.0.5 package for comparative testing.

## Based on reported 1.0.5 screenshots and Azahar log

- Active Ocarina inputs sound the correct notes; do not modify inputs or change
  native song note symbols.
- Full-size play letters were visibly overdrawn despite the independently
  verified replacement atlas. Native button placement also remained X-top/Y-left.
- The main song-sheet copy incorrectly included a red Quit card plus an
  additional custom Quit label. The original secondary page already has Quit.
- Small LT/RT staff markers appeared brighter than the circular note symbols.
- A black/fade artifact appeared on the title menu and projected song sheet.
- Menu item-strip I/X/Y/II remains native in game even with the verified atlas
  replacement; runtime owner/UV identity has not been established.

## Attempted changes, with safety boundaries

1. **Overlay/fade and duplicate UI:** Active play now exclusively owns the
   compact custom Quit chrome and song-button RB lettering. The sheet-page copy
   excludes the native red Quit card (confirmed q34), leaving the native
   secondary Quit control untouched. Capture only a uniquely enqueued native
   lower fade node; suppress the exact node on a projected second pass. This
   can address a duplicate lower fade but does NOT establish the origin of the
   first-title-screen dark band. No general viewport/fade rewrite is attempted.
2. **Native secondary inventory labels:** Hook original native HUD draw once;
   inspect the native 92-quad materialized stream and the four exact verified
   menu_top UV rectangles. Replace those four quads only if ALL FOUR have one
   distinct in-bounds live match and a replacement scene is ready. Otherwise
   call retail unchanged. One diagnostic `TOS_ITEM_UV abcd` logs per-label match
   counts (I/X/Y/II order); `0000` means this renderer does not own those quads
   and needs another producer traced. It is possible no relabel will occur.
3. **Full-size Ocarina:** Restore the native full-size glyph atlas as fallback.
   A guarded live native draw masks exactly L/R/X/Y/A glyph quads, moves full
   native X/Y button groups INCLUDING pressed effects and sparkles, then draws
   LT/RT/X/Y/B with the same preexisting project glyph atlas as the main HUD.
   CPU geometry is restored immediately; the temporary native GPU upload is
   retained through deferred lower draw rather than immediately overwritten,
   with the next native upload expected to refresh it. All native small
   song-staff X/Y and note identity cells are unchanged.
4. **Sheet LT/RT style:** Darken only the two native rectangular trigger-cell
   color blocks to 76% brightness. Alpha, geometry and neighboring art remain
   original. Keep existing native rectangle silhouette, no new art.

The native draw hooks and deferred draw assumption have not been emulator
validated. In particular, an incorrect runtime texture owner may leave I/X/Y/II
unchanged; the targeted fail-closed path should not be mistaken for a repair.

## Tests and known limits

The retail USA Rev1 `code.bin` hash and all expected original patch bytes are
verified, and the clang ARM freestanding compilation, archive packaging,
`verify.py`, `frontend_art.py`, `native_secondary_contracts.py`, and
`secondary_1_0_6_contracts.py` pass. This environment lacks Unicorn, so
`arm_regressions.py` and `ocarina_arm.py` could not be executed. Clang local
output is NOT claimed byte-identical to the original Zig 0.14.1 build.
No emulator/gameplay testing was performed. No guarantee the title-screen band
or missing inventory labels are resolved.

## Azahar smoke-test sequence

1. Exit Azahar, keep a full backup of 1.0.4, then install the **entire** 1.0.6
   `load/mods/0004000000033500` tree, removing the old version's files first.
2. Start on the title's first PRESS START screen, photograph the dark band,
   press any button, and inspect File Select then load a save.
3. Open Items, Map, and Gear. Check for LT/Y/X/RT in every page. Inspect the
   Azahar log for `TOS_BUILD 1.0.6` and the single `TOS_ITEM_UV` line.
4. On full-size Ocarina play, independently press all notes; verify correct
   note sound and button/pressed highlight location. Check LT/RT, X-left,
   Y-top, B, and native red A Quit. Test opening/closing repeatedly.
5. Enter learned-song sheet. Verify no extra Quit on the main screen, that
   native lower Quit still works, correct unaltered Y/X/RT notes, darker LT/RT
   staff symbols, and no translucent wedge. Save a screenshot and log.
6. If there is any crash or visual regression, restore 1.0.4 and provide the
   new log and screens. Do not rely on these changes for your primary playthrough.
