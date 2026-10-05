#pragma once
#include "z3D/z3D.h"
#include <stddef.h>
#include <stdint.h>

/* USA Rev 1 only. Source: exact supplied executable and documented recovered
 * contracts. Range guards reject malformed pointers; they do not prove lifetime. */
#define RETAIL_BASE 0x00100000u
#define RETAIL_SAVE ((volatile SaveContext*)0x00587958u)
#define RETAIL_WORD(a) (*(volatile u32*)(a))
#define RETAIL_HALF(a) (*(volatile u16*)(a))
#define RETAIL_BYTE(a) (*(volatile u8*)(a))
#define RETAIL_MODE_SELECTOR 0x0050BB50u
#define RETAIL_HUD 0x0050AF34u
#define RETAIL_ACTION_ROOT 0x004FC648u
#define RETAIL_OCARINA 0x005093E4u
#define RETAIL_PAUSE 0x0050AF68u
#define RETAIL_ITEMS 0x0050672Cu
#define RETAIL_GEAR 0x00504484u
#define RETAIL_MAP 0x00506CE8u
#define RETAIL_SYSTEM 0x0050A530u
#define RETAIL_FILECHOOSE 0x00504FA0u
#define RETAIL_NAMEENTRY 0x005077F0u
#define RETAIL_CANON_TOUCH 0x005043D4u
#define RETAIL_EDGE_TOUCH 0x0050BB38u
#define RETAIL_HEAP 0x0055A1F8u
#define RETAIL_RENDERER 0x005C0A34u
#define RETAIL_BOARD_PROFILE 0x004D30A4u
#define RETAIL_MINIMAP 0x004FDA84u
#define RETAIL_QUEST_BUFFER 0x004FC660u
#define RETAIL_MOVIE_UPPER 0x00471F40u
#define RETAIL_MOVIE_LOWER 0x00477E10u
/* Callback slots checked against source evidence before activation. */
#define RETAIL_MOVIE_UPPER_SLOT 0x005C59F8u
#define RETAIL_MOVIE_LOWER_SLOT 0x005C59FCu
#define RETAIL_FN(type, address) ((type)(address))

static inline int Retail_Pointer(const void* p) {
    uintptr_t a = (uintptr_t)p;
    return a >= RETAIL_BASE && a < 0x20000000u && !(a & 3u);
}
static inline void* Retail_PointerAt(u32 a) { return *(void* volatile*)a; }
static inline u32 Retail_OcarinaState(void) { return RETAIL_WORD(RETAIL_OCARINA+0x14u); }
static inline int Retail_OcarinaActive(void) {
    u32 s=Retail_OcarinaState(); return s>0 && s<17;
}
static inline int Retail_Gameplay(void) {
    const volatile SaveContext* s=RETAIL_SAVE;
    return s->gameMode==0 || (s->gameMode==1 && (s->cutsceneIndex<0xFFF0 ||
      (s->entranceIndex!=0x629 && s->entranceIndex!=0x147 &&
       s->entranceIndex!=0xA0 && s->entranceIndex!=0x8D)));
}
static inline int Retail_Mounted(GlobalContext* p) {
    if(!Retail_Pointer(p)) return 0;
    void* player=*(void**)((u8*)p+0x20AC);
    if(!Retail_Pointer(player)) return 0;
    void* horse=*(void**)((u8*)player+0x12B8);
    return Retail_Pointer(horse) && *(void**)((u8*)horse+0x128)==player;
}
static inline float* Retail_Positions(void* r,u32 q) {
    return RETAIL_FN(float*(*)(void*,u32),0x002FC3FCu)(r,q);
}
static inline float* Retail_UVs(void* r,u32 q) {
    return RETAIL_FN(float*(*)(void*,u32),0x002FC3F0u)(r,q);
}
static inline float* Retail_Colors(void* r,u32 q) {
    return RETAIL_FN(float*(*)(void*,u32),0x002FC3E4u)(r,q);
}
static inline void Retail_Materialize(void* r) {
    RETAIL_FN(void(*)(void*),0x002F9A1Cu)(r);
}
static inline void Retail_Viewport(s32 x,s32 y,s32 w,s32 h) {
    RETAIL_FN(void(*)(s32,s32,s32,s32),0x002FEABCu)(x,y,w,h);
}
static inline void Retail_Submit(void* r,u32 c) {
    RETAIL_FN(void(*)(void*,u32),0x00300240u)(r,c);
}
static inline void* Retail_Register(void* r,void* b,u32 a,u32 c) {
    return RETAIL_FN(void*(*)(void*,void*,u32,u32),0x0034897Cu)(r,b,a,c);
}
_Static_assert(offsetof(SaveContext,equips)==0x80,"equips ABI");
_Static_assert(offsetof(SaveContext,gameMode)==0x14E4,"game mode ABI");
_Static_assert(offsetof(GlobalContext,sceneNum)==0x104,"scene ABI");
