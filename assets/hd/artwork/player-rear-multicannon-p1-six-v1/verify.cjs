'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {sha,transform}=require('./render.cjs');const P=__dirname;
const inv=JSON.parse(fs.readFileSync(path.join(P,'inventory.json'))),contract=JSON.parse(fs.readFileSync(path.join(P,'semantic-contract.json')));
for(const [name,hash]of Object.entries(inv.inputs))assert.equal(sha(fs.readFileSync(path.join(P,name))),hash,name);
const rows=[];
for(const d of [4,8]){
 const w=12*d,h=14*d,raw={};
 for(const s of contract.specs){const r=inv.outputs.find(x=>x.id===s.id&&x.density===d),b=fs.readFileSync(path.join(P,'output',r.rgba));raw[s.id]=b;assert.equal(b.length,w*h*4);assert.equal(sha(b),r.rgba_sha256);assert.equal(sha(fs.readFileSync(path.join(P,'output',r.png))),r.png_sha256);
  assert.deepEqual(r.bounds_pixels,s.bounds.map(v=>v*d),'Support bounds');
  let outside_nonzero=0,hidden_rgb=0;
  for(let y=0;y<h;y++)for(let x=0;x<w;x++){let i=(y*w+x)*4;let inside=x>=s.bounds[0]*d&&x<s.bounds[2]*d&&y>=s.bounds[1]*d&&y<s.bounds[3]*d;if(!inside&&b[i+3])outside_nonzero++;if(!b[i+3]&&(b[i]||b[i+1]||b[i+2]))hidden_rgb++;}
  assert.equal(outside_nonzero,0);assert.equal(hidden_rgb,0);assert.ok(r.fractional_alpha_samples>0);
  const svg=fs.readFileSync(path.join(P,r.svg),'utf8');assert.match(svg,/<path /);assert.match(svg,/<radialGradient /);assert.match(svg,/<mask id="edgeCoverage" /);assert.equal((svg.match(/stroke-width=/g)||[]).length,32,'32 semantic vector-mask strokes');assert.doesNotMatch(svg,/<(?:image|filter|script|animate)\b|href=|data:|<rect\b/i);
  rows.push({id:s.id,density:d,bounds:r.bounds_pixels,empty_margins_preserved:true,hidden_rgb_zero:true,antialiased_vector_edges:true});
 }
 for(const [id,op]of [[282,'flipX'],[300,'flipY'],[301,'rotate180']])assert.deepEqual(raw[id],transform(raw[281],w,h,op),'Exact whole-canvas '+op);
 const reflected=transform(raw[1],w,h,'flipX');assert.notDeepEqual(raw[39],reflected,'Mode1 must differ');let alpha_diff=0;for(let i=3;i<reflected.length;i+=4)if(reflected[i]!==raw[39][i])alpha_diff++;assert.ok(alpha_diff>0);rows.push({density:d,mode2_byte_exact_transforms:true,mode1_mirror_alpha_differences:alpha_diff});
}
console.log(JSON.stringify({pass:true,tests:rows},null,2));
