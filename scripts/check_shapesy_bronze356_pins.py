#!/usr/bin/env python3
"""Read-only finite356 original identity reproduction; never emits original bytes."""
import argparse,hashlib,json
from pathlib import Path
from build_newshf_hd import fnv
ROOT=Path(__file__).resolve().parents[1]
HEADER='src/current_shapesy_bronze356_source.h'
HEADER_SHA256='fe623c5791da3b8a42a58a7f81b15345cc4b799658e8685e2f8a2a75d2f0c53d'
def verify(root=ROOT,game_data=None):
    p=root/HEADER
    assert p.is_file() and not p.is_symlink(),'missing/unsafe356 source pin'
    raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==HEADER_SHA256,'immutable356 source pin drift'
    if game_data is not None:
        source=(game_data/'shapesy.dat').read_bytes()
        assert hashlib.sha256(source).hexdigest()=='1faf60f8804c4ca52ea41ece94e3d2fd3cdaecb437b63ecb61adc58907c7b869'
        assert source[172387]==0
        pixels=source[172388:173060]
        assert len(pixels)==672 and all(pixels)
        assert hashlib.sha256(pixels).hexdigest()=='51f3ffe68cb363f3df5fb6fa6ccff0047cf343c456bc879e0ba58473d36ea7a6'
        assert fnv(pixels)==0xbf8b5e377e83f473
    return dict(status='PASS',id=356,role=202,identity=2020356,header_sha256=HEADER_SHA256,original_bytes_verified=game_data is not None)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source-root',type=Path,default=ROOT);p.add_argument('--game-data',type=Path);a=p.parse_args();print(json.dumps(verify(a.source_root,a.game_data),sort_keys=True))
