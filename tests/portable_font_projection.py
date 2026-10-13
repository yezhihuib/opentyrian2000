#!/usr/bin/env python3
"""Exact, reversible Title/Settings/Load output delta over immutable 4597e39.

This layer precedes older projections; it does not change their pins or edits.
Only the individually listed files and exact line hunks are admitted. Whole
candidate hashes and exact baseline restoration are both checked. Call verify()
for current files: project() also accepts exact baseline bytes for composition.
"""
from pathlib import Path
from functools import lru_cache
import hashlib,json,subprocess

ROOT=Path(__file__).resolve().parents[1]
BASE='4597e39c75b949d8f4e1f22bbc6117b432294132'
DATA=json.loads((ROOT/'tests/portable_font_source_projection.json').read_text())
assert DATA['baseline']==BASE
EDITS=DATA['changed_files']
sha=lambda b:hashlib.sha256(b).hexdigest()
@lru_cache(maxsize=128)
def original(name):
    return subprocess.check_output(['git','-C',str(ROOT),'show',BASE+':'+name])

def project(name,raw):
    if name not in EDITS:return raw
    pin=EDITS[name];before=original(name)
    assert sha(before)==pin['before_sha256'],(name,'wrong immutable baseline')
    if raw==before:return raw
    assert sha(raw)==pin['after_sha256'],(name,'unapproved portable-output bytes')
    lines=raw.splitlines(keepends=True)
    for edit in reversed(pin['hunks']):
        a,b=edit['after_lines']
        assert b''.join(lines[a:b])==edit['after'].encode(),(name,'changed inverse hunk',a,b)
        lines[a:b]=edit['before'].encode().splitlines(keepends=True)
    restored=b''.join(lines)
    assert restored==before,(name,'portable delta did not restore exact baseline')
    return restored

def qualify_current(name,raw):
    assert name in EDITS,name
    assert sha(raw)==EDITS[name]['after_sha256'],(name,'current delta missing or changed')
    assert project(name,raw)==original(name),name

def verify():
    for name,pin in EDITS.items():
        path=ROOT/name
        assert path.is_file() and not path.is_symlink(),name
        raw=path.read_bytes()
        qualify_current(name,raw)
    for name,digest in DATA['added_test_files'].items():
        path=ROOT/name
        assert path.is_file() and not path.is_symlink() and sha(path.read_bytes())==digest,name
    return {name for name in EDITS if name.startswith('src/')}
