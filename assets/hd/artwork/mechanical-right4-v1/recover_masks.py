from pathlib import Path
from PIL import Image
import hashlib,json,sys
P=Path(__file__).resolve().parent;data=Path(sys.argv[1]).read_bytes();assert hashlib.sha256(data).hexdigest()=='3ecc9b59c82e8e7d9c91889aac7d337ca28a59519c4970e256250e4603a9b248';off=0;mask=Image.new('L',(48,56));records=[]
for i in range(1,601):
 start=off;blank=data[off];off+=1;indices=bytes(672) if blank else data[off:off+672];off+=0 if blank else 672
 if i in [188,189,198,199]:
  m=Image.frombytes('L',(24,28),bytes(255 if v else 0 for v in indices));mask.paste(m,((i%10-8)*24,(i//10-18)*28));records.append({'id':i,'record_offset':start,'indices_sha256':hashlib.sha256(indices).hexdigest(),'transparent':indices.count(0)})
mask.resize((384,448),Image.Resampling.NEAREST).save(P/'masks/source-alpha-density8.png');(P/'proof/restored-source-masks.json').write_text(json.dumps({'source_sha256':hashlib.sha256(data).hexdigest(),'records':records},indent=2))
