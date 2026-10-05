#include "minimap.h"
#include "../render/scene.h"
#include "../frontend/owner.h"
#include "../generated/layout.h"
typedef struct { volatile float* address;u32 source,last; } AuthoredValue;
static AuthoredValue values[514];
static void* owner;
static float dx,dy;
static int projected;
static u32 bits(float f){union{float f;u32 u;}v={.f=f};return v.u;}
static float fromBits(u32 u){union{float f;u32 u;}v={.u=u};return v.f;}
static float original(AuthoredValue* v,volatile float* address) {
    u32 now=*(volatile u32*)address;
    if(v->address!=address||v->last!=now){v->address=address;v->source=now;}
    return fromBits(v->source);
}
static void assign(AuthoredValue* v,volatile float* p,float delta) {
    float native=original(v,p);if(native!=native||native<-4096||native>4096)return;
    v->last=bits(native+delta);*(volatile u32*)p=v->last;
}
void Minimap_Project(void) {
    void* current=Retail_PointerAt(RETAIL_MINIMAP);
    if(current!=owner){for(u32 i=0;i<514;i++)values[i].address=0;owner=current;}
    projected=0;
    if(!Retail_Pointer(current))return;
    int enabled=Frontend_Read().owner==OWNER_GAME;
    if(!enabled) {
        /* Restore only within the same native owner and only our own writes. */
        for(u32 i=0;i<514;i++)if(values[i].address && *(volatile u32*)values[i].address==values[i].last) {
            *(volatile u32*)values[i].address=values[i].source;values[i].address=0;
        }
        return;
    }
    float* bounds=*(float**)((u8*)current+0x0C),*offset=*(float**)((u8*)current+0x1C);Rect b;
    if(!Retail_Pointer(offset)||!Scene_Bounds(bounds,&b)||b.width>256||b.height>256)return;
    float ox=original(&values[0],offset),oy=original(&values[1],offset+1);
    dx=(400-TOS_MINIMAP.x)-(ox+b.x+b.width);
    if(RETAIL_SAVE->masterQuestFlag)dx=-dx;
    GlobalContext* play=Retail_PointerAt(RETAIL_HUD);
    dy=Retail_Mounted(play)?156-(oy+b.y+b.height*.5f):0;
    if(dx<-400||dx>400||dy<-400||dy>400)return;
    assign(&values[0],offset,dx);assign(&values[1],offset+1,dy);
    for(u32 g=0;g<4;g++) {
        void* stream=Retail_PointerAt(RETAIL_MINIMAP+8+g*4);if(!Retail_Pointer(stream))continue;
        u32 count=*(u32*)((u8*)stream+0x0C);void* buffer=*(void**)((u8*)stream+8);
        if(count>64||!Retail_Pointer(buffer))continue;
        float* p=*(float**)((u8*)buffer+0x1C);if(!Retail_Pointer(p))continue;
        for(u32 i=0;i<count;i++) {
            u32 n=2+(g*64+i)*2;
            if(original(&values[n],p+i*2)<400){assign(&values[n],p+i*2,dx);assign(&values[n+1],p+i*2+1,dy);}
        }
    }
    projected=1;
}
void Minimap_Markers(void) {
    Minimap_Project();
    if(!projected)return;
    void* r=Retail_PointerAt(RETAIL_QUEST_BUFFER);
    if(!Retail_Pointer(r)||RETAIL_WORD((u32)r)!=8)return;
    float* p=*(float**)((u8*)r+0x10);if(!Retail_Pointer(p))return;
    /* Exact producer: 0x42AEC0 writes player quad 2 and 0x42B108 writes
     * entrance quad 3 in this stream. Other six quads are not map markers.
     * Called immediately after native materialization: never accumulate. */
    for(u32 q=2;q<=3;q++)for(u32 v=0;v<4;v++) {
        p[q*12+v*3]+=dx;p[q*12+v*3+1]+=dy;
    }
}
void Minimap_MaterializeMarkers(void* r) {
    Retail_Materialize(r);
    if(r==Retail_PointerAt(RETAIL_QUEST_BUFFER))Minimap_Markers();
}
