'use strict';
// Source-only standalone builder. No repository, original-data, capture, or
// preview dependency. D4 and D8 are separate vector renders, never resamples.
const fs=require('fs'),path=require('path'),crypto=require('crypto'),sharp=require('sharp');
const ROOT=__dirname,sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const fnv=b=>{let h=14695981039346656037n;for(const v of b)h=((h^BigInt(v))*1099511628211n)&0xffffffffffffffffn;return '0x'+h.toString(16).padStart(16,'0');};
function canonicalize(b){for(let i=0;i<b.length;i+=4)if(!b[i+3])b.fill(0,i,i+3);return b;}
function flipX(b,w,h){const o=Buffer.alloc(b.length);for(let y=0;y<h;y++)for(let x=0;x<w;x++)b.copy(o,4*(y*w+x),4*(y*w+w-1-x),4*(y*w+w-x));return o;}
function stats(b,w,h){let bounds=[w,h,0,0],nonzero=0,fractional=0,a=Buffer.alloc(w*h);for(let i=0;i<w*h;i++){a[i]=b[4*i+3];if(a[i]){let x=i%w,y=Math.floor(i/w);bounds=[Math.min(bounds[0],x),Math.min(bounds[1],y),Math.max(bounds[2],x+1),Math.max(bounds[3],y+1)];nonzero++;if(a[i]<255)fractional++;}}return {bounds_pixels:bounds,nonzero_alpha_samples:nonzero,fractional_alpha_samples:fractional,alpha_sha256:sha(a)};}
async function build(out){
 if(fs.existsSync(out))throw Error('Output destination must be fresh: '+out);
 const pinsPath=path.join(ROOT,'pins.json');if(!fs.existsSync(pinsPath))throw Error('Required pins.json missing');const pins=JSON.parse(fs.readFileSync(pinsPath));
 if(pins){for(const [name,hash]of Object.entries(pins.inputs))if(sha(fs.readFileSync(path.join(ROOT,name)))!==hash)throw Error('Pinned input mismatch: '+name);if(JSON.stringify(sharp.versions)!==JSON.stringify(pins.renderer.sharp))throw Error('Pinned Sharp renderer versions differ');}
 fs.mkdirSync(out,{recursive:true});const rows=[],comparison=[];
 for(const density of [4,8]){
  let canonical;
  for(const id of [294,295]){
   const svg=fs.readFileSync(path.join(ROOT,'sources',`rear-multi-${id}.svg`));
   const rendered=await sharp(svg,{density:72*density/8}).ensureAlpha().raw().toBuffer({resolveWithObject:true});
   const w=12*density,h=14*density;if(rendered.info.width!==w||rendered.info.height!==h||rendered.info.channels!==4)throw Error('Unexpected dimensions');
   const direct=canonicalize(rendered.data);if(id===294)canonical=Buffer.from(direct);
   const rgba=id===294?canonical:flipX(canonical,w,h);let changed=0,maxDelta=0,maxAlphaDelta=0,maxCompositeDelta=0;
   for(let p=0;p<rgba.length;p++){const d=Math.abs(rgba[p]-direct[p]);if(d)changed++;maxDelta=Math.max(maxDelta,d);if(p%4===3)maxAlphaDelta=Math.max(maxAlphaDelta,d);}
   for(let p=0;p<rgba.length;p+=4)for(let c=0;c<3;c++){const b=[104,72,44][c];const over=(v)=>Math.floor((b*(255-v[p+3])+v[p+c]*v[p+3]+127)/255);maxCompositeDelta=Math.max(maxCompositeDelta,Math.abs(over(rgba)-over(direct)));}
   comparison.push({id,density,direct_svg_rgba_sha256:sha(direct),canonical_rgba_sha256:sha(rgba),direct_svg_different_bytes:changed,direct_svg_max_channel_delta:maxDelta,direct_svg_max_alpha_delta:maxAlphaDelta,direct_svg_max_composited_channel_delta_on_synthetic_brown:maxCompositeDelta});
   const stem=`rear-multi-p7-${id}-${density}`,key=1310000+id;
   const header=Buffer.alloc(28);header.write('HDR1');[key,density,12,14,0,0].forEach((v,i)=>header.writeUInt32LE(v,4+i*4));
   const hda=Buffer.concat([header,rgba]);fs.writeFileSync(path.join(out,stem+'.rgba'),rgba);fs.writeFileSync(path.join(out,stem+'.hda'),hda);
   const png=await sharp(rgba,{raw:{width:w,height:h,channels:4}}).png({compressionLevel:9,adaptiveFiltering:false,palette:false}).toBuffer();fs.writeFileSync(path.join(out,stem+'.png'),png);
   const row={id,role:131,key,density,logical_size:[12,14],anchor:[0,0],authored_size:[w,h],rgba:stem+'.rgba',png:stem+'.png',hda:stem+'.hda',rgba_bytes:rgba.length,hda_bytes:hda.length,rgba_sha256:sha(rgba),rgba_fnv1a64:fnv(rgba),png_sha256:sha(png),hda_sha256:sha(hda),...stats(rgba,w,h)};
   if(pins&&JSON.stringify(row)!==JSON.stringify(pins.outputs.find(r=>r.id===id&&r.density===density)))throw Error('Pinned output mismatch: '+stem);rows.push(row);
  }
 }
 const receipt={schema:'rear-multicannon-p7-mode2-candidate-render-v1',status:'OFFLINE_ART_CANDIDATE',generated_only:true,no_original_raster_or_capture_inputs:true,no_native_1x_intermediate:true,renderer:{node:process.version,sharp:sharp.versions},outputs:rows,standalone_svg_comparison:comparison};
 fs.writeFileSync(path.join(out,'build-receipt.json'),JSON.stringify(receipt,null,2)+'\n');return receipt;
}
module.exports={build,sha,flipX};
if(require.main===module)build(path.resolve(process.argv[2]||path.join(ROOT,'output'))).then(r=>console.log('PASS: two direct-vector renders and two exact reflected RGBA/PNG/HDR1 resources.')).catch(e=>{console.error(e);process.exitCode=1;});
