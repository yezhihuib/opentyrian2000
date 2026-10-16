#!/usr/bin/env python3
"""Bounded exact 18a5452 production inverse; historical evidence and assets freeze."""
import argparse,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE='18a54527795971a4aa8492f86a0fc4996a51961d'
SHA=lambda b:hashlib.sha256(b).hexdigest()
ENVELOPE={'src/render_mirror.c','src/render_mirror.h','src/shots.c'}
PINS={'src/render_mirror.c':'c1388537de5136cadbe49ec647d287074769b602348e3e3073058c665c775113','src/render_mirror.h':'9059baf258530cacb38c52594b4cf13357b0cf19f4060b50f6a826207a38f5ae','src/shots.c':'258fac3b53a6bf5c4b5d101bee6ec60a30f2f2e6967048d2a70228c5adffca2f'}

def git(*args):return subprocess.check_output(['git','-C',str(ROOT),*args])
def once(raw,before,after=b''):
 assert raw.count(before)==1,repr(before)
 return raw.replace(before,after,1)
def inverse(current,baseline):
 assert set(current)==set(baseline)
 assert {n for n in current if current[n]!=baseline[n]}==ENVELOPE
 assert all(SHA(current[n])==h for n,h in PINS.items()),'Frozen production bytes changed'
 restored=dict(current);raw=restored['src/render_mirror.c']
 start=raw.index(b'/* Three authored Storm pieces are leased by actual emission identity')
 end=raw.index(b'static bool recognized_value_effect(',start);raw=raw[:start]+raw[end:]
 raw=once(raw,b'#include "shots.h"\n')
 raw=once(raw,b'ASSET_PLASMA_BODY=129, ASSET_PLASMA_PROJECTILE=130 };',b'ASSET_PLASMA_BODY=129 };')
 raw=once(raw,b'static void plasma_art_reset(void);\n')
 raw=once(raw,b'a->bank==ASSET_PLASMA_PROJECTILE?"option-plasma-projectile":')
 raw=once(raw,b'{plasma_art_reset();ground101_frame_reset();terrain_file=',b'{ground101_frame_reset();terrain_file=')
 restored['src/render_mirror.c']=raw
 raw=restored['src/render_mirror.h']
 for line in [b'#define render_mirror_plasma_art_emit(...) ((void)0)\n',b'#define render_mirror_plasma_art_prepare(...) ((void)0)\n',b'#define render_mirror_plasma_art_end(...) ((void)0)\n',b'void render_mirror_plasma_art_emit(unsigned slot,unsigned weapon,unsigned bay,unsigned pnum,unsigned frame);\n',b'void render_mirror_plasma_art_prepare(SDL_Surface *,int x,int y,unsigned slot,unsigned table,unsigned index);\n',b'void render_mirror_plasma_art_end(SDL_Surface *);\n']:raw=once(raw,line)
 restored['src/render_mirror.h']=raw
 raw=restored['src/shots.c']
 for line in [b'#include "render_mirror.h"\r\n',b'\t\t\trender_mirror_plasma_art_prepare(VGAScreen, *out_shotx+1, *out_shoty, shot_id, OPTION_SHAPES, sprite_frame - 60001);\r\n',b'\t\t\trender_mirror_plasma_art_end(VGAScreen);\r\n',b'\t\trender_mirror_plasma_art_emit(shot_id, wpNum, bay_i, playerNum, shot->shotGr);\r\n']:raw=once(raw,line)
 restored['src/shots.c']=raw
 assert restored==baseline,'Exact baseline inverse failed'
 return restored

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);a=p.parse_args();out=a.out.resolve();assert ROOT not in out.parents and not out.exists()
 names=git('ls-tree','-r','--name-only',BASE,'--','src').decode().splitlines()
 assert set(names)=={str(p.relative_to(ROOT))for p in (ROOT/'src').rglob('*')if p.is_file()or p.is_symlink()}
 assert not any((ROOT/n).is_symlink()for n in names)
 baseline={n:git('show',BASE+':'+n)for n in names};current={n:(ROOT/n).read_bytes()for n in names};restored=inverse(current,baseline)
 negative=[]
 for label,path,before,after in [
  ('source guard broadened','src/render_mirror.c',b'index<22||index>24',b'index<21||index>25'),
  ('wrong emission weapon','src/render_mirror.c',b'weapon==88&&',b'weapon==1088&&'),
  ('stale projection accepted','src/render_mirror.c',b'plasma_art_stamp(plasma_art_projection[k].value,count*sizeof(Uint16))!=plasma_art_projection[k].stamp',b'false'),
  ('wrong ownership','src/render_mirror.c',b'bool owns=alpha||covered;',b'bool owns=alpha;'),
  ('generic alpha blend','src/render_mirror.c',b'plasma_art_blend(under,hd_owner[n],before,plasma_art_projection[index-22].value[at],alpha)',b'under'),
  ('collision size changed','src/shots.c',b'->width / 2',b'->width / 3'),
  ('indexed write changed','src/sprite.c',b' / 2)',b' / 3)'),
  ('unrelated cloud policy','src/render_mirror.c',b'terrain_file!=\'z\'||!map',b'terrain_file!=\'x\'||!map'),
  ('unrelated file','src/player.h',b'#ifndef',b'/* changed */\n#ifndef')]:
  trial=dict(current);assert before in trial[path];trial[path]=trial[path].replace(before,after,1)
  try:inverse(trial,baseline)
  except AssertionError:negative.append(label)
  else:raise AssertionError('Forbidden mutation accepted: '+label)
 # New art has separate receipts. All PREEXISTING image/HDA bytes and modes,
 # and historical Plasma tests/docs, remain exact; manifest extension is allowed.
 rows=git('ls-tree','-r',BASE,'--','assets','prototype/test-plasma-projectile-blend.c','prototype/test-plasma-projectile-blend.py','prototype/test-plasma-projectile-scope.py','docs/option-plasma-projectile-blend-v1','docs/option-plasma-projectile-vertical-v1').decode().splitlines()
 retained=0
 for row in rows:
  meta,name=row.split('\t');mode,kind,oid=meta.split()
  if name=='assets/hd/manifest.json':continue
  f=ROOT/name;assert f.is_file()and not f.is_symlink(),name
  raw=f.read_bytes();assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==oid,name
  assert bool(f.stat().st_mode&0o100)==(mode=='100755'),name
  retained+=1
 report={'status':'PASS','baseline':BASE,'production_files_checked':len(names),'changed_production_files':sorted(ENVELOPE),'exact_baseline_inverse':True,'sprite_blitter_and_compatibility_functions_unchanged':True,'preexisting_assets_and_historical_evidence_retained':retained,'negative_scope_mutations_rejected':negative,'sources':{n:{'baseline':SHA(baseline[n]),'current':SHA(current[n]),'inverse':SHA(restored[n])}for n in names},'limitations':['New art, manifest and packaging are verified separately. This source-only check makes no runtime or visual claim.']}
 out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='sources'},indent=2))
if __name__=='__main__':main()
