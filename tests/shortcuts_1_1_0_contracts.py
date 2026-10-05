#!/usr/bin/env python3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
bridge=(ROOT/'source/input/bridge.c').read_text()
short=(ROOT/'source/input/shortcuts.h').read_text()
hud=(ROOT/'source/hud/hud.c').read_text()
glyphs=(ROOT/'config/glyphs.json').read_text()
assert 'if(edges & BUTTON_UP) return SHORTCUT_ITEMS;' in short
assert 'if(edges & BUTTON_DOWN) return SHORTCUT_GEAR;' in short
assert 'if(edges & BUTTON_START) return SHORTCUT_PAUSE;' in short
assert 'if(edges & BUTTON_SELECT) return SHORTCUT_MAP;' in short
assert 'if(edges & BUTTON_RIGHT) return SHORTCUT_OCARINA;' in short
assert 'switch(Shortcut_FromEdges(edges))' in bridge
assert 'physical.pad.held&SHORTCUT_VIEW_BUTTON' in bridge
assert 'GLYPH_ITEMS' in hud and 'GLYPH_GEAR' in hud
assert '"ITEMS"' in glyphs and '"GEAR"' in glyphs
assert 'GLYPH_MAP' not in hud and 'GLYPH_PAUSE' not in hud
print('1.1.1 shortcut contracts: PASS')
