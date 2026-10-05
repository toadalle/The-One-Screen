# Secondary-screen repair — 1.0.7 test and evidence

**Not emulator tested; do not describe this as fully repaired.** This
pass is based on the supplied 1.0.6 screenshots plus an Azahar log with
`TOS_BUILD 1.0.6` and `TOS_ITEM_UV 0000`.

## Changed in 1.0.7

- **Full-size Ocarina:** The 1.0.6 native draw kept original large letters
  and superimposed another LT/RT/X/Y/B layer, causing the doubled-looking
  labels. Original USA Rev1 UV tables independently prove the isolated large
  19x22 cells (x=392,416,440,464,488; y=232). The atlas now replaces exactly
  these independent cells. Native draw moves entire X/Y groups, including
  pressed effects, but draws the large text just once. Shared staff X/Y cells
  and input are unchanged.
- **Projected song sheet:** Static native Ocarina quad tables establish
  q32/33 as its left-bottom border/background, q34 as the red Quit card,
  and q48/49 as alternate backing. 1.0.6 excluded only q34, leaving the
  empty black card. 1.0.7 excludes all FIVE exact quads solely on the main
  sheet. Native lower-screen red Quit remains. It also removes the stray RB
  label beside the compact PLAY Ocarina, without touching the song-button
  touch/input handling. No change to LT/RT small staff styling in this pass.
- **Inventory:** 1.0.6's runtime `TOS_ITEM_UV 0000` proves all four
  expected labels are absent from the 92-quad HUD stream. Native producer
  remains unidentified. A scoped native lower visual replacement copies
  existing stone sidebar pixels over the original four fixed-position text
  markers (and draws LT/Y/X/RT with existing project glyphs) on settled
  Items/Gear/Map only, without changing assignments or native renderer data.
  This is an interim visual fallback, susceptible to native transition
  changes; the native producer should still be recovered for a final port.
  `TOS_ITEM_OVERLAY ACTIVE` logs once if it actually draws.
- **Title dark band:** No defensible native-fade producer identification
  from current logs/source. Existing duplicate-lower-fade guard is retained;
  global viewport/fade routing was not modified. This symptom remains
  unverified, not reported as fixed.

## Tests

Cross-compile with the exact expected USA Rev 1 executable hash, all 45
original patch bytes, resource round-trips, independent dedicated large
native glyph cell verification, exact Quit-group source coordinates,
static no-second-layer check, full ZIP CRC and packaged checksums. This
build uses available clang target ARM rather than claiming bitwise Zig
parity. Unicorn/ARM tests and in-emulator visuals remain unrun.

## Azahar test sequence

1. Preserve 1.0.4, install the whole 1.0.7 load tree after clearing old files.
2. On full-size playable Ocarina, inspect LT/RT/X/Y/B for single crisp text,
   correct layout and pressed movement. Test five notes and A Quit.
3. Open learned-song sheet; check that the native red Quit remains on the
   secondary display while the main projected sheet has no black leftover.
4. Open Items, Gear, Map; inspect four labels and look for both `TOS_BUILD`
   and `TOS_ITEM_OVERLAY ACTIVE` in the log. Check item selection and controls.
5. Photograph first PRESS START title dark band separately. This remains a
   named diagnostic, not a verified correction.
