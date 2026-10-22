"""Explicit counted subprocess execution for historical top-level oracles."""
from pathlib import Path
import subprocess
import sys
import unittest
class HistoricalOracle(unittest.TestCase):
    def __init__(self,script):
        super().__init__('runTest'); self.script=Path(script).resolve()
    def id(self):return self.script.stem+'.HistoricalOracle.test_original_oracle'
    def __str__(self):return self.id()
    def runTest(self):
        result=subprocess.run([sys.executable,str(self.script)],text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stdout+'\n'+result.stderr)
        self.assertTrue(result.stdout.strip(),'Historical oracle produced no evidence')
def suite(script):return unittest.TestSuite([HistoricalOracle(script)])
