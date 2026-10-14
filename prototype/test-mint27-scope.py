#!/usr/bin/env python3
"""Verify the finite Mint27 source/art/manifest delta. Never starts the game."""
from pathlib import Path
import argparse,hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[1];BASE='a7157ccac97494ecbe3b1d54ba03a9ef42646ffd';SHA=lambda b:hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 get=lambda *args:subprocess.check_output(['git','-C',str(ROOT),*args]);before=get('show',BASE+':assets/hd/manifest.json');m=json.loads((ROOT/'assets/hd/manifest.json').read_text());restored=json.loads((ROOT/'assets/hd/manifest.json').read_text());family=restored.pop('player_mint27_one_v1');assert family['ids']==[27]and family['entries'][0]['slot']==535
 art=ROOT/family['source'];contract=(art/'contract.json').read_bytes();c=json.loads(contract);assert SHA(contract)==family['contract_sha256'];h=c['HDA_sha256'];del restored['source_pngs'][h]
 packs={}
 for key in ['default_preview_pack','default_debug_pack']:
  n=m[key];assert m['packs'][n]['count']==len(m['packs'][n]['files'])==544;del restored['packs'][n]['files']['bullet-27-8.hda'];restored['packs'][n]['count']-=1
  paths=get('ls-tree','-r','--name-only',BASE,'--','assets/hd/packs/'+n).decode().splitlines();assert len([p for p in paths if p.endswith('.hda')])==549
  packs[key]={'name':n,'listed_before':543,'listed_after':544,'physical_before':549,'physical_after':550,'unlisted_preserved':6}
 assert (json.dumps(restored,indent=2,ensure_ascii=False)+'\n').encode()==before,'Unrelated manifest change'
 changes=[line.split('\t')for line in get('diff','--no-renames','--name-status',BASE).decode().splitlines()];modified={q[1]for q in changes if q[0]=='M'};added={q[1]for q in changes if q[0]=='A'};assert modified=={'src/render_mirror.c','assets/hd/manifest.json'}and all(q[0]in {'M','A'}for q in changes),changes
 source_frozen=['sources/generated-mint27-v3.png','output/bullet-27-8.png','output/bullet-27-8.hda','contract.json','rebuild.py','README.md'];assert {str(p.relative_to(art))for p in art.rglob('*')if p.is_file()}==set(source_frozen)
 untracked=set(get('ls-files','--others','--exclude-standard').decode().splitlines());new=added|untracked;allowed={str((art/n).relative_to(ROOT))for n in source_frozen}|{'prototype/build-mint27-art.py','prototype/test-mint27-binding.py','prototype/test-mint27-binding.c','prototype/test-mint27-scope.py'}|{m['packs'][m['default_preview_pack']]['files']['bullet-27-8.hda']['source_png']}|{'assets/hd/packs/'+m[k]+'/bullet-27-8.hda'for k in ['default_preview_pack','default_debug_pack']}
 allowed.add('docs/player-mint27-one-v1/README.md')
 assert new==allowed,'Unexpected new files: '+str(new^allowed)
 report={'status':'PASS','baseline':BASE,'manifest_byte_inverse':True,'only_production_file_changed':'src/render_mirror.c','tracked_delta':changes,'new_files':sorted(new),'new_file_states':{'tracked_added':sorted(added),'untracked':sorted(untracked)},'frozen_art_sha256':{n:SHA((art/n).read_bytes())for n in source_frozen},'packs':packs,'game_runs':0};out=a.out.resolve();assert not out.exists()and ROOT not in out.parents;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n');print('PASS finite source/art/manifest scope; old manifest exact inverse; two defaults543→544; six unlisted files preserved')
if __name__=='__main__':main()
