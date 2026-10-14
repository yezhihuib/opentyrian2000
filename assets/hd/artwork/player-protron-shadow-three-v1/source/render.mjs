#!/usr/bin/env node
/** Offline semantic coverage artwork. No game-data or head-image input. */
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
import crypto from 'node:crypto';
const here=path.dirname(fileURLToPath(import.meta.url));
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const k=1.3807118745769833;
// 226 is a central-symmetric, four-cubic oblique oval. Its cardinal tangent
// locations encode a small directional lean, not the old pixel staircase.
const n=[5.8,4],e=[8,6.2],s=[5.2,9],w=[3,6.8];
const curves=[
 [n,[n[0]+k,n[1]],[e[0],e[1]-k],e],
 [e,[e[0],e[1]+k],[s[0]+k,s[1]],s],
 [s,[s[0]-k,s[1]],[w[0],w[1]+k],w],
 [w,[w[0],w[1]-k],[n[0]-k,n[1]],n],
];
const d=`M ${n.join(' ')} `+curves.map(c=>`C ${c.slice(1).flat().join(' ')}`).join(' ')+' Z';
const specs=[
 {id:225,label:'Small round',bbox:[4,5,8,9],centroid:[6,7],element:'<ellipse cx="6" cy="7" rx="2" ry="2"/>',area:Math.PI*4,geometry:{type:'ellipse',cx:6,cy:7,rx:2,ry:2}},
 {id:244,label:'Large offset round',bbox:[0,1,11,12],centroid:[5.5,6.5],element:'<ellipse cx="5.5" cy="6.5" rx="5.5" ry="5.5"/>',area:Math.PI*30.25,geometry:{type:'ellipse',cx:5.5,cy:6.5,rx:5.5,ry:5.5}},
 {id:226,label:'Small oblique oval',bbox:[3,4,8,9],centroid:[5.5,6.5],element:`<path d="${d}"/>`,geometry:{type:'central-symmetric-cubic-oval',curves}},
];
const mul=(a,b)=>{const c=Array(a.length+b.length-1).fill(0);a.forEach((x,i)=>b.forEach((y,j)=>c[i+j]+=x*y));return c;};
const der=a=>a.slice(1).map((x,i)=>x*(i+1));
const integral=a=>a.reduce((z,x,i)=>z+x/(i+1),0);
const poly=(p,j)=>[p[0][j],3*(p[1][j]-p[0][j]),3*(p[2][j]-2*p[1][j]+p[0][j]),p[3][j]-3*p[2][j]+3*p[1][j]-p[0][j]];
specs[2].area=curves.reduce((a,c)=>{const x=poly(c,0),y=poly(c,1);return a+(integral(mul(x,der(y)))-integral(mul(y,der(x))))/2;},0);
const centroid226=[curves.reduce((a,c)=>{const x=poly(c,0),y=poly(c,1);return a+integral(mul(mul(x,x),der(y)));},0)/(2*specs[2].area),-curves.reduce((a,c)=>{const x=poly(c,0),y=poly(c,1);return a+integral(mul(mul(y,y),der(x)));},0)/(2*specs[2].area)];
if(centroid226.some((v,i)=>Math.abs(v-specs[2].centroid[i])>1e-10))throw Error('Oblique oval centroid drift');
specs[2].geometry.independent_polynomial_integral_centroid=centroid226;
function stats(a,W,H,scale){
 let n=0,full=0,sum=0,mx=0,my=0,x0=W,y0=H,x1=0,y1=0;const values=new Set();
 for(let y=0;y<H;y++) for(let x=0;x<W;x++) {const c=a[y*W+x];values.add(c);if(!c)continue;n++;full+=c===255;sum+=c;mx+=c*(x+.5);my+=c*(y+.5);x0=Math.min(x0,x);y0=Math.min(y0,y);x1=Math.max(x1,x+1);y1=Math.max(y1,y+1);}
 return {grid:[W,H],nonzero:n,opaque:full,fractional:n-full,alpha_sum:sum,effective_area_logical:sum/255/scale**2,support_area_logical:n/scale**2,bbox_samples:[x0,y0,x1,y1],bbox_logical:[x0/scale,y0/scale,x1/scale,y1/scale],alpha_weighted_centroid_logical:[mx/sum/scale,my/sum/scale],unique_alpha:Array.from(values).sort((a,b)=>a-b)};
}
const sample=(a,d)=>{const W=12*d,H=14*d,stride=8/d,off=stride/2;return Uint8Array.from({length:W*H},(_,i)=>a[(Math.floor(i/W)*stride+off)*96+(i%W)*stride+off]);};
const rows=[];
for(const s of specs){
 const svg=`<svg xmlns="http://www.w3.org/2000/svg" width="96" height="112" viewBox="0 0 12 14"><title>Protron ${s.id}: independently authored semantic shadow coverage</title><desc>Opaque geometric interior; raster boundary antialiasing only. Original 12 by 14 canvas and zero anchor. Offline pilot, not frozen or installed.</desc><g fill="#fff" fill-opacity="1" stroke="none">${s.element}</g></svg>\n`;
 const stem=path.join(here,`shadow-${s.id}-8`);fs.writeFileSync(stem+'.svg',svg);
 execFileSync('inkscape',[stem+'.svg','--export-type=png','--export-filename='+stem+'.png','--export-width=96','--export-height=112'],{stdio:'pipe'});
 const alpha=execFileSync('convert',[stem+'.png','-alpha','extract','-depth','8','gray:-']);
 if(alpha.length!==96*112)throw Error('Wrong mask length');
 fs.writeFileSync(stem+'.coverage.bin',alpha);
 const a2=sample(alpha,2),a4=sample(alpha,4);
 const st8=stats(alpha,96,112,8),st2=stats(a2,24,28,2),st4=stats(a4,48,56,4);
 if(JSON.stringify(st8.bbox_logical)!==JSON.stringify(s.bbox))throw Error('Semantic bbox changed');
 if(!st8.opaque||!st8.fractional)throw Error('Need exact full interior and edge-only AA');
 rows.push({id:s.id,label:s.label,geometry:s.geometry,semantic_bbox_logical:s.bbox,semantic_width:s.bbox[2]-s.bbox[0],semantic_height:s.bbox[3]-s.bbox[1],continuous_centroid_logical:s.centroid,continuous_area_logical:s.area,canvas:[12,14],anchor:[0,0],shadow_origin:'Unchanged: original caller emits (x+1,y+shadowYDist); no runtime edits',antialias:'SVG path boundary coverage only, no blur/filter/opacity/normalization; nominal density8 boundary pixel footprint 0.125 logical pixel',svg_sha256:sha(svg),png_sha256:sha(fs.readFileSync(stem+'.png')),coverage_sha256:sha(alpha),density8:st8,native2x:{...st2,alpha_hex_rows:Array.from({length:28},(_,y)=>Buffer.from(a2.slice(y*24,(y+1)*24)).toString('hex'))},native4x:{...st4,alpha_hex_rows:Array.from({length:56},(_,y)=>Buffer.from(a4.slice(y*48,(y+1)*48)).toString('hex'))}});
}
const manifest={status:'OFFLINE_GEOMETRY_PILOT_REQUIRES_ROOT_CONTOUR_GATE',production_changes:0,runtime_runs:0,input_artwork:'NONE: independently authored geometry; original semantic dimensions/registration are numeric constraints only',renderer:{inkscape:execFileSync('inkscape',['--version'],{encoding:'utf8'}).trim(),imagemagick:execFileSync('convert',['--version'],{encoding:'utf8'}).split('\n')[0],node:process.version},sampling:'Native2x: A8[4*y+2,4*x+2]. Native4x: A8[2*y+1,2*x+1]. Never resize an existing native image.',rows};
fs.writeFileSync(path.join(here,'manifest.json'),JSON.stringify(manifest,null,2)+'\n');
console.log(JSON.stringify(rows.map(r=>({id:r.id,bbox:r.density8.bbox_logical,centroid:r.density8.alpha_weighted_centroid_logical,area:r.density8.effective_area_logical,native2x:{full:r.native2x.opaque,positive:r.native2x.nonzero,area:r.native2x.effective_area_logical}})),null,2));
