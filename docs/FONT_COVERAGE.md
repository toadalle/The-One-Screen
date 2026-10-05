# Cascadia Code UI coverage — 1.0.4

The requested style is Cascadia Code Regular, white fill and black stroke.
One raster policy (`tools/ui_font.py`) produces complete words and controller
labels; LT/RT are whole glyphs rather than assembled L+T/R+T fragments.
The pinned Microsoft v2407.24 font and its SIL Open Font License are bundled.
Source: https://github.com/microsoft/cascadia-code/releases/tag/v2407.24

Integrated:
- Custom HUD face/bumper/trigger labels, MAP/PAUSE, and numeric counters.
- Native English action-word atlas cells, keeping their native selector bounds.
- Ocarina HUD A bubble with Quit inside, centered face labels and complete
  LT/RT labels; inventory X/Y and I/II lettering.
- Identified file-select button cells, including B Back.
- Identified name-entry button lettering.

Not yet converted:
- Dynamic native menu headings, file names, timestamps and descriptions.
- Native selected-song text groups and learned-song staff glyphs. The live
  selected title is now projected, retaining its native lettering.
- Other menu-specific baked labels outside the explicitly identified cells.
- Native keyboard character, header and special-key lettering. The guessed grid
  used in 1.0.1 has been removed to restore its original artwork.

NPC dialogue and its shared font resources are not overridden. The requested
complete UI font conversion is therefore still in progress. A global shared
font replacement would also change dialogue and does not satisfy the request.
Each remaining renderer/atlas needs an explicit UI-only integration.

Native stone, coloured panels, bevels, borders and alpha silhouettes are retained.
The old dark replacement panels are removed. Only explicit lettering rectangles
are edited; inpainting repairs the texture immediately beneath the old ink, then
Cascadia Code is drawn over it. The occluded original texture cannot be recovered
exactly, so that small repair is an approximation. An automated pixel comparison
enforces that everything outside those rectangles remains identical to retail,
including every native keyboard key. In-game alignment still needs acceptance.
