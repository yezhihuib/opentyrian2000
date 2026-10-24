#!/usr/bin/env python3
"""Default-off and mirror-disabled identity APIs remain conservative standalone stubs."""
import os, subprocess, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=r'''
#include "enemy_reuse_identity.h"
#include <assert.h>
int main(void) {
 for(unsigned i=0;i<62;i++) {
  assert(!enemy_reuse_identity_generation(i));
  assert(!enemy_reuse_identity_live(i,227,10,20));
  assert(!enemy_reuse_identity_live_generation(i,227,10,20,0));
  assert(!enemy_reuse_identity_live_generation(i,227,10,20,1));
 }
 return 0;
}
'''
class DisabledIdentity(unittest.TestCase):
 def check_mode(self,flags):
  with tempfile.TemporaryDirectory() as temp:
   source=Path(temp)/'test.c';binary=Path(temp)/'test';source.write_text(SOURCE)
   subprocess.run([os.environ.get('CC','cc'),'-std=c99','-Wall','-Wextra','-Werror',*flags,'-I'+str(ROOT/'src'),str(source),'-o',str(binary)],check=True,capture_output=True,text=True)
   subprocess.run([str(binary)],check=True,capture_output=True,text=True)
 def test_default_off(self):self.check_mode([])
 def test_mirror_disabled(self):self.check_mode(['-DENEMY_REUSE_HD_PROTOTYPE=1','-DRENDER_MIRROR_DISABLED'])
if __name__=='__main__':unittest.main()
