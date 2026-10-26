#!/usr/bin/env python3
"""Separate cached Present smoke; does not modify or run the frozen full matrix."""
import hashlib
from pathlib import Path
import linked_newshf_native_validation as base
original=base.transformed
assert hashlib.sha256(Path(base.__file__).read_bytes()).hexdigest()=='801e2119f495b4a96b8e4ffab1455d485a9ab00961b7451ee39541d2247acf95'
def transformed(root,raw):
 source=original(root,raw)
 assert source.count('tests/newshf_compositor_validation.c')==2
 return source.replace('tests/newshf_compositor_validation.c','tests/linked_newshf_cache_smoke.c')
base.transformed=transformed
if __name__=='__main__':base.main()
