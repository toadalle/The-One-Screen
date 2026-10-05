from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
p=(ROOT/'source/render/presentation.c').read_text()
patches={x['name'] for x in json.loads((ROOT/'config/patches.json').read_text())}
assert 'file_rotating_link' not in patches
assert 'queued_foreground' not in patches
assert 'canvas_backdrop' not in patches
assert 'common_backdrop' not in patches
assert 'mode_backdrop_dual' not in patches
assert 'mode_backdrop_single' not in patches
assert 'RETAIL_SAVE->gameMode==1 || RETAIL_SAVE->gameMode==2' in p
assert 'Presentation_AdvanceFrontendFade(fade);' in p
assert 'TOS_FRONTEND_FADE state_only_fullwidth' in p
assert 'Presentation_FileModelTail' not in p
assert 'Presentation_ModeBackdrop' not in p
assert 'Presentation_Backdrop' not in p
assert 'Presentation_QueuedNode' not in p
print('PASS: 1.1.2 keeps native selector/backdrop paths and suppresses frontend-only fade rectangle')
