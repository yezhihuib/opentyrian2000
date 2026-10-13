#!/usr/bin/env python3
"""Read-only exact native4 paired oracle and finite fallback pixel identities.
No launches, captures, resizing of evidence, production edits, or old-receipt writes.
"""
from pathlib import Path
from functools import lru_cache
import argparse,collections,csv,gzip,hashlib,json,struct,subprocess,sys
import numpy as np
from PIL import Image
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;P=json.loads((O/'gates-provenance.json').read_text());D=Path(P['data']);R=Path(P['source_root']);PACK=Path(P['builds']['native4-candidate']['pack']);IDS={171,190,209,228,247,266};S=4;SHAPE=(800,1280)
sys.path.insert(0,str(O.parent/'entry-craft-native-pixel-review-20261012'))
from text_oracle import apply_insert_coin,PALETTE,glyphs,TEXT,XY
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
assets={}
@lru_cache(None)
def art(i):
 q=PACK/f'enemy-newsh2-{i}-8.hda';raw=q.read_bytes();assert raw[:4]==b'HDR1'and sha(q)==P['builds']['native4-candidate']['pack_hashes'][q.name];assert struct.unpack('<6I',raw[4:28])==(1010000+i,8,12,14,0,0)and len(raw)==28+96*112*4
 a=np.frombuffer(raw[28:],np.uint8).reshape(112,96,4);assert np.array_equal(a[:,:,3],np.repeat(np.repeat(original(i)[1],8,0),8,1)*255)
 native=a[1::2,1::2].copy();assert np.array_equal(native,np.array(Image.fromarray(a).resize((48,56),Image.Resampling.NEAREST)));assets[i]={'file':str(q),'sha256':sha(q),'opaque_logical_cells':int(original(i)[1].sum()),'full8x_original_alpha_exact':True}
 return native

def clip(x,y,w,h):
 x=(x-24)*S;y*=S;x0=max(0,x);y0=max(0,y);x1=min(264*S,x+w);y1=min(184*S,y+h)
 return None if x0>=x1 or y0>=y1 else(np.s_[y0:y1,x0:x1],np.s_[y0-y:y1-y,x0-x:x1-x])
def font_footprint():
 mask=np.zeros(SHAPE,bool);x,y=XY
 for ch in TEXT:
  if ch==' ':x+=6;continue
  w,h,gm,idx=glyphs[ord(ch)-ord('A')]
  for ax,ay in [(0,0),(2,2)]:
   for yy,xx in zip(*np.where(gm)):
    q=clip(x+int(xx)+ax,y+int(yy)+ay,S,S)
    if q:mask[q[0]]=True
  x+=w+1
 return mask
FONT=font_footprint()

def readframe(d,t,scale):
 p=d/f'actual-{t}-native{scale}x.png';im=Image.open(p).convert('RGBA');h=next(r for r in json.loads((d/'frame-hashes.json').read_text())if r['tick']==t);assert im.size==(320*scale,200*scale)and sha(p)==h['PNG_sha256']and hashlib.sha256(im.tobytes()).hexdigest()==h['RGBA_sha256'];return np.array(im),h

def integrity(d,label):
 s=json.loads((d/'run-summary.json').read_text());assert s['integrity_passed']and s['commit']==P['builds'][label]['commit'];assert s['logic_ticks']==[0,6183]
 rec=json.loads((d/'stream-receipts.json').read_text())
 for n,r in rec.items():
  if r['gzip_sha256']:assert sha(d/(n+'.tsv.gz'))==r['gzip_sha256'],(label,n)
 for n,c in [('frames','coverage_mismatch'),('effects','restored_mismatches'),('rgb-audit','classic_mismatches')]:
  assert [int(r['tick'])for r in rows(d,n)]==[6181,6182,6183]and all(r[c]=='0'for r in rows(d,n)),(label,n)
 assert rec['fire-events']['lines']<=1 and rec['player-shot-emissions']['lines']<=1
 return {'summary_sha256':sha(d/'run-summary.json'),'frame_hashes_sha256':sha(d/'frame-hashes.json'),'stream_receipts_sha256':sha(d/'stream-receipts.json')}

def native4():
 A=O/'native4-candidate-census-4x';B=O/'native4-baseline-census-4x';pins={label:integrity(d,label)for d,label in [(A,'native4-candidate'),(B,'native4-baseline')]};rr=subprocess.check_output(['git','show',P['candidate']+':src/render_mirror.c'],cwd=R);assert hashlib.sha256(rr).hexdigest()==P['production_src_hashes']['render_mirror.c']and b'SDL_SetTextureScaleMode(texture,SDL_ScaleModeNearest)'in rr
 for n in ['asset-debug-materials','late-census','draw-commands','state','collisions','blend-palette']:assert rows(A,n)==rows(B,n),n
 for d in [A,B]:assert np.array_equal(np.array([[int(r[c])for c in ['r','g','b']]for r in rows(d,'blend-palette')],np.uint8),PALETTE)
 isfamily=lambda r:r['role']=='101'and int(r['index'])in IDS
 scene=rows(A,'scene-draw-commands');assert [r for r in scene if not isfamily(r)]==rows(B,'scene-draw-commands');assert all(r['part']=='0'and r['style']=='0'and r['mirrored']=='1'for r in scene if isfamily(r));SC=grouped(scene);M=grouped(rows(A,'asset-debug-materials'));C=grouped(rows(A,'late-census'));reports=[]
 for i in sorted(IDS):art(i)
 for t in [6181,6182,6183]:
  actual,ah=readframe(A,t,4);baseline,bh=readframe(B,t,4);expected=baseline.copy();support=np.zeros(SHAPE,bool);owner=np.full(SHAPE,-1,np.int16);actors=[];ownmasks={}
  pre=[{k:v if k=='phase'else int(v)for k,v in r.items()}for r in C[t]if r['phase']=='pre-sky-25'and r['avail']!='1'and r['bank']=='1'and r['type']=='3'];lookup={(r['x']+r['mapoffset'],r['y']):r for r in pre}
  visible=[r for r in SC[t]if isfamily(r)and int(r['x'])<288 and int(r['x'])+12>24 and int(r['y'])<184 and int(r['y'])+14>0]
  assert [(r['index'],r['x'],r['y'])for r in visible]==[(r['id'],r['x'],r['y'])for r in M[t]if r['category']=='enemy']
  for r in M[t]:
   cat=r['category'];i=int(r['id']);x,y=int(r['x']),int(r['y'])
   if cat=='terrain-layer1':assert not support.any();continue
   if cat=='player':
    q=clip(x,y,24*S,28*S);assert q is None or not support[q[0]].any();continue
   assert cat=='enemy'and r['sheet']=='newsh2.shp'and i in IDS and i==int(r['tile_id']);a=lookup[x,y];slot=a['slot'];assert a['filter']==0 and i==[171,171,190,190,209,209,228,228,247,247,266,266][a['cycle']%12]
   im=art(i);q=clip(x,y,48,56);local=np.zeros(SHAPE,bool)
   if q:
    dst,src=q;mask=im[src][:,:,3]>0;local[dst]=mask;support[dst]|=mask;owner[dst][mask]=slot;expected[dst][mask]=im[src][mask]
   ownmasks[slot]=local;actors.append({'slot':slot,'base':i,'origin':[x,y],'source_opaque_native_pixels':int((im[:,:,3]>0).sum()),'projected_opaque_native_pixels':int(local.sum()),'full_source_in_view':int(local.sum())==int((im[:,:,3]>0).sum())})
  overlay=apply_insert_coin(expected,support,S);changed=np.any(actual!=baseline,axis=2);mismatch=np.any(actual!=expected,axis=2);assert not mismatch.any()and not np.any(changed&~support),(t,'native4 mismatch')
  for a in actors:
   direct=(owner==a['slot'])&~FONT;a.update({'final_owner_pixels':int((owner==a['slot']).sum()),'direct_uncovered_source_pixels':int(direct.sum()),'direct_changed_native_pixels':int((direct&changed).sum())})
   if direct.any():
    yy,xx=np.argwhere(direct&changed if (direct&changed).any()else direct)[0];sx=int(xx)-(a['origin'][0]-24)*S;sy=int(yy)-a['origin'][1]*S;sample=art(a['base'])[sy,sx];assert np.array_equal(sample,actual[yy,xx]);a['witness']={'native_xy':[int(xx),int(yy)],'source8_xy':[sx*2+1,sy*2+1],'source_RGBA':sample.tolist(),'final_RGBA':actual[yy,xx].tolist()}
  report={'tick':t,'native_dimensions':[1280,800],'whole_frame_RGBA_pixels_compared':1024000,'mismatch_pixels':0,'excluded_pixels':0,'outside_original_alpha_changes':0,'changed_native_pixels':int(changed.sum()),'original_alpha_union_pixels':int(support.sum()),'font_write_overlap_pixels':int((support&FONT).sum()),'later_player_rectangles_disjoint':True,'actors':actors,'original_font_overlay':overlay,'candidate_frame':ah,'baseline_frame':bh};reports.append(report);print(json.dumps(report),flush=True)
 result={'status':'PASS exact paired actual native4 pixels','baseline':P['baseline'],'candidate':P['candidate'],'ticks':[6181,6182,6183],'frames':3,'whole_frame_RGBA_pixels_compared':3072000,'mismatches':0,'excluded_pixels':0,'source_density':8,'native_scale':4,'native_dimensions':[1280,800],'mapping':'Original render_mirror SDL_ScaleModeNearest: source8 taps1,3,5,7 per logical axis into actual native4 readback. Evidence PNGs are original complete frames; no resize, stitching or generated screenshot.','authored_source_ids_verified':sorted(assets),'visible_source_ids':sorted({a['base']for r in reports for a in r['actors']if a['projected_opaque_native_pixels']}),'directly_exposed_ids':sorted({a['base']for r in reports for a in r['actors']if a['direct_uncovered_source_pixels']}),'assets':assets,'frames_detail':reports,'pins':pins,'gates_provenance_sha256':sha(O/'gates-provenance.json'),'verifier_sha256':sha(O/'verify-native4-pixels.py'),'limits':['Three bounded no-fire/private-survival native4 frames only; no native4 full held-twice-cycle or lifecycle claim. Native2 full32-frame verification is separate.','Original INSERT COIN glyph/shadow writes are explicitly replayed; source pixels covered by them are not claimed directly visible.','Paired baseline carries unrelated unchanged scenery. No ram, type16, later boss, whole-level, Windows or hardware-GPU claim.']}
 assert result['visible_source_ids']==result['directly_exposed_ids']==sorted(IDS)
 (O/'native4-pixel-verification.json').write_text(json.dumps(result,indent=2)+'\n');print('NATIVE4_PASS',json.dumps({k:v for k,v in result.items()if k not in ['assets','frames_detail','pins']}),flush=True)

def fallback():
 comparisons=[];pins={}
 for label in ['missing266','corrupt209']:
  d=O/(label+'-census');pins[label]=integrity(d,label)
  for t in [6181,6182,6183]:
   a,ah=readframe(d,t,2);b,bh=readframe(O/'baseline-census',t,2);mismatch=int(np.any(a!=b,axis=2).sum());assert mismatch==0;comparisons.append({'case':label,'tick':t,'dimensions':[640,400],'RGBA_pixels_compared':256000,'mismatches':0,'reference':'original paired baseline e6fd18a at same retained tick, before all artificial pulses','candidate_frame':ah,'baseline_frame':bh})
 for label in ['density4-baseline','density4-candidate']:pins[label]=integrity(O/(label+'-census'),label)
 a,ah=readframe(O/'density4-candidate-census',6181,2);b,bh=readframe(O/'density4-baseline-census',6181,2);assert np.array_equal(a,b);comparisons.append({'case':'density4','tick':6181,'dimensions':[640,400],'RGBA_pixels_compared':256000,'mismatches':0,'reference':'density4-baseline e6fd18a','candidate_frame':ah,'baseline_frame':bh})
 result={'status':'PASS exact fallback pixel identity','comparisons':comparisons,'compared_native_RGBA_pixels':1792000,'mismatches':0,'excluded_pixels':0,'pins':pins,'gates_provenance_sha256':sha(O/'gates-provenance.json'),'verifier_sha256':sha(O/'verify-native4-pixels.py'),'limits':['Pixel identity is bounded to missing266/corrupt209 ticks6181–6183 and density4 tick6181. Parent owns broader configuration/state/family gate verification.','No runtime pack swapping, cache invalidation, other corruption cases, or later lifecycle fallback claim.']}
 (O/'fallback-pixel-verification.json').write_text(json.dumps(result,indent=2)+'\n');print('FALLBACK_PASS',json.dumps({k:v for k,v in result.items()if k not in['comparisons','pins']}),flush=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--fallback-only',action='store_true');a=ap.parse_args()
 if not a.fallback_only:native4()
 fallback()
