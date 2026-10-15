#!/usr/bin/env python3
"""Verify the exact finite Plasma body-only inverse against all published sources.

Never launches the engine or requires replacement artwork. Exact block hashes
freeze the only permitted body additions. Every original gameplay, blitter,
projectile blend, timing, RNG, HUD, menu and unrelated body byte must restore.
"""
from pathlib import Path
import argparse, hashlib, json, subprocess
ROOT=Path(__file__).resolve().parents[1]
BASE='b1a8927fb9e892f87452813010cd206e069cc413'
TREE='a31d6b78214e592e4d4a8615762854ff692d19a0'
ENVELOPE={'src/mainint.c','src/entity_draw.c','src/entity_draw.h','src/render_mirror.c','src/render_mirror.h'}
SHA=lambda b:hashlib.sha256(b).hexdigest()
BLOCKS={'entity_wrapper': {'path': 'src/entity_draw.c', 'start': '\n/* Plasma9 keeps its original twenty-phase animation and single indexed draw. */', 'end': None, 'sha256': '6dd8fc6955132424aeda96a2e14aa9c1be9919de03cf8a6fc40def1d1b5033e7'}, 'source_and_asset': {'path': 'src/render_mirror.c', 'start': "/* Plasma9 is a finite five-frame body role, separate from weapon88's blend.", 'end': 'static Asset *get_asset(', 'sha256': '7a658047e67a0b17e3dfed567d7a010986bbe404ba40adef6e6b422e063cfae1'}, 'body_route': {'path': 'src/render_mirror.c', 'start': '/* Only the existing option9/style0/charge0 normal TILE site enters here.', 'end': '/* Seven original static directions, including shared enemy58 uses.', 'sha256': '0ebbd140202b4e7a61e4d06a0104671917acbe3344989804d88b0c3ddcd55658'}}
NEW_BODY_BRANCH=b'\t\t\t\telse if (this_player->items.sidekick[i] == 9 && this_player->sidekick[i].style == 0 &&\n\t\t\t\t         this_player->sidekick[i].charge == 0 &&\n\t\t\t\t         (sprite == 224 || sprite == 243 || sprite == 262 || sprite == 281 || sprite == 300))\n\t\t\t\t\tdraw_plasma_body_sprite2(VGAScreen, x, y, spriteSheet9, sprite,\n\t\t\t\t\t                        this_player->items.sidekick[i],\n\t\t\t\t\t                        this_player->sidekick[i].style, this_player->sidekick[i].charge);\n'
ENTITY_DECL=b'/* Dedicated five-frame normal Plasma body; original indexed call always runs. */\nvoid draw_plasma_body_sprite2(SDL_Surface *,int x,int y,Sprite2_array,\n                             unsigned int index,unsigned int option,\n                             unsigned int sidekick_style,unsigned int charge);\n\n'
MIRROR_DECL=b'bool render_mirror_plasma_body(SDL_Surface *,int x,int y,Sprite2_array,unsigned int index,\n                              unsigned int option,unsigned int sidekick_style,unsigned int charge);\n'
MIRROR_MACRO=b"#define render_mirror_plasma_body(...) false\n"

def require(ok,text):
 if not ok:raise AssertionError(text)
def git(*args):return subprocess.check_output(['git','-C',str(ROOT),*args])
def once(raw,before,after,label):
 require(raw.count(before)==1,'Missing/repeated inverse: '+label)
 return raw.replace(before,after,1)
def inverse_sources(current,baseline):
 require(set(current)==set(baseline),'Production inventory changed')
 require({p for p in baseline if current[p]!=baseline[p]}==ENVELOPE,'Delta must be exactly five production files')
 restored=dict(current);additions={}
 for name,spec in BLOCKS.items():
  raw=restored[spec['path']];start=spec['start'].encode();end=spec['end'].encode()if spec['end']else None
  require(raw.count(start)==1,'Ambiguous Plasma block');a=raw.index(start);b=raw.index(end,a)if end else len(raw)
  block=raw[a:b];require(SHA(block)==spec['sha256'],'Unreviewed Plasma block: '+name);additions[name]=block;restored[spec['path']]=raw[:a]+raw[b:]
 for path,before,label in [('src/mainint.c',NEW_BODY_BRANCH,'one body branch'),('src/entity_draw.h',ENTITY_DECL,'wrapper declaration'),('src/render_mirror.h',MIRROR_DECL,'mirror declaration'),('src/render_mirror.h',MIRROR_MACRO,'classic-disabled macro')]:restored[path]=once(restored[path],before,b'',label)
 for before,after,label in [(b', ASSET_PLASMA_BODY=129',b'','role129'),(b'static Asset assets[546];',b'static Asset assets[541];','five slots'),(b'a->bank==ASSET_PLASMA_BODY?"option-plasma-bank9":',b'','prefix')]:restored['src/render_mirror.c']=once(restored['src/render_mirror.c'],before,after,label)
 for p,raw in baseline.items():require(restored[p]==raw,'Production byte inverse failed: '+p)
 return restored,additions

def finite_contract(additions):
 source=additions['source_and_asset'];wrapper=additions['entity_wrapper'];route=additions['body_route']
 for token in [b'if(!bank.data||bank.data!=spriteSheet9.data||bank.size!=spriteSheet9.size)',b'Uint8 source[12*14*2]={0};',b'decode_tile(bank,index,source,source+12*14,12,0,0)',b'option!=9||sidekick_style!=0||charge!=0',b'const unsigned int slot=541+(index-224)/19;',b'a->w=12;a->h=14;a->anchor_x=0;a->anchor_y=0;',b'if(!a->valid&&game_probe_density==8)a->valid=read_asset(a,4);']:
  require(token in source,'Missing finite source/resource contract')
 for frame,pin in [(224,'609fb9a7543c01b5'),(243,'6cfe284862651109'),(262,'64e44cd8035dee9a'),(281,'4460b75956a791ca'),(300,'0527c45d2bd85087')]:require(f'case {frame}:wanted=UINT64_C(0x{pin});break;'.encode()in source,'Missing frame identity')
 require(b'xmas'not in source,'Same-source Christmas must not be blanket rejected')
 require(source.index(b'!plasma_body_source_matches(bank,index)')<source.index(b'if(a->initialized)'),'Source guard must precede every cache lookup')
 require(wrapper.count(b'blit_sprite2(')==wrapper.count(b'render_mirror_plasma_body(')==wrapper.count(b'render_mirror_entity_end(')==1,'Exactly one attempt, original blit and end required')
 require(b' (void)render_mirror_plasma_body(target,x,y,bank,index,option,sidekick_style,charge);\n blit_sprite2(target,x,y,bank,index);\n render_mirror_entity_end();'in wrapper,'Wrapper order changed')
 require(b'x<0||x>308||y<-13||y>199'in route and b'return a?draw_asset(x,y,a,MIRROR_NORMAL,NULL):false;'in route,'Registration, compositor or row-wrap changed')
 require(not any(t in b''.join(additions.values())for t in [b'is_alive',b'moveOK',b'moveOk',b'this_player',b'rand(',b'mt_rand']), 'New drawing code contains gameplay control')

def negative_cases(current,baseline):
 result=[]
 for label,path,before,after in [('projectile blend mutation','src/sprite.c',b'#include',b'/*changed*/\n#include'),('unrelated gameplay mutation','src/mainint.c',b'#include',b'/*changed*/\n#include'),('pointer-only admission','src/render_mirror.c',b'!plasma_body_source_matches(bank,index)',b'!bank.data'),('expanded slot capacity','src/render_mirror.c',b'assets[546]',b'assets[547]'),('duplicate original blit','src/entity_draw.c',b' (void)render_mirror_plasma_body(',b' blit_sprite2(target,x,y,bank,index);\n (void)render_mirror_plasma_body('),('broadened frame admission','src/mainint.c',b'(sprite == 224 || sprite == 243 || sprite == 262 || sprite == 281 || sprite == 300)',b'(sprite >= 224)'),('Christmas blanket reject','src/render_mirror.c',b'if(!bank.data||bank.data!=spriteSheet9.data||bank.size!=spriteSheet9.size)return false;\n uint64_t wanted;\n switch(index)',b'if(xmas||!bank.data||bank.data!=spriteSheet9.data||bank.size!=spriteSheet9.size)return false;\n uint64_t wanted;\n switch(index)')]:
  mutated=dict(current);require(before in mutated[path],'Bad negative fixture');mutated[path]=mutated[path].replace(before,after,1)
  try:
   _,added=inverse_sources(mutated,baseline);finite_contract(added)
  except (AssertionError,ValueError):result.append(label)
  else:raise AssertionError('Forbidden mutation accepted: '+label)
 return result

def source_scope(root=ROOT):
 root=Path(root).resolve();require(git('rev-parse',BASE+'^{tree}').decode().strip()==TREE,'Baseline tree changed')
 names=git('ls-tree','-r','--name-only',BASE,'--','src').decode().splitlines();require(len(names)==len(set(names))==153,'Unexpected source inventory')
 actual={str(p.relative_to(root))for p in(root/'src').rglob('*')if p.is_file()or p.is_symlink()};require(actual==set(names),'Added/deleted production source')
 require(not any((root/p).is_symlink()for p in names),'Production symlink forbidden')
 baseline={p:git('show',BASE+':'+p)for p in names};current={p:(root/p).read_bytes()for p in names};restored,additions=inverse_sources(current,baseline);finite_contract(additions)
 report={'status':'PASS','baseline_commit':BASE,'baseline_tree':TREE,'production_files_checked':len(names),'production_files_changed':sorted(ENVELOPE),'whole_source_byte_inverse':True,'gameplay_state_rng_timing_limited_ammo_placement_shots_hud_shops_preserved':True,'plasma_three_piece_variable_size_blend_unchanged':True,'new_role':129,'new_slots':list(range(541,546)),'capacity_before':541,'capacity_after':546,'option':9,'style':0,'charge':0,'source_bank':9,'frame_ids':[224,243,262,281,300],'registration':{'logical':[12,14],'anchor':[0,0]},'new_blocks':{k:{'sha256':SHA(v),'bytes':len(v)}for k,v in additions.items()},'negative_scope_mutations_rejected':negative_cases(current,baseline),'source_sha256':{p:{'baseline':SHA(baseline[p]),'candidate':SHA(current[p]),'inverse':SHA(restored[p])}for p in names},'game_runs':0,'commit_or_publish_actions':0,'verification_limit':'Finite exact source inverse; runtime, art and packs require separate qualification','harness_sha256':SHA(Path(__file__).read_bytes())}
 return {'baseline':baseline,'candidate':current},report

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--out',type=Path,required=True);a=p.parse_args();out=a.out.resolve();require(ROOT not in out.parents and out!=ROOT,'Report must be outside checkout');require(not out.exists(),'Report must be new');_,report=source_scope(a.root);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n');print('PASS: 153 production files, exact five-file Plasma body-only inverse; seven forbidden mutations rejected; no game run')
if __name__=='__main__':main()
