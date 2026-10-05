from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
p=json.loads((R/'config/patches.json').read_text())
by={x['name']:x for x in p}
assert 'canvas_backdrop' not in by
assert 'queued_foreground' not in by
assert by['mode_backdrop_dual']['address']=='0x43fe30' and by['mode_backdrop_single']['address']=='0x44015c'
assert by['file_select_backdrop']['address']=='0x419820'
assert by['file_select_backdrop']['assembly']=='bl tos_file_select_backdrop'
assert by['common_backdrop']['address']=='0x41ee2c'
assert by['common_backdrop']['assembly']=='bl tos_common_backdrop'
for n in ['file_fade_producer_a','file_fade_producer_b','file_fade_producer_c','file_fade_producer_d']:
    assert by[n]['assembly']=='bl Presentation_FadePrimitive'
s=(R/'source/frontend/file_select.c').read_text()
assert 'RETAIL_SAVE->gameMode==2' in s
assert 'FILE_SELECT_PASS_TOP' in s and 'FILE_SELECT_PASS_LOWER' in s
assert 'Retail_Submit(renderer,0x400u)' in s
assert 'Retail_Submit(renderer,0x401u)' in s
pres=(R/'source/render/presentation.c').read_text()
assert 'FileSelect_SubmitBottomAndMaybeReplay' in pres
hooks=(R/'source/patch/hooks.s').read_text()
assert 'tos_file_select_backdrop:' in hooks and 'ldr ip,=0x002FFF7C' in hooks
assert 'tos_common_backdrop:' in hooks and 'blx r5' in hooks
assert hooks.count('bl Presentation_SuppressBackdrop')==2
assert 'Presentation_Backdrop' not in pres
print('frontend_1_1_7_contracts: PASS')
