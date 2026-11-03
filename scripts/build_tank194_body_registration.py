#!/usr/bin/env python3
"""Generate two byte-identical aliases and pins into a new isolated directory.
No art encoding, no originals required, no overwrite, no source-tree mutation.
"""
import argparse,json
from pathlib import Path
from current_tank194_body_registration import generate,load,sha,verify_original_data

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--proof-root',type=Path);p.add_argument('--output',type=Path);p.add_argument('--check',action='store_true');p.add_argument('--verify-original-data',type=Path);a=p.parse_args()
    if a.verify_original_data:
        if a.output or a.check:p.error('Original verification is a separate read-only mode')
        print(json.dumps(verify_original_data(a.root,a.verify_original_data,a.proof_root),sort_keys=True));return
    if a.check:
        if a.output:p.error('Check does not write output')
        rows=load(a.root,a.proof_root);print(json.dumps({'status':'PASS','aliases':len(rows),'scope':'resource and generated-header bytes only'},sort_keys=True));return
    if not a.output:p.error('Generation requires a new --output directory')
    target=a.output.absolute();root=a.root.resolve()
    if target.exists() or target.is_symlink() or not target.parent.is_dir() or target.resolve().is_relative_to(root):p.error('Output must be new and outside the source root')
    data=generate(a.root,a.proof_root) # Validate every input before first output write.
    target.mkdir()
    for name,raw in data.items():
        out=target/name;out.parent.mkdir(parents=True,exist_ok=True)
        with out.open('xb') as f:f.write(raw)
    print(json.dumps({'status':'GENERATED','files':{name:{'bytes':len(raw),'sha256':sha(raw)} for name,raw in sorted(data.items())}},sort_keys=True))
if __name__=='__main__':main()
