from pathlib import Path
import json
r=Path(__file__).resolve().parents[1]
p=(r/'source/render/presentation.c').read_text()
d={x['name']:x for x in json.loads((r/'config/patches.json').read_text())}
# 1.1.11 supersedes the tail flag with exact producer allocations.
assert 'modeBackdropTail' not in p
assert 'PASS_NATIVE_TOP' in p and 'PASS_NATIVE_LOWER' in p and 'PASS_PROMOTED_LOWER' in p
assert 'promoted_pass() && node==modeBackdropNode' in p
assert 'forget_queued_producers();' in p
assert 'Retail_Viewport(0,0,promotedStereo,400);' in p
assert 'Retail_Viewport(0,40,promotedStereo,320);' in p
assert d['frontend_exact_queued_draw']['address']=='0x2feaa4'
assert d['file_select_backdrop']['address']=='0x419820'
assert d['common_backdrop']['address']=='0x41ee2c'
assert d['mode_backdrop_dual']['address']=='0x43fe30'
assert d['mode_backdrop_single']['address']=='0x44015c'
print('frontend 1.1.10 contracts: PASS')
