#!/usr/bin/env python3
"""Read-only type3 actual native2x pixel verification; never launches the game."""
from pathlib import Path
from functools import lru_cache
import argparse,csv,gzip,json,hashlib,struct,collections,sys,subprocess
import numpy as np
from PIL import Image
sys.dont_write_bytecode=True
O=Path('/workspace/scratch/f67dd347fa0a/type3-small-recovery-native-20261013');P=json.loads((O/'provenance.json').read_text());R=Path(P['source_root']);D=Path(P['data']);PACK=Path(P['builds']['candidate']['pack']);A=O/'candidate-census';B=O/'baseline-census'
sys.path.insert(0,str(Path(__file__).resolve().parent))
from text_oracle import apply_insert_coin,PALETTE,glyphs,TEXT,XY
IDS={171,190,209,228,247,266};SHAPE=(400,640);loaded={}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
@lru_cache(None)
def rows(d,n):
 with gzip.open(d/(n+'.tsv.gz'),'rt')as f:return list(csv.DictReader(f,delimiter='\t'))
def grouped(rr):
 out=collections.defaultdict(list)
 for r in rr:out[int(r['tick'])].append(r)
 return out
@lru_cache(None)
def original(i):
 raw=(D/'newsh2.shp').read_bytes();assert sha(D/'newsh2.shp')==P['data_sha256']['newsh2.shp'];p=struct.unpack_from('<H',raw,2*(i-1))[0];idx=np.zeros(168,np.uint8);mask=np.zeros(168,bool);dest=0
 while raw[p]!=15:
  op=raw[p];p+=1;dest+=op&15;n=op>>4
  if n:assert 0<=dest and dest+n<=168;idx[dest:dest+n]=list(raw[p:p+n]);mask[dest:dest+n]=True;p+=n;dest+=n
 return idx.reshape(14,12),mask.reshape(14,12)
@lru_cache(None)
def art(prefix,i):
 p=PACK/f'{prefix}-{i}-8.hda';raw=p.read_bytes();assert raw[:4]==b'HDR1'and sha(p)==P['builds']['candidate']['pack_hashes'][p.name];role,den,w,h,ox,oy=struct.unpack('<6I',raw[4:28]);assert den==8 and len(raw)==28+w*h*64*4;arr=np.frombuffer(raw[28:],np.uint8).reshape(h*8,w*8,4)
 if prefix=='enemy-newsh2'and i in IDS:
  assert (role,den,w,h,ox,oy)==(1010000+i,8,12,14,0,0);assert np.array_equal(arr[:,:,3],np.repeat(np.repeat(original(i)[1],8,0),8,1)*255)
 loaded[p.name]=sha(p)
 # Production explicitly SDL_ScaleModeNearest: exact centers2,6 of each8x cell.
 native=arr[2::4,2::4].copy();assert np.array_equal(native,np.array(Image.fromarray(arr).resize((w*2,h*2),Image.Resampling.NEAREST)))
 return native

def clip(x,y,w,h):
 x=(x-24)*2;y*=2;x0=max(0,x);y0=max(0,y);x1=min(528,x+w);y1=min(368,y+h)
 return None if x0>=x1 or y0>=y1 else (np.s_[y0:y1,x0:x1],np.s_[y0-y:y1-y,x0-x:x1-x])
def project(im,x,y):
 mask=np.zeros(SHAPE,bool);q=clip(x,y,im.shape[1],im.shape[0])
 if q:mask[q[0]]=im[q[1]][:,:,3]>0
 return mask

def font_footprint():
 mask=np.zeros(SHAPE,bool);x,y=XY
 for ch in TEXT:
  if ch==' ':x+=6;continue
  w,h,gm,idx=glyphs[ord(ch)-ord('A')]
  for ax,ay in [(0,0),(2,2)]:
   for yy,xx in zip(*np.where(gm)):
    q=clip(x+int(xx)+ax,y+int(yy)+ay,2,2)
    if q:mask[q[0]]=True
  x+=w+1
 return mask
FONTMASK=font_footprint()

def validate_frames(tick):
 images=[]
 for d in [A,B]:
  summary=json.loads((d/'run-summary.json').read_text());assert summary['integrity_passed'];f=next(f for f in json.loads((d/'frame-hashes.json').read_text())if f['tick']==tick);path=d/f'actual-{tick}-native2x.png';im=Image.open(path).convert('RGBA');assert im.size==(640,400)and sha(path)==f['PNG_sha256']and hashlib.sha256(im.tobytes()).hexdigest()==f['RGBA_sha256'];images.append(np.array(im))
 return images

def first():
 tick=6181;actual,baseline=validate_frames(tick);expected=baseline.copy();support=np.zeros(SHAPE,bool);rr=[r for r in rows(A,'asset-debug-materials')if int(r['tick'])==tick];assert rr==[r for r in rows(B,'asset-debug-materials')if int(r['tick'])==tick];draws=[]
 for r in rr:
  if r['category']=='enemy':
   i=int(r['id']);assert i in IDS and r['id']==r['tile_id'];im=art('enemy-newsh2',i);q=clip(int(r['x']),int(r['y']),24,28)
   if q:
    dst,src=q;mask=im[src][:,:,3]>0;support[dst]|=mask;expected[dst][mask]=im[src][mask];draws.append({'id':i,'origin':[int(r['x']),int(r['y'])],'native_opaque_pixels':int(mask.sum())})
  elif r['category']=='player':
   q=clip(int(r['x']),int(r['y']),48,56);assert q is None or not support[q[0]].any()
  else:assert r['category']=='terrain-layer1'
 text=apply_insert_coin(expected,support,2);changed=np.any(actual!=baseline,axis=2);mismatch=np.any(expected!=actual,axis=2);assert not mismatch.any()and not np.any(changed&~support)
 report={'status':'PASS first actual authored native still','baseline':P['baseline'],'candidate':P['candidate'],'tick':tick,'candidate_native_still':str(A/f'actual-{tick}-native2x.png'),'baseline_native_still':str(B/f'actual-{tick}-native2x.png'),'native_dimensions':[640,400],'original_RLE_alpha_exact_at_full_density8':True,'native_mapping':'Production SDL_ScaleModeNearest, source8x center taps2,6 per logical cell to native2x. No averaging, resizing, stitching, or generated evidence image.','whole_frame_compared_RGBA_pixels':256000,'whole_frame_mismatches':0,'changed_native_pixels':int(changed.sum()),'outside_original_alpha_changes':0,'draws':draws,'text_overlay':text,'candidate_png_sha256':sha(A/f'actual-{tick}-native2x.png'),'baseline_png_sha256':sha(B/f'actual-{tick}-native2x.png'),'pack_pins':loaded.copy(),'limits':['Only first captured frame6181 verified here; full32-frame lifecycle verification remains separate.','Private survival fixture; no ram, type16, later boss, whole-level, Windows, or hardware-GPU claim.']}
 (O/'first-still-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2),flush=True)


def filtered(im,f):
 if not f:return im
 out=im.copy();value=(im[:,:,:3].max(axis=2).astype(np.uint32)*15*256+127)//255;lo=value//256;hi=np.minimum(15,lo+1);frac=value%256
 out[:,:,:3]=((PALETTE[f|lo].astype(np.uint32)*(256-frac[:,:,None])+PALETTE[f|hi].astype(np.uint32)*frac[:,:,None]+128)//256).astype(np.uint8)
 return out

def full():
 assert P['baseline']=='b2a6e4a1e924aed71630f9f63c0ba4648e920d6d'and P['candidate']=='e976cb6a81aaa2eb99f5ffee14e58f9fc050dcb0'
 renderer=subprocess.check_output(['git','show',P['candidate']+':src/render_mirror.c'],cwd=R);assert hashlib.sha256(renderer).hexdigest()==P['production_src_hashes']['render_mirror.c'];source=renderer.decode()
 for fragment in ['SDL_SetTextureScaleMode(texture,SDL_ScaleModeNearest)','value=(peak*15*256+127)/255','next=(source_peak+destination_peak+1)/2','src[c]*next+source_peak/2','d*(255-alpha)+src[c]*alpha+127','*(510-alpha)+255)/510']:
  assert fragment in source,fragment
 names=['asset-debug-materials','scene-draw-commands','draw-commands','blend-writes','blend-palette','late-census','type3-explosion-census','type3-original-effects','type3-pulse-guards','type3-pulse-shots','state','collisions','frames','effects','rgb-audit']
 for d in [A,B]:
  summary=json.loads((d/'run-summary.json').read_text());assert summary['integrity_passed']and summary['native_captures']==32
  receipts=json.loads((d/'stream-receipts.json').read_text())
  for n in names:
   assert sha(d/(n+'.tsv.gz'))==receipts[n]['gzip_sha256'],n
   if receipts[n]['retention']=='all':assert hashlib.sha256(gzip.decompress((d/(n+'.tsv.gz')).read_bytes())).hexdigest()==receipts[n]['raw_sha256'],n
  assert np.array_equal(np.array([[int(r[k])for k in ['r','g','b']]for r in rows(d,'blend-palette')],np.uint8),PALETTE)
  for n,col in [('frames','coverage_mismatch'),('effects','restored_mismatches'),('rgb-audit','classic_mismatches')]:
   rr=rows(d,n);assert [int(r['tick'])for r in rr]==list(range(6181,6532))and all(r[col]=='0'for r in rr),(d,n)
  assert all(r['reason']=='hd-ordered'and not r['all_rejections']for r in rows(d,'frames'))
  assert all(r['brightness_hd_blocks']=='0'and r['filter_fade']=='0'and r['boundary_crossings']=='0'for r in rows(d,'effects'))
  assert receipts['fire-events']['lines']<=1
 for n in ['asset-debug-materials','draw-commands','blend-palette','late-census','type3-explosion-census','type3-original-effects','type3-pulse-guards','type3-pulse-shots','state','collisions']:assert rows(A,n)==rows(B,n),n
 isfamily=lambda r:r['role']=='101'and int(r['index'])in IDS
 scene=rows(A,'scene-draw-commands');assert [r for r in scene if not isfamily(r)]==rows(B,'scene-draw-commands');assert all(r['part']=='0'and r['mirrored']=='1'for r in scene if isfamily(r))
 original_fields=['tick','known_sheet','index','origin_x','origin_y','x','y','before','source','after'];blend=rows(A,'blend-writes');assert [[r[k]for k in original_fields]for r in blend]==[[r[k]for k in original_fields]for r in rows(B,'blend-writes')]
 assert all(int(r['after'])==((int(r['source'])&240)|(((int(r['before'])&15)+(int(r['source'])&15))//2))for r in blend)
 SC=grouped(scene);M=grouped(rows(A,'asset-debug-materials'));C=grouped(rows(A,'draw-commands'));BL=grouped(blend);Census=grouped(rows(A,'late-census'));reports=[];actor_reports=[];operations=collections.Counter();cycle=[];historical_target=np.zeros(SHAPE,bool);historical_effects=np.zeros(SHAPE,bool);restoration=[]
 for i in sorted(IDS):art('enemy-newsh2',i)
 for tick in P['census_ticks']:
  actual,baseline=validate_frames(tick);expected=baseline.copy();support=np.zeros(SHAPE,bool);owner=np.full(SHAPE,-1,np.int16);exposed=np.zeros(SHAPE,bool);covered={k:np.zeros(SHAPE,bool)for k in ['later_family','projectile','player_shadow','player_halfblend','font','effect']};actors={};text_applied=False
  pre=[{k:v if k=='phase'else int(v)for k,v in r.items()}for r in Census[tick]if r['phase']=='pre-sky-25'and r['avail']!='1'and r['type']=='3'and r['bank']=='1']
  lookup={(r['x']+r['mapoffset'],r['y']):r for r in pre};assert len(lookup)==len(pre)
  family_calls=[r for r in SC[tick]if isfamily(r)];visible_calls=[r for r in family_calls if int(r['x'])<288 and int(r['x'])+12>24 and int(r['y'])<184 and int(r['y'])+14>0]
  assert [(r['index'],r['x'],r['y'])for r in visible_calls]==[(r['id'],r['x'],r['y'])for r in M[tick]if r['category']=='enemy'and int(r['id'])in IDS]
  for r in family_calls:
   x,y=int(r['x']),int(r['y']);a=lookup[x,y];assert 0<=x<=308 and -13<=y<=199;assert int(r['style'])==(3 if a['filter']else 0);assert int(r['index'])==[171,171,190,190,209,209,228,228,247,247,266,266][a['cycle']%12]
  def apply(im,x,y,mode,category,slot=None):
   q=clip(x,y,im.shape[1],im.shape[0])
   if not q:return
   dst,src=q;rgba=im[src].astype(np.uint32);alpha=rgba[:,:,3];opacity=alpha>0
   if slot is not None:
    covered['later_family'][dst]|=support[dst]&opacity;mask=opacity;support[dst]|=mask;owner[dst][mask]=slot;exposed[dst][mask]=True
   else:
    mask=support[dst]&opacity;covered[category][dst]|=mask;exposed[dst][mask]=False
   if not mask.any():return
   bg=expected[dst][:,:,:3].astype(np.uint32)
   if mode=='shadow':color=(bg*(510-alpha[:,:,None])+255)//510
   else:
    rgb=rgba[:,:,:3]
    if mode=='explosion':
     sp=rgb.max(axis=2);dp=bg.max(axis=2);nxt=(sp+dp+1)//2;rgb=np.where(sp[:,:,None]>0,(rgb*nxt[:,:,None]+sp[:,:,None]//2)//np.maximum(1,sp[:,:,None]),0)
    if mode=='half':alpha=(alpha+1)//2
    color=(rgb*alpha[:,:,None]+bg*(255-alpha[:,:,None])+127)//255
   expected[dst][:,:,:3][mask]=color.astype(np.uint8)[mask];operations[category]+=int(mask.sum())
  def font():
   proof=apply_insert_coin(expected,support,2);mask=support&FONTMASK;covered['font']|=mask;exposed[mask]=False;return proof
  for r in M[tick]:
   cat=r['category'];i=int(r['id']);x,y=int(r['x']),int(r['y'])
   if cat=='enemy'and i in IDS:
    assert r['sheet']=='newsh2.shp'and r['id']==r['tile_id'];a=lookup[x,y];slot=a['slot'];a=dict(a,draw_base=i,origin=[x,y]);actors[slot]=a;apply(filtered(art('enemy-newsh2',i),a['filter']),x,y,'normal','family',slot)
    if slot==0 and tick>=6512:historical_target|=project(art('enemy-newsh2',i),x,y)
    if slot==0 and tick<6200:cycle.append({'tick':tick,'base':i,'cycle_pre':a['cycle'],'origin':[x,y]})
   elif cat in ['enemy','terrain-layer1','terrain-layer2']:assert not support.any(),(tick,'non-family scenery later than type3',r)
   elif cat in ['player','player-projectile']:
    cmds=[q for q in C[tick]if int(q['bank'])==(9 if cat=='player'else 8)and int(q['index'])==i and int(q['x'])==x and int(q['y'])==y];assert len(cmds)==1 and cmds[0]['mirrored']=='1';style=int(cmds[0]['style'])
    if cat=='player':assert i==233 and style in [1,2];apply(art('ship',i),x,y,'half'if style==1 else'shadow','player_halfblend'if style==1 else'player_shadow')
    else:assert i==59 and style in[0,2];apply(art('bullet',i),x,y,'normal'if style==0 else'shadow','projectile')
   elif cat=='effect':
    if not text_applied:textproof=font();text_applied=True
    assert r['sheet']=='explosions-shapes6'and any(b['known_sheet']=='1'and int(b['index'])==i and int(b['origin_x'])==x and int(b['origin_y'])==y for b in BL[tick]);apply(art('explosion-newsh6',i),x,y,'explosion','effect');historical_effects|=project(art('explosion-newsh6',i),x,y)
   else:raise AssertionError((tick,r))
  if not text_applied:textproof=font()
  changed=np.any(actual!=baseline,axis=2);mismatch=np.any(actual!=expected,axis=2);outside=changed&~support
  report={'tick':tick,'whole_frame_RGBA_compared':256000,'mismatch_pixels':int(mismatch.sum()),'outside_original_family_alpha_changes':int(outside.sum()),'changed_pixels':int(changed.sum()),'original_family_alpha_native_support':int(support.sum()),'direct_source_exposed':int(exposed.sum()),'later_operation_support_pixels':{k:int(v.sum())for k,v in covered.items()},'font':textproof,'actors':sorted(actors)}
  if mismatch.any():
   yy,xx=np.where(mismatch);report['first_mismatches']=[{'x':int(x),'y':int(y),'actual':actual[y,x].tolist(),'expected':expected[y,x].tolist(),'baseline':baseline[y,x].tolist(),'support':bool(support[y,x]),'owner':int(owner[y,x])}for y,x in list(zip(yy,xx))[:20]]
  print(json.dumps(report),flush=True);reports.append(report)
  for slot,a in actors.items():
   owned=owner==slot;direct=owned&exposed;actor_reports.append({'tick':tick,'slot':slot,'base':a['draw_base'],'filter':a['filter'],'iced_pre_draw':a['iced'],'origin':a['origin'],'source_native_alpha_support_unclipped':int((art('enemy-newsh2',a['draw_base'])[:,:,3]>0).sum()),'projected_native_alpha_support':int(project(art('enemy-newsh2',a['draw_base']),*a['origin']).sum()),'final_owner_pixels':int(owned.sum()),'direct_source_exposed':int(direct.sum()),'direct_source_changed':int((direct&changed).sum()),'later_covered':int((owned&~exposed).sum())})
   if direct.any():
    wy,wx=np.argwhere(direct&changed if (direct&changed).any()else direct)[0];sy=int(wy)-a['origin'][1]*2;sx=int(wx)-(a['origin'][0]-24)*2;sample=filtered(art('enemy-newsh2',a['draw_base']),a['filter'])[sy,sx];assert np.array_equal(sample,actual[wy,wx]);rawart=art('enemy-newsh2',a['draw_base'])[sy,sx]
    actor_reports[-1]['direct_source_witness']={'native_xy':[int(wx),int(wy)],'source8_xy':[sx*4+2,sy*4+2],'authored_RGBA':rawart.tolist(),'filtered_RGBA':sample.tolist(),'actual_final_RGBA':actual[wy,wx].tolist(),'baseline_RGBA':baseline[wy,wx].tolist()}
  if tick>=6518:
   clear=(historical_target|historical_effects)&~support;assert not np.any(changed&clear);restoration.append({'tick':tick,'previous_target_and_effect_footprint_native_pixels':int((historical_target|historical_effects).sum()),'currently_owned_by_surviving_type3_native_pixels':int(((historical_target|historical_effects)&support).sum()),'no_longer_owned_native_pixels_exactly_equal_paired_baseline':int(clear.sum()),'mismatch_pixels':int((changed&clear).sum())})
  if mismatch.any()or outside.any():
   (O/'pixel-verification.json').write_text(json.dumps({'status':'FAIL diagnostic incomplete','reports':reports,'actor_exposure':actor_reports},indent=2)+'\n');raise AssertionError((tick,'strict native mismatch'))
 assert [r['base']for r in cycle]==[171,171,190,190,209,209,228,228,247,247,266,266]
 assert all(a['projected_native_alpha_support']==a['source_native_alpha_support_unclipped']and a['direct_source_exposed']==a['projected_native_alpha_support']for a in actor_reports if a['slot']==0 and a['tick']<6200)
 filters=[a for a in actor_reports if a['filter']];assert [(a['tick'],a['base'],a['filter'],a['iced_pre_draw'])for a in filters]==[(6514,190,208,0),(6516,209,208,40),(6517,228,9,39)]
 assert all(a['direct_source_changed']>0 for a in filters)
 post=grouped([r for r in rows(A,'late-census')if r['phase']=='post-projectiles'and r['slot']=='0'])
 assert post[6513][0]['armor']=='1'and post[6513][0]['filter']=='208'and post[6513][0]['iced']=='0'
 assert post[6515][0]['armor']=='1'and post[6515][0]['filter']=='208'and post[6515][0]['iced']=='40'
 assert post[6517][0]['avail']=='1'and all(not any(a['slot']==0 and a['tick']==t for a in actor_reports)for t in range(6518,6532))
 pools=grouped(rows(A,'type3-explosion-census'));first_empty_pool=min(t for t in range(6517,6532)if not any(int(r['ttl'])for r in pools[t]));assert first_empty_pool==6528
 visible_effect_ticks=sorted({int(r['tick'])for r in rows(A,'asset-debug-materials')if r['category']=='effect'});assert max(visible_effect_ticks)==6526 and not any(t in visible_effect_ticks for t in range(6527,6532))
 death_pool=[r for r in rows(A,'type3-explosion-census')if r['slot']=='2'and int(r['tick'])>=6517]
 assert [(int(r['tick']),int(r['ttl']),int(r['sprite']),int(r['y']))for r in death_pool[:12]]==[(t,6528-t,121+t-6517,144+(t-6517)*4)for t in range(6517,6529)]
 lifecycle={'target_slot':0,'artificial_original_pulse_ticks':[6513,6515,6517],'filter_direct_witnesses':filters,'target_last_draw_tick':6517,'target_original_removal_phase':'6517 post-projectiles','first_target_absent_draw_tick':6518,'last_visible_effect_material_tick':6526,'first_native_presentation_without_target_or_visible_target_effects':6527,'first_empty_original_effect_pool_tick':first_empty_pool,'death_effect_lifetime':'slot2 reaches y184/ttl1 at6527 beyond native playfield; reaches y188 at6528 and original y>186 removal prevents final133 draw. No ttl-completion/final133 visible claim.','remaining_type3_actors_at_first_clean_tick':[1,2,3],'clean_is_target_lifecycle_only':'Scene still contains unrelated original actors and accepted type3 siblings. Never claim whole frame equals baseline or whole scene empty.','postremoval_restoration':restoration,'first_clean_native_still':str(A/'actual-6527-native2x.png'),'first_pool_empty_native_still':str(A/'actual-6528-native2x.png')}
 report={'status':'PASS exact paired native2x pixels','baseline':P['baseline'],'candidate':P['candidate'],'frames':len(reports),'whole_frame_RGBA_pixels_compared':len(reports)*256000,'mismatches':0,'excluded_pixels':0,'native_dimensions':[640,400],'lifecycle':lifecycle,'all_six_full_cycle_complete_direct_source':True,'sampling':'Exact production SDL_ScaleModeNearest source8x centers2,6 to native2x; no averaging','cycle':cycle,'actor_exposure':actor_reports,'per_frame':reports,'operation_totals':dict(operations),'pack_pins':loaded,'original_blend_fields':original_fields,'original_blend_rows_equal':len(blend),'method':'Differential counterfactual using exact paired baseline, original binary RLE support, authored HDA center samples, independent production integer filters and ordered later player/projectile/shadow/half-opacity/effect/font operators. All actual final full-frame pixels compared with zero tolerance/exclusions.','limits':['Private player-survival; three artificial original Pulse155 requests. No natural combat, ram/body-hit, type16 other-level reuse, later boss53, whole-level, Windows or hardware-GPU claim.','Unrelated scenery uses exact paired baseline, not an independent redraw. Covered pixels are composed and are not claimed directly exposed.','Only original captured native2x PNGs are evidence; no resized/stiched/forged native capture.'],'receipts':{'provenance_sha256':sha(O/'provenance.json'),'verifier_sha256':sha(Path(__file__).resolve()),'candidate_frame_hashes_sha256':sha(A/'frame-hashes.json'),'baseline_frame_hashes_sha256':sha(B/'frame-hashes.json'),'candidate_stream_receipts_sha256':sha(A/'stream-receipts.json'),'baseline_stream_receipts_sha256':sha(B/'stream-receipts.json')}}
 (O/'pixel-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('FINAL',json.dumps({k:v for k,v in report.items()if k not in ['cycle','actor_exposure','per_frame','pack_pins','lifecycle']}),flush=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--first',action='store_true',help='Verify only first6181 actual native2x still after final run summaries exist.');args=ap.parse_args()
 assert P['baseline']=='b2a6e4a1e924aed71630f9f63c0ba4648e920d6d'and P['candidate']=='e976cb6a81aaa2eb99f5ffee14e58f9fc050dcb0'
 pinned_source=subprocess.check_output(['git','show',P['candidate']+':src/render_mirror.c'],cwd=R)
 assert hashlib.sha256(pinned_source).hexdigest()==P['production_src_hashes']['render_mirror.c']=='7a39ffd4959c307c23707ae63c41030cd92ef757375b95f680445ff4f3e85420'
 first()
 if not args.first:full()
