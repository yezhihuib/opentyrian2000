from pathlib import Path
from PIL import Image
import hashlib,json
P=Path(__file__).resolve().parent;a=Image.open(P/'earth-corrected-two-state-atlas.png').convert('RGBA');w,h=a.size;assert a.getchannel('A').getextrema()==(255,255)
F=P/'components8x';F.mkdir(exist_ok=True);records=[]
for j,(state,ids) in enumerate([('intact',[1,3,5,39,41,43]),('exposed',[7,9,11,45,47,49])]):
 box=(round(j*w/2),0,round((j+1)*w/2),h);im=a.crop(box).resize((576,448),Image.Resampling.LANCZOS);im.save(P/f'{state}-assembly8x.png');re=Image.new('RGBA',(576,448))
 for k,n in enumerate(ids):
  x=k%3*192;y=k//3*224;tile=im.crop((x,y,x+192,y+224));f=F/f'enemy-newshe-{n}-8.png';tile.save(f);re.paste(tile,(x,y));records.append({'namespace':'newshE.shp','source_bank':9,'base':n,'state':state,'logical_size':[24,28],'anchor':[6,7],'assembly_offset':[x//8,y//8],'file':str(f.relative_to(P)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
 assert re.tobytes()==im.tobytes()
m={'identity':'stone516-527-newshe-hd-v1','density':8,'assembly_size':[72,56],'opaque_alpha':255,'source_size':[w,h],'transform':'Split full2009x783 atlas atx1004; each full panel resized576x448 LANCZOS once then exact192x224 grid. No recenter/rotation/cutout.','source_sha256':hashlib.sha256((P/'earth-corrected-two-state-atlas.png').read_bytes()).hexdigest(),'records':records,'registration':'Entity canvas is one logical pixel below frozen terrain341..353; anchors6,7 unchanged. Preserve per-entity/per-quadrant order.','lifecycle':{'516-521':'Original lethal linked collision removes all6, revealing independent foundation; no blue remnant.','522-527':'Shared intact bases convert to persistent exposed7/9/11/45/47/49, enemyAvail2/edamaged1.','hit':'explosiontype25 enemygroundfalse; no natural palette flash. Preserve original filtered compositor capability.'},'limits':['Later right-edge case clips the assembly; full offline geometry and bounded current runtime diagnostic are separate evidence.','Earth rock phase is not perfectly identical to all neighbors.','Actual candidate runtime review pending.']}
(P/'candidate-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
print('PASS:12 opaque components, exact6-part reassembly per state')
