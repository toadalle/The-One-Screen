#pragma once
#include "../render/scene.h"
extern float tosHeartPositions[240],tosHeartUVs[160];
extern const u16 tosHeartIndices[118];
void Hud_Submit(void);
void Hud_Draw(void);
void Hud_ActionBegin(void);
void Hud_ActionEnd(void);

