"""Require frozen art/delta oracles to reject private in-memory corruptions.

No artwork, source, manifest, package or production file is modified.
"""
from pathlib import Path
import argparse, copy, io, json, tempfile
from PIL import Image
import grass_sand_art_oracle as oracle
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--baseline-manifest',type=Path,required=True)
p.add_argument('--package',type=Path,required=True)
p.add_argument('--report',type=Path)
a=p.parse_args();raw=a.baseline_manifest.read_bytes();base=oracle.baseline(raw);frozen=oracle.freeze()
prior=base['packs'][base['default_debug_pack']]['files'];files=copy.deepcopy(prior)
for r in frozen['assets']:
 files[Path(r['hda']).name]={'sha256':r['hda_sha256'],'header_u32':r['header_u32'],'source_png':r['png'],'source_png_sha256':r['png_sha256']}
oracle.delta(files,prior)
r=frozen['assets'][0];png=(a.package/r['png']).read_bytes();hda=(a.package/r['hda']).read_bytes();oracle.selected_asset(r,png,hda)
results=[]
def rejected(name,fn,marker):
 try:fn()
 except AssertionError as e:
  assert marker in str(e),(name,'Wrong rejection',str(e))
  results.append({'case':name,'rejected':True,'diagnostic':str(e)})
 else:raise AssertionError(name+' escaped the frozen oracle')
def bad_delta(name,change,marker):
 changed=copy.deepcopy(files);change(changed);rejected(name,lambda:oracle.delta(changed,prior),marker)
bad_delta('one-grass-member-missing',lambda d:d.pop('terrain-shapesz-66-8.hda'),'exactly nine')
bad_delta('forest68-added',lambda d:d.update({'terrain-shapesz-68-8.hda':d['terrain-shapesz-66-8.hda']}),'exactly nine')
bad_delta('prior47-removed',lambda d:d.pop('terrain-shapesz-47-8.hda'),'exactly nine')
for key,value in [('sha256','0'*64),('header_u32',[2010047,8,24,28,1,0]),('source_png','changed.png'),('source_png_sha256','0'*64)]:
 bad_delta('prior47-'+key+'-changed',lambda d,k=key,v=value:d['terrain-shapesz-47-8.hda'].__setitem__(k,v),'Prior manifest record changed')
bad_delta('current64-reverted',lambda d:d['terrain-shapesz-64-8.hda'].__setitem__('sha256','0'*64),'Prior manifest record changed')
rejected('wrong-baseline-bytes',lambda:oracle.baseline(raw+b' '),'exact current7c7')
for name,key,value in [('wrong-layer','layer',2),('wrong-slot','slot',311),('wrong-density','header_u32',[2010066,4,24,28,0,0]),('wrong-anchor','header_u32',[2010066,8,24,28,6,7]),('wrong-png-size-contract','size',[384,448])]:
 changed=copy.deepcopy(r);changed[key]=value
 rejected(name,lambda c=changed:oracle.selected_asset(c,png,hda),'')
rejected('wrong-member-png',lambda:oracle.selected_asset(r,(a.package/frozen['assets'][1]['png']).read_bytes(),hda),'Frozen PNG file changed')
with Image.open(io.BytesIO(png)) as im:
 altered=im.convert('RGBA');pixel=altered.getpixel((0,0));altered.putpixel((0,0),(*pixel[:3],0));buf=io.BytesIO();altered.save(buf,format='PNG');transparent=buf.getvalue()
rejected('transparent-art-pixel',lambda:oracle.selected_asset(r,transparent,hda),'Frozen PNG file changed')
for name,bad,marker in [('bad-magic',b'BAD1'+hda[4:],'HDA size/magic'),('truncated-payload',hda[:-1],'HDA size/magic'),('trailing-payload',hda+b'X','HDA size/magic'),('wrong-hda-density',hda[:8]+(4).to_bytes(4,'little')+hda[12:],'HDA header')]:
 rejected(name,lambda b=bad:oracle.selected_asset(r,png,b),marker)
bad=bytearray(hda);bad[28]^=1
rejected('changed-hda-rgb',lambda:oracle.selected_asset(r,png,bytes(bad)),'HDA/PNG or alpha')
rejected('escaped-art-path',lambda:oracle.owned(a.package,'../outside.png'),'Artifact path escaped root')
# The strict manifest guard also protects nondefault packs and the complete
# canonical source catalog, independently of the selected-pack file scanner.
manifest=copy.deepcopy(base)
for key in ['default_preview_pack','default_debug_pack']:
 d=manifest['packs'][manifest[key]]
 for r in frozen['assets']:
  filename=Path(r['hda']).name
  d['files'][filename]={'sha256':r['hda_sha256'],'header_u32':r['header_u32'],'source_png':r['png'],'source_png_sha256':r['png_sha256']}
 d['count']=len(d['files'])
for r in frozen['assets']:
 manifest['source_pngs'][r['hda_sha256']]={'path':r['png'],'sha256':r['png_sha256'],'RGBA_sha256':r['rgba_sha256']}
oracle.manifest_delta(manifest,base)
def bad_manifest(name,change,marker):
 m=copy.deepcopy(manifest);change(m);rejected(name,lambda:oracle.manifest_delta(m,base),marker)
other=next(k for k in base['packs'] if k not in [base['default_preview_pack'],base['default_debug_pack']])
first_source=next(iter(base['source_pngs']))
bad_manifest('nondefault-pack-changed',lambda m:m['packs'][other].__setitem__('count',-1),'Nondefault pack changed')
bad_manifest('canonical-source-catalog-entry-missing',lambda m:m['source_pngs'].pop(frozen['assets'][0]['hda_sha256']),'exactly nine additions')
bad_manifest('prior-canonical-source-changed',lambda m:m['source_pngs'][first_source].__setitem__('sha256','0'*64),'Prior canonical source changed')
bad_manifest('new-canonical-RGBA-record-changed',lambda m:m['source_pngs'][frozen['assets'][0]['hda_sha256']].__setitem__('RGBA_sha256','0'*64),'New canonical source record mismatch')
bad_manifest('new-canonical-path-mismatch',lambda m:m['source_pngs'][frozen['assets'][0]['hda_sha256']].__setitem__('path','wrong.png'),'Canonical source path mismatch')
report={'status':'passed','mutants_rejected':len(results),'results':results,'positive_controls_passed':True,'baseline_commit':oracle.BASE,'frozen_manifest_sha256':oracle.FREEZE_SHA,'scope':'Only independent memory copies changed; original source/package/manifests/artwork untouched. Assertion messages must match the intended guard.'}
out=a.report or Path(tempfile.mkdtemp(prefix='grass9-art-mutants-'))/'result.json';out.write_text(json.dumps(report,indent=2)+'\n');print('PASS:',len(results),'artifact/delta corruptions rejected; original guards retained. Report:',out)
