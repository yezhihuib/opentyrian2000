#!/usr/bin/env python3
"""Retired launcher stages fail clearly without selecting changed modern artwork.

Only these two launcher sources and current user-facing documents are inspected.
No engine, data, resource pack, historical projection fixture, or profile is read.
PowerShell execution checks run when pwsh/powershell is available.
"""
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
FLAGS = (
    'BeforeGreenHead', 'BeforeGreenV2', 'BeforeGreenTrail', 'BeforeShield',
    'BeforeWhiteSmoke', 'BeforeLargeGround', 'BeforeImpact', 'BeforeLargeAir',
)
SUFFIXES = (
    'explosion-v2-test', 'explosion-v2-large-air-v1-test',
    'explosion-v2-large-air-v1-impact-v1-test', 'death-effects-v1-test',
    'death-effects-white-smoke-v1-test', 'death-effects-white-smoke-shield-v1-test',
    'death-effects-white-smoke-shield-green-v1-test',
    'death-effects-white-smoke-shield-green-v2-test',
)
LAUNCHERS = {
    'prototype/start-actual-preview.ps1': ('preview', 'talon13'),
    'prototype/start-asset-debug.ps1': ('debug', 'blue-four'),
}
POWERSHELL = shutil.which('pwsh') or shutil.which('powershell')


class RetiredPackSelectors(unittest.TestCase):
    def test_eight_switches_remain_declared_and_fail_before_any_dependencies(self):
        for path, (kind, _) in LAUNCHERS.items():
            with self.subTest(path=path):
                source = (ROOT / path).read_text()
                for flag in FLAGS:
                    self.assertIn('[switch]$' + flag, source)
                    self.assertNotIn('if ($' + flag + ') { $' + kind + 'Assets', source)
                declared = re.search(r'\$retiredSelectors = @\(([^\n]+)\)', source)
                self.assertIsNotNone(declared)
                self.assertEqual(tuple(re.findall(r"'([^']+)'", declared[1])), FLAGS)
                guard = source.index('foreach ($retiredSelector in $retiredSelectors)')
                dependencies = source.index('$' + kind + 'RepoRoot = ')
                self.assertLess(guard, dependencies)
                guard_source = source[guard:dependencies]
                self.assertIn('if ($PSBoundParameters[$retiredSelector])', guard_source)
                self.assertIn('throw "Historical -$retiredSelector is retired.', guard_source)
                self.assertIn('docs/RETIRED_HD_PACKS.md', guard_source)
                self.assertIn('Omit this switch to use the current ', guard_source)
                self.assertNotIn('New-Item', source[:guard])
                self.assertNotIn('Start-Process', source[:guard])

    def test_no_retired_installed_paths_or_default_changes(self):
        for path, (kind, family) in LAUNCHERS.items():
            with self.subTest(path=path):
                source = (ROOT / path).read_text()
                default = ('packed-' + family + '-foundation-type10-'
                           'death-effects-white-smoke-shield-green-v2-head-v1-test')
                self.assertIn("$" + kind + "Assets = Join-Path $" + kind +
                              "RepoRoot 'assets\\hd\\packs\\" + default + "'", source)
                for suffix in SUFFIXES:
                    self.assertNotIn('packed-' + family + '-foundation-type10-' + suffix, source)
                for flag in ('BeforeSmallExplosion', 'BeforeType10', 'BeforeFoundation'):
                    self.assertIn('if ($' + flag + ') { $' + kind +
                                  'Assets = Join-Path $' + kind + 'TaskRoot', source)
                if kind == 'debug':
                    self.assertIn('if ($Assets) { $debugAssets = [IO.Path]::GetFullPath($Assets) }', source)

    def test_current_readme_commands_select_complete_startup_pack(self):
        for path in ('README.md', 'README.zh-CN.md'):
            with self.subTest(path=path):
                source = (ROOT / path).read_text()
                installed = re.findall(r'--startup-assets=assets/hd/packs/([^\s`]+)', source)
                self.assertGreaterEqual(len(installed), 4)
                self.assertEqual(set(installed), {'startup-title-settings-v1'})
                self.assertIn('docs/RETIRED_HD_PACKS.md', source)

    @unittest.skipUnless(POWERSHELL, 'PowerShell is unavailable; source checks still run')
    def test_retired_switches_stop_without_creating_runs_or_launching(self):
        # A dependency-free copy ensures no user data, executable or packs are used.
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for path in LAUNCHERS:
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / path, target)
                for flag in FLAGS:
                    with self.subTest(path=path, flag=flag):
                        command = [POWERSHELL, '-NoLogo', '-NoProfile', '-NonInteractive',
                                   '-File', str(target), '-' + flag]
                        if path.endswith('start-asset-debug.ps1'):
                            command += ['-Assets', str(root / 'override-pack')]
                        result = subprocess.run(command, cwd=root, capture_output=True,
                                                text=True, timeout=20)
                        self.assertNotEqual(result.returncode, 0)
                        output = result.stdout + result.stderr
                        self.assertIn('Historical -' + flag + ' is retired.', output)
                        self.assertIn('docs/RETIRED_HD_PACKS.md', output)
                        self.assertNotIn('dependency missing', output.lower())
                        self.assertEqual({p.name for p in root.iterdir()}, {'prototype'})


if __name__ == '__main__':
    unittest.main(verbosity=2)
