"""Bounded source/consumer checks; no full repository copies or game data."""
import importlib.util
import json
from pathlib import Path
import shutil
import struct
import sys
import tempfile
import unittest
from PIL import Image
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_newshf_hd as build

class NewshfAssets(unittest.TestCase):
    def tiny(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        for relative in build.input_paths(ROOT):
            target=root/relative;target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT/relative,target)
        self.assertEqual(len(build.load(root)),9)
        return root

    def test_exact_generated_consumers(self):
        rows=build.load(ROOT)
        self.assertEqual(len(rows),9)
        self.assertEqual({r['identity'] for r in rows.values()},set(build.IDS))
        for row in rows.values():
            raw=(ROOT/row['source_path']).read_bytes()
            self.assertEqual(raw[:28],b'HDR1'+struct.pack('<6I',row['identity'],8,24,28,6,7))
            with Image.open(ROOT/row['source_png']) as image:
                self.assertEqual(raw[28:],image.tobytes())

    def test_collision_free_material_roles(self):
        old=json.loads((ROOT/'assets/hd/global-assets-v1/registry.json').read_text())
        self.assertFalse(set(build.IDS)&{r['identity'] for r in old['resources']})
        self.assertEqual(len(old['resources']),120)
        for bad in (1,125,1060125,True,2100009):
            with self.assertRaises(ValueError):build.name(bad)

    def test_missing_corrupt_and_extra_consumers(self):
        root=self.tiny();path=root/build.OUTPUT/build.name(build.IDS[0]);raw=path.read_bytes()
        path.unlink()
        with self.assertRaises(ValueError):build.load(root)
        path.write_bytes(raw[:-1]+bytes([raw[-1]^1]))
        with self.assertRaises(ValueError):build.load(root)
        path.write_bytes(raw);extra=path.with_name('unapproved.hda');extra.write_bytes(raw)
        with self.assertRaises(ValueError):build.load(root)

    def test_header_manifest_and_source_drift_rejected(self):
        root=self.tiny()
        for relative in (build.HEADER,build.MANIFEST):
            path=root/relative;raw=path.read_bytes();path.write_bytes(raw+b' ')
            with self.assertRaises(ValueError):build.load(root)
            path.write_bytes(raw)
        art=json.loads((root/build.INPUT/'manifest.json').read_text())['art'][0]
        path=root/build.INPUT/art['file'];raw=path.read_bytes();path.write_bytes(raw+b' ')
        with self.assertRaises(ValueError):build.load(root)

    def test_repin_art_changes_one_payload_not_identity(self):
        root=self.tiny();before=build.derive(root)
        manifest_path=root/build.INPUT/'manifest.json'
        selected=json.loads(manifest_path.read_bytes());art=selected['art'][0]
        path=root/art['source_png'] if 'source_png' in art else root/build.INPUT/art['file']
        with Image.open(path) as image:
            point=next((x,y) for y in range(image.height) for x in range(image.width) if image.getpixel((x,y))[3])
            r,g,b,a=image.getpixel(point);image.putpixel(point,((r+1)%256,g,b,a));image.save(path)
        with self.assertRaises(ValueError):build.derive(root)
        art['art_sha256']=build.hashlib.sha256(path.read_bytes()).hexdigest()
        manifest_path.write_bytes(build.encoded(selected))
        provenance_path=root/build.INPUT/'provenance.json';provenance=json.loads(provenance_path.read_bytes())
        provenance['groups'][0]['poses'][0]['selected_png_sha256']=art['art_sha256']
        provenance_path.write_bytes(build.encoded(provenance))
        after=build.derive(root)
        self.assertEqual({k for k in before if before[k]!=after[k]},
                         {build.HEADER,build.MANIFEST,build.OUTPUT+'/'+build.name(build.IDS[0])})
        self.assertEqual(json.loads(before[build.MANIFEST])['identity'],json.loads(after[build.MANIFEST])['identity'])
        selected['identity']['logical_bank']=11;manifest_path.write_bytes(build.encoded(selected))
        with self.assertRaises(ValueError):build.derive(root)

    def test_all_current_authoring_dependency_closures(self):
        from current_sidekick_body_compatibility import independent_input_paths
        import current_sidekick_body_compatibility as body
        import build_current_sidekick_body as body_builder
        expected=build.input_paths(ROOT)
        self.assertLessEqual(expected,independent_input_paths(ROOT))
        for module in ('build_current_front_multi','build_current_plasma_projectile','build_current_enemy_orb'):
            builder=__import__(module)
            selected=json.loads((ROOT/builder.SELECTION).read_bytes())
            self.assertLessEqual(expected,builder.dependencies(ROOT,selected))
        for method,selection in ((body_builder.charge_plan,body.CHARGE_SELECTION),(body_builder.mf_plan,body.MF_SELECTION)):
            plan=method(ROOT,{},(ROOT/selection).read_bytes())
            self.assertLessEqual(expected,set(plan['inputs_sha256']))

    def test_source_and_consumer_symlinks_rejected(self):
        root=self.tiny();path=root/build.HEADER;target=root/'pin';path.rename(target);path.symlink_to(target)
        with self.assertRaises(ValueError):build.load(root)

if __name__=='__main__':unittest.main()
