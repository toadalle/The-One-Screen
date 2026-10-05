# Version 1.0.8: screenshot-calibrated native labels

**Scope:** Test build, not Azahar-proven. The clean backend's gameplay mappings and known-good user controls remain unchanged. The old `tostrta-alpha-098.zip` is included in the analysis, not in the distributed ZIP.

## Why 1.0.7 looked unchanged

The latest user log confirms `TOS_BUILD 1.0.7`, `TOS_ITEM_UV 0000`, and `TOS_ITEM_OVERLAY ACTIVE`. Thus the overlay drew, but the UV lookup still missed every label. Reexamining the native screenshot reveals a coordinate error: on the 400-pixel upper canvas, the 320-wide lower menu is centered at x≈40. The photographed native yellow labels occupy native x≈274; the fallback covered x235..258, much too far left. The 1.0.8 fallback uses stone covers x269..292; LT/Y/X/RT labels are centered x274, rows 13/73/123/195. This is a targeted *visual cover*, not an identified native font producer; if the renderer uses later draw ordering or scaled transitions, it may still be insufficient.

The alpha-098 build is useful for the original working native screen routing, but its own menu top label change also replaced the same atlas cells used by the modern code. It does not establish a working dynamic I/X/Y/II font hook. Do not transplant its old global Ocarina X/Y input logic into the clean backend.

## Ocarina

The alpha-1.0.7 texture recoloring generated visibly corrupted LT/RT/X/Y/B. All five full-size glyph origins and 19x22 source bounds are verified in the supplied USA Rev 1 executable. In 1.0.8, only their dedicated ETC1A4 alpha blocks are zeroed (20x24 padded extents), so that native lettering cannot overlap a separate drawing layer; color blocks and adjacent native content are preserved. The custom five-label scene draws once, positioned from live native glyph centers and shifted with original X/Y button groups including their pressed effects. Audio/input mapping, compact overlay, native song-note cells, and native A Quit are untouched. Projected song sheets still exclude the five verified native Quit/backing quads, and the native lower song sheet retains its original control.

## Preserved unresolved issues

The title-screen dark vertical band is not fixed here: its exact producer is unproven; speculative viewport/fade edits could break file select. No claim about Azahar runtime rendering is made without the user's screenshots. The native menu label font producer remains a future reliability improvement even if the calibrated visual fallback works.

## Validation

- Original USA Rev 1 executable SHA-256 enforced by build script; 45 expected patch sites verified.
- Atlas checks assert full-size glyph alpha truly empty, neighboring native art and all shared staff-note cells preserved, and native Quit B→A retained.
- All available host-side tests and package CRC/checksums have passed. ARM emulation cannot run here because `unicorn` is missing and network access cannot install it.
- Root-level complete archive: `tos-alpha-1.0.8.zip`.

## Azahar checks

After a clean install verify `TOS_BUILD 1.0.8` in the log. On Items, Gear or Map, look for `TOS_ITEM_OVERLAY CALIBRATED_X274 11` (both cover and lettering draw calls accepted; `10`, `01` or `00` indicate which draw was rejected) and confirm the four native yellow labels are no longer exposed. Open full-sized play Ocarina and verify five clean labels plus X/Y positions; press each note, including animations, and A Quit. Browse learned song sheets and ensure the projected left copy has no extra Quit/black card; inspect the separate title dark band only as an outstanding diagnostic.
