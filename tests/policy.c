#include <assert.h>
#include "../source/input/policy.h"
#include "../source/input/shortcuts.h"
#include "../source/render/layout.h"
int main(void){
    for(unsigned i=0;i<65536;i++){
        unsigned gameplay=(i&~((1u<<10)|(1u<<11)))|((i&(1u<<10))?(1u<<11):0u)|((i&(1u<<11))?(1u<<10):0u);
        assert(Input_Translate(i,INPUT_GAMEPLAY)==gameplay);
        assert(Input_Translate(gameplay,INPUT_GAMEPLAY)==i);
        unsigned expected=(i&~3u)|((i&1u)?2u:0u)|((i&2u)?1u:0u);
        assert(Input_Translate(i,INPUT_OCARINA)==expected);
        assert(Input_Translate(expected,INPUT_OCARINA)==i);
    }
    Digital d={1,2,4};Digital o=Input_TranslateDigital(d,INPUT_OCARINA);
    assert(o.held==2&&o.pressed==1&&o.released==4);
    Digital g={(1u<<10),(1u<<11),4};g=Input_TranslateDigital(g,INPUT_GAMEPLAY);
    assert(g.held==(1u<<11)&&g.pressed==(1u<<10)&&g.released==4);
    assert(Input_Translate((1u<<10)|(1u<<11),INPUT_OCARINA)==((1u<<10)|(1u<<11)));
    assert(Shortcut_FromEdges(BUTTON_UP)==SHORTCUT_ITEMS);
    assert(Shortcut_FromEdges(BUTTON_DOWN)==SHORTCUT_GEAR);
    assert(Shortcut_FromEdges(BUTTON_START)==SHORTCUT_PAUSE);
    assert(Shortcut_FromEdges(BUTTON_SELECT)==SHORTCUT_MAP);
    assert(Shortcut_FromEdges(BUTTON_RIGHT)==SHORTCUT_OCARINA);
    assert(Shortcut_FromEdges(BUTTON_LEFT)==SHORTCUT_NONE);
    assert(Shortcut_FromEdges(BUTTON_UP|BUTTON_START)==SHORTCUT_ITEMS);
    Transform t=Layout_Resolve((Layout){ANCHOR_TOP_RIGHT,8,8,.35f,320,240},400,240);
    Rect r=Layout_Rect((Rect){0,0,320,240},t);
    assert(r.x==280&&r.y==8&&r.width==112&&r.height==84);
    t=Layout_Resolve((Layout){ANCHOR_CENTER,0,0,.85f,320,240},400,240);
    r=Layout_Rect((Rect){0,0,320,240},t);
    assert(r.x>=0&&r.y>=0&&r.x+r.width<=400&&r.y+r.height<=240);
    return 0;
}
