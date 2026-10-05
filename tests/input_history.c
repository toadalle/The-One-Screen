#include <assert.h>
#include <stdio.h>
#include "../source/input/history.h"
#include "../source/input/policy.h"
int main(void) {
    PadCursor c={0};PadSnapshot s={100,50,0,{0}};
    PadBatch b=Pad_Decode(&c,&s);assert(b.count==1);
    /* B down/up entirely between game frames must both reach the consumer. */
    s.index=4;s.held[1]=2;s.held[2]=0;s.held[3]=0x400;s.held[4]=0;
    b=Pad_Decode(&c,&s);assert(b.count==4);
    NoteQueue q={0};
    for(unsigned i=0;i<b.count;i++)Notes_Push(&q,Input_Translate(b.held[i],INPUT_OCARINA));
    assert(Notes_Next(&q)==1);assert(Notes_Next(&q)==0);
    assert(Notes_Next(&q)==0x400);assert(Notes_Next(&q)==0);
    assert(Pad_Decode(&c,&s).count==0); /* No duplicated sample/press. */
    s.index=7;s.held[5]=2;s.held[6]=2;s.held[7]=2;
    b=Pad_Decode(&c,&s);assert(b.count==3);
    for(unsigned i=0;i<b.count;i++)Notes_Push(&q,b.held[i]);
    assert(q.count==1);assert(Notes_Next(&q)==2);assert(Notes_Next(&q)==2);
    s.previous=100;s.tick=200;s.index=1;s.held[0]=0;s.held[1]=2;
    b=Pad_Decode(&c,&s);assert(b.count==2 && b.held[0]==0 && b.held[1]==2);
    Notes_Push(&q,0);Notes_Push(&q,2);
    assert(Notes_Next(&q)==0);assert(Notes_Next(&q)==2);
    /* A full ring is fresh even when the index returns to the same value. */
    s.previous=200;s.tick=300;
    assert(Pad_Decode(&c,&s).count==8);
    s.previous=500;s.tick=600;
    assert(Pad_Decode(&c,&s).count==8 && c.overruns==1);
    Notes_Clear(&q);assert(Notes_Next(&q)==0 && q.count==0);
    for(unsigned i=0;i<100;i++)Notes_Push(&q,(i&1)?0:1);
    assert(q.overflows==1 && q.count<=NOTE_QUEUE_CAPACITY);
    while(q.count)Notes_Next(&q);
    assert(q.output==0); /* Overflow recovery cannot leave a stuck note. */
    puts("PASS: sub-frame taps, order, repeat release, hold, ring wrap, context reset, overflow");
}
