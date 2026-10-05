#include "presentation.h"
#include "../frontend/items.h"
#include "../frontend/file_select.h"
extern s32 svcOutputDebugString(const char*,s32);
static int foregroundFrame,lowerPass,rightEye,projecting;
static int titleFrontendLatched;
typedef enum { PASS_NATIVE_TOP, PASS_PROMOTED_LOWER, PASS_NATIVE_LOWER } PresentationPass;
static PresentationPass activePass;
static s32 promotedStereo=480;
static void* modeBackdropNode;
static void* fadeNodes[24];
static u32 fadeNodeCount;
static int promoted_pass(void) { return activePass==PASS_PROMOTED_LOWER; }
static void forget_queued_producers(void) {
    modeBackdropNode=0;fadeNodeCount=0;
}
static Owner frameOwner;
static u32 traceCommand,traceFrames,traceSignature=~0u;
static int traceEnabled;
static char* trace_hex(char* out,u32 value) {
    static const char digits[]="0123456789abcdef";
    *out++=' ';
    for(int shift=28;shift>=0;shift-=4)*out++=digits[(value>>shift)&15];
    return out;
}
/* Twelve frames per owner/state change. Fields documented in test notes. */
static void trace(u32 site,int suppress) {
    if(!traceEnabled)return;
    Frontend f=Frontend_Read();
    char line[160]="TOS_PASS";char* end=line+8;
    u32 values[]={site,traceCommand,f.owner,RETAIL_SAVE->gameMode,
        foregroundFrame,frameOwner,lowerPass,projecting,activePass,
        FileSelect_CurrentPass(),suppress};
    for(u32 i=0;i<sizeof(values)/sizeof(values[0]);i++)end=trace_hex(end,values[i]);
    *end++='\n';svcOutputDebugString(line,(s32)(end-line));
}

static int foreground(Frontend f) {
    return f.owner==OWNER_FILESELECT || f.owner==OWNER_NAMEENTRY || f.owner==OWNER_MODESELECT;
}

/* Mode Select drops its interaction-enable fields before the native transition
 * has finished drawing the lower frontend. Keep the generalized projection
 * alive across that handoff so common_bg01 cannot flash back onto main. The
 * latch is scoped to title gameMode 1 and releases as soon as File Select or
 * gameplay takes ownership. */
static int foreground_for_frame(Frontend f,int exactFile) {
    if(exactFile) { titleFrontendLatched=0; return 0; }
    if(f.owner==OWNER_MODESELECT) titleFrontendLatched=1;
    if(RETAIL_SAVE->gameMode!=1 || Retail_Gameplay()) titleFrontendLatched=0;
    if(titleFrontendLatched && !foreground(f)) {
        static int logged;
        if(!logged){static const char marker[]="TOS_FRONTEND_BG mode_transition_hold\n";
            svcOutputDebugString(marker,sizeof(marker)-1);logged=1;}
        return 1;
    }
    return foreground(f);
}

void Presentation_Observe(void* object,u32 callback){Frontend_ObserveMovie(callback,object);}

static void bind_target(void* renderer,u32 framebufferOffset,s32 y,s32 width,s32 height,u32 command) {
    RETAIL_FN(void(*)(u32,u32),0x00311364u)(0x8D40,*(volatile u32*)((u8*)renderer+framebufferOffset));
    Retail_Viewport(0,y,width,height);
    *(volatile u32*)((u8*)renderer+0x24)=command;
}

void Presentation_Target(void* renderer,u32 command) {
    if(!Retail_Pointer(renderer)||!*(volatile u8*)((u8*)renderer+4))return;
    Frontend f=Frontend_Read();
    int exactFile=FileSelect_Active();
    traceCommand=command;
    if(command==0x400) {
        u32 signature=((u32)f.owner<<24)|((u32)RETAIL_SAVE->gameMode<<16)|f.state;
        if(signature!=traceSignature){traceSignature=signature;traceFrames=12;}
        traceEnabled=traceFrames && !Retail_Gameplay();
        if(traceFrames)traceFrames--;
    }
    trace(0x00300588u,0);
    if(command==0x400){
        /* Interaction flags can clear before the queued title frontend ends.
         * Exact producer observation holds projection through that handoff. */
        foregroundFrame=foreground_for_frame(f,exactFile);
        frameOwner=(foregroundFrame && f.owner==OWNER_OTHER && titleFrontendLatched)
            ? OWNER_MODESELECT : f.owner;
        rightEye=0;projecting=0;activePass=PASS_NATIVE_TOP;
    }
    if(command==0x410)rightEye=1;
    lowerPass=command==0x401;
    s32 stereo=*(volatile u8*)((u8*)renderer+0x75)?240:480;
    promotedStereo=stereo;

    /* Exact alpha-098 File Select target ordering: first native lower-frontend
     * draw goes to the upper framebuffer; replay goes to untouched lower. */
    if(command==0x401 && FileSelect_Active()) {
        FileSelectPass pass=FileSelect_BeginPass();
        if(pass==FILE_SELECT_PASS_TOP) {
            activePass=PASS_PROMOTED_LOWER;
            bind_target(renderer,0x38,40,stereo,320,command);
            return;
        }
        if(pass==FILE_SELECT_PASS_LOWER) {
            activePass=PASS_NATIVE_LOWER;
            bind_target(renderer,0x3C,0,240,320,command);
            return;
        }
    }

    u32 offset=0; s32 y=0,w=stereo,h=400;
    if(command==0x400 || command==0x410){offset=0x38;if(f.swap && command==0x400){offset=0x3C;w=240;h=320;}}
    if(command==0x401){offset=0x3C;w=240;h=320;if(f.swap || (foregroundFrame && projecting)){offset=0x38;y=40;w=stereo;}}
    if(command==0x401)activePass=(foregroundFrame && projecting)?PASS_PROMOTED_LOWER:PASS_NATIVE_LOWER;
    if(offset)bind_target(renderer,offset,y,w,h,command);
    else *(volatile u32*)((u8*)renderer+0x24)=command;
}

void Presentation_Submit(void* renderer,u32 command) {
    if(foregroundFrame) {
        if(command==0x400 || command==0x410)return;
    }
    Frontend f=Frontend_Read();
    if(command==0x401)Items_BeforeSubmit();
    if(f.swap){if(command==0x400)command=0x401;else if(command==0x401)command=0x400;}
    Retail_Submit(renderer,command);
}

int Presentation_EndLower(void* renderer,u32 command) {
    trace(0x004198B0u,0);
    if(FileSelect_Active()) {
        int replay=FileSelect_SubmitBottomAndMaybeReplay(renderer,command);
        if(!replay){activePass=PASS_NATIVE_TOP;forget_queued_producers();}
        return replay;
    }
    FileSelect_ResetIfInactive();
    if(!foregroundFrame){Presentation_Submit(renderer,command);activePass=PASS_NATIVE_TOP;forget_queued_producers();return 0;}
    if(!projecting) {
        Retail_Submit(renderer,0x401);projecting=1;return 1;
    }
    Retail_Submit(renderer,0x400);
    if(rightEye)Retail_Submit(renderer,0x410);
    /* Both draws have consumed this frame's exact producer allocations. */
    projecting=0;
    lowerPass=0;
    activePass=PASS_NATIVE_TOP;
    forget_queued_producers();
    return 0;
}

/* The alpha-098 File Select path suppresses its canvas on its first/top pass.
 * PRESS START/name handoff and Mode Select still use the newer replay path,
 * where the promoted main-display copy is the second pass. Reuse the same two
 * proven backdrop seams there rather than hooking the renderer globally. */
int Presentation_SuppressBackdrop(u32 site) {
    trace(site,FileSelect_SuppressTopBackdrop() || (foregroundFrame && lowerPass && projecting));
    if(FileSelect_SuppressTopBackdrop())return 1;
    if(foregroundFrame && lowerPass && projecting) {
        static int logged;
        if(!logged){static const char marker[]="TOS_FRONTEND_BG projected_backdrop_suppressed\n";
            svcOutputDebugString(marker,sizeof(marker)-1);logged=1;}
        return 1;
    }
    return 0;
}

/* Exact COmoteUraSelector background producers queue lane-6 nodes AFTER
 * EndLower (observed in Azahar). Always retain the native queue entry; identify
 * this allocation for omission only at its promoted draw callback. */
void Presentation_ModeBackdrop(void* owner,void* sprite,void* texture,void* color) {
    volatile u8* queue=(volatile u8*)0x005C0BA8u;
    u32 before=*(volatile u32*)(queue+0x0C);
    trace((u32)__builtin_return_address(0)-4,0);
    RETAIL_FN(void(*)(void*,void*,void*,void*),0x002E78F8u)(owner,sprite,texture,color);
    if(before<24 && *(volatile u32*)(queue+0x0C)==before+1) {
        modeBackdropNode=*(void* volatile*)(queue+0x154+before*4);
        if(RETAIL_SAVE->gameMode==1 && !Retail_Gameplay())titleFrontendLatched=1;
    }
}

/* Hook only the four established File Select fade producers. Preserve lane,
 * color, order and timing; remember the actual primitive allocation. */
void Presentation_FadePrimitive(void* queue,u32 lane,const float* rgba,u32 order) {
    u32 before=*(volatile u32*)((u8*)queue+8);
    RETAIL_FN(void(*)(void*,u32,const float*,u32),0x003339E8u)(queue,lane,rgba,order);
    if(lane==6 && before<24 && *(volatile u32*)((u8*)queue+8)==before+1 && fadeNodeCount<24)
        fadeNodes[fadeNodeCount++]=*(void* volatile*)((u8*)queue+0xF4+before*4);
}

/* No shape guesses, global texture deletion, or borrowed-node traversal:
 * decisions apply only to exact producer allocations in this queue lifetime. */
void Presentation_DrawQueued(void* node,void(*draw)(void*)) {
    int suppress=promoted_pass() && node==modeBackdropNode;
    if(node==modeBackdropNode)trace(0x002FEAA4u,suppress);
    if(suppress)return;
    if(promoted_pass())for(u32 i=0;i<fadeNodeCount;i++)if(node==fadeNodes[i]) {
        Retail_Viewport(0,0,promotedStereo,400);
        draw(node);
        Retail_Viewport(0,40,promotedStereo,320);
        trace(0x002FEAA4u,2);
        return;
    }
    draw(node);
}
void Presentation_QueuedNode(void* node,void(*draw)(void*)){draw(node);}
void Presentation_FileDecoration(void* node,void(*draw)(void*)){draw(node);}

/* Native fade advances once per frame. The replay reuses its queued node;
 * the native secondary keeps the original lane-6 geometry and alpha. */
void Presentation_LowerFade(void* fade) {
    int replay=projecting || FileSelect_CurrentPass()==FILE_SELECT_PASS_LOWER;
    trace(0x00419868u,replay);
    if(replay)return;
    volatile u8* queue=(volatile u8*)0x005C0BA8u;
    u32 before=*(volatile u32*)(queue+8);
    RETAIL_FN(void(*)(void*),0x0041C3C8u)(fade);
    if(before<24 && *(volatile u32*)(queue+8)==before+1 && fadeNodeCount<24)
        fadeNodes[fadeNodeCount++]=*(void* volatile*)(queue+0xF4+before*4);
}
