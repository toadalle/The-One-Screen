#include "file_select.h"

extern s32 svcOutputDebugString(const char*,s32);

/* Proven alpha-098 FileSelect_Activate owner (USA Rev 1).  This is intentionally
 * a native-state bridge rather than an inferred Frontend owner: alpha-098 used
 * this exact lifetime signal successfully for mode/file/name frontend passes. */
#define FILE_SELECT_OWNER ((volatile u8*)RETAIL_FILECHOOSE)

static FileSelectPass passState;
FileSelectPass FileSelect_CurrentPass(void) { return passState; }
static u8 loggedReady,loggedTop,loggedReplay,loggedLower;

static void log_once(u8* flag,const char* text,u32 length) {
    if(*flag)return;
    *flag=1;
    svcOutputDebugString(text,(s32)length);
}

int FileSelect_Active(void) {
    return RETAIL_SAVE->gameMode==2 &&
           *(volatile u32*)(FILE_SELECT_OWNER+0x10)!=0;
}

void FileSelect_ResetIfInactive(void) {
    if(!FileSelect_Active())passState=FILE_SELECT_PASS_IDLE;
}

FileSelectPass FileSelect_BeginPass(void) {
    if(!FileSelect_Active()) {
        passState=FILE_SELECT_PASS_IDLE;
        return FILE_SELECT_PASS_IDLE;
    }
    static const char ready[]="TOS_FILESELECT_098 native_frontend_dual_pass_ready\n";
    log_once(&loggedReady,ready,sizeof(ready)-1);
    if(passState==FILE_SELECT_PASS_LOWER)return FILE_SELECT_PASS_LOWER;
    passState=FILE_SELECT_PASS_TOP;
    static const char top[]="TOS_FILESELECT_098 top_pass_begin\n";
    log_once(&loggedTop,top,sizeof(top)-1);
    return FILE_SELECT_PASS_TOP;
}

int FileSelect_SuppressTopBackdrop(void) {
    return FileSelect_Active() && passState==FILE_SELECT_PASS_TOP;
}

int FileSelect_SubmitBottomAndMaybeReplay(void* renderer,u32 command) {
    if(!FileSelect_Active()) {
        passState=FILE_SELECT_PASS_IDLE;
        Retail_Submit(renderer,command);
        return 0;
    }
    if(passState==FILE_SELECT_PASS_TOP) {
        /* Exact alpha-098 contract: the promoted 0x401 draw resolves through
         * 0x400, then the same native lower draw span is replayed. */
        Retail_Submit(renderer,0x400u);
        passState=FILE_SELECT_PASS_LOWER;
        static const char replay[]="TOS_FILESELECT_098 top_resolved_replay_lower\n";
        log_once(&loggedReplay,replay,sizeof(replay)-1);
        return 1;
    }
    if(passState==FILE_SELECT_PASS_LOWER) {
        Retail_Submit(renderer,0x401u);
        passState=FILE_SELECT_PASS_IDLE;
        static const char lower[]="TOS_FILESELECT_098 native_lower_replay_complete\n";
        log_once(&loggedLower,lower,sizeof(lower)-1);
        return 0;
    }
    Retail_Submit(renderer,command);
    passState=FILE_SELECT_PASS_IDLE;
    return 0;
}
