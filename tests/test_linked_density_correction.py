import csv
import hashlib
import shutil
from PIL import Image
import importlib.util
from pathlib import Path
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('density_correction',ROOT/'prototype/verify-linked-newshf-density.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class DensityCorrection(unittest.TestCase):
    def test_explicit_density_follows_global_assets(self):
        for density in (4,8):
            cmd=m.command('/exe','/data','/assets with spaces',density)
            self.assertGreater(cmd.index('--render-test='+str(density)),cmd.index('--global-assets=/assets with spaces'))
            self.assertNotIn('--render-original-reference',cmd)
            self.assertEqual(cmd[-1],'--render-test='+str(density))
    def audit(self,density=4,ticks=range(106,181)):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        p=Path(temp.name)/'rgb-audit.tsv'
        with p.open('w') as f:
            writer=csv.writer(f,delimiter='\t');writer.writerow(['tick','density','rgb_hash','classic_mismatches'])
            writer.writerows((t,density,'0','0') for t in ticks)
        return p
    def test_actual_four_passes(self):
        self.assertEqual(m.actual_density(self.audit(),4),4)
    def test_nominal_four_actual_eight_rejected(self):
        with self.assertRaisesRegex(ValueError,'Actual renderer density'):
            m.actual_density(self.audit(8),4)
    def test_mixed_density_rejected(self):
        p=self.audit();s=p.read_text().replace('107\t4\t','107\t8\t');p.write_text(s)
        with self.assertRaisesRegex(ValueError,'Actual renderer density'):m.actual_density(p,4)
    def test_empty_and_wrong_tick_ranges_rejected(self):
        for ticks in ([],range(105,180),range(106,180)):
            with self.subTest(ticks=ticks),self.assertRaises(ValueError):m.actual_density(self.audit(ticks=ticks),4)
    def test_missing_and_mutated_pinned_data_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);p=root/'known.dat';pins={'known.dat':hashlib.sha256(b'qualified').hexdigest()}
            with self.assertRaisesRegex(ValueError,'Missing pinned input'):m.pinned_inputs(root,pins)
            p.write_bytes(b'qualified');self.assertEqual(m.pinned_inputs(root,pins),{str(p):pins['known.dat']})
            p.write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'Changed pinned input'):m.pinned_inputs(root,pins)
    def test_published_masks_reject_widened_or_missing_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for name in m.MASK_SHA256:shutil.copyfile(ROOT/'authoring-inputs/newshf-linked'/name,root/name)
            self.assertEqual(len(m.pinned_inputs(root,m.MASK_SHA256)),4)
            p=root/'mask-121.png';Image.new('L',(24,28),255).save(p)
            with self.assertRaisesRegex(ValueError,'Changed pinned input'):m.pinned_inputs(root,m.MASK_SHA256)
            p.unlink()
            with self.assertRaisesRegex(ValueError,'Missing pinned input'):m.pinned_inputs(root,m.MASK_SHA256)
    def test_post_run_input_mutation_and_deletion_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'driver.py';p.write_bytes(b'original');snap={str(p):m.sha(p)};m.unchanged(snap)
            p.write_bytes(b'mutated')
            with self.assertRaisesRegex(ValueError,'Input bytes changed'):m.unchanged(snap)
            p.unlink()
            with self.assertRaisesRegex(ValueError,'Input bytes changed'):m.unchanged(snap)
    def test_public_parser_semantics_unchanged(self):
        source=(ROOT/'src/game_probe.c').read_text()
        global_branch=source.split('} else if(strncmp(argv[i],"--global-assets=",16)==0) {',1)[1].split('} else if',1)[0]
        self.assertIn('game_probe_density=8;',global_branch)
        self.assertIn('else if(strcmp(argv[i],"--render-original-reference")==0) game_probe_original_reference=true;',source)
    def test_canonical_wrappers_do_not_emit_global_assets(self):
        for n in ['run-controlled.py','start-asset-debug.py','asset-index.py']:
            self.assertNotIn('--global-assets',(ROOT/'prototype'/n).read_text())
if __name__=='__main__':unittest.main()
