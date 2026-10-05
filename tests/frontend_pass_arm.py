"""Execute real ARM pass routing and exact producer handling, not visuals."""
import arm_regressions as a
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import *
import struct
u=a.u;w=a.w;r=a.r;call=a.call;ret=a.ret
viewport=[];draws=[]
def hook(uc,pc,size,_):
    if pc==0x2feabc:
        viewport.append(tuple(u.reg_read(x) for x in a.REGS));ret()
    elif pc==a.DRAW:
        draws.append((u.reg_read(UC_ARM_REG_R0),viewport[-1] if viewport else None));ret()
    elif pc==0x3339e8:
        queue=u.reg_read(UC_ARM_REG_R0);i=r(queue+8)
        w(queue+0xf4+i*4,0x730000+i*0x200);w(queue+8,i+1);ret()
    elif pc==a.symbols['svcOutputDebugString']:ret()
u.hook_add(UC_HOOK_CODE,hook)
renderer=0x710000;queue=0x5c0ba8
save=0x587958
w(save,0x629);w(save+8,0xfff0);w(save+0x14e4,1)
a.owner=9;a.swap=0
w(queue+12,0);w(queue+8,0)
# Producers run outside either lower draw. Preserve background queue entry.
call('Presentation_ModeBackdrop',0x760000,0x760020,0x761000,0x762000)
assert r(queue+12)==1
background=r(queue+0x154)
call('Presentation_FadePrimitive',queue,6,0x762000,9)
fade=r(queue+0xf4)
call('Presentation_Target',renderer,0x400)
call('Presentation_Target',renderer,0x401)
a.events.clear();call('Presentation_LowerFade',0x763000)
call('Presentation_DrawQueued',background,a.DRAW)
assert draws[-1][0]==background
call('Presentation_DrawQueued',fade,a.DRAW)
assert draws[-1][1]==(0,0,240,320),'native fade viewport changed'
assert call('Presentation_EndLower',renderer,0x401)==1
call('Presentation_Target',renderer,0x401)
call('Presentation_LowerFade',0x763000)
assert a.events.count(('fade',0))==1,'fade advanced again on replay'
count=len(draws);call('Presentation_DrawQueued',background,a.DRAW)
assert len(draws)==count,'promoted background still drawn'
call('Presentation_DrawQueued',fade,a.DRAW)
assert draws[-1]==(fade,(0,0,480,400))
assert viewport[-1]==(0,40,480,320),'viewport leaked into next UI draw'
other=0x770000;call('Presentation_DrawQueued',other,a.DRAW)
assert draws[-1][0]==other,'unrelated selector/card suppressed'
assert call('Presentation_EndLower',renderer,0x401)==0
# Reused native allocation is no longer identified after both passes finish.
call('Presentation_DrawQueued',background,a.DRAW)
assert draws[-1][0]==background
call('Presentation_DrawQueued',fade,a.DRAW)
assert draws[-1][1]==(0,40,480,320),'expired fade allocation still widened'
# During Mode -> File handoff, retain exact queued background ownership.
w(queue+12,0);w(queue+8,0)
call('Presentation_ModeBackdrop',0x760000,0x760020,0x761000,0x762000)
call('Presentation_FadePrimitive',queue,6,0x762000,9)
w(save+0x14e4,2);w(0x504fb0,1);a.owner=6
call('Presentation_Target',renderer,0x400)
call('Presentation_Target',renderer,0x401)
a.events.clear();call('Presentation_LowerFade',0x763000)
count=len(draws);call('Presentation_DrawQueued',background,a.DRAW)
assert len(draws)==count
call('Presentation_DrawQueued',fade,a.DRAW)
assert draws[-1][1]==(0,0,480,400)
assert call('Presentation_EndLower',renderer,0x401)==1
call('Presentation_Target',renderer,0x401)
call('Presentation_DrawQueued',background,a.DRAW)
assert draws[-1][0]==background,'native File replay lost backdrop'
call('Presentation_LowerFade',0x763000)
assert a.events.count(('fade',0))==1,'File Select replay advanced fade twice'
call('Presentation_DrawQueued',fade,a.DRAW)
assert draws[-1][1]==(0,0,240,320)
assert call('Presentation_EndLower',renderer,0x401)==0
assert call('FileSelect_CurrentPass')==0
print('PASS: exact queued background native/promoted isolation, fade full viewport/restoration, allocation expiry, Mode -> File handoff, alpha-098 replay')

