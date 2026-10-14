#!/usr/bin/env node
/** Rebuild only this generated-only artwork directory. Never reads game assets. */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
const here=path.dirname(fileURLToPath(import.meta.url));
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
function fnv(b){let n=0xcbf29ce484222325n;for(const x of b)n=((n^BigInt(x))*0x100000001b3n)&0xffffffffffffffffn;return n.toString(16).padStart(16,'0');}
const contract=JSON.parse(fs.readFileSync(path.join(here,'contract.json')));
const temporary=fs.mkdtempSync('/tmp/protron-shadow-frozen-rebuild-');
fs.copyFileSync(path.join(here,'source/render.mjs'),path.join(temporary,'render.mjs'));
execFileSync(process.execPath,[path.join(temporary,'render.mjs')],{stdio:'pipe'});
const manifest=JSON.parse(fs.readFileSync(path.join(temporary,'manifest.json')));
const outputs=[];
for(const pin of contract.pins){
 const stem=path.join(temporary,`shadow-${pin.id}-8`),svg=fs.readFileSync(stem+'.svg'),png=fs.readFileSync(stem+'.png'),coverage=fs.readFileSync(stem+'.coverage.bin');
 if(sha(svg)!==pin.svg_sha256||sha(png)!==pin.png_sha256||sha(coverage)!==pin.coverage_sha256)throw Error(`Approved ${pin.id} artwork changed`);
 if(!svg.equals(fs.readFileSync(path.join(here,`source/shadow-${pin.id}-8.svg`))))throw Error('Frozen vector source mismatch');
 const rgba=execFileSync('convert',[stem+'.png','-depth','8','rgba:-']);
 if(rgba.length!==96*112*4||coverage.length!==96*112)throw Error('Wrong size');
 for(let i=0;i<coverage.length;i++)if(rgba[4*i+3]!==coverage[i])throw Error('PNG alpha differs from frozen coverage');
 const header=Buffer.alloc(28);header.write('HDR1',0,'ascii');[pin.key,8,12,14,0,0].forEach((n,i)=>header.writeUInt32LE(n,4+i*4));const hda=Buffer.concat([header,rgba]);
 const name=`protron-shadow-${pin.id}-8`;
 fs.writeFileSync(path.join(here,'output',name+'.png'),png);fs.writeFileSync(path.join(here,'output',name+'.hda'),hda);fs.writeFileSync(path.join(here,'output',name+'.coverage.bin'),coverage);
 outputs.push({id:pin.id,role:125,slot:pin.slot,key:pin.key,filename:name+'.hda',logical_size:[12,14],pixel_size:[96,112],anchor:[0,0],density:8,bytes:hda.length,SVG_SHA256:sha(svg),PNG_SHA256:sha(png),HDA_SHA256:sha(hda),RGBA_SHA256:sha(rgba),RGBA_FNV1a64:fnv(rgba),COVERAGE_SHA256:sha(coverage),COVERAGE_FNV1a64:fnv(coverage)});
}
manifest.status='FROZEN_GEOMETRY_APPROVED_RUNTIME_PENDING';manifest.root_contour_gate_reported_utc=contract.root_contour_gate_reported_utc;
fs.writeFileSync(path.join(here,'proof/geometry.json'),JSON.stringify(manifest,null,2)+'\n');
const inputs={};for(const name of ['rebuild.mjs','contract.json','source/render.mjs',...contract.pins.map(p=>`source/shadow-${p.id}-8.svg`)])inputs[name]=sha(fs.readFileSync(path.join(here,name)));
const inventory={status:'FROZEN_GENERATED_ONLY_ARTWORK',approval_scope:'Contour/coverage only; no runtime or publication acceptance',inputs,outputs,renderer:manifest.renderer,original_game_pixel_inputs:0,head_asset_edits:0,production_code_changes:0,runtime_runs:0};
fs.writeFileSync(path.join(here,'inventory.json'),JSON.stringify(inventory,null,2)+'\n');
console.log(JSON.stringify(outputs,null,2));
