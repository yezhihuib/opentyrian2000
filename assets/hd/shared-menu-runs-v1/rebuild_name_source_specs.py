#!/usr/bin/env python3
"""Extract authentic table/name source evidence; no runtime/gameplay modifications."""
from pathlib import Path
import argparse,hashlib,json,struct
P=Path(__file__).resolve().parent
ROOT=P.parents[2]
PINS={'tyrian.hdt':'fde8506326e7bb0916b38c362e33bf8a8a5affa561206c021af7f65b4a17745b','tyrian4.lvl':'6589b898094887925e7717c8663c4b8b5e4b76f3c89a7898ed9f4691c1f2cc16','tyrian5.lvl':'275b5aaf55caecee8dc95e26f7cf118a9ee265f095ce61945b9ece56a4523323'}
TABLES={'weaponPort':0,'powerSys':1,'ships':2,'options':3,'shields':4}
SHA=lambda b:hashlib.sha256(b).hexdigest()

def build(data,out):
 manifest=json.loads((ROOT/'assets/hd/manifest.json').read_text())['shared_menu_runs']['files'];targets={r['text']:int(n.split('-')[-1].split('.')[0]) for n,r in manifest.items() if n.startswith('names-')};rows=[];sources=[]
 for filename,bank in [('tyrian.hdt',1),('tyrian4.lvl',4),('tyrian5.lvl',5)]:
  raw=(data/filename).read_bytes();assert SHA(raw)==PINS[filename]
  offset=struct.unpack_from('<i',raw)[0] if bank==1 else struct.unpack_from('<i',raw,2+4*(struct.unpack_from('<H',raw)[0]-1))[0]
  assert struct.unpack_from('<7H',raw,offset)==(818,60,6,18,37,11,850)
  sources.append({'file':filename,'sha256':SHA(raw),'item_table_offset':offset});offset+=14+1638*80
  for name,count,stride,categories,cost_offset in [('weaponPort',61,82,[3,4],76),('special',55,37,[],None),('powerSys',7,37,[6],35),('ships',19,41,[2],38),('options',38,86,[7,8],34),('shields',12,37,[5],35)]:
   for item in range(count):
    length=raw[offset];name30=raw[offset+1:offset+31];assert length==30
    if categories:
     assert len(name30)==30 and all(32<=x<127 for x in name30)
     display=b' '.join(x for x in name30.split(b' ') if x).decode('ascii');assert display in targets
     rows.append({'source_bank':bank,'source_file':filename,'record_offset':offset,'table':name,'table_id':TABLES[name],'item_id':item,'run_id':targets[display],'categories':categories,'category_mask':sum(1<<x for x in categories),'base_cost':struct.unpack_from('<H',raw,offset+cost_offset)[0],'raw30_hex':name30.hex(),'source31_hex':(name30+b'\0').hex(),'display':display})
    offset+=stride
 assert len(rows)==411 and len(set(r['display'] for r in rows))==113
 document={'schema':'new-name-source-specs-from-authenticated-original-data','sources':sources,'source_count':411,'display_count':113,'source_bank_semantics':'Provenance only; never an episode/level admission allowlist. Authenticate actual table/ID/category and exact source31 bytes.','normalization':'ASCII space0x20 trim/collapse only, after source identity verification.','mappings':rows}
 (out/'reconstructed-name-source-manifest.json').write_text(json.dumps(document,indent=2)+'\n')
 lines=['/* Fresh extraction from pinned original item tables, not original generator source. */','#ifndef CMR3_RECONSTRUCTED_NAME_SOURCE_SPECS_H','#define CMR3_RECONSTRUCTED_NAME_SOURCE_SPECS_H','#include <stdint.h>','#define CMR3_NAME_SOURCE_COUNT 411u','enum Cmr3NameTable { CMR3_TABLE_WEAPON_PORT=0, CMR3_TABLE_POWER_SYS, CMR3_TABLE_SHIPS, CMR3_TABLE_OPTIONS, CMR3_TABLE_SHIELDS };','/* source_bank is provenance, not a runtime episode/level allowlist. */','struct Cmr3NameSource { uint8_t source_bank, table, item, run; uint16_t base_cost; uint32_t category_mask; unsigned char source31[31]; };','static const struct Cmr3NameSource cmr3_name_sources[411]={']
 for r in rows:
  text=bytes.fromhex(r['raw30_hex']).decode('ascii');lines.append(' {%d,%d,%d,%d,%d,%du,%s},'%(r['source_bank'],r['table_id'],r['item_id'],r['run_id'],r['base_cost'],r['category_mask'],json.dumps(text)))
 lines+=['};','#endif',''];(out/'reconstructed_name_source_specs.h').write_text('\n'.join(lines))
 print(json.dumps({'sources':411,'distinct_displays':113,'out':str(out)}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--out',type=Path,default=P);a=p.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=True)
 assert not any(q.name=='frozen' for q in [out,*out.parents]);build(a.data,out)
