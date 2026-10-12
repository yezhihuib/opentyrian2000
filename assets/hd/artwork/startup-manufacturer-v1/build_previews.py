from pathlib import Path
from PIL import Image,ImageDraw
import argparse,json,hashlib,shutil
P=Path(__file__).resolve().parent
MASTERS={10:'pic10-xsiv-generated-master.png',12:'pic12-eclipse-generated-master.png'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def build(output,reference_root=None):
 output=output.resolve()
 if output.exists() or output==P or P in output.parents: raise ValueError('Use a new external output directory')
 output.mkdir(parents=True,exist_ok=False);records=[]
 for n,master in MASTERS.items():
  expected_master={10:'8cb1be9d12efd38f129447116ce37bd5bd8347d24ff5e331b0e5cf29bb217ad9',12:'264220752c724600b5912c1de61906bb934c36e7684179d747e3aa5837b91a74'}
  assert sha(P/'masters'/master)==expected_master[n], 'Frozen master mismatch'
  m=Image.open(P/'masters'/master).convert('RGB');four=m.resize((1280,800),Image.Resampling.LANCZOS);two=four.resize((640,400),Image.Resampling.NEAREST)
  p4=output/f'pic{n}-candidate-native4x.png';p2=output/f'pic{n}-candidate-native2x.png';four.save(p4);two.save(p2)
  expected4={10:'00fd3fa8dccd72edc7621fe1b94e0f7ab60ca011e15ea886bfac2dcef63688bd',12:'1e84bae41415ea278257c81ab29397f97e586c87af0169e0fa497a2c87effa34'}
  expected2={10:'7d3e312eadc974d8c9d00c4089a31bb8f0d4b0a8b99096a996af9a05132a4092',12:'6a813b8b851b5c4fe793962100d6f4b4477cf03b38d0a735a01ceba1d0b58fd5'}
  assert sha(p4)==expected4[n] and sha(p2)==expected2[n], 'Canonical sampling mismatch'
  records.append({'pic_id':n,'master':master,'master_dimensions':list(m.size),'master_sha256':sha(P/'masters'/master),'canonical4x_png_sha256':sha(p4),'canonical4x_rgb_sha256':hashlib.sha256(four.tobytes()).hexdigest(),'native2x_png_sha256':sha(p2),'native2x_sampling':'Nearest from canonical4x','logical_size':[320,200],'opaque':True})
  if reference_root:
   original=Image.open(reference_root/f'pic{n}-original-palette{20 if n==10 else 22}.png').convert('RGB').resize((640,400),Image.Resampling.NEAREST)
   comp=Image.new('RGB',(1280,424),(20,20,20));draw=ImageDraw.Draw(comp);draw.text((8,7),f'PIC{n} ORIGINAL / NATIVE2X',fill='white');draw.text((648,7),'OFFLINE HD PILOT / NATIVE2X',fill='white');comp.paste(original,(0,24));comp.paste(two,(640,24));comp.save(output/f'pic{n}-original-vs-pilot-native2x.png')
 (output/'validation.json').write_text(json.dumps({'status':'OFFLINE_PILOT_ONLY','generation':'Built-in imagegen, one edit per original manufacturer card','postprocessing':'Full master RGB LANCZOS fit to1280x800; nearest2x preview. No repaint or fake runtime capture.','files':records},indent=2)+'\n')
 return records
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--output',type=Path,required=True);a.add_argument('--references',type=Path);x=a.parse_args();print(json.dumps(build(x.output,x.references),indent=2))
