#pragma once
#include "../retail/abi.h"

// Minimal IRRST reader for the New-3DS ZL/ZR buttons and C-stick. Standard
// L/R remain in OoT3D's original HID path so target/shield and pause tabs
// stay native; the C-stick is used by the mod's right-stick camera.
u8 Irrst_Init(void);
void Irrst_Scan(void);
u32 Irrst_KeysHeld(void);
void Irrst_CstickRead(s16* x, s16* y);
