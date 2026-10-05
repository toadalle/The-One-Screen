#include "items.h"
#include "../render/scene.h"

extern s32 svcOutputDebugString(const char*,s32);

/* Alpha-098 used one shared, eight-quad menu board: the first four sample
 * neutral stone to hide the retail I/X/Y/II ink, and the last four sample
 * LB/Y/X/RB from menu_top_parts00.ctxb. Do not route this through the HUD
 * 92-quad renderer, and do not draw a glyph from the generic white HUD atlas.
 * The 0x10 menu-lane flag and exact 320x240 positions are essential. */
static Scene itemLabels;
static int visible,loggedReady,loggedDraw;

static void geometry(void) {
    static const Rect cover[] = {
        {268.f,7.f,17.f,15.f}, {269.f,65.f,14.f,14.f},
        {258.f,117.f,15.f,14.f}, {268.f,190.f,17.f,15.f}
    };
    static const Rect replacement[] = {
        {270.f,9.f,13.f,11.f}, {272.f,67.f,9.f,10.f},
        {261.f,119.f,9.f,10.f}, {270.f,192.f,13.f,11.f}
    };
    static const Rect ink[] = {
        {156.f,125.f,19.f,17.f}, {156.f,142.f,19.f,16.f},
        {156.f,158.f,19.f,16.f}, {156.f,190.f,19.f,17.f}
    };
    for(u32 i=0;i<4;i++) {
        Scene_Rect(&itemLabels,i,cover[i]);
        Scene_UV(&itemLabels,i,512,256,(Rect){8.f,8.f,8.f,8.f});
        Scene_Rect(&itemLabels,i+4,replacement[i]);
        Scene_UV(&itemLabels,i+4,512,256,ink[i]);
    }
}

void Items_BeforeSubmit(void) {
    /* Keep the clean presentation owner model for screen routing, but do not
     * make native menu decoration depend on that abstraction. Alpha-098 proved
     * this board belongs to the live Items renderer itself. The raw retail
     * Items state is therefore the lifetime oracle for the label strip. */
    const u32 itemsState=RETAIL_WORD(RETAIL_ITEMS);
    const int active=Retail_Gameplay() && itemsState!=0u;
    if(!active && !visible)return;
    if(!Scene_EnsureColorless(&itemLabels,8,2))return;
    RETAIL_WORD((u32)itemLabels.node+0x178u)|=0x10u;
    if(!loggedReady) {
        static const char msg[]="TOS_ITEMS_098 native_state_menu_lane_ready\n";
        svcOutputDebugString(msg,sizeof(msg)-1);loggedReady=1;
    }
    if(active)geometry();else Scene_Clear(&itemLabels);
    Scene_Upload(&itemLabels);
    visible=active;
    if(active && Scene_Draw(&itemLabels) && !loggedDraw) {
        static const char msg[]="TOS_ITEMS_098 native_state_menu_lane_drawn\n";
        svcOutputDebugString(msg,sizeof(msg)-1);loggedDraw=1;
    }
}
