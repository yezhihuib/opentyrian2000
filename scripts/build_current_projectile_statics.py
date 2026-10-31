"""Check/write six fixed selected statics products; no new art or runtime claim."""
from pathlib import Path
import argparse,json,os,stat
import current_projectile_statics_compatibility as c

def products(root):
    selected,pngs,blobs=c.generate(root,c.read(root,c.SELECTION));rows=c.rows_for(selected,blobs)
    mapping=dict(schema=c.MAPPING_SCHEMA,selection=c.SELECTION,version=selected['version'],files=rows)
    return {**pngs,**{r['source_path']:blobs[(r['identity'],r['density'])]for r in rows},c.MAPPING:(json.dumps(mapping,indent=2)+'\n').encode(),c.HEADER:c.payload_header({pair:c.fnv(b[28:])for pair,b in blobs.items()})}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--write',action='store_true');a=p.parse_args();outputs=products(a.root)
    paths={n:c.path(a.root,n)for n in outputs}
    for path in paths.values():
        if path.exists():
            s=path.lstat()
            if not stat.S_ISREG(s.st_mode)or s.st_nlink!=1:raise ValueError('Refuse linked/nonregular output')
    for name,data in outputs.items():
        path=paths[name]
        if a.write:
            path.parent.mkdir(parents=True,exist_ok=True);c.path(a.root,name)
            fd=os.open(path,os.O_WRONLY|os.O_CREAT|getattr(os,'O_NOFOLLOW',0),0o644)
            with os.fdopen(fd,'wb')as f:
                s=os.fstat(f.fileno())
                if not stat.S_ISREG(s.st_mode)or s.st_nlink!=1:raise ValueError('Refuse linked output descriptor')
                f.truncate(0);f.write(data)
        elif c.read(a.root,name)!=data:raise ValueError('Stale derivative: '+name)
    c.load(a.root)
    print(json.dumps({'status':'PASS_AUTHORING_ONLY','files':{n:c.sha(b)for n,b in outputs.items()}},indent=2))
if __name__=='__main__':main()
