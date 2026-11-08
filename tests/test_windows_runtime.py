"""Synthetic PE/receipts and mocked child process only. Never runs a game."""
import argparse,hashlib,importlib.util,json,os,struct,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('classic_runtime',ROOT/'scripts/windows_classic_runtime.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
def h(b):return hashlib.sha256(b).hexdigest()
def pe(dll=False,machine=0x8664):
 b=bytearray(256);b[:2]=b'MZ';struct.pack_into('<I',b,60,128);b[128:132]=b'PE\0\0';struct.pack_into('<H',b,132,machine);struct.pack_into('<H',b,150,0x2000 if dll else 0);return bytes(b)
class WindowsRuntimeTests(unittest.TestCase):
    def inputs(self,base):
        source=base/'source';source.mkdir();data=base/'original';data.mkdir()
        for name in module.DATA_FILES:(data/name).write_bytes(b'original test input '+name.encode())
        files={}
        for key,dll in (('exe',False),('sdl2',True),('sdl_net',True)):
            f=source/key;raw=pe(dll);f.write_bytes(raw);files[key]=f
        stage={'schema':1,'status':'STAGED_NOT_BUILT','translation_units':112,'source_digest':'a'*64}
        raw=json.dumps(stage).encode();(source/'STAGE.json').write_bytes(raw)
        build={'schema':1,'status':'BUILT_NOT_RUN','exit_code':0,'pe_machine':'AMD64','inputs_unchanged_after_build':True,'stage_sha256':h(raw),'source_digest':'a'*64,'binary':{'sha256':h(files['exe'].read_bytes())}}
        (source/'BUILD.json').write_text(json.dumps(build))
        return argparse.Namespace(output=str(base/'run'),data=str(data),exe=str(files['exe']),exe_sha256=h(files['exe'].read_bytes()),sdl2=str(files['sdl2']),sdl2_sha256=h(files['sdl2'].read_bytes()),sdl_net=str(files['sdl_net']),sdl_net_sha256=h(files['sdl_net'].read_bytes()),build_receipt=str(source/'BUILD.json'),build_sha256=h((source/'BUILD.json').read_bytes()),stage_receipt=str(source/'STAGE.json'),stage_sha256=h(raw),prepare=False,hd=False,public_candidates=False)
    def test_classic_check_only_and_new_preparation(self):
        with tempfile.TemporaryDirectory() as temp:
            a=self.inputs(Path(temp));cwd=os.getcwd();env=dict(os.environ)
            result=module.prepare(a);self.assertEqual(result['status'],'CHECK_ONLY');self.assertFalse(Path(a.output).exists())
            a.prepare=True;result=module.prepare(a);root=Path(a.output)
            self.assertEqual(result['immutable_files'],6);self.assertFalse((root/'assets').exists())
            _,receipt,_=module.verify_run(root,result['runtime_receipt_sha256']);self.assertEqual(receipt['mode'],'classic')
            self.assertEqual(os.getcwd(),cwd);self.assertEqual(dict(os.environ),env)
            self.assertFalse((root/'tyrian1.lvl').exists());self.assertFalse((root/'tyrian.sav').exists())
            with self.assertRaises(ValueError):module.prepare(a)
    def test_changed_binary_missing_data_and_hd_fail_before_write(self):
        with tempfile.TemporaryDirectory() as temp:
            a=self.inputs(Path(temp));a.prepare=True;a.hd=True
            with self.assertRaisesRegex(ValueError,'classic-only'):module.prepare(a)
            a.hd=False;Path(a.exe).write_bytes(b'corrupt')
            with self.assertRaisesRegex(ValueError,'SHA256'):module.prepare(a)
            Path(a.exe).write_bytes(pe(False));(Path(a.data)/'tyrian1.lvl').unlink()
            with self.assertRaises(ValueError):module.prepare(a)
            self.assertFalse(Path(a.output).exists())
    def test_machine_and_role_checks(self):
        with self.assertRaises(ValueError):module.pe_amd64(pe(False,0x14c))
        with self.assertRaises(ValueError):module.pe_amd64(pe(True),False)
        with self.assertRaises(ValueError):module.pe_amd64(b'MZ')
    def test_receipt_or_copied_script_tampering_and_extra_files(self):
        with tempfile.TemporaryDirectory() as temp:
            a=self.inputs(Path(temp));a.prepare=True;r=module.prepare(a);root=Path(a.output);digest=r['runtime_receipt_sha256']
            with self.assertRaises(ValueError):module.verify_run(root,'0'*64)
            script=root/module.SCRIPT;original=script.read_bytes();script.write_bytes(b'# foreign launcher')
            with self.assertRaises(ValueError):module.verify_run(root,digest)
            script.write_bytes(original);(root/'unexpected.dll').write_bytes(pe(True))
            with self.assertRaisesRegex(ValueError,'Unexpected'):module.verify_run(root,digest)
    @unittest.skipUnless(hasattr(os,'symlink'),'No symlink support')
    def test_symlink_rejection(self):
        with tempfile.TemporaryDirectory() as temp:
            a=self.inputs(Path(temp));target=Path(temp)/'alias'
            try:target.symlink_to(Path(a.data),target_is_directory=True)
            except OSError:self.skipTest('Symlinks unavailable without permissions')
            a.data=str(target)
            with self.assertRaisesRegex(ValueError,'Symlink/reparse'):module.prepare(a)
    def test_allowlist_environment_and_mocked_launch(self):
        with tempfile.TemporaryDirectory() as temp:
            a=self.inputs(Path(temp));a.prepare=True;r=module.prepare(a);root=Path(a.output)
            system=Path(temp)/'Windows';system.mkdir();(system/'System32').mkdir()
            inherited={'SystemRoot':str(system),'sDl_VideoDriver':'dummy','SDL_AUDIODRIVER':'dummy','normal270_enable':'1','BUILDING313_FAMILY_CANVAS_ENABLE':'1','PATH':'untrusted','UNRELATED':'ignored'}
            env=module.child_environment(root,inherited)
            self.assertEqual(set(env),{'SYSTEMROOT','PATH'});self.assertNotIn('untrusted',env['PATH']);self.assertEqual(inherited['sDl_VideoDriver'],'dummy')
            calls=[]
            class Child:
                pid=123
                def wait(self):return 0
            def popen(argv,**kw):calls.append((argv,kw));return Child()
            args=argparse.Namespace(root=str(root),trust_sha256=r['runtime_receipt_sha256'],launch=False)
            with patch.object(module.subprocess,'Popen',side_effect=popen):
                self.assertFalse(module.run(args)['game_started']);self.assertEqual(calls,[])
            args.launch=True;cwd=os.getcwd()
            with patch.object(module,'WINDOWS',True),patch.dict(os.environ,{'SYSTEMROOT':str(system),'sDl_VideoDriver':'dummy'}),patch.object(module.subprocess,'Popen',side_effect=popen):
                result=module.run(args)
            self.assertEqual(result['exit_code'],0);self.assertFalse(result['runtime_acceptance']);self.assertEqual(calls[0][1]['cwd'],root)
            self.assertFalse(any(k.upper().startswith('SDL_') for k in calls[0][1]['env']));self.assertEqual(os.getcwd(),cwd)
            self.assertTrue((root/'launch-start.json').exists());self.assertTrue((root/'launch-end.json').exists())
            with self.assertRaises(ValueError):module.verify_run(root,r['runtime_receipt_sha256'])
if __name__=='__main__':unittest.main()
