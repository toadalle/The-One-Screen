"""Execute the built ARM payload against isolated native-call stubs.
Requires unicorn==2.1.4. This checks machine code and ABI, not Azahar visuals.
"""
from pathlib import Path
import struct,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import build
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_ARM, UC_HOOK_CODE
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[1]
b=(ROOT/'.build/tos.elf').read_bytes()
off=struct.unpack_from('<I',b,32)[0];sz,n=struct.unpack_from('<HH',b,46)
secs=[struct.unpack_from('<10I',b,off+i*sz) for i in range(n)]
symbols={}
for s in secs:
    if s[1]!=2:continue
    st=secs[s[6]];strings=b[st[4]:st[4]+st[5]]
    for j in range(s[4],s[4]+s[5],s[9]):
        name,value,_,_,_,_=struct.unpack_from('<IIIBBH',b,j)
        symbols[strings[name:].split(b'\0')[0].decode()]=value
u=Uc(UC_ARCH_ARM,UC_MODE_ARM);u.mem_map(0x100000,0x700000);u.mem_map(0x10080000,0x10000)
u.reg_write(UC_ARM_REG_C1_C0_2,0xf00000);u.reg_write(UC_ARM_REG_FPEXC,0x40000000)
for _,a,data in build.read_elf(ROOT/'.build/tos.elf'):u.mem_write(a,data)
STOP=0x7fff00;DRAW=0x7fff10;STACK=0x1008f000
REGS=[UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]
owner=9;swap=0;events=[];restart=[]
def w(a,v):u.mem_write(a,struct.pack('<I',v))
def r(a):return struct.unpack('<I',u.mem_read(a,4))[0]
def ret():u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
def hook(uc,a,size,_):
    if a==symbols['Frontend_Read']:
        u.mem_write(u.reg_read(UC_ARM_REG_R0),struct.pack('<III',owner,4,swap));ret()
    elif a==0x300240:events.append(('submit',u.reg_read(UC_ARM_REG_R1)));ret()
    elif a in (0x311364,0x2feabc):ret()
    elif a==DRAW:events.append(('draw',u.reg_read(UC_ARM_REG_R0)));ret()
    elif a==0x41c3c8:events.append(('fade',0));ret()
    elif a==0x2e78f8:
        q=0x5c0ba8;i=r(q+12);w(q+0x154+i*4,0x720000+i*0x200);w(q+12,i+1);ret()
    elif a==0x2f9a1c:
        stream=u.reg_read(UC_ARM_REG_R0)
        data=list(struct.unpack('<'+'f'*r(stream)*12,u.mem_read(r(stream+0x0c),r(stream)*48)))
        if r(stream+0x1c):
            for q in range(r(stream)):
                dx,dy=struct.unpack('<2f',u.mem_read(r(stream+0x1c)+q*8,8))
                for v in range(4):data[q*12+v*3]+=dx;data[q*12+v*3+1]+=dy
        u.mem_write(r(stream+0x10),struct.pack('<'+'f'*len(data),*data));ret()
    elif a==0x4197e0:restart.append((a,u.reg_read(UC_ARM_REG_SP)));uc.emu_stop()
u.hook_add(UC_HOOK_CODE,hook)
def call(name,*args):
    for reg,v in zip(REGS,args):u.reg_write(reg,v)
    u.reg_write(UC_ARM_REG_SP,STACK);u.reg_write(UC_ARM_REG_LR,STOP)
    u.emu_start(symbols[name],STOP,count=200000)
    assert u.reg_read(UC_ARM_REG_PC) in (STOP,0x4197e0),(name,hex(u.reg_read(UC_ARM_REG_PC)))
    assert u.reg_read(UC_ARM_REG_SP)==STACK,name
    return u.reg_read(UC_ARM_REG_R0)
# Renderer, primary + lower FBOs, native mode background queued in this frame.
renderer=0x710000;u.mem_write(renderer+4,b'\1');w(renderer+0x38,1);w(renderer+0x3c,2)
call('Presentation_ModeBackdrop',0x730000,0x73001c,0x731000,0x732000)
background=0x720000
call('Presentation_Target',renderer,0x400)
call('Presentation_Submit',renderer,0x400)
call('Presentation_Target',renderer,0x401)
call('Presentation_QueuedNode',background,DRAW)
call('Presentation_Backdrop',0x733000,DRAW)
call('Presentation_LowerFade',0x734000)
# Exercise the actual assembly restart seam, including preserved register state.
for reg in range(UC_ARM_REG_R4,UC_ARM_REG_R12+1):u.reg_write(reg,reg*123)
before=[u.reg_read(reg) for reg in range(UC_ARM_REG_R4,UC_ARM_REG_R12+1)]
call('tos_submit_lower',renderer,0x401)
assert len(restart)==1 and restart[0][1]==STACK
assert before==[u.reg_read(reg) for reg in range(UC_ARM_REG_R4,UC_ARM_REG_R12+1)]
call('Presentation_Target',renderer,0x401)
call('Presentation_QueuedNode',background,DRAW)
call('Presentation_QueuedNode',background+0x200,DRAW)
call('Presentation_Backdrop',0x733000,DRAW)
call('Presentation_LowerFade',0x734000)
call('tos_submit_lower',renderer,0x401)
assert len(restart)==1, 'unbounded render restart'
assert events==[('draw',background),('draw',0x733000),('fade',0),('submit',0x401),('draw',background+0x200),('submit',0x400)],events
# Next gameplay frame resets projection, and ordinary presentation is untouched.
owner=0;events.clear();call('Presentation_Target',renderer,0x400)
call('Presentation_Submit',renderer,0x400)
call('Presentation_Target',renderer,0x401);call('tos_submit_lower',renderer,0x401)
assert events==[('submit',0x400),('submit',0x401)] and len(restart)==1
# Ocarina is a one-sample touch even without an acknowledgement from the menu.
request=symbols['request'];previous=symbols['previous'];out=0x740000
u.mem_write(previous,bytes(12))
def touch(action,x,y):u.mem_write(request,struct.pack('<IHHI',action,x,y,0))
def sample():
    call('Bridge_TouchMaterialized',out,out+2,out+4)
    return struct.unpack('<HHB',u.mem_read(out,5))
touch(4,8,235)
assert sample()==(8,235,1)
assert r(request)==0
assert sample()==(8,235,0)
# A pending different owner receives a release, then down with its own coords.
touch(5,3,3);assert sample()==(3,3,1)
touch(8,290,215);assert sample()==(3,3,0)
assert r(request)==8
assert sample()==(290,215,1)
assert sample()==(290,215,0)
# Held I is continuous until released; no timeout or one-shot behavior.
touch(6,316,3)
for _ in range(40):assert sample()==(316,3,1)
touch(0,0,0);assert sample()==(316,3,0)
# Minimap player/entrance markers share the body delta, never counters/actions.
owner=0;body=0x750000;quest=0x751000
w(0x4fda84,body);w(0x4fc660,quest)
w(body+0x0c,0x752000);w(body+0x1c,0x753000)
u.mem_write(0x752000,struct.pack('<12f',10,230,0,70,230,0,10,170,0,70,170,0))
w(quest,8);w(quest+0x0c,0x754000);w(quest+0x10,0x755000)
native=[float(i) for i in range(96)]
u.mem_write(0x754000,struct.pack('<96f',*native))
call('Minimap_MaterializeMarkers',quest)
delta=struct.unpack('<f',u.mem_read(0x753000,4))[0]
assert delta!=0
got=struct.unpack('<96f',u.mem_read(0x755000,384))
for i,v in enumerate(got):assert v==native[i]+(delta if i//12 in (2,3) and i%3==0 else 0),(i,v)
call('Minimap_MaterializeMarkers',quest)
assert got==struct.unpack('<96f',u.mem_read(0x755000,384)), 'marker drift on repeated materialization'
owner=2;call('Minimap_MaterializeMarkers',quest)
assert r(0x753000)==0
assert tuple(native)==struct.unpack('<96f',u.mem_read(0x755000,384))
print('PASS: ARM render restart/stack/registers, native/main transfers, backdrop identity, once-only fade, touch pulse/release/handoff/hold, minimap marker isolation/no-drift/restoration')
