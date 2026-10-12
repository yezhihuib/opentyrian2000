"""Rebuild raw RGBA HDA files from the three frozen HD PNG exports."""
from pathlib import Path
from PIL import Image
import struct,hashlib,json
p=Path(__file__).resolve().parent
manifest=json.loads((p/'candidate-manifest.json').read_text())
for f in manifest['frames']:
 im=Image.open(p/f['frame']);assert im.mode=='RGBA' and im.size==(96,112)
 raw=struct.pack('<4sIIIIii',b'HDR1',f['runtime_asset_key'],8,12,14,0,0)+im.tobytes()
 assert hashlib.sha256(raw).hexdigest()==f['hda_sha256']
 (p/f['hda']).parent.mkdir(exist_ok=True)
 (p/f['hda']).write_bytes(raw)
 print(f['binding_key'],len(raw),f['hda_sha256'])
