#!/usr/bin/env python3
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
p=(ROOT/'source/render/presentation.c').read_text()
patches={x['name']:x for x in json.loads((ROOT/'config/patches.json').read_text())}
for n in ('queued_foreground','canvas_backdrop','common_backdrop','mode_backdrop_dual','mode_backdrop_single'):
    assert n in patches,n
assert 'file_rotating_link' not in patches
assert 'foregroundFrame && lowerPass && projecting' in p
assert 'TOS_FILE_LINK player_draw_hidden' in p
assert 'player->type!=ACTORTYPE_PLAYER' in p
assert 'player->draw=0' in p and 'hiddenTitlePlayer->draw=hiddenTitleDraw' in p
assert '0x003339E8u' in p and 'queued_400wide' in p
assert '0x005C0BA8u,3,rgba,10' in p
assert 'Presentation_AdvanceFrontendFade(fade)' in p
print('PASS: 1.1.3 live-sky backdrops, guarded title-player suppression, and native 400-wide frontend fade lane')
