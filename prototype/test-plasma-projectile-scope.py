#!/usr/bin/env python3
"""Verify the finite original-art Plasma blend inverse and all asset retention.

No engine launch, external write, or original game data is needed.
"""
from pathlib import Path
import argparse, hashlib, json, subprocess
ROOT=Path(__file__).resolve().parents[1]
BASE='d98556a7798d79980c785b5a25ba67566697bdb0'
VERTICAL_BASE='17d6d000fe4bf76bc7774f0f636576c63d855515'
ENVELOPE={'src/render_mirror.c','src/render_mirror.h','src/sprite.c'}
BLOCK_START=b'/* Weapon88/1088 keeps three independent variable-sized raw sprite calls.'
BLOCK_END=b'static bool recognized_value_effect('
BLOCK_SHA='0d133349e8641806dc9f5623933840d27057c7d3306d3a4fb86390a9950fbf45'
MACROS=b'#define render_mirror_plasma_projectile_begin(...) false\n#define render_mirror_plasma_projectile_pixel(surface,address,source,compatible) ((void)(compatible))\n'
DECLS=b'/* Exact original OPTION_SHAPES22..24 only; independent admission per raw call. */\nbool render_mirror_plasma_projectile_begin(SDL_Surface *,int x,int y,unsigned int table,unsigned int index);\nvoid render_mirror_plasma_projectile_pixel(SDL_Surface *,Uint8 *,Uint8 source,bool compatible);\n'
BEGIN=b'\tconst bool plasma_blend = render_mirror_plasma_projectile_begin(surface, x, y, table, index);\n'
CALL=b'render_mirror_plasma_projectile_pixel(surface,pixels,*data,plasma_blend);'
ORIGINAL=b'render_mirror_pixel(surface,pixels,*data,MIRROR_BLEND);'
SHA=lambda b:hashlib.sha256(b).hexdigest()
def require(ok,message):
 if not ok:raise AssertionError(message)
def git(*args,**kw):return subprocess.check_output(['git','-C',str(ROOT),*args],**kw)
def once(raw,before,after):
 require(raw.count(before)==1,'Missing or repeated finite inverse')
 return raw.replace(before,after,1)
def inverse(current,baseline):
 require(set(current)==set(baseline),'Production source inventory changed')
 require({p for p in current if current[p]!=baseline[p]}==ENVELOPE,'Expected exactly three production files')
 out=dict(current);raw=out['src/render_mirror.c'];require(raw.count(BLOCK_START)==1,'Ambiguous compatibility block')
 a=raw.index(BLOCK_START);b=raw.index(BLOCK_END,a);block=raw[a:b];require(SHA(block)==BLOCK_SHA,'Unreviewed compatibility code')
 out['src/render_mirror.c']=raw[:a]+raw[b:]
 out['src/render_mirror.h']=once(once(out['src/render_mirror.h'],MACROS,b''),DECLS,b'')
 out['src/sprite.c']=once(out['src/sprite.c'],BEGIN,b'')
 # Only this exact callback inside the original raw blend function is replaced.
 raw=out['src/sprite.c'];a=raw.index(b'void blit_sprite_blend(');b=raw.index(b'void blit_sprite_hv_unsafe(',a)
 out['src/sprite.c']=raw[:a]+once(raw[a:b],CALL,ORIGINAL)+raw[b:]
 require(all(out[p]==baseline[p]for p in baseline),'Original source byte inverse failed')
 return out,block

def vertical_inverse(current,baseline):
 require(set(current)==set(baseline),'Vertical-step source inventory changed')
 require({p for p in current if current[p]!=baseline[p]}=={'src/render_mirror.c'},'Vertical step must change one production file')
 restored=dict(current);raw=restored['src/render_mirror.c']
 raw=once(raw,b' * Keep horizontal row-wrap and wholly offscreen calls on the old fallback.\n * A vertically partial piece has no row-wrap when x is in bounds: the original\n * raw loop clips each actual write by address before this display callback.',b' * Reject an entire individual piece when its rectangle crosses an edge: the\n * original raw blitter has linear row-wrap/address clipping, not normal XY clip.')
 raw=once(raw,b'x<0||x>320-(int)w||y<=-(int)h||y>=200||',b'x<0||x>320-(int)w||y<0||y>200-(int)h||')
 restored['src/render_mirror.c']=raw
 require(all(restored[p]==baseline[p]for p in baseline),'Vertical-step byte inverse failed')
 return restored

def turret_lifecycle_projection(current):
 # This independent one-predicate fix does not alter the Plasma contract.
 # Keep the old whole-source inverses exact after reversing that predicate;
 # its actual behavior has a separate production-extracted lifecycle test.
 projected=dict(current);raw=projected['src/render_mirror.c']
 live=b'if(regions[j].live&&regions[j].bank==ASSET_NEWSH2'
 legacy=b'if(regions[j].bank==ASSET_NEWSH2'
 require(raw.count(live)+raw.count(legacy)==1,'Ambiguous turret sibling predicate')
 changed=live in raw
 if changed:projected['src/render_mirror.c']=once(raw,live,legacy)
 return projected,changed

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',type=Path,default=ROOT);parser.add_argument('--out',type=Path,required=True);args=parser.parse_args();root=args.root.resolve();out=args.out.resolve()
 require(out!=ROOT and ROOT not in out.parents,'Report must stay outside checkout');require(not out.exists(),'Report must be new')
 names=git('ls-tree','-r','--name-only',BASE,'--','src').decode().splitlines();require(len(names)==153,'Baseline source inventory changed')
 current_names={str(p.relative_to(root))for p in(root/'src').rglob('*')if p.is_file()or p.is_symlink()};require(current_names==set(names),'Production source inventory changed')
 require(not any((root/p).is_symlink()for p in names),'Production symlink rejected')
 baseline={p:git('show',BASE+':'+p)for p in names};current={p:(root/p).read_bytes()for p in names}
 projected,turret_projected=turret_lifecycle_projection(current);restored,block=inverse(projected,baseline)
 vertical_baseline={p:git('show',VERTICAL_BASE+':'+p)for p in names};vertical_restored=vertical_inverse(projected,vertical_baseline)
 negative=[]
 for name,path,before,after in [
  ('gameplay mutation','src/shots.c',b'#include',b'/*changed*/\n#include'),
  ('indexed arithmetic mutation','src/sprite.c',b' / 2)',b' / 3)'),
  ('duplicate indexed write','src/sprite.c',b'*pixels = (*data & 0xf0)',b'*pixels = 0; *pixels = (*data & 0xf0)'),
  ('broadened source identity','src/render_mirror.c',b'index<22||index>24',b'index<21||index>25'),
  ('removed source guard','src/render_mirror.c',b'return stamp==pins[k];',b'return true;'),
  ('removed per-piece clipping','src/render_mirror.c',b'x<0||x>320-(int)w||y<=-(int)h||y>=200',b'false'),
  ('HD copy owner admission','src/render_mirror.c',b'p[sx]=owner[sx]==1?explosion_blend_rgba',b'p[sx]=owner[sx]?explosion_blend_rgba')]:
  mutated=dict(current);require(before in mutated[path],'Bad negative fixture '+name);mutated[path]=mutated[path].replace(before,after,1)
  try:inverse(turret_lifecycle_projection(mutated)[0],baseline)
  except(AssertionError,ValueError):negative.append(name)
  else:raise AssertionError('Accepted forbidden mutation '+name)
 # Compare every tracked asset byte and mode to this batch's exact baseline.
 entries=git('ls-tree','-r',BASE,'--','assets').decode().splitlines();pins={}
 for row in entries:
  meta,path=row.split('\t');mode,kind,oid=meta.split();require(kind=='blob'and mode in('100644','100755'),'Unsupported baseline asset');pins[path]=(mode,oid)
 actual={str(p.relative_to(root))for p in(root/'assets').rglob('*')if p.is_file()or p.is_symlink()};require(actual==set(pins),'Asset inventory changed')
 paths=sorted(pins);require(not any((root/p).is_symlink()for p in paths),'Asset symlink rejected')
 hashes=subprocess.check_output(['git','-C',str(root),'hash-object','--no-filters','--stdin-paths'],input=('\n'.join(paths)+'\n').encode()).decode().splitlines();require(len(hashes)==len(paths),'Incomplete asset hashes')
 for path,oid in zip(paths,hashes):require(oid==pins[path][1]and bool((root/path).stat().st_mode&0o100)==(pins[path][0]=='100755'),'Asset byte/mode changed: '+path)
 report={'status':'PASS','baseline_commit':BASE,'production_files_checked':len(names),'production_files_changed':sorted(ENVELOPE),'whole_source_byte_inverse':True,'independent_live_turret_sibling_predicate_projected':turret_projected,'vertical_step_baseline':VERTICAL_BASE,'vertical_step_production_files_changed':['src/render_mirror.c'],'vertical_step_all_153_sources_byte_inverse':True,'compatibility_block_sha256':SHA(block),'all_asset_files_byte_and_mode_identical':len(paths),'new_art_or_resource_files':0,'negative_scope_mutations_rejected':negative,'indexed_loop_gameplay_shots_shop_rng_unchanged_after_inverse':True,'source_sha256':{p:{'baseline':SHA(baseline[p]),'candidate':SHA(current[p]),'restored':SHA(restored[p])}for p in names},'engine_launches':0,'limitations':['Source inverse proves bounded code scope; runtime/pixel behavior requires separate tests.','The independent live-sibling predicate is explicitly reversed before the historical Plasma source inverses.']}
 out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n');print(f'PASS: {len(names)}-file exact combined and vertical-step source inverses, {len(paths)} unchanged assets, {len(negative)} rejected mutations; no game run')
if __name__=='__main__':main()
