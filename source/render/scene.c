#include "scene.h"
static int finite(float x) { return x==x && x>-4096 && x<4096; }
int Scene_Bounds(const float* p,Rect* b) {
    if(!Retail_Pointer(p)) return 0;
    float x0=p[0],x1=p[0],y0=p[1],y1=p[1];
    for(u32 i=0;i<4;i++) {
        float x=p[i*3],y=p[i*3+1];if(!finite(x)||!finite(y)) return 0;
        if(x<x0)x0=x;if(x>x1)x1=x;if(y<y0)y0=y;if(y>y1)y1=y;
    }
    *b=(Rect){x0,y0,x1-x0,y1-y0};return b->width>0 && b->height>0;
}
void Scene_Rect(Scene* s,u32 q,Rect r) {
    if(q>=s->count)return;
    float* p=&s->positions[q*12];
    for(u32 i=0;i<4;i++) {p[i*3]=r.x+((i&1)?r.width:0);p[i*3+1]=r.y+((i<2)?r.height:0);p[i*3+2]=0;}
}
void Scene_Clear(Scene* s) {
    for(u32 q=0;q<s->count;q++) Scene_Rect(s,q,(Rect){800,800,0,0});
}
void Scene_UV(Scene* s,u32 q,float aw,float ah,Rect r) {
    if(q>=s->count)return;
    float* uv=&s->uvs[q*8];
    for(u32 i=0;i<4;i++) {uv[i*2]=(r.x+((i&1)?r.width:0))/aw;uv[i*2+1]=1-(r.y+((i<2)?r.height:0))/ah;}
}
static int Scene_EnsureImpl(Scene* s,u32 count,u32 slot,int colors) {
    if(count==0||count>SCENE_QUADS)return 0;
    void* renderer=Retail_PointerAt(RETAIL_RENDERER);
    void* texture=RETAIL_FN(void*(*)(u32),0x002E11D0u)(slot);
    if(!Retail_Pointer(renderer)||!Retail_Pointer(texture))return 0;
    /* Rebuilding scene allocation after owner changes requires a proven native
     * destruction contract. Refuse stale owners instead of dereferencing them. */
    if(s->ready) return s->renderer==renderer && s->texture==texture;
    s->count=count;s->slot=slot;
    for(u32 i=0;i<70;i++) s->profile[i]=RETAIL_WORD(RETAIL_BOARD_PROFILE+i*4);
    if(colors)for(u32 i=0;i<count*16;i++)s->colors[i]=1;
    u32 n=0;
    for(u32 q=0;q<count;q++) {
        if(q){s->indices[n++]=(u16)(q*4-1);s->indices[n++]=(u16)(q*4);}
        for(u32 v=0;v<4;v++)s->indices[n++]=(u16)(q*4+v);
    }
    Scene_Clear(s);
    s->profile[0]=(u32)s->positions;s->profile[1]=(u32)s->uvs;s->profile[2]=colors?(u32)s->colors:0;
    s->profile[3]=count*4;s->profile[4]=(u32)s->indices;s->profile[5]=n;s->profile[6]=2;s->profile[7]=colors?4:0x0C;
    void* heap=Retail_PointerAt(RETAIL_HEAP);if(!Retail_Pointer(heap))return 0;
    void** vt=*(void***)heap;if(!Retail_Pointer(vt)||!Retail_Pointer(vt[2]))return 0;
    void* storage=((void*(*)(void*,u32))vt[2])(heap,440);
    if(!Retail_Pointer(storage))return 0;
    void* board=RETAIL_FN(void*(*)(void*,const void*),0x00348F34u)(storage,s->profile);
    if(!Retail_Pointer(board))return 0;
    RETAIL_FN(void(*)(void*,u32,void*,u32,u32,u32,u32),0x00348A64u)(board,0,texture,0x2601,0x2601,0x812F,0x812F);
    void* node=Retail_Register(renderer,board,0,0);if(!Retail_Pointer(node))return 0;
    RETAIL_WORD((u32)node+0x178)|=3;
    s->board=board;s->node=node;s->renderer=renderer;s->texture=texture;s->ready=1;
    return 1;
}
int Scene_Copy(Scene* s,u32 q,void* renderer,u32 source,Transform t,int color) {
    if(q>=s->count||!Retail_Pointer(renderer))return 0;
    float* p=Retail_Positions(renderer,source),*uv=Retail_UVs(renderer,source);
    Rect b;if(!Scene_Bounds(p,&b)||!Retail_Pointer(uv))return 0;
    for(u32 i=0;i<4;i++) {
        s->positions[q*12+i*3]=t.x+p[i*3]*t.scale;
        s->positions[q*12+i*3+1]=t.y+p[i*3+1]*t.scale;
        s->positions[q*12+i*3+2]=p[i*3+2];
    }
    for(u32 i=0;i<8;i++)s->uvs[q*8+i]=uv[i];
    if(color) {
        float* c=Retail_Colors(renderer,source);if(!Retail_Pointer(c))return 0;
        for(u32 i=0;i<16;i++)s->colors[q*16+i]=c[i];
    }
    return 1;
}
int Scene_Ensure(Scene* s,u32 count,u32 slot) {return Scene_EnsureImpl(s,count,slot,1);}
int Scene_EnsureColorless(Scene* s,u32 count,u32 slot) {return Scene_EnsureImpl(s,count,slot,0);}
void Scene_Upload(Scene* s) {
    if(!s->ready)return;
    RETAIL_FN(void(*)(void*,u32,const void*),0x0036759Cu)(s->board,s->count*48,s->positions);
    RETAIL_FN(void(*)(void*,u32,const void*),0x00317D1Cu)(s->board,s->count*32,s->uvs);
    if(s->profile[2])RETAIL_FN(void(*)(void*,u32,const void*),0x002F9934u)(s->board,s->count*64,s->colors);
}
int Scene_Draw(Scene* s) {
    if(!s->ready || s->renderer!=Retail_PointerAt(RETAIL_RENDERER))return 0;
    void** vt=*(void***)s->node;
    if(!Retail_Pointer(vt)||!Retail_Pointer(vt[3]))return 0;
    ((void(*)(void*))vt[3])(s->node);return 1;
}
