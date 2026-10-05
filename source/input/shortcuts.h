#pragma once
#include <stdint.h>
#include "../platform/hid.h"

typedef enum {
    SHORTCUT_NONE,
    SHORTCUT_ITEMS,
    SHORTCUT_GEAR,
    SHORTCUT_MAP,
    SHORTCUT_OCARINA,
    SHORTCUT_PAUSE
} ShortcutAction;

/* 1.1 controller layout. Keep the semantic actions centralized so presentation
 * and input code never have to infer meaning from a physical button name.
 *
 * D-pad Up    -> Items
 * D-pad Down  -> Gear
 * Start       -> Pause
 * Select      -> Map
 * D-pad Right -> Ocarina
 * D-pad Left  -> View (held, handled separately)
 */
static inline ShortcutAction Shortcut_FromEdges(uint32_t edges) {
    /* Preserve the established semantic priority if simultaneous edges occur:
     * Items > Gear > Map > Ocarina > Pause. */
    if(edges & BUTTON_UP) return SHORTCUT_ITEMS;
    if(edges & BUTTON_DOWN) return SHORTCUT_GEAR;
    if(edges & BUTTON_START) return SHORTCUT_PAUSE;
    if(edges & BUTTON_RIGHT) return SHORTCUT_OCARINA;
    if(edges & BUTTON_SELECT) return SHORTCUT_MAP;
    return SHORTCUT_NONE;
}

#define SHORTCUT_VIEW_BUTTON BUTTON_LEFT
#define SHORTCUT_MASK (BUTTON_START|BUTTON_SELECT|BUTTON_UP|BUTTON_DOWN|BUTTON_LEFT|BUTTON_RIGHT)
