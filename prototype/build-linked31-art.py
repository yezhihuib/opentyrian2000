#!/usr/bin/env python3
"""Rebuild and audit exactly eight generated linked31 assets. No game runs.
Original data is optional read-only occupancy/lifecycle evidence, never RGB input.
"""
from pathlib import Path
import argparse, hashlib, json, re, struct, subprocess, sys
from PIL import Image
sha=lambda b:hashlib.sha256(b).hexdigest()
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,required=True)
p.add_argument('--original-data',type=Path,help='Optional original game-data directory, read only')
a=p.parse_args();repo=Path(__file__).resolve().parents[1];source=repo/'assets/hd/artwork/linked31-assembly-v1'
given=a.output.absolute();out=given.resolve()
if any(q.is_symlink() for q in [given,*given.parents]) or out.exists() or out==repo or repo in out.parents or out in repo.parents:
 p.error('Choose a fresh output outside the repository, without symlink components')
assert all(not q.is_symlink() for q in source.rglob('*'))
m=json.loads((repo/'assets/hd/manifest.json').read_text());f=m['linked31_installation_v1']
assert f['source']=='assets/hd/artwork/linked31-assembly-v1' and f['density']==8 and f['logical_size']==[24,28]
assert f['actor_types']==[42,43,44,45] and f['link']==31 and f['runtime_components']==[0,1,19,20]
assert f['original_relative_actor_y']==1
contract=json.loads((source/'contract.json').read_text());inventory=json.loads((source/'inventory.json').read_text());imp=json.loads((source/'IMPORT.json').read_text())
assert sha((source/'inventory.json').read_bytes())==f['source_inventory_sha256']==imp['source_inventory_sha256']
assert len(imp['files'])==len({e['path'] for e in imp['files']})
assert {e['path'] for e in imp['files']}=={str(q.relative_to(source)) for q in source.rglob('*') if q.is_file() and q.name!='IMPORT.json'}
for e in imp['files']:
 q=source/e['path'];assert source in q.resolve().parents and sha(q.read_bytes())==e['sha256'],e['path']
assert contract['registered_master_size']==[1536,896] and contract['actor_relative_scene_y']==1
assert contract['terrain_assembly_crop']==[192,224,576,672] and contract['actor_assembly_crop']==[960,232,1344,680]
ids=[161,162,171,172,15,17,53,55]
assert len(contract['entries'])==len(f['entries'])==8
for k,(c,b) in enumerate(zip(contract['entries'],f['entries'])):
 terrain=k<4;role=201 if terrain else 101;anchor=[0,0] if terrain else [6,7]
 assert c['kind']==b['kind']==('terrain' if terrain else 'actor') and c['source_id']==b['id']==ids[k]
 assert c['hda_id']==role*10000+ids[k] and c['logical_size']==[24,28] and c['density']==8
 assert c['anchor']==b['anchor']==anchor and b['bank_role']==role and b['slot']==374+k
 assert c['bank']==('shapesz.dat' if terrain else 'newsh2.shp') and c['actor_type']==(None if terrain else 38+k)
 assert c['assembly_crop']==[(k%4)%2*192,(k%4)//2*224,(k%4)%2*192+192,(k%4)//2*224+224]
for guard in json.loads((source/'proof/context-proof.json').read_text())['guards']:
 assert sha((repo/guard['source_png']).read_bytes())==guard['sha256']
proof=json.loads((source/'proof/composite-proof.json').read_text());reuse=json.loads((source/'proof/global-reuse-events.json').read_text())
assert reuse['record_count']==1701 and [r['id'] for r in reuse['bank1_users_of_bases']]==[42,43,44,45]
assert len(reuse['link31_events'])==4 and all(e['eventtime']==3200 and e['dat4']==31 for e in reuse['link31_events'])
if a.original_data:
 original=(a.original_data/'shapesz.dat').read_bytes();assert sha(original)==proof['shapesz_sha256'];pos=0
 for i in range(1,601):
  blank=original[pos];pos+=1;indices=bytes(672) if blank else original[pos:pos+672];pos+=0 if blank else 672
  if i in ids[:4]: assert len(indices)==672 and indices.count(0)==0
 original=(a.original_data/'newsh2.shp').read_bytes();assert sha(original)==proof['newsh2_sha256']
 for record in proof['actor_records']:
  assert record['base'] in ids[4:]
  for part in record['parts']:
   pos=struct.unpack_from('<H',original,2*(part['id']-1))[0];assert pos==part['offset'];start=pos;linear=0;mask=bytearray(168);indices=bytearray(168)
   while original[pos]!=15:
    code=original[pos];pos+=1;linear+=code&15;count=code>>4;assert 0<=linear<=168 and linear+count<=168
    mask[linear:linear+count]=bytes([255])*count;indices[linear:linear+count]=original[pos:pos+count];linear+=count;pos+=count
   assert pos+1-start==part['record_bytes'] and set(mask)=={255} and part['opaque']==168 and sha(indices)==part['index_sha256']
 data=(a.original_data/'tyrian.hdt').read_bytes();reader=(repo/'src/episodes.c').read_text();formats={'u8':'B','s8':'b','u16':'H','s16':'h'}
 def schema(var):return [(m[2],formats[m[1]],int(m[3])) for m in re.finditer(r'fread_(u8|s8|u16|s16)_die\(\s*&?'+var+r'\[i\]\.(\w+),\s*(\d+),\s*f\)',reader)]
 ws,es=schema('weapons'),schema('enemyDat');assert len(es)==28 and ws
 pos=struct.unpack_from('<i',data)[0]+14+1638*sum(n*struct.calcsize(fmt) for _,fmt,n in ws)+61*82+sum(n*s for n,s in [(55,37),(7,37),(19,41),(38,86),(12,37)]);users=[]
 for i in list(range(851))+list(range(1001,1851)):
  r={}
  for name,fmt,n in es:
   vals=list(struct.unpack_from('<'+str(n)+fmt,data,pos));pos+=n*struct.calcsize(fmt);r[name]=vals[0] if n==1 else vals
  if r['shapebank']==1 and (set(r['egraphic'])&set(ids[4:]) or (not r['dani'] and r['dgr'] in ids[4:])):users.append(i)
  if i in [42,43,44,45]:
   assert r['egraphic'][0]==ids[i-38] and r['ani']==1 and r['armor']==12
   assert r['explosiontype']==9 and not ((r['explosiontype']&1)==0) and r['explosiontype']>>1==4
   assert [r[k] for k in ['dgr','dani','dlevel','eenemydie']]==[0]*4
 assert users==[42,43,44,45]
subprocess.run([sys.executable,str(source/'rebuild.py'),str(out)],check=True)
for k,c in enumerate(contract['entries']):
 prefix='terrain-shapesz' if k<4 else 'enemy-newsh2';name=f'{prefix}-{ids[k]}-8';raw=(out/f"{c['hda_id']}.hda").read_bytes();png=(out/(name+'.png')).read_bytes();expected=inventory['outputs'][k]
 header=[c['hda_id'],8,24,28,*c['anchor']]
 assert raw[:28]==b'HDR1'+struct.pack('<6I',*header) and len(raw)==28+192*224*4 and set(raw[31::4])=={255}
 assert sha(raw)==expected['HDA_SHA256'] and sha(raw[28:])==expected['RGBA_SHA256'] and sha(png)==expected['PNG_SHA256']
 assert Image.open(out/(name+'.png')).mode=='RGBA' and Image.open(out/(name+'.png')).size==(192,224)
 for key in ['default_preview_pack','default_debug_pack']:
  pack=m['packs'][m[key]];assert pack['count']==len(pack['files']);e=pack['files'][name+'.hda']
  assert e['header_u32']==header and (repo/'assets/hd/packs'/m[key]/(name+'.hda')).read_bytes()==raw and e['sha256']==sha(raw)
  assert (repo/e['source_png']).read_bytes()==png and e['source_png_sha256']==sha(png)
  indexed=m['source_pngs'][sha(raw)];assert indexed['path']==e['source_png'] and indexed['sha256']==sha(png) and indexed['RGBA_sha256']==sha(raw[28:])
 for pn,pack in m['packs'].items():
  for density in [4,8]:assert (f'{prefix}-{ids[k]}-{density}.hda' in pack['files'])==(density==8 and pn in [m['default_preview_pack'],m['default_debug_pack']])
print('PASS exact eight generated PNG/RGBA/HDR1 members, finite identities/anchors, opaque support, source and unchanged-neighbor guards'+('; original terrain/RLE occupancy and all1701 records verified' if a.original_data else ''))
