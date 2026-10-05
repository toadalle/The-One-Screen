# Secondary UI integration 1.0.11

1.0.10 recovered alpha-098's native Items label board and proved it executes at runtime. The remaining mismatch was semantic: labels showed Y/X at the native X/Y slots, while the clean input bridge and main HUD still used unswapped native X/Y item lanes.

1.0.11 restores the alpha-098 Xbox item-lane contract without reintroducing the old monolithic router. Outside the Ocarina owner, the centralized input bridge swaps native X/Y in held, pressed, and released pad state before native gameplay or pause-menu consumers run. Thus physical Xbox Y drives native X, and physical Xbox X drives native Y. This also makes item assignment from the Items page land in the slot shown by the Xbox label.

The main-display HUD now mirrors the same contract: its Y position reads native X (`buttonItems[2]`, `buttonStatus[2]`) and its X position reads native Y (`buttonItems[1]`, `buttonStatus[1]`). LB/RB (native I/II), B, Ocarina behavior, and the recovered alpha-098 label board are unchanged.
