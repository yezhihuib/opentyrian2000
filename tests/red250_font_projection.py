#!/usr/bin/env python3
"""Finite red250/proof inverse before the unchanged portable-font inverse.

Production is exactly the disjoint union of two immutable qualified commits.
No directories or arbitrary source bytes are exempted. This module does not
import the adapted renderer test or invoke any executable/game entry point.
"""
from pathlib import Path
from functools import lru_cache
import hashlib,json,runpy,subprocess
ROOT=Path(__file__).resolve().parents[1]
BASE='4597e39c75b949d8f4e1f22bbc6117b432294132'
FONT='8d991306b3dcc18b92047ab08fa0f8a063d7d220'
RED='5e40f2bec8e8ec56f6f3f368ecc41ae547924ccf'
DATA=json.loads((ROOT/'tests/red250_font_source_projection.json').read_text())
assert (DATA['baseline'],DATA['font'],DATA['red'])==(BASE,FONT,RED)
PORTABLE=runpy.run_path(str(ROOT/'tests/portable_font_projection.py'))
RED_EDITS=DATA['red_edits'];GUARDS=DATA['proof_edits']
RED_ASSETS=set(DATA['added_assets']);RED_TRACKED=set(RED_EDITS)|RED_ASSETS
RED_ADDED=DATA['red_added_files']
assert len(RED_ADDED)==72 and RED_ASSETS=={n for n in RED_ADDED if n.startswith('assets/')}
assert set(RED_EDITS)=={'src/render_mirror.c','src/render_mirror.h','src/tyrian2.c','assets/hd/manifest.json'}
assert len(RED_ASSETS)==50
sha=lambda raw:hashlib.sha256(raw).hexdigest()
@lru_cache(maxsize=256)
def original(commit,name):
 assert commit in (BASE,FONT),'Only published Git ancestors are required'
 return subprocess.check_output(['git','-C',str(ROOT),'show',commit+':'+name])
def inverse(name,raw,pin,commit):
 # The red-only test existed before publication; its exact inverse is bound
 # by its immutable before hash, never by an unreachable local Git object.
 before=None if commit==RED else original(commit,name)
 if before is not None:assert sha(before)==pin['before_sha256'],(name,'wrong immutable parent')
 if sha(raw)==pin['before_sha256']:return raw
 assert sha(raw)==pin['after_sha256'],(name,'unapproved coexistence bytes')
 lines=raw.splitlines(keepends=True)
 for edit in reversed(pin['hunks']):
  a,b=edit['after_lines']
  assert b''.join(lines[a:b])==edit['after'].encode(),(name,'changed inverse hunk',a,b)
  lines[a:b]=edit['before'].encode().splitlines(keepends=True)
 restored=b''.join(lines)
 assert sha(restored)==pin['before_sha256'],(name,'nonexact coexistence reversal')
 if before is not None:assert restored==before,(name,'nonexact published parent')
 return restored
def outer(name,raw):
 # Older callers may pass the exact already-normalized portable parent.
 if name in GUARDS and name in PORTABLE['EDITS'] and raw==original(BASE,name):return raw
 if name in GUARDS:raw=inverse(name,raw,GUARDS[name],GUARDS[name]['parent'])
 if name in RED_EDITS:raw=inverse(name,raw,RED_EDITS[name],BASE)
 return raw
def red_original(name):
 # Reconstruct the exact accepted red bytes from published base + finite hunks.
 before=original(BASE,name)
 if name not in RED_EDITS:return before
 pin=RED_EDITS[name];assert sha(before)==pin['before_sha256'],name
 lines=before.splitlines(keepends=True)
 for edit in reversed(pin['hunks']):
  a,b=edit['before_lines'];assert b''.join(lines[a:b])==edit['before'].encode(),name
  lines[a:b]=edit['after'].encode().splitlines(keepends=True)
 result=b''.join(lines);assert sha(result)==pin['after_sha256'],name
 return result
def font_project(name,raw):return PORTABLE['project'](name,raw)
def project(name,raw):return font_project(name,outer(name,raw))
def qualify_current(name,raw):
 pins=RED_EDITS if name in RED_EDITS else GUARDS
 assert name in pins and sha(raw)==pins[name]['after_sha256'],(name,'current coexistence delta missing or changed')
 outer(name,raw)
def qualify_asset(name,raw):
 assert name in RED_ASSETS and sha(raw)==DATA['added_assets'][name],(name,'changed red asset')
 pin=RED_ADDED[name]
 assert sha(raw)==pin['sha256'],(name,'red art differs from accepted snapshot')
 assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==pin['blob'],name
def verify():
 for name in RED_EDITS:
  path=ROOT/name;assert path.is_file() and not path.is_symlink(),name
  raw=path.read_bytes();qualify_current(name,raw)
  assert raw==red_original(name),(name,'accepted red production/manifest changed')
 for name in GUARDS:
  path=ROOT/name;assert path.is_file() and not path.is_symlink(),name
  qualify_current(name,path.read_bytes())
 for name in PORTABLE['EDITS']:
  path=ROOT/name;assert path.is_file() and not path.is_symlink(),name
  PORTABLE['qualify_current'](name,outer(name,path.read_bytes()))
 for name,digest in PORTABLE['DATA']['added_test_files'].items():
  path=ROOT/name;assert path.is_file() and not path.is_symlink(),name
  assert sha(outer(name,path.read_bytes()))==digest,name
 for name in RED_ASSETS:
  path=ROOT/name;assert path.is_file() and not path.is_symlink(),name
  assert path.stat().st_mode&0o111==0,(name,'red asset executable mode changed')
  qualify_asset(name,path.read_bytes())
 for name,digest in DATA['added_proof_files'].items():
  path=ROOT/name;assert path.is_file() and not path.is_symlink() and sha(path.read_bytes())==digest,name
 assert (ROOT/'tests/portable_font_source_projection.json').read_bytes()==original(FONT,'tests/portable_font_source_projection.json')
 return {name for name in set(PORTABLE['EDITS'])|set(RED_EDITS) if name.startswith('src/')}
