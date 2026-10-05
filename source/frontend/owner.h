#pragma once
#include "../retail/abi.h"
typedef enum { OWNER_GAME, OWNER_PAUSE, OWNER_OCARINA, OWNER_VISIONS_SELECTOR,
    OWNER_VISIONS_MOVIE, OWNER_BOSS, OWNER_FILESELECT, OWNER_NAMEENTRY, OWNER_OTHER,
    OWNER_MODESELECT } Owner;
typedef struct { Owner owner; u32 state; int swap; } Frontend;
Frontend Frontend_Read(void);
void Frontend_ObserveMovie(u32 callback,void* object);
void Frontend_RequestClose(void);
