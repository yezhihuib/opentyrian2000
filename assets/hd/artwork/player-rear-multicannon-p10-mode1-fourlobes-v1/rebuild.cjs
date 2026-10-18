'use strict';
// Portable generated-only rebuild. It writes only to a fresh explicit directory.
const fs=require('fs'),path=require('path'),crypto=require('crypto'),cp=require('child_process'),sharp=require('sharp');
const ROOT=__dirname,sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const out=process.argv[2]&&path.resolve(process.argv[2]);
if(!out||fs.existsSync(out))throw Error('Usage: node rebuild.cjs /absolute/fresh/output; destination must not exist.');
const freeze=JSON.parse(fs.readFileSync(path.join(ROOT,'freeze.json'))),binding=JSON.parse(fs.readFileSync(path.join(ROOT,'binding.json'))),inputs=JSON.parse(fs.readFileSync(path.join(ROOT,'inputs.json')));
for(const input of inputs.inputs)if(sha(fs.readFileSync(path.join(ROOT,input.path)))!==input.sha256)throw Error('Accepted public style input hash mismatch');
const generator=path.join(ROOT,'src','author-candidates.cjs');
if(sha(fs.readFileSync(generator))!==freeze.reviewed_generator_sha256)throw Error('Reviewed generator changed');
const expected=JSON.parse(fs.readFileSync(path.join(ROOT,'output','candidate-contract.json'))).versions;
if(process.version!==expected.node||JSON.stringify(sharp.versions)!==JSON.stringify(expected.sharp))throw Error('Pinned Node/Sharp renderer versions required');
const result=cp.spawnSync(process.execPath,[generator,out],{cwd:ROOT,encoding:'utf8'});
if(result.status!==0)throw Error(result.stderr||result.stdout||'Generator failed');
for(const [rel,hash] of Object.entries(freeze.frozen_files))if(sha(fs.readFileSync(path.join(out,path.basename(rel))))!==hash)throw Error('Frozen reviewed output mismatch: '+rel);
const rows=[];
for(const e of binding.resources){
 const raw=fs.readFileSync(path.join(out,path.basename(e.rgba))),h=Buffer.alloc(28);h.write('HDR1');
 [e.key,e.density,12,14,0,0].forEach((value,i)=>h.writeUInt32LE(value,4+i*4));
 const packed=Buffer.concat([h,raw]);if(sha(raw)!==e.rgba_sha256||sha(packed)!==e.hda_sha256)throw Error('Frozen payload/HDR1 mismatch');
 const name=path.basename(e.package_hda);fs.writeFileSync(path.join(out,name),packed);rows.push({file:name,sha256:sha(packed),bytes:packed.length});
}
const receipt={schema:'rear-multi-p10-mode1-portable-rebuild-v1',result:'PASS',generated_only:true,original_inputs_or_captures:false,reviewed_outputs_exact:11,hda_outputs:rows,versions:expected};
fs.writeFileSync(path.join(out,'rebuild-receipt.json'),JSON.stringify(receipt,null,2)+'\n');
console.log('PASS: eleven frozen SVG/PNG/RGBA/contract files and four exact HDR1 resources rebuilt without original inputs.');
