#!/usr/bin/env python3
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
p=(ROOT/'source/render/presentation.c').read_text()
patches={x['name']:x for x in json.loads((ROOT/'config/patches.json').read_text())}
for n in ('queued_foreground','canvas_backdrop','common_backdrop','mode_backdrop_dual','mode_backdrop_single'):
    assert n in patches,n
assert 'file_preview_scene' not in patches
assert 'file_rotating_link' not in patches
assert 'player_draw_hidden' not in p
assert 'preview_object_suppressed' not in p
assert 'projected_backdrop_suppressed' not in p
assert 'mode_common_bg01_suppressed' not in p
assert 'foregroundFrame && lowerPass && projecting' in p
assert '0x003339E8u' in p and 'queued_400wide' in p
assert '0x005C0BA8u,3,rgba,10' in p
print('PASS: 1.1.5 recovery uses the intact promoted-menu path with no speculative Link/container suppression')
