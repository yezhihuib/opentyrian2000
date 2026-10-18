#!/usr/bin/env python3
"""Finite exactA2 frozen-art and catalog-inverse checks. No game inputs needed."""
from pathlib import Path
import argparse,copy,hashlib,json,struct
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[3]
sha=lambda b:hashlib.sha256(b).hexdigest()
def fnv(b):
 h=14695981039346656037
 for v in b:h=((h^v)*1099511628211)&0xffffffffffffffff
 return f'0x{h:016x}'
def groups(mask,w,h):
 seen=set();groups=[]
 for i,v in enumerate(mask):
  if not v or i in seen:continue
  q=[i];seen.add(i)
  for p in q:
   for dy in [-1,0,1]:
    for dx in [-1,0,1]:
     x=p%w+dx;y=p//w+dy;j=y*w+x
     if (dx or dy)and 0<=x<w and 0<=y<h and mask[j]and j not in seen:seen.add(j);q.append(j)
  groups.append(len(q))
 return groups

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--package-only',action='store_true');args=ap.parse_args()
 files=json.loads((ROOT/'file-manifest.json').read_text())['files'];actual={str(p.relative_to(ROOT))for p in ROOT.rglob('*')if p.is_file()}
 assert actual==set(files)|{'file-manifest.json'},'Unexpected/missing package file'
 for rel,pin in files.items():assert sha((ROOT/rel).read_bytes())==pin,rel
 freeze=json.loads((ROOT/'freeze.json').read_text());binding=json.loads((ROOT/'binding.json').read_text())
 assert sha((ROOT/'output/candidate-contract.json').read_bytes())==freeze['reviewed_candidate_contract_sha256']=='9000e13ba498c92f797823c5f62193054a5e4a9b6ea050d695702f155a10b94f'
 assert freeze['approved_variant']=='A2'and freeze['status']=='FROZEN_EXACT_A2_AFTER_RENEWED_NATIVE_SIZE_VISUAL_APPROVAL'
 for rel,pin in freeze['frozen_files'].items():assert sha((ROOT/rel).read_bytes())==pin,rel
 assert len(freeze['frozen_files'])==11
 assert sha((ROOT/'src/author-a2.cjs').read_bytes())==freeze['reviewed_generator_sha256']=='0e0f9b717006ec0996e374743b1de0a7a83eb5427d61209c0d54b6b5584d5a94'
 assert {(e['source_id'],e['density'])for e in binding['resources']}=={(i,d)for i in [43,5]for d in [4,8]}
 payloads={}
 for e in binding['resources']:
  rid=e['source_id'];d=e['density'];raw=(ROOT/e['rgba']).read_bytes();hb=(ROOT/e['package_hda']).read_bytes();png=(ROOT/e['png']).read_bytes()
  assert len(raw)==168*d*d*4 and sha(raw)==e['rgba_sha256']and fnv(raw)==e['rgba_fnv1a64']
  assert hb==struct.pack('<4s4I2i',b'HDR1',1310000+rid,d,12,14,0,0)+raw and sha(hb)==e['hda_sha256']and fnv(hb)==e['hda_fnv1a64']
  assert sha(png)==e['png_sha256']and png[:8]==b'\x89PNG\r\n\x1a\n'and struct.unpack('>II',png[16:24])==(12*d,14*d)
  assert all(raw[p:p+3]==b'\0\0\0'for p in range(0,len(raw),4)if not raw[p+3])
  w=12*d;h=14*d;points=[p for p in range(w*h)if raw[4*p+3]]
  assert [min(p%w for p in points),min(p//w for p in points),1+max(p%w for p in points),1+max(p//w for p in points)]==[0,d,12*d,13*d]
  assert len(groups([raw[p+3]for p in range(0,len(raw),4)],w,h))==1
  assert len(groups([raw[p+3]>=160 and raw[p]>=250 and raw[p+1]>=220 and raw[p+2]>=60 for p in range(0,len(raw),4)],w,h))==5
  payloads[rid,d]=raw
 for d in [4,8]:
  w=12*d;h=14*d;a=payloads[43,d]
  assert b''.join(a[4*(y*w+x):4*(y*w+x+1)]for y in range(h)for x in range(w-1,-1,-1))==payloads[5,d]
 native=json.loads((ROOT/'native-core-projection.json').read_text())['rows'];assert len(native)==12
 for e in native:
  d=e['density'];s=e['display_scale'];raw=payloads[e['id'],d];w=12*s;h=14*s;mask=[]
  for y in range(h):
   for x in range(w):
    sx=((2*x+1)*d)//(2*s);sy=((2*y+1)*d)//(2*s);p=4*(sy*12*d+sx)
    mask.append(raw[p+3]>=160 and raw[p]>=250 and raw[p+1]>=220 and raw[p+2]>=60)
  assert groups(mask,w,h)==e['bright_components8']and len(e['bright_components8'])==5
 for rel in actual:
  assert not any(part in {'local-reference','previews','original-inputs'}for part in Path(rel).parts)
  if Path(rel).suffix in {'.py','.cjs','.md','.json'}:assert ('/'+'workspace'+'/').encode()not in (ROOT/rel).read_bytes(),rel
 if args.package_only:
  print('PASS: exactA2 frozen bytes, exact mirrors, fixed bounds, five finite native core groups, four HDR1 resources, generated-only portable package.');return
 manifest=json.loads((REPO/'assets/hd/manifest.json').read_text());inverse=copy.deepcopy(manifest);projection=json.loads((ROOT/'catalog-projection.json').read_text());family=inverse.pop(projection['family_key'])
 assert family['binding_sha256']==sha((ROOT/'binding.json').read_bytes())and family['art_file_manifest_sha256']==sha((ROOT/'file-manifest.json').read_bytes())and family['freeze_sha256']==sha((ROOT/'freeze.json').read_bytes())
 assert family['ids']==[43,5]and family['densities']==[4,8]and family['role']==131
 assert set(projection['default_packs'])=={manifest['default_preview_pack'],manifest['default_debug_pack']}
 for e in binding['resources']:
  hb=(ROOT/e['package_hda']).read_bytes();png=(ROOT/e['png']).read_bytes();hsha=e['hda_sha256'];name=e['filename'];source=e['catalog_source_png']
  assert (REPO/source).read_bytes()==png
  assert inverse['source_pngs'].pop(hsha)=={'path':source,'sha256':e['png_sha256'],'RGBA_sha256':e['rgba_sha256']}
  assert set(e['pack_paths'])=={f'assets/hd/packs/{pack}/{name}'for pack in projection['default_packs']}
  for pack,item in inverse['packs'].items():
   assert item['count']==len(item['files'])
   if pack in projection['default_packs']:
    assert (REPO/f'assets/hd/packs/{pack}/{name}').read_bytes()==hb
    assert item['files'].pop(name)=={'sha256':hsha,'header_u32':[e['key'],e['density'],12,14,0,0],'source_png':source,'source_png_sha256':e['png_sha256']}
    item['count']-=1
   else:assert name not in item['files']and not(REPO/f'assets/hd/packs/{pack}/{name}').exists()
 assert sha((json.dumps(inverse,indent=2)+'\n').encode())==projection['baseline_manifest_sha256'],'Byte-exact baseline inverse differs'
 assert sha(json.dumps(inverse,sort_keys=True,separators=(',',':')).encode())==projection['baseline_canonical_manifest_sha256']
 print('PASS: exactA2 package, both default catalogs625, four PNG mappings, one new family and byte-exact catalog inverse. Separate runtime qualification required.')
if __name__=='__main__':main()
