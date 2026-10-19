#!/usr/bin/env python3
"""Small additive observer boundary; no historical asset/source fixtures."""
from pathlib import Path
from collections import Counter
import re, subprocess
ROOT=Path(__file__).resolve().parents[1]
BASE='8ffe93fa4f991163fd4e6bb6842a1a1b21a46b0d'
diff=subprocess.check_output(['git','diff','--no-ext-diff','--unified=0',BASE,'--','src/game_menu.c'],cwd=ROOT,text=True)
added=[]
for line in diff.splitlines():
 if line.startswith(('+++','---','@@','diff ','index ')):continue
 assert not line.startswith('-'),('original menu line removed',line)
 if line.startswith('+') and line[1:].strip():
  call=line[1:].strip();assert re.fullmatch(r'pregame_font_[a-z_]+\([^;]*\);',call),call
  assert not any(token in call for token in ('++','--','+=','-=','->cash')),call
  added.append(call.split('(')[0])
assert Counter(added)==Counter(pregame_font_product_begin=1,pregame_font_run_begin=8,pregame_font_run_end=8,pregame_font_product_update_begin=2,pregame_font_product_update_end=2,pregame_font_cursor_erased=1)
source=(ROOT/'src/pregame_font.c').read_text()
assert 'SF_EVENTS=40000' in source and 'if(!replay_matches())' in source
assert 'sf.count>sf.static_count' in source and 'p/SF_W>=185' in source
assert 'sf.product&&sf.run_role==PREGAME_CASH' in source
print(f'PASS: original menu lines unchanged; {len(added)} added observer calls; bounded dynamic tail; original menu draw/input/purchase lines preserved')
