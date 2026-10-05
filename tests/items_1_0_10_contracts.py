"""1.0.10: preserve alpha-098 item-label behavior without coupling it to Frontend swap state."""
import hashlib,json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
retail=Path(sys.argv[1])
src=(root/'source/frontend/items.c').read_text()
presentation=(root/'source/render/presentation.c').read_text()
hud=(root/'source/hud/hud.c').read_text()
patches=json.loads((root/'config/patches.json').read_text())
assert any(p['name']=='submit_bottom' for p in patches)
assert not any(p['name']=='native_item_strip' for p in patches)
assert 'TOS_ITEM_UV' not in hud and 'Hud_ItemOverlay' not in hud
assert 'if(command==0x401)Items_BeforeSubmit()' in presentation
assert 'Scene_EnsureColorless(&itemLabels,8,2)' in src
assert 'itemLabels.node+0x178u)|=0x10u' in src
assert 'Retail_Gameplay() && itemsState!=0u' in src
assert 'frontend.owner==OWNER_PAUSE && frontend.swap' not in src
assert 'TOS_ITEMS_098 native_state_menu_lane_ready' in src
assert 'TOS_ITEMS_098 native_state_menu_lane_drawn' in src
for line in (
    '{268.f,7.f,17.f,15.f}', '{269.f,65.f,14.f,14.f}',
    '{258.f,117.f,15.f,14.f}', '{268.f,190.f,17.f,15.f}',
    '{270.f,9.f,13.f,11.f}', '{272.f,67.f,9.f,10.f}',
    '{261.f,119.f,9.f,10.f}', '{270.f,192.f,13.f,11.f}',
    '{156.f,125.f,19.f,17.f}', '{156.f,142.f,19.f,16.f}',
    '{156.f,158.f,19.f,16.f}', '{156.f,190.f,19.f,17.f}',
    '{8.f,8.f,8.f,8.f}',
): assert line in src,line
sys.path.insert(0,str(root/'tools'))
import build_menu_top_atlas as atlas
assert atlas.MAPPING=={'I':'LB','X':'Y','Y':'X','B':'B','II':'RB'}
menu=root/'load/mods/0004000000033500/romfs/menu/01_US_ENGLISH/menu_top_parts00.ctxb'
cursor=root/'load/mods/0004000000033500/romfs/menu/01_US_ENGLISH/menu_cursor00.ctxb'
assert hashlib.sha256(menu.read_bytes()).hexdigest()=='993e3b45fb182cd47889f35f24f21ae99bbc269fc4b2371e57ce45c7b794555a'
assert hashlib.sha256(cursor.read_bytes()).hexdigest()=='bbdc4d88b6d42e7951085659489e38b40e0c6dc616a793c1112830e36c2995d8'
assert hashlib.sha256((retail/'menu_top_parts00_base.ctxb').read_bytes()).hexdigest()=='150c29c4b5207b73a8a676ce076e1402ed90c185439e096b15a8cdc9be707420'
print('PASS: native Items-state gate + exact alpha-098 label board/atlas + restored menu_cursor00')
