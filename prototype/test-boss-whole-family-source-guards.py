#!/usr/bin/env python3
"""Finite source rejection in independent fixtures; no game executable or captures.

Tests call the same pure validators as the builder. CLI output guards and valid
rebuilds also run through its command line. Every real input is fingerprinted.
"""
from pathlib import Path
import argparse
import importlib.util
import json
import os
import shutil
import struct
import subprocess
import sys

from nondefault_pack_fixture import NONDEFAULT_PACK, add_nondefault_pack_fixture

sys.dont_write_bytecode = True
SOURCE = 'assets/hd/artwork/boss-whole-family-v2-inward-alpha'
SCRIPT = 'prototype/build-boss-whole-family-art.py'


def verify_entry_coexistence(repo, out, boss):
    """Use independent copies to prove the narrow shared-empty-quadrant exception."""
    entry_script='prototype/build-newsh4-entry6-art.py'
    entry_source='assets/hd/artwork/newsh4-entry6-v1'
    manifest=boss.load(repo/'assets/hd/manifest.json')
    files={SCRIPT,entry_script,'assets/hd/manifest.json'}
    for source in [SOURCE,boss.V1_SOURCE,entry_source]:
        files.update(p.relative_to(repo).as_posix() for p in (repo/source).rglob('*') if p.is_file())
    for bases in [boss.IDS,[81,83,85,119,121,123]]:
        for base in bases:
            name=f'enemy-newsh4-{base}-8.hda'
            for pack in boss.DEFAULTS:
                files.add(f'assets/hd/packs/{pack}/{name}')
                files.add(manifest['packs'][pack]['files'][name]['source_png'])
    before={n:boss.sha(boss.read_regular(repo/n)) for n in files}
    fixture=out/'entry-coexistence-fixture'
    for name in files:
        boss.safe_relative(name)
        dst=fixture/name;dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(repo/name,dst)
        boss.require(not dst.samefile(repo/name),'coexistence fixture hardlink forbidden')
    spec=importlib.util.spec_from_file_location('entry_art',fixture/entry_script)
    entry=importlib.util.module_from_spec(spec);spec.loader.exec_module(entry)
    entry.inventory(fixture/entry_source)
    def validate():
        return entry.validate_art_and_bindings(fixture,fixture/entry_source,boss.load(fixture/'assets/hd/manifest.json'))
    validate()
    checks=[]
    def reject(label,reason):
        try:
            validate()
        except (ValueError,KeyError,TypeError,OSError,IndexError,struct.error) as exc:
            boss.require(reason in str(exc),f'{label}: expected {reason!r}; got {exc!r}')
            checks.append({'case':label,'reason':reason})
        else:
            raise ValueError('coexistence widened scope: '+label)
    manifest_path=fixture/'assets/hd/manifest.json';original_manifest=manifest_path.read_bytes()
    for label,base,mutation,reason in [
        ('missing-late-member',280,None,'regular file required'),
        ('corrupt-late-member',280,lambda b:b[:-1],'HDR1 length/EOF mismatch'),
        ('corrupt86-payload',86,lambda b:b[:-1]+bytes([b[-1]^1]),'HDR1 frozen payload mismatch'),
        ('raw86-not-composite',86,lambda b:b[:12]+struct.pack('<II',12,14)+b[20:],'HDR1 dimensions/anchor/key mismatch'),
        ('raw124-not-composite',124,lambda b:b[:12]+struct.pack('<II',12,14)+b[20:],'HDR1 dimensions/anchor/key mismatch'),
    ]:
        path=fixture/f'assets/hd/packs/{boss.DEFAULTS[0]}/enemy-newsh4-{base}-8.hda';raw=path.read_bytes()
        try:
            path.unlink() if mutation is None else path.write_bytes(mutation(raw))
            reject(label,reason)
        finally:
            path.write_bytes(raw)
    for label in ['unvalidated-boss-bindings-no-family','flag-only-boss','wrong-boss-record-scope']:
        changed=json.loads(original_manifest)
        if label=='unvalidated-boss-bindings-no-family':
            del changed[boss.FAMILY];reason='widened source PNG index'
        elif label=='flag-only-boss':
            changed[boss.FAMILY]={'enabled':True};reason='family metadata mismatch'
        else:
            changed[boss.FAMILY]['source_records'].append(1);reason='family metadata mismatch'
        try:
            manifest_path.write_text(json.dumps(changed));reject(label,reason)
        finally:
            manifest_path.write_bytes(original_manifest)
    #105/143 are empty raw entry cells and never approved full boss composites.
    for base in [105,143]:
        for form in ['indexed','physical-only']:
            changed=json.loads(original_manifest);pack=changed['packs'][boss.DEFAULTS[0]]
            row=json.loads(json.dumps(pack['files']['enemy-newsh4-86-8.hda']))
            source_path=fixture/f'assets/hd/packs/{boss.DEFAULTS[0]}/enemy-newsh4-86-8.hda'
            raw=source_path.read_bytes();raw=raw[:4]+struct.pack('<I',1020000+base)+raw[8:]
            name=f'enemy-newsh4-{base}-8.hda' if form=='indexed' else f'raw-cell-{base}.bin'
            path=fixture/f'assets/hd/packs/{boss.DEFAULTS[0]}/{name}'
            try:
                path.write_bytes(raw)
                if form=='indexed':
                    row['header_u32'][0]=1020000+base;row['sha256']=boss.sha(raw)
                    pack['files'][name]=row;pack['count']+=1
                    manifest_path.write_text(json.dumps(changed))
                reject(f'raw-{base}-{form}','widened pack, alias, quadrant or density' if form=='indexed' else 'widened on-disk pack inventory')
            finally:
                path.unlink();manifest_path.write_bytes(original_manifest)
    for base in [86,124]:
        raw=(fixture/f'assets/hd/packs/{boss.DEFAULTS[0]}/enemy-newsh4-{base}-8.hda').read_bytes()
        alias=fixture/f'assets/hd/packs/{boss.DEFAULTS[0]}/unapproved-boss-{base}.bin'
        try:
            alias.write_bytes(raw);reject(f'renamed-boss-{base}-physical-alias','widened on-disk pack inventory')
        finally:
            alias.unlink()
    validate()
    boss.require(before=={n:boss.sha(boss.read_regular(repo/n)) for n in files},'real coexistence input changed')
    boss.require(before=={n:boss.sha(boss.read_regular(fixture/n)) for n in files},'coexistence fixture restoration failed')
    return {'status':'PASS','validated_full_composites_only':[86,124],'raw_empty_cells_still_forbidden':[105,143],
            'original_empty_overlap_qualification_unchanged':True,'no_flag_only_or_numeric_exception':True,
            'boss_validation_has_no_entry_dependency':True,'negative_cases':checks,'rejected_count':len(checks),
            'input_file_sha256':before,'real_inputs_unchanged':True,'independent_copies_only':True,
            'game_runs':0,'captures':0,'native_output':False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--original-data',type=Path)
    p.add_argument('--coexistence-only',action='store_true',help='Run only the finite entry/boss source compatibility fixture')
    args = p.parse_args()
    repo = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location('boss_art',repo/SCRIPT)
    boss = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(boss)
    require, sha = boss.require, boss.sha
    out = boss.safe_output(args.out,repo)
    root = boss.original_root(args.original_data,repo) if args.original_data else None
    if root:
        require(out != root and root not in out.parents and out not in root.parents,'output must not overlap original data')
    out.mkdir()
    if args.coexistence_only:
        report=verify_entry_coexistence(repo,out,boss)
        (out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps({k:v for k,v in report.items() if k!='input_file_sha256'},indent=2))
        return
    checks = []
    def reject(label, callback, reason):
        try:
            callback()
        except (ValueError,KeyError,TypeError,OSError,IndexError,struct.error) as exc:
            require(reason in str(exc),f'{label}: expected {reason!r}; got {exc!r}')
            checks.append({'case':label,'reason':reason})
        else:
            raise ValueError('malformed source accepted: '+label)
    def cli(target, original=None):
        cmd=[sys.executable,str(repo/SCRIPT),'--output',str(target)]
        if original:
            cmd += ['--original-data',str(original)]
        return subprocess.run(cmd,capture_output=True,text=True,timeout=90)
    for label,target,reason in [
        ('existing',out,'output must be fresh'),('repository',repo,'output must be fresh'),
        ('repository-child',repo/'boss-forbidden-output','output must be outside repository'),
        ('relative',Path('boss-forbidden-output'),'output must be absolute'),
        ('traversal',out/'..'/'boss-forbidden-output','output traversal forbidden'),
        ('missing-parent',out/'missing'/'output','output parent must exist'),
    ]:
        existed=target.exists()
        result=cli(target)
        require(result.returncode!=0 and 'ERROR:' in result.stderr and reason in result.stderr,label)
        require(existed or not target.exists(),'rejected CLI created output: '+label)
        checks.append({'case':'CLI-'+label,'reason':reason})
    link=out/'link';link.symlink_to(out,target_is_directory=True)
    result=cli(link/'absent')
    require(result.returncode!=0 and 'symlink path forbidden' in result.stderr and not (out/'absent').exists(),'CLI symlink guard')
    checks.append({'case':'CLI-symlink-parent','reason':'symlink path forbidden'})
    manifest=boss.load(repo/'assets/hd/manifest.json')
    files={SCRIPT,'assets/hd/manifest.json',*boss.READERS}
    for art_source in [SOURCE,boss.V1_SOURCE]:
        files.update(p.relative_to(repo).as_posix() for p in (repo/art_source).rglob('*') if p.is_file())
    for base in boss.IDS:
        name=f'enemy-newsh4-{base}-8.hda'
        for pack in boss.DEFAULTS:
            files.add(f'assets/hd/packs/{pack}/{name}')
            files.add(manifest['packs'][pack]['files'][name]['source_png'])
    before={name:sha(boss.read_regular(repo/name)) for name in files}
    fixture=out/'fixture'
    for name in sorted(files):
        boss.safe_relative(name)
        dst=fixture/name;dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(repo/name,dst)
        require(not dst.samefile(repo/name),'fixture hardlink forbidden')
    source=fixture/SOURCE
    frozen=boss.inventory(source)
    logical,outputs=boss.validate_art_and_bindings(fixture,source,manifest,frozen)
    def validate():
        return boss.validate_art_and_bindings(fixture,source,boss.load(fixture/'assets/hd/manifest.json'),boss.inventory(source))
    def change_file(label,relative,callback,reason,mutate=None):
        path=fixture/relative;raw=path.read_bytes()
        try:
            if mutate is None:
                path.unlink()
            else:
                path.write_bytes(mutate(raw))
            reject(label,callback,reason)
        finally:
            path.write_bytes(raw)
    # Both altered and absent forms of every frozen input, output and receipt.
    for path in sorted(source.rglob('*')):
        if not path.is_file():
            continue
        relative=path.relative_to(fixture).as_posix()
        name=path.relative_to(source).as_posix()
        change_file('changed-frozen-'+name,relative,lambda:boss.inventory(source),
                    'source inventory freeze mismatch' if name=='inventory.json' else 'source file mismatch',lambda b:b+b'\0')
        change_file('missing-frozen-'+name,relative,lambda:boss.inventory(source),
                    'inventory.json' if name=='inventory.json' else 'source inventory differs')
    # Direct semantic checks are independent of frozen-file hash rejection.
    # They prove RGB, locked/interior, edit-band and source-support constraints.
    prior=boss.historical_v1(fixture,source,frozen)
    row=next(r for r in frozen['outputs'] if r['base']==10)
    from PIL import Image
    import numpy as np
    image=Image.open(source/'output/enemy-newsh4-10-8.png').copy()
    editable=boss.coverage_mask(source,'editable',10)
    support=np.asarray(logical[10].resize((192,224),Image.Resampling.NEAREST))!=0
    locked=boss.coverage_mask(source,'locked',10)
    for label,mask,channel,value,reason in [
        ('RGB-opaque',support,0,None,'RGB differs from V1'),
        ('RGB-transparent',~support,1,None,'RGB differs from V1'),
        ('alpha-source-expansion',~support,3,1,'alpha expands original support'),
        ('alpha-locked-erasure',locked,3,0,'alpha changed outside editable mask'),
        ('alpha-locked-fractional',locked,3,128,'alpha changed outside editable mask'),
    ]:
        candidate=np.array(image);y,x=np.argwhere(mask)[0]
        candidate[y,x,channel]=candidate[y,x,channel]^1 if value is None else value
        reject('semantic-'+label,lambda c=candidate:boss.validate_coverage(source,10,Image.fromarray(c),logical[10],prior[10],row),reason)
    # Per-file malformed HDR1 helper coverage: the production source validator uses
    # this exact function for all43 outputs and each of the80 selected pack files.
    per_file=[]
    for row in frozen['outputs']:
        base=row['base'];name=f'enemy-newsh4-{base}-8.hda'
        paths=[SOURCE+'/output/'+name]
        if base in boss.IDS:
            paths += [f'assets/hd/packs/{pack}/{name}' for pack in boss.DEFAULTS]
        for relative in paths:
            original=(fixture/relative).read_bytes()
            opaque=next((i for i in range(28,len(original),4) if original[i+3]==255),None)
            transparent=next((i for i in range(28,len(original),4) if original[i+3]==0),None)
            fractional=next((i for i in range(28,len(original),4) if 0<original[i+3]<255),None)
            mutations={'magic':(lambda b:b'BAD!'+b[4:],'HDR1 dimensions/anchor/key mismatch'),
                       'truncated':(lambda b:b[:-1],'HDR1 length/EOF mismatch'),
                       'trailing':(lambda b:b+b'\0','HDR1 length/EOF mismatch')}
            for field in range(6):
                mutations['header-'+str(field)]=(lambda b,i=4+4*field:b[:i]+struct.pack('<I',struct.unpack_from('<I',b,i)[0]+1)+b[i+4:],
                                                'HDR1 dimensions/anchor/key mismatch')
            for label,index,value in [
                ('opaque-RGB',opaque,None),('transparent-RGB',transparent,None),
                ('erased-alpha',None if opaque is None else opaque+3,0),
                ('partial-alpha',None if opaque is None else opaque+3,128),
                ('grown-alpha',None if transparent is None else transparent+3,255),
                ('fractional-alpha-erased',None if fractional is None else fractional+3,0),
                ('fractional-alpha-opaque',None if fractional is None else fractional+3,255),
            ]:
                if index is not None:
                    mutations[label]=(lambda b,i=index,v=value:b[:i]+bytes([b[i]^1 if v is None else v])+b[i+1:],
                                      'HDR1 frozen payload mismatch')
            for label,(mutate,reason) in mutations.items():
                reject('HDA-'+relative+'-'+label,lambda m=mutate:boss.validate_hda(m(original),base,row),reason)
            per_file.append({'path':relative,'cases':list(mutations)})
    # Full pipeline checks every canonical file and both selected-pack instances,
    # not merely a representative first member or in-memory header.
    for base in boss.IDS:
        name=f'enemy-newsh4-{base}-8.hda'
        canonical=manifest['packs'][boss.DEFAULTS[0]]['files'][name]['source_png']
        change_file('changed-canonical-'+str(base),canonical,validate,'canonical PNG mismatch',lambda b:b+b'\0')
        change_file('missing-canonical-'+str(base),canonical,validate,'regular file required')
        for pack_index,pack in enumerate(boss.DEFAULTS):
            relative=f'assets/hd/packs/{pack}/{name}'
            change_file(f'changed-pack{pack_index}-{base}',relative,validate,'HDR1 length/EOF mismatch',lambda b:b+b'\0')
            change_file(f'missing-pack{pack_index}-{base}',relative,validate,'regular file required')
    # Closed source directory, no hidden inputs or special filesystem nodes.
    for label,kind in [('source-extra-file','file'),('source-extra-directory','dir'),('source-fifo','fifo')]:
        path=source/label
        try:
            path.mkdir() if kind=='dir' else os.mkfifo(path) if kind=='fifo' else path.write_bytes(b'unknown')
            reject(label,lambda:boss.inventory(source),'source symlink or special file' if kind=='fifo' else 'source inventory differs')
        finally:
            path.rmdir() if kind=='dir' else path.unlink()
    canonical=manifest['packs'][boss.DEFAULTS[0]]['files']['enemy-newsh4-1-8.hda']['source_png']
    for label,relative in [('source-root',SOURCE),('source-file',SOURCE+'/rebuild.py'),
                           ('canonical',canonical),('canonical-parent','assets/hd/source'),
                           ('pack',f'assets/hd/packs/{boss.DEFAULTS[0]}/enemy-newsh4-1-8.hda'),
                           ('manifest','assets/hd/manifest.json')]:
        path=fixture/relative;saved=out/('saved-'+label);path.rename(saved)
        try:
            path.symlink_to(saved,target_is_directory=saved.is_dir())
            reject('symlink-'+label,validate,'source symlink' if label=='source-file' else 'symlink path forbidden')
        finally:
            path.unlink();saved.rename(path)
    for label,relative in [('canonical',canonical),('pack',f'assets/hd/packs/{boss.DEFAULTS[0]}/enemy-newsh4-1-8.hda'),
                           ('manifest','assets/hd/manifest.json')]:
        path=fixture/relative;saved=out/('fifo-saved-'+label);path.rename(saved)
        try:
            os.mkfifo(path);reject('fifo-'+label,validate,'regular file required')
        finally:
            path.unlink();saved.rename(path)
    manifest_path=fixture/'assets/hd/manifest.json';raw_manifest=manifest_path.read_bytes()
    cases=['density','bank','part','record','record-map','empty','alias','slot','id','FNV','hash','missing-entry','extra-entry',
           'bool-anchor','float-density','extra-field','missing-member','four-density','other-pack','header-alias','empty-pack',
           'pack-count','pack-anchor','pack-bool-anchor','pack-source','source-index','source-index-alias',
           'unsafe-pack','unsafe-file','unsafe-source','unsafe-index','changed-defaults','same-defaults']
    for label in cases:
        changed=json.loads(raw_manifest);family=changed[boss.FAMILY]
        pack=changed['packs'][boss.DEFAULTS[0]];entry=pack['files']['enemy-newsh4-1-8.hda']
        reason='family metadata mismatch'
        if label in ['density','bank','part','record','record-map','empty','alias','bool-anchor','float-density','extra-field']:
            key,value={'density':('density',4),'bank':('bank_role',101),'part':('runtime_components',[0]),
                'record':('source_records',list(range(1,66))),'record-map':('record_bases',{}),
                'empty':('intentional_empty_bases',[]),'alias':('equal_rgba_distinct_header_ids',[]),
                'bool-anchor':('anchor',[True,True]),'float-density':('density',8.0),'extra-field':('new_shadow',True)}[label]
            family[key]=value
        elif label in ['slot','id','FNV','hash']:
            key,value={'slot':('slot',416),'id':('id',2),'FNV':('RGBA_FNV1a64','0'*16),'hash':('HDA_sha256','0'*64)}[label]
            family['entries'][0][key]=value;reason='entry/FNV binding mismatch'
        elif label in ['missing-entry','extra-entry']:
            family['entries'].pop() if label=='missing-entry' else family['entries'].append(dict(family['entries'][0]))
            reason='exact forty entries required'
        elif label=='missing-member':
            del pack['files']['enemy-newsh4-1-8.hda'];pack['count']-=1;reason='enemy-newsh4-1-8.hda'
        elif label in ['four-density','other-pack','header-alias','empty-pack']:
            if label=='other-pack':
                pack=changed['packs'][add_nondefault_pack_fixture(changed)]
            filename={'four-density':'enemy-newsh4-1-4.hda','header-alias':'unapproved-alias.hda',
                      'empty-pack':'enemy-newsh4-238-8.hda'}.get(label,'enemy-newsh4-1-8.hda')
            pack['files'][filename]=dict(entry);pack['count']+=1;reason='widened pack'
        elif label=='pack-count':
            pack['count']+=1;reason='pack count mismatch'
        elif label in ['pack-anchor','pack-bool-anchor','pack-source']:
            if label=='pack-source':entry['source_png']='assets/hd/source/unapproved.png'
            else:entry['header_u32'][4:6]=[False,True] if label=='pack-bool-anchor' else [0,0]
            reason='packed metadata mismatch'
        elif label=='source-index':
            changed['source_pngs'][entry['sha256']]['RGBA_sha256']='0'*64;reason='source PNG index mismatch'
        elif label=='source-index-alias':
            alias=dict(changed['source_pngs'][entry['sha256']]);alias['path']='assets/hd/source/renamed-alias.png'
            changed['source_pngs']['0'*64]=alias;reason='widened source PNG index'
        elif label.startswith('unsafe-'):
            if label=='unsafe-pack':changed['packs']['../outside']={'files':{},'count':0}
            elif label=='unsafe-file':pack['files']['../outside.hda']=dict(entry);pack['count']+=1
            elif label=='unsafe-source':entry['source_png']='../outside.png'
            else:changed['source_pngs']['0'*64]={'path':'/tmp/outside.png','sha256':'0'*64,'RGBA_sha256':'0'*64}
            reason='unsafe manifest path'
        elif label=='changed-defaults':
            changed['default_debug_pack'],changed['default_preview_pack']=boss.DEFAULTS;reason='two established default packs'
        else:
            changed['default_debug_pack']=boss.DEFAULTS[0];reason='two established default packs'
        try:
            manifest_path.write_text(json.dumps(changed));reject('manifest-'+label,validate,reason)
        finally:
            manifest_path.write_bytes(raw_manifest)
    change_file('duplicate-JSON-key','assets/hd/manifest.json',validate,'duplicate JSON key',lambda b:b'{"packs":{},'+b.lstrip()[1:])
    other=NONDEFAULT_PACK
    extras=[('disk-four-density',f'assets/hd/packs/{boss.DEFAULTS[0]}/enemy-newsh4-1-4.hda',False),
            ('disk-other-pack',f'assets/hd/packs/{other}/enemy-newsh4-1-8.hda',False),
            ('disk-renamed-key-alias',f'assets/hd/packs/{boss.DEFAULTS[0]}/renamed.bin',False),
            ('disk-empty-audit',f'assets/hd/packs/{boss.DEFAULTS[0]}/enemy-newsh4-238-8.hda',False),
            ('disk-source-density','assets/hd/source/enemy-newsh4-1-4-unapproved.png',True),
            ('disk-source-renamed-pixels','assets/hd/source/unapproved-alias.png',True)]
    for label,relative,png in extras:
        path=fixture/relative;path.parent.mkdir(parents=True,exist_ok=True)
        src=fixture/(canonical if png else SOURCE+'/output/enemy-newsh4-'+('238' if label=='disk-empty-audit' else '1')+'-8.hda')
        try:
            shutil.copy2(src,path);require(not src.samefile(path),'fixture alias hardlink forbidden')
            reject(label,validate,'widened canonical PNG inventory' if png else 'widened on-disk pack inventory')
        finally:
            path.unlink()
    independent=out/'independent-rebuild';independent.mkdir()
    independent_receipt=boss.reproduce_generated_only(repo/SOURCE,independent)
    original_receipt=None
    if root:
        original_dir=out/'original-inputs';original_dir.mkdir()
        original_before={name:sha(boss.read_regular(root/name)) for name in boss.ORIGINAL_HASHES}
        for name in original_before:
            shutil.copy2(root/name,original_dir/name)
            require(not (root/name).samefile(original_dir/name),'original hardlink forbidden')
        original_receipt=boss.verify_originals(fixture,source,original_dir,logical)
        for name in original_before:
            path=original_dir/name;raw=path.read_bytes()
            try:
                path.write_bytes(raw[:-1]+bytes([raw[-1]^1]))
                reject('changed-original-'+name,lambda:boss.verify_originals(fixture,source,original_dir,logical),'original-data identity mismatch')
                path.unlink()
                reject('missing-original-'+name,lambda:boss.verify_originals(fixture,source,original_dir,logical),'original data must be regular file')
                path.symlink_to(root/name)
                reject('symlink-original-'+name,lambda:boss.verify_originals(fixture,source,original_dir,logical),'symlink path forbidden')
            finally:
                if path.is_symlink():path.unlink()
                path.write_bytes(raw)
        for name in boss.READERS:
            change_file('changed-reader-'+name,name,lambda:boss.verify_originals(fixture,source,original_dir,logical),
                        'source reader pin mismatch',lambda b:b+b'\n')
        result=cli(original_dir/'forbidden-output',original_dir)
        require(result.returncode!=0 and 'output must not overlap original data' in result.stderr and
                not (original_dir/'forbidden-output').exists(),'original/output overlap guard')
        checks.append({'case':'CLI-original-output-overlap','reason':'output must not overlap original data'})
        require(original_before=={n:sha(boss.read_regular(root/n)) for n in original_before},'real original changed')
        require(original_before=={n:sha(boss.read_regular(original_dir/n)) for n in original_before},'original fixture restoration failed')
    validate()
    require(before=={n:sha(boss.read_regular(repo/n)) for n in files},'real repository input changed')
    require(before=={n:sha(boss.read_regular(fixture/n)) for n in files},'fixture restoration failed')
    coexistence=verify_entry_coexistence(repo,out,boss)
    report={'status':'PASS','entry_boss_coexistence':coexistence,'closed_frozen_import_inventory':True,'frozen_files_changed_and_missing':boss.FROZEN_FILES,
            'canonical_files_changed_and_missing':40,'selected_pack_files_changed_and_missing':80,
            'HDA_per_file_malformed_cases':per_file,'HDA_files_exhausted':len(per_file),
            'full_pipeline_rejection_and_pure_validator_cases':checks,'rejected_count':len(checks),
            'generated_only_reproduction_without_frozen_outputs':True,'generated_only_inputs':['base-v1/'+n for n in boss.GENERATED_ONLY],
            'independent_v2_reconstruction':independent_receipt,
            'structural_proof_JSON_is_technical_input_not_original_RGB':True,'input_file_sha256':before,
            'optional_original_validation':original_receipt,'independent_copies_only':True,
            'real_inputs_unchanged':True,'original_RGB_art_inputs':False,'game_runs':0,'captures':0,'native_output':False,
            'scope':'Source validator rejection; production loader/allocation/cache behavior is a separate binding gate.'}
    (out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['HDA_per_file_malformed_cases','full_pipeline_rejection_and_pure_validator_cases','input_file_sha256']},indent=2))


if __name__=='__main__':
    try:
        main()
    except (ValueError,KeyError,TypeError,OSError,IndexError,struct.error,subprocess.SubprocessError) as exc:
        print('ERROR: '+str(exc),file=sys.stderr)
        sys.exit(1)
