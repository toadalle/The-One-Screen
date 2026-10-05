#pragma once
#include "../frontend/owner.h"
void Presentation_Target(void* renderer,u32 command);
void Presentation_Submit(void* renderer,u32 command);
void Presentation_Observe(void* object,u32 callback);

int Presentation_SuppressBackdrop(u32 site);
