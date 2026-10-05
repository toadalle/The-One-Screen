"""Static USA Rev1 native Ocarina seam/glyph provenance regression.

Requires the independently verified pristine code.bin and original CTXB; it
cannot prove that a screen or sound output is correct inside the emulator.
"""
import json
import pathlib
import struct
import sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'tools'))
import build_ocarina_atlas as atlas

ROOT=pathlib.Path(__file__).resolve().parents[1]
retail=pathlib.Path(sys.argv[1])
code=(retail/'code.bin').read_bytes()
expected=bytes.fromhex('331e00eb')
assert code[0x41EE74-0x100000:0x41EE78-0x100000]==expected, 'unexpected Ocarina draw seam'
patches=json.loads((ROOT/'config/patches.json').read_text())
hook=[p for p in patches if p['name']=='ocarina_native_draw']
assert len(hook)==1 and int(hook[0]['address'],16)==0x41EE74 and bytes.fromhex(hook[0]['expected'])==expected
# Recovered native static UV origin/size table for exactly these quads. Large
# full-size glyphs have separate atlas cells from the small staff-note symbols.
for q,x in ((67,392),(72,416),(76,440),(80,464),(84,488)):
    uv=struct.unpack_from('<ff',code,0x509E6C-0x100000+q*8)
    size=struct.unpack_from('<ff',code,0x509B0C-0x100000+q*8)
    assert uv==(float(x),232.) and size==(19.,22.),(q,uv,size)
assert atlas.FULL_GLYPHS==((392,'LT'),(416,'RT'),(440,'X'),(464,'Y'),(488,'B'))
base=atlas.decode_ctxb((retail/'menu_okarina_parts00_base.ctxb').read_bytes())
new=atlas.decode_ctxb((ROOT/'load/mods/0004000000033500/romfs/menu/01_US_ENGLISH/menu_okarina_parts00.ctxb').read_bytes())
for rect in ((128,160,144,176),(176,160,192,176),(192,160,208,176)):
    assert base.crop(rect).tobytes()==new.crop(rect).tobytes(),'shared small staff glyph changed'
assert base.crop(atlas.QUIT_LETTER_BLOCKS).tobytes()!=new.crop(atlas.QUIT_LETTER_BLOCKS).tobytes(),'native Quit remained B'
for x,_ in atlas.FULL_GLYPHS:
    rect=(x,232,x+20,256)
    assert new.crop(rect).getchannel('A').getbbox() is None,'full-size native ink was not made transparent'
src=(ROOT/'source/frontend/ocarina.c').read_text()
assert 'Ocarina_DrawNative(void)' in src
assert 'RET​AIL_FN'.replace('\u200b','') in src
assert 'const u8 xq[]={73,74,75,76,97,98,105};' in src
assert 'const u8 yq[]={77,78,79,80,99,100,106};' in src
assert src.count('0x0036759Cu')==1  # one scoped GPU upload; restore CPU only before deferred draw
print('PASS: native Ocarina seam, single custom lettering, deferred GPU geometry')
