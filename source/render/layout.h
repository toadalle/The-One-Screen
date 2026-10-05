#pragma once
typedef struct { float x,y,width,height; } Rect;
typedef enum { ANCHOR_TOP_LEFT, ANCHOR_TOP_RIGHT, ANCHOR_BOTTOM_RIGHT, ANCHOR_CENTER } Anchor;
typedef struct { Anchor anchor; float x,y,scale,width,height; } Layout;
typedef struct { float x,y,scale; } Transform;
static inline Transform Layout_Resolve(Layout l,float canvasW,float canvasH) {
    Transform t={l.x,l.y,l.scale};
    if(l.anchor==ANCHOR_TOP_RIGHT || l.anchor==ANCHOR_BOTTOM_RIGHT)
        t.x=canvasW-l.x-l.width*l.scale;
    if(l.anchor==ANCHOR_BOTTOM_RIGHT) t.y=canvasH-l.y-l.height*l.scale;
    if(l.anchor==ANCHOR_CENTER) {
        t.x=(canvasW-l.width*l.scale)*0.5f+l.x;
        t.y=(canvasH-l.height*l.scale)*0.5f+l.y;
    }
    return t;
}
static inline Rect Layout_Rect(Rect r,Transform t) {
    Rect o={t.x+r.x*t.scale,t.y+r.y*t.scale,r.width*t.scale,r.height*t.scale};return o;
}
