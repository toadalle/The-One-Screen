# 1.0.5 secondary labels: preliminary test build

**Status: compiled and statically verified; not emulator tested. Not a project-complete release.**

This build is an isolated test of the full-size native secondary Ocarina, not
an assertion that the inventory-label problem is resolved. The 1.0.4 main HUD,
compact Ocarina, button bindings and menu-texture item mapping are preserved.

## Confirmed native contracts (USA Rev1)

- Native owner 0x5093E4: native board at +0, native renderer at +8.
- 0x42590C uploads materialized renderer +0x10 to that board via 0x36759C.
- 0x41EE74 originally calls 0x426748, the native secondary Ocarina draw.
- Quad 67 L, 72 R, 76 X, 80 Y, 84 A read five isolated native atlas
  glyphs, 19x22 UVs at x=392/416/440/464/488, y=232, distinct from
  small learned-song and staff-note symbols at y=160.
- Native X normal 73..76, pressed 97..98, sparkle 105; native Y normal
  77..80, pressed 99..100, sparkle 106.

## Experimental implementation

- Replace only full-size native play glyphs L/R/X/Y/A -> LT/RT/X/Y/B,
  using inherited 512x256 CTXB and bundled Cascadia Code raster policy.
  X/Y *glyphs* remain their original identity. Existing color notes/staff
  cells remain unchanged; no global XY input translation or extra button art.
- Wrap the native lower-screen Ocarina draw *only* in play/transition states.
  Exchange XY normal and pressed groups using live, materialized 76/80
  centers. Upload the temporary native positions, invoke the original draw,
  restore every changed vertex and upload again before return. The main HUD
  overlay does not read the modified stream between those two uploads.
- Reuse native red Quit card (quads 34/57) and repair only its baked B
  lettering to A, preserving its inherited container and alpha. The
  compact main Ocarina independently uses the existing HUD A bubble.

## Still unresolved

**Native secondary menu item-strip I/X/Y/II**: only B is visibly sampling
our menu_top override in the latest user screenshot. I/X/Y/II are not static
quads in the HUD owner's table and have no confirmed runtime texture source.
Editing the same atlas blindly is not a valid fix. A live native UV/texture
producer trace or emulator test evidence is required to finish that issue.

## Validation and rollback

Local clang ARM build is usable for inspection but not byte-equivalent to the
original Zig build. Retail SHA-256 and patch-site checks passed. Python host
contract/art tests passed; Unicorn ARM regressions cannot run in this
workspace. **No Azahar game testing has been performed.** Keep 1.0.4 as the
known-good rollback. If testing this build, focus on active Ocarina X/Y note
highlights (press each separately), LT/RT/B, small staff note symbols,
selected-song title and transition/pressed effects. Also note whether the native red Quit card now correctly shows A,
and whether I/X/Y/II still show Nintendo lettering.
