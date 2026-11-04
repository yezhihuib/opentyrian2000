"""Bounded private24 registration tests. No game, compiler or full old payload pass.
All mutations use new regular-file copies of the finite validation inputs.
The old23 fixture is reconstructed from pinned local proofs in a temporary root;
no sibling workspace, private artwork, original game data or network is needed.
"""
import contextlib
import copy
import difflib
import hashlib
import json
import os
import re
import struct
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
BASE=None  # An exact, independently copied temporary23 fixture is built below.
sys.path.insert(0,str(ROOT/'scripts'))
import current_terrain24_source_bridge as bridge
import current_terrain24_registration as terrain
import current_terrain23_source_bridge as old_bridge
from verify_current_production import source_inventory,source_manifest_digest
MANIFEST='packaging/runtime-assets-v1.json'
PROOF=terrain.authority(ROOT)
SELECTED=sorted(set(PROOF['source_sha256'])|set(PROOF['source_build_input_sha256'])|set(PROOF['historical_validation_sha256'])|{terrain.PROOF,old_bridge.terrain.PROOF,bridge.BINDING,MANIFEST}|{r['source_path'] for r in PROOF['rows']})

def read(root,name=MANIFEST):return json.loads((root/name).read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def snapshot():return {name:sha(ROOT/name) for name in SELECTED}
@contextlib.contextmanager
def fresh():
    with tempfile.TemporaryDirectory(prefix='terrain24-finite-') as tmp:
        root=Path(tmp)/'source';root.mkdir()
        for name in SELECTED:
            (root/name).parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,root/name)
            assert (root/name).stat().st_nlink==1
        yield root

def mutate(path,offset=-1):
    raw=bytearray(path.read_bytes());raw[offset]^=1;path.write_bytes(raw)


# These retained source modules are historical inputs, not reconstructed scripts.
OLD_CODE_PINS={
    'scripts/current_terrain23_source_bridge.py':'84ed9141916f705e20f402f55add5dd494de8e15edd379b71568d1577db80a3f',
    'scripts/current_terrain23_registration.py':'b92bf1d20420e8958a632c0dd32f1050dc2f42f342ed3d3b94093c36056bec16',
}
# Fixed outputs of the previously reviewed private24 generator. These literal
# identities preserve its four Python-output checks without private inputs or
# taking the expected values from the files being tested at runtime.
GENERATED_CODE_PINS={
    'scripts/current_terrain24_registration.py':'b376857ccc72431653be9d4c1a22d7a541543da05369b55aa6b711e62f09ffba',
    'scripts/current_terrain24_source_bridge.py':'22d62f7dc691f72d6c572a10dcacaa66e21bb015c0612c4681c865db6516debf',
    'scripts/package_runtime.py':'6acdc018f414e10940cb1143e38d1a77223882ec4da199002b93ec48cfb24095',
    'scripts/rebuild_recovered_runtime_manifest.py':'71767d52d724e031c62d20f1e58551c5190fc2f29c5932043cb00d00d86be8d7',
}
TERRAIN24_SCOPE_SUFFIX=(' Private terrain24 successor binds exact339 production files; prior terrain23_binding remains a historical ancestor record. '
    'All23 prior terrain bytes and contracts remain unchanged; only the independently guarded static340 slot599 lane is added. '
    'This binding is not complete package, Windows, GPU, or campaign acceptance.')

def encoded(value):return (json.dumps(value,indent=2,sort_keys=True)+'\n').encode()
def digest(raw):return hashlib.sha256(raw).hexdigest()
def pins(raw):return dict(bytes=len(raw),sha256=digest(raw),git_blob=bridge.checked.blob(raw))
def require(condition,message):
    if not condition:raise AssertionError(message)

def public_renderer():
    # The production validator authenticates every339 source file before the
    # separate exact byte transform below reconstructs the335 renderer.
    raw={name:(ROOT/name).read_bytes() for name in PROOF['source_sha256']}
    require(bridge._project_sources(PROOF,raw)==PROOF['projected_source_sha256'],'Invalid339 projection')
    lines=raw['src/render_mirror.c'].decode().splitlines(keepends=True)
    for h in reversed(PROOF['inverse']['inverse_hunks']):
        start=h['start_line_zero_based'];count=len(h['candidate'].splitlines(keepends=True))
        require(''.join(lines[start:start+count])==h['candidate'],'Changed24 inverse bytes')
        lines[start:start+count]=h['public'].splitlines(keepends=True)
    result=''.join(lines).encode()
    require(digest(result)==PROOF['inverse']['public_renderer_sha256'],'Wrong335 renderer')
    return result

def predecessor_bytes():
    """Derive old23 bytes from fixed local proofs, never from a sibling tree."""
    prior=old_bridge.terrain.authority(ROOT)
    lines=public_renderer().decode().splitlines(keepends=True)
    # Earlier forward replacements restore candidate positions for the next
    # hunk. Validate the finished candidate with the old fixed renderer hash.
    for h in prior['inverse']['inverse_hunks']:
        start=h['start_line_zero_based'];count=len(h['public'].splitlines(keepends=True))
        require(''.join(lines[start:start+count])==h['public'],'Changed23 forward bytes')
        lines[start:start+count]=h['candidate'].splitlines(keepends=True)
    renderer=''.join(lines).encode()
    require(digest(renderer)==prior['inverse']['planned_renderer_sha256'],'Wrong338 renderer')
    receipt=read(ROOT,bridge.BINDING)
    require(receipt.pop('terrain24_binding')['epoch']==terrain.MODE,'Wrong24 receipt extension')
    require(receipt['scope'].endswith(TERRAIN24_SCOPE_SUFFIX),'Changed24 scope suffix')
    receipt['scope']=receipt['scope'][:-len(TERRAIN24_SCOPE_SUFFIX)]
    receipt['source_sha256']=copy.deepcopy(prior['source_sha256'])
    receipt['production_source_manifest_sha256']=prior['source_manifest_sha256']
    receipt_raw=encoded(receipt)
    require(pins(receipt_raw)=={k:prior['current_receipt'][k] for k in ('bytes','sha256','git_blob')},'Reconstructed23 receipt differs from fixed pins')
    manifest=read(ROOT)
    fixed=sorted([r for r in manifest['files'] if r['source_path']!=bridge.BINDING and r not in PROOF['rows']],key=lambda r:r['destination'])
    require(len(fixed)==1138 and source_manifest_digest(fixed)==prior['base_nonbinding_rows_sha256'],'Wrong1138 base rows')
    binding=dict(source_path=bridge.BINDING,destination=bridge.BINDING_DESTINATION,group='current-production-validation',revision='reconstructed-local-unpublished',**pins(receipt_raw))
    old_manifest=copy.deepcopy(prior['candidate_metadata'])
    old_manifest['files']=sorted(fixed+copy.deepcopy(prior['rows'])+[binding],key=lambda r:r['destination'])
    require(digest(encoded(old_manifest))==PROOF['predecessor23']['runtime_manifest_sha256'],'Reconstructed23 manifest differs from fixed hash')
    output={}
    for name,expected in prior['source_sha256'].items():
        raw=renderer if name=='src/render_mirror.c' else (ROOT/name).read_bytes()
        require(digest(raw)==expected,'Wrong predecessor source: '+name);output[name]=raw
    for name,expected in {**prior['source_build_input_sha256'],**prior['historical_validation_sha256'],**OLD_CODE_PINS}.items():
        raw=(ROOT/name).read_bytes();require(digest(raw)==expected,'Wrong predecessor input: '+name);output[name]=raw
    for row in prior['rows']:
        raw=(ROOT/row['source_path']).read_bytes()
        require(pins(raw)=={k:row[k] for k in ('bytes','sha256','git_blob')},'Wrong retained23 HDA')
        output[row['source_path']]=raw
    output[old_bridge.terrain.PROOF]=(ROOT/old_bridge.terrain.PROOF).read_bytes()
    output[bridge.BINDING]=receipt_raw;output[MANIFEST]=encoded(old_manifest)
    return output

def make_predecessor(root):
    for name,raw in predecessor_bytes().items():
        path=root/name;path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('xb') as stream:stream.write(raw)
        require(path.stat().st_nlink==1,'Fixture must not share hardlinks')
    old_bridge.verify_source_epoch(root)
    old_bridge.validate_runtime_rows(root,read(root),required=True)

def reproduce_registration_inputs():
    """Recompute the original339/24 registration parameters without private art.

    The pinned24 proof supplies only the frozen authoring evidence, which is
    already an input to registration. Source inventories, inverse hunks, headers,
    payload pins, receipt, manifest, and the remaining proof fields are rebuilt
    independently from the local339 source and exact reconstructed23 predecessor.
    No authoring or runtime acceptance is inferred from this reconstruction.
    """
    prior=old_bridge.terrain.authority(BASE)
    actual=source_inventory(ROOT);current=source_manifest_digest(actual)
    include_sha=dict(prior['include_sha256'])
    include_sha['src/private_static340.inc']=actual['src/private_static340.inc']
    new_lines=(ROOT/'src/render_mirror.c').read_text().splitlines(keepends=True)
    public_lines=public_renderer().decode().splitlines(keepends=True)
    hunks=[]
    for tag,i,j,x,y in difflib.SequenceMatcher(None,new_lines,public_lines,autojunk=False).get_opcodes():
        if tag=='equal':continue
        if i==j:
            require(i>0 and x>0,'Unbounded inverse insertion');i-=1;x-=1
        hunks.append(dict(start_line_zero_based=i,candidate=''.join(new_lines[i:j]),public=''.join(public_lines[x:y]),context_before=''.join(new_lines[max(0,i-3):i]),context_after=''.join(new_lines[j:j+3])))
    name='assets/hd/current-terrain24/terrain-shapesz-340-8.hda'
    raw=(ROOT/name).read_bytes();payload=raw[28:]
    require(len(raw)==172060 and struct.unpack('<4s4I2i',raw[:28])==(b'HDR1',2010340,8,24,28,0,0),'Wrong340 bytes/header')
    require(set(payload[3::4])=={255},'Wrong340 opaque coverage')
    source_pin=re.findall(r'return h==UINT64_C\(0x([0-9a-f]{16})\);',(ROOT/'src/private_static340.inc').read_text())
    require(len(source_pin)==1,'Missing exact static340 source pin')
    authoring=copy.deepcopy(PROOF['static340_authoring'])
    require(authoring['hda']['sha256']==digest(raw) and authoring['hda']['rgba_payload_sha256']==digest(payload),'Authoring pins do not match actual340')
    row=dict(source_path=name,destination='assets/gameplay/terrain-shapesz-340-8.hda',group='gameplay',revision='current-shapesz-terrain24-v1',**pins(raw))
    receipt=read(BASE,bridge.BINDING)
    receipt['source_sha256']=actual;receipt['production_source_manifest_sha256']=current
    receipt['scope']+=TERRAIN24_SCOPE_SUFFIX
    receipt['terrain24_binding']=dict(epoch='current-shapesz-terrain24-v1',proof_path='packaging/terrain24-authoring-epoch-v1.json',source_files=339,source_binding_only=True,full_package_acceptance=False,predecessor_source_manifest_sha256=old_bridge.CURRENT_DIGEST,predecessor_binding_sha256=sha(BASE/bridge.BINDING),static340_slot=599,original23_unchanged=True,capture_helper_present=False)
    receipt_raw=encoded(receipt)
    manifest=read(BASE);binding=[r for r in manifest['files'] if r['source_path']==bridge.BINDING]
    require(len(binding)==1,'Missing exact prior binding');binding[0].update(pins(receipt_raw))
    manifest['files'].append(row);manifest['files'].sort(key=lambda r:r['destination'])
    manifest['source_revision']['current_production_source_manifest_sha256']=current
    manifest['source_revision']['terrain24_epoch']='current-shapesz-terrain24-v1'
    manifest['closure'].update(gameplay_files=729,terrain24_files=24,terrain24_atomic_groups={'ground10':10,'cliff12':12,'corner366':1,'static340':1})
    proof=copy.deepcopy(prior)
    proof.update(schema='opentyrian-terrain24-epoch-v1',epoch='current-shapesz-terrain24-v1',source_count=339,source_manifest_sha256=current,source_sha256=actual,include_sha256=include_sha,current_receipt=dict(path=bridge.BINDING,**pins(receipt_raw)),candidate_metadata={k:v for k,v in manifest.items() if k!='files'})
    old_manifest=read(BASE)
    proof['predecessor23']=dict(proof_path=old_bridge.terrain.PROOF,proof_sha256=old_bridge.terrain.PROOF_SHA256,source_manifest_sha256=old_bridge.CURRENT_DIGEST,runtime_manifest_sha256=sha(BASE/MANIFEST),nonbinding_rows=1161,nonbinding_rows_sha256=source_manifest_digest([r for r in old_manifest['files'] if r['source_path']!=bridge.BINDING]))
    proof['rows']=sorted(copy.deepcopy(prior['rows'])+[row],key=lambda r:r['destination'])
    proof['runtime_groups']['static340']=[340]
    proof['resources'].append(dict(id=340,group='static340',slot=599,header=[2010340,8,24,28,0,0],native_nonzero_cells=672,source_fnv64=source_pin[0],source_native_sha256=authoring['source_sha256']['native_indices'],payload_fnv64=bridge.checked.fnv(payload),payload_sha256=digest(payload),row=row))
    proof['resources'].sort(key=lambda r:r['id'])
    proof['inverse'].update(candidate_source_count=339,planned_renderer_sha256=actual['src/render_mirror.c'],inverse_hunks=hunks,new_source_files_remove_after_exact_hash_check=include_sha,claim='Exact339 authenticated files projected in memory by fixed renderer inverse and four exact include removals to unchanged335 TOPCLIP authority. No old receipt is fabricated; no source or package validator is skipped.',status='EXACT_IN_MEMORY_PROJECTION',public_renderer_source='Existing terrain23 proof exact inverse; no download')
    proof['scope'].update(retained_source_color_lock_pixels=36781+9588,runtime_behavior_change_from_stable23='Only independently guarded static340 slot599 lane; original23 resources/includes unchanged.',source_binding_only=True,full_package_acceptance=False,static340_original_rgb_lock_hd_pixels=9588)
    proof['static340_authoring']=authoring
    return {bridge.BINDING:receipt_raw,MANIFEST:encoded(manifest),terrain.PROOF:encoded(proof)}

class Terrain24Registration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        global BASE
        cls.before=snapshot()
        cls._predecessor_dir=tempfile.TemporaryDirectory(prefix='terrain24-predecessor23-')
        cls.addClassCleanup(cls._predecessor_dir.cleanup)
        BASE=Path(cls._predecessor_dir.name)/'source'
        make_predecessor(BASE)
    @classmethod
    def tearDownClass(cls):
        if snapshot()!=cls.before:raise AssertionError('Frozen source/proof/receipt/payload input changed')
    def reject_source(self,root):
        with self.assertRaises((ValueError,OSError)):bridge.verify_source_epoch(root)
    def reject_rows(self,root,manifest):
        with self.assertRaises((ValueError,OSError)):bridge.validate_runtime_rows(root,manifest,required=True)
    def test_positive339_projection1163_and24_payloads(self):
        result=bridge.validate_runtime_rows(ROOT,read(ROOT),required=True)
        self.assertEqual((result['source_files'],result['runtime_rows'],result['terrain_payloads']),(339,1163,24))
        self.assertEqual(result['projected_body_policy_epoch'],old_bridge.TOPCLIP_DIGEST)
        self.assertFalse(result['old_payloads_revalidated']);self.assertFalse(result['full_package_acceptance'])
        raw={n:(ROOT/n).read_bytes() for n in PROOF['source_sha256']}
        self.assertEqual(bridge._project_sources(PROOF,raw),PROOF['projected_source_sha256'])
        self.assertEqual(len(terrain.load(ROOT)),24)
    def test_original23_bytes_rows_and_code_preserved(self):
        for name in ('scripts/current_terrain23_source_bridge.py','scripts/current_terrain23_registration.py',old_bridge.terrain.PROOF,*old_bridge.terrain.INCLUDES):
            self.assertEqual((ROOT/name).read_bytes(),(BASE/name).read_bytes(),name)
        before=read(BASE);after=read(ROOT)
        old=[r for r in before['files'] if r['source_path']!=bridge.BINDING]
        new=[r for r in after['files'] if r['source_path']!=bridge.BINDING and r['destination']!='assets/gameplay/terrain-shapesz-340-8.hda']
        self.assertEqual(old,new)
        for row in old_bridge.terrain.rows_for(BASE):self.assertEqual((ROOT/row['source_path']).read_bytes(),(BASE/row['source_path']).read_bytes())
        self.assertFalse(bridge.requires_terrain(BASE,before,read(BASE,bridge.BINDING)))
        self.assertEqual(old_bridge.validate_runtime_rows(BASE,before,True)['terrain_payloads'],23)
        with self.assertRaises(ValueError):old_bridge.verify_source_epoch(ROOT)
    def test_every_include_and_unrelated_source_tamper(self):
        for name in (*terrain.INCLUDES,'src/render_mirror.c','src/animlib.c'):
            with self.subTest(name=name),fresh() as root:mutate(root/name);self.reject_source(root)
    def test_hidden_extra_removed_and_renamed_source(self):
        for kind in ('extra','hidden','remove','rename'):
            with self.subTest(kind=kind),fresh() as root:
                p=root/'src/private_static340.inc'
                if kind=='remove':p.unlink()
                elif kind=='rename':p.rename(root/'src/renamed340.inc')
                else:(root/'src'/('.hidden' if kind=='hidden' else 'unexpected.txt')).write_text('unauthorized')
                self.reject_source(root)
    def test_source_symlink_fifo_directory_rejected(self):
        for kind in ('symlink','broken','fifo','directory'):
            with self.subTest(kind=kind),fresh() as root:
                p=root/'src/private_static340.inc';raw=p.read_bytes();p.unlink()
                if kind=='symlink':q=root/'same-bytes';q.write_bytes(raw);p.symlink_to(q)
                elif kind=='broken':p.symlink_to(root/'missing')
                elif kind=='fifo':os.mkfifo(p)
                else:p.mkdir()
                self.reject_source(root)
    def test_proof_binding_build_and_history_mutation(self):
        for name in (terrain.PROOF,old_bridge.terrain.PROOF,bridge.BINDING,*PROOF['source_build_input_sha256'],*PROOF['historical_validation_sha256']):
            with self.subTest(name=name),fresh() as root:mutate(root/name);self.reject_source(root)
    def test_missing_proof_and_forged_json_rejected(self):
        for kind in ('missing','duplicate'):
            with self.subTest(kind=kind),fresh() as root:
                p=root/terrain.PROOF
                if kind=='missing':p.unlink()
                else:p.write_bytes(b'{"schema":"forged",'+p.read_bytes()[1:])
                self.reject_source(root)
    def test_stripped_metadata_old23_receipt_cannot_downgrade339(self):
        for remove_proof in (False,True):
            with self.subTest(remove_proof=remove_proof),fresh() as root:
                (root/bridge.BINDING).write_bytes((BASE/bridge.BINDING).read_bytes())
                (root/MANIFEST).write_bytes((BASE/MANIFEST).read_bytes())
                if remove_proof:(root/terrain.PROOF).unlink()
                self.assertFalse(terrain.epoch_marked_rows(read(root)))
                self.assertTrue(bridge.requires_terrain(root,read(root),read(root,bridge.BINDING)))
                self.reject_rows(root,read(root))
    def test_unique24_broken_root_markers_force_validation(self):
        for name in bridge.ROOT_MARKERS:
            with self.subTest(name=name),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);(root/name).parent.mkdir(parents=True,exist_ok=True);(root/name).symlink_to(root/'absent')
                self.assertTrue(bridge.requires_terrain(root,{}));self.reject_rows(root,{})
    def test_unique24_marker_forms_and_no23_false_promotion(self):
        for row in ({'revision':terrain.MODE},{'identity':2010340},{'source_path':'assets/hd/current-terrain24/x.hda'},{'destination':'assets/gameplay/TERRAIN-SHAPESZ-340-8.HDA'}):
            self.assertTrue(terrain.epoch_marked_rows({'files':[row]}))
        self.assertTrue(terrain.epoch_marked_rows({'closure':{'terrain24_files':0}}))
        self.assertTrue(terrain.epoch_marked_rows({'source_revision':{'terrain24_epoch':None}}))
        self.assertFalse(terrain.epoch_marked_rows(read(BASE)))
    def test_row_mutations_omission_duplicate_extra_and_unsafe(self):
        manifest=read(ROOT)
        for kind in ('remove','duplicate','extra','path','destination','revision','sha256','bytes','oldrow','binding'):
            with self.subTest(kind=kind):
                changed=copy.deepcopy(manifest);row=next(r for r in changed['files'] if r['destination'].endswith('terrain-shapesz-340-8.hda'))
                if kind=='remove':changed['files'].remove(row)
                elif kind=='duplicate':changed['files'].append(copy.deepcopy(row))
                elif kind=='extra':changed['files'].append(dict(row,destination='assets/gameplay/extra.hda'))
                elif kind=='path':row['source_path']='../escape.hda'
                elif kind=='destination':row['destination']='Assets/GamePlay/terrain-shapesz-340-8.hda'
                elif kind=='revision':row['revision']='current-shapesz-terrain23-v1'
                elif kind=='sha256':row['sha256']='0'*64
                elif kind=='bytes':row['bytes']=172060.0
                elif kind=='oldrow':next(r for r in changed['files'] if r['destination'].endswith('terrain-shapesz-361-8.hda'))['revision']='forged'
                else:next(r for r in changed['files'] if r['source_path']==bridge.BINDING)['sha256']='0'*64
                self.reject_rows(ROOT,changed)
    def test_metadata_and_integer_type_changes(self):
        for kind in ('source','groups','24','23','aliases','float'):
            changed=copy.deepcopy(read(ROOT))
            if kind=='source':changed['source_revision']['current_production_source_manifest_sha256']=old_bridge.CURRENT_DIGEST
            elif kind=='groups':changed['closure']['terrain24_atomic_groups']['static340']=2
            else:changed['closure'][{'24':'terrain24_files','23':'terrain23_files','aliases':'global_tank194_body_alias_files','float':'terrain24_files'}[kind]]=24.0 if kind=='float' else 0
            self.reject_rows(ROOT,changed)
    def test_each24_payload_tamper(self):
        for row in PROOF['rows']:
            with self.subTest(path=row['source_path']),fresh() as root:
                mutate(root/row['source_path'])
                with self.assertRaises(ValueError):terrain.load(root)
    def test_static340_header_alpha_missing_truncated_symlink(self):
        name='assets/hd/current-terrain24/terrain-shapesz-340-8.hda'
        for kind in ('header','alpha','missing','truncated','symlink'):
            with self.subTest(kind=kind),fresh() as root:
                p=root/name
                if kind=='header':mutate(p,4)
                elif kind=='alpha':mutate(p,31)
                elif kind=='missing':p.unlink()
                elif kind=='truncated':p.write_bytes(p.read_bytes()[:-1])
                else:raw=p.read_bytes();p.unlink();q=root/'same-hda';q.write_bytes(raw);p.symlink_to(q)
                with self.assertRaises((ValueError,OSError)):terrain.load(root)
    def test_inverse_missing_duplicate_position_context_and_unrelated(self):
        raw={n:(ROOT/n).read_bytes() for n in PROOF['source_sha256']}
        for kind in ('missing','duplicate','position','context','unrelated'):
            with self.subTest(kind=kind):
                p=copy.deepcopy(PROOF);r=dict(raw)
                if kind=='missing':p['inverse']['inverse_hunks'].pop()
                elif kind=='duplicate':p['inverse']['inverse_hunks'][1]=p['inverse']['inverse_hunks'][0]
                elif kind=='position':p['inverse']['inverse_hunks'][0]['start_line_zero_based']+=1
                elif kind=='context':p['inverse']['inverse_hunks'][0]['context_before']='changed'
                else:r['src/animlib.c']+=b'changed'
                with self.assertRaises(ValueError):bridge._project_sources(p,r)
    def test_default_entries_reject_downgrade_before_old_art_loading(self):
        for script in ('package_runtime.py','rebuild_recovered_runtime_manifest.py'):
            with self.subTest(script=script),fresh() as root:
                (root/bridge.BINDING).write_bytes((BASE/bridge.BINDING).read_bytes())
                (root/MANIFEST).write_bytes((BASE/MANIFEST).read_bytes())
                (root/terrain.PROOF).unlink()
                output=root.parent/'must-not-exist.json'
                cmd=[sys.executable,'-B',str(ROOT/'scripts'/script)]
                cmd+=['--source-root',str(root)] if script=='package_runtime.py' else ['--root',str(root),'--output',str(output)]
                proc=subprocess.run(cmd,text=True,capture_output=True,timeout=20)
                self.assertNotEqual(proc.returncode,0);self.assertFalse(output.exists())
                self.assertNotIn('Missing current',proc.stderr)
                self.assertTrue('terrain24-authoring-epoch' in proc.stderr or 'Production source mismatch' in proc.stderr,proc.stderr[-1200:])
    def test_producer_reproducibility_check(self):
        # This independently reconstructs the source339/static340 registration,
        # rather than launching the private artwork workspace generator.
        first=reproduce_registration_inputs();second=reproduce_registration_inputs()
        self.assertEqual(first,second)
        self.assertEqual(set(first),{bridge.BINDING,MANIFEST,terrain.PROOF})
        for name,raw in first.items():self.assertEqual(raw,(ROOT/name).read_bytes(),name)
        self.assertEqual(digest(first[terrain.PROOF]),terrain.PROOF_SHA256)
        rebuilt=json.loads(first[terrain.PROOF])
        self.assertEqual((rebuilt['source_count'],len(rebuilt['rows']),len(rebuilt['inverse']['inverse_hunks'])),(339,24,8))
        self.assertEqual(rebuilt['runtime_groups']['static340'],[340])
        self.assertEqual(len(GENERATED_CODE_PINS),4)
        for name,expected in GENERATED_CODE_PINS.items():self.assertEqual(sha(ROOT/name),expected,name)

if __name__=='__main__':unittest.main(verbosity=2)
