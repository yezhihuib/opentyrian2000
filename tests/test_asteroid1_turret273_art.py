#!/usr/bin/env python3
"""Finite original-coverage/shared-master/material139 artwork regression."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,resource,struct,subprocess,sys
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'assets/hd/artwork/asteroid1-turret273-v1'
PACK=ROOT/'assets/hd/packs/asteroid1-ten-v1'
SHA=lambda raw:hashlib.sha256(raw).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    assert not a.out.exists();a.out.mkdir(parents=True)
    spec=importlib.util.spec_from_file_location('pulsing_art',ROOT/'prototype/build-asteroid1-turret273-art.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    source=(a.data/'newshd.shp').read_bytes();assert len(source)==42012 and m.fnv(source)=='0x913975450e0fc00d'
    provenance=json.loads((ART/'provenance.json').read_text());inventory=json.loads((ART/'art-inventory.json').read_text())
    for name,expected in provenance['masters'].items():assert SHA((ART/name).read_bytes())==expected
    def limits():resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,)*2);resource.setrlimit(resource.RLIMIT_FSIZE,(2*1024**2,)*2)
    subprocess.run([sys.executable,str(ROOT/'prototype/build-asteroid1-turret273-art.py'),'--data',str(a.data),'--out',str(a.out/'rebuilt')],check=True,capture_output=True,preexec_fn=limits,env={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1'})
    decoded={b:m.decode(source,b)for b in m.BASES};union=np.zeros((28,24),bool)
    for b in m.BASES[1:]:union|=decoded[b][0]!=decoded[193][0]
    assert union.sum()==178;yy,xx=np.where(union);bbox=[int(xx.min()),int(yy.min()),int(xx.max()-xx.min()+1),int(yy.max()-yy.min()+1)];assert bbox==[4,2,15,22]
    allowed=np.repeat(np.repeat(union,8,axis=0),8,axis=1);arrays={};checks=[]
    for b in m.BASES:
        stem=f'enemy-newshd-{b}-8';im=Image.open(ART/(stem+'.png'));assert im.mode=='RGBA' and im.size==(192,224)
        raw=(PACK/(stem+'.hda')).read_bytes();assert len(raw)==172060 and struct.unpack('<4s6I',raw[:28])==(b'HDR1',1390000+b,8,24,28,0,0)
        assert raw[28:]==im.tobytes() and m.fnv(im.tobytes())==inventory[stem]['rgba_fnv64'] and SHA(raw)==inventory[stem]['sha256']
        assert (a.out/'rebuilt'/(stem+'.hda')).read_bytes()==raw and (a.out/'rebuilt'/(stem+'.png')).read_bytes()==(ART/(stem+'.png')).read_bytes()
        arrays[b]=np.array(im);assert np.all(arrays[b][:,:,3]==255) and np.all(decoded[b][1]==255)
        checks.append({'base':b,'role':1390000+b,'hda_sha256':SHA(raw),'rgba_fnv64':m.fnv(im.tobytes())})
    for b in m.BASES:
        for other in m.BASES:
            if b==other:continue
            changed=np.any(arrays[b]!=arrays[other],axis=2);assert changed.any() and not np.any(changed&~allowed)
    # Authentic three central glow phases increase warm core energy; no generated projectile.
    central=np.zeros((28,24),bool);central[5:10,9:14]=True
    central=np.repeat(np.repeat(central,8,axis=0),8,axis=1)
    pulse_energy={str(b):float(arrays[b][central,1].mean()) for b in (205,207,169)}
    assert pulse_energy['169']>pulse_energy['207']>pulse_energy['205']
    report={'status':'PASS','source_bank':'NEWSHD','logical_bank':8,'material_role':139,'source_bytes':42012,'source_fnv64':m.fnv(source),'images':checks,'occupied_logical_cells_per_image':672,'state_difference_union_cells':178,'state_difference_bbox':bbox,'housing_outside_source_union_exact':True,'all_seventy_two_directed_pair_transitions_distinct':True,'three_authentic_charge_green_energy_states':pulse_energy,'rebuild_png_and_HDA_exact':True,'masters_match_provenance':True,'scope':'Finite deterministic art conversion only; native original-engine acceptance is separate.'}
    (a.out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
