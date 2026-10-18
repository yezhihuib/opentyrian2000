'use strict';
// Newly authored repo-native vector geometry. This program reads accepted public
// semantic color/softness constants, never original raster artwork or a capture.
const fs=require('fs'),path=require('path'),crypto=require('crypto'),sharp=require('sharp');
const ROOT=path.resolve(__dirname,'..'),out=path.resolve(process.argv[2]||path.join(ROOT,'output'));
const accepted='assets__hd__artwork__player-rear-multicannon-p1-six-v1__semantic-contract.json';
const acceptedBytes=fs.readFileSync(path.join(ROOT,'accepted-sources',accepted));
const old=JSON.parse(acceptedBytes),stops=old.shading.stops;
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const specs=[
 {name:'inner',path:'M1.65 4 C.63 4 0 4.62 0 5.5 C0 6.35 .67 7 1.72 7 C4.28 7 7.73 6.5 11 5.55 C8.21 4.8 4.67 4 1.65 4Z',heat:{cx:1.45,cy:5.48,dx:1,dy:0,L:9.1,W:1.35},bounds:[0,4,11,7]},
 {name:'outer',path:'M4.65 1 C3.63 1 3 1.62 3 2.5 C3 3.35 3.67 4 4.72 4 C6.9 4 9.61 3.5 12 2.55 C9.94 1.8 7.08 1 4.65 1Z',heat:{cx:4.45,cy:2.48,dx:1,dy:0,L:7.1,W:1.35},bounds:[3,1,12,4]}
];
function defs(g,masked){const h=g.heat,id=g.name;
 let s=`<radialGradient id="heat-${id}" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="matrix(${h.L} 0 0 ${h.W} ${h.cx} ${h.cy})">${stops.map(([offset,color])=>`<stop offset="${offset}" stop-color="${color}"/>`).join('')}</radialGradient>`;
 if(masked)s+=`<mask id="edge-${id}" maskUnits="userSpaceOnUse" maskContentUnits="userSpaceOnUse" x="0" y="0" width="12" height="14"><path d="${g.path}" fill="white"/>${Array.from({length:32},(_,i)=>{const t=(32-i)/32,a=.62+.38*t*t*(3-2*t),v=Math.round(255*a);return `<path d="${g.path}" fill="none" stroke="rgb(${v},${v},${v})" stroke-width="${.60*t}" stroke-linejoin="round"/>`;}).join('')}</mask>`;
 return s;
}
function svg(id,masked=true){const one=g=>`<path d="${g.path}" fill="url(#heat-${g.name})"${masked?` mask="url(#edge-${g.name})"`:''}/>`;
 const canonical=specs.map(one).join('\n');
 return `<svg xmlns="http://www.w3.org/2000/svg" width="96" height="112" viewBox="0 0 12 14">\n<!-- NEW P10 MODE1 CANDIDATE, NOT FROZEN. ${id}. Four smooth cubic lobes;12x14 anchor0,0. -->\n<defs>${specs.map(g=>defs(g,masked)).join('')}</defs>\n${id===222?'<g transform="translate(12 0) scale(-1 1)">':''}\n${canonical}\n<g transform="translate(0 14) scale(1 -1)">${canonical}</g>\n${id===222?'</g>':''}\n</svg>\n`;
}
function flipX(b,w,h){const r=Buffer.alloc(b.length);for(let y=0;y<h;y++)for(let x=0;x<w;x++)b.copy(r,4*(y*w+x),4*(y*w+w-1-x),4*(y*w+w-x));return r;}
function stats(b,w,h){let pts=[],fractional=0,alpha=0,peak=[0,0,0];for(let p=0;p<w*h;p++)if(b[4*p+3]){pts.push(p);fractional+=b[4*p+3]<255;alpha+=b[4*p+3];for(let c=0;c<3;c++)peak[c]=Math.max(peak[c],b[4*p+c]);}return {supported_samples:pts.length,fractional_alpha_samples:fractional,alpha_sum:alpha,peak_RGB:peak,bounds:[Math.min(...pts.map(p=>p%w)),Math.min(...pts.map(p=>Math.floor(p/w))),Math.max(...pts.map(p=>p%w))+1,Math.max(...pts.map(p=>Math.floor(p/w)))+1]};}
function fnv(b){let h=14695981039346656037n;for(const v of b)h=((h^BigInt(v))*1099511628211n)&0xffffffffffffffffn;return '0x'+h.toString(16).padStart(16,'0');}
async function main(){fs.mkdirSync(out,{recursive:true});const rows=[];
 for(const id of [203,222])fs.writeFileSync(path.join(out,`rear-multi-${id}.svg`),svg(id));
 for(const d of [4,8]){
  const options={density:72*d/8},w=12*d,h=14*d;
  const softened=await sharp(Buffer.from(svg(203)),options).ensureAlpha().raw().toBuffer();
  const base=await sharp(Buffer.from(svg(203,false)),options).ensureAlpha().raw().toBuffer();
  const rgba=Buffer.from(base);let supportAdded=0,supportRemoved=0,rgbChanged=0;
  for(let i=0;i<rgba.length;i+=4){if(base[i+3])rgba[i+3]=Math.max(1,Math.min(base[i+3],softened[i+3]));else rgba.fill(0,i,i+4);supportAdded+=!!rgba[i+3]&&!base[i+3];supportRemoved+=!rgba[i+3]&&!!base[i+3];if(base[i+3])for(let c=0;c<3;c++)rgbChanged+=rgba[i+c]!==base[i+c];}
  const direct222soft=await sharp(Buffer.from(svg(222)),options).ensureAlpha().raw().toBuffer();
  const direct222=await sharp(Buffer.from(svg(222,false)),options).ensureAlpha().raw().toBuffer();
  for(let i=0;i<direct222.length;i+=4){if(direct222[i+3])direct222[i+3]=Math.max(1,Math.min(direct222[i+3],direct222soft[i+3]));else direct222.fill(0,i,i+4);}
  for(const id of [203,222]){const b=id===203?rgba:flipX(rgba,w,h),stem=`rear-multi-${id}-${d}`;
   fs.writeFileSync(path.join(out,stem+'.rgba'),b);await sharp(b,{raw:{width:w,height:h,channels:4}}).png().toFile(path.join(out,stem+'.png'));
   const direct=id===222?direct222:rgba;let differentBytes=0,maxDelta=0,maxAlphaDelta=0,supportDisagreement=0,maxBlendDelta=0;for(let i=0;i<b.length;i++){const delta=Math.abs(b[i]-direct[i]);differentBytes+=!!delta;maxDelta=Math.max(maxDelta,delta);if(i%4===3)maxAlphaDelta=Math.max(maxAlphaDelta,delta);}
   for(let i=0;i<b.length;i+=4){supportDisagreement+=!!b[i+3]!==!!direct[i+3];for(const bg of [[18,24,34],[112,112,112],[218,228,236]])for(let c=0;c<3;c++)maxBlendDelta=Math.max(maxBlendDelta,Math.abs(Math.floor((bg[c]*(255-b[i+3])+b[i+c]*b[i+3]+127)/255)-Math.floor((bg[c]*(255-direct[i+3])+direct[i+c]*direct[i+3]+127)/255)));}
   rows.push({id,density:d,canvas:[12,14],anchor:[0,0],rgba:stem+'.rgba',png:stem+'.png',rgba_sha256:sha(b),rgba_fnv1a64:fnv(b),png_sha256:sha(fs.readFileSync(path.join(out,stem+'.png'))),...stats(b,w,h),support_added_by_softening:supportAdded,support_removed_by_softening:supportRemoved,RGB_changed_by_softening:rgbChanged,standalone_svg_comparison:{rgba_sha256:sha(direct),different_bytes:differentBytes,max_channel_delta:maxDelta,max_alpha_delta:maxAlphaDelta,support_disagreement_samples:supportDisagreement,maximum_blend_delta_on_three_review_backgrounds:maxBlendDelta,canonical:'203 is direct,222 is exact byte reflection of203; standalone rasterizer differences disclosed. RGB delta255 can include zero-alpha canonicalization; blend delta measures visible magnitude.'}});
  }
 }
 const contract={schema:'rear-multi-p10-mode1-local-candidate-v1',status:'LOCAL_CANDIDATE_REQUIRES_PARENT_VISUAL_APPROVAL_NOT_FROZEN',source_commit:'82c0d3ec0e0750cab217b9d8dc94696a6def0daa',ids:[203,222],logical_size:[12,14],anchor:[0,0],densities:[4,8],construction:'Two NEW compact cubic silhouettes (inner11x3,outer9x3). Lower pair is exact vector full-canvas flipY.222 payload is exact byte flipX of203. No traced raster boundary, no bitmap scaling, no component-reuse claim.',accepted_style_source:{file:accepted,sha256:sha(acceptedBytes),copied_fields:['shading.stops','coverage_softness inner width0.30 and boundary factor0.62;32 nested inward vector mask strokes']},stops,geometry:specs,softness:{inner_width:.30,boundary_factor:.62,steps:32,RGB:'Exact unsoftened straight RGB retained; only alpha softened.',halo:false},canvas_clipping:'All authored geometry lies within[0,1,12,13]. No off-canvas occupied authored geometry or clipped lobe tails.',source_data_inputs:false,approved_existing_assets_modified:false,no_native_1x_intermediate:true,publication:false,runtime:false,versions:{node:process.version,sharp:sharp.versions},outputs:rows};
 fs.writeFileSync(path.join(out,'candidate-contract.json'),JSON.stringify(contract,null,2)+'\n');console.log(JSON.stringify(rows,null,2));
}
main().catch(e=>{console.error(e);process.exitCode=1;});
