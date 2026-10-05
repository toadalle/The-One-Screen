# Frontend presentation 1.1.3

## Intended behavior

- Mode/file/name-entry promoted foregrounds retain the live title sky and do not draw the brown lower-screen backdrop on main.
- Native selectors and cards remain untouched.
- Save select attempts to hide only the rotating title-scene Link actor during the upper render.
- Frontend/title fade timing remains native, but the fade primitive is queued on a native 400-wide lane instead of the stock 320-wide lower-screen lane.

## Runtime diagnostics

`TOS_FILE_LINK player_draw_hidden` means the guarded player actor was found and its draw callback was suppressed for the top pass. If Link remains visible despite this marker, the rotating model is not rendered through that callback. If the marker never appears, the title scene does not expose the model as the standard player actor through the recovered GlobalContext seam.

`TOS_FRONTEND_FADE queued_400wide` means an active frontend fade was advanced and a native 400-wide black rectangle was queued.

## Validation limit

Compilation/static tests cannot prove either visual result. Azahar screenshots and log diagnostics remain the acceptance test.
