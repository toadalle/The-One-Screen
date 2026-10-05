#include "hud.h"
#include "../frontend/owner.h"
#include "../frontend/ocarina.h"
#include "../retail/z3D/z3Ditem.h"
#include "../generated/layout.h"
#include "../generated/glyphs.h"

float tosHeartPositions[240] __attribute__((aligned(16)));
float tosHeartUVs[160] __attribute__((aligned(16)));
#define JOIN(n) (4*(n)-1),4*(n),4*(n),(4*(n)+1),(4*(n)+2),(4*(n)+3)
const u16 tosHeartIndices[118]={0,1,2,3,JOIN(1),JOIN(2),JOIN(3),JOIN(4),JOIN(5),JOIN(6),JOIN(7),JOIN(8),JOIN(9),JOIN(10),JOIN(11),JOIN(12),JOIN(13),JOIN(14),JOIN(15),JOIN(16),JOIN(17),JOIN(18),JOIN(19)};
#undef JOIN
static Scene native,chrome,icons,labels;
static u32 drawFrame,frame;
static int visible,scenesReady;
static float actionOriginal[24],actionUV[8];
static float* actionPositions;
static int actionValid;
static Rect actionBounds;
static void hideHeart(u32 q) {
    for(u32 v=0;v<4;v++){tosHeartPositions[q*12+v*3]=800;tosHeartPositions[q*12+v*3+1]=800;tosHeartPositions[q*12+v*3+2]=0;}
}
static void glyph(u32 q,Glyph g,float x,float y,float w,float h) {
    Scene_Rect(&labels,q,(Rect){x,y,w,h});
    Scene_UV(&labels,q,256,256,tosGlyphs[g]);
}
static void number(u32 q,u32 value,u32 slots,float x,float y,float scale) {
    u32 digits[5],count=0;
    do{digits[count++]=value%10;value/=10;}while(value && count<slots);
    for(u32 i=0;i<count;i++){
        u32 d=digits[count-i-1];
        Scene_Rect(&labels,q+i,(Rect){x+i*9.5f*scale,y,9*scale,10*scale});
        Scene_UV(&labels,q+i,256,256,(Rect){118+(d%5)*12,d<5?184:198,12,14});
    }
}
static int ammo(u8 item) {
    int slot=-1;
    switch(item){
        case ITEM_STICK:slot=SLOT_STICK;break;case ITEM_NUT:slot=SLOT_NUT;break;
        case ITEM_BOMB:slot=SLOT_BOMB;break;case ITEM_BOMBCHU:slot=SLOT_BOMBCHU;break;
        case ITEM_SLINGSHOT:slot=SLOT_SLINGSHOT;break;case ITEM_BEAN:slot=SLOT_BEAN;break;
        case ITEM_BOW:case ITEM_ARROW_FIRE:case ITEM_ARROW_ICE:case ITEM_ARROW_LIGHT:
        case ITEM_BOW_ARROW_FIRE:case ITEM_BOW_ARROW_ICE:case ITEM_BOW_ARROW_LIGHT:slot=SLOT_BOW;break;
        default:break;
    }
    if(slot<0||slot>=15)return -1;
    int n=RETAIL_SAVE->ammo[slot];return n<0?0:(n>99?99:n);
}
static void item(u32 q,u8 id,float cx,float cy,u32 status) {
    if(id==ITEM_NONE||id>ITEM_HEART_PIECE_2)return;
    Scene_Rect(&icons,q,(Rect){cx-7,cy-7,14,14});
    Scene_UV(&icons,q,512,512,(Rect){(id%12)*42,(id/12)*42,42,42});
    for(u32 v=0;v<4;v++){for(u32 c=0;c<3;c++)icons.colors[q*16+v*4+c]=1;
        icons.colors[q*16+v*4+3]=status<5 && RETAIL_SAVE->buttonStatus[status]==255 ? .35f:1;}
    int n=ammo(id);if(n>=0)number(16+q*2,n,2,cx-6,cy+10,.65f);
}
static void heart(void* renderer,u32 q,u32 capacity) {
    hideHeart(q);if(q>=capacity)return;
    float* p=Retail_Positions(renderer,63+q),*uv=Retail_UVs(renderer,63+q);Rect b;
    if(!Scene_Bounds(p,&b)||!Retail_Pointer(uv)||b.width>32||b.height>32)return;
    for(u32 v=0;v<4;v++) {
        tosHeartPositions[q*12+v*3]=TOS_HEALTH.x+4.5f+(q%10)*12+(p[v*3]-b.x-b.width*.5f)*TOS_HEALTH.scale;
        tosHeartPositions[q*12+v*3+1]=TOS_HEALTH.y+4.5f+(q/10)*9.75f+(p[v*3+1]-b.y-b.height*.5f)*TOS_HEALTH.scale;
        tosHeartPositions[q*12+v*3+2]=p[v*3+2];
    }
    for(u32 i=0;i<8;i++)tosHeartUVs[q*8+i]=uv[i];
}
void Hud_ActionBegin(void) {
    actionPositions=0;actionValid=0;
    if(Frontend_Read().owner!=OWNER_GAME)return;
    void* source=Retail_PointerAt(RETAIL_ACTION_ROOT+0x18);if(!Retail_Pointer(source))return;
    float* p=Retail_Positions(source,0);if(!Retail_Pointer(p))return;
    for(u32 i=0;i<24;i++)actionOriginal[i]=p[i];
    /* This exact two-quad action owner is an established recovered seam. */
    for(u32 q=0;q<2;q++) {
        Rect b;if(!Scene_Bounds(p+q*12,&b))continue;
        if(b.width>b.height*1.35f && b.width<200 && b.height<100) {
            float* uv=Retail_UVs(source,q);if(Retail_Pointer(uv)) {
                for(u32 i=0;i<8;i++)actionUV[i]=uv[i];actionBounds=b;actionValid=1;
            }
        }
        for(u32 v=0;v<4;v++){p[q*12+v*3]=-1000;p[q*12+v*3+1]=-1000;}
    }
    actionPositions=p;
}
void Hud_ActionEnd(void){if(actionPositions)for(u32 i=0;i<24;i++)actionPositions[i]=actionOriginal[i];actionPositions=0;}
void Hud_Submit(void) {
    frame++;
    scenesReady=0;
    Frontend f=Frontend_Read();
    visible=f.owner==OWNER_GAME && RETAIL_WORD(RETAIL_HUD+0x34)!=0 && RETAIL_SAVE->health>0;
    for(u32 q=0;q<20;q++)hideHeart(q);
    void* top=Retail_PointerAt(RETAIL_ACTION_ROOT+0x74);
    void* lower=Retail_PointerAt(RETAIL_HUD+4);
    if(visible && Retail_Pointer(lower)) {
        u32 n=((u16)RETAIL_SAVE->healthCapacity+15)/16;if(n>20)n=20;
        for(u32 q=0;q<20;q++)heart(lower,q,n);
    }
    if(Retail_Pointer(top)) {
        RETAIL_FN(void(*)(void*,u32,const void*),0x0036759Cu)(top,sizeof(tosHeartPositions),tosHeartPositions);
        RETAIL_FN(void(*)(void*,u32,const void*),0x00317D1Cu)(top,sizeof(tosHeartUVs),tosHeartUVs);
        /* Keep the established native top draw lane available for the Ocarina. */
        RETAIL_BYTE(RETAIL_ACTION_ROOT)=visible || f.owner==OWNER_OCARINA;
    }
    if(visible && Retail_Pointer(lower) && Scene_Ensure(&native,16,2) &&
        Scene_Ensure(&chrome,7,2) && Scene_Ensure(&icons,6,10) && Scene_Ensure(&labels,32,1)) {
        Scene_Clear(&native);Scene_Clear(&chrome);Scene_Clear(&icons);Scene_Clear(&labels);
        if(RETAIL_SAVE->magicAcquired) {
            Rect group={0};int first=1;
            for(u32 q=0;q<4;q++){Rect b;if(Scene_Bounds(Retail_Positions(lower,59+q),&b)) {
                if(first){group=b;first=0;}else{float rx=group.x+group.width,ry=group.y+group.height;
                    if(b.x<group.x)group.x=b.x;if(b.y<group.y)group.y=b.y;
                    if(b.x+b.width>rx)rx=b.x+b.width;if(b.y+b.height>ry)ry=b.y+b.height;
                    group.width=rx-group.x;group.height=ry-group.y;}
            }}
            if(!first)for(u32 q=0;q<4;q++)Scene_Copy(&native,q,lower,59+q,(Transform){8-group.x*.75f,29.5f-group.y*.75f,.75f},0);
        }
        Transform face=Layout_Resolve(TOS_FACE,400,240);
        const float cx[]={face.x,face.x-22,face.x+22,face.x,292,320};
        const float cy[]={face.y-22,face.y,face.y,face.y+22,22,22};
        const Glyph gs[]={GLYPH_Y,GLYPH_X,GLYPH_B,GLYPH_A,GLYPH_LB,GLYPH_RB};
        for(u32 q=0;q<6;q++) {
            Scene_Rect(&chrome,q,(Rect){cx[q]-11,cy[q]-11,22,22});
            Scene_UV(&chrome,q,512,256,(Rect){384,184,38,38});
            glyph(q,gs[q],cx[q]-(q>=4?5:3),cy[q]-15,q>=4?10:6,7);
        }
        /* Native equips order B,Y,X,I,II. Xbox presentation follows alpha-098:
         * physical Y = native X lane; physical X = native Y lane. Match the
         * same native buttonStatus lane so disabled-item opacity stays native. */
        item(0,RETAIL_SAVE->equips.buttonItems[2],cx[0],cy[0],2);
        item(1,RETAIL_SAVE->equips.buttonItems[1],cx[1],cy[1],1);
        item(2,RETAIL_SAVE->equips.buttonItems[0],cx[2],cy[2],0);
        item(3,RETAIL_SAVE->equips.buttonItems[3],cx[4],cy[4],3);
        item(4,RETAIL_SAVE->equips.buttonItems[4],cx[5],cy[5],4);
        u8 ocarina=RETAIL_SAVE->items[SLOT_OCARINA];
        if(ocarina==ITEM_OCARINA_FAIRY||ocarina==ITEM_OCARINA_TIME)item(5,ocarina,57,72,5);
        if(actionValid) {
            float ratio=actionBounds.width/actionBounds.height,w=10.0f*ratio;
            if(w>42)w=42;
            Scene_Rect(&labels,6,(Rect){cx[3]-w*.5f,cy[3]-5,w,10});
            for(u32 v=0;v<4;v++){labels.uvs[48+v*2]=actionUV[(v^2)*2];labels.uvs[49+v*2]=actionUV[(v^2)*2+1];}
        }
        Scene_Rect(&chrome,6,(Rect){20,58,28,28});Scene_UV(&chrome,6,512,256,(Rect){424,189,28,28});
        glyph(7,GLYPH_ITEMS,19,46,30,9);glyph(8,GLYPH_GEAR,22,91,24,9);
        Scene_Rect(&native,4,(Rect){4,214,18,18});Scene_UV(&native,4,512,256,(Rect){128,96,18,18});
        int rupees=RETAIL_SAVE->rupees;number(9,rupees<0?0:(rupees>999?999:rupees),3,28,219,1);
        GlobalContext* play=Retail_PointerAt(RETAIL_HUD);
        u16 mapIndex=RETAIL_HALF(0x00588EEAu);
        if(Retail_Pointer(play)&&play->sceneNum>=3&&play->sceneNum<=16&&mapIndex<19) {
            s8 keys=*(volatile s8*)(0x00587A2Cu+mapIndex);
            if(keys>=0){Scene_Rect(&native,5,(Rect){4,194,18,18});Scene_UV(&native,5,512,256,(Rect){152,96,18,18});number(12,keys,2,28,199,1);}
        }
        if(Retail_Mounted(play))for(u32 q=0;q<6;q++) {
            float* uv=Retail_UVs(lower,86+q);if(!Retail_Pointer(uv))continue;
            Scene_Rect(&native,6+q,(Rect){148+18*q,196,14,14});
            for(u32 v=0;v<4;v++){native.uvs[(6+q)*8+v*2]=uv[(v^2)*2];native.uvs[(6+q)*8+v*2+1]=uv[(v^2)*2+1];}
        }
        float* viewUV=Retail_UVs(lower,28);
        if(Retail_Pointer(viewUV)) {
            float u=0,v=0;
            for(u32 i=0;i<4;i++){u+=viewUV[i*2]*.25f;v+=viewUV[i*2+1]*.25f;}
            if(v>.6f) {
                int fairy=v>.8f&&u>=.34f;
                Scene_Rect(&native,12,fairy?(Rect){5,65,14,14}:(Rect){4,67,16,10});
                Scene_UV(&native,12,512,256,(Rect){u<.34f?128:176,v>.8f?0:48,48,fairy?48:30});
            }
        }
        Scene_Upload(&native);Scene_Upload(&chrome);Scene_Upload(&icons);Scene_Upload(&labels);
        scenesReady=1;
    }
    RETAIL_FN(void(*)(void),0x0042DD84u)();
}
void Hud_Draw(void) {
    if(drawFrame==frame)return;
    if(Frontend_Read().owner==OWNER_OCARINA){Ocarina_Draw();drawFrame=frame;return;}
    if(!visible||!scenesReady)return;
    Scene_Draw(&native);Scene_Draw(&chrome);Scene_Draw(&icons);Scene_Draw(&labels);drawFrame=frame;
}
