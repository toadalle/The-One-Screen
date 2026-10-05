# 1.0.9 — integration candidate (not yet Azahar-verified)

## Source of truth
The user's alpha-098 runtime screenshots show the secondary Items and Map sidebars with
**LB / Y / X / B / RB**. The alpha-098 `screen_router.c` shows why: the modified
menu atlas is **not enough**. A separate eight-quad native menu board covers the
retail I/X/Y/II with neutral stone quads and draws LB/Y/X/RB from that very atlas.
That board is registered using source texture slot 2 and menu-lane flag `0x10`,
and is drawn before 0x401 native lower submit. The final four replacement
coordinates/UVs and no-color profile are restored exactly.

1.0.9's generated `menu_top_parts00.ctxb` matches the original alpha-098 release
**byte-for-byte**, SHA-256 `993e3b45fb182cd47889f35f24f21ae99bbc269fc4b2371e57ce45c7b794555a`.
The ineffective later HUD UV-match and position-estimated fallback have been
removed. No extra menu_cursor replacement was added: its alpha-098 presence is
not established as causal for these label sprites.

## Unchanged / preserved
- 1.0.8's clean HUD and gameplay input, including original native item semantics.
- 1.0.8's isolated native full-size Ocarina transparent large-letter cells and
  independent labels; original small song-note cells and note inputs untouched.
- Projected song-sheet no-extra-Quit filtering and native lower-screen Quit.
- Existing frontend fade/transition logic. The previously reported title-screen
  dark vertical band is **not proven corrected** by this inventory-only recovery.

## Testing and acceptance
1. Clean-install the contents of `load/mods/0004000000033500` and verify
   `TOS_BUILD 1.0.9` in a new Azahar log.
2. Show both **Items** and **Map**: LB at first slot, Y second, X third,
   B unchanged, RB bottom, no underlying native letters or labels floating off-menu.
   Check `TOS_ITEMS_098 eight_quad_menu_lane_ready` and
   `TOS_ITEMS_098 eight_quad_menu_lane_drawn` in the log.
3. Check full-size playable Ocarina LT/RT/Y(top)/X(bottom)/B lettering and
   native A Quit, including pressed state and note correctness.
4. Check song-sheet projected main display has no added Quit or black card;
   lower native sheet retains its Quit. Check title screen for residual dark band.
5. Return screenshots + new log for unresolved runtime issues. Static tests do
   **not** substitute for this approval.

The complete project is at the ZIP root. Source and installable files are included.

The archive omits the third-party Cascadia Code font file; see README for
the optional source-rebuild input. Installable mod assets are complete.
