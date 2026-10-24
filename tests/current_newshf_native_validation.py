#!/usr/bin/env python3
"""Finite current-NEWSHF adapter; the historical native harness is unchanged.

Runs the full enemy compositor matrix, not natural gameplay or player shadow.
Arguments match newshf_compositor_validation.py plus optional --source-root.
"""
import hashlib
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DRIVER_SHA='d1d47d070ffa7f819366b9183b41a584c3b53a12dccd7487f6d3969fb6810620'

def transformed(root,raw):
    assert hashlib.sha256(raw).hexdigest()==DRIVER_SHA,'Historical driver changed: review finite adapter'
    source=raw.decode()
    marker='ROOT=Path(__file__).resolve().parents[1]'
    assert source.count(marker)==1
    source=source.replace(marker,f'ROOT=Path({str(root)!r})')
    marker=" check(ROOT/'authoring-inputs/enemies/newshf-phase-a',a.original_data)"
    assert source.count(marker)==1
    source=source.replace(marker,marker+"\n import current_newshf_compatibility as current\n rows=current.load(ROOT)\n current_paths=[ROOT/row['source_path'] for row in rows.values()]\n assert len(current_paths)==9")
    marker="(ROOT/'assets/hd/newshf-v1').glob('*.hda')"
    assert source.count(marker)==3
    return source.replace(marker,'current_paths')

def main():
    root=ROOT
    if '--source-root' in sys.argv:
        i=sys.argv.index('--source-root');root=Path(sys.argv[i+1]).resolve();del sys.argv[i:i+2]
    source=transformed(root,(root/'tests/newshf_compositor_validation.py').read_bytes())
    exec(compile(source,str(root/'tests/newshf_compositor_validation.py'),'exec'),{'__name__':'__main__','__file__':str(root/'tests/newshf_compositor_validation.py')})

if __name__=='__main__':main()
