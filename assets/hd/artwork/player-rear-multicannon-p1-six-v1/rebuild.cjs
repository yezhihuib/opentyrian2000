'use strict';
const fs=require('fs'),path=require('path'),sharp=require('sharp');
const {render,sha}=require('./render.cjs');
const P=__dirname,O=path.resolve(process.argv[2]||path.join(P,'rebuilt-output'));
(async()=>{
 const inv=JSON.parse(fs.readFileSync(path.join(P,'inventory.json'),'utf8'));
 for(const [name,hash]of Object.entries(inv.inputs))if(sha(fs.readFileSync(path.join(P,name)))!==hash)throw Error('Frozen input mismatch: '+name);
 if(JSON.stringify(sharp.versions)!==JSON.stringify(inv.renderer.sharp))throw Error('Renderer library versions differ from the recorded toolchain');
 if(process.version!==inv.renderer.node||process.platform!==inv.renderer.platform||process.arch!==inv.renderer.architecture)throw Error('Exact rebuild requires recorded Node/platform/architecture');
 const receipt=await render(O);
 if(JSON.stringify(receipt.outputs)!==JSON.stringify(inv.outputs))throw Error('Generated output differs from frozen hash contract');
 if(JSON.stringify(receipt.standalone_svg_comparison)!==JSON.stringify(inv.standalone_svg_comparison))throw Error('Independent SVG rasterizer check differs from contract');
 console.log('PASS: all six vector masters rebuilt into 12 exact density-specific PNG/RGBA outputs without original data.');
})().catch(e=>{console.error(e);process.exitCode=1;});
