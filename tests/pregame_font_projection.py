#!/usr/bin/env python3
"""Exact finite observer projection, preserving every byte of the qualified published C parent."""
from pathlib import Path
import hashlib,json,subprocess,runpy
from functools import lru_cache
ROOT=Path(__file__).resolve().parents[1]
PORTABLE=runpy.run_path(str(ROOT/'tests/red250_font_projection.py'))
BASE='a35747a9b25a0e7a296165e802e0777a3aaee511'
LEGACY='317bf551db59df9c4e3754d2072446c7313ab1f4'
NATIVE='c9232d59778c8689d85f9e87e8fee260b4c3187a'
EDITS=json.loads((ROOT/'tests/pregame_font_source_projection.json').read_text())
ADDED_SOURCE={'src/pregame_font.c','src/pregame_font.h'}
@lru_cache(maxsize=512)
def git(*args):return subprocess.check_output(['git','-C',str(ROOT),*args])
def project(name,raw):
 if name in EDITS and raw==git('show',BASE+':'+name):return raw
 raw=PORTABLE['project'](name,raw)
 if name not in EDITS:return raw
 for before,after in reversed(EDITS[name]):
  before=before.encode();after=after.encode()
  assert raw.count(after)>0,(name,'missing exact observer addition',after[:70])
  raw=raw.replace(after,before)
 assert raw==git('show',BASE+':'+name),(name,'original published bytes changed')
 return raw
def verify():
 portable_sources=PORTABLE['verify']()
 for name in EDITS:project(name,(ROOT/name).read_bytes())
 return {name for name in EDITS if name.startswith('src/')}|ADDED_SOURCE|portable_sources

# Historical selector/manual/Data tests still compare their original source.
# Bridge only whole files from the exact two qualified immutable commits.
# This is not an asset wildcard: every current file must first equal C parent.
@lru_cache(maxsize=1)
def published_delta():return set(git('diff','--name-only',LEGACY,BASE).decode().splitlines())
def project_legacy(name,raw):
 if name in published_delta():
  previous=git('show',LEGACY+':'+name)
  if raw==previous:return raw  # idempotent use by the historical token verifier
  assert project(name,raw)==git('show',BASE+':'+name),(name,'not exact qualified parent')
  return previous
 return project(name,raw)
def qualify_published_file(name,raw):
 assert name in published_delta(),name
 assert project(name,raw)==git('show',BASE+':'+name),(name,'published B/C delta changed')
def verify_published_delta():
 names=published_delta()
 for name in names:
  path=ROOT/name
  assert path.is_file() and not path.is_symlink(),name
  qualify_published_file(name,path.read_bytes())
 return {n for n in names if n.startswith(('src/','assets/'))}
