"""Build/check only the finite projectile61 candidate; no inventory claim."""
from pathlib import Path
import argparse, json
import current_projectile61_compatibility as c
from build_current_art import fnv

def products(root):
    selected,pngs,blobs=c.generate(root,c.read(root,c.SELECTION))
    blob=blobs[c.PAIRS[0]]
    row=dict(identity=c.IDS[0],density=8,source_path=c.ROOT+'/'+c.name(c.IDS[0]),
             destination='assets/gameplay/'+c.name(c.IDS[0]),sha256=c.sha(blob))
    mapping=dict(schema='opentyrian-current-projectile61-compatibility-v1',selection=c.SELECTION,
                 version=selected['version'],files=[row])
    return {**pngs,row['source_path']:blob,c.MAPPING:(json.dumps(mapping,indent=2)+'\n').encode(),
            c.HEADER:c.payload_header({c.PAIRS[0]:fnv(blob[28:])})}

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--write',action='store_true');a=p.parse_args()
    outputs=products(a.root)
    for name,data in outputs.items():
        path=a.root/name
        if a.write:
            path.parent.mkdir(parents=True,exist_ok=True)
            if path.exists() and (path.is_symlink() or path.stat().st_nlink!=1):raise ValueError('Refuse linked output')
            path.write_bytes(data)
        elif not path.is_file() or path.read_bytes()!=data:raise ValueError('Stale derivative: '+name)
    c.load(a.root)
    print(json.dumps({'status':'PASS_AUTHORING_ONLY','files':{n:c.sha(b) for n,b in outputs.items()}},indent=2))

if __name__=='__main__':main()
