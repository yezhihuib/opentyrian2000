#!/usr/bin/env python3
"""Generate selected byte-identical resource aliases and pins in a new directory.
No art encoding, no originals required, no overwrite, no source-tree mutation.
"""
import argparse,json
from pathlib import Path
from current_tank194_body_registration import generate,load,sha,verify_original_data

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--proof-root',type=Path);p.add_argument('--output',type=Path);p.add_argument('--check',action='store_true');p.add_argument('--verify-original-data',type=Path);group=p.add_mutually_exclusive_group();group.add_argument('--extra-poses',action='store_true',help='Select only the additional51/55 pair; default remains91/93');group.add_argument('--poses15-17',action='store_true',help='Select only the additional15/17 pair');group.add_argument('--pose89',action='store_true',help='Select only the additional89 resource');group.add_argument('--pose13-adaptation',action='store_true',help='Select only actual native13 with unchanged visualHD91; deliberately not an exact native alias');a=p.parse_args()
    selected_generate,selected_load=generate,load
    if a.extra_poses:
        if a.verify_original_data:p.error('Extra-pose registration uses public proof; original verification remains the default pair mode')
        from current_tank194_extra_registration import generate as selected_generate,load as selected_load
    if a.poses15_17:
        if a.verify_original_data:p.error('15/17 registration uses public proof; original verification remains the default pair mode')
        from current_tank194_poses15_17_registration import generate as selected_generate,load as selected_load
    if a.pose89:
        if a.verify_original_data:p.error('89 registration uses public proof; original verification remains the default pair mode')
        from current_tank194_pose89_registration import generate as selected_generate,load as selected_load
    if a.pose13_adaptation:
        if a.verify_original_data:p.error('13 adaptation registration uses the public difference proof; original verification remains the default pair mode')
        from current_tank194_pose13_registration import generate as selected_generate,load as selected_load
    if a.verify_original_data:
        if a.output or a.check:p.error('Original verification is a separate read-only mode')
        print(json.dumps(verify_original_data(a.root,a.verify_original_data,a.proof_root),sort_keys=True));return
    if a.check:
        if a.output:p.error('Check does not write output')
        rows=selected_load(a.root,a.proof_root);print(json.dumps({'status':'PASS','aliases':len(rows),'scope':'resource and generated-header bytes only'},sort_keys=True));return
    if not a.output:p.error('Generation requires a new --output directory')
    target=a.output.absolute();root=a.root.resolve()
    if target.exists() or target.is_symlink() or not target.parent.is_dir() or target.resolve().is_relative_to(root):p.error('Output must be new and outside the source root')
    data=selected_generate(a.root,a.proof_root) # Validate every input before first output write.
    target.mkdir()
    for name,raw in data.items():
        out=target/name;out.parent.mkdir(parents=True,exist_ok=True)
        with out.open('xb') as f:f.write(raw)
    print(json.dumps({'status':'GENERATED','files':{name:{'bytes':len(raw),'sha256':sha(raw)} for name,raw in sorted(data.items())}},sort_keys=True))
if __name__=='__main__':main()
