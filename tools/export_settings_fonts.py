#!/usr/bin/env python3
"""Package immutable authored planes only. No original game bytes are copied."""
import argparse,hashlib,json,pathlib,struct
p=argparse.ArgumentParser();p.add_argument('--large',type=pathlib.Path,required=True);p.add_argument('--repo',type=pathlib.Path,required=True);p.add_argument('--out',type=pathlib.Path,required=True);a=p.parse_args()
def fnv(b):
 h=14695981039346656037
 for v in b:h=((h^v)*1099511628211)&((1<<64)-1)
 return h
specs=[('large',a.large/'canonical','menu-large',1216,384,76,96,60,53,466944,1,12,15,'b0a8226af36e025a','5c12ed2dea448227','5529cd3792b04378','378a4d7af95d996c6173c165c2ddad8d8bb4645d714b546a98e27c54ea7c4056','016684edd0c26c909aeed45e95c9b73fc57247ab9fe7abc15496c44355cb8a90'),('medium',a.repo/'assets/hd/artwork/title-menu-font-v3-1/canonical','menu-normal',896,384,56,64,85,76,344064,1,12,15,'f0dec0f37828f1c4','96f0e4e668876f23','a3861b64f710cb1f','6f9153c664e9fc6bf2aa02cb7f8e67b3275fe84c6d5da9a0b00bcbce3bb52192','6747bc42a57ae7789effaac28c9709b9ad2de61e1f19ede15492096d0e3b947e'),('tiny',a.repo/'assets/hd/artwork/gameplay-hud-font-v1/canonical','tiny',512,320,32,40,127,86,163840,0,7,7,'0908ca85cbf2a1e3','2ed2973d82ce6f3d','68e8c2bab3c43d0d','e4f245519b2922b3f3575ae499f0419bfc85742d059a07680f3693e68ddbaeb7',None)]
a.out.mkdir(parents=True,exist_ok=True);report=[]
for bank,(name,d,prefix,aw,ah,cw,ch,n,e,plane,mode,r0,r1,m,s,i,asha,rsha) in enumerate(specs):
 alpha=(d/(prefix+('-coverage-atlas-4x.alpha.bin' if bank==2 else '-coverage-4x.alpha.bin'))).read_bytes();assert len(alpha)==plane and hashlib.sha256(alpha).hexdigest()==asha
 role=(d/(prefix+'-roles-4x.bin')).read_bytes() if mode else b''
 if mode:assert len(role)==plane and hashlib.sha256(role).hexdigest()==rsha
 payload=alpha+role
 header=b'SFN1'+struct.pack('<15I',1,bank,4,aw,ah,cw,ch,4,n,e,plane,len(role),mode,r0,r1)+struct.pack('<8Q',0x845b16939661b466,int(m,16),int(s,16),int(i,16),0x69f74bd2c5d2ad5b,fnv(payload),0,0)
 assert len(header)==128
 dest=a.out/f'settings-font-{name}-v1.hda';dest.write_bytes(header+payload)
 report.append(dict(file=dest.name,bytes=len(header)+len(payload),payload_fnv=f'{fnv(payload):016x}',sha256=hashlib.sha256(header+payload).hexdigest()))
(a.out/'manifest.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
