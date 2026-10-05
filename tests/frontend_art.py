"""Verify the packaged texture changes are confined to declared lettering."""
import pathlib,sys
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import build_frontend_atlases as frontend
import build_menu_top_atlas as codec
retail=pathlib.Path(sys.argv[1])
for family,regions,height in [('menu_file_select',frontend.FILE_BUTTONS,256),('name_entry00',frontend.NAME_BUTTONS,512)]:
    codec.HEIGHT=height
    mask=np.zeros((height,512),bool)
    for _,(x,y,w,h) in regions:mask[y:y+h,x:x+w]=True
    for v in ('00','01'):
        name=f'{family}_parts{v}.ctxb'
        base=(retail/name).read_bytes()
        target=(ROOT/'load/mods/0004000000033500/romfs/menu/01_US_ENGLISH'/name).read_bytes()
        original=np.array(codec.decode_ctxb(base));modified=np.array(codec.decode_ctxb(target))
        assert target[:72]==base[:72],name
        assert np.array_equal(original[~mask],modified[~mask]),name+' modified native art outside lettering'
        assert np.array_equal(original[:,:,3],modified[:,:,3]),name+' modified container alpha'
        print('PASS:',name,'native art unchanged outside lettering; alpha preserved')
codec.HEIGHT=256
import build_ocarina_atlas as ocarina
base=(retail/'menu_okarina_parts00_base.ctxb').read_bytes()
target=(ROOT/'load/mods/0004000000033500/romfs/menu/01_US_ENGLISH/menu_okarina_parts00.ctxb').read_bytes()
assert target[:72]==base[:72]
for y in range(0,256,4):
    for x in range(0,512,4):
        off=72+ocarina.block_index(x//4,y//4)*16
        a=base[off:off+16];b=target[off:off+16]
        staff=144<=x<160 and 160<=y<176
        trigger=208<=x<240 and 160<=y<176
        full=232<=y<256 and any(a<=x<a+20 for a,_ in ocarina.FULL_GLYPHS)
        if not (staff or full):assert a[:8]==b[:8],('alpha',x,y)
        quit=164<=y<176 and 76<=x<88
        if not (staff or trigger or full or quit):assert a==b,('outside lettering',x,y)
print('PASS: Ocarina native art outside declared blocks and all non-glyph alpha preserved')
# Item-strip relabeling is confined to glyph cells; native icons/containers stay.
codec.WIDTH=512;codec.HEIGHT=256
base=(retail/'menu_top_parts00_base.ctxb').read_bytes()
target=(ROOT/'load/mods/0004000000033500/romfs/menu/01_US_ENGLISH/menu_top_parts00.ctxb').read_bytes()
original=np.array(codec.decode_ctxb(base));modified=np.array(codec.decode_ctxb(target))
mask=np.zeros((256,512),bool)
for x0,y0,x1,y1 in codec.CELLS.values():mask[y0:y1,x0:x1]=True
x0,y0,x1,y1=codec.CHROME_GUARD;mask[y0:y1,x0:x1]=True
assert np.array_equal(original[~mask],modified[~mask])
assert codec.MAPPING=={'I':'LB','X':'Y','Y':'X','B':'B','II':'RB'}
print('PASS: verified alpha-098 inventory lettering map; surrounding native art unchanged')
