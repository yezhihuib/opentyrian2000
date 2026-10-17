'use strict';
// Generated vector geometry only. No game raster, palette, mask, capture, or
// extracted sprite is read. This is a newly authored twin silhouette, not a
// claim that the original sprite is an exact transform of accepted artwork.
const fs=require('fs'),path=require('path');
const stops=[['0','#fffaa1'],['.19','#fff06b'],['.38','#ffd338'],['.57','#ff9e1c'],['.75','#ff680a'],['.91','#ef3904'],['1','#cd2102']];
// Semantic down-left streak: rounded leading cap, two continuous cubic sides,
// narrow tail. Logical bounds [0,1,9,11]. The other streak is offset (+3,+3).
const streak='M1.4 11 C.48 11 0 10.3 0 9.35 C0 7.85 1.14 6.65 2.60 5.39 C4.42 3.79 6.91 1.99 8.72 1.10 Q8.9 1 9 1 C8.14 3.42 6.33 5.75 4.60 7.77 C3.4 9.20 3.21 10.98 1.4 11Z';
const heat={cx:1.35,cy:9.5,dx:Math.SQRT1_2,dy:-Math.SQRT1_2,L:7.8,W:1.62};
function svg(id){
 const h=heat;
 const grad=`<defs><radialGradient id="streak" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="matrix(${h.L*h.dx} ${h.L*h.dy} ${-h.W*h.dy} ${h.W*h.dx} ${h.cx} ${h.cy})">${stops.map(([offset,color])=>`<stop offset="${offset}" stop-color="${color}"/>`).join('')}</radialGradient></defs>`;
 const one=`<path d="${streak}" fill="url(#streak)"/>`;
 return `<svg xmlns="http://www.w3.org/2000/svg" width="96" height="112" viewBox="0 0 12 14">\n<!-- OFFLINE P7 MODE2 CANDIDATE. ${id}: two ${id===294?'down-left':'down-right'} luminous streaks. New semantic geometry; no raster tracing. Canvas12x14 anchor0,0. -->\n${grad}\n${id===295?'<g transform="translate(12 0) scale(-1 1)">':''}\n${one}\n<g transform="translate(3 3)">${one}</g>\n${id===295?'</g>':''}\n</svg>\n`;
}
const contract={schema:'rear-multicannon-p7-mode2-semantic-candidate-v1',status:'OFFLINE_ART_CANDIDATE_NOT_RUNTIME_APPROVED',role:131,resources:[{id:294,key:1310294,velocity:[-6,6]},{id:295,key:1310295,velocity:[6,6]}],logical_size:[12,14],anchor:[0,0],densities:[4,8],semantic_bounds:[0,1,12,14],streak_bounds:[0,1,9,11],twin_offset:[3,3],geometry:streak,heat,stops,style_lineage:'Accepted generated player-front-multi-eight-v1 continuous elliptical heat field and cubic cap/taper vocabulary. Newly authored narrower/shorter twin primitive, not an exact original-source reuse.',edge:'Ordinary SVG rasterizer antialiasing only. No casing, outline, gray, color blur, glow, external halo, or traced pixel boundary.',transform:'295 is the exact full-canvas horizontal reflection of newly authored294, including empty margins. Canonical294 is independently rendered directly from SVG at each density. Standalone295 SVG is independently compared, but canonical payload uses an exact RGBA reflection to eliminate rasterizer asymmetry.',original_data_or_captures_required:false,original_data_or_captures_in_package:false,no_native_1x_intermediate:true,scope_exclusions:['production edits','runtime bindings or integration','gameplay changes','runtime acceptance','publication']};
function author(out){fs.mkdirSync(path.join(out,'sources'),{recursive:true});for(const id of [294,295])fs.writeFileSync(path.join(out,'sources',`rear-multi-${id}.svg`),svg(id));fs.writeFileSync(path.join(out,'semantic-contract.json'),JSON.stringify(contract,null,2)+'\n');}
module.exports={svg,contract,author};
if(require.main===module)author(path.resolve(process.argv[2]||__dirname));
