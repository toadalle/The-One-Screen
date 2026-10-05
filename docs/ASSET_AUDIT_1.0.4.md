# Asset audit - 1.0.4

All 14 bundled PNG assets match the supplied tos_1.1.5 source/assets files
byte-for-byte. ASSET_HASHES_1.0.4.json records the hashes and matching paths.
This establishes inheritance, not the original method used to create each PNG.
The name native_A_shell_clean_38x38.png alone does not prove a lossless native
extraction. The custom D-pad likewise has no creation-history proof in this audit.

The active HUD bubble uses that inherited shell; the D-pad uses custom_DPAD.png.
The user explicitly requested reusing the existing HUD bubble for Ocarina Quit.
This iteration introduces no new container or illustrative artwork and does not
use an image-generation model. Existing procedural font rasterization creates
Cascadia Code lettering and numbers. Most older font PNGs are retained inputs;
current builders rasterize the actual text from the pinned font.

Native file/name containers are read from hash-verified retail resources. Only
specified lettering rectangles are repaired by OpenCV inpainting and relettered.
That reconstructs texture previously covered by ink; it is not exact recovery of
occluded pixels. Pixels outside declared rectangles and container alpha are
checked against retail. Inventory labels occupy isolated transparent text cells,
so no container reconstruction is required there.

The 1.0.3 red Ocarina card repair has been removed. Native card bytes are restored;
main draws the existing HUD bubble with A and Quit. Other Ocarina body, button,
song-card, cursor and title visuals come from current native geometry/textures.
X/Y controls and their feedback are relocated; they are not painted replacements.

No claim is made that every inherited custom asset is original Nintendo artwork
or that its earlier production never involved generative tools. That history is
not established by the supplied file hashes.
