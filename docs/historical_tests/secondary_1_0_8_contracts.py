"""1.0.8: code+decoded resource invariants, NOT Azahar visual tests."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[1]
src=(root/'source/frontend/ocarina.c').read_text()
hud=(root/'source/hud/hud.c').read_text()
assert src.count('Scene_Draw(&nativeLabels)') == 1
assert 'static Scene notes,labels,cursor,chrome,nativeLabels;' in src
assert 'static const u8 xq[]={73,74,75,76,97,98,105};' in src
assert 'static const u8 yq[]={77,78,79,80,99,100,106};' in src
for part in ('q==32','q==33','q==34','q==48','q==49'):
    assert part in src, part
assert 'TOS_ITEM_OVERLAY CALIBRATED_X274' in hud
assert 'Rect cover={269.f,cy[i]-9.f,23.f,19.f}' in hud
assert '274.f-width*.5f' in hud
assert 'if(matches[i]!=1)' in hud # original safe fallback retained
sys.path.insert(0,str(root/'tools'))
import build_ocarina_atlas as o
base=o.decode_ctxb((Path(sys.argv[1])/'menu_okarina_parts00_base.ctxb').read_bytes())
new=o.decode_ctxb((root/'load/mods/0004000000033500/romfs/menu/01_US_ENGLISH/menu_okarina_parts00.ctxb').read_bytes())
for x,_ in o.FULL_GLYPHS:
    assert new.crop((x,232,x+20,256)).getchannel('A').getbbox() is None,x
for rect in ((128,160,144,176),(176,160,192,176),(192,160,208,176)):
    assert new.crop(rect).tobytes()==base.crop(rect).tobytes(),rect
print('PASS: calibrated inventory overlay + five transparent large-play cells + unchanged song-note cells')
