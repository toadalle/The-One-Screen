from pathlib import Path
import json
r=Path(__file__).resolve().parents[1]
p=(r/'source/render/presentation.c').read_text()
d={x['name']:x for x in json.loads((r/'config/patches.json').read_text())}
assert 'titleFrontendLatched' in p
assert 'foreground_for_frame' in p
assert 'f.owner==OWNER_MODESELECT) titleFrontendLatched=1' in p
assert 'RETAIL_SAVE->gameMode!=1 || Retail_Gameplay()' in p
assert 'TOS_FRONTEND_BG mode_transition_hold' in p
assert 'projecting=0;\n    lowerPass=0;' in p
assert 'foregroundFrame && lowerPass && projecting' in p
assert 'PASS_PROMOTED_LOWER' in p and 'modeBackdropNode' in p
assert d['file_select_backdrop']['address']=='0x419820'
assert d['common_backdrop']['address']=='0x41ee2c'
assert d['mode_backdrop_dual']['address']=='0x43fe30'
assert d['mode_backdrop_single']['address']=='0x44015c'
print('frontend 1.1.9 contracts: PASS')
