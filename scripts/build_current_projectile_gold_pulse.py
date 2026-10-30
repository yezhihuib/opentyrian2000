"""Build/check the finite generated two-member gold family; no inventory claim."""
from pathlib import Path
import argparse,json
import current_projectile_gold_pulse_compatibility as c
from build_current_art import fnv

def products(root):
    selected,pngs,blobs=c.generate(root,c.read(root,c.SELECTION));rows=c.rows_for(selected,blobs)
    mapping=dict(schema=c.MAPPING_SCHEMA,selection=c.SELECTION,version=selected['version'],files=rows)
    return {**pngs,**{r['source_path']:blobs[(r['identity'],r['density'])] for r in rows},
            c.MAPPING:(json.dumps(mapping,indent=2)+'\n').encode(),
            c.HEADER:c.payload_header({pair:fnv(blob[28:]) for pair,blob in blobs.items()})}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--write',action='store_true');a=p.parse_args()
    outputs=products(a.root)
    for name,data in outputs.items():
        path=c.path(a.root,name)
        if a.write:
            path.parent.mkdir(parents=True,exist_ok=True)
            if path.exists() and (path.is_symlink() or path.stat().st_nlink!=1):raise ValueError('Refuse linked output')
            path.write_bytes(data)
        elif not path.is_file() or path.read_bytes()!=data:raise ValueError('Stale derivative: '+name)
    c.load(a.root)
    print(json.dumps({'status':'PASS_AUTHORING_ONLY','files':{n:c.sha(b) for n,b in outputs.items()}},indent=2))

if __name__=='__main__':main()
