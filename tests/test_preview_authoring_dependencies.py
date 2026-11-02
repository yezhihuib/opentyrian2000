"""Local stdlib/source checks only; does not execute PowerShell or producers."""
import ast
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/check_preview_authoring_dependencies.py'
spec = importlib.util.spec_from_file_location('preview_preflight', SCRIPT)
CHECK = importlib.util.module_from_spec(spec)
spec.loader.exec_module(CHECK)
ADDITION = "    & $craftPython (Join-Path $RepoRoot 'scripts\\check_preview_authoring_dependencies.py') --root $RepoRoot | Out-Null\n    if ($LASTEXITCODE -ne 0) { throw 'Source preview authoring prerequisites are unavailable; see preflight diagnostics above. No game was launched.' }\n"
BASE_SHA = '427b937ddb0cd02be9907b659b60bbcfa3c204a66e0d1a1fbab160e39d7d631e'


def text(path):
    raw = path.read_bytes().replace(b'\r\n', b'\n')
    if b'\r' in raw:
        raise ValueError('Bare CR unsupported by this source contract')
    return raw.decode('utf-8')


class PreviewDependencies(unittest.TestCase):
    def test_real_declarations_without_importing_producers(self):
        found = {}
        for relative, name, executable in CHECK.DECLARATIONS:
            found[name] = CHECK.declared_path(text(ROOT / relative), name)
        self.assertEqual(found, {'MAGICK': '/usr/bin/magick',
            'NODE': '/opt/codex/runtimes/codex-primary-runtime/dependencies/node/bin/node',
            'SHARP': '/opt/codex/runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp/dist/index.cjs'})
        tree = ast.parse(text(SCRIPT))
        imports = {node.names[0].name for node in ast.walk(tree) if isinstance(node, ast.Import)}
        imports |= {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
        self.assertEqual(imports, {'argparse', 'ast', 'json', 'os', 'pathlib', 'sys'})
        self.assertFalse(any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                             and n.func.id in ('eval', 'exec', '__import__') for n in ast.walk(tree)))

    def test_declarations_fail_closed(self):
        bad = ['', 'MAGICK=x', 'MAGICK="a"\nMAGICK="b"',
               'if True:\n MAGICK="a"', 'MAGICK="a"\nif True:\n MAGICK="b"',
               'MAGICK="a"\ndel MAGICK', 'MAGICK="a"\nimport x as MAGICK',
               'MAGICK="a"\ndef MAGICK(): pass', 'MAGICK="a"\nclass MAGICK: pass',
               'MAGICK: str="a"', 'MAGICK=NODE="a"', 'MAGICK=""', 'MAGICK="a\\x00b"']
        for source in bad:
            with self.subTest(source=source), self.assertRaises(ValueError):
                CHECK.declared_path(source, 'MAGICK')
        self.assertEqual(CHECK.declared_path('MAGICK="a b 中文"', 'MAGICK'), 'a b 中文')

    def test_missing_tools_are_all_reported(self):
        with patch.object(Path, 'is_file', return_value=False), self.assertRaises(ValueError) as caught:
            CHECK.check(ROOT)
        for word in ('MAGICK=', 'NODE=', 'SHARP=', '-AssetsDirectory', '-Assets', 'packaging/start-hd.ps1', 'No pack was built'):
            self.assertIn(word, str(caught.exception))

    def test_executable_and_module_readability_are_distinct(self):
        for missing in ('MAGICK', 'NODE', 'SHARP'):
            def access(path, mode):
                value=str(path)
                selected = ('magick' in value if missing=='MAGICK' else
                            value.endswith('/node') if missing=='NODE' else value.endswith('index.cjs'))
                return not (selected and mode == (os.R_OK if missing=='SHARP' else os.X_OK))
            with self.subTest(missing=missing), patch.object(Path, 'is_file', return_value=True), patch.object(CHECK.os, 'access', side_effect=access), self.assertRaises(ValueError) as caught:
                CHECK.check(ROOT)
            self.assertIn(missing+'=', str(caught.exception))
        def module_not_executable(path, mode):
            return not (str(path).endswith('index.cjs') and mode==os.X_OK)
        with patch.object(Path,'is_file',return_value=True), patch.object(CHECK.os,'access',side_effect=module_not_executable):
            result=CHECK.check(ROOT)
        self.assertEqual(result['status'], 'PRESENCE_ONLY_PASS')
        self.assertFalse(result['versions_verified']); self.assertFalse(result['pack_validated'])

    def test_main_presence_success_is_not_validation(self):
        result={'status':'PRESENCE_ONLY_PASS','versions_verified':False,'pack_validated':False}
        out=io.StringIO()
        with patch.object(CHECK,'check',return_value=result), contextlib.redirect_stdout(out):
            self.assertEqual(CHECK.main(['--root',str(ROOT)]),0)
        self.assertEqual(json.loads(out.getvalue()),result)

    def test_actual_cli_failure_does_not_write_or_run_builder(self):
        with tempfile.TemporaryDirectory(prefix='preview dependency 中文 ') as temp:
            root=Path(temp);(root/'scripts').mkdir()
            missing=str(root/'not installed')
            (root/CHECK.DECLARATIONS[0][0]).write_text('MAGICK='+repr(missing)+'\n',encoding='utf-8')
            (root/CHECK.DECLARATIONS[1][0]).write_text('NODE='+repr(missing)+'\nSHARP='+repr(missing)+'\n',encoding='utf-8')
            before={str(p.relative_to(root)):p.read_bytes() for p in root.rglob('*') if p.is_file()}
            p=subprocess.run([sys.executable,'-I','-B','-S',str(SCRIPT),'--root',str(root)],capture_output=True,timeout=10)
            self.assertEqual(p.returncode,2);self.assertEqual(p.stdout,b'')
            self.assertIn(b'No pack was built',p.stderr)
            self.assertEqual(before,{str(p.relative_to(root)):p.read_bytes() for p in root.rglob('*') if p.is_file()})
            self.assertFalse((root/'current-craft267-packs').exists())

    def test_ps_exact_inverse_and_early_order(self):
        source=text(ROOT/'prototype/current-craft267-pack.ps1')
        self.assertEqual(source.count(ADDITION),1)
        old=source.replace(ADDITION,'',1)
        self.assertEqual(hashlib.sha256(old.encode()).hexdigest(),BASE_SHA)
        self.assertLess(source.index('Get-Command python'),source.index(ADDITION))
        self.assertLess(source.index(ADDITION),source.index('$craftOutput ='))
        self.assertLess(source.index(ADDITION),source.index('scripts\\build_current_craft267.py'))
        self.assertEqual(old, text(ROOT/'prototype/current-craft267-pack.ps1').replace(ADDITION,''))

    def test_existing_runtime_and_explicit_pack_bypass(self):
        manual=text(ROOT/'prototype/start-manual-hd.ps1')
        debug=text(ROOT/'prototype/start-asset-debug.ps1')
        preview=text(ROOT/'prototype/start-actual-preview.ps1')
        runtime=text(ROOT/'packaging/start-hd.ps1')
        self.assertIn("if (-not $AssetsDirectory) {\n    . (Join-Path $PSScriptRoot 'current-craft267-pack.ps1')",manual)
        self.assertIn("if (-not ($Assets -or $BeforeSmallExplosion -or $BeforeType10 -or $BeforeFoundation)) {\n    . (Join-Path $PSScriptRoot 'current-craft267-pack.ps1')",debug)
        self.assertIn("if (-not ($BeforeSmallExplosion -or $BeforeType10 -or $BeforeFoundation -or $BeforeRoad -or $TurretV4 -or $TurretV2 -or $Before101)) {\n    . (Join-Path $PSScriptRoot 'current-craft267-pack.ps1')",preview)
        for source in (manual,debug,preview,runtime):
            self.assertNotIn('check_preview_authoring_dependencies',source)
        self.assertNotIn('New-CurrentCraft267Pack',runtime)


if __name__ == '__main__':
    unittest.main()
