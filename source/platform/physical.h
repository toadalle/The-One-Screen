#pragma once
#include "../input/policy.h"
#include "../input/history.h"
typedef struct { Digital pad,extension; int16_t stickX,stickY; } Physical;
void Physical_Init(void);
Physical Physical_Read(void);
void Physical_BindHid(const void* pointer);
PadBatch Physical_ReadHistory(PadCursor* cursor);
