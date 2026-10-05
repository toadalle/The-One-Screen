#include "ocarina.h"
#include "../render/scene.h"
#include "../generated/layout.h"
#include "../generated/glyphs.h"
static Scene notes,labels,cursor,chrome,nativeLabels;
static int playState(u32 s){return s==12||s==16;}
static int slideState(u32 s){return s==7||s==9||s==10||s==11||s==13||s==14;}
static void* renderer(void){return Retail_PointerAt(RETAIL_OCARINA+8);}
/* Ocarina's materialized stream is renderer +0x10. Other HUD streams use the
 * recovered mapped-buffer accessor. This distinction is part of its ABI. */
static float* positions(void* r,u32 q) {
    float* p=*(float**)((u8*)r+0x10);return Retail_Pointer(p)?p+q*12:0;
}
static Transform controlTransform(u32 q,void* r,Transform t) {
    /* Pressed rims and sparkles are separate from the normal button group.
     * Use authored centers for the translation so pressing a glyph cannot
     * move the other button's anchor. Both families follow the same delta. */
    int x=(q>=73&&q<=76)||(q>=97&&q<=98)||q==105;
    int y=(q>=77&&q<=80)||(q>=99&&q<=100)||q==106;
    if(x||y) {
        Rect from,to;
        if(Scene_Bounds(Retail_Positions(r,x?76:80),&from)&&
           Scene_Bounds(Retail_Positions(r,x?80:76),&to)) {
            t.x+=(to.x+to.width*.5f-from.x-from.width*.5f)*t.scale;
            t.y+=(to.y+to.height*.5f-from.y-from.height*.5f)*t.scale;
        }
    }
    return t;
}
static int copy(u32 q,void* r,Transform t,int controls) {
    float* p=positions(r,q),*uv=Retail_UVs(r,q),*c=Retail_Colors(r,q);Rect b;
    if(!Scene_Bounds(p,&b)||!Retail_Pointer(uv)||!Retail_Pointer(c))return 0;
    if(controls)t=controlTransform(q,r,t);
    for(u32 v=0;v<4;v++){
        notes.positions[q*12+v*3]=t.x+p[v*3]*t.scale;
        notes.positions[q*12+v*3+1]=t.y+p[v*3+1]*t.scale;
        notes.positions[q*12+v*3+2]=p[v*3+2];
    }
    for(u32 i=0;i<8;i++)notes.uvs[q*8+i]=uv[i];
    for(u32 i=0;i<16;i++)notes.colors[q*16+i]=c[i];
    return 1;
}
int Ocarina_SongTouch(u16* x,u16* y) {
    void* r=renderer();if(!Retail_Pointer(r))return 0;
    Retail_Materialize(r);Rect b;
    if(!Scene_Bounds(positions(r,61),&b)||b.x<0||b.x+b.width>320||b.y<0||b.y+b.height>240)return 0;
    *x=(u16)(b.x+b.width*.5f);*y=(u16)(b.y+b.height*.5f);return 1;
}
u32 Ocarina_TargetGlyph(u32 s) {
    switch(s){case 150:return 170;case 151:return 171;case 154:return 174;default:return s;}
}
static void label(u32 q,Glyph g,Rect b,Transform t) {
    Scene_Rect(&labels,q,Layout_Rect(b,t));Scene_UV(&labels,q,256,256,tosGlyphs[g]);
}
static void songTitle(Transform t) {
    void* group=Retail_PointerAt(RETAIL_OCARINA+0x10);
    if(!Retail_Pointer(group))return;
    u32 mode=RETAIL_WORD((u32)group+0x40),count=mode==2?9:(mode==3?1:2);
    void* children[9];float saved[9][4];
    /* Same-frame borrowed text children only. Transform, materialize, draw,
     * then restore their native positions and scales before lower renders. */
    for(u32 i=0;i<count;i++) {
        void* n=*(void**)((u8*)group+0x10+i*4);children[i]=n;
        if(!Retail_Pointer(n))return;
    }
    for(u32 i=0;i<count;i++) {
        float* p=(float*)((u8*)children[i]+0x3C);
        saved[i][0]=p[0];saved[i][1]=p[1];saved[i][2]=p[3];saved[i][3]=p[4];
        p[0]=t.x+p[0]*t.scale;p[1]=t.y+p[1]*t.scale;p[3]*=t.scale;p[4]*=t.scale;
    }
    RETAIL_FN(void(*)(void*),0x002F7684u)(group);
    for(u32 i=0;i<count;i++) {
        void** vt=*(void***)children[i];
        if(Retail_Pointer(vt)&&Retail_Pointer(vt[3]))((void(*)(void*))vt[3])(children[i]);
    }
    for(u32 i=0;i<count;i++) {
        float* p=(float*)((u8*)children[i]+0x3C);
        p[0]=saved[i][0];p[1]=saved[i][1];p[3]=saved[i][2];p[4]=saved[i][3];
    }
    RETAIL_FN(void(*)(void*),0x002F7684u)(group);
}
void Ocarina_Draw(void) {
    u32 state=Retail_OcarinaState();if(!playState(state)&&state!=4&&!slideState(state))return;
    void* r=renderer();if(!Retail_Pointer(r))return;
    if(!Scene_Ensure(&notes,108,5)||!Scene_Ensure(&labels,12,1)||!Scene_Ensure(&chrome,1,2))return;
    Retail_Materialize(r);Scene_Clear(&notes);Scene_Clear(&labels);
    Transform t=Layout_Resolve(playState(state)?TOS_OCARINA_PLAY:TOS_OCARINA_SONGS,400,240);
    for(u32 q=0;q<108;q++) {
        int use=playState(state)?((q>=58&&q<=84)||q>=91):
            (q<=50||(q>=58&&q<=61)||q>=85||(slideState(state)&&q>=62&&q<=84));
        /* q34 is the complete native red Quit card. The native lower page
         * retains its own Quit; the main song-sheet projection does not. */
        if(!use||q==67||q==72||q==76||q==80||q==84)continue;
        Rect b;if(!Scene_Bounds(positions(r,q),&b))continue;
        if(b.width>=300&&b.height>=220)continue;
        /* Decoded USA Rev1 Ocarina tables: native Quit is q34 (red face),
         * q32/33 (backing), q48/49 (alternate backing). Omitting only q34
         * previously exposed a black empty card on the projected song sheet.
         * The native lower page retains all five quads and working A Quit. */
        if(!playState(state) &&
           (q==32||q==33||q==34||q==48||q==49))continue;
        copy(q,r,t,playState(state)||slideState(state));
    }
    /* Native X group moves to the old Y center and vice versa. Input
     * translation only changes A/B. Labels use the actual glyph centers. */
    const u32 qs[]={67,72,76,80,84};
    const Glyph gs[]={GLYPH_LT,GLYPH_RT,GLYPH_X,GLYPH_Y,GLYPH_B};
    for(u32 i=0;i<5 && (playState(state)||slideState(state));i++) {
        Rect b;if(!Scene_Bounds(positions(r,qs[i]),&b))continue;
        float cx=b.x+b.width*.5f,cy=b.y+b.height*.5f;
        float h=b.height*1.15f,w=h*(i<2?1.25f:.8f);
        label(i,gs[i],(Rect){cx-w*.5f,cy-h*.5f,w,h},controlTransform(qs[i],r,t));
    }
    /* Active play owns compact Quit and the song-sheet shortcut label. */
    Scene_Clear(&chrome);
    if(playState(state)) {
        Rect quit={t.x+8,t.y+68,22,22};
        Scene_Rect(&chrome,0,quit);
        Scene_UV(&chrome,0,512,256,(Rect){384,184,38,38});
        label(7,GLYPH_A,(Rect){quit.x+8,quit.y-6,6,7},(Transform){0,0,1});
        label(8,GLYPH_QUIT,(Rect){quit.x+1,quit.y+6,20,10},(Transform){0,0,1});
        /* q61 is the song-sheet icon and the native RB touch target. Anchor
         * lettering above its materialized bounds, leaving the artwork clear. */
        Rect song;
        if(Scene_Bounds(positions(r,61),&song))
            label(9,GLYPH_RB,(Rect){song.x+song.width*.5f-12,song.y-24,24,18},t);
    }
    Scene_Upload(&notes);Scene_Upload(&labels);Scene_Upload(&chrome);
    Scene_Draw(&notes);if(playState(state))Scene_Draw(&chrome);Scene_Draw(&labels);
    if(state==4)songTitle(t);
    if(state==4||slideState(state)) {
        void* object=Retail_PointerAt(RETAIL_OCARINA+0x0C);
        if(!Retail_Pointer(object)||RETAIL_WORD((u32)object+0x0C)<8)return;
        void* cr=*(void**)((u8*)object+8);
        if(!Retail_Pointer(cr)||!Scene_Ensure(&cursor,8,13))return;
        Retail_Materialize(cr);Scene_Clear(&cursor);
        for(u32 q=0;q<8;q++) {
            float* p=positions(cr,q),*uv=Retail_UVs(cr,q),*c=Retail_Colors(cr,q);Rect b;
            if(!Scene_Bounds(p,&b)||!Retail_Pointer(uv)||!Retail_Pointer(c))continue;
            for(u32 v=0;v<4;v++) {
                cursor.positions[q*12+v*3]=t.x+p[v*3]*t.scale;
                cursor.positions[q*12+v*3+1]=t.y+p[v*3+1]*t.scale;
                cursor.positions[q*12+v*3+2]=p[v*3+2];
            }
            for(u32 i=0;i<8;i++)cursor.uvs[q*8+i]=uv[i];
            for(u32 i=0;i<16;i++)cursor.colors[q*16+i]=c[i];
        }
        Scene_Upload(&cursor);Scene_Draw(&cursor);
    }
}

/* Native SECONDARY-screen draw seam. The compact main overlay is copied from
 * this renderer earlier in the frame. Temporarily exchange the positions of
 * the ORIGINAL X and Y groups, including pressed rims/sparkles, then restore
 * the CPU vertex stream AND native GPU buffer immediately after the draw.
 * Never touch UVs, input, texture identity or the song-sheet note producer. */
void Ocarina_DrawNative(void) {
    const u32 state=Retail_OcarinaState();
    if(!playState(state) && !slideState(state)) {
        RETAIL_FN(void(*)(void),0x00426748u)();return;
    }
    void* r=renderer();
    void* board=Retail_PointerAt(RETAIL_OCARINA);
    if(!Retail_Pointer(r)||!Retail_Pointer(board)) {
        RETAIL_FN(void(*)(void),0x00426748u)();return;
    }
    float* stream=*(float**)((u8*)r+0x10);
    Rect xb,yb;
    if(!Retail_Pointer(stream)||!Scene_Bounds(stream+76*12,&xb)||
       !Scene_Bounds(stream+80*12,&yb)||xb.width>100||yb.width>100||
       xb.x<0||yb.x<0||xb.x>400||yb.x>400||
       !Scene_Ensure(&nativeLabels,5,1)) {
        RETAIL_FN(void(*)(void),0x00426748u)();return;
    }
    /* Native full-size glyph atlas cells are transparent in this release.
     * Leave the native play shells and effects; move full X/Y families as
     * in 1.0.6 and draw one independent project lettering layer afterwards.
     * The native shared song-note atlas is not modified. */
    const float dx=yb.x+yb.width*.5f-xb.x-xb.width*.5f;
    const float dy=yb.y+yb.height*.5f-xb.y-xb.height*.5f;
    static const u8 glyphs[]={GLYPH_LT,GLYPH_RT,GLYPH_X,GLYPH_Y,GLYPH_B};
    static const u8 glyphQuad[]={67,72,76,80,84};
    Scene_Clear(&nativeLabels);
    for(u32 i=0;i<5;i++) {
        Rect b;
        if(!Scene_Bounds(stream+glyphQuad[i]*12,&b)) {
            RETAIL_FN(void(*)(void),0x00426748u)();return;
        }
        float cx=b.x+b.width*.5f+(i==2?dx:(i==3?-dx:0));
        float cy=b.y+b.height*.5f+(i==2?dy:(i==3?-dy:0));
        const float w=i<2?21.f:18.f,h=19.f;
        Scene_Rect(&nativeLabels,i,(Rect){cx-w*.5f,cy-h*.5f,w,h});
        Scene_UV(&nativeLabels,i,256,256,tosGlyphs[glyphs[i]]);
    }
    static const u8 xq[]={73,74,75,76,97,98,105};
    static const u8 yq[]={77,78,79,80,99,100,106};
    float backup[14][8];
    for(u32 i=0;i<14;i++) {
        u32 q=i<7?xq[i]:yq[i-7];float* p=stream+q*12;
        for(u32 v=0;v<4;v++) {
            backup[i][v*2]=p[v*3];backup[i][v*2+1]=p[v*3+1];
            p[v*3]+=(i<7?dx:-dx);p[v*3+1]+=(i<7?dy:-dy);
        }
    }
    RETAIL_FN(void(*)(void*,u32,const void*),0x0036759Cu)(board,108u*48u,stream);
    RETAIL_FN(void(*)(void),0x00426748u)();
    for(u32 i=0;i<14;i++) {
        u32 q=i<7?xq[i]:yq[i-7];float* p=stream+q*12;
        for(u32 v=0;v<4;v++) {
            p[v*3]=backup[i][v*2];p[v*3+1]=backup[i][v*2+1];
        }
    }
    /* Retain the temporary GPU geometry until the lower draw queue flushes.
     * Only CPU geometry is restored; native upload refreshes next frame. */
    Scene_Upload(&nativeLabels);Scene_Draw(&nativeLabels);
}
