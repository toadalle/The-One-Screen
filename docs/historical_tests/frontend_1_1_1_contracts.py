#!/usr/bin/env python3
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
p=(ROOT/'source/render/presentation.c').read_text()
patches=json.loads((ROOT/'config/patches.json').read_text())
assert 'OWNER_FILESELECT && f.owner!=OWNER_MODESELECT' in p
assert 'Presentation_FileModelTail' in p and '0x002FB934u' in p
assert 'Presentation_AdvanceFrontendFade' in p
assert 'a=(s16)(a+8)' in p and 'a=(s16)(a-8)' in p
assert 'titleFrontend=(RETAIL_SAVE->gameMode==1 && !Retail_Gameplay())' in p
q=next(x for x in patches if x['name']=='file_rotating_link')
assert q['address'].lower()=='0x41f338' and q['expected']=='7d71fbea'
assert q['assembly']=='b Presentation_FileModelTail'
print('1.1.1 frontend cleanup contracts: PASS')
