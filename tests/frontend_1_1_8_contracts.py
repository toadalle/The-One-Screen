from pathlib import Path
import json
r=Path(__file__).resolve().parents[1]
p=(r/'source/render/presentation.c').read_text()
h=(r/'source/patch/hooks.s').read_text()
d=json.loads((r/'config/patches.json').read_text())
by={x['name']:x for x in d}
assert 'Presentation_SuppressBackdrop' in p
assert 'FileSelect_SuppressTopBackdrop()' in p
assert 'foregroundFrame && lowerPass && projecting' in p
assert 'TOS_FRONTEND_BG projected_backdrop_suppressed' in p
assert 'promoted_pass() && node==modeBackdropNode' in p
assert h.count('bl Presentation_SuppressBackdrop') == 2
assert by['file_select_backdrop']['address']=='0x419820'
assert by['common_backdrop']['address']=='0x41ee2c'
assert by['mode_backdrop_dual']['address']=='0x43fe30'
assert by['mode_backdrop_single']['address']=='0x44015c'
assert 'canvas_backdrop' not in by
assert 'file_preview_scene' not in by
print('frontend 1.1.8 contracts: PASS')
