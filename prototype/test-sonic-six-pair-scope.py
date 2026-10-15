#!/usr/bin/env python3
"""Exact finite Sonic6/44 production, generated-art and manifest scope. No game run."""
from pathlib import Path
import argparse,hashlib,json,re,subprocess
ROOT=Path(__file__).resolve().parents[1];BASE='0ecfef98756fd6e37999d79eb13d5c740d988a7b'
SHA=lambda b:hashlib.sha256(b).hexdigest()
def git(*args):return subprocess.check_output(['git','-C',str(ROOT),*args])
def extract(s,n):
 m=re.search(r'^[A-Za-z_][^\n;{}]*\b'+n+r'\([^;{}]*\)\s*\{',s,re.M);assert m,n;e=s.index('{',m.start())+1;d=1
 while d:d+=(s[e]=='{')-(s[e]=='}');e+=1
 return s[m.start():e]+'\n'
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);a=p.parse_args();out=a.out.resolve();assert not out.exists()and ROOT not in out.parents and out.parent.is_dir()
 src=(ROOT/'src/render_mirror.c').read_text();old=git('show',BASE+':src/render_mirror.c').decode()
 comment='/* Sonic Wave pilot: two static normal player heads, not the full21-ID family.\n * Validate current selected indices AND coverage before EVERY cold/warm lookup. */\n'
 helper=comment+extract(src,'sonic_six_pair_member')+'\n'+extract(src,'sonic_six_pair_source_matches')+'\n'
 binding=''' /* Sonic Wave pilot6/44 only; original/Christmas/diagnostic fallbacks stay classic. */
 if(bank.data==spriteSheet8.data&&layout==ENTITY_TILE&&sonic_six_pair_member(index)>=0) {
  if((game_probe_density!=4&&game_probe_density!=8)||game_probe_missing||game_probe_invalid||
     game_probe_original_reference||!game_probe_assets||!sonic_six_pair_source_matches(bank,index))return NULL;
  slot=546+sonic_six_pair_member(index);role=8;
 }
'''
 shadow=''' /* Sonic Wave6/44 retain original indexed shadow silhouettes, origin and order. */
 if(bank.data==spriteSheet8.data&&layout==ENTITY_TILE&&sonic_six_pair_member(index)>=0&&style==MIRROR_SHADOW)return false;
'''
 restored=src
 for before,after in [('static Asset assets[548];','static Asset assets[546];'),(helper,''),(binding,''),(shadow,'')]:assert restored.count(before)==1;restored=restored.replace(before,after)
 assert restored==old,'Unexpected production renderer change'
 names=git('ls-tree','-r','--name-only',BASE,'--','src').decode().splitlines();production={}
 for n in names:
  raw=(ROOT/n).read_bytes();baseline=git('show',BASE+':'+n);assert (restored.encode()if n=='src/render_mirror.c'else raw)==baseline,n;production[n]=SHA(raw)
 manifest_raw=git('show',BASE+':assets/hd/manifest.json');m=json.loads((ROOT/'assets/hd/manifest.json').read_text());rev=json.loads((ROOT/'assets/hd/manifest.json').read_text());family=rev.pop('player_sonic_six_pair_v1');assert family['ids']==[6,44]and [q['slot']for q in family['entries']]==[546,547]
 cpath=ROOT/family['source']/'contract.json';craw=cpath.read_bytes();assert SHA(craw)==family['contract_sha256'];c=json.loads(craw);assert [e['id']for e in c['entries']]==[6,44]
 for e in c['entries']:del rev['source_pngs'][e['HDA_sha256']]
 packs={};prefixes=['assets/hd/source']
 for key in ('default_preview_pack','default_debug_pack'):
  n=m[key];assert m['packs'][n]['count']==len(m['packs'][n]['files'])==556
  for i in (6,44):del rev['packs'][n]['files'][f'bullet-{i}-8.hda']
  rev['packs'][n]['count']-=2;prefixes.append('assets/hd/packs/'+n)
  physical=len(list((ROOT/'assets/hd/packs'/n).glob('*.hda')));assert physical==562
  packs[key]={'listed_before':554,'listed_after':556,'physical_before':560,'physical_after':562,'unlisted_preserved':6}
 assert (json.dumps(rev,indent=2,ensure_ascii=True)+'\n').encode()==manifest_raw,'Unrelated manifest change'
 preserved=0
 for line in git('ls-tree','-r',BASE,'--',*prefixes).decode().splitlines():
  meta,n=line.split('\t');mode,kind,blob=meta.split();assert kind=='blob';raw=(ROOT/n).read_bytes();assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==blob,n;preserved+=1
 tracked=[r.split('\t')for r in git('diff','--no-renames','--name-status',BASE).decode().splitlines()];assert all(r[0]in('M','A')for r in tracked),tracked
 modified={r[1]for r in tracked if r[0]=='M'};assert modified=={'src/render_mirror.c','assets/hd/manifest.json','prototype/build-hd-assets.py'},modified
 added={r[1]for r in tracked if r[0]=='A'};untracked=set(git('ls-files','--others','--exclude-standard').decode().splitlines());new=added|untracked
 art=ROOT/family['source'];artnames={'sources/generated-sonic6-r5.png','output/bullet-6-8.png','output/bullet-6-8.hda','output/bullet-44-8.png','output/bullet-44-8.hda','contract.json','rebuild.py','README.md'}
 assert {str(q.relative_to(art))for q in art.rglob('*')if q.is_file()}==artnames
 required={str((art/n).relative_to(ROOT))for n in artnames}|{'prototype/build-sonic-six-pair-art.py','prototype/test-sonic-six-pair-scope.py','prototype/test-sonic-six-pair-binding.py','prototype/test-sonic-six-pair-binding.c','prototype/test-sonic-six-pair-shots.c'}
 for e in c['entries']:
  required.add(m['source_pngs'][e['HDA_sha256']]['path'])
  for key in ('default_preview_pack','default_debug_pack'):required.add('assets/hd/packs/'+m[key]+f'/bullet-{e["id"]}-8.hda')
 optional={'prototype/test-sonic-six-pair-original.py','prototype/test-sonic-six-pair-original.c','docs/player-sonic-six-pair-v1/README.md','docs/player-sonic-six-pair-v1/ART_CHECK.json','docs/player-sonic-six-pair-v1/SOURCE_SCOPE.json','docs/player-sonic-six-pair-v1/BUILD.json','docs/player-sonic-six-pair-v1/UNITS.json','docs/player-sonic-six-pair-v1/RUNTIME.json','docs/player-sonic-six-pair-v1/AUTHOR_REVIEW.json'}
 assert required<=new and new<=required|optional,'Unexpected/missing new files: '+str((required-new)|(new-required-optional))
 report={'status':'PASS','baseline':BASE,'production_tracked_src_files_checked':len(names),'production_code_files_checked':sum(Path(n).suffix in {'.c','.h','.inc'}for n in names),'only_production_file_changed':'src/render_mirror.c','renderer_sha256':SHA(src.encode()),'exact_production_inverse':True,'manifest_exact_byte_inverse':True,'old_default_pack_and_source_files_preserved':preserved,'new_files':sorted(new),'packs':packs,'frozen_art_contract_sha256':SHA(craw),'source_sha256':production,'game_runs':0,'scope':'Only normal player6/44 pilot. Other19 Sonic identities, shots, RNG and gameplay unchanged. Runtime/visual checks separate.'}
 out.write_text(json.dumps(report,indent=2)+'\n');print('PASS finite Sonic6/44 source and manifest inverse; old pack/source bytes preserved; defaults554to556, six unlisted retained')
if __name__=='__main__':main()
