# Ocarina and inventory repair - 1.0.4

## Ocarina feedback

The 108-quad native renderer has separate normal and pressed families. Normal
X is 73-76, Y is 77-80. Pressed X rims are 97-98 and its sparkle is 105; pressed
Y rims are 99-100 and its sparkle is 106. The 1.0.3 projection moved only normal
quads. That left pressed effects at the other button, matching the user's images.
1.0.4 applies one translation to all members of each group. Translation comes
from authored glyph centers; labels use their own materialized glyph position,
so pressing X cannot move Y's label anchor or vice versa.

The native construction at 0x467D28 uses positions at owner+0x68 and sizes at
owner+0x3C8. Texture sizes/coordinates start at 0x509B0C / 0x509E6C. These tables
place 97/98/105 around the native X button and 99/100/106 around native Y.
The swap is limited to playable/transition controls; the song-page dynamic tail
keeps its native positions. Physical note mappings remain unchanged.

## Song sheet and accessories

The selector is the native object at Ocarina owner+0x0C. The generic position
accessor 0x2FC3FC returns authored +0x0C vertices; it does not include selection
translation. The copy now uses the materialized +0x10 stream after 0x2F9A1C,
matching the board. This fixes the cursor stuck above the song grid.

The selected-song title was absent because it is a separate text group at
owner+0x10, not part of the copied board. Native 0x2F7684 materializes its current
children: 9 for group mode 2, 1 for mode 3, otherwise 2. On the settled song page
we temporarily transform child X/Y and scale, materialize/draw, then restore and
materialize native state. No node is retained across frames or allocations.
The title keeps its native lettering pending the remaining UI font work.

Quad 58 is only the left border of the music-sheet button. Quad 61 is its full
52x32 content at (264,204). RB and the synthetic song-button touch now center on
61. Main Quit uses the existing HUD A label above the existing 22x22 bubble,
with Quit inside. The extra red card is removed and its atlas patch is reverted.

## Inventory labels

The supplied request explicitly specifies native X -> Xbox Y, Y -> X, I -> LT,
II -> RT. Those text-only cells are updated in menu_top_parts00. Controller
bindings and input semantics remain unchanged. Existing I/II item shortcuts are
LB/RB; an asynchronous question asks whether LT/RT was intended as a label or a
control change. Until clarified, this release follows the literal visual labels
without remapping input. This is a known labeling/control mismatch to resolve.

The local 1.0.3 log confirms this atlas override is loaded. Its installed file
matches the built file. The supplied inventory screenshot still shows native
labels; therefore the updated mapping must be checked in-game, including any
custom-texture interaction or separate menu draw source. Atlas tests establish
the replacement bytes and preserved art, not acceptance of every runtime label.

## Validation focus

Built ARM checks cover independent pressed label/effect geometry, RB centering,
A/quit placement, cursor translation, song-title transform/restoration and the
song-page dynamic tail. Texture checks cover allowed label regions and unchanged
containers. Test X and Y separately, scroll across all 12 songs, check the selected
title, use RB in both directions, and verify the inventory strip against controls.
No 1.0.4 in-game validation is claimed.
