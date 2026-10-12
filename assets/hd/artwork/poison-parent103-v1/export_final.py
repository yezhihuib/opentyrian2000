"""Reproduce the one finite Poison Bomb parent103 texture from its imagegen master.
Only recorded whole-object crop/resize/placement; no procedural repaint or alpha remask.
Original-data references are optional local-only inputs and never packaged.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import hashlib, json, struct, zipfile
ROOT=Path(__file__).resolve().parent
SHA=lambda data:hashlib.sha256(data).hexdigest()
for sub in ['exports','runtime','review']:(ROOT/sub).mkdir(exist_ok=True)
source=ROOT/'selected-masters/poison103-master.png'
master=Image.open(source).convert('RGBA')
transform={'crop':[156,74,1084,1288],'resize':[74,98],'paste':[15,7],'canvas':[96,112],'resampler':'Lanczos'}
out=Image.new('RGBA',(96,112));out.paste(master.crop(tuple(transform['crop'])).resize(tuple(transform['resize']),Image.Resampling.LANCZOS),tuple(transform['paste']))
png=ROOT/'exports/shapes8-id103-96x112.png';out.save(png)
header=[80103,8,12,14,0,0];raw=b'HDR1'+struct.pack('<6I',*header)+out.tobytes();hda=ROOT/'runtime/bullet-103-8.hda';hda.write_bytes(raw)
a=out.getchannel('A');hist=a.histogram();bbox=lambda t:a.point(lambda v:255 if v>t else 0).getbbox()
edge=list(a.crop((0,0,96,1)).getdata())+list(a.crop((0,111,96,112)).getdata())+list(a.crop((0,0,1,112)).getdata())+list(a.crop((95,0,96,112)).getdata())
metrics={'master_size':list(master.size),'output_size':[96,112],'alpha_bbox_gt16':bbox(16),'alpha_bbox_gt128':bbox(128),'alpha_bbox_gt240':bbox(240),'max_outer_edge_alpha':max(edge),'alpha_effective_area_logical_pixels':round(sum(v*n for v,n in enumerate(hist))/255/64,4),'pixels_alpha1_to239':sum(hist[1:240]),'pixels_alpha240_to255':sum(hist[240:]),'rgba_sha256':SHA(out.tobytes()),'hda_rgba_exact':raw[28:]==out.tobytes()}
assert bbox(16)==(16,8,88,104) and bbox(128)==(16,8,88,104) and max(edge)==0
frame={'runtime_role':'player_projectile_only','sprite_sheet':8,'sprite_id':103,'binding_key':'8:103','runtime_asset_key':80103,'logical_size':[12,14],'anchor':[0,0],'density':8,'animation_frames':1,'master':str(source.relative_to(ROOT)),'master_sha256':SHA(source.read_bytes()),'transform':transform,'source_png':str(png.relative_to(ROOT)),'source_png_sha256':SHA(png.read_bytes()),'hda':str(hda.relative_to(ROOT)),'hda_sha256':SHA(raw),'header_u32':header}
manifest={'identity':'poison-bomb-parent103-v1','status':'Root visually approved offline source-vs-HD actual4x/2x on2026-10-12 for runtime trial; in-game acceptance pending.','scope':'Exactly one static spriteSheet8 player parent103; accepted green214–217 and explosion78–84 unchanged; no weapon or gameplay edits.','tool':'Built-in image_gen; two prompts retained, selected second-pass master supplied.','alpha':'Generated straight RGBA preserved; only recorded whole-sprite crop/resample/placement.','frames':[frame],'source_registration':{'logical_size':[12,14],'occupied_bbox':[2,1,11,13],'anchor':[0,0]},'dependencies_unchanged':{'child_shot':71,'head_keys':['8:214','8:215','8:216','8:217'],'trail_keys':[f'explosion:{i}' for i in range(78,85)],'phase_semantics':'Actual collision spawns shot71; surviving children cycle214..217 and emit trail12→explosion78..84.'},'runtime_checks_required':['Existing legal-loadout fixture: front-port33 powers1/6/11 after island priority','Actual parent103 collision→child71→all214..217→all78..84 observed','Integer2x/4x classic, HD, missing-parent-only and invalid fallback','Unchanged state/RNG/collision hashes and accepted child/trail assets','Correct physical parent origin, shadow, occlusion and color; no animation added'],'coverage_limit':'Completes one missing Poison Bomb static parent identity after runtime acceptance; not all player weapons or configurations tested.'}
(ROOT/'candidate-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');(ROOT/'validation-metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')

def comparison(items,name,title):
    board=Image.new('RGB',(len(items)*170,392),(28,28,28));d=ImageDraw.Draw(board);d.text((10,8),title,fill='white');d.text((10,22),'Offline alpha-over; actual output dimensions; no gameplay screenshots.',fill=(170,170,170))
    for row,bg in enumerate([(0,0,0),(215,215,215),(70,91,61)]):
        y=46+row*110;d.rectangle((0,y,board.width-1,y+109),fill=bg)
        for col,(label,asset,scale) in enumerate(items):
            x=col*170+20;d.text((x,y+5),label,fill=(155,155,155));sm=asset.resize((12*scale,14*scale),Image.Resampling.NEAREST);board.paste(sm,(x+36,y+31),sm)
    board.save(ROOT/'review'/name)
comparison([('HD 4x',out,4),('HD 2x',out,2)],'generated-actual4x2x.png','Poison Bomb103 / generated physical parent')
alpha=Image.new('RGB',(340,152),(24,24,24));d=ImageDraw.Draw(alpha);d.text((10,8),'103 alpha / actual4x and2x',fill='white')
for scale,x in [(4,45),(2,225)]:alpha.paste(a.resize((12*scale,14*scale),Image.Resampling.NEAREST).convert('RGB'),(x,45))
alpha.save(ROOT/'review/alpha-actual4x2x.png')
reference=ROOT/'reference/original-8-103.png'
if reference.exists():
    original=Image.open(reference).convert('RGBA')
    comparison([('Original 4x',original,4),('HD 4x',out,4),('Original 2x',original,2),('HD 2x',out,2)],'source-vs-hd-actual4x2x.png','Poison Bomb103 / source vs generated HD / actual4x and2x')
common=[ROOT/n for n in ['README.txt','DEPENDENCIES.md','dependency-bindings.json','candidate-manifest.json','validation-metrics.json']]
reviews=[ROOT/'review/generated-actual4x2x.png',ROOT/'review/alpha-actual4x2x.png']
runtime_files=common+reviews+[png,hda]
source_files=common+reviews+[source,ROOT/'export_final.py']+list((ROOT/'prompts').glob('*.txt'))
for name,files in [('poison-bomb-parent103-v1-runtime.zip',runtime_files),('poison-bomb-parent103-v1-source.zip',source_files)]:
    with zipfile.ZipFile(ROOT/name,'w',zipfile.ZIP_DEFLATED) as z:
        for path in sorted(files):
            entry=zipfile.ZipInfo(str(path.relative_to(ROOT)),date_time=(2026,10,12,0,0,0));entry.compress_type=zipfile.ZIP_DEFLATED;z.writestr(entry,path.read_bytes())
print(json.dumps({'frames':[103],'root_offline_approved':True,'runtime_acceptance':'pending','hda_sha256':SHA(raw),'metrics':metrics},indent=2))
