#!/usr/bin/env python3
"""Deterministic candidate registration and shared-master aperture composition.
Not a game integration or qualification script. Requires original reference PNGs.
"""
from pathlib import Path
from PIL import Image
import numpy as np
import hashlib,json

root=Path(__file__).resolve().parent
refs=root.parent/'next-art-audit-turret39'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def fit(name):
    original=Image.open(root/name).convert('RGBA')
    # Trim only existing raw upper ground margin, then resample the remaining
    # complete image. Bottom ground is real generated texture, never row fill.
    im=original.crop((0,45,original.width,original.height)).resize((192,224),Image.Resampling.LANCZOS)
    a=np.asarray(im).copy()
    a[:,:,3]=255
    return a
a=np.asarray(Image.open(refs/'original-newshf-base39-native.png').convert('RGB'))
b=np.asarray(Image.open(refs/'original-newshf-base41-native.png').convert('RGB'))
mask=np.any(a!=b,axis=2)
assert mask.shape==(28,24) and int(mask.sum())==22
allowed=np.repeat(np.repeat(mask,8,axis=0),8,axis=1)
cold=fit('turret-cold-generated-v1.png'); hot_source=fit('turret-hot-generated-v1.png')
hot=cold.copy(); hot[allowed]=hot_source[allowed]
Image.fromarray(cold).save(root/'turret-cold-registered-v1.png')
Image.fromarray(hot).save(root/'turret-hot-registered-v1.png')
overlay=np.zeros_like(cold);overlay[allowed]=hot_source[allowed]
Image.fromarray(overlay).save(root/'turret-aperture-overlay-v1.png')
Image.fromarray(np.concatenate((cold,hot),axis=1)).save(root/'turret-cold-hot-registered-v1.png')
diff=np.any(cold!=hot,axis=2)
assert not np.any(diff&~allowed)
assert np.all(cold[:,:,3]==255) and np.all(hot[:,:,3]==255)
result={'status':'ART_CANDIDATE_NOT_RUNTIME_QUALIFIED','size':[192,224],
 'registration':{'source_crop':'x=0..width, y=45..height','resize':'LANCZOS 192x224','background_fill':'none; all pixels from existing raw source'},
 'original_changed_cells':np.argwhere(mask).tolist(),'allowed_hd_pixels':int(allowed.sum()),
 'changed_hd_pixels':int(diff.sum()),'outside_allowed_changes':int((diff&~allowed).sum()),
 'both_fully_opaque':True,'canonical_master':'turret-cold-registered-v1.png',
 'overlay':'turret-aperture-overlay-v1.png','source_hashes':{n:sha(root/n)for n in ['turret-cold-generated-v1.png','turret-hot-generated-v1.png']},
 'reference_hashes':{n:sha(refs/n)for n in ['original-newshf-base39-native.png','original-newshf-base41-native.png']},
 'output_hashes':{n:sha(root/n)for n in ['turret-cold-registered-v1.png','turret-hot-registered-v1.png','turret-aperture-overlay-v1.png']}}
(root/'registration-v1.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
