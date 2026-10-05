#include "physical.h"
#include "hid.h"
#include "irrst.h"
#include "../retail/abi.h"

static volatile const struct hid_pad_t* nativePad;
static PadCursor gameCursor;
static u32 lastExtra;
extern s32 svcOutputDebugString(const char*,s32);
void Physical_Init(void) { (void)Irrst_Init(); }
void Physical_BindHid(const void* pointer) {
    /* Captured after the native reader follows HidContext::hid_pad. */
    if(Retail_Pointer(pointer) && nativePad!=pointer) {
        nativePad=pointer;
        char message[]="TOS_HID native_reader=0x00000000\n";
        const char hex[]="0123456789abcdef";
        for(u32 i=0;i<8;i++)message[24+i]=hex[((uintptr_t)pointer>>(28-i*4))&15];
        svcOutputDebugString(message,sizeof(message)-1);
    }
}
PadBatch Physical_ReadHistory(PadCursor* cursor) {
    volatile const struct hid_pad_t* hid=nativePad;
    PadBatch empty={{0},0};
    if(!hid)return empty;
    if(cursor->source!=(uintptr_t)hid){cursor->ready=0;cursor->held=0;cursor->source=(uintptr_t)hid;}
    for(u32 attempt=0;attempt<4;attempt++) {
        PadSnapshot s;
        s.tick=hid->timestamp;s.previous=hid->timestamp_last;s.index=hid->index;
        if(s.index>7 || (int64_t)s.tick<0 || (s.index==0 && s.tick==s.previous))continue;
        for(u32 i=0;i<8;i++)s.held[i]=hid->pads[i].curr.val;
        __asm__ volatile("" ::: "memory");
        if(s.index!=hid->index || s.tick!=hid->timestamp || s.previous!=hid->timestamp_last)continue;
        return Pad_Decode(cursor,&s);
    }
    return empty;
}
Physical Physical_Read(void) {
    Physical result={0};u32 previous=gameCursor.held;
    PadBatch batch=Physical_ReadHistory(&gameCursor);
    for(u32 i=0;i<batch.count;i++) {
        u32 held=batch.held[i];
        result.pad.pressed|=held&~previous;
        result.pad.released|=previous&~held;
        previous=held;
    }
    result.pad.held=gameCursor.held;
    Irrst_Scan();
    result.extension.held=Irrst_KeysHeld();
    result.extension.pressed=result.extension.held&~lastExtra;
    result.extension.released=lastExtra&~result.extension.held;
    lastExtra=result.extension.held;
    Irrst_CstickRead(&result.stickX,&result.stickY);
    return result;
}
