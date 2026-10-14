// Rebuild frozen Data513 resources from authored SVG and phase parameters only.
// Usage: node rebuild.cjs /absolute/path/to/new-output-directory
const fs=require('fs'),path=require('path'),crypto=require('crypto'),sharp=require('sharp');
const P=__dirname,O=path.resolve(process.argv[2]||path.join(P,'output'));
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const inv=fs.existsSync(path.join(P,'inventory.json'))?JSON.parse(fs.readFileSync(path.join(P,'inventory.json'),'utf8')):null;
if(fs.existsSync(O))throw Error('Output directory must not exist; choose a new path.');
if(inv)for(const [file,hash]of Object.entries(inv.inputs))if(sha(fs.readFileSync(path.join(P,file)))!==hash)throw Error('Input hash mismatch: '+file);
const template=fs.readFileSync(path.join(P,'sources/cube-template.svg'),'utf8');
const phases=JSON.parse(fs.readFileSync(path.join(P,'sources/phase-spec.json'),'utf8')).phases;
const expected=[159,161,163,197,199,201,235,237,239,273,275,277];
if(JSON.stringify(phases.map(p=>p.base))!==JSON.stringify(expected))throw Error('Finite phase list mismatch');
const fnv=b=>{let h=14695981039346656037n;for(const v of b)h=((h^BigInt(v))*1099511628211n)&0xffffffffffffffffn;return h.toString(16).padStart(16,'0');};
(async()=>{
 fs.mkdirSync(O,{recursive:true});let rows=[],alpha=null;
 for(let index=0;index<phases.length;index++){
  const phase=phases[index],base=phase.base,key=1240000+base;
  const svg=template.replace(/\{\{([A-Z_]+)\}\}/g,(_,k)=>{if(!phase.colors[k])throw Error('Missing color '+k);return phase.colors[k];});
  const rgba=await sharp(Buffer.from(svg)).ensureAlpha().raw().toBuffer();
  if(rgba.length!==172032)throw Error('RGBA dimensions mismatch');
  const al=Buffer.alloc(192*224),hist={};let nonzero=0,fractional=0;
  for(let i=0;i<al.length;i++){
   const v=rgba[4*i+3];al[i]=v;hist[v]=(hist[v]||0)+1;if(v)nonzero++;if(v&&v<255)fractional++;if(!v)rgba.fill(0,4*i,4*i+3);
  }
  if(alpha&&!alpha.equals(al))throw Error('Phase alpha drift');alpha=al;
  const prefix=`data513-bank11-${base}-8`,png=path.join(O,prefix+'.png');
  await sharp(rgba,{raw:{width:192,height:224,channels:4}}).png().toFile(png);
  const header=Buffer.alloc(28);header.write('HDR1',0,'ascii');[key,8,24,28,6,7].forEach((v,i)=>header.writeUInt32LE(v,4+4*i));
  const hda=Buffer.concat([header,rgba]);if(hda.length!==172060)throw Error('Exact EOF size mismatch');fs.writeFileSync(path.join(O,prefix+'.hda'),hda);
  const row={id:base,role:124,slot:510+index,key,png:prefix+'.png',hda:prefix+'.hda',PNG_SHA256:sha(fs.readFileSync(png)),RGBA_SHA256:sha(rgba),HDA_SHA256:sha(hda),RGBA_FNV1a64:fnv(rgba),ALPHA_SHA256:sha(al),nonzero_samples:nonzero,fractional_samples:fractional,alpha_histogram:hist};
  if(inv&&JSON.stringify(row)!==JSON.stringify(inv.outputs[index]))throw Error('Frozen output hash or metadata mismatch: '+base);
  rows.push(row);
 }
 fs.writeFileSync(path.join(O,'rebuild-receipt.json'),JSON.stringify({pass:true,authored_vector_only:true,no_original_raster_or_mask_inputs:true,all_phase_alpha_identical:true,outputs:rows},null,2)+'\n');
 console.log('PASS: twelve exact authored-vector Data513 PNG/HDR1 resources.');
})().catch(e=>{console.error(e);process.exitCode=1;});
