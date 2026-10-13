#!/usr/bin/env python3
"""Verify exact approved type15 generated-only fractional contour assets.
Original32 source tiles and all1701 records remain read-only lifecycle proof.
"""
from pathlib import Path
import argparse,hashlib,json,re,struct,subprocess,sys
from PIL import Image, ImageChops
sha=lambda b:hashlib.sha256(b).hexdigest()
IDS=[39,41,43,45,91,93,129,131]
ORDER=[91,45,93,39,43,129,41,131]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--original-data',type=Path);a=p.parse_args();repo=Path(__file__).resolve().parents[1];source=repo/'assets/hd/artwork/type15-eightheading-smooth-contour-v2';historical=repo/'assets/hd/artwork/type15-eightheading-v1';given=a.output.absolute();out=given.resolve()
if out.exists() or any(q.is_symlink() for q in [given,*given.parents]) or out==repo or repo in out.parents or out in repo.parents:p.error('Fresh output outside repository, without symlink components, required')
assert all(not q.is_symlink() for q in source.rglob('*'))
m=json.loads((repo/'assets/hd/manifest.json').read_text());f=m['enemy_type15_eightheading_v1'];contract=json.loads((source/'contract.json').read_text())
EXPECTED = {'schema': 'enemy-type15-eightheading-v1',
 'source': 'assets/hd/artwork/type15-eightheading-smooth-contour-v2',
 'source_inventory_sha256': '9bc7fa0d06d4f6077ee48a993d2ac3f511b56e3cf22d95e9a83765a800cf10cc',
 'import_sha256': '93c0e208876a4ac9aed47256f370cfebf577123913cc43226cc311a24d5e1299',
 'bank_id': 1,
 'bank_role': 101,
 'enemy_type': 15,
 'ids': [39, 41, 43, 45, 91, 93, 129, 131],
 'slots': [396, 397, 398, 399, 400, 401, 402, 403],
 'density': 8,
 'logical_size': [24, 28],
 'anchor': [6, 7],
 'runtime_components': [0, 1, 19, 20],
 'selector_order': [91, 45, 93, 39, 43, 129, 41, 131],
 'selector_headings': ['NW', 'N', 'NE', 'W', 'E', 'SW', 'S', 'SE'],
 'selection': 'Original event-selected headings; animate0, no automatic '
              'rotation',
 'source_only_nonpresented_base': 91,
 'original_alpha_exact': False,
 'fallback': 'All eight approved members required before any replacement; '
             '8x-only selected-pack cached fallback is local to this family',
 'entries': [{'id': 39,
              'bank_role': 101,
              'slot': 396,
              'anchor': [6, 7],
              'rgba_fnv1a64': 'cc3d8be70ed2e620'},
             {'id': 41,
              'bank_role': 101,
              'slot': 397,
              'anchor': [6, 7],
              'rgba_fnv1a64': '80d5e7bb507fe084'},
             {'id': 43,
              'bank_role': 101,
              'slot': 398,
              'anchor': [6, 7],
              'rgba_fnv1a64': '3228caecc8f7abe8'},
             {'id': 45,
              'bank_role': 101,
              'slot': 399,
              'anchor': [6, 7],
              'rgba_fnv1a64': '33f828b2c95baa5a'},
             {'id': 91,
              'bank_role': 101,
              'slot': 400,
              'anchor': [6, 7],
              'rgba_fnv1a64': '452516abee3a1d95'},
             {'id': 93,
              'bank_role': 101,
              'slot': 401,
              'anchor': [6, 7],
              'rgba_fnv1a64': 'c8296a713b1af965'},
             {'id': 129,
              'bank_role': 101,
              'slot': 402,
              'anchor': [6, 7],
              'rgba_fnv1a64': '1f937a94539eb9cb'},
             {'id': 131,
              'bank_role': 101,
              'slot': 403,
              'anchor': [6, 7],
              'rgba_fnv1a64': 'b01b2fcfaa46aaf0'}],
 'source_inventory': 'SHA256SUMS.json',
 'art_revision': 'smooth-contour-v2',
 'contour_contract': 'Exact approved fractional outer contours and genuine '
                     'apertures inside original24x28 rectangles; original '
                     'indexed alpha, collision, registration and source events '
                     'unchanged.'}
assert {k:v for k,v in f.items()if k!='runtime_status'}==EXPECTED
assert sha((source/'SHA256SUMS.json').read_bytes())==f['source_inventory_sha256']
assert sha((source/'IMPORT.json').read_bytes())==f['import_sha256']
imp=json.loads((source/'IMPORT.json').read_text());assert imp['source_inventory_sha256']==f['source_inventory_sha256']
assert len(imp['files'])==len({e['path']for e in imp['files']})
assert {e['path']for e in imp['files']}=={str(q.relative_to(source))for q in source.rglob('*')if q.is_file()and q.name!='IMPORT.json'}
for e in imp['files']:
 q=source/e['path'];assert source in q.resolve().parents and sha(q.read_bytes())==e['sha256'],e['path']
inv=json.loads((source/'SHA256SUMS.json').read_text());assert len(inv)==70
for name,h in inv.items():assert sha((source/name).read_bytes())==h,name
assert contract['bank_id']==1 and contract['namespace']==101 and contract['logical_size']==[24,28]and contract['density']==8 and contract['anchor']==[6,7]and contract['quadrant_offsets']==[0,1,19,20]and contract['selector_order']==ORDER
# Historical source records are immutable evidence, never reconstruction inputs.
assert sha((historical/'inventory.json').read_bytes())=='17780d02fef4c08636d22651c1299e3641234d0b992f7283fe32e64d92ca67d9'
assert sha((historical/'IMPORT.json').read_bytes())=='ee659ea7365f457250ddb15fd11f95c0ddb6ca31f80f51156b98adf0f6b6e383'
for e in json.loads((historical/'IMPORT.json').read_text())['files']:assert sha((historical/e['path']).read_bytes())==e['sha256']
proof=json.loads((historical/'proof/type15-source-proof.json').read_text());life=json.loads((historical/'proof/type15-lifecycle.json').read_text());assert proof['selector_order']==ORDER and proof['record15']['animate']==0 and proof['record15']['explosiontype']==3
assert life['record']==15 and life['filter']['enemyground']is False and life['filter']['normal_hit_palette_flash']is False and life['filter']['ice_blue_filter']is False
assert proof['reuse_audit']['loaded_records']==1701 and [e['id']for e in proof['reuse_audit']['base_users']]==[15]and[e['id']for e in proof['reuse_audit']['quadrant_overlap_users']]==[15]
for i in IDS:
 mask=Image.open(historical/f'masks/alpha-{i}.png').convert('L');e=next(x for x in proof['frames']if x['base_id']==i);assert mask.size==(24,28)and set(mask.tobytes())=={0,255}and sha(mask.tobytes())==e['alpha_sha256']
if a.original_data:
 for name,h in proof['original_sources_sha256'].items():assert sha((a.original_data/name).read_bytes())==h,name
 original=(a.original_data/'newsh2.shp').read_bytes()
 for b in IDS:
  mask=bytearray(672);indices=bytearray(672)
  for off,x0,y0 in[(0,0,0),(1,12,0),(19,0,14),(20,12,14)]:
   pos=struct.unpack_from('<H',original,2*(b+off-1))[0];linear=0
   while original[pos]!=15:
    code=original[pos];pos+=1;linear+=code&15
    for _ in range(code>>4):
     y,x=divmod(linear,12);assert y<14;mask[(y+y0)*24+x+x0]=255;indices[(y+y0)*24+x+x0]=original[pos];pos+=1;linear+=1
  e=next(x for x in proof['frames']if x['base_id']==b);assert sha(mask)==e['alpha_sha256']and sha(indices)==e['indices_sha256'];assert mask==Image.open(historical/f'masks/alpha-{b}.png').convert('L').tobytes()
 h=(a.original_data/'tyrian.hdt').read_bytes();reader=(repo/'src/episodes.c').read_text();formats={'u8':'B','s8':'b','u16':'H','s16':'h'}
 def schema(var):return[(x[2],formats[x[1]],int(x[3]))for x in re.finditer(r'fread_(u8|s8|u16|s16)_die\(\s*&?'+var+r'\[i\]\.(\w+),\s*(\d+),\s*f\)',reader)]
 pos=struct.unpack_from('<i',h)[0]+14+1638*sum(n*struct.calcsize(fmt)for _,fmt,n in schema('weapons'))+61*82+sum(n*z for n,z in[(55,37),(7,37),(19,41),(38,86),(12,37)]);users=[];count=0;tiles={b+d for b in IDS for d in[0,1,19,20]}
 for i in list(range(851))+list(range(1001,1851)):
  r={'id':i};count+=1
  for name,fmt,n in schema('enemyDat'):
   vals=list(struct.unpack_from('<'+str(n)+fmt,h,pos));pos+=n*struct.calcsize(fmt);r[name]=vals[0]if n==1 else vals
  if i==15:assert r==proof['record15']
  if r['shapebank']==1:
   bases=set(r['egraphic'])-{0,999}
   if r['dani']==0 and r['dgr']:bases.add(r['dgr'])
   if {b+d for b in bases for d in([0,1,19,20]if r['esize']==1 else[0])}&tiles:users.append(i)
 assert count==1701 and users==[15]
subprocess.run([sys.executable,str(source/'rebuild.py'),'--output',str(out)],check=True)
for e,pin in zip(contract['entries'],f['entries']):
 i=e['id'];assert i==pin['id'];name=f'enemy-newsh2-{i}-8';raw=(out/(name+'.hda')).read_bytes();png=(out/(name+'.png')).read_bytes();header=[1010000+i,8,24,28,6,7]
 assert raw[:28]==b'HDR1'+struct.pack('<6I',*header)and len(raw)==28+192*224*4
 assert sha(raw)==e['HDA_sha256']and sha(raw[28:])==e['RGBA_sha256']and sha(png)==e['PNG_sha256']
 im=Image.open(out/(name+'.png'));assert im.mode=='RGBA'and im.size==(192,224)
 alpha=im.getchannel('A');assert any(0<v<255 for v in alpha.tobytes())
 assert alpha.tobytes()==Image.open(source/f'masks/authored-alpha-{i}-8.png').tobytes()
 assert list(alpha.getbbox())==list(alpha.point(lambda v:255 if v>=128 else 0).getbbox())==[v*8 for v in e['original_bbox_logical']]
 orig=Image.open(source/f'masks/original-alpha-{i}-24x28.png');assert orig.tobytes()==Image.open(historical/f'masks/alpha-{i}.png').tobytes();orig8=orig.resize(im.size,Image.Resampling.NEAREST)
 for label,delta in [('additions',ImageChops.subtract(alpha,orig8)),('removals',ImageChops.subtract(orig8,alpha))]:
  q=source/f'masks/support-{label}-{i}.png';assert delta.tobytes()==Image.open(q).tobytes() and sha(q.read_bytes())==e[f'support_{label}_sha256']
 for aperture in e['authored_apertures']:
  crop=alpha.crop(aperture['bbox_density8']);assert any(v==0 for v in crop.tobytes()) and sum(v<128 for v in crop.tobytes())==aperture['area_density8']
 stamp=0xcbf29ce484222325
 for b in raw[28:]:stamp=((stamp^b)*0x100000001b3)&0xffffffffffffffff
 assert pin['rgba_fnv1a64']==e['RGBA_fnv1a64']==f'{stamp:016x}'
 for key in['default_preview_pack','default_debug_pack']:
  pack=m['packs'][m[key]];assert pack['count']==len(pack['files']);entry=pack['files'][name+'.hda'];assert entry['header_u32']==header and(repo/'assets/hd/packs'/m[key]/(name+'.hda')).read_bytes()==raw and entry['sha256']==sha(raw)
  assert(repo/entry['source_png']).read_bytes()==png and entry['source_png_sha256']==sha(png)
  assert m['source_pngs'][sha(raw)]=={'path':entry['source_png'],'sha256':sha(png),'RGBA_sha256':sha(raw[28:])}
 for pn,pack in m['packs'].items():
  for density in[4,8]:assert(f'enemy-newsh2-{i}-{density}.hda'in pack['files'])==(density==8 and pn in[m['default_preview_pack'],m['default_debug_pack']])
print('PASS eight exact generated-only fractional contours, full delta masks and apertures, namespace101, unchanged finite packs, original event-selected record; NW91 source-only'+('; original32 tiles/all1701 records verified'if a.original_data else''))
