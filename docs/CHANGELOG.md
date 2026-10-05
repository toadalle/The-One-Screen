# 1.1.12

Restore RB above the native music-sheet icon in the compact Ocarina overlay, anchored to the icon bounds. Inputs and frontend rendering are unchanged.

# 1.1.11 current update

Current host and ARM checks pass. Natural Azahar boot trace confirms pass-scoped background/fade decisions. Final visual acceptance remains pending. See TEST_NOTES_1.1.11.md and RUNTIME_SMOKE.json.

The material below is historical.

# 1.1.10 — Mode Select backdrop tail split

- Keep 1.1.9's immediate projected-routing reset so the next real secondary-screen 0x401 pass retains its native background.
- Add a separate Mode Select backdrop-tail lifetime for the late `common_bg01` producer that can run after the promoted resolve. This removes the brown panel from the promoted PRESS START/Mode Select view without re-blackening the secondary screen.
- Clear that tail on the next real 0x400 target or a fresh native 0x401 target, so it cannot leak into the following lower-screen frame.
- Leave alpha-098 File Select replay/backdrop suppression, controller mapping, inventory labels, Ocarina, HUD, and fade-width work unchanged.

# 1.1.8

- Keep alpha-098 File Select backdrop suppression unchanged.
- Reuse only the two proven backdrop seams (0x00419820 / 0x0041EE2C) on the generalized projected pass used by title handoff/name-entry.
- Restore the exact COmoteUraSelector common_bg01 producers at 0x0043FE30 / 0x0044015C, suppressing only their promoted repeat.
- Do not restore the unsafe generic 0x0030005C canvas hook, file-preview suppression, or Link/object filtering.

# 1.1.7

- Fixed immediate boot crash from the 1.1.6 File Select backdrop hook.
- Restored alpha-098's exact separate ABI wrappers for `0x00419820` and `0x0041EE2C`.
- No changes to gameplay controls, HUD, Ocarina, item mapping, or File Select pass logic.

# 1.1.5

- Recovery release: reverted the 1.1.4 projected-backdrop and file-preview suppression experiments that removed or blacked out native frontend UI.
- Removed the ineffective title-player draw suppression from 1.1.3.
- Restored the intact promoted mode/file-select path and native file-select resources.
- Retained Start = Pause/System, Select = Map, Up = Items, Down = Gear, the proven item mappings, Ocarina logic, and the 400-wide frontend fade experiment.
- Rotating file-select Link/background cleanup is deferred until an isolated producer is identified.

# 1.1.3 — live sky + full-width frontend transition

- Restore projection-only suppression of the lower-screen canvas/common/mode backdrops so mode/file/name-entry foregrounds keep the live title sky instead of the brown lower-screen background.
- Keep the native file selector untouched; do not restore the incorrect 1.1.1 `file_rotating_link` hook.
- Attempt rotating-Link suppression through the title scene's guarded player actor draw callback only while file select owns the top render. The callback is restored before the lower pass; `TOS_FILE_LINK player_draw_hidden` proves the guard actually found a player actor.
- Replace the retail frontend fade's lane 6 (native 320-wide rectangle) with native lane 3 (400-wide rectangle), while preserving the original +/-8 alpha timing. `TOS_FRONTEND_FADE queued_400wide` proves the full-width fade was queued.
- Leave Start -> Pause/System, Select -> Map, item lanes, LB/RB labels, Ocarina behavior and gameplay routing unchanged.

# 1.1.2 — selector restore and native frontend backdrop

- Restore the retail file-select selector path; remove the incorrect 1.1.1 `RETAIL_FILECHOOSE+0x34` suppression that hid the selector but did not hide the title-scene Link.
- Stop suppressing native lower-screen backdrops during frontend projection. Mode select, file select and name entry now project their complete native foreground/backdrop over the upper title scene, so the title logo and rotating title Link cannot bleed through behind the cards.
- Remove obsolete queued-node, canvas/common-backdrop and mode-backdrop interception hooks. The frontend projection path drops from 45 to 39 guarded executable patches.
- Treat game modes 1 and 2 directly as frontend fade states instead of relying on the `Retail_Gameplay()` heuristic. Advance fade timing without queueing the native 320-wide blackout rectangle.
- Add one-time `TOS_FRONTEND_FADE state_only_fullwidth` diagnostics when the suppressed frontend fade is actually active.
- Keep the user-confirmed item labels/mapping, Ocarina, HUD, and 1.1 Start/Select layout unchanged.

# 1.1.1 — frontend polish

- Swap Start/Select semantics to the more conventional layout: Start -> Pause/System, Select -> Map. D-pad Up/Down remain Items/Gear.
- Hide the independently drawn rotating Link presentation object while save-select cards own the promoted foreground, preserving the live title sky/background.
- Suppress the native title/logo decorations during mode select as well as file select; retain them on the initial PRESS START title.
- Replace the promoted frontend's 320x240 blackout draw with state-only fade advancement, preventing the partial-width black rectangle while preserving transition timing/state.
- Keep the user-confirmed 1.0.11 item/Ocarina core, alpha-098 menu labels, LB/RB placement and screen-routing architecture unchanged.

# 1.1.0 — controller-layout foundation

- Freeze the user-confirmed 1.0.11 gameplay/item/Ocarina core as the functional baseline.
- Swap gameplay shortcut bindings without changing menu ownership: D-pad Up -> Items, D-pad Down -> Gear, Start -> Map, Select -> Pause.
- Keep D-pad Right -> Ocarina and held D-pad Left -> View.
- Centralize the physical-to-semantic shortcut map in `source/input/shortcuts.h` and add host assertions for every binding.
- Update the main HUD D-pad labels from MAP/PAUSE to ITEMS/GEAR while preserving the existing layout and controller-face geometry.
- Preserve Start/Select as Ocarina Quit and menu Back/Quit shortcuts, and preserve native D-pad navigation once a menu owns input.

# 1.0.11

- Restored alpha-098's semantic Xbox X/Y item-lane mapping: physical Y -> native X, physical X -> native Y.
- Applied the swap in the centralized input bridge for gameplay and pause menus so item use and Items-page assignment match the displayed Y/X labels.
- Updated the main HUD item and button-status lanes to the same mapping.
- Kept the Ocarina note path isolated and unchanged.
- Preserved the verified 1.0.10 alpha-098 label board and menu resources.

# 1.0.10

- Decoupled item-label board activation from `Frontend.owner/swap`; live retail Items state is now the decoration lifetime oracle.
- Restored alpha-098 `menu_cursor00.ctxb` byte-for-byte.
- Kept the clean centralized presentation router and exact alpha-098 eight-quad label geometry/menu-lane semantics.

# 1.0.9 — alpha-098 native inventory integration

- Restored exactly the alpha-098 menu_top_parts00 atlas and the original eight-quad native item-label board. Reinstated its menu-lane bit, original geometry/UVs and no-color profile, drawn before native lower-screen submit. Removed ineffective 1.0.6–1.0.8 inventory UV matching and fixed-coordinate overlays.
- Kept the clean backend HUD, input and full-size Ocarina changes from 1.0.8; no input remapping or X/Y song-note atlas edits.
- Kept current targeted file-select fade logic. Title-screen dark band is **not** verified fixed.
- Static build/contract tests can establish matching resources and hook path but not Azahar visual acceptance.

# 1.0.8 (screenshot-calibrated test build; Azahar validation pending)

- Compared old alpha-098 screen-router/menu-label implementation with 1.0.7. The old build used the same `menu_top_parts00` label cells, and does not provide a proven separate ink producer. Preserve the currently working input and navigation behavior rather than transplanting obsolete hooks.
- Correct the 1.0.7 inventory fallback's coordinate mismatch: the log showed the overlay ACTIVE while it covered x235..258, well to the LEFT of the visible native yellow ink. Based on the 320x240 lower-screen placement in the screenshots, relocate its four limited stone covers to x269..292 and center LT/Y/X/RT near x274 with row centers y13/73/123/195. Use existing native stone art and HUD font.
- Stop editing the large Ocarina glyph colors. Clear alpha in only the five separate 20x24 full-size lettering cells (ETC1A4 alpha bytes), preserving all native shells, animated button geometry, staff-note atlas cells and other texture bytes. Draw one replacement text scene after the native draw, with the guarded working 1.0.6 group relocation. CPU geometry is restored; temporary GPU data survives the deferred draw.
- Keep 1.0.7 projected sheet Quit exclusion and compact stray-RB suppression. No input changes. No speculative first-title-screen fade change.
- Available static/resource/build/ZIP checks pass, but the runtime appearance and inventory fallback still need Azahar testing. See `SECONDARY_1.0.8.md`.

# 1.0.7 (unverified correction test)

- Remove the second full-size Ocarina lettering layer; replace only five
  dedicated large native glyph atlas cells with LT/RT/X/Y/B. Preserve the
  working X/Y geometry exchange and all native music-note identities.
- Remove the compact Ocarina's stray RB text pass without changing input.
- Exclude precisely q32/33/34/48/49 (red native Quit + both backing groups)
  from the projected song sheet. Original lower sheet retains the Quit card.
- When all four exact 92-quad inventory UV matches fail (as in the supplied
  1.0.6 log), apply a small Xbox-lettered stone-background cover ONLY on
  settled Items/Gear/Map pages. This is a visual fallback, not a verified
  native producer hook; it may require positional refinement after testing.
- No speculative first-title-frame viewport/fade changes. That band is
  still unverified and requires its own native producer trace.
- Static validation and host compilation do not establish in-emulator success.
  Detailed scope, risk and test instructions: `SECONDARY_1.0.7.md`.

# 1.0.6 (unverified correction experiment)

- Restrict compact Quit/RB to active play and remove copied native red Quit from
  main learned-song sheet. Leave native secondary sheet Quit untouched.
- Scope duplicate queued lower fade to the first projection pass only.
- Restore full-size Ocarina vanilla glyph cells as a non-destructive fallback,
  supply project LT/RT/X/Y/B lettering through guarded scoped native draw, and
  allow temporary button-group GPU geometry to survive the deferred draw.
- Dim the existing LT/RT native staff rectangles while preserving alpha and art.
- Add fail-closed native materialized UV lookup for inventory I/X/Y/II;
  only relabel if all exact runtime matches are found, else log match counts.
- Tested retail patch identities, host tests, resource diff and archive. Not
  emulator-tested. See `SECONDARY_FIXES_1.0.6.md`.

# 1.0.5 (experimental native secondary Ocarina)

- Added isolated full-size Ocarina glyph cells (LT/RT/X/Y/B) and native red Quit B->A lettering without altering shared song-note art or containers.
- Added draw-scoped native X/Y group exchange including pressed effects, with immediate restore of CPU/GPU positions.
- This is a *test build*, not a final repair: inventory I/X/Y/II labels remain unresolved, runtime untested. See `docs/SECONDARY_LABELS_1.0.5.md`.

# 1.0.0

Initial fresh feature implementation with separated input ownership,
presentation, HUD, Ocarina, camera and layout modules. Removed historical
global X/Y input and song glyph swaps. Added complete original-byte patch
declarations, full executable identity checks, explicit payload allocation,
deterministic root-level ZIP packaging and independent dotted version counters.

CCI ExeFS was independently decompressed and matched to the provided code.
Runtime and visual acceptance remain outstanding; see PROJECT_STATE.md.

# 1.0.1

Promote native file-select/game-mode and name-entry lanes through the existing
target/submission router without borrowed-node replay. Reduce Ocarina play
scale to 0.35 (112×84 group). Crop contextual eye/camera icons away from baked
VIEW/BACK words, using explicit upright atlas coordinates.

Add pinned Cascadia Code Regular and license, one white-fill/black-stroke
raster policy, complete LT/RT labels, custom Back text, and explicit frontend
button/keyboard cell replacements. Font conversion remains incomplete for
native dynamic headings, song groups and unconverted menu-specific textures;
see FONT_COVERAGE.md. Do not describe this patch as replacing every UI font.

Reviewed the user's Azahar log: version 1.0.0 backend marker and all four
LayeredFS replacements were present; the session ended with normal process
cleanup. Missing custom-texture warnings were present, but no fatal crash
was found in the captured session.

# 1.0.2

Restore native file-select and name-entry button/card artwork. Replace only
lettering with Cascadia Code, white fill and black outline. Remove the guessed
keyboard grid from 1.0.1; native keyboard art and lettering are restored.
Every pixel outside the declared text rectangles and all alpha values are
checked against pristine resources.

Replace file/name whole-screen swapping with same-frame foreground composition.
Keep native upper rendering active, omit the canvas/common backdrop draw calls
only during the promoted lower pass, then transfer the finished main frame.
Identify the separate COmoteUraSelector lifetime before gameMode becomes 2.
This implementation is awaiting visual validation; it is not an accepted fix.

Capture HID memory from the native reader rather than hardcoding 0x10002000.
Decode ring generations and preserve ordered Ocarina note transitions at the
native audio-input consumer. Short taps no longer collapse to the final held
state in host traces. Reset queued notes across play/song contexts; preserve
X/Y identity and B-note/A-close. Expose queue/overrun metrics for diagnosis.

Cross-compilation, exact patch gates, input traces, texture preservation and
package checks pass. No emulator acceptance is claimed for this build.

# 1.0.3

Fix the foreground draw flow to render and transfer the native lower display,
then run one bounded projection pass over the same frame's live main scene.
Exclude canvas/common backgrounds and the mode selector's specifically identified
queued background node on the projected pass. Advance lower fade animation only
once. Extend mode-owner coverage through transition states. Skip the file scene's
two decorative nodes so its logo and caption do not overlap save cards.

Replace the thirty-frame menu-touch wait with one down sample and one release.
Require a release when ownership changes between different synthetic touches.
Held View and I/II retain hold behavior. Preserve the ordered Ocarina note queue
and B-note/A-close mapping from 1.0.2.

Translate exact player/entrance marker quads 2/3 after native materialization,
before upload, using the minimap body's delta. Center larger Ocarina letters on
the native glyph geometry; move X/Y button groups with their feedback art while
preserving input semantics. Use the native red Quit card with A above Quit.
Increase the main HUD action-word height from 7.5 to 10 pixels.

Add executable ARM regression coverage for presentation, the restart ABI, touch
transactions and minimap marker isolation/restoration. Native artwork checks now
include Ocarina ETC1 block boundaries and container alpha. All automated checks
pass; in-game visual/audio acceptance for this build remains outstanding.

# 1.0.4

Move Ocarina X/Y pressed rims and sparkles with their normal button groups, using
stable authored translation and each button's own pressed label position.
Use the materialized song-cursor stream and restore the live selected-song title.
Center RB/touch on the full music-sheet button. Replace the projected red Quit
card with the existing HUD A bubble and Quit word; restore native red-card bytes.

Apply requested inventory lettering X -> Y, Y -> X, I -> LT, II -> RT. Existing
bindings remain unchanged; clarify the LT/RT versus LB/RB naming mismatch before
considering an input remap. The reported native inventory display still needs
runtime verification of the new labels.

Audit inherited assets by hash against supplied tos_1.1.5. No new replacement
container artwork is introduced. Extend ARM and pixel-preservation regressions.

# 1.1.9

Preserve the real secondary-screen backdrop during generalized title/mode
projection by clearing the projected-pass state immediately after the replay
submission completes. This prevents the next frame's native 0x401 draw from
inheriting a stale suppression state when it begins before the next 0x400 bind.

Latch Mode Select presentation only across its gameMode-1 transition handoff.
The native selector disables its interaction fields before its final transition
frames are drawn; keeping that short-lived owner prevents common_bg01 from
flashing back onto the promoted main display before File Select takes over.
File Select remains on the exact alpha-098 dual-pass path. The full-width fade
geometry is intentionally unchanged in this revision and remains a separate
follow-up item.
