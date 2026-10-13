#!/usr/bin/env python3
"""Create private profiles/resources, without launching an engine."""
import argparse,json,pathlib,shutil
p=argparse.ArgumentParser();p.add_argument('--resources',type=pathlib.Path,required=True);p.add_argument('--out',type=pathlib.Path,required=True);a=p.parse_args()
if a.out.exists():raise SystemExit('Use a fresh output directory.')
for side in ['reference','candidate']:
 d=a.out/side;(d/'config/opentyrian2000').mkdir(parents=True);(d/'assets').mkdir();(d/'output').mkdir()
 (d/'config/opentyrian2000/opentyrian.cfg').write_text('section video\n\titem fullscreen -1\n\titem scaler "2x"\n\titem scaling_mode "Integer"\n')
 if side=='candidate':
  for name in ['large','medium','tiny']:shutil.copy2(a.resources/f'settings-font-{name}-v1.hda',d/'assets')
(a.out/'PREPARATION.json').write_text(json.dumps({'game_launches':0,'source_gate':'PENDING','initial_config':'native2x/window/Integer; original defaults otherwise','user_profile_access':'none'},indent=2)+'\n')
print(a.out)
