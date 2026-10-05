#include "bridge.h"
#include "../platform/physical.h"
#include "../platform/hid.h"
#include "../frontend/owner.h"
#include "../frontend/ocarina.h"
#include "shortcuts.h"

typedef enum { TOUCH_NONE,TOUCH_ITEMS,TOUCH_GEAR,TOUCH_MAP,TOUCH_OCARINA,TOUCH_VIEW,TOUCH_I,TOUCH_II,TOUCH_SONG } TouchAction;
typedef struct { TouchAction action; u16 x,y; u32 ticks; } TouchRequest;
static TouchRequest request,previous;
static u32 consumed;
static PadCursor noteCursor;
static NoteQueue noteQueue;
static u32 lastNoteState;
/* Exported for RPC/debugger inspection without per-note logging overhead. */
volatile u32 tosInputMetrics[4]; /* queue depth, peak, ring overruns, queue overflow */
static Owner lastOwner=OWNER_OTHER;
static Physical physical;
static int pauseNative;
static void touch(TouchAction a,u16 x,u16 y) { request=(TouchRequest){a,x,y,0}; }
static void inject(GlobalContext* p,u32 b) {
    *(u32*)((u8*)p+0x14)|=b;*(u32*)((u8*)p+0x18)|=b;
}
static int gameOwns(GlobalContext* p) {
    return RETAIL_FN(u8(*)(void*),0x003769D8u)((u8*)p+0x28A0)!=0 ||
        p->activeCamera!=0 || p->mainCamera.status!=7;
}
static void remapGameplayFace(GlobalContext* p) {
    u32* held=(u32*)((u8*)p+0x14),*pressed=(u32*)((u8*)p+0x18),*released=(u32*)((u8*)p+0x1C);
    Digital native={*held,*pressed,*released};
    Digital mapped=Input_TranslateDigital(native,INPUT_GAMEPLAY);
    *held=mapped.held;*pressed=mapped.pressed;*released=mapped.released;
}
void Bridge_Update(GlobalContext* p) {
    physical=Physical_Read();pauseNative=0;
    Frontend f=Frontend_Read();
    if(!Retail_Pointer(p)){request.action=TOUCH_NONE;consumed|=physical.pad.held;return;}
    /* Alpha-098 semantic lane mapping, now kept in the centralized input
     * bridge. Apply it before pause/menu consumers so assigning with physical
     * X writes the native Y slot and physical Y writes the native X slot.
     * The Ocarina owns a separate note translation below; do not double-map it. */
    if(f.owner!=OWNER_OCARINA)remapGameplayFace(p);
    const u32 shortcuts=SHORTCUT_MASK;
    consumed &= physical.pad.held;
    if(lastOwner!=f.owner) {
        /* No held control becomes a new press when a frontend hands back input. */
        consumed|=physical.pad.held & shortcuts;
        if(f.owner!=OWNER_GAME)request.action=TOUCH_NONE;
        lastOwner=f.owner;
    }
    u32 edges=physical.pad.pressed & ~consumed;
    consumed|=edges & shortcuts;
    if(f.owner==OWNER_OCARINA) {
        request.action=TOUCH_NONE;
        Digital notes=Input_TranslateDigital(physical.pad,INPUT_OCARINA);
        const u32 noteMask=BUTTON_A|BUTTON_B|BUTTON_X|BUTTON_Y|BUTTON_L1|BUTTON_R1;
        u32* held=(u32*)((u8*)p+0x14),*pressed=(u32*)((u8*)p+0x18),*released=(u32*)((u8*)p+0x1C);
        *held=(*held&~(noteMask|BUTTON_START|BUTTON_SELECT))|(notes.held&noteMask);
        *pressed=(*pressed&~(noteMask|BUTTON_START|BUTTON_SELECT))|(notes.pressed&noteMask);
        *released=(*released&~(noteMask|BUTTON_START|BUTTON_SELECT))|(notes.released&noteMask);
        if(edges&(BUTTON_START|BUTTON_SELECT))inject(p,BUTTON_B);
        if(physical.extension.pressed&IRRST_BUTTON_ZR) {
            u16 x,y;if(Ocarina_SongTouch(&x,&y))touch(TOUCH_SONG,x,y);
        }
        return;
    }
    if(f.owner==OWNER_PAUSE || f.owner==OWNER_BOSS || f.owner==OWNER_VISIONS_SELECTOR) {
        request.action=TOUCH_NONE;
        *(u32*)((u8*)p+0x14)&=~(BUTTON_START|BUTTON_SELECT);
        *(u32*)((u8*)p+0x18)&=~(BUTTON_START|BUTTON_SELECT);
        if(edges&(BUTTON_START|BUTTON_SELECT)){inject(p,BUTTON_B);Frontend_RequestClose();}
        if(*(u32*)((u8*)p+0x18)&BUTTON_B)Frontend_RequestClose();
        return;
    }
    if(f.owner!=OWNER_GAME || gameOwns(p)) {
        request.action=TOUCH_NONE;consumed|=physical.pad.held&shortcuts;return;
    }
    *(u32*)((u8*)p+0x14)&=~shortcuts;
    *(u32*)((u8*)p+0x18)&=~shortcuts;
    *(u32*)((u8*)p+0x1C)&=~shortcuts;
    /* Menu buttons activate on release. Materialization consumes one down
     * sample, then emits up; waiting for menu activation here deadlocks until
     * the old thirty-frame timeout. Held View and I/II remain separate. */
    if(request.action>=TOUCH_ITEMS && request.action<=TOUCH_OCARINA)return;
    switch(Shortcut_FromEdges(edges)) {
        case SHORTCUT_ITEMS: touch(TOUCH_ITEMS,224,221); break;
        case SHORTCUT_GEAR: touch(TOUCH_GEAR,96,221); break;
        case SHORTCUT_MAP: touch(TOUCH_MAP,160,221); break;
        case SHORTCUT_OCARINA: touch(TOUCH_OCARINA,8,235); break;
        case SHORTCUT_PAUSE:
            request.action=TOUCH_NONE;pauseNative=1;inject(p,BUTTON_START);break;
        default:
            if(physical.pad.held&SHORTCUT_VIEW_BUTTON)touch(TOUCH_VIEW,3,3);
            else if(request.action==TOUCH_VIEW)request.action=TOUCH_NONE;
            break;
    }
    /* Single touchscreen owner: I/II never overlap. A release sample is emitted
     * before handing control to the opposite held bumper. */
    if(request.action==TOUCH_I || request.action==TOUCH_II) {
        u32 mask=request.action==TOUCH_I?IRRST_BUTTON_ZL:IRRST_BUTTON_ZR;
        if(!(physical.extension.held&mask))request.action=TOUCH_NONE;
        return;
    }
    if(request.action==TOUCH_NONE && previous.action==TOUCH_NONE) {
        if(physical.extension.pressed&IRRST_BUTTON_ZL)touch(TOUCH_I,316,3);
        else if(physical.extension.pressed&IRRST_BUTTON_ZR)touch(TOUCH_II,318,238);
    }
}
void Bridge_TouchMaterialized(u16* x,u16* y,u8* activeOut) {
    if(request.action==TOUCH_NONE && previous.action==TOUCH_NONE)return;
    /* A new touch owner must see an up sample before its down sample. Keep
     * the pending request across that release instead of merging two taps. */
    int active=request.action!=TOUCH_NONE &&
        (previous.action==TOUCH_NONE || previous.action==request.action);
    if(active){RETAIL_HALF(RETAIL_CANON_TOUCH+2)=request.x;RETAIL_HALF(RETAIL_CANON_TOUCH+4)=request.y;}
    RETAIL_BYTE(RETAIL_CANON_TOUCH)=active;
    RETAIL_HALF(RETAIL_EDGE_TOUCH+2)=active?request.x:previous.x;
    RETAIL_HALF(RETAIL_EDGE_TOUCH+4)=active?request.y:previous.y;
    *x=active?request.x:previous.x;
    *y=active?request.y:previous.y;
    *activeOut=active;
    /* Native code immediately computes held/pressed/released/repeat from these
     * outputs. Do not overwrite its history or synthesize a second edge. */
    if(active)previous=request;else previous.action=TOUCH_NONE;
    if(active && (request.action==TOUCH_SONG ||
       (request.action>=TOUCH_ITEMS && request.action<=TOUCH_OCARINA)))request.action=TOUCH_NONE;
}
u32 Bridge_OcarinaMask(u32 mask,u32 controller) {
    if(controller)return mask;
    u32 state=Retail_OcarinaState();
    int active=state==4 || state==12 || state==16;
    if(!active) {
        lastNoteState=0;Notes_Clear(&noteQueue);noteCursor.ready=0;
        return mask;
    }
    if(lastNoteState!=state){Notes_Clear(&noteQueue);noteCursor.ready=0;lastNoteState=state;}
    PadBatch batch=Physical_ReadHistory(&noteCursor);
    const u32 bits=BUTTON_A|BUTTON_X|BUTTON_Y|BUTTON_L1|BUTTON_R1;
    for(u32 i=0;i<batch.count;i++) {
        Digital p={batch.held[i],0,0};
        Notes_Push(&noteQueue,Input_TranslateDigital(p,INPUT_OCARINA).held&bits);
    }
    u32 result=Notes_Next(&noteQueue);
    tosInputMetrics[0]=noteQueue.count;
    if(noteQueue.count>tosInputMetrics[1])tosInputMetrics[1]=noteQueue.count;
    tosInputMetrics[2]=noteCursor.overruns;tosInputMetrics[3]=noteQueue.overflows;
    return (mask&~bits)|result;
}
u32 Bridge_PauseMask(void){
    u32 native=RETAIL_FN(u32(*)(void),0x0033B5ECu)();
    if(!Retail_Gameplay())return native;
    return (native&~BUTTON_START)|(pauseNative?BUTTON_START:0);
}
int Bridge_ViewOwned(void){return request.action==TOUCH_VIEW;}
