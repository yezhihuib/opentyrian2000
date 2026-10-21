"""Current semantic art compatibility outputs; historical baseline never mutates."""
import hashlib,json,struct
from pathlib import Path
from package_runtime import contained_file
from current_art_policy import compatibility_name,profile
def load(root,family='pulse'):
    policy=profile(family);IDS=policy['ids'];MAPPING=policy['mapping'];ROOT=policy['compatibility']
    path=contained_file(root,MAPPING)
    if not path.is_file(): raise ValueError('Missing current art consumer mapping')
    data=json.loads(path.read_text())
    if data.get('schema')!=f'opentyrian-current-{family}-compatibility-v1' or tuple(r['identity'] for r in data['files'])!=IDS: raise ValueError('Unexpected current art compatibility scope')
    registry=json.loads(contained_file(root,'assets/hd/global-assets-v1/registry.json').read_text())
    by_id={r['identity']:r for r in registry['resources']};result={}
    for row in data['files']:
        i=row['identity'];name=compatibility_name(i);source=f'{ROOT}/{name}';destination=f'assets/gameplay/{name}'
        if row['source_path']!=source or row['destination']!=destination:raise ValueError('Unexpected compatibility destination')
        raw=contained_file(root,source).read_bytes();r=by_id[i]
        if row['sha256']!=r['sha256'] or len(raw)!=r['bytes'] or hashlib.sha256(raw).hexdigest()!=r['sha256']:raise ValueError('Stale art compatibility output')
        if raw[:4]!=b'HDR1' or list(struct.unpack('<6I',raw[4:28]))!=r['header_u32']:raise ValueError('art compatibility header changed')
        if raw!=contained_file(root,'assets/hd/global-assets-v1/'+r['path']).read_bytes():raise ValueError('Global/compatibility mismatch')
        result[destination]=row
    return result
