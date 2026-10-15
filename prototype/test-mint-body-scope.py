#!/usr/bin/env python3
"""Exact finite three-frame Mint body production-source inverse; no engine run.

All 153 baseline src files must be restored byte-for-byte by removing the four
new functions, their declarations, one finite body branch, role/prefix/slots.
Existing Marlo, Talon, Mint projectile, original blitters, palette/compositor,
and every other production function remain exactly baseline bytes.
"""
from pathlib import Path
import argparse, hashlib, json, subprocess
ROOT=Path(__file__).resolve().parents[1]
BASE='8b71966b59315b7ee67163e160925e0d60a0ae39'
TREE='967e74f99f07e31d3e5d631744de9d20756303dd'
ENVELOPE={'src/mainint.c','src/entity_draw.c','src/entity_draw.h','src/render_mirror.c','src/render_mirror.h'}
SHA=lambda b:hashlib.sha256(b).hexdigest()
BLOCKS={'entity_wrapper': {'path': 'src/entity_draw.c', 'start': b'\n/* Mint16 keeps its original phase, placement and single indexed draw. */', 'end': None, 'functions': ['draw_mint_body_sprite2'], 'sha256': 'b7854a63a9208fb660b3502d007f1f26111dd5cde4305e01cd163cffa6796a9a'}, 'source_and_asset': {'path': 'src/render_mirror.c', 'start': b'/* Mint16 is a finite body role, separate from its bank8 projectile and Marlo.', 'end': b'static Asset *get_asset(', 'functions': ['mint_body_source_matches', 'mint_body_asset'], 'sha256': 'b215b134787dab4f7603467e8295117c7829a5ce9f5078cc7d2e1c76271d81d5'}, 'body_route': {'path': 'src/render_mirror.c', 'start': b'/* Only the existing option16/style3/charge0 normal TILE site enters here.', 'end': b'/* Seven original static directions, including shared enemy58 uses.', 'functions': ['render_mirror_mint_body'], 'sha256': 'bbf9457944273de782c686ab3aac034e53503fb1dfd8778f620494d38f86b399'}}
NEW_BODY_BRANCH=b'\t\t\t\telse if (this_player->items.sidekick[i] == 16 && this_player->sidekick[i].style == 3 &&\n\t\t\t\t         this_player->sidekick[i].charge == 0 && (sprite == 112 || sprite == 131 || sprite == 150))\n\t\t\t\t\tdraw_mint_body_sprite2(VGAScreen, x, y, spriteSheet9, sprite,\n\t\t\t\t\t                      this_player->items.sidekick[i],\n\t\t\t\t\t                      this_player->sidekick[i].style, this_player->sidekick[i].charge);\n'
ENTITY_DECL=b'/* Dedicated three-phase normal Mint body; original indexed call always runs. */\nvoid draw_mint_body_sprite2(SDL_Surface *,int x,int y,Sprite2_array,\n                           unsigned int index,unsigned int option,\n                           unsigned int sidekick_style,unsigned int charge);\n\n'
MIRROR_DECL=b'bool render_mirror_mint_body(SDL_Surface *,int x,int y,Sprite2_array,unsigned int index,\n                            unsigned int option,unsigned int sidekick_style,unsigned int charge);\n'
MIRROR_MACRO=b'#define render_mirror_mint_body(...) false\n'

def require(ok, explanation):
 if not ok:raise AssertionError(explanation)
def git(*args):return subprocess.check_output(['git','-C',str(ROOT),*args])
def replace_once(raw,before,after,label):
 require(raw.count(before)==1,'Missing/repeated finite inverse: '+label)
 return raw.replace(before,after,1)
def inverse_sources(current,baseline):
 require(set(current)==set(baseline),'Production inventory changed')
 changed={p for p in baseline if current[p]!=baseline[p]}
 require(changed==ENVELOPE,'Production delta must be exactly five files: '+str(sorted(changed)))
 restored=dict(current);additions={}
 for name,spec in BLOCKS.items():
  raw=restored[spec['path']];require(raw.count(spec['start'])==1,'Ambiguous Mint addition')
  start=raw.index(spec['start']);end=len(raw)if spec['end']is None else raw.index(spec['end'],start)
  addition=raw[start:end];require(SHA(addition)==spec['sha256'],'Unreviewed finite Mint block: '+name)
  additions[name]=addition;restored[spec['path']]=raw[:start]+raw[end:]
 restored['src/mainint.c']=replace_once(restored['src/mainint.c'],NEW_BODY_BRANCH,b'','one Mint body branch')
 restored['src/entity_draw.h']=replace_once(restored['src/entity_draw.h'],ENTITY_DECL,b'','Mint wrapper declaration')
 restored['src/render_mirror.h']=replace_once(restored['src/render_mirror.h'],MIRROR_DECL,b'','Mint mirror declaration')
 restored['src/render_mirror.h']=replace_once(restored['src/render_mirror.h'],MIRROR_MACRO,b'','classic-disabled macro')
 for before,after,label in [(b', ASSET_MINT_BODY=127',b'','role127'),(b'static Asset assets[540];',b'static Asset assets[537];','three slots'),(b'a->bank==ASSET_MINT_BODY?"option-mint-bank9":',b'','resource prefix')]:
  restored['src/render_mirror.c']=replace_once(restored['src/render_mirror.c'],before,after,label)
 for p,raw in baseline.items():require(restored[p]==raw,'Byte-exact production inverse failed: '+p)
 return restored,additions

def finite_contract(current,additions):
 source=additions['source_and_asset'];wrapper=additions['entity_wrapper'];route=additions['body_route']
 for value in [b'if(xmas||!bank.data||bank.data!=spriteSheet9.data||bank.size!=spriteSheet9.size)',b'Uint8 source[12*14*2]={0};',b'decode_tile(bank,index,source,source+12*14,12,0,0)',b'case 112:wanted=UINT64_C(0xadcb30ca719db2e6)',b'case 131:wanted=UINT64_C(0xadf9398495b924ef)',b'case 150:wanted=UINT64_C(0xd692d598a54a058f)',b'default:return false;',b'option!=16||sidekick_style!=3||charge!=0',b'const unsigned int slot=index==112?537:index==131?538:539;',b'a->initialized=true;a->bank=ASSET_MINT_BODY;a->index=(int)index;',b'a->w=12;a->h=14;a->anchor_x=0;a->anchor_y=0;',b'if(!a->valid&&game_probe_density==8)a->valid=read_asset(a,4);']:
  require(value in source,'Missing finite source/resource contract')
 require(source.index(b'!mint_body_source_matches(bank,index)')<source.index(b'if(a->initialized)'),'Source must be checked before every cache lookup')
 require(wrapper.count(b'blit_sprite2(')==wrapper.count(b'render_mirror_mint_body(')==wrapper.count(b'render_mirror_entity_end(')==1,'Wrapper requires one HD attempt, original blit and lease end')
 require(b' (void)render_mirror_mint_body(target,x,y,bank,index,option,sidekick_style,charge);\n blit_sprite2(target,x,y,bank,index);\n render_mirror_entity_end();'in wrapper,'Original blit/order changed')
 require(b'return a?draw_asset(x,y,a,MIRROR_NORMAL,NULL):false;'in route and b'x<0||x>308||y<-13||y>199'in route,'Original registration, compositor or row-wrap fallback changed')
 require(current['src/mainint.c'].count(b'draw_mint_body_sprite2(')==1,'Only one Mint body call site permitted')
 require(not any(v in b''.join(additions.values())for v in [b'is_alive',b'moveOK',b'moveOk',b'this_player',b'rand(',b'mt_rand']),'Drawing additions contain gameplay control')

def negative_cases(current,baseline):
 cases=[]
 mutations=[('original blitter changed','src/sprite.c',b'#include',b'/*changed*/\n#include'),('unrelated mainint changed','src/mainint.c',b'#include',b'/*changed*/\n#include'),('pointer-only admission','src/render_mirror.c',b'!mint_body_source_matches(bank,index)',b'!bank.data'),('unbounded slot capacity','src/render_mirror.c',b'assets[540]',b'assets[541]'),('extra original blit','src/entity_draw.c',b' (void)render_mirror_mint_body(target,x,y,bank,index,option,sidekick_style,charge);',b' blit_sprite2(target,x,y,bank,index);\n (void)render_mirror_mint_body(target,x,y,bank,index,option,sidekick_style,charge);'),('broadened body branch','src/mainint.c',b'(sprite == 112 || sprite == 131 || sprite == 150)',b'(sprite >= 112)')]
 for label,path,before,after in mutations:
  m=dict(current);require(before in m[path],'Invalid scope fixture: '+label);m[path]=m[path].replace(before,after,1)
  try:
   _,additions=inverse_sources(m,baseline);finite_contract(m,additions)
  except (AssertionError,ValueError):cases.append(label)
  else:raise AssertionError('Forbidden mutation accepted: '+label)
 return cases

def source_scope(root=ROOT):
 root=Path(root).resolve();require(git('rev-parse',BASE+'^{tree}').decode().strip()==TREE,'Baseline tree changed')
 names=git('ls-tree','-r','--name-only',BASE,'--','src').decode().splitlines();require(len(names)==len(set(names))==153,'Unexpected source inventory')
 actual={str(p.relative_to(root))for p in(root/'src').rglob('*')if p.is_file()or p.is_symlink()};require(actual==set(names),'Added/deleted production source')
 require(not any((root/p).is_symlink()for p in names),'Production symlink forbidden')
 baseline={p:git('show',BASE+':'+p)for p in names};current={p:(root/p).read_bytes()for p in names}
 restored,additions=inverse_sources(current,baseline);finite_contract(current,additions)
 report={'status':'PASS','baseline_commit':BASE,'baseline_tree':TREE,'production_files_checked':len(names),'production_files_changed':sorted(ENVELOPE),'whole_source_byte_inverse':True,'mainint_exact_inverse_after_one_finite_body_branch_removal':True,'original_gameplay_state_rng_shots_hud_shops_orbits_preserved':True,'marlo_talon_mint_projectile_get_asset_compositor_pixel_bridge_decoder_blitters_preserved':True,'new_role':127,'new_slots':[537,538,539],'capacity_before':537,'capacity_after':540,'option':16,'style':3,'charge':0,'source_bank':9,'active_indices':[112,131,150],'registration':{'logical':[12,14],'anchor':[0,0]},'new_blocks':{k:{'sha256':SHA(v),'bytes':len(v)}for k,v in additions.items()},'negative_scope_mutations_rejected':negative_cases(current,baseline),'source_sha256':{p:{'baseline':SHA(baseline[p]),'candidate':SHA(current[p]),'inverse':SHA(restored[p])}for p in names},'source_only_audit':True,'game_runs':0,'commit_or_publish_actions':0,'verification_limit':'Static finite inverse and six bounded negative mutations; runtime/asset pack preservation checked separately','harness_sha256':SHA(Path(__file__).read_bytes())}
 return {'baseline':baseline,'candidate':current},report

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--out',type=Path,required=True);a=p.parse_args();out=a.out.resolve();require(ROOT not in out.parents and out!=ROOT,'Report must be outside checkout');require(not out.exists(),'Report must be a new file');_,report=source_scope(a.root);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n');print('PASS: all 153 baseline production files; exact five-file Mint-only inverse; six forbidden mutations rejected; no game run')
if __name__=='__main__':main()
