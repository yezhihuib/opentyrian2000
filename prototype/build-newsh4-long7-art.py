#!/usr/bin/env python3
"""Rebuild the finite approved bank2 family. Optional originals are read-only proof,
never RGB art inputs. This tool does not run the game or claim runtime acceptance.
"""
from pathlib import Path
import argparse,hashlib,json,re,struct,subprocess,sys
from PIL import Image
sha=lambda b:hashlib.sha256(b).hexdigest()
IDS=[153,155,157,159,191,193,195]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--original-data',type=Path);a=p.parse_args();repo=Path(__file__).resolve().parents[1];source=repo/'assets/hd/artwork/newsh4-long7-v1';given=a.output.absolute();out=given.resolve()
if out.exists() or any(q.is_symlink() for q in [given,*given.parents]) or out==repo or repo in out.parents or out in repo.parents:p.error('Fresh output outside the repository, without symlink components, required')
assert all(not q.is_symlink() for q in source.rglob('*'))
m=json.loads((repo/'assets/hd/manifest.json').read_text());f=m['newsh4_long7_v1'];contract=json.loads((source/'contract.json').read_text());inventory=json.loads((source/'inventory.json').read_text());imp=json.loads((source/'IMPORT.json').read_text())
assert f['source']=='assets/hd/artwork/newsh4-long7-v1' and f['density']==8 and f['logical_size']==[24,28] and f['assembly_size']==[168,28]
assert f['ids']==IDS and f['slots']==list(range(382,389)) and f['actor_types']==list(range(66,73)) and f['bank_id']==2 and f['link']==1
assert f['runtime_components']==[0,1,19,20] and f['excluded_actor_types']==list(range(73,80))
assert sha((source/'inventory.json').read_bytes())==f['source_inventory_sha256']==imp['source_inventory_sha256']=='dd6c3f91282e98b9dc583701267ef4963833bbc7ec0dbaaa8ade450be2726fbb'
assert len(imp['files'])==len({e['path'] for e in imp['files']})
assert {e['path'] for e in imp['files']}=={str(q.relative_to(source)) for q in source.rglob('*') if q.is_file() and q.name!='IMPORT.json'}
for e in imp['files']:
 q=source/e['path'];assert source in q.resolve().parents and sha(q.read_bytes())==e['sha256'],e['path']
assert contract['bank_id']==2 and contract['asset_namespace']==102 and contract['logical_assembly_size']==[168,28]
assert contract['registered_master_size']==[1536,512] and contract['assembly_crop']==[96,144,1440,368] and contract['matte_RGB']==[12,8,0]
assert len(contract['entries'])==len(f['entries'])==7
mask=Image.open(source/'masks/alpha-assembly8x.png').convert('L');assert mask.size==(1344,224) and set(mask.tobytes())=={0,255}
for k,(c,b) in enumerate(zip(contract['entries'],f['entries'])):
 assert c['base']==b['id']==IDS[k] and c['enemy_type']==b['enemy_type']==66+k and b['kind']=='actor'
 assert c['hda_id']==1020000+IDS[k] and c['logical_size']==[24,28] and c['density']==8 and c['anchor']==b['anchor']==[6,7]
 assert c['runtime_quad_offsets']==[0,1,19,20] and c['assembly_crop']==[k*192,0,(k+1)*192,224] and b['bank_role']==102 and b['slot']==382+k
reuse=json.loads((source/'proof/reuse-events.json').read_text());proof=json.loads((source/'proof/source-composites.json').read_text());life=json.loads((source/'proof/lifecycle-proof.json').read_text())
assert reuse['records_audited']==1701 and [r['id'] for r in reuse['users']]==list(range(66,73))
assert life['base_armor_all7']==50 and life['enemyground'] and life['explonum']==12 and life['post3500_armor_override_events']==[]
if a.original_data:
 original=(a.original_data/'newsh4.shp').read_bytes();assert sha(original)==proof['newsh4_sha256']
 for k,record in enumerate(proof['records']):
  assert record['base']==IDS[k];component=Image.new('L',(24,28));assert [v['id'] for v in record['parts']]==[IDS[k]+v for v in [0,1,19,20]]
  for part,(ox,oy) in zip(record['parts'],[(0,0),(12,0),(0,14),(12,14)]):
   pos=struct.unpack_from('<H',original,2*(part['id']-1))[0];assert pos==part['offset'];start=pos;linear=0;support=bytearray(168);indices=bytearray(168)
   while original[pos]!=15:
    code=original[pos];pos+=1;linear+=code&15;count=code>>4;assert 0<=linear<=168 and linear+count<=168
    support[linear:linear+count]=bytes([255])*count;indices[linear:linear+count]=original[pos:pos+count];linear+=count;pos+=count
   assert pos+1-start==part['record_bytes'] and support.count(255)==part['opaque'] and sha(indices)==part['index_sha256']
   component.paste(Image.frombytes('L',(12,14),bytes(support)),(ox,oy))
  assert list(component.getbbox())==record['alpha_bbox']
  assert component.resize((192,224),Image.Resampling.NEAREST).tobytes()==mask.crop((k*192,0,(k+1)*192,224)).tobytes()
 data=(a.original_data/'tyrian.hdt').read_bytes();reader=(repo/'src/episodes.c').read_text();formats={'u8':'B','s8':'b','u16':'H','s16':'h'}
 def schema(var):return [(m[2],formats[m[1]],int(m[3])) for m in re.finditer(r'fread_(u8|s8|u16|s16)_die\(\s*&?'+var+r'\[i\]\.(\w+),\s*(\d+),\s*f\)',reader)]
 ws,es=schema('weapons'),schema('enemyDat');assert len(es)==28 and ws
 pos=struct.unpack_from('<i',data)[0]+14+1638*sum(n*struct.calcsize(fmt) for _,fmt,n in ws)+61*82+sum(n*s for n,s in [(55,37),(7,37),(19,41),(38,86),(12,37)]);users=[];count=0
 for i in list(range(851))+list(range(1001,1851)):
  r={'id':i};count+=1
  for name,fmt,n in es:
   vals=list(struct.unpack_from('<'+str(n)+fmt,data,pos));pos+=n*struct.calcsize(fmt);r[name]=vals[0] if n==1 else vals
  if r['shapebank']==2 and (set(r['egraphic'])&set(IDS) or (not r['dani'] and r['dgr'] in IDS)):users.append(i)
  if i in range(66,73):
   assert r==reuse['records'][str(i)]==life['records'][str(i)]
 assert count==1701 and users==list(range(66,73))
 # Independently decode all level9 events before selecting link1 or global overrides.
 data=(a.original_data/'tyrian1.lvl').read_bytes();n=struct.unpack_from('<H',data)[0];pos=struct.unpack_from('<'+str(n)+'i',data,2)[16]+8;n=struct.unpack_from('<H',data,pos)[0];pos+=2+2*n;n=struct.unpack_from('<H',data,pos)[0];pos+=2;events=[]
 for i in range(n):
  v=struct.unpack_from('<HBhhbbbB',data,pos);pos+=11;events.append(dict(zip(['eventtime','type','dat','dat2','dat3','dat5','dat6','dat4'],v)))
 assert len(events)==1010 and [e for e in events if e['dat4']==1]==reuse['potential_link1_events']
 spawns=[e for e in events if e['type'] in [6,7,10,12,15,17,18,23,32,56] and e['dat'] in range(66,73)]
 assert len(spawns)==21 and {e['eventtime'] for e in spawns}=={3574,3798,4068} and all(e['type']==7 and e['dat4']==1 for e in spawns)
 for t in [3574,3798,4068]:
  assert sorted(e['dat'] for e in spawns if e['eventtime']==t)==list(range(66,73))
  for dt,accel in [(5,2),(15,-2)]:assert [e for e in events if e['eventtime']==t+dt and e['type']==20 and e['dat4']==1]==[dict(eventtime=t+dt,type=20,dat=accel,dat2=0,dat3=0,dat5=0,dat6=0,dat4=1)]
 assert not [e for e in events if e['eventtime']>=3500 and e['type'] in [25,47] and e['dat4'] in [0,1]]
subprocess.run([sys.executable,str(source/'rebuild.py'),str(out)],check=True)
for k,i in enumerate(IDS):
 name=f'enemy-newsh4-{i}-8';raw=(out/(name+'.hda')).read_bytes();png=(out/(name+'.png')).read_bytes();expected=inventory['outputs'][k];header=[1020000+i,8,24,28,6,7]
 assert raw[:28]==b'HDR1'+struct.pack('<6I',*header) and len(raw)==28+192*224*4
 assert sha(raw)==expected['HDA_SHA256'] and sha(raw[28:])==expected['RGBA_SHA256'] and sha(png)==expected['PNG_SHA256']
 im=Image.open(out/(name+'.png'));assert im.mode=='RGBA' and im.size==(192,224) and im.getchannel('A').tobytes()==mask.crop((k*192,0,(k+1)*192,224)).tobytes()
 stamp=0xcbf29ce484222325
 for b in raw[28:]:stamp=((stamp^b)*0x100000001b3)&0xffffffffffffffff
 assert f['entries'][k]['rgba_fnv1a64']==f'{stamp:016x}'
 for key in ['default_preview_pack','default_debug_pack']:
  pack=m['packs'][m[key]];assert pack['count']==len(pack['files']);e=pack['files'][name+'.hda'];assert e['header_u32']==header and (repo/'assets/hd/packs'/m[key]/(name+'.hda')).read_bytes()==raw and e['sha256']==sha(raw)
  assert (repo/e['source_png']).read_bytes()==png and e['source_png_sha256']==sha(png)
  indexed=m['source_pngs'][sha(raw)];assert indexed['path']==e['source_png'] and indexed['sha256']==sha(png) and indexed['RGBA_sha256']==sha(raw[28:])
 for pn,pack in m['packs'].items():
  for density in [4,8]:assert (f'enemy-newsh4-{i}-{density}.hda' in pack['files'])==(density==8 and pn in [m['default_preview_pack'],m['default_debug_pack']])
print('PASS seven exact generated PNG/RGBA/HDR1 members, bank2 namespace, anchors, alpha, approved integrity stamps, finite packs'+('; original RLE support, all1701 record reuse, all1010 events and lifecycle verified' if a.original_data else ''))
