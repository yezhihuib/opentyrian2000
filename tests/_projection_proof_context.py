"""Private, single-projection proof reuse; never a persistent filesystem cache.

The manifest is a sequential byte/type/mode check, NOT an atomic snapshot. A
change-and-restore between reads is not detectable. Python/interpreter and
installed native linked system libraries are trusted immutable execution inputs;
this guard covers repository inputs and the explicitly selected external tool,
package, module/configuration trees and renderer profile. It is not a general
concurrent-filesystem security boundary or an installed-OS attestation.
"""
from dataclasses import dataclass
from pathlib import Path
import hashlib
import importlib
import json
import os
import stat
import sys


@dataclass(frozen=True)
class _Dependencies:
    files: tuple = ()
    directories: tuple = ()
    external_files: tuple = ()
    external_trees: tuple = ()
    modules: tuple = ()
    code_modules: tuple = ()


def _freeze(value):
    if isinstance(value, dict):
        return ('dict', tuple((_freeze(k), _freeze(v)) for k, v in value.items()))
    if isinstance(value, list):
        return ('list', tuple(map(_freeze, value)))
    if isinstance(value, tuple):
        return ('tuple', tuple(map(_freeze, value)))
    if isinstance(value, (set, frozenset)):
        return ('frozenset' if isinstance(value, frozenset) else 'set', tuple(map(_freeze, value)))
    if value is None or type(value) in (str, bytes, bool, int, float):
        return ('scalar', value)
    raise TypeError('Unsupported current-proof value')


def _thaw(value):
    kind, items = value
    if kind == 'dict':
        return {_thaw(k): _thaw(v) for k, v in items}
    if kind == 'list':
        return [_thaw(v) for v in items]
    if kind == 'tuple':
        return tuple(_thaw(v) for v in items)
    if kind in ('set', 'frozenset'):
        result = {_thaw(v) for v in items}
        return frozenset(result) if kind == 'frozenset' else result
    return items


def _info(path):
    try:
        return path.lstat()
    except OSError as exc:
        raise ValueError('Missing/unreadable proof dependency: ' + str(path)) from exc


def _reparse(info):
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, 'st_file_attributes', 0) & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 1024))


def _safe_path(path, directory=False):
    path = Path(path).absolute()
    for parent in reversed(path.parents):
        info = _info(parent)
        if _reparse(info) or not stat.S_ISDIR(info.st_mode):
            raise ValueError('Unsafe proof dependency ancestor: ' + str(parent))
    info = _info(path)
    expected = stat.S_ISDIR if directory else stat.S_ISREG
    if _reparse(info) or not expected(info.st_mode):
        raise ValueError('Unsafe proof dependency kind: ' + str(path))
    return path, info


def _digest(path):
    digest = hashlib.sha256()
    try:
        with path.open('rb') as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b''):
                digest.update(block)
    except OSError as exc:
        raise ValueError('Unreadable proof dependency: ' + str(path)) from exc
    return digest.hexdigest()


def _ancestor_modes(path):
    return tuple((str(p), stat.S_IFMT(_info(p).st_mode), stat.S_IMODE(_info(p).st_mode)) for p in reversed(path.parents))


def _repo_stamp(path):
    path, info = _safe_path(path)
    return (stat.S_IMODE(info.st_mode), stat.S_IFMT(info.st_mode), _digest(path), _ancestor_modes(path))


def _directory_stamp(path):
    path, info = _safe_path(path, directory=True)
    try:
        children = tuple(sorted((p.name, stat.S_IFMT(_info(p).st_mode), stat.S_IMODE(_info(p).st_mode)) for p in path.iterdir()))
    except OSError as exc:
        raise ValueError('Unreadable proof dependency directory: ' + str(path)) from exc
    return (stat.S_IMODE(info.st_mode), children, _ancestor_modes(path))


def _external_stamp(path):
    """Installed executable symlinks are allowed, but the full link chain is bound."""
    path = Path(path).absolute()
    links = []
    seen = set()
    while True:
        if path in seen or len(seen) > 40:
            raise ValueError('Cyclic external proof dependency')
        seen.add(path)
        restart = False
        for part in (*reversed(path.parents), path):
            info = _info(part)
            links.append((str(part), stat.S_IFMT(info.st_mode), stat.S_IMODE(info.st_mode)))
            if stat.S_ISLNK(info.st_mode):
                target = os.readlink(part)
                links.append((str(part), stat.S_IMODE(info.st_mode), target))
                suffix = path.relative_to(part)
                replacement = Path(target) if os.path.isabs(target) else part.parent / target
                path = Path(os.path.abspath(replacement / suffix))
                restart = True
                break
            if getattr(info, 'st_file_attributes', 0) & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 1024):
                raise ValueError('Unsupported external reparse dependency')
        if not restart:
            break
    return (tuple(links), str(path), _repo_stamp(path))


def _tree_stamp(path):
    # Tool package/config trees are closed: addition and deletion count as drift.
    path, _ = _safe_path(path, directory=True)
    result = []
    def visit(directory):
        result.append((str(directory.relative_to(path)), 'directory', _directory_stamp(directory)))
        for child in sorted(directory.iterdir()):
            info = _info(child)
            if _reparse(info):
                raise ValueError('Unsafe external package-tree link: ' + str(child))
            if stat.S_ISDIR(info.st_mode):
                visit(child)
            else:
                result.append((str(child.relative_to(path)), 'file', _repo_stamp(child)))
    visit(path)
    return tuple(result)


def _profile(module):
    names = ('NODE', 'SHARP', 'NODE_VERSION', 'SHARP_VERSIONS', 'DRIVER', 'MAGICK', 'MAGICK_VERSION', 'GOLDEN_HASHES', 'GOLDEN_MASTER', 'GOLDEN_SVG', 'PILLOW_VERSION', 'PILLOW_ZLIB_VERSION', 'ZLIB_VERSION')
    values = tuple((name, _freeze(getattr(module, name))) for name in names if hasattr(module, name))
    if hasattr(module, 'tool_environment'):
        values += (('tool_environment', _freeze(module.tool_environment())),)
    return values


def _relative(root, name):
    if not isinstance(name, str) or not name or '\\' in name:
        raise ValueError('Invalid proof dependency path')
    parts = name.split('/')
    if name.startswith('/') or any(p in ('', '.', '..') for p in parts) or ':' in parts[0]:
        raise ValueError('Invalid proof dependency path')
    return root.joinpath(*parts)


def _module_origin(name, expected):
    # A prior worktree import is ordinary contamination, not a trusted cache hit.
    module = sys.modules.get(name)
    actual = getattr(module, '__file__', None)
    if actual is None or Path(actual).absolute() != expected:
        raise ValueError('Current-proof implementation origin mismatch: ' + name)
    _safe_path(expected)
    return (name, str(expected))


class _ProjectionProofContext:
    def __init__(self, root, module_root):
        self.root = Path(root).absolute()
        self.module_root = Path(module_root).absolute()
        if Path(__file__).absolute() != self.module_root / 'tests' / '_projection_proof_context.py':
            raise ValueError('Current-proof context implementation origin mismatch')
        _safe_path(self.root, directory=True)
        _safe_path(self.module_root, directory=True)
        self._entries = {}
        self._closed = False

    def _module(self, family):
        if family not in ('rear281', 'rear1', 'rear39', 'rear_p7', 'missile', 'mint27', 'newshf', 'guided', 'sonic', 'protron'):
            raise ValueError('Unknown current-proof family')
        scripts = str(self.module_root / 'scripts')
        if scripts not in sys.path:
            sys.path.insert(0, scripts)
        name = 'current_' + family + '_compatibility'
        module = importlib.import_module(name)
        _module_origin(name, self.module_root / 'scripts' / (name + '.py'))
        return module

    def _discover(self, family):
        c = self._module(family)
        families = ('rear_p7', 'rear39', 'rear1', 'rear281') if family in ('rear_p7', 'rear39', 'rear1', 'rear281') else (family,)
        modules = tuple(self._module(name) for name in families)
        seeds = {_relative(self.root, m.SELECTION) for m in modules}
        if family == 'newshf':
            seeds |= {_relative(self.root, c.legacy.INPUT + '/' + n) for n in ('manifest.json', 'provenance.json', 'report.json')}
        before = tuple((p, _repo_stamp(p)) for p in sorted(seeds))
        files, directories = set(seeds), set()
        for m in modules:
            names = m.input_paths(self.root) | {m.MAPPING, m.HEADER}
            if m.__name__ == 'current_protron_compatibility':
                names |= {m.ROOT + '/' + m.name(*pair) for pair in m.PAIRS}
            files |= {_relative(self.root, n) for n in names}
        if family == 'newshf':
            files |= {_relative(self.root, n) for n in c.LEGACY_SHA256}
            directories |= {_relative(self.root, n) for n in (c.ROOT, c.INPUT_ROOT + '/derived', c.legacy.OUTPUT, c.legacy.INPUT)}
        # These source inverses execute only for these original proof functions.
        chains = {'rear281': ('rear281',), 'rear1': ('rear1',), 'rear39': ('rear39',), 'rear_p7': ('rear_p7',),
                  'missile': ('rear_p7', 'missile'),
                  'mint27': ('rear_p7', 'missile', 'mint27'),
                  'newshf': ('rear_p7', 'missile', 'mint27', 'newshf')}
        for name in chains.get(family, ()):
            ledger = self.module_root / 'tests' / ('current_' + name + '_source_projection.json')
            files.add(ledger)
            _repo_stamp(ledger)
            for source in json.loads(ledger.read_bytes())['files']:
                files.add(_relative(self.root, source))
        scripts = {'current_craft267_compatibility.py', 'package_runtime.py', 'build_current_art.py'}
        scripts |= {'current_' + name + '_compatibility.py' for name in families}
        if family == 'newshf':
            scripts |= {'current_guided_compatibility.py', 'build_newshf_hd.py', 'check_newshf_phase_a.py'}
        code_modules = tuple((name[:-3], self.module_root / 'scripts' / name) for name in sorted(scripts))
        for name, expected in code_modules:
            importlib.import_module(name)
            _module_origin(name, expected)
        files |= {self.module_root / 'scripts' / name for name in scripts}
        files |= {self.module_root / 'tests' / name for name in ('accepted_later_changes.py', '_projection_proof_context.py')}
        external_files, external_trees = set(), set()
        if family in ('rear281', 'rear1', 'rear39', 'rear_p7'):
            # Rear1's accepted 77 PNG encoder is Pillow, in addition to Sharp.
            import PIL, PIL.Image, PIL.PngImagePlugin
            external_trees.add(Path(PIL.__file__).parent)
            p7 = self._module('rear_p7')
            external_files |= {Path(p7.NODE), Path(p7.SHARP)}
            package = Path(p7.SHARP).parent.parent
            external_trees |= {package, *(package.parent / n for n in ('@img', 'semver', 'detect-libc'))}
        if family == 'missile':
            external_files.add(Path(c.MAGICK))
            external_trees |= {Path(n) for n in ('/etc/ImageMagick-7', '/usr/share/ImageMagick-7', '/usr/lib/x86_64-linux-gnu/ImageMagick-7.1.1')}
        if before != tuple((p, _repo_stamp(p)) for p, _ in before):
            raise ValueError('Current-proof selection changed during dependency discovery')
        return _Dependencies(tuple(sorted(files)), tuple(sorted(directories)), tuple(sorted(external_files)), tuple(sorted(external_trees)), modules, code_modules)

    def _snapshot(self, deps):
        return (tuple((str(p), _repo_stamp(p)) for p in deps.files),
                tuple((str(p), _directory_stamp(p)) for p in deps.directories),
                tuple((str(p), _external_stamp(p)) for p in deps.external_files),
                tuple((str(p), _tree_stamp(p)) for p in deps.external_trees),
                tuple((m.__name__, _profile(m)) for m in deps.modules),
                tuple(_module_origin(name, expected) for name, expected in deps.code_modules))

    def _check_tools(self, family):
        if family in ('rear281', 'rear1', 'rear39', 'rear_p7'):
            self._module('rear_p7').check_tool()
            self._module('rear39').check_tool()
            self._module('rear1').check_tool()
            self._module('rear281').check_tool()
        elif family == 'missile':
            self._module('missile').check_tool()

    def _check(self, family, deps, manifest):
        if self._snapshot(deps) != manifest:
            raise ValueError('Changed current-proof dependency: ' + family)
        self._check_tools(family)
        if self._snapshot(deps) != manifest:
            raise ValueError('Changed current-proof dependency during renderer check: ' + family)

    def get(self, family, validator):
        if self._closed:
            raise ValueError('Current-proof context is closed')
        try:
            if family not in self._entries:
                deps = self._discover(family)
                manifest = self._snapshot(deps)
                proof = validator(self.root)
                if self._snapshot(deps) != manifest:
                    raise ValueError('Changed current-proof dependency during validation: ' + family)
                self._entries[family] = (deps, manifest, _freeze(proof))
            else:
                deps, manifest, _ = self._entries[family]
                self._check(family, deps, manifest)
            return _thaw(self._entries[family][2])
        except BaseException:
            self.close()
            raise

    def finish(self):
        if self._closed:
            raise ValueError('Current-proof context is closed')
        try:
            for family, (deps, manifest, _) in self._entries.items():
                self._check(family, deps, manifest)
        finally:
            self.close()

    def close(self):
        self._entries.clear()
        self._closed = True
