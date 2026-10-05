#pragma once
#include "../retail/abi.h"
#include "layout.h"
#define SCENE_QUADS 128u
typedef struct {
    void* board; void* node; void* renderer; void* texture;
    u32 count,slot,ready; u32 profile[70];
    float positions[SCENE_QUADS*12];
    float uvs[SCENE_QUADS*8];
    float colors[SCENE_QUADS*16];
    u16 indices[SCENE_QUADS*6];
} Scene;
int Scene_Ensure(Scene* s,u32 count,u32 textureSlot);
int Scene_EnsureColorless(Scene* s,u32 count,u32 textureSlot);
void Scene_Clear(Scene* s);
void Scene_Rect(Scene* s,u32 q,Rect r);
void Scene_UV(Scene* s,u32 q,float aw,float ah,Rect r);
int Scene_Copy(Scene* s,u32 q,void* renderer,u32 source,Transform transform,int colors);
void Scene_Upload(Scene* s);
int Scene_Draw(Scene* s);
int Scene_Bounds(const float* p,Rect* bounds);
