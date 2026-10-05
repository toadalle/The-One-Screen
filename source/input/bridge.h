#pragma once
#include "../retail/abi.h"
void Bridge_Update(GlobalContext* play);
void Bridge_TouchMaterialized(u16* x,u16* y,u8* active);
u32 Bridge_OcarinaMask(u32 mask,u32 controller);
u32 Bridge_PauseMask(void);
int Bridge_ViewOwned(void);
