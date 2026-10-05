#include "camera.h"
#include "../frontend/owner.h"
#include "../input/bridge.h"
#include "../platform/irrst.h"
static int active;
static s16 yaw,pitch;
static float distance;
static Vec3f eye;
static float sine(u16 angle) {
    u32 quadrant=angle>>14;u16 local=angle&0x3FFF;
    if(quadrant&1)local=0x4000-local;
    float x=local*.00009587379924285257f,x2=x*x;
    float v=x*(1-x2*(.1666666716f-x2*(.0083333338f-x2*.0001984127f)));
    return quadrant>=2?-v:v;
}
static int nativeOwns(Camera* c,GlobalContext* p) {
    if(Frontend_Read().owner!=OWNER_GAME || Bridge_ViewOwned() || p->activeCamera!=0 ||
       c->status!=7 || !Retail_Pointer(c->player))return 1;
    if(c->player->stateFlags1&0x28010 || c->player->stateFlags2&0x08042000)return 1;
    switch(c->mode){case 6:case 7:case 8:case 9:case 10:case 11:case 20:return 1;default:break;}
    switch(c->setting){case 0x14:case 0x15:case 0x19:case 0x1A:case 0x1B:case 0x1D:case 0x23:case 0x40:case 0x46:return 1;default:break;}
    void* r=Retail_PointerAt(RETAIL_HUD+4);
    if(Retail_Pointer(r)) {
        float* uv=Retail_UVs(r,28);
        if(Retail_Pointer(uv)) {
            float lo=uv[1],hi=uv[1];for(u32 i=1;i<4;i++){if(uv[i*2+1]<lo)lo=uv[i*2+1];if(uv[i*2+1]>hi)hi=uv[i*2+1];}
            float mid=(hi+lo)*.5f;if(mid>.60f&&mid<.82f)return 1;
        }
    }
    return 0;
}
void Camera_UpdateOrbit(GlobalContext* p) {
    if(!Retail_Pointer(p)){active=0;return;}
    Camera* c=&p->mainCamera;
    if(nativeOwns(c,p)){active=0;return;}
    Irrst_Scan();s16 x=0,y=0;Irrst_CstickRead(&x,&y);
    int moving=(s32)x*x+(s32)y*y>18*18;
    if(!active) {
        if(!moving)return;
        active=1;yaw=c->camDir.y;pitch=c->camDir.x;distance=c->dist;eye=c->eye;
    }
    if(moving) {
        yaw=(s16)((s32)yaw-(RETAIL_SAVE->masterQuestFlag?-(s32)x:(s32)x)*6);
        s32 next=pitch+(s32)y*5;pitch=(s16)(next>0x3000?0x3000:(next<-0x3000?-0x3000:next));
    }
    if(c->dist>=40&&c->dist<=800)distance+=(c->dist-distance)*.12f;
    else if(distance<40||distance>800)distance=180;
    float sp=sine((u16)pitch),cp=sine((u16)(pitch+0x4000)),sy=sine((u16)yaw),cy=sine((u16)(yaw+0x4000));
    Vec3f desired={c->at.x-distance*cp*sy,c->at.y-distance*sp,c->at.z-distance*cp*cy};
    CamColChk collision={0};collision.pos=desired;collision.bgId=-1;
    Camera_BGCheckInfo(c,&c->at,&collision);desired=collision.pos;
    Vec3f eo={p->view.eye.x-c->eye.x,p->view.eye.y-c->eye.y,p->view.eye.z-c->eye.z};
    Vec3f ao={p->view.at.x-c->at.x,p->view.at.y-c->at.y,p->view.at.z-c->at.z};
    eye.x+=(desired.x-eye.x)*.68f;eye.y+=(desired.y-eye.y)*.68f;eye.z+=(desired.z-eye.z)*.68f;
    c->eye=eye;c->eyeNext=eye;c->inputDir=(Vec3s){pitch,yaw,0};c->camDir=c->inputDir;
    p->view.eye=(Vec3f){eye.x+eo.x,eye.y+eo.y,eye.z+eo.z};
    p->view.at=(Vec3f){c->at.x+ao.x,c->at.y+ao.y,c->at.z+ao.z};p->view.up=(Vec3f){0,1,0};
}
