"""Prepare exact archived private fixture sources; does not build or run a test."""
from pathlib import Path
import argparse,hashlib,json,shutil
repo=Path(__file__).resolve().parents[2];p=argparse.ArgumentParser();p.add_argument('--family',choices=['white-smoke-v1','shield-v1','green-trail'],required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve()
if out.exists():p.error('Choose a new fixture output directory')
if out==repo or repo in out.parents:p.error('Keep fixture output outside the production checkout')
source=Path(__file__).parent/'effects'/a.family;m=json.loads((source/'manifest.json').read_text());sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
def production_matches(data,digest):
 if hashlib.sha256(data).hexdigest()==digest:return True
 # Production manifests were captured on Windows. Accept Git's LF checkout
 # without ignoring any content changes or normalizing exact fixture overrides.
 crlf=data.replace(b'\r\n',b'\n').replace(b'\n',b'\r\n')
 return hashlib.sha256(crlf).hexdigest()==digest
historical_sources={}
for rel,digest in m['same_other_production_src_sha256'].items():
 data=(repo/rel).read_bytes()
 if production_matches(data,digest):continue
 # The reviewed layer2 registration is the only permitted production delta.
 # Strip one exact whole line, then verify the archived hash again. Never
 # rewrite manifests, other content, or byte-exact archived overrides.
 binding=b'\t\t\t\trender_mirror_bind_terrain(2,z+1,megaData2.shapes[x].sh);'
 lines=data.splitlines(keepends=True)
 matches=[i for i,line in enumerate(lines) if line in (binding+b'\n',binding+b'\r\n')]
 if rel=='src/tyrian2.c' and len(matches)==1:
  archived=b''.join(lines[:matches[0]]+lines[matches[0]+1:])
  if production_matches(archived,digest):
   historical_sources[rel]=archived
   continue
 p.error('Production base changed; review fixture compatibility: '+rel)
out.mkdir(parents=True);shutil.copytree(repo/'src',out/'src');shutil.copytree(repo/'visualc',out/'visualc',ignore=shutil.ignore_patterns('Release','Debug','x64','ipch','*.obj','*.tlog'))
for rel,data in historical_sources.items():(out/rel).write_bytes(data)
for rel,digest in m['tested_exact_source_overrides'].items():
 assert sha(source/'overrides'/rel)==digest;shutil.copy2(source/'overrides'/rel,out/rel)
shutil.copy2(repo/'Makefile',out/'Makefile');(out/'prototype').mkdir();shutil.copy2(repo/'prototype/build-game.ps1',out/'prototype/build-game.ps1')
for n in ['SDL2.dll','SDL2_net.dll']:
 if (repo/n).exists():shutil.copy2(repo/n,out/n)
print('Prepared diagnostic sources only:',out);print('Required asset pack:',m['test_resource_pack']);print('Use original legal game data separately; private hooks never enter production.')
