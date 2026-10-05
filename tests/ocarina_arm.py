"""Production ARM Ocarina composition with controlled native geometry fixtures."""
import arm_regressions as a
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import *
import struct
u=a.u;r=a.r;w=a.w;call=a.call;ret=a.ret
scenes={};text_draws=[];text_updates=[]
def floats(addr,count):return struct.unpack('<'+'f'*count,u.mem_read(addr,count*4))
def put(addr,values):u.mem_write(addr,struct.pack('<'+'f'*len(values),*values))
def reg(n):return u.reg_read([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2][n])
def hook(uc,pc,size,_):
 if pc==a.symbols['Scene_Ensure']:
  w(reg(0)+16,reg(1));w(reg(0)+20,reg(2));w(reg(0)+24,1);u.reg_write(UC_ARM_REG_R0,1);ret()
 elif pc in (a.symbols['Scene_Upload'],):ret()
 elif pc==a.symbols['Scene_Draw']:
  scene=reg(0);scenes[r(scene+20)]=scene;u.reg_write(UC_ARM_REG_R0,1);ret()
 elif pc in (0x2fc3fc,0x2fc3f0,0x2fc3e4):
  offset,stride={0x2fc3fc:(12,48),0x2fc3f0:(20,32),0x2fc3e4:(24,64)}[pc]
  u.reg_write(UC_ARM_REG_R0,r(reg(0)+offset)+reg(1)*stride);ret()
 elif pc==0x2f7684:text_updates.append(floats(0x77803c,5));ret()
 elif pc==0x7fff20:text_draws.append(floats(reg(0)+0x3c,5));ret()
u.hook_add(UC_HOOK_CODE,hook)
renderer=0x760000
w(0x5093ec,renderer);w(renderer,108)
for offset,address in [(12,0x762000),(16,0x764000),(20,0x766000),(24,0x768000),(28,0x76a000)]:w(renderer+offset,address)
put(0x768000,[1.]*108*16)
def quad(q,x,y,width,height,base=0x762000):put(base+q*48,[x,y+height,0,x+width,y+height,0,x,y,0,x+width,y,0])
for q in range(108):quad(q,0,0,0,0)
for q,box in {58:(262,202,8,36),59:(270,202,40,36),60:(310,202,8,36),61:(264,204,52,32),62:(24,62,273,157),67:(71,66,19,22),72:(231,66,19,22),73:(135,89,25,50),74:(160,89,25,50),75:(137,91,46,46),76:(150,102,19,22),77:(86,143,25,50),78:(111,143,25,50),79:(88,145,46,46),80:(101,156,19,22),84:(200,156,19,22),97:(137,93,23,46),98:(160,93,23,46),99:(88,147,23,46),100:(111,147,23,46),105:(128,82,32,32),106:(79,136,32,32)}.items():quad(q,*box)
def xy(scene,q):return floats(scene+308+q*48,12)
def center(p):return (sum(p[::3])/4,sum(p[1::3])/4)
def close(actual,expected):assert all(abs(x-y)<.002 for x,y in zip(actual,expected)),(actual,expected)
w(0x5093f8,12)
# X press: its rim/sparkle/letter move left together, including the press offset.
put(0x76a000+76*8,[0,2]);call('Ocarina_Draw')
notes,labels=scenes[5],scenes[1]
close(center(xy(labels,2)),(280+110.5*.35,8+169*.35))
close(center(xy(labels,3)),(280+159.5*.35,8+113*.35))
close(xy(notes,97)[:2],(280+88*.35,8+193*.35))
close(xy(notes,105)[:2],(280+79*.35,8+168*.35))
# The other button's label anchor does not move when X is pressed.
put(0x76a000+76*8,[0,0]);call('Ocarina_Draw')
close(center(xy(labels,3)),(280+159.5*.35,8+113*.35))
# Y press follows its own moved group and leaves X stationary.
put(0x76a000+80*8,[0,2]);call('Ocarina_Draw')
close(center(xy(labels,2)),(280+110.5*.35,8+167*.35))
close(center(xy(labels,3)),(280+159.5*.35,8+115*.35))
close(xy(notes,99)[:2],(280+137*.35,8+139*.35))
put(0x76a000+80*8,[0,0]);call('Ocarina_Draw')
# RB centers above the complete song-sheet icon, leaving its artwork clear.
close(center(xy(labels,9)),(280+290*.35,8+189*.35))
assert max(xy(labels,9)[1::3])<min(xy(notes,61)[1::3])
# Quit uses the HUD chrome texture, with A above the bubble and Quit inside it.
assert r(scenes[2]+16)==1
assert center(xy(labels,7))[1]<min(xy(scenes[2],0)[1::3])
close(center(xy(labels,8)),center(xy(scenes[2],0)))
# Song page cursor must include its selected tile translation.
selector=0x770000;cr=0x771000
w(0x5093f0,selector);w(selector+8,cr);w(selector+12,8);w(cr,8)
for offset,address in [(12,0x772000),(16,0x773000),(20,0x774000),(24,0x775000),(28,0x776000)]:w(cr+offset,address)
for q in range(8):quad(q,0,0,8,8,0x772000);put(0x776000+q*8,[240,180])
put(0x775000,[1.]*128)
# Borrowed current song title transforms at draw, then restores native state.
group=0x777000;node=0x778000;vt=0x779000
w(0x5093f4,group);w(group+0x40,3);w(group+0x10,node);w(node,vt);w(vt+12,0x7fff20)
put(node+0x3c,[100,220,0,1,1]);original=floats(node+0x3c,5)
w(0x5093f8,4);call('Ocarina_Draw')
close(center(xy(scenes[1],9)),(800.,800.))
close(xy(scenes[13],0)[:2],(64+240*.85,18+188*.85))
assert floats(node+0x3c,5)==original
assert len(text_draws)==1 and len(text_updates)==2
close(text_draws[0],(64+100*.85,18+220*.85,0,.85,.85))
close(text_updates[-1],original)
# On the song page, dynamic tail quads do not receive the play-only XY swap.
close(xy(scenes[5],97)[:2],(64+137*.85,18+139*.85))
print('PASS: ARM Ocarina independent X/Y press geometry, RB above song icon, HUD Quit bubble, materialized cursor, scaled/restored native song title')
