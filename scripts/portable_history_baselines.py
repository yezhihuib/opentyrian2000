"""Read-only, frozen historical test oracles; never resolve HEAD or fetch history.

The fixture contains minimal original bytes, not commits. Additional bytes come
only from explicitly pinned objects in a full public Git clone. See
``docs/portable-history-baselines.md`` for the support boundary.
"""
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess

PIN = '2f10a46d70cb5fed377373f22f484b1c27f2a9cb1a969eab765cbf08407c9b02'
FIXTURE = Path('tests/fixtures/portable-history-v1')


class BaselineError(ValueError):
    """An immutable oracle is missing, altered, or outside the declared scope."""


def require(condition, message):
    if not condition:
        raise BaselineError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()


def blobid(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def valid_path(name):
    require(isinstance(name, str) and '\\' not in name and '\0' not in name
            and all(p not in ('', '.', '..') for p in name.split('/')),
            'invalid baseline path')


def treeid(rows):
    """Reconstruct a tree digest without writing historical objects into Git."""
    root = {}
    for name, row in rows.items():
        valid_path(name)
        node = root
        for part in name.split('/')[:-1]:
            node = node.setdefault(part, {})
            require(isinstance(node, dict), 'overlapping inventory paths')
        leaf = name.split('/')[-1]
        require(leaf not in node, 'duplicate inventory path')
        node[leaf] = (row['mode'], row['blob'])

    def digest(node):
        entries = []
        for name, value in node.items():
            mode, oid = ('40000', digest(value)) if isinstance(value, dict) else value
            entries.append((name + ('/' if mode == '40000' else ''),
                            mode.encode() + b' ' + name.encode() + b'\0' + bytes.fromhex(oid)))
        raw = b''.join(value for _, value in sorted(entries))
        return hashlib.sha1(b'tree ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    return digest(root)


class Provider:
    def __init__(self, fixture, gitdir):
        self.root = Path(fixture)
        self.gitdir = str(gitdir)
        self.cache = {}
        raw = self.readfile('manifest.json')
        require(sha(raw) == PIN, 'manifest pin mismatch')
        self.m = json.loads(raw)
        expected = {'manifest.json'}
        for baseline in self.m['baselines'].values():
            expected.update('blobs/' + row['blob'] for row in baseline['preimages'].values()
                            if row['storage'] == 'fixture')
            if baseline['inventory']:
                expected.add('inventories/' + baseline['inventory_descriptor'])
        actual = set()
        for directory, dirs, files in os.walk(self.root, followlinks=False):
            for name in dirs:
                require(not (Path(directory) / name).is_symlink(), 'symlink fixture directory')
            actual.update((Path(directory) / name).relative_to(self.root).as_posix() for name in files)
        require(actual == expected, 'fixture missing/extra path')
        for name in expected:
            self.readfile(name)
        # Validate every private byte and descriptor, not only the first query.
        for baseline in self.m['baselines'].values():
            for row in baseline['preimages'].values():
                if row['storage'] == 'fixture':
                    self.verify(self.readfile('blobs/' + row['blob']), row)
            if baseline['inventory']:
                name = baseline['inventory_descriptor']
                require(sha(self.readfile('inventories/' + name)) + '.json' == name,
                        'descriptor pin mismatch')

    def readfile(self, name):
        valid_path(name)
        path = self.root / name
        try:
            require(not self.root.is_symlink(), 'symlink fixture root')
            for parent in path.parents:
                if parent == self.root:
                    break
                require(not parent.is_symlink(), 'symlink fixture directory')
            require(stat.S_ISREG(path.lstat().st_mode), 'nonregular fixture')
            return path.read_bytes()
        except OSError as error:
            raise BaselineError('missing/unreadable fixture: ' + name) from error

    def git(self, *args):
        try:
            return subprocess.check_output(['git', '--git-dir=' + self.gitdir, *args],
                                           stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as error:
            raise BaselineError('Required immutable public Git object unavailable; '
                                'use a full public clone (shallow clones/ZIP unsupported); '
                                'no automatic fetch: ' + ' '.join(args)) from error

    @staticmethod
    def verify(raw, row):
        require(row['mode'] in ('100644', '100755', '120000'), 'unsupported baseline mode')
        require(len(raw) == row['size'] and sha(raw) == row['sha256']
                and blobid(raw) == row['blob'], 'preimage mismatch')
        return raw

    def blob(self, oid):
        if oid not in self.cache:
            raw = self.git('cat-file', 'blob', oid)
            require(blobid(raw) == oid, 'public blob ID mismatch')
            self.cache[oid] = raw
        return self.cache[oid]

    def preimage(self, base, path):
        valid_path(path)
        if base in self.m['public_tree_aliases']:
            return self.git('show', self.m['public_tree_aliases'][base] + ':' + path)
        require(base in self.m['baselines'], 'unknown baseline')
        rows = self.m['baselines'][base]['preimages']
        require(path in rows, 'unlisted preimage')
        row = rows[path]
        raw = self.readfile('blobs/' + row['blob']) if row['storage'] == 'fixture' else self.blob(row['blob'])
        return self.verify(raw, row)

    def public_inventory(self, tree):
        rows = {}
        for item in self.git('ls-tree', '-rz', tree).split(b'\0'):
            if not item:
                continue
            head, name = item.split(b'\t')
            mode, kind, oid = head.decode().split()
            require(kind == 'blob', 'non-blob inventory entry')
            raw = self.blob(oid)
            rows[name.decode()] = dict(mode=mode, blob=oid, sha256=sha(raw), size=len(raw))
        require(treeid(rows) == tree, 'public tree mismatch')
        return rows

    def inventory(self, base):
        require(base in self.m['baselines'], 'unknown inventory baseline')
        baseline = self.m['baselines'][base]
        require(bool(baseline['inventory']), 'baseline has no inventory')
        name = baseline['inventory_descriptor']
        raw = self.readfile('inventories/' + name)
        require(sha(raw) + '.json' == name, 'descriptor pin mismatch')
        desc = json.loads(raw)
        require(set(desc['scopes']) == set(baseline['scopes']), 'inventory scope mismatch')
        out = {}
        for scope, entry in desc['scopes'].items():
            if 'public_tree' in entry:
                rows = self.public_inventory(entry['public_tree'])
                for path in entry['removed']:
                    del rows[path]
                rows.update(entry['overrides'])
            else:
                rows = entry['rows']
            require(treeid(rows) == entry['tree'], 'historical subtree mismatch')
            out.update({scope + '/' + p: row for p, row in rows.items()})
        require(sha(encoded(out)) == baseline['inventory'] == desc['expanded_sha256'],
                'inventory mismatch')
        return out

    def names(self, base, scope):
        valid_path(scope)
        if base in self.m['public_tree_aliases']:
            return set(self.git('ls-tree', '-rz', '--name-only',
                                self.m['public_tree_aliases'][base], '--', scope).decode().strip('\0').split('\0')) - {''}
        return {p for p in self.inventory(base) if p.startswith(scope + '/')}

    def changed(self, base, root, scopes=('assets', 'authoring-inputs')):
        """Git diff plus unignored untracked names, preserving prior Git semantics.

        Ignored *tracked* paths remain checked. An ignored untracked __pycache__
        is excluded by Git's actual ignore rules, never a suffix exception.
        """
        if base in self.m['public_tree_aliases']:
            return set(subprocess.check_output(['git', 'diff', '--name-only', '-z',
                       self.m['public_tree_aliases'][base], '--', *scopes], cwd=root).decode().strip('\0').split('\0')) - {''}
        old = {p: row for p, row in self.inventory(base).items()
               if any(p.startswith(s + '/') for s in scopes)}
        tracked_raw = subprocess.check_output(['git', 'ls-files', '--stage', '-z', '--', *scopes], cwd=root)
        tracked = {}
        for record in tracked_raw.split(b'\0'):
            if record:
                head, name = record.split(b'\t', 1)
                tracked[name.decode()] = head.decode().split()[0]
        other = subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard', '-z', '--', *scopes], cwd=root)
        names = set(tracked) | {p for p in other.decode().split('\0') if p}
        filemode = subprocess.run(['git', 'config', '--bool', 'core.filemode'], cwd=root,
                                  stdout=subprocess.PIPE, check=False).stdout.strip() != b'false'
        actual = {}
        for name in names:
            path = Path(root) / name
            # lstat of the leaf alone follows symlinked parent directories.
            # Reject that replacement before reading any data outside the scope.
            parent = path.parent
            while parent != Path(root):
                require(not parent.is_symlink(), 'symlink candidate parent directory')
                parent = parent.parent
            if not path.exists() and not path.is_symlink():
                continue
            mode = path.lstat().st_mode
            if stat.S_ISLNK(mode):
                raw, gitmode = os.readlink(path).encode(), '120000'
            else:
                require(stat.S_ISREG(mode), 'nonregular candidate asset')
                raw = path.read_bytes()
                gitmode = ('100755' if mode & 0o111 else '100644') if filemode else tracked.get(name, '100644')
            oid = blobid(raw)
            # Git diff compares clean-filtered bytes (not CRLF worktree bytes).
            # Never write the resulting object, and never filter a symlink.
            if gitmode != '120000' and name in old and oid != old[name]['blob']:
                oid = subprocess.check_output(
                    ['git', 'hash-object', '--path=' + name, '--stdin'],
                    input=raw, cwd=root).decode().strip()
            actual[name] = (gitmode, oid)
        expected = {p: (row['mode'], row['blob']) for p, row in old.items()}
        return {p for p in expected.keys() | actual.keys() if expected.get(p) != actual.get(p)}


_PROVIDERS = {}


def provider(root):
    root = Path(root).resolve()
    if root not in _PROVIDERS:
        gitdir = subprocess.check_output(['git', 'rev-parse', '--absolute-git-dir'], cwd=root).decode().strip()
        _PROVIDERS[root] = Provider(root / FIXTURE, gitdir)
    return _PROVIDERS[root]


def preimage(base, path, root):
    return provider(root).preimage(base, path)


def names(base, scope, root):
    return provider(root).names(base, scope)


def changed(base, root, scopes=('assets', 'authoring-inputs')):
    return provider(root).changed(base, root, scopes)
