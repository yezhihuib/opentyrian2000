'use strict';
// Optional binder utility. Art source identity is not an HDA resource key.
// Each of 12 output entries must explicitly supply source_id, density, key, and filename.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const [mapArg,outArg]=process.argv.slice(2);
if(!mapArg||!outArg)throw Error('Usage: node pack-hda.cjs /absolute/bindings.json /absolute/new-output-directory');
const P=__dirname,O=path.resolve(outArg),mapping=JSON.parse(fs.readFileSync(mapArg,'utf8')),inv=JSON.parse(fs.readFileSync(path.join(P,'inventory.json'),'utf8'));
if(fs.existsSync(O))throw Error('Output directory must not exist');
if(!Array.isArray(mapping)||mapping.length!==12)throw Error('Exactly 12 explicit bindings are required');
const used=new Set(),names=new Set(),byKey=new Map();let prepared=[];
for(const b of mapping){
 if(![1,39,281,282,300,301].includes(b.source_id)||![4,8].includes(b.density))throw Error('Invalid source identity or density');
 if(!Number.isInteger(b.key)||b.key<1||b.key>0xffffffff)throw Error('Explicit uint32 key required');
 if(typeof b.filename!=='string'||!/^[a-zA-Z0-9_-]+\.hda$/.test(b.filename))throw Error('Explicit safe HDA filename required');
 const token=b.source_id+':'+b.density;if(used.has(token)||names.has(b.filename))throw Error('Duplicate identity or filename');used.add(token);names.add(b.filename);
 if(byKey.has(b.key)&&byKey.get(b.key)!==b.source_id)throw Error('Resource key reused for a different source');byKey.set(b.key,b.source_id);
 const r=inv.outputs.find(x=>x.id===b.source_id&&x.density===b.density),rgba=fs.readFileSync(path.join(P,'output',r.rgba));
 if(rgba.length!==r.rgba_byte_length||sha(rgba)!==r.rgba_sha256)throw Error('Frozen payload mismatch');
 const h=Buffer.alloc(28);h.write('HDR1',0,'ascii');[b.key,b.density,12,14,0,0].forEach((v,i)=>h.writeUInt32LE(v,4+4*i));
 prepared.push({b,rgba,r,bytes:Buffer.concat([h,rgba])});
}
fs.mkdirSync(O,{recursive:true});let rows=[];
for(const {b,bytes,r}of prepared){fs.writeFileSync(path.join(O,b.filename),bytes);rows.push({...b,logical_size:[12,14],anchor:[0,0],hda_bytes:bytes.length,hda_sha256:sha(bytes),rgba_sha256:r.rgba_sha256,rgba_fnv1a64:r.rgba_fnv1a64});}
fs.writeFileSync(path.join(O,'pack-receipt.json'),JSON.stringify({schema:'explicit-binder-hda-v1',role_selection_by:'external binding map, not artwork package',outputs:rows},null,2)+'\n');
console.log('Packed 12 frozen art payloads with explicit binder-selected keys and filenames.');
