#include "owner.h"
static void* movie;
static int closing,pauseLatched;
static int movieInstalled(void) {
    return RETAIL_WORD(RETAIL_MOVIE_UPPER_SLOT)==RETAIL_MOVIE_UPPER &&
        RETAIL_WORD(RETAIL_MOVIE_LOWER_SLOT)==RETAIL_MOVIE_LOWER;
}
void Frontend_ObserveMovie(u32 callback,void* object) {
    if(callback==RETAIL_MOVIE_UPPER && movieInstalled() && Retail_Pointer(object)) movie=object;
}
void Frontend_RequestClose(void) {
    /* A native B inside a nested menu is Back, not necessarily Quit. The owner
     * remains promoted until its root state acknowledges closure. */
    if(RETAIL_WORD(RETAIL_GEAR)==2 || RETAIL_WORD(RETAIL_ITEMS)==2 ||
       RETAIL_WORD(RETAIL_MAP)==2 || RETAIL_WORD(RETAIL_SYSTEM)==2)closing=1;
}
Frontend Frontend_Read(void) {
    Frontend f={OWNER_OTHER,0,0};
    if(RETAIL_WORD(RETAIL_NAMEENTRY+4))return (Frontend){OWNER_NAMEENTRY,RETAIL_WORD(RETAIL_NAMEENTRY+4),0};
    u32 fileState=RETAIL_WORD(RETAIL_FILECHOOSE+0x10);
    /* Match the native file draw gate (state != 0), also during title handoff. */
    if(RETAIL_SAVE->gameMode==2 ||
       (RETAIL_SAVE->gameMode==1 && !Retail_Gameplay() && fileState!=0))
        return (Frontend){OWNER_FILESELECT,fileState,0};
    /* COmoteUraSelector accepts A/Start before SaveContext enters file mode.
     * Require its live allocation, loaded resources and interaction enable. */
    volatile const u8* mode=Retail_PointerAt(RETAIL_MODE_SELECTOR);
    if(RETAIL_SAVE->gameMode==1 && Retail_Pointer((const void*)mode) &&
       !Retail_Gameplay() && mode[9] && mode[10] && mode[4]>0 && mode[4]<=9)
        return (Frontend){OWNER_MODESELECT,mode[4],0};
    if(movieInstalled() && Retail_Pointer(movie)) {
        u32 state=*(volatile u32*)((u8*)movie+0x104);
        if(state<=4)return (Frontend){state<=1?OWNER_VISIONS_SELECTOR:OWNER_VISIONS_MOVIE,state,state<=1};
    } else movie=0;
    if(RETAIL_SAVE->gameMode==4)return (Frontend){OWNER_BOSS,4,1};
    if(Retail_OcarinaActive())return (Frontend){OWNER_OCARINA,Retail_OcarinaState(),0};
    if(!Retail_Gameplay()){pauseLatched=0;closing=0;return f;}
    u32 pages=RETAIL_WORD(RETAIL_ITEMS)|RETAIL_WORD(RETAIL_GEAR)|RETAIL_WORD(RETAIL_MAP)|RETAIL_WORD(RETAIL_SYSTEM);
    if(pages && RETAIL_WORD(RETAIL_PAUSE)!=2)pauseLatched=1;
    if(!pages && RETAIL_WORD(RETAIL_PAUSE)==2){pauseLatched=0;closing=0;}
    if(pauseLatched)return (Frontend){OWNER_PAUSE,RETAIL_WORD(RETAIL_PAUSE),!closing};
    return (Frontend){OWNER_GAME,RETAIL_WORD(RETAIL_PAUSE),0};
}
