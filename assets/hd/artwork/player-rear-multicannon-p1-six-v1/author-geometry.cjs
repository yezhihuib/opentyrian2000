'use strict';
// New semantic cubic-Bezier geometry. No raster tracing, bitmap masks, original data,
// images, screenshots, pixel arrays, or private paths are used by this authoring program.
// The rounded leading cap and smoothly tapered wake extend the accepted front-Multi style.
const fs=require('fs'),path=require('path');
const output=path.resolve(process.argv[2]||__dirname);
const stops=[['0','#fffaa1'],['.19','#fff06b'],['.38','#ffd338'],['.57','#ff9e1c'],['.75','#ff680a'],['.91','#ef3904'],['1','#cd2102']];
const geometry={
 right:{path:'M9.45 4 C10.95 4 12 4.72 12 6 C12 7.23 11.18 8 9.55 8 C7.13 8 4.17 7.56 1 6.92 C2.31 5.87 3.92 4.93 6.28 4.39 C7.46 4.12 8.48 4 9.45 4Z',heat:{cx:10.18,cy:6.05,dx:-.9961947,dy:.0871557,L:9.1,W:1.8}},
 left:{path:'M2.25 4 C.91 4 0 4.8 0 6 C0 7.27 .86 8 2.24 8 C4.63 8 7.86 6.72 11 5.25 C8.34 4.57 5.44 4 2.25 4Z',heat:{cx:1.68,cy:5.92,dx:.9961947,dy:-.0871557,L:9.1,W:1.8}},
 diagonal:{path:'M1.58 0 C.66 0 0 .72 0 1.73 C0 2.88 1.11 3.62 2.86 4.25 C5.15 5.07 8.16 5.7 11 6 C9.13 4.46 6.67 2.84 4.63 1.5 C3.33 .64 2.66 0 1.58 0Z',heat:{cx:1.65,cy:1.65,dx:.9015231,dy:.4327311,L:9.1,W:1.8}}
};
const specs=[
 {id:1,mode:1,phase:2,kind:'right',bounds:[1,4,12,8],transform:'',transform_name:'independent'},
 {id:39,mode:1,phase:1,kind:'left',bounds:[0,4,11,8],transform:'',transform_name:'independent'},
 {id:281,mode:2,phase:1,kind:'diagonal',bounds:[0,0,11,6],transform:'',transform_name:'identity'},
 {id:282,mode:2,phase:2,kind:'diagonal',bounds:[1,0,12,6],transform:'translate(12 0) scale(-1 1)',transform_name:'flipX'},
 {id:300,mode:2,phase:4,kind:'diagonal',bounds:[0,8,11,14],transform:'translate(0 14) scale(1 -1)',transform_name:'flipY'},
 {id:301,mode:2,phase:3,kind:'diagonal',bounds:[1,8,12,14],transform:'translate(12 14) scale(-1 -1)',transform_name:'rotate180'}
];
const gradient=h=>`<defs><radialGradient id="streak" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="matrix(${h.L*h.dx} ${h.L*h.dy} ${-h.W*h.dy} ${h.W*h.dx} ${h.cx} ${h.cy})">${stops.map(([offset,color])=>`<stop offset="${offset}" stop-color="${color}"/>`).join('')}</radialGradient></defs>`;
// Inward-only vector coverage falloff: 32 thin nested strokes encode a smoothstep
// opacity ramp over the inner 0.30 logical pixel of the SAME cubic silhouette.
// The colored path is clipped by its own geometry; no outer halo or color blur.
const coverageMask=g=>`<defs><mask id="edgeCoverage" maskUnits="userSpaceOnUse" maskContentUnits="userSpaceOnUse" x="0" y="0" width="12" height="14"><path d="${g.path}" fill="white"/>${Array.from({length:32},(_,i)=>{let t=(32-i)/32,a=.62+.38*(t*t*(3-2*t)),v=Math.round(255*a);return `<path d="${g.path}" fill="none" stroke="rgb(${v},${v},${v})" stroke-width="${.60*t}" stroke-linejoin="round"/>`;}).join('')}</mask></defs>`;
function svg(s){const g=geometry[s.kind];return `<svg xmlns="http://www.w3.org/2000/svg" width="96" height="112" viewBox="0 0 12 14">\n<!-- Rear Multi-Cannon 10 P1 art pilot. Original bank8 identity ${s.id}; this is not an HDA role or resource key. Static 12x14 canvas; anchor 0,0. -->\n${s.transform?`<g transform="${s.transform}">`:''}\n${gradient(g.heat)}\n${coverageMask(g)}\n<path d="${g.path}" fill="url(#streak)" mask="url(#edgeCoverage)"/>\n${s.transform?'</g>':''}\n</svg>\n`;}
const contract={schema:'rear-multi-p1-semantic-geometry-v1',status:'R2-approved-for-runtime-evaluation-not-publication',scope:'Six static player rear Multi-Cannon 10 power-1 heads, two modes; binding and publication are separate.',logical_size:[12,14],anchor:[0,0],densities:[4,8],role_id:null,resource_keys:null,authoring:'Three new authored smooth cubic-Bezier silhouettes, one continuous elliptical heat field each. Two independent lateral heads and one canonical diagonal head with exact whole-canvas transforms.',coverage_softness:{method:'32 nested vector boundary strokes encoding an inward smoothstep luminance mask',inner_width_logical:.30,minimum_boundary_coverage_factor:.62,external_halo:false,color_blur:false,raw_RGB_policy:'Preserve the exact unsoftened vector-render RGB at every supported sample; replace alpha only. Preserve nonzero support with minimum alpha1.'},raster_geometry_inputs:false,original_inputs_required_to_rebuild:false,style_lineage:'Accepted generated front-Multi eight-head semantic SVG heat-field style; new rear geometry.',shading:{gradient:'elliptical radial',stops,blur:false,halo:false,metallic_casing:false,dark_outline:false,animation:false},geometries:geometry,specs:specs.map(s=>({...s,empty_margins:[s.bounds[0],s.bounds[1],12-s.bounds[2],14-s.bounds[3]]})),transform_contract:{mode1:'1 and 39 are independently authored and must not become exact mirror copies.',mode2:'282=flipX(281),300=flipY(281),301=rotate180(281) over the full 12x14 canvas, including empty margins.'},render_contract:'Render d4 and d8 independently from vector geometry; retain unsoftened RGB while applying inward-only vector coverage mask alpha and preserve every originally nonzero support sample. Canonical diagonal is rasterized once at each density, then exact byte permutations produce its transform variants. Each standalone transformed SVG is also independently rasterized and compared; rasterizer rounding differences are measured, never hidden.',not_in_scope:['gameplay mechanics','runtime integration','HDA role or key assignment','original indexed shadows','night-filter changes','new animation','additional weapon powers or families','publication']};
fs.mkdirSync(path.join(output,'sources'),{recursive:true});
for(const s of specs)fs.writeFileSync(path.join(output,'sources',`rear-multi-${s.id}.svg`),svg(s));
fs.writeFileSync(path.join(output,'semantic-contract.json'),JSON.stringify(contract,null,2)+'\n');
console.log('Authored six standalone semantic SVGs and geometry contract.');
