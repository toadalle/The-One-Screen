"""1.0.6 source/retail seam contract tests, not emulator graphics validation."""
import json,pathlib,sys
root=pathlib.Path(__file__).resolve().parents[1]
retail=pathlib.Path(sys.argv[1]);code=(retail/'code.bin').read_bytes()
patches=json.loads((root/'config/patches.json').read_text())
assert len(patches)==45
lookup={p['name']:p for p in patches}
for name,addr in [('native_item_strip',0x41EE44),('ocarina_native_draw',0x41EE74),('lower_fade',0x419868)]:
    p=lookup[name];assert int(p['address'],16)==addr
    assert code[addr-0x100000:addr-0x100000+p['size']]==bytes.fromhex(p['expected'])
ocarina=(root/'source/frontend/ocarina.c').read_text()
assert 'if(playState(state))Scene_Draw(&chrome)' in ocarina
assert 'if(playState(state)) {' in ocarina
assert 'nativeLabels' in ocarina  # 1.0.8 single custom native lettering path
assert 'letterBackup' not in ocarina
assert ocarina.count('0x0036759Cu')==1
hud=(root/'source/hud/hud.c').read_text()
assert 'matches[i]!=1' in hud and 'TOS_ITEM_UV 0000' in hud
assert 'nativeItemLabels' in hud and 'Scene_Upload(&nativeItemLabels)' in hud
presentation=(root/'source/render/presentation.c').read_text()
assert 'node==lowerFadeNode' in presentation
assert 'before<24' in presentation
print('PASS: native seams, bounded inventory guard, transparent full glyphs and one native label scene and captured fade skip')
