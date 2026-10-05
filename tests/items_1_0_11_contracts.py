"""1.0.11: alpha-098 Xbox item lanes are semantic, not label-only."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
bridge=(ROOT/'source/input/bridge.c').read_text()
hud=(ROOT/'source/hud/hud.c').read_text()
policy=(ROOT/'source/input/policy.h').read_text()
assert 'if(f.owner!=OWNER_OCARINA)remapGameplayFace(p);' in bridge
assert 'INPUT_GAMEPLAY' in policy and '1u<<10,1u<<11' in policy
assert 'buttonItems[2],cx[0],cy[0],2' in hud
assert 'buttonItems[1],cx[1],cy[1],1' in hud
assert 'No XY input or item-lane swap' not in hud
print('1.0.11 item mapping contracts OK')
