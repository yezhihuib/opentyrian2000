#!/usr/bin/env python3
"""Finite ID73 source, generated-art, resource and privacy scope. No game run."""
from pathlib import Path
import argparse,hashlib,json,re,subprocess
ROOT=Path(__file__).resolve().parents[1]
BASE='1f5ab7398a6e0ed369644b50ffdf16bacdb7202d'
SHA=lambda b:hashlib.sha256(b).hexdigest()
def git(*args):return subprocess.check_output(['git','-C',str(ROOT),*args])
def extract(s,name):
 m=re.search(r'^[A-Za-z_][^\n;{}]*\b'+name+r'\([^;{}]*\)\s*\{',s,re.M);assert m,name;e=s.index('{',m.start())+1;depth=1
 while depth:depth+=(s[e]=='{')-(s[e]=='}');e+=1
 return s[m.start():e]+'\n'
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);a=p.parse_args();out=a.out.resolve();assert not out.exists()and ROOT not in out.parents and out.parent.is_dir()
 src=(ROOT/'src/render_mirror.c').read_text();old=git('show',BASE+':src/render_mirror.c').decode()
 helper='/* Sonic Wave ID73: one normal upward arch; other identities stay independent.\n * Validate current selected indices AND coverage before EVERY cold/warm lookup. */\n'+extract(src,'sonic_upward_arch_source_matches')+'\n'
 binding=''' /* Sonic Wave ID73 only; original/Christmas/diagnostic fallbacks stay classic. */
 if(bank.data==spriteSheet8.data&&layout==ENTITY_TILE&&index==73) {
  if((game_probe_density!=4&&game_probe_density!=8)||game_probe_missing||game_probe_invalid||
     game_probe_original_reference||!game_probe_assets||!sonic_upward_arch_source_matches(bank))return NULL;
  slot=548;role=8;
 }
'''
 shadow=''' /* Sonic Wave ID73 retains its original indexed shadow silhouette, origin and order. */
 if(bank.data==spriteSheet8.data&&layout==ENTITY_TILE&&index==73&&style==MIRROR_SHADOW)return false;
'''
 restored=src
 for before,after in [('static Asset assets[549];','static Asset assets[548];'),(helper,''),(binding,''),(shadow,'')]:assert restored.count(before)==1;restored=restored.replace(before,after)
 assert restored==old,'Unexpected production renderer change'
 names=git('ls-tree','-r','--name-only',BASE,'--','src').decode().splitlines();production={}
 for n in names:
  raw=(ROOT/n).read_bytes();baseline=git('show',BASE+':'+n);assert (restored.encode()if n=='src/render_mirror.c'else raw)==baseline,n;production[n]=SHA(raw)
 mpath=ROOT/'assets/hd/manifest.json';m=json.loads(mpath.read_text());rev=json.loads(mpath.read_text());family=rev.pop('player_sonic_upward_arch_v1');assert family['ids']==[73]and family['entries'][0]['slot']==548
 art=ROOT/family['source'];craw=(art/'contract.json').read_bytes();assert SHA(craw)==family['contract_sha256'];c=json.loads(craw);assert [e['id']for e in c['entries']]==[73]
 for e in c['entries']:del rev['source_pngs'][e['HDA_sha256']]
 packs={};prefixes=['assets/hd/source','assets/hd/artwork/player-sonic-six-pair-v1']
 for key in ('default_preview_pack','default_debug_pack'):
  n=m[key];assert m['packs'][n]['count']==len(m['packs'][n]['files'])==557
  del rev['packs'][n]['files']['bullet-73-8.hda'];rev['packs'][n]['count']-=1;prefixes.append('assets/hd/packs/'+n)
  assert len(list((ROOT/'assets/hd/packs'/n).glob('*.hda')))==563
  packs[key]={'listed_before':556,'listed_after':557,'physical_before':562,'physical_after':563,'unlisted_preserved':6}
 assert (json.dumps(rev,indent=2,ensure_ascii=True)+'\n').encode()==git('show',BASE+':assets/hd/manifest.json'),'Unrelated manifest change'
 preserved=0
 for line in git('ls-tree','-r',BASE,'--',*prefixes).decode().splitlines():
  meta,n=line.split('\t');mode,kind,blob=meta.split();assert kind=='blob';raw=(ROOT/n).read_bytes();assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==blob,n;preserved+=1
 tracked=[r.split('\t')for r in git('diff','--no-renames','--name-status',BASE).decode().splitlines()];assert all(r[0]in('M','A')for r in tracked),tracked
 modified={r[1]for r in tracked if r[0]=='M'};assert modified=={'src/render_mirror.c','assets/hd/manifest.json','prototype/build-hd-assets.py'},modified
 added={r[1]for r in tracked if r[0]=='A'};untracked=set(git('ls-files','--others','--exclude-standard').decode().splitlines());new=added|untracked
 artnames={'sources/generated-sonic73-r2.png','output/bullet-73-8.png','output/bullet-73-8.hda','contract.json','rebuild.py','README.md'}
 assert {str(q.relative_to(art))for q in art.rglob('*')if q.is_file()}==artnames
 required={str((art/n).relative_to(ROOT))for n in artnames}|{'prototype/build-sonic-upward-arch-art.py','prototype/test-sonic-upward-arch-scope.py','prototype/test-sonic-upward-arch-binding.py','prototype/test-sonic-upward-arch-binding.c'}
 e=c['entries'][0];required.add(m['source_pngs'][e['HDA_sha256']]['path'])
 for key in ('default_preview_pack','default_debug_pack'):required.add('assets/hd/packs/'+m[key]+'/bullet-73-8.hda')
 optional={'prototype/test-sonic-upward-arch-shots.c'}|{'docs/player-sonic-upward-arch-v1/'+n for n in ('README.md','ART_CHECK.json','SOURCE_SCOPE.json','BUILD.json','UNITS.json','RUNTIME.json','AUTHOR_REVIEW.json')}
 assert required<=new and new<=required|optional,'Unexpected/missing new files: '+str((required-new)|(new-required-optional))
 for n in new:
  assert not any(w in n.lower()for w in ('original','private','capture','reference')),n
 report={'status':'PASS','baseline':BASE,'production_tracked_src_files_checked':len(names),'only_production_file_changed':'src/render_mirror.c','renderer_sha256':SHA(src.encode()),'exact_production_inverse':True,'manifest_exact_byte_inverse':True,'old_default_pack_source_and_sonic6_art_files_preserved':preserved,'sonic6_44_art_and_bindings_unchanged':True,'remaining_original_family_ids':18,'new_files':sorted(new),'packs':packs,'frozen_art_contract_sha256':SHA(craw),'source_sha256':production,'game_runs':0,'scope':'Normal playerID73 only. Existing6/44, other18 Sonic identities, original shots/shadows/indexedblitters/gameplay/RNG preserved. Runtime/visual acceptance separate.'}
 out.write_text(json.dumps(report,indent=2)+'\n');print('PASS finite ID73 production/manifest inverse; existing6/44 and old resources exact; defaults556to557,6unlisted retained')
if __name__=='__main__':main()
