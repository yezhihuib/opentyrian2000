// Rebuild finite frozen normal Vulcan67/70 art from authored SVG only.
// node rebuild.cjs /absolute/new/output-directory
const fs=require('fs'),path=require('path'),crypto=require('crypto'),sharp=require('sharp');
const P=__dirname,O=path.resolve(process.argv[2]||path.join(P,'output'));
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const fnv=b=>{let h=14695981039346656037n;for(const v of b)h=((h^BigInt(v))*1099511628211n)&0xffffffffffffffffn;return h.toString(16).padStart(16,'0');};
const specs=[{id:67,svg:'single-tracer.svg',slot:522},{id:70,svg:'twin-tracer.svg',slot:523}];
const inv=fs.existsSync(path.join(P,'inventory.json'))?JSON.parse(fs.readFileSync(path.join(P,'inventory.json'),'utf8')):null;
if(fs.existsSync(O))throw Error('Output must not exist');
if(inv)for(const [name,hash]of Object.entries(inv.inputs))if(sha(fs.readFileSync(path.join(P,name)))!==hash)throw Error('Input hash mismatch: '+name);
(async()=>{fs.mkdirSync(O,{recursive:true});let rows=[];
for(const spec of specs){const svg=fs.readFileSync(path.join(P,'sources',spec.svg));const {data:rgba,info}=await sharp(svg).ensureAlpha().raw().toBuffer({resolveWithObject:true});if(info.width!==96||info.height!==112||rgba.length!==43008)throw Error('Dimensions');let alpha=Buffer.alloc(10752),hist={},nonzero=0,fractional=0,bbox=[96,112,0,0];
for(let i=0;i<alpha.length;i++){let v=rgba[i*4+3];alpha[i]=v;hist[v]=(hist[v]||0)+1;if(v){nonzero++;let x=i%96,y=Math.floor(i/96);bbox=[Math.min(bbox[0],x),Math.min(bbox[1],y),Math.max(bbox[2],x+1),Math.max(bbox[3],y+1)];if(v<255)fractional++;}else rgba.fill(0,4*i,4*i+3);}
const prefix=`bullet-${spec.id}-8`,png=prefix+'.png',hda=prefix+'.hda',key=80000+spec.id;await sharp(rgba,{raw:{width:96,height:112,channels:4}}).png().toFile(path.join(O,png));
const header=Buffer.alloc(28);header.write('HDR1',0,'ascii');[key,8,12,14,0,0].forEach((v,i)=>header.writeUInt32LE(v,4+i*4));const bytes=Buffer.concat([header,rgba]);if(bytes.length!==43036)throw Error('Exact EOF');fs.writeFileSync(path.join(O,hda),bytes);
const row={id:spec.id,role:8,key,slot:spec.slot,logical_size:[12,14],anchor:[0,0],density:8,authored_size:[96,112],png,hda,PNG_SHA256:sha(fs.readFileSync(path.join(O,png))),RGBA_SHA256:sha(rgba),HDA_SHA256:sha(bytes),RGBA_FNV1a64:fnv(rgba),ALPHA_SHA256:sha(alpha),bbox,nonzero_samples:nonzero,fractional_samples:fractional,alpha_histogram:hist};
if(inv&&JSON.stringify(row)!==JSON.stringify(inv.outputs.find(r=>r.id===spec.id)))throw Error('Frozen output mismatch: '+spec.id);rows.push(row);}
fs.writeFileSync(path.join(O,'rebuild-receipt.json'),JSON.stringify({pass:true,source_only_rebuild:true,original_raster_or_mask_inputs:false,outputs:rows},null,2)+'\n');console.log('PASS: two exact authored-vector Vulcan PNG/HDR1 resources.');})().catch(e=>{console.error(e);process.exitCode=1;});
