'use strict';
// Generated-only renderer. No data lookup or private preview input.
const fs=require('fs'),path=require('path'),crypto=require('crypto'),sharp=require('sharp');
const P=__dirname;
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const fnv=b=>{let h=14695981039346656037n;for(const v of b)h=((h^BigInt(v))*1099511628211n)&0xffffffffffffffffn;return '0x'+h.toString(16).padStart(16,'0');};
const canonicalize=b=>{for(let i=0;i<b.length;i+=4)if(!b[i+3])b.fill(0,i,i+3);return b;};
function transform(b,w,h,op){let r=Buffer.alloc(b.length);for(let y=0;y<h;y++)for(let x=0;x<w;x++){const sx=(op==='flipX'||op==='rotate180')?w-1-x:x,sy=(op==='flipY'||op==='rotate180')?h-1-y:y;b.copy(r,(y*w+x)*4,(sy*w+sx)*4,(sy*w+sx+1)*4);}return r;}
function stats(b,w,h){let alpha=Buffer.alloc(w*h),bounds=[w,h,0,0],nonzero=0,fractional=0;for(let p=0;p<w*h;p++){let a=b[p*4+3];alpha[p]=a;if(a){let x=p%w,y=Math.floor(p/w);nonzero++;if(a<255)fractional++;bounds=[Math.min(bounds[0],x),Math.min(bounds[1],y),Math.max(bounds[2],x+1),Math.max(bounds[3],y+1)];}}return {alpha_sha256:sha(alpha),bounds_pixels:bounds,nonzero_alpha_samples:nonzero,fractional_alpha_samples:fractional};}
async function render(out){
 if(fs.existsSync(out))throw Error('Output directory must not exist: '+out);
 const contract=JSON.parse(fs.readFileSync(path.join(P,'semantic-contract.json')));fs.mkdirSync(out,{recursive:true});let rows=[],standalone=[];
 for(const density of contract.densities){let canonical=null;for(const spec of contract.specs){
  const svg=fs.readFileSync(path.join(P,'sources',`rear-multi-${spec.id}.svg`));
  // SVG density changes intrinsic vector rendering, not a resampling of d8.
  const {data,info}=await sharp(svg,{density:72*density/8}).ensureAlpha().raw().toBuffer({resolveWithObject:true});
  const w=12*density,h=14*density;if(info.width!==w||info.height!==h||info.channels!==4)throw Error('Dimensions');
  // Coverage only: rasterize the same color geometry with the coverage mask removed,
  // retain its straight RGB exactly, and take softened alpha from the masked SVG.
  // All original supported samples stay nonzero; no new support is introduced.
  const colorSvg=svg.toString().replace(/<defs><mask id="edgeCoverage"[\s\S]*?<\/mask><\/defs>\n/,'').replace(' mask="url(#edgeCoverage)"','');
  const baseRGBA=canonicalize(await sharp(Buffer.from(colorSvg),{density:72*density/8}).ensureAlpha().raw().toBuffer());
  const direct=Buffer.from(baseRGBA);
  for(let i=0;i<direct.length;i+=4)if(baseRGBA[i+3])direct[i+3]=Math.max(1,Math.min(baseRGBA[i+3],data[i+3]));
  const literalRGBA=canonicalize(Buffer.from(data));
  let rgba=direct;
  if(spec.id===281)canonical=Buffer.from(direct);
  if([282,300,301].includes(spec.id))rgba=transform(canonical,w,h,spec.transform_name);
  let different_bytes=0,max_channel_delta=0,sum_absolute_delta=0,different_alpha_samples=0,max_alpha_delta=0;
  for(let i=0;i<rgba.length;i++){let diff=Math.abs(rgba[i]-literalRGBA[i]);if(diff)different_bytes++;max_channel_delta=Math.max(max_channel_delta,diff);sum_absolute_delta+=diff;if(i%4===3){if(diff)different_alpha_samples++;max_alpha_delta=Math.max(max_alpha_delta,diff);}}
  standalone.push({id:spec.id,density,standalone_svg_rgba_sha256:sha(literalRGBA),normalized_straight_rgba_sha256:sha(direct),canonical_rgba_sha256:sha(rgba),different_bytes,max_channel_delta,sum_absolute_delta,different_alpha_samples,max_alpha_delta});
  const base=`rear-multi-${spec.id}-${density}`,png=base+'.png',raw=base+'.rgba';
  fs.writeFileSync(path.join(out,raw),rgba);await sharp(rgba,{raw:{width:w,height:h,channels:4}}).png().toFile(path.join(out,png));
  rows.push({id:spec.id,source_bank:8,mode:spec.mode,phase:spec.phase,logical_size:[12,14],anchor:[0,0],density,authored_size:[w,h],png,rgba:raw,svg:`sources/rear-multi-${spec.id}.svg`,role_id:null,rgba_byte_length:rgba.length,png_sha256:sha(fs.readFileSync(path.join(out,png))),rgba_sha256:sha(rgba),rgba_fnv1a64:fnv(rgba),...stats(rgba,w,h)});
 }}
 const receipt={schema:'rear-multi-p1-art-render-v1',generated_only:true,original_inputs:false,role_ids_unassigned:true,versions:{node:process.version,platform:process.platform,architecture:process.arch,sharp:sharp.versions},outputs:rows,standalone_svg_comparison:standalone};
 fs.writeFileSync(path.join(out,'render-receipt.json'),JSON.stringify(receipt,null,2)+'\n');return receipt;
}
module.exports={render,sha,transform};
if(require.main===module)render(path.resolve(process.argv[2]||path.join(P,'output'))).then(r=>console.log(`PASS: ${r.outputs.length} independently rendered density-specific PNG/RGBA pairs; no HDA role IDs assigned.`)).catch(e=>{console.error(e);process.exitCode=1;});
