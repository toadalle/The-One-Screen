#pragma once
#include <stdint.h>
/* HID timestamps identify ring generations, not individual samples. */
typedef struct { uint64_t tick,previous; uint32_t index,held[8]; } PadSnapshot;
typedef struct { uint64_t tick; uint32_t index,held,overruns; int ready; uintptr_t source; } PadCursor;
typedef struct { uint32_t held[8],count; } PadBatch;
static inline PadBatch Pad_Decode(PadCursor* c,const PadSnapshot* s) {
    PadBatch b={{0},0}; uint32_t n;
    if(!c->ready)n=1;
    else if(c->tick==s->tick)n=(s->index-c->index)&7u;
    else if(c->tick==s->previous)n=8u-c->index+s->index;
    else {n=8;c->overruns++;}
    if(n>8){n=8;c->overruns++;}
    for(uint32_t i=0;i<n;i++)b.held[i]=s->held[(s->index+9u-n+i)&7u];
    b.count=n;c->tick=s->tick;c->index=s->index;c->ready=1;
    if(n)c->held=b.held[n-1];
    return b;
}
#define NOTE_QUEUE_CAPACITY 64u
typedef struct { uint32_t values[NOTE_QUEUE_CAPACITY],head,count,latest,output,overflows; } NoteQueue;
static inline void Notes_Clear(NoteQueue* q) {
    q->head=q->count=q->latest=q->output=0;
}
static inline void Notes_Push(NoteQueue* q,uint32_t held) {
    if(held==q->latest)return;
    q->latest=held;
    /* A pathological backlog must recover to physical state, never stick a note. */
    if(q->count==NOTE_QUEUE_CAPACITY){q->overflows++;q->head=q->count=0;}
    q->values[(q->head+q->count)%NOTE_QUEUE_CAPACITY]=held;q->count++;
}
static inline uint32_t Notes_Next(NoteQueue* q) {
    if(q->count){q->output=q->values[q->head];q->head=(q->head+1)%NOTE_QUEUE_CAPACITY;q->count--;}
    return q->output;
}
