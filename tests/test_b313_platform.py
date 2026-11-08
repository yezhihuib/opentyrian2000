"""Compile and run platform primitives only in a disposable directory, never a game."""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
class PlatformPrimitiveTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('cl' if os.name=='nt' else 'cc'),'Native compiler not available in this shell')
    def test_known_vectors_no_replace_and_file_lifecycle(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp);source=ROOT/'tests/test_b313_platform.c';include=ROOT/'experimental/level2-family/src'
            if os.name=='nt':
                exe=p/'primitive-test.exe'
                command=['cl','/nologo','/std:c17','/W4','/I'+str(include),str(source),'/Fe:'+str(exe),'/link','bcrypt.lib']
            else:
                exe=p/'primitive-test'
                command=['cc','-std=c99','-Wall','-Wextra','-I',str(include),str(source),'-lcrypto','-o',str(exe)]
            result=subprocess.run(command,cwd=p,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            result=subprocess.run([str(exe)],cwd=p,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
    def test_no_bypass_of_integrity_or_publish(self):
        header=(ROOT/'experimental/level2-family/src/b313_platform.h').read_text()
        self.assertIn('BCryptFinishHash',header);self.assertIn('CreateHardLinkA(final,temporary,NULL)',header)
        self.assertNotIn('MOVEFILE_REPLACE_EXISTING',header)
        for name in ('b313_family_cache.c','b313_v6_prefix_preparation.c','b313_family_observer.c'):
            text=(ROOT/'experimental/level2-family/src'/name).read_text()
            self.assertIn('b313_sha256(',text);self.assertNotIn('#include <openssl/sha.h>',text)
if __name__=='__main__':unittest.main()
