"""Static regression based on recovered full-size and Quit quad tables."""
import pathlib,struct,sys
root=pathlib.Path(__file__).resolve().parents[1]
code=(pathlib.Path(sys.argv[1])/'code.bin').read_bytes()
source=(root/'source/frontend/ocarina.c').read_text()
hud=(root/'source/hud/hud.c').read_text()
assert 'nativeLabels' in source and 'Scene_Draw(&nativeLabels)' in source, 'single independent lettering path missing'
assert 'label(9,GLYPH_RB' not in source, 'stray compact RB restored'
for q in (32,33,34,48,49):
    assert f'q=={q}' in source, f'native Quit backing {q} reintroduced on main sheet'
for q,x,y,w,h in ((32,0,202,50,38),(33,50,202,8,38),(34,0,204,56,36),
                  (48,0,206,40,36),(49,40,206,16,36)):
    off=0x50944c-0x100000+q*8
    off2=0x5097ac-0x100000+q*8
    assert struct.unpack_from('<2f',code,off)==(float(x),float(y))
    assert struct.unpack_from('<2f',code,off2)==(float(w),float(h))
assert 'TOS_ITEM_OVERLAY CALIBRATED_X274' in hud and 'OWNER_PAUSE' in hud
assert 'RETAIL_WORD(RETAIL_ITEMS)!=2' in hud and 'RETAIL_WORD(RETAIL_GEAR)!=2' in hud
print('PASS: full-size transparent native atlas and one scene, exact original Quit backing quads, guarded inventory fallback')
