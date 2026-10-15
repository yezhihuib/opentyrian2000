#!/usr/bin/env python3
"""Exact finite FrontBlaster option20 QUAD body production-source inverse; no engine run.

All 153 baseline src files must be restored byte-for-byte by removing the four
new functions, their declarations, one finite body branch, role/prefix/slots.
Existing Marlo, Talon, Mint body/projectile, original blitters, palette/compositor,
and every other production function remain exactly baseline bytes.
"""
from pathlib import Path
import argparse, hashlib, json, subprocess
ROOT=Path(__file__).resolve().parents[1]
BASE='d755b79c890d140e294a683664259d6833a3ca6f'
TREE='481455fc0deaf7cf93a7fdf3521b3d4e8618e9ad'
ENVELOPE={'src/mainint.c','src/entity_draw.c','src/entity_draw.h','src/render_mirror.c','src/render_mirror.h'}
SHA=lambda b:hashlib.sha256(b).hexdigest()
BLOCKS={'entity_wrapper': {'path': 'src/entity_draw.c', 'start': b'\n/* FrontBlaster20 keeps the original complete QUAD and four indexed tile calls. */', 'end': None, 'functions': ['draw_frontblaster_body_sprite2'], 'sha256': 'd00d652400c24a5d1e08bd16e9c3c4b6f2a42ffceef1c991c3cd06108b0d47b4'}, 'source_and_asset': {'path': 'src/render_mirror.c', 'start': b'/* FrontBlaster20 is one complete QUAD, separate from shared83 options22/26.', 'end': b'static Asset *get_asset(', 'functions': ['frontblaster_body_source_matches', 'frontblaster_body_asset'], 'sha256': 'e07797a2de2781693535a3cc5caeef55e3e458eb8a9fd3027157ebb78eef260e'}, 'body_route': {'path': 'src/render_mirror.c', 'start': b'/* Only the existing option20/style2/charge0 QUAD site enters this route.', 'end': b'/* Seven original static directions,', 'functions': ['render_mirror_frontblaster_body'], 'sha256': '757e88e582bfdfa8d0ad0cf36abe6529cf1cd114525a3c0ecae35fab7a3ec422'}}
NEW_BODY_BRANCH=b'\t\t\t\tif (this_player->items.sidekick[i] == 20 && this_player->sidekick[i].style == 2 &&\n\t\t\t\t    this_player->sidekick[i].charge == 0 && sprite == 83)\n\t\t\t\t\tdraw_frontblaster_body_sprite2(VGAScreen, x - 6, y, spriteSheet10, sprite,\n\t\t\t\t\t                              this_player->items.sidekick[i],\n\t\t\t\t\t                              this_player->sidekick[i].style, this_player->sidekick[i].charge);\n\t\t\t\telse if (this_player->sidekick[i].style == 1 || this_player->sidekick[i].style == 2)'
OLD_BODY_BRANCH=b'\t\t\t\tif (this_player->sidekick[i].style == 1 || this_player->sidekick[i].style == 2)'
ENTITY_DECL=b'/* Dedicated static FrontBlaster QUAD; the original four-tile draw always runs. */\nvoid draw_frontblaster_body_sprite2(SDL_Surface *,int x,int y,Sprite2_array,\n                                   unsigned int index,unsigned int option,\n                                   unsigned int sidekick_style,unsigned int charge);\n\n'
MIRROR_DECL=b'bool render_mirror_frontblaster_body(SDL_Surface *,int x,int y,Sprite2_array,unsigned int index,\n                                    unsigned int option,unsigned int sidekick_style,unsigned int charge);\n'
MIRROR_MACRO=b'#define render_mirror_frontblaster_body(...) false\n'

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
  raw=restored[spec['path']];require(raw.count(spec['start'])==1,'Ambiguous FrontBlaster addition')
  start=raw.index(spec['start']);end=len(raw)if spec['end']is None else raw.index(spec['end'],start)
  addition=raw[start:end];require(SHA(addition)==spec['sha256'],'Unreviewed finite FrontBlaster block: '+name)
  additions[name]=addition;restored[spec['path']]=raw[:start]+raw[end:]
 restored['src/mainint.c']=replace_once(restored['src/mainint.c'],NEW_BODY_BRANCH,OLD_BODY_BRANCH,'one FrontBlaster body branch')
 restored['src/entity_draw.h']=replace_once(restored['src/entity_draw.h'],ENTITY_DECL,b'','FrontBlaster wrapper declaration')
 restored['src/render_mirror.h']=replace_once(restored['src/render_mirror.h'],MIRROR_DECL,b'','FrontBlaster mirror declaration')
 restored['src/render_mirror.h']=replace_once(restored['src/render_mirror.h'],MIRROR_MACRO,b'','classic-disabled macro')
 for before,after,label in [(b', ASSET_FRONTBLASTER_BODY=128',b'','role128'),(b'static Asset assets[541];',b'static Asset assets[540];','one slot'),(b'a->bank==ASSET_FRONTBLASTER_BODY?"option-frontblaster-bank10":',b'','resource prefix')]:
  restored['src/render_mirror.c']=replace_once(restored['src/render_mirror.c'],before,after,label)
 for p,raw in baseline.items():require(restored[p]==raw,'Byte-exact production inverse failed: '+p)
 return restored,additions

def finite_contract(current,additions):
 source=additions['source_and_asset'];wrapper=additions['entity_wrapper'];route=additions['body_route']
 for value in [b'if(!bank.data||bank.data!=spriteSheet10.data||bank.size!=spriteSheet10.size)',b'Uint8 source[24*28*2]={0};',b'decode_tile(bank,83,source,source+24*28,24,0,0)',b'decode_tile(bank,84,source,source+24*28,24,12,0)',b'decode_tile(bank,102,source,source+24*28,24,0,14)',b'decode_tile(bank,103,source,source+24*28,24,12,14)',b'UINT64_C(0xeb8e5d2261e22274)',b'option!=20||sidekick_style!=2||charge!=0||index!=83',b'Asset *a=&assets[540];',b'a->initialized=true;a->bank=ASSET_FRONTBLASTER_BODY;a->index=83;',b'a->w=24;a->h=28;a->anchor_x=0;a->anchor_y=0;',b'if(!a->valid&&game_probe_density==8)a->valid=read_asset(a,4);']:
  require(value in source,'Missing finite QUAD source/resource contract')
 require(source.index(b'!frontblaster_body_source_matches(bank)')<source.index(b'if(a->initialized)'),'Current source must be checked before every cache lookup')
 require(b'xmas'not in source+route,'No blanket Christmas rejection for matching current source')
 require(wrapper.count(b'blit_sprite2x2(')==wrapper.count(b'render_mirror_frontblaster_body(')==wrapper.count(b'render_mirror_entity_end(')==1,'Wrapper requires one HD attempt, one original quad and lease end')
 require(b' (void)render_mirror_frontblaster_body(target,x,y,bank,index,option,sidekick_style,charge);\n blit_sprite2x2(target,x,y,bank,index);\n render_mirror_entity_end();'in wrapper,'Original quad/order changed')
 require(b'return a?draw_asset(x,y,a,MIRROR_NORMAL,NULL):false;'in route and b'x<0||x>296||y<-27||y>199'in route,'Original registration, compositor or complete-quad row-wrap fallback changed')
 require(current['src/mainint.c'].count(b'draw_frontblaster_body_sprite2(')==1,'Only one FrontBlaster body call site permitted')
 require(not any(v in b''.join(additions.values())for v in [b'is_alive',b'moveOK',b'moveOk',b'this_player',b'rand(',b'mt_rand']),'Drawing additions contain gameplay control')

def negative_cases(current,baseline):
 cases=[]
 mutations=[('original blitter changed','src/sprite.c',b'#include',b'/*changed*/\n#include'),('unrelated mainint changed','src/mainint.c',b'#include',b'/*changed*/\n#include'),('pointer-only admission','src/render_mirror.c',b'!frontblaster_body_source_matches(bank)',b'!bank.data'),('unbounded slot capacity','src/render_mirror.c',b'assets[541]',b'assets[542]'),('extra original quad','src/entity_draw.c',b' (void)render_mirror_frontblaster_body(target,x,y,bank,index,option,sidekick_style,charge);',b' blit_sprite2x2(target,x,y,bank,index);\n (void)render_mirror_frontblaster_body(target,x,y,bank,index,option,sidekick_style,charge);'),('broadened shared22 branch','src/mainint.c',b'this_player->items.sidekick[i] == 20 &&',b'(this_player->items.sidekick[i] == 20 || this_player->items.sidekick[i] == 22) &&'),('blanket Christmas rejection','src/render_mirror.c',b'if(!bank.data||bank.data!=spriteSheet10.data||bank.size!=spriteSheet10.size)',b'if(xmas||!bank.data||bank.data!=spriteSheet10.data||bank.size!=spriteSheet10.size)'),('missing fourth quadrant','src/render_mirror.c',b'!decode_tile(bank,103,source,source+24*28,24,12,14)',b'false'),('wrong source stamp','src/render_mirror.c',b'0xeb8e5d2261e22274',b'0xeb8e5d2261e22275'),('unsafe horizontal wrapping','src/render_mirror.c',b'x<0||x>296||y<-27||y>199',b'x<0||x>308||y<-27||y>199'),('wrong resource prefix','src/render_mirror.c',b'option-frontblaster-bank10',b'option-frontblaster-bank9'),('original Quad origin changed','src/mainint.c',b'draw_frontblaster_body_sprite2(VGAScreen, x - 6, y',b'draw_frontblaster_body_sprite2(VGAScreen, x, y')]

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
 report={'status':'PASS','baseline_commit':BASE,'baseline_tree':TREE,'production_files_checked':len(names),'production_files_changed':sorted(ENVELOPE),'whole_source_byte_inverse':True,'mainint_exact_inverse_after_one_finite_body_branch_removal':True,'original_gameplay_state_rng_shots_hud_shops_orbits_preserved':True,'existing_normal15_christmas_exclusion_preserved':True,'marlo_talon_mint_body_projectile_get_asset_compositor_pixel_bridge_decoder_blitters_preserved':True,'new_role':128,'new_slots':[540],'capacity_before':540,'capacity_after':541,'option':20,'style':2,'charge':0,'source_bank':10,'active_indices':[83],'quad_tiles':[83,84,102,103],'normal_christmas_matching_source_allowed':True,'registration':{'logical':[24,28],'anchor':[0,0]},'new_blocks':{k:{'sha256':SHA(v),'bytes':len(v)}for k,v in additions.items()},'negative_scope_mutations_rejected':negative_cases(current,baseline),'source_sha256':{p:{'baseline':SHA(baseline[p]),'candidate':SHA(current[p]),'inverse':SHA(restored[p])}for p in names},'source_only_audit':True,'game_runs':0,'commit_or_publish_actions':0,'verification_limit':'Static finite inverse and twelve bounded negative mutations; runtime and asset pack preservation checked separately','harness_sha256':SHA(Path(__file__).read_bytes())}

 return {'baseline':baseline,'candidate':current},report

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--out',type=Path,required=True);a=p.parse_args();out=a.out.resolve();require(ROOT not in out.parents and out!=ROOT,'Report must be outside checkout');require(not out.exists(),'Report must be a new file');_,report=source_scope(a.root);out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n');print('PASS: all 153 baseline production files; exact five-file FrontBlaster-only inverse; twelve forbidden mutations rejected; no game run')
if __name__=='__main__':main()
