#include "platform/physical.h"
#include "input/bridge.h"
#include "camera/camera.h"
#include "generated/version.h"
extern s32 svcOutputDebugString(const char*,s32);
void Tos_Before(GlobalContext* play) {
    static int initialized;
    if(!initialized){Physical_Init();static const char marker[]="TOS_BUILD " TOS_VERSION " clean_backend\n";svcOutputDebugString(marker,sizeof(marker)-1);initialized=1;}
    Bridge_Update(play);
}
void Tos_After(GlobalContext* play){Camera_UpdateOrbit(play);}
void* Tos_ObserveRegister(void* renderer,void* board,u32 a,u32 b) {
    /* Diagnostics-only: deliberately do not cache borrowed native nodes. */
    void* node=Retail_Register(renderer,board,a,b);
    static int logged;if(!logged){static const char marker[]="TOS_FRONTEND native_registration_observed_replay_disabled\n";svcOutputDebugString(marker,sizeof(marker)-1);logged=1;}
    return node;
}
