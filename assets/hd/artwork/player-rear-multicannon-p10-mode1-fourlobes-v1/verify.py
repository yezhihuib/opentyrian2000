#!/usr/bin/env python3
"""Finite frozen-art and exact catalog-inverse verification. No game data needed."""
from pathlib import Path
import argparse,copy,hashlib,json,struct
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[3]
sha=lambda b:hashlib.sha256(b).hexdigest()
def fnv(b):
 h=14695981039346656037
 for v in b:h=((h^v)*1099511628211)&0xffffffffffffffff
 return f'0x{h:016x}'
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--package-only',action='store_true');args=ap.parse_args()
 files=json.loads((ROOT/'file-manifest.json').read_text())['files']
 actual={str(p.relative_to(ROOT))for p in ROOT.rglob('*')if p.is_file()}
 assert actual==set(files)|{'file-manifest.json'},'Unexpected/missing package file'
 for rel,pin in files.items():assert sha((ROOT/rel).read_bytes())==pin,rel
 freeze=json.loads((ROOT/'freeze.json').read_text());binding=json.loads((ROOT/'binding.json').read_text())
 assert sha((ROOT/'output/candidate-contract.json').read_bytes())==freeze['reviewed_candidate_contract_sha256']=='07e98e2c6af206d72ec19d6a62614b9d14c0966f0ed9b510993c75f26cca767c'
 assert freeze['reviewed_candidate_verification_sha256']=='ebf58521622bc7730eef1708e0821ce65162f2c54e1c086616931a8e30315f5b'
 for rel,pin in freeze['frozen_files'].items():assert sha((ROOT/rel).read_bytes())==pin,rel
 assert sha((ROOT/'src/author-candidates.cjs').read_bytes())==freeze['reviewed_generator_sha256']
 for e in json.loads((ROOT/'inputs.json').read_text())['inputs']:assert sha((ROOT/e['path']).read_bytes())==e['sha256']
 assert {(e['source_id'],e['density'])for e in binding['resources']}=={(i,d)for i in [203,222]for d in [4,8]}
 payloads={}
 for e in binding['resources']:
  rid=e['source_id'];d=e['density'];raw=(ROOT/e['rgba']).read_bytes();hb=(ROOT/e['package_hda']).read_bytes();png=(ROOT/e['png']).read_bytes()
  assert len(raw)==168*d*d*4 and sha(raw)==e['rgba_sha256'] and fnv(raw)==e['rgba_fnv1a64']
  assert hb==struct.pack('<4s4I2i',b'HDR1',1310000+rid,d,12,14,0,0)+raw and sha(hb)==e['hda_sha256']
  assert sha(png)==e['png_sha256']
  assert png[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',png[16:24])==(12*d,14*d)
  assert all(raw[p:p+3]==b'\0\0\0' for p in range(0,len(raw),4)if not raw[p+3])
  w=12*d;h=14*d;assert not any(raw[3:4*w*d:4])and not any(raw[4*w*13*d+3::4])
  points=[p for p in range(w*h)if raw[4*p+3]]
  assert [min(p%w for p in points),min(p//w for p in points),1+max(p%w for p in points),1+max(p//w for p in points)]==[0,d,12*d,13*d]
  payloads[rid,d]=raw
 for d in [4,8]:
  w=12*d;h=14*d;a=payloads[203,d];assert b''.join(a[4*(y*w+x):4*(y*w+x+1)]for y in range(h)for x in range(w-1,-1,-1))==payloads[222,d]
 # This family contains only generated art, public style metadata, source code,
 # semantic hashes, and documentation. Private previews/audits are not inputs.
 assert not any(any(part in {'local-reference','previews','rebuild-check','original-inputs'}for part in Path(rel).parts)for rel in actual)
 for rel in actual:
  if Path(rel).suffix in {'.py','.cjs','.md','.json'}:assert ('/'+'workspace'+'/').encode() not in (ROOT/rel).read_bytes(),rel
 if args.package_only:
  print('PASS: frozen reviewed bytes, exact mirrors, fixed bounds, four HDR1 resources, public-safe package.');return
 manifest=json.loads((REPO/'assets/hd/manifest.json').read_text());inverse=copy.deepcopy(manifest)
 projection=json.loads((ROOT/'catalog-projection.json').read_text());key=projection['family_key'];family=inverse.pop(key)
 assert family['binding_sha256']==sha((ROOT/'binding.json').read_bytes())
 assert family['art_file_manifest_sha256']==sha((ROOT/'file-manifest.json').read_bytes())
 assert family['freeze_sha256']==sha((ROOT/'freeze.json').read_bytes())
 assert family['ids']==[203,222]and family['densities']==[4,8]and family['role']==131
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
   else:assert name not in item['files']and not (REPO/f'assets/hd/packs/{pack}/{name}').exists()
 assert sha((json.dumps(inverse,indent=2)+'\n').encode())==projection['baseline_manifest_sha256'],'Catalog inverse differs from exact baseline bytes'
 assert sha(json.dumps(inverse,sort_keys=True,separators=(',',':')).encode())==projection['baseline_canonical_manifest_sha256']
 print('PASS: frozen artwork, exact HDR1, both default packs621, four source mappings, and byte-exact baseline catalog inverse. No game/runtime acceptance claim.')
if __name__=='__main__':main()
