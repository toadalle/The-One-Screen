#pragma once
#include <stdint.h>
typedef struct { uint32_t held,pressed,released; } Digital;
typedef enum { INPUT_GAMEPLAY, INPUT_OCARINA } InputContext;

/* Xbox face geometry differs from the 3DS: physical Y occupies the native X
 * lane and physical X occupies the native Y lane. Keep that semantic swap in
 * gameplay/pause contexts so item use and item assignment agree with the
 * LB/Y/X/B/RB presentation recovered from alpha-098. Ocarina translation is
 * intentionally independent because its note path has its own proven mapping. */
static inline uint32_t Input_SwapBits(uint32_t mask,uint32_t a,uint32_t b) {
    const uint32_t av=mask&a,bv=mask&b;
    return (mask&~(a|b))|(av?b:0u)|(bv?a:0u);
}
static inline uint32_t Input_Translate(uint32_t mask, InputContext context) {
    if(context==INPUT_GAMEPLAY)
        return Input_SwapBits(mask,1u<<10,1u<<11); /* X <-> Y */
    return Input_SwapBits(mask,1u<<0,1u<<1);      /* Ocarina A <-> B */
}
static inline Digital Input_TranslateDigital(Digital d,InputContext c) {
    Digital result={Input_Translate(d.held,c),Input_Translate(d.pressed,c),Input_Translate(d.released,c)};
    return result;
}
/* Ownership persists while held, and blocks a press carried across contexts. */
static inline uint32_t Input_Consume(uint32_t* latch,Digital d) {
    *latch &= d.held;
    uint32_t edge=d.pressed & ~*latch;
    *latch |= edge | d.held;
    return edge;
}
