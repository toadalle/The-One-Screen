# Secondary UI integration 1.0.10

## Item labels

1.0.9 restored alpha-098 geometry and atlas data but incorrectly coupled the label board to the refactored `Frontend` owner/swap state. Runtime testing showed the board never reached its ready/drawn diagnostics.

1.0.10 keeps the centralized presentation router for framebuffer ownership, but makes the label board lifetime depend directly on the proven retail Items state (`RETAIL_ITEMS`) while gameplay is active. This is deliberately narrow: native menu decoration is not screen-routing policy. The board still draws only at the native 0x401 submit seam and retains alpha-098's eight quads, texture slot 2, colorless profile, and menu-lane bit `0x10`.

The alpha-098 `menu_cursor00.ctxb` resource is also restored byte-for-byte and hash-checked during the build.

Expected runtime diagnostics when an Items-family menu first materializes:

- `TOS_ITEMS_098 native_state_menu_lane_ready`
- `TOS_ITEMS_098 native_state_menu_lane_drawn`
