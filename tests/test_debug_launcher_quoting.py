"""Source-locked Windows argument model, NOT a PowerShell/Windows execution test.

Microsoft Start-Process joins ArgumentList elements with spaces. SDL2 Windows
main uses CommandLineToArgvW. The documented backslash-before-quote rules are
modeled below only for these finite argument cases:
https://learn.microsoft.com/en-us/windows/win32/api/shellapi/nf-shellapi-commandlinetoargvw
https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/start-process
LF/CRLF grammar: https://learn.microsoft.com/en-us/powershell/scripting/lang-spec/chapter-02
"""
import argparse
import hashlib
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT
ORIGINAL_SHA = '693b51f4b6e6747b6bf8efd3fe9c81f41da806f4f29be9196216eb581b97eedb'
OLD_CALL = '$debugQuotedArgs = @($debugArgs | ForEach-Object { \'"\' + $_ + \'"\' })'
NEW_CALL = '$debugQuotedArgs = @($debugArgs | ForEach-Object { Quote-DebugArgument $_ })'
FUNCTION = r'''function Quote-DebugArgument([string]$Value) {
    if ($Value -match '["\r\n]') { throw 'Paths cannot contain quotes or line breaks.' }
    $tail = $Value.Length - $Value.TrimEnd('\').Length
    return '"' + $Value + ('\' * $tail) + '"'
}'''


def quote_model(value):
    """Models the source-locked helper; no claim of executing PowerShell."""
    if any(c in value for c in ('"', '\r', '\n')):
        raise ValueError('Paths cannot contain quotes or line breaks.')
    tail = len(value) - len(value.rstrip('\\'))
    return '"' + value + '\\' * tail + '"'


def documented_argv_model(command):
    """Independent finite CommandLineToArgvW rule model, excluding argv0 quirks."""
    args = []
    i = 0
    while i < len(command):
        while i < len(command) and command[i] in ' \t':
            i += 1
        if i == len(command):
            break
        part = []
        quoted = False
        while i < len(command):
            c = command[i]
            if c in ' \t' and not quoted:
                break
            if c == '\\':
                start = i
                while i < len(command) and command[i] == '\\':
                    i += 1
                count = i - start
                if i < len(command) and command[i] == '"':
                    part.append('\\' * (count // 2))
                    if count % 2:
                        part.append('"')
                    else:
                        quoted = not quoted
                    i += 1
                else:
                    part.append('\\' * count)
                continue
            if c == '"':
                quoted = not quoted
            else:
                part.append(c)
            i += 1
        args.append(''.join(part))
    return args


def canonical_source(raw):
    # This NEW source-text test allows LF/CRLF (including mixed line endings).
    # It does not normalize or change any existing raw-byte hash validator.
    # PowerShell lexical new-line grammar accepts both; this fixed script has
    # no multiline string payload whose literal newline bytes are significant.
    text = raw.decode('utf-8')
    if '\r' in text.replace('\r\n', ''):
        raise ValueError('Bare CR is outside the finite checkout contract')
    return text.replace('\r\n', '\n')


class DebugLauncherQuoting(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = (ROOT / 'prototype/start-asset-debug.ps1').read_bytes()
        cls.source = canonical_source(cls.raw)

    def test_exact_helper_reuse_without_executing_other_launchers(self):
        self.assertEqual(self.source.count(FUNCTION), 1)
        for path in ('prototype/start-manual-hd.ps1', 'packaging/start-hd.ps1'):
            source = (REFERENCE / path).read_text()
            match = re.search(r'function Quote-ManualArgument\(\[string\]\$Value\) \{\n.*?\n\}', source, re.S)
            self.assertIsNotNone(match)
            self.assertEqual(match.group().replace('Quote-ManualArgument', 'Quote-DebugArgument', 1), FUNCTION)
        self.assertNotIn(". (Join-Path $PSScriptRoot 'start-manual-hd.ps1')", self.source)

    def test_exact_inverse_preserves_all_flags_order_metadata_and_other_code(self):
        self.assertEqual(self.source.count(NEW_CALL), 1)
        self.assertNotIn(OLD_CALL, self.source)
        canonical = self.source.encode('utf-8')
        variants = (self.raw, canonical, canonical.replace(b'\n', b'\r\n'),
                    canonical.replace(b'\n', b'\r\n', 1))
        for raw in variants:
            text = canonical_source(raw)
            restored = text.replace(FUNCTION + '\n', '', 1).replace(NEW_CALL, OLD_CALL, 1)
            self.assertEqual(hashlib.sha256(restored.encode('utf-8')).hexdigest(), ORIGINAL_SHA)
        changed = self.source.replace("'--no-sound'", "'--changed-sound'", 1)
        self.assertNotEqual(changed, self.source)
        restored = changed.replace(FUNCTION + '\n', '', 1).replace(NEW_CALL, OLD_CALL, 1)
        self.assertNotEqual(hashlib.sha256(restored.encode('utf-8')).hexdigest(), ORIGINAL_SHA)
        with self.assertRaises(ValueError):
            canonical_source(b'line\rnext')
        self.assertNotIn('@"', self.source)
        self.assertNotIn("@'", self.source)
        self.assertIn('-ArgumentList $debugQuotedArgs', self.source)
        self.assertIn('argv = @($debugExe) + $debugArgs', self.source)

    def test_explicit_expected_serialization_zero_one_two_three_trailing_slashes(self):
        cases = [('', '""'), ('simple', '"simple"'), ('a b', '"a b"'), ('中文 空格', '"中文 空格"'), ('a\tb', '"a\tb"')]
        for value, expected in cases:
            self.assertEqual(quote_model(value), expected)
        for n in range(4):
            value = '--assets=C:\\工程 空格' + '\\' * n
            expected = '"--assets=C:\\工程 空格' + '\\' * (2 * n) + '"'
            self.assertEqual(quote_model(value), expected)

    def test_roundtrip_boundaries_with_root_unc_and_following_sentinel(self):
        cases = ['', 'plain', '中文 空格', 'a\tb', 'C:\\', '\\\\服务器\\共享\\', '--assets=C:\\工程 空格\\']
        cases += ['--assets=C:\\pack' + '\\' * n for n in range(4)]
        for value in cases:
            values = ['program.exe', value, '--sentinel=next', 'after space']
            command = ' '.join(quote_model(v) for v in values)
            self.assertEqual(documented_argv_model(command), values, value)

    def test_embedded_quote_cr_lf_are_rejected_not_escaped(self):
        for value in ['a"b', '"', 'a\rb', 'a\nb', '\r\n', 'C:\\资料"\\']:
            with self.assertRaises(ValueError):
                quote_model(value)

    def test_original_counterexample_and_ordinary_output_equivalence(self):
        values = ['program.exe', '--render-assets=C:\\项目 素材\\', '--asset-debug-control=C:\\runs\\control.txt']
        old = ' '.join('"' + value + '"' for value in values)
        self.assertNotEqual(documented_argv_model(old), values)
        self.assertEqual(documented_argv_model(' '.join(quote_model(v) for v in values)), values)
        for value in ['--no-sound', '--render-ticks=6000', '--render-assets=C:\\项目 素材', '--asset-debug-control=C:\\runs\\control.txt']:
            self.assertEqual(quote_model(value), '"' + value + '"')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--reference-root', type=Path, default=ROOT)
    args, rest = parser.parse_known_args()
    REFERENCE = args.reference_root.resolve()
    unittest.main(argv=[__file__, *rest])
