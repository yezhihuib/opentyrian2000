"""Reproduce four finite static guided-bomb candidates from selected imagegen RGBA.
Only whole-object crop, Lanczos resize and registered placement. No procedural art,
recoloring or alpha remask. Original images are optional local review inputs only.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import hashlib,json,struct,zipfile
R=Path(__file__).resolve().parent
SHA=lambda data:hashlib.sha256(data).hexdigest()
T={19:('guided19-master.png',[74,180,1086,1173],[82,82],[7,15]),171:('guided171-master.png',[160,260,1001,1098],[82,82],[7,15]),20:('guided20-rounded-master.png',[99,151,956,1352],[46,62],[29,29]),21:('guided21-rounded-master.png',[130,116,811,1589],[44,76],[30,22])}
ORIGINAL_BOUNDS={19:[1,2,11,12],171:[1,2,11,12],20:[4,4,9,11],21:[4,3,9,12]}
SLOTS={19:326,171:327,20:328,21:329}
for sub in ['exports','runtime','review']:(R/sub).mkdir(exist_ok=True)
frames=[];metrics={};images={}
for n,(filename,crop,size,pos) in T.items():
    src=R/'selected-masters'/filename;master=Image.open(src).convert('RGBA')
    out=Image.new('RGBA',(96,112));out.paste(master.crop(tuple(crop)).resize(tuple(size),Image.Resampling.LANCZOS),tuple(pos));images[n]=out
    png=R/'exports'/f'shapes8-id{n}-96x112.png';out.save(png)
    header=[80000+n,8,12,14,0,0];raw=b'HDR1'+struct.pack('<6I',*header)+out.tobytes();hda=R/'runtime'/f'bullet-{n}-8.hda';hda.write_bytes(raw)
    a=out.getchannel('A');hist=a.histogram();bbox=lambda t:a.point(lambda v:255 if v>t else 0).getbbox()
    bounds={str(t):list(bbox(t)) for t in [0,16,64,128,240]}
    edge=list(a.crop((0,0,96,1)).getdata())+list(a.crop((0,111,96,112)).getdata())+list(a.crop((0,0,1,112)).getdata())+list(a.crop((95,0,96,112)).getdata())
    check_threshold=128 if n in [19,171] else 16
    expected=[v*8 for v in ORIGINAL_BOUNDS[n]]
    assert list(bbox(check_threshold))==expected,(n,bbox(check_threshold),expected)
    assert max(edge)==0 and raw[28:]==out.tobytes()
    alpha_sum=sum(v*c for v,c in enumerate(hist));weighted=[sum((i%96+.5)*v for i,v in enumerate(a.getdata()))/alpha_sum,sum((i//96+.5)*v for i,v in enumerate(a.getdata()))/alpha_sum]
    rows={}
    b=bbox(128)
    for part in [.25,.5,.75]:
        y=round(b[1]+part*(b[3]-b[1]-1));spans=[x for x in range(96) if a.getpixel((x,y))>128];rows[str(part)]={'y':y,'width_alpha_gt128':max(spans)-min(spans)+1}
    metrics[n]={'master_size':list(master.size),'output_size':[96,112],'alpha_bounds_by_threshold':bounds,'registration_threshold':check_threshold,'expected_bounds':expected,'max_outer_edge_alpha':max(edge),'alpha_effective_area_logical_pixels':round(alpha_sum/255/64,4),'alpha_weighted_center_logical':[round(v/8,4) for v in weighted],'pixels_alpha1_to239':sum(hist[1:240]),'pixels_alpha240_to255':sum(hist[240:]),'quarter_height_widths':rows,'rgba_sha256':SHA(out.tobytes()),'hda_rgba_exact':True}
    frames.append({'runtime_role':'player_projectile_only','sprite_sheet':8,'sprite_id':n,'binding_key':f'8:{n}','runtime_asset_key':80000+n,'renderer_slot_hint':SLOTS[n],'logical_size':[12,14],'anchor':[0,0],'density':8,'animation_frames':1,'material':'opaque blue metal with warm recessed center' if n in [19,171] else 'warm luminous effect with true partial-alpha shoulder','original_occupied_bounds':ORIGINAL_BOUNDS[n],'master':str(src.relative_to(R)),'master_sha256':SHA(src.read_bytes()),'transform':{'crop':crop,'resize':size,'paste':pos,'canvas':[96,112],'resampler':'Lanczos'},'source_png':str(png.relative_to(R)),'source_png_sha256':SHA(png.read_bytes()),'hda':str(hda.relative_to(R)),'hda_sha256':SHA(raw),'header_u32':header})
manifest={'identity':'guided-bomb-family-v1','status':'All four designs approved offline for a bounded runtime trial by root on2026-10-12. No runtime acceptance claimed.','scope':'Exactly four independent static spriteSheet8 player identities19,171,20,21; no22, no animation or gameplay changes.','tool':'Built-in image_gen; selected unchanged source masters and complete prompts retained.','alpha':'Generated straight RGBA preserved; only recorded whole-object crop/resample/placement.','source_commit':'3f05b84b6b63141f9f7ce3bc3b7e9399ccbb4b8e','frames':frames,'runtime_checks_required':['Root offline review approved all four designs; in-game visual acceptance remains pending','Finite natural collisions under existing legal-loadout fixture','Observe19,171,20 and21 under original tables; no invented frames','Integer2x/4x classic/HD/missing/invalid with original state/RNG/collision parity','Original origin, shadows, smoke overlap and occlusion; unchanged prior assets'],'coverage_limit':'Source contract covers99 guided configurations; no complete shared-user or all-power runtime claim.'}
(R/'candidate-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');(R/'validation-metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')

def contact(include_original=False):
    columns=4;cw=230 if include_original else 180;board=Image.new('RGB',(columns*cw,440),(25,25,25));d=ImageDraw.Draw(board)
    d.text((10,8),'Guided bomb / offline '+('source vs HD' if include_original else 'generated HD')+' / actual4x and2x',fill='white');d.text((10,23),'Nearest sample from8x RGBA; alpha-over preview, not runtime.',fill=(170,170,170))
    for col,n in enumerate(T):
        x=col*cw;d.text((x+10,42),f'bank8:{n}',fill='white')
        original=Image.open(R/'reference'/f'original-8-{n}.png').convert('RGBA') if include_original else None
        items=[(12,'src4x',original,4),(74,'HD4x',images[n],4),(142,'src2x',original,2),(185,'HD2x',images[n],2)] if include_original else [(35,'HD4x',images[n],4),(115,'HD2x',images[n],2)]
        for row,bg in enumerate([(0,0,0),(215,215,215),(70,91,61)]):
            y=63+row*122;d.rectangle((x,y,x+cw-1,y+121),fill=bg)
            for off,label,asset,scale in items:
                d.text((x+off,y+5),label,fill=(150,150,150));sm=asset.resize((12*scale,14*scale),Image.Resampling.NEAREST);board.paste(sm,(x+off,y+26),sm)
    name='source-vs-hd-actual4x2x-local.png' if include_original else 'generated-actual4x2x.png';board.save(R/'review'/name)
contact()
if all((R/'reference'/f'original-8-{n}.png').exists() for n in T):contact(True)
board=Image.new('RGB',(640,180),(25,25,25));d=ImageDraw.Draw(board);d.text((10,8),'Generated alpha / actual4x and2x',fill='white')
for col,n in enumerate(T):
    x=col*160;d.text((x+10,28),str(n),fill='white');a=images[n].getchannel('A')
    for scale,dx in [(4,25),(2,104)]:board.paste(a.resize((12*scale,14*scale),Image.Resampling.NEAREST).convert('RGB'),(x+dx,52))
board.save(R/'review/alpha-actual4x2x.png')
common=[R/n for n in ['README.txt','SOURCE_CONTRACT.md','candidate-manifest.json','validation-metrics.json']]+[R/'review/generated-actual4x2x.png',R/'review/alpha-actual4x2x.png']
source_files=common+[R/'export_final.py']+[R/'selected-masters'/T[n][0] for n in T]+list((R/'prompts').glob('*.txt'))
runtime_files=common+[R/f['source_png'] for f in frames]+[R/f['hda'] for f in frames]
for name,files in [('guided-bomb-family-v1-source.zip',source_files),('guided-bomb-family-v1-runtime.zip',runtime_files)]:
    with zipfile.ZipFile(R/name,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(files):
            entry=zipfile.ZipInfo(str(p.relative_to(R)),date_time=(2026,10,12,0,0,0));entry.compress_type=zipfile.ZIP_DEFLATED;z.writestr(entry,p.read_bytes())
print(json.dumps({'sprite_ids':list(T),'main_edits':False,'runtime_acceptance':False,'frames':[{k:f[k] for k in ['binding_key','hda_sha256']} for f in frames],'metrics':metrics},indent=2))
