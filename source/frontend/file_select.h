#pragma once
#include "owner.h"

typedef enum {
    FILE_SELECT_PASS_IDLE = 0,
    FILE_SELECT_PASS_TOP = 1,
    FILE_SELECT_PASS_LOWER = 2,
} FileSelectPass;

int FileSelect_Active(void);
FileSelectPass FileSelect_BeginPass(void);
int FileSelect_SuppressTopBackdrop(void);
int FileSelect_SubmitBottomAndMaybeReplay(void* renderer,u32 command);
void FileSelect_ResetIfInactive(void);

FileSelectPass FileSelect_CurrentPass(void);
