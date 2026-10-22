"""Count and failure isolation of the eight historical CLI adapters."""
import importlib
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch
import historical_oracle_support as support

NAMES=['test_rear_multi_p1_source_inverse','test_storm_source_inverse']+[
    'test_rear_multi_'+tag+'_assets' for tag in ('p4_mode2','p5_mode1','p5_mode2','p7_mode1','p7_mode2','p9_mode2')]
class AdapterTests(unittest.TestCase):
    def test_all_eight_register_exactly_one_real_case(self):
        for name in NAMES:
            module=importlib.import_module(name)
            suite=unittest.defaultTestLoader.loadTestsFromModule(module)
            self.assertEqual(suite.countTestCases(),1,name)
            case=list(suite)[0]
            self.assertIsInstance(case,support.HistoricalOracle)
            self.assertEqual(case.id(),name+'.HistoricalOracle.test_original_oracle')
            self.assertEqual(case.script,Path(module.__file__).resolve())
    def test_script_failure_cannot_disappear_or_succeed(self):
        module=importlib.import_module(NAMES[0]);case=support.HistoricalOracle(module.__file__)
        with patch('historical_oracle_support.subprocess.run',return_value=subprocess.CompletedProcess([],3,'','intentional oracle failure')) as run:
            result=unittest.TestResult();case.run(result)
        self.assertEqual(result.testsRun,1)
        self.assertEqual(len(result.failures),1)
        self.assertEqual(result.skipped,[])
        self.assertEqual(run.call_args.args[0][1],str(case.script))
        self.assertIn('intentional oracle failure',result.failures[0][1])
if __name__=='__main__':unittest.main()
